import importlib.util
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "motor" / "MOTOR_V15_3_UNICO_20260927.py"
spec = importlib.util.spec_from_file_location("motor_u6_variant", SOURCE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def test_steel_rival_must_equal_actual_h2():
    result={"modo_estricto":{"criterios":{"C2_rival_mas_fuerte_descartado_por_acero":{"ok":True,"rival_mas_fuerte":"H3","veredicto_top1":"SOBREVIVE"}}},"cierre_guardianes":{},"guardianes":{},"apuesta":{"ramas":[]},"motor":{"cuts":[]}}
    pred={"candidates":[{"family":"H1","rank_fusion":4.0},{"family":"H2","rank_fusion":2.0},{"family":"H3","rank_fusion":1.0}]}
    out=mod._cierre_final_016(result,pred)
    assert out["H1"]=="H1" and out["H2"]=="H2"
    assert out["prueba_acero"]["rival_alineado_apuesta"] is False
    assert out["prueba_acero"]["descarta_rival"] is False
    assert "acero_rival_no_alineado" in out["criterios_grado"]["senales_contrarias_fuertes"]

def test_same_steel_objection_counted_once():
    rows=[{"fuente":"guardian","guardian":"HOMBRE_DE_ACERO","tipo":"RIVAL_NO_DESCARTADO","alcance":"global","corte":None},{"fuente":"modo_estricto","criterio":"C2_acero","detalle":"C2: el acero no descarta al rival"}]
    assert len(mod._deduplicar_objeciones_016(rows))==1

def test_distinct_objections_preserved():
    rows=[{"fuente":"guardian","guardian":"HOMBRE_DE_ACERO","tipo":"RIVAL_NO_DESCARTADO","alcance":"global","corte":None},{"fuente":"modo_estricto","criterio":"C1_top1_encabeza_un_corte","detalle":"C1: no encabezó cortes"}]
    assert len(mod._deduplicar_objeciones_016(rows))==2
