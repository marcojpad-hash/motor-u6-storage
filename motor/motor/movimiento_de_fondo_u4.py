#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""movimiento_de_fondo_u4.py — U4_todos_tokens (2026-10-11). Capa LATERAL de traza: «movimiento de fondo».

Pedido de Mj (11-oct 18:01 CT): todos los casos deben llevar MUCHOS tokens. La predictibilidad pasa por el top 3–5
(cuello de botella), pero hay que ver TODOS los tokens para ver cómo y qué se mueve abajo: algo puede estar
cocinándose desde abajo mucho antes de salir a la superficie. Picos y mesetas.

Contrato: can_decide_H=False, reordena=False, writes_canonical=False. No toca rank_fusion, H1/H2, apuesta, grado 020
ni el set 021. Solo lee cortes <= Z (los del input). No usa nombres propios ni años.

Series
 - TOKEN t:   w_t(c) = peso del token en el corte c (máximo entre ejes P/A/C si aparece en varios); 0 si no está.
              presente(c) <=> w_t(c) > 0. Se usa el input COMPLETO (todos los tokens, también los que el cuello
              top-5 no pasa al Engine).
 - FAMILIA f: a_f(c) = media_PAC(p_final_f(c)) - 0.5 en el tablero del Engine canónico alimentado con TODOS los tokens
              (pasada lateral; si ningún corte superó 5 tokens por eje, ese tablero es idéntico al canónico de la
              corrida y se reutiliza). Es activación acumulada (P_final), no probabilidad del desenlace.
              presente(c) <=> la familia recibe masa de tokens_favor (244) en el corte c (evidencia directa).
              rango(c) = posición de f entre las familias con a_f(c) > UMBRAL_ACTIVA (1 = más activa; empates por nombre).

Clases (primera que aplica, en este orden; 'rasgos' lista todas las que se cumplen):
  PICO            algún paso |d| >= GRANDE entre cortes consecutivos presentes, o aparición aislada (1 solo corte).
  LATENTE_DORMIDO presente, ausente >= 1 corte, y vuelve a estar presente antes o en Z.
  ASCENSO_LENTO   primera aparición en la primera mitad de los cortes, sube neto >= 3*EPS (familias) / 2*EPS (tokens)
                  desde que aparece, sube (d >= EPS) en al menos la mitad de los pasos, ningún paso >= GRANDE
                  («se cocina desde abajo»).
  DESCENSO        se apaga antes de Z (presente y luego ausente sin volver), o en Z está >= 3*EPS (familias) /
                  2*EPS (tokens) por debajo de su máximo.
  MESETA          presente >= 3 cortes y rango de valores <= 2*EPS.
  SIN_FORMA_CLARA ninguna de las anteriores.
Umbrales: familias EPS=0.01; GRANDE = max(0.05, percentil 95 de los |d| > 0.001 de todas las familias DEL CASO)
          (0.05 ≈ percentil 95 en Noether/Cobain/JPII U3; en casos con muchos tokens los pasos son mayores y el umbral sube);
          tokens   EPS=0.02, GRANDE=0.10 (peso de contrato 0.60–0.84).  UMBRAL_ACTIVA = 0.005.

Emergentes desde abajo (familias): «abajo» = rango en Z > 5 en el tablero con todos los tokens, O fuera del top-5 que
  publica el predictor (020) aunque en el tablero esté arriba (el cuello predictivo no la deja salir). Además: rango en Z <= 20 Y
  primera aparición en la primera mitad de los cortes Y pendiente MCO de a_f desde la primera aparición > 0.005/corte Y
  sube (d >= EPS) en >= la mitad de los pasos desde que aparece Y ningún paso desde que aparece baja EPS o más Y
  el rango en Z es mejor que el rango con el que apareció (sube de posición).
  Son candidatas a salir a la superficie después de Z. Se marcan si están en el top-5 publicado (020) y en el set 021,
  y pasan por el paso inverso de 021 (qué cortes explican, acero frente al eje, aporte marginal sobre el set).
