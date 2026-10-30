#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hipótesis abiertas y apuesta posterior basada en trayectoria para el motor de trabajo U6.

No modifica Engine_V5_CANONICO_SOLO.py ni patterns_final_v14.json.
El universo de hipótesis tiene cardinalidad variable; H1/H2 son alias históricos,
no una restricción del conjunto. La apuesta se construye DESPUÉS del conjunto y
puede agrupar varias hipótesis en escenarios comunes. Ningún peso es probabilidad.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from typing import Any, Dict, List, Sequence
import math

VERSION = "HIPOTESIS_TRAYECTORIA_ABIERTA_V1_WORKING"


def _num(v, default=0.0):
    try:
        x = float(v)
        return x if math.isfinite(x) else default
    except (TypeError, ValueError):
        return default


def _direction(feat: Dict[str, Any], n_cuts: int) -> Dict[str, Any]:
    micro = _num(feat.get("trajectory_micro_support"), 0.5)
    meso = _num(feat.get("trajectory_meso_support"), 0.5)
    macro = _num(feat.get("trajectory_macro_support"), 0.5)
    acc = _num(feat.get("trajectory_acceleration_support"), 0.5)
    vals = [micro, meso, macro]
    signal = sum(2.0 * x - 1.0 for x in vals) / len(vals)
    conflict = max(vals) - min(vals)
    if n_cuts < 2:
        regime = "SIN_TRAYECTORIA_SUFICIENTE"
    elif conflict >= 0.48 or ((micro - 0.5) * (macro - 0.5) < -0.015):
        regime = "GIRO_O_DIVERGENCIA_MULTIESCALA"
    elif signal > 0.12:
        regime = "CONTINUIDAD_ASCENDENTE"
    elif signal < -0.12:
        regime = "CONTINUIDAD_DESCENDENTE"
    else:
        regime = "MESeta_O_ESTABILIZACION"
    return {"regimen": regime, "senal_multiescala": round(signal, 6),
            "micro": round(micro, 6), "meso": round(meso, 6),
            "macro": round(macro, 6), "aceleracion": round(acc, 6),
            "divergencia_entre_escala": round(conflict, 6),
            "n_cortes_observados": n_cuts}


