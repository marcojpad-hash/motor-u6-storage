#!/usr/bin/env python3
"""test_cableado_pregunta_detras.py — Pregunta detrás v2 cableado en la ruta real de corrida (post-predictor).

Spec: orquestador-central docs/filtros_operativos/PLUGIN_PREGUNTA.md v1.0 + MAPA_GUARDIANES.md §2.2.
Contrato de la familia: el filtro corre DESPUÉS del predictor, solo MARCA
(can_decide_H=False), y un NO_RESUELTO puede retener el cierre vía
ruta_cierre_latente sin decidir H ni tocar patterns.

Capas de este archivo (en orden):
  1) Neutral, fuera de U6: la función del lexema (campo vs etiqueta vs marco) se
     prueba cargando plugin_pregunta_detras_v2.py por ruta explícita, sin
     importar el motor. El plugin es léxico/morfosintáctico por diseño del spec
     (PLUGIN_PREGUNTA.md §2–§4) y se verifica en la corrida.
  2) Estático: el cableado existe en UNICO run() y en correr_guardianes.
  3) Vivo (subproceso correr_estandar.py): en una corrida real el bloque
     PREGUNTA_DETRAS_V2 ejecuta y marca un RED_FLAG por acumulación de etiquetas.
  4) Unidad: un NO_RESUELTO de PREGUNTA_DETRAS_V2 retiene el cierre vía ruta_cierre_latente.
  5) Bypass (subproceso con PREGUNTA_DETRAS_GUARDIAN=off): el apagado queda marcado
     NO_CONFIGURADO en el recibo, no pasa en silencio.
"""
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # motor/
MOTOR_DIR = ROOT / "motor"
DETRAS = MOTOR_DIR / "plugin_pregunta_detras_v2.py"
UNICO = MOTOR_DIR / "MOTOR_V15_3_UNICO_20260927.py"
CONTROL = MOTOR_DIR / "guardianes_control_v1.py"
THEMISTOCLES = ROOT / "inputs" / "THEMISTOCLES_FREEZE_480BC_CATALOG_REPAIR_R2.json"

# Sondas del propio _demo() del plugin (v2.3.3).
RED_FLAG_TEXTO = "¿Era ambicioso y famoso y un genio?"
MARCAJE_TEXTO = "¿Era ambicioso?"
CAMPO_TEXTO = "La ambición aparece durante su etapa empresarial."
ATRIBUTIVO_TEXTO = "El hombre ambicioso dirigió la empresa."
LITOTE_TEXTO = "Su papel no fue ajeno a la crisis; nada desdeñable."
HIPERBOLE_TEXTO = "Fue el más decisivo de la historia, jamás visto."


def _load_detras():
    spec = importlib.util.spec_from_file_location("plugin_pregunta_detras_v2", DETRAS)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


# ------------------------------------------------------------------ 1) neutral, fuera de U6
def test_acumulacion_de_etiquetas_da_red_flag():
    m = _load_detras()
    r = m.filtrar(RED_FLAG_TEXTO)
    assert r["bandera"] == "RED_FLAG_POSIBLE_PERFILAMIENTO", r
    assert r["n_perfilamiento"] == 3, r
    assert r["red_flag"] is True
    assert r["accion"] == "continuar_con_highlight"
    assert all(x["funcion"] == "ETIQUETA_SUJETO" for x in r["marcajes"])
    assert r["pregunta_detras_sugerida"]


def test_una_sola_etiqueta_da_marcaje_no_red_flag():
    m = _load_detras()
    r = m.filtrar(MARCAJE_TEXTO)
    assert r["bandera"] == "MARCAJE_PERFILAMIENTO", r
    assert r["n_perfilamiento"] == 1, r
    assert r["red_flag"] is False
    assert r["accion"] == "continuar_con_highlight"
    assert r["marcajes"][0]["lexema"] == "ambicioso"
    assert r["marcajes"][0]["funcion"] == "ETIQUETA_SUJETO"


def test_fenomeno_de_campo_no_perfilla():
    m = _load_detras()
    r = m.filtrar(CAMPO_TEXTO)
    assert r["bandera"] is None, r
    assert r["n_perfilamiento"] == 0 and r["n_campo"] == 1, r
    assert r["accion"] == "continuar"
    assert r["pregunta_detras_sugerida"] is None
    assert all(x["funcion"] == "FENOMENO_CAMPO" for x in r["marcajes"])


