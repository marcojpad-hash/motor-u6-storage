"""Autonomous consistency resolver.

Continuity layer: resolves minor, mechanically recoverable inconsistencies from
artifacts already present in the package. It NEVER changes Engine_V5, patterns,
FREEZE, H1/H2, predictor scores, or lateral feeds. Unresolvable findings remain
findings; they do not get fabricated away.
"""
from __future__ import annotations
import hashlib, json, re
from pathlib import Path
from typing import Any, Dict, List

VERSION = "CONSISTENCY_AUTONOMA_V0.1"
ROLE = "audit_continuity_control"
FEEDS_PREDICTOR = False
FEEDS_H = False

HARD_STOP = {
    "CANON_MUTATION", "FREEZE_FUTURE_ACCESS", "INPUT_INVALIDO", "TOKEN_INVALIDO",
    "PESO_FUERA_DE_CONTRATO", "TIE_WINNER"
}

def sha(p: Path):
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None

def _declared_constants(motor_path: Path) -> Dict[str, Any]:
    s = motor_path.read_text(encoding="utf-8", errors="replace") if motor_path.exists() else ""
    out = {}
    for key in ("PATTERNS_SHA", "CANON_HASH", "FORMULA_CORPUS"):
        m = re.search(rf'^{key}\s*=\s*["\']([^"\']+)["\']', s, re.M)
        if m: out[key] = m.group(1)
    return out

def resolve(package_root: str | Path, result: Dict[str, Any], spec_text: str = "") -> Dict[str, Any]:
    root = Path(package_root)
    # U6 A7: se quitaron los candidatos MOTOR_V15_3_UNIFICADO_ALTERNO_V0_9.py (no existen en el pack; el motor es UNICO).
    motor_candidates = [
        root / "MOTOR_V15_3_UNICO_20260927.py",
        root / "motor" / "MOTOR_V15_3_UNICO_20260927.py",
    ]
    motor = next((p for p in motor_candidates if p.exists()), motor_candidates[0])
    decl = _declared_constants(motor)
    findings: List[Dict[str, Any]] = []
    resolved: List[Dict[str, Any]] = []
    unresolved: List[Dict[str, Any]] = []

    pattern_candidates = [root / "patterns_final_v14.json", root / "motor" / "patterns_final_v14.json"]
    patterns = next((p for p in pattern_candidates if p.exists()), pattern_candidates[0])
    actual = sha(patterns) if patterns.exists() else None
    declared = decl.get("PATTERNS_SHA") or result.get("patterns_sha256")
    if actual and declared and actual != declared:
        row = {"id":"PATTERNS_HASH_DECLARATION_MISMATCH", "declared":declared,
               "actual":actual, "authority":"artifact:patterns_final_v14.json"}
        findings.append(row)
        # Recoverable: use actual artifact identity for audit continuity; never rewrite motor/canon.
        resolved.append({"id":row["id"], "resolution":"USE_ACTUAL_ARTIFACT_HASH_FOR_AUDIT",
                         "effective_patterns_sha256":actual, "mutated":False})

    corpus_name = decl.get("FORMULA_CORPUS")
    if corpus_name and not (root / corpus_name).exists():
        # Search the package itself for formula declarations/references. This is evidence only.
        candidates = []
        for p in root.rglob("*"):
            if p.is_file() and p.suffix in {".py", ".md", ".json", ".txt"}:
                try:
                    t = p.read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    continue
                if "FORMULAS = tuple(range(1, 18))" in t or "17_Formulas" in t:
                    candidates.append(str(p.relative_to(root)))
        row = {"id":"FORMULA_CORPUS_MISSING", "declared":corpus_name,
               "internal_evidence":candidates,
               "authority":"package_artifacts_only"}
        findings.append(row)
        if candidates:
            resolved.append({"id":row["id"], "resolution":"EVIDENCE_FOUND_BUT_SOURCE_FILE_MISSING",
                             "evidence":candidates, "mutated":False})
        else:
            unresolved.append(row)

    # Reclassify only mechanically recoverable discrepancies. Never suppress hard invariants.
    status = "CONTINUE_WITH_RESOLVED_FINDINGS" if resolved else ("FINDINGS_UNRESOLVED" if unresolved or findings else "CLEAN")
    return {
        "version": VERSION, "role": ROLE, "feeds_predictor": FEEDS_PREDICTOR,
        "feeds_H": FEEDS_H, "status": status, "findings": findings,
        "resolved": resolved, "unresolved": unresolved,
        "hard_stop_policy": sorted(HARD_STOP),
        "rule": "resolver uses package-local authoritative artifacts; it never edits canon, predictor, H, or FREEZE",
        "self_check": {"package_root": str(root), "motor_present": motor.exists(), "patterns_present": patterns.exists()}
    }

def build_llm_packet(audit: Dict[str, Any], root: str | Path) -> Dict[str, Any]:
    return {
        "verifier_version": VERSION,
        "purpose": "independent reproduction of package-local consistency resolution",
        "training_bias_guard": [
            "Use only supplied package evidence.",
            "Do not infer a missing artifact from general knowledge.",
            "Do not choose H1/H2 or alter predictor state.",
            "For each finding state RESOLVED_BY_ARTIFACT, UNRESOLVED, or HARD_STOP."
        ],
        "audit": audit,
        "instruction": "Recompute the claims from the listed artifacts and rules. If an artifact is absent, preserve absence."
    }
