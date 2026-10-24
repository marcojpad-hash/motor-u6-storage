#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""modo_estricto_v1.py — MODO DE CORRIDA ESTRICTO (27-sep-2026). Lateral. can_decide_H=false.

No escribe H1/H2, no reordena candidatos, no toca Engine_V5 ni patterns (solo lectura).
Se llama al final de run() en MOTOR_..._ESTRICTO_20260927.py sobre COPIAS de case/motor/pred.
A CIEGAS: no lee resultados registrados ni objetivos; solo la corrida en curso y piezas del run dir.

1) CIERRE ESTRICTO. Hay cierre solo si se cumplen TODAS:
   C0 la ruta de cierre vigente (guardianes) no quedó LATENTE (el modo estricto nunca es más laxo);
   C1 el top1 encabeza al menos un corte (argmax P_top5_ANEXO de algún corte, misma cadena que Copi);
   C2 el rival más fuerte queda descartado por el hombre de acero: en el steelman (guardian_acero_rival_v1)
      el rival con menor diferencia tras darle los casi-empates deja al top1 en SOBREVIVE (dif_acero > EPS);
   C3 H1≠H2 distinguibles: H1 y H2 existen y difieren, sin subdeterminación (margen rank_fusion <1 con el
      rival visto en ≥ cortes que el top1) y el cierre del décimo hombre fuera de la banda de empate;
   C4 Aquiles estable: plugin_aquiles_h.bootstrap_hasta_parar encuentra N_min (p_H deja de voltearse,
      eps=0.02, m=3 ventanas) y el ganador del remuestreo no cambia en esas m ventanas.
   Si falla alguna -> LATENTE con los motivos (todos, no solo el primero).
2) MAPEO EN NEGATIVO = Ricci–Forman vs Billar sobre el MISMO tablero de cortes (motor.cuts):
   ricci_forman_coocurrencia_v0_1.correr_cuts + billar_circular_convergencia_v0_2.correr_cuts (tal cual)
   y el comparador lectura_negativo_ricci_vs_billar_v0_1.analizar (tal cual). Donde discrepan = negativo.
   Alimenta convergencia como lateral; no gatea el cierre; no escribe H.
3) BLOQUE APARTE rival / 'qué ignoré': qué tendría que ser cierto para que gane top2/top3 (dimensiones
   donde el rival ya va arriba y cuánto falta), y tokens del input que el top1 no usa y el rival sí.
