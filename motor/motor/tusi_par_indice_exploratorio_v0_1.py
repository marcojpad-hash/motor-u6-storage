#!/usr/bin/env python3
"""tusi_par_indice_exploratorio_v0_1.py — PROPUESTA / EXPLORATORIO. Alimenta_H=NO. writes_H=False.
Adaptación del par de Tusi sobre las fases del billar circular v0.1 (misma fórmula, sin modificar el módulo):
  cada familia = punto en círculo unidad, phi_t = phi_{t-1} + 2*pi*dp_t (dp=0 si falta p).
  Par de Tusi: dos movimientos circulares contrarrotantes (omega_a = -omega_b) => punto medio
  m = (z_a+z_b)/2 = cos((phi_a-phi_b)/2) * e^{i(phi_a+phi_b)/2} se mueve sobre una RECTA (eje fijo phi_a+phi_b).
Índice por par (solo pasos con ambos p vivos):
  tusi = 1 - |sum(w_a + w_b)| / sum(|w_a|+|w_b|)   (1 = contrarrotación perfecta -> movimiento rectilíneo;
                                                    0 = co-rotación -> giro conjunto, sin recta)
  n_pasos_vivos = pasos con ambos dp definidos. Nulo: permutación de dp (semilla fija) -> z.
Lee RESULT_G_E_* (solo lectura) e importa billar v0.1 del run dir para extraer series."""
import json, sys, random
from pathlib import Path
from math import pi
RUN = Path(sys.argv[1]); sys.path.insert(0, str(RUN / "lentes_billar_ricci_outputs"))
import billar_circular_convergencia_v0_1 as V1
import billar_circular_convergencia_v0_2 as V2

def dps(s):
    return [None if (a is None or b is None) else (b - a) for a, b in zip(s, s[1:])]

def tusi(da, db):
    pares = [(x, y) for x, y in zip(da, db) if x is not None and y is not None and (x != 0 or y != 0)]
    if len(pares) < 2: return None, len(pares)
    num = abs(sum(2*pi*(x+y) for x, y in pares)); den = sum(2*pi*(abs(x)+abs(y)) for x, y in pares)
    return (1 - num/den if den else None), len(pares)

out = {}
for caso in (sys.argv[2].split(",") if len(sys.argv) > 2 else ["0926", "0924", "CAL"]):
    cuts = V2.cuts_from(RUN / f"RESULT_G_E_V0163_D_lentes_{caso}.json")
    ids, series = V1.extraer_series_p(cuts)
    D = {f: dps(series[f]) for f in series}
    fams = sorted(series); rng = random.Random(20260921); filas = []
    for i, a in enumerate(fams):
        for b in fams[i+1:]:
            t, n = tusi(D[a], D[b])
            if t is None: continue
            nul = []
            for _ in range(200):
                db = D[b][:]; rng.shuffle(db); tn, _n = tusi(D[a], db)
                if tn is not None: nul.append(tn)
            mu = sum(nul)/len(nul) if nul else None
            sd = (sum((x-mu)**2 for x in nul)/len(nul))**0.5 if nul else None
            z = (t-mu)/sd if sd else None
            filas.append({"par": [a, b], "tusi": round(t, 4), "n_pasos_vivos": n,
                          "z_vs_nulo": None if z is None else round(z, 3)})
    filas.sort(key=lambda r: -r["tusi"])
    out[caso] = filas
print(json.dumps(out, ensure_ascii=False, indent=1))
