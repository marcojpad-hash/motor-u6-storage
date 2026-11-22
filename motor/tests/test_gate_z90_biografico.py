import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1] if HERE.name == "tests" and HERE.parent.name == "motor" else HERE
GATE_PATH = ROOT / "motor" / "calibracion" / "gate_z90.py"
if not GATE_PATH.exists():
    GATE_PATH = HERE / "gate_z90.py"
spec = importlib.util.spec_from_file_location("gate_z90_under_test", GATE_PATH)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def _ev(claim="Hecho conocido antes del corte.", claim_date="1758-01-01",
        source_date="1758-01-01", tipo="secundaria"):
    return {
        "afirmacion": claim,
        "source_url": "https://en.wikipedia.org/wiki/Example",
        "source_date": source_date,
        "claim_date": claim_date,
        "tipo_fuente": tipo,
        "conocido_en_Z": "sí",
    }


def _case():
    return {
        "case_id": "MOZART_Z90_GATE_TEST",
        "question": "¿Qué trayectoria sigue el sujeto?",
        "modo_z": "historico",
        "fecha_nacimiento": "1756-01-27",
        "fecha_muerte": "1791-12-05",
        "z_trabajo": "1788-05-04",
        "z90_date": "1788-05-04",
        "preparacion_ciega": {
            "preparador_entrada": "Preparador-A",
            "custodio_destino": "Custodio-B",
            "vio_destino": False,
        },
        "cuts": [
            {
                "id": "C1",
                "date": "1760-01-01",
                "window_start": "1756-01-27",
                "hecho": "Hecho histórico de 1758.",
                "evidencia": [_ev()],
            },
            {
                "id": "C2",
                "date": "1788-05-04",
                "window_start": "1756-01-27",
                "hecho": "Hecho histórico de 1780.",
                "evidencia": [_ev(claim_date="1780-01-01", source_date="1780-01-01")],
            },
        ],
    }


def test_mozart_z90_calculado_y_estructura_valida():
    assert gate.calcular_z90("1756-01-27", "1791-12-05").isoformat() == "1788-05-04"
    assert gate.validar_entrada(_case()) == []


def test_rechaza_z_trabajo_o_z90_date_incorrectos():
    case = _case()
    case["z_trabajo"] = "1788-05-05"
    errs = gate.validar_entrada(case)
    assert any("z_trabajo" in e and "no coincide" in e for e in errs)
    case = _case()
    case["z90_date"] = "1788-05-05"
    errs = gate.validar_entrada(case)
    assert any("z90_date" in e and "no coincide" in e for e in errs)


def test_rechaza_fechas_biograficas_ausentes_o_invalidas():
    case = _case()
    del case["fecha_nacimiento"]
    assert any("fecha_nacimiento" in e for e in gate.validar_entrada(case))
    case = _case()
    case["fecha_muerte"] = "1791-02-30"
    assert any("fecha_muerte" in e for e in gate.validar_entrada(case))


def test_rechaza_muerte_igual_o_anterior_al_nacimiento():
    case = _case()
    case["fecha_muerte"] = case["fecha_nacimiento"]
    assert any("fecha_muerte debe ser posterior" in e for e in gate.validar_entrada(case))


def test_rechaza_ventana_no_acumulativa():
    case = _case()
    case["cuts"][1]["window_start"] = "1760-01-01"
    assert any("window_start debe ser el nacimiento" in e for e in gate.validar_entrada(case))


def test_rechaza_ultimo_corte_antes_de_z90():
    case = _case()
    case["cuts"][-1]["date"] = "1788-05-03"
    assert any("no en Z90" in e for e in gate.validar_entrada(case))


def test_rechaza_cierres_no_ordenados():
    case = _case()
    case["cuts"][0]["date"] = "1780-01-01"
    case["cuts"][1]["date"] = "1770-01-01"
    assert any("no estrictamente crecientes" in e for e in gate.validar_entrada(case))


def test_rechaza_corte_posterior_a_z90():
    case = _case()
    case["cuts"][-1]["date"] = "1788-05-05"
    assert any("posterior a Z90" in e for e in gate.validar_entrada(case))


def test_rechaza_claim_posterior_al_cierre_del_corte():
    case = _case()
    case["cuts"][0]["evidencia"][0]["claim_date"] = "1761-01-01"
    assert any("posterior al cierre del corte" in e for e in gate.validar_entrada(case))


def test_rechaza_fuente_primaria_posterior_al_cierre_del_corte():
    case = _case()
    case["cuts"][0]["evidencia"][0]["tipo_fuente"] = "primaria"
    case["cuts"][0]["evidencia"][0]["source_date"] = "1761-01-01"
    assert any("primaria fechada" in e for e in gate.validar_entrada(case))


def test_rechaza_cortes_con_fecha_parcial_en_historico():
    case = _case()
    case["cuts"][0]["date"] = "1760"
    assert any("date debe ser fecha exacta" in e for e in gate.validar_entrada(case))


def test_rechaza_f007_sin_birth_death():
    case = {
        "case_id": "F007_INCOMPLETO",
        "modo_z": "historico",
        "z_trabajo": "1888-12-31",
        "z90_date": "1888-12-31",
        "preparacion_ciega": {
            "preparador_entrada": "A",
            "custodio_destino": "B",
            "vio_destino": False,
        },
        "cuts": [
            {"id": "C1", "date": "1886", "evidencia": [_ev(claim_date="1886", source_date="1886")]},
            {"id": "C2", "date": "1888-02", "evidencia": [_ev(claim_date="1888-02", source_date="1888-02")]},
        ],
    }
    errs = gate.validar_entrada(case)
    assert any("fecha_nacimiento" in e for e in errs)
    assert any("fecha_muerte" in e for e in errs)


def test_rechaza_window_start_ausente():
    case = _case()
    del case["cuts"][0]["window_start"]
    assert any("window_start ausente" in e for e in gate.validar_entrada(case))


def test_no_exige_datos_de_muerte_en_modo_vivo():
    case = {
        "case_id": "VIVO",
        "modo_z": "vivo",
        "z_trabajo": "2026-11-21",
        "z90_date": "2026-11-21",
        "cuts": [
            {
                "id": "C1",
                "date": "2026-11-21",
                "evidencia": [{
                    "afirmacion": "Hecho observado.",
                    "source_url": "https://example.org/source",
                    "source_date": "2026-11-20",
                    "claim_date": "2026-11-20",
                    "tipo_fuente": "primaria",
                    "conocido_en_Z": "sí",
                }],
            },
        ],
    }
    assert gate.validar_entrada(case) == []
