#!/usr/bin/env python3
"""
Z-RI v0.2 — trayectoria y acoplamiento lateral.

Herramienta de laboratorio.
No modifica el motor ni los datos de cortes sellados.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from math import sqrt
from typing import Dict, List, Optional, Sequence, Tuple


Vector = Tuple[float, ...]


def norm(v: Vector) -> float:
    return sqrt(sum(x * x for x in v))


def distance(a: Vector, b: Vector) -> float:
    if len(a) != len(b):
        raise ValueError("Vectores de distinta dimensión.")
    return sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def cosine(a: Vector, b: Vector) -> Optional[float]:
    na, nb = norm(a), norm(b)
    if na == 0 or nb == 0:
        return None
    return sum(x * y for x, y in zip(a, b)) / (na * nb)


def delta(a: Vector, b: Vector) -> Vector:
    if len(a) != len(b):
        raise ValueError("Vectores de distinta dimensión.")
    return tuple(y - x for x, y in zip(a, b))


@dataclass(frozen=True)
class TracePoint:
    case_id: str
    cut_id: str
    layer_id: str
    input_hash: str
    run_hash: str
    vector: Vector
    sealed: bool = True
    parent_cut: Optional[str] = None

    def validate(self) -> None:
        if not self.sealed:
            raise ValueError("Un punto no sellado no puede entrar en la traza.")
        if not self.input_hash or not self.run_hash:
            raise ValueError("Faltan hashes obligatorios.")
        if not self.vector:
            raise ValueError("Vector vacío.")


@dataclass
class LayerTrace:
    layer_id: str
    points: List[TracePoint] = field(default_factory=list)

    def add(self, point: TracePoint) -> None:
        point.validate()
        if point.layer_id != self.layer_id:
            raise ValueError("layer_id inconsistente.")
        self.points.append(point)

    def deltas(self) -> List[Vector]:
        out = []
        for a, b in zip(self.points, self.points[1:]):
            out.append(delta(a.vector, b.vector))
        return out


@dataclass(frozen=True)
class CoupledState:
    case_id: str
    cut_id: str
    layer_vectors: Dict[str, Vector]
    pairwise_distance: Dict[Tuple[str, str], float]
    pairwise_cosine: Dict[Tuple[str, str], Optional[float]]


def couple_at_cut(
    case_id: str,
    cut_id: str,
    layer_points: Sequence[TracePoint],
) -> CoupledState:
    """
    Acoplamiento descriptivo: NO fusiona ni altera los vectores de origen.
    Las capas deben llegar ya normalizadas a un espacio comparable.
    """
    if not layer_points:
        raise ValueError("No hay capas para acoplar.")

    for p in layer_points:
        p.validate()

    dims = {len(p.vector) for p in layer_points}
    if len(dims) != 1:
        raise ValueError(
            "Las capas no están en la misma dimensión. "
            "Normalizar antes de acoplar."
        )

    vectors = {p.layer_id: p.vector for p in layer_points}
    dist = {}
    cos = {}

    ids = list(vectors)
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            key = (a, b)
            dist[key] = distance(vectors[a], vectors[b])
            cos[key] = cosine(vectors[a], vectors[b])

    return CoupledState(
        case_id=case_id,
        cut_id=cut_id,
        layer_vectors=vectors,
        pairwise_distance=dist,
        pairwise_cosine=cos,
    )


def convergence_summary(state: CoupledState) -> dict:
    """
    Resumen descriptivo. No declara convergencia por sí solo.
    """
    ds = list(state.pairwise_distance.values())
    cs = [x for x in state.pairwise_cosine.values() if x is not None]

    return {
        "cut_id": state.cut_id,
        "n_layers": len(state.layer_vectors),
        "mean_distance": sum(ds) / len(ds) if ds else None,
        "mean_cosine": sum(cs) / len(cs) if cs else None,
    }


if __name__ == "__main__":
    # Demo puramente estructural.
    pts = [
        TracePoint("DEMO", "C1", "zri", "ih1", "rh1", (0.0, 0.0)),
        TracePoint("DEMO", "C1", "tortugas", "ih1", "rh2", (0.1, 0.0)),
        TracePoint("DEMO", "C1", "negativo", "ih1", "rh3", (0.0, 0.1)),
    ]

    state = couple_at_cut("DEMO", "C1", pts)
    print(convergence_summary(state))
