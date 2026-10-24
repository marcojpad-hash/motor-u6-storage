#!/usr/bin/env python3
"""U3_021: escala con base, set necesario/suficiente, paso inverso y capa de traducción (sin pytest: python3 este_archivo)."""
import copy, importlib.util, json, sys
from pathlib import Path
R = Path(__file__).resolve().parents[1]
def _m(name, p):
    s = importlib.util.spec_from_file_location(name, str(p)); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
P = _m("p021", R / "motor/predictibilidad_set_021.py")
T = _m("t021", R / "capa_llm/traduccion_contextual_021.py")
PAT = {"fa": {"description": "Busqueda de poder sin limites.", "tokens_favor": {"x": .9, "y": .7, "poder": .7, "ambicion": .9}, "tokens_contra": {"z": .7}},
       "fb": {"description": "b", "tokens_favor": {"y": .6, "w": .6}, "tokens_contra": {}},
       "fc": {"description": "c", "tokens_favor": {"x": .6}, "tokens_contra": {"y": .6}},
       "fd": {"description": "d", "tokens_favor": {"q": .6}, "tokens_contra": {}}}
CASE = {"cuts": [{"id": "C1", "hecho": "compone una ópera y la estrena", "P": [["x", .8], ["y", .7]], "A": [["w", .6]], "C": [["ambicion", .7]]},
                 {"id": "C2", "P": [["q", .7]], "A": [["y", .66]], "C": [["z", .62]]}]}
def _res():
    dims = ["d1", "d2"]
    c = []
    for n, (a, b, lat) in {"fa": (1.0, .5, .9), "fb": (.5, 1.0, .8), "fc": (0.0, 0.0, .1), "fd": (.25, .25, 0.0)}.items():
        c.append({"family": n, "rank_fusion": a + b + lat, "features": {"d1": a, "d2": b, "lateral_signal_contributions": {"s1": lat}}})
    c.sort(key=lambda z: -z["rank_fusion"])
    return {"predictor": {"candidates": c, "dimensions": dims, "techo_rank": 3,
                          "aporte_por_dimension_021": {x["family"]: {"d1": x["features"]["d1"], "d2": x["features"]["d2"]} for x in c}},
            "cierre_final": {"H1": c[0]["family"], "H2": c[1]["family"],
                             "banda_casi_igualdad": {"grupos_casi_igualdad": [{"miembros_orden_rank_fusion": ["fa", "fb"], "orden_final": ["fa", "fb"], "posiciones_rank_fusion": [1, 2]}]}},
            "motor": {"cuts": [{"P_FULL_244": {"fa": .7, "fb": .7, "fc": .5, "fd": .5}}]}}
def test_escala_base_techo_y_suma():
    r = _res(); o = P.run(CASE, r, R / "motor", PAT); e = o["predictibilidad"]
    assert 0 < e["base_pp"] < 50 and 50 < e["techo_pp"] < 100
    for n, h in e["por_hipotesis"].items():
        assert abs(h["base_pp"] + h["suma_pp_componentes"] - h["predictibilidad_estructural_pct"]) < 0.05, n
        assert h["cuadra_rank_fusion"], n
        assert 0 < h["predictibilidad_estructural_0_1"] < 1
    assert e["es_probabilidad_calibrada"] is False
def test_no_muta_ni_decide():
    r = _res(); r0 = copy.deepcopy(r); o = P.run(CASE, r, R / "motor", PAT)
    assert r == r0 and o["can_decide_H"] is False and o["reordena"] is False
def test_set_eje_banda_y_cobertura():
    o = P.run(CASE, _res(), R / "motor", PAT); s = o["hipotesis_necesarias_suficientes"]
    fam = [m["familia"] for m in s["miembros"]]
    assert fam[0] == "fa" and s["miembros"][0]["rol"] == "eje" and "fb" in fam
    assert s["cobertura_set_frac_de_lo_cubrible"] >= P.THETA_COBERTURA
    assert "fd" in fam and any("C2" in m["cortes_unicos"] for m in s["miembros"] if m["familia"] == "fd") or "C2" in s["cortes_explicados_por_set"]
def test_inverso_contradice_y_acero():
    o = P.run(CASE, _res(), R / "motor", PAT); inv = o["paso_inverso"]["por_hipotesis"]
    est = {f["corte"]: f["estado"] for f in inv["fc"]["cortes"]}
    assert est["C1"] in ("EXPLICA_CON_CONTRA", "CONTRADICE") and inv["fa"]["acero_inverso_vs_eje"] == "ES_EL_EJE"
    assert inv["fc"]["acero_inverso_vs_eje"]["veredicto"] in ("REDUNDANTE_CON_EJE", "COMPLEMENTA_AL_EJE")
    assert "texto" not in json.dumps(inv).lower().replace("texto_del_corte", "")  # el motor no emite texto de corte
def test_traduccion_rol_y_presentismo():
    rol = T.derivar_contexto_rol(CASE); assert rol["oficio"] == "arte_composicion"
    lec = T.lectura_por_oficio("fa", PAT, rol["oficio"]); assert "lectura_presentista_a_evitar" in lec and lec["es_familia_de_impulso"]
    r = _res(); o = P.run(CASE, r, R / "motor", PAT); r["predictibilidad_021"] = o; r["hipotesis_necesarias_suficientes"] = o["hipotesis_necesarias_suficientes"]
    tr = T.traducir(r, CASE, PAT); ev = tr["set"][0]["evidencia_en_contexto"]
    assert ev and ev[0]["texto_del_corte"].startswith("compone")
if __name__ == "__main__":
    ok = 0; tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        try: t(); ok += 1; print("PASS", t.__name__)
        except Exception as e: print("FAIL", t.__name__, type(e).__name__, e)
    print(f"{ok}/{len(tests)}"); sys.exit(0 if ok == len(tests) else 1)
