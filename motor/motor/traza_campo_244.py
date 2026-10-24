#!/usr/bin/env python3
"""TRAZA_CAMPO_244

Toda hipótesis, todo corte, todo Δ. Nada se apaga.
Umbral no es interruptor: es nota opcional.

Δ_i(t) = P_i(t) − P_i(t−1)

Interrelación (posibilidad, no identidad):
  s_ij = corr(serie Δ_i, serie Δ_j)   si hay ≥2 vectores
  o, en un solo tramo, mismo signo de Δ.

No se cuelga de H. No toca Engine_V5.
"""
from __future__ import annotations

import math
from typing import Any, Dict, List, Sequence, Tuple


def _rank(board: Dict[str, float]) -> Dict[str, int]:
    orden = sorted(board, key=lambda k: -board[k])
    return {k: i + 1 for i, k in enumerate(orden)}


def _corr(a: Sequence[float], b: Sequence[float]):
    n = len(a)
    if n < 2:
        return None
    ma = sum(a) / n
    mb = sum(b) / n
    va = sum((x - ma) ** 2 for x in a)
    vb = sum((y - mb) ** 2 for y in b)
    if va <= 1e-18 or vb <= 1e-18:
        return 0.0
    cov = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    return cov / math.sqrt(va * vb)


def analizar(
    cortes: Sequence[Tuple[str, Dict[str, float]]],
    nota_umbral: float | None = None,
) -> Dict[str, Any]:
    ids = [c[0] for c in cortes]
    boards = [c[1] for c in cortes]
    nombres = sorted(set().union(*[b.keys() for b in boards]))

    serie: Dict[str, List[float]] = {n: [] for n in nombres}
    rangos: Dict[str, List[int]] = {n: [] for n in nombres}
    for b in boards:
        rk = _rank(b)
        for n in nombres:
            serie[n].append(round(float(b.get(n, 0.5)), 6))
            rangos[n].append(rk.get(n, len(nombres) + 1))

    # un vector por tramo: TODAS las Δ
    vectores = []
    deltas_por_h: Dict[str, List[float]] = {n: [] for n in nombres}
    for i in range(1, len(boards)):
        a, b = boards[i - 1], boards[i]
        mov = []
        for n in nombres:
            d = float(b.get(n, 0.5)) - float(a.get(n, 0.5))
            deltas_por_h[n].append(d)
            mov.append({
                "h": n,
                "d": round(d, 6),
                "P_de": round(float(a.get(n, 0.5)), 6),
                "P_a": round(float(b.get(n, 0.5)), 6),
                "rango_de": rangos[n][i - 1],
                "rango_a": rangos[n][i],
                "drango": rangos[n][i - 1] - rangos[n][i],
            })
        mov.sort(key=lambda x: -abs(x["d"]))
        vectores.append({
            "vector": f"{ids[i-1]}→{ids[i]}",
            "n": len(mov),
            "movimiento": mov,  # 244
        })

    fichas = []
    for n in nombres:
        vals = serie[n]
        ds = deltas_por_h[n]
        fichas.append({
            "h": n,
            "P": vals,
            "d": [round(x, 6) for x in ds],
            "rangos": rangos[n],
            "neto": round(vals[-1] - vals[0], 6),
        })
    fichas.sort(key=lambda x: -abs(x["neto"]))

    # interrelación: corr de las series Δ (posibilidad)
    pares = []
    if len(boards) >= 3:
        for i, ni in enumerate(nombres):
            di = deltas_por_h[ni]
            if all(abs(x) < 1e-12 for x in di):
                continue
            for nj in nombres[i + 1:]:
                dj = deltas_por_h[nj]
                if all(abs(x) < 1e-12 for x in dj):
                    continue
                c = _corr(di, dj)
                if c is None:
                    continue
                pares.append({"i": ni, "j": nj, "corr_delta": round(c, 4)})
        pares.sort(key=lambda x: -abs(x["corr_delta"]))

    return {
        "modulo": "TRAZA_CAMPO_244",
        "formula": "Δ_i(t)=P_i(t)-P_i(t-1);  r_ij=corr(Δ_i, Δ_j)",
        "cuelga_de_H": False,
        "apaga_luces": False,
        "nota_umbral": nota_umbral,
        "n_hipotesis": len(nombres),
        "cortes": ids,
        "vectores": vectores,
        "fichas": fichas,
        "interrelacion_posible": pares[:80],
        "crudo_P": serie,
    }


if __name__ == "__main__":
    A = {"H1": 0.50, "H2": 0.50, "H3": 0.70}
    B = {"H1": 0.51, "H2": 0.58, "H3": 0.69}
    C = {"H1": 0.73, "H2": 0.66, "H3": 0.68}
    r = analizar([("A", A), ("B", B), ("C", C)])
    assert r["vectores"][0]["n"] == 3
    print("ok", r["interrelacion_posible"])


# --- origen renovable --------------------------------------------------------
# S_{t+1} = F(S_t, X_{t+1})   el motor ya capitaliza
# Ventana local: (S_t, S_{t+1}, S_{t+2}) = ABC_t
# Si |Δ_i(t)| >= δ_señal por primera vez: A' := t
# No afirma el nombre del fenómeno. Solo reabre origen.

def origenes_renovables(
    cortes: Sequence[Tuple[str, Dict[str, float]]],
    delta_senal: float = 0.05,
) -> Dict[str, Any]:
    ids = [c[0] for c in cortes]
    boards = [c[1] for c in cortes]
    nombres = sorted(set().union(*[b.keys() for b in boards]))
    ventanas = []
    for t in range(len(ids) - 2):
        ventanas.append({"A": ids[t], "B": ids[t + 1], "C": ids[t + 2]})
    altas = []
    for i in range(1, len(boards)):
        a, b = boards[i - 1], boards[i]
        for n in nombres:
            d = float(b.get(n, 0.5)) - float(a.get(n, 0.5))
            if abs(d) >= delta_senal:
                altas.append({
                    "en": ids[i],
                    "h": n,
                    "d": round(d, 6),
                    "A_nuevo": ids[i],
                    "traza_nueva": ids[i:],
                })
    # primera vez que cada h cruza delta_senal
    primera = {}
    for ev in altas:
        primera.setdefault(ev["h"], ev)
    return {
        "formula": "S_{t+1}=F(S_t,X_{t+1}); ABC_t=(S_t,S_{t+1},S_{t+2}); A':=t si |Δ|(t) cruza señal",
        "ventanas_ABC": ventanas,
        "origenes_nuevos_por_primera_senal": list(primera.values()),
        "todas_las_cruces": altas,
        "delta_senal_nota": delta_senal,
    }
