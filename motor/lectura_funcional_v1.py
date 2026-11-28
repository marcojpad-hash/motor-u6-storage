#!/usr/bin/env python3
"""Post-run functional review package and fail-closed handoff gate.

This module never runs an LLM, never changes RESULT/RECIBO, and never changes
H1/H2. An independent reviewer produces the review JSON; this module binds it
to a minimal evidence package and validates the resulting handoff decision.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

PACKAGE_SCHEMA = "FUNCTIONAL_REVIEW_PACKAGE_V1"
REVIEW_SCHEMA = "FUNCTIONAL_REVIEW_V1"
GATE_SCHEMA = "FUNCTIONAL_GATE_RESULT_V1"
REVIEW_BASIS = "contract_and_final_artifact_without_producer_self_review"
ROOTS = {"input", "artifact", "evidence"}
REVIEW_KEYS = {
    "schema_version", "case_id", "package_sha256", "contract_sha256",
    "input_sha256", "result_sha256", "artifact_sha256", "producer",
    "reviewer", "review_basis", "decision", "checks", "evidence_map",
    "unmet_requirements", "critical_flags", "summary",
}


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: str | Path) -> str:
    return sha256_bytes(Path(path).read_bytes())


def load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json_new(path: str | Path, value: Any) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        raise FileExistsError("OUTPUT_ALREADY_EXISTS:" + str(target))
    with target.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n")


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _validate_pointer(pointer: Any) -> str:
    if not _nonempty_string(pointer) or not pointer.startswith("/"):
        raise ValueError("INVALID_JSON_POINTER")
    return pointer


def _pointer_get(root: Any, pointer: str) -> Any:
    pointer = _validate_pointer(pointer)
    current = root
    for raw in pointer[1:].split("/"):
        token = raw.replace("~1", "/").replace("~0", "~")
        if isinstance(current, dict) and token in current:
            current = current[token]
        elif isinstance(current, list) and token.isdigit() and int(token) < len(current):
            current = current[int(token)]
        else:
            raise KeyError("JSON_POINTER_NOT_FOUND:" + pointer)
    return current


def _select_paths(root: Any, paths: list[str]) -> dict[str, Any]:
    if not isinstance(paths, list) or not paths:
        raise ValueError("PATH_LIST_REQUIRED")
    if len(paths) != len(set(paths)):
        raise ValueError("DUPLICATE_JSON_POINTER")
    return {path: _pointer_get(root, path) for path in paths}


def validate_contract(contract: Any) -> dict[str, Any]:
    if not isinstance(contract, dict):
        raise ValueError("CONTRACT_MUST_BE_OBJECT")
    required = {
        "contract_id", "purpose", "audience", "desired_outcome",
        "constraints", "non_goals", "evidence_requirements",
        "completion_criteria", "input_paths", "artifact_paths",
        "evidence_paths", "gate_required",
    }
    missing = sorted(required - set(contract))
    if missing:
        raise ValueError("CONTRACT_MISSING_FIELDS:" + ",".join(missing))
    for key in ("contract_id", "purpose", "audience", "desired_outcome"):
        if not _nonempty_string(contract.get(key)):
            raise ValueError("CONTRACT_EMPTY_FIELD:" + key)
    for key in ("constraints", "non_goals", "evidence_requirements"):
        value = contract.get(key)
        if not isinstance(value, list) or any(not _nonempty_string(x) for x in value):
            raise ValueError("CONTRACT_INVALID_LIST:" + key)
    if not isinstance(contract.get("gate_required"), bool):
        raise ValueError("CONTRACT_GATE_REQUIRED_MUST_BE_BOOLEAN")
    criteria = contract.get("completion_criteria")
    if not isinstance(criteria, list) or not criteria:
        raise ValueError("CONTRACT_COMPLETION_CRITERIA_REQUIRED")
    ids = []
    for item in criteria:
        if not isinstance(item, dict):
            raise ValueError("INVALID_COMPLETION_CRITERION")
        if not _nonempty_string(item.get("id")) or not _nonempty_string(item.get("requirement")):
            raise ValueError("INVALID_COMPLETION_CRITERION_FIELDS")
        if not isinstance(item.get("critical"), bool):
            raise ValueError("CRITERION_CRITICAL_MUST_BE_BOOLEAN")
        ids.append(item["id"])
    if len(ids) != len(set(ids)):
        raise ValueError("DUPLICATE_COMPLETION_CRITERION_ID")
    for key in ("input_paths", "artifact_paths", "evidence_paths"):
        paths = contract.get(key)
        if not isinstance(paths, list) or not paths:
            raise ValueError("CONTRACT_PATHS_REQUIRED:" + key)
        for path in paths:
            _validate_pointer(path)
        if len(paths) != len(set(paths)):
            raise ValueError("DUPLICATE_CONTRACT_PATH:" + key)
    return contract


def _package_digest(package: dict[str, Any]) -> str:
    body = {key: value for key, value in package.items() if key != "package_sha256"}
    return sha256_bytes(canonical_bytes(body))


def prepare_package(
    input_path: str | Path,
    result_path: str | Path,
    contract_path: str | Path,
) -> dict[str, Any]:
    input_path = Path(input_path)
    result_path = Path(result_path)
    contract = validate_contract(load_json(contract_path))
    input_data = load_json(input_path)
    result_data = load_json(result_path)
    if not isinstance(input_data, dict) or not isinstance(result_data, dict):
        raise ValueError("INPUT_AND_RESULT_MUST_BE_OBJECTS")
    case_id = input_data.get("case_id")
    if not _nonempty_string(case_id) or result_data.get("case_id") != case_id:
        raise ValueError("CASE_ID_MISMATCH_OR_MISSING")
    selected_input = _select_paths(input_data, contract["input_paths"])
    selected_artifact = _select_paths(result_data, contract["artifact_paths"])
    selected_evidence = _select_paths(result_data, contract["evidence_paths"])
    package = {
        "schema_version": PACKAGE_SCHEMA,
        "case_id": case_id,
        "contract": contract,
        "input": selected_input,
        "artifact": selected_artifact,
        "evidence": selected_evidence,
        "hashes": {
            "input_sha256": sha256_file(input_path),
            "result_sha256": sha256_file(result_path),
            "contract_sha256": sha256_bytes(canonical_bytes(contract)),
            "artifact_sha256": sha256_bytes(canonical_bytes(selected_artifact)),
        },
    }
    package["package_sha256"] = _package_digest(package)
    return package


def _validate_package(package: Any) -> dict[str, Any]:
    if not isinstance(package, dict) or package.get("schema_version") != PACKAGE_SCHEMA:
        raise ValueError("INVALID_PACKAGE_SCHEMA")
    contract = validate_contract(package.get("contract"))
    if not _nonempty_string(package.get("case_id")):
        raise ValueError("PACKAGE_CASE_ID_MISSING")
    for root, key in (
        ("input", "input_paths"),
        ("artifact", "artifact_paths"),
        ("evidence", "evidence_paths"),
    ):
        values = package.get(root)
        if not isinstance(values, dict) or set(values) != set(contract[key]):
            raise ValueError("PACKAGE_PATH_SELECTION_MISMATCH:" + root)
    hashes = package.get("hashes")
    if not isinstance(hashes, dict):
        raise ValueError("PACKAGE_HASHES_MISSING")
    expected = {
        "contract_sha256": sha256_bytes(canonical_bytes(contract)),
        "artifact_sha256": sha256_bytes(canonical_bytes(package["artifact"])),
    }
    for key, value in expected.items():
        if hashes.get(key) != value:
            raise ValueError("PACKAGE_HASH_MISMATCH:" + key)
    for key in ("input_sha256", "result_sha256"):
        value = hashes.get(key)
        if not _nonempty_string(value) or len(value) != 64:
            raise ValueError("PACKAGE_HASH_MISSING:" + key)
    if package.get("package_sha256") != _package_digest(package):
        raise ValueError("PACKAGE_HASH_MISMATCH:package_sha256")
    return package


def _resolve_ref(package: dict[str, Any], ref: Any) -> Any:
    if not _nonempty_string(ref) or "#" not in ref:
        raise ValueError("INVALID_EVIDENCE_REFERENCE")
    root, pointer = ref.split("#", 1)
    if root not in ROOTS or not pointer.startswith("/"):
        raise ValueError("INVALID_EVIDENCE_REFERENCE:" + ref)
    selected = package[root]
    if pointer not in selected:
        raise KeyError("EVIDENCE_REFERENCE_NOT_IN_PACKAGE:" + ref)
    return selected[pointer]


def _blocked(
    package: Any,
    reason: str,
    detail: str = "",
    review_sha256: str | None = None,
) -> dict[str, Any]:
    contract = package.get("contract", {}) if isinstance(package, dict) else {}
    gate_required = contract.get("gate_required", True) if isinstance(contract, dict) else True
    hashes = package.get("hashes", {}) if isinstance(package, dict) else {}
    return {
        "schema_version": GATE_SCHEMA,
        "case_id": package.get("case_id") if isinstance(package, dict) else None,
        "status": "INDETERMINATE",
        "gate_required": bool(gate_required),
        "gate_decision": "BLOCKED" if gate_required else "NOT_GATING",
        "reason_codes": [reason],
        "detail": detail,
        "reviewer_independence_status": "NOT_ESTABLISHED",
        "hashes": hashes,
        "package_sha256": package.get("package_sha256") if isinstance(package, dict) else None,
        "review_sha256": review_sha256,
        "checks": [],
        "evidence_map": [],
        "unmet_requirements": [],
        "critical_flags": [],
        "summary": "No se acreditó una lectura funcional independiente y válida.",
    }


def apply_review(
    package: Any,
    review: Any,
    review_sha256: str | None = None,
) -> dict[str, Any]:
    try:
        package = _validate_package(package)
    except Exception as exc:
        return _blocked(package, "PACKAGE_INVALID", str(exc), review_sha256)
    contract = package["contract"]
    if review is None:
        return _blocked(package, "REVIEW_NOT_PROVIDED", "", review_sha256)
    try:
        if not isinstance(review, dict) or set(review) != REVIEW_KEYS:
            raise ValueError("REVIEW_FIELDS_MISMATCH")
        if review.get("schema_version") != REVIEW_SCHEMA:
            raise ValueError("INVALID_REVIEW_SCHEMA")
        if review.get("case_id") != package["case_id"]:
            raise ValueError("REVIEW_CASE_ID_MISMATCH")
        if review.get("package_sha256") != package["package_sha256"]:
            raise ValueError("REVIEW_HASH_MISMATCH:package_sha256")
        for key in ("contract_sha256", "input_sha256", "result_sha256", "artifact_sha256"):
            if review.get(key) != package["hashes"].get(key):
                raise ValueError("REVIEW_HASH_MISMATCH:" + key)
        if review.get("review_basis") != REVIEW_BASIS:
            raise ValueError("REVIEW_BASIS_MISMATCH")
        producer = review.get("producer")
        reviewer = review.get("reviewer")
        if not isinstance(producer, dict) or set(producer) != {"model", "run_id", "role"}:
            raise ValueError("INVALID_PRODUCER_ATTESTATION")
        if not isinstance(reviewer, dict) or set(reviewer) != {
            "model", "run_id", "role", "independent_attested"
        }:
            raise ValueError("INVALID_REVIEWER_ATTESTATION")
        for who in (producer, reviewer):
            if not _nonempty_string(who.get("model")) or not _nonempty_string(who.get("run_id")):
                raise ValueError("MODEL_AND_RUN_ID_REQUIRED")
        if producer.get("role") != "producer" or reviewer.get("role") != "independent_reviewer":
            raise ValueError("REVIEWER_ROLE_NOT_INDEPENDENT")
        if reviewer.get("independent_attested") is not True:
            raise ValueError("INDEPENDENCE_NOT_ATTESTED")
        if producer["model"] == reviewer["model"] or producer["run_id"] == reviewer["run_id"]:
            raise ValueError("PRODUCER_REVIEWER_NOT_DISTINCT")
        if not _nonempty_string(review.get("summary")):
            raise ValueError("REVIEW_SUMMARY_REQUIRED")
        checks = review.get("checks")
        evidence_map = review.get("evidence_map")
        if not isinstance(checks, list) or not isinstance(evidence_map, list) or not evidence_map:
            raise ValueError("CHECKS_AND_EVIDENCE_MAP_REQUIRED")
        criteria = contract["completion_criteria"]
        expected_ids = [item["id"] for item in criteria]
        check_ids = [item.get("id") for item in checks if isinstance(item, dict)]
        if len(check_ids) != len(checks) or len(check_ids) != len(set(check_ids)) or set(check_ids) != set(expected_ids):
            raise ValueError("REVIEW_CHECK_SET_MISMATCH")
        valid_refs = set()
        for item in evidence_map:
            if not isinstance(item, dict) or set(item) != {"ref", "relation", "note"}:
                raise ValueError("INVALID_EVIDENCE_MAP_ITEM")
            _resolve_ref(package, item.get("ref"))
            if item.get("relation") not in {"supports", "contradicts", "limits"}:
                raise ValueError("INVALID_EVIDENCE_RELATION")
            if not _nonempty_string(item.get("note")):
                raise ValueError("EVIDENCE_NOTE_REQUIRED")
            if item["ref"] in valid_refs:
                raise ValueError("DUPLICATE_EVIDENCE_REFERENCE")
            valid_refs.add(item["ref"])
        status_by_id = {}
        for check in checks:
            if not isinstance(check, dict) or set(check) != {"id", "status", "evidence_refs", "note"}:
                raise ValueError("INVALID_REVIEW_CHECK")
            if check.get("status") not in {"PASS", "FAIL", "UNKNOWN"}:
                raise ValueError("INVALID_CHECK_STATUS")
            refs = check.get("evidence_refs")
            if not isinstance(refs, list) or any(not _nonempty_string(x) for x in refs):
                raise ValueError("INVALID_CHECK_EVIDENCE_REFS")
            if check["status"] != "UNKNOWN" and not refs:
                raise ValueError("CHECK_WITHOUT_EVIDENCE:" + check["id"])
            for ref in refs:
                _resolve_ref(package, ref)
                if ref not in valid_refs:
                    raise ValueError("CHECK_REFERENCE_NOT_MAPPED:" + ref)
            if not _nonempty_string(check.get("note")):
                raise ValueError("CHECK_NOTE_REQUIRED")
            status_by_id[check["id"]] = check["status"]
        unmet = review.get("unmet_requirements")
        flags = review.get("critical_flags")
        if not isinstance(unmet, list) or any(x not in expected_ids for x in unmet):
            raise ValueError("INVALID_UNMET_REQUIREMENTS")
        if len(unmet) != len(set(unmet)):
            raise ValueError("DUPLICATE_UNMET_REQUIREMENT")
        expected_unmet = {key for key, value in status_by_id.items() if value != "PASS"}
        if set(unmet) != expected_unmet:
            raise ValueError("UNMET_REQUIREMENTS_MISMATCH")
        if not isinstance(flags, list) or any(not _nonempty_string(x) for x in flags):
            raise ValueError("INVALID_CRITICAL_FLAGS")
        if any(status == "FAIL" for status in status_by_id.values()) or flags:
            derived = "FAIL"
        elif any(status == "UNKNOWN" for status in status_by_id.values()):
            derived = "INDETERMINATE"
        else:
            derived = "PASS"
        if review.get("decision") != derived:
            raise ValueError("REVIEW_DECISION_MISMATCH")
        gate_required = contract["gate_required"]
        gate_decision = (
            "NOT_GATING" if not gate_required
            else "ALLOWED" if derived == "PASS"
            else "BLOCKED"
        )
        reason = {
            "PASS": "FUNCTIONAL_REVIEW_PASS",
            "FAIL": "FUNCTIONAL_REQUIREMENT_NOT_MET",
            "INDETERMINATE": "FUNCTIONAL_EVIDENCE_INSUFFICIENT",
        }[derived]
        return {
            "schema_version": GATE_SCHEMA,
            "case_id": package["case_id"],
            "contract_id": contract["contract_id"],
            "status": derived,
            "gate_required": gate_required,
            "gate_decision": gate_decision,
            "reason_codes": [reason],
            "reviewer_independence_status": "DECLARED_ONLY",
            "producer_model": producer["model"],
            "producer_run_id": producer["run_id"],
            "reviewer_model": reviewer["model"],
            "reviewer_run_id": reviewer["run_id"],
            "review_basis": REVIEW_BASIS,
            "hashes": package["hashes"],
            "package_sha256": package["package_sha256"],
            "review_sha256": review_sha256,
            "checks": checks,
            "evidence_map": evidence_map,
            "unmet_requirements": unmet,
            "critical_flags": flags,
            "summary": review["summary"],
        }
    except Exception as exc:
        return _blocked(package, "REVIEW_INVALID", str(exc), review_sha256)


def _ensure_distinct_output(out: str | Path, *sources: str | Path) -> None:
    target = Path(out).resolve()
    for source in sources:
        if Path(source).resolve() == target:
            raise ValueError("OUTPUT_MUST_NOT_OVERWRITE_INPUT")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Prepara un paquete mínimo y valida una lectura funcional independiente post-corrida."
    )
    sub = parser.add_subparsers(dest="command", required=True)
    prep = sub.add_parser("prepare")
    prep.add_argument("--input", required=True)
    prep.add_argument("--result", required=True)
    prep.add_argument("--contract", required=True)
    prep.add_argument("--out", required=True)
    apply = sub.add_parser("apply")
    apply.add_argument("--package", required=True)
    apply.add_argument("--review")
    apply.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    if args.command == "prepare":
        try:
            _ensure_distinct_output(args.out, args.input, args.result, args.contract)
            package = prepare_package(args.input, args.result, args.contract)
            write_json_new(args.out, package)
            print(json.dumps({
                "status": "PACKAGE_READY",
                "case_id": package["case_id"],
                "package_sha256": package["package_sha256"],
            }, ensure_ascii=False))
            return 0
        except Exception as exc:
            print(json.dumps({"status": "PREPARATION_FAILED", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
            return 2
    try:
        _ensure_distinct_output(args.out, args.package, *([args.review] if args.review else []))
        package = load_json(args.package)
    except Exception as exc:
        gate = _blocked(None, "PACKAGE_UNREADABLE", str(exc))
        write_json_new(args.out, gate)
        print(json.dumps({"status": gate["status"], "gate_decision": gate["gate_decision"]}, ensure_ascii=False))
        return 5
    if args.review:
        try:
            review = load_json(args.review)
            review_hash = sha256_file(args.review)
        except Exception as exc:
            gate = _blocked(package, "REVIEW_UNREADABLE", str(exc))
        else:
            gate = apply_review(package, review, review_hash)
    else:
        gate = apply_review(package, None)
    try:
        write_json_new(args.out, gate)
    except Exception as exc:
        print(json.dumps({"status": "OUTPUT_FAILED", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps({
        "status": gate["status"],
        "gate_decision": gate["gate_decision"],
        "case_id": gate.get("case_id"),
        "reason_codes": gate["reason_codes"],
    }, ensure_ascii=False))
    return 5 if gate["gate_decision"] == "BLOCKED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
