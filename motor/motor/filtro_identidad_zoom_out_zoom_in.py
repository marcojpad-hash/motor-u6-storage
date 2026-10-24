#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filtro de identidad Zoom Out → Zoom In para Caldero / sidecar de arquetipos.

Reemplaza SelfMatchFilter (demasiado estricto) y DesambiguadorPorAbstraccion
(demasiado laxo). No toca Engine_V5 ni patterns 244.

Candados: TOCA_F=NO, TOCA_244=NO, TOCA_Engine_V5=NO, TOCA_FREEZE=NO.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Iterable, Mapping, Sequence
import hashlib
import json
import re
import unicodedata

VERSION = "1.0.0"
SCHEMA = "identidad_zoom_out_zoom_in_v1"

# Umbral zoom-out: PENDIENTE de validación independiente (spec).
# Valor operativo inicial documentado; no promover a canon sin prueba.
ZOOM_OUT_THRESHOLD_PENDING = True
ZOOM_OUT_PROTOTYPE_OVERLAP_MIN = 0.5  # overlap Jaccard mín. de tags de prototipo


class Decision(str, Enum):
    DESCARTADO_EN_ZOOM_OUT = "descartado_en_zoom_out"
    DISTINTO_EN_ZOOM_IN = "distinto_en_zoom_in"
    MISMA_IDENTIDAD_ZOOM_IN = "misma_identidad_zoom_in"
    # Candidato sin señal de prototipo ni de identidad: se conserva (no es self-match).
    SIN_SENAL_CONSERVAR = "sin_senal_conservar"


# --- normalización ---------------------------------------------------------

_WS = re.compile(r"[\s_\-./]+")
_NON_ALNUM = re.compile(r"[^a-z0-9áéíóúüñ ]+", re.IGNORECASE)

# meses ES / EN (mínimo útil; no inventar parser ambiguo 6/9)
_MONTHS = {
    "enero": 1, "january": 1, "jan": 1,
    "febrero": 2, "february": 2, "feb": 2,
    "marzo": 3, "march": 3, "mar": 3,
    "abril": 4, "april": 4, "apr": 4,
    "mayo": 5, "may": 5,
    "junio": 6, "june": 6, "jun": 6,
    "julio": 7, "july": 7, "jul": 7,
    "agosto": 8, "august": 8, "aug": 8,
    "septiembre": 9, "september": 9, "sep": 9, "sept": 9,
    "octubre": 10, "october": 10, "oct": 10,
    "noviembre": 11, "november": 11, "nov": 11,
    "diciembre": 12, "december": 12, "dec": 12,
}

_ISO = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")
_ES_LONG = re.compile(
    r"\b(\d{1,2})\s+de\s+(" + "|".join(_MONTHS.keys()) + r")\s+de\s+(\d{4})\b",
    re.IGNORECASE,
)
_EN_LONG = re.compile(
    r"\b(" + "|".join(_MONTHS.keys()) + r")\s+(\d{1,2}),?\s+(\d{4})\b",
    re.IGNORECASE,
)


