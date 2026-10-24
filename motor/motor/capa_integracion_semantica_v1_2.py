#!/usr/bin/env python3
# CAPA INTEGRACION SEMANTICA V1.2 — TABLERO SEMANTICO INTERRELACIONAL
# Capa lateral experimental. No toca F, 244, Engine_V5, H1/H2 ni apuesta.

from __future__ import annotations
from copy import deepcopy
from typing import Any, Dict, Iterable, Mapping, Sequence, Tuple

TOCA_F = TOCA_244 = TOCA_ENGINE_V5 = TOCA_H1_H2 = TOCA_APUESTA = "NO"

def _unit_id(x: Any) -> str:
    if isinstance(x, str):
        return x
    if isinstance(x, Mapping):
        for k in ("token", "unidad", "id", "name", "nombre"):
            if x.get(k) is not None:
                return str(x[k])
    return str(x)

def _units(values: Iterable[Any] | None) -> list[str]:
    out, seen = [], set()
    for x in values or []:
        u = _unit_id(x)
        if u and u not in seen:
            out.append(u)
            seen.add(u)
    return out

def _activation_observations(values: Iterable[Any] | None) -> list[Dict[str, Any]]:
    out = []
    for x in values or []:
        if isinstance(x, Mapping):
            token = _unit_id(x)
            if not token:
                continue
            obs = {"token": token}
            if "vector" in x:
                obs["vector"] = deepcopy(x["vector"])
                obs["vectorizacion_estado"] = "DECLARADA_POR_CAPA"
            elif "vectorizacion" in x:
                obs["vectorizacion"] = deepcopy(x["vectorizacion"])
                obs["vectorizacion_estado"] = "DECLARADA_POR_CAPA"
            else:
                obs["vectorizacion_estado"] = "NO_VECTOR_DECLARADO"
            for k in ("intensidad", "peso", "familia", "contexto", "evidence_id"):
                if k in x:
                    obs[k] = deepcopy(x[k])
            out.append(obs)
        else:
            out.append({"token": _unit_id(x), "vectorizacion_estado": "NO_VECTOR_DECLARADO"})
    return out

def _normalise_layer(name: str, payload: Any) -> Dict[str, Any]:
    if isinstance(payload, Mapping):
        raw = payload.get("activaciones") or payload.get("observaciones") or []
        units = _units(payload.get("unidades") or payload.get("tokens") or raw)
        relations = deepcopy(list(payload.get("relaciones") or []))
        metadata = deepcopy(dict(payload.get("metadata") or {}))
        observations = _activation_observations(raw)
        if not observations:
            observations = [{"token": u, "vectorizacion_estado": "NO_VECTOR_DECLARADO"} for u in units]
    else:
        units = _units(payload if isinstance(payload, Iterable) else [])
        relations, metadata = [], {}
        observations = [{"token": u, "vectorizacion_estado": "NO_VECTOR_DECLARADO"} for u in units]
    return {"capa": str(name), "unidades": units, "observaciones": observations,
            "relaciones": relations, "metadata": metadata}

def _intersections(sets_by_layer: Mapping[str, set[str]]) -> list[Dict[str, Any]]:
    names, out = list(sets_by_layer), []
    for i, left in enumerate(names):
        for right in names[i + 1:]:
            common = sorted(sets_by_layer[left] & sets_by_layer[right])
            if common:
                out.append({"capas": [left, right], "unidades": common, "cardinalidad": len(common)})
    return out

def _relation_key(r: Mapping[str, Any]) -> Tuple[str, str, str]:
    a = str(r.get("a") or r.get("origen") or r.get("from") or "")
    b = str(r.get("b") or r.get("destino") or r.get("to") or "")
    k = str(r.get("tipo") or r.get("tipo_relacion") or "declarada")
    return a, b, k

def _context_for_token(token: str, layer: Mapping[str, Any], all_units: Sequence[str]) -> Dict[str, Any]:
    relations = []
    for r in layer.get("relaciones", []):
        if not isinstance(r, Mapping):
            continue
        a, b, k = _relation_key(r)
        if token in (a, b):
            relations.append({"a": a, "b": b, "tipo": k})
    return {"coexistentes_en_corte": [u for u in all_units if u != token],
            "relaciones_declaradas": relations}

