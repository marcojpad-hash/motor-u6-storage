#!/usr/bin/env python3
"""Marcador geométrico de límite para trayectorias P/A/C — V0.1.

Opera sobre la geometría R732 ya calculada. No crea familias, no altera los 244
patrones, no escribe H y no incorpora información posterior al prefijo observado.

Modos:
- ESTIMADO_DESDE_PREFIJO: solo diagnostica contracción/inmovilidad/curvatura en
  los cortes observados. No afirma que el proceso haya llegado a su final.
- RETROSPECTIVO_CON_LIMITE: permite medir distancia geométrica al corte terminal
  únicamente cuando ese corte está incluido en la secuencia. No debe pasarse a
  una corrida predictiva congelada.

Las etiquetas de régimen son heurísticas descriptivas, no probabilidades.
"""
from __future__ import annotations
from typing import Any, Dict, Mapping, Sequence
import math

VERSION = "MARCARDOR_LIMITE_GEOMETRICO_V0_1"
MODOS = {"ESTIMADO_DESDE_PREFIJO", "RETROSPECTIVO_CON_LIMITE"}


def _finite(x: Any) -> bool:
    try:
        return math.isfinite(float(x))
    except (TypeError, ValueError):
        return False


def _clip(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, float(x)))


def _cut_id(cut: Mapping[str, Any], i: int) -> str:
    return str(cut.get("corte", cut.get("id", f"C{i+1}")))


