#!/usr/bin/env python3
"""Entrada estándar. No depende de /workspace/TIRADA ni de CONSOLIDADO.

Uso:
  python3 correr_estandar.py cuts.json NOMBRE
  python3 correr_estandar.py RESULT.json --t1 futuro.json
  python3 correr_estandar.py caso.json

El LLM produce el JSON (ver CONTRATO_ENTRADA_LLM.txt).
Monte Carlo: ON. Solo se apaga con --no-mc.
Familias laterales: ON (no afinadas; van como backup de arranque).
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MOTOR = ROOT / "motor"
ENGINE_SHA = "665c39a2861e58772522e91272563260d980908b1d4ab9f7092d3413d0c36082"
PAT_SHA = "d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _ceb_root_tmpfs() -> Path | None:
    """Default CEB ledger dir on tmpfs (RAM) when CEB_ROOT is not set.

    The CEB audit ledger writes ~12 MB per run in thousands of small appends.
    On a slow disk (btrfs with writeback) that stalls the motor for minutes:
    observed >300 s timeout with the process in D-state on writeback, while the
    same run finishes in ~14 s with the ledger on tmpfs. The ledger is still
    preserved: preservar_ledger_ceb() copies it next to the RESULT file on disk,
    so the tmpfs copy is disposable. Returns None when no writable tmpfs/tmp
    dir is available, in which case the motor falls back to BASE/ceb_runs.
    An explicit CEB_ROOT (env) or case["ceb_root"] always wins over this.
    """
    candidates = ["/dev/shm", "/tmp"]
    tmpdir = os.environ.get("TMPDIR")
    if tmpdir:
        candidates.append(tmpdir)
    for cand in candidates:
        p = Path(cand) / "ceb_runs"
        try:
            p.mkdir(parents=True, exist_ok=True)
            probe = p / ".ceb_write_probe"
            probe.write_text("ok", encoding="utf-8")
            probe.unlink()
            return p
        except Exception:
            continue
    return None


def _sanitize_json_contract(obj):
    """Serialize safely without mislabeling absent data as epistemic TORTUGAS.

    TORTUGAS is an operational/vectorization state emitted by motor logic, not a
    generic replacement for missing metadata. Paths are preserved for audit.
    """
    import math
    missing=[]; nonfinite=[]
    def walk(x, path="$", keep=False):
        if x is None:
            missing.append(path)
            if path.endswith((".data_table_sha256", ".source_sha256", ".sha256")):
                return "HUELLA_ORIGEN_NO_DISPONIBLE"
            return "DATO_AUSENTE_REQUIERE_CLASIFICACION"
        if isinstance(x, float) and not math.isfinite(x):
            nonfinite.append(path); return "VALOR_NO_FINITO_REQUIERE_REMEDICION"
        if isinstance(x, dict):
            return {k: walk(v, f"{path}.{k}", keep) for k,v in x.items()}
        if isinstance(x, list):
            return [walk(v, f"{path}[{i}]", keep) for i,v in enumerate(x)]
        return x
    cleaned=walk(obj)
    return cleaned, missing, nonfinite


def _continuity_result_payload(continuity_pause):
    """Always expose the run-continuity state in the main result JSON.

    The execution receipt already used NO_PAUSADA as a fallback. Keeping the
    same state in the result avoids a split contract between result and receipt.
    """
    if continuity_pause is not None:
        return continuity_pause
    return {"status": "NO_PAUSADA", "final_decision_authorized": True}


def _receipt_status(search_required_failed, missing_paths, nonfinite_paths):
    """A serializable JSON is not necessarily a complete or resolved run."""
    if search_required_failed:
        return "INCOMPLETE_REQUIRED_EXTERNAL_SEARCH"
    if nonfinite_paths:
        return "INCOMPLETE_NONFINITE_OUTPUT"
    if missing_paths:
        metadata_only = all(p.endswith((".data_table_sha256", ".source_sha256", ".sha256")) for p in missing_paths)
        return "COMPLETED_WITH_METADATA_GAP" if metadata_only else "INCOMPLETE_OUTPUT_DATA"
    return "COMPLETED"


def _observed_tortugas_status(result, terminal=None, alternate_terminal=None):
    """LISTO_CALIBRAR_20261024: lee el estado TORTUGAS de todas las ubicaciones conocidas (primera no vacía)."""
    r017 = result.get("resolucion_operativa_terminal_017") or {}
    cands = [(terminal or {}).get("tortugas_status"), (alternate_terminal or {}).get("tortugas_status"),
             (r017.get("tortugas") or {}).get("status") if isinstance(r017.get("tortugas"), dict) else None,
             ((result.get("cierre_guardianes") or {}).get("tortugas") or {}).get("status") if isinstance((result.get("cierre_guardianes") or {}).get("tortugas"), dict) else None,
             ((result.get("predictor") or {}).get("terminal_resolution") or {}).get("tortugas_status"),
             ((result.get("prediccion") or {}).get("terminal_resolution") or {}).get("tortugas_status")]
    for c in cands:
        if c is not None and str(c).strip():
            return str(c).upper()
    return ""


def _index_last_valid_cut(result, case=None):
    """Índice del último corte procesado por la corrida pausada (todos los cortes del input entraron al motor)."""
    explicit = result.get("ultimo_corte_valido")
    if explicit:
        return explicit
    cuts = (case or {}).get("cuts") or (result.get("case_input") or {}).get("cuts") or []
    if cuts:
        last = cuts[-1] if isinstance(cuts[-1], dict) else {}
        return {"index": len(cuts) - 1, "id": str(last.get("id") or last.get("cut_id") or f"C{len(cuts)}"),
                "date": str(last.get("date") or last.get("fecha") or "SIN_FECHA_EN_INPUT"), "n_cortes": len(cuts),
                "semantica": "ultimo corte del input procesado por el motor antes de la pausa; la reanudacion re-ejecuta el input sellado completo"}
    n = result.get("n_cuts") or result.get("n_cortes") or result.get("n_cortes_observados")
    return {"index": int(n) - 1, "n_cortes": int(n)} if n else "CORTE_FINAL_VALIDO_NO_INDEXADO"


def _declared_absent_hashes(obj, path="$"):
    """Huecos de huella DECLARADOS (no fingidos): quedan visibles en el recibo aunque no cuenten como metadato faltante."""
    out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and v.startswith("NO_APLICA_SIN_") and str(k).endswith("sha256"):
                out.append({"path": f"{path}.{k}", "valor": v, "motivo": obj.get(f"{k}_motivo", "SIN_MOTIVO_DECLARADO")})
            elif isinstance(v, (dict, list)) and k not in ("features",):
                out.extend(_declared_absent_hashes(v, f"{path}.{k}"))
    elif isinstance(obj, list):
        for i, v in enumerate(obj[:200]):
            out.extend(_declared_absent_hashes(v, f"{path}[{i}]"))
    return out


_PAUSA = "PAUSADA_REANUDABLE"
_APUESTA_PAUSADA = "APUESTA_NO_AUTORIZADA_PAUSA_REANUDABLE"


def _apply_continuity_pause(result, pause):
    """LISTO_CALIBRAR_20261024: al pausar, ningún campo puede mostrar apuesta autorizada o cierre de H.
    Se conserva el valor previo en *_previo_a_pausa y H1/H2 quedan como PROVISIONALES etiquetadas."""
    tocados = []
    def _mark(d, path, key="status", value=_PAUSA):
        if isinstance(d, dict) and key in d:
            if d.get(key) != value:
                d[key + "_previo_a_pausa"] = d.get(key)
            d[key] = value; tocados.append(path + "." + key)
    def _prov(d, path):
        if isinstance(d, dict):
            d["decision_final_autorizada"] = False
            if "H1" in d or "H2" in d:
                d["H_estado"] = "PROVISIONAL_NO_AUTORIZADA_POR_PAUSA"
            tocados.append(path + ".decision_final_autorizada")
    for key in ("resolucion_operativa_final", "terminal_resolution", "cierre_final"):
        d = result.get(key)
        if isinstance(d, dict):
            _mark(d, "$." + key); _mark(d, "$." + key, "estado_final"); _prov(d, "$." + key)
    r017 = result.get("resolucion_operativa_terminal_017")
    if isinstance(r017, dict):
        _mark(r017, "$.resolucion_operativa_terminal_017"); _prov(r017, "$.resolucion_operativa_terminal_017")
        _mark(r017.get("decision"), "$.resolucion_operativa_terminal_017.decision"); _prov(r017.get("decision"), "$.resolucion_operativa_terminal_017.decision")
    for parent in ("predictor", "prediccion"):
        tr = (result.get(parent) or {}).get("terminal_resolution") if isinstance(result.get(parent), dict) else None
        if isinstance(tr, dict):
            _mark(tr, f"$.{parent}.terminal_resolution"); _prov(tr, f"$.{parent}.terminal_resolution")
    for key in ("estado_final",):
        if key in result:
            _mark(result, "$", key)
    aud = result.get("auditoria_terminal_valores")
    if isinstance(aud, dict):
        _mark(aud, "$.auditoria_terminal_valores", "estado_final")
    si = result.get("salida_interpretable") if isinstance(result.get("salida_interpretable"), dict) else {}
    for path, d in (("$.salida_interpretable.apuesta_multiescenario", si.get("apuesta_multiescenario")),
                    ("$.apuesta", result.get("apuesta")), ("$.apuesta_trayectoria", result.get("apuesta_trayectoria")),
                    ("$.hipotesis_trayectoria_abierta.apuesta", (result.get("hipotesis_trayectoria_abierta") or {}).get("apuesta") if isinstance(result.get("hipotesis_trayectoria_abierta"), dict) else None),
                    ("$.apuesta_escenarios", result.get("apuesta_escenarios"))):
        if isinstance(d, dict):
            _mark(d, path, "estado", _APUESTA_PAUSADA); d["apuesta_autorizada"] = False
    dh = result.get("decimo_hombre_esteroides")
    if isinstance(dh, dict):
        _mark(dh, "$.decimo_hombre_esteroides", "decision_de_proceso", "SUSPENDIDA_POR_PAUSA_REANUDABLE")
    if si:
        si["H_estado"] = "PROVISIONAL_NO_AUTORIZADA_POR_PAUSA"; si["apuesta_autorizada"] = False
    result["H_estado"] = "PROVISIONAL_NO_AUTORIZADA_POR_PAUSA"
    result["estado_ejecucion"] = _PAUSA
    pause["campos_reescritos_por_pausa"] = tocados
    return result


def _terminal_continuity_gate(result, case=None):
    """Return a resumable pause when the engine has not justified terminal closure.

    This gate never fabricates a winner. Candidate hypotheses remain available for
    continuation, but the output is not represented as a completed final decision.
    """
    terminal = (result.get("resolucion_operativa_final") or result.get("resolucion_operativa_terminal_017")
                or result.get("terminal_resolution") or (result.get("prediccion") or {}).get("terminal_resolution") or {})
    status = str(terminal.get("status", "")).upper()
    state = str(terminal.get("state", terminal.get("estado", ""))).upper()
    decision = result.get("resolucion_operativa_final") or result.get("decision_final") or {}
    decision_status = str(decision.get("status", decision.get("estado", ""))).upper() if isinstance(decision, dict) else ""
    alternate_terminal = (result.get("terminal_resolution") or result.get("resolucion_operativa_terminal_017")
                          or (result.get("prediccion") or {}).get("terminal_resolution") or {})
    tortugas_status = _observed_tortugas_status(result, terminal, alternate_terminal)
    tortugas_executed = bool(terminal.get("tortugas_ejecutado", False) or alternate_terminal.get("tortugas_ejecutado", False)
                             or (decision.get("tortugas_ejecutado", False) if isinstance(decision, dict) else False))
    during = str(decision.get("estado_durante_corrida", "")).upper() if isinstance(decision, dict) else ""
    unresolved_states = {"LATENCIA_INFORMACIONAL", "NO_RESUELTO", "UNRESOLVED", "PENDING", "PENDIENTE", "EMPATE"}
    explicit_pause = status in unresolved_states or state in unresolved_states or decision_status in unresolved_states
    tortugas_failed_when_required = (during == "RESOLUCION_REQUERIDA" and
        (tortugas_status in {"ERROR", "NO_DISPONIBLE", "FAILED", "TIMEOUT"} or not tortugas_executed))
    if not (explicit_pause or tortugas_failed_when_required):
        return None
    hypotheses = result.get("hipotesis") or (result.get("prediccion") or {}).get("candidates") or result.get("candidates") or []
    return {
        "status": "PAUSADA_REANUDABLE",
        "final_decision_authorized": False,
        "reason": "TORTUGAS_REQUIERE_CONTINUACION" if tortugas_failed_when_required else "CIERRE_TERMINAL_NO_VALIDADO",
        "last_valid_cut": _index_last_valid_cut(result, case),
        "hypotheses_preserved": hypotheses,
        "tortugas_status_observed": tortugas_status or "NO_REGISTRADO",
        "required_next_action": "reanudar desde este checkpoint, completar vectorizacion/seguimiento TORTUGAS y volver a evaluar el cierre; no emitir apuesta final hasta validar la resolucion",
    }


def _plain_json_copy(obj):
    """Deep-copy JSON payloads without retaining CEB ObservableDict references from a prior run."""
    return json.loads(json.dumps(obj, ensure_ascii=False, default=str))


def _run_internal_case_isolated(case: dict, run_dir: Path, label: str, timeout_seconds: int = 45) -> dict:
    """Run retained-cut analysis in a child process so CEB audit state cannot leak across runs."""
    import subprocess
    run_dir = Path(run_dir)
    in_path = run_dir / f"_{label}_INPUT.json"
    out_kind = "RESULT" if label == "PRIMARY" else "OUTPUT"
    out_path = run_dir / f"_{label}_{out_kind}.json"
    in_path.write_text(json.dumps(_plain_json_copy(case), ensure_ascii=False, default=str), encoding="utf-8")
    code = (
        "import json,sys; from MOTOR_V15_3_UNICO_20260927 import run; "
        "case=json.loads(open(sys.argv[1],encoding='utf-8').read()); "
        "out=run(case,monte_carlo=True); "
        "open(sys.argv[2],'w',encoding='utf-8').write(json.dumps(out,ensure_ascii=False,indent=1,default=str))"
    )
    try:
        env = os.environ.copy()
        if "CEB_ROOT" not in env:
            tmpfs_root = _ceb_root_tmpfs()
            if tmpfs_root is not None:
                env["CEB_ROOT"] = str(tmpfs_root)
        proc = subprocess.run([sys.executable, "-c", code, str(in_path), str(out_path)], cwd=str(run_dir),
                              text=True, capture_output=True, timeout=timeout_seconds, env=env)
    except subprocess.TimeoutExpired as exc:
        return {"_internal_run_status":"TIMEOUT", "label":label, "timeout_seconds":timeout_seconds,
                "stdout_tail":str(exc.stdout or "")[-2000:], "stderr_tail":str(exc.stderr or "")[-2000:]}
    if proc.returncode != 0 or not out_path.is_file():
        return {"_internal_run_status":"ERROR", "label":label, "returncode":proc.returncode,
                "stdout_tail":proc.stdout[-2000:], "stderr_tail":proc.stderr[-2000:]}
    out = json.loads(out_path.read_text(encoding="utf-8"))
    out["_internal_run_status"] = "COMPLETED_ISOLATED_SUBPROCESS"
    out["_internal_run_label"] = label
    return out


def _json_health(obj):
    import math
    nulls=0; nonfinite=0
    def walk(x):
        nonlocal nulls, nonfinite
        if x is None: nulls += 1
        elif isinstance(x,float) and not math.isfinite(x): nonfinite += 1
        elif isinstance(x,dict):
            for v in x.values(): walk(v)
        elif isinstance(x,list):
            for v in x: walk(v)
    walk(obj)
    return {"nulls":nulls,"nonfinite":nonfinite}


def _envolver(raw, nombre: str):
    if isinstance(raw, dict) and raw.get("cuts"):
        raw.setdefault("case_id", nombre)
        raw.setdefault("question", raw.get("case_id", nombre))
        return raw
    if isinstance(raw, list):
        return {"case_id": nombre, "question": nombre, "cuts": raw}
    raise SystemExit("input inválido: se espera lista de cortes o dict con cuts")


def _build(rd: Path) -> None:
    if rd.exists():
        shutil.rmtree(rd)
    rd.mkdir(parents=True)
    for p in MOTOR.iterdir():
        dest = rd / p.name
        if p.is_file():
            shutil.copy2(p, dest)
        elif p.is_dir() and p.name in ("familias_tokens", "vecinos_caldero", "tokens_laterales", "geometria_multicapa"):
            shutil.copytree(p, dest)
    if not (rd / "MOTOR_V15_3_NATIVO_V0_9.py").exists() and (rd / "MOTOR_V15_3_NATIVO_V0_9_UNICO.py").exists():
        shutil.copy2(rd / "MOTOR_V15_3_NATIVO_V0_9_UNICO.py", rd / "MOTOR_V15_3_NATIVO_V0_9.py")


MANIFIESTO = ROOT / "UNIFICACION_SHA256_MANIFEST.json"
_BLOQUEANTES = ("motor/Engine_V5_CANONICO_SOLO.py", "motor/patterns_final_v14.json")


def verificar_manifiesto() -> dict:
    """U6 #4: preflight contra UNIFICACION_SHA256_MANIFEST.json. Deriva = AVISO (se registra en el recibo).
    Solo bloquea si Engine o patterns difieren del manifiesto o de los sha canónicos."""
    rep = {"stage": "unification_manifest_check", "manifest": MANIFIESTO.name}
    if not MANIFIESTO.is_file():
        rep.update({"status": "NOT_CONFIGURED", "bloquea": False}); return rep
    m = json.loads(MANIFIESTO.read_text(encoding="utf-8"))
    rep["manifest_sha256"] = sha(MANIFIESTO); rep["manifest_files"] = len(m.get("files") or [])
    deriva, ausentes = [], []
    for e in m.get("files") or []:
        q = ROOT / e["path"]
        if not q.is_file(): ausentes.append(e["path"]); continue
        h = sha(q)
        if h != e["sha256"]: deriva.append({"path": e["path"], "manifiesto": e["sha256"][:12], "actual": h[:12]})
    en = {e["path"] for e in m.get("files") or []}
    fuera = sorted(str(q.relative_to(ROOT)) for q in MOTOR.rglob("*") if q.is_file() and "__pycache__" not in q.parts
                   and "_ARCHIVADO_U6" not in q.parts and str(q.relative_to(ROOT)) not in en
                   and not any(str(q.relative_to(ROOT)).startswith(x) for x in (m.get("excluidos_estado_mutable") or [])))
    bloq = [d for d in deriva if d["path"] in _BLOQUEANTES] + [{"path": a, "ausente": True} for a in ausentes if a in _BLOQUEANTES]
    if sha(MOTOR / "Engine_V5_CANONICO_SOLO.py") != ENGINE_SHA: bloq.append({"path": _BLOQUEANTES[0], "esperado": ENGINE_SHA[:12]})
    if sha(MOTOR / "patterns_final_v14.json") != PAT_SHA: bloq.append({"path": _BLOQUEANTES[1], "esperado": PAT_SHA[:12]})
    rep.update({"deriva": deriva, "ausentes": ausentes, "motor_fuera_de_manifiesto": fuera, "bloqueantes": bloq,
                "bloquea": bool(bloq),
                "status": "BLOCKED_ENGINE_OR_PATTERNS" if bloq else ("MATCH" if not (deriva or ausentes or fuera) else "DRIFT_WARNED")})
    return rep


def verificar_candado_plugins() -> dict:
    """U6 #2: motor/candado_plugins.py cableado (antes 0 llamadas). Compila cada .py de motor/ y prohíbe imports directos
    al Engine. Solo AVISA; no escribe manifiesto_plugins.json (eso es registrar_o_comparar, que muta estado)."""
    import importlib.util as _iu
    q = MOTOR / "candado_plugins.py"
    if not q.is_file(): return {"stage": "candado_plugins", "status": "NOT_CONFIGURED"}
    sp = _iu.spec_from_file_location("candado_plugins_u6", str(q)); cp = _iu.module_from_spec(sp); sp.loader.exec_module(cp)
    ok, fallos = 0, []
    for f in sorted(MOTOR.glob("*.py")):
        if f.name == "Engine_V5_CANONICO_SOLO.py": continue
        try: cp.verificar_plugin(str(f)); ok += 1
        except Exception as e: fallos.append({"file": f.name, "error": f"{type(e).__name__}: {str(e)[:200]}"})
    return {"stage": "candado_plugins", "status": "OK" if not fallos else "WARN", "verificados": ok, "fallos": fallos, "bloquea": False}


def preservar_ledger_ceb(rd: Path, out: Path, result: dict | None = None) -> dict:
    """U6 #5: _build() hace rmtree de runs/ESTANDAR__X en cada corrida y el ledger CEB se perdía.
    Se copian los .jsonl junto al resultado (antes de cualquier borrado) con su sha256."""
    src = rd / "ceb_runs"; filas = []
    sources = list(sorted(src.glob("*.jsonl"))) if src.is_dir() else []
    external_ledger = ((result or {}).get("ceb") or {}).get("ledger")
    if external_ledger:
        ext = Path(str(external_ledger))
        if ext.is_file() and ext not in sources:
            sources.append(ext)
    for i, f in enumerate(sources):
        dest = out.with_name(f"{out.stem}_CEB_LEDGER_{i + 1}.jsonl")
        shutil.copy2(f, dest)
        with dest.open("rb") as ledger_stream:
            lineas = sum(1 for _ in ledger_stream)
        filas.append({"original": str(f), "copia": str(dest), "sha256": sha(dest), "bytes": dest.stat().st_size,
                      "lineas": lineas})
    man = {"version": "CEB_LEDGER_PRESERVADO_U6", "run_dir": str(rd), "ledgers": filas}
    mp = out.with_name(out.stem + "_CEB_LEDGER_MANIFIESTO.json")
    mp.write_text(json.dumps(man, ensure_ascii=False, indent=1), encoding="utf-8")
    man["manifiesto"] = str(mp)
    return man


def _fam(h):
    if isinstance(h, dict):
        return h.get("family") or h.get("nucleo")
    return h


def puntuar_t1(sello: dict, cuts_t1, motor_t1: dict) -> dict:
    """Contrasta H sellada con evidencia predictiva explícita en T+1.

    Los candidatos recuperados desde el propio corte sirven para continuidad
    operativa/TORTUGAS, pero no se cuentan como predicción prospectiva. El runner
    previo leía solo P/A_top5_ANEXO y devolvía tops_t1=[]; la primera reparación
    encontró candidatos recuperados y habría contado un HIT espurio. Esta versión
    conserva ambos datos y solo emite HIT/MISS cuando hay candidatos predictivos
    no recuperados o anexos explícitos de T+1.
    """
    h1 = _fam(sello.get("H1"))  # legacy compatibility only
    h2 = _fam(sello.get("H2"))  # legacy compatibility only
    open_h = sello.get("hipotesis") or ((sello.get("hipotesis_trayectoria_abierta") or {}).get("hipotesis") or [])
    has_open_set = bool(open_h)
    sealed_hypotheses = []
    for h in open_h:
        fam = _fam(h.get("familia") if isinstance(h, dict) else h)
        if fam and fam not in sealed_hypotheses: sealed_hypotheses.append(fam)
    if not sealed_hypotheses:
        sealed_hypotheses = [x for x in (h1, h2) if x]
    tops, evidence_tops, recovered = [], [], []
    predictor = motor_t1.get("predictor") or {}
    terminal = motor_t1.get("resolucion_operativa_terminal_017") or {}
    for collection in (predictor.get("candidates") or [], terminal.get("candidates") or []):
        for item in collection:
            name = _fam(item)
            if not name:
                continue
            if name not in tops:
                tops.append(name)
            if isinstance(item, dict) and item.get("recovered_from_cut"):
                if name not in recovered:
                    recovered.append(name)
            elif name not in evidence_tops:
                evidence_tops.append(name)
    # Explicit per-cut predictive annexes are valid T+1 evidence.
    cuts = motor_t1.get("cuts") or (motor_t1.get("motor") or {}).get("cuts") or []
    last = cuts[-1] if cuts else {}
    for key in ("P_top5_ANEXO", "A_top5_ANEXO"):
        for row in (last.get(key) or []):
            name = _fam(row[0] if isinstance(row, (list, tuple)) and row else row)
            if name:
                if name not in tops:
                    tops.append(name)
                if name not in evidence_tops:
                    evidence_tops.append(name)
    matched_hypotheses = [h for h in sealed_hypotheses if h in evidence_tops]
    if not evidence_tops:
        hit = "INCONCLUSO_CANDIDATOS_RECUPERADOS_NO_PRONOSTICO" if tops else "INCONCLUSO_SIN_CANDIDATOS_T1"
    elif has_open_set and matched_hypotheses:
        hit = "HIT_HIPOTESIS_SET"
    elif has_open_set:
        hit = "MISS_HIPOTESIS_SET"
    elif h1 and h1 in evidence_tops:
        hit = "HIT_H1"
    elif h2 and h2 in evidence_tops:
        hit = "HIT_H2"
    else:
        hit = "MISS"
    return {
        "t_plus_1_abierto": True,
        "H_intacta": True,
        "hipotesis_selladas": sealed_hypotheses,
        "hipotesis_con_evidencia_t1": matched_hypotheses,
        "evaluacion_primaria": "SET_ABIERTO_DE_HIPOTESIS" if has_open_set else "H1_H2_COMPATIBILIDAD_HISTORICA",
        "H1_sellada_compatibilidad": h1,
        "H2_sellada_compatibilidad": h2,
        "tops_t1": tops[:10],
        "tops_t1_con_evidencia_predictiva": evidence_tops[:10],
        "candidatos_recuperados_no_contados_como_prediccion": recovered[:10],
        "hit_H": hit,
        "n_cuts_t1": len(list(cuts_t1)),
        "fuente_tops_t1": "anexo T+1/candidatos no recuperados" if evidence_tops else "solo candidatos recuperados o sin candidatos",
    }


def _parse_standard_args(argv):
    """Parse input/name/output independently from --no-mc, wherever it appears."""
    positional = [x for x in argv[1:] if x != "--no-mc"]
    if not positional:
        raise SystemExit("uso: python3 correr_estandar.py cuts.json [NOMBRE] [salida.json]")
    src = Path(positional[0]).resolve()
    nombre = positional[1] if len(positional) > 1 and not positional[1].endswith(".json") else src.stem
    out = Path(positional[2]).resolve() if len(positional) > 2 else ROOT / f"RESULT_{nombre}.json"
    return src, nombre, out, "--no-mc" in argv


def _configure_stinkbox_home() -> tuple[Path, Path]:
    """Keep StinkBox storage and registry outside the replaceable motor package."""
    explicit = os.environ.get("STINKBOX_HOME")
    if explicit:
        home = Path(explicit).expanduser().resolve()
    else:
        candidates = [ROOT.parent / "STINKBOX_PERSISTENTE_20261020", ROOT.parent / "STINKBOX_PERSISTENTE", Path.home() / "STINKBOX_PERSISTENTE"]
        home = next((p.resolve() for p in candidates if (p / "data" / "registro_tokens.json").is_file()), candidates[-1].resolve())
    home.mkdir(parents=True, exist_ok=True)
    os.environ["STINKBOX_HOME"] = str(home)
    storage = Path(os.environ.get("STINKBOX_STORAGE_ROOT") or os.environ.get("STINKBOX_STORAGE") or (home / "STINKBOX_STORAGE")).expanduser().resolve()
    storage.mkdir(parents=True, exist_ok=True)
    os.environ["STINKBOX_STORAGE_ROOT"] = str(storage)
    os.environ["STINKBOX_STORAGE"] = str(storage)
    return home, storage

def _ingest_stinkbox_registry(home: Path, storage: Path, run_dir: Path) -> dict:
    """Import persistent case files and this run's discovery/neighbor artifacts."""
    registry_script = ROOT / "stinkbox_registry.py"
    if not registry_script.is_file():
        return {"status": "NOT_CONFIGURED", "reason": "stinkbox_registry.py missing"}
    summaries = []
    for source in (run_dir, storage):
        try:
            proc = __import__("subprocess").run([sys.executable, str(registry_script), "ingest", str(source)], cwd=str(ROOT), text=True, capture_output=True, timeout=120, env=os.environ.copy())
            try: detail = json.loads(proc.stdout)
            except Exception: detail = {"stdout": proc.stdout[-2000:]}
            summaries.append({"source": str(source), "returncode": proc.returncode, "detail": detail, "stderr": proc.stderr[-1000:]})
        except Exception as exc:
            summaries.append({"source": str(source), "returncode": -1, "error": f"{type(exc).__name__}:{exc}"})
    ok = all(x.get("returncode") == 0 for x in summaries)
    return {"status": "OK" if ok else "ERROR", "home": str(home), "storage": str(storage), "imports": summaries}

