#!/usr/bin/env python3
"""VENN por corte entre sistemas (PATCH 010a). Alimenta motor_interrelacion_extensible_v0_1.venn con un
conjunto por sistema y por corte sobre un universo común (tokens de evidencia del corte).
NO decide nada: ALIMENTA_H=False, can_decide_H=False, fuera del ranking.

Sistemas (todo leído de salidas reales del run; nada se inventa):
  souriau        : tokens que portan alguna de las 6 funciones (features.funciones_souriau.por_corte).
  polti          : tokens del corte que están en tokens_favor (catálogo) de las situaciones Polti activas en el
                   corte (features.polti_caldero.polti_por_corte[].union).
  caldero_Q      : tokens del corte en tokens_candidatos del cuadrante activo (plugin_circulo_monomito_v2.
                   ESTRUCTURAS_CANDIDATAS[cuadrante_activo]).
  cameo          : tokens CAMEO activados en el corte (features.cameo_703_lateral.events_by_cut).
  memoria_caldero: activaciones de memoria persistente del Caldero en el corte (features.interrelation.raw_activations).
  area_tokens    : tokens de familias del área de tokens activos en el corte (sidecar_area_tokens_v1).
Sigla Souriau por corte: misma regla que SOURIAU_7783_INVESTIGACION/siglas_souriau_casos.py (sigla_estructural),
con sufijo |Q|P de contexto.
Complemento a anillos/Tusi: anillos dicen CUÁNDO coinciden los sistemas; Venn dice QUÉ comparten.
"""
from __future__ import annotations
from collections import defaultdict
from itertools import combinations
from typing import Any, Dict, List

VERSION = "VENN_SISTEMAS_V1_PATCH010"
ORD = ["leon", "sol", "tierra", "marte", "balanza", "luna"]
LET = dict(zip(ORD, "LSTMBU"))
SISTEMAS = ["souriau", "polti", "caldero_Q", "cameo", "memoria_caldero", "area_tokens"]


def sigla_estructural(funciones):
    """Copia de siglas_souriau_casos.sigla_estructural (SOURIAU_7783_INVESTIGACION)."""
    pres = [f for f in ORD if funciones.get(f)]
    aus = [f for f in ORD if not funciones.get(f)]
    toks = {f: frozenset(funciones[f]) for f in pres}
    padre = {f: f for f in pres}

    def raiz(x):
        while padre[x] != x:
            x = padre[x]
        return x
    for i, a in enumerate(pres):
        for b in pres[i + 1:]:
            if toks[a] & toks[b]:
                padre[raiz(b)] = raiz(a)
    bloques = defaultdict(list)
    for f in pres:
        bloques[raiz(f)].append(f)
    partes = []
    for fs in bloques.values():
        grupos = defaultdict(list)
        for f in fs:
            grupos[toks[f]].append(f)
        sub = sorted(("".join(LET[f] for f in sorted(g, key=ORD.index)) for g in grupos.values()), key=lambda s: "LSTMBU".index(s[0]))
        partes.append("~".join(sub))
    partes.sort(key=lambda s: "LSTMBU".index(s[0]))
    s = f"S{len(partes)}:" + ".".join(partes) + "/" + ("".join(LET[f] for f in aus) or "-")
    if funciones.get("luna"):
        s += ";U>?"
    flags = []
    if funciones.get("sol") and funciones.get("leon") and set(funciones["sol"]) <= set(funciones["leon"]):
        flags.append("artefacto_S_sub_L")
    return s, len(partes), flags


def _tok(c):
    return [str(t) for e in ("P", "A", "C") for t, _ in (c.get(e) or [])]


def conjuntos_por_corte(case_cuts, features, catalogo, estructuras_q, area_por_corte) -> List[Dict[str, Any]]:
    fs = {str(x.get("corte")): x for x in ((features.get("funciones_souriau") or {}).get("por_corte") or [])}
    pol = {str(x.get("corte")): x for x in ((features.get("polti_caldero") or {}).get("polti_por_corte") or [])}
    mono = {str(x.get("corte")): x for x in ((features.get("plugin_circulo_monomito") or {}).get("posicion_monomito_por_corte") or [])}
    cam = (features.get("cameo_703_lateral") or {}).get("events_by_cut") or {}
    mem = defaultdict(set)
    for a in ((features.get("interrelation") or {}).get("raw_activations") or []):
        mem[str(a.get("cut"))].add(str(a.get("token")))
    area = {str(x.get("corte")): {a["token"] for a in x.get("activaciones") or []} for x in area_por_corte or []}
    out = []
    for c in case_cuts or []:
        cid = str(c.get("id"))
        obs = set(_tok(c))
        f = (fs.get(cid) or {}).get("funciones") or {}
        souriau = set(t for v in f.values() for t in (v or []))
        pol_act = list(dict.fromkeys(x[0] for x in ((pol.get(cid) or {}).get("union") or []) if isinstance(x, (list, tuple))))
        polti = set()
        for pid in pol_act:
            polti |= obs & set(((catalogo.get(pid) or {}).get("tokens_favor") or {}))
        q_act = list((mono.get(cid) or {}).get("cuadrante_activo") or [])
        cq = set()
        for q in q_act:
            cq |= obs & set(((estructuras_q or {}).get(q) or {}).get("tokens_candidatos") or [])
        cameo = set()
        for ev in cam.get(cid) or []:
            for k in ("token", "tokens", "code", "cameo_code"):
                v = ev.get(k) if isinstance(ev, dict) else None
                if isinstance(v, list): cameo |= {str(x) for x in v}
                elif v: cameo.add(str(v))
        sig, k, flags = sigla_estructural(f) if f else (None, 0, [])
        ctx = "|" + ("+".join(q.split("_")[0] for q in q_act) or "Q?") + "|P" + ("+".join(p.split("_")[0] for p in pol_act) or "?")
        # PATCH 016: con funciones de personajes, el conjunto souriau son ids de rol (no tokens): se reporta además el Venn
        # de personajes entre las seis funciones (qué agentes comparten funciones en el corte).
        vp = None
        if (features.get("funciones_souriau") or {}).get("modo") == "personajes_016":
            occ = defaultdict(list)
            for fn_ in ORD:
                for ag in (f.get(fn_) or []):
                    occ[ag].append(fn_)
            reg = defaultdict(list)
            for ag, fns in sorted(occ.items()):
                reg["&".join(fns)].append(ag)
            vp = {"regiones_funciones": dict(sorted(reg.items())), "agentes_en_varias_funciones": sorted(a for a, v in occ.items() if len(v) > 1)}
        out.append({"corte": cid, "venn_personajes_016": vp, "sets": {"souriau": sorted(souriau), "polti": sorted(polti), "caldero_Q": sorted(cq), "cameo": sorted(cameo),
                                           "memoria_caldero": sorted(mem.get(cid, set())), "area_tokens": sorted(area.get(cid, set()))},
                    "polti_activas": pol_act, "cuadrantes_activos": q_act, "sigla_souriau": (sig + ctx) if sig else None, "sigla_flags": flags})
    return out


