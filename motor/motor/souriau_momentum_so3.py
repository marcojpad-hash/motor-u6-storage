"""Momentum map for the cotangent-lifted SO(3) action on T*R^3.

Contract: q and p are explicit 3-vectors (position and canonical momentum).
J(q,p)=q x p under the standard Euclidean identification so(3)* ~= R^3.
This module does not infer q/p from narrative P/A/C tokens.
"""
from __future__ import annotations
import math
from typing import Iterable

def momentum_map_so3(q: Iterable[float], p: Iterable[float]) -> tuple[float, float, float]:
    qv = tuple(float(x) for x in q); pv = tuple(float(x) for x in p)
    if len(qv) != 3 or len(pv) != 3:
        raise ValueError("SO(3) momentum map requires q and p with exactly 3 components")
    if not all(math.isfinite(x) for x in (*qv, *pv)):
        raise ValueError("q and p must contain only finite numbers")
    x = (qv[1]*pv[2] - qv[2]*pv[1], qv[2]*pv[0] - qv[0]*pv[2], qv[0]*pv[1] - qv[1]*pv[0])
    if not all(math.isfinite(v) for v in x):
        raise ArithmeticError("non-finite SO(3) momentum-map result")
    return x
