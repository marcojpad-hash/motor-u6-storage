#!/usr/bin/env python3
"""test_cableado_pregunta_dirigida_falacias.py — Pregunta dirigida + post hoc / falacias
cableados en la ruta real de corrida (post-predictor).

Specs: orquestador-central docs/filtros_operativos/PLUGIN_PREGUNTA.md v1.0 y
FALACIAS.md v1.0 + MAPA_GUARDIANES.md §2.3.
Contrato de la familia: los dos bloques corren DESPUÉS del predictor, solo MARCAN
(can_decide_H=False), y un NO_RESUELTO puede retener el cierre vía
ruta_cierre_latente sin decidir H ni tocar patterns. Los dos bloques viven en el
mismo plugin (plugin_pregunta_dirigida_v0_5_1.py) y se cablean como una unidad.

Capas de este archivo (en orden):
  1) Neutral, fuera de U6: los detectores (detectar_pregunta_dirigida,
     detectar_post_hoc, detectar_falacias, analizar_forma_condicional) se prueban
     cargando el plugin por ruta explícita, sin importar el motor.
  2) Estático: el cableado existe en UNICO run() y en correr_guardianes.
  3) Vivo (subproceso correr_estandar.py): en una corrida real los dos bloques
     ejecutan y marcan (FUGA_EN_PREGUNTA en la pregunta, POST_HOC_TEMPORAL y
     AF_AFIRMAR_CONSECUENTE en los textos).
  4) Unidad: un NO_RESUELTO de estos bloques retiene el cierre vía
     ruta_cierre_latente (mecanismo); y los bloques reales nunca emiten
     NO_RESUELTO: son marcadores puros (bandera solo MARCA o LIMPIO).
  5) Bypass (subproceso con PREGUNTA_DIRIGIDA_GUARDIAN=off): el apagado queda
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
DIRIGIDA = MOTOR_DIR / "plugin_pregunta_dirigida_v0_5_1.py"
UNICO = MOTOR_DIR / "MOTOR_V15_3_UNICO_20260927.py"
CONTROL = MOTOR_DIR / "guardianes_control_v1.py"
THEMISTOCLES = ROOT / "inputs" / "THEMISTOCLES_FREEZE_480BC_CATALOG_REPAIR_R2.json"

# Sondas verificadas por ejecución directa del plugin (2026-11-17).
PO_PREGUNTA = "Dado que era inevitable, ¿desde cuándo se veía venir la caída?"
PREGUNTA_PLANA = "¿Qué hora es?"
POST_HOC_TEXTO = "Después de la mudanza, la empresa quebró. La mudanza provocó la quiebra."
POST_HOC_SIN_CAUSAL = "Después de la mudanza, la empresa quebró por la subida de la renta."
AF_TEXTO = "Si llueve, la calle se moja. La calle está mojada, así que es la lluvia."
AF_CLASICO_SIN_MARCA = "Si llueve, la calle se moja. La calle está mojada, así que llovió."
AD_TEXTO = "Si llueve, la calle se moja. Como no llovió, entonces no se mojó la calle."
CS_TEXTO = "Cada vez que canta el gallo, sale el sol, y el canto provoca la salida del sol."
PQ_TEXTO = "¿Por qué siempre miente?"
BC1_TEXTO = "Si y solo si llueve, la calle se moja."
BC2_TEXTO = "Lo necesario es lo mismo que lo suficiente para aprobar."
EQ_TEXTO = "La justicia tarda mucho en llegar, pero la justicia siempre actúa; por tanto, la justicia es lenta y rápida a la vez."
TEXTO_FACTICO = "El agua hierve a 100 grados al nivel del mar."


def _load_dirigida():
    spec = importlib.util.spec_from_file_location("plugin_pregunta_dirigida_v0_5_1", DIRIGIDA)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _tipos(hallazgos):
    return [(h.tipo, h.severidad) for h in hallazgos]


# ------------------------------------------------------------------ 1) neutral, fuera de U6
def test_pregunta_PO_marca_fuga_en_pregunta():
    m = _load_dirigida()
    hall = m.detectar_pregunta_dirigida(PO_PREGUNTA)
    assert ("FUGA_EN_PREGUNTA", "hard") in _tipos(hall), hall
    assert all(h.severidad in ("hard", "soft") for h in hall)


def test_pregunta_plana_no_marca():
    m = _load_dirigida()
    assert m.detectar_pregunta_dirigida(PREGUNTA_PLANA) == []
    assert m.detectar_pregunta_dirigida(TEXTO_FACTICO) == []


def test_post_hoc_biografico_marca_y_sin_causal_no_marca():
    m = _load_dirigida()
    hall = m.detectar_post_hoc(POST_HOC_TEXTO)
    assert ("POST_HOC_TEMPORAL", "soft") in _tipos(hall), hall
    assert m.detectar_post_hoc(POST_HOC_SIN_CAUSAL) == []
    assert m.detectar_post_hoc("La reunión es el martes a las diez.") == []


def test_falacias_af_ad_cs_pq_marcan():
    m = _load_dirigida()
    assert ("AF_AFIRMAR_CONSECUENTE", "hard") in _tipos(m.detectar_falacias(AF_TEXTO))
    assert ("AD_NEGAR_ANTECEDENTE", "soft") in _tipos(m.detectar_falacias(AD_TEXTO))
    assert ("CS_CUM_HOC", "soft") in _tipos(m.detectar_falacias(CS_TEXTO))
    assert ("PQ_PETITIO", "soft") in _tipos(m.detectar_falacias(PQ_TEXTO))


def test_falacias_bc1_bc2_eq_marcan():
    m = _load_dirigida()
    assert ("BC1_BICONDICIONAL_INCOMPLETO", "soft") in _tipos(m.detectar_falacias(BC1_TEXTO))
    assert ("BC2_NECESARIO_SUFICIENTE", "soft") in _tipos(m.detectar_falacias(BC2_TEXTO))
    assert ("EQ_EQUIVOCACION", "soft") in _tipos(m.detectar_falacias(EQ_TEXTO))


def test_texto_factico_no_marca_en_ningun_detector():
    m = _load_dirigida()
    assert m.detectar_post_hoc(TEXTO_FACTICO) == []
    assert m.detectar_falacias(TEXTO_FACTICO) == []
    assert m.detectar_pregunta_dirigida(TEXTO_FACTICO) == []


def test_frontera_raiz_tres_letras_clasico_llovio_queda_no_resuelto():
    # Límite documentado del adaptador, no un fallo del test: analizar_forma_condicional
    # compara átomos por raíz de 3 letras; "llovió" (llo) vs "llueve" (llu) no coinciden,
    # así que la forma clásica de afirmar el consecuente queda NO_RESUELTO y no produce
    # hallazgo. La variante con la misma raíz ("es la lluvia") sí dispara AF hard.
    # Ni siquiera un MP válido se reconoce: "Está lloviendo" (est/llo) vs "llueve" (llu).
    m = _load_dirigida()
    assert m.detectar_falacias(AF_CLASICO_SIN_MARCA) == []
    formas = m.analizar_forma_condicional(AF_CLASICO_SIN_MARCA)
    assert formas and formas[0]["forma"] == "NO_RESUELTO", formas
    mp = m.analizar_forma_condicional(
        "Si llueve, la calle se moja. Está lloviendo, así que la calle se moja.")
    assert mp and mp[0]["forma"] == "NO_RESUELTO", mp


def test_solo_marca_nunca_decide():
    m = _load_dirigida()
    for texto in (PO_PREGUNTA, POST_HOC_TEXTO, AF_TEXTO, CS_TEXTO):
        for h in (m.detectar_pregunta_dirigida(texto)
                  + m.detectar_post_hoc(texto) + m.detectar_falacias(texto)):
            assert h.severidad in ("hard", "soft")
            est = h.estructura or {}
            assert "H1" not in est and "H2" not in est and "veredicto" not in est
            # La acción "bandera_no_bloquea" la declaran los hallazgos de
            # falacias y post hoc; el de FUGA_EN_PREGUNTA (capa 2a_PO) no trae
            # clave "accion" en su estructura, pero tampoco decide nada.
            if "accion" in est:
                assert est["accion"] == "bandera_no_bloquea"


# ------------------------------------------------------------------ 2) estático: el cableado existe
def test_cableado_presente_en_runner_y_control():
    src = UNICO.read_text(encoding="utf-8")
    assert 'gmod.correr_guardianes' in src
    assert 'result["guardianes"]=guard_out' in src
    assert 'PREGUNTA_DIRIGIDA_GUARDIAN' in src
    assert 'omitir=_dirigida_omitir' in src
    assert '"dirigida_modo":_dirigida_modo' in src
    ctrl = CONTROL.read_text(encoding="utf-8")
    assert 'def correr_guardianes(' in ctrl and 'omitir=frozenset()' in ctrl
    assert '"PREGUNTA_DIRIGIDA_POST_HOC" in omitir' in ctrl
    assert '"FALACIAS" in omitir' in ctrl
    assert '"NO_CONFIGURADO"' in ctrl
    assert 'seguro("PREGUNTA_DIRIGIDA_POST_HOC"' in ctrl


# ------------------------------------------------------------------ 3, 4 y 5) vivo: corrida real por subproceso
def _fixture_dirigida(tmp_path):
    d = json.loads(THEMISTOCLES.read_text(encoding="utf-8"))
    d["question"] = PO_PREGUNTA
    d["texto_prueba_post_hoc"] = POST_HOC_TEXTO
    d["texto_prueba_falacia"] = AF_TEXTO + " " + CS_TEXTO
    p = tmp_path / "caso_dirigida.json"
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
    env.pop("PREGUNTA_DIRIGIDA_GUARDIAN", None)
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


def test_corrida_real_ejecuta_dirigida_y_falacias(tmp_path):
    entrada = _fixture_dirigida(tmp_path)
    out = tmp_path / "resultado_dirigida.json"
    res = _corre_estandar(entrada, "DIRIGIDA_SMOKE", out)
    g = res.get("guardianes") or {}
    assert g.get("status") == "EXECUTED"
    assert g.get("can_decide_H") is False
    b1 = _bloque(res, "PREGUNTA_DIRIGIDA_POST_HOC")
    b2 = _bloque(res, "FALACIAS")
    assert b1 is not None, "sin bloque PREGUNTA_DIRIGIDA_POST_HOC en una corrida real"
    assert b2 is not None, "sin bloque FALACIAS en una corrida real"
    assert b1.get("can_decide_H") is False and b2.get("can_decide_H") is False
    assert b1.get("bandera") == "MARCA", b1
    assert b2.get("bandera") == "MARCA", b2
    fuga = [m for m in b1.get("marcas", [])
            if m.get("tipo") == "FUGA_EN_PREGUNTA"
            and (m.get("evidencia") or {}).get("origen") == "question"]
    assert fuga, b1.get("marcas")
    # El fragmento de FUGA_EN_PREGUNTA no es la pregunta entera: son los tramos
    # que casaron las regex (premisa | onset | desenlace), unidos con " | ".
    frag = str(fuga[0].get("evidencia", {}).get("fragmento", ""))
    assert "Dado que" in frag and "desde cuándo" in frag, frag
    ph = [m for m in b1.get("marcas", []) if m.get("tipo") == "POST_HOC_TEMPORAL"]
    assert ph, b1.get("marcas")
    af = [m for m in b2.get("marcas", []) if m.get("tipo") == "AF_AFIRMAR_CONSECUENTE"]
    assert af, b2.get("marcas")
    # H intacto: los guardianes solo marcan, no reescriben predictor ni H
    v = g.get("verificacion_H_intacto") or {}
    assert v.get("predictor_igual") is True and v.get("H1_H2_igual") is True
    assert v.get("patterns_igual") is True
    # el recibo de componentes lo registra como ejecutado, sin poder de decisión
    comp = next((s for s in (res.get("execution") or {}).get("component_status") or []
                 if s.get("component") == "guardianes_control_v1.py"), None)
    assert comp is not None and comp.get("status") == "EXECUTED"
    assert comp.get("can_decide_H") is False
    assert comp.get("dirigida_modo") == "activo"
    assert (comp.get("banderas") or {}).get("PREGUNTA_DIRIGIDA_POST_HOC") == "MARCA"
    assert (comp.get("banderas") or {}).get("FALACIAS") == "MARCA"


def test_retencion_cierre_no_resuelto_dirigida():
    """Un NO_RESUELTO de estos bloques retiene el cierre (ruta_cierre_latente).
    Mecanismo: hoy los bloques reales nunca emiten NO_RESUELTO (ver el test
    siguiente); si alguna vez lo hicieran, la ruta lo retendría como a Copi."""
    spec = importlib.util.spec_from_file_location("guardianes_control_v1", CONTROL)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    bloques = [
        {"guardian": "LOGICA_COPI", "bandera": "LIMPIO", "marcas": []},
        {"guardian": "PREGUNTA_DIRIGIDA_POST_HOC", "bandera": "NO_RESUELTO", "marcas": [
            {"tipo": "POST_HOC_TEMPORAL", "estado": "NO_RESUELTO",
             "evidencia": {"origen": "texto_prueba_post_hoc", "fragmento": POST_HOC_TEXTO}}]},
        {"guardian": "FALACIAS", "bandera": "NO_RESUELTO", "marcas": [
            {"tipo": "AF_AFIRMAR_CONSECUENTE", "estado": "NO_RESUELTO",
             "evidencia": {"origen": "texto_prueba_falacia", "fragmento": AF_TEXTO}}]},
    ]
    ruta = mod.ruta_cierre_latente(bloques, {"case_id": "TEST_DIRIGIDA_RETENCION"},
                                   {"cuts": []}, {}, MOTOR_DIR)
    assert ruta.get("estado_cierre") == "LATENTE", ruta
    assert "PREGUNTA_DIRIGIDA_POST_HOC" in (ruta.get("guardianes_que_objetan") or []), ruta
    assert "FALACIAS" in (ruta.get("guardianes_que_objetan") or []), ruta
    assert ruta.get("can_decide_H") is False


def test_bloques_nunca_emiten_no_resuelto():
    """Comportamiento real: g_dirigida_y_falacias solo emite MARCA o LIMPIO.
    Estos bloques son marcadores puros y no retienen el cierre por sí mismos."""
    spec = importlib.util.spec_from_file_location("guardianes_control_v1", CONTROL)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    textos = [
        {"origen": "question", "texto": PO_PREGUNTA},
        {"origen": "texto_prueba_post_hoc", "texto": POST_HOC_TEXTO},
        {"origen": "texto_prueba_falacia", "texto": AF_TEXTO + " " + CS_TEXTO},
        {"origen": "texto_factico", "texto": TEXTO_FACTICO},
    ]
    b1, b2 = mod.g_dirigida_y_falacias(MOTOR_DIR, PO_PREGUNTA, textos)
    assert b1["guardian"] == "PREGUNTA_DIRIGIDA_POST_HOC"
    assert b2["guardian"] == "FALACIAS"
    assert b1["bandera"] == "MARCA" and b2["bandera"] == "MARCA"
    for b in (b1, b2):
        assert b["bandera"] in ("MARCA", "LIMPIO"), b
        assert all(m.get("estado") in ("DETECTADA", "POSIBLE") for m in b["marcas"]), b
        assert b["can_decide_H"] is False


def test_bypass_dirigida_off_queda_marcado_no_configurado(tmp_path):
    entrada = _fixture_dirigida(tmp_path)
    out = tmp_path / "resultado_dirigida_off.json"
    res = _corre_estandar(entrada, "DIRIGIDA_BYPASS", out, {"PREGUNTA_DIRIGIDA_GUARDIAN": "off"})
    g = res.get("guardianes") or {}
    for nombre in ("PREGUNTA_DIRIGIDA_POST_HOC", "FALACIAS"):
        bloque = _bloque(res, nombre)
        assert bloque is not None, "el bypass no debe borrar el bloque en silencio"
        assert bloque.get("bandera") == "NO_CONFIGURADO", bloque
        assert not [m for m in bloque.get("marcas", []) if m.get("estado") == "DETECTADA"]
    comp = next((s for s in (res.get("execution") or {}).get("component_status") or []
                 if s.get("component") == "guardianes_control_v1.py"), None)
    assert comp is not None and comp.get("dirigida_modo") == "off"
    assert (comp.get("banderas") or {}).get("PREGUNTA_DIRIGIDA_POST_HOC") == "NO_CONFIGURADO"
    assert (comp.get("banderas") or {}).get("FALACIAS") == "NO_CONFIGURADO"
