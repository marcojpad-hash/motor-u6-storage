"""compuerta_cierre.py — Compuerta de cierre.

El trabajo se da por terminado solo cuando no queda nada vivo que lo
contradiga:

- sin pendientes vivos,
- sin contradicciones sin resolver,
- con la secuencia de fases completa,
- con la salida verificada (cuando se declaró que hacía falta).

Si algo de eso falta, la decisión es LATENTE: no es un cierre, es un
"todavía no". Lo no resuelto nunca es cierre.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .tipos import Registro


@dataclass
class DecisionCierre:
    decision: str  # "CERRADO" o "LATENTE"
    motivos: List[str] = field(default_factory=list)

    @property
    def cerrado(self) -> bool:
        return self.decision == "CERRADO"


class CompuertaCierre:
    """Decide si un trabajo puede darse por terminado."""

    def __init__(self) -> None:
        self.bitacora: List[Registro] = []

    def evaluar(
        self,
        pendientes_vivos: Optional[List[str]] = None,
        contradicciones: Optional[List[str]] = None,
        secuencia_terminada: bool = True,
        salida_verificada: bool = True,
    ) -> DecisionCierre:
        motivos: List[str] = []
        for pendiente in pendientes_vivos or []:
            motivos.append(f"pendiente_vivo:{pendiente}")
        for contradiccion in contradicciones or []:
            motivos.append(f"contradiccion_sin_resolver:{contradiccion}")
        if not secuencia_terminada:
            motivos.append("secuencia_incompleta")
        if not salida_verificada:
            motivos.append("salida_sin_verificar")
        decision = DecisionCierre(
            decision="LATENTE" if motivos else "CERRADO", motivos=motivos
        )
        self.bitacora.append(
            Registro(
                "compuerta_cierre",
                decision.decision.lower(),
                "; ".join(motivos) if motivos else "nada vivo: cierre permitido",
            )
        )
        return decision
