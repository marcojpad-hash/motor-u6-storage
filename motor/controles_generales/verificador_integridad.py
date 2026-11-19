"""verificador_integridad.py — Candado de integridad de piezas.

Antes de confiar en una pieza (un módulo, un archivo, un fragmento de
código que el trabajo va a usar), se verifica que sea íntegra:

1. Compila / tiene sintaxis válida (para texto de código).
2. No trae señales típicas de corrupción (caracteres que delatan haber
   pasado por un editor de texto enriquecido).
3. Su huella coincide con el manifiesto conocido, si lo hay.

Un cambio de huella no bloquea: se avisa, se registra en la bitácora y
se actualiza el manifiesto. Las ediciones legítimas existen, pero nunca
pasan en silencio. Lo que sí bloquea es una pieza corrupta.
"""

from __future__ import annotations

import ast
import hashlib
from typing import Dict, List, Optional

from .tipos import PiezaNoIntegra, Registro

# Señales de corrupción típica por pegar código en editores enriquecidos.
SENALES_CORRUPCION = {
    "comillas_curvas": ["\u201c", "\u201d", "\u2018", "\u2019"],
    "guion_largo_o_menos": ["\u2013", "\u2014", "\u2212"],
}


def huella(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


class VerificadorIntegridad:
    """Verifica piezas de texto antes de confiar en ellas."""

    def __init__(self, manifiesto: Optional[Dict[str, str]] = None) -> None:
        # manifiesto: nombre de pieza -> huella conocida.
        self.manifiesto: Dict[str, str] = dict(manifiesto or {})
        self.bitacora: List[Registro] = []

    def _senales_corrupcion(self, texto: str) -> List[str]:
        hallazgos = []
        for nombre, caracteres in SENALES_CORRUPCION.items():
            if any(c in texto for c in caracteres):
                hallazgos.append(nombre)
        return hallazgos

    def verificar(
        self, nombre: str, texto: str, lenguaje: str = "python"
    ) -> Dict[str, object]:
        """Verifica una pieza. Devuelve su estado.

        - ``integra`` False + excepción si no compila o está corrupta.
        - ``cambio_huella`` True si la huella difiere del manifiesto: se
          avisa y se actualiza, sin bloquear.
        """
        if lenguaje == "python":
            try:
                ast.parse(texto)
            except SyntaxError as exc:
                self.bitacora.append(
                    Registro("verificador_integridad", "rechazada", f"{nombre}: no compila: {exc}")
                )
                raise PiezaNoIntegra(f"pieza {nombre!r} no compila: {exc}") from exc
        senales = self._senales_corrupcion(texto)
        if senales:
            self.bitacora.append(
                Registro("verificador_integridad", "rechazada", f"{nombre}: corrupción: {senales}")
            )
            raise PiezaNoIntegra(f"pieza {nombre!r} trae señales de corrupción: {senales}")
        nueva_huella = huella(texto)
        conocida = self.manifiesto.get(nombre)
        cambio = conocida is not None and conocida != nueva_huella
        if cambio:
            self.bitacora.append(
                Registro(
                    "verificador_integridad",
                    "cambio_huella",
                    f"{nombre}: {conocida[:12]} -> {nueva_huella[:12]}",
                    {"nombre": nombre},
                )
            )
        self.manifiesto[nombre] = nueva_huella
        return {"nombre": nombre, "integra": True, "huella": nueva_huella, "cambio_huella": cambio}
