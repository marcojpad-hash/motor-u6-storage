#!/usr/bin/env python3
"""FIX PROVISIONAL DE ENTRADA — no toca Engine_V5.

Lo que el V5 SI hace:
  get_weight = peso del token en la ficha x multiplicador evidence_status
  support / contradict = Bayes por token
  epsilon, p_azar
NO hace: nicho / vecinos / campo semantico. Los tokens no se
empujan entre si. Por eso ambicion suelta enciende 30_ambicion
(ficha = 'poder sin limites') aunque el texto sea agencia.

Este archivo es el candado que no depende de los 3 humanos:

1) Campo semantico: cuenta tokens de CONQUISTA vs AGENCIA.
   Si hay 'ambicion' sin poder/sed_de_mando/escalada → se
   REESCRIBE a 'autonomia' (lexico de Schwartz 10).
2) Alias clinico SOLO con el texto de ESA ventana.
3) Embudo se llama aparte (plugin_embudo_clinico).

Uso:
  from plugin_fix_entrada import preparar_corte
  cid, toks = preparar_corte('E', [('ambicion',0.8)], hechos='quiso controlar su trabajo')
"""
from __future__ import annotations

from typing import List, Sequence, Tuple

from plugin_alias_reactivacion import traducir
from plugin_embudo_clinico import etiquetar

CONQUISTA = {"poder", "sed_de_mando", "escalada", "codicia", "maquiavelismo"}
AGENCIA = {"autonomia", "inconformismo", "desafio_autoridad", "humildad"}


def campo(tokens: Sequence[Tuple[str, float]]) -> dict:
    n = {t for t, v in tokens if v >= 0.5}
    return {
        "conquista": len(n & CONQUISTA),
        "agencia": len(n & AGENCIA),
        "tiene_ambicion": "ambicion" in n,
    }


def remapeo_ambicion(
    tokens: Sequence[Tuple[str, float]],
) -> List[Tuple[str, float]]:
    c = campo(tokens)
    out = []
    for t, v in tokens:
        if t == "ambicion" and c["conquista"] == 0:
            out.append(("autonomia", v))
        else:
            out.append((t, v))
    return out


def preparar_corte(
    cid: str,
    tokens: Sequence[Tuple[str, float]],
    hechos: str = "",
) -> Tuple[str, List[Tuple[str, float]]]:
    """Alias por ventana + remapeo ambicion→autonomia si no hay conquista."""
    toks = traducir(list(tokens), hechos=hechos or "")
    toks = remapeo_ambicion(toks)
    return cid, toks


def preparar_caso(
    cortes: Sequence[Tuple[str, Sequence[Tuple[str, float]], str]],
) -> dict:
    """cortes = [(id, tokens, hechos_de_esa_ventana), ...]"""
    listos = []
    for item in cortes:
        if len(item) == 2:
            cid, toks = item
            hechos = ""
        else:
            cid, toks, hechos = item
        listos.append(preparar_corte(cid, toks, hechos))
    return {
        "cortes": listos,
        "campos": [{"corte": c, **campo(t)} for c, t in listos],
        "embudo": etiquetar(listos),
    }
