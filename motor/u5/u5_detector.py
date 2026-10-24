#!/usr/bin/env python3
"""Detector de anomalías U5. Corre DESPUÉS del runner. Nunca decide H, no reescribe resultados: solo reporta.
Uso: python3 u5/u5_detector.py RECIBO_U5.json [RECIBO_U5.json ...] [--out ANOMALIAS.json]
Por corrida: A1 declarado-sin-aporte, A1b declarado-ejecutado-sin-llamadas, A3 laterales fuera de banda δ,
A4 tokens sin fuente en input, A5 consulta_dirigida (límites / post-Z), A6 tokens no canónicos, A7 módulos faltantes,
A8 deriva de hash vs manifiesto, A9 empates saturados, A10 anomalías CEB propias del motor.
Entre corridas (mismo input sha): A2 cambio de H1 (y H2/grado/top5)."""
import sys, json, re, ast, os
from pathlib import Path
from collections import Counter, defaultdict
sys.path.insert(0, str(Path(__file__).resolve().parent))
from u5_comun import sha_file, PACK
STDLIB = set(getattr(sys, "stdlib_module_names", ())) | {"numpy", "scipy", "networkx", "pandas", "sklearn", "requests", "pytest"}

def A(tipo, sev, detalle, **kw): return {"tipo": tipo, "severidad": sev, "detalle": detalle, **kw}

def vocab_244(pack):
    P = json.loads((pack / "motor/patterns_final_v14.json").read_text(encoding="utf-8"))
    v = set(P)
    for f in P.values():
        if isinstance(f, dict):
            v |= set((f.get("tokens_favor") or {})); v |= set((f.get("tokens_contra") or {}))
    return v

def vocab_lateral(pack):
    v = set()
    def walk(o):
        if isinstance(o, dict):
            for k, x in o.items():
                if isinstance(k, str) and re.fullmatch(r"[a-z0-9_]{3,60}", k): v.add(k)
                walk(x)
        elif isinstance(o, list):
            for x in o: walk(x)
        elif isinstance(o, str) and re.fullmatch(r"[a-z0-9_]{3,60}", o): v.add(o)
    for d in ("familias_tokens", "tokens_laterales"):
        for f in (pack / "motor" / d).rglob("*.json"):
            try: walk(json.loads(f.read_text(encoding="utf-8")))
            except Exception: pass
    for f in ("MATRIZ_EQUIVALENCIAS_ESCALA.json", "PUENTE_244_FAMILIAS.json"):
        p = pack / "motor" / f
        if p.is_file(): walk(json.loads(p.read_text(encoding="utf-8")))
    return v

def input_tokens(case):
    if isinstance(case, list): case = {"cuts": case}
    out = []
    for c in case.get("cuts") or []:
        for eje in ("P", "A", "C"):
            for row in c.get(eje) or []:
                t, w = (row[0], row[1] if len(row) > 1 else None) if isinstance(row, (list, tuple)) else (row, None)
                out.append((c.get("id"), eje, t, w))
    return out

