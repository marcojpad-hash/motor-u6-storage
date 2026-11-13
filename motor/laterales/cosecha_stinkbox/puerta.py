#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""puerta.py — Puerta del lateral cosecha del StinkBox.

G1 (estructural): el catálogo carga (244 familias, 703 tokens), el índice
   de casos resueltos carga (160 entradas) y el archivo manual de
   descubrimientos carga (13 entradas). can_decide_H es False: la cosecha
   solo lee y propone.
G2 (reproducción): la cosecha, corrida sobre los datos reales, reproduce
   los 13 descubrimientos del archivo manual
   (STINKBOX_PERSISTENTE/tokens_descubiertos_ciegos_z90_20261113.json):
   mismos casos, mismas familias, mismo lugar, mismo rank_fusion
   (tolerancia 1e-4) y mismo regimen; para las de Z, mismo valor.
G3 (los 4 que faltan): Tulipán v1/v2, Revolución y Che tienen entradas
   top-15 y en Z, con los top-1 que ya se conocen (Tulipán v1: creador;
   Revolución: tainter_01; Che: gobernante); Tulipán v1/v2 traen el token
   sin familia 'deuda' y Tulipán v2 los 5 tokens delta de Minsky;
   Elvis v2 trae el delta consumo_sustancias.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent  # motor-cameo/
sys.path.insert(0, str(HERE))
import cosecha as C

MANUAL = ROOT / "STINKBOX_PERSISTENTE" / "tokens_descubiertos_ciegos_z90_20261113.json"
FALTAN = ["TRANSICION1_Z90_20261113", "TRANSICION1_Z90_20261113_v2",
          "TRANSICION2_Z90_20261113", "ANONIMO4_Z90_20261113"]
TOP1_ESPERADO = {"TRANSICION1_Z90_20261113": ("arquetipo_el_creador", 29.25),
                 "TRANSICION2_Z90_20261113": ("tainter_01_inversion_complejidad_productiva", 30.89),
                 "ANONIMO4_Z90_20261113": ("arquetipo_el_gobernante", 35.22)}


def _cerca(a, b, tol=1e-4):
    if a is None or b is None:
        return a is b
    return abs(float(a) - float(b)) <= tol


def main():
    fallos = []
    fams, toks = C.cargar_catalogo()
    if len(fams) != 244 or len(toks) != 703:
        fallos.append(f"G1: catálogo {len(fams)} familias / {len(toks)} tokens (esperado 244 / 703)")
    ids_indice, n_entradas = C.cargar_indice()
    if n_entradas != 160:
        fallos.append(f"G1: índice {n_entradas} entradas (esperado 160)")
    manual = json.loads(MANUAL.read_text(encoding="utf-8"))
    descubrimientos = manual["tokens_descubiertos"]
    if len(descubrimientos) != 13:
        fallos.append(f"G1: archivo manual {len(descubrimientos)} descubrimientos (esperado 13)")
    if C.can_decide_H is not False:
        fallos.append("G1: can_decide_H no es False")

    # G2: correr la cosecha de verdad y comparar contra el manual.
    out, destino = C.cosechar_todo(fecha="20261113")
    cands = out["candidatos"]
    por_par = {}
    for c in cands:
        por_par.setdefault((c["caso"], c["familia"]), []).append(c)
    n_reproducidos = 0
    for d in descubrimientos:
        clave = (d["caso"], d["familia"])
        cands_par = por_par.get(clave, [])
        if not cands_par:
            fallos.append(f"G2: falta {clave[0]} / {clave[1]}")
            continue
        c = cands_par[0]
        if d.get("lugar") is not None:
            if c.get("lugar") != d["lugar"]:
                fallos.append(f"G2 {clave}: lugar {c.get('lugar')} != {d['lugar']}")
            if not _cerca(c.get("rank_fusion"), d.get("rank_fusion")):
                fallos.append(f"G2 {clave}: rank_fusion {c.get('rank_fusion')} != {d.get('rank_fusion')}")
        # El regimen del RESULT trae "MESeta_O_ESTABILIZACION" (caja mezclada
        # del motor); el manual lo normalizó a MESETA. Comparar sin caja.
        if str(c.get("regimen") or "").casefold() != str(d.get("regimen") or "").casefold():
            fallos.append(f"G2 {clave}: regimen {c.get('regimen')} != {d.get('regimen')}")
        if d.get("regimen", "").endswith("_en_Z"):
            if not _cerca(c.get("valor"), _valor_manual(d)):
                fallos.append(f"G2 {clave}: valor Z {c.get('valor')} != {_valor_manual(d)} (manual)")
        n_reproducidos += 1
    print(f"G2 reproducción: {n_reproducidos}/13 del archivo manual")

    # G3: los 4 casos que faltan en el manual.
    for caso in FALTAN:
        tops = [c for c in cands if c["caso"] == caso and c["tipo"] == "familia_top15"]
        zs = [c for c in cands if c["caso"] == caso and c["tipo"] == "familia_en_Z"]
        if not tops:
            fallos.append(f"G3 {caso}: sin top-15")
        if not zs:
            fallos.append(f"G3 {caso}: sin familias en Z")
        if caso in TOP1_ESPERADO and tops:
            fam_esp, rf_esp = TOP1_ESPERADO[caso]
            t1 = tops[0]
            if t1["familia"] != fam_esp or not _cerca(t1["rank_fusion"], rf_esp, tol=0.01):
                fallos.append(f"G3 {caso}: top-1 {t1['familia']} {t1['rank_fusion']} != {fam_esp} {rf_esp}")
    for caso in ("TRANSICION1_Z90_20261113", "TRANSICION1_Z90_20261113_v2"):
        if not any(c["caso"] == caso and c.get("token") == "deuda" for c in cands):
            fallos.append(f"G3 {caso}: falta el token sin familia 'deuda'")
    delta_tulipan = {c.get("token") for c in cands
                    if c["caso"] == "TRANSICION1_Z90_20261113_v2" and c["tipo"] == "token_delta_version"}
    for tok in ("busqueda_riesgo", "cautela", "codicia", "negacion_problema", "optimismo"):
        if tok not in delta_tulipan:
            fallos.append(f"G3 Tulipán v2: falta el delta '{tok}'")
    if not any(c["caso"] == "ANONIMO3_Z90_20261113_v2" and c.get("token") == "consumo_sustancias"
               for c in cands):
        fallos.append("G3 Elvis v2: falta el delta 'consumo_sustancias'")

    print(f"G1 catálogo: {len(fams)} familias / {len(toks)} tokens; índice: {n_entradas} entradas")
    print(f"G3 faltan: {len(FALTAN)} casos con top-15 y en Z; delta Minsky Tulipán v2: {sorted(delta_tulipan)}")
    r = out["resumen"]
    print(f"cosecha: {r['familia_top15']} top-15, {r['familia_en_Z']} en Z, "
          f"{r['token_sin_familia']} sin familia, {r['token_delta_version']} delta, total {r['total']}")
    print(f"archivo: {destino}")
    if fallos:
        print("PUERTA RECHAZADA:")
        for f in fallos:
            print(" -", f)
        return 1
    print("PUERTA PASA")
    return 0


def _valor_manual(d):
    """El valor en Z del manual vive en el contexto ('... (X 0.0175 ...)')."""
    import re
    m = re.search(r"(\d+\.\d+)", d.get("contexto") or "")
    return float(m.group(1)) if m else None


if __name__ == "__main__":
    raise SystemExit(main())
