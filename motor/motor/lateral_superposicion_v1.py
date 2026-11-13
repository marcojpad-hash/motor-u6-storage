# lateral_superposicion_v1.py — Lectura de H1/H2 como superposición (observación)
#
# Contrato: SUPERPOSICION_H1_H2_V1.md
#   can_decide_H = False (SENSOR, solo observa; no toca H1/H2 ni ranking).
#   No toca Engine ni catálogo 244. Solo lee H1/H2 y P_FULL_244 por corte.
#
# Reporta por caso:
#   par_superpuesto: "H1+H2"
#   por corte: peso de H1 y de H2, y si ambas >= 0.7 (superposición)
#   simetria: media de |w_H1 - w_H2| por corte (0 = simétrica)
#   subtipo: por las familias compañeras de H1 en el último corte
#     (maestro / creador-heroe / aventurero para sabio; genérico si no hay regla)
#
# Uso:
#   from lateral_superposicion_v1 import observar
#   out = observar(result_dict)

CAN_DECIDE_H = False
CONTRATO = "SUPERPOSICION_H1_H2_V1"
VERSION = "v1_20261113"
UMBRAL_SUPERPOSICION = 0.7

# Subtipos por compañeras (familia H1 -> [(compañeras, subtipo), ...])
SUBTIPOS = {
    "arquetipo_el_sabio": [
        ({"mentor"}, "maestro"),
        ({"arquetipo_el_creador", "heroe"}, "creador-heroe"),
        ({"9_audaz_empresa", "bbk_01_aventurero"}, "aventurero"),
    ],
}


def _subtipo(h1, top_familias):
    """top_familias: set de las familias top del último corte."""
    for companeras, nombre in SUBTIPOS.get(h1, []):
        if companeras <= top_familias:
            return nombre
    return None


def observar(result):
    h1 = (result.get("H1") or {}).get("family")
    h2 = (result.get("H2") or {}).get("family")
    cuts = (result.get("motor") or {}).get("cuts", [])
    por_corte = []
    for c in cuts:
        p = c.get("P_FULL_244", {})
        w1 = p.get(h1)
        w2 = p.get(h2)
        if w1 is None or w2 is None:
            continue
        por_corte.append({
            "w_h1": round(w1, 3),
            "w_h2": round(w2, 3),
            "superposicion": bool(w1 >= UMBRAL_SUPERPOSICION and w2 >= UMBRAL_SUPERPOSICION),
        })
    n_sup = sum(1 for x in por_corte if x["superposicion"])
    if por_corte:
        simetria = sum(abs(x["w_h1"] - x["w_h2"]) for x in por_corte) / len(por_corte)
    else:
        simetria = None
    # Subtipo por compañeras del último corte
    subtipo = None
    if cuts:
        p_ult = cuts[-1].get("P_FULL_244", {})
        top = set(k for k, v in sorted(p_ult.items(), key=lambda kv: -kv[1])[:5])
        subtipo = _subtipo(h1, top)
    return {
        "contrato": CONTRATO,
        "version": VERSION,
        "can_decide_H": CAN_DECIDE_H,
        "case_id": result.get("case_id"),
        "h1": h1,
        "h2": h2,
        "par_superpuesto": f"{h1}+{h2}" if h1 and h2 else None,
        "n_cortes": len(por_corte),
        "cortes_en_superposicion": n_sup,
        "por_corte": por_corte,
        "simetria_media": round(simetria, 3) if simetria is not None else None,
        "subtipo": subtipo,
    }
