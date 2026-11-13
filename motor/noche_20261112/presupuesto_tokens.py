#!/usr/bin/env python3
"""Presupuesto de tokens (2026-11-12, intuicion de Marco).

Hipotesis de Marco: el individuo se acaba, sus tokens. Los tokens estan
definidos por los arquetipos bajo los que se le traza; ciertos arquetipos
tienen cierto numero de USOS de esos tokens antes de llegar a encuentros
fatales. Caveat de Marco: lo vemos desde figuras emblematicas; si no,
todos caen en la media (las figuras ordinarias no tienen varianza para
verlo).

Medicion (nativa del motor, sin inventar nada):
- Para cada caso: la familia H1 (y H2) y en cuantos cortes esta ACTIVA
  (p > 0.5, por encima del plano) ANTES del corte final, y en total.
- Usos totales de tokens de la entrada (suma de tokens P+A+C por corte)
  y vocabulario distinto (cuantos tokens diferentes usa el caso).
- Contra: desenlace con fatalidad (del barrido de mortalidad).

Si hay presupuesto, el numero de usos antes del final deberia
concentrarse (un numero caracteristico) en vez de regarse.
"""
import json, glob
from pathlib import Path
from collections import Counter

BASE = Path("/home/hatch/workspace/u6-alterno/motor-cameo")
OUT = Path("/home/hatch/workspace/u6-alterno")
barrido = json.load(open(OUT / "barrido_mortalidad_reporte.json"))
fatal = {c["caso"]: c["desenlace_con_fatalidad"] for c in barrido["casos"]}

def usos_familia(cuts, fam):
    """Cortes donde la familia esta activa (p>0.5) en el tablero P."""
    return [i for i, c in enumerate(cuts) if c["P_FULL_244"].get(fam, 0.5) > 0.5]

def entrada_tokens(case_id):
    for pat in (f"casos/fabrica/cola/{case_id}/entrada.json",
                f"casos/precedentes/{case_id}/entrada.json"):
        p = BASE / pat
        if p.exists():
            d = json.load(open(p))
            toks, distintos = 0, set()
            for c in d["cuts"]:
                for lado in ("P", "A", "C"):
                    for t, _w in (c.get(lado) or []):
                        toks += 1
                        distintos.add(t)
            return toks, len(distintos), len(d["cuts"])
    return None, None, None

filas = []
for rp in sorted(glob.glob(str(BASE / "motor/RESULT_CAL_F00*.json"))):
    if "LEDGER" in rp or "RECIBO" in rp:
        continue
    nombre = Path(rp).stem.replace("RESULT_", "")
    d = json.load(open(rp))
    cuts = d["motor"]["cuts"]
    h1 = (d.get("H1") or {}).get("family")
    h2 = (d.get("H2") or {}).get("family")
    n = len(cuts)
    u_h1_pre = [i for i in usos_familia(cuts, h1) if i < n - 1]
    u_h2_pre = [i for i in usos_familia(cuts, h2) if i < n - 1]
    toks, distintos, nc = entrada_tokens(nombre)
    filas.append({
        "caso": nombre, "n_cortes": n, "H1": h1, "H2": h2,
        "usos_H1_antes_final": len(u_h1_pre),
        "usos_H1_total": len(usos_familia(cuts, h1)),
        "usos_H2_antes_final": len(u_h2_pre),
        "usos_H2_total": len(usos_familia(cuts, h2)),
        "tokens_usos_total": toks, "tokens_distintos": distintos,
        "desenlace_con_fatalidad": fatal.get(nombre),
    })

# Los dos largos (10 cortes).
for nombre, rp in [("MOZART_Z90", "motor/RESULT_MOZART_Z90_PRECEDENTE.json"),
                   ("NAPOLEON_Z90", "motor/RESULT_NAPOLEON_Z90_10CORTES.json")]:
    d = json.load(open(BASE / rp))
    cuts = d["motor"]["cuts"]
    h1 = (d.get("H1") or {}).get("family")
    h2 = (d.get("H2") or {}).get("family")
    n = len(cuts)
    filas.append({
        "caso": nombre, "n_cortes": n, "H1": h1, "H2": h2,
        "usos_H1_antes_final": len([i for i in usos_familia(cuts, h1) if i < n - 1]),
        "usos_H1_total": len(usos_familia(cuts, h1)),
        "usos_H2_antes_final": len([i for i in usos_familia(cuts, h2) if i < n - 1]),
        "usos_H2_total": len(usos_familia(cuts, h2)),
        "tokens_usos_total": None, "tokens_distintos": None,
        "desenlace_con_fatalidad": None,
    })

f35 = [f for f in filas if f["n_cortes"] == 3]
print("== Usos de H1 ANTES del final (35 casos de 3 cortes; max posible 2):")
print("   distribucion:", dict(sorted(Counter(f["usos_H1_antes_final"] for f in f35).items())))
print("   con fatalidad:", dict(sorted(Counter(f["usos_H1_antes_final"] for f in f35 if f["desenlace_con_fatalidad"]).items())),
      "| sin fatalidad:", dict(sorted(Counter(f["usos_H1_antes_final"] for f in f35 if not f["desenlace_con_fatalidad"]).items())))
print("== Usos de H1 TOTAL (35 casos):")
print("   distribucion:", dict(sorted(Counter(f["usos_H1_total"] for f in f35).items())))
print("== Usos de H2 ANTES del final (35 casos):")
print("   distribucion:", dict(sorted(Counter(f["usos_H2_antes_final"] for f in f35).items())))
print("== Tokens de entrada (35 casos): usos totales por caso:",
      dict(sorted(Counter(f["tokens_usos_total"] for f in f35).items())))
print("   distintos por caso:", dict(sorted(Counter(f["tokens_distintos"] for f in f35).items())))
print("   usos totales: con fatalidad media:",
      round(sum(f["tokens_usos_total"] for f in f35 if f["desenlace_con_fatalidad"]) / max(1, sum(1 for f in f35 if f["desenlace_con_fatalidad"])), 1),
      "| sin fatalidad media:",
      round(sum(f["tokens_usos_total"] for f in f35 if not f["desenlace_con_fatalidad"]) / max(1, sum(1 for f in f35 if not f["desenlace_con_fatalidad"])), 1))
print("== Largos (10 cortes):")
for f in filas:
    if f["n_cortes"] == 10:
        print(f"  {f['caso']}: H1={f['H1']} usos antes del final={f['usos_H1_antes_final']}/9, total={f['usos_H1_total']}/10;"
              f" H2={f['H2']} antes={f['usos_H2_antes_final']}/9, total={f['usos_H2_total']}/10")
json.dump({"casos": filas}, open(OUT / "presupuesto_tokens_reporte.json", "w"), ensure_ascii=False, indent=2)
print("reporte:", OUT / "presupuesto_tokens_reporte.json")
