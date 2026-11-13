#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""vinculacion.py — Lateral: CONTRATO DE VINCULACIÓN de tokens.

Pedido de Mj (2026-11-12 ~21:17 CST): encontrar la forma en la que se
vinculan los tokens. Los tokens flotan: a veces un token es una cosa y
a veces otra, o está superpuesto en dos estados al mismo tiempo; todo
es cíclico, así que al final van a seguir estando allá; lo que falta es
la forma de la vinculación para que haya entendimiento. La ecuación o
el contrato de cómo se vinculan, de qué manera y bajo qué criterios,
como el de no-duplicación, en relación a los tokens de la familia con
la que interactúan, y que dé pauta hacia dónde se podría desplazar la
trayectoria (hacia qué otras familias).

EL CONTRATO (V1_20261112) — en palabras y en fórmula:

Sea t un token, c un corte, w(t,c) su peso de entrada en c (máximo
sobre los ejes P/A/C), F(t) sus familias favor, C(t) sus familias
contra, y w_f(t,f) / w_c(t,f) los pesos favor/contra del catálogo.

1. VINCULACIÓN token↔token en un corte c:
   V(t1,t2,c) = Σ_{f ∈ F(t1)∩F(t2)} mín(w_f(t1,f), w_f(t2,f))
   si t1 y t2 co-ocurren en c; 0 si no co-ocurren.
   Existe vínculo ⇔ V > 0. Un vínculo sin familia compartida no
   existe; un vínculo sin co-ocurrencia en el corte no se activa
   ese corte (aunque el solape estructural J = |F(t1)∩F(t2)| /
   |F(t1)∪F(t2)| sea > 0: J es estructural, V es lo que se activa).
   Solo favor: el contra no vincula tokens entre sí en esta versión.

2. VINCULACIÓN token↔familia:
   - Estructural: t→f para todo f ∈ F(t) (favor) y t→f para todo
     f ∈ C(t) (contra, signo opuesto).
   - RESUELTO en c: la asignación por compañía del lateral de
     no-duplicación (_asignar) da (f, "favor") o (f, "contra"):
     el vínculo t↔f se resuelve en c (motivos "unica" o
     "por_compania").
   - SUPERPOSICIÓN en c: la asignación da latencia
     ("latencia_sin_compania" / "latencia_empate" y sus variantes
     contra): el token queda en SUPERPOSICIÓN sobre F(t) (o C(t)):
     está vinculado a varias familias a la vez, en dos o más
     estados al mismo tiempo. ESO ES el frente de latencia.
   - Vector de vínculo del token en c (masa conservada: la masa
     total del token en c es w(t,c); no se crea ni se destruye
     vínculo, se reparte o se transfiere):
       L_t(c)[f] = +w(t,c)                                   si resuelto favor a f
                 = -w(t,c)                                   si resuelto contra a f
                 = +w(t,c)·w_f(t,f)/Σ_{g∈F(t)} w_f(t,g)       si superposición favor
                 = -w(t,c)·w_c(t,f)/Σ_{g∈C(t)} w_c(t,g)       si superposición contra
                 = 0                                         en otro caso
     Un token sin familia es inerte (vector cero), igual que en el
     canónico.

3. DESPLAZAMIENTO entre cortes:
   L(c) = Σ_t L_t(c)   (vector de vínculo agregado del corte)
   Δ(c→c+1) = L(c+1) − L(c)
   La dirección del desplazamiento sobre un tramo T es
   argmáx_f Σ_{c→c+1 ∈ T} Δ[f]: la familia que más vínculo GANA.
   La pauta: si en los últimos cortes un token (o un grupo) gana
   vínculo con la familia F, la trayectoria se desplaza hacia F.
   El desplazamiento es FLUJO (cambio de masa de vínculo), no
   stock (p_final): incluye que un token entre o salga del corte.

4. CÍCLICO: un vínculo puede volver. Para cada par (t,f) se
   registra la serie L_t(c)[f] por corte:
   - RETORNO: un cambio de sentido pérdida→ganancia en Δ_t[f]
     (el vínculo bajó y luego volvió a subir).
   - REAPARICIÓN: L_t(c)[f] = 0 y L_t(c+1)[f] ≠ 0 habiendo sido
     ≠ 0 en algún corte anterior (el vínculo salió y volvió).
   - VÍNCULO RESUELTO RECUPERADO: t resuelto a f, luego deja de
     estarlo, luego vuelve a resolverse a f.

