#!/usr/bin/env python3
"""test_cableado_autoevidencia.py — Guardián de entrada de autoevidencia
cableado en la ruta real de corrida (hub de laterales, pre_predictor).

Specs: docstring de `guardian_entrada_autoevidencia_v1.py` (PATCH 008,
2026-10-06: marca tokens de ENTRADA P/A/C que son nombres de familia/patrón
del catálogo — p.ej. `30_ambicion`, `arquetipo_el_gobernante` — porque un
token así hace que el motor "encuentre" la familia por su propio nombre:
auto-evidencia, circularidad entrada→salida; contrato SOLO BANDERA,
can_decide_H=False, no modifica el input, no quita tokens, no reordena
candidatos, no escribe H1/H2, no toca Engine_V5 ni patterns, solo lectura)
+ `autoevidencia_stores_011.py` (PATCH 011: memoria sin eventos del mismo
case_id / mismo input sha; la autoevidencia no cuenta) + el registro del hub
(`laterales_unico_v1.pre_predictor`, pieza `guardian_entrada_autoevidencia`).

Hallazgo del cableado: el guardián YA se ejecutaba en la ruta real sin
ninguna prueba (baseline THEMISTOCLES: `EXECUTED`, bandera=False,
n_autoevidencia=0, H intacta, cierre AJUSTADA), y el apagado YA existía
(`LAT_GUARDIAN_ENTRADA_AUTOEVIDENCIA=0` → `APAGADA_POR_FLAG` visible en la
fila `hub:guardian_entrada_autoevidencia`, sin borrar el bloque en
silencio). Este PR no reescribe el núcleo: solo añade la prueba que
demuestra la ejecución, la marca y el apagado visible. Si el guardián
dejara de correr, la capa 3 fallaría (el detalle
`laterales_unico_detalle/guardian_entrada_autoevidencia` no existiría y la
fila del hub no sería HUB_ACTIVA_MUDA); si el apagado dejara de marcarse,
la capa 5 fallaría.

Contrato del guardián: corre ANTES del predictor, en el hub de laterales
(`pre_predictor`), solo MARCA (`FEEDS_H=False`, `FEEDS_PREDICTOR=False`,
solo bandera); nunca escribe H ni patterns ni la apuesta. Su salida es
`status=EXECUTED` o `EXECUTED_WITH_FINDINGS` con `bandera` (True solo si
hay al menos un token que ES nombre de familia del catálogo),
`n_autoevidencia`, `familias_autoevidenciadas` y `banderas` (cada una con
corte, eje, token, peso, tipo y riesgo). Un token con forma de nombre de
familia pero FUERA del catálogo se marca como débil
(`FORMA_DE_NOMBRE_DE_FAMILIA_FUERA_DE_CATALOGO`) sin levantar `bandera`.
El bypass (`LAT_GUARDIAN_ENTRADA_AUTOEVIDENCIA=0`) no debe inventar
bandera ni cambiar el cierre: el grado del cierre final es el mismo con
el guardián activo o apagado.

Capas de este archivo (en orden):
  1) Neutral, fuera de U6: evaluar() directo con cortes sanos (tokens que
     no son nombres de familia) → bandera False, n_autoevidencia 0,
     status EXECUTED, can_decide_H False, no modifica el input.
  2) Vivo por unidad: evaluar() directo con tokens que SÍ son nombres de
     familia del catálogo (`30_ambicion`, `arquetipo_el_gobernante`) →
     bandera True, n_autoevidencia 2, familias listadas, tipo
     AUTOEVIDENCIA_NOMBRE_DE_FAMILIA; forma fuera de catálogo →
     bandera débil sin levantar `bandera`; tokens en forma dict y string
     también se detectan.
  3) Estático: el cableado existe en el hub (pieza registrada con su
     archivo y su flag LAT_) y UNICO expone la fila del hub.
  4) Vivo (subproceso correr_estandar.py, THEMISTOCLES): en una corrida
     real el guardián ejecuta (EXECUTED, bandera False), la fila del hub
     es HUB_ACTIVA_MUDA, H intacta, cierre AJUSTADA, y la fila
     autoevidencia_stores_011.py es EXECUTED.
  5) Vivo con marca (subproceso, caso modificado): con un token
     `30_ambicion` en la entrada, el recibo trae bandera True,
     n_autoevidencia 1, familias ['30_ambicion'] y la fila del hub es
     HUB_ACTIVA; H y cierre intactos.
  6) Bypass (subproceso con LAT_GUARDIAN_ENTRADA_AUTOEVIDENCIA=0): el
     apagado queda marcado APAGADA_POR_FLAG en la fila del hub, el detalle
     del guardián no aparece, no pasa en silencio, el resto de guardianes
     sigue corriendo y el cierre final no cambia de grado.
  7) Constantes y sha: VERSION del guardián y sha del archivo, del engine
     canónico y del catálogo 244.

Límite documentado (del módulo, no del test): el guardián solo marca;
no quita los tokens autoevidenciados ni reordena candidatos, así que una
entrada con un nombre de familia sigue inflando el soporte de esa familia
en el predictor — la corrección queda como sugerencia para el LLM de
entrada (`nota` del recibo), no como acción del motor.
"""
import copy
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # motor/
MOTOR_DIR = ROOT / "motor"
GUARDIAN = MOTOR_DIR / "guardian_entrada_autoevidencia_v1.py"
LATERALES = MOTOR_DIR / "laterales_unico_v1.py"
UNICO = MOTOR_DIR / "MOTOR_V15_3_UNICO_20260927.py"
THEMISTOCLES = ROOT / "inputs" / "THEMISTOCLES_FREEZE_480BC_CATALOG_REPAIR_R2.json"

