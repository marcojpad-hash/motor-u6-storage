#!/usr/bin/env python3
"""test_cableado_beristain.py — Beristáin (tropos) cableado en la ruta real de corrida (post-predictor).

Spec: orquestador-central docs/filtros_operativos/BERISTAIN.md v1.0 + MAPA_GUARDIANES.md §3.1.
Contrato de la familia: el filtro corre DESPUÉS del predictor, solo MARCA
(can_decide_H=False), y un NO_RESUELTO puede retener el cierre vía
ruta_cierre_latente sin decidir H ni tocar patterns.

Capas de este archivo (en orden):
  1) Neutral, fuera de U6: el núcleo retórico genérico + la serie de vecinos se
     prueban cargando guardian_tropos_beristain_v1.py por ruta explícita, sin
     importar el motor. El acoplamiento al tablero 244 y a los vecinos es U6
     por diseño del spec (BERISTAIN.md §5) y se verifica en la corrida.
  2) Estático: el cableado existe en UNICO run() y en correr_guardianes.
  3) Vivo (subproceso correr_estandar.py): en una corrida real el bloque
     TROPOS_BERISTAIN ejecuta y marca una metáfora copulativa.
  4) Unidad: un NO_RESUELTO de tropos retiene el cierre vía ruta_cierre_latente.
  5) Bypass (subproceso con BERISTAIN_GUARDIAN=off): el apagado queda marcado
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
TROPOS = MOTOR_DIR / "guardian_tropos_beristain_v1.py"
UNICO = MOTOR_DIR / "MOTOR_V15_3_UNICO_20260927.py"
CONTROL = MOTOR_DIR / "guardianes_control_v1.py"
THEMISTOCLES = ROOT / "inputs" / "THEMISTOCLES_FREEZE_480BC_CATALOG_REPAIR_R2.json"

# Metáfora copulativa canónica (demo del propio módulo): sujeto humano + cópula
# + nombre de otro dominio.
METAFORA_TEXTO = "Mi padre era un león en los negocios."
METONIMIA_TEXTO = "El Kremlin anunció sanciones."
IRONIA_TEXTO = "¡Qué listo!, otra quiebra."
CATACRESIS_TEXTO = "Hay un cuello de botella en la producción."
SUJETO_ELIDIDO_TEXTO = "Es un león."


def _load_tropos():
    spec = importlib.util.spec_from_file_location("guardian_tropos_beristain_v1", TROPOS)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _hallazgos(mod, texto):
    return mod.analizar_texto(texto)["hallazgos"]


# ------------------------------------------------------------------ 1) neutral, fuera de U6
def test_metafora_copulativa_detectada_con_fragmento():
    m = _load_tropos()
    h = _hallazgos(m, METAFORA_TEXTO)
    det = [x for x in h if x["tropo"] == "METAFORA" and x["estado"] == "DETECTADA"]
    assert det, h
    # la marca trae el fragmento que la sostiene y la transferencia de dominio
    assert "león" in det[0]["evidencia"]["fragmento"]
    assert (det[0].get("transferencia") or {}).get("dominio_origen") == "ANIMAL"


def test_metonimia_lugar_por_institucion_detectada():
    m = _load_tropos()
    h = _hallazgos(m, METONIMIA_TEXTO)
    det = [x for x in h if x["tropo"] == "METONIMIA" and x["estado"] == "DETECTADA"]
    assert det, h
    assert det[0]["subtipo"] == "LUGAR_POR_INSTITUCION"


def test_ironia_solo_no_resuelto_nunca_invierte_el_sentido():
    m = _load_tropos()
    h = _hallazgos(m, IRONIA_TEXTO)
    ir = [x for x in h if x["tropo"] == "IRONIA"]
    assert ir, h
    assert all(x["estado"] == "NO_RESUELTO" for x in ir)
    assert not [x for x in ir if x["estado"] == "DETECTADA"]
    # el inventario la tiene DESCARTADO_FP: solo se registra la posibilidad
    assert all(x.get("no_invertir_sentido") is True for x in ir)


def test_catacresis_no_se_marca_como_figura_viva():
    m = _load_tropos()
    h = _hallazgos(m, CATACRESIS_TEXTO)
    cat = [x for x in h if x["tropo"] == "CATACRESIS"]
    assert cat, h
    assert all(x["estado"] == "OBSERVACION" and x["bloquea_lectura_literal"] is False for x in cat)
    assert not [x for x in h if x["tropo"] == "METAFORA" and x["estado"] == "DETECTADA"], h


def test_frontera_sujeto_elidido_no_resuelto_sin_afirmar_figura():
    m = _load_tropos()
    h = _hallazgos(m, SUJETO_ELIDIDO_TEXTO)
    assert any(x["tropo"] == "METAFORA" and x["estado"] == "NO_RESUELTO" for x in h)
    assert not [x for x in h if x["tropo"] == "METAFORA" and x["estado"] == "DETECTADA"], h


def test_solo_marca_nunca_decide():
    m = _load_tropos()
    r = m.guardian([{"origen": "question", "texto": METAFORA_TEXTO}], question=METAFORA_TEXTO)
    assert r["bandera"] in ("LIMPIO", "MARCA", "NO_RESUELTO")
    assert "H1" not in r and "H2" not in r and "veredicto" not in r
    assert r.get("can_decide_H") is False
    assert all(x["estado"] in ("DETECTADA", "POSIBLE", "NO_RESUELTO", "OBSERVACION")
               for x in r["marcas"])


def test_vecino_corrige_marca_logica_sobre_figura():
    m = _load_tropos()
    bloque_tropos = m.guardian([{"origen": "question", "texto": METAFORA_TEXTO}],
                               question=METAFORA_TEXTO)
    vecinos = [{"guardian": "LOGICA_COPI", "marcas": [
        {"tipo": "FALACIA_ESPEJO:AFIRMAR_EL_CONSECUENTE", "estado": "DETECTADA",
         "evidencia": {"origen": "question", "fragmento": METAFORA_TEXTO}}]}]
    corr = m.corregir_con_vecinos(bloque_tropos, vecinos)
    assert corr, "una marca lógica sobre una figura debe corregirse a NO_RESUELTO"
    assert corr[0]["vecino"] == "LOGICA_COPI" and corr[0]["estado"] == "NO_RESUELTO"
    assert corr[0]["tropo"] == "METAFORA"


# ------------------------------------------------------------------ 2) estático: el cableado existe
def test_cableado_presente_en_runner_y_control():
    src = UNICO.read_text(encoding="utf-8")
    assert 'gmod.correr_guardianes' in src
    assert 'result["guardianes"]=guard_out' in src
    assert 'BERISTAIN_GUARDIAN' in src
    assert 'omitir=_tropos_omitir' in src
    assert '"tropos_modo":_tropos_modo' in src
    ctrl = CONTROL.read_text(encoding="utf-8")
    assert 'def correr_guardianes(' in ctrl and 'omitir=frozenset()' in ctrl
    assert '"TROPOS_BERISTAIN" in omitir' in ctrl
    assert '"NO_CONFIGURADO"' in ctrl
    assert 'seguro("TROPOS_BERISTAIN", lambda: g_tropos' in ctrl


# ------------------------------------------------------------------ 3, 4 y 5) vivo: corrida real por subproceso
def _fixture_con_metafora(tmp_path):
    d = json.loads(THEMISTOCLES.read_text(encoding="utf-8"))
    d["question"] = METAFORA_TEXTO
    p = tmp_path / "caso_beristain.json"
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
    env.pop("BERISTAIN_GUARDIAN", None)
    if env_extra:
        env.update(env_extra)
    r = subprocess.run(
        [PYTHON_MOTOR, "correr_estandar.py", str(entrada), nombre, str(salida)],
        cwd=str(ROOT), env=env, capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-2000:]
    return json.loads(Path(salida).read_text(encoding="utf-8"))


def _bloque_tropos(resultado):
    bloques = (resultado.get("guardianes") or {}).get("bloques") or []
    return next((b for b in bloques if b.get("guardian") == "TROPOS_BERISTAIN"), None)


def test_corrida_real_ejecuta_tropos_y_marca_la_metafora(tmp_path):
    entrada = _fixture_con_metafora(tmp_path)
    out = tmp_path / "resultado_beristain.json"
    res = _corre_estandar(entrada, "BERISTAIN_SMOKE", out)
    g = res.get("guardianes") or {}
    assert g.get("status") == "EXECUTED"
    assert g.get("can_decide_H") is False
    bloque = _bloque_tropos(res)
    assert bloque is not None, "sin bloque TROPOS_BERISTAIN en una corrida real"
    assert bloque.get("can_decide_H") is False
    det = [m for m in bloque.get("marcas", [])
           if m.get("estado") == "DETECTADA" and "METAFORA" in m.get("tipo", "")]
    assert det, bloque.get("marcas")
    assert any("león" in str(m.get("evidencia", {}).get("fragmento", "")) for m in det)
    # H intacto: el guardián solo marca, no reescribe predictor ni H
    v = g.get("verificacion_H_intacto") or {}
    assert v.get("predictor_igual") is True and v.get("H1_H2_igual") is True
    assert v.get("patterns_igual") is True
    # el recibo de componentes lo registra como ejecutado, sin poder de decisión
    comp = next((s for s in (res.get("execution") or {}).get("component_status") or []
                 if s.get("component") == "guardianes_control_v1.py"), None)
    assert comp is not None and comp.get("status") == "EXECUTED"
    assert comp.get("can_decide_H") is False
    assert comp.get("tropos_modo") == "activo"
    # si algún NO_RESUELTO es de tropos, el cierre queda retenido por tropos
    ruta = g.get("ruta_cierre_latente") or {}
    if any(m.get("estado") == "NO_RESUELTO" for m in bloque.get("marcas", [])):
        assert ruta.get("estado_cierre") == "LATENTE", ruta
        assert "TROPOS_BERISTAIN" in (ruta.get("guardianes_que_objetan") or []), ruta


def test_retencion_cierre_no_resuelto_tropos(tmp_path):
    """Un NO_RESUELTO de TROPOS_BERISTAIN retiene el cierre (ruta_cierre_latente)."""
    spec = importlib.util.spec_from_file_location("guardianes_control_v1", CONTROL)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    bloques = [
        {"guardian": "LOGICA_COPI", "bandera": "LIMPIO", "marcas": []},
        {"guardian": "TROPOS_BERISTAIN", "bandera": "NO_RESUELTO", "marcas": [
            {"tipo": "TROPO_IRONIA:NO_RESUELTO", "estado": "NO_RESUELTO",
             "evidencia": {"origen": "question", "fragmento": "¡Qué listo!, otra quiebra."}}]},
    ]
    ruta = mod.ruta_cierre_latente(bloques, {"case_id": "TEST_TROPOS_RETENCION"},
                                   {"cuts": []}, {}, MOTOR_DIR)
    assert ruta.get("estado_cierre") == "LATENTE", ruta
    assert "TROPOS_BERISTAIN" in (ruta.get("guardianes_que_objetan") or []), ruta
    assert ruta.get("can_decide_H") is False


def test_bypass_beristain_off_queda_marcado_no_configurado(tmp_path):
    entrada = _fixture_con_metafora(tmp_path)
    out = tmp_path / "resultado_beristain_off.json"
    res = _corre_estandar(entrada, "BERISTAIN_BYPASS", out, {"BERISTAIN_GUARDIAN": "off"})
    g = res.get("guardianes") or {}
    bloque = _bloque_tropos(res)
    assert bloque is not None, "el bypass no debe borrar el bloque en silencio"
    assert bloque.get("bandera") == "NO_CONFIGURADO", bloque
    assert not [m for m in bloque.get("marcas", []) if m.get("estado") == "DETECTADA"]
    comp = next((s for s in (res.get("execution") or {}).get("component_status") or []
                 if s.get("component") == "guardianes_control_v1.py"), None)
    assert comp is not None and comp.get("tropos_modo") == "off"
    assert (comp.get("banderas") or {}).get("TROPOS_BERISTAIN") == "NO_CONFIGURADO"
