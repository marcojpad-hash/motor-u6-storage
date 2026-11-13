#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""no_duplicacion_latencia.py — Lateral: regla de no duplicación con latencia.

Pedido de Mj (2026-11-12 ~19:40 CST): la regla de no duplicación existe
escrita (capa_integracion_semantica_v1_2.py: token_es_unidad,
reaparicion_no_duplica, reaparicion_no_suma_evidencia) pero solo vive
como PROPUESTA / SENSOR y nunca toca el tablero. El Engine canónico
(process_observation) aplica cada marcador a TODAS las familias que lo
listan como favor, sin revisar si ya apoyó a otra. Medido: 84
ocurrencias de tokens -> 203 eventos de apoyo en Juana y Mandela
(x2.42), 169 en Tubman (x2.01), 146 en Semmelweis (x1.74), 140 en
Kolbe (x1.67). Peores: autoridad alimenta 13 familias, sacrificio 9,
liderazgo 6, valentia 3.

Qué hace este lateral (NO toca Engine, ni 244, ni correr_estandar, ni
los RESULT/entradas sellados; solo los LEE):
  1. Tablero sombra: recomputa p_final por familia y corte con la
     regla de actualización del propio Engine — REUTILIZA la clase
     Hypothesis de Engine_V5_CANONICO_SOLO.py (importada, no copiada)
     y PatternLibrary.get_weight para los pesos (incluido el parche
     Cameo de EVIDENCE_MULTIPLIERS). apply_epsilon una vez por
     observación, support()/contradict() por marcador, mismo clamp
     delta_min. delta_min y sigma se recomputan igual que el Engine
     (media y desviación poblacional de 1-confidence de los
     marcadores); p_azar_t NO se inventa: se RECUPERA del RESULT
     sellado por intersección de intervalos sobre las 244 familias
     (p_final redondeado a 4 decimales acota p_azar; el punto medio
     del intervalo reproduce el tablero sellado).
  2. Regla de no duplicación: dentro de un corte, cada ocurrencia de
     token se aplica COMO MUCHO UNA VEZ, a COMO MUCHO UNA familia.
     Asignación por compañía semántica: un token compartido (favor
     en >1 familia) va a la familia cuyos OTROS tokens favor
     (discriminantes: alimentan solo a esa familia) co-ocurren con él
     en ese mismo corte; gana la de más peso de compañía en el corte.
     Empate exacto, o sin compañía discriminante, abre un frente de
     LATENCIA: el token no cuenta para nadie en ese corte y el frente
     se revisa en cortes posteriores (un corte posterior puede
     resolverlo para ESE corte, nunca reescribiendo cortes pasados).
  3. Puerta de cordura (obligatoria): con la regla APAGADA el tablero
     sombra debe reproducir los P_FULL_244 sellados. Si no, la
     maquinaria está mal, no la regla.

Decisiones de diseño (ambigüedades resueltas por cercanía al código
del Engine, documentadas):
  - Contra: el Engine aplica favor y contra de forma independiente.
    La regla dice UNA aplicación por ocurrencia: si el token tiene
    familias favor, la asignación es por compañía favor y solo se
    aplica el apoyo favor (el contra de esa ocurrencia se suprime:
    ya contó una vez). Si no tiene favor pero sí contra, la
    asignación es por compañía contra (misma lógica) y se aplica un
    solo contradict(). Un token sin familia no hace nada (igual que
    en el canónico).
  - Compañía: se mide sobre TODO el corte (P+A+C), no solo el eje
    del token, porque el contexto semántico es el corte. El peso de
    compañía es el peso de entrada del compañero (máximo si aparece
    en varios ejes del mismo corte). La decisión es por (token,
    corte): todas las ocurrencias del token en ese corte van a la
    misma familia o a latencia.
  - delta_min/sigma/p_azar: se calculan sobre la lista COMPLETA de
    marcadores del eje (como los ve el Engine); lo único que cambia
    con la regla es a qué familias apoya cada token. Así el efecto
    medido es solo de la regla.
  - H1/H2 sombra: por p_final sombra en el corte Z (nivel tablero).
    El rank_fusion del motor NO se reimplementa (vive en el pipeline
    de salida_interpretable, no es importable limpio); se dice así
    en el reporte. Se reporta además el p sombra del H1 canónico y
    el rango de las familias héroe y del trono.
  - Cuello top-5: todas las entradas usadas traen <=5 tokens por
    eje, así que es no-op; se verifica con aserción.

