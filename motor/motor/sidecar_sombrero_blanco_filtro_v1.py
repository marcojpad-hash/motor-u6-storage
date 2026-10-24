#!/usr/bin/env python3
"""SOMBRERO BLANCO como GUARDIAN/FILTRO de ENTRADA y de SALIDA (PATCH 010a). Solo lectura.

Rol (Mj 2026-10-06 03:32): el sombrero blanco NO alimenta al predictor; es un guardián/filtro.
  - ENTRADA (antes del predictor): separa lo observable de lo meta/protocolo. Reporta tokens fuera de
    catálogo (motor.holes.fuera_catalogo, los mismos que plugin_sombrero_blanco_token.revisar manda a
    StinkBox), ruido de protocolo en pregunta/textos (misma regex PROTOCOL_NOISE_RE de UNICO), campos
    probabilísticos prohibidos en los cortes y produce la lista de TEXTOS ADMITIDOS: los canales de texto
    del hub (cuerpo_arco, area_tokens) solo leen esos textos (source_note = metadato -> excluido).
  - SALIDA (después del predictor): verifica que top10/H1/H2 sean familias del catálogo, que la evidencia
    propia del top10 use solo vocabulario del catálogo y ningún token fuera_catalogo, y que las etiquetas
    de salida no traigan ruido de protocolo.
No escribe stores (plugin_sombrero_blanco_token.revisar sí escribe stinkbox_tokens_descubiertos.json; aquí no se llama).
No modifica el input ni la salida: marca. can_decide_H=False, feeds_predictor=False.
"""
from __future__ import annotations
import re
from typing import Any, Dict, List

VERSION = "SOMBRERO_BLANCO_FILTRO_V1_PATCH010"
# Copia literal de MOTOR_V15_3_UNICO_20260927.py (PROTOCOL_NOISE_RE / CAMPOS_PROHIBIDOS).
PROTOCOL_NOISE_RE = re.compile(
    r"(?i)\b(juicio\s+est[eé]tico|fecha\s+de\s+protocolo|sombrero\s+blanco|"
    r"recorte\s+de\s+protocolo|metadato\s+de\s+protocolo)\b"
)
CAMPOS_PROHIBIDOS = {"probability", "probabilidad", "weight", "peso", "confidence", "confianza", "prob"}
# Marcas meta adicionales: SOLO bandera (no filtran por sí solas); documentadas para que Mj decida si suben a regex.
META_MARCAS_RE = re.compile(r"(?i)\b(notion|ejercicio\s+blanco|protocolo|checkpoint|patch\s*\d+)\b")
CAMPOS_TEXTO_HECHO = ("hecho", "narracion", "facts", "texto")   # observables
CAMPOS_TEXTO_META = ("source_note", "nota", "nota_pac")        # metadato del armado del caso


def _tok(c):
    return [str(t) for e in ("P", "A", "C") for t, _ in (c.get(e) or [])]


