#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""pistas_llm_caldero_v1.py — validación de pistas LLM del Caldero en preparar-z (A5 2026-11-07).

Las semillas (SEMILLAS_Z) pueden traer `pistas_llm`: arquetipos que el LLM preparador
propone como vecinos del Caldero para un sujeto. La fábrica NO llama a ningún LLM:
solo valida y copia. Cada pista es un dict:

    {"token": "...", "family": "<familia del catálogo 244>", "relevance": 0.0-1.0}

Claves aceptadas para la familia: family / familia / archetype / arquetipo.
Claves aceptadas para la relevancia: relevance / score / match (opcional, defecto 1.0).

Reglas (la autoridad es el guardián motor/motor/guardian_pistas_llm_caldero_v1.py):
- forma: token no vacío, <=60 caracteres, sin URL, con letras;
- identidad: el token no contiene términos de identidad del caso (nombre/alias);
- futuro: sin marcadores de desenlace ni post-Z;
- calendario: sin años 1000-2099.
Las pistas que violan esas reglas se DESCARTAN y quedan en la auditoría (huella
sha256, no el texto). Son errores que rechazan el lote (como el resto de
validaciones de preparar-z): `pistas_llm` no es una lista, pista sin token,
familia fuera del catálogo 244, relevancia no numérica o fuera de [0,1],
o el guardián ausente cuando hay pistas que validar.

La auditoría se guarda en la entrada como `caldero_llm_neighbor_hints_audit`.
El runner vuelve a pasar las pistas por el guardián antes del sidecar; aquí solo
se evita que una pista con fuga entre en la entrada sin dejar rastro.
Determinista, sin red, sin LLM. No toca Engine/244.
"""
from __future__ import annotations
import importlib.util
import re
from pathlib import Path

VERSION = "PISTAS_LLM_CALDERO_V1_20261107"
_FAMILIA_CLAVES = ("family", "familia", "archetype", "arquetipo")
_RELEVANCIA_CLAVES = ("relevance", "score", "match")


def _terminos_identidad(persona: str) -> set:
    """Nombre del sujeto + sus palabras (>=4 letras), en minúsculas.

    Espejo de la regla de identidad del runner (_identity_terms): el nombre
    completo y cada palabra larga cuentan como término de identidad.
    """
    s = str(persona or "").strip().casefold()
    terms = {s} if s else set()
    terms |= {w for w in re.split(r"\W+", s) if len(w) >= 4}
    return terms


def _cargar_guardian(motor_repo: Path):
    """Carga el guardián por ruta de archivo (mismo patrón que fabrica._gate()).

    Devuelve None si el módulo no existe: el llamador debe fallar cerrado
    (nunca validar con reglas duplicadas ni aceptar pistas sin guardián).
    """
    p = Path(motor_repo) / "motor" / "guardian_pistas_llm_caldero_v1.py"
    if not p.is_file():
        return None
    spec = importlib.util.spec_from_file_location("guardian_pistas_llm_caldero_v1", str(p))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def validar_pistas_llm(pistas, persona, familias_catalogo, motor_repo):
    """Valida `pistas_llm` de una semilla.

    Devuelve (aceptadas, auditoria, errores):
    - aceptadas: lista de pistas que pasaron el guardián (copia tal cual).
    - auditoria: dict del guardián + {"validador": VERSION}.
    - errores: lista de mensajes; si no está vacía, el lote se rechaza.
    Con pistas=None devuelve ([], auditoría vacía, []) sin tocar el guardián.
    """
    if pistas is None:
        return [], {"validador": VERSION, "guardian": "sin_pistas", "entrada": 0,
                    "aceptadas": 0, "descartadas": []}, []
    if not isinstance(pistas, list):
        return [], {}, ["pistas_llm debe ser una lista de pistas (dict con token)"]
    guardian = _cargar_guardian(motor_repo)
    if guardian is None:
        return [], {}, ["pistas_llm presentes pero falta motor/motor/guardian_pistas_llm_caldero_v1.py (guardian ausente)"]
    validas = []
    errores = []
    for i, h in enumerate(pistas):
        if not isinstance(h, dict):
            errores.append(f"pistas_llm[{i}] no es un dict")
            continue
        tok = h.get("token")
        if not isinstance(tok, str) or not tok.strip():
            errores.append(f"pistas_llm[{i}] sin token (str no vacío)")
            continue
        fam = None
        for k in _FAMILIA_CLAVES:
            if h.get(k) is not None:
                fam = h.get(k)
                break
        if fam is not None:
            if not isinstance(fam, str) or not fam.strip():
                errores.append(f"pistas_llm[{i}] familia vacía")
                continue
            if fam.strip() not in familias_catalogo:
                errores.append(f"pistas_llm[{i}] familia fuera del catálogo 244: {fam}")
                continue
        rel = None
        for k in _RELEVANCIA_CLAVES:
            if h.get(k) is not None:
                rel = h.get(k)
                break
        if rel is not None:
            try:
                rel = float(rel)
            except (TypeError, ValueError):
                errores.append(f"pistas_llm[{i}] relevance no numérica")
                continue
            if not (0.0 <= rel <= 1.0):
                errores.append(f"pistas_llm[{i}] relevance fuera de [0,1]: {rel}")
                continue
        validas.append(h)
    if errores:
        return [], {}, errores
    kept, audit = guardian.filtrar(validas, _terminos_identidad(persona))
    audit = {"validador": VERSION, **audit}
    return kept, audit, []
