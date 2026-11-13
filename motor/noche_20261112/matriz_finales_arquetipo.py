#!/usr/bin/env python3
"""Matriz de finales por arquetipo (2026-11-12, orden de Marco).

Idea de Marco: dentro de UN arquetipo hay TIPOS distintos (estereotipos):
el heroe tragico y el heroe epico son los dos del mismo arquetipo pero
terminan distinto. La matriz no debe carecer de finales ligados por
arquetipo: para cada arquetipo, que finales se han visto.

Datos: 35 casos F001-F004 (H1 + desenlace sellado) + Mozart/Napoleon
(10 cortes) como referencia. Se agrupa por H1; se muestra por caso:
perfil de quema, radio (crece/contrae), fatalidad, desenlace.
"""
import json, glob
from pathlib import Path
from collections import defaultdict

BASE = Path("/home/hatch/workspace/u6-alterno/motor-cameo")
OUT = Path("/home/hatch/workspace/u6-alterno")
barrido = {c["caso"]: c for c in json.load(open(OUT / "barrido_mortalidad_reporte.json"))["casos"]}
quema = {c["caso"]: c for c in json.load(open(OUT / "perfiles_quema_reporte.json"))["casos_3c"]}
pres = {c["caso"]: c for c in json.load(open(OUT / "presupuesto_tokens_reporte.json"))["casos"]}

matriz = defaultdict(list)
for rp in sorted(glob.glob(str(BASE / "motor/RESULT_CAL_F00*.json"))):
    if "LEDGER" in rp or "RECIBO" in rp:
        continue
    nombre = Path(rp).stem.replace("RESULT_", "")
    d = json.load(open(rp))
    h1 = (d.get("H1") or {}).get("family")
    h2 = (d.get("H2") or {}).get("family")
    b = barrido[nombre]
    q = quema[nombre]
    matriz[h1].append({
        "caso": nombre.replace("CAL_", "").replace("_", " ").title(),
        "H2": h2,
        "perfil_quema": q["perfil"],
        "radio": "crece" if b["radio_crece_hacia_final"] else "contrae",
        "fatalidad": b["desenlace_con_fatalidad"],
        "desenlace": b["desenlace_familias"],
    })

# Referencia largos.
for nombre, rp, h1f in [("MOZART", "motor/RESULT_MOZART_Z90_PRECEDENTE.json", None),
                        ("NAPOLEON", "motor/RESULT_NAPOLEON_Z90_10CORTES.json", None)]:
    d = json.load(open(BASE / rp))
    h1 = (d.get("H1") or {}).get("family")
    matriz[h1].append({"caso": nombre + " (10 cortes, referencia)",
                       "H2": (d.get("H2") or {}).get("family"),
                       "perfil_quema": "largo",
                       "radio": "crece (rompe margen)" if nombre == "MOZART" else "dentro (acelera)",
                       "fatalidad": None,
                       "desenlace": ["(sin desenlace_sellado en este formato)"]})

print("== MATRIZ: finales por H1 (arquetipo / familia rectora) ==")
for h1 in sorted(matriz, key=lambda k: -len(matriz[k])):
    casos = matriz[h1]
    print(f"\n## {h1}  ({len(casos)} caso{'s' if len(casos) > 1 else ''})")
    for c in casos:
        print(f"  - {c['caso']}: H2={c['H2']} | {c['perfil_quema']} | radio {c['radio']} | "
              f"fatal={'SI' if c['fatalidad'] else ('no' if c['fatalidad'] is False else '?')} | {', '.join(c['desenlace'])}")

json.dump({k: v for k, v in matriz.items()},
          open(OUT / "matriz_finales_arquetipo.json", "w"), ensure_ascii=False, indent=2)
print("\nGuardado:", OUT / "matriz_finales_arquetipo.json")
