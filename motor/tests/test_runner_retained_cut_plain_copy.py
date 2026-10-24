import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('runner_plain_copy_test', ROOT / 'correr_estandar.py')
runner = importlib.util.module_from_spec(spec); spec.loader.exec_module(runner)


def test_retained_cut_copy_is_plain_and_deep():
    source = {'case_id': 'X', 'cuts': [{'id': 'C1', 'P': [['a', .7]]}, {'id': 'C2', 'P': [['b', .8]]}]}
    copied = runner._plain_json_copy(source)
    copied['cuts'][1]['P'][0][1] = .1
    assert source['cuts'][1]['P'][0][1] == .8
    assert type(copied) is dict and type(copied['cuts'][0]) is dict


def test_runtime_motor_build_copies_geometry_multilayer(tmp_path, monkeypatch):
    source_motor = tmp_path / 'source_motor'; source_motor.mkdir()
    (source_motor / 'MOTOR_V15_3_UNICO_20260927.py').write_text('# working motor')
    geo = source_motor / 'geometria_multicapa'; geo.mkdir(); (geo / 'sidecar_latentes_v1.py').write_text('# geo')
    monkeypatch.setattr(runner, 'MOTOR', source_motor)
    dest = tmp_path / 'runtime'
    runner._build(dest)
    assert (dest / 'geometria_multicapa' / 'sidecar_latentes_v1.py').is_file()


def test_t1_scores_open_hypothesis_set_not_only_h1_h2():
    sealed = {
        'H1': {'family': 'old_h1'}, 'H2': {'family': 'old_h2'},
        'hipotesis': [{'familia': 'old_h1'}, {'familia': 'complementaria_h3'}],
    }
    future = {'predictor': {'candidates': [{'family': 'complementaria_h3'}]}, 'cuts': []}
    out = runner.puntuar_t1(sealed, [], future)
    assert out['hit_H'] == 'HIT_HIPOTESIS_SET'
    assert out['hipotesis_selladas'] == ['old_h1', 'complementaria_h3']
    assert out['hipotesis_con_evidencia_t1'] == ['complementaria_h3']


def test_preserve_ledger_copies_external_ceb_path(tmp_path):
    external = tmp_path / 'external_ceb.jsonl'
    external.write_text('{"event":"RUN_END"}\n', encoding='utf-8')
    run_dir = tmp_path / 'runtime'; run_dir.mkdir()
    out = tmp_path / 'result.json'
    manifest = runner.preservar_ledger_ceb(run_dir, out, {'ceb': {'ledger': str(external)}})
    assert len(manifest['ledgers']) == 1
    copied = Path(manifest['ledgers'][0]['copia'])
    assert copied.is_file() and copied.read_text(encoding='utf-8') == external.read_text(encoding='utf-8')
