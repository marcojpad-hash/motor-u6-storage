"""Issue #64: guardián Z90 cableado a correr_estandar + previo_error siempre presente.

Verifica por ejecución (no solo por lectura):
- _guardian_z90: NO_CONFIGURADO sin disciplina Z90; PASS con caso gated válido;
  RECHAZADO (bloquea) con un corte post-Z90 y sin evidencia.
- _efectividad_corte_retenido: previo_error y visto_error presentes en éxito ("")
  y en fallo (stderr_tail), nunca ausentes ni None.
- E2E: correr_estandar bloquea un caso post-Z90 con exit 8 ANTES de correr el
  motor, y escribe resultado + recibo con estado BLOQUEADO_GUARDIAN_Z90.
"""
import importlib.util, json, os, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("runner_guardian_z90_test", ROOT / "correr_estandar.py")
runner = importlib.util.module_from_spec(spec); spec.loader.exec_module(runner)


def _caso_gate_z(corte_fecha="1610-03-13", z="1632-03-31", modo="historico", con_evidencia=True):
    """Caso gated mínimo y válido (espejo de CAL_F002_01_GALILEI): 3 cortes antes
    de Z, cada uno con evidencia fechada antes de Z y preparación ciega."""
    fechas = ["1610-03-13", "1615-06-20", "1620-11-02"]
    cuts = []
    for i, f in enumerate(fechas):
        fecha = corte_fecha if i == 0 else f
        ev = [{"afirmacion": "Hecho de prueba con fuente.",
               "source_url": "https://en.wikipedia.org/wiki/Sidereus_Nuncius",
               "source_date": fecha, "claim_date": fecha,
               "tipo_fuente": "primaria", "conocido_en_Z": "sí"}] if con_evidencia else []
        cuts.append({"id": f"C{i + 1}", "date": fecha, "hecho": f"hecho de prueba {i + 1}", "evidencia": ev})
    return {"case_id": "TEST_Z90", "question": "caso de prueba del guardián Z90",
            "gate_z": "GATE_Z_TRABAJO_20261024", "z_trabajo": z, "modo_z": modo,
            "preparacion_ciega": {"preparador_entrada": "A", "custodio_destino": "B", "vio_destino": False},
            "cuts": cuts}


def test_guardian_z90_no_configurado_sin_disciplina():
    # F001 / ciegos: sin gate_z ni z_trabajo+modo_z -> no se bloquea, no se toca nada.
    caso = {"case_id": "X", "cuts": [{"id": "C1", "date": "1799-11-09", "hecho": "x"}]}
    v = runner._guardian_z90(caso)
    assert v["status"] == "NO_CONFIGURADO" and v["bloquea"] is False


def test_guardian_z90_pass_con_caso_valido():
    v = runner._guardian_z90(_caso_gate_z())
    assert v["status"] == "PASS" and v["bloquea"] is False and v["errores"] == []


def test_guardian_z90_rechaza_corte_post_z():
    # Núcleo del Issue #64: un corte posterior a Z se bloquea.
    v = runner._guardian_z90(_caso_gate_z(corte_fecha="1700-01-01"))
    assert v["status"] == "RECHAZADO" and v["bloquea"] is True
    assert any("R2" in e and "posterior a Z" in e for e in v["errores"])


def test_guardian_z90_rechaza_sin_evidencia():
    v = runner._guardian_z90(_caso_gate_z(con_evidencia=False))
    assert v["bloquea"] is True
    assert any("R3" in e for e in v["errores"])


def test_guardian_z90_sin_nulos_en_veredicto():
    # Regresión: el veredicto va al resultado y al recibo; un None se convierte en
    # hueco de dato y el recibo queda INCOMPLETE_OUTPUT_DATA (exit 4). Por eso los
    # campos ausentes llevan marcador explícito, nunca None.
    for caso in ({"case_id": "X", "cuts": []},
                 {"case_id": "Y", "freeze": "1799-11-09", "cuts": []}):
        v = runner._guardian_z90(caso)
        assert not any(x is None for x in v.values()), v
        assert v["z_trabajo"] in ("1799-11-09", "NO_DECLARADO")
        assert v["modo_z"] == "NO_DECLARADO"
        assert v["activado_por"] == "NO_APLICA"


def test_previo_error_presente_en_exito():
    sello = {"_internal_run_status": "COMPLETED_ISOLATED_SUBPROCESS",
             "H1": {"family": "a"}, "H2": {"family": "b"}}
    visto = {"_internal_run_status": "COMPLETED_ISOLATED_SUBPROCESS",
             "predictor": {"candidates": []}, "cuts": []}
    out = runner._efectividad_corte_retenido(sello, visto, {"id": "C2"})
    assert "previo_error" in out and out["previo_error"] is False
    assert "visto_error" in out and out["visto_error"] is False
    assert out["previo_status"] == "COMPLETED_ISOLATED_SUBPROCESS"
    assert out["visto_status"] == "COMPLETED_ISOLATED_SUBPROCESS"
    assert out["internal_runs_isolated"] is True


def test_previo_error_presente_en_fallo():
    sello = {"_internal_run_status": "ERROR", "stderr_tail": "Traceback: boom"}
    visto = {"_internal_run_status": "COMPLETED_ISOLATED_SUBPROCESS"}
    out = runner._efectividad_corte_retenido(sello, visto, {"id": "C2"})
    assert out["estado"] == "INTERNAL_T1_RUN_FAILED"
    assert out["previo_error"] == "Traceback: boom"
    assert out["visto_error"] is False
    assert out["previo_status"] == "ERROR"


def test_bloqueo_z90_e2e(tmp_path, monkeypatch):
    # Verificación real: correr_estandar bloquea ANTES del motor (rápido, sin Engine).
    caso = _caso_gate_z(corte_fecha="1700-01-01")
    src = tmp_path / "caso_post_z.json"
    src.write_text(json.dumps(caso), encoding="utf-8")
    out = tmp_path / "RESULT_TEST_Z90.json"
    env = dict(os.environ)
    env["STINKBOX_HOME"] = str(tmp_path / "stinkbox_home")
    env["STINKBOX_STORAGE_ROOT"] = str(tmp_path / "stinkbox_storage")
    env.pop("FABRICA_GATE_Z90", None)
    pr = subprocess.run([sys.executable, str(ROOT / "correr_estandar.py"), str(src), "TEST_Z90", str(out)],
                        cwd=str(ROOT), text=True, capture_output=True, timeout=180, env=env)
    assert pr.returncode == 8, pr.stdout[-2000:] + pr.stderr[-2000:]
    res = json.loads(out.read_text(encoding="utf-8"))
    assert res["estado"] == "BLOQUEADO_GUARDIAN_Z90"
    assert res["guardian_z90"]["status"] == "RECHAZADO"
    rec = json.loads(out.with_name(out.stem + "_RECIBO_EJECUCION.json").read_text(encoding="utf-8"))
    assert rec["status"] == "BLOQUEADO_GUARDIAN_Z90"
    assert rec["guardian_z90"]["status"] == "RECHAZADO"
    assert any(s.get("stage") == "guardian_z90" and s.get("status") == "RECHAZADO" for s in rec["stages"])
