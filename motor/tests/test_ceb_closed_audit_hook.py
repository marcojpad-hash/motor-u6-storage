import importlib.util
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
