#!/usr/bin/env python3
"""Medición de ESTABILIDAD de la trayectoria a partir de un RESULT del motor.

Uso:  estabilidad(result_path) -> dict con:
  - R732: dX_norm (media, desv, max), persist_cos (media, min),
    kappa_dir (media, max). Son la señal de estabilidad del motor
    (norma del cambio entre cortes, persistencia del coseno entre
    direcciones consecutivas, cambio de dirección).
  - margen_final_H1H2: rank_fusion(top1) - rank_fusion(top2) del predictor
    (salida_interpretable / conjunto_hipotesis_abiertas). Margen más
    grande = H1 más firme.
  - margen_P_por_corte: por corte, top1 - top2 del tablero P (P_FULL_244)
    del motor. Media y desviación: media alta = margen firme; desviación
    baja = margen estable entre cortes. (No es el margen del predictor
    por corte — el predictor no corre por corte — es el margen del
    tablero P, que es donde vive la hélice.)
  - helice (solo si n_cortes >= 5): PCA a 3 componentes sobre los vectores
    P (244 familias por corte) + ajuste helicoidal descriptivo
    (fit_helix_diagnostic del módulo teseracto). Reporta radio,
    radial_cv (bajo = radio estable), giro_por_paso_deg (mediana del
    cambio de fase por corte), phase_linearity_r2 (cerca de 1 = giro
    regular = trayectoria estable), axial_pitch_r2 y el eje estimado.
    Es DESCRIPTIVO, no una validación física.

La pregunta que responde: ¿la gráfica se vuelve más estable cuando la
pieza se USA (menos saltos, dirección más persistente, margen más firme)?
Si la estabilidad NO cambia o empeora, eso también es un dato.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

# fit_helix_diagnostic vive en el motor (geometría multicapa). Se importa
# desde ahí para no duplicar el mecanismo.
MOTOR = Path(__file__).resolve().parents[2] / "motor" / "motor"
sys.path.insert(0, str(MOTOR / "geometria_multicapa"))
try:
    from teseracto_recursivo_geometria_v0_4 import fit_helix_diagnostic
except Exception:  # pragma: no cover - si no se puede importar, la hélice no se mide
    fit_helix_diagnostic = None


def _media(xs):
    return float(np.mean(xs)) if xs else None


def _desv(xs):
    return float(np.std(xs)) if len(xs) > 1 else 0.0


def _pca3(X):
    """PCA a 3 componentes (centrado, SVD). Devuelve (n_cortes x 3)."""
    X = np.asarray(X, dtype=float)
    Xc = X - X.mean(axis=0)
    _, _, Vt = np.linalg.svd(Xc, full_matrices=False)
    return Xc @ Vt[:3].T


def estabilidad(result_path) -> dict:
    r = json.loads(Path(result_path).read_text(encoding="utf-8"))
    motor = r.get("motor") or {}
    r732 = motor.get("R732") or {}
    dX = [float(x) for x in (r732.get("dX_norm") or [])]
    pc = [float(x) for x in (r732.get("persist_cos") or [])]
    kd = [float(x) for x in (r732.get("kappa_dir") or [])]

    # Margen final H1/H2 (rank_fusion top1 - top2 del predictor).
    # Se toma del predictor.candidates (el ranking completo); el conjunto
    # de hipótesis abiertas puede tener una sola hipótesis y no dar margen.
    cands = ((r.get("predictor") or {}).get("candidates") or [])
    if not cands:
        cands = (((r.get("salida_interpretable") or {}).get("conjunto_hipotesis_abiertas") or {}).get("hipotesis") or [])
    rfs = sorted((float(c.get("rank_fusion", 0.0)) for c in cands if isinstance(c, dict)), reverse=True)
    margen_final = (rfs[0] - rfs[1]) if len(rfs) > 1 else None

    # Margen del tablero P por corte (top1 - top2 de P_FULL_244).
    margenes_p = []
    vectores_p = []
    fams = None
    for c in (motor.get("cuts") or []):
        p = c.get("P_FULL_244") or {}
        if not p:
            continue
        vals = sorted((float(v) for v in p.values()), reverse=True)
        if len(vals) > 1:
            margenes_p.append(vals[0] - vals[1])
        if fams is None:
            fams = sorted(p.keys())
        vectores_p.append([float(p.get(f, 0.0)) for f in fams])
    n_cortes = len(vectores_p)

    helice = None
    if n_cortes >= 5 and fit_helix_diagnostic is not None and vectores_p:
        X3 = _pca3(vectores_p)
        h = fit_helix_diagnostic(X3.tolist())
        if isinstance(h, dict) and h.get("status") == "DESCRIPTIVE_FIT_ONLY":
            giro_deg = math.degrees(float(h.get("phase_step_slope_rad_per_cut", 0.0)))
            helice = {
                "status": h.get("status"),
                "n_cortes": n_cortes,
                "radio": round(float(h.get("radius", 0.0)), 4),
                "radial_cv": round(float(h.get("radial_cv", 0.0)), 4),
                "giro_por_paso_deg": round(giro_deg, 2),
                "phase_linearity_r2": round(float(h.get("phase_linearity_r2", 0.0)), 4),
                "axial_pitch_r2": round(float(h.get("axial_pitch_r2", 0.0)), 4),
                "eje": [round(float(v), 3) for v in (h.get("axis_unit_vector_estimate") or [])],
            }
        else:
            helice = {"status": (h or {}).get("status", "SIN_AJUSTE"), "n_cortes": n_cortes}

    si = r.get("salida_interpretable") or {}
    return {
        "case_id": r.get("case_id"),
        "n_cortes": n_cortes,
        "H1": (si.get("H1") or {}).get("familia"),
        "H2": (si.get("H2") or {}).get("familia"),
        "dX_norm": {"media": _media(dX), "desv": _desv(dX), "max": max(dX) if dX else None,
                    "valores": [round(x, 4) for x in dX]},
        "persist_cos": {"media": _media(pc), "min": min(pc) if pc else None,
                        "valores": [round(x, 4) for x in pc]},
        "kappa_dir": {"media": _media(kd), "max": max(kd) if kd else None,
                      "valores": [round(x, 4) for x in kd]},
        "margen_final_H1H2": round(margen_final, 4) if margen_final is not None else None,
        "margen_P_por_corte": {"media": _media(margenes_p), "desv": _desv(margenes_p),
                               "valores": [round(x, 4) for x in margenes_p]},
        "helice": helice,
    }


if __name__ == "__main__":
    print(json.dumps(estabilidad(sys.argv[1]), ensure_ascii=False, indent=1))
