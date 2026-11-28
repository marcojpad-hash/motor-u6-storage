import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MOD = ROOT / 'motor' / 'ceb_runtime_v0_6_flow.py'
spec = importlib.util.spec_from_file_location('ceb_closed_audit_test', MOD)
ceb = importlib.util.module_from_spec(spec); spec.loader.exec_module(ceb)


def test_closed_ledger_audit_hook_is_inert_on_later_file_io(tmp_path):
    ledger = ceb.FlowLedger(tmp_path / 'ceb', run_id='closed-hook-test')
    ledger.register('s', 'stage')
    ledger.close()
    before = ledger.path.stat().st_size
    old_stage = getattr(ceb._CTX, 'stage', None)
    ceb._CTX.stage = 'later_run'
    try:
        target = tmp_path / 'unrelated.json'
        target.write_text('{"ok":true}', encoding='utf-8')
        target.read_text(encoding='utf-8')
    finally:
        ceb._CTX.stage = old_stage
    assert ledger.path.stat().st_size == before
    assert ledger._closed is True


def test_verifier_marca_salida_persistida_sin_consumidor(tmp_path):
    # V7 (C-F7): el neighbor_store de la corrida V7 quedó con
    # OUTPUT_NO_OBSERVED_CONSUMER — la única anomalía del
    # VERIFIED_FLOW_WITH_ANOMALIES. Este test demuestra el veredicto con un
    # ledger sintético: una etapa que produce salida sin consumidor observado
    # y un recibo que la declara como feed.
    ledger = tmp_path / "ledger.jsonl"
    rows = [
        {"event": "STAGE_REGISTER", "stage_id": "neighbor_store",
         "payload": {"name": "vecinos_caldero.neighbor_store"}},
        {"event": "STAGE_START", "stage_id": "neighbor_store", "payload": {}},
        {"event": "STAGE_OUTPUT", "stage_id": "neighbor_store",
         "payload": {"output": {"empty": False}}},
        {"event": "STAGE_END", "stage_id": "neighbor_store", "payload": {}},
        {"event": "RUN_END", "stage_id": "run", "payload": {}},
    ]
    ledger.write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")
    report = {"component_status": [
        {"component": "vecinos_caldero.neighbor_store", "status": "EXECUTED",
         "feeds_predictor": True}]}
    out = ceb.FlowVerifier(ledger).verify(report)
    assert out["stages"]["neighbor_store"]["status"] == "OUTPUT_NO_OBSERVED_CONSUMER"
    assert out["status"] == "VERIFIED_FLOW_WITH_ANOMALIES"
    assert any(a.get("type") == "FEEDS_OUTPUT_NOT_CONSUMED" for a in out["anomalies"])


def test_verifier_optional_failed_stage_is_non_blocking_but_visible(tmp_path):
    ledger = tmp_path / "optional-failure.jsonl"
    stage_id = "sidecar_caldero_busqueda_arquetipos#1"
    rows = [
        {"event": "STAGE_REGISTER", "stage_id": stage_id,
         "payload": {"name": "sidecar_caldero_busqueda_arquetipos"}},
        {"event": "STAGE_START", "stage_id": stage_id, "payload": {}},
        {"event": "STAGE_ERROR", "stage_id": stage_id,
         "payload": {"type": "RuntimeError", "message": "búsqueda externa deshabilitada"}},
        {"event": "STAGE_END", "stage_id": stage_id, "payload": {}},
        {"event": "RUN_END", "stage_id": "run", "payload": {}},
    ]
    ledger.write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")
    report = {"execution": {"component_status": [
        {"component": "sidecar_caldero_busqueda_arquetipos.py",
         "status": "OPTIONAL_STAGE_FAILED", "required": False,
         "feeds_predictor": False, "error": "búsqueda externa deshabilitada"}
    ]}}
    out = ceb.FlowVerifier(ledger).verify(report)
    assert out["stages"][stage_id]["status"] == "FAILED_OPTIONAL_STAGE"
    assert out["status"] == "VERIFIED_FLOW_WITH_ANOMALIES"
    assert any(a.get("type") == "OPTIONAL_STAGE_FAILED" and a.get("required") is False
               for a in out["anomalies"])


def test_verifier_required_failed_stage_remains_incomplete(tmp_path):
    ledger = tmp_path / "required-failure.jsonl"
    stage_id = "required_stage#1"
    rows = [
        {"event": "STAGE_REGISTER", "stage_id": stage_id,
         "payload": {"name": "required_stage"}},
        {"event": "STAGE_START", "stage_id": stage_id, "payload": {}},
        {"event": "STAGE_ERROR", "stage_id": stage_id,
         "payload": {"type": "RuntimeError", "message": "required failure"}},
        {"event": "STAGE_END", "stage_id": stage_id, "payload": {}},
        {"event": "RUN_END", "stage_id": "run", "payload": {}},
    ]
    ledger.write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")
    report = {"execution": {"component_status": [
        {"component": "required_stage.py", "status": "FAILED",
         "required": True, "feeds_predictor": True}
    ]}}
    out = ceb.FlowVerifier(ledger).verify(report)
    assert out["stages"][stage_id]["status"] == "FAILED"
    assert out["status"] == "INCOMPLETE"
