#!/usr/bin/env python3
"""Sidecar Polti/Caldero — interfaz al MOTOR, no a un dataset.

Entrada: salida de MOTOR_V15_3_NATIVO.correr_5x3 (cualquier caso).
No lee MUSK_*.json. No escribe H1/H2.
Alimenta_H = NO.

Capa A: las 36 Polti y arquetipos ya están en el 244 (tablero).
Capa B: este sidecar observa ese tablero + R732 y produce
señales de transición/proyección/convergencia para ANTES de H.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List

ALIMENTA_H = "NO"
RX_POLTI = re.compile(r"^(\d+)_")
RX_ARQ = re.compile(r"^arquetipo_")


def _tops(rows, n=5):
    return [[name, float(p)] for name, p in rows[:n]] if rows else []


def _from_cut(cut: Dict[str, Any], eje: str) -> List[List[Any]]:
    key = f"{eje}_top5_ANEXO"
    return list(cut.get(key) or [])


def _filter(rows: List[List[Any]], rx) -> List[List[Any]]:
    out = []
    for item in rows:
        if not item:
            continue
        name = item[0]
        p = float(item[1]) if len(item) > 1 else 0.0
        if rx.match(str(name)):
            out.append([name, p])
    return out


def _transicion(prev: List[List[Any]], curr: List[List[Any]]) -> Dict[str, Any]:
    a = {n: p for n, p in prev}
    b = {n: p for n, p in curr}
    names = sorted(set(a) | set(b))
    mov = []
    for n in names:
        d = b.get(n, 0.0) - a.get(n, 0.0)
        # Missing family in a top-five list means zero in this transition calculation;
        # serialize the same value used by d instead of leaking None into p_de/p_a.
        mov.append({"h": n, "p_de": a.get(n, 0.0), "p_a": b.get(n, 0.0), "d": round(d, 6)})
    mov.sort(key=lambda x: -abs(x["d"] or 0))
    return {"movimiento": mov[:8], "sube": [m["h"] for m in mov if (m["d"] or 0) > 0][:3],
            "baja": [m["h"] for m in mov if (m["d"] or 0) < 0][:3]}


def observar_corrida(motor_out: Dict[str, Any]) -> Dict[str, Any]:
    cuts = list(motor_out.get("cuts") or [])
    r732 = motor_out.get("R732") or {}
    polti_por_corte = []
    arq_por_corte = []
    for c in cuts:
        p_rows = _from_cut(c, "P")
        a_rows = _from_cut(c, "A")
        c_rows = _from_cut(c, "C")
        merged = p_rows + a_rows + c_rows
        polti_por_corte.append({
            "corte": c.get("corte"),
            "P": _filter(p_rows, RX_POLTI),
            "A": _filter(a_rows, RX_POLTI),
            "C": _filter(c_rows, RX_POLTI),
            "union": _filter(merged, RX_POLTI)[:8],
        })
        arq_por_corte.append({
            "corte": c.get("corte"),
            "P": _filter(p_rows, RX_ARQ),
            "A": _filter(a_rows, RX_ARQ),
            "C": _filter(c_rows, RX_ARQ),
            "union": _filter(merged, RX_ARQ)[:8],
        })

    trans = []
    for i in range(1, len(polti_por_corte)):
        trans.append({
            "tramo": f"{polti_por_corte[i-1]['corte']}→{polti_por_corte[i]['corte']}",
            "polti": _transicion(polti_por_corte[i-1]["union"], polti_por_corte[i]["union"]),
            "arquetipos": _transicion(arq_por_corte[i-1]["union"], arq_por_corte[i]["union"]),
        })

    last_p = (polti_por_corte[-1]["union"] if polti_por_corte else [])
    last_a = (arq_por_corte[-1]["union"] if arq_por_corte else [])
    proyeccion = {
        "nota": "Proyección = inercia del último tablero Polti/arquetipo. No es H.",
        "polti_persistentes": [x[0] for x in last_p[:3]],
        "arquetipos_persistentes": [x[0] for x in last_a[:3]],
        "dX_norm": r732.get("dX_norm"),
        "persist_cos": r732.get("persist_cos"),
        "kappa_dir": r732.get("kappa_dir"),
        "n_cuts": len(cuts),
    }
    convergencia = {
        "en_tubo_y_polti": [x[0] for x in last_p],
        "en_tubo_y_arquetipo": [x[0] for x in last_a],
        "solo_polti_visible": [x[0] for x in last_p],
        "solo_arquetipo_visible": [x[0] for x in last_a],
    }
    return {
        "sidecar": "polti_caldero",
        "entrada": "motor_out.cuts + R732",
        "dataset_hardcode": False,
        "Alimenta_H": ALIMENTA_H,
        "escribe_H": False,
        "polti_por_corte": polti_por_corte,
        "arquetipos_por_corte": arq_por_corte,
        "transicion": trans,
        "proyeccion": proyeccion,
        "convergencia": convergencia,
        "uso": "Señales para formular H. No son H.",
    }
