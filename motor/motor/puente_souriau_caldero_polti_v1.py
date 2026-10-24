#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""puente_souriau_caldero_polti_v1.py — PATCH 009 (2026-10-06).

Puente geométrico: seis funciones de Souriau (marco_7783) + cuadrante Caldero II (Q1-Q4,
plugin_circulo_monomito_v2) + situaciones Polti activas (sidecar_polti_caldero) por corte,
y sus deltas entre cortes consecutivos. Lo consume la trazabilidad (sidecar_trazabilidad_temporal,
campo aditivo) desde el hub laterales_unico_v1.

Candados: can_decide_H=False · no escribe H1/H2 · no reordena candidatos · no escribe catálogo ·
no escribe archivos (el calor de zonas es en memoria, por caso; NO usa marco_7783.visitar ni zonas_7783.json).

Entradas (todas ya calculadas por el pack; aquí no se deriva nada nuevo):
  dist      = marco_funciones_souriau.distribuir(cuts)            (seis funciones + cúmulo por corte)
  marco     = módulo marco_7783 (se usan SOLO zona_de/_estado, puras; N=7783)
  monomito  = features["plugin_circulo_monomito"]                (posicion_monomito_por_corte[*].cuadrante_activo)
  polti     = features["polti_caldero"]                          (polti_por_corte[*].union: familias ^\\d+_ del catálogo)

Codificación de zona: la de marco_7783.zona_de tal cual (base 3 sobre las seis funciones, mod 7783):
solo 3^6 = 729 zonas alcanzables. La regla que lleva las seis funciones al espacio completo 7783
NO está definida en disco: PENDIENTE de la regla de Mj (no se inventa aquí).
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import re

VERSION = "PUENTE_SOURIAU_CALDERO_POLTI_V1_20261006"
FUNCIONES = ("leon", "sol", "tierra", "marte", "balanza", "luna")   # mismo orden que marco_7783.zona_de
CUADRANTES = ("Q1_Separacion_1_3", "Q2_Descenso_4_6", "Q3_Ordeal_7_9", "Q4_Retorno_10_12")
N_POLTI = 36
RX_POLTI = re.compile(r"^(\d+)_")
ESTADO_TXT = {0: "vacia", 1: "presente", 2: "cumulo"}
VECTOR_SCHEMA = (["fn:" + f for f in FUNCIONES] + ["q:" + q.split("_")[0] for q in CUADRANTES]
                 + [f"polti:{i}" for i in range(1, N_POLTI + 1)])


def _por_id(rows: List[Dict[str, Any]], key: str = "corte") -> Dict[str, Dict[str, Any]]:
    return {str(r.get(key)): r for r in rows or [] if isinstance(r, dict)}


def _fila(rows_by_id, rows_list, cid, i):
    r = rows_by_id.get(str(cid))
    if r is None and i < len(rows_list or []):
        r = rows_list[i]
    return r or {}


def _estados(marco, pc) -> List[int]:
    fn = pc.get("funciones") or {}
    cum = pc.get("cumulo") or {}
    return [int(marco._estado(fn.get(n) or [], cum, n)) for n in FUNCIONES]


