#!/usr/bin/env python3
"""Capa 3: ESTABILIDAD_VECTORIAL_H
No modifica Engine_V5. No inventa tokens. No llama CONFIRMADA.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional

EPS_1PT = 0.01
EPS_2PT = 0.02
THETA_PHI = 0.85
I_FLOOR = 0.02
I_CAP_ESTABLE = 0.15


def _mass(chain: Optional[List[Dict[str, Any]]]) -> float:
    if not chain:
        return 0.0
    s = 0.0
    for t in chain:
        w = float(t.get("weight_favor_effective") or 0.0)
        c = float(t.get("confidence") or 0.0)
        s += w * c
    return s


def dispersion_mark(delta: Optional[float]) -> str:
    if delta is None:
        return "SIN_DELTA"
    a = abs(delta)
    if a <= EPS_1PT:
        return "BANDA_1PT"
    if a <= EPS_2PT:
        return "BANDA_2PT"
    return "FUERA_BANDA"


def imprevisto(sigma_sorpresa: Optional[float], p_azar: Optional[float] = None) -> float:
    # Nunca cero. Piso 2%. p_azar entra como sacudida acotada alrededor del piso.
    sig = 0.0 if sigma_sorpresa is None else max(0.0, float(sigma_sorpresa))
    az = 0.5 if p_azar is None else float(p_azar)
    I = max(I_FLOOR, sig + abs(az - 0.5))
    return round(min(1.0, I), 4)


def evaluar(
    p1: Optional[float],
    p2: Optional[float],
    freeze_h: Optional[str],
    top2: Optional[str],
    inverse_h: Optional[List[Dict[str, Any]]] = None,
    inverse_rival: Optional[List[Dict[str, Any]]] = None,
    sigma_sorpresa: Optional[float] = None,
    p_azar: Optional[float] = None,
) -> Dict[str, Any]:
    delta = None if (p1 is None or p2 is None) else round(p2 - p1, 4)
    marca = dispersion_mark(delta)
    S = _mass(inverse_h)
    R = _mass(inverse_rival)
    phi = None if (S + R) == 0 else round(S / (S + R), 4)
    I = imprevisto(sigma_sorpresa, p_azar)
    mismo_top = bool(freeze_h) and freeze_h == top2
    en_banda = marca in {"BANDA_1PT", "BANDA_2PT"}
    phi_ok = phi is not None and phi >= THETA_PHI
    I_ok = I <= I_CAP_ESTABLE

    if freeze_h is None:
        estado = "SIN_H"
    elif not mismo_top:
        estado = "RIVAL_AUN_POSIBLE"
    elif en_banda and phi_ok and I_ok:
        estado = "ESTABLE_VECTORIAL"
    elif en_banda and I_ok:
        estado = "MISMO_RUMBO_BANDA_SIN_MASA"
    elif mismo_top and not en_banda:
        estado = "MISMO_RUMBO_FUERA_BANDA"
    else:
        estado = "NO_ESTABLE"

    return {
        "estado": estado,
        "confirmada": False,
        "delta_p": delta,
        "marca_dispersion": marca,
        "epsilon_1pt": EPS_1PT,
        "epsilon_2pt": EPS_2PT,
        "phi": phi,
        "S_H": round(S, 4),
        "R": round(R, 4),
        "factor_imprevisto": I,
        "imprevisto_piso": I_FLOOR,
        "imprevisto_cap_estable": I_CAP_ESTABLE,
        "freeze_h": freeze_h,
        "top2": top2,
        "mismo_top": mismo_top,
        "regla": "ESTABLE_VECTORIAL exige misma H, |delta|<=0.02, phi>=0.85 e I<=0.15. I nunca es 0. No es CONFIRMADA.",
    }


def desde_agente(ag: Dict[str, Any]) -> Dict[str, Any]:
    fr = (ag.get("freeze") or {}).get("hypothesis")
    top = ag.get("top_cut2")
    inv_h = ag.get("inverse_cut2_H") or ag.get("inverse_cut1_H") or []
    inv_top = ((ag.get("inverse_cut2_top") or {}).get("chain") or [])
    rival = inv_top if top and fr and top != fr else []
    ctrl = ag.get("control_cut2") or ag.get("control_cut1") or {}
    out = evaluar(
        ag.get("cut1_p_final_H"),
        ag.get("cut2_p_final_H"),
        fr,
        top,
        inv_h,
        rival,
        ctrl.get("sigma_sorpresa_t"),
        ctrl.get("p_azar_t"),
    )
    out["label"] = ag.get("label")
    out["eje"] = ag.get("eje")
    out["aprendizaje"] = ag.get("aprendizaje")
    return out


if __name__ == "__main__":
    import json, sys
    from pathlib import Path
    raw = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    corridas = raw["corridas"]
    filas = []
    for caso, ejes in corridas.items():
        for eje, ag in ejes.items():
            r = desde_agente(ag)
            r["caso"] = caso
            filas.append(r)
    print(json.dumps({"n": len(filas), "filas": filas}, ensure_ascii=False, indent=2))
