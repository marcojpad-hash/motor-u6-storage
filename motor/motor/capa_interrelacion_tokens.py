#!/usr/bin/env python3
"""
capa_interrelacion_tokens.py

PROPUESTA — capa general de interrelación entre familias del 244.
No se cablea al limpio sin autorización.

Candados:
TOCA_F: NO
TOCA_244: NO
TOCA_Engine_V5: NO

Principio: cuando 2+ familias se activan por evidencia relacionada en el
mismo corte, se registra una sola unidad de evidencia con múltiples facetas.
No se fusionan familias, no se elimina ninguna y no se suman ciegamente.

La relación semántica debe venir declarada por la capa de activación:
este módulo no inventa que dos evidencias son "relacionadas".
"""

from __future__ import annotations
from itertools import combinations
from typing import Any, Dict, Iterable, List, Mapping, Sequence


RELACIONES = {"co-ocurrencia", "tension", "gradiente"}


def _family(x: Mapping[str, Any]) -> str:
    return str(x.get("familia") or x.get("family"))


def _weight(x: Mapping[str, Any]) -> float:
    try:
        return float(x.get("peso", x.get("weight", 0.0)))
    except (TypeError, ValueError):
        return 0.0


def _related(a: Mapping[str, Any], b: Mapping[str, Any]) -> bool:
    # Declaración explícita preferida. También acepta un mismo evidence_group.
    if "relacionada" in a or "relacionada" in b:
        return bool(a.get("relacionada", False) or b.get("relacionada", False))
    ga, gb = a.get("evidence_group"), b.get("evidence_group")
    return ga is not None and ga == gb


def _relation(items: Sequence[Mapping[str, Any]]) -> str:
    vals = {str(x.get("tipo_relacion")) for x in items if x.get("tipo_relacion")}
    if len(vals) == 1 and next(iter(vals)) in RELACIONES:
        return next(iter(vals))
    # Si la relación no fue especificada, el evento general se etiqueta
    # co-ocurrencia; no se afirma una tensión/gradiente no suministrada.
    return "co-ocurrencia"


def _context_score(item: Mapping[str, Any]) -> float:
    """
    Score de contexto ya calculado por los tokens P/A/C restantes.
    No compara directamente familia A contra familia B.
    """
    try:
        return float(item.get("context_score", 0.0))
    except (TypeError, ValueError):
        return 0.0


def _dominant_from_context(
    activated: Sequence[Mapping[str, Any]],
    context_tokens: Sequence[Mapping[str, Any]] | None,
) -> tuple[str | None, Dict[str, float]]:
    """
    Calcula dominancia a partir del RESTO de tokens P/A/C, excluyendo las
    familias que participan en la co-ocurrencia. Si no hay contexto explícito,
    no inventa una dominancia.
    """
    families = {_family(x) for x in activated}
    scores: Dict[str, float] = {}
    for tok in context_tokens or []:
        fam = _family(tok)
        if fam in families:
            continue
        scores[fam] = scores.get(fam, 0.0) + _weight(tok)
    if not scores:
        # Algunos callers ya entregan context_score por familia.
        for x in activated:
            fam = _family(x)
            if "context_score" in x:
                scores[fam] = _context_score(x)
    if not scores:
        return None, {}
    return max(scores, key=scores.get), scores


def analizar_corte(
    corte_id: Any,
    activaciones: Sequence[Mapping[str, Any]],
    *,
    context_tokens: Sequence[Mapping[str, Any]] | None = None,
) -> Dict[str, Any]:
    """
    Produce registros de interrelación sin alterar activaciones originales.

    dominante_este_corte es lectura humana solamente. Ninguna familia se
    elimina del board/apuesta.
    """
    acts = [dict(x) for x in activaciones if _family(x)]
    groups: List[List[Dict[str, Any]]] = []
    unused = set(range(len(acts)))

    while unused:
        i = min(unused)
        component = {i}
        changed = True
        while changed:
            changed = False
            for j in list(unused - component):
                if any(_related(acts[k], acts[j]) for k in component):
                    component.add(j)
                    changed = True
        unused -= component
        if len(component) >= 2:
            groups.append([acts[k] for k in sorted(component)])

    eventos = []
    for group in groups:
        families = []
        for x in group:
            fam = _family(x)
            if fam not in families:
                families.append(fam)

        dominant, context_scores = _dominant_from_context(group, context_tokens)
        eventos.append({
            "cortes": [corte_id],
            "familias": families,
            "tipo_relacion": _relation(group),
            "dominante_este_corte": dominant,
            "evidencia_dominancia": context_scores,
            "cuenta_doble": False,
            "evento_multifaceta": True,
            "unidad_evidencia": 1,
            "board_familias_vivas": families,
            "no_descarta_no_dominante": True,
        })

    # Activaciones aisladas siguen siendo visibles; no se transforman en
    # interrelaciones artificiales.
    return {
        "plugin": "capa_interrelacion_tokens",
        "estado": "PROPUESTA",
        "TOCA_F": "NO",
        "TOCA_244": "NO",
        "TOCA_Engine_V5": "NO",
        "corte": corte_id,
        "eventos": eventos,
        "activaciones_sin_relacion": [
            _family(acts[i]) for i in range(len(acts))
            if not any(acts[i] is x for g in groups for x in g)
        ],
    }


def analizar_cortes(
    cortes: Sequence[Mapping[str, Any]],
) -> Dict[str, Any]:
    """
    Formato esperado:
      {"id": "C1", "activaciones": [...], "context_tokens": [...]}
    """
    resultados = []
    for i, cut in enumerate(cortes):
        resultados.append(
            analizar_corte(
                cut.get("id", i),
                cut.get("activaciones", []),
                context_tokens=cut.get("context_tokens", []),
            )
        )
    return {
        "plugin": "capa_interrelacion_tokens",
        "estado": "PROPUESTA",
        "TOCA_F": "NO",
        "TOCA_244": "NO",
        "TOCA_Engine_V5": "NO",
        "cortes": resultados,
        "cuenta_doble_global": False,
    }


__all__ = ["analizar_corte", "analizar_cortes", "RELACIONES"]
