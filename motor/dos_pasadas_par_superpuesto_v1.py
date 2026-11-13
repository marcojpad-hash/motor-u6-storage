#!/usr/bin/env python3
"""dos_pasadas_par_superpuesto_v1.py — Pre-paso: del empate al par unificado en el input.

Uso:
  python3 dos_pasadas_par_superpuesto_v1.py <RESULT_previo.json> <entrada_sin_puente.json> <entrada_salida.json>

Lee el RESULT de la primera pasada, extrae H1/H2 y el margen (diferencia de
rank_fusion entre las dos primeras hipótesis). Si el margen < UMBRAL (1.0,
GATE_SEPARATION), escribe una variante de la entrada con el campo
`par_superpuesto_entrada` declarando el par. Si no hay empate, no escribe
nada y sale con código 2.

La entrada original no se toca; solo se añade el campo a la variante.
"""
import copy
import json
import sys

UMBRAL = 1.0


def main():
    if len(sys.argv) != 4:
        print("uso: dos_pasadas_par_superpuesto_v1.py <RESULT_previo.json> <entrada.json> <entrada_salida.json>", file=sys.stderr)
        return 3
    result_path, entrada_path, salida_path = sys.argv[1:4]
    result = json.load(open(result_path, encoding="utf-8"))
    entrada = json.load(open(entrada_path, encoding="utf-8"))
    hips = (result.get("salida_interpretable") or {}).get("conjunto_hipotesis_abiertas", {}).get("hipotesis") or []
    if len(hips) < 2:
        print("sin dos hipótesis en el RESULT; no hay par", file=sys.stderr)
        return 2
    h1 = hips[0].get("familia")
    h2 = hips[1].get("familia")
    r1 = hips[0].get("rank_fusion")
    r2 = hips[1].get("rank_fusion")
    if h1 is None or h2 is None or r1 is None or r2 is None:
        print("hipótesis sin familia o rank_fusion; no hay par", file=sys.stderr)
        return 2
    margen = round(r1 - r2, 6)
    print(f"H1={h1} H2={h2} margen={margen} umbral={UMBRAL}")
    if margen >= UMBRAL:
        print(f"sin empate (margen {margen} >= {UMBRAL}); no se escribe variante", file=sys.stderr)
        return 2
    variante = copy.deepcopy(entrada)
    variante["par_superpuesto_entrada"] = {
        "par": [h1, h2],
        "origen": "empate_detectado_en_corrida_previa",
        "corrida_origen": result.get("case_id"),
        "margen": margen,
        "umbral": UMBRAL,
    }
    json.dump(variante, open(salida_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"variante escrita: {salida_path} (par {h1}+{h2})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
