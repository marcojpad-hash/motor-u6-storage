#!/usr/bin/env python3
"""PLUGIN_OTTO_NUMINOSO
Sidecar. No pisa patterns_final_v14.json.

Sustituye el parche carisma_sacro_vocacion_religiosa por Otto 1917
(mysterium tremendum et fascinans). Solo tokens del lexico 244.
fama_reputacion_gloria_publica se deja aparte (secular).
"""
from __future__ import annotations

from typing import Dict

OTTO_KEY = "otto_01_numinoso_tremendum"

OTTO = {
    OTTO_KEY: {
        "description": (
            "Rudolf Otto, Das Heilige (1917): lo numinoso como categoria propia, "
            "distinta del carisma weberiano y del ritual. "
            "Polo tremendum (miedo/misterio/desafio_sagrado) + polo fascinans "
            "(devocion/piedad/paz_interior/carisma)."
        ),
        "tokens_favor": {
            "desafio_sagrado": 0.85,
            "misterio": 0.80,
            "miedo": 0.78,
            "devocion": 0.82,
            "piedad": 0.80,
            "paz_interior": 0.72,
            "carisma": 0.70,
            "sabiduria": 0.65,
            "humildad_religiosa": 0.75,
            "humildad": 0.68,
        },
        "tokens_contra": {
            "cotidiano": 0.80,
            "orgullo": 0.78,
            "poder": 0.70,
            "estatus_social": 0.68,
        },
        "evidence_status": "secondary_verified",
        "fuente": "Otto 1917 Das Heilige / Lo santo; sidecar no canonico.",
    }
}

FAMA_SE_QUEDA = "fama_reputacion_gloria_publica"
PARCHE_A_REEMPLAZAR = "carisma_sacro_vocacion_religiosa"


def fusionar(patterns: Dict) -> Dict:
    out = dict(patterns)
    out.pop(PARCHE_A_REEMPLAZAR, None)
    out.update(OTTO)
    return out


if __name__ == "__main__":
    import json
    from pathlib import Path
    base = json.loads(Path("patterns_final_v14.json").read_text(encoding="utf-8"))
    lib = fusionar(base)
    assert PARCHE_A_REEMPLAZAR not in lib
    assert OTTO_KEY in lib
    print("ok otto sidecar", "n", len(lib))
