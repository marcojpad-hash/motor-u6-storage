import subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]


def test_no_mc_is_rejected_before_input_is_read():
    p=subprocess.run([sys.executable,str(ROOT/'correr_estandar.py'),'/does/not/exist.json','CASE','/tmp/no.json','--no-mc'],cwd=ROOT,text=True,capture_output=True)
    assert p.returncode != 0
    assert 'MONTE_CARLO_OBLIGATORIO' in p.stderr
    assert 'FileNotFoundError' not in p.stderr


def test_static_search_fixture_requires_explicit_opt_in():
    src=(ROOT/'motor'/'MOTOR_V15_3_UNICO_20260927.py').read_text(encoding='utf-8')
    assert 'case.get("allow_static_search_fixture") is True' in src
    assert 'case.get("caldero_search_fixture")' in src
    assert 'supplied=case.get("caldero_search_sources")' not in src
    assert '"live_web_calls":bool((features.get("external_archetype_search_receipt") or {}).get("status") == "EXECUTED")' in src


def test_no_mc_is_rejected_even_with_t1_mode():
    p=subprocess.run([sys.executable,str(ROOT/'correr_estandar.py'),'/does/not/exist.json','--t1','/also/missing.json','--no-mc'],cwd=ROOT,text=True,capture_output=True)
    assert p.returncode != 0
    assert 'MONTE_CARLO_OBLIGATORIO' in p.stderr
    assert 'FileNotFoundError' not in p.stderr
