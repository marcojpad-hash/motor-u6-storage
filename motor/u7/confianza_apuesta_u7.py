#!/usr/bin/env python3
"""U7 · Confianza de la apuesta (post-corrida, solo lee RESULT json; no toca motor/Engine/patterns).
NO calibrada: pesos iguales fijados a priori, sin ajuste a desenlaces.
uso: python3 confianza_apuesta_u7.py RESULT.json [...]  -> imprime json por caso
"""
import json, sys

W = {"B1_dominancia": 1, "B2_set_mezcla": 1, "B3_laterales": 1, "B4_robustez_adversarial": 1,
     "B5_estabilidad_sin_ultimo": 1, "B6_fondo": 1}
PEN_POR_OBJECION = 0.05; PEN_MAX = 0.30
MEZCLA = {"H1_DOMINANTE": 1.0, "H1_CON_COMPONENTES_DE_H2": 0.5, "MEZCLA_H1_H2_SIN_SEPARACION": 0.0}
# El veredicto se refiere al RIVAL sometido al hombre de acero: si SOBREVIVE,
# contradice la apuesta; si CAE, la favorece. No invertir el signo.
ACERO = {"SOBREVIVE": 0.0, "OBJECION_RESUELTA_EN_CIERRE": 0.5, "CAE": 1.0}


def _objeciones_unicas(cf):
    """Cuenta objeciones semánticamente únicas y no cobra C2 dos veces por el mismo acero."""
    rows = list(cf.get("objeciones") or [])
    # El legado puede guardar solo el contador; no inventar detalle para deduplicar.
    if not rows:
        return max(0, int(cf.get("n_objeciones", 0) or 0)), []
    out = []
    seen = set()
    has_global_steel_guardian = any(
        r.get("fuente") == "guardian" and
        (r.get("guardian") == "HOMBRE_DE_ACERO" or r.get("tipo") == "RIVAL_NO_DESCARTADO") and
        r.get("alcance") == "global" for r in rows
    )
    for r in rows:
        # C2_acero y la objeción global del guardián describen el mismo fallo.
        if r.get("fuente") == "modo_estricto" and r.get("criterio") == "C2_acero" and has_global_steel_guardian:
            continue
        key = (r.get("fuente"), r.get("guardian"), r.get("tipo"), r.get("criterio"), r.get("alcance"), r.get("corte"), r.get("detalle"))
        if key in seen:
            continue
        seen.add(key); out.append(r)
    return len(out), out

def clip(x): return max(0.0, min(1.0, float(x)))