def entrada(case: Dict[str, Any], motor: Dict[str, Any], vocab: set) -> Dict[str, Any]:
    q = str(case.get("question", case.get("case_id", "")))
    fuera = []
    for cid, rec in sorted((motor.get("holes") or {}).items(), key=lambda kv: str(kv[0])):
        if isinstance(rec, dict):
            for it in rec.get("fuera_catalogo") or []:
                fuera.append({"corte": it.get("corte") or cid, "eje": it.get("eje"), "token": it.get("token"),
                              "equivalente": it.get("equivalente"), "llega_al_predictor": False,
                              "motivo": "token fuera del vocabulario del catálogo: ningún patrón lo cuenta; va a StinkBox (sombrero post-apuesta)"})
    tokens_fuera_vocab = sorted({t for c in case.get("cuts") or [] for t in _tok(c) if t not in vocab})
    admitidos, excluidos, ruido = [], [], []
    for c in case.get("cuts") or []:
        cid = c.get("id")
        for k in CAMPOS_TEXTO_HECHO:
            v = c.get(k)
            if isinstance(v, list):
                v = " ".join(str(x) for x in v)
            if not v:
                continue
            v = str(v)
            if PROTOCOL_NOISE_RE.search(v):
                excluidos.append({"corte": cid, "campo": k, "motivo": "ruido de protocolo (PROTOCOL_NOISE_RE)"})
                ruido.append({"corte": cid, "campo": k, "match": PROTOCOL_NOISE_RE.search(v).group(0)})
                continue
            admitidos.append({"corte": cid, "campo": k, "texto": v,
                              "marcas_meta": sorted({m.group(0).lower() for m in META_MARCAS_RE.finditer(v)})})
        for k in CAMPOS_TEXTO_META:
            if c.get(k):
                m = sorted({x.group(0).lower() for x in META_MARCAS_RE.finditer(str(c.get(k)))})
                excluidos.append({"corte": cid, "campo": k, "motivo": "metadato de armado del caso (no es hecho observable)", "marcas_meta": m})
    prohibidos = [{"corte": c.get("id"), "campo": k} for c in case.get("cuts") or [] for k in c.keys() if str(k).lower() in CAMPOS_PROHIBIDOS]
    return {"version": VERSION, "rol": "GUARDIAN/FILTRO de entrada", "feeds_predictor": False, "can_decide_H": False,
            "fuera_catalogo": fuera, "n_fuera_catalogo": len(fuera), "tokens_entrada_fuera_vocabulario": tokens_fuera_vocab,
            "ruido_protocolo_pregunta": bool(PROTOCOL_NOISE_RE.search(q)), "ruido_protocolo_textos": ruido,
            "campos_probabilisticos_prohibidos": prohibidos,
            "textos_admitidos": admitidos, "textos_excluidos": excluidos,
            "efecto": "los canales de texto del hub (cuerpo_arco, area_tokens) solo leen textos_admitidos; el tablero 244 ya ignora tokens fuera de vocabulario"}


def salida(pred: Dict[str, Any], motor: Dict[str, Any], catalogo: Dict[str, Any], ent: Dict[str, Any] | None) -> Dict[str, Any]:
    fams = set(catalogo or {})
    vocab = set()
    for pv in (catalogo or {}).values():
        vocab |= set((pv.get("tokens_favor") or {})) | set((pv.get("tokens_contra") or {}))
    fuera_tok = {x.get("token") for x in ((ent or {}).get("fuera_catalogo") or [])}
    cands = [c.get("family") for c in (pred.get("candidates") or [])[:10]]
    h = [x.get("family") if isinstance(x, dict) else x for x in (pred.get("H1"), pred.get("H2")) if x]
    no_catalogo = sorted({f for f in cands + h if f not in fams})
    ev = pred.get("own_evidence") or {}
    ev_fuera_vocab, ev_fuera_cat = {}, {}
    for f in cands:
        e = ev.get(f) or {}
        toks = set(e.get("favor_tokens") or []) | set(e.get("contra_tokens") or [])
        a = sorted(t for t in toks if t not in vocab)
        b = sorted(t for t in toks if t in fuera_tok)
        if a: ev_fuera_vocab[f] = a
        if b: ev_fuera_cat[f] = b
    ruido = sorted({f for f in cands + h if f and PROTOCOL_NOISE_RE.search(str(f))})
    sb = motor.get("sombrero_blanco") or {}
    limpio = not (no_catalogo or ev_fuera_vocab or ev_fuera_cat or ruido)
    return {"version": VERSION, "rol": "GUARDIAN/FILTRO de salida", "feeds_predictor": False, "can_decide_H": False,
            "salida_limpia": limpio, "familias_fuera_de_catalogo": no_catalogo,
            "evidencia_top10_fuera_vocabulario": ev_fuera_vocab, "evidencia_top10_con_token_fuera_catalogo": ev_fuera_cat,
            "ruido_protocolo_en_etiquetas": ruido, "n_top10_revisados": len(cands),
            "sombrero_post_apuesta_UNICO": {"status": sb.get("status"), "n_esta_corrida": sb.get("n_esta_corrida"), "n_stinkbox": sb.get("n_stinkbox"),
                                            "nota": "UNICO lo corre DESPUÉS de la apuesta y escribe stinkbox_tokens_descubiertos.json; su fila dice feeds_predictor=True (falso: no llega a ningún voto) -> corregido en 010b"}}
