#!/usr/bin/env python3
"""PLUGIN_PREGUNTA_DETRAS — decimo hombre de la PREGUNTA.
No toca F ni p. No autorizar fusion.

El problema nunca es el problema. El problema es el falso problema:
la pregunta que el mapper/LLM va a responder si nadie la para.

Uso (humano o wrapper):
  from plugin_pregunta_detras import interrogar
  interrogar("que va a pasar con este cocinero")
"""
from __future__ import annotations

# pregunta de superficie -> default que el sistema suelta -> pregunta real
TRAMPAS = [
    (("quien es", "quién es"), "apellido / aristos", "que ↗ que no es el eje, en que ventana"),
    (("que va a pasar", "qué va a pasar", "que le va a pasar"), "desenlace dossier", "que se falsearia en el siguiente corte"),
    (("es adicto", "se muere", "se va a morir", "va a morir"), "DSM de biografia", "en QUE ventana hay evidencia clinica"),
    (("es ambicioso", "ambicion", "ambición"), "30_ambicion", "conquista sobre otros o agencia sobre si"),
    (("por que famoso", "por qué famoso", "es famoso"), "fama como causa", "fama es eje o laterales"),
    (("que ficha falta", "qué ficha falta"), "inventar 247", "que token FRIO no pegue"),
    (("el motor fallo", "el motor falló"), "culpa F", "el mapper pego el token caliente"),
]


def interrogar(pregunta_superficie: str) -> dict:
    p = (pregunta_superficie or "").lower()
    golpe = None
    for agujas, falso, real in TRAMPAS:
        if any(a in p for a in agujas):
            golpe = {"trampa": agujas[0], "falso_problema": falso, "pregunta_detras": real}
            break
    return {
        "plugin": "PREGUNTA_DETRAS",
        "superficie": pregunta_superficie,
        "golpe": golpe,
        "siempre": {
            "1_superficie": pregunta_superficie,
            "2_default_si_nadie_para": "aristos + Top-1 + desenlace",
            "3_detras": "que fuerza, que ventana, que token no puse, que la falsearia",
            "4_falso_si": "la respuesta no cambia si quito el apellido",
        },
    }
