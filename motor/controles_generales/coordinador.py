"""coordinador.py — Coordinador general de controles operativos.

Un solo objeto que reúne todos los controles del paquete y los aplica
en orden, con una bitácora común y un recibo final. El coordinador no
sabe nada del proyecto que lo usa: solo conoce unidades, fases,
piezas, salidas, contextos y ventanas, todo en términos genéricos.

Política operativa del coordinador (su única regla de conducta):
PARAR solo ante una parada dura declarada. Ante cualquier otro
obstáculo: CONTORNEAR y REGISTRAR. Nada pasa en silencio: cada
decisión, bypass y contorno queda en la bitácora y en el recibo.
"""

from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional, Sequence

from .compuerta_cierre import CompuertaCierre, DecisionCierre
from .corte_temporal import CorteTemporal
from .filtro_admision import Admision, FiltroAdmision
from .guardia_separacion import GuardiaSeparacion
from .secuencia_fases import SecuenciaFases
from .tipos import Registro, ResultadoControl, UnidadEntrada
from .verificador_integridad import VerificadorIntegridad
from .verificador_salida import VerificadorSalida


class CoordinadorControles:
    """Coordinador de controles operativos, agnóstico al proyecto anfitrión."""

    def __init__(
        self,
        fases: Sequence[str],
        campos_requeridos_salida: Optional[Sequence[str]] = None,
        orden_salida: Optional[Sequence[str]] = None,
        fecha_cierre_ventana: Optional[Any] = None,
        paradas_duras: Optional[Sequence[str]] = None,
        modo_filtro: str = "activo",
    ) -> None:
        self.filtro = FiltroAdmision(modo=modo_filtro)
        self.secuencia = SecuenciaFases(fases, paradas_duras=paradas_duras)
        self.integridad = VerificadorIntegridad()
        self.cierre = CompuertaCierre()
        self.verificador_salida = (
            VerificadorSalida(campos_requeridos_salida or [], orden=orden_salida)
            if campos_requeridos_salida is not None
            else None
        )
        self.ventana = (
            CorteTemporal(fecha_cierre_ventana)
            if fecha_cierre_ventana is not None
            else None
        )
        self._salida_verificada = False
        self._salida: Optional[Dict[str, Any]] = None

    # -- entrada -----------------------------------------------------
    def admitir_entrada(self, unidades: List[UnidadEntrada]) -> Admision:
        return self.filtro.filtrar(unidades)

    # -- flujo -------------------------------------------------------
    def completar_fase(self, fase: str) -> None:
        self.secuencia.completar(fase)

    def contornear(self, fase: str, obstaculo: str, accion: str) -> str:
        return self.secuencia.contornear(fase, obstaculo, accion)

    # -- piezas ------------------------------------------------------
    def verificar_pieza(self, nombre: str, texto: str, lenguaje: str = "python") -> Dict[str, object]:
        return self.integridad.verificar(nombre, texto, lenguaje=lenguaje)

    # -- salida ------------------------------------------------------
    def verificar_salida(self, salida: Mapping[str, Any], referencias_permitidas: Optional[Sequence[str]] = None) -> ResultadoControl:
        if self.verificador_salida is None:
            raise ValueError("este coordinador se creó sin contrato de salida")
        if referencias_permitidas is not None:
            self.verificador_salida.referencias_permitidas = set(referencias_permitidas)
        resultado = self.verificador_salida.verificar(salida)
        self._salida_verificada = resultado.conforme
        if resultado.conforme:
            self._salida = dict(salida)
        return resultado

    # -- contextos ---------------------------------------------------
    def guardia(self, contexto: Dict[str, Any], corte_id: str = "sin_id") -> GuardiaSeparacion:
        return GuardiaSeparacion(contexto, corte_id=corte_id)

    # -- cierre ------------------------------------------------------
    def evaluar_cierre(
        self,
        pendientes_vivos: Optional[List[str]] = None,
        contradicciones: Optional[List[str]] = None,
    ) -> DecisionCierre:
        return self.cierre.evaluar(
            pendientes_vivos=pendientes_vivos,
            contradicciones=contradicciones,
            secuencia_terminada=self.secuencia.terminada,
            salida_verificada=self._salida_verificada if self.verificador_salida else True,
        )

    # -- bitácora y recibo -------------------------------------------
    @property
    def bitacora(self) -> List[Registro]:
        registros: List[Registro] = []
        for control in (self.filtro, self.secuencia, self.integridad, self.cierre):
            registros.extend(control.bitacora)
        if self.verificador_salida is not None:
            registros.extend(self.verificador_salida.bitacora)
        if self.ventana is not None:
            registros.extend(self.ventana.bitacora)
        return registros

    def recibo(self) -> Dict[str, Any]:
        bypass_filtro = self.filtro.modo == "apagado"
        return {
            "fases_completadas": list(self.secuencia.completadas),
            "fases_pendientes": [f for f in self.secuencia.fases if f not in self.secuencia.completadas],
            "contornos": list(self.secuencia.contornos),
            "salida_verificada": self._salida_verificada,
            "ventana_sellada": self.ventana.sellada if self.ventana is not None else None,
            "bypass_filtro_apagado": bypass_filtro,
            "registros_bitacora": len(self.bitacora),
        }
