#!/usr/bin/env python3
"""Matriz de mortalidad Z90: integración observacional, sin inventar tasas ni alterar H."""
from __future__ import annotations
import csv, gzip, hashlib, importlib.util, json, re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

TEXT_KEYS = {
    "texto", "text", "descripcion", "description", "hecho", "evento", "evidencia",
    "narrativa", "observacion", "observation", "resumen", "biografia", "contexto_textual"
}
BASE_REQUIRED_STATS = {
    "population", "year", "age_interval", "rate_type",
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
        missing = sorted(BASE_REQUIRED_STATS - set(row))
        if missing:
            rejected.append({"index": i, "reason": "MISSING_REQUIRED_FIELDS", "fields": missing}); continue
        rate_type = str(row.get("rate_type", "")).strip().lower()
        try:
            year = int(row["year"])
        except (TypeError, ValueError):
            rejected.append({"index": i, "reason": "INVALID_NUMERIC_FIELD", "field": "year"}); continue
        if not (1 <= year <= 2100):
            rejected.append({"index": i, "reason": "OUT_OF_RANGE", "field": "year"}); continue
        if not re.fullmatch(r"[0-9a-fA-F]{64}", str(row["source_sha256"])):
            rejected.append({"index": i, "reason": "INVALID_SOURCE_SHA256"}); continue
        if not str(row["source_url"]).startswith(("https://", "http://")):
            rejected.append({"index": i, "reason": "INVALID_SOURCE_URL"}); continue
        if not str(row["population"]).strip() or not str(row["age_interval"]).strip():
            rejected.append({"index": i, "reason": "EMPTY_DIMENSION"}); continue
        r = dict(row)
        r["year"] = year
        if rate_type == "deaths_per_100000_exposure":
            try:
                deaths = float(row["deaths"])
                exposure = float(row["exposure"])
            except (KeyError, TypeError, ValueError):
                rejected.append({"index": i, "reason": "MISSING_OR_INVALID_DEATHS_EXPOSURE"}); continue
            if deaths < 0 or exposure <= 0:
                rejected.append({"index": i, "reason": "OUT_OF_RANGE", "field": "deaths_or_exposure"}); continue
            r["deaths"] = deaths
            r["exposure"] = exposure
            r["calculated_rate"] = round(deaths / exposure * 100000.0, 8)
        elif rate_type in {"q_x", "m_x"}:
            try:
                rate_value = float(row["rate_value"])
            except (KeyError, TypeError, ValueError):
                rejected.append({"index": i, "reason": "MISSING_OR_INVALID_RATE_VALUE"}); continue
            if rate_value < 0 or (rate_type == "q_x" and rate_value > 1):
                rejected.append({"index": i, "reason": "RATE_VALUE_OUT_OF_RANGE"}); continue
            r["rate_value"] = rate_value
        elif rate_type == "life_table_mx_qx":
            try:
                mx = float(row["mx"])
                qx = float(row["qx"])
            except (KeyError, TypeError, ValueError):
                rejected.append({"index": i, "reason": "MISSING_OR_INVALID_LIFE_TABLE_RATES"}); continue
            if mx < 0 or not 0 <= qx <= 1:
                rejected.append({"index": i, "reason": "LIFE_TABLE_RATE_OUT_OF_RANGE"}); continue
            r["mx"] = mx
            r["qx"] = qx
        else:
            rejected.append({"index": i, "reason": "UNSUPPORTED_RATE_TYPE", "rate_type": rate_type}); continue
        for field in ("deaths", "exposure"):
            if field in r:
                try:
                    r[field] = float(r[field])
                except (TypeError, ValueError):
                    rejected.append({"index": i, "reason": "INVALID_NUMERIC_FIELD", "field": field}); break
        else:
            accepted.append(r)
    return accepted, rejected

def _new_accumulator():
    return {
        "records": 0, "deaths_sum": 0.0, "deaths_count": 0,
        "exposure_sum": 0.0, "exposure_count": 0,
        "qx_sum": 0.0, "qx_count": 0, "mx_sum": 0.0, "mx_count": 0,
        "life_qx_sum": 0.0, "life_qx_count": 0,
        "life_mx_sum": 0.0, "life_mx_count": 0,
        "rate_types": set(), "populations": set(), "age_intervals": set(),
        "source_sha256": set()
    }


def _accumulate(acc, row):
    acc["records"] += 1
    if "deaths" in row:
        acc["deaths_sum"] += row["deaths"]
        acc["deaths_count"] += 1
    if "exposure" in row:
        acc["exposure_sum"] += row["exposure"]
        acc["exposure_count"] += 1
    if row.get("rate_type") == "q_x" and "rate_value" in row:
        acc["qx_sum"] += row["rate_value"]; acc["qx_count"] += 1
    if row.get("rate_type") == "m_x" and "rate_value" in row:
        acc["mx_sum"] += row["rate_value"]; acc["mx_count"] += 1
    if row.get("rate_type") == "life_table_mx_qx":
        if "qx" in row:
            acc["life_qx_sum"] += row["qx"]; acc["life_qx_count"] += 1
        if "mx" in row:
            acc["life_mx_sum"] += row["mx"]; acc["life_mx_count"] += 1
    acc["rate_types"].add(str(row.get("rate_type")))
    acc["populations"].add(str(row.get("population")))
    acc["age_intervals"].add(str(row.get("age_interval")))
    acc["source_sha256"].add(str(row.get("source_sha256")))


def _finish_accumulator(acc):
    return {
        "records": acc["records"],
        "deaths_sum": round(acc["deaths_sum"], 8) if acc["deaths_count"] else None,
        "exposure_sum": round(acc["exposure_sum"], 8) if acc["exposure_count"] else None,
        "calculated_rate_per_100000": round(acc["deaths_sum"] / acc["exposure_sum"] * 100000.0, 8)
            if acc["deaths_count"] and acc["exposure_count"] and acc["exposure_sum"] > 0
            and acc["rate_types"] == {"deaths_per_100000_exposure"} else None,
        "qx_rate_value_mean": round(acc["qx_sum"] / acc["qx_count"], 8) if acc["qx_count"] else None,
        "mx_rate_value_mean": round(acc["mx_sum"] / acc["mx_count"], 8) if acc["mx_count"] else None,
        "life_table_qx_mean": round(acc["life_qx_sum"] / acc["life_qx_count"], 8) if acc["life_qx_count"] else None,
        "life_table_mx_mean": round(acc["life_mx_sum"] / acc["life_mx_count"], 8) if acc["life_mx_count"] else None,
        "rate_types": sorted(acc["rate_types"]),
        "populations": sorted(acc["populations"]),
        "age_intervals": sorted(acc["age_intervals"]),
        "source_sha256": sorted(acc["source_sha256"])
    }


def _iter_stats_file(path):
    if path.name.endswith(".jsonl.gz"):
        with gzip.open(path, "rt", encoding="utf-8") as f:
            for line_no, line in enumerate(f, 1):
                if not line.strip():
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    yield {"_invalid_line": line_no}
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("records", [])
    if isinstance(data, list):
        yield from data


def _sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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
    table_path = root / "MORTALITY_AUDIT" / "mortality_statistics.jsonl.gz"
    if not stat_rows and not table_path.is_file():
        table_path = root / "MORTALITY_AUDIT" / "mortality_statistics.json"
    table_sha = None
    table_error = None
    if stat_rows:
        source_rows = stat_rows
        table_sha = hashlib.sha256(json.dumps(stat_rows, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")).hexdigest()
        table_sha_motivo = "sha256 de las filas estadísticas entregadas en el input (JSON canónico)"
        data_table = "CASE_INPUT"
    elif table_path.is_file():
        source_rows = _iter_stats_file(table_path)
        table_sha = _sha256_file(table_path)
        table_sha_motivo = "sha256 del archivo estadístico original"
        data_table = str(table_path.relative_to(root))
    else:
        source_rows = []
        table_sha = "NO_APLICA_SIN_TABLA"
        table_sha_motivo = ("no existe mortality_statistics.jsonl.gz ni mortality_statistics.json ni filas "
                            "mortality_statistics/mortality_observations en el input; ausencia declarada, no hash inventado")
        data_table = "NO_APLICA_SIN_TABLA"

    by_year = {}
    by_epoch = {}
    accepted_count = 0
    rejected_count = 0
    rejected_samples = []
    for source_row in source_rows:
        if isinstance(source_row, dict) and "_invalid_line" in source_row:
            rejected_count += 1
            if len(rejected_samples) < 20:
                rejected_samples.append({"line": source_row["_invalid_line"], "reason": "INVALID_JSONL"})
            continue
        accepted, rejected = _validate_stats([source_row])
        if rejected:
            rejected_count += len(rejected)
            if len(rejected_samples) < 20:
                rejected_samples.extend(rejected[:20 - len(rejected_samples)])
            continue
        row = accepted[0]
        accepted_count += 1
        year_key = str(row["year"])
        by_year.setdefault(year_key, _new_accumulator())
        _accumulate(by_year[year_key], row)
        epoch = row.get("historical_epoch") or row.get("epoch")
        if epoch:
            epoch_key = str(epoch)
            by_epoch.setdefault(epoch_key, _new_accumulator())
            _accumulate(by_epoch[epoch_key], row)

    stats_by_year = {k: _finish_accumulator(v) for k, v in sorted(by_year.items())}
    stats_by_epoch = {k: _finish_accumulator(v) for k, v in sorted(by_epoch.items())}
    ready = bool(accepted_count) and rejected_count == 0
    status = "STATISTICAL_TABLE_LOADED" if ready else "WIRED_WAITING_VERIFIED_MORTALITY_DATA"
    source_hashes = sorted({h for acc in by_year.values() for h in acc["source_sha256"]})
    return {
        "version": "MATRIZ_MORTALIDAD_Z90_V0_2",
        "status": status,
        "wired_to_active_runner": True,
        "data_table": data_table,
        "data_table_sha256": table_sha,
        "data_table_sha256_motivo": table_sha_motivo,
        "data_table_estado": ("DECLARADO_AUSENTE_SIN_TABLA" if table_sha == "NO_APLICA_SIN_TABLA"
                              else ("ERROR_LECTURA_TABLA" if table_sha is None else "TABLA_HASHEADA")),
        "accepted_statistical_rows": accepted_count,
        "rejected_statistical_rows": rejected_count,
        "rejected_statistical_row_samples": rejected_samples,
        "statistics_by_year": stats_by_year,
        "statistics_by_historical_epoch": stats_by_epoch,
        "narrative_text_fields_scanned": len(text_rows),
        "classified_mortality_events": classified,
        "unresolved_event_count": sum(1 for x in classified for e in x["classification"] if e.get("status") == "TORTUGAS"),
        "verified_rates_required_for_statistical_claims": True,
        "feeds_H": False,
        "can_decide_H": False,
        "changes_canonical_patterns": False,
        "changes_canonical_engine": False,
        "reason": ("Estadísticas agregadas por año/época solo desde filas con dimensiones, tipo de tasa, fuente, fecha y SHA-256 válidos. "
                   "La clasificación textual es observacional y no altera H1/H2. No se generaron tasas ni datos faltantes.")
    }
