import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
p = ROOT / 'motor' / 'hipotesis_trayectoria_abierta_v1.py'
spec = importlib.util.spec_from_file_location('hta_test', p)
hta = importlib.util.module_from_spec(spec); spec.loader.exec_module(hta)


def cand(name, rank, micro=.7, meso=.65, macro=.6, accel=.55):
    return {'family': name, 'rank_fusion': rank, 'features': {
        'trajectory_micro_support': micro, 'trajectory_meso_support': meso,
        'trajectory_macro_support': macro, 'trajectory_acceleration_support': accel,
        'geometric_inertia_alignment': .7, 'geometric_direction_change': .6}}


def test_zero_hypotheses_no_invented_bet():
    out = hta.construir({'predictor': {'candidates': []}}, {'cuts': []}, {})
    assert out['n_hipotesis'] == 0
    assert out['apuesta']['estado'] == 'SIN_HIPOTESIS'
    assert out['apuesta']['apuesta_principal'] is None


def test_one_hypothesis_not_duplicated_as_h2():
    out = hta.construir({'predictor': {'candidates': [cand('a', 3)]}}, {'cuts': [{'id':'C1'}, {'id':'C2'}]}, {})
    assert out['n_hipotesis'] == 1
    assert [h['familia'] for h in out['hipotesis']] == ['a']
    assert out['apuesta']['estado'] == 'APUESTA_MULTIESCENARIO_SELLABLE'


def test_open_set_has_no_fixed_maximum_and_bet_follows_set():
    cs = [cand(f'f{i}', 20-i, .8, .75, .7) for i in range(7)]
    out = hta.construir({'predictor': {'candidates': cs}}, {'cuts': [{'id':'C1'}, {'id':'C2'}, {'id':'C3'}]}, {})
    assert out['cardinalidad_fija'] is False and out['maximo_hipotesis'] is None
    assert out['n_hipotesis'] == 7
    assert len(out['apuesta']['escenarios']) == 1
    assert out['apuesta']['escenarios'][0]['n_hipotesis'] == 7
    assert out['apuesta']['escenarios'][0]['es_probabilidad'] is False


def test_necessary_sufficient_set_can_select_many_and_preserve_alternatives():
    cs = [cand(f'f{i}', 20-i) for i in range(6)]
    result = {'predictor': {'candidates': cs}, 'hipotesis_necesarias_suficientes': {'miembros': [
        {'familia':'f0','rol':'eje'}, {'familia':'f2','rol':'complementaria'}, {'familia':'f4','rol':'complementaria'}]}}
    out = hta.construir(result, {'cuts':[{'id':'C1'}, {'id':'C2'}]}, {})
    assert [h['familia'] for h in out['hipotesis']] == ['f0','f2','f4']
    assert len(out['alternativas_fuera_del_set']) == 3
    assert out['metodo_seleccion'] == 'SET_NECESARIO_SUFICIENTE_021'


def test_one_cut_does_not_invent_trajectory():
    out = hta.construir({'predictor': {'candidates': [cand('a', 3)]}}, {'cuts': [{'id':'C1'}]}, {})
    assert out['apuesta']['estado'] == 'TRAYECTORIA_INSUFICIENTE'
    assert out['apuesta']['apuesta_principal'] is None

if __name__ == '__main__':
    tests = [v for k,v in sorted(globals().items()) if k.startswith('test_')]
    for t in tests: t(); print('PASS', t.__name__)
    print(f'{len(tests)}/{len(tests)} PASS')
