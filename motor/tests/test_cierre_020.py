#!/usr/bin/env python3
"""Pruebas del cierre 020 (ejecutable sin pytest): banda, grupos, desempate solo en banda, pesos sin igualdades creadas."""
import importlib.util, sys
from pathlib import Path
M = Path(__file__).resolve().parents[1] / "motor" / "MOTOR_V15_3_UNICO_20260927.py"
sys.path.insert(0, str(M.parent))
spec = importlib.util.spec_from_file_location("motor_u2", M); mo = importlib.util.module_from_spec(spec); spec.loader.exec_module(mo)

def C(f, rf, v=0, m=0.0, s=0): return {"family": f, "rank_fusion": rf, "_v": v, "_m": m, "_s": s}

def test_banda():
    assert mo._banda_020({"calibracion_estructural": {"entropia": {"n_candidatos": 12}}}, [])["delta_rank_fusion"] == 0.25
    assert abs(mo._banda_020({"calibracion_estructural": {"entropia": {"n_candidatos": 5}}}, [])["delta_rank_fusion"] - 0.5) < 1e-9
    assert mo._banda_020({"calibracion_estructural": {"entropia": {"n_candidatos": 2}}}, [])["delta_rank_fusion"] == 1.0  # tope GATE_SEPARATION

def test_grupos_y_desempate_no_toca_ventaja_clara():
    cs = [C("a", 20.0), C("b", 19.2), C("c", 19.0), C("d", 17.0)]
    g = mo._grupos_banda_020(cs, 0.5)
    assert g == [[0], [1, 2], [3]], g
    # tortugas favorecen d (fuera de banda) y c (en banda con b): d no sube; c pasa a 2º
    orig = mo._tortugas_guardianes
    mo._tortugas_guardianes = lambda *a, **k: {"status": "EJECUTADO", "apoyo_por_candidata": {"d": {"votos_argmax": 9}, "c": {"votos_argmax": 2}}}
    try:
        out, tort, banda = mo._ordenar_020([dict(x) for x in cs], {"calibracion_estructural": {"entropia": {"n_candidatos": 5}}}, [], [], {}, {}, {}, {}, {"d": 1.0})
    finally:
        mo._tortugas_guardianes = orig
    assert [x["family"] for x in out] == ["a", "c", "b", "d"], [x["family"] for x in out]
    assert banda["H1_en_banda"] is False and banda["H2_cambiado_por_desempate"] is True
    assert banda["pistas_llm_en_orden"] is False and out[3]["pista_llm_arquetipos_traza"] == 1.0

def test_pesos_suma_1_sin_igualdades():
    cs = [C("a", 18.3774), C("b", 18.3773999), C("c", 17.0), C("d", 17.0)]
    p = mo._pesos_020(cs)
    w = [x["peso_relativo"] for x in p["pesos"]]
    assert abs(sum(w) - 1.0) < 1e-9, sum(w)
    assert w[0] > w[1] and w[2] == w[3] and p["sin_igualdades_creadas_por_normalizacion"], (w, p["decimales"])

if __name__ == "__main__":
    ok = 0
    for n, f in sorted(globals().items()):
        if n.startswith("test_"):
            try: f(); print("PASS", n); ok += 1
            except Exception as e: print("FAIL", n, repr(e))
    print(f"{ok} PASS")
