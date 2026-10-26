import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "casos" / "fabrica"))
import fabrica


def test_sidecars_no_cuentan_como_casos(tmp_path):
    fila = {"componente": "sidecar_caldero_busqueda_arquetipos.py", "estado_busqueda_externa": "EJECUTADO", "severidad": "OK"}
    (tmp_path / "C1__w0.json").write_text(json.dumps({"laterales_unico": {"post": {"estado_verificado": {"filas": [fila]}}}}))
    (tmp_path / "C1__w0_RECIBO_EJECUCION.json").write_text(json.dumps({"status": "COMPLETED"}))
    (tmp_path / "C1__w0_CEB_LEDGER_MANIFIESTO.json").write_text(json.dumps({}))
    assert [p.name for p in fabrica._corridas_caso(tmp_path)] == ["C1__w0.json"]
    assert set(fabrica.compuerta_piezas(tmp_path)["por_caso"]) == {"C1__w0"}