def calc(d):
    cf = d["cierre_final"]; cg = cf["criterios_grado"]; ap = cf["apuesta"]
    h1, h2 = ap["familia_apostada"], ap["frente_a"]
    det = {}
    # B1 dominancia/margen/banda
    sep = cg.get("separacion") or 1.0
    b1 = clip(ap["margen"] / sep) * (0.5 if cg.get("H1_en_banda") else 1.0)
    det["B1"] = {"margen": ap["margen"], "separacion": sep, "H1_en_banda": cg.get("H1_en_banda")}
    # B2 set + mezcla
    si = d["salida_interpretable"]; lect = (si.get("mezcla") or {}).get("lectura")
    set_ok = 1.0 if si.get("grado_inverso_set") == "SET_EXPLICA_TODOS_LOS_CORTES" else 0.0
    b2 = (set_ok + MEZCLA.get(lect, 0.5)) / 2
    det["B2"] = {"grado_inverso_set": si.get("grado_inverso_set"), "mezcla": lect}
    # B3 laterales: H1 vs H2 en cada señal lateral discriminante del registro del predictor
    votos = []
    for s in d["predictor"].get("lateral_signal_registry") or []:
        cv = s.get("candidate_values") or {}
        if not s.get("discriminates") or h1 not in cv or h2 not in cv: continue
        a, b = cv[h1], cv[h2]; votos.append((s["signal"], 1.0 if a > b else 0.5 if a == b else 0.0))
    tort = (((d.get("cierre_guardianes") or {}).get("tortugas") or {}).get("remedicion_misma_resolucion") or {}).get("micro")
    if tort and tort.get("argmax") and not str(tort["argmax"]).startswith("DESEMPATE"):
        votos.append(("tortugas_micro", 1.0 if tort["argmax"] == h1 else 0.0))
    b3 = sum(v for _, v in votos) / len(votos) if votos else 0.5
    det["B3"] = {"votos": dict(votos), "n": len(votos)}
    # B4 décimo hombre + acero
    dh = d["decimo_hombre_esteroides"]; sv = dh.get("contador_supervivencia") or {}
    share = sv.get(h1, 0) / max(1, sum(sv.values()))
    aq = next((a for a in dh.get("ataques") or [] if a.get("ataque") == "AQUILES_DIMENSIONAL"), {})
    abl = 1 - aq.get("cambios_de_lider", 0) / max(1, aq.get("n_contrafactuales", 1))
    acero_raw = cf.get("prueba_acero") or {}
    rival_acero = acero_raw.get("rival_mas_fuerte")
    acero_alineado = acero_raw.get("rival_alineado_apuesta")
    if acero_alineado is None:
        acero_alineado = bool(rival_acero and rival_acero == h2)
    # Si el acero evaluó a otro rival (o no se puede verificar cuál), no atribuir
    # ese resultado a H1: neutral 0.5, nunca invertirlo ni aplicarlo a ciegas.
    acero = ACERO.get(acero_raw.get("veredicto_top1"), 0.5) if acero_alineado else 0.5
    cambio = 0.0 if dh.get("cambio_tras_adversario") else 1.0
    b4 = (share + abl + acero + cambio) / 4
    det["B4"] = {"supervivencia_H1": share, "ablacion_sin_cambio_lider": abl, "acero": acero_raw.get("veredicto_top1"), "acero_rival": rival_acero, "acero_alineado_a_H2": bool(acero_alineado), "acero_aporte": acero, "cambio_tras_adversario": dh.get("cambio_tras_adversario")}
    # B5 SIN_ULTIMO (RETENIDO no usable: tops_t1 vacío por defecto de cableado en puntuar_t1)
    e = d.get("efectividad_corte_retenido") or {}
    set_f = [m["familia"] for m in (d.get("hipotesis_necesarias_suficientes") or {}).get("miembros", [])] if isinstance(d.get("hipotesis_necesarias_suficientes"), dict) else []
    hs = e.get("H1_sellada")
    b5 = 1.0 if hs == h1 else 0.5 if (hs == h2 or hs in set_f) else 0.0
    det["B5"] = {"H1_sin_ultimo": hs, "retenido_hit": e.get("hit_H"), "retenido_usable": bool(e.get("tops_t1"))}
    # B6 fondo: emergentes que no compiten (acero inverso) y ausencia de corriente fuerte fuera del top5
    ab = d.get("lo_que_se_cocina_abajo") or []
    if ab:
        nocomp = sum(1 for a in ab if (a.get("inverso") or {}).get("acero_inverso_vs_eje") in ("COMPLEMENTA_AL_EJE", "REDUNDANTE_CON_EJE", "EQUIVALENTE_AL_EJE", "NO_APLICA")) / len(ab)
        fuera = sum(1 for a in ab if a.get("donde_esta_abajo") == "ARRIBA_EN_TABLERO_PERO_FUERA_DEL_TOP5_020") / len(ab)
        b6 = (nocomp + (1 - fuera)) / 2
    else: nocomp = fuera = None; b6 = 0.5
    det["B6"] = {"n_emergentes": len(ab), "frac_no_compite": nocomp, "frac_arriba_fuera_top5": fuera}
    B = {"B1_dominancia": b1, "B2_set_mezcla": b2, "B3_laterales": b3, "B4_robustez_adversarial": b4, "B5_estabilidad_sin_ultimo": b5, "B6_fondo": b6}
    S = sum(W[k] * v for k, v in B.items()) / sum(W.values())
    nob, objeciones_unicas = _objeciones_unicas(cf); pen = min(PEN_MAX, PEN_POR_OBJECION * nob)
    pr = d["predictibilidad_021"]["predictibilidad"]; base, techo = pr["base_pp"], pr["techo_pp"]
    conf = base + (techo - base) * S * (1 - pen)
    return {"case_id": d["case_id"], "apuesta": h1, "frente_a": h2, "grado_020": cf.get("grado", "NO_DISPONIBLE"),
            "bloques": {k: round(v, 4) for k, v in B.items()}, "S": round(S, 4), "n_objeciones": nob, "penalizacion": round(pen, 4),
            "base_pct": base, "techo_pct": techo, "confianza_apuesta_pct": round(conf, 2),
            "predictibilidad_021_H1_pct": d["salida_interpretable"]["H1"].get("predictibilidad_estructural_pct"),
            "calibrada": False, "objeciones_unicas": objeciones_unicas, "detalle": det}

if __name__ == "__main__":
    print(json.dumps([calc(json.load(open(p))) for p in sys.argv[1:]], ensure_ascii=False, indent=1))
