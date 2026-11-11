#!/usr/bin/env python3
"""PLUGIN_ARCO_DRAMATICO
Sid Field + Blake Snyder (Save the Cat) + Robert McKee.

NO son lo mismo. Tres lecturas del MISMO timeline.
NO toca Engine_V5. NO agrega hipótesis a las 244.
VACIO se deja. No se rellena de a huevo.

Field  = dónde se parte el TIEMPO (actos, plot points).
Snyder = qué MOMENTO de catálogo comercial hay cerca.
McKee  = si el VALOR se voltea (carga +/−) hacia crisis/clímax.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

FIELD = [
    ("ACTO_1", "planteamiento / casa"),
    ("PLOT_POINT_1", "ya no hay vuelta fácil"),
    ("PUNTO_MEDIO", "se ve el tipo de cinta"),
    ("PLOT_POINT_2", "segundo golpe"),
    ("ACTO_3", "se paga o se recoge"),
]

SNYDER = [
    ("opening_image", "foto de entrada"),
    ("theme_stated", "de qué va, sin querer"),
    ("setup", "casa"),
    ("catalyst", "el jalón"),
    ("debate", "¿entro o no?"),
    ("break_into_two", "cruza"),
    ("b_story", "otro hilo"),
    ("fun_and_games", "promesa del género"),
    ("midpoint", "falso triunfo o falso fondo"),
    ("bad_guys_close_in", "aprieta"),
    ("all_is_lost", "muerte aparente"),
    ("dark_night", "quieto y feo"),
    ("break_into_three", "se levanta"),
    ("finale", "paga"),
    ("final_image", "foto de salida vs entrada"),
]

MCKEE = [
    ("incidente_incitador", "el valor de la vida se toca por primera vez"),
    ("complicaciones", "el valor se aprieta, no se resuelve"),
    ("crisis", "dilema: dos males o dos bienes, hay que elegir"),
    ("climax", "la elección se ACTÚA y el valor se voltea"),
    ("resolucion", "el mundo nuevo, más chico que el clímax"),
]


def _dmax(cut: Dict[str, Any]) -> float:
    if cut.get("delta_max") is not None:
        return abs(float(cut["delta_max"]))
    if cut.get("d_max") is not None:
        return abs(float(cut["d_max"]))
    movers = cut.get("movers") or []
    if movers:
        return max(abs(float(x.get("d", 0))) for x in movers)
    return 0.0


def _carga(cut: Dict[str, Any]) -> Optional[str]:
    """McKee: + o − si el caller lo manda; si no, se infiere del signo de delta_neto."""
    if cut.get("carga") in ("+", "-", "0"):
        return cut["carga"]
    neto = cut.get("delta_neto")
    if neto is None:
        return None
    if neto > 0:
        return "+"
    if neto < 0:
        return "-"
    return "0"


def _nota(cut: Dict[str, Any], umbral: float) -> bool:
    return _dmax(cut) >= umbral


def _pick(cortes: Sequence[Dict[str, Any]], frac: float) -> Dict[str, Any]:
    n = len(cortes)
    j = min(n - 1, max(0, round(frac * (n - 1))))
    return cortes[j]


def leer(
    cortes: Sequence[Dict[str, Any]],
    umbral: float = 0.04,
) -> Dict[str, Any]:
    n = len(cortes)
    if n == 0:
        return {"plugin": "PLUGIN_ARCO_DRAMATICO", "error": "sin cortes"}

    # Field por posición
    if n == 1:
        f_idx = [(0, "ACTO_1")]
    elif n == 2:
        f_idx = [(0, "ACTO_1"), (1, "ACTO_3")]
    elif n == 3:
        f_idx = [(0, "ACTO_1"), (1, "PUNTO_MEDIO"), (2, "ACTO_3")]
    else:
        f_idx = [
            (0, "ACTO_1"),
            (max(1, n // 4), "PLOT_POINT_1"),
            (n // 2, "PUNTO_MEDIO"),
            (min(n - 2, (3 * n) // 4), "PLOT_POINT_2"),
            (n - 1, "ACTO_3"),
        ]
    glosa_f = {a: b for a, b in FIELD}
    field = []
    for i, nombre in f_idx:
        cut = cortes[i]
        field.append({
            "beat": nombre,
            "glosa": glosa_f.get(nombre, ""),
            "corte": cut.get("id"),
            "se_nota": _nota(cut, umbral),
            "carga": _carga(cut),
            "forzado": False,
        })

    snyder = []
    for i, (bid, glosa) in enumerate(SNYDER):
        cut = _pick(cortes, i / max(1, len(SNYDER) - 1))
        snyder.append({
            "beat": bid,
            "glosa": glosa,
            "corte_cerca": cut.get("id"),
            "estado": "SE_NOTA" if _nota(cut, umbral) else "VACIO",
            "forzado": False,
        })

    # McKee: 5 hitos + volteos de carga entre cortes consecutivos
    m_frac = [0.0, 0.3, 0.55, 0.8, 1.0]
    mckee = []
    for frac, (bid, glosa) in zip(m_frac, MCKEE):
        cut = _pick(cortes, frac)
        mckee.append({
            "beat": bid,
            "glosa": glosa,
            "corte": cut.get("id"),
            "se_nota": _nota(cut, umbral),
            "carga": _carga(cut),
            "forzado": False,
        })
    volteos = []
    for i in range(1, n):
        a, b = _carga(cortes[i - 1]), _carga(cortes[i])
        if a and b and a != b and a != "0" and b != "0":
            volteos.append({
                "de": cortes[i - 1].get("id"),
                "a": cortes[i].get("id"),
                "carga": f"{a}→{b}",
            })

    return {
        "plugin": "PLUGIN_ARCO_DRAMATICO",
        "engine_tocado": False,
        "nuevas_hipotesis_244": 0,
        "regla": "Tres lecturas. VACIO se deja. No encajar de a huevo.",
        "para_que": (
            "Ver si la trazabilidad de una vida/época SE NOTA como cinta "
            "(Field), como catálogo de momentos (Snyder) o como volteo de valor "
            "(McKee). Hueco = dato. No es predecir el iPhone."
        ),
        "matices": {
            "Field": "arquitectura del tiempo",
            "Snyder": "momentos de taller comercial",
            "McKee": "carga de valor que se voltea",
        },
        "field": field,
        "snyder": snyder,
        "mckee": mckee,
        "mckee_volteos": volteos,
        "n_snyder_vacios": sum(1 for x in snyder if x["estado"] == "VACIO"),
        "n_field_sin_nota": sum(1 for x in field if not x["se_nota"]),
    }


if __name__ == "__main__":
    import json
    demo = [
        {"id": "A", "delta_max": 0.02, "delta_neto": 0.01},
        {"id": "B", "delta_max": 0.12, "delta_neto": 0.10},
        {"id": "C", "delta_max": 0.08, "delta_neto": -0.06},
        {"id": "D", "delta_max": 0.03, "delta_neto": -0.02},
        {"id": "E", "delta_max": 0.11, "delta_neto": 0.09},
    ]
    print(json.dumps(leer(demo), ensure_ascii=False, indent=2))
