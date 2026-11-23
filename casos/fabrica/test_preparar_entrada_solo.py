from __future__ import annotations

import hashlib
import importlib.util
import inspect
import json
import uuid
from datetime import date
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parent / "preparar_entrada_solo.py"
SPEC = importlib.util.spec_from_file_location("preparar_entrada_solo_test", MODULE_PATH)
prep = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(prep)


def _case(case_id: str | None = None, person: str | None = None) -> dict:
    helper = prep._helpers()
    gate = helper._gate()
    tokens, _families = helper.vocab()
    token = sorted(tokens)[0]
    birth = "2000-01-01"
    death = "2020-01-01"
    z90 = gate.calcular_z90(birth, death).isoformat()
    person = person or f"TEST_SUBJECT_{uuid.uuid4().hex}"
    case_id = case_id or f"TEST_ENTRY_ONLY_{uuid.uuid4().hex}"
    evidence_1 = {
        "afirmacion": "Afirmación sintética de prueba, no un caso real.",
        "claim_date": birth,
        "source_date": birth,
        "source_url": "https://example.org/primary/birth",
        "tipo_fuente": "primaria",
        "conocido_en_Z": "sí",
    }
    evidence_2 = {
        "afirmacion": "Afirmación sintética de prueba anterior al corte final.",
        "claim_date": "2017-12-31",
        "source_date": "2017-12-31",
        "source_url": "https://example.org/primary/pre-z",
        "tipo_fuente": "primaria",
        "conocido_en_Z": "sí",
    }
    return {
        "case_id": case_id,
        "question": "Caso sintético para probar separación de entrada y destino.",
        "person": person,
        "tipo_sujeto": "biografia",
        "freeze": z90,
        "modo_z": "historico",
        "fecha_nacimiento": birth,
        "fecha_muerte": death,
        "z_trabajo": z90,
        "z90_date": z90,
        "gate_z": gate.VERSION,
        "random_seed": 20261123,
        "z_work_kind": "CASE_CUTOFF",
        "z_work_date": z90,
        "preparacion_ciega": {
            "preparador_entrada": "PREPARADOR_TEST",
            "custodio_destino": "CUSTODIO_TEST",
            "vio_destino": False,
        },
        "source_notes": "Fixture sintético de prueba; no aporta evidencia experimental.",
        "cuts": [
            {
                "cut_id": "C1",
                "date": birth,
                "window_start": birth,
                "hecho": "Hecho sintético en el corte de nacimiento.",
                "P": [[token, 0.70]],
                "A": [],
                "C": [],
                "evidencia": [evidence_1],
            },
            {
                "cut_id": "C2",
                "date": z90,
                "window_start": birth,
                "hecho": "Hecho sintético anterior al corte Z90.",
                "P": [[token, 0.72]],
                "A": [],
                "C": [],
                "evidencia": [evidence_2],
            },
        ],
    }


