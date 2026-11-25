#!/usr/bin/env python3
"""PLUGIN_METODO_RIGOR — Holmes / Hecate / Schopenhauer
No toca F. No puntua. No fusionar al V5 sin visto.

V7 (hallazgo B-H2): Holmes y Schopenhauer DE ESTE PLUGIN son plantilla de
alarma manual, no vigilancia automática de la ruta real. Holmes solo dispara
con literales ("se llama", "es kant/freud/monroe") que un nombre de familia
del catálogo 244 nunca contiene, y Schopenhauer necesita un `inverso` que
nadie produce en el paquete de corrida. La vigilancia automática real es
Hécate (cadena de 4 iguales, aquí) + los dos checks del orquestador en
guardianes_control_v1.py (HOLMES_TOP1_SIN_TOKENS_DE_HECHO y
SCHOPENHAUER_TABLERO_EN_CONTRA). Generalizar Holmes exigiría definir la
fuente de `inverso` antes de cablearlo; sin fuente definida, no es cableable.

Por que "se les olvida" si es matematica:
  F no olvida. Quien narra olvida. Este plugin obliga el bloque
  DESPUES de correr(), igual que pregunta_detras va ANTES.

Uso:
  from plugin_metodo_rigor import rigor
  print(rigor(out, hipotesis="...", inverso="..."))
"""
from __future__ import annotations


def rigor(out: dict | None = None, hipotesis: str = "", inverso: str = "") -> dict:
    cadena = ""
    if out:
        cadena = out.get("cadena_top1") or ""
    tops = [x.strip() for x in cadena.split("→") if x.strip()]
    flags = []
    if len(tops) >= 4 and len(set(tops[:4])) == 1:
        flags.append("HECATE_MAS_DE_LO_MISMO: el letrero no cambio 4 cortes")
    if hipotesis and any(n in hipotesis.lower() for n in
                         ("se llama", "es kant", "es freud", "es monroe")):
        flags.append("HOLMES: la hipotesis nombra apellido (ciego roto)")
    if inverso and "como yo dije" in inverso.lower():
        flags.append("SCHOPENHAUER: defender el tanteo, no el tablero")

    return {
        "plugin": "METODO_RIGOR",
        "plantilla": {
            "holmes": "tokens de HECHOS del corte o de mi tesis?",
            "hecate": "pedi mas de lo mismo / forcé una lampara?",
            "schopenhauer": "defiendo lo que vi o leo el tablero?",
            "sigue_en_cuaderno": "si/no",
        },
        "auto": flags,
        "cadena_top1": cadena,
        "nota": "auto no sustituye las 4 lineas humanas. Es alarma.",
    }
