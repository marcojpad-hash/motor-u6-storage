#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sidecar_ablacion_hombre_acero.py

SIDE-CAR AISLADO — Ablación del Pilar de Acero (POST-freeze, read-only on H).
Quita la evidencia MÁS FUERTE (no la más débil) y reevalúa si H se sostiene.

Candados:
    TOCA_F = NO
    TOCA_244 = NO
    TOCA_Engine_V5 = NO
    TOCA_FREEZE = NO
    TOCA_PAC = NO
    TOCA_H1_H2 = NO  (lee, nunca escribe / no reescribe freeze)

Tres criterios EN PARALELO (fijados de antemano):
    1. persistencia (consec / total cortes; umbral N default 4)
    2. coincidencia P/A/C directa a Z
    3. independencia entre lentes

Veredictos: robusta | fragil-de-un-pilar | fragil-de-conjunto
(también etiquetas compuestas como string si aplica).

Spec: SPEC_USO_ABLACION_PILLAR_ACERO.md
Protocolo: EXPERIMENTOS/HAWKING_Z90_.../02_HOMBRE_DE_ACERO_ABLACION.md
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

VERSION = "0.1"
SCHEMA = "ablacion_hombre_acero_sidecar_v1"
PLUGIN = "sidecar_ablacion_hombre_acero"

CANON_LOCK = {
    "TOCA_F": False,
    "TOCA_244": False,
    "TOCA_Engine_V5": False,
    "TOCA_FREEZE": False,
    "TOCA_PAC": False,
    "TOCA_H1_H2": False,
}

N_PERSIST_DEFAULT = 4

# Definición operativa default de "H se sostiene" (caller puede sobreescribir).
H_HOLDS_DEFAULT = (
    "la configuración H sigue siendo la mejor lectura del conjunto restante "
    "frente a rivales declarados (no exige mismos p-numbers del board)"
)


def manifest() -> dict[str, Any]:
    return {
        "plugin": PLUGIN,
        "version": VERSION,
        "schema": SCHEMA,
        "momento": "POST-freeze",
        "CANON_LOCK": dict(CANON_LOCK),
        "modifies_freeze": False,
        "modifies_244": False,
        "modifies_engine_v5": False,
        "rewrites_H": False,
        "prediction": False,
        "estado": "EXPERIMENTAL_SIDECAR",
        "n_persist_default": N_PERSIST_DEFAULT,
    }


def _norm(value: Any) -> str:
    return str(value).strip()


def _as_list(raw: Any) -> list[Any]:
    if raw is None:
        return []
    if isinstance(raw, (str, bytes)):
        return [raw]
    if isinstance(raw, Sequence):
        return list(raw)
    return [raw]


def parse_evidence_piece(raw: Mapping[str, Any], idx: int) -> dict[str, Any]:
    eid = _norm(raw.get("id", raw.get("eid", f"E{idx + 1}")))
    token = _norm(raw.get("token", raw.get("nombre", "")))
    axis = _norm(raw.get("axis", raw.get("eje", "")))
    cuts = [str(c) for c in _as_list(raw.get("cuts", raw.get("cortes", [])))]
    lenses = [str(x) for x in _as_list(raw.get("lenses", raw.get("lentes", [])))]
    consec = raw.get("consec", raw.get("consecutive", raw.get("consecutivo")))
    if consec is None:
        consec = len(cuts)
    try:
        consec_i = int(consec)
    except (TypeError, ValueError):
        consec_i = 0
    n_cortes = raw.get("n_cortes", raw.get("n", len(cuts)))
    try:
        n_cortes_i = int(n_cortes)
    except (TypeError, ValueError):
        n_cortes_i = len(cuts)
    # Opcional: caller ya declara si es coincidencia P/A/C a Z
    pac_direct = bool(
        raw.get("pac_direct", raw.get("coincidencia_pac", raw.get("pac_match", False)))
    )
    # Opcional: score de independencia (n lentes únicas) o lista
    if not lenses and raw.get("lente"):
        lenses = [str(raw.get("lente"))]
    supports_rivals = bool(raw.get("supports_rivals", raw.get("apoya_rivales", False)))
    holds_without = raw.get("holds_without")  # None | True | False (caller override)
    return {
        "id": eid,
        "token": token,
        "axis": axis.upper() if axis else "",
        "cuts": cuts,
        "lenses": lenses,
        "consec": consec_i,
        "n_cortes": n_cortes_i,
        "pac_direct": pac_direct,
        "supports_rivals": supports_rivals,
        "holds_without": holds_without,
        "raw_meta": {
            k: v
            for k, v in raw.items()
            if k
            not in {
                "id",
                "eid",
                "token",
                "nombre",
                "axis",
                "eje",
                "cuts",
                "cortes",
                "lenses",
                "lentes",
                "consec",
                "consecutive",
                "consecutivo",
                "n_cortes",
                "n",
                "pac_direct",
                "coincidencia_pac",
                "pac_match",
                "supports_rivals",
                "apoya_rivales",
                "holds_without",
                "lente",
            }
        },
    }


