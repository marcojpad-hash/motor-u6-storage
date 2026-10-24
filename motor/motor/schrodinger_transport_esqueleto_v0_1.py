#!/usr/bin/env python3
"""schrodinger_transport_esqueleto_v0_1.py — PROPUESTA / ESQUELETO. NO EJECUTA TRANSPORTE.
Ver SPEC_SCHRODINGER_V0_1.md. Alimenta_H=NO, writes_H=False. No importa Engine ni 244.
Solo fija interfaces; las funciones marcadas NO_VERIFICADO esperan decisión de Mj (μ_t, costo, pesos)."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
ESTADO = "PROPOSAL"
ALIMENTA_H = "NO"
PARAMS_DEFAULT = {"alpha": 1.0, "beta": 1.0, "gamma": 1.0, "delta": 1.0, "lam": 1.0, "epsilon": 0.05}  # PRE-REGISTRO pendiente Mj

def candidatos(cut: Dict[str, Any], soporte_acero: Optional[List[str]], billar_fams: List[str], eps: float = 1e-9) -> List[str]:
    vivos = [k for k, p in (cut.get("P_FULL_244") or {}).items() if p is not None and abs(float(p) - 0.5) > eps]
    return sorted(set(vivos) | set(soporte_acero or []) | set(billar_fams))

def mu_t(cut: Dict[str, Any], K: List[str]) -> Dict[str, float]:
    """NO_VERIFICADO: definición propuesta p-0.5 recortado; Mj debe fijarla."""
    P = cut.get("P_FULL_244") or {}
    w = {k: max(0.0, float(P.get(k) or 0.5) - 0.5) for k in K}
    s = sum(w.values())
    return {k: (v / s if s else 0.0) for k, v in w.items()}

def costo(i: str, j: str, ctx: Dict[str, Any], prm: Dict[str, float] = PARAMS_DEFAULT) -> float:
    raise NotImplementedError("NO_VERIFICADO: costo de transición pendiente de decisión Mj (SPEC §5)")

def sinkhorn(mu: Dict[str, float], nu_prior: Dict[str, float], C: Dict[tuple, float], eps: float):
    raise NotImplementedError("NO_VERIFICADO: runner de transporte no aprobado")

def memento_inversa(estado: Dict[str, Any], orden=("P", "A", "C")):
    raise NotImplementedError("NO_VERIFICADO: orden de recuperación pendiente Mj (SPEC §6)")

def salida_vacia(case_id: str) -> Dict[str, Any]:
    return {"estado": ESTADO, "Alimenta_H": ALIMENTA_H, "writes_H": False, "alimenta_convergencia": True,
            "case_id": case_id, "por_transicion": [], "null": None, "future_hidden": True,
            "nota": "Esqueleto: no hay resultado numérico."}

if __name__ == "__main__":
    import json; print(json.dumps(salida_vacia("DEMO"), ensure_ascii=False))
