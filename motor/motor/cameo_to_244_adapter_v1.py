"""CAMEO -> 244 candidate-specific adapter.

No weights are defined here. Scores are raw occurrence counts in candidate-specific
texts/events after an explicitly approved CAMEO->244 mapping is loaded.

The adapter never writes the canonical catalog and never decides H.
"""
from __future__ import annotations
import json
import re
from pathlib import Path

VERSION = "CAMEO_TO_244_ADAPTER_V1"
MAP_FILE = "cameo_to_244.json"

def _load_map(base: Path):
    p = Path(__file__).with_name(MAP_FILE)
    data = json.loads(p.read_text(encoding="utf-8"))
    if data.get("schema") != "CAMEO_TO_244_V1":
        raise ValueError("CAMEO_TO_244_SCHEMA_INVALID")
    mapping = data.get("mappings") or {}
    if not isinstance(mapping, dict):
        raise ValueError("CAMEO_TO_244_MAPPINGS_INVALID")
    return mapping, data

def _hits(text, code, entry):
    blob = str(text or "").casefold()
    needles = [str(code).casefold()]
    for k in ("label", "token"):
        v = entry.get(k)
        if v: needles.append(str(v).casefold())
    return sum(1 for n in needles if n and re.search(r"(?<![\w])" + re.escape(n) + r"(?![\w])", blob))

def adapt(cameo_result, candidate_texts, patterns):
    """Return family->raw count only where an approved unique mapping exists.

    candidate_texts: {family_244: [event/text strings]}
    patterns: canonical 244 catalog dict, used only to validate destinations.
    """
    try:
        mapping, meta = _load_map(Path(__file__).parent)
    except FileNotFoundError:
        return {
            "status": "NOT_APPLICABLE",
            "version": VERSION,
            "scores": {str(k): 0.0 for k in (candidate_texts or {})},
            "feeds_H": False,
            "can_decide_H": False,
            "mutates_canonical": False,
            "role": "candidate_specific_cameo_to_244_adapter",
            "mapping_version": None,
            "audit": {
                "mapping_file": MAP_FILE,
                "mapping_present": False,
                "reason": "APPROVED_MAPPING_FILE_ABSENT",
                "reaches_candidates": False,
                "discriminates": False,
            },
        }
    candidates = {str(k): list(v or []) for k, v in (candidate_texts or {}).items()}
    valid_families = set(patterns or {})
    out = {c: 0.0 for c in candidates}
    audit = {"exact": 0, "unmapped_code": 0, "invalid_destination": 0, "ambiguous_mapping": 0,
             "candidate_hits": 0, "reaches_candidates": False, "discriminates": False,
             "mapped_codes": 0}
    selected = cameo_result.get("selected_codes") or [] if isinstance(cameo_result, dict) else []
    for item in selected:
        code = str(item.get("code") if isinstance(item, dict) else "").strip()
        if not code:
            continue
        entry = mapping.get(code)
        if entry is None:
            audit["unmapped_code"] += 1
            continue
        if isinstance(entry, list):
            audit["ambiguous_mapping"] += 1
            continue
        family = str(entry.get("familia_244") or "").strip()
        if family not in valid_families:
            audit["invalid_destination"] += 1
            continue
        audit["mapped_codes"] += 1
        for cand, texts in candidates.items():
            n = sum(_hits(t, code, {**entry, "label": item.get("label", entry.get("label")), "token": item.get("token", entry.get("token"))}) for t in texts)
            if n:
                out[cand] += float(n)
                audit["candidate_hits"] += n
                audit["exact"] += 1
    vals=list(out.values())
    audit["reaches_candidates"] = any(v > 0 for v in vals)
    audit["discriminates"] = bool(vals) and (max(vals)-min(vals)) > 1e-12
    return {
        "status": "EXECUTED",
        "version": VERSION,
        "scores": out,
        "feeds_H": bool(audit["discriminates"]),
        "can_decide_H": False,
        "mutates_canonical": False,
        "role": "candidate_specific_cameo_to_244_adapter",
        "mapping_version": meta.get("version"),
        "audit": audit,
    }
