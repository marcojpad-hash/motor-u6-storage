#!/usr/bin/env python3
"""Thin wrapper (new file; v153_lateral_metrics_v1_1.py untouched) to run the V15.3 lateral
academic metrics on a native V0.9 motor dict. Alimenta_H=NO, writes_H=False.

X reconstruction: native V0.9 annex.traza_P.crudo_P exists but is P-only and 4-decimal rounded;
the Mozart v1_1 recipe X=[P;0;0] does NOT reproduce V0.9 R732 (A and C are populated here), so:
X_t = [P_FULL_244 ; A_FULL_244 ; C_FULL_244] in patterns_final_v14 key order (the order of
the cut dicts). FULL_244 values are rounded to 4 decimals by the native motor, so validation
against recorded R732.dX_norm is approximate (max abs diff reported).
Ricci edges for B(i): from ricci_forman_coocurrencia_v0_1 over P_top5 vivos.
Prospective baselines (prefix-only via prefix_audit): PERSISTENCE and CONSTANT_VELOCITY.
Per-family ranking score = B(i)/sum B (negative-curvature mass share).
Raw B(i) is emitted as [name,value] pairs (not dict keys) so the motor's named-hit bridge only sees the [0,1] share."""
from __future__ import annotations
import hashlib, json
import numpy as np
import v153_lateral_metrics_v1_1 as LM
import ricci_forman_coocurrencia_v0_1 as RF

def reconstruct_X(motor):
    cuts = motor["cuts"]; order = list(cuts[0]["P_FULL_244"].keys())
    X = np.array([[float(c[a + "_FULL_244"][k]) for a in "PAC" for k in order] for c in cuts], float)
    rec = np.linalg.norm(np.diff(X, axis=0), axis=1)
    reg = np.array((motor.get("R732") or {}).get("dX_norm") or [], float)
    annex = motor.get("annex") or {}
    traza_p = annex.get("traza_P")
    if not isinstance(traza_p, dict):
        traza_p = {}
    val = {"source": "cuts[].{P,A,C}_FULL_244 (4-decimal rounded)", "crudo_P_present": bool(traza_p.get("crudo_P")),
           "X_shape": list(X.shape), "max_abs_diff_vs_R732_dX_norm": float(np.max(np.abs(rec - reg))) if len(reg) == len(rec) else None,
           "max_rel_diff": float(np.max(np.abs(rec - reg) / (reg + 1e-12))) if len(reg) == len(rec) else None}
    try:
        cp = traza_p["crudo_P"]
        XP = np.array([[float(cp[k][t]) for k in order] + [0.0] * (2 * len(order)) for t in range(len(cuts))])
        d0 = np.linalg.norm(np.diff(XP, axis=0), axis=1)
        val["mozart_recipe_P00_from_crudo_P_max_abs_diff"] = float(np.max(np.abs(d0 - reg)))
    except Exception as e:
        val["mozart_recipe_P00_from_crudo_P_max_abs_diff"] = f"ERR {type(e).__name__}: {e}"
    return X, val

def baselines(X):
    out = {}
    for name, f, start in (("PERSISTENCE", lambda P: P[-1], 1), ("CONSTANT_VELOCITY", lambda P: P[-1] + (P[-1] - P[-2]), 2)):
        rows = [LM.prefix_audit(X, f, k, predictor_id=name, predictor_version="baseline") for k in range(start, X.shape[0])]
        rl = [r["relative_l2"] for r in rows]
        if not rows:
            out[name] = {"n": 0, "mean_l2": None, "mean_rel_l2": None, "median_rel_l2": None,
                         "future_accessed_during_predict": False, "status": "INSUFFICIENT_ROWS"}
            continue
        out[name] = {"n": len(rows), "mean_l2": float(np.mean([r["error_l2"] for r in rows])), "mean_rel_l2": float(np.mean(rl)), "median_rel_l2": float(np.median(rl)),
                     "future_accessed_during_predict": any(r["future_accessed_during_predict"] for r in rows), "status": "EXECUTED"}
    return out

def correr_motor(motor):
    X, val = reconstruct_X(motor)
    # UNICO 27-sep: dimensión = 3 × len(catálogo cargado) (732 con el v14); no se asume 244.
    LM.N_PATTERNS = X.shape[1] // 3; LM.DIM = X.shape[1]
    val["n_patrones"] = LM.N_PATTERNS
    ric = RF.correr_cuts(motor["cuts"], "motor_run")
    edges = [{"source": a["par"][0], "target": a["par"][1], "weight": a["w"], "ricci_forman": a["Ric_F"]} for a in ric["ricci"]["aristas"]]
    res = LM.run_sidecar(X, edges)
    tr = res["trajectory"]; nm = res["negative_curvature_mass"]
    tot = nm["total_incident_mass"] or 0.0
    h = lambda o: hashlib.sha256(json.dumps(o).encode()).hexdigest()[:16]
    return {"lens": "v153_lateral_metrics_v1_1", "spec": res["spec"], "Alimenta_H": "NO", "writes_H": False,
            "curvature_method": ric.get("curvature_method", "UNSPECIFIED"),
            "forman_ricci_verified": bool(ric.get("forman_ricci_verified", False)),
            "graph_topology": ric.get("graph_topology", "UNSPECIFIED"),
            "curvature_note": ric.get("note_method", "No method note supplied by sidecar."),
            "X_validation": val,
            "trajectory": {k: tr[k] for k in ("delta_norm", "persistence_cosine", "kappa_dir", "kappa_ext", "zero_velocity_count")},
            "negative_curvature_mass": {"total_incident_mass": tot, "node_mass_pairs": [[k, v] for k, v in nm["node_mass"].items()], "n_contributing_edges": len(nm["contributing_edges"])},
            "matrices_sha16": {"pattern_pairwise_distance": h(res["pattern_pairwise_distance"]), "pattern_velocity_cosine": h(res["pattern_velocity_cosine"]), "P_delta_correlation": h(res["P_delta_correlation"])},
            "prospective_baselines": baselines(X),
            "por_familia": {f: {"score": round(v / tot, 6)} for f, v in nm["node_mass"].items()} if tot else {}}

if __name__ == "__main__":
    import sys
    raw = json.load(open(sys.argv[1])); m = raw.get("motor", raw)
    print(json.dumps(correr_motor(m), ensure_ascii=False, indent=1, default=float))
