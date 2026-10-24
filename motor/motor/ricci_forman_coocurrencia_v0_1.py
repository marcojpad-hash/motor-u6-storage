#!/usr/bin/env python3
"""Ricci-Forman sobre coocurrencia de tokens P entre cortes consecutivos.
Un solo archivo. Alimenta_H=NO.
"""
from __future__ import annotations
import math
from typing import Any, Dict, List

def _tanh(x: float) -> float:
    return math.tanh(x)

def _pairs_P(cut: Dict[str, Any]) -> List[tuple]:
    """Motor UNICO cuts expose P_top5_ANEXO / P_candidatos_0a3, not raw P.
    Accept legacy P=[(tok,w),...] and annex forms so the lens feeds fusion."""
    raw = cut.get("P")
    if not raw:
        raw = cut.get("P_top5_ANEXO") or cut.get("P_candidatos_0a3") or []
    out = []
    for item in raw:
        if isinstance(item, (list, tuple)) and len(item) >= 2:
            out.append((item[0], float(item[1])))
        elif isinstance(item, dict):
            tok = item.get("token") or item.get("familia") or item.get("family")
            w = item.get("p") or item.get("w") or item.get("peso") or item.get("score")
            if tok is not None and w is not None:
                out.append((tok, float(w)))
    return out


# PATCH 010a: nulo real por permutación, misma política de semilla que billar_circular_convergencia_v0_2
# (SEED_NULO=20260921, n_rep=40, numpy default_rng) -> determinista.
SEED_NULO = 20260921
N_REP_NULO = 40


def _media_ricci(cuts: List[Dict[str, Any]]) -> float | None:
    """Misma cuenta que correr_cuts (media de Ric_F por arista), sin construir aristas."""
    tot, n = 0.0, 0
    for a, b in zip(cuts, cuts[1:]):
        pa = _pairs_P(a)
        pb = _pairs_P(b)
        if not pa or not pb:
            continue
        base = sum(w for _, w in pa) / len(pa)
        local = sum(w for _, w in pb) / len(pb)
        curv = _tanh(local - base)
        k = len(pa) * len(pb)
        tot += curv * k
        n += k
    return (tot / n) if n else None


def _nulo_permutacion(cuts: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Nulo: se baraja el ORDEN de los cortes (se conservan los P de cada corte) y se recalcula la media.
    Pregunta que contesta: ¿la curvatura media observada depende del orden temporal o sale igual al azar?"""
    import numpy as np
    rng = np.random.default_rng(SEED_NULO)
    idx = list(range(len(cuts)))
    medias = []
    for _ in range(N_REP_NULO):
        perm = rng.permutation(idx)
        m = _media_ricci([cuts[i] for i in perm])
        if m is not None:
            medias.append(m)
    if len(medias) < 2:
        return {"tipo": "permutacion_orden_cortes", "n_rep": N_REP_NULO, "semilla": SEED_NULO, "n_validas": len(medias),
                "media": None, "sd": None, "motivo": "menos de 2 réplicas válidas (cortes sin P)"}
    mu = float(np.mean(medias)); sd = float(np.std(medias))
    return {"tipo": "permutacion_orden_cortes", "n_rep": N_REP_NULO, "semilla": SEED_NULO, "n_validas": len(medias),
            "media": round(mu, 6), "sd": round(sd, 6), "min": round(float(min(medias)), 6), "max": round(float(max(medias)), 6)}


def correr_cuts(cuts: List[Dict[str, Any]], _tag: str = "") -> Dict[str, Any]:
    flujo = {}
    aristas = []
    vivas = set()
    for a, b in zip(cuts, cuts[1:]):
        pa = _pairs_P(a)
        pb = _pairs_P(b)
        if not pa or not pb:
            continue
        wa = [float(w) for _, w in pa]
        wb = [float(w) for _, w in pb]
        base = sum(wa) / len(wa)
        local = sum(wb) / len(wb)
        curv = _tanh(local - base)
        absc = _tanh(abs(local - base))
        for x, _ in pa:
            for y, _ in pb:
                k = f"{x}|{y}"
                flujo[k] = flujo.get(k, 0.0) + abs(curv)
                # Dual schema: legacy a/b/ricci_forman + negativo/lateral_metrics par/Ric_F/w
                aristas.append({
                    "a": x, "b": y, "par": [x, y],
                    "ricci_forman": curv, "Ric_F": curv,
                    "abs": absc, "w": abs(curv),
                })
                vivas.add(x); vivas.add(y)
    vals = [x["ricci_forman"] for x in aristas]
    media = sum(vals) / len(vals) if vals else 0.0
    nulo = _nulo_permutacion(cuts)
    if nulo["sd"] is None or not vals:
        z = None
    elif nulo["sd"] <= 1e-12:
        z = 0.0  # nulo degenerado: toda permutación da la misma media -> sin señal vs nulo
    else:
        z = round((media - nulo["media"]) / (nulo["sd"] + 1e-9), 4)
    return {
        "gamma": 1.0,
        "curvature_method": "TEMPORAL_WEIGHT_DRIFT_PROXY_NOT_EXACT_FORMAN",
        "forman_ricci_verified": False,
        "graph_topology": "IMPLICIT_CROSS_PRODUCT_BETWEEN_CONSECUTIVE_P_CANDIDATES",
        "note_method": "This sidecar computes tanh(mean_weight_delta) and a permutation-order null; it does not implement the weighted Forman edge-curvature formula.",
        "flujo_un_paso_w": flujo,
        "nulo": nulo,
        "z_media_Ric": z,
        "media_cruda_Ric": media,
        "nota_z": "PATCH 010a: z real contra nulo de permutación del orden de cortes (antes z_media_Ric = media cruda con nulo fijo 0/1)",
        "familias_vivas": sorted(vivas),
        "ricci": {"media": media, "aristas": sorted(aristas, key=lambda z: -z["abs"])},
    }