def construir(dist: Dict[str, Any], marco, monomito: Optional[Dict[str, Any]] = None,
              polti: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    por_corte_fn = list((dist or {}).get("por_corte") or [])
    mono_rows = list((monomito or {}).get("posicion_monomito_por_corte") or [])
    polti_rows = list((polti or {}).get("polti_por_corte") or [])
    mono_by, polti_by = _por_id(mono_rows), _por_id(polti_rows)
    n_zonas = int(getattr(marco, "N", 7783))

    cortes: List[Dict[str, Any]] = []
    calor: Dict[int, int] = {}
    for i, pc in enumerate(por_corte_fn):
        cid = pc.get("corte")
        est = _estados(marco, pc)
        zona = int(marco.zona_de(pc))
        calor[zona] = calor.get(zona, 0) + 1
        cum = pc.get("cumulo") or {}
        pares_cumulo = sorted({f"{a}~{b}" for fns in cum.values() for a in fns for b in fns if FUNCIONES.index(a) < FUNCIONES.index(b)}) \
            if all(f in FUNCIONES for fns in cum.values() for f in fns) else []
        mrow = _fila(mono_by, mono_rows, cid, i)
        qs = [q for q in (mrow.get("cuadrante_activo") or []) if q in CUADRANTES]
        prow = _fila(polti_by, polti_rows, cid, i)
        pol = [[str(x[0]), float(x[1])] for x in (prow.get("union") or []) if isinstance(x, (list, tuple)) and x and RX_POLTI.match(str(x[0]))]
        pol_idx = sorted({int(RX_POLTI.match(n).group(1)) for n, _ in pol if 1 <= int(RX_POLTI.match(n).group(1)) <= N_POLTI})
        vec = est + [1 if q in qs else 0 for q in CUADRANTES] + [1 if k in pol_idx else 0 for k in range(1, N_POLTI + 1)]
        # discrepancia ENTRE los seis agentes dentro del corte: |e_a - e_b| por par (15 pares)
        disc_int = {f"{FUNCIONES[a]}~{FUNCIONES[b]}": abs(est[a] - est[b]) for a in range(6) for b in range(a + 1, 6)}
        _sin_dato = pc.get("estado_personajes") == "SIN_TEXTO"  # PATCH 016: corte sin texto propio -> anillo Souriau sin dato (fase congelada)
        cortes.append({
            "corte": cid, "zona": zona, "calor_en_caso": calor[zona],
            "agentes_por_funcion": {f: list((pc.get("funciones") or {}).get(f) or []) for f in FUNCIONES} if (dist or {}).get("modo") == "personajes_016" else None,
            "funciones_del_protagonista": pc.get("funciones_del_protagonista"), "luna_ayuda_a": pc.get("luna_ayuda_a"),
            "sin_dato_souriau": _sin_dato,
            "funciones_estado": dict(zip(FUNCIONES, est)), "vector_funciones": est,
            "cumulos": {t: list(f) for t, f in sorted(cum.items())}, "n_cumulos": len(cum), "pares_en_cumulo": pares_cumulo,
            "discrepancia_entre_agentes": {"suma": sum(disc_int.values()), "pares_distintos": sum(1 for v in disc_int.values() if v)},
            "cuadrantes_caldero": qs, "cuadrante_fuente": "plugin_circulo_monomito_v2.posicion_monomito_por_corte" if mrow else None,
            "polti_activas": pol, "polti_idx": pol_idx, "polti_fuente": "sidecar_polti_caldero.polti_por_corte.union" if prow else None,
            "vector": vec,
        })

    deltas: List[Dict[str, Any]] = []
    vistos: List[int] = []
    for i, c in enumerate(cortes):
        if i == 0:
            vistos.append(c["zona"]); continue
        a = cortes[i - 1]
        cambian = {FUNCIONES[j]: [ESTADO_TXT[a["vector_funciones"][j]], ESTADO_TXT[c["vector_funciones"][j]]]
                   for j in range(6) if a["vector_funciones"][j] != c["vector_funciones"][j]}
        dv = [c["vector"][k] - a["vector"][k] for k in range(len(c["vector"]))]
        revisita = (c["zona"] != a["zona"]) and (c["zona"] in vistos)
        vistos.append(c["zona"])
        deltas.append({
            "de": a["corte"], "a": c["corte"],
            "funciones_cambian": cambian,
            "discrepancia_hamming": len(cambian),
            "discrepancia_vector": [c["vector_funciones"][j] - a["vector_funciones"][j] for j in range(6)],
            "zona": [a["zona"], c["zona"]], "transicion_zona": c["zona"] != a["zona"], "revisita_zona": revisita,
            "cuadrante_entra": [q for q in c["cuadrantes_caldero"] if q not in a["cuadrantes_caldero"]],
            "cuadrante_sale": [q for q in a["cuadrantes_caldero"] if q not in c["cuadrantes_caldero"]],
            "polti_entra": [n for n, _ in c["polti_activas"] if n not in {x for x, _ in a["polti_activas"]}],
            "polti_sale": [n for n, _ in a["polti_activas"] if n not in {x for x, _ in c["polti_activas"]}],
            "delta_vector": dv, "delta_L1": sum(abs(x) for x in dv),
        })

    ham = [d["discrepancia_hamming"] for d in deltas]
    cambios_por_fn = {f: sum(1 for d in deltas if f in d["funciones_cambian"]) for f in FUNCIONES}
    pares_cum: Dict[str, int] = {}
    for c in cortes:
        for p in c["pares_en_cumulo"]:
            pares_cum[p] = pares_cum.get(p, 0) + 1
    resumen = {
        "n_cortes": len(cortes),
        "zonas_visitadas": sorted(calor), "n_zonas_distintas": len(calor),
        "secuencia_zonas": [c["zona"] for c in cortes],
        "n_transiciones_zona": sum(1 for d in deltas if d["transicion_zona"]),
        "n_revisitas_zona": sum(1 for d in deltas if d["revisita_zona"]),
        "discrepancia_media": round(sum(ham) / len(ham), 4) if ham else None,
        "discrepancia_max": max(ham) if ham else None,
        "cambios_por_funcion": cambios_por_fn,
        "cumulos_total": sum(c["n_cumulos"] for c in cortes),
        "cumulos_por_corte": [c["n_cumulos"] for c in cortes],
        "pares_en_cumulo_conteo": dict(sorted(pares_cum.items())),
        "cortes_con_cuadrante": sum(1 for c in cortes if c["cuadrantes_caldero"]),
        "cortes_con_polti": sum(1 for c in cortes if c["polti_activas"]),
        "delta_L1_medio": round(sum(d["delta_L1"] for d in deltas) / len(deltas), 4) if deltas else None,
        "calor_en_caso": {str(k): v for k, v in sorted(calor.items())},
    }
    return {
        "version": VERSION, "status": "EXECUTED" if cortes else "SIN_CORTES",
        "can_decide_H": False, "escribe_H": False, "entra_al_ranking": False, "escribe_archivos": False,
        "n_zonas_marco": n_zonas, "zonas_alcanzables_codificacion_actual": 3 ** 6,
        "codificacion_zona": "marco_7783.zona_de: base3(leon,sol,tierra,marte,balanza,luna; 0 vacia/1 presente/2 cumulo) mod 7783",
        "brecha_7783": "PENDIENTE regla de Mj: 7783 = funciones posibles notables por discrepancias entre los seis agentes en interacción consistente (y sus representaciones animales); la codificación actual solo alcanza 729. No se inventa el mapeo.",
        "modo_funciones": (dist or {}).get("modo"),
        "advertencia_extractor": ("PATCH 016: funciones = personajes del corte (personajes_corte_016, ids de rol neutros, solo texto propio hecho/narracion; corte sin texto -> sin dato Souriau). Funciones DERIVADAS por regla, no declaradas."
                                  if (dist or {}).get("modo") == "personajes_016" else
                                  "marco_funciones_souriau: sol=P[:3] ⊂ leon=P[:5] → leon/sol casi siempre en cúmulo (estado 2) cuando hay P; marte=A[:5], tierra=C[:5]; balanza/luna por raíces léxicas (suelen quedar vacías). Funciones DERIVADAS, no declaradas."),
        "vector_schema": VECTOR_SCHEMA,
        "por_corte": cortes, "deltas": deltas, "resumen": resumen,
    }


# ======================================================================= ANILLOS (visión Mj 02:32 CT)
# Cada anillo = una fase φ_t en la MISMA circunferencia (círculo unidad, igual que billar_circular v0_1/v0_2).
# Mapeos fase<-dato (DECISIONES DE DISEÑO, documentadas; los datos son reales del corte):
#   caldero : cuadrante activo Qk (monomito v2) -> centro del cuadrante (k-1)·π/2 + π/4; varios Q -> media circular.
#   polti   : situación Polti n (1..36, numeración del catálogo) -> 2π(n-1)/36; varias -> media circular ponderada por p (top5_ANEXO).
#   souriau : zona marco_7783 -> 2π·zona/7783 (circunferencia de 7783; con la codificación actual solo hay 729 zonas -> arco [0, 2π·728/7783]).
# Corte sin dato para un anillo: fase CONGELADA (ω=0) como la regla one_empty de billar v0_2; si nunca hubo dato, None.
# Tamaño (radio) de anillo: no definido en disco -> radio 1 para todos (no se inventa).
# Intersección: distancia de cuerda |z_a - z_b| = 2|sin(Δφ/2)| <= TAU (TAU de billar_circular v0_1 = 0.35, heredado).
import math

ANILLOS = ("caldero", "polti", "souriau")


def _wrap(x: float) -> float:
    x = (x + math.pi) % (2 * math.pi) - math.pi
    return x if x != -math.pi else math.pi


def _media_circular(angs_w):
    sx = sum(w * math.cos(a) for a, w in angs_w); sy = sum(w * math.sin(a) for a, w in angs_w)
    if abs(sx) < 1e-12 and abs(sy) < 1e-12:
        return None, 0.0
    tot = sum(w for _a, w in angs_w) or 1.0
    ang = math.atan2(sy, sx) % (2 * math.pi)
    if ang >= 2 * math.pi - 1e-9:
        ang = 0.0
    return ang, math.hypot(sx, sy) / tot


def _fase_dato(c: Dict[str, Any], n_zonas: int):
    out = {}
    qs = c.get("cuadrantes_caldero") or []
    out["caldero"] = _media_circular([((CUADRANTES.index(q)) * math.pi / 2 + math.pi / 4, 1.0) for q in qs]) if qs else (None, 0.0)
    pol = [(int(RX_POLTI.match(n).group(1)), p) for n, p in (c.get("polti_activas") or []) if 1 <= int(RX_POLTI.match(n).group(1)) <= N_POLTI]
    out["polti"] = _media_circular([(2 * math.pi * (k - 1) / N_POLTI, float(p)) for k, p in pol]) if pol else (None, 0.0)
    out["souriau"] = ((2 * math.pi * int(c["zona"]) / n_zonas) % (2 * math.pi), 1.0) if (c.get("zona") is not None and not c.get("sin_dato_souriau")) else (None, 0.0)
    return out


def anillos(p: Dict[str, Any], tau: float, n_rep: int = 40, seed: int = 20260921) -> Dict[str, Any]:
    cortes = p.get("por_corte") or []
    n_zonas = int(p.get("n_zonas_marco") or 7783)
    ids = [c["corte"] for c in cortes]
    fases = {a: [] for a in ANILLOS}; dato = {a: [] for a in ANILLOS}; coher = {a: [] for a in ANILLOS}
    for c in cortes:
        fd = _fase_dato(c, n_zonas)
        for a in ANILLOS:
            ph, r = fd[a]
            prev = fases[a][-1] if fases[a] else None
            fases[a].append(ph if ph is not None else prev)
            dato[a].append(ph is not None); coher[a].append(round(r, 4))
    omega = {a: [None] + [(None if (fases[a][t] is None or fases[a][t - 1] is None) else round(_wrap(fases[a][t] - fases[a][t - 1]), 6))
                          for t in range(1, len(cortes))] for a in ANILLOS}

    def _inter(F, D):
        ev = []
        for t in range(len(ids)):
            hits = {}
            for i in range(3):
                for j in range(i + 1, 3):
                    a, b = ANILLOS[i], ANILLOS[j]
                    if F[a][t] is None or F[b][t] is None:
                        continue
                    if not (D[a][t] or D[b][t]):      # ambos congelados = par fantasma (regla corte 2 billar v0_2)
                        continue
                    d = 2 * abs(math.sin((F[a][t] - F[b][t]) / 2))
                    if d <= tau:
                        hits[f"{a}~{b}"] = round(d, 6)
            ev.append(hits)
        return ev
    inter = _inter(fases, dato)
    n_real = sum(len(h) for h in inter)
    # nulo: permutar la secuencia de fases de cada anillo (misma lógica que el nulo de billar; semilla 20260921, R=40)
    import random as _r
    rng = _r.Random(seed); cuentas = []
    for _ in range(n_rep):
        Fm, Dm = {}, {}
        for a in ANILLOS:
            seq = list(zip(fases[a], dato[a])); rng.shuffle(seq)
            Fm[a] = [x for x, _d in seq]; Dm[a] = [d for _x, d in seq]
        cuentas.append(sum(len(h) for h in _inter(Fm, Dm)))
    mu = sum(cuentas) / len(cuentas) if cuentas else 0.0
    sd = (sum((x - mu) ** 2 for x in cuentas) / len(cuentas)) ** 0.5 if cuentas else 0.0
    pares = [f"{ANILLOS[i]}~{ANILLOS[j]}" for i in range(3) for j in range(i + 1, 3)]
    por_corte = []
    for t, cid in enumerate(ids):
        h = inter[t]
        por_corte.append({
            "corte": cid,
            "fase": {a: (None if fases[a][t] is None else round(fases[a][t], 6)) for a in ANILLOS},
            "fase_con_dato": {a: dato[a][t] for a in ANILLOS},
            "coherencia": {a: coher[a][t] for a in ANILLOS},
            "omega": {a: omega[a][t] for a in ANILLOS},
            "z": {a: (None if fases[a][t] is None else [round(math.cos(fases[a][t]), 6), round(math.sin(fases[a][t]), 6)]) for a in ANILLOS},
            "intersecciones": h,
            "vector_interseccion": [1 if k in h else 0 for k in pares] + [1 if len(h) == 3 else 0],
        })
    it_idx = [t for t, h in enumerate(inter) if h]
    inercia = {}
    for a in ANILLOS:
        w = [x for x in omega[a] if x is not None]
        nz = [x for x in w if abs(x) > 1e-9]
        inercia[a] = {"omega_media": round(sum(w) / len(w), 6) if w else None,
                      "omega_abs_media": round(sum(abs(x) for x in w) / len(w), 6) if w else None,
                      "pasos_quietos": sum(1 for x in w if abs(x) <= 1e-9), "pasos_con_giro": len(nz),
                      "persistencia_signo": (round(sum(1 for x, y in zip(nz, nz[1:]) if (x > 0) == (y > 0)) / (len(nz) - 1), 4) if len(nz) > 1 else None),
                      "cortes_con_dato": sum(dato[a])}
    return {
        "modelo": "anillos en una circunferencia (círculo unidad, mismo mapa que billar_circular v0_1/v0_2)",
        "anillos": list(ANILLOS), "tau": tau, "tau_fuente": "billar_circular_convergencia_v0_1.TAU",
        "mapeo_fase": {"caldero": "Qk -> (k-1)·π/2+π/4 (centro de cuadrante); media circular si hay varios [DISEÑO]",
                       "polti": "n -> 2π(n-1)/36; media circular ponderada por p del top5_ANEXO [DISEÑO]",
                       "souriau": "zona -> 2π·zona/7783 [DISEÑO; solo 729 zonas alcanzables -> arco ≈ 0..0.588 rad]",
                       "sin_dato": "fase congelada ω=0 (regla one_empty de billar v0_2); par con ambos congelados no se evalúa",
                       "radio": "no definido en disco: 1 para todos"},
        "pares": pares, "vector_interseccion_schema": pares + ["triple"],
        "por_corte": por_corte, "inercia": inercia,
        "iteraciones_con_interseccion": [ids[t] for t in it_idx],
        "intervalos_entre_intersecciones": [it_idx[k + 1] - it_idx[k] for k in range(len(it_idx) - 1)],
        "n_intersecciones": n_real,
        "nulo_permutacion": {"n_rep": n_rep, "semilla": seed, "media": round(mu, 4), "sd": round(sd, 4),
                             "z": (round((n_real - mu) / sd, 4) if sd > 0 else None)},
        "can_decide_H": False,
    }


def tray_para_billar(r: Dict[str, Any]) -> Dict[str, Any]:
    """Formato de trayectorias de billar_circular (p, z) para que billar v0_2.convergencias_v2 lea los anillos sin editarse.
    p = 1.0 si el anillo tiene dato en el corte, None si su fase está congelada (regla corte 2: par con ambos None se excluye)."""
    out = {}
    for a in r.get("anillos") or []:
        ps, zs = [], []
        for c in r.get("por_corte") or []:
            z = c["z"][a]
            ps.append(1.0 if c["fase_con_dato"][a] else None)
            zs.append(z if z is not None else [0.0, 0.0])
        out[a] = {"p": ps, "z": zs}
    return out


# ======================================================================= HÉLICE + TUSI + Z-RI (visión Mj 02:33 CT)
# 3D: cada anillo gira (fase φ, ω) y avanza en un eje común. Avance axial (DECISIÓN DE DISEÑO, dos lecturas):
#   z_indice  = índice del corte t (0..n-1)  -> paso uniforme.
#   z_inercia = Σ_{s<=t} media_anillos(|ω_s|) -> el punto guía ("Sol") avanza arrastrado por la inercia de giro de los anillos.
#   (Qué anillo/función es el "Sol" de Mj no está definido en disco: aquí el eje lo lleva la inercia conjunta; no se elige anillo.)
# Alineación en la hélice = fase alineada (cuerda <= TAU) en el MISMO corte (mismo z) -> coincide con 'intersecciones'.
# Tusi: misma fórmula de tusi_par_indice_exploratorio_v0_1 (1 - |Σ(ωa+ωb)| / Σ(|ωa|+|ωb|)) aplicada a las ω de los anillos.
# Z-RI: zri_coupling_v0_2.couple_at_cut con cada anillo como capa (vector 3D = cos φ, sin φ, z_inercia) -> distancia/coseno por corte.


def _tusi(da, db):
    pares = [(x, y) for x, y in zip(da, db) if x is not None and y is not None and (x != 0 or y != 0)]
    if len(pares) < 2:
        return None, len(pares)
    num = abs(sum(x + y for x, y in pares)); den = sum(abs(x) + abs(y) for x, y in pares)
    return (1 - num / den if den else None), len(pares)


def helice(an: Dict[str, Any], zri=None, case_id: str = "", seed: int = 20260921, n_null: int = 200) -> Dict[str, Any]:
    import hashlib, json as _j, random as _r
    pc = an.get("por_corte") or []
    rings = list(an.get("anillos") or [])
    z_inercia, acc = [], 0.0
    for c in pc:
        w = [abs(v) for v in (c.get("omega") or {}).values() if v is not None]
        acc += (sum(w) / len(w)) if w else 0.0
        z_inercia.append(round(acc, 6))
    puntos = []
    for t, c in enumerate(pc):
        puntos.append({"corte": c["corte"], "z_indice": t, "z_inercia": z_inercia[t],
                       "xyz": {a: (None if c["z"][a] is None else [c["z"][a][0], c["z"][a][1], z_inercia[t]]) for a in rings},
                       "alineaciones": c.get("intersecciones")})
    # Tusi sobre ω de anillos
    W = {a: [c["omega"][a] for c in pc][1:] for a in rings}
    rng = _r.Random(seed); tus = []
    for i, a in enumerate(rings):
        for b in rings[i + 1:]:
            t, n = _tusi(W[a], W[b])
            if t is None:
                tus.append({"par": [a, b], "tusi": None, "n_pasos_vivos": n}); continue
            nul = []
            for _ in range(n_null):
                db = W[b][:]; rng.shuffle(db); tn, _n = _tusi(W[a], db)
                if tn is not None: nul.append(tn)
            mu = sum(nul) / len(nul) if nul else None
            sd = (sum((x - mu) ** 2 for x in nul) / len(nul)) ** 0.5 if nul else None
            tus.append({"par": [a, b], "tusi": round(t, 4), "n_pasos_vivos": n, "z_vs_nulo": (round((t - mu) / sd, 3) if sd else None)})
    # Z-RI acople por corte (sin editar zri_coupling_v0_2)
    zri_out, zri_status = [], "NO_DISPONIBLE"
    if zri is not None and hasattr(zri, "couple_at_cut"):
        zri_status = "EJECUTADO"
        rh = hashlib.sha256(_j.dumps([p["corte"] for p in puntos], default=str).encode()).hexdigest()[:16]
        for p in puntos:
            ih = hashlib.sha256(_j.dumps(p["xyz"], sort_keys=True, default=str).encode()).hexdigest()[:16]
            pts = [zri.TracePoint(str(case_id), str(p["corte"]), a, ih, rh, tuple(p["xyz"][a])) for a in rings if p["xyz"][a] is not None]
            if len(pts) < 2:
                zri_out.append({"cut_id": p["corte"], "n_layers": len(pts), "mean_distance": None, "mean_cosine": None, "nota": "<2 anillos con fase"}); continue
            st = zri.couple_at_cut(str(case_id), str(p["corte"]), pts)
            sm = zri.convergence_summary(st)
            sm["pairwise_distance"] = {f"{k[0]}~{k[1]}": round(v, 6) for k, v in st.pairwise_distance.items()}
            sm["mean_distance"] = None if sm["mean_distance"] is None else round(sm["mean_distance"], 6)
            sm["mean_cosine"] = None if sm["mean_cosine"] is None else round(sm["mean_cosine"], 6)
            zri_out.append(sm)
    return {"eje_axial": {"z_indice": "índice de corte [DISEÑO]", "z_inercia": "Σ media|ω| de los anillos hasta t [DISEÑO; 'Sol' = punto guía arrastrado por la inercia conjunta]"},
            "puntos": puntos, "alineaciones_en_helice": [{"corte": p["corte"], "z_inercia": p["z_inercia"], "pares": sorted((p["alineaciones"] or {}).keys())} for p in puntos if p["alineaciones"]],
            "tusi_anillos": tus, "tusi_formula": "tusi_par_indice_exploratorio_v0_1 (sobre ω de anillos; nulo permutación seed 20260921, R=200)",
            "zri_acople": {"lector": "zri_coupling_v0_2.couple_at_cut/convergence_summary (sin editar)", "status": zri_status, "por_corte": zri_out},
            "can_decide_H": False}


def compacto_para_traza(p: Dict[str, Any]) -> Dict[str, Any]:
    """Resumen aditivo que recibe la trazabilidad (sin el detalle completo)."""
    return {
        "fuente": "laterales_unico_v1.marco_7783_geometria (" + VERSION + ")",
        "can_decide_H": False, "aditivo_no_decide": True,
        "vector_schema": p.get("vector_schema"),
        "por_corte": [{"corte": c["corte"], "zona": c["zona"], "vector_funciones": c["vector_funciones"],
                       "cuadrantes": c["cuadrantes_caldero"], "polti_idx": c["polti_idx"], "n_cumulos": c["n_cumulos"],
                       "vector": c["vector"]} for c in p.get("por_corte") or []],
        "deltas": [{"de": d["de"], "a": d["a"], "hamming": d["discrepancia_hamming"], "funciones_cambian": sorted(d["funciones_cambian"]),
                    "zona": d["zona"], "revisita": d["revisita_zona"], "cuadrante_entra": d["cuadrante_entra"], "cuadrante_sale": d["cuadrante_sale"],
                    "polti_entra": d["polti_entra"], "polti_sale": d["polti_sale"], "delta_L1": d["delta_L1"]} for d in p.get("deltas") or []],
        "resumen": p.get("resumen"),
        "anillos": ({"por_corte": [{"corte": c["corte"], "fase": c["fase"], "omega": c["omega"], "vector_interseccion": c["vector_interseccion"]}
                                   for c in (p.get("anillos") or {}).get("por_corte") or []],
                     "inercia": (p.get("anillos") or {}).get("inercia"),
                     "iteraciones_con_interseccion": (p.get("anillos") or {}).get("iteraciones_con_interseccion"),
                     "nulo_permutacion": (p.get("anillos") or {}).get("nulo_permutacion"),
                     "vector_interseccion_schema": (p.get("anillos") or {}).get("vector_interseccion_schema"),
                     "helice": ({"z_inercia": [x["z_inercia"] for x in ((p["anillos"].get("helice") or {}).get("puntos") or [])],
                                 "alineaciones_en_helice": (p["anillos"].get("helice") or {}).get("alineaciones_en_helice"),
                                 "tusi_anillos": (p["anillos"].get("helice") or {}).get("tusi_anillos")} if p["anillos"].get("helice") else None)} if p.get("anillos") else None),
        "brecha_7783": p.get("brecha_7783"),
    }
