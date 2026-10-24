"""V0.1 — Metacognición del arco predictivo.

Agrupa en una sola capa los procesos que deben permanecer relacionados pero no
confundidos:
  PRE-H       orientación analógica (recibida como evidencia ya producida)
  POST-H      contraste de H contra los análogos ciegos; no reescribe H/apuesta
  RETRO       validación/ingeniería inversa después de abrir el futuro

La capa es lateral y no modifica Engine, patterns, P/A/C, H ni apuesta.
"""
from __future__ import annotations
import hashlib, re
from typing import Any, Dict, Iterable, List, Optional

VERSION = "METACOG_V0.1"


def _norm(x: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(x).casefold()).strip("_")


def _tokens_from_patterns(patterns: Dict[str, Any], family: Optional[str]) -> set[str]:
    if not family or not isinstance(patterns, dict):
        return set()
    p = patterns.get(family) or {}
    out = set()
    for k in ("tokens_favor", "tokens_contra"):
        v = p.get(k) or {}
        if isinstance(v, dict):
            out.update(_norm(x) for x in v)
        elif isinstance(v, (list, tuple, set)):
            out.update(_norm(x) for x in v)
    return {x for x in out if x}


def _analog_values(pre_h: Dict[str, Any]) -> List[str]:
    vals: List[str] = []
    for x in pre_h.get("tokens_neighbors") or []:
        if isinstance(x, dict):
            v = x.get("token") or x.get("name") or x.get("family")
        else:
            v = x
        if v:
            vals.append(_norm(v))
    for k in ("query_terms",):
        for v in pre_h.get(k) or []:
            if v:
                vals.append(_norm(v))
    return sorted(set(v for v in vals if v))


def _candidate_name_forms(family: Optional[str]) -> set[str]:
    if not family:
        return set()
    n = _norm(family)
    forms = {n}
    for p in ("arquetipo_el_", "arquetipo_la_", "arquetipo_los_", "arquetipo_"):
        if n.startswith(p):
            forms.add(n[len(p):])
    return forms


def post_h_contrast(pre_h: Dict[str, Any], pred: Dict[str, Any], patterns: Dict[str, Any]) -> Dict[str, Any]:
    """Contrasta la H sellada contra los análogos obtenidos antes de H.

    No consulta futuro, no reordena candidatos y no escribe H/apuesta.
    """
    analogs = _analog_values(pre_h or {})
    candidates = pred.get("candidates") or []
    rows = []
    for c in candidates[:10]:
        family = c.get("family") if isinstance(c, dict) else None
        forms = _candidate_name_forms(family)
        own = _tokens_from_patterns(patterns, family)
        direct = sorted(forms & set(analogs))
        overlap = sorted(own & set(analogs))
        # Escala diagnóstica, no peso del predictor.
        support = len(overlap) + len(direct)
        rows.append({
            "family": family,
            "analog_family_match": direct,
            "analog_token_overlap": overlap,
            "support_count": support,
            "contrast": "ALINEA" if support else "SIN_ALINEACION_DIRECTA",
        })
    h1 = pred.get("H1") or {}
    h2 = pred.get("H2") or {}
    by = {r.get("family"): r for r in rows}
    h1r = by.get(h1.get("family")) if isinstance(h1, dict) else None
    h2r = by.get(h2.get("family")) if isinstance(h2, dict) else None
    return {
        "status": "EXECUTED" if pre_h.get("status") in {"EXECUTED", "API_PENDING"} else "NO_ANALOGS",
        "phase": "POST_H_CONTRAST",
        "input_source": "PRE_H_BLIND_ANALOGICAL_ARC",
        "analog_count": len(analogs),
        "H1": h1r,
        "H2": h2r,
        "top10": rows,
        "can_rewrite_H": False,
        "can_rewrite_apuesta": False,
        "reads_future": False,
        "feeds_predictor": False,
        "note": "Contrasta la apuesta ya sellada contra los análogos ciegos; no valida el desenlace.",
    }


def retrospective_validation(reveal: Optional[Dict[str, Any]], pred: Dict[str, Any], apuesta: Optional[Dict[str, Any]], z_work: Optional[str]) -> Dict[str, Any]:
    """Valida después del freeze. Sólo se activa con una revelación post-freeze explícita."""
    if not reveal:
        return {
            "status": "WAITING_FOR_FUTURE",
            "phase": "RETROSPECTIVE_CALIBRATION",
            "z_work": z_work,
            "future_read": False,
            "reason": "no_post_freeze_reveal",
            "can_rewrite_H": False,
            "can_rewrite_apuesta": False,
        }
    future = reveal.get("future_cuts") or reveal.get("cuts") or []
    observed = reveal.get("observed_tokens") or []
    if not future and not observed and reveal.get("validation") is None:
        return {
            "status": "INSUFFICIENT_REVEAL",
            "phase": "RETROSPECTIVE_CALIBRATION",
            "z_work": z_work,
            "future_read": False,
            "can_rewrite_H": False,
            "can_rewrite_apuesta": False,
        }
    explicit = reveal.get("validation")
    h1 = (pred.get("H1") or {}).get("family") if isinstance(pred.get("H1"), dict) else None
    bet = (apuesta or {}).get("family") if isinstance(apuesta, dict) else h1
    return {
        "status": "EXECUTED",
        "phase": "RETROSPECTIVE_CALIBRATION",
        "z_work": z_work,
        "z_final": reveal.get("z_final_date"),
        "future_read": True,
        "future_cut_count": len(future),
        "observed_token_count": len(observed),
        "H1": h1,
        "apuesta_family": bet,
        "validation": explicit,
        "engineering_inverse": reveal.get("engineering_inverse"),
        "can_rewrite_H": False,
        "can_rewrite_apuesta": False,
        "feeds_predictor": False,
        "note": "El futuro se abre sólo después de H/apuesta; el aprendizaje queda como metacognición, no como retroalimentación retrospectiva de la misma corrida.",
    }


def run(pre_h: Dict[str, Any], pred: Dict[str, Any], patterns: Dict[str, Any], apuesta: Optional[Dict[str, Any]], case: Dict[str, Any], z_work: Optional[str]) -> Dict[str, Any]:
    contrast = post_h_contrast(pre_h or {}, pred or {}, patterns or {})
    reveal = case.get("post_freeze_reveal")
    retro = retrospective_validation(reveal, pred or {}, apuesta, z_work)
    frozen = {
        "H1": (pred.get("H1") or {}).get("family") if isinstance(pred.get("H1"), dict) else None,
        "H2": (pred.get("H2") or {}).get("family") if isinstance(pred.get("H2"), dict) else None,
        "apuesta": (apuesta or {}).get("family") if isinstance(apuesta, dict) else None,
    }
    return {
        "version": VERSION,
        "status": "EXECUTED",
        "model_role": "METACOGNITION",
        "z_work": z_work,
        "frozen_prediction": frozen,
        "pre_H": {
            "status": pre_h.get("status"),
            "phase": "PRE_H_ORIENTATION",
            "can_decide_H": False,
        },
        "post_H": contrast,
        "retrospective": retro,
        "invariants": {
            "canonical_244_unchanged": True,
            "H_rewrite_forbidden": True,
            "apuesta_rewrite_forbidden": True,
            "future_used_before_H": False,
        },
        "calibration_role": "aprendizaje_sobre_caso_y_experiencia_sin_reescribir_la_corrida_congelada",
        "fingerprint": hashlib.sha256(repr((frozen, contrast, retro.get("status"), z_work)).encode()).hexdigest(),
    }
