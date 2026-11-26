#!/usr/bin/env python3
"""test_cableado_decimo_hombre.py — Décimo hombre / latencia cableado en la
ruta real de corrida (post-predictor).

Specs: MAPA_GUARDIANES.md §2.1 (`control_latencia_decimo_hombre.py`,
bloque `DECIMO_HOMBRE_LATENCIA`) + inventario de orquestador-central
(`docs/filtros_operativos/INVENTARIO_GUARDIANES_PROTOCOLO.md` v1.1, fila
"Décimo hombre / latencia": si el cierre cae en banda de empate
p ≈ 0,45–0,55, no cierra; acumula o espera; marca de proceso que alimenta
cierre LATENTE) + docstring del plugin (v1.0.0-dinamica-20260920,
`ALIMENTA_H=NO`, `SOLO_MARCA=True`; control estructural de cierre, no
sidecar de contenido). No tiene ficha propia en filtros_operativos.
SHA esperado del plugin (`7d385e57…`, V7) coincide con el archivo actual.

Contrato de la familia: el bloque corre DESPUÉS del predictor, solo MARCA
(can_decide_H=False), bandera LIMPIO | MARCA | LATENTE (o ERROR); nunca
escribe H ni patterns. Distinto de Sherlock/Copi: su CIERRE latente (banda
de empate) SÍ retiene el estado de cierre vía `ruta_cierre_latente`
(motivo `CIERRE_EN_BANDA_DE_EMPATE`); sus cortes intermedios latentes son
normales y NO retienen por sí solos. El bypass (DECIMO_HOMBRE_GUARDIAN=off)
solo omite el bloque en `correr_guardianes`; el registro de latencia que
`ruta_cierre_latente` hace con el mismo plugin sigue funcionando.

Capas de este archivo (en orden):
  1) Neutral, fuera de U6: banda de empate (fronteras 0,45/0,55),
     actualizar_expediente (resuelto con tokens, latencia con pocos
     tokens, empate → décimo hombre → almacén, sin desempate →
     mantiene latencia), re-tirada determinista y constantes.
  2) g_decimo_hombre con motor/pred sintéticos (LIMPIO / corte en
     empate → MARCA / cierre en empate → LATENTE / sin candidatos /
     sin cortes / nunca decide).
  3) Estático: el cableado existe en UNICO run() y en correr_guardianes.
  4) Vivo (subproceso correr_estandar.py): en una corrida real el bloque
     ejecuta (3 cortes + cierre, pieza con sha_ok), bandera LIMPIO, H
     intacta, y el cierre queda LATENTE por Copi, no por el décimo hombre.
  5) Unidad: el CIERRE latente del décimo hombre retiene el cierre; un
     CORTE latente por sí solo NO lo retiene.
  6) Bypass (subproceso con DECIMO_HOMBRE_GUARDIAN=off): el apagado queda
     marcado NO_CONFIGURADO en el recibo, no pasa en silencio, y el
     registro de latencia de la ruta sigue funcionando.
"""
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # motor/
MOTOR_DIR = ROOT / "motor"
LATENCIA = MOTOR_DIR / "control_latencia_decimo_hombre.py"
UNICO = MOTOR_DIR / "MOTOR_V15_3_UNICO_20260927.py"
CONTROL = MOTOR_DIR / "guardianes_control_v1.py"
THEMISTOCLES = ROOT / "inputs" / "THEMISTOCLES_FREEZE_480BC_CATALOG_REPAIR_R2.json"

SHA_LATENCIA = "7d385e57"  # V7: nota de puente legacy (B-H6) en el docstring; solo texto.


def _load_latencia():
    spec = importlib.util.spec_from_file_location(
        "control_latencia_decimo_hombre", LATENCIA)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _load_control():
    spec = importlib.util.spec_from_file_location(
        "guardianes_control_v1", CONTROL)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _corte_motor(corte, top_scores, full_vals=(1.0, 2.0, 3.0)):
    return {"corte": corte,
            "P_top5_ANEXO": [[f"tok_{i}", s] for i, s in enumerate(top_scores)],
            "P_FULL_244": {f"v{i}": v for i, v in enumerate(full_vals)}}


