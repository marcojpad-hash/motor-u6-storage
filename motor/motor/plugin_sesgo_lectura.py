#!/usr/bin/env python3
"""PLUGIN_SESGO_LECTURA v2

Repetir tokens NO es sesgo. Los universales se escriben con las
mismas palabras (hambre, caída, grupo). Eso es el cliché / arquetipo.

Lo que se mide:
  C  = solape de tokens (diccionario estable o no)
  N  = tokens NUEVOS en t+1 (color de ESTA vida)
  K  = tokens que se fueron
  P  = el letrero #1 se quedó

Vector de diferenciación D = N ∪ K
  Si P y D no vacío: el universal se quedó CON otra carne.
  Si P y D vacío: misma frase otra vez. No condena; avisa "poca carne nueva".
  Si no P: cambió el letrero.

No hay etiqueta 'sesgo' automática.
Hay: universal_con_color | universal_sin_color_nueva | cambio_de_letrero
"""
from __future__ import annotations

from typing import Any, Dict, List, Sequence, Set


def _toks(cut: Dict[str, Any]) -> Set[str]:
    raw = cut.get("tokens") or cut.get("markers") or []
    out = set()
    for x in raw:
        if isinstance(x, str):
            out.add(x)
        elif isinstance(x, dict):
            t = x.get("token") or x.get("name")
            if t:
                out.add(str(t))
        elif isinstance(x, (list, tuple)) and x:
            out.add(str(x[0]))
    return out


def jaccard(a: Set[str], b: Set[str]) -> float:
    if not a and not b:
        return 1.0
    u = a | b
    return len(a & b) / len(u) if u else 0.0


def leer(cortes: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    filas = []
    for i in range(len(cortes) - 1):
        a, b = cortes[i], cortes[i + 1]
        ta, tb = _toks(a), _toks(b)
        nuevos = sorted(tb - ta)
        idos = sorted(ta - tb)
        C = round(jaccard(ta, tb), 4)
        Ha, Hb = a.get("H"), b.get("H")
        P = Ha is not None and Ha == Hb
        if not P:
            tag = "cambio_de_letrero"
        elif nuevos or idos:
            tag = "universal_con_color"
        else:
            tag = "universal_sin_color_nueva"
        filas.append({
            "de": a.get("id"),
            "a": b.get("id"),
            "H_de": Ha,
            "H_a": Hb,
            "C_solape": C,
            "tokens_nuevos": nuevos,
            "tokens_idos": idos,
            "D_diferenciacion": sorted(set(nuevos) | set(idos)),
            "letrero_igual": P,
            "etiqueta": tag,
        })
    return {
        "plugin": "PLUGIN_SESGO_LECTURA",
        "version": 2,
        "engine_tocado": False,
        "regla": (
            "Mismas palabras no equivalen a sesgo. "
            "Sesgo solo se SOSPECHA si el letrero se queda y D está vacío "
            "(cero carne nueva). Aun así no se anula el hallazgo."
        ),
        "con_aquiles": (
            "Aquiles + universal_con_color = rumbo con instancia. "
            "Aquiles + universal_sin_color_nueva = rumbo, pero esta vida "
            "no aportó pigmento: no lo vendas como caso nuevo."
        ),
        "transiciones": filas,
    }


if __name__ == "__main__":
    import json
    demo = [
        {"id": "A", "H": "30_ambicion", "tokens": ["ambicion", "aprendizaje"]},
        {"id": "B", "H": "30_ambicion", "tokens": ["ambicion", "poder", "liderazgo"]},
        {"id": "C", "H": "30_ambicion", "tokens": ["ambicion", "poder", "liderazgo"]},
        {"id": "D", "H": "6_desastre", "tokens": ["desastre", "caida"]},
    ]
    print(json.dumps(leer(demo), ensure_ascii=False, indent=2))