def test_modificador_atributivo_es_trazable_pero_no_cuenta():
    # v2.3.2: N+Adj atributivo ("hombre ambicioso") → MODIFICADOR_ATRIBUTIVO:
    # se traza, pero NO cuenta a red_flag/perfil (la corrección sintáctica del léxico).
    m = _load_detras()
    r = m.filtrar(ATRIBUTIVO_TEXTO)
    assert r["bandera"] is None, r
    assert r["n_perfilamiento"] == 0, r
    assert any(x["funcion"] == "MODIFICADOR_ATRIBUTIVO" and x["lexema"] == "ambicioso"
               for x in r["marcajes"]), r


def test_tropos_estructurales_litote_e_hiperbole():
    m = _load_detras()
    lit = m.filtrar(LITOTE_TEXTO)
    assert lit["bandera"] == "RED_FLAG_POSIBLE_PERFILAMIENTO", lit
    assert any(x["funcion"] == "MARCO_EVALUATIVO" and x["lexema"] == "marco_litotes"
               for x in lit["marcajes"]), lit
    hip = m.filtrar(HIPERBOLE_TEXTO)
    assert hip["bandera"] == "MARCAJE_PERFILAMIENTO", hip
    assert any(x["funcion"] == "MARCO_EVALUATIVO" and x["lexema"] == "marco_hiperbole"
               for x in hip["marcajes"]), hip


def test_solo_marca_nunca_decide():
    m = _load_detras()
    for texto in (RED_FLAG_TEXTO, MARCAJE_TEXTO, CAMPO_TEXTO):
        r = m.filtrar(texto)
        assert "H1" not in r and "H2" not in r and "veredicto" not in r and "familia" not in r
        assert r["accion"] in ("continuar", "continuar_con_highlight")
        assert r["plugin"] == "plugin_pregunta_detras_v2"


# ------------------------------------------------------------------ 2) estático: el cableado existe
def test_cableado_presente_en_runner_y_control():
    src = UNICO.read_text(encoding="utf-8")
    assert 'gmod.correr_guardianes' in src
    assert 'result["guardianes"]=guard_out' in src
    assert 'PREGUNTA_DETRAS_GUARDIAN' in src
    # Tras fusionar, el omitir es la unión de los conjuntos; lo que importa
    # es que _detras_omitir llegue a correr_guardianes.
    _lineas_guardianes = [ln for ln in src.splitlines() if "correr_guardianes" in ln and "omitir=" in ln]
    assert _lineas_guardianes and "_detras_omitir" in _lineas_guardianes[0]
    assert '"detras_modo":_detras_modo' in src
    ctrl = CONTROL.read_text(encoding="utf-8")
    assert 'def correr_guardianes(' in ctrl and 'omitir=frozenset()' in ctrl
    assert '"PREGUNTA_DETRAS_V2" in omitir' in ctrl
    assert '"NO_CONFIGURADO"' in ctrl
    assert 'seguro("PREGUNTA_DETRAS_V2", lambda: g_detras' in ctrl


# ------------------------------------------------------------------ 3, 4 y 5) vivo: corrida real por subproceso
def _fixture_con_red_flag(tmp_path):
    d = json.loads(THEMISTOCLES.read_text(encoding="utf-8"))
    d["question"] = RED_FLAG_TEXTO
    p = tmp_path / "caso_detras.json"
    p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    return p


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
    env.pop("PREGUNTA_DETRAS_GUARDIAN", None)
    if env_extra:
        env.update(env_extra)
    r = subprocess.run(
        [PYTHON_MOTOR, "correr_estandar.py", str(entrada), nombre, str(salida)],
        cwd=str(ROOT), env=env, capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-2000:]
    return json.loads(Path(salida).read_text(encoding="utf-8"))


def _bloque_detras(resultado):
    bloques = (resultado.get("guardianes") or {}).get("bloques") or []
    return next((b for b in bloques if b.get("guardian") == "PREGUNTA_DETRAS_V2"), None)


