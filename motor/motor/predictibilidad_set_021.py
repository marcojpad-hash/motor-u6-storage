#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""predictibilidad_set_021.py — U3_predictibilidad (2026-10-11). Capa lateral POST-FREEZE, POST-cierre 020.

Pedido de Mj (11-oct 16:03 CT):
 A) ESCALA: volver a una escala < 1 con base desde el inicio (como el soporte P_final del Engine canónico)
    y mostrar cuánto aporta cada componente de rank_fusion a ese porcentaje.
 B) SET DE HIPÓTESIS: no forzar H1/H2; emitir el conjunto necesario y suficiente (eje + componentes).
 C) PASO INVERSO post-freeze: desde cada hipótesis de vuelta a los cortes (qué explica, qué deja sin explicar,
    acero de cada rival), alimentando el set y su grado.

Reglas: no cambia rank_fusion, ni el orden de H, ni H1/H2, ni la apuesta, ni el grado 020 (can_decide_H=False).
No usa nombres propios ni años: solo ids de corte, ejes, tokens del input y familias del catálogo 244.
No lee el futuro: solo los cortes que entraron al freeze. No modifica Engine_V5 ni patterns_final_v14.json.

A) Fórmula (misma forma que la Fórmula 22 del Engine canónico, P_final, con F_h en lugar de P):
     F_h      = rank_fusion_h / techo_rank            (fracción del máximo aritmético; PATCH02)
     pred_h   = (1 - dmin_Z - sigma_Z) * F_h + dmin_Z * 0.5 + sigma_Z * E[P_azar]     con E[P_azar] = 0.5
     dmin_Z   = delta_min_base + (delta_min_max - delta_min_base) * media(1 - w)   (marcadores del corte Z)
     sigma_Z  = desviación estándar poblacional de (1 - w) en el corte Z
   Constantes leídas del Engine canónico (firma de TracingEngine.__init__); si no se puede, 0.1 / 0.25.
   Base (piso) = (dmin_Z + sigma_Z) * 0.5 > 0 ; techo = 1 - (dmin_Z + sigma_Z) * 0.5 < 1  -> nunca llega a 100 %.
   Contribución de cada componente k (dimensión ordinal o señal lateral) en puntos porcentuales:
     pp_k = 100 * (1 - dmin_Z - sigma_Z) * s_k(h) / techo_rank ,  s_k en [0,1] = fracción de su máximo
   y  100 * pred_h = base_pp + suma_k pp_k  (exacto salvo redondeo).
   Es PREDICTIBILIDAD ESTRUCTURAL (soporte interno relativo a las candidatas), no probabilidad calibrada del desenlace.
