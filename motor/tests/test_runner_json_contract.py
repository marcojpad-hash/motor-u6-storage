import importlib.util
import shutil
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


def test_continuity_state_is_explicit_when_no_pause_is_required():
    assert runner._continuity_result_payload(None) == {
        "status": "NO_PAUSADA",
        "final_decision_authorized": True,
    }

def test_continuity_state_preserves_reanudable_pause_contract():
    pause = {
        "status": "PAUSADA_REANUDABLE",
        "final_decision_authorized": False,
        "required_next_action": "reanudar",
    }
    assert runner._continuity_result_payload(pause) == pause

# Integration cases for the cloned enunciative-context lateral in U6.
_control_spec = importlib.util.spec_from_file_location(
    "guardianes_control_contexto_test", ROOT / "motor" / "guardianes_control_v1.py"
)
_control = importlib.util.module_from_spec(_control_spec)
_control_spec.loader.exec_module(_control)

_OMIT_OTHER_GUARDIANS = {
    "DECIMO_HOMBRE_LATENCIA", "PREGUNTA_DETRAS_V2",
    "PREGUNTA_DIRIGIDA_POST_HOC", "FALACIAS", "LOGICA_COPI",
    "POLARIDAD_CAUSAL", "HOMBRE_DE_ACERO", "SHERLOCK_RIGOR",
    "TROPOS_BERISTAIN",
}


def test_u6_full_guardian_pack_runs_case_and_routes_context_without_changing_decisions(tmp_path):
    base = tmp_path / "motor"
    shutil.copytree(ROOT / "motor", base)
    case = {"case_id": "CTX-01", "enunciador": "FUENTE_DE_INPUT", "question": "Ariadna es brillante. Ariadna es admirable. Bruno es mediocre. Bruno es un traidor."}
    result = _control.correr_guardianes(case, {}, {}, base)
    blocks = {b["guardian"]: b for b in result["bloques"]}
    lateral = blocks["CONTEXTO_ENUNCIATIVO"]
    assert lateral["bandera"] == "MARCA"
    assert lateral["can_decide_H"] is False
    assert "EXPRESIVA" in lateral["detalle"]["observaciones"][0]["funciones_linguisticas"]["buhler"]
    assert "EMOTIVA" in lateral["detalle"]["observaciones"][0]["funciones_linguisticas"]["jakobson"]
    assert "INTERPERSONAL" in lateral["detalle"]["observaciones"][0]["funciones_linguisticas"]["halliday"]
    assert any(m["tipo"] == "CARGA_VALORATIVA_REITERADA" for m in lateral["marcas"])
    assert any(m["tipo"] == "ASIMETRIA_VALORATIVA_ENTRE_ACTORES" for m in lateral["marcas"])
    assert lateral["detalle"]["observaciones"][0]["enunciador"] == "FUENTE_DE_INPUT"
    for name in ("SHERLOCK_RIGOR", "FALACIAS", "LOGICA_COPI", "TROPOS_BERISTAIN"):
        assert blocks[name]["bandera"] != "ERROR", (name, blocks[name])
        assert "contexto_lateral_enunciativo" in blocks[name].get("detalle", {}), (name, blocks[name])
    assert result["ruta_cierre_latente"]["estado_cierre"] == "SIN_OBJECION_DE_GUARDIANES"


def test_u6_pipeline_keeps_neutral_input_clean(tmp_path):
    shutil.copy2(ROOT / "motor" / "lateral_contexto_enunciativo_v1.py",
                 tmp_path / "lateral_contexto_enunciativo_v1.py")
    case = {"case_id": "CTX-02", "question": "La reunión comenzó a las nueve y terminó a las diez."}
    result = _control.correr_guardianes(case, {}, {}, tmp_path, omitir=_OMIT_OTHER_GUARDIANS)
    blocks = {b["guardian"]: b for b in result["bloques"]}
    assert blocks["CONTEXTO_ENUNCIATIVO"]["bandera"] == "LIMPIO"
    assert blocks["CONTEXTO_ENUNCIATIVO"]["n_marcas"] == 0


# Regression tests for unclassified linguistic polarity in the U6 lateral.
_lateral_spec = importlib.util.spec_from_file_location(
    "lateral_contexto_enunciativo_test", ROOT / "motor" / "lateral_contexto_enunciativo_v1.py"
)
_lateral = importlib.util.module_from_spec(_lateral_spec)
_lateral_spec.loader.exec_module(_lateral)


def test_lateral_counts_all_four_polarities_without_key_error():
    report = _lateral.analyze([
        {"text": "Ariadna debe cumplir."},
        {"text": "Bruno es brillante."},
        {"text": "Carla es mediocre."},
        {"text": "Dalia es brillante y mediocre."},
    ])
    counts = report["conteos_por_actor"]
    assert counts["Ariadna"] == {
        "POSITIVA": 0, "NEGATIVA": 0, "MIXTA": 0, "NO_CLASIFICADA": 1
    }
    assert counts["Bruno"]["POSITIVA"] == 1
    assert counts["Carla"]["NEGATIVA"] == 1
    assert counts["Dalia"]["MIXTA"] == 1
    assert all("NO_CLASIFICADA" in actor_counts for actor_counts in counts.values())
    # Unclassified observations are preserved but do not inflate evaluative signals.
    assert not any(s["tipo"] == "CARGA_VALORATIVA_REITERADA" for s in report["senales"])


def test_lateral_empty_and_blank_records_are_safe():
    report = _lateral.analyze([None, {}, {"text": "   "}, {"text": ""}])
    assert report["observaciones"] == []
    assert report["senales"] == []
    assert report["conteos_por_actor"] == {}