def load_evidence(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    raw = (
        payload.get("evidence")
        or payload.get("evidencia")
        or payload.get("evidencias")
        or payload.get("pieces")
        or payload.get("piezas")
        or []
    )
    # Lista raíz: [{id, token, ...}, ...]
    if not raw and isinstance(payload, Mapping) and any(
        k in payload for k in ("id", "token", "nombre")
    ):
        raw = [payload]
    if isinstance(payload, list):
        raw = payload
    if not isinstance(raw, Sequence):
        raise ValueError("evidence debe ser lista de piezas {id, token, axis, cuts, lenses}")
    return [parse_evidence_piece(item, i) for i, item in enumerate(raw) if isinstance(item, Mapping)]


def criterion_persistence(
    pieces: Sequence[Mapping[str, Any]],
    *,
    n_persist: int,
) -> list[str]:
    """Piezas con consec >= N (o n_cortes >= N si consec no alcanza)."""
    selected = []
    best = 0
    for p in pieces:
        score = max(int(p["consec"]), int(p["n_cortes"]))
        if score >= n_persist:
            if score > best:
                best = score
                selected = [p["id"]]
            elif score == best:
                selected.append(p["id"])
    # Si nadie llega a N, no inventar: lista vacía (umbral fijado antes).
    return selected


def criterion_pac_direct(
    pieces: Sequence[Mapping[str, Any]],
    *,
    pac_tops: Mapping[str, Sequence[str]] | None = None,
) -> list[str]:
    """
    Coincidencia P/A/C directa.
    - Si la pieza trae pac_direct=True, cuenta.
    - Si pac_tops dado {P:[tokens],...}, match token∈tops[axis].
    """
    tops: dict[str, set[str]] = {}
    if pac_tops:
        for axis, tokens in pac_tops.items():
            tops[str(axis).upper()] = {_norm(t) for t in tokens}

    selected = []
    for p in pieces:
        if p.get("supports_rivals"):
            # Coincide con rival (p.ej. arte_prestigio para H2A) — no pilar de H.
            continue
        if p.get("pac_direct"):
            selected.append(p["id"])
            continue
        axis = p.get("axis") or ""
        token = p.get("token") or ""
        if axis and token and axis in tops and token in tops[axis]:
            selected.append(p["id"])
    return selected


def criterion_independence(pieces: Sequence[Mapping[str, Any]]) -> list[str]:
    """
    Independencia entre lentes: piezas con lentes no vacías y eje distinto
    del resto del set fuerte. Señala piezas que aportan un lente/eje propio
    (sin doble-conteo del mismo lente).
    """
    # Agrupar por lente; si una lente solo la carga una pieza → independiente.
    lens_owners: dict[str, list[str]] = {}
    axis_owners: dict[str, list[str]] = {}
    for p in pieces:
        for lens in p.get("lenses") or []:
            lens_owners.setdefault(str(lens), []).append(p["id"])
        ax = p.get("axis") or ""
        if ax:
            axis_owners.setdefault(ax, []).append(p["id"])

    independent: list[str] = []
    for p in pieces:
        lenses = p.get("lenses") or []
        # Independiente si tiene al menos una lente exclusiva O un eje con poca competencia
        exclusive_lens = any(len(lens_owners.get(str(L), [])) == 1 for L in lenses)
        exclusive_axis = bool(p.get("axis")) and len(axis_owners.get(p["axis"], [])) <= 2
        if exclusive_lens or (exclusive_axis and lenses):
            independent.append(p["id"])
        elif exclusive_axis and not lenses:
            # Sin lentes declaradas: eje distinto aún cuenta como independencia débil
            independent.append(p["id"])
    # Dedup preserve order
    seen = set()
    out = []
    for i in independent:
        if i not in seen:
            seen.add(i)
            out.append(i)
    return out


def select_steel_pillars(
    pieces: Sequence[Mapping[str, Any]],
    *,
    n_persist: int,
    pac_tops: Mapping[str, Sequence[str]] | None = None,
) -> dict[str, Any]:
    by_id = {p["id"]: p for p in pieces}
    c1 = criterion_persistence(pieces, n_persist=n_persist)
    c2 = criterion_pac_direct(pieces, pac_tops=pac_tops)
    c3 = criterion_independence(pieces)

    votes: dict[str, list[str]] = {}
    for label, ids in (
        ("persistencia", c1),
        ("pac_directa", c2),
        ("independencia", c3),
    ):
        for eid in ids:
            votes.setdefault(eid, []).append(label)

    # Pilares = unión de lo señalado (hallazgo si >1); excluir rivales
    pillar_ids = [eid for eid in votes.keys() if not by_id[eid].get("supports_rivals")]
    # Orden: más criterios primero, luego mayor consec
    pillar_ids.sort(
        key=lambda eid: (
            -len(votes[eid]),
            -int(by_id[eid]["consec"]),
            -int(by_id[eid]["n_cortes"]),
            eid,
        )
    )

    return {
        "criterios": {
            "persistencia": c1,
            "pac_directa": c2,
            "independencia": c3,
        },
        "votos": {eid: votes[eid] for eid in pillar_ids},
        "pillar_ids": pillar_ids,
        "colapso_a_una": len(pillar_ids) == 1,
        "hallazgo_varios_sostenes": len(pillar_ids) > 1,
    }


def _holds_after_removal(
    removed_ids: Sequence[str],
    pieces: Sequence[Mapping[str, Any]],
    *,
    overrides: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Evalúa si H se sostiene sin las piezas removed_ids.

    Prioridad:
      1) overrides[ablation_key] si existe (caller declara holds True/False)
      2) holds_without en cada pieza removida (AND: si alguna dice False → no)
      3) heurística: si se quitan TODOS los pilares de ejes P y A con consec>=N
         y no queda ninguna pieza con consec>=N → no sostiene
         si queda ≥1 pieza fuerte no-rival → sostiene (debilitada)
    """
    removed = set(removed_ids)
    remaining = [p for p in pieces if p["id"] not in removed]
    key = "+".join(sorted(removed_ids))
    if overrides and key in overrides:
        val = overrides[key]
        holds = bool(val.get("holds", val)) if isinstance(val, Mapping) else bool(val)
        note = val.get("nota", "") if isinstance(val, Mapping) else "override_caller"
        return {
            "holds": holds,
            "remaining_ids": [p["id"] for p in remaining],
            "source": "override",
            "nota": note,
        }

    # Pieza-level holds_without: si el caller marcó la pieza removida
    flagged = []
    for p in pieces:
        if p["id"] in removed and p.get("holds_without") is not None:
            flagged.append(bool(p["holds_without"]))
    if flagged:
        # H se sostiene sin esa pieza solo si TODAS las removidas con flag dicen True
        # (para ablación multi-pieza: AND)
        holds = all(flagged)
        return {
            "holds": holds,
            "remaining_ids": [p["id"] for p in remaining],
            "source": "holds_without_flags",
            "nota": "AND de holds_without de piezas removidas",
        }

    strong_remaining = [
        p
        for p in remaining
        if not p.get("supports_rivals") and max(p["consec"], p["n_cortes"]) >= 3
    ]
    holds = len(strong_remaining) >= 1
    return {
        "holds": holds,
        "remaining_ids": [p["id"] for p in remaining],
        "source": "heuristic_strong_remaining",
        "nota": (
            "heurística: queda ≥1 pieza fuerte no-rival"
            if holds
            else "heurística: no queda pieza fuerte no-rival"
        ),
    }


def build_verdict(
    individual: Sequence[Mapping[str, Any]],
    conjunto: Mapping[str, Any],
) -> dict[str, Any]:
    """
    robusta | fragil-de-un-pilar | fragil-de-conjunto (+ compuestos).
    """
    labels: list[str] = []
    any_holds = False
    any_fails = False
    fragile_pillars = []
    robust_pillars = []

    for row in individual:
        if row["resultado"]["holds"]:
            any_holds = True
            robust_pillars.append(row["ablated_id"])
            labels.append(f"robusta-ante-ablacion-de-{row['ablated_id']}")
        else:
            any_fails = True
            fragile_pillars.append(row["ablated_id"])
            labels.append(f"fragil-ante-ablacion-de-{row['ablated_id']}")

    conjunto_holds = bool(conjunto.get("resultado", {}).get("holds"))
    if not conjunto_holds:
        labels.append("fragil-de-conjunto-si-caen-pilares")
    else:
        labels.append("robusta-de-conjunto-sin-pilares")

    if not individual:
        primary = "sin-pilares-seleccionados"
    elif any_fails and any_holds:
        primary = "fragil-de-un-pilar"  # al menos un pilar crítico
    elif any_fails and not any_holds:
        primary = "fragil-de-un-pilar"
    elif not conjunto_holds:
        primary = "fragil-de-conjunto"
    else:
        primary = "robusta"

    # Si el conjunto cae al quitar todos pero individuales mixtos → compuesto
    if not conjunto_holds and any_holds and any_fails:
        primary = "fragil-de-conjunto"

    return {
        "primary": primary,
        "compound": labels,
        "fragile_pillar_ids": fragile_pillars,
        "robust_pillar_ids": robust_pillars,
        "conjunto_holds": conjunto_holds,
    }


def run_ablacion(
    payload: Mapping[str, Any],
    *,
    n_persist: int | None = None,
) -> dict[str, Any]:
    # Si el payload es lista cruda de piezas
    if isinstance(payload, list):
        payload = {"evidence": payload}

    pieces = load_evidence(payload)
    n = int(
        n_persist
        if n_persist is not None
        else (payload.get("n_persist", payload.get("N", N_PERSIST_DEFAULT)) if isinstance(payload, Mapping) else N_PERSIST_DEFAULT)
    )
    if not pieces:
        return {
            "plugin": PLUGIN,
            "schema": SCHEMA,
            "version": VERSION,
            "estado": "EXPERIMENTAL_SIDECAR",
            "momento": "POST-freeze",
            "candados": {
                "TOCA_F": "NO",
                "TOCA_244": "NO",
                "TOCA_Engine_V5": "NO",
                "TOCA_FREEZE": "NO",
                "TOCA_PAC": "NO",
                "TOCA_H1_H2": "NO",
            },
            "n_persist": n,
            "evidence": [],
            "seleccion_pilares": {
                "criterios": {"persistencia": [], "pac_directa": [], "independencia": []},
                "votos": {},
                "pillar_ids": [],
                "colapso_a_una": False,
                "hallazgo_varios_sostenes": False,
            },
            "ablaciones_individuales": [],
            "reinterrelacion_conjunto": {
                "ablated_ids": [],
                "resultado": {"holds": True, "remaining_ids": [], "source": "no_evidence", "nota": "sin evidencia"},
                "restantes": [],
            },
            "veredicto": {
                "primary": "sin-pilares-seleccionados",
                "compound": [],
                "fragile_pillar_ids": [],
                "robust_pillar_ids": [],
                "conjunto_holds": True,
            },
            "CANON_LOCK": dict(CANON_LOCK),
            "nota": "Sin evidencia declarada — no se fabrica pilar.",
        }

    if n < 1:
        raise ValueError("n_persist debe ser >= 1 (fijar ANTES del run)")

    h_holds_def = payload.get("h_holds_definition") or payload.get("definicion_h_sostiene") or H_HOLDS_DEFAULT
    pac_tops = payload.get("pac_tops") or payload.get("tops_pac")
    overrides = payload.get("ablation_overrides") or payload.get("overrides_ablacion") or {}

    selection = select_steel_pillars(pieces, n_persist=n, pac_tops=pac_tops)
    pillar_ids = selection["pillar_ids"]

    individual = []
    for eid in pillar_ids:
        result = _holds_after_removal([eid], pieces, overrides=overrides)
        individual.append(
            {
                "ablated_id": eid,
                "ablated_token": next(p["token"] for p in pieces if p["id"] == eid),
                "criterios": selection["votos"].get(eid, []),
                "resultado": result,
            }
        )

    # Reinterrelación obligatoria: quitar TODOS los pilares de acero
    if pillar_ids:
        conjunto_res = _holds_after_removal(pillar_ids, pieces, overrides=overrides)
    else:
        conjunto_res = {
            "holds": True,
            "remaining_ids": [p["id"] for p in pieces],
            "source": "no_pillars",
            "nota": "sin pilares seleccionados; conjunto intacto",
        }

    conjunto = {
        "ablated_ids": list(pillar_ids),
        "resultado": conjunto_res,
        "restantes": [
            {"id": p["id"], "token": p["token"], "axis": p["axis"]}
            for p in pieces
            if p["id"] not in set(pillar_ids)
        ],
    }

    verdict = build_verdict(individual, conjunto)

    return {
        "plugin": PLUGIN,
        "schema": SCHEMA,
        "version": VERSION,
        "estado": "EXPERIMENTAL_SIDECAR",
        "momento": "POST-freeze",
        "candados": {
            "TOCA_F": "NO",
            "TOCA_244": "NO",
            "TOCA_Engine_V5": "NO",
            "TOCA_FREEZE": "NO",
            "TOCA_PAC": "NO",
            "TOCA_H1_H2": "NO",
        },
        "prohibitions": {
            "rewrites_freeze": False,
            "rewrites_H_text": False,
            "fabricates_steel_pillar": False,
        },
        "n_persist": n,
        "h_holds_definition": h_holds_def,
        "evidence": pieces,
        "seleccion_pilares": selection,
        "ablaciones_individuales": individual,
        "reinterrelacion_conjunto": conjunto,
        "veredicto": verdict,
        "CANON_LOCK": dict(CANON_LOCK),
        "nota": "Solo reporta; no modifica freeze ni texto de H.",
    }



def ablar_hombre_acero(
    evidencias: Sequence[Mapping[str, Any]] | Mapping[str, Any],
    *,
    n_persist: int | None = None,
    pac_tops: Mapping[str, Sequence[str]] | None = None,
    board_z_tokens: Sequence[str] | None = None,
    cut_order: Sequence[str] | None = None,
    min_piezas_para_sostener: int | None = None,
    require_axes: Sequence[str] | None = None,
    ablation_overrides: Mapping[str, Any] | None = None,
    h_holds_definition: str | None = None,
) -> dict[str, Any]:
    """API corta POST-freeze. No reescribe H. Wrapper sobre run_ablacion."""
    if isinstance(evidencias, Mapping) and not any(
        k in evidencias for k in ("evidence", "evidencia", "evidencias", "pieces", "piezas")
    ):
        # una sola pieza
        payload: dict[str, Any] = {"evidence": [evidencias]}
    elif isinstance(evidencias, Mapping):
        payload = dict(evidencias)
    else:
        payload = {"evidence": list(evidencias)}

    if n_persist is not None:
        payload["n_persist"] = n_persist
    if pac_tops is not None:
        payload["pac_tops"] = pac_tops
    elif board_z_tokens:
        # tokens del board Z → match pac en cualquier eje si la pieza coincide
        toks = [str(t) for t in board_z_tokens]
        payload["pac_tops"] = {"P": toks, "A": toks, "C": toks}
    if ablation_overrides is not None:
        payload["ablation_overrides"] = ablation_overrides
    if h_holds_definition is not None:
        payload["h_holds_definition"] = h_holds_definition
    # cut_order / min_piezas / require_axes: metadatos de contrato (no cambian freeze)
    if cut_order is not None:
        payload.setdefault("meta", {})["cut_order"] = list(cut_order)
    if min_piezas_para_sostener is not None:
        payload.setdefault("meta", {})["min_piezas_para_sostener"] = int(min_piezas_para_sostener)
    if require_axes is not None:
        payload.setdefault("meta", {})["require_axes"] = list(require_axes)

    report = run_ablacion(payload, n_persist=n_persist)
    # Alias de campos para smoke / protocolo en español
    sel = report.get("seleccion_pilares") or {}
    report["seleccion"] = {
        "pilares_acero_ids": list(sel.get("pillar_ids") or []),
        "criterios": sel.get("criterios"),
        "votos": sel.get("votos"),
        "colapso_a_una": sel.get("colapso_a_una"),
        "hallazgo_varios_sostenes": sel.get("hallazgo_varios_sostenes"),
    }
    verd = report.get("veredicto")
    if isinstance(verd, Mapping):
        report["veredicto_detalle"] = verd
        report["veredicto"] = verd.get("primary", "sin-pilares-seleccionados")
    report["reinterrelacion_sin_todos_los_pilares"] = report.get("reinterrelacion_conjunto")
    return report


def load_input(path_or_dash: str) -> dict[str, Any]:
    if path_or_dash == "-":
        return json.load(sys.stdin)
    path = Path(path_or_dash)
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Ablación Hombre de Acero POST-freeze — report only, no rewrite H"
    )
    ap.add_argument("--input", "-i", required=True, help="JSON evidence path o '-' (stdin)")
    ap.add_argument("--out", "-o", default=None, help="JSON report path (default stdout)")
    ap.add_argument(
        "--n-persist",
        type=int,
        default=None,
        help=f"Umbral N persistencia (default {N_PERSIST_DEFAULT}; fijar ANTES)",
    )
    args = ap.parse_args(list(argv) if argv is not None else None)

    payload = load_input(args.input)
    report = run_ablacion(payload, n_persist=args.n_persist)
    text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
