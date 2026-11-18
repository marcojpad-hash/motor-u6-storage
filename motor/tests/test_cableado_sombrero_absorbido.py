#!/usr/bin/env python3
"""test_cableado_sombrero_absorbido.py — Veredicto honesto de `_protocol_quality`
(sombrero blanco absorbido) en `MOTOR_V15_3_UNICO_20260927.py`.

Hallazgo (ADORNO 2 de la auditoría de ejecución real): el veredicto de
`_protocol_quality` estaba hardcodeado — siempre reportaba
`status: PASS`, `sombrero_blanco: ENFORCED` y `facts_only_boundary: True`
aunque la pregunta trajera ruido de protocolo o los cortes trajeran campos
probabilísticos. El filtro sombrero SÍ corre y la GuardiaNoCruce SÍ hace
cumplir (levanta excepción si un lente lateral muta los tableros); solo el
veredicto era decorativo. Este PR no reescribe el filtro: hace honesto el
veredicto, derivando `status`, `sombrero_blanco` y `facts_only_boundary`
de las comprobaciones reales y listando cada violación en `violaciones`.

Qué es honesto ahora:
  - `status` es PASS solo si no hay violaciones; si hay alguna, FAIL.
  - `sombrero_blanco` es ENFORCED solo si no hay violaciones; si hay
    alguna, VIOLATED.
  - `facts_only_boundary` es True solo si no hay ruido de protocolo en la
    pregunta ni campos probabilísticos en la entrada (antes: True literal).
  - `violaciones` lista el motivo: SIN_PREGUNTA, RUIDO_PROTOCOLO_EN_PREGUNTA,
    CAMPOS_PROBABILISTICOS_EN_ENTRADA, SIN_CORTES.
  - La entrada `guardia_no_cruce` de `_run_transversal_guards` sigue en
    PASS tras una salida limpia del guardián (el guardián levanta excepción
    si hay mutación, así que llegar al return ya es la prueba), pero ahora
    trae evidencia: `features_validadas` (cuántos laterales validó) y
    `mutaciones_detectadas: 0`.

Decisión de bypass (documentada): este módulo NO tiene bypass por env.
El contrato del veredicto ES la honestidad: un flag que lo apagara dejaría
a la corrida sin veredicto y permitiría afirmar una frontera limpia sin
haberla comprobado — exactamente la mentira que este PR corrige. La
GuardiaNoCruce es además un invariante de seguridad (impide contaminación
bayesiana de los tableros) y no debe ser apagable. El filtro sombrero
blanco v2 (PR #30, puerta de entrada) tiene su propio bypass
(`SOMBRERO_BLANCO`) para su propio filtro; este veredicto absorbido no.

El veredicto es un REPORTE, no una puerta: un FAIL no bloquea la corrida
ni reescribe H (la aplicación es la GuardiaNoCruce, que levanta excepción
al mutar, y el filtro v2 en la puerta). El FAIL queda visible en el recibo
(`protocol_controls.question_white_hat`) para que ningún lector posterior
lo confunda con un PASS.

Capas de este archivo (en orden):
  1) Neutral, fuera de U6: `_protocol_quality` directo con un caso sano →
     PASS/ENFORCED, violaciones [], facts_only_boundary True, sin mutar el
     input.
  2) Vivo por unidad: `_protocol_quality` directo con ruido de protocolo en
     la pregunta (cada variante del regex), con campo probabilístico en un
     corte, sin pregunta, sin cortes y con violaciones combinadas → FAIL/
     VIOLATED con la violación listada. Si el veredicto volviera a mentir
     (PASS con violación presente), estas capas fallan.
  3) Estático: el cableado existe (`_run_transversal_guards` llama a
     `_protocol_quality`, `run()` guarda el resultado como
     `protocol_controls`) y no quedan literales decorativos en la función.
  4) Vivo (subproceso correr_estandar.py, THEMISTOCLES): en una corrida
     real el veredicto es PASS/ENFORCED con violaciones [], la guardia
     reporta features_validadas > 0, H intacta, cierre AJUSTADA, y la fila
     de componentes `protocolo_transversal_absorbido` es EXECUTED.
  5) Vivo con violación (subproceso, THEMISTOCLES con ruido en la
     pregunta): el recibo trae FAIL/VIOLATED con RUIDO_PROTOCOLO_EN_PREGUNTA
     listado; H y cierre intactos (el veredicto reporta, no reescribe).
  6) Constantes y sha: sha del UNICO modificado, del engine canónico y del
     catálogo 244.
"""
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # motor/
MOTOR_DIR = ROOT / "motor"
UNICO = MOTOR_DIR / "MOTOR_V15_3_UNICO_20260927.py"
THEMISTOCLES = ROOT / "inputs" / "THEMISTOCLES_FREEZE_480BC_CATALOG_REPAIR_R2.json"

SHA_UNICO = "473f56cc"
SHA_ENGINE = "665c39a2"
SHA_PATTERNS = "d827dcc3"