_STATIC = None
def estatico(pack):
    """A7 módulos faltantes (imports y nombres de archivo literales) + A8 deriva vs manifiesto. Una vez por pack."""
    global _STATIC
    if _STATIC is not None: return _STATIC
    motor = pack / "motor"; presentes = {p.name for p in motor.rglob("*") if p.is_file()} | {p.name for p in pack.rglob("*") if p.is_file() and "runs" not in p.parts}
    mods = {p.stem for p in motor.glob("*.py")} | {p.name for p in motor.iterdir() if p.is_dir()} | {"MOTOR_V15_3_NATIVO_V0_9"}
    falt_imp, falt_lit = defaultdict(set), defaultdict(set)
    for f in sorted(list(motor.glob("*.py")) + [pack / "correr_estandar.py"] + list((pack / "capa_llm").glob("*.py"))):
        src = f.read_text(encoding="utf-8", errors="replace")
        try: tree = ast.parse(src)
        except SyntaxError as e: falt_imp[f.name].add(f"SYNTAX_ERROR:{e}"); continue
        for n in ast.walk(tree):
            names = []
            if isinstance(n, ast.Import): names = [a.name.split(".")[0] for a in n.names]
            elif isinstance(n, ast.ImportFrom) and n.module and n.level == 0: names = [n.module.split(".")[0]]
            for m in names:
                if m not in STDLIB and m not in mods and m != "__future__":
                    try:
                        __import__(m)
                    except Exception:
                        falt_imp[f.name].add(m)
            if isinstance(n, ast.Constant) and isinstance(n.value, str) and re.fullmatch(r"[\w\-./]+\.(py|json)", n.value):
                b = Path(n.value).name
                if b not in presentes and "{" not in b and not b.startswith(("RESULT", "_", "test")):
                    falt_lit[f.name].add(n.value)
    man = json.loads((pack / "UNIFICACION_SHA256_MANIFEST.json").read_text(encoding="utf-8"))
    drift, ausentes = [], []
    for e in man["files"]:
        p = pack / e["path"]
        if not p.is_file(): ausentes.append(e["path"]); continue
        h = sha_file(p)
        if h != e["sha256"]: drift.append({"path": e["path"], "manifiesto": e["sha256"][:12], "actual": h[:12]})
    en_man = {e["path"] for e in man["files"]}
    nuevos = sorted(str(p.relative_to(pack)) for p in (pack / "motor").rglob("*") if p.is_file() and "__pycache__" not in p.parts and str(p.relative_to(pack)) not in en_man and not any(str(p.relative_to(pack)).startswith(x) for x in (man.get("excluidos_estado_mutable") or [])))
    _a7 = pack / "u6" / "A7_REFERENCIAS_CLASIFICADAS.json"
    _a7c = json.loads(_a7.read_text(encoding="utf-8")).get("clasificacion", {}) if _a7.is_file() else {}
    _STATIC = {"a7_clasificacion": _a7c, "imports_no_resueltos": {k: sorted(v) for k, v in falt_imp.items()},
               "archivos_referenciados_ausentes": {k: sorted(v) for k, v in falt_lit.items()},
               "manifiesto": "UNIFICACION_SHA256_MANIFEST.json", "manifiesto_n": len(man["files"]),
               "deriva_hash": drift, "en_manifiesto_ausentes": ausentes, "motor_fuera_de_manifiesto": nuevos}
    return _STATIC

