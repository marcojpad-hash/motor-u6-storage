#!/usr/bin/env python3
"""Arnés de calibración: matemática de Laplace/Brier/recorte con registros SINTÉTICOS de prueba (no son desenlaces reales)."""
import importlib.util
from pathlib import Path
P = Path(__file__).resolve().parents[1] / "calibracion" / "arnes_calibracion.py"
spec = importlib.util.spec_from_file_location("arnes_cal", P); A = importlib.util.module_from_spec(spec); spec.loader.exec_module(A)


def _reg():
    def r(h1, hs, esc, hesc):
        return {"H1": h1, "hipotesis": [{"familia": h, "soporte_estructural_relativo": 1.0 / len(hs)} for h in hs],
                "escenarios": [{"escenario": esc, "hipotesis": hesc, "soporte": 1.0}], "escenario_principal": esc, "hipotesis_escenario_principal": hesc}
    reg = {"version": A.VERSION, "pesos": [0.0], "casos": {
        "x1": {"por_peso": {"0": r("a", ["a", "b"], "CONTINUIDAD_ASCENDENTE", ["a", "b"])}},
        "x2": {"por_peso": {"0": r("c", ["c", "d"], "MESETA_O_ESTABILIZACION", ["c"])}}}, "errores": []}
    reg["sha256_registro"] = A._sha_obj({k: v for k, v in reg.items() if k != "sha256_registro"})
    return reg


def test_laplace_y_recorte():
    assert A.laplace(0, 0) == 0.5 and A.clip(1.0) == 0.95 and A.clip(0.0) == 0.05
    assert abs(A.laplace(3, 3) - 0.8) < 1e-12


def test_evaluar_tasas_brier_en_rango():
    out = A.evaluar_registro(_reg(), {"x1": {"familias": ["b"]}, "x2": {"familias": ["c"]}})
    w = out["por_peso"]["0"]
    assert out["integridad_registro"] == "OK" and out["n_casos_con_desenlace"] == 2
    assert w["H1"]["aciertos"] == 1 and w["set"]["aciertos"] == 2 and w["escenario"]["aciertos"] == 2
    for k in ("H1", "set", "escenario"):
        assert 0.05 <= w[k]["tasa_laplace"] <= 0.95 and 0.0 <= w[k]["brier_loo_laplace"] <= 1.0
    assert out["aviso_muestra"].startswith("MUESTRA_INSUFICIENTE")


def test_registro_modificado_se_detecta_y_casos_sin_desenlace_no_cuentan():
    reg = _reg(); reg["casos"]["x1"]["por_peso"]["0"]["H1"] = "b"
    out = A.evaluar_registro(reg, {"x1": {"familias": ["b"]}})
    assert out["integridad_registro"] == "REGISTRO_MODIFICADO_TRAS_SELLO"
    assert out["n_casos_con_desenlace"] == 1 and out["n_casos_sellados_sin_desenlace"] == 1


def test_input_con_desenlace_se_rechaza():
    assert A._tiene_desenlace({"cuts": [], "meta": {"outcome": "x"}})
    assert not A._tiene_desenlace({"cuts": [{"id": "C1", "P": [["t", 0.5]]}]})


def test_copia_sin_geometria_peso_un_solo_peso_y_rechaza_barrido(tmp_path):
    assert A.motor_soporta_peso() is False and A.PESOS_DEFECTO == [0.0]
    (tmp_path / "c.json").write_text('{"case_id":"c","cuts":[{"id":"C1","P":[["t",0.5]]}]}', encoding="utf-8")
    assert A.correr(tmp_path, tmp_path / "out", [0.0, 0.1]) == 4 and not (tmp_path / "out").exists()


def test_validar_seco_no_sella(tmp_path):
    (tmp_path / "ok.json").write_text('{"case_id":"ok","cuts":[{"id":"C1","P":[["t",0.5]]}]}', encoding="utf-8")
    (tmp_path / "malo.json").write_text('{"case_id":"m","outcome":"x","cuts":[{"id":"C1"}]}', encoding="utf-8")
    assert A.validar(tmp_path) == 1 and not list(tmp_path.glob("REGISTRO*"))


def test_extraer_forma_de_esta_copia():
    r = {"H1": {"family": "a"}, "H2": {"family": "b"}, "hipotesis": [{"familia": "a", "soporte_estructural_relativo": 0.6}],
         "salida_interpretable": {"apuesta_multiescenario": {"estado": "APUESTA_MULTIESCENARIO_SELLABLE",
             "escenarios": [{"escenario": "E", "hipotesis_que_convergen": ["a"], "soporte_estructural_agregado": 1.0}],
             "apuesta_principal": {"escenario": "E", "hipotesis_que_convergen": ["a"]}}}}
    x = A.extraer(r, 0.0)
    assert x["H1"] == "a" and x["escenario_principal"] == "E" and x["hipotesis_escenario_principal"] == ["a"] and len(x["huella_salida_sha256"]) == 64
