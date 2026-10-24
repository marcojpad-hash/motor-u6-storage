#!/usr/bin/env python3
"""PLUGIN_OTTO_NUMINOSO
Sidecar. No pisa patterns_final_v14.json.

Dos polos (Otto 1917, mysterium tremendum et fascinans).
El JSON de esta carpeta venia en UNA ficha
(otto_01_numinoso_tremendum_fascinans). El wrapper anterior
acorto el nombre a otto_01_...tremendum: recorte de nombre.

Claude 2026-09-07: partir en 01 tremendum + 02 fascinans.
Se pueden encender los dos a la vez.
"""
from __future__ import annotations

from typing import Dict

PARCHE_A_REEMPLAZAR = "carisma_sacro_vocacion_religiosa"

OTTO = {
    "otto_01_numinoso_tremendum": {
        "description": (
            "Otto 1917 polo tremendum: miedo, misterio, "
            "desafio_sagrado. No es el fascinans."
        ),
        "tokens_favor": {
            "desafio_sagrado": 0.85,
            "misterio": 0.80,
            "miedo": 0.78,
        },
        "tokens_contra": {
            "cotidiano": 0.80,
            "orgullo": 0.78,
            "poder": 0.70,
        },
        "evidence_status": "secondary_verified",
        "fuente": "Otto 1917 Das Heilige; polo tremendum.",
    },
    "otto_02_numinoso_fascinans": {
        "description": (
            "Otto 1917 polo fascinans: devocion, piedad, "
            "paz_interior, carisma que atrae. Coexiste con 01."
        ),
        "tokens_favor": {
            "devocion": 0.82,
            "piedad": 0.80,
            "paz_interior": 0.72,
            "carisma": 0.70,
            "sabiduria": 0.65,
            "humildad_religiosa": 0.75,
            "humildad": 0.68,
        },
        "tokens_contra": {
            "orgullo": 0.78,
            "estatus_social": 0.68,
            "poder": 0.70,
        },
        "evidence_status": "secondary_verified",
        "fuente": "Otto 1917 Das Heilige; polo fascinans.",
    },
}


def fusionar(patterns: Dict) -> Dict:
    out = dict(patterns)
    out.pop(PARCHE_A_REEMPLAZAR, None)
    out.pop("otto_01_numinoso_tremendum_fascinans", None)
    out.update(OTTO)
    return out


if __name__ == "__main__":
    import json
    from pathlib import Path
    base = json.loads(Path("patterns_final_v14.json").read_text(encoding="utf-8"))
    lib = fusionar(base)
    assert "otto_01_numinoso_tremendum" in lib
    assert "otto_02_numinoso_fascinans" in lib
    print("ok otto 01+02", "n", len(lib))