def test_corrida_real_ejecuta_detras_y_marca_el_red_flag(tmp_path):
    entrada = _fixture_con_red_flag(tmp_path)
    out = tmp_path / "resultado_detras.json"
    res = _corre_estandar(entrada, "DETRAS_SMOKE", out)
    g = res.get("guardianes") or {}
    assert g.get("status") == "EXECUTED"
    assert g.get("can_decide_H") is False
    bloque = _bloque_detras(res)
    assert bloque is not None, "sin bloque PREGUNTA_DETRAS_V2 en una corrida real"
    assert bloque.get("can_decide_H") is False
    assert bloque.get("bandera") == "MARCA", bloque
    red = [m for m in bloque.get("marcas", [])
           if m.get("tipo") == "RED_FLAG_POSIBLE_PERFILAMIENTO"
           and (m.get("evidencia") or {}).get("origen") == "question"]
    assert red, bloque.get("marcas")
    # la marca trae el texto de la pregunta y los marcajes del plugin
    assert RED_FLAG_TEXTO[:40] in str(red[0].get("evidencia", {}).get("texto", ""))
    assert any(x.get("funcion") == "ETIQUETA_SUJETO"
               for x in (red[0].get("evidencia", {}).get("marcajes") or []))
    # H intacto: el guardián solo marca, no reescribe predictor ni H
    v = g.get("verificacion_H_intacto") or {}
    assert v.get("predictor_igual") is True and v.get("H1_H2_igual") is True
    assert v.get("patterns_igual") is True
    # el recibo de componentes lo registra como ejecutado, sin poder de decisión
    comp = next((s for s in (res.get("execution") or {}).get("component_status") or []
                 if s.get("component") == "guardianes_control_v1.py"), None)
    assert comp is not None and comp.get("status") == "EXECUTED"
    assert comp.get("can_decide_H") is False
    assert comp.get("detras_modo") == "activo"
    assert (comp.get("banderas") or {}).get("PREGUNTA_DETRAS_V2") == "MARCA"


def test_retencion_cierre_no_resuelto_detras(tmp_path):
    """Un NO_RESUELTO de PREGUNTA_DETRAS_V2 retiene el cierre (ruta_cierre_latente)."""
    spec = importlib.util.spec_from_file_location("guardianes_control_v1", CONTROL)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    bloques = [
        {"guardian": "LOGICA_COPI", "bandera": "LIMPIO", "marcas": []},
        {"guardian": "PREGUNTA_DETRAS_V2", "bandera": "NO_RESUELTO", "marcas": [
            {"tipo": "MARCAJE_PERFILAMIENTO", "estado": "NO_RESUELTO",
             "evidencia": {"origen": "question", "fragmento": RED_FLAG_TEXTO}}]},
    ]
    ruta = mod.ruta_cierre_latente(bloques, {"case_id": "TEST_DETRAS_RETENCION"},
                                   {"cuts": []}, {}, MOTOR_DIR)
    assert ruta.get("estado_cierre") == "LATENTE", ruta
    assert "PREGUNTA_DETRAS_V2" in (ruta.get("guardianes_que_objetan") or []), ruta
    assert ruta.get("can_decide_H") is False


def test_bypass_detras_off_queda_marcado_no_configurado(tmp_path):
    entrada = _fixture_con_red_flag(tmp_path)
    out = tmp_path / "resultado_detras_off.json"
    res = _corre_estandar(entrada, "DETRAS_BYPASS", out, {"PREGUNTA_DETRAS_GUARDIAN": "off"})
    g = res.get("guardianes") or {}
    bloque = _bloque_detras(res)
    assert bloque is not None, "el bypass no debe borrar el bloque en silencio"
    assert bloque.get("bandera") == "NO_CONFIGURADO", bloque
    assert not [m for m in bloque.get("marcas", []) if m.get("estado") == "DETECTADA"]
    comp = next((s for s in (res.get("execution") or {}).get("component_status") or []
                 if s.get("component") == "guardianes_control_v1.py"), None)
    assert comp is not None and comp.get("detras_modo") == "off"
    assert (comp.get("banderas") or {}).get("PREGUNTA_DETRAS_V2") == "NO_CONFIGURADO"