def por_corrida(rp, pack=PACK, v244=None, vlat=None):
    rec = json.loads(Path(rp).read_text(encoding="utf-8"))
    out = Path(next(a["path"] for a in rec["archivos_clave"] if a["rol"] == "resultado"))
    inp = Path(next(a["path"] for a in rec["archivos_clave"] if a["rol"] == "input"))
    R = json.loads(out.read_text(encoding="utf-8")); case = json.loads(inp.read_text(encoding="utf-8"))
    if isinstance(case, list): case = {"cuts": case}
    an = []
    # A1
    for d in rec["componentes_declarados_vs_ejecutados"]:
        if d["feeds_predictor_declarado"] and not d["feeds_predictor"] and str(d["status_declarado"]).startswith(("EXECUTED", "HUB_ACTIVA")) and d.get("declaracion_U6") == "CABLEADA_SIN_SENAL_EN_CASO":
            # U6: hay vía real al ranking pero la entrada de este caso es vacía/igual para todas -> se informa aparte (no es declaración falsa)
            an.append(A("A1_CABLEADA_SIN_SENAL_EN_CASO", "INFO", f"{d['componente']}: vía cableada al ranking, sin señal en este caso: {d.get('motivo_declaracion_U6')}", componente=d["componente"]))
        elif d["feeds_predictor_declarado"] and not d["feeds_predictor"] and str(d["status_declarado"]).startswith(("EXECUTED", "HUB_ACTIVA")):
            an.append(A("A1_DECLARADO_ACTIVO_APORTE_CERO", "MEDIA", f"{d['componente']}: declara alimentar predictor, aporte verificado a rank_fusion = 0", componente=d["componente"], status=d["status_declarado"], n_llamadas=d["n_llamadas_instrumentadas"]))
        # A1b
        if str(d["status_declarado"]).startswith("EXECUTED") and not d["n_llamadas_instrumentadas"]:
            existe = (pack / "motor" / (d["archivo_mapeado"] or "_")).is_file()
            if existe:
                an.append(A("A1b_DECLARADO_EJECUTADO_SIN_LLAMADAS", "ALTA", f"{d['componente']}: status {d['status_declarado']} pero {d['archivo_mapeado']} existe y tuvo 0 llamadas", componente=d["componente"]))
            else:
                an.append(A("A1c_EJECUTADO_SIN_ARCHIVO_PROPIO", "INFO", f"{d['componente']}: status {d['status_declarado']}, sin archivo propio con llamadas (en línea en otro módulo o nombre no mapeable); no verificable por traza", componente=d["componente"]))
    rf = rec["rank_fusion"]
    for s in rf["senales_laterales"]:
        if s.get("rank_eligible") and not s.get("discriminates"):
            an.append(A("A1_SENAL_LATERAL_NO_DISCRIMINA", "BAJA", f"señal {s['signal']} elegible pero no discrimina", senal=s["signal"]))
    if rf.get("excluidas_constantes"):
        an.append(A("A1_DIMENSIONES_CONSTANTES", "INFO", f"{len(rf['excluidas_constantes'])} de {rf.get('n_numericas')} dimensiones numéricas son constantes entre candidatas (aporte 0): {rf['excluidas_constantes']}"))
    # A3
    P_ = R.get("predictor") or {}; cands = P_.get("candidates") or []
    tr = P_.get("terminal_resolution") or {}; b = tr.get("banda_020") or {}; delta = b.get("delta_rank_fusion")
    if delta is not None and cands:
        byop = sorted([c for c in cands if c.get("operational_rank") is not None], key=lambda c: c["operational_rank"])
        for i in range(len(byop)):
            for j in range(i + 1, len(byop)):
                if (byop[j]["rank_fusion"] or 0) - (byop[i]["rank_fusion"] or 0) > delta + 1e-9:
                    an.append(A("A3_LATERAL_REORDENA_FUERA_DE_BANDA", "ALTA", f"{byop[i]['family']} (rf {byop[i]['rank_fusion']}) quedó por delante de {byop[j]['family']} (rf {byop[j]['rank_fusion']}); diferencia > δ={delta}"))
        for g in b.get("grupos_casi_igualdad") or []:
            if g.get("orden_cambio"):
                an.append(A("A3_INFO_REORDEN_DENTRO_DE_BANDA", "INFO", f"reorden dentro de banda δ por {g.get('decidio')}: {g.get('miembros_orden_rank_fusion')} → {g.get('orden_final')}", toca_H1=g.get("toca_H1"), toca_H2=g.get("toca_H2")))
    if tr.get("llm_hints_en_orden") or b.get("pistas_llm_en_orden"):
        an.append(A("A3_PISTAS_LLM_EN_ORDEN", "ALTA", "pistas LLM participan en el orden final"))
    # A4
    itk = input_tokens(case); iset = {t for _, _, t, _ in itk}
    cd = R.get("consulta_dirigida")
    if cd: iset = iset | {t for f in cd.get("filas") or [] for t in (f.get("tokens_entregados_al_motor") or [])}
    sinf = defaultdict(list)
    for fam, ev in (P_.get("own_evidence") or {}).items():
        for t in (ev.get("favor_tokens") or []) + (ev.get("contra_tokens") or []):
            if t not in iset: sinf[t].append(fam)
    for t, fams in sorted(sinf.items()):
        an.append(A("A4_TOKEN_DISPARA_SIN_FUENTE_EN_INPUT", "ALTA", f"token '{t}' aparece como evidencia propia de {sorted(set(fams))} y no está en el input", token=t))
    # A5
    cd = R.get("consulta_dirigida")
    if cd is not None:
        an += chequear_consulta(cd, case, (v244 or vocab_244(pack)) | (vlat or vocab_lateral(pack)))
    # A6
    v244 = v244 or vocab_244(pack); vlat = vlat or vocab_lateral(pack)
    no244 = sorted({t for t in iset if t not in v244}); nolat = sorted({t for t in no244 if t not in vlat})
    if no244:
        an.append(A("A6_TOKENS_FUERA_DEL_244", "INFO", f"{len(no244)}/{len(iset)} tokens del input no están en el 244 (van a laterales; al Engine solo pasan si entran por el cuello)", tokens=no244))
    _lb = pack / "u6" / "TOKENS_LATENTES_BASE.json"
    _lat = {e["token"]: e for e in (json.loads(_lb.read_text(encoding="utf-8")).get("tokens") or [])} if _lb.is_file() else {}
    reg = [t for t in nolat if t in _lat]; nolat = [t for t in nolat if t not in _lat]
    if reg:
        an.append(A("A6_TOKEN_LATENTE_REGISTRADO", "INFO", f"{len(reg)} tokens no canónicos registrados como latentes en u6/TOKENS_LATENTES_BASE.json: " + ", ".join(f"{t}({_lat[t]['estado']}, eq={_lat[t].get('equivalente_regla_existente')})" for t in reg), tokens=reg))
    if nolat:
        an.append(A("A6_TOKENS_NO_CANONICOS", "MEDIA", f"{len(nolat)}/{len(iset)} tokens no están en el 244 ni en ningún catálogo lateral/puente del pack", tokens=nolat))
    # A7/A8 (estático, vale para todas las corridas de este pack)
    st = estatico(pack)
    for f, ms in st["imports_no_resueltos"].items():
        an.append(A("A7_IMPORT_NO_RESUELTO", "MEDIA", f"{f} importa {ms} y no existe en el pack ni en el entorno"))
    _cls = st.get("a7_clasificacion") or {}
    for f, ms in st["archivos_referenciados_ausentes"].items():
        reales = [m for m in ms if not (_cls.get(f) or {}).get(m)]
        expl = {m: (_cls.get(f) or {}).get(m) for m in ms if (_cls.get(f) or {}).get(m)}
        if reales:
            an.append(A("A7_ARCHIVO_REFERENCIADO_AUSENTE", "BAJA", f"{f} nombra {reales} y no hay archivo con ese nombre en el pack"))
        if expl:
            an.append(A("A7_REFERENCIA_CLASIFICADA", "INFO", f"{f}: {expl}"))
    if st["deriva_hash"]:
        an.append(A("A8_DERIVA_HASH_VS_MANIFIESTO", "MEDIA", f"{len(st['deriva_hash'])} archivos difieren de {st['manifiesto']}", archivos=st["deriva_hash"]))
    if st["en_manifiesto_ausentes"]:
        an.append(A("A8_AUSENTE_VS_MANIFIESTO", "MEDIA", f"{len(st['en_manifiesto_ausentes'])} archivos del manifiesto no están", archivos=st["en_manifiesto_ausentes"]))
    if st["motor_fuera_de_manifiesto"]:
        an.append(A("A8_MOTOR_FUERA_DE_MANIFIESTO", "BAJA", f"{len(st['motor_fuera_de_manifiesto'])} archivos de motor/ no figuran en el manifiesto", archivos=st["motor_fuera_de_manifiesto"]))
    if not rec["engine_ok"] or not rec["patterns_ok"]:
        an.append(A("A8_ENGINE_O_PATTERNS_CAMBIADO", "CRITICA", "Engine o patterns no coincide con 665c39a2/d827dcc3"))
    # A9
    ws = [w for *_, w in itk if isinstance(w, (int, float))]
    if ws:
        mx = max(ws); cnt = Counter(round(w, 4) for w in ws)
        top_por_eje = Counter()
        for c in case.get("cuts") or []:
            for eje in ("P", "A", "C"):
                rows = [r for r in c.get(eje) or [] if isinstance(r, (list, tuple)) and len(r) > 1]
                if rows: top_por_eje[round(max(r[1] for r in rows), 4)] += 1
                ww = Counter(round(r[1], 4) for r in rows)
                for w, n in ww.items():
                    if n > 1: an.append(A("A9_EMPATE_PESO_EN_EJE", "BAJA", f"corte {c.get('id')} eje {eje}: {n} tokens con peso {w}"))
        tw, tn = top_por_eje.most_common(1)[0]; n_ejes = sum(top_por_eje.values())
        if tn / n_ejes >= 0.5 and n_ejes >= 4:
            an.append(A("A9_TECHO_SATURADO", "MEDIA", f"el peso máximo {tw} se repite como tope en {tn}/{n_ejes} ejes (techo de la escala de entrada saturado)", peso=tw))
    # U6: ¿cómo se resolvieron los empates en el borde del cuello top-5 (lo que llega al Engine)?
    _cu = ((R.get("motor") or {}).get("cuello_top5_engine") or {}).get("cortes") or []
    _pos = _ev = 0
    for _c in _cu:
        d6 = _c.get("desempate_U6")
        if d6:
            _pos += (d6.get("decididos_por") or {}).get("posicion", 0); _ev += sum(v for k, v in (d6.get("decididos_por") or {}).items() if k != "posicion")
        else:
            wk = _c.get("peso_corte"); dentro = sum(1 for r in _c.get("al_engine") or [] if r[1] == wk)
            fuera = sum(1 for r in _c.get("quedan_fuera_del_engine") or [] if r.get("w") == wk and r.get("en_catalogo"))
            _pos += dentro * fuera
    if _cu:
        an.append(A("A9_CUELLO_DESEMPATE", "MEDIA" if _pos else "INFO", f"pares en el borde del cuello top-5: {_pos} decididos por posición, {_ev} por evidencia", por_posicion=_pos, por_evidencia=_ev))
    emp = P_.get("empates") or {}
    if emp.get("top1_top2_empate"): an.append(A("A9_EMPATE_TOP1_TOP2", "ALTA", "rank_fusion empata top1/top2"))
    for g in emp.get("grupos_empate_top10") or []: an.append(A("A9_EMPATE_RANK_FUSION_TOP10", "MEDIA", f"grupo empatado: {g}"))
    # A11 módulos .py de motor/ sin ninguna llamada en la corrida (traza real)
    ex = {e["basename"] for e in rec["ejecutado_instrumentado"]}
    sin = sorted(p.name for p in (pack / "motor").glob("*.py") if p.name not in ex)
    if sin: an.append(A("A11_MODULO_EN_MOTOR_SIN_LLAMADAS", "INFO", f"{len(sin)} .py de motor/ no ejecutaron ni una función en esta corrida", modulos=sin))
    # A10
    for x in (R.get("ceb") or {}).get("anomalies") or []:
        an.append(A("A10_CEB_" + str(x.get("type")), "BAJA", f"{x.get('component')}: {x.get('diagnosis')}"))
    return {"recibo": str(rp), "run_id": rec["run_id"], "case_id": rec["case_id"], "input_sha256": rec["hash_input"],
            "H1": rec["H"]["H1"], "H2": rec["H"]["H2"], "decide_H": False, "anomalias": an,
            "conteo": dict(Counter(a["tipo"] for a in an)), "conteo_severidad": dict(Counter(a["severidad"] for a in an))}

