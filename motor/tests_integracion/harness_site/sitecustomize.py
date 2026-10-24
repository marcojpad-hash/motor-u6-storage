"""Harness de prueba (NO motor): si U6_HARNESS_TORTUGAS_FALLA=1, al importarse
MOTOR_V15_3_UNICO_20260927 se reemplaza _tortugas_guardianes por una función que
lanza excepción. El motor captura el error (status ERROR) y la compuerta de
continuidad del runner debe pausar. No se edita ningún archivo del motor."""
import os, sys, importlib.abc, importlib.machinery
_TARGET = "MOTOR_V15_3_UNICO_20260927"
if os.environ.get("U6_HARNESS_TORTUGAS_FALLA") == "1":
    def _falla(*a, **k):
        raise RuntimeError("HARNESS_TORTUGAS_FORZADO_A_FALLAR")
    class _Loader(importlib.abc.Loader):
        def __init__(self, inner): self.inner = inner
        def create_module(self, spec): return self.inner.create_module(spec)
        def exec_module(self, module):
            self.inner.exec_module(module)
            module._tortugas_guardianes = _falla
            module._HARNESS_TORTUGAS_FALLA = True
    class _Finder(importlib.abc.MetaPathFinder):
        def find_spec(self, name, path, target=None):
            if name != _TARGET: return None
            spec = importlib.machinery.PathFinder.find_spec(name, path)
            if spec is not None: spec.loader = _Loader(spec.loader)
            return spec
    sys.meta_path.insert(0, _Finder())

# U6_HARNESS_BUSCADOR_MOCK=1: buscador simulado SIN RED. Se precarga sys.modules["caldero_buscadores"]
# (el sidecar reutiliza el módulo ya cargado) con una cadena cuyo 1er proveedor falla y el 2º devuelve
# resultados SINTÉTICOS marcados como mock. Además se bloquea toda conexión de red del proceso.
if os.environ.get("U6_HARNESS_BUSCADOR_MOCK") == "1":
    import socket, types, hashlib
    def _no_net(*a, **k):
        raise OSError("HARNESS_SIN_RED")
    socket.socket.connect = _no_net; socket.create_connection = _no_net
    _m = types.ModuleType("caldero_buscadores")
    class _Cadena:
        def __init__(self, S, sel): self.S = S; self.sel = sel; self.last_receipt = {"provider": "mock_chain", "status": "NOT_RUN"}
        def search(self, query):
            att = [{"provider": "mock_falla", "status": "FAILED", "error": "simulado"}]
            rows = [self.S(url=f"https://mock.invalid/{i}", title=f"mock {i}", snippet="leadership rivalry ambition sacrifice strategy",
                           metadata={"provider": "mock_ok", "mock": True}) for i in range(3)]
            att.append({"provider": "mock_ok", "status": "EXECUTED"})
            self.last_receipt = {"provider": "mock_ok", "status": "EXECUTED", "query_count": 1, "result_count": 3, "query": query,
                                 "query_sha256": hashlib.sha256(query.encode("utf-8")).hexdigest(), "consultado_utc": "MOCK",
                                 "urls": [r.url for r in rows], "selector": self.sel, "attempts": att, "llm": False}
            return rows
    _m.crear_cadena = lambda S, sel=None: _Cadena(S, sel)
    _m.MOCK = True
    sys.modules["caldero_buscadores"] = _m