RUIDOS = [
    "juicio estético",
    "fecha de protocolo",
    "sombrero blanco",
    "recorte de protocolo",
    "metadato de protocolo",
]

CAMPOS_PROHIBIDOS = ["probability", "probabilidad", "weight", "peso",
                     "confidence", "confianza", "prob"]


def _load_runner():
    spec = importlib.util.spec_from_file_location(
        "runner_u6_sombrero_absorbido", UNICO)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _caso_sano():
    return {
        "case_id": "CASO_SANO",
        "question": "Caso ciego de liderazgo estratégico ante amenaza externa.",
        "cuts": [{"id": "C1",
                  "P": [["amenaza_central", 0.80], ["defensa_debil", 0.72]],
                  "A": [["liderazgo", 0.78]],
                  "C": [["poder", 0.80]]}],
    }


# ------------------------------------------------------------------ 1) neutral, fuera de U6
def test_veredicto_sano_es_pass_enforced():
    r = _load_runner()
    q = r._protocol_quality(_caso_sano())
    assert q.get("status") == "PASS", q
    assert q.get("sombrero_blanco") == "ENFORCED", q
    assert q.get("question_present") is True, q
    assert q.get("protocol_noise_in_question") is False, q
    assert q.get("facts_only_boundary") is True, q
    assert q.get("no_probabilistic_fields_in_input") is True, q
    assert q.get("violaciones") == [], q
    assert q.get("observed_cut_shape") == [
        {"id": "C1", "P": 2, "A": 1, "C": 1}], q


def test_veredicto_no_muta_input():
    r = _load_runner()
    case = _caso_sano()
    antes = json.dumps(case, sort_keys=True)
    r._protocol_quality(case)
    assert json.dumps(case, sort_keys=True) == antes


# ------------------------------------------------------------------ 2) vivo por unidad: el veredicto no miente
def test_ruido_en_pregunta_es_fail_violated():
    r = _load_runner()
    for ruido in RUIDOS:
        case = _caso_sano()
        case["question"] = f"Caso ciego con {ruido} en la pregunta."
        q = r._protocol_quality(case)
        assert q.get("status") == "FAIL", (ruido, q)
        assert q.get("sombrero_blanco") == "VIOLATED", (ruido, q)
        assert q.get("protocol_noise_in_question") is True, (ruido, q)
        assert q.get("facts_only_boundary") is False, (ruido, q)
        assert "RUIDO_PROTOCOLO_EN_PREGUNTA" in (q.get("violaciones") or []), (ruido, q)


def test_campo_probabilistico_en_corte_es_fail():
    r = _load_runner()
    for campo in CAMPOS_PROHIBIDOS:
        case = _caso_sano()
        case["cuts"][0][campo] = 0.5
        q = r._protocol_quality(case)
        assert q.get("status") == "FAIL", (campo, q)
        assert q.get("sombrero_blanco") == "VIOLATED", (campo, q)
        assert q.get("no_probabilistic_fields_in_input") is False, (campo, q)
        assert q.get("facts_only_boundary") is False, (campo, q)
        assert "CAMPOS_PROBABILISTICOS_EN_ENTRADA" in (q.get("violaciones") or []), (campo, q)


def test_sin_pregunta_es_fail():
    r = _load_runner()
    case = _caso_sano()
    case.pop("question")
    case.pop("case_id")
    q = r._protocol_quality(case)
    assert q.get("status") == "FAIL", q
    assert q.get("sombrero_blanco") == "VIOLATED", q
    assert q.get("question_present") is False, q
    assert "SIN_PREGUNTA" in (q.get("violaciones") or []), q


def test_sin_cortes_es_fail():
    r = _load_runner()
    case = _caso_sano()
    case["cuts"] = []
    q = r._protocol_quality(case)
    assert q.get("status") == "FAIL", q
    assert q.get("sombrero_blanco") == "VIOLATED", q
    assert q.get("observed_cut_shape") == [], q
    assert "SIN_CORTES" in (q.get("violaciones") or []), q


def test_violaciones_combinadas_se_listan_todas():
    r = _load_runner()
    case = _caso_sano()
    case["question"] = "Caso con sombrero blanco y fecha de protocolo."
    case["cuts"][0]["peso"] = 0.9
    q = r._protocol_quality(case)
    assert q.get("status") == "FAIL", q
    assert q.get("sombrero_blanco") == "VIOLATED", q
    assert "RUIDO_PROTOCOLO_EN_PREGUNTA" in (q.get("violaciones") or []), q
    assert "CAMPOS_PROBABILISTICOS_EN_ENTRADA" in (q.get("violaciones") or []), q


def test_case_id_suple_pregunta_ausente():
    r = _load_runner()
    case = _caso_sano()
    case.pop("question")
    q = r._protocol_quality(case)
    assert q.get("status") == "PASS", q
    assert q.get("question_present") is True, q
    assert "SIN_PREGUNTA" not in (q.get("violaciones") or []), q


