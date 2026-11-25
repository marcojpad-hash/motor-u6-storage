import importlib.util
from pathlib import Path

P = Path(__file__).resolve().parents[1] / 'u7' / 'confianza_apuesta_u7.py'
spec = importlib.util.spec_from_file_location('confianza_apuesta_u7', P)
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

def test_steel_sign_is_from_rival_perspective():
    assert mod.ACERO['SOBREVIVE'] == 0.0
    assert mod.ACERO['CAE'] == 1.0
    assert mod.ACERO['OBJECION_RESUELTA_EN_CIERRE'] == 0.5


def _fixture_b5():
    # Fixture con la forma REAL del RESULT (V7, C-F5): H1_sellada_compatibilidad
    # (nunca H1_sellada) y tops_t1 con 10 ítems.
    return {
      'case_id':'SYNTH_B5',
      'cierre_final': {'criterios_grado': {'separacion':1.0,'H1_en_banda':False}, 'apuesta': {'familia_apostada':'H1','frente_a':'H2','margen':1.0}, 'prueba_acero': {'veredicto_top1':'SOBREVIVE','rival_mas_fuerte':'H2'}, 'n_objeciones':0,'objeciones':[],'grado':'AJUSTADA'},
      'salida_interpretable': {'grado_inverso_set':'SET_EXPLICA_TODOS_LOS_CORTES','mezcla':{'lectura':'H1_DOMINANTE'},'H1':{'predictibilidad_estructural_pct':50}},
      'predictor': {'lateral_signal_registry':[]},
      'cierre_guardianes': {}, 'decimo_hombre_esteroides': {'contador_supervivencia':{'H1':1},'ataques':[]},
      'efectividad_corte_retenido': {'H1_sellada_compatibilidad':'H1', 'tops_t1':[{'familia':'H1'}]*10, 'hit_H': True}, 'hipotesis_necesarias_suficientes': {'miembros':[]},
      'lo_que_se_cocina_abajo': [], 'predictibilidad_021': {'predictibilidad':{'base_pp':40,'techo_pp':60}}
    }


def test_b5_usa_el_campo_real_del_result():
    # V7 (C-F5): antes B5 leía H1_sellada, que no existe en el RESULT real,
    # y puntuaba 0.0 siempre; solo pasaba en el fixture con el esquema supuesto.
    d = _fixture_b5()
    out = mod.calc(d)
    assert out['detalle']['B5']['H1_sin_ultimo'] == 'H1'
    assert out['detalle']['B5']['retenido_usable'] is True
    assert out['bloques']['B5_estabilidad_sin_ultimo'] == 1.0
    # Control: si el retenido es H2, B5 es 0.5 (no 0.0 ni 1.0).
    d['efectividad_corte_retenido']['H1_sellada_compatibilidad'] = 'H2'
    out2 = mod.calc(d)
    assert out2['bloques']['B5_estabilidad_sin_ultimo'] == 0.5

def test_b5_sin_tops_t1_es_neutral_05():
    # V7 (B5 retenido no usable): sin tops_t1 la evaluación retenida no
    # corrió; B5 es neutral 0.5, nunca 0.0 por un hs None que no se evaluó.
    # Tampoco se premia con 1.0 aunque hs diga H1: sin tops_t1 no hay
    # evidencia de estabilidad.
    d = _fixture_b5()
    d['efectividad_corte_retenido'] = {'H1_sellada_compatibilidad': None, 'tops_t1': [], 'hit_H': None}
    out = mod.calc(d)
    assert out['detalle']['B5']['retenido_usable'] is False
    assert out['bloques']['B5_estabilidad_sin_ultimo'] == 0.5
    d['efectividad_corte_retenido'] = {'H1_sellada_compatibilidad': 'H1', 'tops_t1': None, 'hit_H': True}
    out2 = mod.calc(d)
    assert out2['detalle']['B5']['retenido_usable'] is False
    assert out2['bloques']['B5_estabilidad_sin_ultimo'] == 0.5