def _fold(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.casefold().strip()


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    t = _fold(str(value))
    t = t.replace("_", " ").replace("-", " ")
    t = _WS.sub(" ", t)
    t = _NON_ALNUM.sub(" ", t)
    return _WS.sub(" ", t).strip()


def normalize_name(name: str | None) -> str:
    return normalize_text(name or "")


def name_parts(name: str | None) -> tuple[str, ...]:
    n = normalize_name(name)
    return tuple(p for p in n.split(" ") if p)


def surname(name: str | None) -> str | None:
    parts = name_parts(name)
    return parts[-1] if parts else None


def parse_date_to_iso(value: str | None) -> str | None:
    """Devuelve YYYY-MM-DD o None. No adivina ambigüedades tipo 6/9."""
    if not value:
        return None
    raw = str(value).strip()
    m = _ISO.search(raw)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    m = _ES_LONG.search(_fold(raw))
    if m:
        d, mon, y = int(m.group(1)), _MONTHS[m.group(2).lower()], int(m.group(3))
        return f"{y:04d}-{mon:02d}-{d:02d}"
    m = _EN_LONG.search(_fold(raw))
    if m:
        mon, d, y = _MONTHS[m.group(1).lower()], int(m.group(2)), int(m.group(3))
        return f"{y:04d}-{mon:02d}-{d:02d}"
    # solo ISO compacto ya cubierto; no parsear 6/9
    return None


def normalize_url_for_name(url: str | None) -> str:
    if not url:
        return ""
    # quitar scheme/host path noise suave: quedarnos con path+query texto
    t = url
    t = re.sub(r"^https?://", "", t, flags=re.I)
    return normalize_text(t)


# --- identidad / fuente ----------------------------------------------------

@dataclass(frozen=True)
class CaseIdentity:
    name: str | None = None
    birth_date: str | None = None  # preferir ISO; se acepta ES/EN largo
    death_date: str | None = None
    unique_facts: tuple[str, ...] = ()
    # tags de prototipo opcionales para zoom-out (PENDIENTE calibrar lista cerrada)
    prototype_tags: tuple[str, ...] = ()

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "CaseIdentity":
        facts = raw.get("unique_facts", raw.get("hechos_unicos", ())) or ()
        tags = raw.get("prototype_tags", raw.get("prototipo", ())) or ()
        if isinstance(tags, str):
            tags = (tags,)
        return cls(
            name=raw.get("name", raw.get("nombre")),
            birth_date=raw.get("birth_date", raw.get("fecha_nacimiento")),
            death_date=raw.get("death_date", raw.get("fecha_muerte")),
            unique_facts=tuple(str(x) for x in facts),
            prototype_tags=tuple(normalize_text(x) for x in tags if x),
        )

    @property
    def birth_iso(self) -> str | None:
        return parse_date_to_iso(self.birth_date)

    @property
    def death_iso(self) -> str | None:
        return parse_date_to_iso(self.death_date)


@dataclass(frozen=True)
class Source:
    url: str = ""
    title: str = ""
    snippet: str = ""
    metadata: Mapping[str, Any] | None = None
    # si el caller ya tipificó prototipo del candidato (opcional)
    prototype_tags: tuple[str, ...] = ()

    def haystack(self) -> str:
        return " ".join([self.url or "", self.title or "", self.snippet or ""])

    def as_dict(self) -> dict[str, Any]:
        return {
            "url": self.url,
            "title": self.title,
            "snippet": self.snippet,
            "metadata": dict(self.metadata or {}),
            "prototype_tags": list(self.prototype_tags),
        }


@dataclass
class PassAudit:
    zoom_out: dict[str, Any] = field(default_factory=dict)
    zoom_in: dict[str, Any] = field(default_factory=dict)
    decision: str = Decision.SIN_SENAL_CONSERVAR.value


# --- zoom out / zoom in ----------------------------------------------------

_DEFAULT_PROTO_HINTS = (
    # pistas débiles de prototipo en texto (no confirman identidad)
    "fundador", "ceo", "empresario", "tecnologia", "technology",
    "cohete", "rocket", "space", "startup", "billionaire", "inventor",
)


def infer_prototype_tags_from_text(text: str) -> set[str]:
    n = normalize_text(text)
    found = set()
    for h in _DEFAULT_PROTO_HINTS:
        if h in n:
            found.add(h)
    return found


def zoom_out(
    identity: CaseIdentity,
    source: Source,
) -> dict[str, Any]:
    """
    Pasada gruesa. NUNCA confirma identidad.
    Decide si vale la pena hacer zoom in (posible self-match / mismo prototipo).
    """
    id_tags = set(identity.prototype_tags)
    src_tags = set(t for t in source.prototype_tags if t) | infer_prototype_tags_from_text(
        source.haystack()
    )

    # Señal de apellido solo = "posible" a nivel categoría (decisión Mj),
    # NO confirma; solo habilita zoom in.
    sur = surname(identity.name)
    hay = normalize_text(source.haystack())
    surname_only_hit = bool(sur) and re.search(rf"\b{re.escape(sur)}\b", hay) is not None
    full_name_hit = bool(normalize_name(identity.name)) and normalize_name(identity.name) in hay

    # fecha cruda/ISO en haystack → también motiva zoom in
    birth_iso = identity.birth_iso
    date_hint = False
    if birth_iso and (birth_iso in hay or birth_iso.replace("-", "") in hay.replace(" ", "")):
        date_hint = True
    if identity.birth_date and normalize_text(identity.birth_date) in hay:
        date_hint = True
    # fecha en español en haystack (sin confirmar aún)
    if birth_iso and parse_date_to_iso(source.haystack()) == birth_iso:
        date_hint = True

    overlap = 0.0
    if id_tags and src_tags:
        overlap = len(id_tags & src_tags) / max(1, len(id_tags | src_tags))

    worth_zoom_in = bool(
        full_name_hit
        or surname_only_hit
        or date_hint
        or any(normalize_text(f) and normalize_text(f) in hay for f in identity.unique_facts)
        or (overlap >= ZOOM_OUT_PROTOTYPE_OVERLAP_MIN and (id_tags and src_tags))
    )

    return {
        "worth_zoom_in": worth_zoom_in,
        "surname_only_hit": surname_only_hit,
        "full_name_hit": full_name_hit,
        "date_hint": date_hint,
        "prototype_overlap": round(overlap, 4),
        "id_tags": sorted(id_tags),
        "src_tags": sorted(src_tags),
        "threshold_pending": ZOOM_OUT_THRESHOLD_PENDING,
        "threshold_used": ZOOM_OUT_PROTOTYPE_OVERLAP_MIN,
        "confirms_identity": False,  # regla no negociable
    }


def zoom_in(
    identity: CaseIdentity,
    source: Source,
) -> dict[str, Any]:
    """
    Pasada fina OBLIGATORIA antes de confirmar.
    Compara valores normalizados reales, nunca categoría.
    """
    hay_raw = source.haystack()
    hay = normalize_text(hay_raw)
    url_n = normalize_url_for_name(source.url)

    full = normalize_name(identity.name)
    parts = name_parts(identity.name)
    sur = surname(identity.name)

    name_full_match = bool(full) and (full in hay or full in url_n)
    # nombre en URL tipo Elon_Musk
    name_url_match = bool(full) and full.replace(" ", "") in url_n.replace(" ", "")
    if parts and len(parts) >= 2:
        slug = "_".join(parts)
        if slug in normalize_text(source.url).replace(" ", "_"):
            name_url_match = True
        if " ".join(parts) in url_n:
            name_url_match = True

    # apellido solo NO confirma identidad (regla Mj)
    surname_alone_match = bool(sur) and re.search(rf"\b{re.escape(sur)}\b", hay) is not None
    # confirmar apellido solo si va acompañado de otro ancla (fecha o hecho) — se evalúa abajo

    birth_iso = identity.birth_iso
    hay_dates = set()
    for m in _ISO.finditer(hay_raw):
        hay_dates.add(f"{m.group(1)}-{m.group(2)}-{m.group(3)}")
    for m in _ES_LONG.finditer(_fold(hay_raw)):
        d, mon, y = int(m.group(1)), _MONTHS[m.group(2).lower()], int(m.group(3))
        hay_dates.add(f"{y:04d}-{mon:02d}-{d:02d}")
    for m in _EN_LONG.finditer(_fold(hay_raw)):
        mon, d, y = _MONTHS[m.group(1).lower()], int(m.group(2)), int(m.group(3))
        hay_dates.add(f"{y:04d}-{mon:02d}-{d:02d}")

    birth_match = bool(birth_iso) and birth_iso in hay_dates
    death_iso = identity.death_iso
    death_match = bool(death_iso) and death_iso in hay_dates

    fact_hits = []
    for f in identity.unique_facts:
        nf = normalize_text(f)
        if nf and nf in hay:
            fact_hits.append(f)

    # Confirmación: al menos un ancla fuerte de identidad individual
    # - nombre completo o slug URL, O
    # - fecha de nacimiento/muerte parseada, O
    # - hecho único
    # Apellido solo NUNCA basta.
    same = bool(name_full_match or name_url_match or birth_match or death_match or fact_hits)

    return {
        "same_identity": same,
        "name_full_match": name_full_match,
        "name_url_match": name_url_match,
        "surname_alone_match": surname_alone_match,
        "surname_alone_confirms": False,
        "birth_iso": birth_iso,
        "birth_match": birth_match,
        "death_match": death_match,
        "fact_hits": fact_hits,
        "hay_dates_found": sorted(hay_dates),
    }


def evaluate_source(
    identity: CaseIdentity,
    source: Source,
) -> PassAudit:
    zo = zoom_out(identity, source)
    audit = PassAudit(zoom_out=zo)

    if not zo["worth_zoom_in"]:
        # sin señal de posible self-match → conservar (no es descarte por prototipo ajeno
        # en este filtro: el filtro SOLO descarta auto-coincidencia del caso)
        audit.decision = Decision.SIN_SENAL_CONSERVAR.value
        audit.zoom_in = {"skipped": True, "reason": "zoom_out_not_worth"}
        return audit

    zi = zoom_in(identity, source)
    audit.zoom_in = zi
    if zi["same_identity"]:
        audit.decision = Decision.MISMA_IDENTIDAD_ZOOM_IN.value
    else:
        # compartió señal gruesa (apellido/proto) pero no es la misma persona
        audit.decision = Decision.DISTINTO_EN_ZOOM_IN.value
    return audit


class ZoomIdentityFilter:
    """
    Filtro externo al Caldero.
    Solo descarta fuentes con decision == misma_identidad_zoom_in.
    Identidad NUNCA debe entrar al query ciego ni a caldero_input.
    """

    def __init__(self, identity: CaseIdentity | Mapping[str, Any]):
        if isinstance(identity, CaseIdentity):
            self.identity = identity
        else:
            self.identity = CaseIdentity.from_mapping(identity)

    def evaluate(self, source: Source | Mapping[str, Any]) -> PassAudit:
        if not isinstance(source, Source):
            source = Source(
                url=str(source.get("url", "")),
                title=str(source.get("title", "")),
                snippet=str(source.get("snippet", "")),
                metadata=source.get("metadata"),
                prototype_tags=tuple(source.get("prototype_tags", ()) or ()),
            )
        return evaluate_source(self.identity, source)

    def filter(
        self, sources: Sequence[Source | Mapping[str, Any]]
    ) -> tuple[list[Source], list[dict[str, Any]]]:
        kept: list[Source] = []
        discarded: list[dict[str, Any]] = []
        for raw in sources:
            src = raw if isinstance(raw, Source) else Source(
                url=str(raw.get("url", "")),
                title=str(raw.get("title", "")),
                snippet=str(raw.get("snippet", "")),
                metadata=raw.get("metadata"),
                prototype_tags=tuple(raw.get("prototype_tags", ()) or ()),
            )
            audit = evaluate_source(self.identity, src)
            row = {
                "url": src.url,
                "title": src.title,
                "decision": audit.decision,
                "zoom_out": audit.zoom_out,
                "zoom_in": audit.zoom_in,
            }
            if audit.decision == Decision.MISMA_IDENTIDAD_ZOOM_IN.value:
                discarded.append(row)
            else:
                kept.append(src)
                # audit de conservados no se mezcla al caldero; el caller puede loguear
        return kept, discarded


def stable_hash(payload: Any) -> str:
    raw = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def run_acceptance_suite() -> dict[str, Any]:
    """Criterios Obra 1 (ASIGNACIONES Claude + decisión Mj apellido)."""
    identity = CaseIdentity(
        name="Elon Musk",
        birth_date="1971-06-28",
        unique_facts=("SpaceX",),
        prototype_tags=("fundador", "tecnologia"),
    )
    filt = ZoomIdentityFilter(identity)

    cases = [
        ("musk_title", Source(url="https://news.example/a", title="Elon Musk lanza cohete", snippet=""), "discard"),
        ("birth_es", Source(url="https://bio.example/x", title="Biografía", snippet="nació el 28 de junio de 1971 en Pretoria"), "discard"),
        ("url_slug", Source(url="https://es.wikipedia.org/wiki/Elon_Musk", title="Wikipedia", snippet=""), "discard"),
        ("curie", Source(url="https://ex/c", title="Marie Curie y el radio", snippet="descubrimiento"), "keep"),
        ("bezos", Source(url="https://ex/b", title="Jeff Bezos funda Amazon", snippet="empresario tecnologia"), "keep"),
        ("jobs", Source(url="https://ex/j", title="Steve Jobs presenta iPhone", snippet="fundador tecnologia"), "keep"),
        ("surname_only", Source(url="https://ex/s", title="Musk anuncia nueva fábrica", snippet=""), "keep"),  # apellido ≠ confirmación
    ]

    results = []
    ok = True
    for cid, src, expect in cases:
        audit = filt.evaluate(src)
        discarded = audit.decision == Decision.MISMA_IDENTIDAD_ZOOM_IN.value
        got = "discard" if discarded else "keep"
        passed = got == expect
        ok = ok and passed
        results.append(
            {
                "id": cid,
                "expect": expect,
                "got": got,
                "pass": passed,
                "decision": audit.decision,
                "zoom_out": audit.zoom_out,
                "zoom_in": audit.zoom_in,
            }
        )

    kept, disc = filt.filter([c[1] for c in cases])
    report = {
        "schema": SCHEMA,
        "version": VERSION,
        "all_pass": ok,
        "n_kept": len(kept),
        "n_discarded": len(disc),
        "cases": results,
        "candados": {
            "TOCA_Engine_V5": False,
            "TOCA_244": False,
            "TOCA_FREEZE": False,
            "identity_enters_caldero_query": False,
        },
    }
    report["sha256_report"] = stable_hash(report)
    return report


if __name__ == "__main__":
    rep = run_acceptance_suite()
    print(json.dumps({k: rep[k] for k in ("version", "all_pass", "n_kept", "n_discarded", "sha256_report")}, ensure_ascii=False, indent=2))
    for c in rep["cases"]:
        mark = "OK" if c["pass"] else "FAIL"
        print(f"  [{mark}] {c['id']}: expect={c['expect']} got={c['got']} decision={c['decision']}")
    raise SystemExit(0 if rep["all_pass"] else 1)
