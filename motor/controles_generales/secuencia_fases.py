"""secuencia_fases.py — Candados de flujo: orden de fases y contornos.

El trabajo se declara como fases en orden. No se puede completar una
fase sin haber completado las anteriores: saltarse pasos está prohibido.

Ante un obstáculo la conducta es: contornear + registrar, no parar.
Solo se para cuando el obstáculo está en la lista de paradas duras
declarada al crear la secuencia. Cada contorno queda en la bitácora.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Sequence

from .tipos import FaseFueraDeOrden, ParadaDura, Registro


class SecuenciaFases:
    """Fases ordenadas con candado de orden y política de contorno."""

    def __init__(
        self,
        fases: Sequence[str],
        paradas_duras: Optional[Sequence[str]] = None,
    ) -> None:
        if not fases:
            raise ValueError("la secuencia necesita al menos una fase")
        if len(set(fases)) != len(fases):
            raise ValueError("las fases no se pueden repetir")
        self.fases: List[str] = list(fases)
        self.paradas_duras = set(paradas_duras or [])
        self.completadas: List[str] = []
        self.contornos: List[Dict[str, str]] = []
        self.bitacora: List[Registro] = []

    @property
    def siguiente(self) -> Optional[str]:
        for fase in self.fases:
            if fase not in self.completadas:
                return fase
        return None

    @property
    def terminada(self) -> bool:
        return len(self.completadas) == len(self.fases)

    def completar(self, fase: str) -> None:
        if fase not in self.fases:
            raise ValueError(f"fase desconocida: {fase!r}")
        if fase in self.completadas:
            raise ValueError(f"fase ya completada: {fase!r}")
        pendientes = [f for f in self.fases[: self.fases.index(fase)] if f not in self.completadas]
        if pendientes:
            raise FaseFueraDeOrden(
                f"no se puede completar {fase!r} antes que {pendientes!r}"
            )
        self.completadas.append(fase)
        self.bitacora.append(Registro("secuencia_fases", "completada", fase))

    def contornear(self, fase: str, obstaculo: str, accion: str) -> str:
        """Registra un contorno ante un obstáculo y devuelve la acción a seguir.

        Si el obstáculo es una parada dura, se para (excepción) en vez de
        contornear. El contorno no marca la fase como completada: solo
        deja registrado cómo se siguió adelante.
        """
        if obstaculo in self.paradas_duras:
            self.bitacora.append(
                Registro("secuencia_fases", "parada_dura", obstaculo, {"fase": fase})
            )
            raise ParadaDura(f"parada dura en {fase!r}: {obstaculo}")
        registro = {"fase": fase, "obstaculo": obstaculo, "accion": accion}
        self.contornos.append(registro)
        self.bitacora.append(
            Registro("secuencia_fases", "contorno", f"{fase}: {obstaculo} -> {accion}", registro)
        )
        return accion
