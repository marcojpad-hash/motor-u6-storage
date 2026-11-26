"""V7 (C-F3): los except que convierten un fallo de guardián/cierre en bloque
ERROR del recibo llaman a contornar (control_flujo_soluciones) y adjuntan el
plan al bloque. Antes ningún except del runner llamaba jamás a
contornar/aplicar_protocolo: el fallo llegaba solo con el error.
"""
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
MOTOR_DIR = ROOT / "motor"
UNICO = MOTOR_DIR / "MOTOR_V15_3_UNICO_20260927.py"


def _load_unico():
    spec = importlib.util.spec_from_file_location("motor_unico_v7_cf3", str(UNICO))
    mod = importlib.util.module_from_spec(spec)
    sys.modules["motor_unico_v7_cf3"] = mod
    spec.loader.exec_module(mod)
    return mod


def test_plan_contorno_devuelve_plan():
    runner = _load_unico()
    plan = runner._plan_contorno("piedra de prueba: guardián X falló",
                                 contexto="prueba")
    assert plan is not None
    assert plan.get("plugin") == "CONTROL_FLUJO_SOLUCIONES"
    assert plan.get("contornos"), plan
    assert plan.get("formato_respuesta_obligatorio"), plan
    assert plan.get("tipo_piedra"), plan


def test_excepts_cierre_llevan_plan_contorno():
    # Estático: los dos except que emiten bloque ERROR (resolución operativa
    # terminal 017 y cierre final 016) adjuntan plan_contorno.
    src = UNICO.read_text(encoding="utf-8")
    assert src.count('plan_contorno":_plan_contorno(') == 2, (
        "se esperan exactamente 2 adjuntos de plan_contorno (017 y 016)")


def test_except_cierre_final_adjunta_plan():
    # Ejecución: se fuerza el fallo de _cierre_final_020 y el recibo trae el
    # bloque ERROR con su plan de contorno (no solo el error).
    runner = _load_unico()
    caso = json.loads(
        (ROOT / "inputs" / "THEMISTOCLES_FREEZE_480BC_CATALOG_REPAIR_R2.json"
         ).read_text(encoding="utf-8"))
    real = runner._cierre_final_020

    def _falla(*a, **k):
        raise RuntimeError("fallo sintético de prueba en cierre_final_020")

    runner._cierre_final_020 = _falla
    try:
        res = runner.run(caso)
    finally:
        runner._cierre_final_020 = real
    cf = res.get("cierre_final") or {}
    assert cf.get("status") == "ERROR", cf
    plan = cf.get("plan_contorno")
    assert plan is not None, cf
    assert plan.get("plugin") == "CONTROL_FLUJO_SOLUCIONES", plan
    assert plan.get("contornos"), plan
    assert (res.get("H1") or {}).get("family") == "arquetipo_el_gobernante"


def test_contornar_hash_engine_is_hard_stop_not_bypass():
    runner = _load_unico()
    plan = runner._plan_contorno("hash mismatch Engine V5 canonical", contexto="candado")
    assert plan is not None
    assert plan.get("parada_dura") is True
    assert plan.get("accion") == "DIAGNOSTICAR_SIN_EJECUTAR"
    assert not any("BYPASS_HASH_CAMBIO" in str(x) for x in plan.get("contornos") or [])