def _write_seed(path: Path, cases: list[dict]) -> Path:
    path.write_text(json.dumps({"cases": cases}, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def test_entry_only_writes_input_and_hash_only(tmp_path: Path):
    case = _case()
    seed = _write_seed(tmp_path / "seeds.json", [case])
    out = tmp_path / "entradas_solo"

    code, messages = prep.preparar_entrada_solo(seed, out)

    assert code == 0, messages
    case_dir = out / case["case_id"]
    assert sorted(p.name for p in case_dir.iterdir()) == ["entrada.json", "entrada.sha256"]
    raw = (case_dir / "entrada.json").read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    assert (case_dir / "entrada.sha256").read_text(encoding="utf-8") == f"{digest}  entrada.json\n"
    written = json.loads(raw)
    assert written["case_id"] == case["case_id"]
    assert written["gate_z"] == prep._helpers()._gate().VERSION
    assert written["z_work_date"] == written["z_trabajo"]
    assert not (case_dir / "desenlace_sellado.json").exists()
    assert not (case_dir / "destino_sellado.json").exists()
    assert "ENTRY_ONLY_STAGED" in messages[0]


def test_secondary_source_is_rejected_without_writing(tmp_path: Path):
    case = _case()
    case["cuts"][0]["evidencia"][0]["tipo_fuente"] = "secundaria"
    seed = _write_seed(tmp_path / "seeds.json", [case])
    out = tmp_path / "entradas_solo"

    code, messages = prep.preparar_entrada_solo(seed, out)

    assert code == 1
    assert any("no es fuente primaria" in message for message in messages)
    assert not out.exists()


def test_destination_fields_are_rejected_without_writing(tmp_path: Path):
    case = _case()
    case["destino"] = "NO_DEBE_EXISTIR"
    seed = _write_seed(tmp_path / "seeds.json", [case])
    out = tmp_path / "entradas_solo"

    code, messages = prep.preparar_entrada_solo(seed, out)

    assert code == 1
    assert any("campos de destino/desenlace" in message for message in messages)
    assert not out.exists()


def test_duplicate_case_id_rejects_entire_batch(tmp_path: Path):
    first = _case(case_id="TEST_DUPLICATE_CASE", person="TEST_SUBJECT_DUPLICATE_A")
    second = _case(case_id="TEST_DUPLICATE_CASE", person="TEST_SUBJECT_DUPLICATE_B")
    seed = _write_seed(tmp_path / "seeds.json", [first, second])
    out = tmp_path / "entradas_solo"

    code, messages = prep.preparar_entrada_solo(seed, out)

    assert code == 1
    assert any("case_id repetido" in message for message in messages)
    assert not out.exists()


def test_path_traversal_case_id_rejected(tmp_path: Path):
    case = _case(case_id="../DESTINO", person="TEST_SUBJECT_PATH_TRAVERSAL")
    seed = _write_seed(tmp_path / "seeds.json", [case])
    out = tmp_path / "entradas_solo"

    code, messages = prep.preparar_entrada_solo(seed, out)

    assert code == 1
    assert any("case_id inválido o inseguro" in message for message in messages)
    assert not out.exists()


def test_entry_only_api_has_no_destination_parameter():
    params = inspect.signature(prep.preparar_entrada_solo).parameters
    assert "destinos" not in params
    assert "destination" not in params

def test_existing_output_root_accepts_new_case_without_overwriting(tmp_path: Path):
    first = _case()
    second = _case()
    out = tmp_path / "entradas_solo"
    seed_one = _write_seed(tmp_path / "first.json", [first])
    seed_two = _write_seed(tmp_path / "second.json", [second])

    code_one, messages_one = prep.preparar_entrada_solo(seed_one, out)
    code_two, messages_two = prep.preparar_entrada_solo(seed_two, out)

    assert code_one == 0, messages_one
    assert code_two == 0, messages_two
    assert (out / first["case_id"] / "entrada.json").is_file()
    assert (out / second["case_id"] / "entrada.json").is_file()


def test_hypothesis_fields_are_rejected_before_write(tmp_path: Path):
    case = _case()
    case["H1"] = "NO_DEBE_EXISTIR_ANTES_DE_Z"
    seed = _write_seed(tmp_path / "seeds.json", [case])
    out = tmp_path / "entradas_solo"

    code, messages = prep.preparar_entrada_solo(seed, out)

    assert code == 1
    assert any("campos de destino/desenlace" in message for message in messages)
    assert not out.exists()


def test_entry_only_does_not_import_destination_module(tmp_path: Path):
    import sys

    before = {name for name in sys.modules if "destinos_lote" in name.lower()}
    case = _case()
    seed = _write_seed(tmp_path / "seeds.json", [case])
    out = tmp_path / "entradas_solo"
    code, messages = prep.preparar_entrada_solo(seed, out)

    assert code == 0, messages
    after = {name for name in sys.modules if "destinos_lote" in name.lower()}
    assert after == before

def test_previous_index_extracts_f007_identity_without_executing_module(tmp_path, monkeypatch):
    helper = prep._helpers()
    fake_repo = tmp_path / "repo"
    seed_dir = fake_repo / "casos" / "fabrica"
    seed_dir.mkdir(parents=True)
    f007_text = (
        'raise RuntimeError("no debe ejecutarse")' + chr(10)
        + 'SEMILLAS_Z = [{"id": "F007_TEST_01", "person": "SUJETO_F007_RESERVADO"}]' + chr(10)
    )
    (seed_dir / "semillas_lote_F007.py").write_text(f007_text, encoding="utf-8")
    monkeypatch.setattr(helper, "REPO", fake_repo)

    ids, subjects, errors = prep._ids_y_sujetos_previos()

    assert "f007_test_01" in ids
    assert "sujeto_f007_reservado" in subjects
    assert errors == []
def test_previous_index_reserves_c01_ids_and_never_reads_custody(tmp_path, monkeypatch):
    helper = prep._helpers()
    fake_repo = tmp_path / "repo"
    c01 = fake_repo / "casos" / "ciegos" / "lote_20" / "C01"
    custody = fake_repo / "casos" / "ciegos" / "lote_20" / "custodia"
    c01.mkdir(parents=True)
    custody.mkdir(parents=True)
    (c01 / "entrada.json").write_text('{"case_id":"C01","question":"input only"}', encoding="utf-8")
    (custody / "entrada.json").write_text("{this file must never be read", encoding="utf-8")
    monkeypatch.setattr(helper, "REPO", fake_repo)

    ids, subjects, errors = prep._ids_y_sujetos_previos()

    assert "c01" in ids
    assert errors == []
    assert subjects == set()


def test_previous_index_reads_seed_json_and_entry_only_outputs(tmp_path, monkeypatch):
    helper = prep._helpers()
    fake_repo = tmp_path / "repo"
    seeds = fake_repo / "casos" / "fabrica" / "semillas_entrada"
    staged = fake_repo / "casos" / "fabrica" / "entradas_solo" / "OLD_CASE"
    seeds.mkdir(parents=True)
    staged.mkdir(parents=True)
    (seeds / "old.json").write_text(
        json.dumps({"cases":[{"case_id":"OLD_SEED","person":"SUJETO_SEMILLA_ANTERIOR"}]}),
        encoding="utf-8",
    )
    (staged / "entrada.json").write_text(
        json.dumps({"case_id":"OLD_STAGED","person":"SUJETO_ENTRADA_ANTERIOR"}),
        encoding="utf-8",
    )
    monkeypatch.setattr(helper, "REPO", fake_repo)

    ids, subjects, errors = prep._ids_y_sujetos_previos()

    assert {"old_seed", "old_staged"} <= ids
    assert {"sujeto_semilla_anterior", "sujeto_entrada_anterior"} <= subjects
    assert errors == []


def test_previous_index_excludes_the_seed_being_prepared(tmp_path, monkeypatch):
    helper = prep._helpers()
    fake_repo = tmp_path / "repo"
    seeds = fake_repo / "casos" / "fabrica" / "semillas_entrada"
    seeds.mkdir(parents=True)
    current = seeds / "current.json"
    current.write_text(
        json.dumps({"cases":[{"case_id":"CURRENT","person":"SUJETO_ACTUAL"}]}),
        encoding="utf-8",
    )
    monkeypatch.setattr(helper, "REPO", fake_repo)

    ids, subjects, errors = prep._ids_y_sujetos_previos(exclude_path=current)

    assert "current" not in ids
    assert "sujeto_actual" not in subjects
    assert errors == []


def test_duplicate_subject_in_f007_is_rejected_before_staging(tmp_path, monkeypatch):
    helper = prep._helpers()
    fake_repo = tmp_path / "repo"
    seed_dir = fake_repo / "casos" / "fabrica"
    seed_dir.mkdir(parents=True)
    f007_text = (
        'SEMILLAS_Z = [{"id": "F007_TEST_01", "person": "SUJETO_DUPLICADO"}]' + chr(10)
    )
    (seed_dir / "semillas_lote_F007.py").write_text(f007_text, encoding="utf-8")
    monkeypatch.setattr(helper, "REPO", fake_repo)
    case = _case(person="SUJETO_DUPLICADO")
    seed = _write_seed(tmp_path / "new-seed.json", [case])
    out = tmp_path / "entradas_solo"

    code, messages = prep.preparar_entrada_solo(seed, out)

    assert code == 1
    assert any("sujeto repetido" in message for message in messages)
    assert not out.exists()
def test_case_id_from_lote20_is_rejected_before_staging(tmp_path, monkeypatch):
    helper = prep._helpers()
    fake_repo = tmp_path / "repo"
    c01 = fake_repo / "casos" / "ciegos" / "lote_20" / "C01"
    c01.mkdir(parents=True)
    (c01 / "entrada.json").write_text('{"case_id":"C01"}', encoding="utf-8")
    monkeypatch.setattr(helper, "REPO", fake_repo)
    case = _case(case_id="C01", person="SUJETO_NUEVO")
    seed = _write_seed(tmp_path / "new-seed.json", [case])
    out = tmp_path / "entradas_solo"

    code, messages = prep.preparar_entrada_solo(seed, out)

    assert code == 1
    assert any("case_id repetido" in message for message in messages)
    assert not out.exists()


def test_malformed_previous_seed_fails_closed(tmp_path, monkeypatch):
    helper = prep._helpers()
    fake_repo = tmp_path / "repo"
    seeds = fake_repo / "casos" / "fabrica" / "semillas_entrada"
    seeds.mkdir(parents=True)
    (seeds / "old.json").write_text("{broken", encoding="utf-8")
    monkeypatch.setattr(helper, "REPO", fake_repo)

    _ids, _subjects, errors = prep._ids_y_sujetos_previos()

    assert any("JSONDecodeError" in error for error in errors)

