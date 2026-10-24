#!/usr/bin/env python3
"""
Z-RI v0.1
Capa lateral experimental: experiencia retrospectiva incremental.

NO toca el motor canónico, patterns/244 ni resultados sellados.
"""

from __future__ import annotations
from dataclasses import dataclass, asdict
from hashlib import sha256
from typing import Optional, Tuple


def clip(x: float, lo: float = -1.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, float(x)))


def rank_error(rank: Optional[int], k: int = 5) -> float:
    """Mapea rango real dentro/fuera de Top-K a [-1, 1]."""
    if rank is None or rank < 1 or rank > k:
        return -1.0
    if k <= 1:
        return 1.0
    return clip(1.0 - 2.0 * (rank - 1) / (k - 1))


@dataclass(frozen=True)
class CutSeal:
    case_id: str
    cut_id: str
    input_hash: str
    top5: Tuple[str, ...]
    hypothesis: str
    run_hash: str
    sealed: bool = True

    def assert_valid(self) -> None:
        if not self.sealed:
            raise ValueError("Z-RI: no existe resultado antes del sellado.")
        if not self.input_hash or not self.run_hash:
            raise ValueError("Z-RI: input_hash y run_hash son obligatorios.")
        if len(self.top5) != 5:
            raise ValueError("Z-RI v0.1 exige Top-5.")


@dataclass(frozen=True)
class ReleasedResult:
    target: str
    rank_in_topk: Optional[int]
    q_observed: float
    block_observed: float
    lamp_observed: int


@dataclass(frozen=True)
class Experience:
    e_rank: float
    e_margin: float
    e_block: float
    e_lamp: float

    def vector(self) -> Tuple[float, float, float, float]:
        return (self.e_rank, self.e_margin, self.e_block, self.e_lamp)


@dataclass(frozen=True)
class ExperienceMemory:
    values: Tuple[float, float, float, float]
    alpha: float  # peso de la experiencia nueva

    def update(self, e: Experience) -> "ExperienceMemory":
        a = self.alpha
        old = self.values
        new = tuple(clip((1.0 - a) * old[i] + a * e.vector()[i])
                    for i in range(4))
        return ExperienceMemory(new, a)


def make_experience(
    *,
    rank_in_topk: Optional[int],
    k: int,
    q_predicted: float,
    q_observed: float,
    block_expected: float,
    block_observed: float,
    lamp_expected: int,
    lamp_observed: int,
) -> Experience:
    """
    Calcula E_n SOLO después de que el corte fue sellado
    y su resultado fue liberado.
    """
    e_rank = rank_error(rank_in_topk, k)
    e_margin = clip(q_observed - q_predicted)
    e_block = clip(block_expected - block_observed)
    e_lamp = clip(float(lamp_expected) - float(lamp_observed))

    return Experience(e_rank, e_margin, e_block, e_lamp)


def canonical_payload(seal: CutSeal) -> str:
    """
    Huella reproducible del sello. No incluye ningún resultado posterior.
    """
    raw = (
        f"{seal.case_id}|{seal.cut_id}|{seal.input_hash}|"
        f"{'|'.join(seal.top5)}|{seal.hypothesis}|{seal.run_hash}|{seal.sealed}"
    )
    return sha256(raw.encode("utf-8")).hexdigest()


def release_and_compute(
    seal: CutSeal,
    result: ReleasedResult,
    *,
    q_predicted: float,
    block_expected: float,
    lamp_expected: int,
    k: int = 5,
) -> Experience:
    """
    Flujo protegido:
      1) valida sello
      2) solo entonces acepta resultado
      3) calcula experiencia lateral

    No hay función que modifique `seal`.
    """
    seal.assert_valid()

    if result.target in seal.top5:
        rank = seal.top5.index(result.target) + 1
    else:
        rank = None

    # Si el resultado trae un rank explícito, se verifica contra el Top-K.
    if result.rank_in_topk != rank:
        raise ValueError(
            f"Rank inconsistente: Top-5 da {rank}, "
            f"resultado declara {result.rank_in_topk}."
        )

    return make_experience(
        rank_in_topk=rank,
        k=k,
        q_predicted=q_predicted,
        q_observed=result.q_observed,
        block_expected=block_expected,
        block_observed=result.block_observed,
        lamp_expected=lamp_expected,
        lamp_observed=result.lamp_observed,
    )


if __name__ == "__main__":
    # Demo mínimo: NO representa una corrida V15.1 real.
    seal = CutSeal(
        case_id="DEMO",
        cut_id="C1",
        input_hash="INPUT_HASH_C1",
        top5=("A", "B", "C", "D", "E"),
        hypothesis="A",
        run_hash="RUN_HASH_C1",
    )

    print("seal_hash:", canonical_payload(seal))

    released = ReleasedResult(
        target="B",
        rank_in_topk=2,
        q_observed=0.50,
        block_observed=0.70,
        lamp_observed=0,
    )

    exp = release_and_compute(
        seal,
        released,
        q_predicted=0.80,
        block_expected=0.90,
        lamp_expected=1,
    )

    print("E1 =", asdict(exp))

    memory = ExperienceMemory(values=(0.0, 0.0, 0.0, 0.0), alpha=0.5)
    print("M1 =", memory.update(exp).values)
