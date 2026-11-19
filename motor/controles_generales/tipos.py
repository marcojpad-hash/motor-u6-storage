"""tipos.py — Tipos compartidos del paquete controles_generales.

Solo stdlib. Ningún tipo aquí conoce al proyecto anfitrión: todo se
expresa en unidades, fases, piezas, salidas y contextos genéricos.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Registro:
    """Una entrada de la bitácora del coordinador.

    La bitácora es el registro trazable de todo lo que los controles
    hicieron: qué se admitió, qué se apartó, qué se contorneó, qué
    cambió y qué se cerró. Nada pasa en silencio.
    """

    control: str
    accion: str
    detalle: str = ""
    datos: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResultadoControl:
    """Resultado de aplicar un control a algo."""

    conforme: bool
    motivo: str = ""
    violaciones: List[str] = field(default_factory=list)
    detalle: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UnidadEntrada:
    """Una unidad de entrada que pide admisión.

    - ``contenido``: el texto o valor de la unidad.
    - ``procedencia``: de dónde viene (fuente + referencia exacta).
      Sin procedencia no hay nada verificable: la unidad no se admite.
    - ``marcas``: etiquetas de función de la unidad, por ejemplo
      ``observable``, ``medible``, ``verificable`` (admisibles) o
      ``juicio``, ``opinion``, ``atribucion``, ``figura``,
      ``conclusion`` (no admisibles: son valoración, no dato).
    """

    contenido: str
    procedencia: str = ""
    marcas: frozenset = frozenset()
    identificador: str = ""


class ControlRechazado(Exception):
    """Un control rechazó algo: la operación no procede."""


class FaseFueraDeOrden(Exception):
    """Se intentó completar una fase sin haber completado las anteriores."""


class ParadaDura(Exception):
    """Obstáculo en la lista de paradas duras: aquí sí se para."""


class PiezaNoIntegra(Exception):
    """Una pieza registrada no es íntegra (no compila / está corrupta)."""


class SalidaNoConforme(Exception):
    """La salida no cumple su contrato."""


class CierreNoPermitido(Exception):
    """Se pidió cerrar cuando la compuerta de cierre dice LATENTE."""


class ContextoContaminado(Exception):
    """Un contexto protegido fue mutado, o una salida trae campos prohibidos."""


class VentanaSellada(Exception):
    """La ventana temporal ya se selló: no admite más datos."""
