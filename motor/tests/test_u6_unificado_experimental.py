from __future__ import annotations
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "motor" / "u6" / "U6_UNIFICADO_EXPERIMENTAL.py"

def load():
    spec = importlib.util.spec_from_file_location("u6_unificado_experimental_test", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod

def test_experimental_mode_clears_ablations_and_disables_strict_gate(monkeypatch):
    monkeypatch.setenv("CONSOLIDADO_OFF", "geometria,polti_caldero")
    monkeypatch.setenv("FAMILIAS_TOKENS", "0")
    monkeypatch.setenv("MODO_ESTRICTO", "1")
    monkeypatch.setenv("LAT_memento", "0")
    mod = load()
    state = mod.activar_modo_unificado()
    assert state["consolidado_off"] == ""
    assert state["familias_tokens"] == "1"
    assert state["modo_estricto"] == "0"
    assert __import__("os").environ["LAT_memento"] == "1"

def test_canonical_artifacts_exist_and_are_not_replaced():
    mod = load()
    assert mod.ENGINE.is_file()
    assert mod.CANON.is_file()
    assert mod.PATTERNS.is_file()

# Trigger the paired ACTIVA_MUDA diagnostic workflow.
