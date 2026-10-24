"""Adversarial consistency verifier.

Purpose: test the execution contract against explicit spec/formula rules without
feeding H1/H2 or changing predictor state. It creates reproducible adversarial
fixtures and an LLM review packet. The LLM packet contains only the rules,
observations and expected invariant checks; it does not contain a desired
hypothesis or winner.
"""
from __future__ import annotations
import json, hashlib
from pathlib import Path
from typing import Any, Dict, List

VERSION = "CONSISTENCY_ADVERSARIAL_V0.1"
ROLE = "control_only"
FEEDS_H = False
FEEDS_PREDICTOR = False

RULES = [
    ("LATENCIA_NO_STOP", "LATENCIA es estado de información no resuelta; no detiene la exploración del input congelado."),
    ("TORTUGA_NO_CAMBIA_FAMILIA", "Borrosidad activa remesura; no cambia familia por sí misma."),
    ("TIE_NO_WINNER", "Margen exacto 0.0 no puede producir H1/H2 por desempate."),
    ("RESOLUTION_BEFORE_CLOSE", "El cierre sólo puede ocurrir después de agotar la resolución disponible del input."),
    ("LATERAL_NO_H", "Caldero/interrelación aportan evidencia lateral; no escriben H1/H2."),
    ("FREEZE_NO_FUTURE", "La resolución prospectiva usa únicamente información <= FREEZE."),
    ("CANON_IMMUTABLE", "Engine V5 y catálogo 244 no se modifican."),
    ("CALDERO_PERSIST_CROSS_CASE", "Vecinos pueden persistir transversalmente entre casos sin convertirse automáticamente en canon/H."),
]


def _hash_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _case(name: str, observation: Dict[str, Any], expected: str, rule: str) -> Dict[str, Any]:
    return {"id": name, "observation": observation, "expected_state": expected, "rule": rule}


def adversarial_fixtures() -> List[Dict[str, Any]]:
    return [
        _case("TIE_EXACT_0", {"top": 8.0, "second": 8.0, "new_signal": True, "resolution_exhausted": True, "repeated": True}, "LATENCIA_INFORMACIONAL", "TIE_NO_WINNER"),
        _case("MISSING_DATA_BUT_INPUT_PRESENT", {"input_present": True, "extraction_complete": False, "new_signal": True, "resolution_exhausted": False}, "RESOLVER_INPUT", "LATENCIA_NO_STOP"),
        _case("REPEATED_WITHOUT_NEW_SIGNAL", {"repeated": True, "margin": 1.5, "new_signal": False, "resolution_exhausted": True}, "LATENCIA_INFORMACIONAL", "RESOLUTION_BEFORE_CLOSE"),
        _case("NEW_SIGNAL_WITHOUT_RESOLUTION", {"repeated": True, "margin": 1.5, "new_signal": True, "resolution_exhausted": False}, "RESOLVER_INPUT", "RESOLUTION_BEFORE_CLOSE"),
        _case("LATERAL_TRIES_TO_WRITE_H", {"caldero_feeds_H": True, "interrelation_feeds_H": True}, "REJECT_LATERAL_H", "LATERAL_NO_H"),
        _case("FUTURE_DATA_DURING_FREEZE", {"freeze": "C2", "observed_cut": "C3", "future_accessed": True}, "REJECT_FUTURE", "FREEZE_NO_FUTURE"),
        _case("CANON_MUTATION", {"engine_hash_changed": True, "patterns_hash_changed": False}, "REJECT_CANON_MUTATION", "CANON_IMMUTABLE"),
        _case("CROSS_CASE_NEIGHBOR", {"cases": ["A", "B"], "neighbor": "inquisicion", "promote_to_pattern": False, "write_H": False}, "PERSIST_LATERAL", "CALDERO_PERSIST_CROSS_CASE"),
    ]


def run(result: Dict[str, Any], package_root: str | Path, spec_text: str = "") -> Dict[str, Any]:
    root = Path(package_root)
    info = result.get("information_state") or result.get("predictor", {}).get("information_state") or {}
    pred = result.get("predictor") or {}
    comps = result.get("execution", {}).get("component_status") or result.get("components_executed") or []
    comp_map = {x.get("component"): x for x in comps if isinstance(x, dict) and x.get("component")}
    violations = []

    # Actual-run invariant checks.
    if info.get("top_margin") == 0.0 and (pred.get("H1") or pred.get("H2")):
        violations.append("TIE_NO_WINNER")
    # Detect stale/mismatched canonical pattern identity without modifying canon.
    patterns = root / "patterns_final_v14.json"
    if patterns.exists():
        actual_patterns_sha = hashlib.sha256(patterns.read_bytes()).hexdigest()
        declared_patterns_sha = str(result.get("patterns_sha256") or "")
        if declared_patterns_sha and declared_patterns_sha != actual_patterns_sha:
            violations.append("PATTERNS_HASH_DECLARATION_MISMATCH")
    # Formula corpus is declared by the motor; absence is a concrete missing-input condition.
    formula_decl = (result.get("formula_corpus") or {}).get("file")
    if formula_decl and not (root / formula_decl).exists():
        violations.append("FORMULA_CORPUS_MISSING")
    if info.get("state") == "DETERMINADO" and not info.get("resolution_exhausted", False):
        violations.append("RESOLUTION_BEFORE_CLOSE")
    for name, row in comp_map.items():
        if name in {"sidecar_caldero_busqueda_arquetipos.py", "motor_interrelacion_extensible_v0_1.py"}:
            # Lateral evidence may contribute to the H-forming surface, but it
            # must never write or independently decide H1/H2.
            if row.get("writes_H") is True or row.get("can_decide_H") is True:
                violations.append("LATERAL_NO_H")

    fixtures = adversarial_fixtures()
    packet = {
        "verifier_version": VERSION,
        "role": ROLE,
        "feeds_predictor": FEEDS_PREDICTOR,
        "feeds_H": FEEDS_H,
        "rules": [{"id": r, "text": t} for r, t in RULES],
        "fixtures": fixtures,
        "actual_run_observation": {
            "information_state": info,
            "predictor_status": pred.get("status"),
            "H1_present": bool(pred.get("H1")),
            "H2_present": bool(pred.get("H2")),
            "components": list(comp_map),
        },
        "instruction_to_llm": (
            "Reproduce each fixture independently from the stated rule only. "
            "Do not infer a desired H, do not use training priors, do not choose a winner. "
            "For each fixture return PASS/FAIL and the exact rule that was violated. "
            "Then compare the actual-run observation to the same invariants."
        ),
    }
    packet_json = json.dumps(packet, ensure_ascii=False, indent=2)
    packet_path = root / "CONSISTENCY_ADVERSARIAL_LLM_PACKET.json"
    packet_path.write_text(packet_json, encoding="utf-8")
    audit = {
        "status": "PASS" if not violations else "FAIL",
        "verifier_version": VERSION,
        "violations": violations,
        "fixture_count": len(fixtures),
        "packet": str(packet_path),
        "packet_sha256": _hash_text(packet_json),
        "rule_source": "explicit invariants + adversarial fixtures; no H mapping",
    }
    (root / "CONSISTENCY_ADVERSARIAL_AUDIT.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    return audit
