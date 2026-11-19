#!/usr/bin/env python3
"""adaptador_proyecto_a_controles_generales.py — EJEMPLO de adaptador fino.

Este archivo vive FUERA del paquete agnóstico ``controles_generales`` y
es el único lugar que conoce ambos lados: las estructuras propias del
proyecto anfitrión y los controles genéricos. El coordinador nunca
importa nada del proyecto; el adaptador traduce en ambos sentidos.

NO está cableado a ninguna ruta: es documentación ejecutable. Para
usarlo de verdad, el proyecto copia este patrón con sus estructuras
reales y lo llama desde su propia puerta de entrada.

Correspondencia que implementa este ejemplo (proyecto anfitrión -> genérico):

- filtro de entrada del proyecto (solo lo objetivamente medible;
  el juicio es ruido tipado que se anota aparte)
  -> ``FiltroAdmision`` (marcas ``observable``/``medible``/``verificable``;
  marcas de juicio -> apartado tipado).
- control de flujo del proyecto (orden de fases; ante un obstáculo,
  contornear y registrar; parar solo en parada dura)
  -> ``SecuenciaFases`` + ``CoordinadorControles.contornear``.
- candado de piezas del proyecto (la pieza debe compilar y su huella
  conocida; un cambio de huella se avisa y se registra, no bloquea)
  -> ``VerificadorIntegridad``.
- verificación de salida del proyecto (la salida cumple su contrato:
  completa, sin huecos, sin datos inventados, en orden)
  -> ``VerificadorSalida``.
- compuerta de cierre del proyecto (cierre solo sin pendientes vivos
  ni contradicciones sin resolver; si no, LATENTE)
  -> ``CompuertaCierre``.
- guardia de no cruce del proyecto (un contexto no contamina a otro;
  foto al entrar, comparación al salir; campos prohibidos en salida)
  -> ``GuardiaSeparacion``.
- compuerta de entrada temporal del proyecto (solo información existente
  hasta la fecha de cierre; nada futuro; sello al cerrar)
  -> ``CorteTemporal``.
- protocolo de conducta del proyecto (parar solo en excepción rara;
  ante un problema operativo, contornear y reportar)
  -> política operativa del ``CoordinadorControles`` (paradas duras
  declaradas; todo lo demás se contornea y se registra).
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from controles_generales import CoordinadorControles, UnidadEntrada  # noqa: E402


def adaptar_unidades(registros_proyecto):
    """Traduce registros del proyecto a unidades genéricas.

    Entrada esperada (dicts del proyecto): cada registro trae ``texto``,
    ``fuente`` (procedencia) y ``clase``: ``"dato"`` para lo observable /
    medible, o la clase de valoración (``"juicio"``, ``"opinion"``,
    ``"atribucion"``, ``"figura"``, ``"conclusion"``, ``"intencion"``).
    """
    unidades = []
    for i, reg in enumerate(registros_proyecto):
        clase = reg.get("clase", "dato")
        marcas = {"observable", "medible"} if clase == "dato" else {clase}
        unidades.append(
            UnidadEntrada(
                contenido=reg.get("texto", ""),
                procedencia=reg.get("fuente", ""),
                marcas=frozenset(marcas),
                identificador=reg.get("id", f"r{i}"),
            )
        )
    return unidades


def ejemplo_uso(registros_proyecto):
    """Recorrido completo con el adaptador: entrada -> fases -> salida -> cierre."""
    coord = CoordinadorControles(
        fases=["entrada", "proceso", "cierre"],
        campos_requeridos_salida=["resumen", "referencias"],
        orden_salida=["resumen", "referencias"],
        paradas_duras=["pieza_canonica_corrupta"],
    )
    admision = coord.admitir_entrada(adaptar_unidades(registros_proyecto))
    coord.completar_fase("entrada")
    coord.completar_fase("proceso")
    salida = {
        "resumen": "; ".join(u.contenido for u in admision.admitidas),
        "referencias": [u.identificador for u in admision.admitidas],
    }
    coord.verificar_salida(
        salida, referencias_permitidas=[u.identificador for u in admision.admitidas]
    )
    coord.completar_fase("cierre")
    decision = coord.evaluar_cierre()
    return {"decision": decision.decision, "recibo": coord.recibo()}


if __name__ == "__main__":
    resultado = ejemplo_uso(
        [
            {"id": "r1", "texto": "dato medible 1", "fuente": "registro 1", "clase": "dato"},
            {"id": "r2", "texto": "valoración subjetiva", "fuente": "registro 1", "clase": "juicio"},
        ]
    )
    print(resultado["decision"])
    print(resultado["recibo"])
