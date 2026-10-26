#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""guardian_pistas_llm_caldero_v1.py — guardián de entrada para pistas LLM del Caldero (arquetipos).

«Quemaduras ajenas»: el Caldero busca situaciones similares (web + pistas del LLM) para que el motor
aprenda de otros. Antes de este guardián, las pistas LLM (case.caldero_llm_neighbor_hints) se anexaban
CRUDAS a tokens_neighbors, sin pasar el filtro de identidad que sí pasan las fuentes web.
Este guardián filtra cada pista ANTES de que llegue al sidecar:
  - IDENTIDAD: token que contiene nombre/alias/término de identidad del caso -> descartado
  - FUTURO: marcadores de desenlace / post-Z (outcome, desenlace, finalmente, fracaso, éxito, muerte...) -> descartado
  - CALENDARIO: años 1000-2099 -> descartado
  - FORMA: vacío, >60 chars, URL, sin letras -> descartado
Determinista, sin red, sin LLM. can_decide_H=False. No toca Engine/244.
"""
from __future__ import annotations
import re
from typing import Any, Iterable

VERSION = "GUARDIAN_PISTAS_LLM_CALDERO_V1_20261025"
_FUTURO = re.compile(r"\b(outcome|desenlace|resultado_real|ground_truth|finalmente|terminar[ií]a|posteriormente|m[aá]s tarde|"
                     r"fracas\w*|[eé]xito|triunf\w*|muri[oó]|muerte|falleci\w*|post[_ ]?z|t1_resultado)\b", re.I)
_ANIO = re.compile(r"\b(1\d{3}|20\d{2})\b")


def filtrar(hints: Any, identity_terms: Iterable[str]) -> tuple[list, dict]:
    ident = [str(t).casefold() for t in (identity_terms or []) if len(str(t).strip()) >= 3]
    kept, descartes = [], []
    for h in (hints or []):
        tok = h.get("token") if isinstance(h, dict) else h
        s = str(tok or "").strip()
        low = s.casefold()
        motivo = None
        if not s or len(s) > 60 or "://" in s: motivo = "FORMA"
        elif _ANIO.search(low): motivo = "CALENDARIO"
        elif not re.search(r"[^\W\d_]", s): motivo = "FORMA"
        elif any(t in low for t in ident): motivo = "IDENTIDAD"
        elif _FUTURO.search(low): motivo = "FUTURO"
        elif _ANIO.search(low): motivo = "CALENDARIO"
        if motivo: descartes.append({"motivo": motivo, "huella": __import__("hashlib").sha256(low.encode()).hexdigest()[:8]})
        else: kept.append(h)
    return kept, {"guardian": VERSION, "entrada": len(list(hints or [])), "aceptadas": len(kept),
                  "descartadas": descartes, "can_decide_H": False}
