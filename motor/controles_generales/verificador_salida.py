"""verificador_salida.py — Verificación de salida contra su contrato.

La salida cumple el contrato cuando:
- trae todos los campos requeridos,
- ninguno está vacío (sin huecos),
- respeta el orden declarado (cuando el contrato lo fija),
- todo lo que referencia existe en las unidades admitidas: nada
  inventado, nada que no venga de la entrada admitida.

No verifica que la salida sea "correcta" en sentido de fondo: verifica
que esté completa, ordenada y anclada a lo admitido.
"""

from __future__ import annotations

from typing import Dict, List, Mapping, Optional, Sequence

from .tipos import Registro, ResultadoControl, SalidaNoConforme


class VerificadorSalida:
    """Verifica una salida (dict campo -> valor) contra un contrato."""

    def __init__(
        self,
        campos_requeridos: Sequence[str],
        orden: Optional[Sequence[str]] = None,
        referencias_permitidas: Optional[Sequence[str]] = None,
        campo_referencias: str = "referencias",
    ) -> None:
        self.campos_requeridos = list(campos_requeridos)
        self.orden = list(orden) if orden is not None else None
        # Identificadores de unidades admitidas que la salida puede citar.
        self.referencias_permitidas = set(referencias_permitidas or [])
        self.campo_referencias = campo_referencias
        self.bitacora: List[Registro] = []

    def verificar(self, salida: Mapping[str, object]) -> ResultadoControl:
        violaciones: List[str] = []
        for campo in self.campos_requeridos:
            if campo not in salida:
                violaciones.append(f"falta_campo:{campo}")
            elif salida[campo] in (None, "", [], {}):
                violaciones.append(f"hueco:{campo}")
        if self.orden is not None:
            # El orden es el de la salida tal como viene (el dict conserva
            # su orden de inserción): debe seguir el del contrato.
            presentes = [c for c in salida if c in self.orden]
            # El orden relativo de los campos presentes debe seguir el contrato.
            indices = [self.orden.index(c) for c in presentes]
            if indices != sorted(indices):
                violaciones.append("orden_incorrecto")
        refs = salida.get(self.campo_referencias)
        if isinstance(refs, (list, tuple, set)):
            for ref in refs:
                if ref not in self.referencias_permitidas:
                    violaciones.append(f"referencia_inventada:{ref}")
        conforme = not violaciones
        self.bitacora.append(
            Registro(
                "verificador_salida",
                "conforme" if conforme else "no_conforme",
                "; ".join(violaciones) if violaciones else "salida conforme al contrato",
            )
        )
        return ResultadoControl(
            conforme=conforme,
            motivo="conforme" if conforme else "; ".join(violaciones),
            violaciones=violaciones,
        )

    def exigir(self, salida: Mapping[str, object]) -> ResultadoControl:
        """Como verificar(), pero levanta excepción si no es conforme."""
        resultado = self.verificar(salida)
        if not resultado.conforme:
            raise SalidaNoConforme(f"salida no conforme: {resultado.motivo}")
        return resultado
