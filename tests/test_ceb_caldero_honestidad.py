import importlib.util, sys
from pathlib import Path
B = Path(__file__).resolve().parent.parent / "motor/motor"
sys.path.insert(0, str(B))
spec = importlib.util.spec_from_file_location("lu", B / "laterales_unico_v1.py")
lu = importlib.util.module_from_spec(spec); spec.loader.exec_module(lu)

def _est(rc, cal):
    cb = {"presente": bool(cal), **lu._recibo_caldero(rc, cal)}
    return lu.estado_honesto_caldero(cb)

def test_fixture_no_es_ejecutado():
    rc = {"status": "EXECUTED_FIXTURE", "provider": "provided_fixture", "query_count": 1, "result_count": 5}
    e = _est(rc, {"status": "OK", "caldero_input": {"tokens_neighbors": [{"token": "x"}]}})
    assert e == "SIMULADO_FIXTURE" and e not in ("EJECUTADO", "EXECUTED")

def test_static_fixture_aun_con_status_executed():
    assert _est({"status": "EXECUTED", "provider": "static_fixture", "query_count": 1, "result_count": 3}, {"status": "OK"}) == "SIMULADO_FIXTURE"

def test_real():
    assert _est({"status": "EXECUTED", "provider": "exa", "query_count": 1, "result_count": 4}, {"status": "OK"}) == "EJECUTADO"

def test_real_cero_resultados():
    assert _est({"status": "EXECUTED", "provider": "exa", "query_count": 1, "result_count": 0}, {"status": "OK"}) == "INTENTADO_FALLIDO"

def test_fallido():
    assert _est({"status": "FAILED", "provider": "tavily", "error": "x"}, {"status": "REQUIRED_STAGE_FAILED"}) == "INTENTADO_FALLIDO"

def test_no_invocado():
    assert _est(None, {}) == "NO_INVOCADO"

def test_omitido():
    assert _est({"status": "SKIPPED_INTERNAL_ANALYSIS", "provider": "none"}, {"status": "SKIPPED_INTERNAL_ANALYSIS"}) == "OMITIDO_POR_CONDICION"
