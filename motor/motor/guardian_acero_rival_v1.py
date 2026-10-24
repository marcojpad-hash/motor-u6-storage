#!/usr/bin/env python3
"""guardian_acero_rival_v1.py — HOMBRE DE ACERO sobre el rival · 2026-09-27

Qué existía: sidecar_ablacion_hombre_acero.py v0.1 (7db774c0, en
CHECKPOINT_REPRODUCIBLE_20260920.zip) = ablación de los pilares de H (quitar su evidencia más
fuerte). No construía la mejor versión del rival. caldero_zoomout_acero_v0_1.py (aef32944, ya
cableado en el consolidado) es un proxy de zoom-out sobre traza_P, no un steelman.
Este módulo añade la parte que faltaba: construir la MEJOR versión del candidato rival y medir
si el top1 sobrevive. Regla fija, escrita antes de correr:

  1) Base: se recalcula la fusión por rangos (mismo método del motor: rango fraccional con
     empates promediados + lateral_contribution) SOLO entre los candidatos publicados (top10),
     sobre las dimensiones que el motor usó.
  2) Acero del rival R (la mejor versión honesta de R): cada dimensión donde R pierde contra
     el top1 por menos de la banda de empate (10% del rango de esa dimensión entre los top10)
     se resuelve a favor de R (R toma el valor del top1).
  3) Veredicto (sobre el acero del paso 2): SOBREVIVE si top1 sigue arriba por más de EPS;
     NO_RESUELTO si |dif| <= EPS; CAE si R queda arriba. EPS = 0.25 puntos de rango.
  4) Sensibilidad aparte (no decide el veredicto): además se retira el pilar del top1 (su
     mayor ventaja de rango sobre R) y se informa si con eso cae ("cae_si_ademas_se_quita_pilar").
     Calibración 1.0.1: en la 1.0.0 el pilar entraba en el veredicto (mezclaba steelman con
     ablación) y marcaba 12/14 corridas de los 7 casos, aciertos incluidos. La ablación de
     pilares ya la hace el sidecar v0.1 por separado.

Solo mide. can_decide_H=False: no reordena, no escribe H ni patterns.
"""
from __future__ import annotations
from typing import Any, Dict, List, Sequence

VERSION = "1.0.1-20260927"
BANDA_EMPATE_REL = 0.10
EPS = 0.25
TIE_EPS = 1e-9


def _frac(vals: Dict[str, float]) -> Dict[str, float]:
    orden = sorted(vals.items(), key=lambda z: -z[1])
    N = len(orden); out = {}; i = 0
    while i < N:
        j = i
        while j + 1 < N and abs(orden[j + 1][1] - orden[i][1]) <= TIE_EPS:
            j += 1
        avg = (i + j) / 2.0
        for t in range(i, j + 1):
            out[orden[t][0]] = 1.0 - avg / max(1, N - 1)
        i = j + 1
    return out


def _fusion(feats: Dict[str, Dict[str, float]], dims: Sequence[str]) -> Dict[str, float]:
    tot = {n: float(f.get("lateral_contribution", 0.0) or 0.0) for n, f in feats.items()}
    for k in dims:
        sc = _frac({n: float(f.get(k, 0.0) or 0.0) for n, f in feats.items()})
        for n in tot:
            tot[n] += sc[n]
    return tot


def acero_rival(pred: Dict[str, Any], rivales_max: int = 3, extra_rivales: Sequence[str] = ()) -> Dict[str, Any]:
    cands = pred.get("candidates") or []
    dims = [d for d in (pred.get("dimensions") or []) if d != "lateral_contribution"]
    if len(cands) < 2 or not dims:
        return {"estado": "NO_APLICA", "motivo": "menos_de_2_candidatos_o_sin_dimensiones", "pruebas": []}
    feats = {c["family"]: {k: v for k, v in (c.get("features") or {}).items() if isinstance(v, (int, float))} for c in cands}
    top1 = cands[0]["family"]
    base = _fusion(feats, dims)
    orden_base = sorted(base, key=lambda n: -base[n])
    rivales = [c["family"] for c in cands[1:1 + rivales_max]]
    for r in extra_rivales:
        if r in feats and r != top1 and r not in rivales:
            rivales.append(r)
    pruebas = []
    for R in rivales:
        rng = {k: (max(f.get(k, 0.0) for f in feats.values()) - min(f.get(k, 0.0) for f in feats.values())) for k in dims}
        fav = []
        fR = dict(feats[R])
        for k in dims:
            d = feats[top1].get(k, 0.0) - fR.get(k, 0.0)
            if 0 < d <= BANDA_EMPATE_REL * rng[k]:
                fR[k] = feats[top1].get(k, 0.0); fav.append(k)
        # pilar del top1 = dimensión con mayor ventaja de rango sobre R (en la base)
        ventaja = {}
        for k in dims:
            sc = _frac({n: float(f.get(k, 0.0) or 0.0) for n, f in feats.items()})
            ventaja[k] = sc[top1] - sc[R]
        pilar = max(ventaja, key=lambda k: ventaja[k])
        feats_acero = dict(feats); feats_acero[R] = fR
        fus = _fusion(feats_acero, dims)
        dif = fus[top1] - fus[R]
        veredicto = "SOBREVIVE" if dif > EPS else ("NO_RESUELTO" if abs(dif) <= EPS else "CAE")
        fus_p = _fusion(feats_acero, [k for k in dims if k != pilar])
        dif_p = fus_p[top1] - fus_p[R]
        pruebas.append({"rival": R, "dif_base": round(base[top1] - base[R], 6), "dif_acero": round(dif, 6),
                        "dimensiones_empate_a_favor_del_rival": fav, "veredicto_top1": veredicto,
                        "orden_acero_top3": sorted(fus, key=lambda n: -fus[n])[:3],
                        "sensibilidad_pilar": {"pilar_top1": pilar, "ventaja_pilar": round(ventaja[pilar], 6),
                                               "dif_sin_pilar": round(dif_p, 6), "cae_si_ademas_se_quita_pilar": dif_p < -EPS}})
    return {"estado": "EJECUTADO", "top1": top1, "orden_base_recalculado_top3": orden_base[:3],
            "base_coincide_con_motor": orden_base[0] == top1, "pruebas": pruebas,
            "regla": "acero = empates<=10% rango a favor del rival; EPS=0.25; pilar solo como sensibilidad"}


def evidencia_pilares_H(case: Dict[str, Any], pred: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Piezas de evidencia del top1 para la ablación original (sidecar v0.1): sus tokens a favor
    presentes en los cortes, con cortes, eje y persistencia consecutiva."""
    cands = pred.get("candidates") or []
    if not cands:
        return []
    top1 = cands[0]["family"]
    own = ((pred.get("own_evidence") or {}).get(top1) or {})
    favor = list(own.get("favor_tokens") or [])
    cuts = case.get("cuts") or []
    piezas = []
    for i, tok in enumerate(favor):
        cortes, ejes = [], set()
        for c in cuts:
            for eje in ("P", "A", "C"):
                if tok in {str(t) for t, _ in (c.get(eje) or [])}:
                    cortes.append(str(c.get("id"))); ejes.add(eje)
        idx = [k for k, c in enumerate(cuts) if str(c.get("id")) in set(cortes)]
        consec = best = 0; prev = None
        for k in idx:
            consec = consec + 1 if prev is not None and k == prev + 1 else 1
            best = max(best, consec); prev = k
        piezas.append({"id": f"E{i + 1}", "token": tok, "axis": sorted(ejes)[0] if ejes else "", "cuts": cortes,
                       "consec": best, "lenses": sorted(ejes)})
    return piezas