"""
from __future__ import annotations
import copy, hashlib, importlib.util, json, shutil, statistics
from pathlib import Path
import numpy as np

VERSION = "MODO_ESTRICTO_V1_20260927"
EPS_ACERO = 0.25
SEP_B9 = 1.0
SEED_AQ = 20260927


def _load(base: Path, fn: str, alias: str):
    p = base / fn
    if not p.is_file():
        return None, {"archivo": fn, "presente": False}
    spec = importlib.util.spec_from_file_location(alias, p)
    m = importlib.util.module_from_spec(spec)
    import sys
    sys.path.insert(0, str(base))
    spec.loader.exec_module(m)
    return m, {"archivo": fn, "presente": True, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}


def _bloque(guard, name):
    for b in guard.get("bloques") or []:
        if b.get("guardian") == name:
            return b
    return {}


# ------------------------------------------------------------------ Aquiles
def aquiles(base, motor, pred, H):
    aq, meta = _load(base, "plugin_aquiles_h.py", "me_aquiles")
    if aq is None or not H:
        return {"status": "NO_DISPONIBLE", "pieza": meta}
    cuts = motor.get("cuts") or []
    fams = [c["family"] for c in (pred.get("candidates") or [])[:10]]
    if H not in fams:
        fams = [H] + fams
    M = []
    for c in cuts:
        row = []
        for f in fams:
            v = [float((c.get(k) or {}).get(f, 0.5)) for k in ("P_FULL_244", "A_FULL_244", "C_FULL_244")]
            row.append(float(np.mean(v)))
        M.append(row)
    M = np.array(M)
    n = len(cuts)
    rng = np.random.default_rng(SEED_AQ)
    hi = fams.index(H)

    def replicar():
        idx = np.sort(rng.choice(n, n, replace=True))
        s = M[idx].mean(axis=0)
        order = list(np.argsort(-s, kind="stable"))
        return {"p_H": float(s[hi]), "winner": fams[order[0]], "topk": [fams[i] for i in order[:3]], "I": None}

    out = aq.bootstrap_hasta_parar(replicar, eps_p=0.02, m=3, k=3, n0=32, fusible=8192)
    pts = out.get("puntos") or []
    ult = pts[-3:]
    winners = [p.get("winner") for p in ult]
    sin_volteo_ganador = len(set(winners)) == 1 and len(ult) == 3
    estable = out.get("estado_H") == "PARA_DE_EMPUJAR_H" and sin_volteo_ganador
    return {"status": "EJECUTADO", "pieza": meta, "H_evaluada": H, "estado_H": out.get("estado_H"), "N_min": out.get("N_min"),
            "n_replicas_usadas": out.get("n_replicas_usadas"), "toque_fusible": out.get("toque_fusible"),
            "ganador_remuestreo_ultimas_ventanas": winners, "ganador_remuestreo_es_H": bool(winners) and all(w == H for w in winners),
            "p_H_por_N": [(p["n"], round(p["p_H"], 5)) for p in pts], "estable": estable,
            "replica": "bootstrap de cortes (con reemplazo, orden temporal conservado) sobre los tableros 244 del motor; "
                       "p_H = media P/A/C de H; ganador = argmax entre top10 del predictor. Proxy de la misma foto; no re-corre el predictor.",
            "nota_motor": "features.aquiles_h del motor vigente recibe claves 'p'/'corte' en vez de 'p_H'/'n' y sale siempre nulo; aquí se usa el plugin con sus claves."}


# ------------------------------------------------------------------ Ricci vs Billar
def negativo_ricci_billar(base, motor, pred, result_view, case_id):
    ric, m1 = _load(base, "ricci_forman_coocurrencia_v0_1.py", "me_ricci")
    bil, m2 = _load(base, "billar_circular_convergencia_v0_2.py", "me_billar")
    neg, m3 = _load(base, "lectura_negativo_ricci_vs_billar_v0_1.py", "me_negativo")
    piezas = [m1, m2, m3]
    if ric is None or bil is None or neg is None:
        return {"status": "LATENTE_FALTA_PIEZA", "piezas": piezas, "can_decide_H": False}
    cuts = copy.deepcopy(motor.get("cuts") or [])
    K = ric.correr_cuts(cuts, str(case_id))
    B = bil.correr_cuts(cuts, str(case_id))
    tmp = base / "_negativo_tmp"
    if tmp.exists(): shutil.rmtree(tmp)
    (tmp / "lentes_billar_ricci_outputs").mkdir(parents=True)
    caso = "RUN"
    R = {"case_id": case_id, "features": result_view.get("features") or {}, "H1": result_view.get("H1"), "H2": result_view.get("H2")}
    (tmp / f"RESULT_G_E_V0163_D_lentes_{caso}.json").write_text(json.dumps(R, ensure_ascii=False, default=str))
    (tmp / "lentes_billar_ricci_outputs" / f"BILLAR_V0_2_{caso}.json").write_text(json.dumps(B, ensure_ascii=False, default=str))
    (tmp / "lentes_billar_ricci_outputs" / f"RICCI_V0_1_{caso}.json").write_text(json.dumps(K, ensure_ascii=False, default=str))
    A = neg.analizar(tmp, caso)
    shutil.rmtree(tmp)
    cands = [c["family"] for c in (pred.get("candidates") or [])]
    filas = {f["familia"]: f for f in A["filas"]}
    def fila(f):
        x = filas.get(f)
        if not x:
            return {"familia": f, "cuadrante": "FUERA_DE_TOP5_EN_TODOS_LOS_CORTES", "senal": "LATENTE", "cuadrante_estricto": "—", "senal_estricta": "LATENTE"}
        return {"familia": f, "billar_n_conv": x["billar_n_conv"], "billar_n_conv_vivo": x["billar_n_conv_vivo"], "ricci_mean_inc": x["ricci_mean_inc"],
                "ricci_aristas_neg": x["ricci_aristas_neg"], "ricci_aristas": x["ricci_aristas"], "cuadrante": x["cuadrante"], "senal": x["senal_descarte"],
                "cuadrante_estricto": x["cuadrante_estricto"], "senal_estricta": x["senal_descarte_estricto"]}
    tops = [fila(f) for f in cands[:3]]
    par12 = None
    if len(cands) > 1:
        k2 = sorted(cands[:2])
        par12 = next((p for p in A["pares"] if sorted(p["par"]) == k2), {"par": k2, "cuadrante": "SIN_ARISTA_NI_CONVERGENCIA"})
    discord = [f["familia"] for f in A["filas"] if f["cuadrante"] in ("AMBOS", "NINGUNO", "SOLO_RICCI")]
    discord_e = [f["familia"] for f in A["filas"] if f["cuadrante_estricto"] in ("AMBOS", "NINGUNO", "SOLO_RICCI")]
    descarte = [f["familia"] for f in A["filas"] if f["cuadrante"] == "SOLO_RICCI"]
    descarte_e = [f["familia"] for f in A["filas"] if f["cuadrante_estricto"] == "SOLO_RICCI"]
    t1 = cands[0] if cands else None
    lectura = []
    for x in tops:
        rol = "top1" if x["familia"] == t1 else "rival"
        lectura.append(f"{rol} {x['familia']}: {x['cuadrante']}/{x['senal']} (estricto {x['cuadrante_estricto']}/{x['senal_estricta']})")
    bajo = sorted({b for f in A["filas"] for b in f["lentes_sin_senal_vs_nulo"]})
    return {"status": "EJECUTADO", "version": "NEGATIVO_RICCI_VS_BILLAR_EN_MODO_ESTRICTO_V1", "piezas": piezas,
            "can_decide_H": False, "alimenta": "convergencia (lateral); no gatea el cierre", "writes_H": False,
            "z_billar_v0_2": A["z_billar_v0_2"], "z_ricci_media": A["z_ricci_media"], "lentes_sin_senal_vs_nulo": bajo,
            "consistencia_embebida_vs_standalone": A["consistencia_ok"],
            "top1_top3": tops, "par_top1_top2": par12, "resumen_pares": A["resumen_pares"],
            "familias_discordantes": discord, "familias_discordantes_estricto": discord_e,
            "descarte_ricci_y_billar": descarte, "descarte_estricto": descarte_e,
            "top1_en_descarte": t1 in descarte, "top1_en_descarte_estricto": t1 in descarte_e,
            "lectura": lectura, "detalle_comparador": A}


# ------------------------------------------------------------------ rival / qué ignoré
def rival_que_ignore(base, case, pred):
    try:
        pat = json.loads((base / "patterns_final_v14.json").read_text(encoding="utf-8"))
    except Exception:
        pat = {}
    cands = pred.get("candidates") or []
    used = [d for d in (pred.get("dimensions") or [])]
    if len(cands) < 2:
        return {"status": "SIN_RIVAL"}
    toks = {}
    for c in case.get("cuts") or []:
        for e in ("P", "A", "C"):
            for t, w in c.get(e) or []:
                toks.setdefault(t, []).append(f"{c.get('id')}:{e}")
    top1 = cands[0]; tf = set((pat.get(top1["family"], {}).get("tokens_favor") or {}))
    tc = set((pat.get(top1["family"], {}).get("tokens_contra") or {}))
    out = []
    for r in cands[1:3]:
        rf = set((pat.get(r["family"], {}).get("tokens_favor") or {}))
        dims_rival = sorted([(d, round(float(r["features"].get(d, 0)) - float(top1["features"].get(d, 0)), 4)) for d in used
                             if float(r["features"].get(d, 0)) > float(top1["features"].get(d, 0)) + 1e-12], key=lambda x: -x[1])
        dims_top1 = sorted([(d, round(float(top1["features"].get(d, 0)) - float(r["features"].get(d, 0)), 4)) for d in used
                            if float(top1["features"].get(d, 0)) > float(r["features"].get(d, 0)) + 1e-12], key=lambda x: -x[1])
        gap = float(top1["rank_fusion"]) - float(r["rank_fusion"])
        ign = sorted(t for t in toks if t in rf and t not in tf)
        contra = sorted(t for t in toks if t in tc)
        out.append({"rival": r["family"], "gap_rank_fusion": round(gap, 6),
                    "para_que_gane_tendria_que_ser_cierto": {
                        "dimensiones_donde_el_rival_ya_va_arriba": dims_rival[:8],
                        "dimensiones_que_sostienen_al_top1": dims_top1[:8],
                        "texto": f"el rival necesita recuperar {gap:.3f} de rank_fusion: que las dimensiones donde hoy va abajo "
                                 f"({', '.join(d for d, _ in dims_top1[:3]) or '—'}) se inviertan, sin cambiar el input."},
                    "que_ignore_tokens_del_input_a_favor_del_rival_y_no_del_top1": [{"token": t, "donde": toks[t][:6]} for t in ign],
                    "tokens_del_input_en_contra_del_top1": [{"token": t, "donde": toks[t][:6]} for t in contra]})
    return {"status": "EJECUTADO", "top1": top1["family"], "rivales": out, "can_decide_H": False,
            "nota": "bloque aparte (no es el mapeo en negativo); lectura inversa, no veredicto"}


# ------------------------------------------------------------------ cierre estricto
def evaluar(case, motor, pred, result_view, base):
    base = Path(base)
    cands = pred.get("candidates") or []
    top1 = cands[0]["family"] if cands else None
    top2 = cands[1]["family"] if len(cands) > 1 else None
    guard = result_view.get("guardianes") or {}
    motivos, crit = [], {}
    # C0
    ec = (result_view.get("estado_cierre") or {}).get("valor")
    cg = result_view.get("cierre_guardianes") or {}
    crit["C0_ruta_vigente_no_latente"] = {"ok": ec != "LATENTE", "estado_cierre_vigente": ec,
                                          "motivos_vigentes": [f"{m.get('guardian')}:{m.get('tipo')}" for m in cg.get("motivos") or []]}
    if ec == "LATENTE":
        motivos.append("C0: la ruta vigente ya dejó el cierre LATENTE (" + "; ".join(crit["C0_ruta_vigente_no_latente"]["motivos_vigentes"]) + ")")
    # C1
    cadena = [((c.get("P_top5_ANEXO") or [[None]])[0][0]) for c in motor.get("cuts") or []]
    ids = [c.get("corte") for c in motor.get("cuts") or []]
    enc = [i for i, f in zip(ids, cadena) if f == top1]
    otros = {e: [c.get("corte") for c in motor.get("cuts") or [] if (c.get(f"{e}_top5_ANEXO") or [[None]])[0][0] == top1] for e in ("A", "C")}
    crit["C1_top1_encabeza_un_corte"] = {"ok": bool(enc), "cortes_que_encabeza_P": enc, "cadena_P": cadena, "info_encabeza_A_C": otros}
    if not enc:
        motivos.append(f"C1: {top1} no encabeza ningún corte (cadena P: {', '.join(str(x) for x in cadena)})")
    # C2
    ac = ((_bloque(guard, "HOMBRE_DE_ACERO").get("detalle") or {}).get("steelman_rival") or {})
    pr = ac.get("pruebas") or []
    if pr:
        fuerte = min(pr, key=lambda p: float(p.get("dif_acero", 1e9)))
        ok2 = fuerte.get("veredicto_top1") == "SOBREVIVE"
        crit["C2_rival_mas_fuerte_descartado_por_acero"] = {"ok": ok2, "rival_mas_fuerte": fuerte.get("rival"), "dif_base": fuerte.get("dif_base"),
            "dif_acero": fuerte.get("dif_acero"), "veredicto_top1": fuerte.get("veredicto_top1"), "EPS": EPS_ACERO,
            "todos": [(p.get("rival"), p.get("dif_acero"), p.get("veredicto_top1")) for p in pr]}
        if not ok2:
            motivos.append(f"C2: el acero no descarta al rival más fuerte {fuerte.get('rival')} (dif_acero {fuerte.get('dif_acero')}, top1 {fuerte.get('veredicto_top1')})")
    else:
        crit["C2_rival_mas_fuerte_descartado_por_acero"] = {"ok": False, "estado": ac.get("estado") or "SIN_STEELMAN"}
        motivos.append("C2: steelman del rival no disponible (" + str(ac.get("estado") or "sin pruebas") + ")")
    # C3
    H1 = (result_view.get("H1") or {}).get("family") if isinstance(result_view.get("H1"), dict) else result_view.get("H1")
    H2 = (result_view.get("H2") or {}).get("family") if isinstance(result_view.get("H2"), dict) else result_view.get("H2")
    margen = (float(cands[0]["rank_fusion"]) - float(cands[1]["rank_fusion"])) if len(cands) > 1 else None
    vistos = lambda fam: sum(1 for c in motor.get("cuts") or [] if fam in {x.get("familia") for x in (c.get("P_candidatos_0a3") or [])})
    v1, v2 = (vistos(top1) if top1 else 0), (vistos(top2) if top2 else 0)
    subdet = bool(top2 and margen is not None and margen < SEP_B9 and v2 >= v1)
    dh = (_bloque(guard, "DECIMO_HOMBRE_LATENCIA").get("detalle") or {}).get("cierre") or {}
    empate = bool(dh.get("LATENTE"))
    ok3 = bool(H1) and bool(H2) and H1 != H2 and not subdet and not empate
    crit["C3_H1_H2_distinguibles"] = {"ok": ok3, "H1": H1, "H2": H2, "margen_rank_fusion": None if margen is None else round(margen, 6),
        "cortes_con_top1": v1, "cortes_con_rival": v2, "subdeterminado": subdet, "decimo_hombre_cierre_p": dh.get("p_momento"), "cierre_en_banda_empate": empate}
    if not ok3:
        why = []
        if not H1: why.append("sin H1")
        if not H2: why.append("sin H2")
        if H1 and H2 and H1 == H2: why.append("H1=H2")
        if subdet: why.append(f"subdeterminado (margen {margen:.3f} < {SEP_B9}, rival en {v2} cortes vs top1 en {v1})")
        if empate: why.append(f"décimo hombre: cierre en banda de empate (p={dh.get('p_momento')})")
        motivos.append("C3: H1/H2 no distinguibles: " + "; ".join(why))
    # C4
    aq = aquiles(base, motor, pred, top1)
    crit["C4_aquiles_estable"] = {"ok": bool(aq.get("estable")), **{k: aq.get(k) for k in ("estado_H", "N_min", "n_replicas_usadas", "ganador_remuestreo_ultimas_ventanas", "ganador_remuestreo_es_H", "toque_fusible")}}
    if not aq.get("estable"):
        motivos.append(f"C4: Aquiles no estable (estado {aq.get('estado_H')}, N_min {aq.get('N_min')}, ganadores {aq.get('ganador_remuestreo_ultimas_ventanas')})")
    estado = "CIERRE_ESTRICTO" if not motivos else "LATENTE"
    neg = negativo_ricci_billar(base, motor, pred, result_view, case.get("case_id"))
    riv = rival_que_ignore(base, case, pred)
    conv_lat = {"negativo_top1_en_descarte": neg.get("top1_en_descarte"), "negativo_top1_en_descarte_estricto": neg.get("top1_en_descarte_estricto"),
                "nota": "entra a convergencia como voto lateral; no cambia el estado estricto ni H"}
    return {"version": VERSION, "can_decide_H": False, "escribe_H": False, "reordena_candidatos": False, "escribe_patterns": False,
            "a_ciegas": True, "top1": top1, "top2": top2, "top3": cands[2]["family"] if len(cands) > 2 else None,
            "estado_cierre_estricto": estado, "motivos": motivos, "criterios": crit, "aquiles": aq,
            "negativo_ricci_vs_billar": neg, "rival_que_ignore": riv, "convergencia_lateral": conv_lat}
