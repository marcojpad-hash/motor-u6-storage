"""
plugin_arquetipos_dinamicos.py
V15.1 — sidecar arquetipos dinámicos
No toca 244 en disco. Fusiona en memoria vía fusionar(lib)
Evidence_status PROPUESTO — ajustar a taxonomía real si difiere
Nota Propp: propp_07_falso_heroe_impostor renumerado — en Morphology 1928 falso héroe es función 7, héroe es 6.
"""

from typing import Dict, Any

VERSION = "V15.1_arquetipos_dinamicos_v01"
HASH_REF = "48333cd11b9234f1"

ARQUETIPOS_DINAMICOS = {
  "jung_trickster_atipico": {
    "subapendice": "psicologia_caos",
    "description": "Agente de disrupción que altera el orden mediante astucia. Genera variaciones impredecibles en la trayectoria de los vectores.",
    "evidence_status": "fuente_academica_propuesta_jung_radin",
    "tokens_favor": {
      "incidente_detonante": 0.85,
      "cambio_repentino": 0.80,
      "enigma": 0.80,
      "insubordinacion": 0.85
    },
    "tokens_contra": {
      "planificacion": 0.90,
      "metodicidad": 0.85,
      "apego_normas": 0.90
    }
  },
  "propp_01_villano_agresor": {
    "subapendice": "morfologia_trama",
    "description": "Rol funcional del agresor. Detonante primario de deltas negativas en la estabilidad del entorno.",
    "evidence_status": "fuente_academica_propuesta_propp_1928",
    "tokens_favor": {
      "antagonismo": 0.90,
      "crueldad": 0.85,
      "discordia": 0.80,
      "persecucion": 0.75
    },
    "tokens_contra": {
      "estabilidad": 0.85,
      "armonia": 0.80,
      "proteccion": 0.80
    }
  },
  "propp_07_falso_heroe_impostor": {
    "subapendice": "morfologia_trama",
    "description": "Falso héroe / impostor que reclama mérito ajeno. Función 7 en numeración canónica Propp 1928 (borrador original venía como 06, renumerado para no chocar con héroe 06 si se agrega aparte).",
    "evidence_status": "PROPUESTO — ajustar a taxonomía real del proyecto si difiere",
    "tokens_favor": {
      "impostura": 0.85,
      "usurpacion": 0.85,
      "falsedad": 0.80,
      "engaño": 0.80
    },
    "tokens_contra": {
      "autenticidad": 0.90,
      "legitimidad": 0.85,
      "merito_propio": 0.85
    }
  }
}

def fusionar(lib: Dict[str, Any]) -> Dict[str, Any]:
    """Fusiona arquetipos dinámicos en lib en memoria. No toca disco."""
    out = dict(lib)
    for k, v in ARQUETIPOS_DINAMICOS.items():
        if k in out:
            # no sobrescribir si ya existe, loggear
            continue
        out[k] = v
    return out

def info():
    return {
      "version": VERSION,
      "hash_ref": HASH_REF,
      "n_nuevos": len(ARQUETIPOS_DINAMICOS),
      "keys": list(ARQUETIPOS_DINAMICOS.keys()),
      "nota_propp": "propp_07_falso_heroe_impostor renumerado: borrador traía propp_06, canónica Propp 1928 falso héroe es función 7, héroe es 6",
      "evidence_status": "PROPUESTO — ajustar a taxonomía real si difiere"
    }
