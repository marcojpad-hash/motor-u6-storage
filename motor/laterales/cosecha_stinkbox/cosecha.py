#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosecha.py — Cosecha del StinkBox (lateral, contrato COSECHA_V1_20261113).

El StinkBox acumula casos; al ejecutarlos se activan tokens y familias que
no habíamos visto. Esta cosecha es el REGRESO: lee el índice de casos
resueltos y los RESULT disponibles, y escribe la propuesta de lo que se
juntó, como material de lateral. No decide nada: Marco decide cuáles
candidatos se activan como análogos.

Qué cosecha, por caso:
  - familia_top15: las 15 hipótesis de
    salida_interpretable.conjunto_hipotesis_abiertas (lugar, rank_fusion,
    regimen de trazabilidad_geometrica).
  - familia_en_Z: las familias activas en Z
    (apuesta_destino_personal.familias_activas_en_Z: auge / caída /
    ruptura, con su valor).
  - token_sin_familia: tokens de la entrada (P/A/C de todos los cortes)
    que NO están en los 703 del catálogo. Un token sin familia es inerte
    (vector cero): el motor no lo puede prender. Son los candidatos
    nuevos de verdad.
  - token_delta_version: tokens que entraron en una versión _v2 (o _vN)
    y no estaban en la _v1 del mismo caso (p. ej. consumo_sustancias
    en Elvis v2; los 5 de Minsky en Tulipán v2).

Una familia que es top-15 Y está activa en Z sale UNA sola vez (como
top-15, con la evidencia en Z guardada en regimen_z / valor_z).

NO toca el Engine (MOTOR_V15_3_UNICO) ni el catálogo 244: solo lee.
can_decide_H = False. Salida:
  motor/laterales/cosecha_stinkbox/COSECHA_YYYYMMDD.json

Uso:
  python3 motor/laterales/cosecha_stinkbox/cosecha.py [--fecha YYYYMMDD]