def configurar_corte(corte_id: Any, capas: Mapping[str, Any]) -> Dict[str, Any]:
    normalizadas = {str(n): _normalise_layer(str(n), p) for n, p in capas.items()}
    sets = {n: set(d["unidades"]) for n, d in normalizadas.items()}
    union = sorted(set().union(*sets.values())) if sets else []

    membership = []
    for unit in union:
        presentes = [n for n in normalizadas if unit in sets[n]]
        membership.append({"unidad": unit, "capas": presentes, "n_capas": len(presentes)})

    by_token: Dict[str, Dict[str, Any]] = {}
    for lname, layer in normalizadas.items():
        for obs in layer["observaciones"]:
            token = obs["token"]
            item = deepcopy(obs)
            item["capa"] = lname
            item["contexto_corte"] = _context_for_token(token, layer, union)
            rec = by_token.setdefault(token, {
                "token": token, "unidad_evidencia": 1,
                "no_duplicar_por_capa": True, "instancias_contextuales": [],
            })
            rec["instancias_contextuales"].append(item)

    observaciones = []
    for token in sorted(by_token):
        rec = by_token[token]
        rec["capas"] = sorted({x["capa"] for x in rec["instancias_contextuales"]})
        rec["n_instancias_contextuales"] = len(rec["instancias_contextuales"])
        observaciones.append(rec)

    return {
        "corte": corte_id,
        "capas": normalizadas,
        "configuracion": {"union_unidades": union,
                          "intersecciones": _intersections(sets),
                          "membresias": membership},
        "observaciones_tokens": observaciones,
        "candados": {"TOCA_F": TOCA_F, "TOCA_244": TOCA_244,
                     "TOCA_Engine_V5": TOCA_ENGINE_V5, "TOCA_H1_H2": TOCA_H1_H2,
                     "TOCA_APUESTA": TOCA_APUESTA},
    }

def comparar_configuraciones(anterior: Mapping[str, Any], actual: Mapping[str, Any]) -> Dict[str, Any]:
    a = set(anterior.get("configuracion", {}).get("union_unidades", []))
    b = set(actual.get("configuracion", {}).get("union_unidades", []))
    prev_rel = {_relation_key(r) for l in anterior.get("capas", {}).values()
                for r in l.get("relaciones", []) if isinstance(r, Mapping)}
    curr_rel = {_relation_key(r) for l in actual.get("capas", {}).values()
                for r in l.get("relaciones", []) if isinstance(r, Mapping)}

    persistentes = sorted(a & b)
    prev_obs = {o.get("token"): o for o in anterior.get("observaciones_tokens", [])}
    curr_obs = {o.get("token"): o for o in actual.get("observaciones_tokens", [])}
    reapariciones = []
    for token in sorted(set(prev_obs) & set(curr_obs)):
        prev, curr = prev_obs[token], curr_obs[token]
        reapariciones.append({
            "token": token, "misma_identidad": True, "nueva_observacion": True,
            "evidencia_acumulada_por_reaparicion": False,
            "instancias_contextuales_anterior": deepcopy(prev.get("instancias_contextuales", [])),
            "instancias_contextuales_actual": deepcopy(curr.get("instancias_contextuales", [])),
            "capas_anterior": deepcopy(prev.get("capas", [])),
            "capas_actual": deepcopy(curr.get("capas", [])),
        })

    return {"de": anterior.get("corte"), "a": actual.get("corte"),
            "transicion": {"persisten": persistentes, "aparecen": sorted(b-a),
                           "desaparecen": sorted(a-b),
                           "relaciones_nuevas_declaradas": [list(x) for x in sorted(curr_rel-prev_rel)],
                           "relaciones_que_dejan_de_aparecer": [list(x) for x in sorted(prev_rel-curr_rel)],
                           "reapariciones_contextuales": reapariciones}}

def _traza_tokens(cortes: Sequence[Mapping[str, Any]]) -> list[Dict[str, Any]]:
    traza: Dict[str, list] = {}
    for cfg in cortes:
        for obs in cfg.get("observaciones_tokens", []):
            token = obs.get("token")
            if not token:
                continue
            traza.setdefault(token, []).append({
                "corte": cfg.get("corte"),
                "capas": deepcopy(obs.get("capas", [])),
                "n_instancias_contextuales": obs.get("n_instancias_contextuales", 0),
                "instancias_contextuales": deepcopy(obs.get("instancias_contextuales", [])),
            })
    return [{"token": token, "apariciones": len(obs), "reaparece": len(obs)>1,
             "unidad_evidencia_acumulada": 1, "no_duplicar_por_reaparicion": True,
             "no_duplicar_por_capa": True, "observaciones": obs}
            for token, obs in sorted(traza.items())]

def integrar(cortes: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    configs = [configurar_corte(c.get("id", i), c.get("capas", {})) for i, c in enumerate(cortes)]
    transiciones = [comparar_configuraciones(configs[i-1], configs[i]) for i in range(1, len(configs))]
    return {"plugin": "capa_integracion_semantica_v1",
            "version": "1.2-identidad-global-subindices-contextuales",
            "estado": "PROPUESTA",
            "principio_central": {
                "token_es_unidad": True, "reaparicion_no_duplica": True,
                "reaparicion_no_suma_evidencia": True,
                "reaparicion_genera_nueva_observacion_contextual": True,
                "misma_identidad_across_capas": True,
                "instancias_contextuales_no_son_tokens_nuevos": True,
                "vectorizacion_debe_ser_declarada_o_provista_por_capa_origen": True,
                "esta_capa_no_inventa_formula_vectorizacion": True},
            "candados": {"TOCA_F": TOCA_F, "TOCA_244": TOCA_244,
                         "TOCA_Engine_V5": TOCA_ENGINE_V5, "TOCA_H1_H2": TOCA_H1_H2,
                         "TOCA_APUESTA": TOCA_APUESTA},
            "cortes": configs, "transiciones": transiciones,
            "traza_tokens": _traza_tokens(configs)}
