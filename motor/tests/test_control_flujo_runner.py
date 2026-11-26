"""U7: runner-wide integration of control_flujo_soluciones."""
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "correr_estandar.py"


def _load_runner():
    spec = importlib.util.spec_from_file_location("runner_control_flujo_test", RUNNER)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_runner_control_flujo_produces_plan():
    runner = _load_runner()
    plan = runner._plan_contorno("ModuleNotFoundError: lateral faltante", "test")
    assert plan["plugin"] == "CONTROL_FLUJO_SOLUCIONES"
    assert plan["tipo_piedra"] == "import_o_dependencia"
    assert plan["contornos"] and plan["formato_respuesta_obligatorio"]
    assert plan["Alimenta_H"] == "NO"


def test_unhandled_runner_exception_gets_contour_and_nonzero_exit(monkeypatch, capsys):
    runner = _load_runner()
    def fail(_argv):
        raise RuntimeError("fallo sintético de runner")
    monkeypatch.setattr(runner, "main", fail)
    rc = runner._main_with_control_flujo(["correr_estandar.py", "caso.json"])
    payload = json.loads(capsys.readouterr().err.strip())
    assert rc == 3
    assert payload["estado_ejecucion"] == "FALLIDA"
    assert payload["stage"] == "runner_unhandled_exception"
    assert payload["plan_contorno"]["plugin"] == "CONTROL_FLUJO_SOLUCIONES"
    assert payload["plan_contorno"]["contornos"]


def test_contour_does_not_bypass_hard_gate():
    runner = _load_runner()
    plan = runner._plan_contorno("hash mismatch ENGINE canonical", "test_hard_gate")
    assert plan["plugin"] == "CONTROL_FLUJO_SOLUCIONES"
    assert plan["Alimenta_H"] == "NO"
    assert plan["parada_dura"] is True
    assert plan["accion"] == "DIAGNOSTICAR_SIN_EJECUTAR"
    assert not any("BYPASS_HASH_CAMBIO" in str(x) for x in plan["contornos"])
