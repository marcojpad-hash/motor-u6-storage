#!/usr/bin/env python3
"""Perfiles de quema (2026-11-12, intuicion de Marco).

Intuicion: hay dos formas de quemar los recursos — (a) estar plano todo
el tiempo y de repente consumirlos todos muy rapido, o (b) consumirlos
muy rapido desde el inicio. Marco duda que sea tan asi; debe haber otros
factores. Se mide con el perfil de movimiento (dX_norm por paso):
- 3 cortes (2 pasos): ratio ultimo/primero. >1.25 = quema al final;
  <0.8 = quema al inicio; entre = plano.
- 10 cortes (9 pasos): ultimo paso vs mediana de los 8 anteriores, y
  nivel general (mediana de dX) vs la mediana de todos los casos.
- Noether y Carson (freeze sept 2026, motor V15.1): dX ya publicado en
  sus FREEZE/SALIDA_TECNICA; se incluyen como referencia.
Contra: desenlace con fatalidad (barrido de mortalidad).
"""
import json, glob
from pathlib import Path
import numpy as np

BASE = Path("/home/hatch/workspace/u6-alterno/motor-cameo")
OUT = Path("/home/hatch/workspace/u6-alterno")
barrido = json.load(open(OUT / "barrido_mortalidad_reporte.json"))
fatal = {c["caso"]: c["desenlace_con_fatalidad"] for c in barrido["casos"]}

def clasificar_3(dx):
    r = dx[1] / dx[0] if dx[0] > 1e-12 else None
    if r is None:
        return "?", None
    if r > 1.25:
        return "plano_y_quema_al_final", r
    if r < 0.8:
        return "quema_al_inicio", r
    return "plano", r

filas = []
for rp in sorted(glob.glob(str(BASE / "motor/RESULT_CAL_F00*.json"))):
    if "LEDGER" in rp or "RECIBO" in rp:
        continue
    nombre = Path(rp).stem.replace("RESULT_", "")
    d = json.load(open(rp))
    dx = np.array(d["motor"]["R732"]["dX_norm"], dtype=float)
    clase, r = clasificar_3(dx)
    filas.append({"caso": nombre, "n_cortes": 3, "dX": [round(float(x), 3) for x in dx],
                  "perfil": clase, "ratio": round(float(r), 2) if r else None,
                  "fatalidad": fatal.get(nombre)})

# Largos: perfil completo.
largos = []
for nombre, rp in [("MOZART_Z90", "motor/RESULT_MOZART_Z90_PRECEDENTE.json"),
                   ("NAPOLEON_Z90", "motor/RESULT_NAPOLEON_Z90_10CORTES.json")]:
    d = json.load(open(BASE / rp))
    dx = np.array(d["motor"]["R732"]["dX_norm"], dtype=float)
    med_prev = float(np.median(dx[:-1]))
    r = float(dx[-1] / med_prev) if med_prev > 1e-12 else None
    largos.append({"caso": nombre, "n_cortes": 10, "dX": [round(float(x), 3) for x in dx],
                   "mediana_dX": round(float(np.median(dx)), 3),
                   "ultimo_vs_mediana_previa": round(r, 2) if r else None})

# Referencia vieja (freeze sept).
ref = {
    "NOETHER_freeze_sep": [0.6103, 0.7165, 0.4773, 0.4472, 0.4988, 0.5309],
    "CARSON_freeze_sep": [0.5985, 0.6752, 0.3586, 0.4682, 0.7048, 0.6698],
}

from collections import Counter
print("== 35 casos (3 cortes): perfil de quema")
print("  ", dict(Counter(f["perfil"] for f in filas)))
for perfil in ["plano_y_quema_al_final", "quema_al_inicio", "plano"]:
    sub = [f for f in filas if f["perfil"] == perfil]
    nf = sum(1 for f in sub if f["fatalidad"])
    print(f"  {perfil}: {len(sub)} casos, con fatalidad {nf}")
print("== Largos (10 cortes)")
for L in largos:
    print(f"  {L['caso']}: mediana dX={L['mediana_dX']}, ultimo vs mediana previa={L['ultimo_vs_mediana_previa']}, dX={L['dX']}")
print("== Referencia freeze sept (7 cortes)")
for k, v in ref.items():
    print(f"  {k}: dX={v}, ultimo vs mediana previa={round(v[-1]/float(np.median(v[:-1])), 2)}, mediana={round(float(np.median(v)), 3)}")
json.dump({"casos_3c": filas, "largos": largos, "referencia_freeze": ref},
          open(OUT / "perfiles_quema_reporte.json", "w"), ensure_ascii=False, indent=2)
