#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""U6 unificado experimental: activa el camino integrado completo sin alterar el canon.

El modo experimental elimina ablations/flags de apagado y desactiva MODO_ESTRICTO
como filtro de cierre. Cada módulo conserva su rol contractual (voto, sensor,
trazabilidad o control); no se convierte indiscriminadamente en escritor de H.
"""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, os, sys, tempfile, traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENGINE = ROOT / "motor" / "motor" / "MOTOR_V15_3_UNICO_20260927.py"
CANON = ROOT / "motor" / "motor" / "Engine_V5_CANONICO_SOLO.py"
PATTERNS = ROOT / "motor" / "motor" / "patterns_final_v14.json"

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def activar_modo_unificado() -> dict:
    # Ninguna ablación heredada ni flag LAT_* puede apagar una pieza en esta variante.
    os.environ["CONSOLIDADO_OFF"] = ""
    os.environ["FAMILIAS_TOKENS"] = "1"
    os.environ["MODO_ESTRICTO"] = "0"
    for key in list(os.environ):
        if key.startswith("LAT_"):
            os.environ[key] = "1"
    return {
        "consolidado_off": os.environ["CONSOLIDADO_OFF"],
        "familias_tokens": os.environ["FAMILIAS_TOKENS"],
        "modo_estricto": os.environ["MODO_ESTRICTO"],
        "lat_flags_forzados_on": sorted(k for k in os.environ if k.startswith("LAT_")),
        "regla_roles": "los módulos ejecutan su rol declarado; los sensores no se convierten en escritores de H"
    }

def cargar_motor():
    if not ENGINE.is_file():
        raise FileNotFoundError(f"UNICO_ENGINE_MISSING:{ENGINE}")
    spec = importlib.util.spec_from_file_location("u6_v153_unificado_experimental_core", ENGINE)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod

def ejecutar_caso(input_path: Path, live_search: bool = True, tag: str = "EXP") -> dict:
    activar = activar_modo_unificado()
    if not all(p.is_file() for p in (CANON, PATTERNS)):
        raise FileNotFoundError("CANON_ENGINE_OR_PATTERNS_MISSING")
    case = json.loads(input_path.read_text(encoding="utf-8"))
    if not isinstance(case.get("cuts"), list) or not case["cuts"]:
        raise ValueError(f"INPUT_CUTS_INVALID:{input_path}")
    original_id = str(case.get("case_id") or input_path.stem)
    case["case_id"] = f"{original_id}_{tag}"
    case["consolidado_off"] = []
    case.pop("_internal_analysis_no_external_search", None)
    tmp = Path(tempfile.gettempdir()) / "u6_unificado_experimental" / case["case_id"]
    tmp.mkdir(parents=True, exist_ok=True)
    case["ceb_root"] = str(tmp / "ceb")
    case["stinkbox_root"] = str(tmp / "stinkbox")
    case["caldero_neighbor_store_root"] = str(tmp / "neighbors")
    os.environ["STINKBOX_STORAGE_ROOT"] = str(tmp / "stinkbox")
    if live_search:
        os.environ["CALDERO_BUSQUEDA_VIVA"] = "1"
        os.environ["CALDERO_BUSCADOR"] = "auto"
        os.environ["SEARCH_PROVIDER"] = "auto"
    else:
        case["_internal_analysis_no_external_search"] = True
    core = cargar_motor()
    result = core.run(case, monte_carlo=False)
    statuses = result.get("execution", {}).get("component_status", [])
    inventory = result.get("execution", {}).get("component_inventory", [])
    registry = result.get("registro_componentes", {}).get("filas", [])
    states = {}
    for row in statuses:
        state = str(row.get("status") or "UNKNOWN")
        states[state] = states.get(state, 0) + 1
    registry_states = {}
    for row in registry:
        state = str(row.get("estado") or "UNKNOWN")
        registry_states[state] = registry_states.get(state, 0) + 1
    critical_errors = [
        {"component": x.get("component"), "status": x.get("status"), "error": x.get("error") or x.get("reason")}
        for x in statuses
        if x.get("status") in {"ERROR", "REQUIRED_STAGE_FAILED", "NO_CORRE", "APAGADO_ABLACION", "PLUGIN_SALTADO"}
    ]
    critical_errors.extend(
        {"component": x.get("pieza"), "status": x.get("estado"), "error": x.get("motivo")}
        for x in registry
        if x.get("severidad") == "FALLO_EJECUCION" or x.get("estado") in {"NO_CORRE", "APAGADA_POR_FLAG"}
    )
    caldero = result.get("features", {}).get("external_archetype_search_receipt", {})
    if live_search and caldero.get("status") != "EXECUTED":
        critical_errors.append({"component": "sidecar_caldero_busqueda_arquetipos.py",
                                "status": caldero.get("status", "NO_RECEIPT"),
                                "error": "la búsqueda viva no quedó confirmada"})
    report = {
        "case_id": case["case_id"],
        "source_input": str(input_path.relative_to(ROOT)),
        "live_search_requested": live_search,
        "live_search_receipt": caldero,
        "engine_version": result.get("version"),
        "catalogue": result.get("catalogo_patrones"),
        "canonical_sha256": {"engine": sha(CANON), "patterns": sha(PATTERNS)},
        "H1": result.get("H1"),
        "H2": result.get("H2"),
        "candidate_count": len(result.get("predictor", {}).get("candidates") or []),
        "component_status_counts": states,
        "registry_state_counts": registry_states,
        "component_inventory": {
            "total": len(inventory),
            "present": sum(bool(x.get("present")) for x in inventory),
            "missing": [x.get("component") for x in inventory if not x.get("present")]
        },
        "critical_errors": critical_errors,
        "activation": activar,
        "execution_identity": result.get("execution_identity"),
        "flow_ledger": result.get("ceb", {}).get("ledger_path") if isinstance(result.get("ceb"), dict) else None,
        "classification": "EXECUTION_CONFIRMED" if not critical_errors else "EXECUTION_PARTIAL_OR_FAILED"
    }
    return {"report": report, "result": result}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", action="append", required=True, help="Ruta a entrada JSON del contrato U6")
    ap.add_argument("--output", default="/tmp/U6_UNIFICADO_EXPERIMENTAL_REPORT.json")
    ap.add_argument("--offline-search", action="store_true", help="Solo para smoke estructural sin proveedor externo")
    args = ap.parse_args()
    reports = []
    for i, name in enumerate(args.case, 1):
        p = (ROOT / name).resolve()
        item = ejecutar_caso(p, live_search=not args.offline_search, tag=f"U6EXP{i}")
        reports.append(item["report"])
        print(json.dumps(item["report"], ensure_ascii=False, indent=2, default=str))
    summary = {
        "version": "U6_UNIFICADO_EXPERIMENTAL_20261104",
        "cases": reports,
        "cases_total": len(reports),
        "cases_without_critical_errors": sum(not x["critical_errors"] for x in reports),
        "components_present_total": sum(x["component_inventory"]["present"] for x in reports),
        "components_declared_total": sum(x["component_inventory"]["total"] for x in reports),
        "critical_errors_total": sum(len(x["critical_errors"]) for x in reports)
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print("U6_UNIFICADO_SUMMARY=" + json.dumps({k:v for k,v in summary.items() if k != "cases"}, ensure_ascii=False))
    if summary["cases_without_critical_errors"] != summary["cases_total"]:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
