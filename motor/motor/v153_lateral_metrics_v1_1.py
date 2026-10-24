#!/usr/bin/env python3
"""
V15.3 lateral academic integration.

This module NEVER modifies the canonical engine.
It consumes an already-produced X[t, 732] trajectory and optional
Ricci-Forman lateral edges.

Python stdlib + numpy only.
"""

from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any, Callable, Iterable, Mapping, Sequence
import hashlib
import json
import math
import platform
import sys

import numpy as np

EPS = 1e-12
N_PATTERNS = 244
DIM = 732


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_json(obj: Any) -> str:
    payload = json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256_bytes(payload)


def validate_X(X: np.ndarray) -> np.ndarray:
    X = np.asarray(X, dtype=float)
    if X.ndim != 2 or X.shape[1] != DIM:
        raise ValueError(f"Expected X shape [T, {DIM}], got {X.shape}")
    if X.shape[0] < 2:
        raise ValueError("At least two temporal cuts are required.")
    if not np.isfinite(X).all():
        raise ValueError("X contains NaN or infinite values.")
    return X


def delta(X: np.ndarray) -> np.ndarray:
    X = validate_X(X)
    return np.diff(X, axis=0)


def delta2(X: np.ndarray) -> np.ndarray:
    X = validate_X(X)
    if X.shape[0] < 3:
        return np.empty((0, DIM))
    return X[2:] - 2.0 * X[1:-1] + X[:-2]


def row_norm(A: np.ndarray) -> np.ndarray:
    return np.linalg.norm(A, axis=1)


def safe_cos(a: np.ndarray, b: np.ndarray, eps: float = EPS) -> float:
    den = float(np.linalg.norm(a) * np.linalg.norm(b))
    if den <= eps:
        return float("nan")
    return float(np.dot(a, b) / den)


def trajectory_metrics(X: np.ndarray, eps: float = EPS) -> dict[str, Any]:
    X = validate_X(X)
    V = delta(X)
    speeds = row_norm(V)

    directions = np.full_like(V, np.nan)
    nz = speeds > eps
    directions[nz] = V[nz] / speeds[nz, None]

    A = delta2(X)

    persistence = []
    kappa_dir = []
    for t in range(1, len(V)):
        c = safe_cos(V[t-1], V[t], eps)
        persistence.append(c)
        kappa_dir.append(float(math.sqrt(max(0.0, 1.0 - c*c))) if math.isfinite(c) else float("nan"))

    kappa_ext = []
    # v_t corresponds X[t+1]-X[t]; a_t = v_{t+1}-v_t.
    for t in range(len(V)-1):
        v = V[t]
        a = V[t+1] - V[t]
        nv2 = float(np.dot(v, v))
        na2 = float(np.dot(a, a))
        va = float(np.dot(v, a))
        numerator = max(0.0, nv2 * na2 - va * va)
        denom = float((math.sqrt(nv2) ** 3) + eps)
        kappa_ext.append(float(math.sqrt(numerator) / denom))

    return {
        "n_cuts": int(X.shape[0]),
        "dimension": int(X.shape[1]),
        "delta_norm": speeds.tolist(),
        "delta2_norm": row_norm(A).tolist(),
        "persistence_cosine": persistence,
        "kappa_dir": kappa_dir,
        "kappa_ext": kappa_ext,
        "zero_velocity_count": int((~nz).sum()),
    }


def pattern_tensor(X: np.ndarray) -> np.ndarray:
    """X[t,732]=[P_t;A_t;C_t] -> Q[t,244,3]=[P_i,A_i,C_i]."""
    X = validate_X(X)
    return X.reshape(X.shape[0], 3, N_PATTERNS).transpose(0, 2, 1)


def pattern_pairwise_distance(X: np.ndarray) -> list[np.ndarray]:
    Q = pattern_tensor(X)
    out = []
    for Qt in Q:
        # 244 x 244 Euclidean distance matrix in the local P/A/C coordinates.
        diff = Qt[:, None, :] - Qt[None, :, :]
        out.append(np.linalg.norm(diff, axis=2))
    return out


def pattern_velocity_cosine(X: np.ndarray, eps: float = EPS) -> list[np.ndarray]:
    Q = pattern_tensor(X)
    DQ = np.diff(Q, axis=0)
    out = []
    for dQt in DQ:
        norms = np.linalg.norm(dQt, axis=1)
        dots = dQt @ dQt.T
        den = norms[:, None] * norms[None, :]
        M = np.full_like(dots, np.nan, dtype=float)
        np.divide(dots, den, out=M, where=den > eps)
        out.append(M)
    return out


