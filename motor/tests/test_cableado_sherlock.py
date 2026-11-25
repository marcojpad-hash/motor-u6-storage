#!/usr/bin/env python3
"""test_cableado_sherlock.py — Sherlock / método de rigor cableado en la ruta
real de corrida (post-predictor).

Specs: MAPA_GUARDIANES.md §2.7 (`plugin_metodo_rigor.py`, bloque
`SHERLOCK_RIGOR`). Sherlock NO tiene ficha propia en filtros_operativos
(igual que Polaridad y Acero), así que la spec es el MAPA §2.7 + el
docstring del plugin (`PLUGIN_METODO_RIGOR — Holmes / Hecate /
Schopenhauer`). El plugin suelto es una alarma corta (Hecate: el letrero no
cambió en 4 cortes; Holmes: la hipótesis nombra apellido; Schopenhauer:
"como yo dije"); el bloque en `guardianes_control` lo envuelve con la
cadena top1 por corte, tokens de hecho del top1
(`HOLMES_TOP1_SIN_TOKENS_DE_HECHO`) y masa a favor vs en contra
(`SCHOPENHAUER_TABLERO_EN_CONTRA`).
Contrato de la familia: el bloque corre DESPUÉS del predictor, solo MARCA
(can_decide_H=False), bandera MARCA o LIMPIO (o ERROR); nunca emite
NO_RESUELTO, así que nunca retiene el cierre por sí mismo: la ruta solo
recoge NO_RESUELTO y DOBLE_NEGACION_LITOTE de los vecinos.

Capas de este archivo (en orden):
  1) Neutral, fuera de U6: rigor() directo (frontera Hecate 3 vs 4 cortes,
     apellidos Holmes, inverso Schopenhauer, vacío) y g_rigor con motor/pred
     sintéticos (LIMPIO / HOLMES sin tokens / SCHOPENHAUER tablero en
     contra / HECATE / sin candidatos / empate de masa / own_evidence
     ausente).
  2) Estático: el cableado existe en UNICO run() y en correr_guardianes.
  3) Vivo (subproceso correr_estandar.py): en una corrida real el bloque
     ejecuta (cadena_top1 "sombra → sombra → sombra", 3 cortes, pieza con
     sha_ok), bandera LIMPIO, H intacta, y el cierre queda LATENTE por
     Copi, no por Sherlock.
  4) Unidad: g_rigor devuelve MARCA / LIMPIO según el caso, y una MARCA de
     Sherlock por sí sola NO retiene el cierre (la ruta solo recoge
     NO_RESUELTO/DOBLE_NEGACION_LITOTE); el mecanismo sí retiene cuando un
     vecino (Copi) objeta con NO_RESUELTO.
  5) Bypass (subproceso con SHERLOCK_GUARDIAN=off): el apagado queda
     marcado NO_CONFIGURADO en el recibo, no pasa en silencio.
"""
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # motor/
MOTOR_DIR = ROOT / "motor"
RIGOR = MOTOR_DIR / "plugin_metodo_rigor.py"
UNICO = MOTOR_DIR / "MOTOR_V15_3_UNICO_20260927.py"
CONTROL = MOTOR_DIR / "guardianes_control_v1.py"
THEMISTOCLES = ROOT / "inputs" / "THEMISTOCLES_FREEZE_480BC_CATALOG_REPAIR_R2.json"


def _motor_con(cadenas):
    return {"cuts": [{"P_top5_ANEXO": [[t]]} for t in cadenas]}


def _pred_con(top1, own):
    return {"candidates": [{"family": top1}], "own_evidence": {top1: own}}


def _load_rigor():
    spec = importlib.util.spec_from_file_location("plugin_metodo_rigor", RIGOR)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _load_control():
    spec = importlib.util.spec_from_file_location("guardianes_control_v1", CONTROL)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


# ------------------------------------------------------------------ 1) neutral, fuera de U6
def test_rigor_hecate_frontera_3_vs_4():
    m = _load_rigor()
    # 3 cortes iguales no bastan: Hecate exige 4 o más con el mismo letrero.
    assert m.rigor({"cadena_top1": "A → A → A"})["auto"] == []
    assert m.rigor({"cadena_top1": "A → B → C"})["auto"] == []
    assert m.rigor({"cadena_top1": "A → A → A → A"})["auto"] == [
        "HECATE_MAS_DE_LO_MISMO: el letrero no cambio 4 cortes"]
    assert m.rigor({"cadena_top1": "A → A → A → A → A"})["auto"] == [
        "HECATE_MAS_DE_LO_MISMO: el letrero no cambio 4 cortes"]


