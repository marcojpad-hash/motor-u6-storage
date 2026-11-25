import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # motor/
MOTOR_DIR = ROOT / "motor"


def _load_f017():
    spec = importlib.util.spec_from_file_location(
        "filtro_entrada_dirigida_017", ROOT / "capa_llm" / "filtro_entrada_dirigida_017.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _catalogo():
    return json.loads((MOTOR_DIR / "patterns_final_v14.json").read_text(encoding="utf-8"))


def _caso_017():
    return {"case_id": "TEST_017", "person": "Gustave Courbet", "question": "test",
            "cuts": [{"id": "C1", "date": "1871-05-01",
                      "hecho": "Gustave Courbet pinto un cuadro en 1866",
                      "P": [], "A": [], "C": []}]}


def test_compuerta_traza_no_modifica_y_status_no_miente():
    f017 = _load_f017()
    case = _caso_017()
    payload, tr = f017.compuerta(case, "traza", _catalogo())
    assert payload == case  # traza no modifica nada
    assert tr["modo"] == "traza"
    assert tr["status"] != "EXECUTED"  # A5: en traza nada se ejecutó
    assert tr["status"] == "TRAZA_SIN_MODIFICACION"
    assert "Courbet" not in json.dumps(tr, ensure_ascii=False)
    assert "1866" not in json.dumps(tr, ensure_ascii=False)  # solo huellas


def test_compuerta_activo_neutraliza_texto_y_sidecar_guarda_mapa():
    f017 = _load_f017()
    case = _caso_017()
    payload, tr = f017.compuerta(case, "activo", _catalogo())
    assert tr["status"] == "EXECUTED"
    hecho = payload["cuts"][0]["hecho"]
    assert "Courbet" not in hecho and "1866" not in hecho
    assert "PROTAGONISTA" in hecho and "(fecha)" in hecho
    # El campo de control `person` conserva el nombre a propósito: el motor lo
    # usa para el filtro de self-match (anti-fuga), no alimenta al predictor.
    assert payload["person"] == "Gustave Courbet"
    # El mapa nombre->rol queda en el sidecar sellado, nunca en la traza.
    out, inf = f017.aplicar(case, set(f017.TIPOS_ACTIVOS_EN_VIVO), _catalogo())
    assert out["cuts"][0]["hecho"] == hecho
    assert inf["sidecar_sellado"]["mapa_nombres"]
    assert "Courbet" not in json.dumps(tr, ensure_ascii=False)


def test_runner_resuelve_z_corte_sin_confudir_fechas():
    spec = importlib.util.spec_from_file_location(
        "runner_u6", MOTOR_DIR / "MOTOR_V15_3_UNICO_20260927.py")
    runner = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = runner
    spec.loader.exec_module(runner)
    assert runner._resolver_z_corte({"freeze": "1871-05-01", "z_work_date": "C3_1895B"}) == "1871-05-01"
    assert runner._resolver_z_corte({"z_trabajo": "1871-05-01"}) == "1871-05-01"
    assert runner._resolver_z_corte({"z90_date": "1871-05-01"}) == "1871-05-01"
    assert runner._resolver_z_corte({"z_work_date": "C3_1895B"}) is None  # id de corte, no fecha
    assert runner._resolver_z_corte({}) is None  # LIVE_PRESENT: sin corte
    assert runner._resolver_z_corte({"freeze": "1855"}) == "1855-01-01"  # fecha parcial


def test_runner_aplica_filtro_017_al_entrar():
    spec = importlib.util.spec_from_file_location(
        "runner_u6", MOTOR_DIR / "MOTOR_V15_3_UNICO_20260927.py")
    runner = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = runner
    spec.loader.exec_module(runner)
    os.environ.pop("FILTRO_017", None)  # defecto: traza
    case = _caso_017()
    out, tr = runner._aplicar_filtro_017(case)
    assert tr["modo"] == "traza" and tr["status"] == "TRAZA_SIN_MODIFICACION"
    assert out == case
    os.environ["FILTRO_017"] = "activo"
    try:
        out2, tr2 = runner._aplicar_filtro_017(case)
        assert tr2["status"] == "EXECUTED" and tr2["payload_aplicado"] is True
        assert "Courbet" not in out2["cuts"][0]["hecho"]
    finally:
        os.environ.pop("FILTRO_017", None)


def test_cableado_presente_en_runner_y_correr_estandar():
    # Verificación estática de que el cableado existe en los dos archivos que
    # importan el runner. La integración de corrida completa la verifica CI
    # (test-motor-contracts + fabrica-real-traza con un caso sellado real).
    runner_src = (MOTOR_DIR / "MOTOR_V15_3_UNICO_20260927.py").read_text(encoding="utf-8")
    assert "_aplicar_filtro_017(case)" in runner_src
    assert 'result["filtro_entrada_dirigida_017"]=_f017_traza' in runner_src
    assert "cutoff_date=_z_corte" in runner_src
    assert "_resolver_z_corte" in runner_src
    est_src = (ROOT / "correr_estandar.py").read_text(encoding="utf-8")
    assert 'os.environ.get("FILTRO_017", "traza")' in est_src
    assert '"stage": "filtro_entrada_dirigida_017"' in est_src
    assert '"stage": "consulta_dirigida"' in est_src
    assert 'result["consulta_dirigida"] = _cd_traza' in est_src


# ------------------------------------------------- V7 (A-F1): verificación de salida cableada
def _cierre_017():
    return {"H1": "arquetipo_el_gobernante", "H2": "13_enemistad_de_parientes",
            "margen": None, "grado": "AJUSTADA", "n_objeciones": 2,
            "objeciones": [{"guardian": "LOGICA_COPI", "tipo": "NO_RESUELTO_TOP1_NO_ES_TOP_DE_NINGUN_CORTE"},
                           {"criterio": "C1_top1_encabeza_un_corte"}],
            "apuesta": {"familia_apostada": "arquetipo_el_gobernante",
                        "frente_a": "13_enemistad_de_parientes"}}


def test_verificar_salida_llm_detecta_h1_h2_invertidas():
    f017 = _load_f017()
    cf = _cierre_017()
    texto = ("H2: 13_enemistad_de_parientes. H1: arquetipo_el_gobernante. "
             "Grado: AJUSTADA. Hay 2 objeciones.")
    v = f017.verificar_salida_llm(texto, cf, catalogo=_catalogo())
    assert "ORDEN_H1_H2_INVERTIDO" in v["violaciones"]
    assert v["huella_salida_017"] == f017.huella_salida(cf)


def test_verificar_salida_llm_texto_limpio_pasa():
    f017 = _load_f017()
    cf = _cierre_017()
    hs = f017.huella_salida(cf)
    texto = ("H1: arquetipo_el_gobernante. H2: 13_enemistad_de_parientes. "
             "Grado: AJUSTADA. Hay 2 objeciones. Huella: " + hs)
    v = f017.verificar_salida_llm(texto, cf, catalogo=_catalogo())
    assert v["ok"] is True, v
    assert v["huella_citada"] is True


def _python_con_numpy_017():
    for cand in (sys.executable, "/usr/bin/python3"):
        try:
            subprocess.run([cand, "-c", "import numpy"], capture_output=True,
                           timeout=60, check=True)
            return cand
        except Exception:
            continue
    return sys.executable


def test_runner_verifica_salida_llm(tmp_path):
    # Vivo (subproceso correr_estandar.py, THEMISTOCLES): la verificación de
    # salida existe en el RESULT con su huella (A-F1: antes nadie la llamaba).
    entrada = ROOT / "inputs" / "THEMISTOCLES_FREEZE_480BC_CATALOG_REPAIR_R2.json"
    salida = tmp_path / "resultado_017.json"
    env = dict(os.environ)
    env.pop("FILTRO_017", None)
    r = subprocess.run([_python_con_numpy_017(), "correr_estandar.py", str(entrada),
                        "V7_017_SMOKE", str(salida)],
                       cwd=str(ROOT), env=env, capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-2000:]
    res = json.loads(salida.read_text(encoding="utf-8"))
    v = res.get("verificacion_salida_llm")
    assert v is not None, "sin verificacion_salida_llm en una corrida real"
    assert v.get("status") == "EJECUTADA"
    assert v.get("huella_salida_017")
    assert "respuesta_humana" in v.get("por_salida", {})
    assert "traduccion_salida" in v.get("por_salida", {})
