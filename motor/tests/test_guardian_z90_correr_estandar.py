"""Regresión del guardián Z90 en el runner estándar (Issue #64)."""
import importlib.util
import json
import os
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("runner_guardian_z90_test", ROOT / "correr_estandar.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


def _caso_gate_z(corte_fecha=None, con_evidencia=True):
    nacimiento = date(1600, 1, 1)
    muerte = date(1640, 1, 1)
    z90 = nacimiento + timedelta(days=((muerte - nacimiento).days * 9) // 10)
    fechas = [nacimiento, date(1610, 1, 1), z90]
    cuts = []
    for i, fecha in enumerate(fechas):
        if i == 0 and corte_fecha:
            fecha = date.fromisoformat(corte_fecha)
        iso = fecha.isoformat()
        evidencia = [{
            "afirmacion": "Hecho de prueba con fuente primaria.",
            "source_url": "https://example.org/fixture-primary-source",
            "source_date": iso,
            "claim_date": iso,
            "tipo_fuente": "primaria",
            "conocido_en_Z": "sí",
        }] if con_evidencia else []
        cuts.append({
            "id": f"C{i + 1}",
            "date": iso,
            "window_start": nacimiento.isoformat(),
            "hecho": f"Observación del corte {i + 1}.",
            "evidencia": evidencia,
        })
    return {
        "case_id": "TEST_Z90_RUNNER",
        "question": "Caso sintético para probar la compuerta temporal.",
        "source_notes": "Fixture de prueba; no representa una corrida ni un sujeto real.",
        "gate_z": "GATE_Z_TRABAJO_20261024",
        "fecha_nacimiento": nacimiento.isoformat(),
        "fecha_muerte": muerte.isoformat(),
        "z_trabajo": z90.isoformat(),
        "z90_date": z90.isoformat(),
        "modo_z": "historico",
        "preparacion_ciega": {
            "preparador_entrada": "Preparador A",
            "custodio_destino": "Custodio B",
            "vio_destino": False,
        },
        "cuts": cuts,
    }


def test_guardian_z90_no_configurado_sin_disciplina():
    caso = {"case_id": "X", "cuts": [{"id": "C1", "date": "1799-11-09", "hecho": "x"}]}
    veredicto = runner._guardian_z90(caso)
    assert veredicto["status"] == "NO_CONFIGURADO"
    assert veredicto["bloquea"] is False


def test_guardian_z90_pass_con_z90_biografico_completo():
    veredicto = runner._guardian_z90(_caso_gate_z())
    assert veredicto["status"] == "PASS"
    assert veredicto["bloquea"] is False
    assert veredicto["errores"] == []


def test_guardian_z90_rechaza_corte_posterior_a_z90():
    veredicto = runner._guardian_z90(_caso_gate_z(corte_fecha="1700-01-01"))
    assert veredicto["status"] == "RECHAZADO"
    assert veredicto["bloquea"] is True
    assert any("posterior a Z" in error for error in veredicto["errores"])


def test_guardian_z90_rechaza_cortes_sin_evidencia():
    veredicto = runner._guardian_z90(_caso_gate_z(con_evidencia=False))
    assert veredicto["bloquea"] is True
    assert any("sin 'evidencia'" in error for error in veredicto["errores"])


def test_guardian_z90_veredicto_no_contiene_nulos():
    for caso in ({"case_id": "X", "cuts": []}, {"case_id": "Y", "freeze": "1799-11-09", "cuts": []}):
        veredicto = runner._guardian_z90(caso)
        assert all(value is not None for value in veredicto.values())


def test_previo_error_presente_en_exito_y_fallo():
    sello = {"_internal_run_status": "COMPLETED_ISOLATED_SUBPROCESS", "H1": {"family": "a"}, "H2": {"family": "b"}}
    visto = {"_internal_run_status": "COMPLETED_ISOLATED_SUBPROCESS", "predictor": {"candidates": []}, "cuts": []}
    out = runner._efectividad_corte_retenido(sello, visto, {"id": "C2"})
    assert out["previo_error"] is False and out["visto_error"] is False
    assert out["previo_status"] == "COMPLETED_ISOLATED_SUBPROCESS"
    assert out["visto_status"] == "COMPLETED_ISOLATED_SUBPROCESS"
    assert out["internal_runs_isolated"] is True

    fallo = runner._efectividad_corte_retenido(
        {"_internal_run_status": "ERROR", "stderr_tail": "Traceback: boom"},
        {"_internal_run_status": "COMPLETED_ISOLATED_SUBPROCESS"},
        {"id": "C2"},
    )
    assert fallo["estado"] == "INTERNAL_T1_RUN_FAILED"
    assert fallo["previo_error"] == "Traceback: boom"
    assert fallo["visto_error"] is False


def test_runner_bloquea_antes_de_ejecutar_motor_y_escribe_recibo(tmp_path):
    caso = _caso_gate_z(corte_fecha="1700-01-01")
    src = tmp_path / "caso_post_z.json"
    src.write_text(json.dumps(caso), encoding="utf-8")
    out = tmp_path / "RESULT_TEST_Z90.json"
    env = dict(os.environ)
    env["STINKBOX_HOME"] = str(tmp_path / "stinkbox_home")
    env["STINKBOX_STORAGE_ROOT"] = str(tmp_path / "stinkbox_storage")
    env.pop("FABRICA_GATE_Z90", None)
    proceso = subprocess.run(
        [sys.executable, str(ROOT / "correr_estandar.py"), str(src), "TEST_Z90", str(out)],
        cwd=str(ROOT), text=True, capture_output=True, timeout=180, env=env,
    )
    assert proceso.returncode == 8, proceso.stdout[-2000:] + proceso.stderr[-2000:]
    resultado = json.loads(out.read_text(encoding="utf-8"))
    assert resultado["estado"] == "BLOQUEADO_GUARDIAN_Z90"
    assert resultado["guardian_z90"]["status"] == "RECHAZADO"
    recibo = json.loads(out.with_name(out.stem + "_RECIBO_EJECUCION.json").read_text(encoding="utf-8"))
    assert recibo["status"] == "BLOQUEADO_GUARDIAN_Z90"
    assert recibo["guardian_z90"]["status"] == "RECHAZADO"
    assert any(stage.get("stage") == "guardian_z90" and stage.get("status") == "RECHAZADO" for stage in recibo["stages"])
