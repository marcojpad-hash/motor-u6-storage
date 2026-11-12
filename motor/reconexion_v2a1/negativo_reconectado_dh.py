#!/usr/bin/env python3
"""Reconexión v2.A.1 (reserva): el "no" del Décimo Hombre alimenta el negativo.

El DH calcula contador_supervivencia (cuántos de los 53 contrafactuales sobrevive
cada candidata) pero NADIE lo lee: la corriente va a la nada. Aquí se reconecta:
supervivencia 0 -> DESCARTE (el "no" del DH cuenta); supervivencia > 0 -> SE_SOSTIENE
con el conteo. Se aplica al top 5 por rank_fusion del RESULT (post-corrida, sin tocar
Engine ni catálogo). Versión reserva, no la que se maneja ahorita.
"""
import json, sys

R_PATH = 'motor/RESULT_NAPOLEON_Z90_10CORTES.json'
r = json.load(open(R_PATH))
dh = r.get('decimo_hombre_esteroides', {})
sup = dh.get('contador_supervivencia', {})
n_cf = len(dh.get('contrafactuales_ejecutados', [])) or 53

# top 5 por rank_fusion (de predictibilidad_021 / H1-H2)
ph = r.get('predictibilidad_021', {}).get('predictibilidad', {}).get('por_hipotesis', {})
top5 = sorted(ph.items(), key=lambda kv: kv[1].get('rank_fusion', 0), reverse=True)[:5]

print(f"Décimo Hombre: {n_cf} contrafactuales, can_decide_H={dh.get('can_decide_H')}, rewrites_H={dh.get('rewrites_H')}")
print(f"contador_supervivencia leído por: NADIE (antes de esta reconexión)")
print("\n=== NEGATIVO RECONECTADO (DH -> DESCARTE) ===")
out = {"caso": "NAPOLEON_Z90_10CORTES", "n_contrafactuales": n_cf, "filas": []}
descartados = 0
for fam, vals in top5:
    s = sup.get(fam, 0)
    rf = vals.get('rank_fusion')
    if s == 0:
        veredicto = "DESCARTE"
        descartados += 1
    else:
        veredicto = "SE_SOSTIENE"
    print(f"{fam} (rf {rf:.2f}): sobrevive {s}/{n_cf} -> {veredicto}")
    out["filas"].append({"familia": fam, "rank_fusion": rf, "supervivencia": s,
                          "n_contrafactuales": n_cf, "veredicto": veredicto})
out["descartados"] = descartados
out["sostenidos"] = len(top5) - descartados
print(f"\n{len(top5)} -> {len(top5)-descartados} sostenidos, {descartados} descartados por el DH.")
print("Antes: el DH no descartaba nada (LATENTE). Ahora su 'no' cuenta.")
json.dump(out, open('NEGATIVO_RECONECTADO_DH_NAPOLEON_10CORTES.json', 'w'), indent=1, ensure_ascii=False)
print("guardado: NEGATIVO_RECONECTADO_DH_NAPOLEON_10CORTES.json")
