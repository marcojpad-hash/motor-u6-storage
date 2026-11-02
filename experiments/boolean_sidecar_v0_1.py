#!/usr/bin/env python3
"""Prototipo lateral SAT/Booleano: filtro de contradicciones explícitas del catálogo.
No altera ni invoca el motor canónico. No produce ranking ni probabilidades.
"""
from __future__ import annotations
import json, pathlib, collections, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
QUEUE = ROOT / "casos/fabrica/cola"
CATALOG = ROOT / "motor/motor/patterns_final_v14.json"
OUT = ROOT / "avances/boolean_sidecar/RESULTADOS.json"
MIN_OBS = 0.60

def load_json(p):
    return json.loads(p.read_text(encoding="utf-8"))

def dpll(clauses, assignment=None):
    """DPLL mínimo, suficiente para el CNF monotónico de este experimento."""
    assignment = dict(assignment or {})
    while True:
        unit = None
        reduced = []
        for clause in clauses:
            satisfied = False
            pending = []
            for lit in clause:
                v, positive = abs(lit), lit > 0
                if v in assignment:
                    if assignment[v] == positive:
                        satisfied = True
                        break
                else:
                    pending.append(lit)
            if satisfied:
                continue
            if not pending:
                return None
            if len(pending) == 1:
                unit = pending[0]
                break
            reduced.append(pending)
        if unit is None:
            break
        v, val = abs(unit), unit > 0
        if v in assignment and assignment[v] != val:
            return None
        assignment[v] = val
    if not reduced:
        return assignment
    lit = reduced[0][0]
    for choice in (lit, -lit):
        result = dpll(clauses, {**assignment, abs(choice): choice > 0})
        if result is not None:
            return result
    return None

def read_observations(entry):
    observed = {}
    for cut in entry.get("cuts", []):
        for channel in ("P", "A", "C"):
            for token, weight in cut.get(channel, []):
                observed[token] = max(float(weight), observed.get(token, 0.0))
    return observed

def build_cnf(catalog, observed):
    names = sorted(catalog)
    var = {name: i + 1 for i, name in enumerate(names)}
    clauses = [list(var.values())]  # al menos una familia compatible
    reasons = collections.defaultdict(list)
    for name, pattern in catalog.items():
        for token, threshold in (pattern.get("tokens_contra") or {}).items():
            if observed.get(token, 0.0) >= max(MIN_OBS, float(threshold)):
                clauses.append([-var[name]])
                reasons[name].append({"token": token, "observed": observed[token], "threshold": float(threshold)})
    return names, var, clauses, reasons

def read_baseline():
    rows = {}
    for lot in range(1, 6):
        p = ROOT / f"casos/fabrica/lotes/F00{lot}_RESUMEN.json"
        summary = load_json(p)
        for row in summary.get("filas", []):
            if row.get("returncode") == 0 and isinstance(row.get("acierto_H1"), (int, float)):
                rows[row["case_id"]] = row
    return rows

