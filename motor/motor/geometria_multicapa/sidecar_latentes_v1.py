#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sidecar_latentes_v1.py — SIDECAR LATERAL de memoria de factores (primer destello, convergencia,
trayectoria, reconvergencia, lectura olvidada, suma restando, tabla contrafactual con regla de Laplace).

Reglas (contrato):
  * Solo lee. No modifica el motor canónico, ni las 244 familias, ni el RESULT. No decide H ni reordena.
    can_decide_H=False, reordena=False, writes_H=False.
  * Agnóstico: solo ids de corte (C1..Cn), ejes P/A/C, tokens del input y nombres de familias del catálogo.
    No emite fechas ni nombres de caso.
  * Ningún número de salida > 1 en valor absoluto. Conteos van como texto "s/n". Probabilidades como
    fracción en [0.05, 0.95] (= 5–95 %).
  * Sin fuga de futuro: toda lectura "en el corte k" usa solo C1..Ck (Ricci y billar se corren por prefijo).
    Lo que mira todos los cortes va en bloques marcados RETRO.
  * Vocabulario de estado: OBSERVADA / LATENTE_INFERIDA / REAPARICION_COMPROBADA. No se usa "LATENTE"
    a secas (en el motor significa "factor faltante").
  * Tablas de verdad = lo observado en cortes, no prueba causal.
