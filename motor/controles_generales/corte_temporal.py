"""corte_temporal.py — Corte temporal: ventana con fecha de cierre.

Una ventana de trabajo va de un inicio a una fecha de cierre:

- Solo entra información que ya existía hasta la fecha de cierre.
  Un dato posterior a la fecha de cierre se aparta (no entra, queda
  registrado como fuera de ventana).
- Al llegar a la fecha de cierre, la ventana se sella: el resultado
  queda cerrado y ya no admite más datos.

Las fechas son valores comparables (texto ISO ``AAAA-MM-DD``, fecha o
número): el proyecto anfitrión elige la representación; la ventana
solo exige que se puedan comparar con ``<=``.
"""

from __future__ import annotations

from typing import Any, List, Optional

from .tipos import Registro, VentanaSellada


class CorteTemporal:
    """Ventana temporal con fecha de cierre y sello."""

    def __init__(self, fecha_cierre: Any, fecha_inicio: Optional[Any] = None) -> None:
        self.fecha_cierre = fecha_cierre
        self.fecha_inicio = fecha_inicio
        self.sellada = False
        self.admitidos: List[dict] = []
        self.fuera_de_ventana: List[dict] = []
        self.bitacora: List[Registro] = []

    def admitir(self, dato: Any, fecha: Any, identificador: str = "") -> bool:
        """True si el dato entra (fecha <= fecha de cierre); si no, se aparta."""
        if self.sellada:
            raise VentanaSellada("la ventana ya está sellada: no admite más datos")
        if fecha > self.fecha_cierre:
            self.fuera_de_ventana.append(
                {"dato": dato, "fecha": fecha, "id": identificador}
            )
            self.bitacora.append(
                Registro(
                    "corte_temporal",
                    "fuera_de_ventana",
                    f"{identificador or dato!r} fecha {fecha} posterior al cierre {self.fecha_cierre}",
                )
            )
            return False
        self.admitidos.append({"dato": dato, "fecha": fecha, "id": identificador})
        return True

    def sellar(self) -> None:
        """Sella la ventana: el resultado queda cerrado."""
        self.sellada = True
        self.bitacora.append(
            Registro(
                "corte_temporal",
                "sellada",
                f"ventana sellada en {self.fecha_cierre} con {len(self.admitidos)} datos admitidos",
            )
        )
