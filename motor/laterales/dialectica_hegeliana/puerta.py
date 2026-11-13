#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""puerta.py — Puerta del lateral dialéctica hegeliana.

G1 (estructural, del catálogo): el vocabulario ya entrelaza las tres
   familias — insubordinación es contra de tesis y favor de antítesis;
   paz_interior es contra de antítesis y favor de síntesis.
G2 (fixture): A={autoridad, control} + B={insubordinación,
   confrontación} -> C contiene paz_interior (el token que resuelve el
   conflicto y es síntesis) y todo C está en favor de síntesis (nada
   inventado); el ciclo corre >= 2 vueltas y la síntesis se acarrea.
G3 (datos sellados): el ciclo corre sobre las 8 entradas ciegas sin
   inventar tokens; el resolver encuentra análogo activo para lo que
   falta — el héroe en Che (#12, no corona) y consumo_sustancias en
   Elvis v1 (no está en la entrada).
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent  # motor-cameo/
sys.path.insert(0, str(HERE))
import dialectica as D

CASOS = [
    "ANONIMO_Z90_20261113", "ANONIMO2_Z90_20261113",
    "ANONIMO3_Z90_20261113", "ANONIMO3_Z90_20261113_v2",
    "TRANSICION1_Z90_20261113", "TRANSICION1_Z90_20261113_v2",
    "TRANSICION2_Z90_20261113", "ANONIMO4_Z90_20261113",
]


def _favor(pat, fam):
    return {str(t).strip().casefold() for t in (pat.get(fam) or {}).get("tokens_favor", {}).keys()}


def _contra(pat, fam):
    return {str(t).strip().casefold() for t in (pat.get(fam) or {}).get("tokens_contra", {}).keys()}


def _hipotesis_activas(result_path):
    r = json.loads(Path(result_path).read_text(encoding="utf-8"))
    h = ((r.get("salida_interpretable") or {})
         .get("conjunto_hipotesis_abiertas", {}).get("hipotesis", []))
    return [x.get("familia") for x in h if x.get("familia")]


def main():
    pat = D.cargar_patrones()
    fallos = []
    t1, t2, t3 = D.DIALECTICA_FAMS
    for f in (t1, t2, t3):
        if f not in pat:
            fallos.append(f"G1: falta la familia {f} en el catálogo")

    # G1: entrelace
    if "insubordinacion" not in (_contra(pat, t1) & _favor(pat, t2)):
        fallos.append("G1: insubordinación no está en tesis-contra ∩ antítesis-favor")
    if "paz_interior" not in (_contra(pat, t2) & _favor(pat, t3)):
        fallos.append("G1: paz_interior no está en antítesis-contra ∩ síntesis-favor")

    # G2: fixture
    a = ["autoridad", "control"]
    b = ["insubordinacion", "confrontacion"]
    s = D.sintesis_desde(a, b, pat)
    if "paz_interior" not in s["sintesis"]:
        fallos.append(f"G2: la síntesis no contiene paz_interior: {s}")
    if not set(s["sintesis"]) <= _favor(pat, t3):
        fallos.append(f"G2: síntesis con tokens fuera de síntesis-favor: {s}")
    cyc = D.ciclo([("C1", a + b), ("C2", ["rutina", "opresion"])], pat)
    if len(cyc["cadena"]) != 2:
        fallos.append("G2: el ciclo no corrió los 2 cortes")
    if not cyc["cadena"][1]["tesis_acarreada_de_anterior"]:
        fallos.append("G2: la síntesis del C1 no se acarreó como tesis del C2")
    if cyc.get("can_decide_H") is not False:
        fallos.append("G2: can_decide_H no es False")

    # G3: las 8 selladas
    sint_favor = _favor(pat, t3)
    for caso in CASOS:
        ent = json.loads((ROOT / "casos" / "precedentes" / caso / "entrada.json").read_text(encoding="utf-8"))
        res = D.sobre_entrada(ent, pat)
        n_cortes = len(ent.get("cuts") or [])
        if len(res["cadena"]) != n_cortes:
            fallos.append(f"G3 {caso}: cadena {len(res['cadena'])} != cortes {n_cortes}")
        for paso in res["cadena"]:
            fuera = set(paso["sintesis"]) - sint_favor
            if fuera:
                fallos.append(f"G3 {caso} {paso['corte']}: síntesis inventada {fuera}")
    # resolver: el héroe en Che y consumo_sustancias en Elvis v1
    activas_che = _hipotesis_activas(ROOT / "motor" / "RESULT_ANONIMO4_Z90_20261113.json")
    r_heroe = D.resolver_falta("arquetipo_el_heroe", activas_che, pat, activas=set(activas_che))
    if not r_heroe.get("analogo") or r_heroe["analogo"] not in activas_che:
        fallos.append(f"G3 Che: resolver(héroe) sin análogo activo: {r_heroe}")
    activas_elvis = _hipotesis_activas(ROOT / "motor" / "RESULT_ANONIMO3_Z90_20261113.json")
    r_cons = D.resolver_falta("consumo_sustancias", activas_elvis, pat, activas=set(activas_elvis))
    if not r_cons.get("analogo") or r_cons["analogo"] not in activas_elvis:
        fallos.append(f"G3 Elvis: resolver(consumo_sustancias) sin análogo activo: {r_cons}")

    print("G1 entrelace: insubordinación tesis-contra/antítesis-favor; paz_interior antítesis-contra/síntesis-favor")
    print(f"G2 fixture: síntesis={s['sintesis']} vía={s['via']}; ciclo 2 cortes, acarreo OK")
    print(f"G3 Che: héroe -> análogo {r_heroe.get('analogo')} (solape {r_heroe.get('solape')}, {r_heroe.get('tokens_compartidos')})")
    print(f"G3 Elvis v1: consumo_sustancias -> análogo {r_cons.get('analogo')} (solape {r_cons.get('solape')}, {r_cons.get('tokens_compartidos')})")
    if fallos:
        print("PUERTA RECHAZADA:")
        for f in fallos:
            print(" -", f)
        return 1
    print("PUERTA PASA")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
