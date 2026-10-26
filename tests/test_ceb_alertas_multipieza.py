import importlib.util, json, sys
from pathlib import Path
R = Path(__file__).resolve().parent.parent
def _m(name, p):
    spec = importlib.util.spec_from_file_location(name, p); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
sys.path.insert(0, str(R / "motor/motor"))
lu = _m("lu3", R / "motor/motor/laterales_unico_v1.py")
fa = _m("fa3", R / "casos/fabrica/fabrica.py")

def test_clasificacion_por_estado():
    assert lu.alerta_pieza("ACTIVA")["severidad"] == "OK"
    assert lu.alerta_pieza("ACTIVA_MUDA")["severidad"] == "INFO_CORRIO_SIN_SENAL"
    assert lu.alerta_pieza("SUPERADA")["severidad"] == "INFO_OMISION_CONTRACTUAL"
    for e in ("NO_CORRE", "APAGADA_POR_FLAG", "API_PENDING", "NO_INVOCADO", "SIN_EJECUCION", "NO_ENCONTRADO_EN_STORE", "SIMULADO_FIXTURE"):
        a = lu.alerta_pieza(e); assert a["severidad"] == "FALLO_EJECUCION" and a["incumplimiento"] and a["accion"]
    assert lu.alerta_pieza("ALGO_RARO")["severidad"] == "REQUIERE_CONTRATO"
    assert lu.alerta_pieza("SKIPPED", contrato_permite_omision=True)["incumplimiento"] is False

def test_aplicar_alertas_multipieza_no_pisa_caldero():
    reg = [{"pieza": "lente_souriau", "estado": "NO_CORRE"}, {"pieza": "polti", "estado": "ACTIVA"},
           {"pieza": "stinkbox", "estado": "APAGADA_POR_FLAG"}]
    filas = [{"componente": "pre_h_analogical_search(V0.18)", "estado_verificado": "ACTIVA_MUDA", "declarado_UNICO": "API_PENDING"},
             {"componente": "sidecar_caldero_busqueda_arquetipos.py", "estado_verificado": "ACTIVA", **lu.alerta_ejecucion("SIMULADO_FIXTURE")},
             {"componente": "vecinos_caldero/neighbor_store.py", "estado_verificado": "NO_ENCONTRADO_EN_STORE"}]
    r = lu.aplicar_alertas(reg, filas)
    assert set(r["fallos"]) == {"lente_souriau", "stinkbox", "pre_h_analogical_search(V0.18)", "sidecar_caldero_busqueda_arquetipos.py", "vecinos_caldero/neighbor_store.py"}
    assert r["veredicto"] == "FALLO_EJECUCION_PIEZAS" and filas[1]["alerta"].endswith("SIMULADO_FIXTURE")

def test_compuerta_piezas_lote(tmp_path):
    ok = {"r": [{"pieza": "polti", **lu.alerta_pieza("ACTIVA")}]}
    malo = {"r": [{"pieza": "lente_souriau", "estado": "NO_CORRE", **lu.alerta_pieza("NO_CORRE")},
                  {"componente": "billar", "estado": "X", **lu.alerta_pieza("X")}]}
    (tmp_path / "a.json").write_text(json.dumps(ok)); (tmp_path / "b.json").write_text(json.dumps(malo))
    g = fa.compuerta_piezas(tmp_path)
    assert g["fallos_ejecucion"] == ["lente_souriau"] and g["requiere_contrato"] == ["billar"]
    assert g["por_pieza"]["lente_souriau"]["casos"] == ["b"] and g["veredicto"] == "FALLO_EJECUCION_PIEZAS"
    (tmp_path / "b.json").unlink()
    assert fa.compuerta_piezas(tmp_path)["veredicto"] == "OK"
