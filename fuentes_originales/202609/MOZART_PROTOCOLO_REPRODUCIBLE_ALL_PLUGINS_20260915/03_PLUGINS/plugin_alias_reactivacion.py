#!/usr/bin/env python3
"""PLUGIN_ALIAS_REACTIVACION — provisional. No toca V5 ni el 244.

Problema: sustancias_* y trayectoria_musicos_* exigen
consumo_sustancias, desgaste_cambaceo_itinerante, aislamiento_social.
El texto lavado dice desorden, carretera, soledad. El mapper
pone caida/presion y esas fichas se quedan en 0.5.

Esto NO sube p solo. Traduce sinonimos del texto lavado
al lexico que YA existe. Agente2 pobre.

Uso:
  from plugin_alias_reactivacion import traducir
  tokens = traducir([('caida', 0.82), ('presion_social', 0.86)],
                    hechos='periodos de desorden, desplazamientos')
"""
from __future__ import annotations

from typing import List, Sequence, Tuple

# lavado -> token canonico (peso tope si el hecho esta)
ALIAS = {
    "desorden": "consumo_sustancias",
    "irregular": "consumo_sustancias",
    "habitos": "consumo_sustancias",
    "trago": "consumo_sustancias",
    "alcohol": "consumo_sustancias",
    "carretera": "desgaste_cambaceo_itinerante",
    "desplazamientos": "desgaste_cambaceo_itinerante",
    "horarios": "desgaste_cambaceo_itinerante",
    "itinerante": "desgaste_cambaceo_itinerante",
    "soledad": "aislamiento_social",
    "aislamiento": "aislamiento_social",
    "agencia": "inconformismo",
    "control sobre su trabajo": "desafio_autoridad",
}


def traducir(
    tokens: Sequence[Tuple[str, float]],
    hechos: str = "",
    peso: float = 0.78,
) -> List[Tuple[str, float]]:
    out = list(tokens)
    have = {t for t, _ in out}
    h = (hechos or "").lower()
    for needle, canon in ALIAS.items():
        if needle in h and canon not in have:
            out.append((canon, peso))
            have.add(canon)
    return out


def faltaron(hechos: str, board: dict, piso: float = 0.55) -> list:
    """Auditor: el texto pedia X y el tablero no lo encendio."""
    flags = []
    h = (hechos or "").lower()
    if any(w in h for w in ("desorden", "trago", "alcohol", "irregular")):
        if board.get("sustancias_01_leve", 0) < piso and board.get("sustancias_02_moderado", 0) < piso:
            flags.append("sustancias_* pedida por texto y no prendio")
    if any(w in h for w in ("carretera", "desplazamientos", "musicos", "grabaciones")):
        if board.get("trayectoria_musicos_populares", 0) < piso:
            flags.append("trayectoria_musicos pedida y no prendio")
    return flags
