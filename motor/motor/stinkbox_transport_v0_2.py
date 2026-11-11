#!/usr/bin/env python3
"""STINKBOX / TRANSPORT LAYER v0.2

Persistent, case-local lateral memory.  It is deliberately downstream of FREEZE
and upstream of the predictor.  It never mutates Engine V5, the 244-pattern
catalogue, P/A/C, R732, FREEZE or H1/H2.

The layer stores evidence; it does not execute or claim to implement the missing
Billard/Poincare source pair.  Existing R732 trajectory metrics are recorded as
observations. Formula-10 contradictions are recorded only when an upstream
component explicitly supplies them.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping

VERSION = "STINKBOX_TRANSPORT_V0.2"
FEEDS_PREDICTOR = True
FEEDS_H = False
MUTATES_CANON = False
CROSSES_FREEZE = False
INTEGRATION_POINT = "post_freeze_pre_predictor"
KAPPA_ALERT_THRESHOLD = None  # no unverified hard threshold


def _safe_case_id(case_id: str) -> str:
    value = str(case_id).strip()
    if not value or not re.fullmatch(r"[A-Za-z0-9_.-]+", value):
        raise ValueError(f"Invalid case_id for StinkBox: {case_id!r}")
    return value


def _now() -> float:
    return time.time()


class StinkBox:
    def __init__(self, case_id: str, root: str | Path):
        self.case_id = _safe_case_id(case_id)
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.path = self.root / f"stinkbox_{self.case_id}.json"
        self.corrupt_path = self.root / f"stinkbox_{self.case_id}.corrupt"
        self.data = self._load_or_create()

    def _new(self) -> Dict[str, Any]:
        now = _now()
        return {
            "schema": VERSION,
            "case_id": self.case_id,
            "architecture_layer": "STINKBOX_CONTAINMENT_VAULT",
            "created_at": now,
            "updated_at": now,
            "contract": {
                "feeds_predictor": FEEDS_PREDICTOR,
                "feeds_H": FEEDS_H,
                "mutates_canon": MUTATES_CANON,
                "crosses_FREEZE": CROSSES_FREEZE,
                "integration_point": INTEGRATION_POINT,
                "billard_source_execution": "NOT_IMPLEMENTED_HERE",
                "formula10_recording": "ONLY_IF_EXPLICITLY_SUPPLIED"
            },
            "token_events": [],
            "token_frequency": {},
            "token_cuts": {},
            "token_sources": {},
            "coactivation": {},
            "trajectory_events": [],
            "formula10_contradictions": [],
            "latency_events": [],
            "persistent_neighbor_tokens": [],
            "persistent_neighbor_lights": [],
            "persistent_neighbor_activation_events": []
        }

    def _load_or_create(self) -> Dict[str, Any]:
        if not self.path.exists():
            return self._new()
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except Exception as exc:
            # Preserve the corrupt artifact instead of silently resetting it.
            if not self.corrupt_path.exists():
                os.replace(self.path, self.corrupt_path)
            raise RuntimeError(f"STINKBOX_CORRUPT_JSON:{self.path}:{exc}") from exc
        if not isinstance(data, dict) or data.get("case_id") != self.case_id:
            raise RuntimeError(f"STINKBOX_SCHEMA_ERROR:{self.path}")
        return data

    def _save(self) -> None:
        payload = json.dumps(self.data, ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8")
        fd, tmp_name = tempfile.mkstemp(prefix=self.path.name + ".", dir=str(self.root))
        try:
            with os.fdopen(fd, "wb") as fh:
                fh.write(payload)
                fh.flush()
                os.fsync(fh.fileno())
            os.replace(tmp_name, self.path)
        finally:
            try:
                os.unlink(tmp_name)
            except FileNotFoundError:
                pass

    def _touch(self) -> None:
        self.data["updated_at"] = _now()

    def archive_tokens(self, *, cut_id: str, tokens: Iterable[str], source: str, kind: str = "external") -> int:
        source = str(source)
        unique = sorted({str(t).strip().lower() for t in tokens if str(t).strip()})
        if not unique:
            return 0
        cuts = self.data["token_cuts"]
        sources = self.data["token_sources"]
        freq = self.data["token_frequency"]
        for token in unique:
            self.data["token_events"].append({
                "timestamp": _now(), "cut_id": str(cut_id), "token": token,
                "source": source, "kind": kind
            })
            freq[token] = int(freq.get(token, 0)) + 1
            cuts.setdefault(token, [])
            if str(cut_id) not in cuts[token]:
                cuts[token].append(str(cut_id))
            sources.setdefault(token, [])
            if source not in sources[token]:
                sources[token].append(source)
        # Coactivation is defined here as distinct tokens observed in the same cut.
        for i, a in enumerate(unique):
            for b in unique[i + 1:]:
                key = "|".join(sorted((a, b)))
                self.data["coactivation"][key] = int(self.data["coactivation"].get(key, 0)) + 1
        self._touch(); self._save()
        return len(unique)

    def record_trajectory(self, *, cut_id: str, dX_norm: float, persist_cos: float, kappa_dir: float) -> None:
        self.data["trajectory_events"].append({
            "cut_id": str(cut_id), "timestamp": _now(),
            "dX_norm": round(float(dX_norm), 9),
            "persist_cos": round(float(persist_cos), 9),
            "kappa_dir": round(float(kappa_dir), 9),
            "source_semantics": "R732_TRAJECTORY_METRIC",
            "billard_executed": False
        })
        self._touch(); self._save()

    def record_formula10(self, *, cut_id: str, marker: Any, context_tokens: Iterable[str], source: str) -> None:
        self.data["formula10_contradictions"].append({
            "cut_id": str(cut_id), "timestamp": _now(), "marker": marker,
            "context_tokens": sorted({str(x) for x in context_tokens}), "source": str(source)
        })
        self._touch(); self._save()

    def register_persistent_neighbor_lights(self, *, tokens: Iterable[str], source: str, cut_id: str = "Z_TRABAJO", branch: str = "caldero_memory", stereotype: str = "caldero_neighbor") -> int:
        """Register persisted neighbors as reusable light vocabulary.

        Registration is persistent and does not itself activate a light. Activation
        is allowed only when the same token is observed again in the current run.
        branch/stereotype permiten registrar tambien tokens descubiertos de
        StinkBox (branch stinkbox_discovered) con la misma regla: se registran,
        no se activan solos.
        """
        unique = sorted({str(t).strip().casefold() for t in tokens if str(t).strip()})
        if not unique:
            return 0
        existing = set(self.data.get("persistent_neighbor_tokens") or [])
        lights = self.data.setdefault("persistent_neighbor_lights", [])
        for token in unique:
            existing.add(token)
            if not any(isinstance(x, dict) and x.get("token") == token for x in lights):
                lights.append({"token": token, "branch": str(branch),
                               "stereotype": str(stereotype), "axes": [],
                               "source": str(source), "persistent": True})
        self.data["persistent_neighbor_tokens"] = sorted(existing)
        self._touch(); self._save()
        return len(unique)

    def record_persistent_neighbor_activation(self, *, cut_id: str, token: str, source: str) -> None:
        self.data.setdefault("persistent_neighbor_activation_events", []).append({
            "timestamp": _now(), "cut_id": str(cut_id), "token": str(token).strip().casefold(),
            "source": str(source), "kind": "persistent_caldero_neighbor_light"
        })
        self._touch(); self._save()

    def record_latency(self, *, state: str, reason: str, cut_id=None, front_id=None, detail=None, save=True) -> None:
        self.data["latency_events"].append({
            "timestamp": _now(), "state": str(state), "reason": str(reason),
            "cut_id": cut_id, "front_id": front_id, "detail": detail,
        })
        if save:
            self._touch(); self._save()

    def transport(self, patterns_path: str | Path, extra_tokens: Iterable[str] = ()) -> Dict[str, Any]:
        """Read persisted lateral evidence and turn it into predictor features.

        extra_tokens: tokens persistentes de StinkBox (otros vaults + descubiertos)
        que alimentan el soporte de esta corrida. Solo se leen: no se escriben en
        este vault, no se les inventa equivalente y no mutan el canon.
        """
        tokens = set(self.data.get("token_frequency", {}))
        extra = {str(t).strip().casefold() for t in (extra_tokens or ()) if str(t).strip()}
        tokens = tokens | extra
        token_sources = self.data.get("token_sources", {})
        token_cuts = self.data.get("token_cuts", {})
        source_diversity = sum(1 for t in tokens if len(token_sources.get(t, [])) >= 2)
        repeated = sum(1 for t in tokens if len(token_cuts.get(t, [])) >= 2)
        coactive = sum(int(v) for v in self.data.get("coactivation", {}).values())
        traj = self.data.get("trajectory_events", [])
        contradictions = self.data.get("formula10_contradictions", [])

        raw = Path(patterns_path).read_text(encoding="utf-8")
        patterns = json.loads(raw)
        candidate_support: Dict[str, float] = {}
        candidate_details: Dict[str, Any] = {}
        for name, pat in (patterns.items() if isinstance(patterns, dict) else []):
            favor = set((pat.get("tokens_favor") or {}).keys())
            contra = set((pat.get("tokens_contra") or {}).keys())
            fh = len(tokens & favor) / max(1, len(favor))
            ch = len(tokens & contra) / max(1, len(contra))
            # bounded signed evidence; no pattern mutation and no direct H write
            signed = max(-1.0, min(1.0, fh - ch))
            candidate_support[str(name)] = signed
            candidate_details[str(name)] = {"favor_hits": sorted(tokens & favor), "contra_hits": sorted(tokens & contra)}

        mean_kappa = None
        mean_persist = None
        if traj:
            mean_kappa = sum(x["kappa_dir"] for x in traj) / len(traj)
            mean_persist = sum(x["persist_cos"] for x in traj) / len(traj)

        return {
            "schema": VERSION,
            "case_id": self.case_id,
            "feeds_predictor": True,
            "feeds_H": False,
            "mutates_canon": False,
            "crosses_FREEZE": False,
            "integration_point": INTEGRATION_POINT,
            "global": {
                "unique_tokens": len(tokens),
                "repeated_tokens": repeated,
                "multi_source_tokens": source_diversity,
                "coactivation_events": coactive,
                "trajectory_events": len(traj),
                "formula10_contradictions": len(contradictions),
                "mean_kappa_dir": mean_kappa,
                "mean_persist_cos": mean_persist
            },
            "candidate_support": candidate_support,
            "candidate_details": candidate_details,
            "audit": {
                "billard_executed": False,
                "trajectory_source": "motor.R732",
                "patterns_sha256": hashlib.sha256(Path(patterns_path).read_bytes()).hexdigest()
            }
        }


    def pendientes_vivos(self):
        out = []
        for v in self.data.get("pendientes_vivos") or []:
            if isinstance(v, dict) and v.get("front_id"):
                out.append(v)
        return out

    def review_pending(self, rows=None, cut_id=None, closing_candidate=None, latest_dX=None,
                       separation=None, discard_gap=None, absent_limit=None, **_k):
        vivos = self.pendientes_vivos()
        ids = [v.get("front_id") for v in vivos]
        return {
            "revisados": ids,
            "resueltos_a_favor": [],
            "resueltos_en_contra": [],
            "siguen_latentes": ids,
            "contradicen_cierre": [],
            "detalle": [],
        }

    @staticmethod
    def _pending_key(row) -> tuple:
        return (str(row.get("front_id")), str(row.get("cut_id")), str(row.get("reason")))

    def record_pending(self, **kwargs):
        # PATCH 011: escritura idempotente. Clave (front_id, cut_id, reason). Si ya existe con el mismo
        # input_sha o sin procedencia (legado), no se agrega otra vez: re-correr el mismo input no acumula.
        # Si existe pero de OTRA versión del input, se agrega la nueva (la vieja queda como contexto marcado).
        row = dict(kwargs)
        key = self._pending_key(row)
        sha = row.get("input_sha")
        for v in self.data.get("pendientes_vivos") or []:
            if isinstance(v, dict) and self._pending_key(v) == key:
                vs = v.get("input_sha")
                if vs is None or sha is None or vs == sha:
                    self.pending_dedup_011 = getattr(self, "pending_dedup_011", 0) + 1
                    return v
        self.data.setdefault("pendientes_vivos", []).append(row)
        if kwargs.get("save", True):
            self._touch(); self._save()
        return row

    def marcar_entrada_011(self, input_sha) -> bool:
        """PATCH 011: registra el input sha en el vault. Devuelve True si ya estaba (= repetición idéntica)."""
        if not input_sha:
            return False
        reg = self.data.setdefault("entradas_registradas_011", {})
        if input_sha in reg:
            return True
        reg[str(input_sha)] = {"primera_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        self._touch(); self._save()
        return False

    def pending_digest(self) -> str:
        raw = json.dumps(self.data.get("pendientes_vivos") or [], sort_keys=True, default=str)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _load_persistent_stinkbox_tokens(*, root: str | Path, exclude_case_ids: Iterable[str]) -> Dict[str, Any]:
    """Tokens persistentes de StinkBox que alimentan la siguiente corrida.

    Fuentes (solo lectura, nunca se escribe en ellas):
    - otros vaults stinkbox_<caso>.json bajo root. Se excluye el vault del caso
      actual (sus tokens ya estan en el vault que se esta transportando) y los
      *_RETENIDO / *_SIN_ULTIMO (estados alternos del mismo caso, no evidencia
      nueva).
    - stinkbox_tokens_descubiertos.json junto a este modulo: tokens descubiertos
      fuera de catalogo. Se cargan como evidencia; NUNCA se les inventa un
      equivalente ni entran al canon (equivalente null queda null, entra_a_canon
      false queda false). Solo cuentan en el solape favor/contra de cada patron,
      igual que cualquier otro token lateral.
    """
    excluded = {str(c).strip() for c in (exclude_case_ids or ()) if str(c).strip()}
    tokens: set = set()
    vaults: Dict[str, int] = {}
    root_path = Path(root)
    for path in sorted(root_path.glob("stinkbox_*.json")):
        stem = path.name[len("stinkbox_"):-len(".json")]
        if stem in excluded or stem.endswith("_RETENIDO") or stem.endswith("_SIN_ULTIMO"):
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        keys = {str(k).strip().casefold() for k in (data.get("token_frequency") or {}).keys() if str(k).strip()}
        if keys:
            vaults[path.name] = len(keys)
            tokens |= keys
    discovered_path = Path(__file__).resolve().parent / "stinkbox_tokens_descubiertos.json"
    discovered = []
    if discovered_path.is_file():
        try:
            d = json.loads(discovered_path.read_text(encoding="utf-8"))
            for row in (d.get("tokens") or []):
                if isinstance(row, dict) and str(row.get("token") or "").strip():
                    discovered.append({
                        "token": str(row["token"]).strip().casefold(),
                        "case_id": row.get("case_id"),
                        "corte": row.get("corte"),
                        "eje": row.get("eje"),
                        "estado": row.get("estado"),
                        "equivalente": row.get("equivalente"),
                        "entra_a_canon": bool(row.get("entra_a_canon")),
                    })
        except Exception:
            discovered = []
    for row in discovered:
        tokens.add(row["token"])
    return {"tokens": sorted(tokens), "vaults": vaults, "discovered": discovered}


def capture_and_transport(*, case_id: str, root: str | Path, motor_output: Mapping[str, Any], lateral_features: Mapping[str, Any], patterns_path: str | Path, external_lights: Iterable[Mapping[str, Any]] = (), pending_case_id: str | None = None, caldero_neighbor_store_root: str | Path | None = None, input_sha: str | None = None, **_extra) -> Dict[str, Any]:
    box = StinkBox(pending_case_id or case_id, root)
    # PATCH 011: idempotencia por input sha. Si este input ya se registró en el vault, no se vuelven a
    # sumar trayectoria/tokens/coactivación/F10/latencia (re-correr lo mismo no infla contadores).
    repeticion = box.marcar_entrada_011(input_sha)

    # Persistent Caldero vocabulary: load it into StinkBox on every run so the
    # memory survives case completion and can feed the light bus later.
    # Historical neighbors are registered as available lights, but are NOT
    # activated merely because they exist. A current-run observation of the same
    # token is required for activation.
    neighbor_root = Path(caldero_neighbor_store_root) if caldero_neighbor_store_root else (Path(__file__).resolve().parent / "vecinos_caldero")
    neighbor_index = neighbor_root / "neighbor_index.json"
    persistent_tokens = []
    if neighbor_index.is_file():
        try:
            nd = json.loads(neighbor_index.read_text(encoding="utf-8"))
            persistent_tokens = sorted({str(k).strip().casefold() for k in (nd.get("neighbors") or {}).keys() if str(k).strip()})
            box.register_persistent_neighbor_lights(tokens=persistent_tokens, source="vecinos_caldero/neighbor_index.json")
        except Exception:
            persistent_tokens = []

    # Cable StinkBox persistente: los tokens de otros vaults y los descubiertos
    # alimentan esta corrida como evidencia. Solo lectura: no se escribe en sus
    # fuentes, no se inventan equivalentes, no se toca el canon. El vault del
    # caso actual se excluye: sus tokens ya estan en box.data.
    persistent = _load_persistent_stinkbox_tokens(
        root=box.root, exclude_case_ids={str(pending_case_id or case_id), str(case_id)})
    discovered_tokens = [r["token"] for r in persistent["discovered"]]
    if discovered_tokens:
        box.register_persistent_neighbor_lights(
            tokens=discovered_tokens, source="stinkbox_tokens_descubiertos.json",
            branch="stinkbox_discovered", stereotype="stinkbox_discovered_token")

    cuts = list(motor_output.get("cuts") or [])
    for i, c in enumerate(cuts):
        # R732 kappa/persistence are defined between adjacent trajectory steps.
        rcut = i + 1
        r732 = motor_output.get("R732") or {}
        dx = (r732.get("dX_norm") or [])
        pc = (r732.get("persist_cos") or [])
        kp = (r732.get("kappa_dir") or [])
        if not repeticion and i < len(dx) and i > 0 and (i - 1) < len(pc) and (i - 1) < len(kp):
            box.record_trajectory(cut_id=f"{c.get('corte', c.get('id', 'G_C'+str(rcut)))}", dX_norm=dx[i], persist_cos=pc[i-1], kappa_dir=kp[i-1])

    # External lights are explicitly post-FREEZE evidence/context.
    by_cut: Dict[str, list[str]] = defaultdict(list)
    for item in external_lights or []:
        if isinstance(item, Mapping):
            by_cut[str(item.get("cut") or item.get("corte") or "Z_TRABAJO")].append(str(item.get("token", "")))
        else:
            by_cut["Z_TRABAJO"].append(str(item))
    for source_name, payload in lateral_features.items():
        if isinstance(payload, Mapping):
            for key in ("favor", "contra", "clinico", "co_oficio", "tokens_favor", "tokens_contra", "unique_tokens"):
                vals = payload.get(key)
                if isinstance(vals, list):
                    by_cut["Z_TRABAJO"].extend(str(v) for v in vals)
            cal_in = payload.get("caldero_input")
            if isinstance(cal_in, Mapping):
                for row in cal_in.get("tokens_neighbors", []) if isinstance(cal_in.get("tokens_neighbors"), list) else []:
                    if isinstance(row, Mapping) and row.get("token"):
                        by_cut["Z_TRABAJO"].append(str(row["token"]))
            # Preserve explicitly supplied Formula-10 contradiction records.
            for row in payload.get("formula10_contradictions", []) if isinstance(payload.get("formula10_contradictions"), list) else []:
                if isinstance(row, Mapping) and not repeticion:
                    box.record_formula10(cut_id=str(row.get("cut_id", "Z_TRABAJO")), marker=row.get("marker"), context_tokens=row.get("context_tokens", []), source=source_name)
    for cut_id, tokens in (by_cut.items() if not repeticion else ()):
        box.archive_tokens(cut_id=cut_id, tokens=tokens, source="external_lights" if cut_id != "Z_TRABAJO" else "lateral_features")

    # Explicit F10 records may be supplied at case level through a lateral feature.
    pred_state = (motor_output.get("predictor") or {}).get("information_state") or {}
    if pred_state and not repeticion:
        box.record_latency(state=pred_state.get("state", "UNKNOWN"), reason=pred_state.get("reason", ""))
    transported = box.transport(patterns_path, extra_tokens=persistent["tokens"])
    transported["vault_path"] = str(box.path)
    transported["persistent_neighbor_tokens"] = list(box.data.get("persistent_neighbor_tokens") or [])
    transported["persistent_neighbor_lights"] = list(box.data.get("persistent_neighbor_lights") or [])
    transported["persistent_neighbor_activation_events"] = list(box.data.get("persistent_neighbor_activation_events") or [])
    transported["persistent_neighbor_store"] = str(neighbor_index)
    transported["idempotencia_011"] = {"input_sha": input_sha, "repeticion": bool(repeticion),
                                       "escrituras_omitidas": (["trajectory_events", "token_events/token_frequency/coactivation", "formula10", "latency_events"] if repeticion else []),
                                       "regla": "mismo input sha => no se vuelven a sumar contadores"}
    transported["persistent_input"] = {
        "version": "STINKBOX_PERSISTENT_INPUT_V0.1",
        "tokens_loaded": len(persistent["tokens"]),
        "tokens": persistent["tokens"],
        "vaults": persistent["vaults"],
        "discovered": persistent["discovered"],
        "rule": "solo lectura; sin equivalentes inventados; sin escritura en fuentes; sin mutacion del canon",
    }
    token_occurrences = sum(len(v) for v in by_cut.values())
    token_unique = sorted({str(t).strip().casefold() for vals in by_cut.values() for t in vals if str(t).strip()})
    token_events_total = len(box.data.get("token_events") or [])
    transported["token_persistence_audit"] = {
        "status": ("SKIPPED_IDEMPOTENT_REPLAY" if repeticion else ("NO_TOKEN_INPUT" if not token_unique else "TOKENS_PERSISTED")),
        "input_token_occurrences": token_occurrences,
        "input_unique_tokens": len(token_unique),
        "input_cut_buckets": len(by_cut),
        "persisted_token_events_total": token_events_total,
        "persisted_unique_tokens_total": len(box.data.get("token_frequency") or {}),
        "input_sha": input_sha,
        "note": "No se inventan tokens: NO_TOKEN_INPUT significa que las fuentes laterales no aportaron tokens en esta corrida."
    }
    return transported
