
"""
plugin_souriau_210141.py
SIDE-CAR LATERAL — Souriau / 210,141 situaciones

V1.3 — revisión posterior a Cloud.

Candados:
    TOCA_F = NO
    TOCA_244 = NO
    TOCA_Engine_V5 = NO
    TOCA_PAC = NO
    TOCA_FREEZE = NO
    TOCA_H1_H2 = NO

El sidecar ilumina; no decide.
No suma a p. No modifica P/A/C, freeze, H1/H2 ni el catálogo 244.
No convierte las seis funciones Souriau en patrones.
"""

from __future__ import annotations
from dataclasses import dataclass, asdict
from itertools import combinations
from typing import Any, Iterable, Mapping, Sequence
import hashlib
import json

PLUGIN_ID = "souriau_210141"
VERSION = "1.4"
EXPECTED_CASES = 210_141

FUNCTIONS = ("leon", "marte", "sol", "tierra", "balanza", "luna")
P_REF = "leon"
A_REF = "marte"
DESIRED = "sol"
RECIPIENT = "tierra"
ARBITER = "balanza"
HELPER = "luna"

STATES = ("observado", "ausente", "latente", "fuera_de_ventana", "no_observado")

CANON_LOCK = {
    "TOCA_F": False,
    "TOCA_244": False,
    "TOCA_Engine_V5": False,
    "TOCA_PAC": False,
    "TOCA_FREEZE": False,
    "TOCA_H1_H2": False,
}


@dataclass(frozen=True)
class TemporalCut:
    corte_actual: int

    def validate(self, corte: int | None) -> None:
        if corte is None:
            raise ValueError("corte_ausente_bajo_corte_actual")
        if corte > self.corte_actual:
            raise ValueError(
                f"dato_posterior_al_corte:corte={corte}:actual={self.corte_actual}"
            )


@dataclass(frozen=True)
class SouriauFunction:
    nombre: str
    valor: Any = None
    estado: str = "no_observado"
    evidencia: Any = None
    corte: int | None = None

    def as_dict(self):
        return asdict(self)


@dataclass(frozen=True)
class SouriauCase:
    case_id: str
    funciones: tuple[SouriauFunction, ...]
    grouping: tuple[tuple[str, ...], ...] = ()
    source: str = "souriau"
    evidence_status: str = "reference"
    metadata: Mapping[str, Any] | None = None

    def as_dict(self):
        d = asdict(self)
        d["funciones"] = [x.as_dict() for x in self.funciones]
        return d


def _norm(x: Any) -> str:
    return str(x).strip().casefold()


def _stable_id(payload: Mapping[str, Any]) -> str:
    """ID determinista del contenido cuando la fuente no da case_id."""
    raw = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )
    return "souriau:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:20]


def _content_signature(case: SouriauCase) -> str:
    """Firma canónica del contenido para detectar conflictos de case_id."""
    payload = {
        "funciones": [f.as_dict() for f in case.funciones],
        "grouping": case.grouping,
        "source": case.source,
        "evidence_status": case.evidence_status,
        "metadata": case.metadata,
    }
    return _stable_id(payload)


def _function_item(raw: Any, name: str, corte: int | None) -> SouriauFunction:
    if raw is None:
        return SouriauFunction(name, estado="no_observado", corte=corte)

    if isinstance(raw, Mapping):
        estado = _norm(raw.get("estado", "observado"))
        if estado not in STATES:
            raise ValueError(f"estado_invalido:{estado}")
        raw_corte = raw.get("corte")
        if raw_corte is None:
            raw_corte = corte
        if raw_corte is not None:
            raw_corte = int(raw_corte)
        return SouriauFunction(
            nombre=name,
            valor=raw.get("valor"),
            estado=estado,
            evidencia=raw.get("evidencia"),
            corte=raw_corte,
        )

    return SouriauFunction(
        nombre=name,
        valor=raw,
        estado="observado",
        evidencia=None,
        corte=corte,
    )


def normalize_case(record: Mapping[str, Any], corte: int | None = None) -> SouriauCase:
    """Normaliza un caso conservando explícitamente las seis funciones."""
    if not isinstance(record, Mapping):
        raise TypeError("record_debe_ser_mapping")

    raw_funcs = record.get("funciones", record.get("functions", {}))

    if isinstance(raw_funcs, Sequence) and not isinstance(raw_funcs, (str, bytes, dict)):
        raw_funcs = {
            FUNCTIONS[i]: raw_funcs[i]
            for i in range(min(len(raw_funcs), len(FUNCTIONS)))
        }
    elif raw_funcs is None:
        raw_funcs = {}
    elif not isinstance(raw_funcs, Mapping):
        raise TypeError("funciones_debe_ser_mapping_o_sequence")

    funciones = tuple(_function_item(raw_funcs.get(f), f, corte) for f in FUNCTIONS)

    grouping = record.get("agrupacion", record.get("grouping", ())) or ()
    if not isinstance(grouping, Sequence) or isinstance(grouping, (str, bytes)):
        raise TypeError("agrupacion_debe_ser_sequence_de_grupos")

    grouping_norm = []
    for group in grouping:
        if not isinstance(group, Sequence) or isinstance(group, (str, bytes)):
            raise TypeError("cada_grupo_debe_ser_sequence")
        grouping_norm.append(tuple(_norm(x) for x in group if _norm(x)))
    grouping_norm = tuple(grouping_norm)

    identity_payload = {
        "funciones": [
            {
                "nombre": f.nombre,
                "valor": f.valor,
                "estado": f.estado,
                "evidencia": f.evidencia,
                "corte": f.corte,
            }
            for f in funciones
        ],
        "grouping": grouping_norm,
        "source": str(record.get("source", "souriau")),
        "evidence_status": str(record.get("evidence_status", "reference")),
        "metadata": record.get("metadata"),
    }

    case_id = str(record.get("case_id") or record.get("id") or "").strip()
    if not case_id:
        case_id = _stable_id(identity_payload)

    return SouriauCase(
        case_id=case_id,
        funciones=funciones,
        grouping=grouping_norm,
        source=str(record.get("source", "souriau")),
        evidence_status=str(record.get("evidence_status", "reference")),
        metadata=record.get("metadata"),
    )


