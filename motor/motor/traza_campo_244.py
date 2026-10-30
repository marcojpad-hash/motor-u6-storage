#!/usr/bin/env python3
"""Adaptador de compatibilidad: conecta el runner existente con TRAZA_CAMPO_244_V2.

El runner carga este nombre fijo. La implementación V2 vive en un archivo lateral
versionado; este adaptador no modifica el runner, el motor canónico ni el catálogo.
"""
from __future__ import annotations
import importlib.util
from pathlib import Path

_IMPL = Path(__file__).resolve().parents[1] / "traza_campo_244_v2.py"
_SPEC = importlib.util.spec_from_file_location("traza_campo_244_v2_runtime", _IMPL)
if _SPEC is None or _SPEC.loader is None:
    raise ImportError(f"No se pudo cargar la implementación lateral: {_IMPL}")
_MOD = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MOD)

analizar = _MOD.analizar
origenes_renovables = _MOD.origenes_renovables

__all__ = ["analizar", "origenes_renovables"]