SHA_GUARDIAN = "42dd6c1c"
SHA_ENGINE = "665c39a2"
SHA_PATTERNS = "d827dcc3"
VERSION_GUARDIAN = "GUARDIAN_ENTRADA_AUTOEVIDENCIA_V1_20261006"


def _load_guardian():
    spec = importlib.util.spec_from_file_location(
        "guardian_entrada_autoevidencia_v1", GUARDIAN)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _catalogo():
    return json.loads((MOTOR_DIR / "patterns_final_v14.json").read_text(encoding="utf-8"))


def _sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _cortes_neutros():
    return [{"id": "C1", "P": [["amenaza_central", 0.80], ["defensa_debil", 0.72]],
             "A": [["liderazgo", 0.78]], "C": [["poder", 0.80]]}]


def _cortes_marcados():
    return [{"id": "C1", "P": [["30_ambicion", 0.70], ["amenaza_central", 0.80]],
             "A": [["arquetipo_el_gobernante", 0.65]], "C": [["poder", 0.80]]}]


# ------------------------------------------------------------------ 1) neutral, fuera de U6
def test_evaluar_neutro_no_marca():
    g = _load_guardian()
    r = g.evaluar(_cortes_neutros(), _catalogo())
    assert r.get("status") == "EXECUTED", r
    assert r.get("bandera") is False, r
    assert r.get("n_banderas") == 0, r
    assert r.get("n_autoevidencia") == 0, r
    assert r.get("familias_autoevidenciadas") == [], r
    assert r.get("banderas") == [], r
    assert r.get("accion") == "SOLO_BANDERA", r
    assert r.get("can_decide_H") is False, r
    assert r.get("escribe_H") is False, r
    assert r.get("modifica_input") is False, r
    assert r.get("reordena_candidatos") is False, r


def test_evaluar_no_muta_input():
    g = _load_guardian()
    cuts = _cortes_marcados()
    antes = copy.deepcopy(cuts)
    g.evaluar(cuts, _catalogo())
    assert cuts == antes


def test_evaluar_sin_catalogo_no_marca_fuerte():
    g = _load_guardian()
    r = g.evaluar(_cortes_marcados(), None)
    assert r.get("bandera") is False, r
    assert r.get("n_autoevidencia") == 0, r
    # La forma sí se marca como débil aunque no haya catálogo.
    assert r.get("n_banderas") == 2, r
    assert {b.get("tipo") for b in r.get("banderas") or []} == {
        "FORMA_DE_NOMBRE_DE_FAMILIA_FUERA_DE_CATALOGO"}, r


# ------------------------------------------------------------------ 2) vivo por unidad
def test_evaluar_marca_nombre_de_familia():
    g = _load_guardian()
    r = g.evaluar(_cortes_marcados(), _catalogo())
    assert r.get("status") == "EXECUTED_WITH_FINDINGS", r
    assert r.get("bandera") is True, r
    assert r.get("n_autoevidencia") == 2, r
    assert r.get("familias_autoevidenciadas") == [
        "30_ambicion", "arquetipo_el_gobernante"], r
    assert r.get("n_banderas") == 2, r
    for b in r.get("banderas") or []:
        assert b.get("tipo") == "AUTOEVIDENCIA_NOMBRE_DE_FAMILIA", b
        assert b.get("familia") in ("30_ambicion", "arquetipo_el_gobernante"), b
        assert b.get("riesgo"), b
    por_token = {b.get("token"): b for b in r.get("banderas") or []}
    assert por_token["30_ambicion"].get("corte") == "C1", por_token
    assert por_token["30_ambicion"].get("eje") == "P", por_token
    assert por_token["30_ambicion"].get("peso") == 0.70, por_token
    assert por_token["arquetipo_el_gobernante"].get("eje") == "A", por_token


