#!/usr/bin/env python3
"""PLUGIN_FAMILIAS_GLORIA_SACRO

No toca Engine_V5 ni reescribe patterns_final_v14.json.
Suma DOS hipótesis al diccionario en memoria / a un JSON de salida.

Candado de tokens:
- tokens_favor/contra SOLO del léxico ya existente en las 244.
- No se plantan fama_hegemonica, evangelizacion, etc.: no dispararían.
- cap conceptual: estas fichas USAN reconocimiento y humildad_religiosa
  como favor; no cancelan las vías contra que ya tenían esas palabras.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Dict

EXTRA = {
    "fama_reputacion_gloria_publica": {
        "description": (
            "El nombre se multiplica en la memoria colectiva. "
            "No es poder de cargo ni logro Schwartz: es que te vean."
        ),
        "tokens_favor": {
            "reconocimiento": 0.8,
            "estatus_social": 0.75,
            "redes_prestigio": 0.7,
            "escalada_status": 0.7,
        },
        "tokens_contra": {
            "humildad": 0.7,
            "olvido": 0.75,
        },
        "evidence_status": "unverified",
        "fuente": "PLUGIN_FAMILIAS_GLORIA_SACRO; no calibrado.",
    },
    "carisma_sacro_vocacion_religiosa": {
        "description": (
            "El sujeto opera como canal de lo sacro (starets, predicador, piedad operativa). "
            "No es kwml_03_mago ni solo tradicion Schwartz."
        ),
        "tokens_favor": {
            "humildad_religiosa": 0.85,
            "humildad": 0.7,
            "piedad": 0.8,
            "devocion": 0.75,
            "desafio_sagrado": 0.65,
        },
        "tokens_contra": {
            "orgullo": 0.8,
        },
        "evidence_status": "unverified",
        "fuente": "PLUGIN_FAMILIAS_GLORIA_SACRO; no calibrado.",
    },
}


def fusionar(patterns: Dict) -> Dict:
    out = copy.deepcopy(patterns)
    for k, v in EXTRA.items():
        if k in out:
            raise ValueError(f"colision con 244: {k}")
        out[k] = v
    return out


def escribir_fusion(
    patterns_path: str,
    dest: str = "patterns_v14_plus_gloria_sacro.json",
) -> str:
    p = json.loads(Path(patterns_path).read_text(encoding="utf-8"))
    q = fusionar(p)
    Path(dest).write_text(json.dumps(q, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return dest


if __name__ == "__main__":
    import sys
    src = sys.argv[1] if len(sys.argv) > 1 else "patterns_final_v14.json"
    dest = escribir_fusion(src)
    print("n", len(json.loads(Path(dest).read_text())), "->", dest)
