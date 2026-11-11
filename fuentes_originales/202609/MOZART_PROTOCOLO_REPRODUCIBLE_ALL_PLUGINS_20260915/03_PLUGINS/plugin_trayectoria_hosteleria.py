#!/usr/bin/env python3
"""SIDECAR — trayectoria_hosteleria_turno_sustancias
NO fusionar a patterns_final_v14.json (244 en disco).
Se carga en memoria con sidecar V15.1.

Oficio cocina/barra/sala: turno raro + desgaste + consumo.
Perfil de ventana, no destino.

Fuente primaria (Claude web 2026-09-07):
Bush & Lipari, SAMHSA CBHSQ Report, 16 abril 2015.
Alojamiento y alimentos #1 SUD 16.9% y #1 ilicitas 19.1%
entre 19 industrias. Mineria/construccion lideran binge
alcohol, no SUD general. La cita "3er lugar" estaba invertida.
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
    "fuente": "SAMHSA 2015 (Bush & Lipari, CBHSQ Report, 16 abril 2015): alojamiento y servicios de alimentos = 16.9% SUD, EL MAS ALTO de 19 industrias medidas (no 3o -- corregido tras verificar fuente primaria; mineria/construccion solo lideran en consumo excesivo de alcohol especificamente, no en SUD general).",
    "evidence_status": "secondary_verified",
}


def fusionar(lib: dict) -> dict:
    out = dict(lib)
    out[FICHA] = dict(PATRON)
    return out
