"""guardia_separacion.py — Guardia de no cruce entre contextos.

Dos contextos no se mezclan:

1. Al entrar a un bloque protegido, la guardia toma una foto del
   contexto (copia profunda). Al salir, compara: si alguien mutó el
   contexto dentro del bloque, es contaminación y se levanta excepción.
2. La salida de una fase se valida contra campos prohibidos: si trae
   un campo que pertenece a otro contexto, se rechaza.

Uso:

    with GuardiaSeparacion(contexto, corte_id="paso-3") as guardia:
        ...
        guardia.validar_salida(salida_fase, campos_prohibidos={...})
"""

from __future__ import annotations

import copy
from typing import Any, Dict, Mapping, Optional, Sequence

from .tipos import ContextoContaminado, Registro


class GuardiaSeparacion:
    """Protege un contexto contra mutaciones y cruces de campos."""

    def __init__(self, contexto: Dict[str, Any], corte_id: str = "sin_id") -> None:
        self.corte_id = corte_id
        self._foto = copy.deepcopy(contexto)
        self._referencia = contexto
        self.bitacora: list = []

    def __enter__(self) -> "GuardiaSeparacion":
        return self

    def __exit__(self, tipo_exc, valor_exc, traza) -> bool:
        if self._referencia != self._foto:
            cambios = []
            claves = set(self._foto.keys()) | set(self._referencia.keys())
            for clave in sorted(claves):
                antes = self._foto.get(clave)
                despues = self._referencia.get(clave)
                if antes != despues:
                    cambios.append(f"{clave}: {antes!r} -> {despues!r}")
            self.bitacora.append(
                Registro(
                    "guardia_separacion",
                    "contaminacion",
                    f"[{self.corte_id}] contexto mutado: {'; '.join(cambios)}",
                )
            )
            raise ContextoContaminado(
                f"[{self.corte_id}] contexto mutado dentro de la guardia: "
                f"{'; '.join(cambios)}"
            )
        return False

    def validar_salida(
        self,
        salida: Mapping[str, Any],
        campos_prohibidos: Sequence[str],
        campos_permitidos: Optional[Sequence[str]] = None,
    ) -> None:
        """Rechaza una salida que traiga campos de otro contexto."""
        prohibidos = [c for c in salida if c in set(campos_prohibidos)]
        if prohibidos:
            self.bitacora.append(
                Registro(
                    "guardia_separacion",
                    "campo_prohibido",
                    f"[{self.corte_id}] campos prohibidos en salida: {prohibidos}",
                )
            )
            raise ContextoContaminado(
                f"[{self.corte_id}] salida trae campos prohibidos: {prohibidos}"
            )
        if campos_permitidos is not None:
            fuera = [c for c in salida if c not in set(campos_permitidos)]
            if fuera:
                self.bitacora.append(
                    Registro(
                        "guardia_separacion",
                        "campo_fuera_de_lista",
                        f"[{self.corte_id}] campos fuera de la lista permitida: {fuera}",
                    )
                )
                raise ContextoContaminado(
                    f"[{self.corte_id}] salida trae campos fuera de la lista permitida: {fuera}"
                )
