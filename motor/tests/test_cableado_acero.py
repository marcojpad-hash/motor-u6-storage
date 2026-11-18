#!/usr/bin/env python3
"""test_cableado_acero.py — Hombre de acero cableado en la ruta real de corrida
(post-predictor).

Specs: MAPA_GUARDIANES.md §2.6 + orquestador-central
docs/filtros_operativos/INVENTARIO_GUARDIANES_PROTOCOLO.md (fila "Hombre de
acero": ¿el top1 sobrevive a la mejor versión del rival? Marca. Lo usa el modo
estricto, criterio C2). Acero NO tiene ficha propia en filtros_operativos (igual
que Polaridad), así que la spec es el MAPA §2.6 + el inventario + los docstrings
de `guardian_acero_rival_v1.py` v1.0.1 (steelman) y
`sidecar_ablacion_hombre_acero.py` v0.1 (ablación de pilares de H1).
Contrato de la familia: el bloque corre DESPUÉS del predictor, solo MARCA
(can_decide_H=False), y un NO_RESUELTO (empate tras el acero) retiene el cierre
vía ruta_cierre_latente sin decidir H ni tocar patterns. Un CAE (rival que
supera al top1 con su mejor versión) marca MARCA pero NO retiene el cierre por
sí solo: la ruta solo recoge NO_RESUELTO y DOBLE_NEGACION_LITOTE. La ablación
de pilares es observación (casi siempre "frágil"): se registra como marca de
estado OBSERVACION, no levanta la bandera ni retiene el cierre.

Capas de este archivo (en orden):
  1) Neutral, fuera de U6: acero_rival se prueba cargando el guardián por ruta
     explícita, sin importar el motor (SOBREVIVE / NO_RESUELTO / CAE, banda de
     empate del 10%, EPS=0.25, evidencia de pilares).
  2) Estático: el cableado existe en UNICO run() y en correr_guardianes.
  3) Vivo (subproceso correr_estandar.py): en una corrida real el bloque
     ejecuta (steelman EJECUTADO, 3 pruebas SOBREVIVE, ablación frágil como
     observación), bandera LIMPIO, H intacta, y el cierre queda LATENTE por
     Copi, no por el acero.
  4) Unidad: g_acero devuelve MARCA / NO_RESUELTO / LIMPIO según los
     veredictos, y ruta_cierre_latente retiene el cierre por un NO_RESUELTO
     de acero (pero no por un CAE ni por una observación de ablación).
  5) Bypass (subproceso con ACERO_GUARDIAN=off): el apagado queda marcado
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
ACERO = MOTOR_DIR / "guardian_acero_rival_v1.py"
SIDECAR = MOTOR_DIR / "sidecar_ablacion_hombre_acero.py"
UNICO = MOTOR_DIR / "MOTOR_V15_3_UNICO_20260927.py"
CONTROL = MOTOR_DIR / "guardianes_control_v1.py"
THEMISTOCLES = ROOT / "inputs" / "THEMISTOCLES_FREEZE_480BC_CATALOG_REPAIR_R2.json"

# Sondas verificadas por ejecución directa del guardián (2026-11-17).
# A domina a B y C en todas las dimensiones por más de la banda de empate.
PRED_SOBREVIVE = {
    "candidates": [
        {"family": "A", "features": {"d1": 10.0, "d2": 10.0, "lateral_contribution": 0.0}},
        {"family": "B", "features": {"d1": 2.0, "d2": 3.0, "lateral_contribution": 0.0}},
        {"family": "C", "features": {"d1": 0.0, "d2": 0.0, "lateral_contribution": 0.0}},
    ],
    "dimensions": ["d1", "d2"],
}
# B empata con A en x e y tras el acero (dentro de la banda del 10%) y ya
# ganaba en z: con su mejor versión honesta supera al top1 -> CAE.
PRED_CAE = {
    "candidates": [
        {"family": "A", "features": {"x": 10.0, "y": 10.0, "z": 0.0, "lateral_contribution": 0.0}},
        {"family": "B", "features": {"x": 9.5, "y": 9.5, "z": 10.0, "lateral_contribution": 0.0}},
        {"family": "C", "features": {"x": 0.0, "y": 0.0, "z": 5.0, "lateral_contribution": 0.0}},
    ],
    "dimensions": ["x", "y", "z"],
}
# Una sola dimensión: B empata con A tras el acero -> dif 0 -> NO_RESUELTO.
PRED_NO_RESUELTO = {
    "candidates": [
        {"family": "A", "features": {"d1": 10.0, "lateral_contribution": 0.0}},
        {"family": "B", "features": {"d1": 9.5, "lateral_contribution": 0.0}},
        {"family": "C", "features": {"d1": 0.0, "lateral_contribution": 0.0}},
    ],
    "dimensions": ["d1"],
}
# Solo x está dentro de la banda de empate (d=0.5 <= 10% del rango 10);
# y no (d=5 > 1.0): el acero solo favorece x.
PRED_BANDA = {
    "candidates": [
        {"family": "A", "features": {"x": 10.0, "y": 10.0, "lateral_contribution": 0.0}},
        {"family": "B", "features": {"x": 9.5, "y": 5.0, "lateral_contribution": 0.0}},
        {"family": "C", "features": {"x": 0.0, "y": 0.0, "lateral_contribution": 0.0}},
    ],
    "dimensions": ["x", "y"],
}
CASE_PILAR = {
    "case_id": "TEST_ACERO_PILAR",
    "cuts": [
        {"id": "C1", "P": [("tok1", 1)], "A": [], "C": []},
        {"id": "C2", "P": [("tok1", 1), ("tok2", 1)], "A": [], "C": []},
    ],
}
PRED_PILAR = {
    "candidates": [{"family": "TOP", "features": {}}],
    "own_evidence": {"TOP": {"favor_tokens": ["tok1", "tok2"]}},
}


def _load_acero():
    spec = importlib.util.spec_from_file_location("guardian_acero_rival_v1", ACERO)
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
def test_no_aplica_sin_rivales_o_dimensiones():
    m = _load_acero()
    assert m.acero_rival({"candidates": [], "dimensions": ["d1"]})["estado"] == "NO_APLICA"
    assert m.acero_rival({"candidates": [{"family": "A", "features": {"d1": 10.0}}],
                          "dimensions": ["d1"]})["estado"] == "NO_APLICA"
    assert m.acero_rival({"candidates": [{"family": "A", "features": {"d1": 10.0}},
                                         {"family": "B", "features": {"d1": 5.0}}],
                          "dimensions": []})["estado"] == "NO_APLICA"
    assert m.acero_rival({"candidates": [{"family": "A", "features": {"d1": 10.0}},
                                         {"family": "B", "features": {"d1": 5.0}}],
                          "dimensions": []})["motivo"] == "menos_de_2_candidatos_o_sin_dimensiones"


def test_sobrevive_ganador_claro():
    m = _load_acero()
    r = m.acero_rival(PRED_SOBREVIVE)
    assert r["estado"] == "EJECUTADO", r
    assert r["top1"] == "A" and r["base_coincide_con_motor"] is True
    assert r["orden_base_recalculado_top3"] == ["A", "B", "C"], r
    assert [p["veredicto_top1"] for p in r["pruebas"]] == ["SOBREVIVE", "SOBREVIVE"]
    assert all(p["dif_acero"] > m.EPS for p in r["pruebas"])
    assert all(p["dimensiones_empate_a_favor_del_rival"] == [] for p in r["pruebas"])
    assert r["regla"].startswith("acero = empates<=10% rango a favor del rival; EPS=0.25")


def test_cae_rival_supera_con_acero():
    m = _load_acero()
    r = m.acero_rival(PRED_CAE)
    assert r["estado"] == "EJECUTADO", r
    por_rival = {p["rival"]: p for p in r["pruebas"]}
    b = por_rival["B"]
    # En base A y B empataban (dif 0.0); con el acero B queda arriba por 1.0.
    assert b["dif_base"] == 0.0 and b["dif_acero"] == -1.0, b
    assert b["veredicto_top1"] == "CAE", b
    assert b["dimensiones_empate_a_favor_del_rival"] == ["x", "y"], b
    assert por_rival["C"]["veredicto_top1"] == "SOBREVIVE"
    # La sensibilidad del pilar es informativa: no cambia el veredicto (ya CAE).
    # El pilar del top1 es x (ventaja de rango 0.5); quitándolo, B queda aún
    # más arriba (dif -1.0), así que también cae en la sensibilidad.
    assert b["sensibilidad_pilar"]["pilar_top1"] == "x"
    assert b["sensibilidad_pilar"]["dif_sin_pilar"] == -1.0
    assert b["sensibilidad_pilar"]["cae_si_ademas_se_quita_pilar"] is True


def test_no_resuelto_empate_tras_acero():
    m = _load_acero()
    r = m.acero_rival(PRED_NO_RESUELTO)
    assert r["estado"] == "EJECUTADO", r
    por_rival = {p["rival"]: p for p in r["pruebas"]}
    assert por_rival["B"]["dif_acero"] == 0.0, por_rival["B"]
    assert por_rival["B"]["veredicto_top1"] == "NO_RESUELTO", por_rival["B"]
    assert por_rival["C"]["veredicto_top1"] == "SOBREVIVE"


def test_acero_solo_favorece_empates_dentro_de_banda():
    # Límite de la regla, verificado por ejecución: el acero solo resuelve a
    # favor del rival las dimensiones donde el top1 gana por <= 10% del rango
    # de esa dimensión entre los top10. Una ventaja mayor no se toca.
    m = _load_acero()
    r = m.acero_rival(PRED_BANDA)
    por_rival = {p["rival"]: p for p in r["pruebas"]}
    assert por_rival["B"]["dimensiones_empate_a_favor_del_rival"] == ["x"], por_rival["B"]
    assert por_rival["B"]["dif_acero"] == 0.5 and por_rival["B"]["veredicto_top1"] == "SOBREVIVE"


def test_evidencia_pilares_H():
    m = _load_acero()
    piezas = m.evidencia_pilares_H(CASE_PILAR, PRED_PILAR)
    assert [p["token"] for p in piezas] == ["tok1", "tok2"], piezas
    e1, e2 = piezas
    assert e1["axis"] == "P" and e1["cuts"] == ["C1", "C2"] and e1["consec"] == 2, e1
    assert e2["axis"] == "P" and e2["cuts"] == ["C2"] and e2["consec"] == 1, e2
    assert m.evidencia_pilares_H({"cuts": []}, {"candidates": []}) == []
    # Sin cortes no hay dónde buscar los tokens: las piezas salen con cortes
    # vacíos y consec 0 (no desaparecen: el top1 sí tiene tokens a favor).
    vacias = m.evidencia_pilares_H({"cuts": []}, PRED_PILAR)
    assert [p["token"] for p in vacias] == ["tok1", "tok2"], vacias
    assert all(p["cuts"] == [] and p["consec"] == 0 and p["axis"] == "" for p in vacias)


def test_solo_mide_nunca_decide():
    m = _load_acero()
    assert m.VERSION == "1.0.1-20260927"
    assert m.EPS == 0.25 and m.BANDA_EMPATE_REL == 0.10
    assert "can_decide_H=False" in (m.__doc__ or "")
    for pred in (PRED_SOBREVIVE, PRED_CAE, PRED_NO_RESUELTO):
        r = m.acero_rival(pred)
        assert set(r) == {"estado", "top1", "orden_base_recalculado_top3",
                          "base_coincide_con_motor", "pruebas", "regla"}, r
        assert "H1" not in r and "H2" not in r
        for p in r["pruebas"]:
            assert p["veredicto_top1"] in ("SOBREVIVE", "NO_RESUELTO", "CAE")
            assert set(p["sensibilidad_pilar"]) == {"pilar_top1", "ventaja_pilar",
                                                    "dif_sin_pilar", "cae_si_ademas_se_quita_pilar"}


# ------------------------------------------------------------------ 2) estático: el cableado existe
def test_cableado_presente_en_runner_y_control():
    src = UNICO.read_text(encoding="utf-8")
    assert 'gmod.correr_guardianes' in src
    assert 'result["guardianes"]=guard_out' in src
    assert 'ACERO_GUARDIAN' in src
    assert 'omitir=_acero_omitir' in src
    assert '"acero_modo":_acero_modo' in src
    ctrl = CONTROL.read_text(encoding="utf-8")
    assert 'def correr_guardianes(' in ctrl and 'omitir=frozenset()' in ctrl
    assert '"HOMBRE_DE_ACERO" in omitir' in ctrl
    assert '"NO_CONFIGURADO"' in ctrl
    assert 'seguro("HOMBRE_DE_ACERO"' in ctrl


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
    env.pop("ACERO_GUARDIAN", None)
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


def test_corrida_real_ejecuta_acero(tmp_path):
    out = tmp_path / "resultado_acero.json"
    res = _corre_estandar(THEMISTOCLES, "ACERO_SMOKE", out)
    g = res.get("guardianes") or {}
    assert g.get("status") == "EXECUTED"
    assert g.get("can_decide_H") is False
    b = _bloque(res, "HOMBRE_DE_ACERO")
    assert b is not None, "sin bloque HOMBRE_DE_ACERO en una corrida real"
    assert b.get("can_decide_H") is False
    # Baseline THEMISTOCLES: el top1 sobrevive a sus 3 rivales por mucho
    # (dif_acero 3.88 / 4.22 / 9.38, EPS=0.25) -> bandera LIMPIO.
    assert b.get("bandera") == "LIMPIO", b
    assert b.get("n_revisados") == 4, b  # 3 pruebas de steelman + 1 ablación
    det = b.get("detalle") or {}
    sm = det.get("steelman_rival") or {}
    assert sm.get("estado") == "EJECUTADO", sm
    assert sm.get("top1") == "arquetipo_el_gobernante"
    assert sm.get("base_coincide_con_motor") is True
    assert [p["rival"] for p in sm.get("pruebas", [])] == [
        "13_enemistad_de_parientes", "social_08_girard_mimesis_y_chivo_expiatorio", "30_ambicion"], sm
    assert [p["veredicto_top1"] for p in sm.get("pruebas", [])] == ["SOBREVIVE"] * 3
    assert all(p["dif_acero"] > 0.25 for p in sm.get("pruebas", [])), sm
    # Las piezas del sidecar coinciden con el SHA esperado declarado.
    piezas_meta = {p.get("archivo"): p for p in b.get("piezas", [])}
    assert piezas_meta["sidecar_ablacion_hombre_acero.py"]["sha_ok"] is True, piezas_meta
    assert piezas_meta["guardian_acero_rival_v1.py"]["version"] == "1.0.1-20260927"
    # La ablación de pilares sale frágil (como casi siempre): es observación,
    # no levanta la bandera ni retiene el cierre.
    ab = det.get("ablacion_pilares_H") or {}
    assert ab.get("veredicto") == "fragil-de-conjunto", ab
    assert len(ab.get("piezas") or []) == 3, ab
    obs = [x for x in b.get("marcas", []) if x.get("estado") == "OBSERVACION"]
    assert [x["tipo"] for x in obs] == ["OBS_H1_FRAGIL_DE_CONJUNTO"], b.get("marcas")
    assert b.get("n_marcas") == 1, b
    # H intacto: los guardianes solo marcan, no reescriben predictor ni H
    v = g.get("verificacion_H_intacto") or {}
    assert v.get("predictor_igual") is True and v.get("H1_H2_igual") is True
    assert v.get("patterns_igual") is True
    assert (res.get("H1") or {}).get("family") == "arquetipo_el_gobernante"
    assert (res.get("H2") or {}).get("family") == "13_enemistad_de_parientes"
    # El cierre queda LATENTE por Copi, no por el acero.
    ruta = g.get("ruta_cierre_latente") or {}
    assert ruta.get("estado_cierre") == "LATENTE", ruta
    assert "HOMBRE_DE_ACERO" not in (ruta.get("guardianes_que_objetan") or []), ruta
    cg = res.get("cierre_guardianes") or {}
    assert "HOMBRE_DE_ACERO" not in (cg.get("guardianes_que_objetan") or []), cg
    # el recibo de componentes lo registra como ejecutado, sin poder de decisión
    comp = next((s for s in (res.get("execution") or {}).get("component_status") or []
                 if s.get("component") == "guardianes_control_v1.py"), None)
    assert comp is not None and comp.get("status") == "EXECUTED"
    assert comp.get("can_decide_H") is False
    assert comp.get("acero_modo") == "activo"
    assert (comp.get("banderas") or {}).get("HOMBRE_DE_ACERO") == "LIMPIO"


def test_unidad_g_acero_banderas():
    mod = _load_control()
    case = {"case_id": "TEST_ACERO_UNIDAD", "cuts": []}
    b = mod.g_acero(MOTOR_DIR, case, PRED_CAE, [])
    assert b["guardian"] == "HOMBRE_DE_ACERO"
    assert b["bandera"] == "MARCA", b
    assert b["can_decide_H"] is False
    cae = [x for x in b["marcas"] if x["tipo"] == "TOP1_CAE_ANTE_ACERO_DE_B"]
    assert cae and cae[0]["estado"] == "DETECTADA", b["marcas"]
    b = mod.g_acero(MOTOR_DIR, case, PRED_NO_RESUELTO, [])
    assert b["bandera"] == "NO_RESUELTO", b
    nr = [x for x in b["marcas"] if x["tipo"] == "TOP1_NO_RESUELTO_ANTE_ACERO_DE_B"]
    assert nr and nr[0]["estado"] == "NO_RESUELTO", b["marcas"]
    b = mod.g_acero(MOTOR_DIR, case, PRED_SOBREVIVE, [])
    assert b["bandera"] == "LIMPIO" and b["n_marcas"] == 0, b
    # Sin pilares a favor no hay ablación que observar: veredicto del sidecar
    # "sin-pilares-seleccionados", sin marca OBS.
    assert (b.get("detalle") or {}).get("ablacion_pilares_H", {}).get("veredicto") == "sin-pilares-seleccionados", b


def test_retencion_cierre_no_resuelto_acero():
    """Un NO_RESUELTO de acero retiene el cierre (ruta_cierre_latente); un CAE
    (DETECTADA) o una observación de ablación, por sí solos, no lo retienen."""
    mod = _load_control()
    ruta = mod.ruta_cierre_latente(
        [{"guardian": "LOGICA_COPI", "bandera": "LIMPIO", "marcas": []},
         {"guardian": "HOMBRE_DE_ACERO", "bandera": "NO_RESUELTO", "marcas": [
             {"tipo": "TOP1_NO_RESUELTO_ANTE_ACERO_DE_B", "estado": "NO_RESUELTO",
              "evidencia": {"rival": "B", "dif_acero": 0.0, "veredicto_top1": "NO_RESUELTO"}}]}],
        {"case_id": "TEST_ACERO_RETENCION"}, {"cuts": []}, {}, MOTOR_DIR)
    assert ruta.get("estado_cierre") == "LATENTE", ruta
    assert "HOMBRE_DE_ACERO" in (ruta.get("guardianes_que_objetan") or []), ruta
    assert ruta.get("can_decide_H") is False
    # CAE solo: marca MARCA, pero la ruta no objeta (no es NO_RESUELTO).
    ruta2 = mod.ruta_cierre_latente(
        [{"guardian": "HOMBRE_DE_ACERO", "bandera": "MARCA", "marcas": [
            {"tipo": "TOP1_CAE_ANTE_ACERO_DE_B", "estado": "DETECTADA",
             "evidencia": {"rival": "B", "dif_acero": -1.0, "veredicto_top1": "CAE"}}]}],
        {"case_id": "TEST_ACERO_SIN_RETENCION"}, {"cuts": []}, {}, MOTOR_DIR)
    assert ruta2.get("estado_cierre") == "SIN_OBJECION_DE_GUARDIANES", ruta2
    assert "HOMBRE_DE_ACERO" not in (ruta2.get("guardianes_que_objetan") or []), ruta2
    # Observación de ablación sola: tampoco retiene.
    ruta3 = mod.ruta_cierre_latente(
        [{"guardian": "HOMBRE_DE_ACERO", "bandera": "LIMPIO", "marcas": [
            {"tipo": "OBS_H1_FRAGIL_DE_CONJUNTO", "estado": "OBSERVACION",
             "evidencia": {"n_piezas": 3, "veredicto": "fragil-de-conjunto"}}]}],
        {"case_id": "TEST_ACERO_OBS"}, {"cuts": []}, {}, MOTOR_DIR)
    assert ruta3.get("estado_cierre") == "SIN_OBJECION_DE_GUARDIANES", ruta3


def test_bypass_acero_off_queda_marcado_no_configurado(tmp_path):
    out = tmp_path / "resultado_acero_off.json"
    res = _corre_estandar(THEMISTOCLES, "ACERO_BYPASS", out, {"ACERO_GUARDIAN": "off"})
    g = res.get("guardianes") or {}
    bloque = _bloque(res, "HOMBRE_DE_ACERO")
    assert bloque is not None, "el bypass no debe borrar el bloque en silencio"
    assert bloque.get("bandera") == "NO_CONFIGURADO", bloque
    assert not [m for m in bloque.get("marcas", []) if m.get("estado") == "DETECTADA"]
    comp = next((s for s in (res.get("execution") or {}).get("component_status") or []
                 if s.get("component") == "guardianes_control_v1.py"), None)
    assert comp is not None and comp.get("acero_modo") == "off"
    assert (comp.get("banderas") or {}).get("HOMBRE_DE_ACERO") == "NO_CONFIGURADO"
    # El resto de guardianes sigue corriendo con el bypass de acero.
    assert _bloque(res, "LOGICA_COPI") is not None
    assert _bloque(res, "POLARIDAD_CAUSAL") is not None
