#!/usr/bin/env python3
"""test_cableado_z90.py — Compuerta de entrada Z90 (POST_Z90_EN_INPUT)
cableada en la ruta real de corrida (primera línea de run() de UNICO).

La compuerta: `_validate_case` (motor/motor/MOTOR_V15_3_UNICO_20260927.py)
rechaza la entrada cuando un corte trae `date` posterior a `z90_date`
(corte de trabajo): `ValueError("POST_Z90_EN_INPUT: <id>")`. Es la
primera línea de `run()`, así que nada posterior al corte entra al motor:
ni predictor, ni H, ni apuesta.

Hallazgo del cableado (auditoría de ejecución real): Z90 YA se ejecutaba
y bloqueaba en la ruta real sin ninguna prueba que lo demostrara. Este PR
no reescribe el núcleo: solo añade la prueba que demuestra la ejecución
y el bloqueo. Si la compuerta dejara de correr, la capa 1 fallaría
(`_validate_case` no levantaría el ValueError) y la capa 3 fallaría
(la corrida real con un corte post-Z90 terminaría en éxito en vez de
bloquearse con exit 3).

SIN BYPASS, por diseño (decisión documentada): Z90 es un validador duro
de entrada, como INPUT_INVALIDO, TOKEN_INVALIDO y PESO_FUERA_DE_CONTRATO,
que viven en la misma función y tampoco tienen bypass. Un bypass dejaría
entrar evidencia posterior al corte de trabajo y rompería el contrato de
integridad temporal del motor; el apagado "visible" no existe porque no
hay resultado que lo registre: la validación ocurre antes de construir
cualquier resultado. La capa 2 fija este diseño en el código (ninguna
lectura de entorno ni `_off("z90...")` en `_validate_case`).

Capas de este archivo (en orden):
  1) Unidad, fuera de U6: `_validate_case` directo — caso neutro con
     fechas <= Z90 no bloquea; fecha == Z90 pasa (el límite es estricto,
     `>`); fecha > Z90 levanta ValueError POST_Z90_EN_INPUT con el id
     del corte infractor; sin `z90_date` no hay compuerta que aplicar;
     corte sin `date` no bloquea.
  2) Estático: el cableado existe en UNICO (`POST_Z90_EN_INPUT`,
     `_validate_case(case)` como primera línea de `run()`, la
     comparación `str(c["date"]) > str(z90)`) y no hay bypass por diseño.
  3) Vivo (subproceso correr_estandar.py, THEMISTOCLES): la corrida
     baseline pasa con H intacta y cierre AJUSTADA; con `z90_date` y un
     corte con `date` posterior, la corrida se bloquea (exit 3,
     POST_Z90_EN_INPUT en la salida, sin archivo de resultado); con
     `date` == `z90_date` la corrida pasa con H intacta.
  4) Constantes y sha: Engine canónico y catálogo 244 intactos.
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
UNICO = MOTOR_DIR / "MOTOR_V15_3_UNICO_20260927.py"
THEMISTOCLES = ROOT / "inputs" / "THEMISTOCLES_FREEZE_480BC_CATALOG_REPAIR_R2.json"

SHA_ENGINE = "665c39a2"
SHA_PATTERNS = "d827dcc3"

_UNICO_MOD = None


def _load_unico():
    global _UNICO_MOD
    if _UNICO_MOD is None:
        spec = importlib.util.spec_from_file_location(
            "MOTOR_V15_3_UNICO_20260927", UNICO)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
        _UNICO_MOD = mod
    return _UNICO_MOD


def _sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _caso_base():
    return {"case_id": "Z90_PRUEBA",
            "cuts": [{"id": "C1", "date": "0480-01-01",
                      "P": [["amenaza_central", 0.70]], "A": [], "C": []}],
            "z90_date": "0480-06-01"}


# ------------------------------------------------------------------ 1) unidad: _validate_case directo
def test_validar_caso_neutro_no_bloquea():
    m = _load_unico()
    m._validate_case(_caso_base())  # no levanta nada


def test_validar_caso_limite_fecha_igual_a_z90_pasa():
    m = _load_unico()
    case = _caso_base()
    case["cuts"][0]["date"] = "0480-06-01"  # == z90_date: el límite es estricto (>)
    m._validate_case(case)


def test_validar_caso_post_z90_bloquea():
    m = _load_unico()
    case = _caso_base()
    case["cuts"][0]["date"] = "0481-01-01"
    try:
        m._validate_case(case)
    except ValueError as e:
        assert str(e) == "POST_Z90_EN_INPUT: C1", e
    else:
        raise AssertionError("Z90 no bloqueó un corte posterior al corte de trabajo")


def test_validar_caso_post_z90_nombra_el_corte_infractor():
    m = _load_unico()
    case = _caso_base()
    case["cuts"].append({"id": "C2", "date": "0490-01-01",
                         "P": [["defensa_debil", 0.72]], "A": [], "C": []})
    try:
        m._validate_case(case)
    except ValueError as e:
        assert str(e) == "POST_Z90_EN_INPUT: C2", e
    else:
        raise AssertionError("Z90 no bloqueó el segundo corte posterior al corte")


def test_validar_sin_z90_date_no_hay_compuerta():
    m = _load_unico()
    case = _caso_base()
    del case["z90_date"]
    case["cuts"][0]["date"] = "0999-01-01"  # sin z90_date no hay nada que comparar
    m._validate_case(case)


def test_validar_corte_sin_date_no_bloquea():
    m = _load_unico()
    case = _caso_base()
    del case["cuts"][0]["date"]
    m._validate_case(case)


# ------------------------------------------------------------------ 2) estático: el cableado existe, sin bypass por diseño
def test_estatico_compuerta_en_unico_y_run():
    src = UNICO.read_text(encoding="utf-8")
    assert "POST_Z90_EN_INPUT" in src, src
    assert 'str(c["date"]) > str(z90)' in src, src
    assert "def _validate_case(case" in src, src
    # _validate_case es la primera línea de run(): nada entra sin pasar por ella.
    i_run = src.index("def run(case: Dict[str,Any], monte_carlo: bool=True) -> Dict[str,Any]:")
    i_call = src.index("_validate_case(case)", i_run)
    entre = src[i_run:i_call]
    assert entre.count("\n") <= 2, entre  # solo la firma y la llamada


def test_estatico_sin_bypass_por_diseno():
    src = UNICO.read_text(encoding="utf-8")
    i_def = src.index("def _validate_case(case")
    i_end = src.index("def _run_module_features", i_def)
    cuerpo = src[i_def:i_end]
    assert "os.environ" not in cuerpo, cuerpo
    assert "os.getenv" not in cuerpo, cuerpo
    assert "_off(" not in cuerpo, cuerpo
    # Ninguna llamada _off("z90...") en todo UNICO: la compuerta no se apaga.
    assert '_off("z90' not in src, src
    assert "_off('z90" not in src, src


# ------------------------------------------------------------------ 3) vivo por subproceso (correr_estandar.py)
def _python_con_numpy():
    """El motor exige numpy; se usa el python del venv cuando el actual no lo trae."""
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
        cwd=str(ROOT), env=env, capture_output=True, text=True, timeout=600)
    return r


def _h_intacta(resultado):
    assert (resultado.get("H1") or {}).get("family") == "arquetipo_el_gobernante", resultado
    assert (resultado.get("H2") or {}).get("family") == "13_enemistad_de_parientes", resultado
    assert (resultado.get("cierre_final") or {}).get("grado") == "AJUSTADA", resultado


def test_corrida_baseline_themistocles_pasa(tmp_path):
    out = tmp_path / "resultado_z90_baseline.json"
    r = _corre_estandar(THEMISTOCLES, "Z90_BASELINE", out)
    assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-2000:]
    res = json.loads(out.read_text(encoding="utf-8"))
    _h_intacta(res)


def test_corrida_post_z90_bloquea(tmp_path):
    case = json.loads(THEMISTOCLES.read_text(encoding="utf-8"))
    case["z90_date"] = "0480-01-01"
    case["cuts"][0]["date"] = "0481-01-01"  # posterior al corte de trabajo
    entrada = tmp_path / "caso_z90_post.json"
    entrada.write_text(json.dumps(case, ensure_ascii=False), encoding="utf-8")
    out = tmp_path / "resultado_z90_post.json"
    r = _corre_estandar(entrada, "Z90_POST", out)
    combinado = r.stdout + r.stderr
    assert r.returncode == 3, combinado[-2000:]
    assert "POST_Z90_EN_INPUT" in combinado, combinado[-2000:]
    assert "C1_490BC" in combinado, combinado[-2000:]
    assert not out.is_file(), "la corrida bloqueada no debe producir resultado"


def test_corrida_limite_fecha_igual_a_z90_pasa(tmp_path):
    case = json.loads(THEMISTOCLES.read_text(encoding="utf-8"))
    case["z90_date"] = "0480-01-01"
    case["cuts"][0]["date"] = "0480-01-01"  # == z90_date: el límite es estricto
    entrada = tmp_path / "caso_z90_limite.json"
    entrada.write_text(json.dumps(case, ensure_ascii=False), encoding="utf-8")
    out = tmp_path / "resultado_z90_limite.json"
    r = _corre_estandar(entrada, "Z90_LIMITE", out)
    assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-2000:]
    res = json.loads(out.read_text(encoding="utf-8"))
    _h_intacta(res)


# ------------------------------------------------------------------ 4) constantes y sha
def test_constantes_y_sha_engine_y_catalogo():
    assert _sha256(MOTOR_DIR / "Engine_V5_CANONICO_SOLO.py").startswith(SHA_ENGINE)
    assert _sha256(MOTOR_DIR / "patterns_final_v14.json").startswith(SHA_PATTERNS)
