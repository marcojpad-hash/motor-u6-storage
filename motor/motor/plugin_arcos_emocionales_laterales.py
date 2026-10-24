"""Lateral emotional-arc data layer.

Preserves supplied emotional-pattern data outside the canonical 244.
It does not mutate Engine V5, patterns_final_v14.json, P/A/C, R732 or H.
Activation is mechanical: observed token names are matched against the
supplied token dictionaries. No semantic substitutions are introduced.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, Iterable

VERSION = "ARCO_EMOCIONAL_LATERAL_V0_1"
FEEDS_PREDICTOR = True
FEEDS_H = False
MUTATES_CANON = False


def load_catalog(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _observed_names(value: Any) -> set[str]:
    out: set[str] = set()
    if isinstance(value, str):
        out.add(value)
    elif isinstance(value, dict):
        for k, v in value.items():
            out.add(str(k))
            out |= _observed_names(v)
    elif isinstance(value, (list, tuple, set)):
        for v in value:
            out |= _observed_names(v)
    return out


def evaluate(cuts: Iterable[Dict[str, Any]], external_lights: Any, catalog: Dict[str, Any]) -> Dict[str, Any]:
    observed = _observed_names(external_lights)
    cut_observed = []
    for cut in cuts:
        names = _observed_names(cut)
        cut_observed.append(sorted(names))
        observed |= names

    activations = {}
    for name, spec in (catalog.get("patterns") or {}).items():
        favor = spec.get("tokens_favor") or {}
        contra = spec.get("tokens_contra") or {}
        favor_hits = {k: float(v) for k, v in favor.items() if k in observed}
        contra_hits = {k: float(v) for k, v in contra.items() if k in observed}
        activations[name] = {
            "description": spec.get("description", ""),
            "tokens_favor": favor,
            "tokens_contra": contra,
            "favor_hits": favor_hits,
            "contra_hits": contra_hits,
            "favor_activation": sum(favor_hits.values()),
            "contra_activation": sum(abs(v) for v in contra_hits.values()),
            "net_activation": sum(favor_hits.values()) + sum(contra_hits.values()),
        }

    return {
        "version": VERSION,
        "catalog_source": "arcos_emocionales_laterales.json",
        "observed_token_count": len(observed),
        "cut_observed": cut_observed,
        "activations": activations,
        "feeds_predictor": FEEDS_PREDICTOR,
        "feeds_H": FEEDS_H,
        "mutates_canon": MUTATES_CANON,
    }