"""
import json
import re
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent  # motor-cameo/

CONTRATO = "COSECHA_V1_20261113"
can_decide_H = False

REGIMEN_Z = {"auge": "auge_en_Z", "caida": "caida_en_Z", "ruptura": "ruptura_en_Z"}


def cargar_catalogo(root=ROOT):
    """Devuelve (familias_244: set, tokens_703: set)."""
    pat = json.loads((root / "motor" / "motor" / "patterns_final_v14.json").read_text(encoding="utf-8"))
    fams = set(pat.keys())
    toks = set()
    for d in pat.values():
        toks |= set((d.get("tokens_favor") or {}).keys())
        toks |= set((d.get("tokens_contra") or {}).keys())
    return fams, toks


def cargar_indice(root=ROOT):
    """Casos distintos del índice (sin los sufijos _SIN_ULTIMO/_RETENIDO)."""
    idx = json.loads((root / "STINKBOX_STORAGE" / "resolved_cases_index.json").read_text(encoding="utf-8"))
    out = set()
    for e in idx.get("cases", []):
        cid = e.get("case_id") or ""
        cid = re.sub(r"_(SIN_ULTIMO|RETENIDO)$", "", cid)
        if cid:
            out.add(cid)
    return out, len(idx.get("cases", []))


def buscar_entrada(root, case_id):
    for base in ("casos/precedentes", "casos/fabrica/cola"):
        p = root / base / case_id / "entrada.json"
        if p.is_file():
            return p
    return None


def buscar_result(root, case_id):
    p = root / "motor" / f"RESULT_{case_id}.json"
    return p if p.is_file() else None


def tokens_de_entrada(entrada):
    """token -> {cortes, ejes, peso_max, n}."""
    out = {}
    for cut in entrada.get("cuts") or []:
        nombre = cut.get("corte") or cut.get("cut_id") or cut.get("id") or "?"
        for eje in ("P", "A", "C"):
            for par in cut.get(eje) or []:
                tok, peso = par[0], par[1]
                d = out.setdefault(tok, {"cortes": [], "ejes": [], "peso_max": 0.0, "n": 0})
                d["cortes"].append(nombre)
                d["ejes"].append(eje)
                d["peso_max"] = max(d["peso_max"], float(peso))
                d["n"] += 1
    for d in out.values():
        d["cortes"] = sorted(set(d["cortes"]))
        d["ejes"] = sorted(set(d["ejes"]))
    return out


def _top15(result):
    """Las 15 hipótesis abiertas: [(familia, lugar, rank_fusion, regimen)]."""
    h = ((result.get("salida_interpretable") or {})
         .get("conjunto_hipotesis_abiertas", {}).get("hipotesis") or [])
    out = []
    for i, x in enumerate(h, start=1):
        fam = x.get("familia")
        if not fam:
            continue
        out.append((fam, i, float(x.get("rank_fusion") or 0.0),
                    ((x.get("trazabilidad_geometrica") or {}).get("regimen"))))
    if out:
        return out, "conjunto_hipotesis_abiertas"
    # Respaldo: por_hipotesis ordenado por rank_fusion (sin regimen propio).
    ph = ((result.get("predictibilidad_021") or {})
          .get("predictibilidad", {}).get("por_hipotesis") or {})
    orden = sorted(ph.items(), key=lambda kv: -float((kv[1] or {}).get("rank_fusion") or 0.0))
    return [(f, i, float((d or {}).get("rank_fusion") or 0.0), None)
            for i, (f, d) in enumerate(orden[:15], start=1)], "por_hipotesis"


def _en_z(result):
    """[(familia, regimen_z, valor)] de familias_activas_en_Z."""
    z = ((result.get("apuesta_destino_personal") or {}).get("familias_activas_en_Z") or {})
    out = []
    for clave, regimen in REGIMEN_Z.items():
        for par in z.get(clave) or []:
            out.append((par[0], regimen, float(par[1])))
    return out


def cosechar_caso(root, case_id, tokens_703, entradas_cache=None):
    """Cosecha un caso. Devuelve (entradas, notas)."""
    entradas = []
    notas = []
    rpath = buscar_result(root, case_id)
    epath = buscar_entrada(root, case_id)
    result = None
    if rpath is not None:
        try:
            result = json.loads(rpath.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001 - un RESULT roto no tumba la cosecha
            notas.append(f"RESULT ilegible: {exc}")
    if result is not None:
        top, fuente = _top15(result)
        z = _en_z(result)
        zmap = {fam: (reg, val) for fam, reg, val in z}
        for fam, lugar, rf, regimen in top:
            e = {"tipo": "familia_top15", "caso": case_id, "familia": fam,
                 "lugar": lugar, "rank_fusion": round(rf, 6),
                 "regimen": regimen, "valor": None,
                 "contexto": f"Top 15 por rank_fusion en {case_id} (lugar {lugar} de 15, fuente {fuente}).",
                 "en_catalogo_244": True}
            if fam in zmap:
                e["regimen_z"], e["valor_z"] = zmap[fam]
                e["contexto"] += f" También activa en Z ({zmap[fam][0]}: {zmap[fam][1]})."
            entradas.append(e)
        for fam, reg, val in z:
            if fam in {x["familia"] for x in entradas}:
                continue
            entradas.append({"tipo": "familia_en_Z", "caso": case_id, "familia": fam,
                             "lugar": None, "rank_fusion": None,
                             "regimen": reg, "valor": val,
                             "contexto": f"Activa en Z en {case_id} ({reg}: {val}).",
                             "en_catalogo_244": True})
    elif rpath is None:
        notas.append("sin RESULT en motor/")
    entrada = None
    if epath is not None:
        try:
            entrada = json.loads(epath.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            notas.append(f"entrada ilegible: {exc}")
    if entrada is not None:
        toks = tokens_de_entrada(entrada)
        sin_familia = {t: d for t, d in toks.items() if t not in tokens_703}
        delta = {}
        m = re.match(r"^(.*)_v(\d+)$", case_id)
        if m:
            base_id = m.group(1)
            base_path = buscar_entrada(root, base_id)
            if base_path is not None:
                base_toks = tokens_de_entrada(json.loads(base_path.read_text(encoding="utf-8")))
                delta = {t: d for t, d in toks.items() if t not in base_toks}
        for tok, d in sorted(sin_familia.items()):
            entradas.append({"tipo": "token_sin_familia", "caso": case_id,
                             "familia": tok, "token": tok,
                             "lugar": None, "rank_fusion": None,
                             "regimen": "token_sin_familia", "valor": d["peso_max"],
                             "contexto": (f"Token en la entrada de {case_id} ({', '.join(d['cortes'])}; "
                                          f"ejes {', '.join(d['ejes'])}; peso max {d['peso_max']}) "
                                          f"sin familia en el 244: el motor no lo puede prender."),
                             "cortes": d["cortes"], "ejes": d["ejes"],
                             "n_apariciones": d["n"], "en_catalogo_244": False})
        for tok, d in sorted(delta.items()):
            entradas.append({"tipo": "token_delta_version", "caso": case_id,
                             "familia": tok, "token": tok,
                             "lugar": None, "rank_fusion": None,
                             "regimen": "token_de_entrada", "valor": d["peso_max"],
                             "contexto": (f"Token que entró en {case_id} y no estaba en la versión "
                                          f"anterior ({', '.join(d['cortes'])}; ejes {', '.join(d['ejes'])}; "
                                          f"peso max {d['peso_max']})."),
                             "cortes": d["cortes"], "ejes": d["ejes"],
                             "n_apariciones": d["n"],
                             "en_catalogo_244": tok in tokens_703})
    elif epath is None:
        notas.append("sin entrada en casos/precedentes ni casos/fabrica/cola")
    return entradas, notas


def cosechar_todo(root=ROOT, fecha=None):
    """Cosecha todo el StinkBox y escribe COSECHA_YYYYMMDD.json."""
    fecha = fecha or date.today().strftime("%Y%m%d")
    fams_244, tokens_703 = cargar_catalogo(root)
    ids_indice, n_entradas_indice = cargar_indice(root)
    ids_result = set()
    for f in (root / "motor").glob("RESULT_*.json"):
        nombre = f.name[7:-5]
        if nombre.endswith("_RECIBO_EJECUCION") or nombre.endswith("_CEB_LEDGER_MANIFIESTO"):
            continue
        ids_result.add(nombre)
    ids_entrada = set()
    for base in ("casos/precedentes", "casos/fabrica/cola"):
        for d in (root / base).glob("*/entrada.json"):
            ids_entrada.add(d.parent.name)
    casos = sorted(ids_indice | ids_result | ids_entrada)
    candidatos = []
    sin_result = []
    sin_entrada = []
    notas_por_caso = {}
    for cid in casos:
        ents, notas = cosechar_caso(root, cid, tokens_703)
        candidatos.extend(ents)
        if buscar_result(root, cid) is None:
            sin_result.append(cid)
        if buscar_entrada(root, cid) is None:
            sin_entrada.append(cid)
        if notas:
            notas_por_caso[cid] = notas
    resumen = {}
    for tipo in ("familia_top15", "familia_en_Z", "token_sin_familia", "token_delta_version"):
        resumen[tipo] = sum(1 for c in candidatos if c["tipo"] == tipo)
    resumen["total"] = len(candidatos)
    out = {"contrato": CONTRATO,
           "fecha": fecha,
           "can_decide_H": False,
           "fuente_indice": "STINKBOX_STORAGE/resolved_cases_index.json",
           "n_entradas_indice": n_entradas_indice,
           "n_casos_distintos_indice": len(ids_indice),
           "n_result_en_motor": len(ids_result),
           "n_entradas_disponibles": len(ids_entrada),
           "n_casos_cosechados": len(casos),
           "casos_sin_result": sorted(sin_result),
           "casos_sin_entrada": sorted(sin_entrada),
           "notas_por_caso": notas_por_caso,
           "resumen": resumen,
           "candidatos": candidatos}
    destino = HERE / f"COSECHA_{fecha}.json"
    destino.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return out, destino


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    fecha = None
    if "--fecha" in argv:
        fecha = argv[argv.index("--fecha") + 1]
    out, destino = cosechar_todo(fecha=fecha)
    r = out["resumen"]
    print(f"cosecha {out['fecha']}: {out['n_casos_cosechados']} casos "
          f"({out['n_result_en_motor']} RESULT, {out['n_entradas_disponibles']} entradas)")
    print(f"  familias top15: {r['familia_top15']} | familias en Z: {r['familia_en_Z']} | "
          f"tokens sin familia: {r['token_sin_familia']} | tokens delta versión: {r['token_delta_version']} | "
          f"total: {r['total']}")
    print(f"  sin RESULT: {len(out['casos_sin_result'])} | sin entrada: {len(out['casos_sin_entrada'])}")
    print(f"  escrito: {destino}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