def test_rigor_holmes_apellidos():
    m = _load_rigor()
    for h in ("es kant", "ES FREUD", "se llama Temistocles", "es monroe"):
        auto = m.rigor({"cadena_top1": "A → B"}, hipotesis=h)["auto"]
        assert auto == ["HOLMES: la hipotesis nombra apellido (ciego roto)"], h
    # Una hipótesis sin apellido no dispara Holmes.
    assert m.rigor({"cadena_top1": "A → B"},
                   hipotesis="arquetipo_el_gobernante")["auto"] == []
    assert m.rigor({"cadena_top1": "A → B"}, hipotesis="")["auto"] == []


def test_rigor_solo_hecate_con_hipotesis_de_catalogo():
    # V7 (B-H2): con una hipótesis que es un nombre de familia del catálogo
    # 244, Holmes/Schopenhauer del plugin no pueden disparar (literales e
    # inverso sin fuente en la ruta real); lo único vivo del plugin es Hécate.
    m = _load_rigor()
    auto = m.rigor({"cadena_top1": "A → A → A → A"},
                   hipotesis="arquetipo_el_gobernante")["auto"]
    assert auto == ["HECATE_MAS_DE_LO_MISMO: el letrero no cambio 4 cortes"]


def test_rigor_schopenhauer_inverso():
    m = _load_rigor()
    assert m.rigor({"cadena_top1": "A → B"},
                   inverso="Como yo dije, era obvio")["auto"] == [
        "SCHOPENHAUER: defender el tanteo, no el tablero"]
    assert m.rigor({"cadena_top1": "A → B"},
                   inverso="el tablero dice otra cosa")["auto"] == []
    assert m.rigor()["auto"] == []
    r = m.rigor()
    assert r["plugin"] == "METODO_RIGOR"
    assert set(r) == {"plugin", "plantilla", "auto", "cadena_top1", "nota"}


def test_g_rigor_limpio_caso_sano():
    mod = _load_control()
    b = mod.g_rigor(MOTOR_DIR, _motor_con(["A", "B", "C"]),
                    _pred_con("TOP", {"favor_tokens": ["t1"],
                                      "favor_mass": [3.0], "contra_mass": [1.0]}))
    assert b["guardian"] == "SHERLOCK_RIGOR"
    assert b["bandera"] == "LIMPIO" and b["n_marcas"] == 0, b
    assert b["marcas"] == []
    assert b["can_decide_H"] is False
    assert b["escribe_H"] is False and b["escribe_patterns"] is False
    assert b["n_revisados"] == 3, b
    assert [(p["archivo"], p["sha_ok"]) for p in b["piezas"]] == [
        ("plugin_metodo_rigor.py", True)], b["piezas"]


def test_g_rigor_holmes_sin_tokens_de_hecho():
    mod = _load_control()
    b = mod.g_rigor(MOTOR_DIR, _motor_con(["A", "B", "C"]),
                    _pred_con("TOP", {"favor_tokens": [],
                                      "favor_mass": [3.0], "contra_mass": [1.0]}))
    assert b["bandera"] == "MARCA", b
    assert [x["tipo"] for x in b["marcas"]] == ["HOLMES_TOP1_SIN_TOKENS_DE_HECHO"]
    assert b["marcas"][0]["estado"] == "DETECTADA"
    # own_evidence ausente para el top1: tampoco hay tokens a favor.
    b = mod.g_rigor(MOTOR_DIR, _motor_con(["A", "B", "C"]),
                    _pred_con("TOP", {}))
    assert b["bandera"] == "MARCA", b
    assert [x["tipo"] for x in b["marcas"]] == ["HOLMES_TOP1_SIN_TOKENS_DE_HECHO"]


def test_g_rigor_schopenhauer_tablero_en_contra():
    mod = _load_control()
    b = mod.g_rigor(MOTOR_DIR, _motor_con(["A", "B", "C"]),
                    _pred_con("TOP", {"favor_tokens": ["t1"],
                                      "favor_mass": [1.0], "contra_mass": [5.0]}))
    assert b["bandera"] == "MARCA", b
    assert [x["tipo"] for x in b["marcas"]] == ["SCHOPENHAUER_TABLERO_EN_CONTRA"]
    assert b["marcas"][0]["estado"] == "DETECTADA"
    # Empate de masa (contra == favor) no es tablero en contra: es estricto.
    b = mod.g_rigor(MOTOR_DIR, _motor_con(["A", "B", "C"]),
                    _pred_con("TOP", {"favor_tokens": ["t1"],
                                      "favor_mass": 2.0, "contra_mass": 2.0}))
    assert b["bandera"] == "LIMPIO" and b["n_marcas"] == 0, b


def test_g_rigor_hecate_cuatro_cortes_iguales():
    mod = _load_control()
    b = mod.g_rigor(MOTOR_DIR, _motor_con(["A", "A", "A", "A"]),
                    _pred_con("TOP", {"favor_tokens": ["t1"],
                                      "favor_mass": [3.0], "contra_mass": [1.0]}))
    assert b["bandera"] == "MARCA", b
    assert [x["tipo"] for x in b["marcas"]] == ["HECATE_MAS_DE_LO_MISMO"]