"""
from __future__ import annotations
import copy, hashlib, importlib.util, itertools, json, math, sys, time
from pathlib import Path
from typing import Any, Dict, List

VERSION = "SIDECAR_LATENTES_V1_20261019"
UMBRAL_ACTIVA = 0.005          # mismo umbral que movimiento_de_fondo_u4
EPS_DELTA = 0.01               # cambio simultáneo: |delta| > EPS en ambos (EPS familias de U4)
EPS_MARGEN = 0.01              # margen de liderazgo bajo el cual "la explicación pudo cambiar"
MIN_FILAS_SUF = 2              # una condición/conjunto debe aparecer en >=2 transiciones para llamarla suficiente
MAX_CONJ = 3                   # p', p'', p'''
P_MIN, P_MAX = 0.05, 0.95
EJES = ("P", "A", "C")
CONTRATO = {"can_decide_H": False, "reordena": False, "writes_H": False, "writes_canonical": False,
            "writes_244": False, "lateral": True, "agnostico": True, "sin_fuga_de_futuro": True,
            "tabla_de_verdad": "OBSERVADA_EN_CORTES_NO_PRUEBA_CAUSAL"}


def _r(x, n=4):
    return round(float(x), n)


def laplace(s: int, n: int) -> float:
    """Regla de sucesión de Laplace (s+1)/(n+2), recortada a [0.05, 0.95]. No viene del motor (no existe ahí)."""
    return _r(min(P_MAX, max(P_MIN, (s + 1) / (n + 2))))


def _frac(s, n):
    return f"{s}/{n}"


# ----------------------------------------------------------------- carga de piezas existentes (solo lectura)
def _load(motor_dir: Path, fname: str, alias: str):
    sys.dont_write_bytecode = True          # no dejar __pycache__ dentro del pack
    p = motor_dir / fname
    if not p.exists():
        return None
    if str(motor_dir) not in sys.path:
        sys.path.insert(0, str(motor_dir))
    spec = importlib.util.spec_from_file_location(alias, p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# ----------------------------------------------------------------- vistas por corte
def _tokens_corte(cut) -> Dict[str, List[str]]:
    out: Dict[str, List[str]] = {}
    for e in EJES:
        for item in cut.get(e) or []:
            t = item[0] if isinstance(item, (list, tuple)) else (item.get("token") if isinstance(item, dict) else item)
            out.setdefault(str(t), []).append(e)
    return {t: sorted(set(v)) for t, v in out.items()}


def _familias_corte(mcut) -> Dict[str, Dict[str, Any]]:
    """Para cada familia: nivel en el corte (TOP5 / ACTIVA_BAJO_CUELLO / BAJO_UMBRAL / APAGADA) y valor por eje."""
    res = {}
    top5 = {e: [f for f, _ in (mcut.get(f"{e}_top5_ANEXO") or [])] for e in EJES}
    full = {e: mcut.get(f"{e}_FULL_244") or {} for e in EJES}
    fams = set().union(*[set(full[e]) for e in EJES])
    for f in fams:
        act = {e: abs(float(full[e].get(f, 0.5)) - 0.5) for e in EJES}
        a = max(act.values())
        ejes_top = [e for e in EJES if f in top5[e]]
        if ejes_top:
            nivel = "TOP5"
        elif a > UMBRAL_ACTIVA:
            nivel = "ACTIVA_BAJO_CUELLO"
        elif a > 0:
            nivel = "BAJO_UMBRAL"
        else:
            nivel = "APAGADA"
        res[f] = {"nivel": nivel, "activacion_max": _r(a), "ejes_top5": ejes_top,
                  "P": _r(full["P"].get(f, 0.5))}
    return res


def _lider_P(mcut):
    full = mcut.get("P_FULL_244") or {}
    if not full:
        return [], 0.0
    vals = sorted(full.items(), key=lambda kv: (-kv[1], kv[0]))
    top = vals[0][1]
    lideres = [f for f, v in vals if abs(v - top) < 1e-9]
    seg = next((v for f, v in vals if abs(v - top) >= 1e-9), top)
    return lideres, _r(top - seg)


def _pares_tokens(tok: Dict[str, List[str]]):
    out = {}
    for a, b in itertools.combinations(sorted(tok), 2):
        out[f"{a}|{b}"] = {"forma": f"{'+'.join(tok[a])}~{'+'.join(tok[b])}"}
    return out


# ----------------------------------------------------------------- (1) primer destello
def primer_destello(ids, toks, fams, pares_t, pares_f):
    tk, rel, fm = {}, {}, {}
    for i, c in enumerate(ids):
        for t, ejes in toks[i].items():
            if t not in tk:
                otros = sorted(x for x in toks[i] if x != t)
                tk[t] = {"token": t, "corte": c, "ejes": ejes, "contexto_en_ese_corte": otros}
        for k, v in list(pares_t[i].items()) + list(pares_f[i].items()):
            if k not in rel:
                rel[k] = {"relacion": k, "tipo": "TOKEN_TOKEN" if k in pares_t[i] else "FAMILIA_FAMILIA_TOP5",
                          "corte": c, "forma": v["forma"]}
        for f, d in fams[i].items():
            if d["nivel"] == "APAGADA":
                continue
            if f not in fm:
                fm[f] = {"familia": f, "corte": c, "nivel_en_destello": d["nivel"], "activacion": d["activacion_max"]}
            if d["nivel"] == "TOP5" and "corte_entrada_top5" not in fm[f]:
                fm[f]["corte_entrada_top5"] = c
    bajo = [x for x in fm.values() if x["nivel_en_destello"] != "TOP5"]
    sub = [x for x in fm.values() if x["nivel_en_destello"] == "BAJO_UMBRAL"]
    return {"tokens": sorted(tk.values(), key=lambda x: (ids.index(x["corte"]), x["token"])),
            "relaciones": sorted(rel.values(), key=lambda x: (ids.index(x["corte"]), x["relacion"])),
            "familias": sorted(fm.values(), key=lambda x: (ids.index(x["corte"]), x["familia"])),
            "familias_que_destellan_bajo_cuello_top5": [x["familia"] for x in bajo],
            "familias_bajo_umbral_activa_en_destello": [x["familia"] for x in sub],
            "nota_bajo_umbral": ("Ninguna familia tuvo 0<|p-0.5|<=0.005 en los tableros 244 de este caso; "
                                 "lo 'bajo umbral' observable aquí es 'activa bajo el cuello top5'.") if not sub else ""}


# ----------------------------------------------------------------- (2) convergencia
def convergencia(ids, toks, fams):
    n = len(ids)
    first = {}
    pres = {}
    for i in range(n):
        for t in toks[i]:
            first.setdefault(t, i); pres.setdefault(t, set()).add(i)
    precede = []
    for a, b in itertools.permutations(sorted(first), 2):
        ia, ib = first[a], first[b]
        if ia < ib and (ib - 1 in pres[a] or ib in pres[a]):
            precede.append({"antes": a, "despues": b, "corte_a": ids[ia], "corte_b": ids[ib],
                            "a_sigue_presente_al_llegar_b": ib in pres[a]})
    coocurren = []
    for a, b in itertools.combinations(sorted(first), 2):
        both = sorted(pres[a] & pres[b])
        if both:
            coocurren.append({"par": [a, b], "cortes": [ids[i] for i in both],
                              "fraccion_cortes": _r(len(both) / n),
                              "jaccard": _r(len(pres[a] & pres[b]) / len(pres[a] | pres[b]))})
    # cambio simultáneo: deltas de activación P entre cortes consecutivos, familias que alguna vez fueron TOP5
    vis = sorted({f for i in range(n) for f, d in fams[i].items() if d["nivel"] == "TOP5"})
    simult = []
    for i in range(1, n):
        dl = {f: fams[i][f]["P"] - fams[i - 1][f]["P"] for f in vis if f in fams[i] and f in fams[i - 1]}
        sube = sorted(f for f, d in dl.items() if d > EPS_DELTA)
        baja = sorted(f for f, d in dl.items() if d < -EPS_DELTA)
        tin = sorted(set(toks[i]) - set(toks[i - 1])); tout = sorted(set(toks[i - 1]) - set(toks[i]))
        simult.append({"de": ids[i - 1], "a": ids[i], "familias_suben_juntas": sube, "familias_bajan_juntas": baja,
                       "tokens_entran_juntos": tin, "tokens_salen_juntos": tout})
    return {"precede": precede, "coocurren": coocurren, "cambian_a_la_vez": simult,
            "fuente": "diffs entre cortes de motor.cuts *_FULL_244 + tokens del input"}


# ----------------------------------------------------------------- (3)+(4) trayectoria y reconvergencia
def trayectorias(ids, toks, pares_t):
    """Para cada relación token|token: estado por corte, usando en el corte k solo C1..Ck."""
    n = len(ids)
    rels = sorted(set().union(*[set(p) for p in pares_t]))
    out = []
    reconv = []
    for rk in rels:
        a, b = rk.split("|")
        estados = []
        first_i = None; first_ctx = None; first_forma = None
        visto_hueco = False
        for i in range(n):
            if rk in pares_t[i]:
                forma = pares_t[i][rk]["forma"]
                ctx = sorted(set(toks[i]) - {a, b})
                if first_i is None:
                    first_i, first_ctx, first_forma = i, ctx, forma
                    est = "OBSERVADA"
                elif visto_hueco:
                    est = "REAPARICION_COMPROBADA"
                    j = len(set(ctx) & set(first_ctx)) / max(1, len(set(ctx) | set(first_ctx)))
                    misma = (forma == first_forma) and j >= 0.5
                    reconv.append({"relacion": rk, "corte_reaparicion": ids[i], "corte_primer_destello": ids[first_i],
                                   "forma_destello": first_forma, "forma_regreso": forma,
                                   "contexto_destello": first_ctx, "contexto_regreso": ctx,
                                   "jaccard_contexto": _r(j),
                                   "veredicto": "MISMA" if misma else "NUEVA_POSIBLE_GIRO",
                                   "entran_en_contexto": sorted(set(ctx) - set(first_ctx)),
                                   "salen_del_contexto": sorted(set(first_ctx) - set(ctx))})
                    visto_hueco = False
                else:
                    est = "OBSERVADA"
                    if forma != first_forma:
                        est = "OBSERVADA_CAMBIA_FORMA"
            elif first_i is None:
                est = "NO_APARECIDA_AUN"
            else:
                visto_hueco = True
                pa, pb = a in toks[i], b in toks[i]
                if pa or pb:
                    est = "SE_SEPARA:sigue_" + (a if pa else b)
                else:
                    est = "LATENTE_INFERIDA"   # sin dato en este corte; no se afirma continuidad
            estados.append(est)
        out.append({"relacion": rk, "estados_por_corte": dict(zip(ids, estados))})
    return out, reconv


# ----------------------------------------------------------------- Ricci / billar por prefijo (sin fuga)
def ricci_billar_por_prefijo(motor_dir: Path, mcuts):
    ric = _load(motor_dir, "ricci_forman_coocurrencia_v0_1.py", "sl_ricci")
    bil = _load(motor_dir, "billar_circular_convergencia_v0_2.py", "sl_billar")
    if ric is None or bil is None:
        return {"status": "FALTA_PIEZA"}
    res = {}
    for k in range(2, len(mcuts) + 1):
        pref = copy.deepcopy(mcuts[:k]); cid = mcuts[k - 1].get("corte")
        K = ric.correr_cuts(copy.deepcopy(pref), "PREFIJO")
        B = bil.correr_cuts(copy.deepcopy(pref), "PREFIJO")
        nul = (B.get("v0_2") or {}).get("null") or {}
        conv_k = sorted({"|".join(sorted(e["familias"])) for e in B.get("convergencias_v0_2") or [] if e.get("corte") == cid})
        ar = ((K.get("ricci") or {}).get("aristas") or [])
        neg = sorted({f"{x['a']}|{x['b']}" for x in ar if x.get("ricci_forman", 0) < 0})
        res[cid] = {"cortes_usados": [c.get("corte") for c in pref],
                    "billar_convergencias_en_este_corte": conv_k,
                    "billar_sobre_nulo": bool((nul.get("z_score") or 0) > 1.0),
                    "ricci_media": _r((K.get("ricci") or {}).get("media") or 0.0),
                    "ricci_sobre_nulo": bool((K.get("z_media_Ric") or 0) > 1.0),
                    "ricci_aristas_negativas_ejemplo": neg[:5],
                    "ricci_aristas_negativas_n": _frac(len(neg), len(ar))}
    return {"status": "EJECUTADO", "por_corte": res,
            "nota": "ricci_forman_coocurrencia_v0_1.correr_cuts y billar_circular_convergencia_v0_2.correr_cuts sobre C1..Ck; z del nulo solo como booleano sobre_nulo (z>1)."}


# ----------------------------------------------------------------- (5) lectura olvidada
def lectura_olvidada(ids, toks, pares_t, mcuts, cands, patterns, rival_motor):
    out = []
    names = [c.get("family") for c in cands if c.get("family")]
    for k in range(len(ids)):
        lideres, margen = _lider_P(mcuts[k])
        lider = lideres[0] if lideres else None
        vistos = {}
        for i in range(k + 1):
            for t, ejes in toks[i].items():
                vistos.setdefault(t, []).extend(f"{ids[i]}:{e}" for e in ejes)
        lf = set((patterns.get(lider, {}) or {}).get("tokens_favor") or {})
        ign = []
        for f in names:
            if f in lideres:
                continue
            ff = set((patterns.get(f, {}) or {}).get("tokens_favor") or {})
            t_ign = sorted(t for t in vistos if t in ff and t not in lf)
            if t_ign:
                ign.append({"candidata": f, "tokens_a_favor_no_leidos_por_el_lider": [{"token": t, "donde": vistos[t]} for t in t_ign]})
        perdidas = sorted(set(pares_t[k - 1]) - set(pares_t[k])) if k else []
        pudo = []
        if len(lideres) > 1:
            pudo.append("EMPATE_EN_LA_CIMA_P")
        if margen < EPS_MARGEN:
            pudo.append("MARGEN_BAJO_EPS")
        if k and set(_lider_P(mcuts[k - 1])[0]) != set(lideres):
            pudo.append("CAMBIO_DE_LIDER_RESPECTO_AL_CORTE_ANTERIOR")
        out.append({"corte": ids[k], "cortes_usados": ids[:k + 1], "lider_P_en_corte": lideres, "margen_P": margen,
                    "informacion_ignorada": ign, "relaciones_perdidas_en_este_corte": perdidas,
                    "aqui_la_explicacion_pudo_cambiar": bool(pudo), "motivos": pudo})
    return {"por_corte": out, "extiende": "modo_estricto_v1.rival_que_ignore (top1 vs 2 rivales) -> todas las candidatas del top, por corte",
            "rival_que_ignore_motor_resumen": [{"rival": r.get("rival"),
                                                 "tokens_ignorados": [x.get("token") for x in r.get("que_ignore_tokens_del_input_a_favor_del_rival_y_no_del_top1") or []]}
                                                for r in (rival_motor or {}).get("rivales") or []]}


# ----------------------------------------------------------------- tabla contrafactual (p || q), INUS, Laplace
def _filas(ids, toks, mcuts, fam, k, modo):
    """Transiciones j-1 -> j con j<=k. p = q en j-1; condiciones = tokens en j-1; q = estado de fam en j."""
    def q_at(i):
        if modo == "TOP5_P":
            return fam in [f for f, _ in (mcuts[i].get("P_top5_ANEXO") or [])]
        lid, _ = _lider_P(mcuts[i]); return lid == [fam]
    filas = []
    for j in range(1, k + 1):
        filas.append({"de": ids[j - 1], "a": ids[j], "p": q_at(j - 1), "cond": set(toks[j - 1]), "q": q_at(j)})
    return filas


def tabla_contrafactual(ids, toks, mcuts, fam, k, modo):
    F = _filas(ids, toks, mcuts, fam, k, modo)
    n = len(F); nq = sum(f["q"] for f in F)
    out = {"q": f"{fam}::{modo}", "cortes_usados": ids[:k + 1], "n_transiciones": _frac(n, n) if n else "0/0",
           "q_verdadero_en": _frac(nq, n)}
    if n == 0:
        out["estado"] = "SIN_TRANSICIONES"; return out
    # p || q (tabla de verdad observada)
    cel = {"p_y_q": 0, "p_y_no_q": 0, "no_p_y_q": 0, "no_p_y_no_q": 0}
    for f in F:
        cel[("p" if f["p"] else "no_p") + ("_y_q" if f["q"] else "_y_no_q")] += 1
    out["tabla_p_q"] = {kk: _frac(v, n) for kk, v in cel.items()}
    out["p_o_q_observado"] = _frac(sum(1 for f in F if f["p"] or f["q"]), n)
    out["p_entonces_q_laplace"] = laplace(cel["p_y_q"], cel["p_y_q"] + cel["p_y_no_q"])
    conds = sorted(set().union(*[f["cond"] for f in F]))
    filas_cond = []
    def suf(S):
        rows = [f for f in F if S <= f["cond"]]
        return rows, len(rows) >= MIN_FILAS_SUF and all(f["q"] for f in rows)
    def nec(S):
        rq = [f for f in F if f["q"]]
        return bool(rq) and all(S <= f["cond"] for f in rq)
    for c in conds:
        rows = [f for f in F if c in f["cond"]]
        s = sum(f["q"] for f in rows)
        rp = [f for f in rows if f["p"]]
        p_solo = [f for f in F if f["p"]]
        filas_cond.append({"condicion": c,
                           "presente_en": _frac(len(rows), n),
                           "c_y_q": _frac(s, len(rows)),
                           "necesaria_en_datos": nec({c}),
                           "suficiente_en_datos": suf({c})[1],
                           "soporte_suficiencia_laplace": laplace(s, len(rows)),
                           "soporte_necesidad_laplace": laplace(s, nq),
                           "ademas_de_p": {"p_y_c_entonces_q": _frac(sum(f["q"] for f in rp), len(rp)),
                                           "p_solo_entonces_q": _frac(sum(f["q"] for f in p_solo), len(p_solo)),
                                           "c_completa_a_p": bool(rp) and len(rp) >= MIN_FILAS_SUF and all(f["q"] for f in rp)
                                           and not all(f["q"] for f in p_solo)}})
    # INUS: conjuntos mínimos suficientes (tamaño 2..3) no necesarios; cada miembro insuficiente y no redundante
    inus = []
    frecuentes = [c for c in conds if sum(c in f["cond"] for f in F) >= MIN_FILAS_SUF]
    minimos = []
    for size in range(2, MAX_CONJ + 1):
        for S in itertools.combinations(frecuentes, size):
            S = frozenset(S)
            if any(m <= S for m in minimos):
                continue
            rows, ok = suf(S)
            if not ok:
                continue
            if any(suf(set(S) - {x})[1] for x in S):
                continue
            minimos.append(S)
            miembros_inus = [x for x in S if not suf({x})[1]]
            if len(miembros_inus) == len(S):
                es_nec = nec(S)
                inus.append({"conjunto": sorted(S), "filas": _frac(len(rows), n),
                             "soporte_laplace": laplace(len(rows), len(rows)),
                             "tipo": "CONJUNTO_SUFICIENTE_Y_NECESARIO_EN_DATOS" if es_nec else "INUS_LIKE",
                             "lectura": ("cada miembro es parte insuficiente y no redundante de un conjunto que en estos cortes fue suficiente y además necesario (no hay otra vía observada)"
                                         if es_nec else
                                         "cada miembro es parte insuficiente pero no redundante de un conjunto suficiente-en-datos que no es necesario (hay otras vías a q)")})
    out["condiciones"] = filas_cond
    out["inus_like"] = inus[:12]
    out["inus_like_total"] = _frac(len(inus[:12]), max(len(inus), 1)) if inus else "0/0"
    out["nota"] = "Valores observados en cortes C1..Ck; no prueba causal. Laplace = (s+1)/(n+2) recortado a 5–95 %."
    if nq == n:
        out["advertencia"] = "q siempre verdadero en estas transiciones: necesidad/suficiencia degeneradas (sin contraste)."
    return out


def parecia_que_iba_a_ser(ids, toks, mcuts, final_fam, k):
    """Candidata que lideraba P en algún corte j<k y ya no lidera en k (solo C1..Ck)."""
    out = []
    lid = [_lider_P(mcuts[i])[0] for i in range(k + 1)]
    for j in range(k):
        for f in lid[j]:
            if f in lid[k] or f == final_fam:
                continue
            # corte donde perdió: primer i>j con f fuera del liderazgo
            i = next((x for x in range(j + 1, k + 1) if f not in lid[x]), None)
            if i is None:
                continue
            antes, despues = set(toks[i - 1]), set(toks[i])
            out.append({"candidata": f, "lideraba_en": ids[j], "pierde_en": ids[i],
                        "lider_que_la_desplaza": lid[i],
                        "condiciones_que_faltaron_al_perder": sorted(antes - despues),
                        "condiciones_que_aparecieron_al_perder": sorted(despues - antes),
                        "lectura": "lo que tuvo que no estar (o estar) para que no fuera lo que parecía; observado, no causal"})
    seen = set(); uniq = []
    for x in out:
        key = (x["candidata"], x["pierde_en"])
        if key not in seen:
            seen.add(key); uniq.append(x)
    return uniq


# ----------------------------------------------------------------- suma restando (anotación)
def suma_restando(tray, reconv, olvido, rb):
    mas = []; menos_desap = []; menos_acc = []; indecid = []
    last = olvido["por_corte"][-1] if olvido["por_corte"] else {}
    for g in last.get("informacion_ignorada", []):
        for t in g["tokens_a_favor_no_leidos_por_el_lider"]:
            mas.append({"suma": "relacion_omitida", "token": t["token"], "favorece_a": g["candidata"]})
    for tr in tray:
        est = list(tr["estados_por_corte"].values())
        if any(e.startswith("SE_SEPARA") for e in est) or any(e == "OBSERVADA_CAMBIA_FORMA" for e in est):
            menos_desap.append({"resta": "explicacion_que_asume_que_el_factor_desaparecio", "relacion": tr["relacion"],
                                "porque": "un miembro sigue presente o la relación cambió de forma"})
        obs = sum(1 for e in est if e.startswith("OBSERVADA") or e == "REAPARICION_COMPROBADA")
        if obs == 1:
            menos_acc.append({"resta": "coincidencia_de_un_solo_corte", "relacion": tr["relacion"]})
        if est and est[-1] == "LATENTE_INFERIDA":
            indecid.append({"queda": "LATENTE_INFERIDA", "relacion": tr["relacion"]})
    nulo = {c: v.get("billar_sobre_nulo") for c, v in (rb.get("por_corte") or {}).items()}
    return {"estado": "ANOTACION_NO_DECIDE", "suma_relaciones_omitidas": mas,
            "resta_explicaciones_de_desaparicion_con_trayectoria_viva": menos_desap,
            "resta_coincidencias_accidentales": menos_acc[:60],
            "resta_coincidencias_accidentales_total": _frac(min(60, len(menos_acc)), max(1, len(menos_acc))),
            "convergencias_billar_sobre_nulo_por_prefijo": nulo,
            "indecidibles_se_quedan_como_latente_inferida": indecid}


# ----------------------------------------------------------------- ledger acumulativo (nunca borra)
def actualizar_ledger(path: Path, case_key: str, primer, tray, reconv):
    path.parent.mkdir(parents=True, exist_ok=True)
    prev = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                e = json.loads(line); prev[(e["caso_hash"], e["relacion"], e["evento"], e["corte"])] = e
    nuevos = []
    def add(rel, ev, corte, extra=None):
        key = (case_key, rel, ev, corte)
        if key in prev:
            return
        e = {"caso_hash": case_key, "relacion": rel, "evento": ev, "corte": corte, **(extra or {})}
        prev[key] = e; nuevos.append(e)
    for r in primer["relaciones"]:
        add(r["relacion"], "PRIMER_DESTELLO", r["corte"], {"forma": r["forma"], "tipo": r["tipo"]})
    for tr in tray:
        for c, est in tr["estados_por_corte"].items():
            if est not in ("NO_APARECIDA_AUN",):
                add(tr["relacion"], est, c)
    for x in reconv:
        add(x["relacion"], "RECONVERGENCIA_" + x["veredicto"], x["corte_reaparicion"])
    with path.open("a", encoding="utf-8") as fh:      # append-only
        for e in nuevos:
            fh.write(json.dumps(e, ensure_ascii=False, sort_keys=True) + "\n")
    return {"ruta": str(path), "eventos_nuevos_esta_corrida": _frac(len(nuevos), len(prev)), "politica": "APPEND_ONLY_NUNCA_BORRA"}


def huella_H(result) -> str:
    keep = {"H1": result.get("H1"), "H2": result.get("H2"), "apuesta": result.get("apuesta"),
            "orden": [c.get("family") for c in (result.get("predictor") or {}).get("candidates") or []],
            "rank": [c.get("rank_fusion") for c in (result.get("predictor") or {}).get("candidates") or []],
            "cierre_final": result.get("cierre_final")}
    return hashlib.sha256(json.dumps(keep, sort_keys=True, default=str, ensure_ascii=False).encode()).hexdigest()


def max_abs_num(o) -> float:
    if isinstance(o, bool):
        return 0.0
    if isinstance(o, (int, float)):
        return abs(float(o))
    if isinstance(o, dict):
        return max([max_abs_num(v) for v in o.values()] + [0.0])
    if isinstance(o, list):
        return max([max_abs_num(v) for v in o] + [0.0])
    return 0.0


# ----------------------------------------------------------------- run
def run(result: Dict[str, Any], case: Dict[str, Any], motor_dir: Path, ledger_path: Path | None = None) -> Dict[str, Any]:
    h0 = huella_H(result)
    result_ro = copy.deepcopy(result)
    mcuts = (result_ro.get("motor") or {}).get("cuts") or []
    icuts = case.get("cuts") or []
    ids = [c.get("corte") for c in mcuts]
    if [c.get("id") for c in icuts] != ids:
        raise ValueError("ids de corte del input y del RESULT no coinciden")
    patterns = json.loads((motor_dir / "patterns_final_v14.json").read_text(encoding="utf-8"))
    toks = [_tokens_corte(c) for c in icuts]
    fams = [_familias_corte(c) for c in mcuts]
    pares_t = [_pares_tokens(t) for t in toks]
    pares_f = []
    for c in mcuts:
        t5 = [f for f, _ in (c.get("P_top5_ANEXO") or [])]
        pares_f.append({f"{a}|{b}": {"forma": "P_top5"} for a, b in itertools.combinations(sorted(t5), 2)})
    cands = (result_ro.get("predictor") or {}).get("candidates") or []
    final_fam = (result_ro.get("H1") or {}).get("family")
    # reuso: trazar_temporal por prefijo (estado del token en el corte k usando solo C1..Ck)
    tt = _load(motor_dir, "sidecar_trazabilidad_temporal.py", "sl_traza")
    traza = {}
    if tt is not None:
        for k in range(len(icuts)):
            T = tt.trazar_temporal(copy.deepcopy(icuts[:k + 1]))
            traza[ids[k]] = {x["token"]: x.get("estado_actual") for x in T.get("tokens") or []}
    # reuso: capa_integracion comparar_configuraciones entre consecutivos
    ci = _load(motor_dir, "capa_integracion_semantica_v1_2.py", "sl_ci")
    trans = []
    if ci is not None:
        confs = [ci.configurar_corte(ids[i], {e: [t for t, ej in toks[i].items() if e in ej] for e in EJES}) for i in range(len(ids))]
        for a, b in zip(confs, confs[1:]):
            t = ci.comparar_configuraciones(a, b)["transicion"]
            trans.append({"de": a["corte"], "a": b["corte"], "aparecen": t["aparecen"], "desaparecen": t["desaparecen"]})
    primer = primer_destello(ids, toks, fams, pares_t, pares_f)
    conv = convergencia(ids, toks, fams)
    tray, reconv = trayectorias(ids, toks, pares_t)
    rb = ricci_billar_por_prefijo(motor_dir, mcuts)
    olvido = lectura_olvidada(ids, toks, pares_t, mcuts, cands, patterns,
                              (result_ro.get("modo_estricto") or {}).get("rival_que_ignore"))
    sr = suma_restando(tray, reconv, olvido, rb)
    cf = {}
    for k in range(1, len(ids)):
        cf[ids[k]] = {"q_principal": tabla_contrafactual(ids, toks, mcuts, final_fam, k, "LIDER_UNICO_P"),
                      "q_top5": tabla_contrafactual(ids, toks, mcuts, final_fam, k, "TOP5_P"),
                      "parecia_que_iba_a_ser": parecia_que_iba_a_ser(ids, toks, mcuts, final_fam, k)}
    mf = result_ro.get("movimiento_de_fondo") or {}
    dormidos = sorted(f for f, s in (mf.get("series_familias") or {}).items() if s.get("clase") == "LATENTE_DORMIDO")
    out = {"version": VERSION, "contrato": CONTRATO, "cortes": ids,
           "laplace_y_contrafactual_existente": {
               "regla_de_sucesion_en_motor": "NO_ENCONTRADA",
               "usada": "Laplace (s+1)/(n+2) recortada a 5–95 % (añadida por este sidecar)",
               "piezas_reusadas_como_contexto": {
                   "hipotesis_necesarias_suficientes(predictibilidad_set_021)": (result_ro.get("hipotesis_necesarias_suficientes") or {}).get("eje"),
                   "decimo_hombre_contrafactuales_ablacion": bool((result_ro.get("decimo_hombre_esteroides") or {}))}},
           "1_primer_destello": primer,
           "2_convergencia": conv,
           "3_trayectorias_relaciones": tray,
           "4_reconvergencia": reconv,
           "5_lectura_olvidada": olvido,
           "suma_restando": sr,
           "contrafactual_por_corte": cf,
           "ricci_billar_por_prefijo": rb,
           "reuso": {"trazar_temporal_por_prefijo": traza,
                     "capa_integracion_transiciones": trans,
                     "movimiento_de_fondo_LATENTE_DORMIDO_retro": dormidos,
                     "metacognicion": "PRE-H: bloques por corte usan C1..Ck. RETRO: veredicto de reconvergencia y suma_restando miran todos los cortes."}}
    if ledger_path is not None:
        out["ledger"] = actualizar_ledger(ledger_path, hashlib.sha256(json.dumps(ids + [sorted(t) for t in toks]).encode()).hexdigest()[:16],
                                          primer, tray, reconv)
    h1 = huella_H(result)
    out["verificacion_H_intacto"] = {"huella_antes": h0, "huella_despues": h1, "H_intacto": h0 == h1}
    out["max_abs_numero_en_salida"] = _r(max_abs_num(out))
    return out


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--result", required=True); ap.add_argument("--case", required=True)
    ap.add_argument("--motor", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--ledger", required=True)
    a = ap.parse_args(argv)
    res = json.loads(Path(a.result).read_text(encoding="utf-8"))
    case = json.loads(Path(a.case).read_text(encoding="utf-8"))
    out = run(res, case, Path(a.motor).resolve(), Path(a.ledger).resolve())
    Path(a.out).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"H_intacto": out["verificacion_H_intacto"]["H_intacto"], "max_abs": out["max_abs_numero_en_salida"]}))


if __name__ == "__main__":
    main()
