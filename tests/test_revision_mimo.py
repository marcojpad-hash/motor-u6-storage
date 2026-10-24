import datetime as dt, importlib.util, subprocess, sys
from pathlib import Path
import pytest

spec = importlib.util.spec_from_file_location("rm", Path(__file__).resolve().parent.parent / "scripts/revision_mimo.py")
rm = importlib.util.module_from_spec(spec); spec.loader.exec_module(rm)

@pytest.fixture
def repo(tmp_path, monkeypatch):
    g = lambda *a: subprocess.run(["git", *a], cwd=tmp_path, check=True, capture_output=True)
    g("init", "-q"); g("config", "user.email", "t@t"); g("config", "user.name", "t")
    for i in range(3):
        (tmp_path / f"f{i}.txt").write_text("x" * 500 * (i + 1)); g("add", "."); g("commit", "-qm", f"c{i}")
    d = tmp_path / "avances/mimo"; d.mkdir(parents=True)
    monkeypatch.setattr(rm, "REPO", tmp_path); monkeypatch.setattr(rm, "DIR", d)
    monkeypatch.setattr(rm, "SHA_FILE", d / ".ultimo_sha"); monkeypatch.setattr(rm, "USO_FILE", d / "uso.json")
    monkeypatch.setattr(rm, "llamar_mimo", lambda *a: pytest.fail("no debe llamar a la API"))
    return tmp_path

def head(r): return subprocess.run(["git", "rev-parse", "HEAD"], cwd=r, capture_output=True, text=True).stdout.strip()

def test_sin_cambios(repo):
    rm.SHA_FILE.write_text(head(repo)); assert rm.commits_nuevos()[1] == []
    assert rm.main([]) == 0

def test_detecta_commits_y_recorta(repo):
    first = subprocess.run(["git", "rev-list", "--max-parents=0", "HEAD"], cwd=repo, capture_output=True, text=True).stdout.strip()
    rm.SHA_FILE.write_text(first)
    base, shas = rm.commits_nuevos(); assert len(shas) == 2
    t = rm.resumen_diff(base, shas, limite=300); assert len(t) < 360 and "recortado" in t

def test_sin_key_no_llama(repo, monkeypatch):
    monkeypatch.delenv("MIMO_API_KEY", raising=False); assert rm.main([]) == 0
    assert not rm.USO_FILE.exists()

def test_dry_run_no_escribe(repo, monkeypatch):
    monkeypatch.setenv("MIMO_API_KEY", "sk-x"); assert rm.main(["--dry-run"]) == 0
    assert not rm.SHA_FILE.exists() and not rm.USO_FILE.exists()

def test_fecha_limite(repo, monkeypatch):
    monkeypatch.setenv("MIMO_API_KEY", "sk-x"); assert rm.main([], hoy=dt.date(2027, 1, 1)) == 0

def test_tope_diario(repo, monkeypatch):
    monkeypatch.setenv("MIMO_API_KEY", "sk-x")
    rm.USO_FILE.write_text('{"dias": {"2026-11-01": %d}, "llamadas": []}' % rm.TOPE_DIARIO)
    assert rm.main([], hoy=dt.date(2026, 11, 1)) == 0

def test_llamada_simulada_escribe(repo, monkeypatch):
    monkeypatch.setenv("MIMO_API_KEY", "sk-x")
    monkeypatch.setattr(rm, "llamar_mimo", lambda k, r: ("todo bien", {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}))
    assert rm.main([], hoy=dt.date(2026, 11, 1)) == 0
    md = (rm.DIR / "2026-11-01_revision.md").read_text(); assert head(repo) in md and "total=15" in md
    assert rm.leer_uso()["dias"]["2026-11-01"] == 15 and rm.SHA_FILE.read_text().strip() == head(repo)