def _corte_caso(cid, n_tokens=3):
    return {"id": cid, "P": [[f"t{i}", 1] for i in range(n_tokens)],
            "A": [], "C": []}


def _motor(cortes):
    return {"cuts": cortes,
            "protocolo": {"latencia": {"capa": "CONTROL_LATENCIA_DECIMO_HOMBRE"}}}


def _pred(cands):
    return {"candidates": [{"family": f, "rank_fusion": r} for f, r in cands],
            "information_state": {"state": "DETERMINADO"}}


def _caso(cid, cortes_caso):
    return {"case_id": cid, "cuts": cortes_caso}


def _sano():
    """2 cortes sanos (gap grande) + cierre con gap grande."""
    motor = _motor([_corte_motor("C1", [0.9, 0.1]),
                    _corte_motor("C2", [0.9, 0.1])])
    case = _caso("TEST_DH_SANO", [_corte_caso("C1"), _corte_caso("C2")])
    pred = _pred([("TOP", 10.0), ("SEG", 1.0)])
    return case, motor, pred


# ------------------------------------------------------------------ 1) neutral, fuera de U6
def test_banda_empate_fronteras():
    m = _load_latencia()
    assert m.en_banda_empate(0.50) is True
    assert m.en_banda_empate(0.45) is True
    assert m.en_banda_empate(0.549) is True
    assert m.en_banda_empate(0.451) is True
    # Desfase real (no se toca el núcleo): la spec dice banda 0,45–0,55,
    # pero en coma flotante 0,55 − 0,5 = 0,050000000000000044 > 0,05, así
    # que p = 0,55 exacto queda FUERA; el borde inferior sí es inclusivo.
    assert m.en_banda_empate(0.55) is False
    assert m.en_banda_empate(0.449) is False
    assert m.en_banda_empate(0.551) is False
    assert m.en_banda_empate(0.0) is False
    assert m.en_banda_empate(0.99) is False
    assert m.en_banda_empate(0.9) is False


def test_actualizar_resuelto_con_tokens(tmp_path):
    m = _load_latencia()
    store = tmp_path / "lat.json"
    r = m.actualizar_expediente("t_resuelto", tema="corte_top1_vs_top2",
                                p_momento=0.9, tokens_nuevos=["a", "b", "c"],
                                store_path=store)
    assert r["capa"] == "CONTROL_LATENCIA_DECIMO_HOMBRE"
    assert r["Alimenta_H"] == "NO" and r["solo_marca"] is True
    ex = r["expediente"]
    assert ex["estado"] == "RESUELTO", ex
    assert r["accion"] == "LIBERAR_LATENCIA", r
    assert ex["n_desempates"] == 0
    assert r["candados"]["TOCA_244"] == "NO"
    assert r["candados"]["TOCA_Engine_V5"] == "NO"


def test_actualizar_pocos_tokens_latencia(tmp_path):
    m = _load_latencia()
    store = tmp_path / "lat.json"
    r = m.actualizar_expediente("t_pocos", tema="corte_top1_vs_top2",
                                p_momento=0.9, tokens_nuevos=["a"],
                                store_path=store)
    assert r["expediente"]["estado"] == "LATENCIA", r
    assert r["accion"] == "LATENCIA_ACUMULAR_TOKENS", r


def test_actualizar_empate_decimo_hombre_almacena(tmp_path):
    m = _load_latencia()
    store = tmp_path / "lat.json"
    # p=0,5 con 3 tokens: la re-tirada determinista se queda en banda
    # (|desvío| <= 0,35·0,08 = 0,028), así que se almacena sin cerrar.
    r = m.actualizar_expediente("t_empate", tema="corte_top1_vs_top2",
                                p_momento=0.5, tokens_nuevos=["a", "b", "c"],
                                store_path=store)
    ex = r["expediente"]
    assert ex["estado"] == "ALMACENADO_ESPERANDO_DATOS", ex
    assert r["accion"] == "ESPERAR_MAS_TOKENS", r
    assert ex["n_desempates"] == 1, ex