def P_delta_correlation(X: np.ndarray) -> np.ndarray:
    """Correlation matrix of temporal P-differences across the 244 pattern axes."""
    X = validate_X(X)
    P = X[:, :N_PATTERNS]
    dP = np.diff(P, axis=0)
    if dP.shape[0] < 2:
        return np.full((N_PATTERNS, N_PATTERNS), np.nan)
    x = dP - np.mean(dP, axis=0, keepdims=True)
    cov = x.T @ x
    den = np.sqrt(np.diag(cov))[:, None] * np.sqrt(np.diag(cov))[None, :]
    out = np.full((dP.shape[1], dP.shape[1]), np.nan, dtype=float)
    np.divide(cov, den, out=out, where=den > np.finfo(float).eps)
    return out


def negative_curvature_mass(edges: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    """
    B(i)=sum_j weight_ij * max(0, -K_ij)
    K_ij is the existing lateral Ricci-Forman edge curvature.
    """
    by_node: dict[str, float] = {}
    used_edges = []
    for e in edges:
        u = str(e["source"])
        v = str(e["target"])
        w = float(e.get("weight", 1.0))
        k = float(e["ricci_forman"])
        contribution = w * max(0.0, -k)
        if contribution:
            by_node[u] = by_node.get(u, 0.0) + contribution
            by_node[v] = by_node.get(v, 0.0) + contribution
            used_edges.append({
                "source": u, "target": v, "weight": w,
                "ricci_forman": k, "negative_mass_contribution": contribution
            })
    total_incident_mass = float(sum(by_node.values()))
    return {
        "node_mass": dict(sorted(by_node.items(), key=lambda kv: (-kv[1], kv[0]))),
        "total_incident_mass": total_incident_mass,
        "contributing_edges": used_edges,
    }


def prefix_audit(
    X: np.ndarray,
    predictor: Callable[[np.ndarray], np.ndarray],
    prefix_cut: int,
    *,
    predictor_id: str,
    predictor_version: str,
) -> dict[str, Any]:
    """
    Enforces the API boundary: predictor receives X[:prefix_cut] only.
    The actual future is accessed only after predictor returns.
    prefix_cut is the number of observed cuts.
    """
    X = validate_X(X)
    if prefix_cut < 1 or prefix_cut >= X.shape[0]:
        raise ValueError("prefix_cut must leave at least one future cut for evaluation.")

    prefix = X[:prefix_cut].copy()
    prefix_hash = sha256_bytes(prefix.tobytes(order="C"))

    predicted = np.asarray(predictor(prefix), dtype=float)
    if predicted.shape != (DIM,):
        raise ValueError(f"Predictor must return shape ({DIM},), got {predicted.shape}")
    if not np.isfinite(predicted).all():
        raise ValueError("Prediction contains NaN or infinite values.")

    prediction_hash = sha256_bytes(predicted.tobytes(order="C"))

    # Future is deliberately accessed only after prediction.
    actual = X[prefix_cut].copy()
    actual_hash = sha256_bytes(actual.tobytes(order="C"))

    error_l2 = float(np.linalg.norm(predicted - actual))
    denom = float(np.linalg.norm(actual))
    relative_l2 = float(error_l2 / (denom + EPS))

    return {
        "predictor_id": predictor_id,
        "predictor_version": predictor_version,
        "prefix_cut": prefix_cut,
        "future_cut": prefix_cut + 1,
        "prefix_hash_sha256": prefix_hash,
        "prediction_hash_sha256": prediction_hash,
        "actual_future_hash_sha256": actual_hash,
        "future_accessed_during_predict": False,
        "error_l2": error_l2,
        "relative_l2": relative_l2,
    }


def run_sidecar(
    X: np.ndarray,
    ricci_edges: Iterable[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    X = validate_X(X)
    out = {
        "spec": "V15.3_LATERAL_ACADEMIC_INTEGRATION@1.0",
        "canonical_untouched": True,
        "trajectory": trajectory_metrics(X),
        "pattern_pairwise_distance": [
            m.tolist() for m in pattern_pairwise_distance(X)
        ],
        "pattern_velocity_cosine": [
            m.tolist() for m in pattern_velocity_cosine(X)
        ],
        "P_delta_correlation": P_delta_correlation(X).tolist(),
    }
    if ricci_edges is not None:
        out["negative_curvature_mass"] = negative_curvature_mass(ricci_edges)
    else:
        out["negative_curvature_mass"] = {
            "status": "NOT_PROVIDED",
            "node_mass": {},
            "total_incident_mass": 0.0,
            "contributing_edges": [],
        }
    return out


def environment_manifest() -> dict[str, Any]:
    return {
        "python": sys.version,
        "platform": platform.platform(),
        "numpy": np.__version__,
    }


if __name__ == "__main__":
    # Deterministic smoke test only; no project data are embedded here.
    rng = np.random.default_rng(20260922)
    X = rng.normal(size=(5, DIM))
    result = run_sidecar(X)
    print(json.dumps({
        "ok": True,
        "spec": result["spec"],
        "environment": environment_manifest(),
        "n_cuts": result["trajectory"]["n_cuts"],
        "dimension": result["trajectory"]["dimension"],
    }, indent=2))
