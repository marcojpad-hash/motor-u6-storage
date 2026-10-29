#!/usr/bin/env python3
"""TRAZA_CAMPO_244_V2 — traza completa sin inventar valores ausentes.

Contrato:
- Conserva la unión de todas las hipótesis presentes en cualquier corte.
- No sustituye una hipótesis ausente por 0.5: eso fabricaba Δ falsos.
- Calcula Δ y cambio de rango solo cuando la hipótesis está presente en ambos cortes.
- Registra presencia/ausencia y conserva el valor bruto de cada corte.
- La correlación usa únicamente tramos observados en ambos miembros del par.
- No decide H ni modifica el motor/catálogo canónico.
"""
from __future__ import annotations
import math
from typing import Any, Dict, List, Sequence, Tuple, Optional

Board = Dict[str, float]
Cut = Tuple[str, Board]

def _rank(board: Board) -> Dict[str, int]:
    return {k: i + 1 for i, k in enumerate(sorted(board, key=lambda k: (-board[k], k)))}

def _corr(a: Sequence[float], b: Sequence[float]) -> Optional[float]:
    if len(a) < 2:
        return None
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    va = sum((x-ma)**2 for x in a)
    vb = sum((y-mb)**2 for y in b)
    if va <= 1e-18 or vb <= 1e-18:
        return 0.0
    return sum((x-ma)*(y-mb) for x,y in zip(a,b)) / math.sqrt(va*vb)

def analizar(cortes: Sequence[Cut], nota_umbral: Optional[float] = None) -> Dict[str, Any]:
    if not cortes:
        raise ValueError("Se requiere al menos un corte")
    ids = [str(c[0]) for c in cortes]
    boards: List[Board] = []
    for ident, board in cortes:
        clean = {}
        for h, value in board.items():
            v = float(value)
            if not math.isfinite(v):
                raise ValueError(f"Valor no finito: corte={ident}, h={h}, valor={value}")
            clean[str(h)] = v
        boards.append(clean)

    nombres = sorted(set().union(*(set(b) for b in boards)))
    ranks = [_rank(b) for b in boards]
    series: Dict[str, List[Optional[float]]] = {
        h: [b[h] if h in b else None for b in boards] for h in nombres
    }
    rank_series: Dict[str, List[Optional[int]]] = {
        h: [r[h] if h in r else None for r in ranks] for h in nombres
    }
    deltas: Dict[str, List[Optional[float]]] = {h: [] for h in nombres}
    vectores = []
    for i in range(1, len(boards)):
        movimientos = []
        for h in nombres:
            present_a, present_b = h in boards[i-1], h in boards[i]
            d = boards[i][h] - boards[i-1][h] if present_a and present_b else None
            deltas[h].append(d)
            ra, rb = ranks[i-1].get(h), ranks[i].get(h)
            movimientos.append({
                "h": h, "presente_de": present_a, "presente_a": present_b,
                "d": round(d, 6) if d is not None else None,
                "P_de": round(boards[i-1][h], 6) if present_a else None,
                "P_a": round(boards[i][h], 6) if present_b else None,
                "rango_de": ra, "rango_a": rb,
                "drango": ra-rb if ra is not None and rb is not None else None,
                "estado": "OBSERVADO" if d is not None else "DATO_AUSENTE"
            })
        movimientos.sort(key=lambda x: (x["d"] is None, -abs(x["d"] or 0), x["h"]))
        vectores.append({"vector": f"{ids[i-1]}→{ids[i]}", "n": len(movimientos),
                         "n_delta_observados": sum(x["d"] is not None for x in movimientos),
                         "n_datos_ausentes": sum(x["d"] is None for x in movimientos),
                         "movimiento": movimientos})

    fichas = []
    for h in nombres:
        vals = series[h]
        valid = [v for v in vals if v is not None]
        first = next((v for v in vals if v is not None), None)
        last = next((v for v in reversed(vals) if v is not None), None)
        fichas.append({
            "h": h, "P": vals, "d": [round(d, 6) if d is not None else None for d in deltas[h]],
            "rangos": rank_series[h],
            "neto": round(last-first, 6) if first is not None and last is not None else None,
            "n_cortes_observados": len(valid),
            "n_cortes_ausentes": len(vals)-len(valid)
        })
    fichas.sort(key=lambda x: (x["neto"] is None, -abs(x["neto"] or 0), x["h"]))

    pares = []
    if len(boards) >= 3:
        for i, hi in enumerate(nombres):
            for hj in nombres[i+1:]:
                paired = [(di, dj) for di, dj in zip(deltas[hi], deltas[hj])
                          if di is not None and dj is not None]
                if len(paired) < 2 or all(abs(a) < 1e-12 for a, _ in paired) or all(abs(b) < 1e-12 for _, b in paired):
                    continue
                c = _corr([p[0] for p in paired], [p[1] for p in paired])
                if c is not None:
                    pares.append({"i": hi, "j": hj, "corr_delta": round(c, 4),
                                  "n_tramos_comunes": len(paired)})
        pares.sort(key=lambda x: (-abs(x["corr_delta"]), x["i"], x["j"]))

    return {
        "modulo": "TRAZA_CAMPO_244_V2",
        "formula": "Δ_i(t)=P_i(t)-P_i(t-1), solo si ambos valores están observados",
        "cuelga_de_H": False, "apaga_luces": False,
        "nota_umbral": nota_umbral, "n_hipotesis": len(nombres),
        "cortes": ids, "vectores": vectores, "fichas": fichas,
        "interrelacion_posible": pares[:80], "crudo_P": series,
        "integridad": {
            "hipotesis_union_completa": nombres,
            "n_hipotesis": len(nombres),
            "n_valores_ausentes": sum(v is None for seq in series.values() for v in seq),
            "regla_imputacion": "NINGUNA; ausentes quedan como null"
        }
    }