def main(argv) -> int:
    if "--no-mc" in argv:
        raise SystemExit("MONTE_CARLO_OBLIGATORIO: --no-mc está bloqueado en corridas estándar; úsese solo en pruebas unitarias aisladas.")
    if len(argv) < 2:
        print("uso: python3 correr_estandar.py cuts.json [NOMBRE] [salida.json]", file=sys.stderr)
        print("     python3 correr_estandar.py RESULT.json --t1 futuro.json [salida.json]", file=sys.stderr)
        return 2

    stink_home, stink_storage = _configure_stinkbox_home()

    if "--t1" in argv:
        i = argv.index("--t1")
        seal_path = Path(argv[1]).resolve()
        future_path = Path(argv[i + 1]).resolve()
        sello = json.loads(seal_path.read_text(encoding="utf-8"))
        fut = json.loads(future_path.read_text(encoding="utf-8"))
        cuts_t1 = fut["cuts"] if isinstance(fut, dict) and "cuts" in fut else fut
        out = Path(argv[i + 2]).resolve() if len(argv) > i + 2 else (ROOT / "RESULT_T1.json").resolve()
        nombre = str((sello.get("case_id") or "T1") + "_t1")
        case = _envolver({"cuts": cuts_t1, "case_id": nombre, "question": nombre}, nombre)
        case["random_seed"] = 0
        rd = ROOT / "runs" / f"ESTANDAR__{nombre}"
        _build(rd)
        sys.path.insert(0, str(rd))
        os.chdir(rd)
        os.environ["PYTHONHASHSEED"] = "0"
        from MOTOR_V15_3_UNICO_20260927 import run
        motor_t1 = run(case, monte_carlo=True)
        # Persist tokens before scoring/formatting; a later failure must not lose the primary run's memory.
        stinkbox_primary_checkpoint = _ingest_stinkbox_registry(stink_home, stink_storage, rd)
        score = puntuar_t1(sello, cuts_t1, motor_t1)
        score["stinkbox_persistent_registry_primary_checkpoint"] = stinkbox_primary_checkpoint
        score["motor_t1_H1"] = _fam(motor_t1.get("H1"))
        score["nota"] = "H del sello no se reescribe. motor_t1_H1 es solo contraste."
        score["stinkbox_persistent_registry"] = _ingest_stinkbox_registry(stink_home, stink_storage, rd)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(score, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
        print(json.dumps({"ok": True, **{k: score[k] for k in ("hit_H", "H1_sellada", "H2_sellada")}, "stinkbox_persistent_registry": score["stinkbox_persistent_registry"]}, ensure_ascii=False))
        return 0

    # Flags are never interpreted as file paths; MC is then enforced below.
    try:
        src, nombre, out, no_mc = _parse_standard_args(argv)
    except SystemExit as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if no_mc:
        raise SystemExit("MONTE_CARLO_OBLIGATORIO: --no-mc está bloqueado en corridas estándar; úsese solo en pruebas unitarias aisladas.")
    raw = json.loads(src.read_text(encoding="utf-8"))
    case = _envolver(raw, nombre)
    if "random_seed" not in case:
        case["random_seed"] = 0

    # Mandatory package-integrity gate: never run a reconstructed pack with
    # duplicate critical artifacts carrying different bytes.
    preflight = ROOT / "scripts" / "preflight_integridad.py"
    if preflight.is_file():
        import subprocess as _subprocess
        pf = _subprocess.run([sys.executable, str(preflight)], cwd=str(ROOT), text=True, capture_output=True)
        if pf.returncode != 0:
            print(pf.stdout, file=sys.stderr)
            print("PREFLIGHT_INTEGRIDAD_FALLIDO: corrida bloqueada", file=sys.stderr)
            return 4

    eng = MOTOR / "Engine_V5_CANONICO_SOLO.py"
    pat = MOTOR / "patterns_final_v14.json"
    if not eng.is_file() or not pat.is_file():
        print("FALTA Engine o patterns en motor/", file=sys.stderr)
        return 3
    # U6 #4: manifiesto SHA256 del pack en preflight (aviso + recibo; bloquea solo Engine/patterns)
    man_check = verificar_manifiesto()
    if man_check.get("bloquea"):
        print("MANIFIESTO: Engine o patterns no coinciden -> corrida bloqueada " + json.dumps(man_check.get("bloqueantes")), file=sys.stderr)
        return 5
    if man_check.get("status") == "DRIFT_WARNED":
        print(f"AVISO MANIFIESTO: deriva={len(man_check['deriva'])} ausentes={len(man_check['ausentes'])} fuera={len(man_check['motor_fuera_de_manifiesto'])}", file=sys.stderr)
    candado_check = verificar_candado_plugins()
    if candado_check.get("fallos"):
        print("AVISO CANDADO_PLUGINS: " + json.dumps(candado_check["fallos"], ensure_ascii=False)[:500], file=sys.stderr)
    if sha(pat) != PAT_SHA:
        print("AVISO: patterns no es v14 d827dcc3", file=sys.stderr)
    if sha(eng) != ENGINE_SHA:
        print("AVISO: Engine no coincide con el canónico autorizado de este pack", file=sys.stderr)

    # A5_20261107 — filtro 017 (filtro_entrada_dirigida) en la entrada estándar.
    # FILTRO_017=traza (defecto): analiza y deja traza sin modificar el caso.
    # activo: neutraliza identidad/obra/calendario en el payload. off: apagado.
    # Se aplica ANTES de escribir _INPUT.json para que el input sellado sea el
    # que el motor consume (el runner lo vuelve a aplicar dentro de run() como
    # red de seguridad para llamadas directas; es idempotente). La consulta
    # dirigida NO se duplica en run(): ya vive aquí y duplicarla preguntaría dos veces.
    _f017_traza = None
    _f017_modo = os.environ.get("FILTRO_017", "traza").strip().lower()
    if _f017_modo in ("activo", "traza"):
        import importlib.util as _iuf017
        _f017p = ROOT / "capa_llm" / "filtro_entrada_dirigida_017.py"
        _f017s = _iuf017.spec_from_file_location("filtro_entrada_dirigida_017", str(_f017p))
        _f017 = _iuf017.module_from_spec(_f017s); _f017s.loader.exec_module(_f017)
        _f017_cat = json.loads((MOTOR / "patterns_final_v14.json").read_text(encoding="utf-8"))
        case, _f017_traza = _f017.compuerta(case, _f017_modo, _f017_cat)

    # UNIFICADO_20261011 — capa LLM de CONSULTAS DIRIGIDAS (fuera del motor). CONSULTA_DIRIGIDA=off (defecto) no toca nada.
    #   on|offline: adaptador OFFLINE (sin respuestas, sin red)   mock: respuestas fijas de prueba (CONSULTA_FIXTURE, CONSULTA_CASE_KEY)
    _cd_traza = None
    _cd_modo = os.environ.get("CONSULTA_DIRIGIDA", "off").strip().lower()
    if _cd_modo in ("on", "offline", "mock"):
        import importlib.util as _iucd
        _cdp = ROOT / "capa_llm" / "consulta_dirigida_v1.py"
        _cds = _iucd.spec_from_file_location("consulta_dirigida_v1", str(_cdp))
        _cd = _iucd.module_from_spec(_cds); _cds.loader.exec_module(_cd)
        _cdR = _cd.Recursos(MOTOR)
        if _cd_modo == "mock":
            _cdfx = json.loads(Path(os.environ["CONSULTA_FIXTURE"]).read_text(encoding="utf-8"))
            _cdad = _cd.AdaptadorMock(_cdfx, os.environ.get("CONSULTA_CASE_KEY") or nombre)
        else:
            _cdad = _cd.AdaptadorOffline()
        case, _cd_traza, _cd_side = _cd.aplicar(case, _cdad, _cdR)
        out.parent.mkdir(parents=True, exist_ok=True)
        # SIDECAR SELLADO: procedencia y texto original de cada respuesta. Fuera de runs/: el motor no lo lee.
        out.with_name(out.stem + "_CONSULTA_SELLADO.json").write_text(json.dumps(_cd_side, ensure_ascii=False, indent=1, default=str), encoding="utf-8")

    rd = ROOT / "runs" / f"ESTANDAR__{nombre}"
    _build(rd)
    inp = rd / "_INPUT.json"
    inp.write_text(json.dumps(case, ensure_ascii=False, indent=2), encoding="utf-8")
    sys.path.insert(0, str(rd))
    os.chdir(rd)
    os.environ["PYTHONHASHSEED"] = "0"
    os.environ.pop("MOTOR_PATTERNS_PATH", None)
    t0 = time.time()
    toks=[]
    for c in case.get("cuts") or []:
        for eje in ("P","A","C"):
            for row in c.get(eje) or []:
                toks.append(row[0] if isinstance(row,(list,tuple)) else row)
    # PATCH10: no se fabrican fuentes ni recibos de búsqueda. Si el input no trae
    # fixtures verificables, el motor debe llamar Exa mediante EXA_API_KEY y marcar
    # el fallo como etapa obligatoria cuando el proveedor no esté configurado.
    result = _run_internal_case_isolated(case, rd, "PRIMARY", timeout_seconds=90)
    if result.get("_internal_run_status") != "COMPLETED_ISOLATED_SUBPROCESS":
        print(json.dumps({"ok": False, "stage": "primary_motor_subprocess", "error": result}, ensure_ascii=False))
        return 3
    result.pop("_internal_run_status", None)
    result.pop("_internal_run_label", None)
    result["primary_run_isolated_subprocess"] = True
    # Durable checkpoint immediately after the primary run, before retained-cut analyses/ledgers.
    # If later work times out, token events from the primary run are already indexed.
    _stinkbox_primary_checkpoint = _ingest_stinkbox_registry(stink_home, stink_storage, rd)
    result["stinkbox_persistent_registry_primary_checkpoint"] = _stinkbox_primary_checkpoint
    # U6 repair 2026-10-15: active observational mortality matrix. It cannot write H or rank.
    from motor.matriz_mortalidad_z90_v0_2 import build_mortality_matrix
    _mortality_matrix = build_mortality_matrix(case, result, ROOT)
    result["matriz_mortalidad_z90"] = _mortality_matrix
    _component_rows = result.setdefault("registro_componentes", {}).setdefault("filas", [])
    _component_rows.append({
    "pieza": "matriz_mortalidad_z90_v0_2",
    "fuente": "motor",
    "estado": "ACTIVA_DIAGNOSTICA",
    "estado_crudo": _mortality_matrix["status"],
    "alimenta_predictor": False,
    "can_decide_H": False,
    "motivo": "Cableada en runner; estadísticas solo con filas verificadas; no escribe H1/H2."
    })
    result["registro_componentes"]["conteo"] = len(_component_rows)
    _search_run = ((result.get("features") or {}).get("external_archetype_search_receipt") or {})
    result["external_archetype_search_receipt"] = _search_run
    _hist_path = ROOT / "HISTORICAL_PREDICTIVE_REFERENCE.json"
    _hist_ref = json.loads(_hist_path.read_text(encoding="utf-8")) if _hist_path.is_file() else None
    result["predictive_validation"] = {
        "status": "NOT_CALIBRATED_NO_CASE_LEVEL_OUTCOMES",
        "structural_fill_is_probability": False,
        "rank_fusion_is_probability": False,
        "historical_reference": _hist_ref,
        "reason": "hay una referencia histórica de acierto Top-1/Top-3 del predictor lateral, pero faltan scores y desenlaces sellados por caso para ajustar/calibrar una probabilidad del motor actual; no se sustituyen por porcentajes estructurales ni por ejemplos de otros dominios"
    }
    import importlib.util
    _sp = Path(__file__).resolve().parent / "motor" / "plugin_entrega_luces_v1.py"
    _spec = importlib.util.spec_from_file_location("entrega", _sp)
    _mod = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_mod)
    result["entrega"] = _mod.entregar(result)
    dt = time.time() - t0
    result["estandar"] = {
        "entrada": "correr_estandar.py",
        "monte_carlo": True,
        "engine_sha256": sha(eng),
        "patterns_sha256": sha(pat),
        "seconds": round(dt, 3),
        "familias_tokens": "ON_NO_AFINADAS",
        "entrada_por": "LLM",
        "contrato_entrada": "CONTRATO_ENTRADA_LLM.txt",
        "t1": "despues: correr_estandar.py RESULT.json --t1 futuro.json",
    }
    cuts=_plain_json_copy(case.get("cuts") or [])
    if len(cuts)>=2:
        retenido=_plain_json_copy(cuts[-1])
        previo=_plain_json_copy(case)
        previo["cuts"]=_plain_json_copy(cuts[:-1])
        previo["case_id"]=str(case.get("case_id"))+"_SIN_ULTIMO"
        previo["_internal_analysis_no_external_search"]=True
        visto_case={"cuts":[retenido],"case_id":str(case.get("case_id"))+"_RETENIDO","question":"retenido",
                    "random_seed":int(case.get("random_seed",0)),"_internal_analysis_no_external_search":True}
        # The CEB tracer installs process audit hooks. Isolate the retained-cut reruns so
        # one execution cannot contaminate or stall the next calibration comparison.
        sello=_run_internal_case_isolated(previo, rd, "INTERNAL_PREVIO")
        visto=_run_internal_case_isolated(visto_case, rd, "INTERNAL_RETENIDO")
        if sello.get("_internal_run_status") != "COMPLETED_ISOLATED_SUBPROCESS" or visto.get("_internal_run_status") != "COMPLETED_ISOLATED_SUBPROCESS":
            result["efectividad_corte_retenido"]={"estado":"INTERNAL_T1_RUN_FAILED", "previo_status":sello.get("_internal_run_status"),
                "visto_status":visto.get("_internal_run_status"), "previo_error":sello.get("stderr_tail"), "visto_error":visto.get("stderr_tail"),
                "hit_H":"INCONCLUSO_CORRIDA_INTERNA_FALLIDA"}
        else:
            result["efectividad_corte_retenido"]=puntuar_t1(_plain_json_copy(sello), [retenido], _plain_json_copy(visto))
            result["efectividad_corte_retenido"]["internal_runs_isolated"] = True
    _ceb_pres = preservar_ledger_ceb(rd, out, result)
    if isinstance(result.get("ceb"), dict):
        result["ceb"]["ledger_preservado_U6"] = _ceb_pres
        # The main result points at the preserved artifact, not the temporary runtime copy.
        original_ledger = result["ceb"].get("ledger")
        if original_ledger:
            match = next((row for row in _ceb_pres.get("ledgers", [])
                          if str(Path(row.get("original", "")).resolve()) == str(Path(str(original_ledger)).resolve())), None)
            if match:
                result["ceb"]["ledger_original_runtime_path"] = str(original_ledger)
                result["ceb"]["ledger"] = match["copia"]
                result["ceb"]["ledger_path_kind"] = "PRESERVED_COPY"
    if _cd_traza is not None:
        result["consulta_dirigida"] = _cd_traza  # traza sin contenido original (ids, estados, motivos, huellas)
    # A5_20261107: la traza del filtro 017 ya viene en result si run() la puso;
    # aquí solo se registra la de la entrada estándar si run() no la dejó.
    if _f017_traza is not None and "filtro_entrada_dirigida_017" not in result:
        result["filtro_entrada_dirigida_017"] = _f017_traza  # traza sin contenido original (solo huellas)
    # A missing terminal justification pauses the execution for continuation; it is
    # never converted into a final hypothesis/decision by the serializer.
    _continuity_pause = _terminal_continuity_gate(result, case)
    result["continuidad_corrida"] = _continuity_result_payload(_continuity_pause)
    if _continuity_pause is not None:
        _apply_continuity_pause(result, _continuity_pause)
    # Final serialization is not epistemic resolution: missing data remain explicit
    # data-quality markers and are recorded in the receipt, never relabeled TORTUGAS.
    result, _result_missing_paths, _result_nonfinite_paths = _sanitize_json_contract(result)
    result["auditoria_salida_json"] = {
        "contrato": "SIN_NULL_SIN_NAN_SIN_NAPIC",
        "faltantes_detectados": len(_result_missing_paths),
        "no_finitos_detectados": len(_result_nonfinite_paths),
        "rutas_faltantes": _result_missing_paths,
        "rutas_no_finitas": _result_nonfinite_paths,
        "estado": "LIMPIO" if not _result_missing_paths and not _result_nonfinite_paths else "REQUIERE_CLASIFICACION_O_REMEDICION"
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False, default=str), encoding="utf-8")

    # Sidecar de evidencia de ejecución: se escribe solo después de terminar la corrida
    # y de existir el JSON de resultado. La búsqueda externa se marca ejecutada únicamente
    # cuando el input trae un recibo de búsqueda con consultas y resultados registrados.
    receipt_path = out.with_name(out.stem + "_RECIBO_EJECUCION.json")
    search_receipt = result.get("external_archetype_search_receipt") or {}
    search_performed = bool(search_receipt.get("status") == "EXECUTED" and
                            search_receipt.get("provider") not in (None, "provided_fixture", "static_fixture") and
                            int(search_receipt.get("query_count", 0)) >= 1 and
                            int(search_receipt.get("result_count", 0)) >= 1)
    search_required_failed = bool(search_receipt.get("required") and not search_performed)
    terminal = result.get("terminal_resolution") or result.get("resolucion_operativa_final") or result.get("resolucion_operativa_terminal_017") or (result.get("prediccion") or {}).get("terminal_resolution") or {}
    receipt = {
        "receipt_version": "EXECUTION_RECEIPT_V1",
        "status": "PAUSED_REQUIRES_RESUME" if _continuity_pause is not None else _receipt_status(search_required_failed, _result_missing_paths, _result_nonfinite_paths),
        "case_id": result.get("case_id"),
        "started_epoch": round(t0, 6),
        "finished_epoch": round(t0 + dt, 6),
        "duration_seconds": round(dt, 3),
        "input_path": str(src.resolve()),
        "input_sha256": sha(src),
        "normalized_input_sha256": hashlib.sha256(json.dumps(case, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")).hexdigest(),
        "output_path": str(out.resolve()),
        "output_sha256": sha(out),
        "runner_path": str(Path(__file__).resolve()),
        "runner_sha256": sha(Path(__file__).resolve()),
        "motor_sha256": sha(rd / "MOTOR_V15_3_UNICO_20260927.py"),
        "canonical_engine_sha256": sha(eng),
        "patterns_sha256": sha(pat),
        "monte_carlo": True,
        "stages": [
            {"stage": "input_read_and_normalization", "status": "COMPLETED"},
            {"stage": "integrity_preflight", "status": "COMPLETED" if preflight.is_file() else "NOT_CONFIGURED"},
            {"stage": "canonical_engine_and_patterns_hash_check", "status": "MATCH" if sha(eng) == ENGINE_SHA and sha(pat) == PAT_SHA else "MISMATCH", "canonical_engine_expected_sha256": ENGINE_SHA, "patterns_expected_sha256": PAT_SHA},
            {"stage": "motor_run", "status": "COMPLETED", "monte_carlo": True},
            {"stage": "monte_carlo_diagnostics", **((result.get("motor") or {}).get("monte_carlo_audit") or {"status":"NO_METRICS_RETURNED"})},
            {"stage": "terminal_resolution", "status": terminal.get("status", result.get("estado_final", "OUTPUT_WRITTEN")), "method": terminal.get("method", terminal.get("metodo")), "H1": (result.get("salida_interpretable") or {}).get("H1"), "H2": (result.get("salida_interpretable") or {}).get("H2")},
            {"stage": "external_archetype_search", "status": "EXECUTED_WITH_RESULTS" if search_performed else ("FAILED_REQUIRED_STAGE" if search_required_failed else "NOT_VERIFIED"), "required": True, "provider": search_receipt.get("provider"), "query_count": search_receipt.get("query_count", 0), "result_count": search_receipt.get("result_count", 0), **({"error": search_receipt.get("error")} if search_receipt.get("error") is not None else {}), **({"query_sha256": search_receipt.get("query_sha256")} if search_receipt.get("query_sha256") is not None else {})},
            {"stage": "filtro_entrada_dirigida_017", "status": (_f017_traza or {}).get("status", "NO_CONFIGURADO"), "modo": (_f017_traza or {}).get("modo", "off"), "n_aplicadas": (_f017_traza or {}).get("n_aplicadas", 0)},
            {"stage": "consulta_dirigida", "status": "COMPLETED" if _cd_traza is not None else "NO_CONFIGURADO", "modo": _cd_modo, "adaptador": (_cd_traza or {}).get("adaptador"), "n_preguntas": (_cd_traza or {}).get("n_preguntas", 0), "verificacion_no_escribe_H": (_cd_traza or {}).get("verificacion_no_escribe_H")},
            {"stage": "result_json_written", "status": "COMPLETED", "sha256": sha(out)},
            man_check,
            candado_check,
            {"stage": "ceb_ledger_preserved", "status": "COMPLETED" if _ceb_pres.get("ledgers") else "NO_LEDGER", "manifiesto": _ceb_pres.get("manifiesto"),
             "ledgers": [{k: x[k] for k in ("copia", "sha256", "lineas")} for x in _ceb_pres.get("ledgers") or []]},
        ],
        "archetype_search_receipt": search_receipt,
        "terminal_resolution": terminal,
        "continuidad_corrida": result.get("continuidad_corrida") or {"status": "NO_PAUSADA", "final_decision_authorized": True},
        "huellas_declaradas_ausentes": _declared_absent_hashes(result),
        "salida_interpretable": result.get("salida_interpretable"),
        "hypothesis_fronts_active_at_terminal": (result.get("cierre_memoria_operativa", {}).get("frentes_activos_al_cierre", result.get("frentes_hipotesis_activos_al_cierre")) if result.get("cierre_memoria_operativa", {}).get("frentes_activos_al_cierre", result.get("frentes_hipotesis_activos_al_cierre")) is not None else 0),
        "null_values_in_result_json": _json_health(result)["nulls"],
        "nonfinite_values_in_result_json": _json_health(result)["nonfinite"],
        "result_missing_paths": _result_missing_paths,
        "result_nonfinite_paths": _result_nonfinite_paths,
        "receipt_written_after_result": True,
    }
    receipt, _receipt_missing_paths, _receipt_nonfinite_paths = _sanitize_json_contract(receipt)
    receipt["null_values_in_receipt"] = _json_health(receipt)["nulls"]
    receipt["nonfinite_values_in_receipt"] = _json_health(receipt)["nonfinite"]
    receipt["null_values_replaced_as_tortugas_in_receipt"] = len(_receipt_missing_paths)
    receipt["nonfinite_values_replaced_as_tortugas_in_receipt"] = len(_receipt_nonfinite_paths)
    receipt["receipt_missing_paths"] = _receipt_missing_paths
    receipt["receipt_nonfinite_paths"] = _receipt_nonfinite_paths
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, allow_nan=False, default=str), encoding="utf-8")
    # Automatic post-run persistence: registry and case vault are outside the motor ZIP.
    _stinkbox_ingest = _ingest_stinkbox_registry(stink_home, stink_storage, rd)
    result["stinkbox_persistent_registry"] = _stinkbox_ingest
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False, default=str), encoding="utf-8")
    receipt["output_sha256"] = sha(out)
    for _stage in receipt.get("stages") or []:
        if _stage.get("stage") == "result_json_written": _stage["sha256"] = receipt["output_sha256"]
    receipt["null_values_in_result_json"] = _json_health(result)["nulls"]
    receipt["nonfinite_values_in_result_json"] = _json_health(result)["nonfinite"]
    receipt["stinkbox_persistent_registry_primary_checkpoint"] = _stinkbox_primary_checkpoint
    receipt["stinkbox_persistent_registry"] = _stinkbox_ingest
    receipt["stages"].append({"stage": "stinkbox_persistent_registry_primary_checkpoint", "status": _stinkbox_primary_checkpoint.get("status", "ERROR"), "home": str(stink_home), "storage": str(stink_storage)})
    receipt["stages"].append({"stage": "stinkbox_persistent_registry_ingest", "status": _stinkbox_ingest.get("status", "ERROR"), "home": str(stink_home), "storage": str(stink_storage)})
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, allow_nan=False, default=str), encoding="utf-8")
    print(json.dumps({
        "ok": not search_required_failed and not _result_missing_paths and not _result_nonfinite_paths and _continuity_pause is None and _json_health(result)["nulls"] == 0 and _json_health(result)["nonfinite"] == 0,
        "case_id": result.get("case_id"),
        "salida_interpretable": result.get("salida_interpretable"),
        "H1": result.get("salida_interpretable", {}).get("H1"),
        "H2": result.get("salida_interpretable", {}).get("H2"),
        "monte_carlo": True,
        "monte_carlo_audit": (result.get("motor") or {}).get("monte_carlo_audit"),
        "seconds": round(dt, 3),
        "output": str(out),
        "execution_receipt": str(receipt_path),
        "archetype_search": "EXECUTED_WITH_RESULTS" if search_performed else ("FAILED_REQUIRED_STAGE" if search_required_failed else "NOT_VERIFIED"),
        "result_missing_paths": _result_missing_paths,
        "result_nonfinite_paths": _result_nonfinite_paths,
        "predictive_validation": result.get("predictive_validation"),
        "stinkbox_persistent_registry": _stinkbox_ingest,
    }, ensure_ascii=False))
    # Exit code 0 is reserved for a clean, complete artifact. A JSON file can be
    # syntactically valid while still requiring data repair or a resumed run.
    final_status = _receipt_status(search_required_failed, _result_missing_paths, _result_nonfinite_paths)
    if _continuity_pause is not None:
        checkpoint = out.with_name(out.stem + "_CHECKPOINT_REANUDABLE.json")
        checkpoint.write_text(json.dumps({"checkpoint_schema": "U6_CONTINUITY_CHECKPOINT_V1",
            "status": "PAUSADA_REANUDABLE", "case_id": result.get("case_id"),
            "input_path": str(src.resolve()), "input_sha256": sha(src),
            "result_path": str(out.resolve()), "result_sha256": sha(out),
            "runner_path": str(Path(__file__).resolve()), "runner_sha256": sha(Path(__file__).resolve()),
            "continuidad_corrida": result.get("continuidad_corrida"),
            "hypothesis_fronts_active_at_pause": result.get("cierre_memoria_operativa", {}).get("frentes_activos_al_cierre", result.get("frentes_hipotesis_activos_al_cierre")),
            "resume_contract": "Reabrir input_path, conservar result_path y continuar desde continuidad_corrida.last_valid_cut; ejecutar TORTUGAS/vectorizacion y seguimiento antes de autorizar apuesta final.",
            "result_snapshot": result}, ensure_ascii=False, indent=2, allow_nan=False, default=str), encoding="utf-8")
        return 6
    return 3 if search_required_failed else (4 if final_status in ("INCOMPLETE_OUTPUT_DATA", "INCOMPLETE_NONFINITE_OUTPUT") else 5 if final_status == "COMPLETED_WITH_METADATA_GAP" else 0)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