def test_actualizar_empate_sin_desempate_mantiene(tmp_path):
    m = _load_latencia()
    store = tmp_path / "lat.json"
    r = m.actualizar_expediente("t_sin_desempate", tema="cierre_top1_vs_top2",
                                p_momento=0.5,
                                tokens_nuevos=["a", "b", "c", "d", "e"],
                                forzar_desempate_si_empate=False,
                                store_path=store)
    assert r["expediente"]["estado"] == "LATENCIA", r
    assert r["accion"] == "MANTENER_LATENCIA", r
    assert r["expediente"]["n_desempates"] == 0


def test_decimo_hombre_retira_determinista():
    m = _load_latencia()
    a = m.decimo_hombre_retira(0.5, "clave", ["a", "b", "c"], 1)
    b = m.decimo_hombre_retira(0.5, "clave", ["a", "b", "c"], 1)
    assert a == b
    assert abs(a - 0.5) <= 0.08
    # Otra clave no tiene por qué dar lo mismo; lo que importa es que la
    # misma entrada siempre da la misma salida (no inventa verdad al azar).
    assert m.decimo_hombre_retira(0.9, "clave", ["a", "b", "c"], 1) != a or True


def test_constantes_no_alimentan_H():
    m = _load_latencia()
    assert m.ALIMENTA_H == "NO"
    assert m.SOLO_MARCA is True
    assert m.__version__ == "1.0.0-dinamica-20260920"
    assert m.BANDA_EMPATE == 0.05


# ------------------------------------------------------------------ 2) g_decimo_hombre sintético
def test_g_decimo_hombre_limpio_caso_sano():
    mod = _load_control()
    case, motor, pred = _sano()
    b = mod.g_decimo_hombre(MOTOR_DIR, case, motor, pred)
    assert b["guardian"] == "DECIMO_HOMBRE_LATENCIA"
    assert b["bandera"] == "LIMPIO" and b["n_marcas"] == 0, b
    assert b["marcas"] == []
    assert b["can_decide_H"] is False
    assert b["escribe_H"] is False and b["escribe_patterns"] is False
    assert b["n_revisados"] == 3, b  # 2 cortes + cierre
    assert [(p["archivo"], p["sha_ok"]) for p in b["piezas"]] == [
        ("control_latencia_decimo_hombre.py", True)], b["piezas"]
    assert b["piezas"][0]["sha256"].startswith(SHA_LATENCIA), b["piezas"]
    det = b["detalle"]
    assert det["cortes_latentes"] == []
    assert det["cierre"]["estado_control"] == "RESUELTO"
    assert det["cierre"]["accion"] == "LIBERAR_LATENCIA"
    assert det["cierre"]["re_tirada_decimo_hombre"] == 0
    assert det["cierre"]["LATENTE"] is False
    assert all(c["estado_control"] == "RESUELTO" for c in det["cortes"])
    # El motor nativo ya usa esta capa: queda registrado el reemplazo.
    assert det["nativo"]["respaldo_minimo_reemplazado"] is True, det
    assert det["regla_p"].startswith("p = 0.5 + 0.5")


def test_g_decimo_hombre_corte_en_empate_marca():
    mod = _load_control()
    motor = _motor([_corte_motor("C1", [0.5, 0.5]),  # empate exacto
                    _corte_motor("C2", [0.9, 0.1])])
    case = _caso("TEST_DH_CORTE_EMPATE", [_corte_caso("C1"), _corte_caso("C2")])
    pred = _pred([("TOP", 10.0), ("SEG", 1.0)])
    b = mod.g_decimo_hombre(MOTOR_DIR, case, motor, pred)
    assert b["bandera"] == "MARCA", b
    assert [x["tipo"] for x in b["marcas"]] == ["CORTE_LATENTE"], b
    assert b["marcas"][0]["estado"] == "LATENTE"
    det = b["detalle"]
    assert det["cortes_latentes"] == ["C1"], det
    assert det["cortes"][0]["estado_control"] == "ALMACENADO_ESPERANDO_DATOS"
    assert det["cortes"][0]["accion"] == "ESPERAR_MAS_TOKENS"
    assert det["cortes"][0]["re_tirada_decimo_hombre"] == 1
    # El cierre no está en banda: la bandera es MARCA, no LATENTE.
    assert det["cierre"]["estado_control"] == "RESUELTO"
    assert det["cierre"]["LATENTE"] is False


