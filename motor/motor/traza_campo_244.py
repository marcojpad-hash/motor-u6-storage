#!/usr/bin/env python3
"""Adaptador de compatibilidad hacia TRAZA_CAMPO_244_V2.

El runner copia este módulo a un directorio temporal de ejecución. Por eso la
implementación se localiza subiendo los ancestros, no suponiendo que conserva
la ruta original del repositorio.
"""
from __future__ import annotations
import importlib.util
from pathlib import Path

_HERE = Path(__file__).resolve()
_IMPL = next((parent / "traza_campo_244_v2.py" for parent in _HERE.parents
              if (parent / "traza_campo_244_v2.py").is_file()), None)
if _IMPL is None:
    raise ImportError(f"No se encontró traza_campo_244_v2.py desde {_HERE}")
_SPEC = importlib.util.spec_from_file_location("traza_campo_244_v2_runtime", _IMPL)
if _SPEC is None or _SPEC.loader is None:
    raise ImportError(f"No se pudo cargar la implementación lateral: {_IMPL}")
_MOD = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MOD)

analizar = _MOD.analizar
origenes_renovables = _MOD.origenes_renovables
__all__ = ["analizar", "origenes_renovables"]
