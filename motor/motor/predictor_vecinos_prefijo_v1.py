#!/usr/bin/env python3
"""
predictor_vecinos_prefijo_v1.py

Predictor lateral por vecinos mas cercanos para las 15 biografias codificadas.
No modifica el motor bayesiano.

Metodologia implementada:
- Needleman-Wunsch / optimal matching
- costo indel = 1.0
- costo sustitucion = 2.0
- compara SOLO prefijos del mismo largo k
- excluye referencias que no alcanzan k (no las trunca)
- selecciona top-k vecinos
- la etapa siguiente se consulta SOLO despues de seleccionar vecinos
- peso provisional = similitud = 1 - distancia_normalizada
  (esta transformacion debe considerarse parametrizable y pendiente de validacion)

No produce probabilidad poblacional.
"""

from __future__ import annotations
import json
import math
from typing import Dict, List, Any, Tuple

BIOGRAFIAS: Dict[str, List[str]] = {
  "aquiles": ["mundo_ordinario","mentor","llamado_aventura","rechazo_o_duda","cruce_umbral","pruebas_aliados_enemigos","prueba_suprema","recompensa","resurreccion_transformacion"],
  "alejandro_magno": ["mundo_ordinario","mentor","llamado_aventura","cruce_umbral","pruebas_aliados_enemigos","prueba_suprema","recompensa","camino_regreso","resurreccion_transformacion"],
  "julio_cesar": ["mundo_ordinario","llamado_aventura","cruce_umbral","pruebas_aliados_enemigos","prueba_suprema","recompensa","camino_regreso","resurreccion_transformacion","retorno_con_elixir"],
  "genghis_khan": ["mundo_ordinario","rechazo_o_duda","llamado_aventura","cruce_umbral","pruebas_aliados_enemigos","prueba_suprema","recompensa","resurreccion_transformacion"],
  "napoleon": ["mundo_ordinario","mentor","llamado_aventura","cruce_umbral","pruebas_aliados_enemigos","prueba_suprema","recompensa","camino_regreso","resurreccion_transformacion","retorno_con_elixir"],
  "rulfo": ["mundo_ordinario","llamado_aventura","cruce_umbral","pruebas_aliados_enemigos","prueba_suprema","recompensa"],
  "garcia_marquez": ["mundo_ordinario","mentor","llamado_aventura","rechazo_o_duda","cruce_umbral","pruebas_aliados_enemigos","prueba_suprema","recompensa","camino_regreso","resurreccion_transformacion","retorno_con_elixir"],
  "cortazar": ["mundo_ordinario","mentor","llamado_aventura","rechazo_o_duda","cruce_umbral","pruebas_aliados_enemigos","prueba_suprema","recompensa","camino_regreso","resurreccion_transformacion","retorno_con_elixir"],
  "borges": ["mundo_ordinario","mentor","llamado_aventura","cruce_umbral","pruebas_aliados_enemigos","prueba_suprema","recompensa","resurreccion_transformacion","retorno_con_elixir"],
  "hemingway": ["mundo_ordinario","llamado_aventura","rechazo_o_duda","mentor","cruce_umbral","pruebas_aliados_enemigos","prueba_suprema","recompensa","camino_regreso","resurreccion_transformacion"],
  "freddie_mercury": ["mundo_ordinario","llamado_aventura","rechazo_o_duda","cruce_umbral","pruebas_aliados_enemigos","prueba_suprema","recompensa","resurreccion_transformacion"],
  "mozart": ["mundo_ordinario","mentor","llamado_aventura","cruce_umbral","pruebas_aliados_enemigos","prueba_suprema","recompensa"],
  "paganini": ["mundo_ordinario","mentor","llamado_aventura","cruce_umbral","pruebas_aliados_enemigos","prueba_suprema","recompensa","camino_regreso","resurreccion_transformacion"],
  "luis_eduardo_aute": ["mundo_ordinario","llamado_aventura","rechazo_o_duda","cruce_umbral","pruebas_aliados_enemigos","prueba_suprema","recompensa","camino_regreso","resurreccion_transformacion","retorno_con_elixir"],
  "beethoven": ["mundo_ordinario","mentor","llamado_aventura","rechazo_o_duda","cruce_umbral","pruebas_aliados_enemigos","prueba_suprema","recompensa","resurreccion_transformacion","retorno_con_elixir"]
}