def test_evaluar_forma_fuera_de_catalogo_es_debil():
    g = _load_guardian()
    cuts = [{"id": "C1", "P": [["99_nombre_inventado", 0.70]], "A": [], "C": []}]
    r = g.evaluar(cuts, _catalogo())
    assert r.get("bandera") is False, r
    assert r.get("n_autoevidencia") == 0, r
    assert r.get("n_banderas") == 1, r
    b = (r.get("banderas") or [])[0]
    assert b.get("tipo") == "FORMA_DE_NOMBRE_DE_FAMILIA_FUERA_DE_CATALOGO", b
    assert b.get("familia") is None, b


def test_evaluar_detecta_token_en_dict_y_string():
    g = _load_guardian()
    cuts = [{"id": "C1",
             "P": [{"token": "30_ambicion"}, "arquetipo_el_gobernante"],
             "A": [], "C": []}]
    r = g.evaluar(cuts, _catalogo())
    assert r.get("bandera") is True, r
    assert r.get("n_autoevidencia") == 2, r


# ------------------------------------------------------------------ 3) estático: el cableado existe
def test_estatico_cableado_en_hub_y_unico():
    hub = LATERALES.read_text(encoding="utf-8")
    assert '_pieza("guardian_entrada_autoevidencia"' in hub, hub
    assert "guardian_entrada_autoevidencia_v1.py" in hub, hub
    assert "g.evaluar(case.get(\"cuts\")" in hub, hub
    assert "APAGADA_POR_FLAG" in hub, hub
    assert 'LAT_' in hub and "flag_on" in hub, hub
    unico = UNICO.read_text(encoding="utf-8")
    assert '"guardian_entrada_autoevidencia"' in unico, unico
    assert "hub:" in unico, unico
    assert "HUB_ACTIVA" in unico, unico


# ------------------------------------------------------------------ 4, 5 y 6) vivo y bypass por subproceso
def _python_con_numpy():
    """El motor exige numpy; el intérprete de pytest (venv) no lo tiene.
    Se usa el python3 del sistema cuando el actual no lo trae."""
    for cand in (sys.executable, "/usr/bin/python3"):
        try:
            subprocess.run([cand, "-c", "import numpy"], capture_output=True,
                           timeout=60, check=True)
            return cand
        except Exception:
            continue
    return sys.executable


PYTHON_MOTOR = _python_con_numpy()


def _corre_estandar(entrada, nombre, salida, env_extra=None):
    env = dict(os.environ)
    env.pop("LAT_GUARDIAN_ENTRADA_AUTOEVIDENCIA", None)
    if env_extra:
        env.update(env_extra)
    r = subprocess.run(
        [PYTHON_MOTOR, "correr_estandar.py", str(entrada), nombre, str(salida)],
        cwd=str(ROOT), env=env, capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-2000:]
    return json.loads(Path(salida).read_text(encoding="utf-8"))


def _componente(resultado, nombre):
    comps = (resultado.get("execution") or {}).get("component_status") or []
    return next((s for s in comps if s.get("component") == nombre), None)


def _detalle_guardian(resultado):
    return ((resultado.get("features") or {}).get("laterales_unico_detalle") or {}).get(
        "guardian_entrada_autoevidencia")


def _h_intacta(resultado):
    assert (resultado.get("H1") or {}).get("family") == "arquetipo_el_gobernante", resultado
    assert (resultado.get("H2") or {}).get("family") == "13_enemistad_de_parientes", resultado
    assert (resultado.get("cierre_final") or {}).get("grado") == "AJUSTADA", resultado