def _construir_impl(result: Dict[str, Any], case: Dict[str, Any], patterns: Dict[str, Any] | None = None) -> Dict[str, Any]:
    pred = result.get("predictor") or {}
    candidates = [c for c in (pred.get("candidates") or []) if isinstance(c, dict) and c.get("family")]
    candidates.sort(key=lambda c: (-_num(c.get("rank_fusion")), str(c.get("family"))))
    n_cuts = len(case.get("cuts") or [])
    p021 = result.get("hipotesis_necesarias_suficientes") or {}
    geo = result.get("geometria_multicapa") or {}
    trace_support = {str(k): int(v) for k, v in (geo.get("candidate_trace_support") or {}).items()}
    members = [m for m in (p021.get("miembros") or []) if isinstance(m, dict) and m.get("familia")]
    member_by_name = {str(m["familia"]): m for m in members}
    if members:
        selected_names = set(member_by_name)
        # Keep the sufficient set, then preserve candidates with repeated explicit links in temporal/geometry traces.
        trace_complements = {c["family"] for c in candidates
                             if c["family"] not in selected_names and trace_support.get(str(c["family"]), 0) >= 2}
        for name in trace_complements:
            member_by_name[name] = {"familia": name, "rol": "complementaria_trazabilidad_geometrica",
                                    "cobertura_unica_frac": None, "cortes_unicos": []}
        selected = [c for c in candidates if c["family"] in member_by_name]
        selection_status = "SET_021_MAS_COMPLEMENTARIAS_DE_TRAZABILIDAD" if trace_complements else "SET_NECESARIO_SUFICIENTE_021"
    elif candidates:
        # No cardinality cap: preserve the whole observed candidate universe if the set module failed.
        selected = list(candidates)
        selection_status = "FALLBACK_UNIVERSO_COMPLETO_SIN_MAXIMO"
    else:
        selected = []
        selection_status = "SIN_CANDIDATAS"

    max_rank = max((_num(c.get("rank_fusion")) for c in selected), default=0.0)
    min_rank = min((_num(c.get("rank_fusion")) for c in selected), default=0.0)
    # Shift negative/zero scores only for relative structural weighting, not probability.
    shifted = {c["family"]: max(0.0, _num(c.get("rank_fusion")) - min(0.0, min_rank)) for c in selected}
    total = sum(shifted.values())
    if total <= 0 and selected:
        shifted = {c["family"]: 1.0 for c in selected}; total = float(len(selected))

    observed_tokens = Counter()
    for c in selected:
        pat = (patterns or {}).get(c["family"], {}) if isinstance(patterns, dict) else {}
        for token in set((pat.get("tokens_favor") or {})) | set((pat.get("tokens_contra") or {})):
            observed_tokens[str(token)] += 1
    shared_tokens = [{"token": t, "n_hipotesis": n} for t, n in sorted(observed_tokens.items(), key=lambda x: (-x[1], x[0])) if n >= 2]

    hypotheses = []
    scenarios = defaultdict(list)
    for c in selected:
        name = str(c["family"])
        feat = c.get("features") or {}
        trajectory = _direction(feat, n_cuts)
        rank = _num(c.get("rank_fusion"))
        rel = shifted.get(name, 0.0) / total if total else 0.0
        member = member_by_name.get(name, {})
        h = {
            "id": f"H_{len(hypotheses)+1:03d}", "familia": name,
            "rank_fusion": rank,
            "soporte_estructural_relativo": round(rel, 8),
            "es_probabilidad": False,
            "rol_en_set": member.get("rol", "alternativa_del_universo_observado"),
            "cobertura_unica_frac": member.get("cobertura_unica_frac"),
            "cortes_unicos": member.get("cortes_unicos", []),
            "trazabilidad_geometrica": trajectory,
            "enlaces_traza_multicapa": trace_support.get(name, 0),
            "contexto_geometrico_multicapa": {
                "estado": geo.get("status", "NO_DISPONIBLE"),
                "ricci_billar_por_prefijo": ((geo.get("sidecar_latentes") or {}).get("ricci_billar_por_prefijo") or {}).get("por_corte", {}),
                "convergencia_pares_tableros": ((geo.get("convergencia_multinivel") or {}).get("pares_tableros") or {}),
                "jerarquia_recursiva": (geo.get("teseracto") or {}).get("recursive_hierarchy"),
                "helice": (geo.get("teseracto") or {}).get("helical_trace"),
                "geometria_es_descriptiva_no_fisica": True,
            },
            "evidencia_vectorial": {k: feat.get(k) for k in (
                "geometric_inertia_alignment", "geometric_direction_change",
                "trajectory_micro_support", "trajectory_meso_support", "trajectory_macro_support",
                "trajectory_acceleration_support", "trajectory_multiscale_convergence",
                "trajectory_inertia_alignment", "trajectory_curvature_response") if k in feat},
        }
        hypotheses.append(h)
        scenarios[trajectory["regimen"]].append(h)

    scenario_rows = []
    for regime, hs in scenarios.items():
        mass = sum(h["soporte_estructural_relativo"] for h in hs)
        scenario_rows.append({
            "escenario": regime,
            "hipotesis_que_convergen": [h["familia"] for h in hs],
            "n_hipotesis": len(hs),
            "soporte_estructural_agregado": round(mass, 8),
            "es_probabilidad": False,
            "lectura": "convergencia de trayectorias de las hipótesis; soporte relativo, no probabilidad calibrada",
        })
    scenario_rows.sort(key=lambda x: (-x["soporte_estructural_agregado"], x["escenario"]))

    if not selected:
        forecast = {"estado": "SIN_HIPOTESIS", "escenarios": [], "apuesta_principal": None,
                    "motivo": "No hay candidatas observadas suficientes; no se inventa una apuesta."}
    elif n_cuts < 2:
        forecast = {"estado": "TRAYECTORIA_INSUFICIENTE", "escenarios": scenario_rows,
                    "apuesta_principal": None,
                    "motivo": "Se requiere al menos una transición observada para inferir inercia."}
    else:
        forecast = {"estado": "APUESTA_MULTIESCENARIO_SELLABLE", "escenarios": scenario_rows,
                    "apuesta_principal": scenario_rows[0] if scenario_rows else None,
                    "regla": "primero se forma el set abierto de hipótesis; después se agrupan continuaciones de trayectoria compartidas",
                    "horizonte": "siguiente_corte",
                    "no_es_forzoso_que_el_desenlace_coincida_con_una_hipotesis_individual": True,
                    "calibracion": "NO_CALIBRADA_SIN_DESENLACES_POSTERIORES_SELLADOS"}

    all_names = {str(c["family"]) for c in candidates}
    selected_names = {h["familia"] for h in hypotheses}
    excluded = [{"familia": c["family"], "rank_fusion": _num(c.get("rank_fusion")),
                 "motivo": "fuera_del_set_necesario_suficiente_021; se conserva como alternativa diagnóstica"}
                for c in candidates if str(c["family"]) in (all_names - selected_names)]
    return {
        "version": VERSION,
        "estado": "EJECUTADO",
        "cardinalidad_fija": False,
        "maximo_hipotesis": None,
        "n_hipotesis": len(hypotheses),
        "metodo_seleccion": selection_status,
        "hipotesis": hypotheses,
        "alternativas_fuera_del_set": excluded,
        "tokens_compartidos_entre_hipotesis": shared_tokens,
        "trazabilidad_geometrica": {
            "fuente": "predictor.candidates.features + P/A/C por cortes + R732 + sidecar_latentes + convergencia_multinivel + teseracto",
            "multiescala": ["micro", "meso", "macro", "aceleracion", "persistencia", "curvatura/giros", "Ricci-Forman proxy", "Billard", "Tusi", "convergencia entre tableros"],
            "contexto_multicapa_status": geo.get("status", "NO_DISPONIBLE"),
            "candidate_trace_support": trace_support,
            "sin_uso_de_datos_posteriores_a_Z": True,
            "los_modulos_geometricos_no_son_probabilidades": True,
            "jerarquia_recursiva_y_helice_son_diagnosticos_descriptivos_no_prueba_fisica": True,
        },
        "apuesta": forecast,
        "compatibilidad": {
            "H1_H2": "alias históricos; no delimitan el conjunto ni obligan a que el desenlace sea uno de ellos",
            "motor_canonico_modificado": False,
            "catalogo_244_modificado": False,
        },
    }


def _ceb_from_result(result: Dict[str, Any]):
    """Obtiene el verificador CEB del ObservableDict del núcleo, si esta corrida lo instrumenta."""
    motor = result.get("motor") if isinstance(result, dict) else None
    ceb = getattr(motor, "_ceb", None)
    if ceb is not None and callable(getattr(ceb, "call", None)):
        return ceb
    return None


def construir(result: Dict[str, Any], case: Dict[str, Any], patterns: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Instrumenta la ejecución lateral en CEB sin alterar su cálculo ni su salida."""
    ceb = _ceb_from_result(result)
    if ceb is None:
        return _construir_impl(result, case, patterns)
    return ceb.call(
        "hipotesis_trayectoria_abierta_v1",
        lambda: _construir_impl(result, case, patterns),
        shared=[result, case],
    )
