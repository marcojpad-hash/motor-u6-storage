#!/usr/bin/env python3
"""test_cableado_esteroides.py — Décimo hombre con esteroides cableado en la ruta real
de corrida (post-cierre, PATCH 017 en run() de UNICO).

Specs: MAPA_GUARDIANES.md §2.9 (`decimo_hombre_esteroides_mayeutica_v1.py` v1.1.0:
contrafactuales reales y mayéutica después del cierre; solo marca/audita; no altera
predictor, H ni la apuesta original; diagnostica Copi/Sherlock si vinieron vacíos en vez
de un PASS falso) + inventario de orquestador-central
(`docs/filtros_operativos/INVENTARIO_GUARDIANES_PROTOCOLO.md` v1.1, fila "Décimo hombre
con esteroides": contrafactuales y mayéutica después del cierre; auditoría, no toca H;
conectado en UNICO con recuperaciones si falla) + docstring del plugin
(`Décimo Hombre iterativo: contrafactuales reales, mayéutica y cierre operacional`,
CANON_LOCK todo False). No tiene ficha propia en filtros_operativos.

Hallazgo del cableado: el bloque YA se ejecutaba en la ruta real sin ninguna prueba
(baseline THEMISTOCLES: EJECUTADO_CIERRE_ADVERSARIAL, 8 ataques, 53 rankings
contrafactuales reales, H intacta, cierre AJUSTADA), pero no existía apagado: no había
bandera y el bloque corría siempre. Este PR no reescribe el núcleo: añade la bandera
`ESTEROIDES_GUARDIAN` (defecto activo; `off` = bypass visible NO_CONFIGURADO con
`esteroides_modo: off`) y registra `esteroides_modo` en la fila de componentes en ambos
casos, más `modo` en el recibo del bloque.
SHA esperado del plugin (`5f494ace…`) coincide con el archivo actual.
(V7: el docstring B-H4 añadió 5 líneas al plugin; SHA anterior `1fa9b779…`.)

Contrato de la familia: el bloque corre DESPUÉS del cierre final (016), solo AUDITA
(`can_decide_H=False`, `rewrites_H=False`); nunca escribe H ni patterns ni la apuesta
original. Su conclusión adversarial es una hipótesis aparte (`hipotesis_apuesta`,
`no_equivale_a_verdad_demostrada: True`); ni siquiera cuando un contrafactual
derrota al líder cierra solo: la reapertura mayéutica reevalúa y el superviviente
se reconfirma (`victoria_del_decimo_hombre_no_cierra_sola: True`). El bypass
(`ESTEROIDES_GUARDIAN=off`) no debe inventar auditoría ni cambiar el cierre: el
grado del cierre final es el mismo con el bloque activo o apagado.

Capas de este archivo (en orden):
  1) Neutral, fuera de U6: run() directo con predictor sintético (vacío sin
     candidatas → diagnóstico; sano → cierre adversarial con 8 ataques;
     Copi/Sherlock vacíos → NO_EVALUADO, no PASS falso; presentes → se
     reflejan; volteo de líder → reapertura mayéutica sin cerrar sola;
     run() no muta el resultado ni H; constantes y contrato).
  2) Estático: el cableado existe en UNICO run() (flag, rama else con
     NO_CONFIGURADO, esteroides_modo en la fila, modo en el recibo).
  3) Vivo (subproceso correr_estandar.py): en una corrida real el bloque
     ejecuta (EJECUTADO_CIERRE_ADVERSARIAL, 8 ataques, 53 rankings), H
     intacta, cierre AJUSTADA, fila EXECUTED_WITH_CONCLUSION con
     esteroides_modo activo.
  4) Unidad: la auditoría post-cierre no retiene ni reescribe el cierre
     (cierre_final y H intactos tras run(); el registro NO_CONFIGURADO no
     trae decisión ni hipótesis).
  5) Bypass (subproceso con ESTEROIDES_GUARDIAN=off): el apagado queda
     marcado NO_CONFIGURADO en el recibo, no pasa en silencio, el resto
     de guardianes sigue corriendo y el cierre final no cambia de grado.

Límite documentado (del módulo, no del test): sin runner contrafactual, la
ablación dimensional recalcula rank_fusion en local (RANK_FUSION_RECOMPUTED);
la verificación de recalculo base puede no coincidir con los scores
declarados en datos sintéticos (en THEMISTOCLES real sí coincide). Por eso
la capa 1 no afirma `score_recalculation_matches_original` en sintético.
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
ESTEROIDES = MOTOR_DIR / "decimo_hombre_esteroides_mayeutica_v1.py"
UNICO = MOTOR_DIR / "MOTOR_V15_3_UNICO_20260927.py"
THEMISTOCLES = ROOT / "inputs" / "THEMISTOCLES_FREEZE_480BC_CATALOG_REPAIR_R2.json"

SHA_ESTEROIDES = "5f494ace"
SHA_ENGINE = "665c39a2"
SHA_PATTERNS = "d827dcc3"

ATAQUES_SANO = [
    ("CONVERGENCIA_Y_SATURACION", "RESUELTO_POR_DESCONTAR_COMO_VOTO"),
    ("AQUILES_DIMENSIONAL", "RESUELTO_POR_ABLACION_REAL"),
    ("FUENTES_LATERALES", "NO_EJECUTADO_SIN_FUENTES_DECLARADAS"),
    ("AQUILES_SIN_EL_PALO", "RESUELTO_POR_ABLACIONES_DIMENSIONALES"),
    ("REAPERTURA_MAYEUTICA_DIALECTICA", "NO_REABIERTO_SIN_RIVAL_DERROTADOR"),
    ("PICOS_MESETAS_DEPRESIONES", "RESUELTO_DESCRIPTIVAMENTE"),
    ("COPI_FALACIAS", "RESUELTO_CON_DIAGNOSTICO_LOGICO"),
    ("SHERLOCK_HOMBRE_DE_ACERO", "RESUELTO_POR_COMPARACION_ADVERSARIAL"),
]

ATAQUES_THEMISTOCLES = [
    ("CONVERGENCIA_Y_SATURACION", "RESUELTO_POR_DESCONTAR_COMO_VOTO"),
    ("AQUILES_DIMENSIONAL", "RESUELTO_POR_ABLACION_REAL"),
    ("FUENTES_LATERALES", "RESUELTO_POR_CONTRAFÁCTICOS"),
    ("AQUILES_SIN_EL_PALO", "RESUELTO_POR_REEJECUCION_CORE"),
    ("REAPERTURA_MAYEUTICA_DIALECTICA", "NO_REABIERTO_SIN_RIVAL_DERROTADOR"),
    ("PICOS_MESETAS_DEPRESIONES", "RESUELTO_DESCRIPTIVAMENTE"),
    ("COPI_FALACIAS", "RESUELTO_CON_DIAGNOSTICO_LOGICO"),
    ("SHERLOCK_HOMBRE_DE_ACERO", "RESUELTO_POR_COMPARACION_ADVERSARIAL"),
]


def _load_esteroides():
    spec = importlib.util.spec_from_file_location(
        "decimo_hombre_esteroides_mayeutica_v1", ESTEROIDES)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# ------------------------------------------------------------------ builders
def _sano():
    """Predictor sintético sano: TOP lidera con margen, 2 dimensiones finitas."""
    rows = [
        {"family": "TOP", "rank_fusion": 10.0,
         "features": {"d1": 0.9, "d2": 0.8}},
        {"family": "SEG", "rank_fusion": 5.0,
         "features": {"d1": 0.1, "d2": 0.2}},
        {"family": "TER", "rank_fusion": 1.0,
         "features": {"d1": 0.05, "d2": 0.1}},
    ]
    copi = {"guardian": "LOGICA_COPI",
            "detalle": {"cierre_motor": {"evaluacion": {"estado": "VALIDO"}}}}
    rigor = {"guardian": "SHERLOCK_RIGOR",
             "detalle": {"salida_plugin": {"plugin": "METODO_RIGOR"}}}
    result = {"predictor": {"candidates": rows, "dimensions": ["d1", "d2"]},
              "guardianes": {"bloques": [copi, rigor]}}
    case = {"case_id": "TEST_SANO",
            "cuts": [{"P": [["tok", 1]], "A": [], "C": []}]}
    return case, result


def _ataques(out):
    return [(a.get("ataque"), a.get("estado")) for a in out.get("ataques") or []]


# ------------------------------------------------------------------ 1) neutral, fuera de U6
def test_run_vacio_sin_candidatas_diagnostico():
    dh = _load_esteroides()
    out = dh.run({"case_id": "TEST_VACIO"}, {"predictor": {"candidates": []}})
    assert out.get("status") == "EJECUTADO_CON_DIAGNOSTICO", out
    assert out.get("hipotesis_apuesta", {}).get("candidata") == \
        "NO_IDENTIFICABLE_CON_ESTA_ENTRADA", out
    assert out.get("can_decide_H") is False
    assert out.get("ataques") == [], out
    assert out.get("version") == "1.1.0-20261009-PATCH05"


def test_run_sano_cierre_adversarial():
    dh = _load_esteroides()
    case, result = _sano()
    out = dh.run(case, result)
    assert out.get("status") == "EJECUTADO_CIERRE_ADVERSARIAL", out
    assert out.get("decision_de_proceso") == \
        "CONCLUSION_OPERACIONAL_CERRADA_CON_TRAZABILIDAD", out
    ap = out.get("hipotesis_apuesta") or {}
    assert ap.get("candidata") == "TOP", ap
    assert ap.get("estado") == "CONCLUSION_ABDUCTIVA_OPERACIONAL", ap
    assert ap.get("no_equivale_a_verdad_demostrada") is True
    assert out.get("cambio_tras_adversario") is False
    assert out.get("can_decide_H") is False
    assert out.get("rewrites_H") is False
    assert out.get("rewrites_apuesta_original") is False
    assert _ataques(out) == ATAQUES_SANO, out
    diag = out.get("diagnosticos") or {}
    assert diag.get("copi") == "VALIDO", diag
    assert diag.get("sherlock") == "METODO_RIGOR", diag
    assert diag.get("actual_counterfactual_rankings") == 2, diag
    assert diag.get("adversarial_coverage_complete") is True, diag
    assert diag.get("baseline_recalculation_executed") is True, diag
    assert (out.get("reapertura_iterativa") or {}).get("punto_fijo") is True
    assert (out.get("orthogonal_residual_analysis") or {}).get("status") == \
        "NOT_IMPLEMENTED"


def test_run_copi_sherlock_vacios_diagnostico_no_pass_falso():
    """Copi/Sherlock ausentes se diagnostican como NO_EVALUADO: un control no
    disponible no prueba validez y no se convierte en un PASS falso."""
    dh = _load_esteroides()
    case, result = _sano()
    result["guardianes"] = {"bloques": []}
    out = dh.run(case, result)
    diag = out.get("diagnosticos") or {}
    assert diag.get("copi") == "NO_EVALUADO", diag
    assert diag.get("sherlock") == "NO_EVALUADO", diag
    por_ataque = {a.get("ataque"): a for a in out.get("ataques") or []}
    assert por_ataque["COPI_FALACIAS"].get("resultado") == "NO_EVALUADO"
    assert por_ataque["SHERLOCK_HOMBRE_DE_ACERO"].get("resultado") == "NO_EVALUADO"
    # El diagnóstico no veta la auditoría: sigue cerrando con trazabilidad.
    assert out.get("status") == "EJECUTADO_CIERRE_ADVERSARIAL", out


def test_run_copi_sherlock_presentes_se_reflejan():
    dh = _load_esteroides()
    case, result = _sano()
    out = dh.run(case, result)
    por_ataque = {a.get("ataque"): a for a in out.get("ataques") or []}
    assert por_ataque["COPI_FALACIAS"].get("resultado") == "VALIDO"
    assert por_ataque["SHERLOCK_HOMBRE_DE_ACERO"].get("resultado") == "METODO_RIGOR"
    assert por_ataque["SHERLOCK_HOMBRE_DE_ACERO"].get("rival") == "SEG"


def test_run_volteo_reabre_mayeutica_sin_cerrar_sola():
    """Ablar d1 derriba al líder (cambios_de_lider 1): la reapertura mayéutica
    reevalúa en una ronda adicional y el superviviente se reconfirma; la
    derrota no cierra sola."""
    dh = _load_esteroides()
    rows = [
        {"family": "TOP", "rank_fusion": 10.0,
         "features": {"d1": 0.1, "d2": 0.9}},
        {"family": "SEG", "rank_fusion": 9.0,
         "features": {"d1": 0.9, "d2": 0.1}},
    ]
    result = {"predictor": {"candidates": rows, "dimensions": ["d1", "d2"]}}
    out = dh.run({"case_id": "TEST_VOLTEO", "cuts": []}, result)
    aquiles = next(a for a in out.get("ataques") or []
                   if a.get("ataque") == "AQUILES_DIMENSIONAL")
    assert aquiles.get("cambios_de_lider") == 1, aquiles
    reap = out.get("reapertura_iterativa") or {}
    assert reap.get("punto_fijo") is True, reap
    assert reap.get("iteraciones") == 2, reap
    assert reap.get("victoria_del_decimo_hombre_no_cierra_sola") is True
    hist = reap.get("historial") or []
    assert hist[1].get("reabierta") is True, hist
    assert hist[1].get("motivo", "").startswith(
        "UN_CONTRAFACTUAL_DERRIBO_LA_CANDIDATA_BASE"), hist
    # El superviviente final sigue siendo TOP: la derrota no lo sustituyó.
    assert out.get("hipotesis_apuesta", {}).get("candidata") == "TOP", out
    assert out.get("cambio_tras_adversario") is False


def test_run_no_mutacion_h_ni_resultado():
    """La auditoría no escribe H ni toca el resultado que recibe: el cierre
    que ya venía queda exactamente igual después de run()."""
    dh = _load_esteroides()
    case, result = _sano()
    result["H1"] = {"family": "TOP"}
    result["H2"] = {"family": "SEG"}
    result["cierre_final"] = {"grado": "AJUSTADA",
                              "objeciones": [{"fuente": "LOGICA_COPI"}]}
    antes = json.dumps(result, sort_keys=True, default=str)
    out = dh.run(case, result)
    assert json.dumps(result, sort_keys=True, default=str) == antes
    assert "decimo_hombre_esteroides" not in result
    assert out.get("can_decide_H") is False
    assert out.get("rewrites_H") is False
    assert out.get("rewrites_apuesta_original") is False


def test_constantes_y_sha_del_plugin():
    dh = _load_esteroides()
    assert dh.VERSION == "1.1.0-20261009-PATCH05"
    assert dh.CANON_LOCK == {"Engine_V5": False, "patterns_244": False,
                             "FREEZE": False, "PAC": False, "H1_H2": False,
                             "apuesta": False}
    assert _sha256(ESTEROIDES).startswith(SHA_ESTEROIDES)
    assert _sha256(MOTOR_DIR / "Engine_V5_CANONICO_SOLO.py").startswith(SHA_ENGINE)
    assert _sha256(MOTOR_DIR / "patterns_final_v14.json").startswith(SHA_PATTERNS)


# ------------------------------------------------------------------ 2) estático: el cableado existe
def test_estatico_cableado_en_unico():
    src = UNICO.read_text(encoding="utf-8")
    assert 'result["decimo_hombre_esteroides"]' in src
    assert "ESTEROIDES_GUARDIAN" in src
    assert '"esteroides_modo"' in src
    inicio = src.index("# PATCH 017 — Décimo Hombre con esteroides")
    fin = src.index("# U3_predictibilidad", inicio)
    seccion = src[inicio:fin]
    # La rama else del apagado: NO_CONFIGURADO visible, no silencio.
    assert '"NO_CONFIGURADO"' in seccion, seccion
    assert "apagado por ESTEROIDES_GUARDIAN=off" in seccion, seccion
    assert '"esteroides_modo"' in seccion, seccion
    assert "_esteroides_modo" in seccion, seccion
    assert 'if _esteroides_modo == "activo":' in seccion, seccion


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
    env.pop("ESTEROIDES_GUARDIAN", None)
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


def test_corrida_real_ejecuta_esteroides(tmp_path):
    out = tmp_path / "resultado_esteroides.json"
    res = _corre_estandar(THEMISTOCLES, "ESTEROIDES_SMOKE", out)
    dh = res.get("decimo_hombre_esteroides") or {}
    assert dh.get("status") == "EJECUTADO_CIERRE_ADVERSARIAL", dh
    assert dh.get("modo") == "activo", dh
    assert dh.get("version") == "1.1.0-20261009-PATCH05", dh
    assert dh.get("can_decide_H") is False
    assert dh.get("decision_de_proceso") == \
        "CONCLUSION_OPERACIONAL_CERRADA_CON_TRAZABILIDAD", dh
    assert _ataques(dh) == ATAQUES_THEMISTOCLES, dh
    ap = dh.get("hipotesis_apuesta") or {}
    assert ap.get("candidata") == "arquetipo_el_gobernante", ap
    assert ap.get("no_equivale_a_verdad_demostrada") is True
    assert dh.get("cambio_tras_adversario") is False
    diag = dh.get("diagnosticos") or {}
    assert diag.get("copi") == "VALIDO", diag
    assert diag.get("sherlock") == "METODO_RIGOR", diag
    assert diag.get("actual_counterfactual_rankings") == 53, diag
    assert diag.get("source_counterfactuals_executed") == 10, diag
    assert diag.get("dimension_counterfactuals_executed") == 42, diag
    assert diag.get("token_core_counterfactual_executed") is True, diag
    assert diag.get("token_core_counterfactual_ranked") is True, diag
    assert diag.get("adversarial_defeats_of_baseline") == 0, diag
    assert diag.get("adversarial_coverage_complete") is True, diag
    assert diag.get("score_recalculation_matches_original") is True, diag
    # H intacto: la auditoría post-cierre solo marca, no reescribe nada.
    assert (res.get("H1") or {}).get("family") == "arquetipo_el_gobernante"
    assert (res.get("H2") or {}).get("family") == "13_enemistad_de_parientes"
    assert (res.get("cierre_final") or {}).get("grado") == "AJUSTADA"
    # La fila de componentes lo registra como ejecutado, con el modo visible.
    comp = _componente(res, "decimo_hombre_esteroides_mayeutica_v1.py")
    assert comp is not None and comp.get("status") == "EXECUTED_WITH_CONCLUSION", comp
    assert comp.get("esteroides_modo") == "activo", comp
    assert comp.get("can_decide_H") is False
    assert comp.get("n_attacks") == 8, comp
    assert comp.get("n_real_counterfactual_rankings") == 53, comp
    assert comp.get("decision_de_proceso") == \
        "CONCLUSION_OPERACIONAL_CERRADA_CON_TRAZABILIDAD", comp


def test_bypass_esteroides_off_queda_marcado_no_configurado(tmp_path):
    out = tmp_path / "resultado_esteroides_off.json"
    res = _corre_estandar(THEMISTOCLES, "ESTEROIDES_BYPASS", out,
                          {"ESTEROIDES_GUARDIAN": "off"})
    dh = res.get("decimo_hombre_esteroides")
    assert dh is not None, "el bypass no debe borrar el bloque en silencio"
    assert dh.get("status") == "NO_CONFIGURADO", dh
    assert dh.get("modo") == "off", dh
    assert dh.get("can_decide_H") is False
    # Sin ataques ni decisión: el apagado no debe leerse como auditoría.
    assert dh.get("ataques") == [], dh
    assert "hipotesis_apuesta" not in dh, dh
    comp = _componente(res, "decimo_hombre_esteroides_mayeutica_v1.py")
    assert comp is not None and comp.get("status") == "NO_CONFIGURADO", comp
    assert comp.get("esteroides_modo") == "off", comp
    assert comp.get("n_attacks") == 0, comp
    # H intacta e idéntica al baseline; el resto de guardianes sigue corriendo.
    assert (res.get("H1") or {}).get("family") == "arquetipo_el_gobernante"
    assert (res.get("H2") or {}).get("family") == "13_enemistad_de_parientes"
    g = res.get("guardianes") or {}
    assert g.get("status") == "EXECUTED", g
    bloques = {b.get("guardian") for b in g.get("bloques") or []}
    assert "LOGICA_COPI" in bloques, bloques
    assert "DECIMO_HOMBRE_LATENCIA" in bloques, bloques
    # El cierre final no cambia de grado sin la auditoría: la auditoría no
    # retiene ni reescribe el cierre.
    assert (res.get("cierre_final") or {}).get("grado") == "AJUSTADA"


# ------------------------------------------------------------------ 4) unidad: la auditoría no retiene el cierre
def test_unidad_auditoria_no_retiene_ni_reescribe_cierre():
    """La auditoría corre DESPUÉS del cierre final: su salida no puede
    retenerlo ni reescribirlo. Con cierre AJUSTADA y H fijas, run() deja el
    cierre y las H exactamente iguales y su conclusión es aparte."""
    dh = _load_esteroides()
    case, result = _sano()
    result["H1"] = {"family": "TOP"}
    result["H2"] = {"family": "SEG"}
    result["cierre_final"] = {"grado": "AJUSTADA",
                              "objeciones": [{"fuente": "LOGICA_COPI"}]}
    antes = json.dumps({k: result[k] for k in ("H1", "H2", "cierre_final")},
                       sort_keys=True, default=str)
    out = dh.run(case, result)
    despues = json.dumps({k: result[k] for k in ("H1", "H2", "cierre_final")},
                         sort_keys=True, default=str)
    assert despues == antes
    assert out.get("hipotesis_apuesta", {}).get("candidata") == "TOP", out
    assert out.get("hipotesis_apuesta", {}).get(
        "no_equivale_a_verdad_demostrada") is True
    assert out.get("can_decide_H") is False
    assert out.get("rewrites_H") is False
    assert out.get("rewrites_apuesta_original") is False


def test_unidad_registro_no_configurado_sin_decision_ni_hipotesis():
    """El registro del bypass no debe confundirse con una auditoría: no trae
    decisión de proceso ni hipótesis de apuesta, solo el motivo de apagado."""
    registro = {"version": "1.1.0-20261009-PATCH05", "status": "NO_CONFIGURADO",
                "file": "decimo_hombre_esteroides_mayeutica_v1.py", "modo": "off",
                "motivo": "apagado por ESTEROIDES_GUARDIAN=off",
                "can_decide_H": False, "rewrites_H": False,
                "rewrites_apuesta_original": False,
                "ataques": [], "decision_de_proceso": "NO_CONFIGURADO"}
    assert registro.get("status") == "NO_CONFIGURADO"
    assert registro.get("modo") == "off"
    assert registro.get("ataques") == []
    assert "hipotesis_apuesta" not in registro
    assert registro.get("decision_de_proceso") == "NO_CONFIGURADO"
    assert registro.get("can_decide_H") is False
