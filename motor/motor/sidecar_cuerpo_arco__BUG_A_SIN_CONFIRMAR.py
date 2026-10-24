#!/usr/bin/env python3
"""
sidecar_cuerpo_arco.py

PROPUESTA — sidecar corporal/arco.
Estado: PROPUESTA. No se cablea al motor limpio.

Candados:
TOCA_F: NO
TOCA_244: NO
TOCA_Engine_V5: NO

Este módulo es un sidecar: no modifica F, CAT=244 ni Engine_V5.
La semántica de "evidencia" entra ya tokenizada por corte; el sidecar
no inventa umbrales ni convierte una ausencia en evidencia.

Cadena:
desgaste (opcional) -> enfermedad|herida -> agonia -> muerte_propia

Si falta un eslabón obligatorio, la cadena es VACIO.
cuerpo_muerte_propia nunca puede ser H1.
"""

from __future__ import annotations
from typing import Any, Dict, Iterable, List, Mapping, Sequence


FAMILIAS = ("cuerpo_desgaste_agente", "cuerpo_inhabilita")
TOKENS_CODIGO = {
    "cuerpo_desgaste": 0.60,
    "cuerpo_enfermedad": 0.72,
    "cuerpo_herida": 0.72,
    "cuerpo_agonia": 0.80,
    "cuerpo_muerte_propia": 0.84,
    "salud_estable": 0.60,
    "salud_recuperacion": 0.70,
}
CONTRA = {"salud_estable"}
APARTE = {"salud_recuperacion"}
MORTE = "cuerpo_muerte_propia"
ENFERMEDAD_O_HERIDA = {"cuerpo_enfermedad", "cuerpo_herida"}
OBLIGATORIOS = {"cuerpo_agonia", MORTE}


def _tokens(cut: Mapping[str, Any]) -> List[Dict[str, Any]]:
    """Normaliza cut['tokens'] como lista de dicts o mapping token->peso."""
    raw = cut.get("tokens", [])
    if isinstance(raw, Mapping):
        return [{"token": str(k), "peso": v} for k, v in raw.items()]
    result = []
    for item in raw:
        if isinstance(item, str):
            result.append({"token": item})
        elif isinstance(item, Mapping) and "token" in item:
            result.append(dict(item))
    return result


def _token_names(cut: Mapping[str, Any]) -> set[str]:
    return {x["token"] for x in _tokens(cut)}


def _cut_id(cut: Mapping[str, Any], fallback: int) -> Any:
    return cut.get("id", fallback)


def _find_first(cuts: Sequence[Mapping[str, Any]], token: str, start: int = 0):
    for i in range(start, len(cuts)):
        if token in _token_names(cuts[i]):
            return i
    return None


