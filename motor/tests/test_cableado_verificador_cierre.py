"""V7 (B-H4): las violaciones del verificador de consistencia adversarial
llegan al cierre final como objeciones (vía _cierre_final_016). Antes el
paquete LLM no lo leía nadie y las violaciones no las consumía nadie.
"""
import importlib.util
import sys
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "motor" / "MOTOR_V15_3_UNICO_20260927.py"
spec = importlib.util.spec_from_file_location("motor_u6_v7_bh4", SOURCE)
mod = importlib.util.module_from_spec(spec)
sys.modules["motor_u6_v7_bh4"] = mod
spec.loader.exec_module(mod)


def _result_con_violaciones():
    return {"modo_estricto": {"criterios": {}}, "cierre_guardianes": {},
            "consistency_adversarial": {"status": "FAIL",
                                       "violations": ["TIE_NO_WINNER", "LATERAL_NO_H"]},
            "guardianes": {}, "apuesta": {"ramas": []}, "motor": {"cuts": []}}


def _pred():
    return {"candidates": [{"family": "H1", "rank_fusion": 4.0},
                           {"family": "H2", "rank_fusion": 2.0},
                           {"family": "H3", "rank_fusion": 1.0}]}


def test_violaciones_verificador_llegan_a_objeciones():
    out = mod._cierre_final_016(_result_con_violaciones(), _pred())
    objs = out["objeciones"]
    crits = [o.get("criterio") for o in objs
             if o.get("fuente") == "verificador_consistencia"]
    assert "TIE_NO_WINNER" in crits, objs
    assert "LATERAL_NO_H" in crits, objs
    # Las objeciones gradúan, no reescriben H.
    assert out["H1"] == "H1" and out["H2"] == "H2"


def test_sin_violaciones_no_hay_objecion_verificador():
    res = _result_con_violaciones()
    res["consistency_adversarial"] = {"status": "PASS", "violations": []}
    out = mod._cierre_final_016(res, _pred())
    assert not [o for o in out["objeciones"]
                if o.get("fuente") == "verificador_consistencia"]
