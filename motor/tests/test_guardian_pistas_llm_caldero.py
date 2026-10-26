import importlib.util, pathlib
p = pathlib.Path(__file__).resolve().parents[1] / "motor" / "guardian_pistas_llm_caldero_v1.py"
spec = importlib.util.spec_from_file_location("gpl", p); g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)

def test_filtra_identidad_futuro_calendario():
    hints = [{"token": "rivalidad"}, {"token": "pasteur_vacuna"}, "fracaso final", "1885", "https://x.y", "metodicidad"]
    kept, audit = g.filtrar(hints, ["louis pasteur", "pasteur"])
    toks = [h["token"] if isinstance(h, dict) else h for h in kept]
    assert toks == ["rivalidad", "metodicidad"]
    assert {d["motivo"] for d in audit["descartadas"]} == {"IDENTIDAD", "FUTURO", "CALENDARIO", "FORMA"}
    assert audit["can_decide_H"] is False
