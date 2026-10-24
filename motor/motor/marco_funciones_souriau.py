"""Seis funciones de Souriau. Un agente puede ocupar varias. No decide H.

PATCH 016 (2026-10-06): las funciones se derivan de los PERSONAJES del corte (personajes_corte_016: protagonista y
sus facetas por fase de vida, instituciones, colectivos, antagonistas, mentor, familia, pareja...; ids de rol neutros,
solo del texto propio del corte). El reparto POSICIONAL anterior (leon=P[:5], sol=P[:3], tierra=C[:5], marte=A[:5])
era un artefacto (sol ⊂ leon casi siempre) y queda como variante medible: SOURIAU_FUNCIONES_016=posicional.
Corte sin texto propio -> funciones vacías con estado SIN_TEXTO (no se rellenan con tokens).
"""
from __future__ import annotations
import importlib.util
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

LUNA = ("ayuda", "aliado", "desvio", "auxilio", "complice")
BALANZA = ("ley", "juez", "arbitro", "juicio", "norma", "corte")
ORD = ("leon", "sol", "tierra", "marte", "balanza", "luna")
MODO_DEFAULT = "personajes"


def _toks(corte: Dict[str, Any], eje: str) -> List[str]:
    out = []
    for item in corte.get(eje) or []:
        if isinstance(item, (list, tuple)) and item:
            out.append(str(item[0]))
        elif isinstance(item, str):
            out.append(item)
    return out


def _hit(tokens: List[str], claves: tuple) -> List[str]:
    return [t for t in tokens if any(k in t.lower() for k in claves)]


def _por_corte_posicional(cuts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    por_corte = []
    for i, c in enumerate(cuts or []):
        p, a, ctx = _toks(c, "P"), _toks(c, "A"), _toks(c, "C")
        todos = p + a + ctx
        funciones = {
            "leon": p[:5],
            "sol": p[:3],
            "tierra": ctx[:5],
            "marte": a[:5],
            "balanza": _hit(todos, BALANZA)[:4],
            "luna": _hit(todos, LUNA)[:4],
        }
        ocupacion = {}
        for nombre, toks in funciones.items():
            for t in toks:
                ocupacion.setdefault(t, []).append(nombre)
        cumulo = {t: fn for t, fn in ocupacion.items() if len(fn) > 1}
        por_corte.append({
            "corte": c.get("id") or i,
            "funciones": funciones,
            "cumulo": cumulo,
            "mismo_agente_varias_funciones": bool(cumulo),
        })
    return por_corte


def _personajes_mod():
    p = Path(__file__).resolve().parent / "personajes_corte_016.py"
    if not p.is_file():
        return None
    name = "personajes_corte_016"
    if name in sys.modules and getattr(sys.modules[name], "__file__", None) == str(p):
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    sys.modules[name] = m
    return m


def _inercia(por_corte: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    mov = []
    for i in range(1, len(por_corte)):
        a, b = por_corte[i - 1], por_corte[i]
        entra = [t for t in b["funciones"]["marte"] if t in a["funciones"]["leon"]]
        fa = {r: [f for f in ORD if r in a["funciones"][f]] for f in ORD for r in a["funciones"][f]}
        fb = {r: [f for f in ORD if r in b["funciones"][f]] for f in ORD for r in b["funciones"][f]}
        cambia = [{"agente": r, "de": fa[r], "a": fb[r]} for r in fb if r in fa and fa[r] != fb[r]]
        mov.append({"de": a["corte"], "a": b["corte"], "leon_pasa_a_marte": entra, "quieto": not entra,
                    "cambios_de_funcion": cambia})
    return mov


def distribuir(cuts: List[Dict[str, Any]], modo: str = None) -> Dict[str, Any]:
    modo = (modo or os.environ.get("SOURIAU_FUNCIONES_016") or MODO_DEFAULT).strip().lower()
    pm = _personajes_mod() if modo != "posicional" else None
    if pm is None:
        por_corte = _por_corte_posicional(cuts)
        mov = [{"de": por_corte[i - 1]["corte"], "a": por_corte[i]["corte"],
                "leon_pasa_a_marte": [t for t in por_corte[i]["funciones"]["marte"] if t in por_corte[i - 1]["funciones"]["leon"]],
                "quieto": not [t for t in por_corte[i]["funciones"]["marte"] if t in por_corte[i - 1]["funciones"]["leon"]]}
               for i in range(1, len(por_corte))]
        return {"status": "EXECUTED", "can_decide_H": False, "feeds_inercia": True,
                "modo": "posicional_015" if modo == "posicional" else "posicional_015_SIN_MODULO_PERSONAJES",
                "semantics": "NARRATIVE_ROLE_ASSIGNMENT_ONLY",
                "mathematical_momentum_map": "NOT_IMPLEMENTED_BY_THIS_MODULE",
                "coadjoint_orbit": "NOT_COMPUTED",
                "regla": "un agente puede ocupar mas de una funcion en el mismo corte",
                "por_corte": por_corte, "inercia": mov}
    ext = pm.extraer(cuts)
    por_corte = pm.funciones(ext)
    return {"status": "EXECUTED", "can_decide_H": False, "escribe_H": False, "feeds_inercia": True,
            "modo": "personajes_016", "version_personajes": getattr(pm, "VERSION", None),
            "semantics": "NARRATIVE_ROLE_ASSIGNMENT_ONLY",
            "mathematical_momentum_map": "NOT_IMPLEMENTED_BY_THIS_MODULE",
            "coadjoint_orbit": "NOT_COMPUTED",
            "regla": "un agente puede ocupar mas de una funcion en el mismo corte; agentes = personajes del corte (ids de rol neutros)",
            "por_corte": por_corte, "inercia": _inercia(por_corte), "personajes": ext,
            "variante_medible": "SOURIAU_FUNCIONES_016=posicional -> reparto posicional 015 (artefacto leon=P[:5], sol=P[:3])"}