Puerta de cordura: la clasificación resuelto/superposición de este
lateral usa _asignar del lateral de no-duplicación (importado, no
copiado). La contabilidad de frentes se reimplementa aquí; la puerta
exige reproducir los frentes de no_duplicacion_resultado.json por
caso (abiertos y resueltos). Si no reproduce, la maquinaria está
mal, no el contrato.

Reglas del lateral: can_decide_H=False. No decide H1/H2 del motor;
solo mide vínculos, superposiciones y desplazamientos, y si el
desplazamiento apunta al H1 sombra del C7.
"""
from __future__ import annotations

import importlib.util
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

VERSION = "VINCULACION_TOKENS_V1_20261112"
BASE = Path("/home/hatch/workspace/u6-alterno/motor-cameo")
MOTOR_DIR = BASE / "motor" / "motor"
CASOS_DIR = BASE / "casos" / "precedentes"
RESULTS_DIR = BASE / "motor"
ND_PATH = BASE / "motor" / "reconexion_v2a1" / "no_duplicacion_latencia.py"
ND_RESULTADO = BASE / "motor" / "reconexion_v2a1" / "no_duplicacion_resultado.json"
CASOS = [
    "JUANA_DE_ARCO_HEROE_20261112",
    "TUBMAN_HEROE_20261112",
    "MANDELA_HEROE_20261112",
    "SEMMELWEIS_HEROE_SIN_TRONO_20261112",
    "KOLBE_HEROE_SIN_TRONO_20261112",
]


def _cargar_nd():
    spec = importlib.util.spec_from_file_location("nd_vinc", str(ND_PATH))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _cargar_catalogo_pesos(nd, eng, pl):
    """token -> {'favor': {fam: peso}, 'contra': {fam: peso}} (lectura)."""
    out: Dict[str, Dict[str, Dict[str, float]]] = {}
    for fam, d in pl.patterns.items():
        for t, w in (d.get("tokens_favor") or {}).items():
            out.setdefault(t, {"favor": {}, "contra": {}})["favor"][fam] = float(w)
        for t, w in (d.get("tokens_contra") or {}).items():
            out.setdefault(t, {"favor": {}, "contra": {}})["contra"][fam] = float(w)
    return out


def _pesos_corte(cut: Dict[str, Any]) -> Dict[str, float]:
    """Peso de entrada por token en el corte (máximo sobre P/A/C)."""
    out: Dict[str, float] = {}
    for eje in ("P", "A", "C"):
        for t, w in cut.get(eje) or []:
            out[t] = max(out.get(t, 0.0), float(w))
    return out


def _vinculo_token_token(t1: str, t2: str,
                         pesos: Dict[str, Dict[str, Dict[str, float]]]
                         ) -> Tuple[float, List[str], float]:
    """(fuerza V, familias compartidas, Jaccard estructural). Solo favor."""
    f1 = set((pesos.get(t1) or {}).get("favor", {}))
    f2 = set((pesos.get(t2) or {}).get("favor", {}))
    compartidas = sorted(f1 & f2)
    union = f1 | f2
    jac = (len(f1 & f2) / len(union)) if union else 0.0
    fuerza = 0.0
    for f in compartidas:
        fuerza += min(pesos[t1]["favor"][f], pesos[t2]["favor"][f])
    return fuerza, compartidas, jac


def _vector_vinculo_token(token: str, masa: float,
                          asignacion: Tuple[Optional[str], Optional[str], str],
                          pesos: Dict[str, Dict[str, Dict[str, float]]]
                          ) -> Dict[str, float]:
    """L_t(c): vínculo del token en el corte. Masa conservada = masa."""
    fam, lado, motivo = asignacion
    info = pesos.get(token) or {"favor": {}, "contra": {}}
    if fam is not None:
        return {fam: masa if lado == "favor" else -masa}
    if motivo.startswith("latencia"):
        if "contra" in motivo:
            contra = info["contra"]
            total = sum(contra.values())
            if total <= 0:
                return {}
            return {f: -masa * w / total for f, w in contra.items()}
        favor = info["favor"]
        total = sum(favor.values())
        if total <= 0:
            return {}
        return {f: masa * w / total for f, w in favor.items()}
    return {}  # sin_familia: inerte


def _frentes(entrada: Dict[str, Any], nd,
             fam_por_token) -> List[Dict[str, Any]]:
    """Replica la contabilidad de frentes de no-duplicación:
    un frente por token, se abre en el primer corte con latencia y
    se resuelve en el primer corte posterior con asignación."""
    frentes: List[Dict[str, Any]] = []
    abiertos: Dict[str, Dict[str, Any]] = {}
    for cut in entrada["cuts"]:
        cid = cut["id"]
        cut_pesos = _pesos_corte(cut)
        for t in cut_pesos:
            fam, lado, motivo = nd._asignar(t, cut_pesos, fam_por_token)
            if fam is None:
                if motivo.startswith("latencia") and t not in abiertos:
                    fr = {"token": t, "corte_apertura": cid,
                          "motivo": motivo, "corte_resolucion": None,
                          "familia_resuelta": None}
                    abiertos[t] = fr
                    frentes.append(fr)
                continue
            fr = abiertos.pop(t, None)
            if fr is not None:
                fr["corte_resolucion"] = cid
                fr["familia_resuelta"] = fam
    return frentes


def _serie_retornos(series: List[float]) -> Dict[str, Any]:
    """Analiza la serie L_t(c)[f] por corte: retornos (pérdida→ganancia),
    cambios de sentido, reapariciones (0 → ≠0 habiendo sido ≠0 antes)."""
    deltas = [series[i + 1] - series[i] for i in range(len(series) - 1)]
    signos = [0 if abs(d) < 1e-12 else (1 if d > 0 else -1) for d in deltas]
    retornos = 0
    cambios = 0
    ultimo = 0
    for s in signos:
        if s == 0:
            continue
        if ultimo != 0 and s != ultimo:
            cambios += 1
            if ultimo == -1 and s == 1:
                retornos += 1
        ultimo = s
    reapariciones = 0
    visto_no_cero = False
    for i, v in enumerate(series):
        if abs(v) > 1e-12:
            if i > 0 and abs(series[i - 1]) <= 1e-12 and visto_no_cero:
                reapariciones += 1
            visto_no_cero = True
    return {"retornos": retornos, "cambios_sentido": cambios,
            "reapariciones": reapariciones}


def analizar_caso(nombre: str, nd, eng, pl, fam_por_token,
                  pesos) -> Dict[str, Any]:
    entrada = json.loads((CASOS_DIR / nombre / "entrada.json").read_text(encoding="utf-8"))
    resultado = json.loads((RESULTS_DIR / f"RESULT_{nombre}.json").read_text(encoding="utf-8"))
    nd_res = json.loads(ND_RESULTADO.read_text(encoding="utf-8"))
    ref = next(c for c in nd_res["casos"] if c["caso"] == nombre)
    h1_sombra = ref["h1_sombra"]

    cortes: List[Dict[str, Any]] = []
    vectores: List[Dict[str, float]] = []  # L(c) agregado por corte
    series_token_fam: Dict[Tuple[str, str], List[float]] = defaultdict(list)
    tokens_por_corte: List[List[str]] = []

    for cut in entrada["cuts"]:
        cid = cut["id"]
        cut_pesos = _pesos_corte(cut)
        toks = sorted(cut_pesos)
        tokens_por_corte.append(toks)
        # asignación por (token, corte) — misma maquinaria que no-duplicación
        asignacion = {t: nd._asignar(t, cut_pesos, fam_por_token) for t in toks}
        # --- grafo token↔token del corte ---
        aristas = []
        for i in range(len(toks)):
            for j in range(i + 1, len(toks)):
                fuerza, comp, jac = _vinculo_token_token(toks[i], toks[j], pesos)
                if fuerza > 0:
                    aristas.append({"t1": toks[i], "t2": toks[j],
                                    "fuerza": round(fuerza, 4),
                                    "familias_compartidas": comp,
                                    "jaccard": round(jac, 4)})
        aristas.sort(key=lambda a: (-a["fuerza"], a["t1"], a["t2"]))
        # --- superposición por corte ---
        superposicion = []
        for t in toks:
            fam, lado, motivo = asignacion[t]
            if fam is None and motivo.startswith("latencia"):
                info = pesos.get(t) or {"favor": {}, "contra": {}}
                fams = sorted(info["favor"] if "contra" not in motivo
                              else info["contra"])
                superposicion.append({"token": t, "lado": "favor" if "contra" not in motivo else "contra",
                                      "familias": fams, "motivo": motivo})
        # --- vector de vínculo del corte ---
        vec_corte: Dict[str, float] = defaultdict(float)
        vec_token: Dict[str, Dict[str, float]] = {}
        for t in toks:
            vt = _vector_vinculo_token(t, cut_pesos[t], asignacion[t], pesos)
            vec_token[t] = vt
            for f, v in vt.items():
                vec_corte[f] += v
        vectores.append(dict(vec_corte))
        # registrar series por (token, familia) para el análisis cíclico
        cortes.append({
            "corte": cid,
            "n_tokens": len(toks),
            "n_aristas": len(aristas),
            "fuerza_total": round(sum(a["fuerza"] for a in aristas), 4),
            "fuerza_media": round(sum(a["fuerza"] for a in aristas) / len(aristas), 4) if aristas else 0.0,
            "top_vinculos": aristas[:5],
            "superposicion": superposicion,
            "n_superposicion": len(superposicion),
            "vector_corte": {f: round(v, 4) for f, v in sorted(vec_corte.items(), key=lambda kv: (-abs(kv[1]), kv[0]))[:10]},
        })
        # guardar vectores por token para series y desplazamientos
        cortes[-1]["_vec_token"] = {t: {f: round(v, 4) for f, v in vt.items()}
                                    for t, vt in vec_token.items()}

    # --- series (token, familia) sobre todos los cortes ---
    universo: set = set()
    for c in cortes:
        for t, vt in c["_vec_token"].items():
            for f in vt:
                universo.add((t, f))
    for (t, f) in sorted(universo):
        series_token_fam[(t, f)] = [
            c["_vec_token"].get(t, {}).get(f, 0.0) for c in cortes]
    analisis_ciclico = {}
    total_retornos = 0
    total_cambios = 0
    total_reapariciones = 0
    ejemplos_retorno = []
    for (t, f), serie in series_token_fam.items():
        a = _serie_retornos(serie)
        analisis_ciclico[f"{t} -> {f}"] = {**a, "serie": [round(v, 3) for v in serie]}
        total_retornos += a["retornos"]
        total_cambios += a["cambios_sentido"]
        total_reapariciones += a["reapariciones"]
        if a["retornos"] > 0:
            ejemplos_retorno.append({"token": t, "familia": f, **a,
                                     "serie": [round(v, 3) for v in serie]})
    ejemplos_retorno.sort(key=lambda e: (-e["retornos"], -e["cambios_sentido"],
                                         e["token"], e["familia"]))

    # --- vínculos resueltos recuperados (resuelto a f, se pierde, se recupera) ---
    recuperados = []
    # reconstruir asignación resuelta por (token, corte)
    resuelto_por_corte: List[Dict[str, str]] = []
    for cut in entrada["cuts"]:
        cut_pesos = _pesos_corte(cut)
        resuelto_por_corte.append({
            t: nd._asignar(t, cut_pesos, fam_por_token)[0]
            for t in cut_pesos
            if nd._asignar(t, cut_pesos, fam_por_token)[0] is not None})
    for t in sorted({t for d in resuelto_por_corte for t in d}):
        fams_t = sorted({d[t] for d in resuelto_por_corte if t in d})
        for f in fams_t:
            seq = [d.get(t) == f for d in resuelto_por_corte]
            # patrón True ... False ... True
            if any(seq) and not all(seq):
                idx_true = [i for i, v in enumerate(seq) if v]
                if len(idx_true) >= 2 and max(idx_true) - min(idx_true) >= 2:
                    hueco = any(not seq[i] for i in range(min(idx_true), max(idx_true) + 1))
                    if hueco:
                        recuperados.append({"token": t, "familia": f,
                                            "cortes_resuelto": [entrada["cuts"][i]["id"] for i in idx_true]})

    # --- desplazamientos entre cortes consecutivos ---
    # deltas_full: delta COMPLETO por transición (no truncado); los top-5
    # de cada transición son solo para display. La pauta agrega deltas_full.
    desplazamientos = []
    deltas_full: List[Dict[str, float]] = []
    for i in range(len(vectores) - 1):
        delta: Dict[str, float] = defaultdict(float)
        for f in set(vectores[i]) | set(vectores[i + 1]):
            delta[f] = vectores[i + 1].get(f, 0.0) - vectores[i].get(f, 0.0)
        deltas_full.append(dict(delta))
        gana = sorted(((f, round(v, 4)) for f, v in delta.items() if v > 1e-9),
                      key=lambda kv: (-kv[1], kv[0]))
        pierde = sorted(((f, round(v, 4)) for f, v in delta.items() if v < -1e-9),
                        key=lambda kv: (kv[1], kv[0]))
        desplazamientos.append({
            "transicion": f"{entrada['cuts'][i]['id']} -> {entrada['cuts'][i + 1]['id']}",
            "gana_top": gana[:5], "pierde_top": pierde[:5],
            "argmax_gana": gana[0] if gana else None,
        })

    def _pauta(idxs):
        """Agrega los deltas COMPLETOS de las transiciones en idxs y
        devuelve argmax, top y rango del H1 sombra. idxs son índices de
        transición (0 = C1->C2); se normalizan los negativos."""
        n = len(deltas_full)
        idxs = [i if i >= 0 else n + i for i in idxs]
        agg: Dict[str, float] = defaultdict(float)
        for ix in idxs:
            for f, v in deltas_full[ix].items():
                agg[f] += v
        orden = sorted(agg.items(), key=lambda kv: (-kv[1], kv[0]))
        rango = next((i + 1 for i, (f, _) in enumerate(orden) if f == h1_sombra), None)
        # contribuyentes al argmax en el tramo: cambio por token entre los extremos
        contrib = []
        if orden:
            fam_top = orden[0][0]
            idx0 = idxs[0]        # primer corte del tramo
            idx1 = idxs[-1] + 1   # último corte del tramo
            for t in set(tokens_por_corte[idx0]) | set(tokens_por_corte[idx1]):
                v0 = cortes[idx0]["_vec_token"].get(t, {}).get(fam_top, 0.0)
                v1 = cortes[idx1]["_vec_token"].get(t, {}).get(fam_top, 0.0)
                if abs(v1 - v0) > 1e-9:
                    contrib.append([t, round(v1 - v0, 4)])
            contrib.sort(key=lambda kv: (-kv[1], kv[0]))
        return {
            "argmax_gana": list(orden[0]) if orden else None,
            "top3_gana": [[f, round(v, 4)] for f, v in orden[:3]],
            "delta_h1_sombra": round(agg.get(h1_sombra, 0.0), 4),
            "rango_h1_sombra": rango,
            "acierta": bool(orden and orden[0][0] == h1_sombra),
            "contribuyentes_top_argmax": contrib[:5],
        }

    ultimas_dos = _pauta([-2, -1])
    ultima = _pauta([-1])
    # limpiar claves privadas de los cortes antes de serializar
    for c in cortes:
        c.pop("_vec_token", None)

    # --- puerta de cordura: frentes reproducidos vs no-duplicación ---
    frentes = _frentes(entrada, nd, fam_por_token)
    frentes_abiertos = len(frentes)
    frentes_resueltos = sum(1 for f in frentes if f["corte_resolucion"])
    gate_pasa = (frentes_abiertos == ref["frentes_abiertos"]
                 and frentes_resueltos == ref["frentes_resueltos"])

    # --- prueba secundaria: flujo vs flujo (no flujo vs stock).
    # ¿La familia que más p_final GANA en el tablero sombra P entre C5
    # y C7 es la misma que el argmax del flujo de vínculo? El H1 sombra
    # es un stock (p acumulado); esta prueba compara dos flujos.
    prueba_secundaria = None
    try:
        tab = json.loads((BASE / "motor" / "reconexion_v2a1"
                          / f"sombra_tableros_{nombre}.json").read_text(encoding="utf-8"))
        p5, p7 = tab["boards"]["P"][4], tab["boards"]["P"][6]
        dp = sorted(((f, round(p7[f] - p5[f], 4)) for f in p5),
                    key=lambda kv: (-kv[1], kv[0]))
        rango_p = next((i + 1 for i, (f, _) in enumerate(dp) if f == h1_sombra), None)
        prueba_secundaria = {
            "argmax_ganancia_p": list(dp[0]) if dp else None,
            "top3_ganancia_p": [[f, v] for f, v in dp[:3]],
            "delta_p_h1_sombra": round(p7[h1_sombra] - p5[h1_sombra], 4),
            "rango_p_h1_sombra": rango_p,
            "coincide_con_flujo": bool(dp and ultimas_dos["argmax_gana"]
                                       and dp[0][0] == ultimas_dos["argmax_gana"][0]),
        }
    except Exception as exc:  # noqa: BLE001 - si no hay tableros, se reporta
        prueba_secundaria = {"error": f"{type(exc).__name__}: {exc}"}

    return {
        "caso": nombre,
        "h1_sombra": h1_sombra,
        "p_h1_sombra": ref["p_h1_sombra"],
        "h1_canonico": ref["h1_canonico"],
        "gate": {
            "frentes_referencia": ref["frentes_abiertos"],
            "frentes_reproducidos": frentes_abiertos,
            "resueltos_referencia": ref["frentes_resueltos"],
            "resueltos_reproducidos": frentes_resueltos,
            "gate_pasa": gate_pasa,
            "frentes": frentes,
        },
        "cortes": cortes,
        "desplazamientos": desplazamientos,
        "pauta_ultimas_dos": ultimas_dos,
        "pauta_ultima": ultima,
        "prueba_secundaria_flujo_vs_p": prueba_secundaria,
        "ciclico": {
            "total_retornos": total_retornos,
            "total_cambios_sentido": total_cambios,
            "total_reapariciones": total_reapariciones,
            "pares_token_familia": len(series_token_fam),
            "vinculos_resueltos_recuperados": recuperados,
            "n_vinculos_resueltos_recuperados": len(recuperados),
            "ejemplos_retorno": ejemplos_retorno[:10],
        },
    }


def verificar() -> Dict[str, Any]:
    nd = _cargar_nd()
    eng = nd._cargar_engine()
    pl = eng.PatternLibrary(str(nd.MOTOR_DIR / "patterns_final_v14.json"))
    fam_por_token = nd._familias_por_token(pl)
    pesos = _cargar_catalogo_pesos(nd, eng, pl)
    out: Dict[str, Any] = {"version": VERSION, "casos": []}
    aciertos = 0
    for nombre in CASOS:
        res = analizar_caso(nombre, nd, eng, pl, fam_por_token, pesos)
        out["casos"].append(res)
        if res["pauta_ultimas_dos"]["acierta"]:
            aciertos += 1
        print(f"{nombre}: gate={'PASA' if res['gate']['gate_pasa'] else 'FALLA'} "
              f"frentes {res['gate']['frentes_reproducidos']}/{res['gate']['frentes_referencia']} "
              f"| H1 sombra={res['h1_sombra']} | pauta ult2: argmax={res['pauta_ultimas_dos']['argmax_gana']} "
              f"rango H1={res['pauta_ultimas_dos']['rango_h1_sombra']} "
              f"acierta={res['pauta_ultimas_dos']['acierta']} "
              f"| retornos={res['ciclico']['total_retornos']} "
              f"reapariciones={res['ciclico']['total_reapariciones']}")
    out["prueba_desplazamiento"] = {
        "aciertos_ultimas_dos": aciertos, "de": len(CASOS),
        "aciertos_ultima": sum(1 for c in out["casos"] if c["pauta_ultima"]["acierta"]),
        "aciertos_secundaria_flujo_vs_p": sum(
            1 for c in out["casos"]
            if (c.get("prueba_secundaria_flujo_vs_p") or {}).get("coincide_con_flujo")),
        "por_caso": {c["caso"]: {"h1_sombra": c["h1_sombra"],
                                 "argmax_ult2": c["pauta_ultimas_dos"]["argmax_gana"],
                                 "rango_h1_ult2": c["pauta_ultimas_dos"]["rango_h1_sombra"],
                                 "acierta_ult2": c["pauta_ultimas_dos"]["acierta"],
                                 "argmax_ult1": c["pauta_ultima"]["argmax_gana"],
                                 "acierta_ult1": c["pauta_ultima"]["acierta"]}
                     for c in out["casos"]},
    }
    return out


if __name__ == "__main__":
    data = verificar()
    out_path = Path(__file__).resolve().parent / "vinculacion_resultado.json"
    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("escrito:", out_path)
