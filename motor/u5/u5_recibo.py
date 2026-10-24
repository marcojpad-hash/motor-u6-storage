#!/usr/bin/env python3
"""Recibo post-corrida U5 (JSON + md). Uso: python3 u5/u5_recibo.py <..._TRAZA_U5.json>
Lo que ejecutó se toma de la TRAZA instrumentada (llamadas reales), no de lo declarado.
Lo declarado (component_status, CEB) se pone al lado para poder contrastar."""
import sys, json, hashlib, time, os, datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from u5_comun import sha_file, self_hash, canon, ENGINE_SHA, PAT_SHA

MUTABLE = ("stinkbox_vault", "vecinos_caldero", "STINKBOX_STORAGE", "stinkbox_tokens_descubiertos", "resolved_cases_index", "neighbor_")

def _fam(h): return (h.get("family") or h.get("nucleo")) if isinstance(h, dict) else h

def construir(traza_path):
    tp = Path(traza_path); T = json.loads(tp.read_text(encoding="utf-8"))
    pack = Path(T["pack"]); out = Path(T["output"]); inp = Path(T["input"])
    R = json.loads(out.read_text(encoding="utf-8")) if out.is_file() else {}
    escritos = {a["path"] for a in T["aperturas"] if a["modo"] == "w"}
    cand = {}
    for f in T["modulos_importados"].values(): cand[f] = "modulo"
    for f in T["calls_por_archivo"]: cand.setdefault(f, "modulo")
    for a in T["aperturas"]:
        p = a["path"]
        if a["modo"] == "r" and p.startswith(str(pack)) and "__pycache__" not in p and not p.endswith(".pyc"):
            cand.setdefault(p, "catalogo" if not p.endswith(".py") else "modulo")
    archivos = []
    for p, clase in sorted(cand.items()):
        P = Path(p)
        if not P.is_file(): archivos.append({"path": p, "clase": clase, "presente_al_cierre": False}); continue
        rel = os.path.relpath(p, pack)
        parts = Path(rel).parts
        fuente = None
        if len(parts) >= 3 and parts[0] == "runs":
            sub = Path(*parts[2:])
            cand_src = pack / "motor" / sub
            fuente = str(Path("motor") / sub) if cand_src.is_file() else None
        else:
            fuente = rel
        mut = any(m in p for m in MUTABLE) or p in escritos or P.name == "_INPUT.json"
        archivos.append({"path": p, "rel_pack": rel, "fuente_en_pack": fuente, "clase": "estado_mutable" if mut else clase,
                         "sha256": sha_file(P), "bytes": P.stat().st_size,
                         "n_llamadas": T["calls_por_archivo"].get(p, 0)})
    fijos = [("input", inp), ("resultado", out), ("runner", pack / "correr_estandar.py"),
             ("engine_canonico", pack / "motor" / "Engine_V5_CANONICO_SOLO.py"), ("patterns_244", pack / "motor" / "patterns_final_v14.json"),
             ("traza_u5", tp)]
    rec_prev = out.with_name(out.stem + "_RECIBO_EJECUCION.json")
    if rec_prev.is_file(): fijos.append(("recibo_ejecucion_v1_existente", rec_prev))
    sidecar = out.with_name(out.stem + "_CONSULTA_SELLADO.json")
    if sidecar.is_file(): fijos.append(("consulta_sellado", sidecar))
    for u in sorted(Path(__file__).resolve().parent.glob("u5_*.py")): fijos.append(("u5_tool", u))
    # U6 #5: ledger CEB preservado junto al resultado (correr_estandar lo copia antes del rmtree): se puede recomputar.
    for lg in sorted(out.parent.glob(out.stem + "_CEB_LEDGER_*.jsonl")): fijos.append(("ceb_ledger_preservado", lg))
    _man = out.with_name(out.stem + "_CEB_LEDGER_MANIFIESTO.json")
    if _man.is_file(): fijos.append(("ceb_ledger_manifiesto", _man))
    clave = [{"rol": r, "path": str(p), "rel_pack": (os.path.relpath(p, pack) if str(p).startswith(str(pack)) else None), "sha256": sha_file(p) if p.is_file() else None, "bytes": p.stat().st_size if p.is_file() else None} for r, p in fijos]
    # ejecutado (instrumentado)
    ejecutados = sorted(({"archivo": os.path.relpath(f, pack), "basename": Path(f).name, "n_llamadas": n} for f, n in T["calls_por_archivo"].items()), key=lambda x: -x["n_llamadas"])
    calls_by_base = {}
    for e in ejecutados: calls_by_base[e["basename"]] = calls_by_base.get(e["basename"], 0) + e["n_llamadas"]
    P_ = R.get("predictor") or {}
    cs = (R.get("execution") or {}).get("component_status") or []
    stages = (R.get("ceb") or {}).get("stages") or {}
    declarados = []
    for c in cs:
        name = str(c.get("component")); arch = c.get("archivo")
        base, metodo = mapear(name, arch, calls_by_base)
        st = stages.get(name + "#1") or stages.get(name) or {}
        declarados.append({"componente": name, "status_declarado": c.get("status"), "feeds_predictor_declarado": c.get("feeds_predictor_declarado", c.get("feeds_predictor")),
                           "feeds_predictor": c.get("feeds_predictor"), "llega_verificado": c.get("llega_verificado"),
                           "declaracion_U6": c.get("declaracion_U6"), "motivo_declaracion_U6": c.get("motivo_declaracion_U6"),
                           "feeds_predictor_declarado_original": c.get("feeds_predictor_declarado_original"),
                           "archivo_mapeado": base, "mapeo": metodo, "n_llamadas_instrumentadas": calls_by_base.get(base) if base else None,
                           "ceb_started": st.get("started"), "ceb_output": st.get("output"), "ceb_status": st.get("status")})
    lat = [{"signal": s.get("signal"), "discriminates": s.get("discriminates"), "rank_eligible": s.get("rank_eligible"), "range": s.get("range"),
            "valor_H1": (s.get("candidate_values") or {}).get(_fam(R.get("H1"))), "valor_H2": (s.get("candidate_values") or {}).get(_fam(R.get("H2")))}
           for s in P_.get("lateral_signal_registry") or []]
    dg = P_.get("dimension_guard") or {}
    apd = P_.get("aporte_por_dimension_021") or {}
    h1, h2 = _fam(R.get("H1")), _fam(R.get("H2"))
    cands = [{"family": c.get("family"), "rank_fusion": c.get("rank_fusion"), "operational_rank": c.get("operational_rank"),
              "tortugas_votos": c.get("apoyo_tortugas_votos"), "pista_llm": c.get("pista_llm_arquetipos_traza")} for c in (P_.get("candidates") or [])[:12]]
    hs = R.get("hipotesis_necesarias_suficientes") or {}
    cf = R.get("cierre_final") or {}
    tr = P_.get("terminal_resolution") or {}
    now = time.time()
    rec = {
        "recibo_version": "U5_RECIBO_V1",
        "run_id": hashlib.sha256(f"{R.get('case_id')}|{T['t0_epoch']}|{out}".encode()).hexdigest()[:16],
        "case_id": R.get("case_id"),
        "timestamp_utc": datetime.datetime.fromtimestamp(T["t0_epoch"], datetime.timezone.utc).isoformat(),
        "timestamp_local": datetime.datetime.fromtimestamp(T["t0_epoch"]).astimezone().isoformat(),
        "duracion_s": round(T["t1_epoch"] - T["t0_epoch"], 3),
        "runner_exit": T["runner_exit"], "runner_exception": T["runner_exception"],
        "entorno": {k: os.environ.get(k) for k in ("CONSULTA_DIRIGIDA", "SEARCH_PROVIDER", "PYTHONHASHSEED")},
        "hash_input": sha_file(inp) if inp.is_file() else None,
        "hash_input_normalizado": (json.loads(rec_prev.read_text()).get("normalized_input_sha256") if rec_prev.is_file() else None),
        "engine_ok": sha_file(pack / "motor/Engine_V5_CANONICO_SOLO.py") == ENGINE_SHA,
        "patterns_ok": sha_file(pack / "motor/patterns_final_v14.json") == PAT_SHA,
        "archivos_clave": clave,
        "archivos_cargados": archivos,
        "ejecutado_instrumentado": ejecutados,
        "componentes_declarados_vs_ejecutados": declarados,
        "rank_fusion": {"metodo": P_.get("method"), "dimensiones_usadas": dg.get("used"), "n_numericas": dg.get("n_numeric"),
                        "excluidas_constantes": dg.get("excluded_constant"), "excluidas_duplicadas": dg.get("excluded_duplicate"),
                        "senales_laterales": lat, "aporte_por_dimension_H1": apd.get(h1), "aporte_por_dimension_H2": apd.get(h2),
                        "candidatas_top": cands, "empates": P_.get("empates")},
        "H": {"H1": h1, "H2": h2, "grado_H1": (R.get("H1") or {}).get("grado") if isinstance(R.get("H1"), dict) else None,
              "eje_set_021": hs.get("eje"), "set_021": [(m.get("familia"), m.get("rol")) for m in hs.get("miembros") or []]},
        "cierre": {"estado_final": R.get("estado_final"), "cierre_final_status": cf.get("status"), "grado": cf.get("grado"),
                   "H1": cf.get("H1"), "H2": cf.get("H2"), "metodo_terminal": tr.get("method"), "banda_020": tr.get("banda_020"),
                   "llm_hints_en_orden": tr.get("llm_hints_en_orden")},
        "consulta_dirigida": R.get("consulta_dirigida"),
        "ceb_status": (R.get("ceb") or {}).get("status"), "ceb_anomalias": (R.get("ceb") or {}).get("anomalies"),
        "nota": "n_llamadas = eventos 'call' de sys.setprofile en ese archivo durante la corrida completa (incluye las 3 llamadas a run(): principal, SIN_ULTIMO y RETENIDO). Archivos bajo runs/ se borran tras la corrida en el harness; verificar contra fuente_en_pack.",
    }
    rec["self_sha256"] = self_hash(rec)
    rp = out.with_name(out.stem + "_RECIBO_U5.json")
    rp.write_text(json.dumps(rec, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    md = [f"# Recibo U5 · {rec['case_id']} · run {rec['run_id']}", "",
          f"- Hora: {rec['timestamp_local']} (CT) · duración {rec['duracion_s']} s · exit {rec['runner_exit']}",
          f"- Input sha256: `{rec['hash_input']}`", f"- Engine OK: {rec['engine_ok']} · patterns OK: {rec['patterns_ok']}",
          f"- H1 **{h1}** ({rec['H']['grado_H1']}) · H2 {h2} · eje set 021: {hs.get('eje')} · cierre {rec['cierre']['estado_final']} / {cf.get('grado')}",
          f"- Archivos cargados con hash: {len(archivos)} · archivos con llamadas reales: {len(ejecutados)}",
          f"- Señales laterales que discriminan en rank_fusion: {[s['signal'] for s in lat if s['discriminates']]}",
          f"- self_sha256: `{rec['self_sha256']}` (sha256 del JSON canónico sin ese campo; sort_keys, separators=(',',':'), ensure_ascii=False)",
          "", "Verificar: `python3 u5/u5_verificar.py " + rp.name + "`"]
    rp.with_suffix(".md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return rp

def mapear(name, arch, calls_by_base):
    cands = []
    if arch: cands.append(Path(arch).name)
    n = name.split("/")[-1].replace(".output", "").replace(".absorbed", "")
    n = n.split(".pre_")[0].split(".post_")[0].split("(")[0]
    cands += [n if n.endswith(".py") else n + ".py"]
    for c in cands:
        if c in calls_by_base: return c, "exacto"
    stem = cands[-1][:-3]
    hits = [b for b in calls_by_base if stem and stem in b]
    if not hits:
        import re
        st2 = re.sub(r"_v\d.*$", "", stem)
        hits = [b for b in calls_by_base if st2 and len(st2) > 4 and st2 in b]
    if len(hits) == 1: return hits[0], "contiene"
    return (cands[-1], "sin_archivo_con_llamadas") if not hits else (sorted(hits)[0], "ambiguo:" + ",".join(sorted(hits)))

if __name__ == "__main__":
    print(construir(sys.argv[1]))
