#!/usr/bin/env python3
"""test_cableado_copi.py — Copi cableado en la ruta real de corrida (post-predictor).

Spec: orquestador-central docs/filtros_operativos/COPI.md v1.0 + MAPA_GUARDIANES.md §2.4.
Contrato de la familia: el filtro corre DESPUÉS del predictor, solo MARCA
(can_decide_H=False), y un NO_RESUELTO puede retener el cierre vía
ruta_cierre_latente sin decidir H ni tocar patterns.

Capas de este archivo (en orden):
  1) Neutral, fuera de U6: el núcleo proposicional genérico + el adaptador (a)
     (condicionales/causales del texto) se prueban cargando
     guardian_logica_copi_v1.py por ruta explícita, sin importar el motor.
     Los adaptadores (b) cierre y (c) cadena del top1 son U6 por diseño del
     spec (COPI.md §5) y se verifican en la corrida, no aquí.
  2) Estático: el cableado existe en UNICO run() y en correr_guardianes.
  3) Vivo (subproceso correr_estandar.py): en una corrida real el bloque
     LOGICA_COPI ejecuta y marca un caso de conclusión disfrazada de dato.
  4) Bypass (subproceso con COPI_GUARDIAN=off): el apagado queda marcado
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
COPI = MOTOR_DIR / "guardian_logica_copi_v1.py"
UNICO = MOTOR_DIR / "MOTOR_V15_3_UNICO_20260927.py"
CONTROL = MOTOR_DIR / "guardianes_control_v1.py"
THEMISTOCLES = ROOT / "inputs" / "THEMISTOCLES_FREEZE_480BC_CATALOG_REPAIR_R2.json"

# Caso de conclusión disfrazada de dato (afirmar el consecuente). Misma frase
# que la batería del test viejo de guardianes: si p entonces q; q; por tanto p.
FALACIA_TEXTO = ("Si alguien es un líder nato, entonces funda empresas. "
                 "Fundó empresas, así que es un líder nato.")
MP_TEXTO = "Si invierte, entonces crece. Invirtió, así que crece."
FRONTERA_TEXTO = ("Si llueve, entonces la calle se moja. "
                  "Llueve, así que el suelo está húmedo.")


def _load_copi():
    spec = importlib.util.spec_from_file_location("guardian_logica_copi_v1", COPI)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


# ------------------------------------------------------------------ 1) neutral, fuera de U6
def test_nucleo_mp_valido_y_reconocido():
    c = _load_copi()
    P, Q = c.A("p"), c.A("q")
    e = c.evaluar_argumento([c.IMP(P, Q), P], Q)
    assert e["estado"] == "VALIDO" and "MP" in e["regla_copi"]
    e = c.evaluar_argumento([c.IMP(P, Q), c.NOT(Q)], c.NOT(P))
    assert e["estado"] == "VALIDO" and "MT" in e["regla_copi"]


def test_nucleo_afirmar_consecuente_invalido_con_contraejemplo():
    c = _load_copi()
    P, Q = c.A("p"), c.A("q")
    e = c.evaluar_argumento([c.IMP(P, Q), Q], P)
    assert e["estado"] == "INVALIDO"
    assert "AFIRMAR_EL_CONSECUENTE" in e["falacia_espejo"]
    assert e["contraejemplo"]  # hay un mundo donde las premisas son verdad y la conclusión no
    assert "MP" in e["espejo_de"]


def test_texto_conclusion_disfrazada_de_dato_marcada():
    c = _load_copi()
    t = c.analizar_texto([FALACIA_TEXTO])
    det = [m for m in t["marcas"] if m["estado"] == "DETECTADA"]
    assert any("AFIRMAR_EL_CONSECUENTE" in m["tipo"] for m in det), t["marcas"]
    # la marca trae el fragmento que la sostiene
    m = next(m for m in det if "AFIRMAR_EL_CONSECUENTE" in m["tipo"])
    assert "Fundó empresas" in str(m["evidencia"])


def test_texto_negar_antecedente_marcado():
    c = _load_copi()
    # "así que" es el marcador de conclusión que el adaptador reconoce;
    # "entonces" solo abre el condicional.
    t = c.analizar_texto(["Si llueve, la calle se moja. No llueve, así que no puede estar mojada."])
    assert any("NEGAR_EL_ANTECEDENTE" in m["tipo"] for m in t["marcas"] if m["estado"] == "DETECTADA")


def test_texto_razonamiento_valido_sin_marca():
    c = _load_copi()
    t = c.analizar_texto([MP_TEXTO])
    assert not [m for m in t["marcas"] if m["estado"] == "DETECTADA"], t["marcas"]


def test_texto_frontera_no_clara_no_resuelto_sin_afirmar_falacia():
    c = _load_copi()
    t = c.analizar_texto([FRONTERA_TEXTO])
    assert any(m["estado"] == "NO_RESUELTO" for m in t["marcas"])
    assert not [m for m in t["marcas"] if m["estado"] == "DETECTADA"], t["marcas"]


def test_solo_marca_nunca_decide():
    c = _load_copi()
    r = c.guardian([FALACIA_TEXTO], {"cuts": []},
                   {"information_state": {"state": "LATENCIA"}, "candidates": []})
    assert r["bandera"] in ("LIMPIO", "MARCA", "NO_RESUELTO")
    assert "H1" not in r and "H2" not in r and "veredicto" not in r
    assert all(m["estado"] in ("DETECTADA", "NO_RESUELTO") for m in r["marcas"])
    # el módulo no declara ningún poder de decisión: no hay can_decide_H en True
    assert "can_decide_H" not in json.dumps(r, ensure_ascii=False) or "true" not in json.dumps(r).lower()


# ------------------------------------------------------------------ 2) estático: el cableado existe
def test_cableado_presente_en_runner_y_control():
    src = UNICO.read_text(encoding="utf-8")
    assert 'gmod.correr_guardianes' in src
    assert 'result["guardianes"]=guard_out' in src
    assert 'COPI_GUARDIAN' in src
    assert 'omitir=_copi_omitir' in src
    assert '"copi_modo":_copi_modo' in src
    ctrl = CONTROL.read_text(encoding="utf-8")
    assert 'def correr_guardianes(' in ctrl and 'omitir=frozenset()' in ctrl
    assert '"LOGICA_COPI" in omitir' in ctrl
    assert '"NO_CONFIGURADO"' in ctrl
    assert 'seguro("LOGICA_COPI", lambda: g_copi' in ctrl


# ------------------------------------------------------------------ 3 y 4) vivo: corrida real por subproceso
def _fixture_con_falacia(tmp_path):
    d = json.loads(THEMISTOCLES.read_text(encoding="utf-8"))
    d["question"] = FALACIA_TEXTO
    p = tmp_path / "caso_copi.json"
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
    env.pop("COPI_GUARDIAN", None)
    if env_extra:
        env.update(env_extra)
    r = subprocess.run(
        [PYTHON_MOTOR, "correr_estandar.py", str(entrada), nombre, str(salida)],
        cwd=str(ROOT), env=env, capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-2000:]
    return json.loads(Path(salida).read_text(encoding="utf-8"))


def _bloque_copi(resultado):
    bloques = (resultado.get("guardianes") or {}).get("bloques") or []
    return next((b for b in bloques if b.get("guardian") == "LOGICA_COPI"), None)


def test_corrida_real_ejecuta_copi_y_marca_la_falacia(tmp_path):
    entrada = _fixture_con_falacia(tmp_path)
    out = tmp_path / "resultado_copi.json"
    res = _corre_estandar(entrada, "COPI_SMOKE", out)
    g = res.get("guardianes") or {}
    assert g.get("status") == "EXECUTED"
    assert g.get("can_decide_H") is False
    bloque = _bloque_copi(res)
    assert bloque is not None, "sin bloque LOGICA_COPI en una corrida real"
    assert bloque.get("bandera") == "MARCA", bloque
    assert bloque.get("can_decide_H") is False
    assert any("AFIRMAR_EL_CONSECUENTE" in m.get("tipo", "")
               for m in bloque.get("marcas", []) if m.get("estado") == "DETECTADA"), bloque["marcas"]
    # H intacto: el guardián solo marca, no reescribe predictor ni H
    v = g.get("verificacion_H_intacto") or {}
    assert v.get("predictor_igual") is True and v.get("H1_H2_igual") is True
    assert v.get("patterns_igual") is True
    # el recibo de componentes lo registra como ejecutado, sin poder de decisión
    comp = next((s for s in (res.get("execution") or {}).get("component_status") or []
                 if s.get("component") == "guardianes_control_v1.py"), None)
    assert comp is not None and comp.get("status") == "EXECUTED"
    assert comp.get("can_decide_H") is False
    assert comp.get("copi_modo") == "activo"


def test_bypass_copi_off_queda_marcado_no_configurado(tmp_path):
    entrada = _fixture_con_falacia(tmp_path)
    out = tmp_path / "resultado_copi_off.json"
    res = _corre_estandar(entrada, "COPI_BYPASS", out, {"COPI_GUARDIAN": "off"})
    g = res.get("guardianes") or {}
    bloque = _bloque_copi(res)
    assert bloque is not None, "el bypass no debe borrar el bloque en silencio"
    assert bloque.get("bandera") == "NO_CONFIGURADO", bloque
    assert not [m for m in bloque.get("marcas", []) if m.get("estado") == "DETECTADA"]
    comp = next((s for s in (res.get("execution") or {}).get("component_status") or []
                 if s.get("component") == "guardianes_control_v1.py"), None)
    assert comp is not None and comp.get("copi_modo") == "off"
    assert (comp.get("banderas") or {}).get("LOGICA_COPI") == "NO_CONFIGURADO"
