#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Matriz de ablación controlada para las filas ACTIVA_MUDA del registro U6."""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNNER_PATH = ROOT / "motor" / "u6" / "U6_UNIFICADO_EXPERIMENTAL.py"
MOTOR_TO_LAT = {
    "trayectoria_hosteleria": "trayectoria_hosteleria",
    "plugin_metodo_rigor": "plugin_metodo_rigor (alimentado)",
    "plugin_arquetipos_dinamicos": "plugin_arquetipos_dinamicos",
    "plugin_pregunta_dirigida": "plugin_pregunta_dirigida (verificado)",
    "predictor_vecinos_prefijo_v1.py": "predictor_vecinos_prefijo",
    "hub:sombrero_blanco_entrada": "sombrero_blanco_entrada",
    "hub:familias_tokens_puente": "familias_tokens_puente",
    "hub:guardian_entrada_autoevidencia": "guardian_entrada_autoevidencia",
}
MANUAL_ROWS = {"traza_campo_244_dedupe", "plugin_sombrero_blanco_token (declaración)", "n_piezas (verificado)"}

def load_runner():
    spec = importlib.util.spec_from_file_location("u6_unificado_ablation_runner", RUNNER_PATH)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod

def sha_obj(value):
    raw = json.dumps(value, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()

def target_for_row(row):
    piece, source = str(row.get("pieza") or ""), row.get("fuente")
    if piece.startswith("verificado:"):
        return None, "AUDIT_ROW_NOT_INDEPENDENT_COMPONENT"
    if piece in MANUAL_ROWS:
        return None, "MANUAL_CONTROL_OR_DECLARATION"
    if source == "laterales_unico_v1":
        return ("lat_flag", piece), "DIRECT_LAT_FLAG"
    if source == "motor":
        if piece in MOTOR_TO_LAT:
            return ("lat_flag", MOTOR_TO_LAT[piece]), "DUPLICATE_REGISTRY_ROW"
        if piece == "resolucion_operativa_terminal_017":
            return ("consolidado_off", "resolucion"), "CORE_ABLATION_SWITCH"
        if piece == "plugin_guardia_no_cruce.py":
            return None, "ABSORBED_IN_TRANSVERSAL_GUARD"
        if piece == "cameo_to_244_adapter_v1.py":
            return None, "NOT_APPLICABLE_MAPPING_ABSENT"
        if piece == "matriz_clases":
            return None, "STATIC_INVENTORY_ONLY"
        if piece == "plugin_sombrero_blanco_token.py":
            return None, "DECLARATION_DUPLICATE_NOT_EXECUTABLE"
    return None, "NO_INDEPENDENT_SWITCH_IDENTIFIED"

def prediction(result):
    pred = result.get("predictor") or {}
    candidates = pred.get("candidates") or []
    ranks, order = {}, []
    for row in candidates:
        if isinstance(row, dict) and row.get("family"):
            family = str(row["family"])
            order.append(family)
            val = row.get("rank_fusion")
            if isinstance(val, (int, float)):
                ranks[family] = float(val)
    h1, h2 = result.get("H1") or {}, result.get("H2") or {}
    resolution = pred.get("resolution") or {}
    return {
        "H1": h1.get("family") if isinstance(h1, dict) else None,
        "H2": h2.get("family") if isinstance(h2, dict) else None,
        "candidate_order": order, "rank_fusion": ranks, "candidate_count": len(candidates),
        "resolution_status": resolution.get("status") if isinstance(resolution, dict) else None,
        "ablation_off": pred.get("ablation_off") or [],
    }

def compare(base, current):
    a, b = base["prediction"], current["prediction"]
    common = set(a["rank_fusion"]) & set(b["rank_fusion"])
    deltas = {k: round(b["rank_fusion"][k] - a["rank_fusion"][k], 9) for k in sorted(common)}
    return {
        "H_changed": (a["H1"], a["H2"]) != (b["H1"], b["H2"]),
        "candidate_set_changed": set(a["candidate_order"]) != set(b["candidate_order"]),
        "candidate_order_changed": a["candidate_order"] != b["candidate_order"],
        "rank_scores_changed": any(abs(v) > 1e-9 for v in deltas.values()),
        "max_abs_rank_delta": max((abs(v) for v in deltas.values()), default=0.0),
        "rank_deltas": deltas,
    }

def disabled_confirmation(result, kind, value):
    if kind == "lat_flag":
        rows = (result.get("registro_componentes") or {}).get("filas") or []
        matches = [r for r in rows if r.get("pieza") == value]
        return {"confirmed": any(r.get("estado") == "APAGADA_POR_FLAG" for r in matches),
                "rows": [{"pieza": r.get("pieza"), "estado": r.get("estado")} for r in matches[:3]]}
    pred = result.get("predictor") or {}
    off = pred.get("ablation_off") or []
    resolution = pred.get("resolution") or {}
    return {"confirmed": value in off or (value == "resolucion" and resolution.get("status") == "ABLATED"),
            "ablation_off": off, "resolution_status": resolution.get("status")}

def run_case(runner, case_path, case_index):
    baseline_item = runner.ejecutar_caso(case_path, live_search=True, tag=f"ABLBASE{case_index}")
    baseline_report, baseline_result = baseline_item["report"], baseline_item["result"]
    cal = (baseline_result.get("features") or {}).get("caldero_busqueda_arquetipos") or {}
    fixture = ((cal.get("audit") or {}).get("raw_sources_before_self_match") or [])
    receipt = ((cal.get("audit") or {}).get("provider_receipt") or {})
    if not fixture or receipt.get("status") != "EXECUTED":
        raise RuntimeError(f"BASELINE_SEARCH_NOT_FREEZABLE:{case_path}:{receipt}")
    base_pred = prediction(baseline_result)
    base = {
        "case": str(case_path.relative_to(ROOT)), "case_id": baseline_report.get("case_id"),
        "baseline_classification": baseline_report.get("classification"),
        "baseline_search_receipt": {k: receipt.get(k) for k in ("provider", "status", "query_count", "result_count", "query_sha256")},
        "fixture_sources_n": len(fixture), "fixture_sources_sha256": sha_obj(fixture),
        "prediction": base_pred, "canonical_sha256": baseline_report.get("canonical_sha256"),
        "active_muda_rows": baseline_report.get("activa_muda_rows") or [],
        "baseline_ledger_events": baseline_report.get("flow_ledger_events"),
    }
    grouped, row_classifications = {}, []
    for row in base["active_muda_rows"]:
        target, classification = target_for_row(row)
        row_classifications.append({
            "pieza": row.get("pieza"), "fuente": row.get("fuente"), "motivo": row.get("motivo"),
            "classification": classification, "target": list(target) if target else None,
        })
        if target:
            key = target[0] + "::" + target[1]
            grouped.setdefault(key, {"kind": target[0], "value": target[1], "source_rows": []})
            grouped[key]["source_rows"].append({"pieza": row.get("pieza"), "fuente": row.get("fuente")})
    base["row_classifications"] = row_classifications
    results = []
    for i, target in enumerate(grouped.values(), 1):
        kind, value = target["kind"], target["value"]
        original_activate = runner.activar_modo_unificado
        if kind == "lat_flag":
            def activate_one(original=original_activate, flag=value):
                state = original()
                os.environ["LAT_" + flag.upper()] = "0"
                return state
            runner.activar_modo_unificado = activate_one
        try:
            item = runner.ejecutar_caso(
                case_path, live_search=False, tag=f"AB{case_index}_{i:02d}",
                ablation_kind=kind, ablation_value=value, fixture_sources=fixture
            )
        finally:
            runner.activar_modo_unificado = original_activate
        result = item["result"]
        current_pred = prediction(result)
        delta = compare(base, {"prediction": current_pred})
        results.append({
            "target": {"kind": kind, "value": value, "source_rows": target["source_rows"]},
            "classification": item["report"].get("classification"),
            "search_receipt": item["report"].get("live_search_receipt"),
            "disabled_switch_confirmed": disabled_confirmation(result, kind, value),
            "prediction": current_pred, "comparison": delta,
            "critical_errors": item["report"].get("critical_errors"),
            "flow_ledger_events": item["report"].get("flow_ledger_events"),
        })
    return {
        **base, "ablation_targets_total": len(grouped), "ablation_results": results,
        "ablation_targets_not_run": [x for x in row_classifications if x["target"] is None],
    }

def markdown_report(matrix):
    lines = [
        "# U6 — matriz de ablación ACTIVA_MUDA", "",
        "La búsqueda viva se ejecutó una vez por caso. Cada ablación reutilizó exactamente sus fuentes como fixture estático, con stores y ledger aislados.", "",
    ]
    for case in matrix["cases"]:
        lines += [
            f"## {case['case_id']}", "",
            f"- Filas ACTIVA_MUDA: {len(case['active_muda_rows'])}",
            f"- Targets de ablación independientes: {case['ablation_targets_total']}",
            f"- Fuentes congeladas: {case['fixture_sources_n']} (SHA-256 {case['fixture_sources_sha256']})",
            f"- H1/H2 base: {case['prediction']['H1']} / {case['prediction']['H2']}", "",
            "| Componente desactivado | Switch confirmado | H1/H2 cambió | Orden candidatas cambió | Puntajes cambiaron | Máx. Δ rank_fusion |",
            "|---|---:|---:|---:|---:|---:|",
        ]
        for r in case["ablation_results"]:
            c = r["comparison"]
            lines.append(f"| {r['target']['value']} | {'sí' if r['disabled_switch_confirmed']['confirmed'] else 'NO'} | {'sí' if c['H_changed'] else 'no'} | {'sí' if c['candidate_order_changed'] else 'no'} | {'sí' if c['rank_scores_changed'] else 'no'} | {c['max_abs_rank_delta']} |")
        lines += ["", f"Filas sin ablación independiente: {len(case['ablation_targets_not_run'])}. Se detallan en el JSON.", ""]
    return "\n".join(lines) + "\n"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", action="append", required=True)
    ap.add_argument("--output", default="/tmp/U6_ACTIVA_MUDA_ABLATION_MATRIX.json")
    args = ap.parse_args()
    runner = load_runner()
    cases = [run_case(runner, (ROOT / p).resolve(), i) for i, p in enumerate(args.case, 1)]
    totals = {
        "cases": len(cases),
        "active_muda_rows": sum(len(c["active_muda_rows"]) for c in cases),
        "unique_ablation_runs": sum(len(c["ablation_results"]) for c in cases),
        "h_changed": sum(r["comparison"]["H_changed"] for c in cases for r in c["ablation_results"]),
        "candidate_order_changed": sum(r["comparison"]["candidate_order_changed"] for c in cases for r in c["ablation_results"]),
        "rank_scores_changed": sum(r["comparison"]["rank_scores_changed"] for c in cases for r in c["ablation_results"]),
        "unablatable_rows": sum(len(c["ablation_targets_not_run"]) for c in cases),
        "unconfirmed_switches": sum(not r["disabled_switch_confirmed"]["confirmed"] for c in cases for r in c["ablation_results"]),
    }
    matrix = {"version": "U6_ACTIVA_MUDA_ABLATION_MATRIX_20261104_V1",
              "runner_commit": os.environ.get("GITHUB_SHA", "NO_REGISTRADO"),
              "cases": cases, "totals": totals}
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(matrix, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    out.with_suffix(".md").write_text(markdown_report(matrix), encoding="utf-8")
    print("U6_ACTIVA_MUDA_ABLATION_SUMMARY=" + json.dumps(totals, ensure_ascii=False))
    if totals["unconfirmed_switches"]:
        print("ABALATION_SWITCHES_UNCONFIRMED=" + str(totals["unconfirmed_switches"]))

if __name__ == "__main__":
    main()