def venn(case_cuts, features, catalogo, estructuras_q, area_por_corte, interrel_mod) -> Dict[str, Any]:
    filas = conjuntos_por_corte(case_cuts, features, catalogo, estructuras_q, area_por_corte)
    eng = interrel_mod.InterrelationEngine()
    for r in filas:
        memb = defaultdict(set)
        for s, toks in r["sets"].items():
            for t in toks:
                memb[t].add(s)
        for t in sorted(memb):
            eng.register(f"{r['corte']}::{t}", "venn_evidencia", None, tuple(sorted(memb[t])))
            eng.activate(r["corte"], f"{r['corte']}::{t}", None, "PATCH010_venn_sistemas")
    run = eng.run()
    por_corte, nucleos = [], {}
    for r in filas:
        vs = run["venn_sets"].get(r["corte"], {})
        sets = {s: set(r["sets"][s]) for s in SISTEMAS}
        vivos = [s for s in SISTEMAS if sets[s]]
        memb = defaultdict(set)
        for s in vivos:
            for t in sets[s]:
                memb[t].add(s)
        regiones = defaultdict(list)
        for t, ss in sorted(memb.items()):
            regiones["&".join(s for s in SISTEMAS if s in ss)].append(t)
        pares = []
        for a, b in combinations(vivos, 2):
            i = sets[a] & sets[b]; u = sets[a] | sets[b]
            pares.append({"par": [a, b], "interseccion": sorted(i), "jaccard": round(len(i) / len(u), 4) if u else 0.0})
        nucleo = sorted(t for t, ss in memb.items() if len(ss) >= 3)
        nucleos[r["corte"]] = set(nucleo)
        por_corte.append({"corte": r["corte"], "venn_personajes_016": r.get("venn_personajes_016"), "sigla_souriau": r["sigla_souriau"], "sigla_flags": r["sigla_flags"], "polti_activas": r["polti_activas"],
                          "cuadrantes_activos": r["cuadrantes_activos"], "tamanos": {s: len(sets[s]) for s in SISTEMAS},
                          "sistemas_vacios": [s for s in SISTEMAS if not sets[s]], "venn_sets_motor_interrelacion": {k: [x.split("::", 1)[1] for x in v] for k, v in vs.items()},
                          "regiones_no_vacias": dict(sorted(regiones.items())), "intersecciones_por_par": pares,
                          "nucleo_3_o_mas_sistemas": nucleo})
    cuts = [r["corte"] for r in filas]
    mov = [{"de": a, "a": b, "persiste": sorted(nucleos[a] & nucleos[b]), "entra": sorted(nucleos[b] - nucleos[a]), "sale": sorted(nucleos[a] - nucleos[b])}
           for a, b in zip(cuts, cuts[1:])]
    vacios_siempre = [s for s in SISTEMAS if all(not x["tamanos"][s] for x in por_corte)]
    return {"version": VERSION, "ALIMENTA_H": False, "can_decide_H": False, "feeds_predictor": False, "por_corte": por_corte,
            "movimiento_nucleo": mov, "sistemas_vacios_en_todo_el_caso": vacios_siempre,
            "motivos_vacios": {"cameo": "cameo_703_lateral.events_by_cut sin eventos en este caso (sin texto/actores CAMEO en el input)",
                               "memoria_caldero": "sin activaciones de memoria persistente del Caldero en el corte (solo hay si la memoria coincide con el caso)",
                               "area_tokens": "ningún token de familias del área en el corte"},
            "interrelation_engine": {"n_luces": len(run["unique_tokens"]), "n_activaciones": len(run["raw_activations"]), "failures": run["failures"]}}