"""
from __future__ import annotations
import importlib.util, inspect, math, statistics
from pathlib import Path
from typing import Any, Dict, List

VERSION = "PREDICTIBILIDAD_SET_021_20261011"
THETA_COBERTURA = 0.90      # suficiencia: el set debe cubrir >= 90 % de la masa de evidencia que cubren todas las publicadas
P_INDET = 0.5
E_P_AZAR = 0.5


def _num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(float(x))


def _cal_group(k):  # mismo agrupamiento que PATCH03 en _predict
    if k in {"state", "continuity", "delta", "axis_convergence", "own_pattern_evidence"}: return "trayectoria_estado"
    for p, g in (("booker_", "booker"), ("greimas_", "greimas"), ("frye_", "frye"), ("coupling_", "acoplamiento"),
                 ("structural_", "estructura"), ("dynamis_", "dynamis"), ("resolution_", "resolucion"), ("geometric_", "geometria_inercia")):
        if k.startswith(p): return g
    return "otras_dimensiones"


def constantes_engine(base: Path) -> Dict[str, Any]:
    out = {"delta_min_base": 0.1, "delta_min_max": 0.25, "fuente": "DEFECTO_DOCUMENTADO_ANTECEDENTE_TURING_V1"}
    try:
        spec = importlib.util.spec_from_file_location("eng_const_021", str(Path(base) / "Engine_V5_CANONICO_SOLO.py"))
        m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        ps = inspect.signature(m.TracingEngine.__init__).parameters
        out = {"delta_min_base": float(ps["delta_min_base"].default), "delta_min_max": float(ps["delta_min_max"].default),
               "fuente": "Engine_V5_CANONICO_SOLO.py: firma de TracingEngine.__init__ (solo lectura)"}
    except Exception as e:  # pragma: no cover
        out["error_lectura"] = f"{type(e).__name__}"
    return out


def incertidumbre_Z(cut: Dict[str, Any], const: Dict[str, Any]) -> Dict[str, Any]:
    """dmin y sigma como los calcula process_observation del Engine canónico, por eje del corte Z; se promedian los ejes con marcadores."""
    por_eje = {}
    for e in ("P", "A", "C"):
        u = [1.0 - max(0.0, min(1.0, float(p[1]))) for p in (cut.get(e) or []) if isinstance(p, (list, tuple)) and len(p) >= 2 and _num(p[1])]
        if not u: continue
        dh = sum(u) / len(u); sg = statistics.pstdev(u) if len(u) >= 2 else 0.0
        por_eje[e] = {"n_marcadores": len(u), "delta_h_t": round(dh, 6), "sigma_sorpresa_t": round(sg, 6),
                      "delta_min_t": round(const["delta_min_base"] + (const["delta_min_max"] - const["delta_min_base"]) * dh, 6)}
    if not por_eje:
        return {"delta_min_Z": const["delta_min_base"], "sigma_Z": 0.0, "por_eje": {}, "nota": "corte Z sin marcadores: se usa delta_min_base"}
    dm = sum(v["delta_min_t"] for v in por_eje.values()) / len(por_eje)
    sg = sum(v["sigma_sorpresa_t"] for v in por_eje.values()) / len(por_eje)
    return {"delta_min_Z": round(dm, 6), "sigma_Z": round(sg, 6), "por_eje": por_eje,
            "regla": "promedio sobre los ejes del corte Z con marcadores; fórmulas de process_observation (Engine canónico)"}


def _frac_scores(vals: Dict[str, float]) -> Dict[str, float]:
    orden = sorted(vals.items(), key=lambda z: -z[1]); N = len(orden); out = {}; i = 0
    while i < N:
        j = i
        while j + 1 < N and abs(orden[j + 1][1] - orden[i][1]) <= 1e-9: j += 1
        for t in range(i, j + 1): out[orden[t][0]] = 1.0 - ((i + j) / 2.0) / max(1, N - 1)
        i = j + 1
    return out


# ---------------------------------------------------------------- A) escala
# Reconexión v2.A.1 (2026-11-11): el "no" del Décimo Hombre y la dirección del
# cuadrante del monomito alimentan la predictibilidad. Antes iban a la nada
# (el contador_supervivencia no lo leía nadie; el cuadrante solo se contaba).
# NO cambia la Fórmula 22 original (predictibilidad_estructural_0_1 queda
# intacta para comparar); añade la variante ajustada por hipótesis.
ORDEN_CUADRANTES = ['Q1_Separacion_1_3', 'Q2_Descenso_4_6', 'Q3_Ordeal_7_9', 'Q4_Retorno_10_12']


def _ajuste_reconexion(result):
    """Por familia: dh_frac (supervivencia en contrafactuales del DH, 0-1) y
    dir_norm (alineación con la dirección del cuadrante, 0-1). ajuste es la
    media; factor = 0.5 + 0.5*ajuste, en [0.5, 1.0]. Si falta el dato, None
    (factor 1.0: la ajustada es igual a la original)."""
    dh = (result.get("decimo_hombre_esteroides") or {})
    sup = dh.get("contador_supervivencia") or {}
    cfs = dh.get("contrafactuales_ejecutados") or []
    n_cf = len(cfs) if cfs else 0
    mono = ((result.get("features") or {}).get("plugin_circulo_monomito") or {}).get("posicion_monomito_por_corte") or []
    cp = ((result.get("motor") or {}).get("annex") or {}).get("traza_P") or {}
    crudo = cp.get("crudo_P") or {}
    q = [(f.get("cuadrante_activo") or [None])[0] for f in mono]
    seq = [x for x in q if x]
    actual = seq[-1] if seq else None
    siguiente = ORDEN_CUADRANTES[(ORDEN_CUADRANTES.index(actual) + 1) % 4] if actual in ORDEN_CUADRANTES else None
    ia = [i for i, x in enumerate(q) if x == actual]
    ib = [i for i, x in enumerate(q) if x == siguiente]
    out = {"cuadrante_actual": actual, "cuadrante_siguiente": siguiente,
           "n_contrafactuales": n_cf, "dh_disponible": bool(sup and n_cf),
           "cuadrante_disponible": bool(actual and siguiente and ia and ib), "por_familia": {}}
    fams = set(sup.keys()) | set(crudo.keys())
    for fam in fams:
        dh_frac = (float(sup.get(fam, 0)) / n_cf) if (sup and n_cf) else None
        dir_delta = None; dir_norm = None
        ps = crudo.get(fam) or []
        if actual and siguiente and ia and ib and ps and len(ps) >= max(ia + ib) + 1:
            m_a = sum(ps[i] for i in ia) / len(ia)
            m_b = sum(ps[i] for i in ib) / len(ib)
            dir_delta = m_b - m_a
            dir_norm = max(0.0, min(1.0, 0.5 + dir_delta * 5.0))
        partes = [x for x in (dh_frac, dir_norm) if x is not None]
        ajuste = (sum(partes) / len(partes)) if partes else None
        factor = (0.5 + 0.5 * ajuste) if ajuste is not None else 1.0
        out["por_familia"][fam] = {"dh_supervivencia_frac": dh_frac,
                                   "direccion_cuadrante_delta": dir_delta,
                                   "direccion_cuadrante_norm": dir_norm,
                                   "ajuste_reconexion": ajuste, "factor_reconexion": round(factor, 6)}
    return out


def escala_predictibilidad(result: Dict[str, Any], case: Dict[str, Any], base: Path) -> Dict[str, Any]:
    recon = _ajuste_reconexion(result)
    pred = result.get("predictor") or {}
    cands = [c for c in (pred.get("candidates") or []) if isinstance(c, dict) and c.get("family")]
    dims = list(pred.get("dimensions") or [])
    T = float(pred.get("techo_rank") or 0) or float(len(dims) + max((len((c.get("features") or {}).get("lateral_signal_contributions") or {}) for c in cands), default=0))
    aportes = pred.get("aporte_por_dimension_021") or {}
    fuente_aportes = "predictor.aporte_por_dimension_021 (rangos fraccionales sobre las N candidatas de la fusión)"
    if not all(c["family"] in aportes for c in cands):
        fuente_aportes = "RECALCULADO_SOLO_SOBRE_PUBLICADAS (el predictor no expuso aporte_por_dimension_021)"
        aportes = {c["family"]: {} for c in cands}
        for k in dims:
            if all(_num((c.get("features") or {}).get(k)) for c in cands):
                sc = _frac_scores({c["family"]: float(c["features"][k]) for c in cands})
                for n in sc: aportes[n][k] = sc[n]
    const = constantes_engine(base)
    cuts = case.get("cuts") or []
    inc = incertidumbre_Z(cuts[-1] if cuts else {}, const)
    dm, sg = float(inc["delta_min_Z"]), float(inc["sigma_Z"])
    K = max(0.0, 1.0 - dm - sg)
    base_pp = 100.0 * (dm * P_INDET + sg * E_P_AZAR)
    techo_pp = 100.0 * K + base_pp
    mboards = ((result.get("motor") or {}).get("cuts") or [{}])[-1]
    sat = {}
    for e in ("P", "A", "C"):
        b = mboards.get(f"{e}_FULL_244") or {}
        if b:
            mx = max(b.values()); sat[e] = {"max_p_final": mx, "familias_empatadas_en_el_max": sum(1 for v in b.values() if abs(v - mx) <= 1e-9),
                                          "familias_en_0_5": sum(1 for v in b.values() if abs(v - 0.5) <= 1e-9), "n": len(b)}
    por_h = {}
    for c in cands:
        n = c["family"]; f = c.get("features") or {}
        rows = []
        for k in dims:
            s = float((aportes.get(n) or {}).get(k, 0.0))
            rows.append({"componente": k, "tipo": "dimension_ordinal", "grupo": _cal_group(k),
                         "valor_bruto": round(float(f[k]), 6) if _num(f.get(k)) else "NO_NUMERICO",
                         "aporte_0_1": round(s, 6), "pp": round(100.0 * K * s / T, 4) if T else 0.0})
        for sig, v in sorted((f.get("lateral_signal_contributions") or {}).items()):
            s = float(v) if _num(v) else 0.0
            rows.append({"componente": sig, "tipo": "senal_lateral", "grupo": "puente_lateral", "valor_bruto": round(s, 6),
                         "aporte_0_1": round(s, 6), "pp": round(100.0 * K * s / T, 4) if T else 0.0})
        suma_rangos = sum(r["aporte_0_1"] for r in rows)
        rf = float(c.get("rank_fusion") or 0.0)
        F = rf / T if T else 0.0
        p = K * F + base_pp / 100.0
        grupos = {}
        for r in rows:
            g = grupos.setdefault(r["grupo"], {"pp": 0.0, "aporte": 0.0, "maximo": 0})
            g["pp"] += r["pp"]; g["aporte"] += r["aporte_0_1"]; g["maximo"] += 1
        for g in grupos.values():
            g["pp"] = round(g["pp"], 4); g["aporte"] = round(g["aporte"], 6); g["fraccion_de_su_maximo"] = round(g["aporte"] / g["maximo"], 6) if g["maximo"] else 0.0
        top = sorted(rows, key=lambda r: (-r["pp"], r["componente"]))
        old = {e: (mboards.get(f"{e}_FULL_244") or {}).get(n, "NO_EN_244") for e in ("P", "A", "C")}
        aj = (recon.get("por_familia") or {}).get(n) or {}
        factor = float(aj.get("factor_reconexion") or 1.0)
        p_aj = K * F * factor + base_pp / 100.0
        por_h[n] = {"rank_fusion": round(rf, 6), "F_fraccion_del_techo": round(F, 6),
                    "predictibilidad_estructural_0_1": round(p, 6), "predictibilidad_estructural_pct": round(100.0 * p, 2),
                    "predictibilidad_estructural_ajustada_0_1": round(p_aj, 6),
                    "predictibilidad_estructural_ajustada_pct": round(100.0 * p_aj, 2),
                    "dh_supervivencia_frac": aj.get("dh_supervivencia_frac"),
                    "direccion_cuadrante_delta": (round(aj["direccion_cuadrante_delta"], 6) if aj.get("direccion_cuadrante_delta") is not None else None),
                    "direccion_cuadrante_norm": aj.get("direccion_cuadrante_norm"),
                    "ajuste_reconexion": aj.get("ajuste_reconexion"),
                    "factor_reconexion": round(factor, 6),
                    "base_pp": round(base_pp, 4), "suma_pp_componentes": round(sum(r["pp"] for r in rows), 4),
                    "cuadra_rank_fusion": abs(suma_rangos - rf) <= 1e-4, "suma_aportes_recalculada": round(suma_rangos, 6),
                    "top_componentes": [{"componente": r["componente"], "grupo": r["grupo"], "pp": r["pp"], "aporte_0_1": r["aporte_0_1"]} for r in top[:6]],
                    "componentes_en_cero": [r["componente"] for r in rows if r["aporte_0_1"] <= 1e-12],
                    "por_grupo": grupos, "tabla_componentes": rows,
                    "soporte_canonico_p_final_en_Z": old}
    return {"version": VERSION, "nombre": "predictibilidad estructural (soporte interno)",
            "es_probabilidad_calibrada": False, "es_porcentaje_de_acierto": False,
            "formula": "pred = (1 - dmin_Z - sigma_Z) * rank_fusion/techo_rank + dmin_Z*0.5 + sigma_Z*E[P_azar]; E[P_azar]=0.5 (Fórmula 22 del Engine canónico con F en lugar de P). Variante ajustada (reconexión v2.A.1): pred_ajustada = K * F * factor_reconexion + base_pp/100, factor = 0.5 + 0.5*ajuste, ajuste = media(dh_supervivencia_frac, direccion_cuadrante_norm); la original queda intacta para comparar.",
            "reconexion_v2a1": {"cuadrante_actual": recon.get("cuadrante_actual"),
                                "cuadrante_siguiente": recon.get("cuadrante_siguiente"),
                                "n_contrafactuales": recon.get("n_contrafactuales"),
                                "dh_disponible": recon.get("dh_disponible"),
                                "cuadrante_disponible": recon.get("cuadrante_disponible"),
                                "nota": "El 'no' del DH (contador_supervivencia) y la dirección del cuadrante del monomito alimentan la predictibilidad ajustada; la Fórmula 22 original no cambia."},
            "techo_rank": T, "delta_min_Z": dm, "sigma_Z": sg, "peso_evidencia_K": round(K, 6),
            "base_pp": round(base_pp, 4), "techo_pp": round(techo_pp, 4),
            "pp_por_punto_de_rank_fusion": round(100.0 * K / T, 6) if T else 0.0,
            "incertidumbre_Z": inc, "constantes_engine": const, "fuente_aportes": fuente_aportes,
            "saturacion_tablero_canonico_en_Z": sat,
            "lectura": "F es posición relativa entre las candidatas (rango fraccional por dimensión), no soporte absoluto; la base y el techo vienen de la incertidumbre del corte Z como en P_final",
            "calibracion": "ACTIVA_CON_DESENLACES_SELLADOS: hay pares (predictibilidad sellada antes de t+1, desenlace observado) por caso en el StinkBox; calibracion_predictiva_v1 (Brier/log-loss/ECE/Platt) disponible con >= 20 filas",
            "por_hipotesis": por_h}


# ---------------------------------------------------------------- C) paso inverso (hipótesis -> cortes)
def _items(case):
    out = []
    for i, c in enumerate(case.get("cuts") or []):
        cid = str(c.get("id") or c.get("corte") or f"C{i+1}")
        for e in ("P", "A", "C"):
            for p in c.get(e) or []:
                if isinstance(p, (list, tuple)) and len(p) >= 2 and _num(p[1]):
                    out.append({"corte": cid, "idx": i, "eje": e, "token": str(p[0]), "w": float(p[1])})
    return out


def paso_inverso(case, cands, patterns, eje):
    items = _items(case)
    cortes = []
    for it in items:
        if it["corte"] not in cortes: cortes.append(it["corte"])
    por_h = {}
    for n in cands:
        pv = patterns.get(n) or {}
        fav = set(pv.get("tokens_favor") or {}); con = set(pv.get("tokens_contra") or {})
        filas = []; expl = set(); contra = set()
        for cid in cortes:
            its = [x for x in items if x["corte"] == cid]
            ef = [x for x in its if x["token"] in fav]; ec = [x for x in its if x["token"] in con]
            mf = sum(x["w"] for x in ef); mc = sum(x["w"] for x in ec); mt = sum(x["w"] for x in its)
            if mf <= 0 and mc <= 0: est = "NO_EXPLICA"
            elif mc > mf: est = "CONTRADICE"
            elif mc > 0: est = "EXPLICA_CON_CONTRA"
            else: est = "EXPLICA"
            for x in ef: expl.add((x["corte"], x["eje"], x["token"]))
            for x in ec: contra.add((x["corte"], x["eje"], x["token"]))
            filas.append({"corte": cid, "estado": est, "masa_explicada": round(mf, 4), "masa_contra": round(mc, 4), "masa_corte": round(mt, 4),
                          "fraccion_explicada": round(mf / mt, 4) if mt else 0.0,
                          "tokens_explicados": [[x["eje"], x["token"], x["w"]] for x in ef],
                          "tokens_en_contra": [[x["eje"], x["token"], x["w"]] for x in ec],
                          "tokens_no_explicados": [[x["eje"], x["token"], x["w"]] for x in its if x not in ef and x not in ec]})
        por_h[n] = {"en_catalogo_244": n in patterns, "cortes": filas, "_expl": expl, "_contra": contra,
                    "cortes_explicados": [f["corte"] for f in filas if f["estado"] in ("EXPLICA", "EXPLICA_CON_CONTRA")],
                    "cortes_sin_explicar": [f["corte"] for f in filas if f["estado"] == "NO_EXPLICA"],
                    "cortes_que_contradice": [f["corte"] for f in filas if f["estado"] == "CONTRADICE"],
                    "masa_explicada": round(sum(f["masa_explicada"] for f in filas), 4),
                    "masa_total_input": round(sum(x["w"] for x in items), 4)}
    W = {(x["corte"], x["eje"], x["token"]): x["w"] for x in items}
    def mass(s): return sum(W[k] for k in s)
    E = por_h.get(eje, {}).get("_expl", set())
    for n, h in por_h.items():
        h["fraccion_cortes_explicados"] = round(len(h["cortes_explicados"]) / len(cortes), 4) if cortes else 0.0
        if n == eje:
            h["acero_inverso_vs_eje"] = "ES_EL_EJE"; continue
        R = h["_expl"]
        solo_R = R - E; solo_E = E - R
        cortes_E = set(por_h[eje]["cortes_explicados"]) if eje in por_h else set()
        cortes_R_no_E = [c for c in h["cortes_explicados"] if c not in cortes_E]
        if R == E: ver = "EQUIVALENTE_AL_EJE"
        elif E < R: ver = "SUBSUME_AL_EJE"
        elif R <= E: ver = "REDUNDANTE_CON_EJE"
        else: ver = "COMPLEMENTA_AL_EJE"
        h["acero_inverso_vs_eje"] = {
            "regla": "mejor versión honesta del rival: todo lo que el rival explica del input que el eje no explica, y lo que el eje sostiene solo",
            "veredicto": ver, "masa_que_explica_y_el_eje_no": round(mass(solo_R), 4), "masa_que_el_eje_explica_y_el_rival_no": round(mass(solo_E), 4),
            "tokens_que_explica_y_el_eje_no": sorted([list(k) for k in solo_R]),
            "cortes_que_explica_y_el_eje_deja_sin_explicar": cortes_R_no_E}
    return por_h, cortes, W


# ---------------------------------------------------------------- B) set necesario y suficiente
def set_necesario_suficiente(result, case, patterns, escala, theta=THETA_COBERTURA):
    pred = result.get("predictor") or {}; cf = result.get("cierre_final") or {}
    cands = [c["family"] for c in (pred.get("candidates") or []) if isinstance(c, dict) and c.get("family")]
    rf = {c["family"]: float(c.get("rank_fusion") or 0.0) for c in (pred.get("candidates") or []) if isinstance(c, dict) and c.get("family")}
    if not cands:
        return {"status": "SIN_CANDIDATAS"}, {}
    eje = cf.get("H1") if cf.get("H1") in cands else cands[0]
    banda = cf.get("banda_casi_igualdad") or {}
    banda_eje = [eje]
    for g in banda.get("grupos_casi_igualdad") or []:
        if eje in (g.get("miembros_orden_rank_fusion") or []):
            banda_eje = [eje] + [m for m in g.get("orden_final") or g.get("miembros_orden_rank_fusion") or [] if m != eje]
    inv, cortes, W = paso_inverso(case, cands, patterns, eje)
    def mass(s): return sum(W[k] for k in s)
    def cov(S):
        u = set()
        for n in S: u |= inv[n]["_expl"]
        return u
    U = cov(cands); MU = mass(U); MT = sum(W.values())
    S = list(banda_eje); motivo = {eje: "eje (H1 del orden del motor, cierre 020)"}
    for m in banda_eje[1:]: motivo[m] = "en banda de casi igualdad con el eje (no separada a la resolución del motor)"
    pasos = []
    while MU > 0 and mass(cov(S)) < theta * MU - 1e-12:
        rest = [n for n in cands if n not in S]
        if not rest: break
        gain = {n: mass(inv[n]["_expl"] - cov(S)) for n in rest}
        best = max(rest, key=lambda n: (gain[n], -cands.index(n)))
        if gain[best] <= 0: break
        S.append(best); motivo[best] = f"suficiencia: mayor cobertura marginal ({round(gain[best],4)} de masa)"
        pasos.append({"agrega": best, "masa_marginal": round(gain[best], 4), "cobertura_tras": round(mass(cov(S)) / MU, 4)})
    def cortes_expl(S):
        s = set()
        for n in S: s |= set(inv[n]["cortes_explicados"])
        return s
    for cid in cortes:
        if cid in cortes_expl(S): continue
        cand_c = [(n, next(f["masa_explicada"] for f in inv[n]["cortes"] if f["corte"] == cid)) for n in cands if n not in S and cid in inv[n]["cortes_explicados"]]
        if cand_c:
            best = max(cand_c, key=lambda z: (z[1], -cands.index(z[0])))[0]
            S.append(best); motivo[best] = f"cobertura única: explica el corte {cid} que ningún miembro explica"
            pasos.append({"agrega": best, "corte_unico": cid})
    podados = []
    for n in list(reversed(S)):
        if n == eje or n in banda_eje: continue
        S2 = [m for m in S if m != n]
        if mass(cov(S2)) >= theta * MU - 1e-12 and cortes_expl(S2) >= cortes_expl(S):
            S = S2; podados.append({"quita": n, "motivo": "redundante: sin él se mantiene la suficiencia y ningún corte queda sin explicar"}); motivo.pop(n, None)
    S = sorted(S, key=lambda n: (n != eje, cands.index(n)))
    suma_rf = sum(rf[n] for n in S) or 1.0
    ph = escala.get("por_hipotesis") or {}
    miembros = []
    for n in S:
        otros = cov([m for m in S if m != n])
        uni = inv[n]["_expl"] - otros
        cort_otros = cortes_expl([m for m in S if m != n])
        miembros.append({"familia": n, "rol": "eje" if n == eje else "componente", "en_banda_con_eje": n in banda_eje and n != eje,
                         "orden_motor": cands.index(n) + 1, "rank_fusion": round(rf[n], 6),
                         "peso_en_set": round(rf[n] / suma_rf, 6),
                         "predictibilidad_estructural_pct": (ph.get(n) or {}).get("predictibilidad_estructural_pct", "NO_CALCULADA"),
                         "cobertura_propia_frac": round(mass(inv[n]["_expl"]) / MU, 4) if MU else 0.0,
                         "cobertura_unica_masa": round(mass(uni), 4), "cobertura_unica_frac": round(mass(uni) / MU, 4) if MU else 0.0,
                         "tokens_unicos": sorted([list(k) for k in uni]),
                         "cortes_unicos": [c for c in inv[n]["cortes_explicados"] if c not in cort_otros],
                         "cortes_explicados": inv[n]["cortes_explicados"], "motivo_inclusion": motivo.get(n, "")})
    excluidas = []
    for n in cands:
        if n in S: continue
        a = inv[n].get("acero_inverso_vs_eje")
        excluidas.append({"familia": n, "orden_motor": cands.index(n) + 1, "aporte_marginal_masa": round(mass(inv[n]["_expl"] - cov(S)), 4),
                          "acero_inverso": a.get("veredicto") if isinstance(a, dict) else a,
                          "motivo": "no necesaria: lo que explica ya lo explica el set (o aporta < umbral) y no cubre ningún corte sin explicar"})
    ce = cortes_expl(S); sin = [c for c in cortes if c not in ce]
    subsume = [n for n in cands if n != eje and isinstance(inv[n].get("acero_inverso_vs_eje"), dict) and inv[n]["acero_inverso_vs_eje"]["veredicto"] == "SUBSUME_AL_EJE"]
    eje_cortes = len(inv[eje]["cortes_explicados"])
    grado = ("SET_EXPLICA_TODOS_LOS_CORTES" if not sin else "SET_CON_CORTES_SIN_EXPLICAR")
    set_out = {"version": VERSION, "status": "CALCULADO", "can_decide_H": False, "reordena": False,
               "criterio": {"theta_cobertura": theta,
                            "regla": "S = eje (H1 del motor) + candidatas en su banda de casi igualdad (020); se agrega por mayor cobertura marginal de evidencia (masa de tokens del input explicados por tokens_favor del 244) hasta cubrir >= theta de lo que cubren todas las publicadas; se agrega toda candidata que explique un corte que ningún miembro explica; se poda (fuera de banda) quien sea redundante. No son excluyentes: el eje gana el orden; los demás son componentes.",
                            "unidad_cobertura": "masa = suma de pesos del input (corte, eje, token) que caen en tokens_favor de la familia"},
               "eje": eje, "n": len(S), "miembros": miembros, "excluidas": excluidas, "pasos": pasos, "podados": podados,
               "cobertura_set_frac_de_lo_cubrible": round(mass(cov(S)) / MU, 4) if MU else 0.0,
               "cobertura_set_frac_del_input": round(mass(cov(S)) / MT, 4) if MT else 0.0,
               "cubrible_por_todas_frac_del_input": round(MU / MT, 4) if MT else 0.0,
               "cortes_explicados_por_set": [c for c in cortes if c in ce], "cortes_sin_explicar_por_set": sin,
               "grado_inverso": {"estado": grado, "autonomia_eje_frac_cortes": round(eje_cortes / len(cortes), 4) if cortes else 0.0,
                                  "rivales_que_subsumen_al_eje": subsume,
                                  "senal_contraria": bool(subsume),
                                  "nota": "gradúa el set; no cambia el grado 020 ni el orden"},
               "H1_H2_compatibilidad": {"H1": cf.get("H1"), "H2": cf.get("H2"), "H2_en_set": cf.get("H2") in S}}
    return set_out, inv


def run(case: Dict[str, Any], result: Dict[str, Any], base, patterns: Dict[str, Any]) -> Dict[str, Any]:
    base = Path(base)
    esc = escala_predictibilidad(result, case, base)
    st, inv = set_necesario_suficiente(result, case, patterns, esc)
    if st.get("status") == "CALCULADO":
        st1, _ = set_necesario_suficiente(result, case, patterns, esc, theta=1.0)
        st["variante_theta_1_0_solo_traza"] = {"miembros": [m["familia"] for m in st1.get("miembros") or []], "n": st1.get("n"),
                                               "nota": "con theta=1.0 entra toda candidata con evidencia propia que el resto no cubre (decisión de Mj)"}
    cf = result.get("cierre_final") or {}
    banda = cf.get("banda_casi_igualdad") or {}
    alt = []
    for g in banda.get("grupos_casi_igualdad") or []:
        mem = [m for m in (g.get("orden_final") or []) if m in inv]
        if len(mem) < 2: continue
        orden_inv = sorted(mem, key=lambda m: (-inv[m]["masa_explicada"], mem.index(m)))
        alt.append({"posiciones": g.get("posiciones_rank_fusion"), "orden_020": mem, "orden_si_el_inverso_desempatara": orden_inv,
                    "cambiaria": orden_inv != mem, "aplicado": False})
    inv_pub = {}
    for n, h in inv.items():
        inv_pub[n] = {k: v for k, v in h.items() if not k.startswith("_")}
        inv_pub[n]["en_set"] = any(m["familia"] == n for m in st.get("miembros") or [])
    ctx = case.get("contexto_rol") if isinstance(case.get("contexto_rol"), dict) else {}
    return {"version": VERSION, "can_decide_H": False, "reordena": False, "writes_canonical": False,
            "momento": "post-freeze (cortes <= Z), después del cierre 020 y del Décimo Hombre",
            "predictibilidad": esc, "hipotesis_necesarias_suficientes": st,
            "paso_inverso": {"regla": "desde cada hipótesis publicada de vuelta a cada corte: tokens del input que explica (tokens_favor 244), que la contradicen (tokens_contra) y que deja sin explicar; acero inverso de cada rival frente al eje",
                             "por_hipotesis": inv_pub, "desempate_inverso_en_banda_solo_traza": alt},
            "contexto_rol": {"recibido": bool(ctx), "oficio": ctx.get("oficio", "NO_SUMINISTRADO"),
                             "entra_al_puntaje": False, "uso": "solo condiciona la interpretación en la capa de traducción (fuera del motor)"}}
