#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""guardian_entrada_autoevidencia_v1.py — Guardián de entrada (PATCH 008, 2026-10-06).

Marca tokens de ENTRADA (P/A/C) que son nombres de familia/patrón del catálogo (p.ej. `30_ambicion`,
`12_obtencion`, `arquetipo_el_gobernante`). Un token así hace que el motor "encuentre" la familia
porque se le dio su propio nombre: auto-evidencia (circularidad entrada→salida).

Contrato: SOLO BANDERA. can_decide_H=False. No modifica el input, no quita tokens, no reordena
candidatos, no escribe H1/H2, no toca Engine_V5 ni patterns (solo lectura).
"""
from __future__ import annotations
import re
from typing import Any, Dict, Iterable, List, Mapping

VERSION = "GUARDIAN_ENTRADA_AUTOEVIDENCIA_V1_20261006"
# Forma de nombre de familia aunque no esté en el catálogo cargado (bandera débil).
FORMA_FAMILIA = re.compile(r"^(\d{1,3}_[a-z]|arquetipo_|schwartz_\d|anacyclosis_\d|situacion_dramatica_|mbti_)")


def _tok(item: Any) -> str | None:
    if isinstance(item, (list, tuple)) and item:
        return str(item[0]).strip()
    if isinstance(item, str):
        return item.strip()
    if isinstance(item, Mapping) and "token" in item:
        return str(item["token"]).strip()
    return None


def evaluar(cuts: Iterable[Mapping[str, Any]], catalogo: Mapping[str, Any] | None,
            nombres_extra: Iterable[str] = ()) -> Dict[str, Any]:
    cat = dict(catalogo or {})
    nombres = {k.casefold(): k for k in cat}
    for n in nombres_extra or ():
        nombres.setdefault(str(n).casefold(), str(n))
    banderas: List[Dict[str, Any]] = []
    for i, c in enumerate(cuts or []):
        cid = c.get("id") or c.get("corte") or i
        for eje in ("P", "A", "C"):
            for item in c.get(eje) or []:
                t = _tok(item)
                if not t:
                    continue
                k = t.casefold()
                peso = item[1] if isinstance(item, (list, tuple)) and len(item) > 1 else None
                if k in nombres:
                    fam = nombres[k]
                    tf = (cat.get(fam) or {}).get("tokens_favor") or {}
                    banderas.append({"corte": cid, "eje": eje, "token": t, "peso": peso, "tipo": "AUTOEVIDENCIA_NOMBRE_DE_FAMILIA",
                                     "familia": fam, "en_tokens_favor_de_si_misma": t in tf,
                                     "riesgo": "la familia puede ganar soporte por su propio nombre en la entrada"})
                elif FORMA_FAMILIA.match(k):
                    banderas.append({"corte": cid, "eje": eje, "token": t, "peso": peso, "tipo": "FORMA_DE_NOMBRE_DE_FAMILIA_FUERA_DE_CATALOGO",
                                     "familia": None, "riesgo": "parece etiqueta de familia, no hecho/rasgo observable"})
    fuertes = [b for b in banderas if b["tipo"] == "AUTOEVIDENCIA_NOMBRE_DE_FAMILIA"]
    return {
        "version": VERSION,
        "status": "EXECUTED_WITH_FINDINGS" if banderas else "EXECUTED",
        "bandera": bool(fuertes),
        "n_banderas": len(banderas),
        "n_autoevidencia": len(fuertes),
        "familias_autoevidenciadas": sorted({b["familia"] for b in fuertes}),
        "banderas": banderas,
        "accion": "SOLO_BANDERA",
        "can_decide_H": False, "escribe_H": False, "modifica_input": False, "reordena_candidatos": False,
        "nota": "Sugerencia para el LLM de entrada: reemplazar nombres de familia por hechos/rasgos observables. El motor no los quita.",
    }
