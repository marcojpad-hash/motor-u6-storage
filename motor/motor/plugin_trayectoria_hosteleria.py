#!/usr/bin/env python3
"""SIDECAR — trayectoria_hosteleria_turno_sustancias
NO fusionar a patterns_final_v14.json hasta Claude.
Se carga en memoria como Otto/fama.

Hecho de oficio (misma familia que musicos / policia / trailer):
turnos atipicos + desgaste + consumo. No es destino.
Fuente: SAMHSA 2015 — industria restaurantera 3a en tasa de
abuso de sustancias entre profesiones (EE.UU.), detras de
mineria y construccion. evidence_status: secondary_verified.
Autorizado Claude 2026-09-07. No es destino.

Tokens: solo lexico 244 ya existente.
"""
from __future__ import annotations

FICHA = "trayectoria_hosteleria_turno_sustancias"

PATRON = {
    "description": (
        "Oficio de cocina/barra/sala: turno raro, desgaste, "
        "co-ocurrencia frecuente con consumo. Perfil de ventana, "
        "no prediccion de cierre."
    ),
    "tokens_favor": {
        "consumo_sustancias": 0.8,
        "turno_atipico_nocturno": 0.8,
        "desgaste_psicosocial": 0.7,
        "desgaste_cambaceo_itinerante": 0.55,
        "aislamiento_social": 0.5,
    },
    "tokens_contra": {
        "estabilidad_horario": 0.85,
        "entorno_controlado_oficina": 0.8,
    },
    "fuente": "SAMHSA 2015; restaurantes 3er oficio en abuso de sustancias (EE.UU.), tras mineria y construccion.",
    "evidence_status": "secondary_verified",
}


def fusionar(lib: dict) -> dict:
    out = dict(lib)
    out[FICHA] = dict(PATRON)
    return out
