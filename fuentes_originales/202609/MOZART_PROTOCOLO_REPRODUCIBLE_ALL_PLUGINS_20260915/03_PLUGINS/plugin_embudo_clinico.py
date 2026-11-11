#!/usr/bin/env python3
"""PLUGIN_EMBUDO_CLINICO — provisional. No toca F del V5.

No depende de que Grok/ChatGPT/Marco recuerden en qué corte pegar el token.
Lee la SERIE de cortes ya corrida + los tokens de cada ventana.

Embudo:
  1. ¿El token clinico (consumo_sustancias, etc.) esta en ESTA ventana?
  2. ¿Hay co-token de oficio/itinerancia/cronicidad en ESA misma ventana?
  3. ¿En cuantas ventanas seguidas se sostiene?
  4. ¿La primera ventana de la vida (formacion) solo trae aprendizaje/casa?

Salidas (etiqueta, no pronostico):
  RUIDO_ALIAS     — clinico en cuna sin carretera/desorden local
  PERFIL_VENTANA  — clinico + co-token en ventanas de oficio; no es cierre
  SENAL_TEMPRANA  — clinico ↗ al menos 1 corte ANTES de un hecho de quiebre
                    que el texto de esa ventana aun no nombra (raro; hay
                    que marcarlo a mano el 'quiebre' o no existe)
  NO_APLICA       — no hubo token clinico

Sustancias_03 no se declara por un solo corte con alias.
Hace falta sosten + co-token.
"""
from __future__ import annotations

from typing import Dict, List, Sequence, Tuple

CLINICO = {"consumo_sustancias", "cronicidad_sintomatica", "estancamiento_crisis"}
CO_OFICIO = {
    "desgaste_cambaceo_itinerante", "aislamiento_social",
    "busqueda_riesgo", "presion_social", "caida",
}
CUNA = {"aprendizaje", "humildad", "alianza", "cotidiano"}


def _nombres(tokens: Sequence[Tuple[str, float]]) -> set:
    return {t for t, v in tokens if v >= 0.5}


def etiquetar(
    cortes: Sequence[Tuple[str, Sequence[Tuple[str, float]]]],
) -> Dict:
    filas = []
    for cid, toks in cortes:
        n = _nombres(toks)
        clin = bool(n & CLINICO)
        co = bool(n & CO_OFICIO)
        cuna = bool(n <= (CUNA | CLINICO | {"creatividad", "conocimiento"}) or
                    (n & CUNA and not (n & {"desgaste_cambaceo_itinerante", "cronicidad_sintomatica"})))
        if clin and not co:
            et = "RUIDO_ALIAS"
        elif clin and co:
            et = "PERFIL_VENTANA"
        else:
            et = "NO_APLICA"
        # cuna + clinico sin itinerancia = ruido aunque haya presion floja
        if clin and cid.lower().startswith("a") and "desgaste_cambaceo_itinerante" not in n:
            et = "RUIDO_ALIAS"
        filas.append({"corte": cid, "clinico": clin, "co_oficio": co, "etiqueta": et})

    sosten = 0
    max_sosten = 0
    for f in filas:
        if f["etiqueta"] == "PERFIL_VENTANA":
            sosten += 1
            max_sosten = max(max_sosten, sosten)
        else:
            sosten = 0

    if any(f["etiqueta"] == "RUIDO_ALIAS" for f in filas) and max_sosten == 0:
        global_et = "RUIDO_ALIAS"
    elif max_sosten >= 2:
        global_et = "PERFIL_SOSTENIDO"
    elif max_sosten == 1:
        global_et = "PERFIL_VENTANA"
    else:
        global_et = "NO_APLICA"

    return {
        "plugin": "EMBUDO_CLINICO",
        "global": global_et,
        "sosten_max": max_sosten,
        "nota": "PERFIL no es prediccion de cierre. SENAL_TEMPRANA no se declara sin quiebre aun no escrito.",
        "cortes": filas,
    }