# ------------------------------------------------------------------ 3) estático: cableado y sin literales decorativos
def test_cableado_y_sin_veredicto_decorativo():
    src = UNICO.read_text(encoding="utf-8")
    assert "q=_protocol_quality(case)" in src
    assert '"protocol_controls":transversal' in src
    assert '"guardia_no_cruce":{"status":"PASS","scope":"features_before_predictor","features_validadas":len(features),"mutaciones_detectadas":0}' in src
    # El veredicto ya no se afirma por literal dentro de _protocol_quality.
    fn_src = src.split("def _protocol_quality(case):")[1].split("def _run_transversal_guards")[0]
    assert '"status":"PASS"' not in fn_src, fn_src
    assert '"sombrero_blanco":"ENFORCED"' not in fn_src, fn_src
    assert '"facts_only_boundary":True' not in fn_src, fn_src
    assert '"status": "PASS" if not violaciones else "FAIL"' in fn_src
    assert '"sombrero_blanco": "ENFORCED" if not violaciones else "VIOLATED"' in fn_src
    assert '"violaciones": violaciones' in fn_src


# ------------------------------------------------------------------ 4 y 5) vivo por subproceso
def _python_con_numpy():
    for cand in (sys.executable, "/usr/bin/python3"):
        try:
            subprocess.run([cand, "-c", "import numpy"], capture_output=True,
                           timeout=60, check=True)
            return cand
        except Exception:
            continue
    return sys.executable


PYTHON_MOTOR = _python_con_numpy()


def _corre_estandar(entrada, nombre, salida):
    env = dict(os.environ)
    r = subprocess.run(
        [PYTHON_MOTOR, "correr_estandar.py", str(entrada), nombre, str(salida)],
        cwd=str(ROOT), env=env, capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-2000:]
    return json.loads(Path(salida).read_text(encoding="utf-8"))


def _componente(resultado, nombre):
    comps = (resultado.get("execution") or {}).get("component_status") or []
    return next((s for s in comps if s.get("component") == nombre), None)


def test_corrida_real_veredicto_honesto_pass(tmp_path):
    out = tmp_path / "resultado_sombrero_absorbido.json"
    res = _corre_estandar(THEMISTOCLES, "SOMBRERO_ABSORBIDO_SMOKE", out)
    pc = res.get("protocol_controls") or {}
    q = pc.get("question_white_hat") or {}
    assert q.get("status") == "PASS", q
    assert q.get("sombrero_blanco") == "ENFORCED", q
    assert q.get("violaciones") == [], q
    assert q.get("facts_only_boundary") is True, q
    guardia = pc.get("guardia_no_cruce") or {}
    assert guardia.get("status") == "PASS", guardia
    assert guardia.get("features_validadas", 0) > 0, guardia
    assert guardia.get("mutaciones_detectadas") == 0, guardia
    comp = _componente(res, "protocolo_transversal_absorbido")
    assert comp is not None and comp.get("status") == "EXECUTED", comp
    assert (res.get("H1") or {}).get("family") == "arquetipo_el_gobernante"
    assert (res.get("H2") or {}).get("family") == "13_enemistad_de_parientes"
    assert (res.get("cierre_final") or {}).get("grado") == "AJUSTADA"


def test_corrida_real_con_ruido_reporta_fail_sin_reescribir_h(tmp_path):
    entrada = tmp_path / "THEMISTOCLES_RUIDO.json"
    caso = json.loads(THEMISTOCLES.read_text(encoding="utf-8"))
    caso["question"] = str(caso.get("question")) + " sombrero blanco."
    entrada.write_text(json.dumps(caso, ensure_ascii=False), encoding="utf-8")
    out = tmp_path / "resultado_sombrero_absorbido_ruido.json"
    res = _corre_estandar(entrada, "SOMBRERO_ABSORBIDO_RUIDO", out)
    pc = res.get("protocol_controls") or {}
    q = pc.get("question_white_hat") or {}
    assert q.get("status") == "FAIL", q
    assert q.get("sombrero_blanco") == "VIOLATED", q
    assert q.get("protocol_noise_in_question") is True, q
    assert q.get("facts_only_boundary") is False, q
    assert "RUIDO_PROTOCOLO_EN_PREGUNTA" in (q.get("violaciones") or []), q
    # El veredicto reporta, no reescribe: H y cierre intactos.
    assert (res.get("H1") or {}).get("family") == "arquetipo_el_gobernante"
    assert (res.get("H2") or {}).get("family") == "13_enemistad_de_parientes"
    assert (res.get("cierre_final") or {}).get("grado") == "AJUSTADA"


# ------------------------------------------------------------------ 6) constantes y sha
def test_shas_engine_catalogo_y_unico():
    import hashlib

    def _sha8(path):
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()[:8]

    assert _sha8(UNICO) == SHA_UNICO, "UNICO cambió; actualiza SHA_UNICO si el cambio es intencional"
    assert _sha8(MOTOR_DIR / "Engine_V5_CANONICO_SOLO.py") == SHA_ENGINE
    assert _sha8(MOTOR_DIR / "patterns_final_v14.json") == SHA_PATTERNS