def analizar_cadena(cortes: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    """
    Evalúa la cadena en orden temporal.

    Desgaste es opcional. Después debe aparecer enfermedad o herida,
    luego agonia y finalmente muerte_propia. Saltar un eslabón obligatorio
    produce VACIO y no se rescata mirando hacia adelante.
    """
    cuts = list(cortes)
    if not cuts:
        return {"estado": "VACIO", "motivo": "sin_cortes", "cadena": []}

    pos = 0
    desgaste_i = _find_first(cuts, "cuerpo_desgaste", pos)
    if desgaste_i is not None:
        pos = desgaste_i + 1

    eh_i = None
    for i in range(pos, len(cuts)):
        if _token_names(cuts[i]) & ENFERMEDAD_O_HERIDA:
            eh_i = i
            break
        # Una muerte antes del eslabón invalida la secuencia.
        if MORTE in _token_names(cuts[i]):
            return {"estado": "VACIO", "motivo": "cadena_rota_sin_enfermedad_o_herida",
                    "cadena": []}
    if eh_i is None:
        return {"estado": "VACIO", "motivo": "falta_enfermedad_o_herida", "cadena": []}

    ag_i = _find_first(cuts, "cuerpo_agonia", eh_i + 1)
    if ag_i is None:
        return {"estado": "VACIO", "motivo": "falta_agonia", "cadena": []}

    death_i = _find_first(cuts, MORTE, ag_i + 1)
    if death_i is None:
        return {"estado": "VACIO", "motivo": "falta_muerte_propia", "cadena": []}

    # No aceptamos muerte como sustituto de agonia ni retroceso temporal.
    return {
        "estado": "HIT",
        "familias": list(FAMILIAS),
        "cadena": [
            {"token": "cuerpo_desgaste", "corte": _cut_id(cuts[desgaste_i], desgaste_i)}
            if desgaste_i is not None else {"token": "cuerpo_desgaste", "corte": None, "opcional": True},
            {"token": next(iter(_token_names(cuts[eh_i]) & ENFERMEDAD_O_HERIDA)),
             "corte": _cut_id(cuts[eh_i], eh_i)},
            {"token": "cuerpo_agonia", "corte": _cut_id(cuts[ag_i], ag_i)},
            {"token": MORTE, "corte": _cut_id(cuts[death_i], death_i)},
        ],
    }


def _h1_prohibido(tokens: Iterable[str]) -> bool:
    return MORTE in set(tokens)


def voto_caldero_cuerpo(cortes: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    """
    Voto de t+1_CUERPO, separado del voto de oficio.

    Convención de entrada:
      cut['caldero_cuerpo'] = lista de tokens/registro no vacío, o
      cut['caldero_cuerpo_vacio'] = True.

    Si aparece muerte_propia en t y el caldero cuerpo de t-1 está vacío,
    el evento se etiqueta RUIDO.
    """
    cuts = list(cortes)
    eventos = []
    for i, cut in enumerate(cuts):
        names = _token_names(cut)
        if MORTE not in names:
            continue
        prev = cuts[i - 1] if i > 0 else {}
        empty = bool(prev.get("caldero_cuerpo_vacio", False))
        if "caldero_cuerpo" in prev:
            raw = prev["caldero_cuerpo"]
            empty = empty or raw is None or raw == [] or raw == {}
        eventos.append({
            "corte_muerte": _cut_id(cut, i),
            "corte_previo": _cut_id(prev, i - 1) if i > 0 else None,
            "voto": "RUIDO" if empty else "t+1_CUERPO",
            "separado_de_oficio": True,
        })
    return {"votos": eventos, "n": len(eventos)}


def monomito_etiqueta(cortes: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    """
    Q3/Q4 son etiquetas laterales. Nunca entran en p.
    Q3 = inhabilita. Q4 = recuperación o muerte_propia.
    """
    out = []
    for i, cut in enumerate(cortes):
        names = _token_names(cut)
        q = []
        if "cuerpo_enfermedad" in names or "cuerpo_herida" in names or "cuerpo_agonia" in names:
            q.append("Q3_inhabilita")
        if "salud_recuperacion" in names or MORTE in names:
            q.append("Q4_recuperacion_o_muerte_propia")
        if q:
            out.append({"corte": _cut_id(cut, i), "etiquetas": q, "suma_a_p": False})
    return {"etiquetas": out}


def aquiles_sensibilidad(
    cortes: Sequence[Mapping[str, Any]],
    *,
    eje_oficio_antes: Any = None,
    eje_oficio_sin_cuerpo: Any = None,
) -> Dict[str, Any]:
    """
    Pregunta de sensibilidad. No aplica a VACIO.
    La comparación numérica queda a cargo del caller: el sidecar solo registra
    los dos valores entregados y la pregunta.
    """
    cadena = analizar_cadena(cortes)
    if cadena["estado"] == "VACIO":
        return {"aplica": False, "motivo": "Control B / cadena VACIO"}
    return {
        "aplica": True,
        "pregunta": "¿si quito el token cuerpo, se cae el eje de oficio?",
        "eje_oficio_antes": eje_oficio_antes,
        "eje_oficio_sin_cuerpo": eje_oficio_sin_cuerpo,
    }


def analizar_cuerpo(cortes: Sequence[Mapping[str, Any]], **kwargs: Any) -> Dict[str, Any]:
    cuts = list(cortes)
    cadena = analizar_cadena(cuts)
    tokens = {t for c in cuts for t in _token_names(c)}
    return {
        "plugin": "sidecar_cuerpo_arco",
        "estado": "PROPUESTA",
        "TOCA_F": "NO",
        "TOCA_244": "NO",
        "TOCA_Engine_V5": "NO",
        "familias": list(FAMILIAS),
        "tokens_codigo": dict(TOKENS_CODIGO),
        "cadena": cadena,
        "h1_prohibido": _h1_prohibido(tokens),
        "caldero": voto_caldero_cuerpo(cuts),
        "monomito": monomito_etiqueta(cuts),
        "aquiles": aquiles_sensibilidad(cuts, **kwargs),
        "salud_estable": "salud_estable" in tokens,
        "salud_recuperacion_aparte": "salud_recuperacion" in tokens,
    }


__all__ = [
    "analizar_cadena", "voto_caldero_cuerpo", "monomito_etiqueta",
    "aquiles_sensibilidad", "analizar_cuerpo", "FAMILIAS", "TOKENS_CODIGO",
]
