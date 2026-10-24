#!/usr/bin/env python3
"""Matriz de mortalidad Z90: integración observacional, sin inventar tasas ni alterar H."""
from __future__ import annotations
import csv, hashlib, importlib.util, json, re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

TEXT_KEYS = {
    "texto", "text", "descripcion", "description", "hecho", "evento", "evidencia",
    "narrativa", "observacion", "observation", "resumen", "biografia", "contexto_textual"
}
REQUIRED_STATS = {
    "population", "year", "age_interval", "deaths", "exposure", "rate_type",
    "source_url", "retrieved_at", "source_sha256"
}

def _load_classifier(root: Path):
    path = root / "motor" / "familias_tokens" / "mortalidad_clasificador_lateral_v0_1.py"
    if not path.is_file():
        return None
    spec = importlib.util.spec_from_file_location("mortalidad_clasificador_activo_u6", path)
    mod = importlib.util.module_from_spec(spec)
    import sys
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod

def _extract_text(cuts):
    rows = []
    def walk(obj, cut_id, cut_date=None, parent_key=""):
        if isinstance(obj, dict):
            local_date = obj.get("fecha") or obj.get("date") or obj.get("year") or cut_date
            local_id = obj.get("cut_id") or obj.get("id") or cut_id
            for k, v in obj.items():
                if str(k).lower() in TEXT_KEYS and isinstance(v, str) and v.strip():
                    rows.append({"cut_id": str(local_id), "date": str(local_date) if local_date else None,
                                 "field": str(k), "text": v.strip()})
                elif isinstance(v, (dict, list)):
                    walk(v, local_id, local_date, str(k))
        elif isinstance(obj, list):
            for item in obj:
                walk(item, cut_id, cut_date, parent_key)
    for i, cut in enumerate(cuts or []):
        cut_id = (cut.get("cut_id") or cut.get("id") or f"C{i+1}") if isinstance(cut, dict) else f"C{i+1}"
        walk(cut, str(cut_id), (cut.get("fecha") or cut.get("date") or cut.get("year")) if isinstance(cut, dict) else None)
    # Exact duplicate text fields in nested projections are deduplicated by (cut, field, text).
    uniq = {}
    for row in rows:
        uniq[(row["cut_id"], row["field"], row["text"])] = row
    return list(uniq.values())

def _validate_stats(rows):
    accepted, rejected = [], []
    for i, row in enumerate(rows or []):
        if not isinstance(row, dict):
            rejected.append({"index": i, "reason": "ROW_NOT_OBJECT"}); continue
        missing = sorted(REQUIRED_STATS - set(row))
        if missing:
            rejected.append({"index": i, "reason": "MISSING_REQUIRED_FIELDS", "fields": missing}); continue
        try:
            year = int(row["year"])
            deaths = float(row["deaths"])
            exposure = float(row["exposure"])
        except (TypeError, ValueError):
            rejected.append({"index": i, "reason": "INVALID_NUMERIC_FIELD"}); continue
        if not (1 <= year <= 2100) or deaths < 0 or exposure <= 0:
            rejected.append({"index": i, "reason": "OUT_OF_RANGE"}); continue
        if not re.fullmatch(r"[0-9a-fA-F]{64}", str(row["source_sha256"])):
            rejected.append({"index": i, "reason": "INVALID_SOURCE_SHA256"}); continue
        if not str(row["source_url"]).startswith(("https://", "http://")):
            rejected.append({"index": i, "reason": "INVALID_SOURCE_URL"}); continue
        if not str(row["population"]).strip() or not str(row["age_interval"]).strip() or not str(row["rate_type"]).strip():
            rejected.append({"index": i, "reason": "EMPTY_DIMENSION"}); continue
        r = dict(row)
        r["year"] = year
        r["deaths"] = deaths
        r["exposure"] = exposure
        # Derived crude rate is explicitly a calculated rate; exposure unit must be declared.
        if str(row["rate_type"]).lower() == "deaths_per_100000_exposure":
            r["calculated_rate"] = round(deaths / exposure * 100000.0, 8)
        accepted.append(r)
    return accepted, rejected

