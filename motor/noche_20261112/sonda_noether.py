#!/usr/bin/env python3
"""Sonda helicoidal v2 aplicada a Noether (7 cortes, corrida fresca 2026-11-12).

Mismo protocolo que la v2: PCA + eje inferido ajustados SOLO con C1..C6
(ciego), C7 proyectado sin reajustar. Margen de radio del prefijo vs
radio real de C7. La C7 es el corte Z (1932); el desenlace sellado es:
HIT (H1 mentor > H2 gobernante), expulsion 1933, muere 1935.
"""
import json, math
from pathlib import Path
import numpy as np
import sys
sys.path.insert(0, "/home/hatch/workspace/u6-alterno")
from sonda_helicoidal_v2 import tableros_p, helice_coords, ajuste_eje, predecir

R = Path("/home/hatch/workspace/u6-alterno/motor-cameo/motor/runs/ESTANDAR__NOETHER_CIEGO_Z90_20261112/_PRIMARY_RESULT.json")
fams, X = tableros_p(R)
n = X.shape[0]
pref, test = X[:n - 1], X[n - 1:n]
mu = pref.mean(axis=0)
U, S, Vt = np.linalg.svd(pref - mu, full_matrices=False)
Zp = (pref - mu) @ Vt.T[:, :3]
Zt = (test - mu) @ Vt.T[:, :3]
sd = Zp.std(axis=0)
sd[sd < 1e-12] = 1.0
Wp, Wt = Zp / sd, Zt / sd
muw = Wp.mean(axis=0)
Wpc, Wtc = Wp - muw, Wt - muw
u, cv, giran = ajuste_eje(Wpc)
hp, rp, phip, *_ = helice_coords(Wpc, u)
ht, rt, phit, *_ = helice_coords(Wtc, u)
margen = (float(rp.min()), float(rp.max()))
# Angulo del eje respecto al PC1.
ang = math.degrees(math.acos(min(1.0, abs(float(u[0])))))
dphi = np.diff(np.unwrap(phip))
pred = predecir(hp, rp, phip)
print("Noether (7 cortes; prefijo C1..C6, test C7=Z1932)")
print(f"  eje inclinado {ang:.1f}° respecto al PC1 | CV radio {cv:.3f} | gira: {giran}")
print(f"  radio prefijo: {[round(float(x), 3) for x in rp]} | margen [{margen[0]:.3f}, {margen[1]:.3f}]")
print(f"  radio real C7: {float(rt[0]):.3f} -> {'ROMPE el margen (fuera)' if not (margen[0] <= float(rt[0]) <= margen[1]) else 'DENTRO del margen'}")
print(f"  fase por paso (prefijo): {[round(float(np.degrees(x)), 1) for x in dphi]} | mediana {round(float(np.degrees(np.median(dphi))), 1)}°")
print(f"  fase C7: {round(float(np.degrees(phit[0])), 1)}° | avance h prefijo: {[round(float(x), 3) for x in hp]} | h C7: {round(float(ht[0]), 3)}")
print(f"  predicho C7 (mediana del paso): h={pred[0]:.3f} r={pred[1]:.3f} | real: h={float(ht[0]):.3f} r={float(rt[0]):.3f}")
print(f"  dX (motor): {[round(float(x), 3) for x in json.load(open(R))['motor']['R732']['dX_norm']]}")
json.dump({"eje_grados_pc1": round(ang, 1), "cv_radio": round(cv, 3),
           "margen_radio": [round(margen[0], 3), round(margen[1], 3)],
           "radio_real_C7": round(float(rt[0]), 3),
           "rompe_margen": not (margen[0] <= float(rt[0]) <= margen[1]),
           "fase_mediana_prefijo_grados": round(float(np.degrees(np.median(dphi))), 1),
           "fase_C7_grados": round(float(np.degrees(phit[0])), 1),
           "h_C7": round(float(ht[0]), 3), "h_predicho": round(pred[0], 3),
           "r_predicho": round(pred[1], 3)},
          open("/home/hatch/workspace/u6-alterno/sonda_noether_reporte.json", "w"), ensure_ascii=False, indent=2)
