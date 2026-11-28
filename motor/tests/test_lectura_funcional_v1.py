import json

from motor.lectura_funcional_v1 import (
    REVIEW_BASIS,
    REVIEW_SCHEMA,
    apply_review,
    prepare_package,
)


def _write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def _fixture(tmp_path, gate_required=True):
    input_data = {
        "case_id": "SYNTH_FUNCTIONAL_01",
        "question": "What does the result support?",
        "cuts": [{"id": "C1", "fact": "A dated observation."}],
        "private_unselected": "must not be copied into the review package",
    }
    result_data = {
        "case_id": "SYNTH_FUNCTIONAL_01",
        "cierre_final": {"apuesta": {"familia_apostada": "H1", "frente_a": "H2"}},
        "respuesta_humana": {"respuesta": "The answer is bounded by the recorded observation."},
        "traduccion_salida": {"lectura": "The result supports a bounded conclusion."},
        "sources": [{"id": "SRC-1", "url": "https://example.org/primary"}],
        "producer_notes": "must not be copied into the review package",
    }
    contract = {
        "contract_id": "SYNTH_TASK_CONTRACT",
        "task_type": "analysis",
        "purpose": "Answer the task using traceable evidence.",
        "audience": "requester",
        "desired_outcome": "A concise answer with an auditable path.",
        "constraints": ["Do not alter the sealed result."],
        "non_goals": ["Do not infer facts absent from the evidence."],
        "evidence_requirements": ["Every material conclusion has an evidence reference."],
        "completion_criteria": [
            {"id": "purpose_fulfilled", "requirement": "The answer serves the stated purpose.", "critical": True},
            {"id": "intent_coherence", "requirement": "The answer remains coherent with the task contract.", "critical": True},
            {"id": "evidence_traceable", "requirement": "The answer can be reconstructed from admitted evidence.", "critical": True},
        ],
        "input_paths": ["/question", "/cuts/0"],
        "artifact_paths": ["/respuesta_humana/respuesta", "/traduccion_salida/lectura"],
        "evidence_paths": ["/cierre_final/apuesta", "/sources/0"],
        "gate_required": gate_required,
    }
    input_path = tmp_path / "input.json"
    result_path = tmp_path / "result.json"
    contract_path = tmp_path / "contract.json"
    _write(input_path, input_data)
    _write(result_path, result_data)
    _write(contract_path, contract)
    package = prepare_package(input_path, result_path, contract_path)
    return input_path, result_path, package


def _review(package, statuses=None, reviewer_model="Model-B", reviewer_run="review-run-1"):
    statuses = statuses or {}
    criteria = package["contract"]["completion_criteria"]
    refs = {
        "purpose_fulfilled": ["input#/question", "artifact#/respuesta_humana/respuesta"],
        "intent_coherence": ["artifact#/traduccion_salida/lectura", "evidence#/cierre_final/apuesta"],
        "evidence_traceable": ["input#/cuts/0", "evidence#/sources/0"],
    }
    checks = []
    for criterion in criteria:
        status = statuses.get(criterion["id"], "PASS")
        checks.append({
            "id": criterion["id"],
            "status": status,
            "evidence_refs": refs.get(criterion["id"], ["artifact#/respuesta_humana/respuesta"]) if status != "UNKNOWN" else [],
            "note": "Concise criterion-level finding.",
        })
    evidence_refs = sorted({ref for check in checks for ref in check["evidence_refs"]})
    evidence_map = [
        {"ref": ref, "relation": "supports", "note": "Evidence excerpt relevant to the criterion."}
        for ref in evidence_refs
    ]
    unmet = [check["id"] for check in checks if check["status"] != "PASS"]
    if any(check["status"] == "FAIL" for check in checks):
        decision = "FAIL"
    elif any(check["status"] == "UNKNOWN" for check in checks):
        decision = "INDETERMINATE"
    else:
        decision = "PASS"
    return {
        "schema_version": REVIEW_SCHEMA,
        "case_id": package["case_id"],
        "package_sha256": package["package_sha256"],
        "contract_sha256": package["hashes"]["contract_sha256"],
        "input_sha256": package["hashes"]["input_sha256"],
        "result_sha256": package["hashes"]["result_sha256"],
        "artifact_sha256": package["hashes"]["artifact_sha256"],
        "producer": {"model": "Model-A", "run_id": "producer-run-1", "role": "producer"},
        "reviewer": {
            "model": reviewer_model,
            "run_id": reviewer_run,
            "role": "independent_reviewer",
            "independent_attested": True,
        },
        "review_basis": REVIEW_BASIS,
        "decision": decision,
        "checks": checks,
        "evidence_map": evidence_map,
        "unmet_requirements": unmet,
        "critical_flags": [],
        "summary": "The artifact was evaluated against its task-specific contract.",
    }


