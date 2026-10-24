#!/usr/bin/env python3
"""Geometría de la corrida. Siempre. Alimenta_H=NO.

Usa solo R732 del motor: dX, persist_cos, kappa_dir.
No elige 'a veces Ricci / a veces no'. Si no hay ≥2 cortes, lo declara.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional


def _last(xs: Optional[List], default=None):
    if not xs:
        return default
    return xs[-1]


def observar_corrida(motor_out: Dict[str, Any]) -> Dict[str, Any]:
    r = motor_out.get("R732") or {}
    dX = list(r.get("dX_norm") or [])
    persist = list(r.get("persist_cos") or [])
    kappa = list(r.get("kappa_dir") or [])
    shape = r.get("X_shape")
    n_cuts = int((motor_out.get("n_cuts") or (shape[0] if shape else 0)))

    accel = []
    for i in range(1, len(dX)):
        accel.append(round(float(dX[i]) - float(dX[i - 1]), 6))

    suficiente = n_cuts >= 2
    return {
        "sidecar": "geometria",
        "Alimenta_H": "NO",
        "escribe_H": False,
        "n_cuts": n_cuts,
        "X_shape": shape,
        "suficiente_para_dX": suficiente,
        "dX_norm": dX,
        "persist_cos": persist,
        "kappa_dir": kappa,
        "aceleracion_dX": accel,
        "dX_ultimo": _last(dX),
        "persist_ultima": _last(persist),
        "kappa_ultimo": _last(kappa),
        "lectura": (
            "Hay trayectoria medible."
            if suficiente
            else "Un corte: no hay dX/κ. No inventar geometría."
        ),
    }
