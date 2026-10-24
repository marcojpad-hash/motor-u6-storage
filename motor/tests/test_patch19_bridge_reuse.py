import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "tests" / "fixtures" / "patch19_result_summary.json"
RECEIPT = ROOT / "tests" / "fixtures" / "patch19_receipt_summary.json"


def test_pre_h_reuses_validated_connected_bridge_without_live_search():
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    pre = result["features"]["pre_h_analogical_search"]
    assert pre["status"] == "EXECUTED"
    assert pre["reason"] == "pre_h_orientation_reused_connected_bridge"
    assert pre["provider_receipt"]["reused_bridge"] is True
    assert pre["provider_receipt"]["origin"] == "connected_tool_call"
    assert pre["raw_source_count"] == 3
    assert pre["analog_token_count"] > 0
    assert pre["query_blind"] is True
    assert pre["identity_exposed"] is False
    assert pre["future_outcome_exposed"] is False
    # Full source metadata remains in the main Caldero audit, not duplicated in PRE-H.
    assert "raw_sources" not in pre


def test_identity_filter_consumes_bridge_sources():
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    f = result["features"]["laterales_unico_detalle"]["sensores_pre"]["filtro_identidad"]
    assert f["n_fuentes"] == 3
    assert len(f["conservadas"]) + len(f["descartadas"]) == 3
    assert f["can_decide_H"] is False


def test_terminal_contract_and_canonical_hashes_preserved():
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert receipt["status"] == "COMPLETED" and receipt["schema"] == "COMPACTED_EVIDENCE_FIXTURE_V1"
    assert receipt["null_values_in_result_json"] == 0
    assert receipt["nonfinite_values_in_result_json"] == 0
    assert result["execution"]["component_inventory"][0]["sha256"] == "665c39a2861e58772522e91272563260d980908b1d4ab9f7092d3413d0c36082"
    assert result["patterns_sha256"] == "d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1"
    # Core predictor objects and final terminal hypotheses are different schemas;
    # do not copy one into the other to make the audit count look smaller.
    assert result["salida_interpretable"]["H1"]["familia"] == "arquetipo_el_sabio"
    assert result["salida_interpretable"]["H2"]["familia"] == "kwml_03_mago"
    assert len(result["auditoria_terminal_valores"]["campos_sin_valor"]) == 474


def test_optional_source_metadata_is_not_serialized_as_null():
    # This tests the serialization contract implemented by SearchSource.as_dict.
    import importlib.util
    import sys
    mod_path = ROOT / "motor" / "sidecar_caldero_busqueda_arquetipos.py"
    spec = importlib.util.spec_from_file_location("patch19_caldero", mod_path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    row = mod.SearchSource(url="https://example.org", title="Example", snippet="text").as_dict()
    assert "metadata" not in row
    assert row["metadata_estado"] == "NO_ENTREGADA_POR_FUENTE"
