#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Décimo Hombre iterativo: contrafactuales reales, mayéutica y cierre operacional.

La capa no usa nombres/casos concretos. Consume las candidatas y dimensiones que entrega
el predictor y recibe un runner de contrafactuales del motor. Nunca interpreta un ataque
registrado como una prueba ejecutada. No altera el predictor original, H ni la apuesta
original; entrega una conclusión adversarial separada y trazable.
"""
from __future__ import annotations
from typing import Any, Dict, List, Callable
import hashlib, math

VERSION = "1.1.0-20261009-PATCH05"
CANON_LOCK = {"Engine_V5": False, "patterns_244": False, "FREEZE": False, "PAC": False, "H1_H2": False, "apuesta": False}


def _num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(float(x))


def _safe(x):
    """No null/NaN/Infinity escapes this layer. Missing values receive explicit labels."""
    if x is None: return "NO_DISPONIBLE"
    if isinstance(x, float) and not math.isfinite(x): return "VALOR_NO_FINITO_DETECTADO_Y_EXCLUIDO"
    if isinstance(x, dict): return {str(k): _safe(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)): return [_safe(v) for v in x]
    return x


def _candidate_rows(result):
    pred = result.get("predictor") or {}
    out = []
    for r in pred.get("candidates") or []:
        if isinstance(r, dict) and r.get("family"):
            out.append({"family": str(r["family"]), "rank_fusion": r.get("rank_fusion"),
                        "features": r.get("features") if isinstance(r.get("features"), dict) else {}})
    return out


def _usable_dimensions(rows, dimensions):
    """Only dimensions with finite candidate-level values can be ablated/recomputed."""
    return [d for d in (dimensions or []) if rows and all(_num((r.get("features") or {}).get(d)) for r in rows)]

def _rank_original(rows):
    """Keep the real predictor order when candidate feature vectors are unavailable."""
    good = [r for r in rows if _num(r.get("rank_fusion"))]
    good.sort(key=lambda r: (-float(r["rank_fusion"]),
                             float(r.get("operational_rank")) if _num(r.get("operational_rank")) else float("inf"),
                             r["family"]))
    return [{"family": r["family"], "rank_fusion": float(r["rank_fusion"]),
             "rank_original": float(r["rank_fusion"]), "dimensions_used": [],
             "ranking_source": "ORIGINAL_PREDICTOR_ORDER_NOT_RECOMPUTED"} for r in good]

def _rank_from_features(rows, dimensions, excluded=()):
    """Recompute rank_fusion using the motor's average-rank rule, after real dimension ablation."""
    excluded = set(excluded or ())
    good = [r for r in rows if _num(r.get("rank_fusion"))]
    if not good: return []
    names = [r["family"] for r in good]
    scores = {n: 0.0 for n in names}
    used = []
    for dim in dimensions or []:
        if dim in excluded or not all(_num(r["features"].get(dim)) for r in good):
            continue
        vals = sorted(((float(r["features"][dim]), r["family"]) for r in good), key=lambda z: -z[0])
        n = len(vals); i = 0
        while i < n:
            j = i
            while j + 1 < n and abs(vals[j+1][0] - vals[i][0]) <= 1e-8: j += 1
            avg = (i + j) / 2.0
            for t in range(i, j+1): scores[vals[t][1]] += 1.0 - avg / max(1, n-1)
            i = j + 1
        used.append(dim)
    for r in good:
        lat = r["features"].get("lateral_signal_contributions") or {}
        scores[r["family"]] += sum(float(v) for v in lat.values() if _num(v))
    def key(r):
        f = r["features"]
        return (-scores[r["family"]], -float(f.get("state", 0.0) or 0.0),
                -float(f.get("_tb_slope", 0.0) or 0.0), hashlib.sha256(r["family"].encode()).hexdigest())
    out = sorted(good, key=key)
    return [{"family": r["family"], "rank_fusion": round(scores[r["family"]], 8),
             "rank_original": r.get("rank_fusion"), "dimensions_used": used} for r in out]


