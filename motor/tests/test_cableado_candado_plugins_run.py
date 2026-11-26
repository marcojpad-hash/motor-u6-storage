"""V7 (C-F4): el candado de plugins corre al inicio de run().

Antes solo corría en correr_estandar.py (preflight); una llamada directa a
run() lo saltaba. Ahora run() lo ejecuta primero y lo deja en el recibo
(result["candado_plugins"]): un plugin no compilable o que importe el Engine
directo ABORTA la corrida (muro, no aviso).
"""
import importlib.util
import json
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
MOTOR_DIR = ROOT / "motor"
UNICO = MOTOR_DIR / "MOTOR_V15_3_UNICO_20260927.py"


def _load_unico():
    spec = importlib.util.spec_from_file_location("motor_unico_v7_cf4", str(UNICO))
    mod = importlib.util.module_from_spec(spec)
    sys.modules["motor_unico_v7_cf4"] = mod
    spec.loader.exec_module(mod)
    return mod


def test_verificar_candado_plugins_run_ok():
    runner = _load_unico()
    res = runner._verificar_candado_plugins_run(force=True)
    assert res["status"] == "OK", res
    assert res["verificados"] >= 100, res
    assert res["fallos"] == []


def test_candado_bloquea_plugin_corrupto(tmp_path):
    # El candado se prueba contra un BASE temporal (copia de candado_plugins.py
    # + un plugin roto): no se toca el árbol real.
    runner = _load_unico()
    base_tmp = tmp_path / "motor_tmp"
    base_tmp.mkdir()
    shutil.copy2(MOTOR_DIR / "candado_plugins.py", base_tmp / "candado_plugins.py")
    (base_tmp / "plugin_roto_prueba.py").write_text(
        "def rota(:\n    esto no compila\n", encoding="utf-8")
    (base_tmp / "plugin_sano_prueba.py").write_text(
        "VERSION = 'sano'\n", encoding="utf-8")
    base_real = runner.BASE
    runner.BASE = base_tmp
    try:
        # El helper re-ejecuta la copia temporal de candado_plugins.py; la
        # clase de la excepción es la de ESA copia, así que se comprueba por
        # nombre (no por identidad de clase).
        with pytest.raises(Exception) as ei:
            runner._verificar_candado_plugins_run(force=True)
        assert type(ei.value).__name__ == "PluginCorruptoError", ei.value
    finally:
        runner.BASE = base_real
        runner._CANDADO_PLUGINS_CACHE = None


def test_runner_lleva_candado_plugins(tmp_path):
    # Vivo (subproceso correr_estandar.py, THEMISTOCLES): el recibo lleva el
    # candado con status OK y H intacta.
    import os
    import subprocess

    entrada = ROOT / "inputs" / "THEMISTOCLES_FREEZE_480BC_CATALOG_REPAIR_R2.json"
    salida = tmp_path / "resultado_cf4.json"
    r = subprocess.run([sys.executable, "correr_estandar.py", str(entrada),
                        "V7_CF4_SMOKE", str(salida)],
                       cwd=str(ROOT), capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-2000:]
    res = json.loads(salida.read_text(encoding="utf-8"))
    c = res.get("candado_plugins")
    assert c is not None, "sin candado_plugins en una corrida real"
    assert c.get("status") == "OK", c
    assert c.get("verificados", 0) >= 100, c
    assert c.get("fallos") == []
    assert (res.get("H1") or {}).get("family") == "arquetipo_el_gobernante"
    assert (res.get("H2") or {}).get("family") == "13_enemistad_de_parientes"
