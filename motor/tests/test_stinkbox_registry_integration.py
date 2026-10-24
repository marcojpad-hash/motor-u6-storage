import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "stinkbox_registry.py"


def _run(home, *args):
    env = os.environ.copy()
    env["STINKBOX_HOME"] = str(home)
    return subprocess.run([sys.executable, str(REGISTRY), *map(str, args)], env=env,
                          text=True, capture_output=True, check=True, timeout=30)


def test_registry_ingests_run_tokens_outside_package_and_is_idempotent(tmp_path):
    home = tmp_path / "persistent-home"
    storage = tmp_path / "STINKBOX_STORAGE"
    storage.mkdir()
    artifact = storage / "stinkbox_CASE_TEST.json"
    artifact.write_text(json.dumps({
        "schema": "STINKBOX_TRANSPORT_V0.2",
        "case_id": "CASE_TEST",
        "token_events": [{"cut_id": "C1", "token": "token_nuevo_prueba", "source": "lateral_features", "kind": "external", "timestamp": "T1"}],
        "token_frequency": {"token_nuevo_prueba": 1},
        "persistent_neighbor_tokens": []
    }), encoding="utf-8")

    first = json.loads(_run(home, "ingest", storage).stdout)
    second = json.loads(_run(home, "ingest", storage).stdout)
    registry = json.loads((home / "data" / "registro_tokens.json").read_text(encoding="utf-8"))
    events = (home / "data" / "eventos_tokens.jsonl").read_text(encoding="utf-8").splitlines()

    assert first["status"] == "OK"
    assert first["new_token_strings"] >= 1
    assert second["artifacts_skipped_same_sha"] >= 1
    assert len(events) == 1
    assert "token_nuevo_prueba" in registry["tokens"]
    assert (home / "data" / "familias_candidatas_documentales.json").is_file()


def test_black_mirror_candidates_are_not_counted_as_run_observations(tmp_path):
    home = tmp_path / "persistent-home"
    empty_source = tmp_path / "empty-source"
    empty_source.mkdir()
    _run(home, "ingest", empty_source)
    doc = json.loads((home / "data" / "familias_candidatas_documentales.json").read_text(encoding="utf-8"))
    registry = json.loads((home / "data" / "registro_tokens.json").read_text(encoding="utf-8"))
    assert len(doc["candidates"]) == 18
    assert all(x["integrated_into_motor"] is False for x in doc["candidates"])
    assert all(x["must_not_count_as_observed_token"] is True for x in doc["candidates"])
    assert not any(x["token"].startswith("bm_") for x in registry["tokens"].values())
    assert (home / "reports" / "familias_candidatas_documentales.csv").is_file()


def test_runner_contains_automatic_post_run_import_for_standard_and_t1():
    text = (ROOT / "correr_estandar.py").read_text(encoding="utf-8")
    assert "_configure_stinkbox_home()" in text
    assert "_ingest_stinkbox_registry(stink_home, stink_storage, rd)" in text
    assert '"stinkbox_persistent_registry_ingest"' in text


def test_unknown_token_is_not_mapped_by_substring_to_existing_catalog_token():
    import importlib.util
    native = ROOT / "motor" / "MOTOR_V15_3_NATIVO_V0_9_UNICO.py"
    spec = importlib.util.spec_from_file_location("native_token_holes_test", native)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    holes = module.validar_corte("C1", [("token_prueba_fuera_catalogo", 0.7)], [], [], {"prueba"})
    record = holes["fuera_catalogo"][0]
    assert record["equivalente"] is None
    assert record["n_candidatos"] == 0


def test_same_case_cut_token_from_discovery_and_vault_counts_one_observation(tmp_path):
    home = tmp_path / "persistent-home"
    run_dir = tmp_path / "run"
    storage = tmp_path / "STINKBOX_STORAGE"
    run_dir.mkdir(); storage.mkdir()
    token = "token_nuevo_duplicado_fuentes"
    (run_dir / "stinkbox_tokens_descubiertos.json").write_text(json.dumps({"tokens": [{
        "case_id": "CASE_DUP", "corte": "C1", "eje": "P", "token": token,
        "estado": "PENDIENTE_REVISION", "entra_a_canon": False
    }]}), encoding="utf-8")
    (storage / "stinkbox_CASE_DUP.json").write_text(json.dumps({
        "case_id": "CASE_DUP", "token_events": [{"cut_id": "CASE_DUP::C1", "token": token,
        "source": "lateral_features", "kind": "external", "timestamp": "T1"}]
    }), encoding="utf-8")
    _run(home, "ingest", run_dir)
    _run(home, "ingest", storage)
    reg = json.loads((home / "data" / "registro_tokens.json").read_text(encoding="utf-8"))
    item = reg["tokens"][token]
    assert item["observations"] == 1
    assert item["evidence_events"] == 2
    assert item["status"] == "PENDIENTE_REVISION"


def test_external_search_vocabulary_is_reported_separately_from_missing_families(tmp_path):
    home = tmp_path / "persistent-home"
    storage = tmp_path / "STINKBOX_STORAGE"; storage.mkdir()
    (storage / "stinkbox_CASE_WEB.json").write_text(json.dumps({
        "case_id": "CASE_WEB", "token_events": [{"cut_id": "CASE_WEB::C1", "token": "archetypal",
        "source": "lateral_features", "kind": "external", "timestamp": "T1"}]
    }), encoding="utf-8")
    _run(home, "ingest", storage)
    external = (home / "reports" / "tokens_vocabulario_externo.csv").read_text(encoding="utf-8-sig")
    outside = (home / "reports" / "tokens_fuera_catalogo.csv").read_text(encoding="utf-8-sig")
    assert "archetypal" in external
    assert "archetypal" not in outside


def test_primary_token_checkpoint_precedes_retained_cut_analyses():
    text = (ROOT / "correr_estandar.py").read_text(encoding="utf-8")
    primary = text.index('_stinkbox_primary_checkpoint = _ingest_stinkbox_registry(stink_home, stink_storage, rd)')
    retained = text.index('if len(cuts)>=2:')
    assert primary < retained
    assert 'stinkbox_persistent_registry_primary_checkpoint' in text