def chequear_consulta(cd, case, v244=None, vlat=None):
    an = []
    import importlib.util
    sp = importlib.util.spec_from_file_location("cdv1", str(PACK / "capa_llm/consulta_dirigida_v1.py")); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
    MQ, MT = m.MAX_PREGUNTAS_POR_CORTE, m.MAX_TOKENS_POR_RESPUESTA
    filas = cd.get("filas") or []
    idx = {c.get("id"): k for k, c in enumerate(case.get("cuts") or [])}
    zi = cd.get("z_idx")
    for c, n in Counter(f.get("corte") for f in filas).items():
        if n > MQ: an.append(A("A5_CONSULTA_EXCEDE_PREGUNTAS", "ALTA", f"corte {c}: {n} preguntas > {MQ}"))
    for f in filas:
        ent = f.get("tokens_entregados_al_motor") or []
        if len(ent) > MT or len(f.get("tokens_aceptados") or []) > MT:
            an.append(A("A5_CONSULTA_EXCEDE_TOKENS", "ALTA", f"{f.get('pregunta_id')}: {len(ent)} tokens entregados > {MT}"))
        if ent and zi is not None and idx.get(f.get("corte"), -1) > zi:
            an.append(A("A5_CONSULTA_FUGA_POST_Z", "CRITICA", f"{f.get('pregunta_id')}: corte {f.get('corte')} (idx {idx.get(f.get('corte'))}) > z_idx {zi} y entregó {ent}"))
        if ent and str(f.get("estado", "")).startswith("RECHAZ"):
            an.append(A("A5_CONSULTA_RECHAZADA_PERO_ENTREGA", "CRITICA", f"{f.get('pregunta_id')} rechazada pero entregó {ent}"))
        if v244 is not None:
            nc = [t for t in ent if t not in v244 and t not in (vlat or set())]
            if nc: an.append(A("A5_CONSULTA_TOKEN_NO_CANONICO", "ALTA", f"{f.get('pregunta_id')} entregó tokens no canónicos {nc}"))
    an.append(A("A5_CONSULTA_PRESENTE", "INFO", f"consulta_dirigida {cd.get('adaptador')}: {cd.get('n_preguntas')} preguntas, estados {cd.get('conteo_por_estado')}, entregados {[t for f in filas for t in (f.get('tokens_entregados_al_motor') or [])]}, red {cd.get('llamadas_red')}"))
    return an

