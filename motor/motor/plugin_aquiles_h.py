#!/usr/bin/env python3
"""PLUGIN_AQUILES_H — capa plugin. NO modifica Engine_V5.

Busca N_min: el menor n donde p_H ya no se voltea
si sigues remuestreando LA MISMA foto.

No hay N oficial (400, 3200, un millón). Eso es sesgo.
Hay un fusible de recursos (N_FUSIBLE). Si lo tocas,
no encontraste N_min: reportas NO_ENCONTRADO, no “N=fusible”.

estado_H: PARA_DE_EMPUJAR_H | SEGUIR_EMPUJANDO_H | NO_ENCONTRADO_FUSIBLE
estado_traza: ABIERTA siempre — el eje quieto no cierra AB/BC.
"""
from __future__ import annotations

from collections import Counter
from typing import Any, Callable, Dict, List, Sequence

EPS_2PT = 0.02
M_VENTANAS = 3
# I = intensidad residual de la foto (masa que no es ruido puro).
# Si la replica no manda I, se usa I_FLOOR. Nunca 0: un tablero
# vacio no cuenta como "H ya es H". No es p_azar (eso es MC1).
I_FLOOR = 0.02
N0 = 32
FACTOR = 2
N_FUSIBLE = 8192


def _overlap(a: Sequence[str], b: Sequence[str]) -> float:
    if not a and not b:
        return 1.0
    sa, sb = set(a), set(b)
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / max(len(sa), len(sb))


def evaluar_serie(
    puntos: List[Dict[str, Any]],
    eps_p: float = EPS_2PT,
    m: int = M_VENTANAS,
) -> Dict[str, Any]:
    if len(puntos) < 2:
        return {
            "estado_H": "SEGUIR_EMPUJANDO_H",
            "estado": "SEGUIR_EMPUJANDO_H",
            "estado_traza": "ABIERTA",
            "N_min": None,
            "plugin": "PLUGIN_AQUILES_H",
        }

    estables = 0
    n_min = None
    hist = []
    for i in range(1, len(puntos)):
        a, b = puntos[i - 1], puntos[i]
        p1, p2 = a.get("p_H"), b.get("p_H")
        d = None if (p1 is None or p2 is None) else abs(p2 - p1)
        I = b.get("I") if b.get("I") is not None else I_FLOOR
        h_quieta = d is not None and d <= eps_p and I >= I_FLOOR
        hist.append({
            "n": b.get("n"),
            "delta_H": None if d is None else round(d, 4),
            "H_quieta": h_quieta,
            "viento": {
                "winner_modal": b.get("winner"),
                "winner_cambio": a.get("winner") != b.get("winner"),
                "overlap_topk": round(_overlap(a.get("topk") or [], b.get("topk") or []), 4),
            },
            "I": I,
        })
        if h_quieta:
            estables += 1
            if estables >= m and n_min is None:
                n_min = b.get("n")
        else:
            estables = 0

    if n_min is not None:
        estado_H = "PARA_DE_EMPUJAR_H"
    else:
        estado_H = "SEGUIR_EMPUJANDO_H"

    return {
        "estado": estado_H,
        "estado_H": estado_H,
        "estado_traza": "ABIERTA",
        "N_min": n_min,
        "N_estable": n_min,
        "eps_p": eps_p,
        "m_ventanas": m,
        "bloques": hist,
        "regla": (
            "N_min = menor n donde p_H aguantó m ventanas seguidas. "
            "No es un tope elegido. Letrero modal no frena. Traza ABIERTA."
        ),
        "plugin": "PLUGIN_AQUILES_H",
        "engine_tocado": False,
    }


def _ns_crecimiento(n0: int = N0, factor: int = FACTOR, fusible: int = N_FUSIBLE):
    n = n0
    while n <= fusible:
        yield n
        n = n * factor


def bootstrap_hasta_parar(
    replicar: Callable[[], Dict[str, Any]],
    bloques: Sequence[int] | None = None,
    eps_p: float = EPS_2PT,
    m: int = M_VENTANAS,
    k: int = 5,
    seed: int = 12345,
    n0: int = N0,
    fusible: int = N_FUSIBLE,
) -> Dict[str, Any]:
    grid = list(bloques) if bloques else list(_ns_crecimiento(n0=n0, fusible=fusible))
    pool: List[Dict[str, Any]] = []
    puntos: List[Dict[str, Any]] = []
    for n in grid:
        if n < n0:
            continue
        if n > fusible:
            break
        while len(pool) < n:
            pool.append(replicar())
        slice_n = pool[:n]
        ps = [x["p_H"] for x in slice_n if x.get("p_H") is not None]
        winners = [x.get("winner") for x in slice_n]
        winner = Counter(winners).most_common(1)[0][0] if winners else None
        names = []
        for x in slice_n:
            names.extend(x.get("topk") or [])
        topk = [nm for nm, _ in Counter(names).most_common(k)]
        p_mean = sum(ps) / len(ps) if ps else None
        I_vals = [x.get("I") for x in slice_n if x.get("I") is not None]
        I = max(I_FLOOR, sum(I_vals) / len(I_vals)) if I_vals else I_FLOOR
        puntos.append({"n": n, "p_H": p_mean, "winner": winner, "topk": topk, "I": I})
        ver = evaluar_serie(puntos, eps_p=eps_p, m=m)
        if ver["estado_H"] == "PARA_DE_EMPUJAR_H":
            ver["puntos"] = puntos
            ver["n_replicas_usadas"] = n
            ver["fusible"] = fusible
            ver["toque_fusible"] = False
            ver["seed"] = seed
            return ver

    ver = evaluar_serie(puntos, eps_p=eps_p, m=m)
    toque = (puntos[-1]["n"] >= fusible) if puntos else False
    if toque and ver["N_min"] is None:
        ver["estado_H"] = "NO_ENCONTRADO_FUSIBLE"
        ver["estado"] = "NO_ENCONTRADO_FUSIBLE"
    ver["puntos"] = puntos
    ver["n_replicas_usadas"] = puntos[-1]["n"] if puntos else 0
    ver["fusible"] = fusible
    ver["toque_fusible"] = toque
    ver["seed"] = seed
    return ver


if __name__ == "__main__":
    import json
    pts = [
        {"n": 32, "p_H": 0.64, "winner": "9_audaz_empresa", "topk": ["9_audaz_empresa", "30_ambicion"], "I": 0.03},
        {"n": 64, "p_H": 0.669, "winner": "9_audaz_empresa", "topk": ["9_audaz_empresa", "30_ambicion"], "I": 0.03},
        {"n": 128, "p_H": 0.670, "winner": "30_ambicion", "topk": ["30_ambicion", "9_audaz_empresa"], "I": 0.03},
        {"n": 256, "p_H": 0.671, "winner": "9_audaz_empresa", "topk": ["9_audaz_empresa", "30_ambicion"], "I": 0.03},
    ]
    print(json.dumps(evaluar_serie(pts), ensure_ascii=False, indent=2))
