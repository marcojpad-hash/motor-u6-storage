#!/usr/bin/env python3
"""PLUGIN_REPORTE_3D
No toca V5. A partir de una secuencia de tableros 244 arma, por corte:
  H              letrero
  se_movieron    las que más cambiaron vs el corte previo
  no_se_apagaron las que siguen altas aunque no griten
"""
from __future__ import annotations
from typing import Any, Dict, List, Sequence, Tuple

PISO = 0.62
N_MOV = 3
N_PERSIST = 3


def _top(board: Dict[str, float], n: int = 1) -> List[Tuple[str, float]]:
    return sorted(board.items(), key=lambda x: -x[1])[:n]


def leer(
    seq: Sequence[Tuple[str, Dict[str, float]]],
    piso: float = PISO,
    n_mov: int = N_MOV,
    n_persist: int = N_PERSIST,
) -> Dict[str, Any]:
    cortes = []
    prev = None
    for i, (cid, board) in enumerate(seq):
        H, p = _top(board, 1)[0]
        if prev is None:
            mov = []
        else:
            deltas = []
            keys = set(board) | set(prev)
            for k in keys:
                d = board.get(k, 0.5) - prev.get(k, 0.5)
                deltas.append((k, round(d, 4), round(board.get(k, 0.5), 4)))
            deltas.sort(key=lambda x: -abs(x[1]))
            mov = [{"h": k, "d": d, "p": pv} for k, d, pv in deltas[:n_mov]]
        persist = [
            {"h": k, "p": round(v, 4)}
            for k, v in _top(board, 12)
            if k != H and v >= piso
        ][:n_persist]
        cortes.append({
            "corte": cid,
            "H": H,
            "p": round(p, 4),
            "se_movieron": mov,
            "no_se_apagaron": persist,
        })
        prev = board
    return {"plugin": "PLUGIN_REPORTE_3D", "engine_tocado": False, "cortes": cortes}


if __name__ == "__main__":
    print("ok")
