#!/usr/bin/env python3
"""Unit OFFLINE: cadena de buscadores agnóstica (fallback) con proveedores simulados; la red queda bloqueada."""
import importlib.util, socket, urllib.request
from dataclasses import dataclass, field
from pathlib import Path
import pytest
P = Path(__file__).resolve().parents[1] / "motor" / "caldero_buscadores.py"
spec = importlib.util.spec_from_file_location("cb_test", P); CB = importlib.util.module_from_spec(spec); spec.loader.exec_module(CB)


@dataclass
class S:
    url: str; title: str = ""; snippet: str = ""; metadata: dict = field(default_factory=dict)


@pytest.fixture(autouse=True)
def sin_red(monkeypatch):
    def no(*a, **k): raise AssertionError("RED_PROHIBIDA_EN_TEST")
    monkeypatch.setattr(urllib.request, "urlopen", no); monkeypatch.setattr(socket.socket, "connect", no)
    for k in ("CALDERO_BUSCADOR", "SEARCH_PROVIDER", "EXA_API_KEY", "BRAVE_API_KEY", "SERPER_API_KEY", "TAVILY_API_KEY"):
        monkeypatch.delenv(k, raising=False)


def _prov(nombre, comportamiento):
    class X(CB._Base):
        name = nombre
        def _rows(self, q):
            if comportamiento == "falla": raise ConnectionError("simulado")
            if comportamiento == "vacio": return 200, []
            return 200, [{"url": f"https://mock.invalid/{nombre}/{i}", "title": "t", "snippet": "s"} for i in range(3)] + [{"url": "ftp://x"}]
    return X


def test_fallback_usa_el_primero_con_resultados(monkeypatch):
    monkeypatch.setattr(CB, "LIBRES", {"a": _prov("a", "falla"), "b": _prov("b", "vacio"), "c": _prov("c", "ok"), "d": _prov("d", "ok")})
    ch = CB.CadenaBuscadores(["a", "b", "c", "d"], S)
    rows = ch.search("consulta ciega")
    r = ch.last_receipt
    assert r["provider"] == "c" and r["status"] == "EXECUTED" and len(rows) == 3 and all(x.url.startswith("https://") for x in rows)
    assert [a["status"] for a in r["attempts"]] == ["FAILED", "FAILED_NO_RESULTS", "EXECUTED"]
    assert r["query_sha256"] == CB._sha("consulta ciega") and r["llm"] is False and r["selector"] == "auto"


def test_todos_fallan_no_inventa(monkeypatch):
    monkeypatch.setattr(CB, "LIBRES", {"a": _prov("a", "falla"), "b": _prov("b", "vacio")})
    ch = CB.CadenaBuscadores(["a", "b"], S)
    with pytest.raises(RuntimeError):
        ch.search("q")
    assert ch.last_receipt["status"] == "FAILED_ALL_PROVIDERS" and ch.last_receipt["result_count"] == 0


def test_con_clave_se_salta_sin_clave_y_selector(monkeypatch):
    monkeypatch.setattr(CB, "LIBRES", {**CB.LIBRES, "c": _prov("c", "ok")})
    monkeypatch.setenv("CALDERO_BUSCADOR", "exa,c")
    ch = CB.crear_cadena(S)
    ch.search("q")
    assert ch.last_receipt["attempts"][0]["status"] == "SALTADO_SIN_CLAVE" and ch.last_receipt["selector"] == "exa,c"
    with pytest.raises(ValueError):
        CB.crear_cadena(S, "no_existe")
    assert CB.crear_cadena(S, "auto").nombres == CB.ORDEN_AUTO
    assert CB.crear_cadena(S, "duckduckgo").nombres == ["ddgs", "ddg", "ddg_lite"]


def test_query_vacia_rechazada():
    with pytest.raises(ValueError):
        _prov("z", "ok")(S).search("  ")