"""
from __future__ import annotations
import importlib.util, math, random
from pathlib import Path
from typing import Any, Dict, List, Optional

VERSION = "MOVIMIENTO_DE_FONDO_U4_20261011"
CUELLO_K = 5
UMBRAL_ACTIVA = 0.005
FAM = {"EPS": 0.01, "GRANDE": 0.05, "NETO_ASC": 0.03, "NETO_DESC": 0.03, "MESETA_RANGO": 0.02}
TOK = {"_tok": True, "EPS": 0.02, "GRANDE": 0.10, "NETO_ASC": 0.04, "NETO_DESC": 0.04, "MESETA_RANGO": 0.04}
EMERGE = {"rango_Z_mayor_que": 5, "rango_Z_max": 20, "pendiente_min": 0.005, "frac_pasos_que_suben_min": 0.5, "sin_caidas_mayores_a_EPS": True}
ORDEN_CLASES = ("PICO", "LATENTE_DORMIDO", "ASCENSO_LENTO", "DESCENSO", "MESETA")


def _ols(xs: List[float], ys: List[float]) -> float:
    n = len(xs)
    if n < 2: return 0.0
    mx = sum(xs) / n; my = sum(ys) / n
    den = sum((x - mx) ** 2 for x in xs)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den if den else 0.0


def clasificar(valores: List[float], presente: List[bool], U: Dict[str, float]) -> Dict[str, Any]:
    n = len(valores)
    idx = [i for i, p in enumerate(presente) if p]
    if not idx:
        return {"clase": "SIN_SENAL", "rasgos": [], "primera": None}
    first, last = idx[0], idx[-1]
    rasgos = []
    gap = any(idx[j + 1] - idx[j] > 1 for j in range(len(idx) - 1))
    span = list(range(first, n))                     # desde que aparece hasta Z
    vals = [valores[i] for i in span]
    ds = [vals[j + 1] - vals[j] for j in range(len(vals) - 1)]
    # pasos entre cortes presentes consecutivos (para tokens: no cuenta la entrada desde 0)
    dpres = [valores[idx[j + 1]] - valores[idx[j]] for j in range(len(idx) - 1) if idx[j + 1] - idx[j] == 1]
    dsharp = dpres if U.get("_tok") else ds
    if len(idx) == 1 or any(abs(d) >= U["GRANDE"] for d in dsharp):
        rasgos.append("PICO")
    if gap:
        rasgos.append("LATENTE_DORMIDO")
    temprano = first <= (n - 1) // 2
    vref = [valores[i] for i in idx] if U.get("_tok") else vals
    dref = dpres if U.get("_tok") else ds
    neto = vref[-1] - vref[0] if vref else 0.0
    ups = sum(1 for d in dref if d >= U["EPS"])
    if temprano and len(dref) >= 2 and neto >= U["NETO_ASC"] and ups >= math.ceil(len(dref) / 2) and not any(d >= U["GRANDE"] for d in dref):
        rasgos.append("ASCENSO_LENTO")
    se_apaga = last < n - 1 and not gap if U.get("_tok") else (last < n - 1 and valores[-1] <= UMBRAL_ACTIVA)
    if se_apaga or (vref and vref[-1] <= max(vref) - U["NETO_DESC"]):
        rasgos.append("DESCENSO")
    if len(idx) >= 3 and (max(vref) - min(vref)) <= U["MESETA_RANGO"]:
        rasgos.append("MESETA")
    clase = next((c for c in ORDEN_CLASES if c in rasgos), "SIN_FORMA_CLARA")
    return {"clase": clase, "rasgos": rasgos, "primera": first, "ultima": last, "neto": round(neto, 4),
            "pasos_que_suben": ups, "n_pasos": len(dref), "temprano": temprano}


def _rows(c, e):
    return [(str(p[0]), float(p[1])) for p in (c.get(e) or []) if isinstance(p, (list, tuple)) and len(p) >= 2]


def _tableros_completos(case, motor, native, base: Path, monte_carlo: bool, seed: int):
    cuello = (motor or {}).get("cuello_top5_engine") or {}
    mcuts = (motor or {}).get("cuts") or []
    if not cuello.get("aplicado") and all(c.get("P_FULL_244") for c in mcuts):
        return [{e: c[e + "_FULL_244"] for e in "PAC"} for c in mcuts], "TABLERO_CANONICO_DE_LA_CORRIDA (ningún eje superó 5 tokens: idéntico al de todos los tokens)"
    spec = importlib.util.spec_from_file_location("eng_fondo_u4", str(base / "Engine_V5_CANONICO_SOLO.py"))
    eng = importlib.util.module_from_spec(spec); spec.loader.exec_module(eng)
    pat = str(native._PATTERNS_PATH())
    q = str(case.get("question", case.get("case_id", "")))
    st = random.getstate()
    try:
        random.seed(seed)
        E = {e: native._engine(eng, pat, q + "_FONDO_" + e) for e in "PAC"}
        out = []
        for c in case.get("cuts") or []:
            cid = str(c.get("id"))
            out.append({e: native._board(eng, E[e], cid + "_" + e + "_FONDO", _rows(c, e), monte_carlo=monte_carlo) for e in "PAC"})
        for e in E.values():
            try: native._close_engine(e)
            except Exception: pass
    finally:
        random.setstate(st)
    return out, "PASADA_LATERAL_ENGINE_CANONICO_TODOS_LOS_TOKENS (semilla del caso; estado RNG restaurado)"


def run(case: Dict[str, Any], result: Dict[str, Any], base, patterns: Dict[str, Any], native, monte_carlo: bool = True,
        seed: int = 0, p021=None) -> Dict[str, Any]:
    base = Path(base)
    cuts = case.get("cuts") or []
    ids = [str(c.get("id") or f"C{i+1}") for i, c in enumerate(cuts)]
    n = len(ids)
    motor = result.get("motor") or {}
    # ---------------- tokens (todos)
    fav_of: Dict[str, List[str]] = {}
    for f, p in patterns.items():
        if isinstance(p, dict):
            for t in (p.get("tokens_favor") or {}): fav_of.setdefault(t, []).append(f)
    cuello = motor.get("cuello_top5_engine") or {}
    fuera_cuello = {(x["corte"], x["eje"], x["token"]) for lg in cuello.get("cortes") or [] for x in lg.get("quedan_fuera_del_engine") or []}
    tok_series: Dict[str, Dict[str, Any]] = {}
    masa_fam = {}
    for i, c in enumerate(cuts):
        for e in "PAC":
            for t, w in _rows(c, e):
                s = tok_series.setdefault(t, {"w": [0.0] * n, "ejes": [[] for _ in range(n)], "en_catalogo_244": t in fav_of or any(t in (p.get("tokens_contra") or {}) for p in patterns.values() if isinstance(p, dict)),
                                              "cortes_fuera_del_engine": []})
                s["w"][i] = max(s["w"][i], w); s["ejes"][i].append(e)
                if (ids[i], e, t) in fuera_cuello: s["cortes_fuera_del_engine"].append(ids[i] + ":" + e)
                for f in fav_of.get(t, []):
                    masa_fam.setdefault(f, [0.0] * n)[i] += w
    tokens_out = {}
    for t, s in tok_series.items():
        cl = clasificar(s["w"], [w > 0 for w in s["w"]], TOK)
        tokens_out[t] = {"serie_peso": [round(w, 4) for w in s["w"]], "ejes_por_corte": s["ejes"], "en_catalogo_244": s["en_catalogo_244"],
                         "familias_favor": sorted(fav_of.get(t, [])), "cortes_fuera_del_engine_por_cuello": s["cortes_fuera_del_engine"], **cl,
                         "primera": ids[cl["primera"]] if cl.get("primera") is not None else None,
                         "ultima": ids[cl["ultima"]] if cl.get("ultima") is not None else None}
    # ---------------- familias (tablero con todos los tokens)
    boards, fuente = _tableros_completos(case, motor, native, base, monte_carlo, seed)
    fams = sorted(boards[0]["P"].keys()) if boards else []
    act = {f: [sum(b[e].get(f, 0.5) for e in "PAC") / 3.0 - 0.5 for b in boards] for f in fams}
    _nz = sorted(abs(s[i] - s[i - 1]) for s in act.values() for i in range(1, len(s)) if abs(s[i] - s[i - 1]) > 0.001)
    U_F = dict(FAM); U_F["GRANDE"] = round(max(FAM["GRANDE"], _nz[int(0.95 * (len(_nz) - 1))] if _nz else 0.0), 4)
    def ranks(A):
        R = []
        for i in range(n):
            vivos = sorted([f for f in fams if A[f][i] > UMBRAL_ACTIVA], key=lambda f: (-A[f][i], f))
            R.append({f: k + 1 for k, f in enumerate(vivos)})
        return R
    R = ranks(act)
    # tablero del cuello (el que ve el predictor) para comparar qué esconde el cuello
    mcuts = motor.get("cuts") or []
    actC = {f: [sum((c.get(e + "_FULL_244") or {}).get(f, 0.5) for e in "PAC") / 3.0 - 0.5 for c in mcuts] for f in fams} if mcuts and all(c.get("P_FULL_244") for c in mcuts) else None
    RC = ranks(actC) if actC else None
    pred = result.get("predictor") or {}
    top5_020 = [c.get("family") for c in (pred.get("candidates") or [])[:CUELLO_K] if isinstance(c, dict)]
    hns = result.get("hipotesis_necesarias_suficientes") or {}
    set021 = [m.get("familia") for m in hns.get("miembros") or []]
    eje = hns.get("eje") or (result.get("cierre_final") or {}).get("H1")
    fam_out = {}; abajo = []
    for f in fams:
        pres = [masa_fam.get(f, [0.0] * n)[i] > 0 for i in range(n)]
        if not any(pres) and max(act[f]) <= UMBRAL_ACTIVA:
            continue
        cl = clasificar(act[f], pres, U_F)
        rs = [R[i].get(f) for i in range(n)]
        first = cl.get("primera")
        if first is None:   # activa sin evidencia directa (solo por arrastre del tablero)
            first = next((i for i in range(n) if act[f][i] > UMBRAL_ACTIVA), None)
        xs = list(range(first, n)) if first is not None else []
        pend = _ols([float(x) for x in xs], [act[f][x] for x in xs]) if xs else 0.0
        rr = [(x, rs[x]) for x in xs if rs[x] is not None]
        pend_r = -_ols([float(x) for x, _ in rr], [float(r) for _, r in rr]) if len(rr) >= 2 else 0.0
        ds = [act[f][x + 1] - act[f][x] for x in xs[:-1]]
        ups = sum(1 for d in ds if d >= FAM["EPS"])
        rZ = rs[-1] if rs else None
        r0 = next((r for _, r in rr), None)
        row = {"serie_activacion": [round(v, 4) for v in act[f]], "serie_rango": rs, "presente_por_evidencia": pres,
               "masa_favor_por_corte": [round(v, 4) for v in masa_fam.get(f, [0.0] * n)], **{k: v for k, v in cl.items() if k not in ("primera", "ultima")},
               "primera_aparicion": ids[first] if first is not None else None, "pendiente_activacion_por_corte": round(pend, 5),
               "pendiente_rango_por_corte_(+sube)": round(pend_r, 4), "rango_al_aparecer": r0, "rango_en_Z": rZ,
               "rango_en_Z_tablero_cuello": (RC[-1].get(f) if RC else None), "en_top5_020": f in top5_020, "en_set_021": f in set021}
        bajo = (rZ is not None and rZ > EMERGE["rango_Z_mayor_que"]) or (f not in top5_020)
        emerg = (rZ is not None and bajo and rZ <= EMERGE["rango_Z_max"] and first is not None and first <= (n - 1) // 2 and
                 pend > EMERGE["pendiente_min"] and len(ds) >= 1 and ups >= math.ceil(EMERGE["frac_pasos_que_suben_min"] * len(ds) - 1e-9) and
                 all(d > -FAM["EPS"] for d in ds) and r0 is not None and rZ < r0)
        row["emergente_desde_abajo"] = bool(emerg)
        row["donde_esta_abajo"] = ("BAJO_TOP5_DEL_TABLERO" if (rZ is not None and rZ > EMERGE["rango_Z_mayor_que"]) else "ARRIBA_EN_TABLERO_PERO_FUERA_DEL_TOP5_020") if emerg else "NO_EMERGENTE"
        fam_out[f] = row
        if rZ is not None and rZ > CUELLO_K and pend_r > 0:
            abajo.append(f)
    emergentes = sorted([f for f, r in fam_out.items() if r["emergente_desde_abajo"]], key=lambda f: (fam_out[f]["rango_en_Z"], f))
    abajo = sorted(abajo, key=lambda f: (-fam_out[f]["pendiente_rango_por_corte_(+sube)"], f))
    # ---------------- paso inverso 021 sobre las emergentes
    inv_out = {}
    if p021 is not None and emergentes and eje:
        try:
            cand = [eje] + [f for f in emergentes if f != eje]
            inv, cortes, W = p021.paso_inverso(case, cand, patterns, eje)
            set_inv, _, _ = p021.paso_inverso(case, set021 or [eje], patterns, eje)
            cov = set()
            for m in set021 or [eje]: cov |= set_inv[m]["_expl"]
            ce_set = set()
            for m in set021 or [eje]: ce_set |= set(set_inv[m]["cortes_explicados"])
            for f in emergentes:
                if f == eje: continue
                h = inv[f]; a = h.get("acero_inverso_vs_eje")
                marg = h["_expl"] - cov
                inv_out[f] = {"cortes_explicados": h["cortes_explicados"], "cortes_sin_explicar": h["cortes_sin_explicar"],
                              "cortes_que_contradice": h["cortes_que_contradice"], "masa_explicada": h["masa_explicada"],
                              "acero_inverso_vs_eje": a.get("veredicto") if isinstance(a, dict) else a,
                              "masa_que_explica_y_el_eje_no": a.get("masa_que_explica_y_el_eje_no") if isinstance(a, dict) else 0.0,
                              "aporte_marginal_sobre_el_set_021_masa": round(sum(W[k] for k in marg), 4),
                              "tokens_que_el_set_no_explica": sorted([list(k) for k in marg]),
                              "explica_cortes_que_el_set_deja_sin_explicar": [c for c in h["cortes_explicados"] if c not in ce_set],
                              "en_set_021": f in set021, "en_top5_020": f in top5_020}
        except Exception as ex:
            inv_out = {"status": "ERROR", "error": f"{type(ex).__name__}:{ex}"}
    cocina = []
    for f in emergentes:
        r = fam_out[f]
        cocina.append({"familia": f, "donde_esta_abajo": r["donde_esta_abajo"], "rango_en_Z": r["rango_en_Z"], "rango_al_aparecer": r["rango_al_aparecer"], "primera_aparicion": r["primera_aparicion"],
                       "clase": r["clase"], "pendiente_activacion_por_corte": r["pendiente_activacion_por_corte"],
                       "activacion_en_Z": r["serie_activacion"][-1], "en_top5_020": r["en_top5_020"], "en_set_021": r["en_set_021"],
                       "inverso": {k: (inv_out.get(f) or {}).get(k) for k in ("cortes_explicados", "acero_inverso_vs_eje", "aporte_marginal_sobre_el_set_021_masa", "explica_cortes_que_el_set_deja_sin_explicar")}})
    tok_abajo = sorted([t for t, r in tokens_out.items() if r["clase"] == "ASCENSO_LENTO" or (r["cortes_fuera_del_engine_por_cuello"] and r["clase"] in ("MESETA", "LATENTE_DORMIDO"))])
    resumen_clases = {"tokens": {}, "familias": {}}
    for t, r in tokens_out.items(): resumen_clases["tokens"][r["clase"]] = resumen_clases["tokens"].get(r["clase"], 0) + 1
    for f, r in fam_out.items(): resumen_clases["familias"][r["clase"]] = resumen_clases["familias"].get(r["clase"], 0) + 1
    return _sin_null({"version": VERSION, "can_decide_H": False, "reordena": False, "writes_canonical": False, "lateral": True,
            "momento": "post-freeze (cortes <= Z), después del cierre 020 y de 021",
            "cortes": ids, "fuente_tablero_familias": fuente,
            "umbrales": {"familias": U_F, "tokens": {k: v for k, v in TOK.items() if k != "_tok"}, "umbral_activa": UMBRAL_ACTIVA, "emergente": EMERGE, "orden_clases": list(ORDEN_CLASES)},
            "cuello_top5_engine": {k: cuello.get(k) for k in ("k", "aplicado", "n_ejes_con_cuello", "n_tokens_entrada", "n_tokens_al_engine", "n_tokens_fuera_del_engine", "regla")},
            "top5_020": top5_020, "set_021": set021, "eje": eje,
            "resumen_clases": resumen_clases,
            "lo_que_se_cocina_abajo": cocina,
            "familias_bajo_top5_subiendo_de_rango": [{"familia": f, "rango_en_Z": fam_out[f]["rango_en_Z"], "primera_aparicion": fam_out[f]["primera_aparicion"],
                                                      "pendiente_rango_por_corte_(+sube)": fam_out[f]["pendiente_rango_por_corte_(+sube)"], "clase": fam_out[f]["clase"],
                                                      "emergente": fam_out[f]["emergente_desde_abajo"]} for f in abajo],
            "tokens_que_se_cocinan_abajo": tok_abajo,
            "paso_inverso_emergentes": inv_out,
            "series_tokens": tokens_out, "series_familias": fam_out})


def _sin_null(o):
    """Contrato terminal del motor: sin null. None -> 'NO_APLICA' (rango de una familia inactiva en ese corte, etc.)."""
    if o is None: return "NO_APLICA"
    if isinstance(o, dict): return {k: _sin_null(v) for k, v in o.items()}
    if isinstance(o, list): return [_sin_null(v) for v in o]
    if isinstance(o, float) and not math.isfinite(o): return "NO_FINITO"
    return o
