#!/usr/bin/env python3
"""plugin_polaridad_causal.py — polaridad causal + doble negación (litote)

CANON DE CIERRE (Mj / Puta 3 · 2026-09-20)
------------------------------------------
- FALSO PROBLEMA respecto a H1/H2: este plugin SOLO MARCA.
  No mueve H, no toca Engine/244/FREEZE, no reescribe freeze.
- Caso simple: «no explica / no causó» → NIEGA → post_hoc NO dispara.
- Caso doble: «no es que no explica…» → DOBLE_NEGACION_LITOTE
  (no se trata como negación simple; no se «apaga» por error).
- Cerrado: no reabrir T5 / doble negación como hueco de motor.

API pública:
  clasificar_polaridad_causal(texto) -> dict
  causalidad_negada_simple(texto) -> bool   # True solo NIEGA simple
"""
from __future__ import annotations

import json
import re
import unicodedata
from typing import Any, Dict

__version__ = "1.0.0-cierre-20260920"
ALIMENTA_H = "NO"
TOCA_ENGINE = "NO"
TOCA_244 = "NO"
TOCA_FREEZE = "NO"
SOLO_MARCA = True

_VERBO_CAUSAL = (
    r"(?:explica|explican|explicaba|explico|explique|expliquen|"
    r"predijo|predecia|predecía|predice|prediga|"
    r"demuestra|demostró|demostro|demuestre|"
    r"causo|causó|causa|cause|"
    r"provoco|provocó|provoca|provoque|"
    r"por\s+eso)"
)

_RX_DOBLE = re.compile(
    rf"(?:"
    rf"\bno\s+es\s+que\s+no\b|"
    rf"\btampoco\s+es\s+que\s+no\b|"
    rf"\bno\s+es\s+que\s+(?:eso|esto|aquello|él|ella|a|b|[a-záéíóúñ]+)?\s*no\s+{_VERBO_CAUSAL}|"
    rf"\bno\s+es\s+que\s+(?:eso|esto|aquello|[a-záéíóúñ]+)\s+no\s+{_VERBO_CAUSAL}"
    rf")",
    re.I,
)

_RX_NIEGA = re.compile(
    rf"(?:^|\b)(?:pero\s+)?(?:eso|esto|aquello|lo\s+anterior)?\s*"
    rf"(?:no|nunca|tampoco)\s+"
    rf"(?:eso|esto|aquello)?\s*"
    rf"{_VERBO_CAUSAL}",
    re.I,
)

_RX_NO_POR_ESO = re.compile(r"\bno\s+(?:es\s+que\s+)?(?:por\s+eso|entonces)\b", re.I)
_RX_SIN_QUE = re.compile(
    r"\bsin\s+que\s+(?:eso|esto)?\s*(?:explique|cause|demuestre|prediga)",
    re.I,
)


def _norm(texto: str) -> str:
    s = unicodedata.normalize("NFKC", texto or "")
    s = s.lower()
    s = re.sub(r"\s+", " ", s).strip()
    return s


def clasificar_polaridad_causal(texto: str) -> Dict[str, Any]:
    """Clasifica polaridad del claim causal.

    etiquetas:
      NEUTRO | AFIRMA_IMPLICITA | NIEGA | DOBLE_NEGACION_LITOTE
    """
    n = _norm(texto)
    if not n:
        return {
            "etiqueta": "NEUTRO",
            "causalidad_negada_simple": False,
            "post_hoc_puede_marcar": True,
            "solo_marca": True,
            "Alimenta_H": ALIMENTA_H,
            "motivo": "vacio",
            "version": __version__,
        }

    if _RX_DOBLE.search(n):
        return {
            "etiqueta": "DOBLE_NEGACION_LITOTE",
            "causalidad_negada_simple": False,
            "post_hoc_puede_marcar": True,  # no apagar por falso NIEGA
            "solo_marca": True,
            "Alimenta_H": ALIMENTA_H,
            "motivo": "litote/doble_negacion_no_es_negacion_simple",
            "version": __version__,
            "candado": "CERRADO_NO_REABRIR_COMO_HUECO_MOTOR",
        }

    if _RX_NIEGA.search(n) or _RX_NO_POR_ESO.search(n) or _RX_SIN_QUE.search(n):
        return {
            "etiqueta": "NIEGA",
            "causalidad_negada_simple": True,
            "post_hoc_puede_marcar": False,
            "solo_marca": True,
            "Alimenta_H": ALIMENTA_H,
            "motivo": "negacion_simple_de_causalidad",
            "version": __version__,
        }

    return {
        "etiqueta": "NEUTRO",
        "causalidad_negada_simple": False,
        "post_hoc_puede_marcar": True,
        "solo_marca": True,
        "Alimenta_H": ALIMENTA_H,
        "motivo": "sin_negacion_causal_explicita",
        "version": __version__,
    }


def causalidad_negada_simple(texto: str) -> bool:
    """True solo si hay NIEGA simple (no litote/doble). Drop-in para post_hoc."""
    return bool(clasificar_polaridad_causal(texto)["causalidad_negada_simple"])


# alias compat con nombre viejo del plugin pregunta
def causalidad_negada(texto: str) -> bool:
    return causalidad_negada_simple(texto)


if __name__ == "__main__":
    cases = [
        ("no explica el resultado", "NIEGA"),
        ("eso no causó el conflicto", "NIEGA"),
        ("no por eso se derrumbó", "NIEGA"),
        ("no es que no explica el resultado", "DOBLE_NEGACION_LITOTE"),
        ("no es que no causó el conflicto", "DOBLE_NEGACION_LITOTE"),
        ("No es que A no explique B; de hecho lo aclara.", "DOBLE_NEGACION_LITOTE"),
        ("tampoco es que no explique nada", "DOBLE_NEGACION_LITOTE"),
        ("explica el resultado", "NEUTRO"),
        ("A ocurrió. Por eso B.", "NEUTRO"),
        ("A ocurrió. No por eso B.", "NIEGA"),
    ]
    fail = 0
    for text, expect in cases:
        got = clasificar_polaridad_causal(text)
        ok = got["etiqueta"] == expect
        if not ok:
            fail += 1
        print(("OK" if ok else "FAIL"), expect, "→", got["etiqueta"], "|", text)
    # contrato motor
    assert ALIMENTA_H == "NO" and SOLO_MARCA is True
    print("PASS" if fail == 0 else f"FAIL n={fail}")
    raise SystemExit(fail)

# Dinámica (no atascarse): usar sidecar_latencia_decimo_hombre.polaridad_con_latencia
# — litote/empate → LATENCIA; décimo hombre a ~50%; si no desempata → almacenar.