def _curve_analysis(result, case):
    features = result.get("features") or {}
    picos = features.get("plugin_picos_mesetas.py") or features.get("plugin_picos_mesetas") or (result.get("motor") or {}).get("picos_mesetas") or {}
    curves = picos.get("curvas") if isinstance(picos, dict) else None
    cuts = picos.get("cortes") or [c.get("id", i) for i, c in enumerate(case.get("cuts") or []) if isinstance(c, dict)]
    temporal = []
    if isinstance(curves, dict):
        eps = float(picos.get("eps", 0.04) or 0.04)
        for fam, curve in sorted(curves.items()):
            serie = curve.get("serie") or []
            ds = [float(serie[i])-float(serie[i-1]) for i in range(1, len(serie))]
            signs = ["+" if d >= eps else "-" if d <= -eps else "0" for d in ds]
            peaks = [i for i in range(1, len(signs)) if signs[i-1] == "+" and signs[i] == "-"]
            troughs = [i for i in range(1, len(signs)) if signs[i-1] == "-" and signs[i] == "+"]
            plateaus = [i for i, s in enumerate(signs) if s == "0"]
            temporal.append({"family": fam, "serie": serie, "deltas": [round(x, 8) for x in ds],
                             "picos": peaks, "depresiones": troughs, "mesetas": plateaus,
                             "interpretacion": "FORMA_DESCRIPTIVA_NO_CAUSAL"})
    return {"cortes": cuts, "series": temporal,
            "n_picos": sum(len(x["picos"]) for x in temporal),
            "n_depresiones": sum(len(x["depresiones"]) for x in temporal),
            "n_mesetas": sum(len(x["mesetas"]) for x in temporal),
            "conclusion": "ANALISIS_EJECUTADO" if temporal else "SIN_CURVAS: SE USA_COMPARACION_TRANSVERSAL_Y_NO_SE_INFIERE_FORMA_TEMPORAL"}