def entre_corridas(dets, recs):
    an = []; g = defaultdict(list)
    for d, r in zip(dets, recs): g[(d["case_id"], d["input_sha256"], (r.get("entorno") or {}).get("CONSULTA_DIRIGIDA"))].append(r)
    for (c, h, cdm), rs in g.items():
        if len(rs) < 2: continue
        for k, f in (("H1", lambda r: r["H"]["H1"]), ("H2", lambda r: r["H"]["H2"]), ("grado", lambda r: r["H"]["grado_H1"]), ("cierre", lambda r: r["cierre"]["estado_final"])):
            vals = {f(r) for r in rs}
            if len(vals) > 1:
                an.append(A(f"A2_CAMBIO_{k}_MISMO_INPUT", "CRITICA" if k == "H1" else "ALTA", f"{c}: {k} cambia entre corridas con input idéntico {h[:12]}: {sorted(map(str, vals))}", case_id=c))
    return an

if __name__ == "__main__":
    a = sys.argv[1:]; outp = None
    if "--out" in a: i = a.index("--out"); outp = a[i + 1]; a = a[:i] + a[i + 2:]
    v244, vlat = vocab_244(PACK), vocab_lateral(PACK)
    dets = [por_corrida(p, PACK, v244, vlat) for p in a]
    recs = [json.loads(Path(p).read_text(encoding="utf-8")) for p in a]
    res = {"detector": "U5_DETECTOR_V1+U6", "decide_H": False, "estatico_pack": estatico(PACK), "por_corrida": dets, "entre_corridas": entre_corridas(dets, recs)}
    s = json.dumps(res, ensure_ascii=False, indent=1, default=str)
    if outp: Path(outp).write_text(s, encoding="utf-8")
    print(json.dumps({"n": len(dets), "entre_corridas": len(res["entre_corridas"]), "por_caso": {d["case_id"] + ":" + d["run_id"]: d["conteo_severidad"] for d in dets}}, ensure_ascii=False, indent=1))
