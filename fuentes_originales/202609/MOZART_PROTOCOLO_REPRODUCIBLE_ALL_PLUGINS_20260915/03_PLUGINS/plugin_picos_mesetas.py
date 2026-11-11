#!/usr/bin/env python3
"""PLUGIN_PICOS_MESETAS

Forma temporal de cada hipótesis. No es el eje (eso es Aquiles).
No entra a Engine_V5. Se corre sobre la secuencia de tableros.

Para cada k:
  serie p_k(t0)...p_k(tn)
  d_t = p_k(t) - p_k(t-1)
  ↗ si d >= eps
  ↘ si d <= -eps
  → si |d| < eps   (meseta de movimiento, no "es el campeón")

Señal de trabajo (no ley):
  un ↗ de k que ocurre ANTES de que k sea Top1.
"""
from __future__ import annotations
from typing import Any, Dict, List, Sequence, Tuple

EPS = 0.04


def signo(d: float, eps: float = EPS) -> str:
    if d >= eps:
        return "↗"
    if d <= -eps:
        return "↘"
    return "→"


def curvas(
    seq: Sequence[Tuple[str, Dict[str, float]]],
    eps: float = EPS,
    piso: float = 0.62,
) -> Dict[str, Any]:
    if not seq:
        return {"plugin": "PLUGIN_PICOS_MESETAS", "curvas": {}}
    ids = [s[0] for s in seq]
    keys = set()
    for _, b in seq:
        keys.update(b)
    tops = []
    for _, b in seq:
        tops.append(max(b, key=lambda k: b[k]))
    out = {}
    for k in keys:
        serie = [round(b.get(k, 0.5), 4) for _, b in seq]
        if max(serie) < piso:
            continue
        ds = [round(serie[i] - serie[i - 1], 4) for i in range(1, len(serie))]
        forma = "".join(signo(d, eps) for d in ds)
        if set(forma) <= {"→"}:
            continue
        i_top = next((i for i, t in enumerate(tops) if t == k), None)
        subio_antes = False
        if i_top is not None and i_top >= 1:
            subio_antes = any(ds[j] >= eps for j in range(i_top))
        out[k] = {
            "serie": serie,
            "deltas": ds,
            "forma": forma,
            "fue_top1": i_top,
            "subio_antes_de_ser_top1": subio_antes,
        }
    return {
        "plugin": "PLUGIN_PICOS_MESETAS",
        "eps": eps,
        "cortes": ids,
        "top1": tops,
        "curvas": out,
        "eje": "Aquiles / meseta del tema. Esta pieza no lo declara.",
    }


if __name__ == "__main__":
    print("PLUGIN_PICOS_MESETAS listo")
