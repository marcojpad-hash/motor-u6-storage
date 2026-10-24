#!/usr/bin/env python3
"""billar_circular_convergencia_v0_2.py  (corte 2 fix over v0.1; v0.1 file untouched)

Lateral. Alimenta_H = NO. No toca Engine_V5 / 244 / FREEZE / H.
Same phi0 (sha256(name) first 8 hex = digest()[:4]), same omega, same order, same TAU,
same null (permute observed p per family, seed 20260921, R=40) as v0.1.

FIX corte 2: a pair (i,j) at cut t is NOT evaluable (excluded, counted neither for nor
against) if p_i(t) is None AND p_j(t) is None ("par fantasma": both absent from Top5).
Rule for exactly ONE absent: pair IS counted (per SPEC corte 2); the absent family keeps
its frozen phase (omega=0), which is documented in output as 'one_empty_rule'.
Also reported (corte 3 diagnostic, not applied): count of convergences where both are
present AND vivos (p != 0.5).
"""
from __future__ import annotations
import hashlib, json
from pathlib import Path
from typing import Any, Dict, List
import numpy as np
import billar_circular_convergencia_v0_1 as V1

VERSION = "billar_circular_v0_2_corte2"
ALIMENTA_H = "NO"
TAU = V1.TAU
SEED_NULO = V1.SEED_NULO
ONE_EMPTY_RULE = "COUNTED: one p=None and other present -> pair evaluated; absent family phase frozen (omega=0)."

def _vivo(p): return p is not None and abs(float(p) - 0.5) > 1e-9

def convergencias_v2(tray, ids, tau=TAU):
    names = list(tray); ev = []; excl = 0; both_vivo = 0; one_empty = 0
    for t in range(len(ids)):
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                a, b = names[i], names[j]
                pa, pb = tray[a]["p"][t], tray[b]["p"][t]
                if pa is None and pb is None:
                    d = float(np.linalg.norm(np.array(tray[a]["z"][t]) - np.array(tray[b]["z"][t])))
                    if d <= tau: excl += 1          # would have counted in v0.1
                    continue
                d = float(np.linalg.norm(np.array(tray[a]["z"][t]) - np.array(tray[b]["z"][t])))
                if d <= tau:
                    oe = (pa is None) != (pb is None); one_empty += int(oe)
                    bv = _vivo(pa) and _vivo(pb); both_vivo += int(bv)
                    ev.append({"corte": ids[t], "t": t, "familias": [a, b], "distancia": round(d, 6),
                               "p_en_corte": {a: pa, b: pb}, "one_empty": oe, "both_present_vivo": bv})
    return ev, {"excluded_both_empty_convergences": excl, "one_empty_counted": one_empty, "both_present_vivo": both_vivo}

def control_nulo_v2(series, ids, n_rep=40):
    rng = np.random.default_rng(SEED_NULO)
    n_real = len(convergencias_v2(V1.trayectorias(series), ids)[0]); cuentas = []
    for _ in range(n_rep):
        mez = {}
        for nom, ps in series.items():
            vals = [x for x in ps if x is not None]
            if len(vals) < 2: mez[nom] = list(ps); continue
            it = iter(list(rng.permutation(vals)))
            mez[nom] = [next(it) if x is not None else None for x in ps]
        cuentas.append(len(convergencias_v2(V1.trayectorias(mez), ids)[0]))
    arr = np.array(cuentas, float)
    return {"n_rep": n_rep, "semilla": SEED_NULO, "n_conv_real": n_real,
            "n_conv_nulo_media": round(float(arr.mean()), 4), "n_conv_nulo_std": round(float(arr.std()), 4),
            "n_conv_nulo_min": int(arr.min()), "n_conv_nulo_max": int(arr.max()),
            "z_score": round(float((n_real - arr.mean()) / (arr.std() + 1e-9)), 4)}

def correr_cuts(cuts, etiqueta="caso"):
    ids, series = V1.extraer_series_p(cuts)
    tray = V1.trayectorias(series)
    v1_ev = V1.convergencias(tray, ids); v1_null = V1.control_nulo(series, ids)
    ev, diag = convergencias_v2(tray, ids); nul = control_nulo_v2(series, ids)
    phi0 = {n: round(V1._phi0(n), 9) for n in series}
    phi0_digest4 = {n: round(int.from_bytes(hashlib.sha256(n.encode()).digest()[:4], "big") / 2**32 * 2 * np.pi, 9) for n in series}
    return {"version": VERSION, "caso": etiqueta, "cortes": ids, "orden": "array order (no reorder by id)",
            "familias": list(series), "tau": TAU, "one_empty_rule": ONE_EMPTY_RULE,
            "phi0": phi0, "phi0_equals_digest4": phi0 == phi0_digest4,
            "v0_1": {"N_real": len(v1_ev), "null": v1_null},
            "v0_2": {"N_real": len(ev), "null": nul, **diag},
            "convergencias_v0_2": ev, "H1": None, "H2": None, "Alimenta_H": ALIMENTA_H,
            "TOCA_Engine_V5": "NO", "TOCA_244": "NO", "TOCA_FREEZE": "NO", "TOCA_H": "NO"}

def cuts_from(path):
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return raw.get("cuts") if raw.get("cuts") and "P_top5_ANEXO" in raw["cuts"][0] else raw["motor"]["cuts"]

if __name__ == "__main__":
    import sys
    out = correr_cuts(cuts_from(sys.argv[1]), sys.argv[2] if len(sys.argv) > 2 else Path(sys.argv[1]).stem)
    print(json.dumps(out, ensure_ascii=False, indent=1))
