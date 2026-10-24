"""Pruebas de la capa consulta_dirigida (sin red, sin motor). python3 -m pytest tests/test_consulta_dirigida_v1.py"""
import copy, importlib.util, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("cd", str(ROOT / "capa_llm" / "consulta_dirigida_v1.py"))
CD = importlib.util.module_from_spec(spec); spec.loader.exec_module(CD)
R = CD.Recursos(ROOT / "motor")
CASE = {"case_id": "T", "question": "q", "z90_date": "1500-12-31",
        "cuts": [{"id": "C1", "date": "1490-01-01", "P": [["aprendizaje", 0.8]], "A": [], "C": []},
                 {"id": "C2", "date": "1500-01-01", "P": [["aprendizaje", 0.8]], "A": [], "C": [["escasez", 0.7]]},
                 {"id": "C3", "date": "1510-01-01", "P": [["aprendizaje", 0.8]], "A": [], "C": []}]}

def _q(tipo="AGENTES_PRESENTES", corte="C1"):
    P = CD.construir_preguntas(CASE, R)
    return next(q for q in P["preguntas"] if q["tipo"] == tipo and q["corte"] == corte)

def test_no_pregunta_despues_de_Z():
    P = CD.construir_preguntas(CASE, R)
    assert P["huecos"]["z_idx"] == 1
    assert all(q["corte"] != "C3" for q in P["preguntas"])

def test_plantillas_validas_y_pregunta_mala_rechazada():
    for q in CD.construir_preguntas(CASE, R)["preguntas"]:
        assert q["validacion"] == []
    mala = "Hasta el corte C1 (nada posterior a la fecha del corte): ¿cuál es la hipótesis y qué apuesta gana? ¿qué pasó después?"
    m = CD.validar_pregunta(mala, R)
    assert any(x.startswith("Q_HIPOTESIS") for x in m) and any(x.startswith("Q_FUTURO") for x in m)
    assert any(x.startswith("Q_ETIQUETA_244") for x in CD.validar_pregunta("Hasta el corte C1 (nada posterior a X): ¿es arquetipo_el_sabio?", R))

def _f(texto, tokens=(), fuente="t", q=None):
    return CD.filtrar_respuesta({"texto": texto, "tokens": list(tokens), "fuente": fuente}, q or _q(), CASE, R)

def test_filtros_rechazan():
    assert _f("Más tarde sería condenado y llegaría a ser famoso.")["estado"] == "RECHAZADA"
    assert _f("La hipótesis probable es arquetipo_el_sabio, apuesta segura.")["estado"] == "RECHAZADA"
    assert _f("En 1550 un tribunal abre un proceso contra el protagonista.")["estado"] == "RECHAZADA"
    assert _f("Como es sabido por los historiadores fue un precursor.")["estado"] == "RECHAZADA"
    assert _f("Un grupo de colegas apoya al protagonista.", fuente="")["estado"] == "RECHAZADA"
    assert _f("Muere el protagonista en su casa con su familia.")["estado"] == "RECHAZADA"  # C1 no es el último corte

def test_nombre_y_anio_pasado_se_neutralizan():
    r = _f("En 1485 está presente Federico Gonzaga con un grupo de colegas que lo apoyan.")
    assert r["estado"] == "ACEPTADA_NEUTRALIZADA"
    assert "Gonzaga" not in r["texto_neutral"] and "1485" not in r["texto_neutral"]

def test_tokens():
    r = _f("Un consejo local supervisa los encargos del protagonista.", tokens=["arquetipo_el_gobernante", "1588", "inventado", "alianza", "proteccion", "dependencia"])
    assert r["tokens_aceptados"] == ["alianza", "proteccion"]

def test_offline_no_cambia_nada_y_no_escribe_H():
    aug, tr, side = CD.aplicar(copy.deepcopy(CASE), CD.AdaptadorOffline(), R)
    assert aug == CASE and tr["verificacion_no_escribe_H"] == "OK"
    mal = copy.deepcopy(CASE); mal["question"] = "otra"; mal["external_lights"] = [{"token": "x"}]
    v = CD.verificar_no_escribe_H(CASE, mal, 1)
    assert v and any("CLAVES_DE_CASO_CAMBIADAS" in x for x in v)
    mal2 = copy.deepcopy(CASE); mal2["cuts"][2]["hecho"] = "x"
    assert any("POSTERIOR_A_Z" in x for x in CD.verificar_no_escribe_H(CASE, mal2, 1))

if __name__ == "__main__":  # sin pytest: python3 tests/test_consulta_dirigida_v1.py
    import sys
    fallos = 0
    for n, f in sorted(globals().items()):
        if n.startswith("test_") and callable(f):
            try: f(); print("PASS", n)
            except AssertionError as e: fallos += 1; print("FAIL", n, e)
    sys.exit(1 if fallos else 0)
