import importlib.util
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("runner_json_contract", ROOT / "correr_estandar.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)

def test_missing_data_is_not_mislabeled_tortugas():
    cleaned, missing, nonfinite = runner._sanitize_json_contract({"a": None, "b": [float("nan"), {"c": float("inf")}]})
    assert cleaned == {"a": "DATO_AUSENTE_REQUIERE_CLASIFICACION", "b": ["VALOR_NO_FINITO_REQUIERE_REMEDICION", {"c": "VALOR_NO_FINITO_REQUIERE_REMEDICION"}]}
    assert missing == ["$.a"]
    assert nonfinite == ["$.b[0]", "$.b[1].c"]
    assert runner._json_health(cleaned) == {"nulls": 0, "nonfinite": 0}

def test_provenance_hash_gap_is_distinct_from_missing_decision_data():
    cleaned, missing, nonfinite = runner._sanitize_json_contract({"matriz": {"data_table_sha256": None}, "H1": None})
    assert cleaned["matriz"]["data_table_sha256"] == "HUELLA_ORIGEN_NO_DISPONIBLE"
    assert cleaned["H1"] == "DATO_AUSENTE_REQUIERE_CLASIFICACION"
    assert missing == ["$.matriz.data_table_sha256", "$.H1"]
    assert not nonfinite

def test_receipt_status_distinguishes_metadata_gap_from_incomplete_data():
    assert runner._receipt_status(False, [], []) == "COMPLETED"
    assert runner._receipt_status(False, ["$.x.data_table_sha256"], []) == "COMPLETED_WITH_METADATA_GAP"
    assert runner._receipt_status(False, ["$.H1"], []) == "INCOMPLETE_OUTPUT_DATA"
    assert runner._receipt_status(False, [], ["$.score"]) == "INCOMPLETE_NONFINITE_OUTPUT"
    assert runner._receipt_status(True, [], []) == "INCOMPLETE_REQUIRED_EXTERNAL_SEARCH"

def test_result_health_counts_real_nulls_not_assumed_zero():
    assert runner._json_health({"x": None, "y": [float("nan")]}) == {"nulls": 1, "nonfinite": 1}

def test_terminal_gate_pauses_instead_of_accepting_unresolved_state():
    result = {"terminal_resolution": {"status": "LATENCIA_INFORMACIONAL"}, "hipotesis": [{"familia": "A"}]}
    pause = runner._terminal_continuity_gate(result)
    assert pause["status"] == "PAUSADA_REANUDABLE"
    assert pause["final_decision_authorized"] is False
    assert pause["hypotheses_preserved"] == [{"familia": "A"}]

def test_terminal_gate_pauses_if_tortugas_failed_when_required():
    result = {"terminal_resolution": {"status": "RESUELTO_OPERACIONALMENTE", "tortugas_status": "ERROR", "tortugas_ejecutado": False},
              "resolucion_operativa_final": {"estado_durante_corrida": "RESOLUCION_REQUERIDA"},
              "hipotesis": [{"familia": "A"}, {"familia": "B"}]}
    pause = runner._terminal_continuity_gate(result)
    assert pause["status"] == "PAUSADA_REANUDABLE"
    assert pause["reason"] == "TORTUGAS_REQUIERE_CONTINUACION"
    assert pause["final_decision_authorized"] is False

def test_terminal_gate_allows_validated_operational_resolution():
    result = {"terminal_resolution": {"status": "RESUELTO_OPERACIONALMENTE", "tortugas_status": "EJECUTADO", "tortugas_ejecutado": True},
              "resolucion_operativa_final": {"estado_durante_corrida": "RESOLUCION_REQUERIDA"}}
    assert runner._terminal_continuity_gate(result) is None