def ingest(
    records: Iterable[Mapping[str, Any]],
    expected_count: int | None = EXPECTED_CASES,
    corte_actual: int | None = None,
) -> dict[str, Any]:
    """Ingesta lateral determinista, deduplicada y temporalmente cerrada."""
    cases = {}
    duplicates = 0
    temporal = TemporalCut(int(corte_actual)) if corte_actual is not None else None

    for record in records:
        if not isinstance(record, Mapping):
            raise TypeError("record_debe_ser_mapping")

        record_corte = record.get("corte")
        if temporal is not None:
            if record_corte is None:
                raise ValueError("corte_ausente_bajo_corte_actual")
            record_corte = int(record_corte)
            temporal.validate(record_corte)

        case = normalize_case(record, corte=record_corte)

        if temporal is not None:
            for fn in case.funciones:
                temporal.validate(fn.corte)

        if case.case_id in cases:
            existing = cases[case.case_id]
            if _content_signature(existing) != _content_signature(case):
                raise ValueError(
                    f"case_id_conflict:{case.case_id}:contenido_distinto"
                )
            duplicates += 1
            continue
        cases[case.case_id] = case

    count = len(cases)
    return {
        "plugin": PLUGIN_ID,
        "version": VERSION,
        "namespace": "souriau",
        "expected_cases": expected_count,
        "unique_cases": count,
        "duplicate_records": duplicates,
        "complete_claim": expected_count is not None and count == expected_count,
        "cases": [c.as_dict() for c in cases.values()],
        "temporal_cut": {
            "enabled": temporal is not None,
            "corte_actual": corte_actual,
            "lookahead": False,
            "reconstructs_future": False,
        },
        "CANON_LOCK": dict(CANON_LOCK),
    }


def build_declared_relations(case: SouriauCase) -> list[dict[str, Any]]:
    """Solo relaciones explícitamente observables/declaradas."""
    relations = []
    observed = [f.nombre for f in case.funciones if f.estado == "observado"]

    for a, b in combinations(observed, 2):
        relations.append({"type": "co_presence", "source": case.case_id, "a": a, "b": b})

    for group in case.grouping:
        relations.append({
            "type": "group_membership",
            "source": case.case_id,
            "members": list(group),
        })

    return relations


def reflector_signals(case: SouriauCase) -> dict[str, Any]:
    by_name = {f.nombre: f for f in case.funciones}
    return {
        "referencia_P": by_name[P_REF].as_dict(),
        "referencia_A": by_name[A_REF].as_dict(),
        "cobertura_lateral": {
            "sol_deseado": by_name[DESIRED].as_dict(),
            "tierra_destinatario": by_name[RECIPIENT].as_dict(),
            "balanza_arbitro": by_name[ARBITER].as_dict(),
            "luna_ayudante": by_name[HELPER].as_dict(),
        },
        "espejo_pac": False,
        "sustituye_pac": False,
        "decide": False,
    }


def emit_for_integration(ingested: Mapping[str, Any]) -> dict[str, Any]:
    """Emite el contrato lateral sin perder cortes ni identidad funcional."""
    units = []
    relations = []

    for raw in ingested.get("cases", []):
        case = normalize_case(raw)
        units.append({
            "unit_id": case.case_id,
            "namespace": "souriau",
            "kind": "dramatic_situation",
            "payload": case.as_dict(),
            "reflector": reflector_signals(case),
            "provenance": {
                "source": case.source,
                "evidence_status": case.evidence_status,
            },
            "state": "lateral_reference",
        })
        relations.extend(build_declared_relations(case))

    return {
        "schema": "lateral_unit_relation_v1",
        "namespace": "souriau",
        "units": units,
        "relations": relations,
        "temporal_cut": ingested.get("temporal_cut"),
        "decision_layer": {
            "freeze_decides": True,
            "sidecar_decides": False,
            "adds_probability": False,
            "modifies_pac": False,
            "creates_patterns": False,
            "modifies_h1_h2": False,
        },
        "CANON_LOCK": dict(ingested.get("CANON_LOCK", CANON_LOCK)),
    }


def manifest() -> dict[str, Any]:
    return {
        "plugin": PLUGIN_ID,
        "version": VERSION,
        "namespace": "souriau",
        "expected_cases": EXPECTED_CASES,
        "grouping_semantics": (
            "pertenencia_explicita_al_grupo; "
            "co_presence solo por co-presencia explicita en funciones observadas"
        ),
        "functions": list(FUNCTIONS),
        "functional_references": {
            "leon": "P_reference_only",
            "marte": "A_reference_only",
            "sol": "deseado",
            "tierra": "destinatario",
            "balanza": "arbitro",
            "luna": "ayudante_condicional",
        },
        "states": list(STATES),
        "status": "SIDE_CAR_ONLY",
        "integration_schema": "lateral_unit_relation_v1",
        "CANON_LOCK": dict(CANON_LOCK),
    }


if __name__ == "__main__":
    print(json.dumps(manifest(), ensure_ascii=False, indent=2))