def test_steel_only_applies_when_rival_is_h2():
    # Test the decision helper through a minimal full fixture.
    d = {
      'case_id':'SYNTH',
      'cierre_final': {'criterios_grado': {'separacion':1.0,'H1_en_banda':False}, 'apuesta': {'familia_apostada':'H1','frente_a':'H2','margen':1.0}, 'prueba_acero': {'veredicto_top1':'SOBREVIVE','rival_mas_fuerte':'H3'}, 'n_objeciones':0,'objeciones':[],'grado':'AJUSTADA'},
      'salida_interpretable': {'grado_inverso_set':'SET_EXPLICA_TODOS_LOS_CORTES','mezcla':{'lectura':'H1_DOMINANTE'},'H1':{'predictibilidad_estructural_pct':50}},
      'predictor': {'lateral_signal_registry':[]},
      'cierre_guardianes': {}, 'decimo_hombre_esteroides': {'contador_supervivencia':{'H1':1},'ataques':[]},
      'efectividad_corte_retenido': {'H1_sellada_compatibilidad':'H1', 'tops_t1':[{'familia':'H1'}], 'hit_H': True}, 'hipotesis_necesarias_suficientes': {'miembros':[]},
      'lo_que_se_cocina_abajo': [], 'predictibilidad_021': {'predictibilidad':{'base_pp':40,'techo_pp':60}}
    }
    out = mod.calc(d)
    assert out['detalle']['B4']['acero_alineado_a_H2'] is False
    assert out['detalle']['B4']['acero_aporte'] == 0.5
    d['cierre_final']['prueba_acero']['rival_mas_fuerte']='H2'
    out2=mod.calc(d)
    assert out2['detalle']['B4']['acero_aporte'] == 0.0

def test_duplicate_steel_objection_not_charged_twice():
    cf={'n_objeciones':2,'objeciones':[
      {'fuente':'guardian','guardian':'HOMBRE_DE_ACERO','tipo':'RIVAL_NO_DESCARTADO','alcance':'global','corte':None},
      {'fuente':'modo_estricto','criterio':'C2_acero','detalle':'C2: el acero no descarta al rival'}
    ]}
    n, rows=mod._objeciones_unicas(cf)
    assert n == 1 and len(rows) == 1

def test_exact_duplicate_objection_removed_but_distinct_kept():
    cf={'objeciones':[
      {'fuente':'guardian','guardian':'X','tipo':'T','alcance':'global','corte':None},
      {'fuente':'guardian','guardian':'X','tipo':'T','alcance':'global','corte':None},
      {'fuente':'modo_estricto','criterio':'C1_top1_encabeza_un_corte'}
    ]}
    n, rows=mod._objeciones_unicas(cf)
    assert n == 2 and len(rows) == 2

def test_semiotica_does_not_turn_contra_tokens_into_positive_support(tmp_path):
    # Exercise polarity accounting with an isolated synthetic catalog/input.
    import json
    from unittest.mock import patch
    sempath = Path(__file__).resolve().parents[1] / 'motor' / 'semiotica_deriva_v0_1.py'
    spec2 = importlib.util.spec_from_file_location('semiotica_under_test', sempath)
    sem = importlib.util.module_from_spec(spec2); spec2.loader.exec_module(sem)
    cat = tmp_path / 'patterns_final_v14.json'
    cat.write_text(json.dumps({'F': {'tokens_favor': {'apoya': 1.0}, 'tokens_contra': {'contradice': 1.0}}}))
    with patch.object(sem, '__file__', str(tmp_path / 'semiotica_deriva_v0_1.py')):
        out = sem.revisar({'cuts':[{'id':'C1','P':[['contradice',0.8]],'A':[],'C':[]}]}, {})
    assert out['por_familia']['F']['score'] == -0.4
    assert out['por_familia']['F']['contra'] == 0.4
