#!/usr/bin/env python3
"""Preparación aislada de entradas Z: no carga destinos ni ejecuta el motor.

Entrada: JSON con {"cases": [<entrada completa>, ...]}.
Salida: únicamente entradas_solo/<case_id>/entrada.json y entrada.sha256.
La custodia independiente y la ejecución son procesos posteriores distintos.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
import os
import re
import sys
import tempfile
from functools import lru_cache
from pathlib import Path
from typing import Any

AQUI = Path(__file__).resolve().parent
SEMILLAS_DIR = AQUI / "semillas_entrada"
ENTRADAS_SOLO = AQUI / "entradas_solo"
ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,79}\Z")
CLAVES_DESTINO = {
    "destino", "destino_sellado", "destino_personal", "destino_real",
    "desenlace", "desenlace_sellado", "resultado_real", "ground_truth",
    "label_real", "familias", "familias_desenlace", "prohibidas_post_z",
    "outcome", "truth", "target", "destination", "destinations",
    "h1", "h2", "hypothesis", "hypotheses", "hipotesis", "hipotesis_1",
    "hipotesis_2", "prediction", "prediccion", "predictions", "ranking",
    "caldero_llm_neighbor_hints", "caldero_llm_neighbor_hints_audit",
}


@lru_cache(maxsize=1)
def _helpers():
    """Carga solo helpers puros de fabrica.py; nunca llama preparar_z/correr."""
    path = AQUI / "fabrica.py"
    spec = importlib.util.spec_from_file_location("fabrica_helpers_entry_only", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"No se pudo cargar el módulo de helpers: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _dentro(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def _contiene_clave_destino(value: Any, ruta: str = "$") -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = str(key).strip().lower()
            if normalized in CLAVES_DESTINO:
                found.append(f"{ruta}.{key}")
            found.extend(_contiene_clave_destino(item, f"{ruta}.{key}"))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            found.extend(_contiene_clave_destino(item, f"{ruta}[{index}]"))
    return found


def _agregar_identidad_previa(row: Any, ids: set[str], sujetos: set[str]) -> None:
    if not isinstance(row, dict):
        return
    case_id = row.get("case_id") or row.get("id")
    person = row.get("person") or row.get("subject") or row.get("sujeto")
    if isinstance(case_id, str) and case_id.strip():
        ids.add(case_id.strip().casefold())
    if isinstance(person, str) and person.strip():
        sujetos.add(person.strip().casefold())


def _filas_de_entrada_previa(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict):
        cases = payload.get("cases")
        if isinstance(cases, list):
            return [row for row in cases if isinstance(row, dict)]
        return [payload]
    if isinstance(payload, list):
        return [row for row in payload if isinstance(row, dict)]
    return []


def _leer_entrada_previa(path: Path, ids: set[str], sujetos: set[str], errores: list[str]) -> None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        errores.append(f"{path}: {type(exc).__name__}: {exc}")
        return
    rows = _filas_de_entrada_previa(payload)
    if not rows:
        errores.append(f"{path}: no contiene un objeto de entrada ni una lista cases válida")
        return
    for row in rows:
        _agregar_identidad_previa(row, ids, sujetos)


def _ids_y_sujetos_previos(exclude_path: Path | None = None) -> tuple[set[str], set[str], list[str]]:
    """Indexa entradas previas visibles sin abrir custodia ni salidas congeladas."""
    helper = _helpers()
    repo = Path(helper.REPO)
    ids: set[str] = set()
    sujetos: set[str] = set()
    errores: list[str] = []
    excluded = Path(exclude_path).resolve() if exclude_path is not None else None

    # Registro histórico: solo se extraen case_id/person; no se usan H1/H2 ni desenlaces.
    resultados = repo / "casos" / "resultados" / "resultados.jsonl"
    if resultados.is_file():
        try:
            with resultados.open(encoding="utf-8") as handle:
                for line_number, line in enumerate(handle, start=1):
                    if not line.strip():
                        continue
                    try:
                        row = json.loads(line)
                    except json.JSONDecodeError as exc:
                        errores.append(f"{resultados}:{line_number}: JSONDecodeError: {exc}")
                        continue
                    _agregar_identidad_previa(row, ids, sujetos)
        except (OSError, UnicodeError) as exc:
            errores.append(f"{resultados}: {type(exc).__name__}: {exc}")

    # Entradas ciegas previas: solo entrada.json; cualquier ruta bajo custodia se excluye antes de leer.
    blind_root = repo / "casos" / "ciegos"
    if blind_root.is_dir():
        for path in sorted(blind_root.rglob("entrada.json")):
            if any(part.casefold() == "custodia" for part in path.parts):
                continue
            _leer_entrada_previa(path, ids, sujetos, errores)

    # C01–C20 quedan reservados por ID sin abrir SALIDA_CONGELADA ni custodia.
    lote20 = blind_root / "lote_20"
    if lote20.is_dir():
        try:
            for child in sorted(lote20.iterdir()):
                if child.is_dir() and re.fullmatch(r"C\d{2}", child.name):
                    ids.add(child.name.casefold())
        except OSError as exc:
            errores.append(f"{lote20}: {type(exc).__name__}: {exc}")

    # Semillas F007: AST literal; nunca se importa ni ejecuta el módulo.
    f007 = repo / "casos" / "fabrica" / "semillas_lote_F007.py"
    if f007.is_file():
        try:
            tree = ast.parse(f007.read_text(encoding="utf-8"), filename=str(f007))
        except (OSError, UnicodeError, SyntaxError) as exc:
            errores.append(f"{f007}: {type(exc).__name__}: {exc}")
        else:
            found_assignment = False
            for node in tree.body:
                if not isinstance(node, ast.Assign):
                    continue
                if not any(isinstance(target, ast.Name) and target.id == "SEMILLAS_Z" for target in node.targets):
                    continue
                found_assignment = True
                if not isinstance(node.value, (ast.List, ast.Tuple)):
                    errores.append(f"{f007}: SEMILLAS_Z no es una lista/tupla literal; no se ejecutó el módulo")
                    continue
                for item in node.value.elts:
                    if not isinstance(item, ast.Dict):
                        continue
                    row: dict[str, Any] = {}
                    for key_node, value_node in zip(item.keys, item.values):
                        if not isinstance(key_node, ast.Constant) or not isinstance(key_node.value, str):
                            continue
                        if key_node.value not in {"id", "case_id", "person", "subject", "sujeto"}:
                            continue
                        if isinstance(value_node, ast.Constant):
                            row[key_node.value] = value_node.value
                    _agregar_identidad_previa(row, ids, sujetos)
            if not found_assignment:
                errores.append(f"{f007}: no se encontró SEMILLAS_Z literal; no se ejecutó el módulo")

    fabrica = repo / "casos" / "fabrica"
    semillas_dir = fabrica / "semillas_entrada"
    if semillas_dir.is_dir():
        for path in sorted(semillas_dir.glob("*.json")):
            if path.name == "entrada_schema_v1.json":
                continue
            if excluded is not None and path.resolve() == excluded:
                continue
            _leer_entrada_previa(path, ids, sujetos, errores)

    entradas_dir = fabrica / "entradas_solo"
    if entradas_dir.is_dir():
        for path in sorted(entradas_dir.glob("*/entrada.json")):
            _leer_entrada_previa(path, ids, sujetos, errores)

    return ids, sujetos, errores

def _validar_pares(caso: dict[str, Any], tokens: set[str]) -> list[str]:
    errores: list[str] = []
    case_id = str(caso.get("case_id", "<sin-case_id>"))
    cuts = caso.get("cuts")
    if not isinstance(cuts, list) or not cuts:
        return [f"{case_id}: cuts debe ser una lista no vacía"]
    for index, cut in enumerate(cuts, start=1):
        if not isinstance(cut, dict):
            errores.append(f"{case_id}: cuts[{index - 1}] no es objeto")
            continue
        for field in ("P", "A", "C"):
            pairs = cut.get(field)
            if not isinstance(pairs, list):
                errores.append(f"{case_id}: corte {index}: {field} debe ser lista")
                continue
            for pair_index, pair in enumerate(pairs, start=1):
                if not isinstance(pair, (list, tuple)) or len(pair) != 2:
                    errores.append(f"{case_id}: corte {index} {field}[{pair_index}] debe ser [token, peso]")
                    continue
                token, weight = pair
                if not isinstance(token, str) or token not in tokens:
                    errores.append(f"{case_id}: token fuera del catálogo en corte {index} {field}[{pair_index}]")
                if isinstance(weight, bool) or not isinstance(weight, (int, float)) or not 0.60 <= float(weight) <= 0.84:
                    errores.append(f"{case_id}: peso fuera de 0.60–0.84 en corte {index} {field}[{pair_index}]")
        evidence = cut.get("evidencia")
        if not isinstance(evidence, list) or not evidence:
            errores.append(f"{case_id}: corte {index} requiere evidencia fechada")
            continue
        for ev_index, ev in enumerate(evidence, start=1):
            if not isinstance(ev, dict):
                errores.append(f"{case_id}: evidencia {index}.{ev_index} no es objeto")
                continue
            if str(ev.get("tipo_fuente", "")).strip().lower() != "primaria":
                errores.append(f"{case_id}: evidencia {index}.{ev_index} no es fuente primaria")
    return errores


def _normalizar_caso(caso: dict[str, Any], gate: Any) -> dict[str, Any]:
    normalizado = dict(caso)
    normalizado.setdefault("gate_z", gate.VERSION)
    normalizado.setdefault("z_work_kind", "CASE_CUTOFF")
    cuts = normalizado.get("cuts") or []
    if cuts and isinstance(cuts[-1], dict):
        normalizado.setdefault("z_work_date", cuts[-1].get("date"))
    normalizado.setdefault("source_notes", "")
    raw_cuts = normalizado.get("cuts")
    if isinstance(raw_cuts, list):
        normalized_cuts = []
        for index, raw_cut in enumerate(raw_cuts, start=1):
            if not isinstance(raw_cut, dict):
                normalized_cuts.append(raw_cut)
                continue
            cut = dict(raw_cut)
            cut_id = cut.get("cut_id") or cut.get("id") or f"C{index}"
            cut_date = cut.get("date") or cut.get("fecha_corte")
            cut.setdefault("id", cut_id)
            cut.setdefault("corte", cut_id)
            cut.setdefault("cut_id", cut_id)
            cut.setdefault("date", cut_date)
            cut.setdefault("fecha_corte", cut_date)
            normalized_cuts.append(cut)
        normalizado["cuts"] = normalized_cuts
    return normalizado


def preparar_entrada_solo(seed_json: Path, output_root: Path = ENTRADAS_SOLO) -> tuple[int, list[str]]:
    """Valida un lote JSON y escribe solo entrada.json + entrada.sha256."""
    helper = _helpers()
    seed_json = Path(seed_json)
    output_root = Path(output_root)
    errores: list[str] = []
    if not seed_json.is_file():
        return 2, [f"No existe el JSON de semillas: {seed_json}"]
    try:
        payload = json.loads(seed_json.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return 2, [f"JSON de semillas inválido: {type(exc).__name__}: {exc}"]

    gate = helper._gate()
    tokens, _familias = helper.vocab()
    previous_hashes = helper.hashes_previos()
    previous_ids, previous_subjects, previous_errors = _ids_y_sujetos_previos(exclude_path=seed_json)
    if previous_errors:
        return 1, [f"Índice previo incompleto; no se escribe ninguna entrada: {error}" for error in previous_errors]

    cases = payload.get("cases") if isinstance(payload, dict) else None
    if not isinstance(cases, list) or not cases:
        return 2, ['El JSON debe contener {"cases": [ ... ]} con al menos un caso']

    forbidden_roots = [
        Path(helper.COLA),
        Path(helper.REPO) / "casos" / "ciegos",
        Path(helper.REPO) / "casos" / "fabrica" / "cola",
    ]
    out_resolved = output_root.resolve()
    for forbidden in forbidden_roots:
        f_resolved = forbidden.resolve()
        if out_resolved == f_resolved or _dentro(out_resolved, f_resolved) or _dentro(f_resolved, out_resolved):
            errores.append(f"Salida no aislada; no puede coincidir con ni contener/acceder a {forbidden}")
    if output_root.exists() and not output_root.is_dir():
        errores.append(f"La salida existe y no es directorio: {output_root}")

    seen_ids: set[str] = set()
    seen_subjects: set[str] = set()
    prepared: list[tuple[str, dict[str, Any], str]] = []

    for raw in cases:
        if not isinstance(raw, dict):
            errores.append("Cada elemento de cases debe ser un objeto")
            continue
        caso = _normalizar_caso(raw, gate)
        case_id = caso.get("case_id")
        person = caso.get("person") or caso.get("subject") or caso.get("sujeto")
        if not isinstance(case_id, str) or not ID_RE.fullmatch(case_id):
            errores.append(f"case_id inválido o inseguro: {case_id!r}")
            continue
        if not isinstance(person, str) or not person.strip():
            errores.append(f"{case_id}: falta person/sujeto")
        else:
            person_key = person.strip().casefold()
            if person_key in previous_subjects or person_key in seen_subjects:
                errores.append(f"{case_id}: sujeto repetido; cada caso debe usar sujeto nuevo")
            seen_subjects.add(person_key)
        id_key = case_id.casefold()
        if id_key in previous_ids or id_key in seen_ids:
            errores.append(f"{case_id}: case_id repetido")
        seen_ids.add(id_key)

        forbidden = _contiene_clave_destino(caso)
        if forbidden:
            errores.append(f"{case_id}: contiene campos de destino/desenlace: {', '.join(forbidden)}")
        if caso.get("freeze") != caso.get("z_trabajo"):
            errores.append(f"{case_id}: freeze debe coincidir exactamente con z_trabajo")
        if caso.get("z90_date") != caso.get("z_trabajo"):
            errores.append(f"{case_id}: z90_date debe coincidir exactamente con z_trabajo")
        if not isinstance(caso.get("random_seed"), int) or isinstance(caso.get("random_seed"), bool):
            errores.append(f"{case_id}: random_seed debe ser entero")
        if caso.get("gate_z") != gate.VERSION:
            errores.append(f"{case_id}: gate_z no coincide con la versión vigente {gate.VERSION}")
        if caso.get("z_work_kind") != "CASE_CUTOFF":
            errores.append(f"{case_id}: z_work_kind debe ser CASE_CUTOFF")
        cuts = caso.get("cuts") or []
        if cuts and isinstance(cuts[-1], dict) and caso.get("z_work_date") != cuts[-1].get("date"):
            errores.append(f"{case_id}: z_work_date debe coincidir con el último corte")
        hints, hints_audit, hints_errors = helper._validar_pistas_llm(
            caso.pop("pistas_llm", None), str(person or ""), _familias
        )
        errores.extend(f"{case_id}: {error}" for error in hints_errors)
        caso["caldero_llm_neighbor_hints"] = hints
        caso["caldero_llm_neighbor_hints_audit"] = hints_audit
        errores.extend(_validar_pares(caso, tokens))
        errores.extend(gate.validar_entrada(caso))

        serialized = json.dumps(caso, ensure_ascii=False, indent=2) + "\n"
        digest = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        if digest in previous_hashes or any(digest == item[2] for item in prepared):
            errores.append(f"{case_id}: hash de entrada duplicado")
        prepared.append((case_id, caso, digest))

    if errores:
        return 1, errores

    output_root.parent.mkdir(parents=True, exist_ok=True)
    for case_id, _caso, _digest in prepared:
        if (output_root / case_id).exists():
            errores.append(f"{case_id}: ya existe en entradas_solo; no se sobrescribe")
    if errores:
        return 1, errores
    try:
        with tempfile.TemporaryDirectory(prefix=f".{output_root.name}.stage-", dir=output_root.parent) as tmp:
            stage = Path(tmp)
            for case_id, caso, digest in prepared:
                case_dir = stage / case_id
                case_dir.mkdir()
                serialized = json.dumps(caso, ensure_ascii=False, indent=2) + "\n"
                (case_dir / "entrada.json").write_text(serialized, encoding="utf-8")
                (case_dir / "entrada.sha256").write_text(f"{digest}  entrada.json\n", encoding="utf-8")
            output_root.mkdir(parents=True, exist_ok=True)
            for case_id, _caso, _digest in prepared:
                os.replace(stage / case_id, output_root / case_id)
    except FileExistsError:
        return 1, [f"La salida apareció durante la preparación; no se sobrescribió: {output_root}"]
    except OSError as exc:
        return 3, [f"Error al escribir entrada-only: {type(exc).__name__}: {exc}"]

    return 0, [
        f"ENTRY_ONLY_STAGED: {len(prepared)} entrada(s); no se creó destino, desenlace ni resultado; custodia independiente pendiente",
        "WARN_SUBJECT_UNIQUENESS: las identidades selladas de C01–C20 no se leen; el custodio debe verificar duplicados contra su índice privado antes de aceptar o sellar el lote",
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Prepara únicamente entradas Z desde JSON, sin importar destinos.")
    parser.add_argument("seed_json", help="JSON dentro de casos/fabrica/semillas_entrada/")
    args = parser.parse_args(argv)
    seed_path = Path(args.seed_json).resolve()
    if not _dentro(seed_path, SEMILLAS_DIR):
        print(f"Bloqueado: el JSON debe estar dentro de {SEMILLAS_DIR}", file=sys.stderr)
        return 2
    if seed_path.suffix.lower() != ".json":
        print("Bloqueado: la ruta entry-only acepta únicamente JSON; no importa módulos Python", file=sys.stderr)
        return 2
    code, messages = preparar_entrada_solo(seed_path, ENTRADAS_SOLO)
    for message in messages:
        print(message)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
