#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sujetos_014.py — PATCH 014 (2026-10-06) + política 015 (2026-10-06).

Un sujeto cuenta una sola vez en el soporte del vocabulario de vecinos.

- sujeto_de_caso(case): id de sujeto desde metadatos del input, en este orden:
    1) campo `person` del input (slug);  2) tabla explícita por case_id;  3) reglas explícitas de prefijo de case_id;
    4) `caldero_identity.nombre_o_alias` (slug);  5) el propio case_id (sujeto desconocido = solo él mismo).
- sujeto_de_case_id(cid): para eventos del store (no traen metadatos de persona): audit_meta.sujeto_014 si existe,
    si no tabla -> prefijo -> case_id.
- nombres_que_no_votan(case): POLÍTICA INTENCIONAL (015, confirmada por Mj): excluye TODOS los nombres propios
    de sujetos conocidos en TABLA/PREFIJOS (y el `person` del caso), de forma GLOBAL — no solo el sujeto actual.
    Lectura canónica: 'nombres propios de sujetos no votan en otros casos'. NO es sobre-filtrado.
    El motor trabaja por patrones/operaciones; el LLM (no el motor) traduce nombres de entrada/salida.
    Traza: `nombres_sujeto_015` (antes `nombres_sujeto_014`).

TABLA documentada (sin adivinar más allá de prefijos obvios del nombre). Se lista también en 014_*.md / 015_*.md.
Contrato: no escribe nada, no decide H, no toca favor/contra de familias ni el 244.
"""
from __future__ import annotations
import re
import unicodedata
from typing import Any, Dict, Iterable, Mapping, Optional, Set, Tuple

VERSION = "SUJETOS_014_20261006+POLITICA_015_20261006"


def _sin_acentos(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


def slug(s: Any) -> str:
    t = _sin_acentos(str(s or "")).casefold()
    return re.sub(r"[^a-z0-9]+", "_", t).strip("_")


def _tokens_nombre(nombre: Any) -> Set[str]:
    out: Set[str] = set()
    for w in re.split(r"[^\w]+", str(nombre or ""), flags=re.UNICODE):
        w = w.strip("_").casefold()
        if len(w) >= 3 and not w.isdigit():
            out.add(w); out.add(_sin_acentos(w))
    return out


# case_id -> (sujeto, fuente, nombre visible)
TABLA: Dict[str, Tuple[str, str, str]] = {
    "PAPA_PIO_NOCTURNA_20261005": ("pio_ii_enea_silvio_piccolomini", "input.person", "Pío II / Enea Silvio Piccolomini"),
    "CALIBRACION_ELON_MUSK_DESDE_CERO_20260924": ("elon_musk", "input.person", "Elon Musk"),
    "EXTRA_GOBERNADOR_JUAREZ_20261006": ("benito_juarez", "input.person", "Benito Juárez"),
    "EXTRA_VISIONARIO_TESLA_20261006": ("nikola_tesla", "input.person", "Nikola Tesla"),
    "MOZART_NOCTURNA_20261005": ("mozart", "prefijo_case_id (input sin campo person)", "Mozart"),
    "MOZART_FRESH_WEB_BIO_V04_20260930": ("mozart", "prefijo_case_id (sin input en disco)", "Mozart"),
    "CIEGO_15_ANTECEDENTES_C": ("ciego_15_sellado", "input.caldero_identity.nombre_o_alias (identidad sellada; no se agrupa)", ""),
    "SMOKE_ESTANDAR": ("smoke_estandar", "case_id (caso sintético sin persona)", ""),
    "CAMEO_SMOKE_20260928": ("cameo_smoke_20260928", "case_id (sin persona)", ""),
}
# prefijo de case_id -> (sujeto, nombre visible). Solo nombres obvios.
PREFIJOS: Tuple[Tuple[str, str, str], ...] = (
    ("MOZART_", "mozart", "Mozart"),
    ("PAPA_PIO_", "pio_ii_enea_silvio_piccolomini", "Pío II / Enea Silvio Piccolomini"),
    ("CALIBRACION_ELON_MUSK_", "elon_musk", "Elon Musk"),
    ("ELON_MUSK_", "elon_musk", "Elon Musk"),
    ("MUSK_", "elon_musk", "Elon Musk"),
)


def sujeto_de_case_id(cid: Any, audit_meta: Optional[Mapping[str, Any]] = None) -> Tuple[str, str]:
    if isinstance(audit_meta, Mapping) and audit_meta.get("sujeto_014"):
        return str(audit_meta["sujeto_014"]), "audit_meta.sujeto_014"
    c = str(cid or "")
    if c in TABLA:
        return TABLA[c][0], "tabla:" + TABLA[c][1]
    for p, s, _n in PREFIJOS:
        if c.upper().startswith(p):
            return s, "prefijo:" + p
    return "caso:" + c, "case_id"


def sujeto_de_caso(case: Mapping[str, Any]) -> Tuple[str, str]:
    if case.get("person"):
        return slug(case["person"]), "input.person"
    s, f = sujeto_de_case_id(case.get("case_id"))
    if f != "case_id":
        return s, f
    ci = case.get("caldero_identity") or {}
    if isinstance(ci, Mapping) and ci.get("nombre_o_alias"):
        return slug(ci["nombre_o_alias"]), "input.caldero_identity.nombre_o_alias"
    return s, f


def nombres_que_no_votan(case: Optional[Mapping[str, Any]] = None) -> Set[str]:
    """Conjunto GLOBAL de tokens de nombres propios de sujetos (TABLA+PREFIJOS+person).

    Intencional (015): un token que sea SOLO nombre propio de sujeto de la tabla nunca vota en ningún caso.
    No se limita al sujeto del caso actual.
    """
    out: Set[str] = set()
    for _s, _f, n in TABLA.values():
        out |= _tokens_nombre(n)
    for _p, _s, n in PREFIJOS:
        out |= _tokens_nombre(n)
    if case is not None and case.get("person"):
        out |= _tokens_nombre(case.get("person"))
    return out


def contexto(case: Mapping[str, Any]) -> Dict[str, Any]:
    s, f = sujeto_de_caso(case)
    return {"version": VERSION, "sujeto": s, "fuente": f, "nombres_no_votan": sorted(nombres_que_no_votan(case)),
            "can_decide_H": False}
