#!/usr/bin/env python3
"""Matriz de mortalidad Z90: integración observacional, sin inventar tasas ni alterar H."""
from __future__ import annotations
import csv, gzip, hashlib, importlib.util, json, re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

TEXT_KEYS = {
    "texto", "text", "descripcion", "description", "hecho", "evento", "evidencia",
    "narrativa", "observacion", "observation", "resumen", "biografia", "contexto_textual"
}
BASE_REQUIRED_STATS = {
    "population", "year", "age_interval", "rate_type",
    "source_url", "retrieved_at", "source_sha256"
}

def _load_classifier(root: Path):
    path = root / "motor" / "familias_tokens" / "mortalidad_clasificador_lateral_v0_1.py"
    if not path.is_file():
        return None
    spec = importlib.util.spec_from_file_location("mortalidad_clasificador_activo_u6", path)
    mod = importlib.util.module_from_spec(spec)
    import sys
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod
