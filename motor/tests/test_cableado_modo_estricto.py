#!/usr/bin/env python3
"""test_cableado_modo_estricto.py — Modo estricto cableado en la ruta real
de corrida (post-guardianes, en run() de UNICO).

Specs: MAPA_GUARDIANES.md §2.8 (`modo_estricto_v1.py`: cierre estricto
C0–C4, mapeo en negativo Ricci–Forman vs Billar, bloque rival/'qué
ignoré') + inventario de orquestador-central
(`docs/filtros_operativos/INVENTARIO_GUARDIANES_PROTOCOLO.md` v1.1, fila
"Modo estricto": C0–C4 deben cumplirse o el cierre estricto queda
`LATENTE`; no toca H; se apaga con `MODO_ESTRICTO=0`, por defecto on;
regla del inventario: un código no se da por cableado si su apagado por
variable de entorno lo deja en silencio) + docstring del plugin
(`MODO_ESTRICTO_V1_20260927`, lateral, `can_decide_H=False`). No tiene
ficha propia en filtros_operativos.

Hallazgo del cableado: el bloque YA se ejecutaba en la ruta real sin
ninguna prueba (baseline THEMISTOCLES: EXECUTED, LATENTE por C0+C1, H
intacta), pero con `MODO_ESTRICTO=0` desaparecía en silencio: ni
`result["modo_estricto"]`, ni `result["estado_cierre_estricto"]`, ni fila
de componentes. Este PR no reescribe el núcleo: añade la rama `else`
que deja el apagado marcado `NO_CONFIGURADO` (con `estricto_modo: off`)
y registra `estricto_modo` en la fila de componentes en ambos casos.
SHA esperado del plugin (`9143a098…`) coincide con el archivo actual.
(V7: el docstring corrigió la referencia obsoleta al runner; SHA anterior
`c0fe7fbd…`.)

Contrato de la familia: el bloque corre DESPUÉS del predictor y de los
guardianes, solo RETIENE el estado de cierre estricto
(`can_decide_H=False`); nunca escribe H ni patterns. Su `LATENTE`
(C0–C4) llega a `cierre_final` (016) como objeciones con fuente
`modo_estricto` (C1/C2/C4 directas; C3 solo si subdeterminado o décimo
hombre en banda de empate). El bypass (`MODO_ESTRICTO=0`) no debe
inventar objeciones: su registro trae `motivos: []`.

Capas de este archivo (en orden):
  1) Neutral, fuera de U6: evaluar() directo con motor/pred sintéticos
     (todo pasa → CIERRE_ESTRICTO; cada criterio C0/C1/C2/C3 que falla
     → LATENTE con su motivo; Aquiles estable y NO_DISPONIBLE sin H;
     negativo Ricci vs Billar y rival/'qué ignoré' directos;
     constantes y contrato).
  2) Estático: el cableado existe en UNICO run() (flag, rama else con
     NO_CONFIGURADO, estricto_modo en la fila, claves de recibo).
  3) Vivo (subproceso correr_estandar.py): en una corrida real el bloque
     ejecuta (EXECUTED, LATENTE por C0+C1), H intacta, y el cierre final
     recoge la objeción C1 del modo estricto.
  4) Unidad: el LATENTE estricto retiene como objeción en
     _cierre_final_016; el CIERRE_ESTRICTO no retiene (FIRME con acero
     que descarta); el NO_CONFIGURADO no inventa objeciones.
  5) Bypass (subproceso con MODO_ESTRICTO=0): el apagado queda marcado
     NO_CONFIGURADO en el recibo, no pasa en silencio ni inventa
     objeciones, y el resto de guardianes sigue corriendo.

Límite documentado (del módulo, no del test): Aquiles hace bootstrap
hasta parar, así que C4=False no se alcanza con datos sintéticos de 3
cortes (el remuestreo se estabiliza por construcción); C4 solo falla
vía NO_DISPONIBLE (sin H / sin plugin) o fusible. Por eso no hay un
caso sintético C4-falso en la capa 1; C4 se prueba en sano (ok) y en
vivo (ok en THEMISTOCLES).
"""
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # motor/
MOTOR_DIR = ROOT / "motor"
ESTRICTO = MOTOR_DIR / "modo_estricto_v1.py"
UNICO = MOTOR_DIR / "MOTOR_V15_3_UNICO_20260927.py"
THEMISTOCLES = ROOT / "inputs" / "THEMISTOCLES_FREEZE_480BC_CATALOG_REPAIR_R2.json"

SHA_ESTRICTO = "9143a098"
SHA_ENGINE = "665c39a2"
SHA_PATTERNS = "d827dcc3"


def _load_estricto():
    spec = importlib.util.spec_from_file_location("modo_estricto_v1", ESTRICTO)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _load_unico_func(nombre):
    """Carga solo la función nombrada de UNICO sin ejecutar el módulo."""
    import re
    src = UNICO.read_text(encoding="utf-8")
    inicio = src.index(f"def {nombre}(")
    # _cierre_final_016 termina antes de _aplicar_cierre_final_016
    fin = src.index("def _aplicar_cierre_final_016(", inicio)
    fragmento = src[inicio:fin]
    # _cierre_final_016 usa el deduplicador y la constante de separación.
    d_ini = src.index("def _deduplicar_objeciones_016(")
    d_fin = src.index("def _cierre_final_016(", d_ini)
    separacion = float(re.search(
        r"^GATE_SEPARATION\s*=\s*([0-9.]+)", src, re.M).group(1))
    espacio = {"__name__": "unico_fragmento",
               "GATE_SEPARATION": separacion}
    exec(compile(src[d_ini:d_fin],
                 "UNICO::_deduplicar_objeciones_016", "exec"), espacio)
    exec(compile(fragmento, f"UNICO::{nombre}", "exec"), espacio)
    return espacio[nombre]


def _sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# ------------------------------------------------------------------ builders
def _corte_motor(cid, top, full):
    return {"corte": cid,
            "P_top5_ANEXO": [[top, 0.9], ["SEG", 0.1]],
            "A_top5_ANEXO": [[top, 0.9], ["SEG", 0.1]],
            "C_top5_ANEXO": [[top, 0.9], ["SEG", 0.1]],
            "P_FULL_244": dict(full), "A_FULL_244": dict(full),
            "C_FULL_244": dict(full),
            "P_candidatos_0a3": [{"familia": top}, {"familia": "SEG"}]}


def _corte_caso(cid):
    return {"id": cid, "P": [["tok_top", 1]], "A": [], "C": []}


def _sano():
    """3 cortes sanos: TOP encabeza todos, acero SOBREVIVE, H1≠H2."""
    full = {"TOP": 0.9, "SEG": 0.1, "TER": 0.05}
    motor = {"cuts": [_corte_motor("C1", "TOP", full),
                      _corte_motor("C2", "TOP", full),
                      _corte_motor("C3", "TOP", full)]}
    case = {"case_id": "TEST_ME_SANO",
            "cuts": [_corte_caso("C1"), _corte_caso("C2"), _corte_caso("C3")]}
    pred = {"candidates": [
        {"family": "TOP", "rank_fusion": 10.0,
         "features": {"d1": 0.9, "d2": 0.8}},
        {"family": "SEG", "rank_fusion": 1.0,
         "features": {"d1": 0.1, "d2": 0.2}},
        {"family": "TER", "rank_fusion": 0.5,
         "features": {"d1": 0.05, "d2": 0.1}}],
        "information_state": {"state": "DETERMINADO"}}
    acero = {"guardian": "HOMBRE_DE_ACERO", "detalle": {"steelman_rival": {
        "pruebas": [{"rival": "SEG", "dif_base": 9.0, "dif_acero": 5.0,
                     "veredicto_top1": "SOBREVIVE"}]}}}
    rv = {"H1": {"family": "TOP"}, "H2": {"family": "SEG"},
          "features": {"billar_circular_v0_2": {"N_real_v0_2": 0},
                       "ricci_forman_v0_1": {"media_Ric": 0.0}},
          "guardianes": {"bloques": [acero]},
          "cierre_guardianes": {}, "estado_cierre": {"valor": "DETERMINADO"}}
    return case, motor, pred, rv


# ------------------------------------------------------------------ 1) neutral, fuera de U6
def test_evaluar_todo_pasa_cierre_estricto():
    me = _load_estricto()
    case, motor, pred, rv = _sano()
    out = me.evaluar(case, motor, pred, rv, MOTOR_DIR)
    assert out.get("estado_cierre_estricto") == "CIERRE_ESTRICTO", out
    assert out.get("motivos") == [], out
    crit = out.get("criterios") or {}
    assert {k: v.get("ok") for k, v in crit.items()} == {
        "C0_ruta_vigente_no_latente": True,
        "C1_top1_encabeza_un_corte": True,
        "C2_rival_mas_fuerte_descartado_por_acero": True,
        "C3_H1_H2_distinguibles": True,
        "C4_aquiles_estable": True}, crit
    assert out.get("can_decide_H") is False
    assert out.get("escribe_H") is False
    assert out.get("reordena_candidatos") is False
    assert out.get("escribe_patterns") is False
    assert out.get("version") == "MODO_ESTRICTO_V1_20260927"
    assert (out.get("aquiles") or {}).get("estable") is True
    assert (out.get("negativo_ricci_vs_billar") or {}).get("status") == "EJECUTADO"
    assert (out.get("rival_que_ignore") or {}).get("status") == "EJECUTADO"


def test_evaluar_c0_latente_retiene():
    me = _load_estricto()
    case, motor, pred, rv = _sano()
    rv["estado_cierre"] = {"valor": "LATENTE"}
    out = me.evaluar(case, motor, pred, rv, MOTOR_DIR)
    assert out.get("estado_cierre_estricto") == "LATENTE", out
    assert (out.get("criterios") or {}).get(
        "C0_ruta_vigente_no_latente", {}).get("ok") is False
    assert any(m.startswith("C0:") for m in out.get("motivos") or []), out
    assert (out.get("criterios") or {}).get(
        "C1_top1_encabeza_un_corte", {}).get("ok") is True


def test_evaluar_c1_top1_no_encabeza():
    me = _load_estricto()
    case, motor, pred, rv = _sano()
    full = {"TOP": 0.1, "SEG": 0.9, "TER": 0.05}
    motor["cuts"] = [_corte_motor("C1", "SEG", full),
                     _corte_motor("C2", "SEG", full),
                     _corte_motor("C3", "SEG", full)]
    out = me.evaluar(case, motor, pred, rv, MOTOR_DIR)
    assert out.get("estado_cierre_estricto") == "LATENTE", out
    assert (out.get("criterios") or {}).get(
        "C1_top1_encabeza_un_corte", {}).get("ok") is False
    assert any(m.startswith("C1:") for m in out.get("motivos") or []), out
    assert "SEG, SEG, SEG" in (out.get("motivos") or [""])[0], out


def test_evaluar_c2_sin_steelman():
    me = _load_estricto()
    case, motor, pred, rv = _sano()
    rv["guardianes"] = {"bloques": []}
    out = me.evaluar(case, motor, pred, rv, MOTOR_DIR)
    assert out.get("estado_cierre_estricto") == "LATENTE", out
    assert (out.get("criterios") or {}).get(
        "C2_rival_mas_fuerte_descartado_por_acero", {}).get("ok") is False
    assert any("steelman del rival no disponible" in m
               for m in out.get("motivos") or []), out


def test_evaluar_c2_acero_cae():
    me = _load_estricto()
    case, motor, pred, rv = _sano()
    prueba = rv["guardianes"]["bloques"][0]["detalle"]["steelman_rival"]["pruebas"][0]
    prueba["veredicto_top1"] = "CAE"
    prueba["dif_acero"] = -1.0
    out = me.evaluar(case, motor, pred, rv, MOTOR_DIR)
    assert out.get("estado_cierre_estricto") == "LATENTE", out
    assert (out.get("criterios") or {}).get(
        "C2_rival_mas_fuerte_descartado_por_acero", {}).get("ok") is False
    assert any("no descarta al rival más fuerte SEG" in m
               for m in out.get("motivos") or []), out


def test_evaluar_c3_h1_h2_no_distinguibles():
    me = _load_estricto()
    case, motor, pred, rv = _sano()
    rv["H2"] = {"family": "TOP"}
    out = me.evaluar(case, motor, pred, rv, MOTOR_DIR)
    assert out.get("estado_cierre_estricto") == "LATENTE", out
    assert (out.get("criterios") or {}).get(
        "C3_H1_H2_distinguibles", {}).get("ok") is False
    assert any("H1=H2" in m for m in out.get("motivos") or []), out


def test_aquiles_estable_directo_y_no_disponible_sin_h():
    me = _load_estricto()
    _, motor, pred, _ = _sano()
    aq = me.aquiles(MOTOR_DIR, motor, pred, "TOP")
    assert aq.get("status") == "EJECUTADO", aq
    assert aq.get("estable") is True, aq
    assert aq.get("estado_H") == "PARA_DE_EMPUJAR_H", aq
    assert aq.get("ganador_remuestreo_es_H") is True, aq
    assert me.aquiles(MOTOR_DIR, motor, pred, None).get("status") == "NO_DISPONIBLE"


def test_negativo_ricci_billar_directo():
    me = _load_estricto()
    case, motor, pred, rv = _sano()
    neg = me.negativo_ricci_billar(MOTOR_DIR, motor, pred, rv, "TEST_ME")
    assert neg.get("status") == "EJECUTADO", neg
    assert neg.get("can_decide_H") is False
    assert neg.get("version") == "NEGATIVO_RICCI_VS_BILLAR_EN_MODO_ESTRICTO_V1"
    assert neg.get("alimenta") == "convergencia (lateral); no gatea el cierre"


def test_rival_que_ignore_directo():
    me = _load_estricto()
    case, motor, pred, _ = _sano()
    riv = me.rival_que_ignore(MOTOR_DIR, case, pred)
    assert riv.get("status") == "EJECUTADO", riv
    assert riv.get("top1") == "TOP", riv
    assert [r.get("rival") for r in riv.get("rivales") or []] == ["SEG", "TER"], riv
    assert riv.get("can_decide_H") is False
    primero = (riv.get("rivales") or [{}])[0]
    assert primero.get("gap_rank_fusion") == 9.0, primero
    assert "recuperar 9.000 de rank_fusion" in (
        (primero.get("para_que_gane_tendria_que_ser_cierto") or {}).get("texto") or "")


def test_constantes_y_sha_del_plugin():
    me = _load_estricto()
    assert me.VERSION == "MODO_ESTRICTO_V1_20260927"
    assert me.EPS_ACERO == 0.25
    assert me.SEP_B9 == 1.0
    assert _sha256(ESTRICTO).startswith(SHA_ESTRICTO)
    assert _sha256(MOTOR_DIR / "Engine_V5_CANONICO_SOLO.py").startswith(SHA_ENGINE)
    assert _sha256(MOTOR_DIR / "patterns_final_v14.json").startswith(SHA_PATTERNS)


# ------------------------------------------------------------------ 2) estático: el cableado existe
def test_estatico_cableado_en_unico():
    src = UNICO.read_text(encoding="utf-8")
    assert 'result["modo_estricto"]' in src
    assert 'result["estado_cierre_estricto"]' in src
    assert 'MODO_ESTRICTO' in src
    assert '"estricto_modo"' in src
    # La rama else del apagado: NO_CONFIGURADO visible, no silencio.
    inicio = src.index("# MODO ESTRICTO")
    fin = src.index("# UNICO: HUB post-predictor", inicio)
    seccion = src[inicio:fin]
    assert '"NO_CONFIGURADO"' in seccion, seccion
    assert 'apagado por MODO_ESTRICTO=0' in seccion, seccion
    assert '"estricto_modo"' in seccion, seccion
    assert '_estricto_modo' in seccion, seccion


# ------------------------------------------------------------------ 3 y 5) vivo y bypass por subproceso
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
    env.pop("MODO_ESTRICTO", None)
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


def test_corrida_real_ejecuta_modo_estricto(tmp_path):
    out = tmp_path / "resultado_modo_estricto.json"
    res = _corre_estandar(THEMISTOCLES, "MODO_ESTRICTO_SMOKE", out)
    me = res.get("modo_estricto") or {}
    assert me.get("status") == "EXECUTED", me
    assert me.get("modo") == "activo", me
    assert me.get("version") == "MODO_ESTRICTO_V1_20260927", me
    assert me.get("can_decide_H") is False
    # Baseline THEMISTOCLES: la ruta vigente ya está LATENTE por Copi (C0)
    # y el top1 no encabeza ningún corte (cadena P: sombra, sombra, sombra).
    assert me.get("estado_cierre_estricto") == "LATENTE", me
    crit = me.get("criterios") or {}
    assert {k: v.get("ok") for k, v in crit.items()} == {
        "C0_ruta_vigente_no_latente": False,
        "C1_top1_encabeza_un_corte": False,
        "C2_rival_mas_fuerte_descartado_por_acero": True,
        "C3_H1_H2_distinguibles": True,
        "C4_aquiles_estable": True}, crit
    assert me.get("motivos") == [
        "C0: la ruta vigente ya dejó el cierre LATENTE "
        "(LOGICA_COPI:NO_RESUELTO_TOP1_NO_ES_TOP_DE_NINGUN_CORTE)",
        "C1: arquetipo_el_gobernante no encabeza ningún corte "
        "(cadena P: sombra, sombra, sombra)"], me
    assert (me.get("negativo_ricci_vs_billar") or {}).get("status") == "EJECUTADO"
    assert (me.get("rival_que_ignore") or {}).get("status") == "EJECUTADO"
    # H intacto: el modo estricto solo retiene el estado, no reescribe nada.
    assert (res.get("H1") or {}).get("family") == "arquetipo_el_gobernante"
    assert (res.get("H2") or {}).get("family") == "13_enemistad_de_parientes"
    v = me.get("verificacion_H_intacto") or {}
    assert v.get("predictor_igual") is True and v.get("H1_H2_igual") is True
    assert v.get("top1_igual") is True and v.get("patterns_igual") is True
    # El estado estricto durante la corrida queda en el recibo (016).
    durante = res.get("estado_estricto_durante_corrida") or {}
    assert durante.get("valor") == "LATENTE", durante
    # La fila de componentes lo registra como ejecutado, con el modo visible.
    comp = _componente(res, "modo_estricto_v1.py")
    assert comp is not None and comp.get("status") == "EXECUTED", comp
    assert comp.get("estricto_modo") == "activo", comp
    assert comp.get("can_decide_H") is False
    assert comp.get("estado_cierre_estricto") == "LATENTE", comp
    assert (comp.get("H_intacto") or {}).get("predictor_igual") is True
    # El cierre final recoge la objeción C1 del modo estricto.
    cf = res.get("cierre_final") or {}
    objs = [o for o in cf.get("objeciones") or []
            if o.get("fuente") == "modo_estricto"]
    assert [o.get("criterio") for o in objs] == [
        "C1_top1_encabeza_un_corte"], cf


def test_bypass_modo_estricto_off_queda_marcado_no_configurado(tmp_path):
    out = tmp_path / "resultado_modo_estricto_off.json"
    res = _corre_estandar(THEMISTOCLES, "MODO_ESTRICTO_BYPASS", out,
                          {"MODO_ESTRICTO": "0"})
    me = res.get("modo_estricto")
    assert me is not None, "el bypass no debe borrar el bloque en silencio"
    assert me.get("status") == "NO_CONFIGURADO", me
    assert me.get("modo") == "off", me
    assert me.get("estado_cierre_estricto") == "NO_CONFIGURADO", me
    # Sin motivos: el apagado no debe leerse como objeción en ningún lado.
    assert me.get("motivos") == [], me
    assert me.get("can_decide_H") is False
    durante = res.get("estado_estricto_durante_corrida") or {}
    assert durante.get("valor") == "NO_CONFIGURADO", durante
    comp = _componente(res, "modo_estricto_v1.py")
    assert comp is not None and comp.get("status") == "NO_CONFIGURADO", comp
    assert comp.get("estricto_modo") == "off", comp
    assert comp.get("estado_cierre_estricto") == "NO_CONFIGURADO", comp
    # H intacta e idéntica al baseline; el resto de guardianes sigue corriendo.
    assert (res.get("H1") or {}).get("family") == "arquetipo_el_gobernante"
    assert (res.get("H2") or {}).get("family") == "13_enemistad_de_parientes"
    g = res.get("guardianes") or {}
    assert g.get("status") == "EXECUTED", g
    bloques = {b.get("guardian") for b in g.get("bloques") or []}
    assert "LOGICA_COPI" in bloques, bloques
    assert "DECIMO_HOMBRE_LATENCIA" in bloques, bloques
    # El cierre sigue LATENTE por Copi, y el cierre final no tiene ninguna
    # objeción con fuente modo_estricto: el apagado no inventa objeciones.
    ruta = g.get("ruta_cierre_latente") or {}
    assert ruta.get("estado_cierre") == "LATENTE", ruta
    assert "LOGICA_COPI" in (ruta.get("guardianes_que_objetan") or []), ruta
    cf = res.get("cierre_final") or {}
    assert "modo_estricto" not in [
        o.get("fuente") for o in cf.get("objeciones") or []], cf