def test_g_rigor_sin_candidatos_no_marca():
    mod = _load_control()
    b = mod.g_rigor(MOTOR_DIR, _motor_con(["A", "B"]),
                    {"candidates": [], "own_evidence": {}})
    assert b["bandera"] == "LIMPIO" and b["n_marcas"] == 0, b


def test_solo_marca_nunca_decide():
    mod = _load_control()
    for motor, pred in (
            (_motor_con(["A", "B", "C"]),
             _pred_con("TOP", {"favor_tokens": ["t1"],
                              "favor_mass": [3.0], "contra_mass": [1.0]})),
            (_motor_con(["A", "A", "A", "A"]),
             _pred_con("TOP", {"favor_tokens": [],
                              "favor_mass": [1.0], "contra_mass": [5.0]}))):
        b = mod.g_rigor(MOTOR_DIR, motor, pred)
        assert b["can_decide_H"] is False
        assert b["escribe_H"] is False and b["escribe_patterns"] is False
        assert "H1" not in b and "H2" not in b
        assert b["bandera"] in ("MARCA", "LIMPIO")


# ------------------------------------------------------------------ 2) estático: el cableado existe
def test_cableado_presente_en_runner_y_control():
    src = UNICO.read_text(encoding="utf-8")
    assert 'gmod.correr_guardianes' in src
    assert 'result["guardianes"]=guard_out' in src
    assert 'SHERLOCK_GUARDIAN' in src
    # Tras fusionar, el omitir es la unión de los conjuntos; lo que importa
    # es que _sherlock_omitir llegue a correr_guardianes.
    _lineas_guardianes = [ln for ln in src.splitlines() if "correr_guardianes" in ln and "omitir=" in ln]
    assert _lineas_guardianes and "_sherlock_omitir" in _lineas_guardianes[0]
    assert '"sherlock_modo":_sherlock_modo' in src
    ctrl = CONTROL.read_text(encoding="utf-8")
    assert 'def correr_guardianes(' in ctrl and 'omitir=frozenset()' in ctrl
    assert '"SHERLOCK_RIGOR" in omitir' in ctrl
    assert '"NO_CONFIGURADO"' in ctrl
    assert 'seguro("SHERLOCK_RIGOR"' in ctrl


# ------------------------------------------------------------------ 3, 4 y 5) vivo: corrida real por subproceso
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
    env.pop("SHERLOCK_GUARDIAN", None)
    if env_extra:
        env.update(env_extra)
    r = subprocess.run(
        [PYTHON_MOTOR, "correr_estandar.py", str(entrada), nombre, str(salida)],
        cwd=str(ROOT), env=env, capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-2000:]
    return json.loads(Path(salida).read_text(encoding="utf-8"))


def _bloque(resultado, nombre):
    bloques = (resultado.get("guardianes") or {}).get("bloques") or []
    return next((b for b in bloques if b.get("guardian") == nombre), None)


def test_corrida_real_ejecuta_sherlock(tmp_path):
    out = tmp_path / "resultado_sherlock.json"
    res = _corre_estandar(THEMISTOCLES, "SHERLOCK_SMOKE", out)
    g = res.get("guardianes") or {}
    assert g.get("status") == "EXECUTED"
    assert g.get("can_decide_H") is False
    b = _bloque(res, "SHERLOCK_RIGOR")
    assert b is not None, "sin bloque SHERLOCK_RIGOR en una corrida real"
    assert b.get("can_decide_H") is False
    # Baseline THEMISTOCLES: cadena_top1 "sombra → sombra → sombra" (3
    # cortes, Hecate exige 4), el top1 sí tiene tokens de hecho a favor y
    # la masa a favor supera a la de en contra -> bandera LIMPIO, 0 marcas.
    assert b.get("bandera") == "LIMPIO", b
    assert b.get("n_marcas") == 0, b
    assert b.get("marcas") == [], b
    assert b.get("n_revisados") == 3, b
    det = b.get("detalle") or {}
    sal = det.get("salida_plugin") or {}
    assert sal.get("plugin") == "METODO_RIGOR", sal
    assert sal.get("cadena_top1") == "sombra → sombra → sombra", sal
    assert sal.get("auto") == [], sal
    piezas_meta = {p.get("archivo"): p for p in b.get("piezas", [])}
    assert piezas_meta["plugin_metodo_rigor.py"]["sha_ok"] is True, piezas_meta
    assert piezas_meta["plugin_metodo_rigor.py"]["sha256"].startswith("d274814d")  # V7: nota B-H2 en el docstring; solo texto.
    # H intacto: los guardianes solo marcan, no reescriben predictor ni H
    v = g.get("verificacion_H_intacto") or {}
    assert v.get("predictor_igual") is True and v.get("H1_H2_igual") is True
    assert v.get("patterns_igual") is True
    assert (res.get("H1") or {}).get("family") == "arquetipo_el_gobernante"
    assert (res.get("H2") or {}).get("family") == "13_enemistad_de_parientes"
    # El cierre queda LATENTE por Copi, no por Sherlock.
    ruta = g.get("ruta_cierre_latente") or {}
    assert ruta.get("estado_cierre") == "LATENTE", ruta
    assert "SHERLOCK_RIGOR" not in (ruta.get("guardianes_que_objetan") or []), ruta
    cg = res.get("cierre_guardianes") or {}
    assert "SHERLOCK_RIGOR" not in (cg.get("guardianes_que_objetan") or []), cg
    # el recibo de componentes lo registra como ejecutado, sin poder de decisión
    comp = next((s for s in (res.get("execution") or {}).get("component_status") or []
                 if s.get("component") == "guardianes_control_v1.py"), None)
    assert comp is not None and comp.get("status") == "EXECUTED"
    assert comp.get("can_decide_H") is False
    assert comp.get("sherlock_modo") == "activo"
    assert (comp.get("banderas") or {}).get("SHERLOCK_RIGOR") == "LIMPIO"


