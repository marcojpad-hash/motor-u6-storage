"""controles_generales — Coordinador general de controles operativos.

Paquete autónomo y agnóstico: no conoce al proyecto que lo usa. Solo
conoce unidades, fases, piezas, salidas, contextos y ventanas.
"""

from .compuerta_cierre import CompuertaCierre, DecisionCierre
from .coordinador import CoordinadorControles
from .corte_temporal import CorteTemporal
from .filtro_admision import Admision, FiltroAdmision
from .guardia_separacion import GuardiaSeparacion
from .secuencia_fases import SecuenciaFases
from .tipos import (
    CierreNoPermitido,
    ContextoContaminado,
    ControlRechazado,
    FaseFueraDeOrden,
    ParadaDura,
    PiezaNoIntegra,
    Registro,
    ResultadoControl,
    SalidaNoConforme,
    UnidadEntrada,
    VentanaSellada,
)
from .verificador_integridad import VerificadorIntegridad, huella
from .verificador_salida import VerificadorSalida

__all__ = [
    "Admision",
    "CierreNoPermitido",
    "CompuertaCierre",
    "ContextoContaminado",
    "ControlRechazado",
    "CoordinadorControles",
    "CorteTemporal",
    "DecisionCierre",
    "FaseFueraDeOrden",
    "FiltroAdmision",
    "GuardiaSeparacion",
    "ParadaDura",
    "PiezaNoIntegra",
    "Registro",
    "ResultadoControl",
    "SalidaNoConforme",
    "SecuenciaFases",
    "UnidadEntrada",
    "VentanaSellada",
    "VerificadorIntegridad",
    "VerificadorSalida",
    "huella",
]