Reglas del lateral: can_decide_H=False. No decide H1/H2 del motor;
solo mide qué cambiaría si la regla estuviera encendida.
"""
from __future__ import annotations

import importlib.util
import json
import math
import statistics
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

VERSION = "NO_DUPLICACION_LATENCIA_V1_20261112"
MOTOR_DIR = Path("/home/hatch/workspace/u6-alterno/motor-cameo/motor/motor")
CASOS_DIR = Path("/home/hatch/workspace/u6-alterno/motor-cameo/casos/precedentes")
RESULTS_DIR = Path("/home/hatch/workspace/u6-alterno/motor-cameo/motor")
CASOS = [
    "JUANA_DE_ARCO_HEROE_20261112",
    "TUBMAN_HEROE_20261112",
    "MANDELA_HEROE_20261112",
    "SEMMELWEIS_HEROE_SIN_TRONO_20261112",
    "KOLBE_HEROE_SIN_TRONO_20261112",
]
HEROES = ["heroe", "arquetipo_heroe", "arquetipo_el_heroe"]
TRONO = ["arquetipo_el_gobernante", "kwml_01_rey"]
EPSILON = 0.05
DELTA_MIN_BASE = 0.1
DELTA_MIN_MAX = 0.25
QUARANTINE_PATTERN = "vulnerabilidad_sistemica"
QUARANTINE_THRESHOLD = 0.85


def _cargar_engine():
    spec = importlib.util.spec_from_file_location(
        "eng_no_dup", str(MOTOR_DIR / "Engine_V5_CANONICO_SOLO.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _familias_por_token(pl) -> Dict[str, Dict[str, List[str]]]:
    """token -> {'favor': [...], 'contra': [...]} (solo lectura del catálogo)."""
    out: Dict[str, Dict[str, List[str]]] = {}
    for fam, d in pl.patterns.items():
        for t in (d.get("tokens_favor") or {}):
            out.setdefault(t, {"favor": [], "contra": []})["favor"].append(fam)
        for t in (d.get("tokens_contra") or {}):
            out.setdefault(t, {"favor": [], "contra": []})["contra"].append(fam)
    return out


def _compania(cut_pesos: Dict[str, float], token: str, familia: str,
              lado: str, fam_por_token: Dict[str, Dict[str, List[str]]]) -> float:
    """Peso de compañía discriminante: compañeros del corte que alimentan
    SOLO a `familia` por el lado dado (excluye al propio token)."""
    total = 0.0
    for t, w in cut_pesos.items():
        if t == token:
            continue
        fams = (fam_por_token.get(t) or {}).get(lado) or []
        if fams == [familia]:
            total += w
    return total


def _asignar(token: str, cut_pesos: Dict[str, float],
             fam_por_token: Dict[str, Dict[str, List[str]]]
             ) -> Tuple[Optional[str], Optional[str], str]:
    """Devuelve (familia | None, lado 'favor'/'contra' | None, motivo).
    None + motivo 'latencia_*' = frente de latencia. None + motivo
    'sin_familia' = el token no hace nada (igual que en el canónico)."""
    info = fam_por_token.get(token) or {"favor": [], "contra": []}
    favor = info["favor"]
    contra = info["contra"]
    if favor:
        if len(favor) == 1:
            return favor[0], "favor", "unica"
        pesos = {f: _compania(cut_pesos, token, f, "favor", fam_por_token)
                 for f in favor}
        mejor = max(pesos.values())
        if mejor <= 0:
            return None, None, "latencia_sin_compania"
        ganadoras = [f for f, p in pesos.items() if p == mejor]
        if len(ganadoras) > 1:
            return None, None, "latencia_empate"
        return ganadoras[0], "favor", "por_compania"
    if contra:
        if len(contra) == 1:
            return contra[0], "contra", "unica_contra"
        pesos = {f: _compania(cut_pesos, token, f, "contra", fam_por_token)
                 for f in contra}
        mejor = max(pesos.values())
        if mejor <= 0:
            return None, None, "latencia_sin_compania_contra"
        ganadoras = [f for f, p in pesos.items() if p == mejor]
        if len(ganadoras) > 1:
            return None, None, "latencia_empate_contra"
        return ganadoras[0], "contra", "por_compania_contra"
    return None, None, "sin_familia"


def _recuperar_p_azar(board_sellado: Dict[str, float],
                      probs: Dict[str, float],
                      dmin: float, sigma: float) -> Tuple[float, float]:
    """Recupera p_azar_t del RESULT sellado por intersección de
    intervalos (p_final redondeado a 4 decimales). Devuelve
    (p_azar, ancho_del_intervalo). Si sigma ~ 0, p_azar es irrelevante.
    """
    if sigma < 1e-12:
        return 0.5, 0.0
    w_ev = max(0.0, 1.0 - dmin - sigma)
    lo, hi = 0.0, 1.0
    for name, prob in probs.items():
        pf = board_sellado[name]
        centro = (pf - w_ev * prob - dmin * 0.5) / sigma
        half = 0.00005 / sigma
        lo = max(lo, centro - half)
        hi = min(hi, centro + half)
    if hi < lo:  # no debería pasar; cae a mínimos cuadrados
        ests = [((board_sellado[n] - w_ev * p - dmin * 0.5) / sigma)
                for n, p in probs.items()]
        mid = sum(ests) / len(ests)
        return mid, float("nan")
    return (lo + hi) / 2.0, hi - lo


def _cuarentena(markers, pl) -> list:
    """Réplica de TracingEngine._filter_quarantine (solo lectura)."""
    suma = sum(pl.get_weight(QUARANTINE_PATTERN, m.token, True,
                             apply_evidence=False) for m in markers)
    if suma >= QUARANTINE_THRESHOLD:
        limpios = []
        for m in markers:
            w = pl.get_weight(QUARANTINE_PATTERN, m.token, True,
                              apply_evidence=False)
            if w <= 0:
                limpios.append(m)
        return limpios
    return markers


def correr_tablero_sombra(entrada: Dict[str, Any], resultado: Dict[str, Any],
                          eng, pl, fam_por_token, dedup: bool
                          ) -> Dict[str, Any]:
    """Recomputa los 3 tableros (P/A/C) corte a corte. Con dedup=False
    debe reproducir los P_FULL_244 sellados (puerta de cordura)."""
    Hypothesis = eng.Hypothesis
    Marker = eng.Marker
    boards: Dict[str, List[Dict[str, float]]] = {"P": [], "A": [], "C": []}
    gate_max_diff = 0.0
    gate_mismatch = 0
    eventos_favor = 0
    eventos_contra = 0
    eventos_favor_canon = 0
    eventos_contra_canon = 0
    ocurrencias = 0
    frentes: List[Dict[str, Any]] = []
    abiertos: Dict[str, Dict[str, Any]] = {}
    p_azar_ancho_max = 0.0

    hyps = {eje: {n: Hypothesis(n, 0.5) for n in pl.patterns}
            for eje in ("P", "A", "C")}

    for cut in entrada["cuts"]:
        cid = cut["id"]
        # pesos del corte entero (los 3 ejes) para la compañía semántica
        cut_pesos: Dict[str, float] = {}
        for eje in ("P", "A", "C"):
            for t, w in cut.get(eje) or []:
                cut_pesos[t] = max(cut_pesos.get(t, 0.0), float(w))
        # asignación por (token, corte): misma para los 3 ejes
        asignacion: Dict[str, Tuple[Optional[str], Optional[str], str]] = {}
        if dedup:
            for t in cut_pesos:
                asignacion[t] = _asignar(t, cut_pesos, fam_por_token)
        for eje in ("P", "A", "C"):
            rows = [(str(t), float(w)) for t, w in (cut.get(eje) or [])]
            assert len(rows) <= 5, f"cuello top-5 activo en {cid} {eje}"
            ocurrencias += len(rows)
            markers = [Marker(t, t, w) for t, w in rows]
            markers = _cuarentena(markers, pl)
            dh = (sum(m.uncertainty() for m in markers) / len(markers)
                  if markers else 0.0)
            sg = (statistics.pstdev([m.uncertainty() for m in markers])
                  if len(markers) > 1 else 0.0)
            dmin = DELTA_MIN_BASE + (DELTA_MIN_MAX - DELTA_MIN_BASE) * dh
            hs = hyps[eje]
            for h in hs.values():
                h.apply_epsilon(EPSILON)
            if not dedup:
                for m in markers:
                    for name, h in hs.items():
                        wf = pl.get_weight(name, m.token, True)
                        if wf > 0:
                            h.support(wf)
                            eventos_favor_canon += 1
                        wc = pl.get_weight(name, m.token, False)
                        if wc > 0:
                            h.contradict(wc)
                            eventos_contra_canon += 1
            else:
                for m in markers:
                    fam, lado, motivo = asignacion[m.token]
                    if fam is None:
                        if motivo.startswith("latencia"):
                            fr = abiertos.get(m.token)
                            if fr is None:
                                fr = {"token": m.token, "corte_apertura": cid,
                                      "motivo": motivo, "corte_resolucion": None,
                                      "familia_resuelta": None}
                                abiertos[m.token] = fr
                                frentes.append(fr)
                        continue
                    if lado == "favor":
                        wf = pl.get_weight(fam, m.token, True)
                        if wf > 0:
                            hs[fam].support(wf)
                            eventos_favor += 1
                    else:
                        wc = pl.get_weight(fam, m.token, False)
                        if wc > 0:
                            hs[fam].contradict(wc)
                            eventos_contra += 1
                    fr = abiertos.pop(m.token, None)
                    if fr is not None:
                        fr["corte_resolucion"] = cid
                        fr["familia_resuelta"] = fam
            for h in hs.values():
                h.probability = max(dmin, min(1.0 - dmin, h.probability))
            probs = {n: h.probability for n, h in hs.items()}
            board_sellado = resultado["motor"]["cuts"][
                [c["corte"] for c in resultado["motor"]["cuts"]].index(cid)
            ][f"{eje}_FULL_244"]
            p_azar, ancho = _recuperar_p_azar(board_sellado, probs, dmin, sg)
            p_azar_ancho_max = max(p_azar_ancho_max, ancho if ancho == ancho else 0.0)
            w_ev = max(0.0, 1.0 - dmin - sg)
            board: Dict[str, float] = {}
            for n, p in probs.items():
                pf = round(w_ev * p + dmin * 0.5 + sg * p_azar, 4)
                board[n] = pf
                if not dedup:
                    diff = abs(pf - board_sellado[n])
                    gate_max_diff = max(gate_max_diff, diff)
                    if diff > 0:
                        gate_mismatch += 1
            boards[eje].append(board)

    return {
        "boards": boards,
        "gate_max_diff": gate_max_diff,
        "gate_mismatch": gate_mismatch,
        "eventos_favor": eventos_favor if dedup else eventos_favor_canon,
        "eventos_contra": eventos_contra if dedup else eventos_contra_canon,
        "ocurrencias": ocurrencias,
        "frentes": frentes,
        "p_azar_ancho_max": p_azar_ancho_max,
    }


def resumen_caso(nombre: str, sombra: Dict[str, Any],
                 resultado: Dict[str, Any]) -> Dict[str, Any]:
    """H1/H2 sombra por p_final en el corte Z (nivel tablero)."""
    final_p = sombra["boards"]["P"][-1]
    top = sorted(final_p.items(), key=lambda kv: -kv[1])
    h1_canon = (resultado.get("H1") or {}).get("family")
    h2_canon = (resultado.get("H2") or {}).get("family")
    rango = {fam: i + 1 for i, (fam, _) in enumerate(top)}
    return {
        "caso": nombre,
        "h1_sombra": top[0][0],
        "p_h1_sombra": top[0][1],
        "h2_sombra": top[1][0],
        "p_h2_sombra": top[1][1],
        "h1_canonico": h1_canon,
        "h2_canonico": h2_canon,
        "p_h1_canonico_en_sombra": final_p.get(h1_canon),
        "rango_h1_canonico_en_sombra": rango.get(h1_canon),
        "top10_sombra": [[f, p] for f, p in top[:10]],
        "heroes": {f: {"p": final_p.get(f), "rango": rango.get(f)}
                   for f in HEROES},
        "trono": {f: {"p": final_p.get(f), "rango": rango.get(f)}
                  for f in TRONO},
        "factor_duplicacion": (sombra["eventos_favor"] / sombra["ocurrencias"]
                               if sombra["ocurrencias"] else 0.0),
        "eventos_favor": sombra["eventos_favor"],
        "eventos_contra": sombra["eventos_contra"],
        "ocurrencias": sombra["ocurrencias"],
        "frentes_abiertos": len(sombra["frentes"]),
        "frentes_resueltos": sum(1 for f in sombra["frentes"]
                                 if f["corte_resolucion"]),
        "frentes_sin_resolver": sum(1 for f in sombra["frentes"]
                                    if not f["corte_resolucion"]),
        "frentes": sombra["frentes"],
    }


def verificar_casos() -> Dict[str, Any]:
    eng = _cargar_engine()
    pl = eng.PatternLibrary(str(MOTOR_DIR / "patterns_final_v14.json"))
    fam_por_token = _familias_por_token(pl)
    out: Dict[str, Any] = {"version": VERSION, "casos": []}
    for nombre in CASOS:
        entrada = json.loads((CASOS_DIR / nombre / "entrada.json").read_text(encoding="utf-8"))
        resultado = json.loads((RESULTS_DIR / f"RESULT_{nombre}.json").read_text(encoding="utf-8"))
        sombra_off = correr_tablero_sombra(entrada, resultado, eng, pl, fam_por_token, dedup=False)
        sombra_on = correr_tablero_sombra(entrada, resultado, eng, pl, fam_por_token, dedup=True)
        res_on = resumen_caso(nombre, sombra_on, resultado)
        res_on["gate_max_diff"] = sombra_off["gate_max_diff"]
        res_on["gate_mismatch"] = sombra_off["gate_mismatch"]
        res_on["gate_pasa"] = (sombra_off["gate_mismatch"] == 0
                               and sombra_off["gate_max_diff"] <= 1e-6)
        res_on["factor_duplicacion_canonico"] = (
            sombra_off["eventos_favor"] / sombra_off["ocurrencias"])
        res_on["eventos_favor_canonico"] = sombra_off["eventos_favor"]
        res_on["eventos_contra_canonico"] = sombra_off["eventos_contra"]
        res_on["p_azar_ancho_max"] = sombra_off["p_azar_ancho_max"]
        out["casos"].append(res_on)
        print(f"{nombre}: gate mismatch={sombra_off['gate_mismatch']} "
              f"max_diff={sombra_off['gate_max_diff']} | canon "
              f"H1={res_on['h1_canonico']} -> sombra H1={res_on['h1_sombra']} "
              f"(p={res_on['p_h1_sombra']}) | factor "
              f"{res_on['factor_duplicacion_canonico']:.2f} -> "
              f"{res_on['factor_duplicacion']:.2f} | frentes "
              f"{res_on['frentes_abiertos']} ({res_on['frentes_resueltos']} resueltos)")
    return out


if __name__ == "__main__":
    data = verificar_casos()
    out_path = Path(__file__).resolve().parent / "no_duplicacion_resultado.json"
    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("escrito:", out_path)