def build_mortality_matrix(case: dict, motor_result: dict | None, root: Path) -> dict[str, Any]:
    cuts = case.get("cuts") or []
    text_rows = _extract_text(cuts)
    classifier = _load_classifier(root)
    subject = case.get("case_subject") or case.get("subject") or case.get("person")
    z90 = case.get("z90_date") or case.get("Z90") or case.get("freeze_date")
    classified = []
    if classifier:
        for row in text_rows:
            events = classifier.classify_death(row["text"], case_subject=subject, z90_date=z90)
            if events:
                classified.append({**row, "classification": events})
    stat_rows = case.get("mortality_statistics") or case.get("mortality_observations") or []
    table_path = root / "MORTALITY_AUDIT" / "mortality_statistics.json"
    table_sha = None
    if not stat_rows and table_path.is_file():
        try:
            loaded = json.loads(table_path.read_text(encoding="utf-8"))
            stat_rows = loaded.get("records", []) if isinstance(loaded, dict) else loaded
            table_sha = hashlib.sha256(table_path.read_bytes()).hexdigest()
        except Exception as exc:
            stat_rows = []
            table_error = f"{type(exc).__name__}: {exc}"
        else:
            table_error = None
    else:
        table_error = None
    # LISTO_CALIBRAR_20261024: huella de origen siempre explícita. Tabla real -> sha real;
    # sin tabla -> ausencia DECLARADA (no metadato faltante, no hash fingido); error de lectura -> None (se reporta).
    table_sha_motivo = None
    if table_sha is None and stat_rows and table_error is None:
        table_sha = hashlib.sha256(json.dumps(stat_rows, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")).hexdigest()
        table_sha_motivo = "sha256 de las filas estadísticas entregadas en el input (JSON canónico)"
    elif table_sha is None and table_error is None:
        table_sha = "NO_APLICA_SIN_TABLA"
        table_sha_motivo = ("no existe MORTALITY_AUDIT/mortality_statistics.json ni filas mortality_statistics/"
                            "mortality_observations en el input; no hay tabla que hashear (ausencia declarada, no hash inventado)")
    elif table_sha is not None:
        table_sha_motivo = "sha256 de MORTALITY_AUDIT/mortality_statistics.json"
    valid, rejected = _validate_stats(stat_rows)
    by_year = defaultdict(list)
    by_epoch = defaultdict(list)
    for row in valid:
        by_year[str(row["year"])].append(row)
        epoch = row.get("historical_epoch") or row.get("epoch")
        if epoch:
            by_epoch[str(epoch)].append(row)
    def summarize(group):
        out = {}
        for key, vals in sorted(group.items()):
            out[key] = {
                "records": len(vals),
                "deaths_sum": round(sum(v["deaths"] for v in vals), 8),
                "exposure_sum": round(sum(v["exposure"] for v in vals), 8),
                "calculated_rate_per_100000": round(sum(v["deaths"] for v in vals) / sum(v["exposure"] for v in vals) * 100000, 8)
                    if vals and all(v.get("rate_type") == "deaths_per_100000_exposure" for v in vals) else None,
                "populations": sorted({str(v["population"]) for v in vals}),
                "age_intervals": sorted({str(v["age_interval"]) for v in vals}),
                "source_sha256": sorted({str(v["source_sha256"]) for v in vals})
            }
        return out
    ready = bool(valid) and not rejected
    return {
        "version": "MATRIZ_MORTALIDAD_Z90_V0_2",
        "status": "STATISTICAL_TABLE_LOADED" if ready else "WIRED_WAITING_VERIFIED_MORTALITY_DATA",
        "wired_to_active_runner": True,
        "data_table": str(table_path.relative_to(root)) if table_path.is_file() else "input.mortality_statistics|input.mortality_observations",
        "data_table_sha256": table_sha,
        "data_table_sha256_motivo": table_sha_motivo if table_sha_motivo is not None else f"ERROR_LECTURA_TABLA: {table_error}",
        "data_table_estado": ("DECLARADO_AUSENTE_SIN_TABLA" if table_sha == "NO_APLICA_SIN_TABLA" else ("ERROR_LECTURA_TABLA" if table_sha is None else "TABLA_HASHEADA")),
        "accepted_statistical_rows": len(valid),
        "rejected_statistical_rows": rejected,
        "statistics_by_year": summarize(by_year),
        "statistics_by_historical_epoch": summarize(by_epoch),
        "narrative_text_fields_scanned": len(text_rows),
        "classified_mortality_events": classified,
        "unresolved_event_count": sum(1 for x in classified for e in x["classification"] if e.get("status") == "TORTUGAS"),
        "verified_rates_required_for_statistical_claims": True,
        "feeds_H": False,
        "can_decide_H": False,
        "changes_canonical_patterns": False,
        "changes_canonical_engine": False,
        "reason": ("Estadísticas agregadas por año/época solo desde filas con dimensiones, exposición, fuente, fecha y SHA-256 válidos. "
                   "La clasificación textual es observacional y no altera H1/H2. No se generaron tasas ni datos faltantes.")
    }
