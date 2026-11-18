#!/usr/bin/env python3
"""test_cableado_polaridad_causal.py — Polaridad causal cableada en la ruta real
de corrida (post-predictor).

Specs: MAPA_GUARDIANES.md §2.5 + orquestador-central
docs/filtros_operativos/INVENTARIO_GUARDIANES_PROTOCOLO.md (fila "Polaridad
causal": FIEL al canon estrecho que declara; sorteble porque la detección es
frase fija). Polaridad NO tiene ficha propia en filtros_operativos (README del
apartado: "piezas hermanas que no tienen ficha propia aquí (..., polaridad,
...)"), así que la spec es el MAPA §2.5 + el inventario + el docstring del
plugin (v1.0.0-cierre-20260920, canon de cierre 2026-09-20).
Contrato de la familia: el bloque corre DESPUÉS del predictor, solo MARCA
(can_decide_H=False), y una DOBLE_NEGACION_LITOTE retiene el cierre vía
ruta_cierre_latente sin decidir H ni tocar patterns. El plugin también lo usan
el décimo hombre (control_latencia_decimo_hombre.polaridad_con_latencia),
el protocolo kernel y pregunta dirigida (que delega causalidad_negada en él).

Capas de este archivo (en orden):
  1) Neutral, fuera de U6: clasificar_polaridad_causal se prueba cargando el
     plugin por ruta explícita, sin importar el motor.
  2) Estático: el cableado existe en UNICO run() y en correr_guardianes.
  3) Vivo (subproceso correr_estandar.py): en una corrida real el bloque
     ejecuta y marca (NIEGA + DOBLE_NEGACION_LITOTE), bandera LATENTE, H
     intacta, y la lítote retiene el cierre (POLARIDAD_CAUSAL objeta).
  4) Unidad: g_polaridad devuelve LATENTE / MARCA / LIMPIO según las marcas,
     y ruta_cierre_latente retiene el cierre por una lítote de polaridad.
  5) Bypass (subproceso con POLARIDAD_GUARDIAN=off): el apagado queda
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
POLARIDAD = MOTOR_DIR / "plugin_polaridad_causal.py"
UNICO = MOTOR_DIR / "MOTOR_V15_3_UNICO_20260927.py"
CONTROL = MOTOR_DIR / "guardianes_control_v1.py"
THEMISTOCLES = ROOT / "inputs" / "THEMISTOCLES_FREEZE_480BC_CATALOG_REPAIR_R2.json"

# Sondas verificadas por ejecución directa del plugin (2026-11-17).
NIEGA_TEXTO = "No explica el resultado."
NIEGA_TEXTO_2 = "Eso no causó el conflicto."
NIEGA_POR_ESO = "No por eso se derrumbó."
NIEGA_NUNCA = "Nunca provocó el cambio."
NIEGA_SIN_QUE = "Sin que explique el motivo, no hay caso."
NIEGA_DEMUESTRA = "Eso no demuestra nada."
LITOTE_TEXTO = "No es que no explica el resultado."
LITOTE_TEXTO_2 = "Tampoco es que no explique nada."
LITOTE_TEXTO_3 = "No es que A no explique B; de hecho lo aclara."
NEUTRO_AFIRMA = "Explica el resultado."
NEUTRO_POR_ESO = "A ocurrió. Por eso B."
NEUTRO_DEMOSTRO = "El comité demostró que la medida funciona."
TEXTO_FACTICO = "El agua hierve a 100 grados al nivel del mar."
TEXTO_HORA = "La reunión es el martes a las diez."
NEGACION_SIN_VERBO_CAUSAL = "No llovió ayer."
LITOTE_SIN_VERBO_CAUSAL = "No es que no llueva."


def _load_polaridad():
    spec = importlib.util.spec_from_file_location("plugin_polaridad_causal", POLARIDAD)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


# ------------------------------------------------------------------ 1) neutral, fuera de U6
def test_niega_simple_marca_y_apaga_post_hoc():
    m = _load_polaridad()
    for texto in (NIEGA_TEXTO, NIEGA_TEXTO_2, NIEGA_POR_ESO, NIEGA_NUNCA,
                  NIEGA_SIN_QUE, NIEGA_DEMUESTRA):
        r = m.clasificar_polaridad_causal(texto)
        assert r["etiqueta"] == "NIEGA", (texto, r)
        assert r["causalidad_negada_simple"] is True, (texto, r)
        # La negación simple es justo el caso en que post hoc NO debe disparar.
        assert r["post_hoc_puede_marcar"] is False, (texto, r)
        assert r["solo_marca"] is True and r["Alimenta_H"] == "NO"


def test_litote_no_es_negacion_simple_y_no_apaga_post_hoc():
    m = _load_polaridad()
    for texto in (LITOTE_TEXTO, LITOTE_TEXTO_2, LITOTE_TEXTO_3):
        r = m.clasificar_polaridad_causal(texto)
        assert r["etiqueta"] == "DOBLE_NEGACION_LITOTE", (texto, r)
        assert r["causalidad_negada_simple"] is False, (texto, r)
        # La lítote no se trata como negación simple: no apaga post hoc por error.
        assert r["post_hoc_puede_marcar"] is True, (texto, r)
        assert r.get("candado") == "CERRADO_NO_REABRIR_COMO_HUECO_MOTOR", r


def test_causalidad_negada_simple_solo_niega():
    m = _load_polaridad()
    assert m.causalidad_negada_simple(NIEGA_TEXTO) is True
    assert m.causalidad_negada_simple(LITOTE_TEXTO) is False
    assert m.causalidad_negada_simple(NEUTRO_AFIRMA) is False
    assert m.causalidad_negada_simple("") is False
    # Alias de compatibilidad con el nombre viejo del plugin pregunta.
    assert m.causalidad_negada(NIEGA_TEXTO) is True
    assert m.causalidad_negada(LITOTE_TEXTO) is False


def test_neutro_no_marca():
    m = _load_polaridad()
    for texto in (NEUTRO_AFIRMA, NEUTRO_POR_ESO, NEUTRO_DEMOSTRO, TEXTO_FACTICO,
                  TEXTO_HORA, NEGACION_SIN_VERBO_CAUSAL, ""):
        r = m.clasificar_polaridad_causal(texto)
        assert r["etiqueta"] == "NEUTRO", (texto, r)
        assert r["causalidad_negada_simple"] is False
        assert r["post_hoc_puede_marcar"] is True
    assert m.clasificar_polaridad_causal("")["motivo"] == "vacio"


def test_afirma_implicita_declarada_pero_nunca_devuelta():
    # Desfase docstring vs código (reportado, no corregido): el docstring de
    # clasificar_polaridad_causal lista NEUTRO | AFIRMA_IMPLICITA | NIEGA |
    # DOBLE_NEGACION_LITOTE, pero el código solo devuelve NEUTRO, NIEGA y
    # DOBLE_NEGACION_LITOTE. Un claim causal afirmativo sale NEUTRO.
    m = _load_polaridad()
    assert m.clasificar_polaridad_causal(NEUTRO_AFIRMA)["etiqueta"] == "NEUTRO"
    assert m.clasificar_polaridad_causal(NEUTRO_DEMOSTRO)["etiqueta"] == "NEUTRO"


def test_limite_litote_sin_verbo_causal():
    # Límite documentado del adaptador, no un fallo del test: las dos primeras
    # alternativas de _RX_DOBLE ("no es que no", "tampoco es que no") no exigen
    # verbo causal, así que una lítote sin verbo causal también marca
    # DOBLE_NEGACION_LITOTE. Es la misma detección por frase fija que el
    # inventario califica de sorteble.
    m = _load_polaridad()
    r = m.clasificar_polaridad_causal(LITOTE_SIN_VERBO_CAUSAL)
    assert r["etiqueta"] == "DOBLE_NEGACION_LITOTE", r
    assert m.clasificar_polaridad_causal("No es que no me guste.")["etiqueta"] == "DOBLE_NEGACION_LITOTE"


def test_solo_marca_nunca_decide():
    m = _load_polaridad()
    assert m.SOLO_MARCA is True
    assert m.ALIMENTA_H == "NO" and m.TOCA_ENGINE == "NO"
    assert m.TOCA_244 == "NO" and m.TOCA_FREEZE == "NO"
    for texto in (NIEGA_TEXTO, LITOTE_TEXTO, NEUTRO_AFIRMA):
        r = m.clasificar_polaridad_causal(texto)
        assert r["solo_marca"] is True and r["Alimenta_H"] == "NO"
        assert "H1" not in r and "H2" not in r


# ------------------------------------------------------------------ 2) estático: el cableado existe
def test_cableado_presente_en_runner_y_control():
    src = UNICO.read_text(encoding="utf-8")
    assert 'gmod.correr_guardianes' in src
    assert 'result["guardianes"]=guard_out' in src
    assert 'POLARIDAD_GUARDIAN' in src
    # Tras fusionar, el omitir es la unión de los conjuntos; lo que importa
    # es que _polaridad_omitir llegue a correr_guardianes.
    _lineas_guardianes = [ln for ln in src.splitlines() if "correr_guardianes" in ln and "omitir=" in ln]
    assert _lineas_guardianes and "_polaridad_omitir" in _lineas_guardianes[0]
    assert '"polaridad_modo":_polaridad_modo' in src
    ctrl = CONTROL.read_text(encoding="utf-8")
    assert 'def correr_guardianes(' in ctrl and 'omitir=frozenset()' in ctrl
    assert '"POLARIDAD_CAUSAL" in omitir' in ctrl
    assert '"NO_CONFIGURADO"' in ctrl
    assert 'seguro("POLARIDAD_CAUSAL"' in ctrl


# ------------------------------------------------------------------ 3, 4 y 5) vivo: corrida real por subproceso
def _fixture_polaridad(tmp_path):
    d = json.loads(THEMISTOCLES.read_text(encoding="utf-8"))
    d["texto_prueba_niega"] = NIEGA_TEXTO
    d["texto_prueba_litote"] = LITOTE_TEXTO
    p = tmp_path / "caso_polaridad.json"
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
    env.pop("POLARIDAD_GUARDIAN", None)
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


def test_corrida_real_ejecuta_polaridad(tmp_path):
    entrada = _fixture_polaridad(tmp_path)
    out = tmp_path / "resultado_polaridad.json"
    res = _corre_estandar(entrada, "POLARIDAD_SMOKE", out)
    g = res.get("guardianes") or {}
    assert g.get("status") == "EXECUTED"
    assert g.get("can_decide_H") is False
    b = _bloque(res, "POLARIDAD_CAUSAL")
    assert b is not None, "sin bloque POLARIDAD_CAUSAL en una corrida real"
    assert b.get("can_decide_H") is False
    # Hay lítote en los textos: la bandera es LATENTE (no MARCA).
    assert b.get("bandera") == "LATENTE", b
    marcas = b.get("marcas") or []
    niega = [x for x in marcas if x.get("tipo") == "NIEGA"
             and (x.get("evidencia") or {}).get("origen") == "texto_prueba_niega"]
    assert niega and niega[0].get("estado") == "DETECTADA", marcas
    litote = [x for x in marcas if x.get("tipo") == "DOBLE_NEGACION_LITOTE"
              and (x.get("evidencia") or {}).get("origen") == "texto_prueba_litote"]
    assert litote and litote[0].get("estado") == "LATENTE", marcas
    assert (b.get("detalle") or {}).get("conteo", {}).get("DOBLE_NEGACION_LITOTE", 0) >= 1
    assert (b.get("detalle") or {}).get("conteo", {}).get("NIEGA", 0) >= 1
    # H intacto: los guardianes solo marcan, no reescriben predictor ni H
    v = g.get("verificacion_H_intacto") or {}
    assert v.get("predictor_igual") is True and v.get("H1_H2_igual") is True
    assert v.get("patterns_igual") is True
    assert (res.get("H1") or {}).get("family") == "arquetipo_el_gobernante"
    assert (res.get("H2") or {}).get("family") == "13_enemistad_de_parientes"
    # La lítote retiene el cierre: POLARIDAD_CAUSAL objeta en la ruta latente.
    # (El resultado no trae "cierre" en el nivel superior: el estado vive en
    # guardianes.ruta_cierre_latente y el registro de UNICO en cierre_guardianes.)
    ruta = g.get("ruta_cierre_latente") or {}
    assert ruta.get("estado_cierre") == "LATENTE", ruta
    assert "POLARIDAD_CAUSAL" in (ruta.get("guardianes_que_objetan") or []), ruta
    motivos_pol = [x for x in ruta.get("motivos", [])
                   if x.get("guardian") == "POLARIDAD_CAUSAL"
                   and x.get("tipo") == "DOBLE_NEGACION_LITOTE"]
    assert motivos_pol, ruta.get("motivos")
    cg = res.get("cierre_guardianes") or {}
    assert "POLARIDAD_CAUSAL" in (cg.get("guardianes_que_objetan") or []), cg
    assert [x for x in cg.get("motivos", [])
            if x.get("guardian") == "POLARIDAD_CAUSAL"
            and x.get("tipo") == "DOBLE_NEGACION_LITOTE"], cg.get("motivos")
    # el recibo de componentes lo registra como ejecutado, sin poder de decisión
    comp = next((s for s in (res.get("execution") or {}).get("component_status") or []
                 if s.get("component") == "guardianes_control_v1.py"), None)
    assert comp is not None and comp.get("status") == "EXECUTED"
    assert comp.get("can_decide_H") is False
    assert comp.get("polaridad_modo") == "activo"
    assert (comp.get("banderas") or {}).get("POLARIDAD_CAUSAL") == "LATENTE"


def test_unidad_g_polaridad_banderas():
    spec = importlib.util.spec_from_file_location("guardianes_control_v1", CONTROL)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    b = mod.g_polaridad(MOTOR_DIR, [{"origen": "t1", "texto": NIEGA_TEXTO}])
    assert b["guardian"] == "POLARIDAD_CAUSAL"
    assert b["bandera"] == "MARCA", b
    assert b["can_decide_H"] is False
    b = mod.g_polaridad(MOTOR_DIR, [{"origen": "t1", "texto": LITOTE_TEXTO}])
    assert b["bandera"] == "LATENTE", b
    b = mod.g_polaridad(MOTOR_DIR, [{"origen": "t1", "texto": NEUTRO_AFIRMA},
                                    {"origen": "t2", "texto": TEXTO_FACTICO}])
    assert b["bandera"] == "LIMPIO" and b["n_marcas"] == 0, b
    b = mod.g_polaridad(MOTOR_DIR, [{"origen": "t1", "texto": NIEGA_TEXTO},
                                    {"origen": "t2", "texto": LITOTE_TEXTO}])
    assert b["bandera"] == "LATENTE" and b["n_marcas"] == 2, b
    assert (b.get("detalle") or {}).get("conteo") == {"NIEGA": 1, "DOBLE_NEGACION_LITOTE": 1}, b


def test_retencion_cierre_litote_polaridad():
    """Una DOBLE_NEGACION_LITOTE de polaridad retiene el cierre
    (ruta_cierre_latente). Mecanismo: la lítote no es NO_RESUELTO, pero la
    ruta la recoge por tipo en cualquier guardián."""
    spec = importlib.util.spec_from_file_location("guardianes_control_v1", CONTROL)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    bloques = [
        {"guardian": "LOGICA_COPI", "bandera": "LIMPIO", "marcas": []},
        {"guardian": "POLARIDAD_CAUSAL", "bandera": "LATENTE", "marcas": [
            {"tipo": "DOBLE_NEGACION_LITOTE", "estado": "LATENTE",
             "evidencia": {"origen": "texto_prueba_litote", "texto": LITOTE_TEXTO,
                           "motivo": "litote/doble_negacion_no_es_negacion_simple"}}]},
    ]
    ruta = mod.ruta_cierre_latente(bloques, {"case_id": "TEST_POLARIDAD_RETENCION"},
                                   {"cuts": []}, {}, MOTOR_DIR)
    assert ruta.get("estado_cierre") == "LATENTE", ruta
    assert "POLARIDAD_CAUSAL" in (ruta.get("guardianes_que_objetan") or []), ruta
    assert ruta.get("can_decide_H") is False
    # Sin lítote ni NO_RESUELTO, la ruta no objeta.
    ruta2 = mod.ruta_cierre_latente(
        [{"guardian": "POLARIDAD_CAUSAL", "bandera": "MARCA", "marcas": [
            {"tipo": "NIEGA", "estado": "DETECTADA",
             "evidencia": {"origen": "texto_prueba_niega", "texto": NIEGA_TEXTO}}]}],
        {"case_id": "TEST_POLARIDAD_SIN_RETENCION"}, {"cuts": []}, {}, MOTOR_DIR)
    assert ruta2.get("estado_cierre") == "SIN_OBJECION_DE_GUARDIANES", ruta2
    assert "POLARIDAD_CAUSAL" not in (ruta2.get("guardianes_que_objetan") or []), ruta2


def test_bypass_polaridad_off_queda_marcado_no_configurado(tmp_path):
    entrada = _fixture_polaridad(tmp_path)
    out = tmp_path / "resultado_polaridad_off.json"
    res = _corre_estandar(entrada, "POLARIDAD_BYPASS", out, {"POLARIDAD_GUARDIAN": "off"})
    g = res.get("guardianes") or {}
    bloque = _bloque(res, "POLARIDAD_CAUSAL")
    assert bloque is not None, "el bypass no debe borrar el bloque en silencio"
    assert bloque.get("bandera") == "NO_CONFIGURADO", bloque
    assert not [m for m in bloque.get("marcas", []) if m.get("estado") == "DETECTADA"]
    comp = next((s for s in (res.get("execution") or {}).get("component_status") or []
                 if s.get("component") == "guardianes_control_v1.py"), None)
    assert comp is not None and comp.get("polaridad_modo") == "off"
    assert (comp.get("banderas") or {}).get("POLARIDAD_CAUSAL") == "NO_CONFIGURADO"
    # El resto de guardianes sigue corriendo con el bypass de polaridad.
    assert _bloque(res, "LOGICA_COPI") is not None