def test_corrida_real_ejecuta_guardian_entrada(tmp_path):
    out = tmp_path / "resultado_autoevidencia.json"
    res = _corre_estandar(THEMISTOCLES, "AUTOEVIDENCIA_SMOKE", out)
    det = _detalle_guardian(res)
    assert det is not None, "el guardián no corrió en la ruta real"
    assert det.get("status") == "EXECUTED", det
    assert det.get("version") == VERSION_GUARDIAN, det
    assert det.get("bandera") is False, det
    assert det.get("n_autoevidencia") == 0, det
    assert det.get("familias_autoevidenciadas") == [], det
    assert det.get("can_decide_H") is False, det
    # La fila del hub lo registra como ejecutado, sin bandera en THEMISTOCLES.
    comp = _componente(res, "hub:guardian_entrada_autoevidencia")
    assert comp is not None and comp.get("status") == "HUB_ACTIVA_MUDA", comp
    assert comp.get("can_decide_H") is False, comp
    assert "bandera=False" in (comp.get("reason") or ""), comp
    # La otra pata de autoevidencia (stores 011) también corre.
    comp011 = _componente(res, "autoevidencia_stores_011.py")
    assert comp011 is not None and comp011.get("status") == "EXECUTED", comp011
    _h_intacta(res)


def test_corrida_real_marca_token_nombre_de_familia(tmp_path):
    case = json.loads(THEMISTOCLES.read_text(encoding="utf-8"))
    case["cuts"][0]["P"] = [["30_ambicion", 0.70]] + case["cuts"][0]["P"]
    entrada = tmp_path / "caso_autoevidencia_marcado.json"
    entrada.write_text(json.dumps(case, ensure_ascii=False), encoding="utf-8")
    out = tmp_path / "resultado_autoevidencia_marcado.json"
    res = _corre_estandar(entrada, "AUTOEVIDENCIA_MARCADO", out)
    det = _detalle_guardian(res)
    assert det is not None, "el guardián no corrió en la ruta real"
    assert det.get("status") == "EXECUTED_WITH_FINDINGS", det
    assert det.get("bandera") is True, det
    assert det.get("n_autoevidencia") == 1, det
    assert det.get("familias_autoevidenciadas") == ["30_ambicion"], det
    b = (det.get("banderas") or [])[0]
    assert b.get("tipo") == "AUTOEVIDENCIA_NOMBRE_DE_FAMILIA", b
    assert b.get("corte") == "C1_490BC", b
    assert b.get("eje") == "P", b
    assert b.get("token") == "30_ambicion", b
    comp = _componente(res, "hub:guardian_entrada_autoevidencia")
    assert comp is not None and comp.get("status") == "HUB_ACTIVA", comp
    assert "bandera=True" in (comp.get("reason") or ""), comp
    # Solo bandera: la marca no reescribe H ni el cierre.
    _h_intacta(res)


def test_bypass_guardian_off_queda_marcado_apagada_por_flag(tmp_path):
    out = tmp_path / "resultado_autoevidencia_off.json"
    res = _corre_estandar(THEMISTOCLES, "AUTOEVIDENCIA_BYPASS", out,
                          {"LAT_GUARDIAN_ENTRADA_AUTOEVIDENCIA": "0"})
    det = _detalle_guardian(res)
    assert det is None, "el apagado no debe inventar un detalle del guardián"
    comp = _componente(res, "hub:guardian_entrada_autoevidencia")
    assert comp is not None, "el bypass no debe borrar la fila del hub en silencio"
    assert comp.get("status") == "APAGADA_POR_FLAG", comp
    assert "LAT_GUARDIAN_ENTRADA_AUTOEVIDENCIA=0" in (comp.get("reason") or ""), comp
    # H intacta e idéntica al baseline; el resto de guardianes sigue corriendo.
    _h_intacta(res)
    g = res.get("guardianes") or {}
    assert g.get("status") == "EXECUTED", g
    bloques = {b.get("guardian") for b in g.get("bloques") or []}
    assert "LOGICA_COPI" in bloques, bloques
    assert "DECIMO_HOMBRE_LATENCIA" in bloques, bloques
    # La otra pata (stores 011) no se apaga con este flag: sigue ejecutando.
    comp011 = _componente(res, "autoevidencia_stores_011.py")
    assert comp011 is not None and comp011.get("status") == "EXECUTED", comp011


# ------------------------------------------------------------------ 7) constantes y sha
def test_constantes_y_sha_del_guardian():
    g = _load_guardian()
    assert g.VERSION == VERSION_GUARDIAN
    assert _sha256(GUARDIAN).startswith(SHA_GUARDIAN)
    assert _sha256(MOTOR_DIR / "Engine_V5_CANONICO_SOLO.py").startswith(SHA_ENGINE)
    assert _sha256(MOTOR_DIR / "patterns_final_v14.json").startswith(SHA_PATTERNS)