# ------------------------------------------------------------------ 4) unidad: retención en cierre_final_016
def _resultado_cierre_final(criterios, motivos, c2_extra=None):
    est = {"estado_cierre_estricto": "LATENTE" if any(
        not (c or {}).get("ok", True) for c in criterios.values()) else "CIERRE_ESTRICTO",
        "criterios": criterios, "motivos": motivos}
    result = {"modo_estricto": est, "cierre_guardianes": {},
              "motor": {"cuts": []}, "guardianes": {}}
    pred = {"candidates": [
        {"family": "TOP", "rank_fusion": 10.0},
        {"family": "SEG", "rank_fusion": 1.0}],
        "information_state": {"state": "DETERMINADO"}}
    return result, pred


def _criterios_base():
    return {
        "C1_top1_encabeza_un_corte": {"ok": True},
        "C2_rival_mas_fuerte_descartado_por_acero": {
            "ok": True, "rival_mas_fuerte": "SEG", "dif_base": 9.0,
            "dif_acero": 5.0, "veredicto_top1": "SOBREVIVE", "EPS": 0.25},
        "C3_H1_H2_distinguibles": {"ok": True, "subdeterminado": False,
                                   "cierre_en_banda_empate": False},
        "C4_aquiles_estable": {"ok": True}}


def test_unidad_cierre_estricto_latente_retiene_como_objecion():
    """Un LATENTE estricto (C1) retiene como objeción en el cierre final:
    el grado ya no puede ser FIRME."""
    fn = _load_unico_func("_cierre_final_016")
    crit = _criterios_base()
    crit["C1_top1_encabeza_un_corte"] = {"ok": False}
    result, pred = _resultado_cierre_final(
        crit, ["C1: TOP no encabeza ningún corte (cadena P: SEG, SEG, SEG)"])
    cf = fn(result, pred)
    objs = [o for o in cf.get("objeciones") or []
            if o.get("fuente") == "modo_estricto"]
    assert [o.get("criterio") for o in objs] == [
        "C1_top1_encabeza_un_corte"], cf
    assert cf.get("grado") != "FIRME", cf


def test_unidad_cierre_estricto_ok_no_retiene():
    """Con los 4 criterios ok y el acero descartando al rival alineado,
    el cierre final es FIRME y no hay objeciones del modo estricto."""
    fn = _load_unico_func("_cierre_final_016")
    result, pred = _resultado_cierre_final(_criterios_base(), [])
    cf = fn(result, pred)
    assert "modo_estricto" not in [
        o.get("fuente") for o in cf.get("objeciones") or []], cf
    assert cf.get("grado") == "FIRME", cf


def test_unidad_modo_no_configurado_no_inventa_objecion():
    """El NO_CONFIGURADO (bypass) no aporta criterios ni motivos: el
    cierre final no debe inventar objeciones con fuente modo_estricto."""
    fn = _load_unico_func("_cierre_final_016")
    result, pred = _resultado_cierre_final({}, [])
    result["modo_estricto"] = {
        "status": "NO_CONFIGURADO", "file": "modo_estricto_v1.py",
        "modo": "off", "estado_cierre_estricto": "NO_CONFIGURADO",
        "motivos": [], "motivo": "apagado por MODO_ESTRICTO=0",
        "can_decide_H": False}
    cf = fn(result, pred)
    assert "modo_estricto" not in [
        o.get("fuente") for o in cf.get("objeciones") or []], cf
    assert cf.get("grado") != "FIRME", cf
