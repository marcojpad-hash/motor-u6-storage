# lateral_par_superpuesto_entrada_v1.py — Lectura del par superpuesto declarado en el INPUT (observación)
#
# Contrato: PAR_SUPERPUESTO_ENTRADA_V1.md
#   can_decide_H = False (SENSOR, solo observa; no toca H1/H2 ni ranking).
#   No toca Engine ni catálogo 244. Solo lee el par declarado en el input
#   y H1/H2 + P_FULL_244 por corte del RESULT.
#
# El empate (margen < GATE_SEPARATION) se traduce en el input como un par
# unificado: el motor ya no lee dos patrones simples que compiten, sino
# una sola cosa con dos caras. Este lateral verifica que el par declarado
# coincide con H1/H2 y mide la superposición por corte.
#
# Uso:
#   from lateral_par_superpuesto_entrada_v1 import observar
#   out = observar(entrada, motor, pred)

CAN_DECIDE_H = False
CONTRATO = "PAR_SUPERPUESTO_ENTRADA_V1"
VERSION = "v1_20261113"
UMBRAL_SUPERPOSICION = 0.7


def observar(entrada, motor, pred):
    decl = (entrada or {}).get("par_superpuesto_entrada") or {}
    par = decl.get("par") or []
    f1 = par[0] if len(par) > 0 else None
    f2 = par[1] if len(par) > 1 else None
    cands = (pred or {}).get("candidates") or []
    h1 = (cands[0] or {}).get("family") if len(cands) > 0 else None
    h2 = (cands[1] or {}).get("family") if len(cands) > 1 else None
    cuts = (motor or {}).get("cuts", [])
    por_corte = []
    for c in cuts:
        p = c.get("P_FULL_244", {})
        w1 = p.get(f1) if f1 else None
        w2 = p.get(f2) if f2 else None
        if w1 is None or w2 is None:
            continue
        por_corte.append({
            "corte": c.get("corte"),
            "w_f1": round(w1, 3),
            "w_f2": round(w2, 3),
            "w_par_media": round((w1 + w2) / 2, 3),
            "w_par_min": round(min(w1, w2), 3),
            "superposicion": bool(w1 >= UMBRAL_SUPERPOSICION and w2 >= UMBRAL_SUPERPOSICION),
        })
    n_sup = sum(1 for x in por_corte if x["superposicion"])
    if por_corte:
        simetria = sum(abs(x["w_f1"] - x["w_f2"]) for x in por_corte) / len(por_corte)
    else:
        simetria = None
    coincide = bool(f1 and f2 and {f1, f2} == {h1, h2})
    top2 = [(cands[i] or {}).get("family") for i in range(min(2, len(cands)))]
    adyacente_top2 = bool(f1 and f2 and set(top2) == {f1, f2})
    return {
        "contrato": CONTRATO,
        "version": VERSION,
        "can_decide_H": CAN_DECIDE_H,
        "case_id": (entrada or {}).get("case_id"),
        "declarado": bool(f1 and f2),
        "par": f"{f1}+{f2}" if f1 and f2 else None,
        "f1": f1,
        "f2": f2,
        "origen": decl.get("origen"),
        "corrida_origen": decl.get("corrida_origen"),
        "margen_origen": decl.get("margen"),
        "h1": h1,
        "h2": h2,
        "coincide_con_H1_H2": coincide,
        "adyacente_top2": adyacente_top2,
        "n_cortes": len(por_corte),
        "cortes_en_superposicion": n_sup,
        "por_corte": por_corte,
        "simetria_media": round(simetria, 3) if simetria is not None else None,
        "lectura": "par unificado" if coincide else "par declarado no coincide con H1/H2",
    }