def _median(xs: Sequence[float]) -> float:
    vals = sorted(float(x) for x in xs if _finite(x))
    if not vals:
        return 0.0
    n = len(vals)
    return vals[n//2] if n % 2 else (vals[n//2-1] + vals[n//2]) / 2.0


def evaluar_marcador(
    X_by_cut: Sequence[Sequence[float]],
    cuts: Sequence[Mapping[str, Any]],
    dX_norm: Sequence[float],
    persist_cos: Sequence[float],
    kappa_dir: Sequence[float],
    spec: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    spec = dict(spec or {})
    modo = str(spec.get("modo", "ESTIMADO_DESDE_PREFIJO")).upper()
    if modo not in MODOS:
        raise ValueError(f"modo no válido: {modo}")
    n = min(len(X_by_cut), len(cuts))
    if n == 0:
        return {
            "version": VERSION, "status": "SIN_TRAYECTORIA", "modo": modo,
            "can_decide_H": False, "feeds_H": False, "rank_effect": "NONE",
            "future_accessed": False, "per_cut": [],
        }

    ids = [_cut_id(cuts[i], i) for i in range(n)]
    xs = [[float(v) for v in X_by_cut[i]] for i in range(n)]
    if len({len(v) for v in xs}) != 1 or not xs[0]:
        raise ValueError("X_by_cut debe conservar dimensión constante y no vacía")
    if any(not _finite(v) for row in xs for v in row):
        raise ValueError("X_by_cut contiene valor no finito")

    dx = [float(v) for v in dX_norm[:max(0, n-1)]]
    pc = [float(v) for v in persist_cos]
    kap = [float(v) for v in kappa_dir]
    per_cut = []
    prior_moves = []
    contraction_streak = 0
    acceleration_streak = 0
    for i in range(n):
        if i == 0:
            move = 0.0
            prev_med = 0.0
            ratio = 1.0
            slope = 0.0
            persist = 0.0
            curvature = 0.0
            regime = "INSUFICIENTE"
        else:
            move = dx[i-1] if i-1 < len(dx) else 0.0
            hist = prior_moves[-3:]
            prev_med = _median(hist)
            ratio = move / prev_med if prev_med > 1e-12 else (1.0 if move <= 1e-12 else 2.0)
            trend_values = (prior_moves + [move])[-4:]
            slope = (trend_values[-1] - trend_values[0]) / max(1, len(trend_values)-1)
            persist = pc[i-2] if i >= 2 and i-2 < len(pc) else 0.0
            curvature = kap[i-2] if i >= 2 and i-2 < len(kap) else 0.0
            if prev_med > 1e-12 and ratio < 0.75:
                contraction_streak += 1
            else:
                contraction_streak = 0
            if prev_med > 1e-12 and ratio > 1.25:
                acceleration_streak += 1
            else:
                acceleration_streak = 0
            if i < 2:
                regime = "INSUFICIENTE"
            elif move <= 1e-12 and prev_med <= 1e-12:
                regime = "INMOVILIDAD_OBSERVADA"
            elif contraction_streak >= 2 and move <= prev_med:
                regime = "CONVERGENCIA_CANDIDATA"
            elif acceleration_streak >= 2:
                regime = "MOVIMIENTO_ACELERADO"
            elif curvature >= 0.8:
                regime = "GIRO_FUERTE"
            elif persist >= 0.5 and move > 1e-12:
                regime = "MOVIMIENTO_PERSISTENTE"
            else:
                regime = "IRREGULAR_O_MIXTO"
        quiescence = _clip(1.0 - min(1.0, ratio)) if i > 0 else 0.0
        row = {
            "corte": ids[i], "cut_index": i,
            "movement_norm": round(move, 9),
            "prior_movement_median": round(prev_med, 9),
            "movement_ratio_to_prior": round(ratio, 9),
            "movement_trend_per_step": round(slope, 9),
            "directional_persistence_cos": round(_clip(persist, -1.0, 1.0), 9),
            "directional_curvature": round(_clip(curvature), 9),
            "quiescence_index_heuristic": round(quiescence, 9),
            "regime": regime,
            "is_terminal": False,
            "terminal_distance_available": False,
        }
        per_cut.append(row)
        if i > 0:
            prior_moves.append(move)

    terminal_id = None
    if modo == "RETROSPECTIVO_CON_LIMITE":
        terminal_id = str(spec.get("terminal_cut_id", ""))
        if not terminal_id or terminal_id not in ids:
            raise ValueError("RETROSPECTIVO_CON_LIMITE requiere terminal_cut_id presente en los cortes")
        end_i = ids.index(terminal_id)
        end_x = xs[end_i]
        raw_distances = []
        for i in range(n):
            dist = math.sqrt(sum((xs[i][j] - end_x[j]) ** 2 for j in range(len(end_x))))
            raw_distances.append(dist)
        max_dist = max(raw_distances) if raw_distances else 0.0
        path_remaining = [sum(dx[i:end_i]) if i < end_i else 0.0 for i in range(n)]
        max_path = max(path_remaining) if path_remaining else 0.0
        for i, row in enumerate(per_cut):
            row["is_terminal"] = i == end_i
            row["terminal_distance_available"] = True
            row["distance_to_terminal_state"] = round(raw_distances[i], 9)
            row["distance_to_terminal_normalized"] = round(raw_distances[i] / max_dist, 9) if max_dist > 1e-12 else 0.0
            row["path_length_remaining_to_terminal"] = round(path_remaining[i], 9)
            row["path_remaining_normalized"] = round(path_remaining[i] / max_path, 9) if max_path > 1e-12 else 0.0

    last = per_cut[-1]
    return {
        "version": VERSION,
        "status": "EXECUTED_DIAGNOSTIC",
        "modo": modo,
        "terminal_cut_id": terminal_id if modo == "RETROSPECTIVO_CON_LIMITE" else "NO_EXPOSED_IN_FORECAST",
        "n_cuts": n,
        "dimension_state_vector": len(xs[0]),
        "per_cut": per_cut,
        "current_marker": {k: last[k] for k in (
            "corte", "movement_norm", "prior_movement_median", "movement_ratio_to_prior",
            "movement_trend_per_step", "directional_persistence_cos", "directional_curvature",
            "quiescence_index_heuristic", "regime")},
        "interpretation": {
            "quiescence_index_heuristic": "descriptive_heuristic_not_probability",
            "regime_labels": "diagnostic_only_not_terminal_claim",
            "retrospective_terminal_distance": "available_only_when_terminal_cut_is_included",
        },
        "can_decide_H": False,
        "feeds_H": False,
        "rank_effect": "NONE",
        "future_accessed_in_predictive_path": False,
        "retrospective_endpoint_used": modo == "RETROSPECTIVO_CON_LIMITE",
        "canonical_engine_modified": False,
        "canonical_patterns_modified": False,
    }



def integrar_funciones_souriau(marker: Mapping[str, Any], souriau: Mapping[str, Any]) -> Dict[str, Any]:
    """Anexa ciclo/recurrencia de funciones al marcador sin tocar el ranking.

    La recurrencia se calcula sobre las funciones presentes por corte. El turnover
    de asignaciones es una distancia de conjuntos, no una probabilidad ni una
    afirmación sobre estados psicológicos.
    """
    import copy
    out = copy.deepcopy(dict(marker))
    rows = out.get("per_cut") or []
    por_corte = list(souriau.get("por_corte") or [])
    inertia = list(souriau.get("inercia") or [])
    if not rows or not por_corte:
        out["funciones_souriau"] = {"status": "SIN_DATOS", "n_cortes": 0}
        out["can_decide_H"] = False
        out["feeds_H"] = False
        out["rank_effect"] = "NONE"
        return out

    prev_signature = None
    signature_seen: dict[tuple, int] = {}
    prev_assignments: set[tuple[str, str]] = set()
    last_turnover = 0.0
    last_signature = ()
    enriched = []
    for i, row in enumerate(rows):
        frow = por_corte[i] if i < len(por_corte) else {}
        functions = frow.get("funciones") or {}
        active = tuple(sorted(str(fn) for fn, vals in functions.items() if vals))
        assignments = set()
        for fn, vals in functions.items():
            if isinstance(vals, (list, tuple, set)):
                for val in vals:
                    assignments.add((str(fn), str(val)))
            elif vals:
                assignments.add((str(fn), str(vals)))
        union = prev_assignments | assignments
        turnover = (len(prev_assignments ^ assignments) / len(union)) if union else 0.0
        repeat_index = signature_seen.get(active) if active else None
        repeat_cut = rows[repeat_index].get("corte") if repeat_index is not None else "NO_REPETICION"
        period = i - repeat_index if repeat_index is not None else 0
        if active and active not in signature_seen:
            signature_seen[active] = i
        inertia_row = inertia[i-1] if i > 0 and i-1 < len(inertia) else {}
        moves = list(inertia_row.get("leon_pasa_a_marte") or [])
        function_changes = list(inertia_row.get("cambios_de_funcion") or [])
        enriched_row = dict(row)
        enriched_row.update({
            "funciones_activas": list(active),
            "n_funciones_activas": len(active),
            "asignaciones_funcionales_n": len(assignments),
            "turnover_funcional_desde_corte_anterior": round(turnover, 9) if i else 0.0,
            "cambios_de_funcion_reportados": len(function_changes),
            "transiciones_leon_a_marte": len(moves),
            "quieto_segun_inercia_souriau": (bool(inertia_row.get("quieto")) if assignments and i else ("SIN_DATOS" if not assignments else True)),
            "asignacion_funcional_observada": bool(assignments),
            "firma_funcional_recurrente": bool(repeat_index is not None),
            "repite_firma_de_corte": repeat_cut,
            "periodo_de_recurrencia": period,
        })
        enriched.append(enriched_row)
        prev_assignments = assignments
        prev_signature = active
        last_turnover = turnover
        last_signature = active

    current = dict(out.get("current_marker") or {})
    if enriched:
        current.update({k: enriched[-1][k] for k in (
            "funciones_activas", "n_funciones_activas", "asignaciones_funcionales_n",
            "turnover_funcional_desde_corte_anterior", "cambios_de_funcion_reportados",
            "transiciones_leon_a_marte", "quieto_segun_inercia_souriau", "asignacion_funcional_observada",
            "firma_funcional_recurrente", "repite_firma_de_corte", "periodo_de_recurrencia")})
    movement_ratio = float(current.get("movement_ratio_to_prior", 1.0))
    movement_trend = float(current.get("movement_trend_per_step", 0.0))
    if len(enriched) < 3:
        joint_regime = "INSUFICIENTE"
    elif movement_ratio < 0.75 and movement_trend <= 0 and last_turnover <= 1e-12:
        joint_regime = "QUIESCENCIA_CONJUNTA_CANDIDATA"
    elif movement_ratio < 0.75 and last_turnover > 1e-12:
        joint_regime = "GEOMETRIA_SE_FRENA_FUNCIONES_CAMBIAN"
    elif movement_ratio >= 1.0 and last_turnover <= 1e-12:
        joint_regime = "FUNCIONES_ESTABLES_CON_MOVIMIENTO"
    elif bool(current.get("firma_funcional_recurrente")):
        joint_regime = "RECURRENCIA_FUNCIONAL"
    else:
        joint_regime = "DINAMICA_MIXTA"
    out["per_cut"] = enriched
    out["current_marker"] = current
    out["joint_geometric_function_regime"] = joint_regime
    out["funciones_souriau"] = {
        "status": "INTEGRATED_DIAGNOSTIC",
        "source_status": souriau.get("status", "UNSPECIFIED"),
        "n_cortes_funcionales": len(por_corte),
        "active_function_signature_current": list(last_signature),
        "turnover_funcional_actual": round(last_turnover, 9),
        "repeticiones_de_firma": sum(1 for r in enriched if r.get("firma_funcional_recurrente")),
        "joint_regime": joint_regime,
        "interpretation": "recurrencia funcional y quiescencia conjunta son descriptores; no prueban un final ni un equilibrio termodinámico",
    }
    out["can_decide_H"] = False
    out["feeds_H"] = False
    out["rank_effect"] = "NONE"
    return out


__all__ = ["VERSION", "MODOS", "evaluar_marcador", "integrar_funciones_souriau"]