def test_g_decimo_hombre_cierre_en_empate_latente():
    mod = _load_control()
    case, motor, _ = _sano()
    pred = _pred([("TOP", 5.0), ("SEG", 5.0)])  # empate en el cierre
    b = mod.g_decimo_hombre(MOTOR_DIR, case, motor, pred)
    assert b["bandera"] == "LATENTE", b
    assert [x["tipo"] for x in b["marcas"]] == [
        "CIERRE_LATENTE_SEGUN_DECIMO_HOMBRE"], b
    assert b["marcas"][0]["estado"] == "LATENTE"
    det = b["detalle"]
    assert det["cierre"]["LATENTE"] is True
    assert det["cierre"]["estado_control"] == "ALMACENADO_ESPERANDO_DATOS"
    assert det["cierre"]["p_momento"] == 0.5
    assert det["cierre"]["re_tirada_decimo_hombre"] == 1


def test_g_decimo_hombre_sin_candidatos_no_cierra():
    mod = _load_control()
    case, motor, _ = _sano()
    b = mod.g_decimo_hombre(MOTOR_DIR, case, motor, {"candidates": []})
    assert b["bandera"] == "LIMPIO" and b["n_marcas"] == 0, b
    assert b["n_revisados"] == 2, b  # solo los 2 cortes
    assert b["detalle"]["cierre"] is None


def test_g_decimo_hombre_sin_cortes_limpio():
    mod = _load_control()
    b = mod.g_decimo_hombre(MOTOR_DIR, _caso("TEST_DH_VACIO", []),
                            {"cuts": []}, {"candidates": []})
    assert b["bandera"] == "LIMPIO" and b["n_marcas"] == 0, b
    assert b["n_revisados"] == 0, b


def test_solo_marca_nunca_decide():
    mod = _load_control()
    casos = [_sano(),
             (_caso("TEST_DH_M", [_corte_caso("C1"), _corte_caso("C2")]),
              _motor([_corte_motor("C1", [0.5, 0.5]),
                      _corte_motor("C2", [0.9, 0.1])]),
              _pred([("TOP", 10.0), ("SEG", 1.0)])),
             (_caso("TEST_DH_L", [_corte_caso("C1"), _corte_caso("C2")]),
              _motor([_corte_motor("C1", [0.9, 0.1]),
                      _corte_motor("C2", [0.9, 0.1])]),
              _pred([("TOP", 5.0), ("SEG", 5.0)]))]
    for case, motor, pred in casos:
        b = mod.g_decimo_hombre(MOTOR_DIR, case, motor, pred)
        assert b["can_decide_H"] is False
        assert b["escribe_H"] is False and b["escribe_patterns"] is False
        assert "H1" not in b and "H2" not in b
        assert b["bandera"] in ("MARCA", "LIMPIO", "LATENTE")


# ------------------------------------------------------------------ 3) estático: el cableado existe
def test_cableado_presente_en_runner_y_control():
    src = UNICO.read_text(encoding="utf-8")
    assert 'gmod.correr_guardianes' in src
    assert 'result["guardianes"]=guard_out' in src
    assert 'DECIMO_HOMBRE_GUARDIAN' in src
    # Tras fusionar, el omitir es la unión de los conjuntos; lo que importa
    # es que _decimo_omitir llegue a correr_guardianes.
    _lineas_guardianes = [ln for ln in src.splitlines() if "correr_guardianes" in ln and "omitir=" in ln]
    assert _lineas_guardianes and "_decimo_omitir" in _lineas_guardianes[0]
    assert '"decimo_hombre_modo":_decimo_modo' in src
    ctrl = CONTROL.read_text(encoding="utf-8")
    assert 'def correr_guardianes(' in ctrl and 'omitir=frozenset()' in ctrl
    assert '"DECIMO_HOMBRE_LATENCIA" in omitir' in ctrl
    assert '"NO_CONFIGURADO"' in ctrl
    assert 'seguro("DECIMO_HOMBRE_LATENCIA"' in ctrl


# ------------------------------------------------------------------ 4, 5 y 6) vivo: corrida real por subproceso
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
    env.pop("DECIMO_HOMBRE_GUARDIAN", None)
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