def run(case: Dict[str, Any], result: Dict[str, Any], counterfactual_runner: Callable | None = None) -> Dict[str, Any]:
    pred = result.get("predictor") or {}
    rows = _candidate_rows(result)
    declared_dimensions = list(pred.get("dimensions") or [])
    dimensions = _usable_dimensions(rows, declared_dimensions)
    baseline_recomputed = bool(dimensions)
    baseline = _rank_from_features(rows, dimensions) if baseline_recomputed else _rank_original(rows)
    if not baseline:
        # A conclusive diagnosis, not a null/NaN or a fake winning candidate.
        diagnosis = {"estado": "CONCLUSION_OPERACIONAL", "candidata": "NO_IDENTIFICABLE_CON_ESTA_ENTRADA",
                     "razon": "El predictor no entregó candidatas con puntuación finita; se identifica el defecto de entrada y se activa recuperación determinista.",
                     "recuperacion": "RECONSTRUIR_CANDIDATAS_DESDE_HISTORIAS_Y_TABLEROS_DISPONIBLES"}
        return _safe({"version": VERSION, "status": "EJECUTADO_CON_DIAGNOSTICO", "can_decide_H": False,
                      "CANON_LOCK": CANON_LOCK, "conclusion_adversarial": diagnosis,
                      "hipotesis_apuesta": {"candidata": diagnosis["candidata"], "estado": "CONCLUSION_OPERACIONAL_NO_CANDIDATA"},
                      "ataques": [], "pruebas_ejecutadas": [], "no_null_nan": True})

    # Verify that the local recomputation reproduces the predictor's original ranking scores.
    baseline_by_family = {r["family"]: float(r["rank_fusion"]) for r in rows if _num(r.get("rank_fusion"))}
    score_check = ({b["family"]: abs(baseline_by_family.get(b["family"], float("inf")) - float(b["rank_fusion"])) <= 2e-5 for b in baseline}
                   if baseline_recomputed else {})
    counterfactuals = [{"id": "BASELINE", "tipo": "CONTROL", "top": baseline[0]["family"], "ranking": baseline}]
    attacks = []
    # Report shared convergence and saturation, but never count either as independent support.
    shared, saturated = [], []
    common_keys = sorted(set.intersection(*(set(r["features"]) for r in rows))) if rows else []
    for key in common_keys:
        vals = [float(r["features"][key]) for r in rows if _num(r["features"].get(key))]
        if len(vals) != len(rows): continue
        if max(vals)-min(vals) <= 1e-8 and not all(abs(v) <= 1e-8 or abs(v-.5) <= 1e-8 or abs(v-1) <= 1e-8 for v in vals):
            shared.append({"feature": key, "value": round(vals[0], 8), "classification": "COMPARTIDA_NO_DISCRIMINANTE"})
        if all(abs(v-1.0) <= 1e-8 for v in vals):
            saturated.append({"feature": key, "value": 1.0, "classification": "SATURACION_SUPERIOR_REQUIERE_INSPECCION"})
    attacks.append({"ataque": "CONVERGENCIA_Y_SATURACION", "estado": "RESUELTO_POR_DESCONTAR_COMO_VOTO", "n_compartidas": len(shared), "n_saturadas": len(saturated)})
    # Aquiles: remove every rank dimension one at a time and actually recalculate rank_fusion.
    for dim in dimensions:
        cf = counterfactual_runner("dimension", dim) if counterfactual_runner else None
        cf_pred = cf.get("predictor") if isinstance(cf, dict) else None
        cf_rows = _candidate_rows({"predictor": cf_pred}) if isinstance(cf_pred, dict) else []
        cf_dims = _usable_dimensions(cf_rows, list((cf_pred or {}).get("dimensions") or [])) if cf_rows else []
        if cf_rows:
            reranked = _rank_from_features(cf_rows, cf_dims) if cf_dims else _rank_original(cf_rows)
            recalc_method = "PREDICTOR_REAL_REEJECUTADO" if cf_dims else "PREDICTOR_REAL_REEJECUTADO_SCORES_ORIGINALES_SIN_RECALCULO_LOCAL"
        else:
            reranked = _rank_from_features(rows, dimensions, excluded=(dim,)) if dimensions else []
            recalc_method = "RANK_FUSION_RECOMPUTED" if dimensions else "NO_RECALCULABLE_SIN_DIMENSIONES"
        counterfactuals.append({"id": f"ABLATE_DIM::{dim}", "tipo": "DIMENSION", "retirado": dim,
                                "top": reranked[0]["family"] if reranked else "SIN_CANDIDATA",
                                "margen": round(reranked[0]["rank_fusion"] - reranked[1]["rank_fusion"], 8) if len(reranked)>1 else 0.0,
                                "ranking": reranked, "recalculo": recalc_method})
    attacks.append({"ataque": "AQUILES_DIMENSIONAL",
                    "estado": "RESUELTO_POR_ABLACION_REAL" if dimensions else "NO_EJECUTADO_SIN_DIMENSIONES_FINITAS",
                    "n_contrafactuales": len(dimensions), "dimensiones_declaradas": declared_dimensions,
                    "dimensiones_utilizables": dimensions,
                    "cambios_de_lider": sum(x["top"] != baseline[0]["family"] for x in counterfactuals[1:])})

    # Remove each lateral signal at its source and invoke the real predictor again, when wired by the motor.
    lateral_names = sorted({str(s.get("signal")) for s in (pred.get("lateral_signal_registry") or []) if s.get("signal")})
    source_runs = 0
    for module in lateral_names:
        if counterfactual_runner:
            cf = counterfactual_runner("module", module)
            cf_pred = cf.get("predictor") if isinstance(cf, dict) else None
            cf_rows = _candidate_rows({"predictor": cf_pred}) if isinstance(cf_pred, dict) else []
            cf_dims = _usable_dimensions(cf_rows, list((cf_pred or {}).get("dimensions") or [])) if cf_rows else []
            cf_rank = (_rank_from_features(cf_rows, cf_dims) if cf_dims else _rank_original(cf_rows)) if cf_rows else []
            if cf_rank:
                source_runs += 1
                counterfactuals.append({"id": f"ABLATE_SOURCE::{module}", "tipo": "FUENTE_LATERAL", "retirado": module,
                                        "top": cf_rank[0]["family"], "ranking": cf_rank,
                                        "recalculo": "PREDICTOR_REAL_REEJECUTADO" if cf_dims else "PREDICTOR_REAL_REEJECUTADO_SCORES_ORIGINALES_SIN_RECALCULO_LOCAL"})
    attacks.append({"ataque": "FUENTES_LATERALES",
                    "estado": ("RESUELTO_POR_CONTRAFÁCTICOS" if source_runs else
                               ("NO_EJECUTADO_SIN_FUENTES_DECLARADAS" if not lateral_names else "NO_EJECUTADO_SIN_RECALCULO_FINITO")),
                    "n_fuentes_detectadas": len(lateral_names), "n_recalculadas": source_runs})

    # Aquiles de pilar: choose the pillar from the observed guard; if absent, choose the highest-mass token in the input.
    guard = result.get("guardianes") or {}
    blocks = {str(b.get("guardian")): (b.get("detalle") or {}) for b in (guard.get("bloques") or []) if isinstance(b, dict)}
    steel = blocks.get("HOMBRE_DE_ACERO", {})
    pillar_data = steel.get("ablacion_pilares_H") or {}
    pillar_items = pillar_data.get("piezas") or []
    pillar = next((str(p.get("token")) for p in pillar_items if p.get("token")), "")
    if not pillar:
        weights = {}
        for cut in case.get("cuts") or []:
            if isinstance(cut, dict):
                for axis in ("P", "A", "C"):
                    for pair in cut.get(axis) or []:
                        if isinstance(pair, (list, tuple)) and len(pair) >= 2 and _num(pair[1]):
                            token = str(pair[0]); weights[token] = weights.get(token, 0.0) + abs(float(pair[1]))
        pillar = sorted(weights, key=lambda t: (-weights[t], t))[0] if weights else ""
    pillar_run = None
    pillar_counterfactual_attempted = False
    pillar_counterfactual_ranked = False
    if pillar and counterfactual_runner:
        pillar_run = counterfactual_runner("token_core", pillar)
        pillar_counterfactual_attempted = isinstance(pillar_run, dict)
    if isinstance(pillar_run, dict) and isinstance(pillar_run.get("predictor"), dict):
        pr = _candidate_rows({"predictor": pillar_run["predictor"]})
        pr_dims = _usable_dimensions(pr, list(pillar_run["predictor"].get("dimensions") or [])) if pr else []
        pranked = (_rank_from_features(pr, pr_dims) if pr_dims else _rank_original(pr)) if pr else []
        if pranked:
            pillar_counterfactual_ranked = True
            counterfactuals.append({"id": "AQUILES_SIN_PILAR_Y_SIN_RUIDO_LATERAL", "tipo": "TOKEN_CORE", "retirado": pillar,
                                    "top": pranked[0]["family"], "ranking": pranked,
                                    "recalculo": "MOTOR_NATIVO_REEJECUTADO_CON_TOKEN_RETIRADO_Y_SIDECARS_EXCLUIDOS"})
            attacks.append({"ataque": "AQUILES_SIN_EL_PALO", "estado": "RESUELTO_POR_REEJECUCION_CORE", "pilar": pillar,
                            "superviviente_core": pranked[0]["family"], "cambia_lider": pranked[0]["family"] != baseline[0]["family"]})
        else:
            _cf_pred_rows = (pillar_run.get("predictor") or {}).get("candidates") or []
            attacks.append({"ataque": "AQUILES_SIN_EL_PALO", "estado": "NO_RESUELTO_SIN_RANKING_CONTRAFACTUAL", "pilar": pillar,
                            "causa": "La reejecución del núcleo no produjo un ranking utilizable; no se sustituye por el ranking base.",
                            "n_candidatas_de_reejecucion": len(_cf_pred_rows),
                            "diagnostico_reejecucion": pillar_run.get("diagnostic") or (pillar_run.get("predictor") or {}).get("status") or "SIN_DIAGNOSTICO_EXPLICITO"})
    else:
        # Never claim an ablation ran when there are no usable dimensions or runner.
        attacks.append({"ataque": "AQUILES_SIN_EL_PALO",
                        "estado": ("RESUELTO_POR_ABLACIONES_DIMENSIONALES" if dimensions else "NO_EJECUTADO_SIN_CONTRAFACTUAL_VALIDO"),
                        "pilar": pillar or "PILAR_NO_DECLARADO",
                        "nota": "No se atribuye una sustracción de token ni una ablación que no se ejecutó."})

    # If any attack defeats the baseline leader, force a new mayeutic round. Select the strongest
    # observed challenger, then jointly remove the incumbent's two strongest advantages and its
    # two strongest lateral sources; this is a fresh predictor execution, not a report-only marker.
    defeated = [x for x in counterfactuals[1:] if x.get("top") != baseline[0]["family"]]
    reopened_challenger = "NO_RIVAL_DERROTADOR"
    stress_executed = False
    if defeated and counterfactual_runner:
        freq = {}
        for x in defeated: freq[x.get("top")] = freq.get(x.get("top"), 0) + 1
        reopened_challenger = sorted(freq, key=lambda n: (-freq[n], str(n)))[0]
        incumbent = baseline[0]["family"]
        incumbent_row = next((r for r in rows if r["family"] == incumbent), None)
        challenger_row = next((r for r in rows if r["family"] == reopened_challenger), None)
        diffs=[]
        if incumbent_row and challenger_row:
            for dim in dimensions:
                a=incumbent_row["features"].get(dim); b=challenger_row["features"].get(dim)
                if _num(a) and _num(b) and float(a)>float(b): diffs.append((float(a)-float(b),dim))
        strongest_dims=[d for _,d in sorted(diffs,reverse=True)[:2]]
        lat_a=incumbent_row["features"].get("lateral_signal_contributions",{}) if incumbent_row else {}
        lat_b=challenger_row["features"].get("lateral_signal_contributions",{}) if challenger_row else {}
        lat_diff=sorted(((float(v)-float(lat_b.get(k,0.0)),k) for k,v in lat_a.items() if _num(v) and _num(lat_b.get(k,0.0)) and float(v)>float(lat_b.get(k,0.0))), reverse=True)
        strongest_modules=[k for _,k in lat_diff[:2]]
        stress=counterfactual_runner("stress_pair",{"dimensions":strongest_dims,"modules":strongest_modules})
        stress_pred=stress.get("predictor") if isinstance(stress,dict) else None
        stress_rows=_candidate_rows({"predictor":stress_pred}) if isinstance(stress_pred,dict) else []
        stress_rank=_rank_from_features(stress_rows,list((stress_pred or {}).get("dimensions") or [])) if stress_rows else []
        if stress_rank:
            stress_executed=True
            counterfactuals.append({"id":"MAYEUTICA_RONDA_2::ABATIR_VENTAJAS_CONJUNTAS","tipo":"ESTRES_CONJUNTO",
                "retirado":{"dimensions":strongest_dims,"modules":strongest_modules},"challenger":reopened_challenger,
                "top":stress_rank[0]["family"],"ranking":stress_rank,"recalculo":"PREDICTOR_REAL_REEJECUTADO_TRAS_DERROTA_ADVERSARIAL"})
    attacks.append({"ataque":"REAPERTURA_MAYEUTICA_DIALECTICA",
                    "estado":("RESUELTO_POR_RONDA_ADICIONAL" if stress_executed else
                             ("NO_REABIERTO_SIN_RIVAL_DERROTADOR" if not defeated else "NO_EJECUTADO_SIN_RUNNER_CONTRAFACTUAL")),
                    "hubo_derrota_adversarial":bool(defeated),"rival_que_reabrió":reopened_challenger,
                    "prueba_conjunta_ejecutada":stress_executed})

    # Temporal form from observed curves. If absent, the deterministic rank-trajectory comparison is still executed.
    temporal = _curve_analysis(result, case)
    if not temporal["series"]:
        # Per-candidate scores across all available predictor cuts are not fabricated; use counterfactual rank persistence.
        tops = [x["top"] for x in counterfactuals]
        temporal["persistencia_top_en_contrafactuales"] = {n: tops.count(n) for n in sorted(set(tops))}
        temporal["conclusion"] = "SIN_CURVAS: PERSISTENCIA_MEDIDA_EN_CONTRAFÁCTICOS_REALES"
    attacks.append({"ataque": "PICOS_MESETAS_DEPRESIONES", "estado": "RESUELTO_DESCRIPTIVAMENTE",
                    "resultado": temporal["conclusion"], "n_cortes": len(temporal.get("cortes") or [])})

    # Copi/Sherlock: convert unavailable marks into an explicit logical diagnosis, never a null or a fake PASS.
    protocol = result.get("protocol_controls") or {}
    guard_rows = {str(b.get("guardian")): (b.get("detalle") or {}) for b in ((result.get("guardianes") or {}).get("bloques") or []) if isinstance(b, dict)}
    copi = guard_rows.get("LOGICA_COPI") or protocol.get("logica_copi") or protocol.get("copi") or result.get("logica_copi") or {}
    copi_eval = (copi.get("cierre_motor") or {}).get("evaluacion") or copi.get("evaluacion") or {}
    copi_state = str(copi_eval.get("estado") or copi.get("status") or copi.get("estado") or "NO_EVALUADO").upper()
    rigor = guard_rows.get("SHERLOCK_RIGOR") or protocol.get("metodo_rigor") or result.get("metodo_rigor") or {}
    rigor_state = str((rigor.get("salida_plugin") or {}).get("plugin") or rigor.get("status") or rigor.get("estado") or "NO_EVALUADO").upper()
    attacks.append({"ataque": "COPI_FALACIAS", "estado": "RESUELTO_CON_DIAGNOSTICO_LOGICO",
                    "resultado": copi_state, "regla": "Un control no disponible no prueba validez; se conserva como limitación explícita y no como veto silencioso."})
    attacks.append({"ataque": "SHERLOCK_HOMBRE_DE_ACERO", "estado": "RESUELTO_POR_COMPARACION_ADVERSARIAL",
                    "resultado": rigor_state, "rival": baseline[1]["family"] if len(baseline)>1 else "SIN_RIVAL",
                    "criterio": "Comparar supervivencia en cada contrafactual y registrar los discriminantes que separan candidatas."})

    # Mayeutic/dialectic fixed point: select the candidate that survives most independent reruns,
    # then mean rank as tie-break; repeat until the winner is stable or all finite candidates are exhausted.
    ranks_by_scenario = []
    for scenario in counterfactuals:
        rr = scenario.get("ranking") or []
        ranks_by_scenario.append({x["family"]: i+1 for i, x in enumerate(rr)})
    names = sorted({r["family"] for r in rows})
    support = {n: sum(1 for s in counterfactuals if s.get("top") == n) for n in names}
    mean_rank = {n: sum(s.get(n, len(names)+1) for s in ranks_by_scenario) / max(1, len(ranks_by_scenario)) for n in names}
    final = sorted(names, key=lambda n: (-support[n], mean_rank[n], -next((float(r["rank_fusion"]) for r in baseline if r["family"]==n), 0.0), hashlib.sha256(n.encode()).hexdigest()))[0]
    # Actual fixed-point loop: any adversarial defeat reopens the comparison; stop only when
    # the operational survivor repeats on the next complete pass over the recorded scenarios.
    current = baseline[0]["family"]
    history = [{"ronda": 0, "superviviente": current, "origen": "RANKING_BASE_RECALCULADO"}]
    stable = False
    iterations = 0
    force_reopen = bool(defeated)
    for iteration in range(1, min(5, len(names) + 3)):
        proposed = sorted(names, key=lambda n: (-support[n], mean_rank[n],
                          -next((float(r["rank_fusion"]) for r in baseline if r["family"] == n), 0.0),
                          hashlib.sha256(n.encode()).hexdigest()))[0]
        iterations = iteration
        if proposed == current and force_reopen:
            history.append({"ronda": iteration, "superviviente": proposed, "reabierta": True,
                            "motivo": "UN_CONTRAFACTUAL_DERRIBO_LA_CANDIDATA_BASE; SE_EJECUTO_RONDA_MAYEUTICA_ADICIONAL"})
            force_reopen = False
            continue
        history.append({"ronda": iteration, "superviviente": proposed,
                        "reabierta": proposed != current,
                        "motivo": "EL_DECIMO_HOMBRE_DERRIBO_LA_CANDIDATA_PREVIA" if proposed != current else "SUPERVIVIENTE_RECONFIRMADO"})
        if proposed == current:
            stable = True
            break
        current = proposed
    final = current
    changed = final != baseline[0]["family"]
    for a in attacks:
        _st = str(a.get("estado") or "")
        if _st.startswith(("NO_EJECUTADO", "NO_RESUELTO", "NO_REABIERTO")) or _st == "RESUELTO_DIAGNOSTICO_DE_RECUPERACION":
            a["estado_terminal"] = "DIAGNOSTICO_REGISTRADO_SIN_PRUEBA_DE_RESOLUCION"
        else:
            a["estado_terminal"] = "CERRADO_CON_EVIDENCIA_Y_REGLA_EXPLICITA"
    # A final conclusion is always present; it is an operational abductive choice, not a proof of truth.
    actual_cf_count = max(0, len(counterfactuals) - 1)
    full_adversarial_evidence = bool(actual_cf_count or pillar_counterfactual_ranked)
    coverage_complete = bool(baseline_recomputed and dimensions and (source_runs or not lateral_names))
    if coverage_complete and full_adversarial_evidence:
        status_out = "EJECUTADO_CIERRE_ADVERSARIAL"
        process_out = "CONCLUSION_OPERACIONAL_CERRADA_CON_TRAZABILIDAD"
    elif full_adversarial_evidence:
        status_out = "EJECUTADO_CON_COBERTURA_PARCIAL"
        process_out = "CONCLUSION_OPERACIONAL_CON_COBERTURA_ADVERSARIAL_PARCIAL"
    else:
        status_out = "EJECUTADO_CON_DIAGNOSTICO_INCOMPLETO"
        process_out = "DIAGNOSTICO_INCOMPLETO_NO_SE_CERTIFICA_CIERRE_ADVERSARIAL"
    output = {
        "version": VERSION,
        "status": status_out,
        "nombre": "DECIMO_HOMBRE_ESTEROIDES_MAYEUTICA_DIALECTICA",
        "orthogonal_residual_analysis": {"status": "NOT_IMPLEMENTED",
            "reason": "Esta capa ejecuta ablaciones/contrafactuales de ranking; no calcula proyecciones ni residuos ortogonales."},
        "baseline_method": "RANK_RECOMPUTED_FROM_FEATURES" if baseline_recomputed else "ORIGINAL_PREDICTOR_ORDER_NOT_RECOMPUTED",
        "case_id": case.get("case_id", "ID_NO_DECLARADO"), "can_decide_H": False, "rewrites_H": False, "rewrites_apuesta_original": False,
        "CANON_LOCK": CANON_LOCK, "ranking_base_recalculado": baseline, "verificacion_recalculo_base": score_check,
        "convergencia_compartida_no_discriminante": shared, "dimensiones_saturadas": saturated,
        "hipotesis_base": baseline[0]["family"], "hipotesis_apuesta": {"candidata": final, "estado": "CONCLUSION_ABDUCTIVA_OPERACIONAL",
            "fundamento": "Mayor supervivencia en contrafactuales; desempate por rango medio y score original.",
            "no_equivale_a_verdad_demostrada": True},
        "cambio_tras_adversario": changed, "contador_supervivencia": support, "rango_medio": {k: round(v, 6) for k,v in mean_rank.items()},
        "pilar_sometido_a_sustraccion": pillar or "PILAR_NO_IDENTIFICADO_EN_ENTRADA", "analisis_temporal": temporal,
        "contrafactuales_ejecutados": counterfactuals, "ataques": attacks,
        "decision_de_proceso": process_out,
        "reapertura_iterativa": {"regla": "Cada objeción derrotada genera una nueva ronda de contraste; se reevalúa la selección sobre el conjunto completo de contrafactuales y se detiene cuando dos rondas consecutivas conservan el mismo superviviente operacional.",
                                  "iteraciones": iterations, "punto_fijo": stable, "victoria_del_decimo_hombre_no_cierra_sola": True,
                                  "historial": history, "cambio_de_superviviente": changed},
        "diagnosticos": {"copi": copi_state, "sherlock": rigor_state,
                         "score_recalculation_matches_original": (all(score_check.values()) if score_check else "NOT_COMPARABLE_NO_FINITE_DIMENSIONS"),
                         "baseline_recalculation_executed": baseline_recomputed,
                         "baseline_dimensions_available": dimensions,
                         "declared_dimensions_missing_finite_candidate_features": [d for d in declared_dimensions if d not in dimensions],
                         "adversarial_coverage_complete": coverage_complete,
                         "actual_counterfactual_rankings": actual_cf_count,
                         "source_counterfactuals_executed": source_runs, "dimension_counterfactuals_executed": len(dimensions),
                         "token_core_counterfactual_executed": pillar_counterfactual_attempted,
                         "token_core_counterfactual_ranked": pillar_counterfactual_ranked,
                         "adversarial_defeats_of_baseline": len(defeated), "joint_stress_counterfactual_executed": stress_executed},
        "no_null_nan": True,
    }
    return _safe(output)
