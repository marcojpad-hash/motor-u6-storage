"""
sidecar_lente_souriau.py
Lente lateral Souriau: Sol, Tierra, Balanza, Luna.

Candados:
  TOCA_F: NO
  TOCA_244: NO
  TOCA_Engine_V5: NO

Este módulo NO modifica P/A/C ni el catálogo de patrones.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any, Mapping, Sequence
import copy

FOCOS = ("sol", "tierra", "balanza", "luna")

@dataclass(frozen=True)
class Foco:
    valor: Any = None
    evidencia: str | None = None
    corte: int | None = None
    ventana: tuple[int, ...] = ()
    estado: str = "referencia"

class VentanaCiega:
    """Vista de cortes permitidos; impide acceso fuera de la ventana."""
    def __init__(self, cortes: Sequence[str], corte_actual: int):
        self._cortes = tuple(cortes)
        self.corte_actual = corte_actual

    def texto(self) -> str:
        return self._cortes[self.corte_actual]

    def get(self, indice: int) -> str:
        if indice < 0 or indice > self.corte_actual:
            raise IndexError(
                f"LOOKAHEAD_BLOCKED: corte {indice} fuera de la ventana "
                f"0..{self.corte_actual}"
            )
        return self._cortes[indice]

    def indices_disponibles(self) -> tuple[int, ...]:
        return tuple(range(self.corte_actual + 1))

def _evidencia(corte: Any, foco: str) -> tuple[Any, str | None]:
    """
    Adaptador deliberadamente agnóstico: la extracción semántica NO se
    inventa aquí. Acepta un mapping con los focos ya candidatos, o devuelve
    None. Así el sidecar puede recibir salidas de distintos extractores.
    """
    if isinstance(corte, Mapping):
        item = corte.get(foco)
        if isinstance(item, Mapping):
            return item.get("valor"), item.get("evidencia")
        if item is not None:
            return item, str(item)
    return None, None

def asignar_focos_por_corte(
    corte: Any,
    ventana_disponible: VentanaCiega | Sequence[str],
    corte_actual: int | None = None,
) -> dict[str, dict[str, Any]]:
    """
    Asigna candidatos sin mirar cortes futuros.
    Si se pasa una secuencia, corte_actual es obligatorio.
    """
    if isinstance(ventana_disponible, VentanaCiega):
        ventana = ventana_disponible
        idx = ventana.corte_actual
    else:
        if corte_actual is None:
            raise ValueError("corte_actual es obligatorio con una secuencia")
        ventana = VentanaCiega(ventana_disponible, corte_actual)
        idx = corte_actual

    if corte is not ventana.texto() and not isinstance(corte, Mapping):
        # No se usa para inferir información; solo evita mezclar un corte
        # externo con la ventana declarada.
        raise ValueError("CORTE_NO_COINCIDE_CON_VENTANA")

    salida = {}
    for foco in FOCOS:
        valor, evidencia = _evidencia(corte, foco)
        salida[foco] = asdict(Foco(
            valor=valor,
            evidencia=evidencia,
            corte=idx,
            ventana=ventana.indices_disponibles(),
            estado="referencia",
        ))
    return salida

def _norm(v: Any) -> str:
    return str(v).strip().casefold()

def _pac_tokens(pac_actual: Any) -> set[str]:
    if pac_actual is None:
        return set()
    if isinstance(pac_actual, Mapping):
        vals = []
        for v in pac_actual.values():
            vals.extend(v if isinstance(v, (list, tuple, set)) else [v])
        return {_norm(x) for x in vals if x is not None}
    if isinstance(pac_actual, (list, tuple, set)):
        return {_norm(x) for x in pac_actual if x is not None}
    return {_norm(pac_actual)}

def evaluar_entrada_freeze(
    historial_focos: Sequence[Mapping[str, Any]],
    pac_actual: Any,
    N: int = 3,
) -> dict[str, dict[str, Any]]:
    """
    Decide el estado por foco:
      - confirmada: mismo valor semántico en N cortes consecutivos.
      - corroborada: coincide con un token P/A/C del corte actual.
      - referencia: ninguna de las anteriores.

    N debe fijarse antes de ejecutar el caso; esta función no lo ajusta.
    """
    if N < 1:
        raise ValueError("N debe ser >= 1")
    if not historial_focos:
        return {f: {"estado": "referencia", "valor": None} for f in FOCOS}

    actual = historial_focos[-1]
    pac = _pac_tokens(pac_actual)
    salida = {}

    for foco in FOCOS:
        actual_item = actual.get(foco, {})
        valor = actual_item.get("valor") if isinstance(actual_item, Mapping) else None
        estado = "referencia"

        if valor is not None:
            clave = _norm(valor)
            consecutivos = 0
            for corte in reversed(historial_focos):
                item = corte.get(foco, {})
                v = item.get("valor") if isinstance(item, Mapping) else None
                if v is not None and _norm(v) == clave:
                    consecutivos += 1
                else:
                    break
            if consecutivos >= N:
                estado = "confirmada"
            elif clave in pac:
                estado = "corroborada"

        salida[foco] = {
            "estado": estado,
            "valor": valor,
            "entra_freeze": estado in {"confirmada", "corroborada"},
        }
    return salida

def copia_pac(pac: Any) -> Any:
    """Utilidad de prueba: copia profunda para comprobar no contaminación."""
    return copy.deepcopy(pac)