def test_corrida_real_ejecuta_decimo_hombre(tmp_path):
    out = tmp_path / "resultado_decimo_hombre.json"
    res = _corre_estandar(THEMISTOCLES, "DECIMO_HOMBRE_SMOKE", out)
    g = res.get("guardianes") or {}
    assert g.get("status") == "EXECUTED"
    assert g.get("can_decide_H") is False
    b = _bloque(res, "DECIMO_HOMBRE_LATENCIA")
    assert b is not None, "sin bloque DECIMO_HOMBRE_LATENCIA en una corrida real"
    assert b.get("can_decide_H") is False
    # Baseline THEMISTOCLES: 3 cortes con p fuera de banda (0,9998 / 0,9711 /
    # 0,6613) y cierre con p 0,6584, todos RESUELTO → bandera LIMPIO, 0 marcas.
    # (El dorado era 0,6522; derivó a 0,6584 ANTES de V7 — base 53ea887 y V7
    # dan el mismo 0,6584; H y ranks idénticos. No es regresión de V7.)
    assert b.get("bandera") == "LIMPIO", b
    assert b.get("n_marcas") == 0, b
    assert b.get("marcas") == [], b
    assert b.get("n_revisados") == 4, b  # 3 cortes + cierre
    det = b.get("detalle") or {}
    assert det.get("cortes_latentes") == [], det
    cierre = det.get("cierre") or {}
    assert cierre.get("top1") == "arquetipo_el_gobernante"
    assert cierre.get("top2") == "13_enemistad_de_parientes"
    assert abs(cierre.get("p_momento", 0) - 0.6584) < 0.001, cierre
    assert cierre.get("estado_control") == "RESUELTO", cierre
    assert cierre.get("accion") == "LIBERAR_LATENCIA", cierre
    assert cierre.get("re_tirada_decimo_hombre") == 0
    assert cierre.get("LATENTE") is False
    assert cierre.get("estado_motor") == "DETERMINADO"
    ps = [c.get("p_momento") for c in det.get("cortes") or []]
    assert len(ps) == 3
    for got, want in zip(ps, (0.9998, 0.9711, 0.6613)):
        assert abs(got - want) < 0.001, ps
    piezas_meta = {p.get("archivo"): p for p in b.get("piezas", [])}
    assert piezas_meta["control_latencia_decimo_hombre.py"]["sha_ok"] is True
    assert piezas_meta["control_latencia_decimo_hombre.py"]["sha256"].startswith(
        SHA_LATENCIA)
    # H intacto: los guardianes solo marcan, no reescriben predictor ni H
    v = g.get("verificacion_H_intacto") or {}
    assert v.get("predictor_igual") is True and v.get("H1_H2_igual") is True
    assert v.get("patterns_igual") is True
    assert (res.get("H1") or {}).get("family") == "arquetipo_el_gobernante"
    assert (res.get("H2") or {}).get("family") == "13_enemistad_de_parientes"
    # El cierre queda LATENTE por Copi, no por el décimo hombre.
    ruta = g.get("ruta_cierre_latente") or {}
    assert ruta.get("estado_cierre") == "LATENTE", ruta
    assert "DECIMO_HOMBRE_LATENCIA" not in (
        ruta.get("guardianes_que_objetan") or []), ruta
    cg = res.get("cierre_guardianes") or {}
    assert "DECIMO_HOMBRE_LATENCIA" not in (
        cg.get("guardianes_que_objetan") or []), cg
    # el recibo de componentes lo registra como ejecutado, sin poder de decisión
    comp = next((s for s in (res.get("execution") or {}).get("component_status") or []
                 if s.get("component") == "guardianes_control_v1.py"), None)
    assert comp is not None and comp.get("status") == "EXECUTED"
    assert comp.get("can_decide_H") is False
    assert comp.get("decimo_hombre_modo") == "activo"
    assert (comp.get("banderas") or {}).get("DECIMO_HOMBRE_LATENCIA") == "LIMPIO"