def om_dist(a: List[str], b: List[str], indel: float = 1.0, sub: float = 2.0) -> float:
    n, m = len(a), len(b)
    dp = [[0.0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1): dp[i][0] = i * indel
    for j in range(1, m + 1): dp[0][j] = j * indel
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            c = 0.0 if a[i-1] == b[j-1] else sub
            dp[i][j] = min(
                dp[i-1][j-1] + c,
                dp[i-1][j] + indel,
                dp[i][j-1] + indel,
            )
    return dp[n][m]


def normalized_distance_same_length(a: List[str], b: List[str]) -> float:
    if len(a) != len(b):
        raise ValueError("Los prefijos deben tener exactamente el mismo largo")
    if not a:
        return 0.0
    return om_dist(a, b) / (2.0 * len(a))


def predict_next(user_prefix: List[str], top_n: int = 5) -> Dict[str, Any]:
    k = len(user_prefix)
    if k == 0:
        return {"status": "partial", "reason": "prefijo_vacio"}

    eligible = []
    excluded = []
    for name, seq in BIOGRAFIAS.items():
        if len(seq) < k:
            excluded.append({"name": name, "reason": "referencia_mas_corta_que_el_prefijo", "reference_length": len(seq)})
            continue
        ref_prefix = seq[:k]
        d = normalized_distance_same_length(user_prefix, ref_prefix)
        sim = max(0.0, min(1.0, 1.0 - d))
        eligible.append({
            "name": name,
            "distance_normalized": round(d, 6),
            "similarity": round(sim, 6),
            "prefix_length": k,
            "reference_prefix": ref_prefix,
            "next_stage": seq[k] if len(seq) > k else None,
            "reference_length": len(seq),
        })

    eligible.sort(key=lambda x: (-x["similarity"], x["name"]))
    neighbors = eligible[:max(1, top_n)]

    # Aggregate only among selected neighbors. This is an estimate, not a population probability.
    route_weights: Dict[str, float] = {}
    route_sources: Dict[str, List[str]] = {}
    for n in neighbors:
        nxt = n["next_stage"]
        if nxt is None:
            continue
        w = n["similarity"]
        route_weights[nxt] = route_weights.get(nxt, 0.0) + w
        route_sources.setdefault(nxt, []).append(n["name"])
    total = sum(route_weights.values())
    transition_candidates = []
    for stage, raw in route_weights.items():
        transition_candidates.append({
            "next_stage": stage,
            "raw_weight": round(raw, 6),
            "normalized_weight_within_selected_neighbors": round(raw / total, 6) if total else 0.0,
            "supporting_neighbors": route_sources[stage],
        })
    transition_candidates.sort(key=lambda x: (-x["raw_weight"], x["next_stage"]))

    status = "ok" if len(neighbors) >= min(5, len(eligible)) and all(n["next_stage"] is not None for n in neighbors) else "partial"
    return {
        "status": status,
        "stage_current_index": k,
        "prefix_length": k,
        "user_prefix": user_prefix,
        "eligible_reference_count": len(eligible),
        "excluded_references": excluded,
        "neighbors": neighbors,
        "transition_candidates": transition_candidates,
        "weight_function": "similarity = 1 - normalized_distance",
        "weight_function_status": "provisional_unvalidated",
        "disclaimer": "Estimación por vecinos más cercanos entre 15 casos; no es una probabilidad poblacional real.",
    }


def run_fixture() -> Dict[str, Any]:
    # Fixture already present in the historical tracing script; retained only as a reproducible test.
    prefix = [
        "mundo_ordinario",
        "llamado_aventura",
        "rechazo_o_duda",
        "cruce_umbral",
        "pruebas_aliados_enemigos",
    ]
    return predict_next(prefix, top_n=5)


if __name__ == "__main__":
    out = run_fixture()
    print(json.dumps(out, ensure_ascii=False, indent=2))