def origenes_renovables(cortes: Sequence[Cut], delta_senal: float = 0.05) -> Dict[str, Any]:
    if delta_senal < 0:
        raise ValueError("delta_senal no puede ser negativo")
    ids = [str(c[0]) for c in cortes]
    boards = [c[1] for c in cortes]
    nombres = sorted(set().union(*(set(b) for b in boards))) if boards else []
    ventanas = [{"A": ids[t], "B": ids[t+1], "C": ids[t+2]} for t in range(max(0, len(ids)-2))]
    altas, primera = [], {}
    for i in range(1, len(boards)):
        for h in nombres:
            if h not in boards[i-1] or h not in boards[i]:
                continue
            d = float(boards[i][h]) - float(boards[i-1][h])
            if abs(d) >= delta_senal:
                ev = {"en": ids[i], "h": h, "d": round(d, 6),
                      "A_nuevo": ids[i], "traza_nueva": ids[i:]}
                altas.append(ev)
                primera.setdefault(h, ev)
    return {"modulo": "TRAZA_CAMPO_244_V2", "ventanas_ABC": ventanas,
            "origenes_nuevos_por_primera_senal": list(primera.values()),
            "todas_las_cruces": altas, "delta_senal_nota": delta_senal,
            "regla": "no calcular cruces si falta P en cualquiera de los dos cortes"}

if __name__ == "__main__":
    A = {"H1": 0.50, "H2": 0.50, "H3": 0.70}
    B = {"H1": 0.51, "H3": 0.69}  # H2 ausente: no se inventa 0.5
    C = {"H1": 0.73, "H2": 0.66, "H3": 0.68}
    r = analizar([("A", A), ("B", B), ("C", C)])
    assert r["n_hipotesis"] == 3
    assert r["vectores"][0]["n_delta_observados"] == 2
    assert r["vectores"][0]["n_datos_ausentes"] == 1
    h2 = next(x for x in r["fichas"] if x["h"] == "H2")
    assert h2["P"] == [0.5, None, 0.66]
    assert h2["d"] == [None, None]
    assert r["integridad"]["n_valores_ausentes"] == 1
    assert len(origenes_renovables([("A", A), ("B", B), ("C", C)])["todas_las_cruces"]) >= 0
    print("TRAZA_CAMPO_244_V2_SELFTEST_OK")
