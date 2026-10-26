import importlib.util, json, sys
from pathlib import Path
R = Path(__file__).resolve().parent.parent
def _m(name, p):
    spec = importlib.util.spec_from_file_location(name, p); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
sys.path.insert(0, str(R / "motor/motor"))
lu = _m("lu2", R / "motor/motor/laterales_unico_v1.py")
fa = _m("fa2", R / "casos/fabrica/fabrica.py")

def test_estados_no_ejecutados_son_fallo():
    for e in ("SIMULADO_FIXTURE", "NO_INVOCADO", "INTENTADO_FALLIDO", "OMITIDO_POR_CONDICION"):
        a = lu.alerta_ejecucion(e)
        assert a["incumplimiento"] and a["debe_ejecutarse"] and a["severidad"] == "FALLO_EJECUCION" and e in a["alerta"]

def test_ejecutado_ok_y_omision_contractual():
    assert lu.alerta_ejecucion("EJECUTADO")["incumplimiento"] is False
    a = lu.alerta_ejecucion("OMITIDO_POR_CONDICION", contrato_permite_omision=True)
    assert a["incumplimiento"] is False and a["severidad"] == "INFO_OMISION_CONTRACTUAL"

def _corrida(tmp, nombre, fila):
    (tmp / f"{nombre}.json").write_text(json.dumps({"x": {"filas": [fila] if fila else []}}), encoding="utf-8")

def test_compuerta_fabrica(tmp_path):
    C = "sidecar_caldero_busqueda_arquetipos.py"
    _corrida(tmp_path, "a", {"componente": C, "estado_busqueda_externa": "EJECUTADO", **lu.alerta_ejecucion("EJECUTADO")})
    _corrida(tmp_path, "b", {"componente": C, "estado_busqueda_externa": "SIMULADO_FIXTURE", **lu.alerta_ejecucion("SIMULADO_FIXTURE")})
    _corrida(tmp_path, "c", None)
    g = fa.compuerta_caldero(tmp_path, True)
    assert g["veredicto"] == "FALLO_EJECUCION_CALDERO" and g["incumplimientos"] == ["b", "c"]
    assert g["por_caso"]["c"]["estado"] == "SIN_RECIBO_CEB"
    assert fa.compuerta_caldero(tmp_path, False)["incumplimientos"] == []