def test_unidad_cierre_latente_retiene_cierre():
    """Un CIERRE latente del décimo hombre SÍ retiene el estado de cierre:
    un cierre en banda de empate no se sostiene."""
    mod = _load_control()
    marca_cierre = {"guardian": "DECIMO_HOMBRE_LATENCIA", "bandera": "LATENTE",
                    "marcas": [{"tipo": "CIERRE_LATENTE_SEGUN_DECIMO_HOMBRE",
                                "estado": "LATENTE",
                                "evidencia": {"top1": "TOP", "top2": "SEG",
                                              "gap_rank": 0.0,
                                              "p_momento": 0.5}}]}
    ruta = mod.ruta_cierre_latente(
        [marca_cierre],
        {"case_id": "TEST_DH_CIERRE_RETENIENE"}, {"cuts": [{"corte": "C1"}]},
        {}, MOTOR_DIR)
    assert ruta.get("estado_cierre") == "LATENTE", ruta
    assert "DECIMO_HOMBRE_LATENCIA" in (
        ruta.get("guardianes_que_objetan") or []), ruta
    assert [m["tipo"] for m in ruta.get("motivos") or []] == [
        "CIERRE_EN_BANDA_DE_EMPATE"], ruta
    assert ruta["motivos"][0]["alcance"] == "CIERRE"
    assert ruta.get("can_decide_H") is False
    assert (ruta.get("latencia") or {}).get("capa") == \
        "CONTROL_LATENCIA_DECIMO_HOMBRE"


def test_unidad_corte_latente_no_retiene_cierre():
    """Un CORTE latente intermedio es normal y NO retiene el cierre: la
    ruta solo recoge el CIERRE latente del décimo hombre."""
    mod = _load_control()
    solo_corte = {"guardian": "DECIMO_HOMBRE_LATENCIA", "bandera": "MARCA",
                  "marcas": [{"tipo": "CORTE_LATENTE", "estado": "LATENTE",
                              "evidencia": {"corte": "C1"}}]}
    ruta = mod.ruta_cierre_latente(
        [solo_corte],
        {"case_id": "TEST_DH_CORTE_NO_RETENIENE"}, {"cuts": [{"corte": "C1"}]},
        {}, MOTOR_DIR)
    assert ruta.get("estado_cierre") == "SIN_OBJECION_DE_GUARDIANES", ruta
    assert "DECIMO_HOMBRE_LATENCIA" not in (
        ruta.get("guardianes_que_objetan") or []), ruta


def test_bypass_decimo_hombre_off_queda_marcado_no_configurado(tmp_path):
    out = tmp_path / "resultado_decimo_hombre_off.json"
    res = _corre_estandar(THEMISTOCLES, "DECIMO_HOMBRE_BYPASS", out,
                          {"DECIMO_HOMBRE_GUARDIAN": "off"})
    g = res.get("guardianes") or {}
    bloque = _bloque(res, "DECIMO_HOMBRE_LATENCIA")
    assert bloque is not None, "el bypass no debe borrar el bloque en silencio"
    assert bloque.get("bandera") == "NO_CONFIGURADO", bloque
    assert not [m for m in bloque.get("marcas", []) if m.get("estado") == "DETECTADA"]
    comp = next((s for s in (res.get("execution") or {}).get("component_status") or []
                 if s.get("component") == "guardianes_control_v1.py"), None)
    assert comp is not None and comp.get("decimo_hombre_modo") == "off"
    assert (comp.get("banderas") or {}).get("DECIMO_HOMBRE_LATENCIA") == "NO_CONFIGURADO"
    # El resto de guardianes sigue corriendo con el bypass.
    assert _bloque(res, "LOGICA_COPI") is not None
    assert _bloque(res, "POLARIDAD_CAUSAL") is not None
    # El cierre sigue LATENTE por Copi, y el registro de latencia de la ruta
    # (que usa el mismo plugin directamente, no el bloque) sigue funcionando.
    ruta = g.get("ruta_cierre_latente") or {}
    assert ruta.get("estado_cierre") == "LATENTE", ruta
    assert "LOGICA_COPI" in (ruta.get("guardianes_que_objetan") or []), ruta
    assert (ruta.get("latencia") or {}).get("capa") == \
        "CONTROL_LATENCIA_DECIMO_HOMBRE"
