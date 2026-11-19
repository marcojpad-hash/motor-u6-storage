"""filtro_admision.py — Filtro de admisión de entrada.

Regla: solo entra lo objetivamente medible / verificable, con
procedencia. Lo demás no se borra: se aparta, tipado, en la traza.

El filtro nunca decide el resultado del trabajo: solo separa dato de
valoración. Un texto que hable del propio filtro, o que mencione una
palabra de valoración sin usarla como valoración, no se aparta entero.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from .tipos import Registro, UnidadEntrada

# Marcas que hacen admisible a una unidad (dato observable/verificable).
MARCAS_ADMISIBLES = frozenset({"observable", "medible", "verificable", "registrado"})

# Marcas que tipan lo apartado (valoración, no dato). El tipo queda en
# la traza; el contenido original nunca se pierde.
MARCAS_APARTADO = frozenset({"juicio", "opinion", "atribucion", "figura", "conclusion", "intencion"})


@dataclass
class Admision:
    """Resultado de filtrar un lote de unidades."""

    admitidas: List[UnidadEntrada] = field(default_factory=list)
    apartadas: List[Dict[str, object]] = field(default_factory=list)
    # Cada apartado: {"unidad": UnidadEntrada, "tipo": str, "motivo": str}

    @property
    def total(self) -> int:
        return len(self.admitidas) + len(self.apartadas)


class FiltroAdmision:
    """Filtro de admisión. Modos:

    - ``activo`` (defecto): lo admitido sigue; lo apartado queda en la
      traza, no se borra.
    - ``solo_traza``: analiza sin modificar nada (todo sigue, todo se anota).
    - ``apagado``: no filtra. El apagado queda marcado en el recibo del
      coordinador como bypass: nunca pasa en silencio.
    """

    MODOS = ("activo", "solo_traza", "apagado")

    def __init__(
        self,
        modo: str = "activo",
        verificadores: Optional[List[Callable[[UnidadEntrada], bool]]] = None,
    ) -> None:
        if modo not in self.MODOS:
            raise ValueError(f"modo desconocido: {modo!r} (esperado uno de {self.MODOS})")
        self.modo = modo
        # Verificadores extra del proyecto anfitrión: cada uno recibe la
        # unidad y dice si es verificable por sus propios medios. Si el
        # proyecto no registra ninguno, valen solo las marcas.
        self.verificadores: List[Callable[[UnidadEntrada], bool]] = list(verificadores or [])
        self.bitacora: List[Registro] = []

    def _es_verificable(self, unidad: UnidadEntrada) -> bool:
        if unidad.marcas & MARCAS_ADMISIBLES:
            return True
        return any(v(unidad) for v in self.verificadores)

    def _tipo_apartado(self, unidad: UnidadEntrada) -> str:
        for marca in sorted(unidad.marcas & MARCAS_APARTADO):
            return marca
        if not unidad.procedencia:
            return "sin_procedencia"
        return "no_verificable"

    def filtrar(self, unidades: List[UnidadEntrada]) -> Admision:
        admision = Admision()
        for unidad in unidades:
            if self.modo == "apagado":
                admision.admitidas.append(unidad)
                continue
            if self.modo == "solo_traza":
                admision.admitidas.append(unidad)
                if not self._es_verificable(unidad) or (unidad.marcas & MARCAS_APARTADO):
                    tipo = self._tipo_apartado(unidad)
                    admision.apartadas.append(
                        {"unidad": unidad, "tipo": tipo, "motivo": "solo_traza: anotado, no apartado"}
                    )
                    self.bitacora.append(
                        Registro("filtro_admision", "anotado", f"tipo={tipo}", {"id": unidad.identificador})
                    )
                continue
            # modo activo: sin procedencia no hay nada verificable.
            if (
                (unidad.marcas & MARCAS_APARTADO)
                or not unidad.procedencia
                or not self._es_verificable(unidad)
            ):
                tipo = self._tipo_apartado(unidad)
                motivo = "sin_procedencia" if not unidad.procedencia else f"marca={tipo}"
                admision.apartadas.append({"unidad": unidad, "tipo": tipo, "motivo": motivo})
                self.bitacora.append(
                    Registro("filtro_admision", "apartado", f"tipo={tipo} motivo={motivo}", {"id": unidad.identificador})
                )
            else:
                admision.admitidas.append(unidad)
        return admision