def test_unidad_sherlock_marca_no_retiene_cierre():
    """Una MARCA de Sherlock por sí sola NO retiene el cierre: la ruta
    solo recoge NO_RESUELTO y DOBLE_NEGACION_LITOTE, y Sherlock nunca
    emite NO_RESUELTO. El mecanismo sí retiene cuando un vecino objeta."""
    mod = _load_control()
    marca_sherlock = {"guardian": "SHERLOCK_RIGOR", "bandera": "MARCA", "marcas": [
        {"tipo": "HOLMES_TOP1_SIN_TOKENS_DE_HECHO", "estado": "DETECTADA",
         "evidencia": {"top1": "TOP", "own_evidence": {}}}]}
    ruta = mod.ruta_cierre_latente(
        [{"guardian": "LOGICA_COPI", "bandera": "LIMPIO", "marcas": []},
         marca_sherlock],
        {"case_id": "TEST_SHERLOCK_SIN_RETENCION"}, {"cuts": []}, {}, MOTOR_DIR)
    assert ruta.get("estado_cierre") == "SIN_OBJECION_DE_GUARDIANES", ruta
    assert "SHERLOCK_RIGOR" not in (ruta.get("guardianes_que_objetan") or []), ruta
    # Con un vecino que objeta con NO_RESUELTO, la ruta sí retiene, y
    # Sherlock no aparece entre los que objetan.
    ruta2 = mod.ruta_cierre_latente(
        [{"guardian": "LOGICA_COPI", "bandera": "NO_RESUELTO", "marcas": [
            {"tipo": "NO_RESUELTO_TOP1_NO_ES_TOP_DE_NINGUN_CORTE",
             "estado": "NO_RESUELTO",
             "evidencia": {"top1": "arquetipo_el_gobernante"}}]},
         marca_sherlock],
        {"case_id": "TEST_SHERLOCK_VECINO_RETENIENE"}, {"cuts": []}, {}, MOTOR_DIR)
    assert ruta2.get("estado_cierre") == "LATENTE", ruta2
    assert "LOGICA_COPI" in (ruta2.get("guardianes_que_objetan") or []), ruta2
    assert "SHERLOCK_RIGOR" not in (ruta2.get("guardianes_que_objetan") or []), ruta2
    assert ruta2.get("can_decide_H") is False


def test_bypass_sherlock_off_queda_marcado_no_configurado(tmp_path):
    out = tmp_path / "resultado_sherlock_off.json"
    res = _corre_estandar(THEMISTOCLES, "SHERLOCK_BYPASS", out,
                          {"SHERLOCK_GUARDIAN": "off"})
    g = res.get("guardianes") or {}
    bloque = _bloque(res, "SHERLOCK_RIGOR")
    assert bloque is not None, "el bypass no debe borrar el bloque en silencio"
    assert bloque.get("bandera") == "NO_CONFIGURADO", bloque
    assert not [m for m in bloque.get("marcas", []) if m.get("estado") == "DETECTADA"]
    comp = next((s for s in (res.get("execution") or {}).get("component_status") or []
                 if s.get("component") == "guardianes_control_v1.py"), None)
    assert comp is not None and comp.get("sherlock_modo") == "off"
    assert (comp.get("banderas") or {}).get("SHERLOCK_RIGOR") == "NO_CONFIGURADO"
    # El resto de guardianes sigue corriendo con el bypass de Sherlock.
    assert _bloque(res, "LOGICA_COPI") is not None
    assert _bloque(res, "POLARIDAD_CAUSAL") is not None