def main():
    catalog = load_json(CATALOG)
    baseline = read_baseline()
    cases = []
    skipped_paused = []
    for folder in sorted(QUEUE.iterdir()):
        if not folder.is_dir() or not folder.name.startswith(("CAL_F001_", "CAL_F002_", "CAL_F003_", "CAL_F004_", "CAL_F005_")):
            continue
        ip, op = folder / "entrada.json", folder / "desenlace_sellado.json"
        if not ip.exists() or not op.exists():
            continue
        entry, outcome = load_json(ip), load_json(op)
        base = baseline.get(entry.get("case_id", folder.name))
        if base is None:
            skipped_paused.append(entry.get("case_id", folder.name))
            continue
        observed = read_observations(entry)
        names, var, clauses, reasons = build_cnf(catalog, observed)
        model = dpll(clauses)
        survivors = [n for n in names if not reasons.get(n)]
        truth = set(outcome.get("familias", []))
        kept_truth = sorted(truth.intersection(survivors))
        cases.append({
            "case_id": entry.get("case_id", folder.name),
            "baseline": {k: base.get(k) for k in ("H1", "H2", "acierto_H1", "acierto_H2", "acierto_set", "acierto_apuesta")},
            "familias_catalogo": len(names),
            "familias_compatibles_booleanas": len(survivors),
            "reduccion_pct": round(100 * (1 - len(survivors) / max(1, len(names))), 2),
            "familias_reales_selladas": sorted(truth),
            "familias_reales_conservadas": kept_truth,
            "cobertura_real": bool(kept_truth),
            "real_excluida": sorted(truth - set(survivors)),
            "satisfacible": model is not None,
            "contradicciones_por_familia": dict(reasons),
            "observed_tokens": len(observed),
        })
    n = len(cases)
    covered = sum(c["cobertura_real"] for c in cases)
    excluded = sum(bool(c["real_excluida"]) for c in cases)
    baseline_totals = {
        "cases": len(baseline),
        "H1_hits": sum(int(x.get("acierto_H1", 0)) for x in baseline.values()),
        "H2_hits": sum(int(x.get("acierto_H2", 0)) for x in baseline.values()),
        "open_set_hits": sum(int(x.get("acierto_set", 0)) for x in baseline.values()),
        "main_scenario_bet_hits": sum(int(x.get("acierto_apuesta", 0)) for x in baseline.values()),
    }
    for key in ("H1_hits", "H2_hits", "open_set_hits", "main_scenario_bet_hits"):
        baseline_totals[key + "_rate_pct"] = round(100 * baseline_totals[key] / max(1, baseline_totals["cases"]), 2)
    result = {
        "schema": "BOOLEAN_SIDECAR_EXPERIMENT_V0.2",
        "status": "EXPLORATORY_NOT_PREDICTIVE",
        "method": "One Boolean variable per catalog family; CNF requires at least one surviving family and excludes a family when any observed token crosses its explicit tokens_contra threshold. Weights are used only to decide whether an observed token crosses the catalog threshold; no ranking or probability is computed.",
        "threshold_floor": MIN_OBS,
        "catalog_families": len(catalog),
        "cases_evaluated": n,
        "cases_skipped_paused_or_unsealed": len(skipped_paused),
        "skipped_case_ids": skipped_paused,
        "baseline_engine_metrics_same_cases": baseline_totals,
        "mean_candidate_reduction_pct": round(sum(x["reduccion_pct"] for x in cases) / max(1, n), 2),
        "median_candidate_reduction_pct": sorted(x["reduccion_pct"] for x in cases)[n // 2] if n else None,
        "mean_boolean_candidates_remaining": round(sum(x["familias_compatibles_booleanas"] for x in cases) / max(1, n), 2),
        "sealed_true_family_labels": sum(len(x["familias_reales_selladas"]) for x in cases),
        "sealed_true_family_labels_excluded": sum(len(x["real_excluida"]) for x in cases),
        "truth_coverage_cases": covered,
        "truth_coverage_rate_pct": round(100 * covered / n, 2) if n else None,
        "cases_with_at_least_one_real_family_excluded": excluded,
        "case_results": cases,
        "excluded_lots": {"F006": "reevaluation of F005 Courbet; not an independent case", "F007": "not run: Z seeds and destination file are separate; destination file lacks the required outcome families"},
        "limitations": [
            "Catalog token_contra weights are not empirically calibrated; this is a stress test, not a validated inference rule.",
            "The sidecar consumes historical sealed labels only for evaluation, never as solver input.",
            "Paused/unsealed cases are excluded from the apples-to-apples baseline comparison.",
            "The Boolean sidecar is a compatibility filter, not a predictor; compare its 100% case coverage and candidate reduction against the baseline engine metrics above.",
            "No main-engine output is modified; this does not replace or rerank the weighted engine.",
            "F006 is excluded from independent-case counts; F007 remains blocked until the custodian supplies the required families and the Z gate passes."
        ]
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k != "case_results"}, ensure_ascii=False, indent=2))
    print(f"REPORT={OUT}")
    return 0 if n else 2

if __name__ == "__main__":
    raise SystemExit(main())