def test_prepare_package_selects_only_declared_minimum_paths(tmp_path):
    input_path, result_path, package = _fixture(tmp_path)
    assert package["schema_version"] == "FUNCTIONAL_REVIEW_PACKAGE_V1"
    assert set(package["input"]) == {"/question", "/cuts/0"}
    assert set(package["artifact"]) == {
        "/respuesta_humana/respuesta", "/traduccion_salida/lectura"
    }
    assert "private_unselected" not in json.dumps(package)
    assert "producer_notes" not in json.dumps(package)
    assert len(package["package_sha256"]) == 64
    assert input_path.exists() and result_path.exists()


def test_valid_independent_review_allows_handoff_and_does_not_mutate_result(tmp_path):
    input_path, result_path, package = _fixture(tmp_path)
    before_input = input_path.read_bytes()
    before_result = result_path.read_bytes()
    gate = apply_review(package, _review(package))
    assert gate["status"] == "PASS"
    assert gate["gate_decision"] == "ALLOWED"
    assert gate["reviewer_independence_status"] == "DECLARED_ONLY"
    assert input_path.read_bytes() == before_input
    assert result_path.read_bytes() == before_result


def test_failed_functional_criterion_blocks_handoff(tmp_path):
    _, _, package = _fixture(tmp_path)
    review = _review(package, {"intent_coherence": "FAIL"})
    gate = apply_review(package, review)
    assert gate["status"] == "FAIL"
    assert gate["gate_decision"] == "BLOCKED"
    assert "intent_coherence" in gate["unmet_requirements"]


def test_unknown_criterion_is_indeterminate_and_blocks_handoff(tmp_path):
    _, _, package = _fixture(tmp_path)
    review = _review(package, {"evidence_traceable": "UNKNOWN"})
    gate = apply_review(package, review)
    assert gate["status"] == "INDETERMINATE"
    assert gate["gate_decision"] == "BLOCKED"


def test_missing_review_fails_closed(tmp_path):
    _, _, package = _fixture(tmp_path)
    gate = apply_review(package, None)
    assert gate["status"] == "INDETERMINATE"
    assert gate["gate_decision"] == "BLOCKED"
    assert gate["reason_codes"] == ["REVIEW_NOT_PROVIDED"]


def test_hash_mismatch_fails_closed(tmp_path):
    _, _, package = _fixture(tmp_path)
    review = _review(package)
    review["result_sha256"] = "0" * 64
    gate = apply_review(package, review)
    assert gate["status"] == "INDETERMINATE"
    assert gate["gate_decision"] == "BLOCKED"
    assert gate["reason_codes"] == ["REVIEW_INVALID"]


def test_same_model_cannot_attest_as_independent_reviewer(tmp_path):
    _, _, package = _fixture(tmp_path)
    review = _review(package, reviewer_model="Model-A")
    gate = apply_review(package, review)
    assert gate["status"] == "INDETERMINATE"
    assert gate["gate_decision"] == "BLOCKED"


def test_same_run_cannot_attest_as_independent_reviewer(tmp_path):
    _, _, package = _fixture(tmp_path)
    review = _review(package, reviewer_run="producer-run-1")
    gate = apply_review(package, review)
    assert gate["status"] == "INDETERMINATE"
    assert gate["gate_decision"] == "BLOCKED"


def test_invalid_evidence_reference_fails_closed(tmp_path):
    _, _, package = _fixture(tmp_path)
    review = _review(package)
    review["checks"][0]["evidence_refs"] = ["input#/not_in_package"]
    review["evidence_map"].append({
        "ref": "input#/not_in_package",
        "relation": "supports",
        "note": "invalid reference",
    })
    gate = apply_review(package, review)
    assert gate["status"] == "INDETERMINATE"
    assert gate["gate_decision"] == "BLOCKED"


def test_non_gating_contract_keeps_diagnostic_without_claiming_release(tmp_path):
    _, _, package = _fixture(tmp_path, gate_required=False)
    review = _review(package, {"purpose_fulfilled": "FAIL"})
    gate = apply_review(package, review)
    assert gate["status"] == "FAIL"
    assert gate["gate_decision"] == "NOT_GATING"


def test_task_specific_criteria_are_not_hardcoded_to_editorial_checks(tmp_path):
    _, _, package = _fixture(tmp_path)
    ids = {item["id"] for item in package["contract"]["completion_criteria"]}
    assert ids == {"purpose_fulfilled", "intent_coherence", "evidence_traceable"}
