#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rueda_conjuncion.py — Lateral: rueda de conjunción v1.

Pedido de Mj (2026-11-12 ~20:12 CST): el círculo cromático es donde se
conjuntan el héroe partido en tres, la duplicación, la latencia, el
trono y el radio. Este lateral conjuga tres piezas ya verificadas:

  1. Teoria del color v1 (motor/laterales/teoria_color/teoria_color.py):
     color() por hipótesis desde los tableros P/A/C (interno/externo/
     situación), mezcla final ponderada por rank_fusion.
  2. Rueda cromática (motor/laterales/teoria_color/equivalencias.py):
     hue() proyecta un tono al plano (0°=interno, 120°=externo,
     240°=situación); croma = distancia al gris; análogos Δmatiz<=30°;
     complementarios |Δmatiz| en [150,210] y croma>0.02;
     neutralización = 1 - croma_mezcla / Σ(w·croma_H).
  3. No duplicación con latencia (motor/reconexion_v2a1/
     no_duplicacion_latencia.py): tablero sombra (cada token se aplica
     una sola vez, a la familia que perfila por su compañía; lo demás
     va a latencia). Puerta PASA: con la regla apagada el tablero
     sombra reproduce los P_FULL_244 sellados exacto.

Qué hace este lateral (NO toca Engine, ni 244, ni correr_estandar, ni
teoria_color.py, ni equivalencias.py, ni ningún RESULT/entrada/COLOR
sellado; solo los LEE):
  1. Tableros sombra por corte para los TRES ejes (P, A, C), emitidos
     a motor/reconexion_v2a1/sombra_tableros_<caso>.json (la maquinaria
     ya los computa; solo se emiten). Puerta: con la regla apagada
     deben igualar los FULL_244 sellados (misma puerta que el lateral
     de no duplicación).
  2. Colores sombra: la misma función color() de teoria_color.py
     (importada, no copiada) sobre los tableros sombra, con los mismos
     pesos rank_fusion canónicos (la mezcla compara solo el cambio de
     tablero, no de pesos). Salen COLOR_SOMBRA_<caso>.json (mismo
     esquema que COLOR_RESULT, lateral rueda_conjuncion).
  3. Latencia como desaturación (el único mapeo nuevo, y sigue la
     lógica propia de la rueda: el croma es señal pura resuelta; la
     evidencia pendiente es gris): por familia,
     croma_desat = croma_sombra * (ocurrencias resueltas para esa
     familia / ocurrencias totales que la alimentan). Resuelta = la
     ocurrencia fue asignada a esa familia en el tablero sombra;
     total = ocurrencias que la alimentan en el canónico. Se aplica
     SOLO al croma, nunca a las proporciones del tono. Se registran
     ambos cromas.
  4. Ruedas polares por caso, canónica y sombra (mismo trazado que
     equivalencias.py: puntos en (matiz, croma), tamaño por peso
     rank_fusion, estrella MEZCLA; ejes a 0/120/240°). La rueda sombra
     grafica el croma DESATURADO (la latencia tira los puntos hacia
     el gris). Las familias héroe/trono que no están en el set de
     candidatas se grafican como marcadores huecos (no entran en la
     mezcla, que usa solo el set canónico).

Decisiones de diseño (ambigüedades resueltas por cercanía a los
laterales existentes, documentadas):
  - Conteo de ocurrencias: por ocurrencia de marcador (por eje y
    corte), igual que el Engine y que el lateral de no duplicación.
    Canónico: cada ocurrencia cuenta 1 para CADA familia que la
    lista (favor o contra). Sombra: cada ocurrencia cuenta 1 solo
    para la familia asignada (favor o contra, según la asignación).
    La fracción resuelta es sombra/canónico (favor+contra juntos).
    Si una familia no tiene evidencia canónica (0 ocurrencias), la
    fracción es 1.0 (nada pendiente) y se registra así.
  - La asignación sombra se recomputa con la propia _asignar() del
    lateral de no duplicación, por (token, corte), sobre los 3 ejes;
    se verifica que los totales favor/contra coincidan con los del
    lateral (si no, el conteo está mal, no la regla).
  - hue() y hx() NO se reimplementan: se extraen por AST del propio
    equivalencias.py (el archivo es un script sin guarda __main__ y
    no se puede importar sin ejecutarlo). La matemática es la misma,
    byte por byte.
  - color() y hexrgb() se importan de teoria_color.py (tiene guarda
    __main__, importación segura).
  - H1/H2 sombra: por p_final en el corte Z (nivel tablero), como en
    el lateral de no duplicación. El rank_fusion no se reimplementa.
    La rueda es lectura de tablero, no veredicto del motor.

Reglas del lateral: can_decide_H=False. No decide H1/H2 del motor.
"""
from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

VERSION = "RUEDA_CONJUNCION_V1_20261112"
MOTOR_DIR = Path("/home/hatch/workspace/u6-alterno/motor-cameo/motor/motor")
MOTOR_ROOT = Path("/home/hatch/workspace/u6-alterno/motor-cameo/motor")
RESULTS_DIR = MOTOR_ROOT
CASOS_DIR = Path("/home/hatch/workspace/u6-alterno/motor-cameo/casos/precedentes")
TC_DIR = MOTOR_ROOT / "laterales" / "teoria_color"
RECON_DIR = MOTOR_ROOT / "reconexion_v2a1"
CASOS = [
    "JUANA_DE_ARCO_HEROE_20261112",
    "TUBMAN_HEROE_20261112",
    "MANDELA_HEROE_20261112",
    "SEMMELWEIS_HEROE_SIN_TRONO_20261112",
    "KOLBE_HEROE_SIN_TRONO_20261112",
]
HEROES = ["heroe", "arquetipo_heroe", "arquetipo_el_heroe"]
TRONO = ["arquetipo_el_gobernante", "kwml_01_rey"]
INTERES = HEROES + TRONO
AX = ["interno", "externo", "situacion"]
DIM = ["P", "A", "C"]
R = lambda x: round(float(x), 6)


# ------------------------------------------------------------------
# Carga de matemáticas existentes (sin reimplementar)
# ------------------------------------------------------------------
def _cargar_hue():
    """Extrae AX, R, hue y hx de equivalencias.py por AST y los ejecuta.
    El archivo es un script sin guarda __main__; importarlo lo
    ejecutaría entero. La matemática extraída es byte por byte la
    misma del archivo."""
    src = (TC_DIR / "equivalencias.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    piezas = []
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "AX" for t in node.targets):
            piezas.append(node)
        elif isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "R" for t in node.targets):
            piezas.append(node)
        elif isinstance(node, ast.FunctionDef) and node.name in ("hue", "hx"):
            piezas.append(node)
    mod = ast.Module(body=piezas, type_ignores=[])
    ns: Dict[str, Any] = {"math": math}
    exec(compile(mod, "equivalencias_hue", "exec"), ns)
    assert callable(ns.get("hue")) and callable(ns.get("hx"))
    return ns["hue"], ns["hx"], ns["AX"]


def _cargar_color():
    spec = importlib.util.spec_from_file_location(
        "tc_color", str(TC_DIR / "teoria_color.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.color, m.hexrgb


def _cargar_no_dup():
    spec = importlib.util.spec_from_file_location(
        "nd_lat", str(RECON_DIR / "no_duplicacion_latencia.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# ------------------------------------------------------------------
# Conteo de ocurrencias por familia (canónico vs sombra)
# ------------------------------------------------------------------
def _eventos_por_familia(entrada, fam_por_token, asignar):
    """Devuelve (canon, sombra): fam -> {'favor': n, 'contra': n}.
    Canónico: cada ocurrencia cuenta 1 para CADA familia que la lista.
    Sombra: cada ocurrencia cuenta 1 solo para la familia asignada
    (misma _asignar() del lateral de no duplicación, por token/corte).
    """
    canon: Dict[str, Dict[str, int]] = {}
    sombra: Dict[str, Dict[str, int]] = {}

    def _suma(tabla, fam, lado):
        d = tabla.setdefault(fam, {"favor": 0, "contra": 0})
        d[lado] += 1

    for cut in entrada["cuts"]:
        cut_pesos: Dict[str, float] = {}
        for eje in ("P", "A", "C"):
            for t, w in cut.get(eje) or []:
                cut_pesos[t] = max(cut_pesos.get(t, 0.0), float(w))
        asignacion = {t: asignar(t, cut_pesos, fam_por_token)
                      for t in cut_pesos}
        for eje in ("P", "A", "C"):
            for t, _w in cut.get(eje) or []:
                info = fam_por_token.get(t) or {"favor": [], "contra": []}
                for f in info["favor"]:
                    _suma(canon, f, "favor")
                for f in info["contra"]:
                    _suma(canon, f, "contra")
                fam, lado, _mot = asignacion[t]
                if fam is not None and lado is not None:
                    _suma(sombra, fam, lado)
    return canon, sombra


# ------------------------------------------------------------------
# Color desde tableros (misma lógica que teoria_color.run)
# ------------------------------------------------------------------
def _color_desde_tableros(boards, resultado, color_fn, hexrgb_fn):
    """boards: {'P': [dict fam->p por corte], 'A': [...], 'C': [...]}.
    Pesos W: rank_fusion canónico de predictor.candidates. Huecos por
    n_tokens del RESULT sellado (mismos inputs)."""
    cuts = resultado["motor"]["cuts"]
    fcuts = resultado.get("features", {}).get("cuts", [])
    cands = resultado["predictor"]["candidates"]
    tot = sum(max(0, c["rank_fusion"]) for c in cands)
    W = {c["family"]: R(max(0, c["rank_fusion"]) / tot) for c in cands}
    masa = {k: sum(len(fc.get(k) or []) for fc in fcuts) for k in DIM}
    huecos: List[str] = []
    for k in DIM:
        if masa[k] == 0:
            huecos.append(f"features: 0 tokens {k} en todos los cortes -> eje {AX[DIM.index(k)]} HUECO")
    per_h: Dict[str, List[List[Optional[float]]]] = {h: [] for h in W}
    tray = []
    for i, c in enumerate(cuts):
        nt = c.get("n_tokens", {})
        hole = [nt.get(k, 0) == 0 for k in DIM]
        for j, k in enumerate(DIM):
            if hole[j]:
                huecos.append(f"{c['corte']}: n_tokens {k}=0 -> {k}_FULL_244 no es dato, eje {AX[j]} hueco")
        mix = [0.0] * 3
        wsum = [0.0] * 3
        for h, w in W.items():
            vals = [None if hole[j] else boards[DIM[j]][i].get(h)
                    for j in range(3)]
            col = color_fn(vals)
            per_h[h].append(vals)
            for j in range(3):
                if vals[j] is not None and col:
                    mix[j] += w * col["tono"][AX[j]]
                    wsum[j] += w
        mixv = [mix[j] if wsum[j] > 0 else None for j in range(3)]
        tray.append({"corte": c["corte"], "n_tokens": nt, "mezcla": color_fn(mixv)})
    hyp: Dict[str, Any] = {}
    for h, rows in per_h.items():
        avg = []
        for j in range(3):
            xs = [r[j] for r in rows if r[j] is not None]
            avg.append(sum(xs) / len(xs) if xs else None)
        col = color_fn(avg)
        if col:
            col["hex_ilustrativo"] = hexrgb_fn(col["tono"])
        hyp[h] = {"peso_rank_fusion_norm": W[h],
                  "vector_medio_PAC": [None if a is None else R(a) for a in avg],
                  "color": col}
    fin = [0.0] * 3
    has = [False] * 3
    for h, v in hyp.items():
        if not v["color"]:
            continue
        for j in range(3):
            t = v["color"]["tono"][AX[j]]
            if t is not None:
                fin[j] += v["peso_rank_fusion_norm"] * t
                has[j] = True
    final = color_fn([fin[j] if has[j] else None for j in range(3)])
    if final:
        final["hex_ilustrativo"] = hexrgb_fn(final["tono"])
    grp: Dict[str, List[str]] = {}
    for h, rows in per_h.items():
        grp.setdefault(json.dumps(rows), []).append(h)
    ident = [g for g in grp.values() if len(g) > 1]
    mov = []
    for a, b in zip(tray, tray[1:]):
        if not (a["mezcla"] and b["mezcla"]):
            mov.append({"de": a["corte"], "a": b["corte"], "eje": None})
            continue
        dl = {x: R((b["mezcla"]["tono"][x] or 0) - (a["mezcla"]["tono"][x] or 0))
              for x in AX
              if a["mezcla"]["tono"][x] is not None and b["mezcla"]["tono"][x] is not None}
        dl2 = {x: v for x, v in dl.items() if v != 0}
        mov.append({"de": a["corte"], "a": b["corte"], "delta": dl,
                    "eje_que_mueve": max(dl2, key=lambda x: abs(dl2[x])) if dl2 else "sin_cambio"})
    return {"hipotesis": hyp, "tono_final_mezcla": final,
            "pigmentos_identicos": ident, "trayectoria": tray,
            "movimiento": mov, "huecos": huecos, "pesos": W}


def _color_familia(boards, familia, color_fn, hexrgb_fn, resultado):
    """Color de UNA familia (esté o no en el set de candidatas) desde
    los tableros dados: media por corte de sus valores P/A/C."""
    cuts = resultado["motor"]["cuts"]
    rows = []
    for i, c in enumerate(cuts):
        nt = c.get("n_tokens", {})
        vals = []
        for j, k in enumerate(DIM):
            vals.append(None if nt.get(k, 0) == 0 else boards[k][i].get(familia))
        rows.append(vals)
    avg = []
    for j in range(3):
        xs = [r[j] for r in rows if r[j] is not None]
        avg.append(sum(xs) / len(xs) if xs else None)
    col = color_fn(avg)
    if col:
        col["hex_ilustrativo"] = hexrgb_fn(col["tono"])
    return {"vector_medio_PAC": [None if a is None else R(a) for a in avg],
            "color": col, "por_corte": rows}


# ------------------------------------------------------------------
# Rueda: matiz/croma, análogos, complementarios, neutralización
# ------------------------------------------------------------------
def _dif_angular(a: float, b: float) -> float:
    return min(abs(a - b), 360 - abs(a - b))


def _analogos(hue_map: Dict[str, Tuple[float, float]]) -> List[List[Any]]:
    out = []
    hs = sorted(hue_map)
    for i, a in enumerate(hs):
        for b in hs[i + 1:]:
            d = _dif_angular(hue_map[a][0], hue_map[b][0])
            if d <= 30:
                out.append([a, b, R(d)])
    return out


def _complementarios(hue_map: Dict[str, Tuple[float, float]]) -> List[List[Any]]:
    out = []
    hs = sorted(hue_map)
    for i, a in enumerate(hs):
        for b in hs[i + 1:]:
            d = abs(hue_map[a][0] - hue_map[b][0])
            if 150 <= d <= 210 and min(hue_map[a][1], hue_map[b][1]) > 0.02:
                out.append([a, b, R(d)])
    return out


def _neutralizacion(hue_map: Dict[str, Tuple[float, float]],
                    pesos: Dict[str, float],
                    croma_mezcla: float) -> Optional[float]:
    s = sum(pesos[h] * hue_map[h][1] for h in pesos if h in hue_map)
    if s <= 0:
        return None
    return R(max(0.0, 1 - croma_mezcla / s))


def _dibujar_rueda(hue_fn, hx_fn, titulo: str, ruta: Path,
                   puntos: Dict[str, Dict[str, Any]],
                   mezcla_tono: Dict[str, Optional[float]],
                   mezcla_hue_croma: Tuple[float, float],
                   extras: Dict[str, Dict[str, Any]]):
    """Mismo trazado que equivalencias.py: dispersión polar en
    (matiz, croma), tamaño 3000*peso, color hx(tono), estrella MEZCLA.
    `puntos`: candidatas (puntos rellenos). `extras`: familias fuera
    del set (marcadores huecos). En la rueda sombra el radio es el
    croma DESATURADO por latencia."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(projection="polar")
    for h, v in puntos.items():
        a, c = v["matiz"], v["croma"]
        ax.scatter(math.radians(a), c, s=3000 * v["peso"],
                   color=hx_fn(v["tono"]), edgecolor="k")
        ax.annotate(h[:22], (math.radians(a), c), fontsize=7)
    for h, v in extras.items():
        a, c = v["matiz"], v["croma"]
        ax.scatter(math.radians(a), c, s=180, marker="s",
                   facecolor="none", edgecolor="red", linewidth=1.5)
        ax.annotate(h[:22] + " (fuera set)", (math.radians(a), c), fontsize=7, color="darkred")
    ax.scatter(math.radians(mezcla_hue_croma[0]), mezcla_hue_croma[1],
               marker="*", s=300, color="k")
    ax.annotate("MEZCLA", (math.radians(mezcla_hue_croma[0]), mezcla_hue_croma[1]),
                fontsize=8, weight="bold")
    ax.set_xticks([0, math.radians(120), math.radians(240)])
    ax.set_xticklabels(["interno (P)", "externo (A)", "situación (C)"])
    top = max([v["croma"] for v in puntos.values()] +
              [v["croma"] for v in extras.values()] +
              [mezcla_hue_croma[1], 0.05]) * 1.25
    ax.set_ylim(0, top)
    ax.set_title(titulo, fontsize=8)
    fig.savefig(ruta, dpi=110, bbox_inches="tight")
    plt.close(fig)
    Path(str(ruta) + ".sha256").write_text(
        hashlib.sha256(Path(ruta).read_bytes()).hexdigest() + "  " + ruta.name + "\n")


# ------------------------------------------------------------------
# Caso completo
# ------------------------------------------------------------------
def procesar_caso(nombre: str, nd, hue_fn, hx_fn, color_fn, hexrgb_fn,
                  eng, pl, fam_por_token) -> Dict[str, Any]:
    entrada = json.loads((CASOS_DIR / nombre / "entrada.json").read_text(encoding="utf-8"))
    resultado = json.loads((RESULTS_DIR / f"RESULT_{nombre}.json").read_text(encoding="utf-8"))
    color_canon = json.loads((MOTOR_ROOT / f"COLOR_RESULT_{nombre}.json").read_text(encoding="utf-8"))

    sombra_off = nd.correr_tablero_sombra(entrada, resultado, eng, pl, fam_por_token, dedup=False)
    sombra_on = nd.correr_tablero_sombra(entrada, resultado, eng, pl, fam_por_token, dedup=True)
    gate_pasa = (sombra_off["gate_mismatch"] == 0 and sombra_off["gate_max_diff"] <= 1e-6)

    boards = sombra_on["boards"]
    (MOTOR_ROOT / "reconexion_v2a1" / f"sombra_tableros_{nombre}.json").write_text(
        json.dumps({"version": VERSION, "caso": nombre,
                    "lateral": "no_duplicacion_latencia_v1 + rueda_conjuncion_v1",
                    "gate_max_diff": sombra_off["gate_max_diff"],
                    "gate_mismatch": sombra_off["gate_mismatch"],
                    "gate_pasa": gate_pasa,
                    "frentes": sombra_on["frentes"],
                    "eventos_favor": sombra_on["eventos_favor"],
                    "eventos_contra": sombra_on["eventos_contra"],
                    "ocurrencias": sombra_on["ocurrencias"],
                    "boards": boards}, ensure_ascii=False, indent=1), encoding="utf-8")

    canon_ev, sombra_ev = _eventos_por_familia(entrada, fam_por_token, nd._asignar)
    # verificación cruzada: los conteos sombra deben igualar los del lateral
    tot_fav = sum(v["favor"] for v in sombra_ev.values())
    tot_con = sum(v["contra"] for v in sombra_ev.values())
    assert tot_fav == sombra_on["eventos_favor"], (nombre, tot_fav, sombra_on["eventos_favor"])
    assert tot_con == sombra_on["eventos_contra"], (nombre, tot_con, sombra_on["eventos_contra"])

    # colores sombra (misma color() y mismos pesos canónicos)
    col_sombra = _color_desde_tableros(boards, resultado, color_fn, hexrgb_fn)

    # matiz/croma canónico y sombra por hipótesis del set
    def _hc(color_data):
        out = {}
        for h, v in color_data["hipotesis"].items():
            if v["color"]:
                out[h] = hue_fn(v["color"]["tono"])
        return out
    hc_canon = _hc(color_canon)
    hc_sombra = _hc(col_sombra)
    mezcla_hc_canon = hue_fn(color_canon["tono_final_mezcla"]["tono"])
    mezcla_hc_sombra = hue_fn(col_sombra["tono_final_mezcla"]["tono"])
    neut_canon = _neutralizacion(hc_canon, col_sombra["pesos"], mezcla_hc_canon[1])
    neut_sombra = _neutralizacion(hc_sombra, col_sombra["pesos"], mezcla_hc_sombra[1])

    # familias de interés: color sombra aunque no estén en el set
    set_canon = set(color_canon["hipotesis"].keys())
    interes_sombra: Dict[str, Any] = {}
    interes_canon: Dict[str, Any] = {}
    for f in INTERES:
        cs = _color_familia(boards, f, color_fn, hexrgb_fn, resultado)
        interes_sombra[f] = cs
        # canónico: del COLOR file si está, si no desde los tableros sellados
        if f in color_canon["hipotesis"]:
            interes_canon[f] = color_canon["hipotesis"][f]
        else:
            boards_canon = {k: [c[f"{k}_FULL_244"] for c in resultado["motor"]["cuts"]]
                            for k in DIM}
            interes_canon[f] = _color_familia(boards_canon, f, color_fn, hexrgb_fn, resultado)

    # desaturación por latencia (solo al croma, nunca al tono)
    desat: Dict[str, Any] = {}
    for f in INTERES:
        c_ev = canon_ev.get(f, {"favor": 0, "contra": 0})
        s_ev = sombra_ev.get(f, {"favor": 0, "contra": 0})
        tot_c = c_ev["favor"] + c_ev["contra"]
        tot_s = s_ev["favor"] + s_ev["contra"]
        frac = (tot_s / tot_c) if tot_c > 0 else 1.0
        cs = interes_sombra[f]["color"]
        cc = interes_canon[f]["color"]
        hc_s = hue_fn(cs["tono"]) if cs else (None, None)
        hc_c = hue_fn(cc["tono"]) if cc else (None, None)
        desat[f] = {
            "ocurrencias_canonicas": tot_c,
            "ocurrencias_resueltas_sombra": tot_s,
            "fraccion_resuelta": R(frac),
            "matiz_canonico": hc_c[0], "croma_canonico": hc_c[1],
            "matiz_sombra": hc_s[0], "croma_sombra": hc_s[1],
            "croma_sombra_desaturado": R(hc_s[1] * frac) if hc_s[1] is not None else None,
            "tono_sombra": cs["tono"] if cs else None,
            "tono_canonico": cc["tono"] if cc else None,
            "en_set_canonico": f in set_canon,
        }
    # desaturación para todas las del set (para la rueda sombra)
    desat_set: Dict[str, float] = {}
    for h in col_sombra["hipotesis"]:
        c_ev = canon_ev.get(h, {"favor": 0, "contra": 0})
        s_ev = sombra_ev.get(h, {"favor": 0, "contra": 0})
        tot_c = c_ev["favor"] + c_ev["contra"]
        tot_s = s_ev["favor"] + s_ev["contra"]
        desat_set[h] = (tot_s / tot_c) if tot_c > 0 else 1.0

    # COLOR_SOMBRA (mismo esquema que COLOR_RESULT)
    out_sombra = {
        "lateral": "rueda_conjuncion_v1",
        "decide_H": False,
        "fuente": f"tableros sombra no_duplicacion_latencia_v1 (sombra_tableros_{nombre}.json)",
        "fuente_resultado_sellado": f"RESULT_{nombre}.json",
        "mapeo": {"interno": "P sombra", "externo": "A sombra", "situacion": "C sombra"},
        "pesos": "predictor.candidates[].rank_fusion / suma (CANONICOS; la mezcla compara solo el cambio de tablero)",
        "H_motor": {"H1": None, "H2": None},
        "H1_sombra_tablero": None,
        "tono_final_mezcla": col_sombra["tono_final_mezcla"],
        "hipotesis": col_sombra["hipotesis"],
        "pigmentos_identicos": col_sombra["pigmentos_identicos"],
        "trayectoria": col_sombra["trayectoria"],
        "movimiento": col_sombra["movimiento"],
        "huecos": col_sombra["huecos"],
        "desaturacion_latencia": desat,
        "familias_interes_sombra": {
            f: {"vector_medio_PAC": interes_sombra[f]["vector_medio_PAC"],
                "color": interes_sombra[f]["color"]} for f in INTERES},
    }
    final_p = boards["P"][-1]
    top_s = sorted(final_p.items(), key=lambda kv: -kv[1])
    out_sombra["H1_sombra_tablero"] = {"familia": top_s[0][0], "p_final": top_s[0][1]}
    (MOTOR_ROOT / f"COLOR_SOMBRA_{nombre}.json").write_text(
        json.dumps(out_sombra, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")

    # puntos para las ruedas
    def _puntos(color_data, hc, desat_radio=None):
        pts = {}
        for h, v in color_data["hipotesis"].items():
            if h not in hc or not v["color"]:
                continue
            c = hc[h][1]
            if desat_radio is not None:
                c = R(c * desat_radio.get(h, 1.0))
            pts[h] = {"matiz": hc[h][0], "croma": c,
                      "peso": v["peso_rank_fusion_norm"],
                      "tono": v["color"]["tono"]}
        return pts

    pts_canon = _puntos(color_canon, hc_canon)
    pts_sombra = _puntos(col_sombra, hc_sombra, desat_set)
    extras_canon: Dict[str, Any] = {}
    extras_sombra: Dict[str, Any] = {}
    for f in INTERES:
        if f in pts_canon:
            continue
        # canónico: no está en el set -> no se grafica (no hay color canónico en el COLOR file)
        # sombra: se grafica como hueco con su croma desaturado
        cs = interes_sombra[f]["color"]
        if cs:
            a, c = hue_fn(cs["tono"])
            extras_sombra[f] = {"matiz": a,
                                "croma": R(c * desat[f]["fraccion_resuelta"]),
                                "tono": cs["tono"]}
    _dibujar_rueda(hue_fn, hx_fn,
                   f"Rueda conjunción CANÓNICA — {nombre}",
                   TC_DIR / f"RUEDA_CONJUNCION_{nombre}_canonico.png",
                   pts_canon, color_canon["tono_final_mezcla"]["tono"],
                   mezcla_hc_canon, extras_canon)
    # la estrella MEZCLA sombra usa el croma de la mezcla desaturada por
    # el promedio ponderado de las fracciones resueltas del set
    frac_mezcla = sum(col_sombra["pesos"][h] * desat_set.get(h, 1.0)
                      for h in col_sombra["pesos"])
    mezcla_hc_sombra_desat = (mezcla_hc_sombra[0], R(mezcla_hc_sombra[1] * frac_mezcla))
    _dibujar_rueda(hue_fn, hx_fn,
                   f"Rueda conjunción SOMBRA (croma desaturado por latencia) — {nombre}",
                   TC_DIR / f"RUEDA_CONJUNCION_{nombre}_sombra.png",
                   pts_sombra, col_sombra["tono_final_mezcla"]["tono"],
                   mezcla_hc_sombra_desat, extras_sombra)

    # clúster héroe: diferencias de matiz entre las tres (canónico y sombra)
    cluster_canon = {f: desat[f]["matiz_canonico"] for f in HEROES}
    cluster_sombra = {f: desat[f]["matiz_sombra"] for f in HEROES}
    pares = []
    for i, a in enumerate(HEROES):
        for b in HEROES[i + 1:]:
            pares.append({
                "par": [a, b],
                "d_canonico": R(_dif_angular(cluster_canon[a], cluster_canon[b]))
                if cluster_canon[a] is not None and cluster_canon[b] is not None else None,
                "d_sombra": R(_dif_angular(cluster_sombra[a], cluster_sombra[b]))
                if cluster_sombra[a] is not None and cluster_sombra[b] is not None else None,
            })

    resumen = {
        "caso": nombre,
        "gate_pasa": gate_pasa,
        "gate_max_diff": sombra_off["gate_max_diff"],
        "gate_mismatch": sombra_off["gate_mismatch"],
        "frentes_abiertos": len(sombra_on["frentes"]),
        "frentes_resueltos": sum(1 for f in sombra_on["frentes"] if f["corte_resolucion"]),
        "mezcla_canonica": {"tono": color_canon["tono_final_mezcla"]["tono"],
                            "matiz": mezcla_hc_canon[0], "croma": mezcla_hc_canon[1],
                            "saturacion": color_canon["tono_final_mezcla"]["saturacion"],
                            "neutralizacion": neut_canon},
        "mezcla_sombra": {"tono": col_sombra["tono_final_mezcla"]["tono"],
                          "matiz": mezcla_hc_sombra[0], "croma": mezcla_hc_sombra[1],
                          "croma_desaturado": mezcla_hc_sombra_desat[1],
                          "saturacion": col_sombra["tono_final_mezcla"]["saturacion"],
                          "neutralizacion": neut_sombra},
        "cluster_heroe": {"matices_canonicos": cluster_canon,
                          "matices_sombra": cluster_sombra,
                          "pares": pares,
                          "analogos_canonico": _analogos({f: (cluster_canon[f], desat[f]["croma_canonico"])
                                                          for f in HEROES}),
                          "analogos_sombra": _analogos({f: (cluster_sombra[f], desat[f]["croma_sombra"])
                                                        for f in HEROES}),
                          "pigmentos_identicos_canonico": color_canon["pigmentos_identicos"],
                          "pigmentos_identicos_sombra": col_sombra["pigmentos_identicos"]},
        "trono": {f: {"matiz_canonico": desat[f]["matiz_canonico"],
                      "croma_canonico": desat[f]["croma_canonico"],
                      "matiz_sombra": desat[f]["matiz_sombra"],
                      "croma_sombra": desat[f]["croma_sombra"],
                      "croma_desaturado": desat[f]["croma_sombra_desaturado"],
                      "fraccion_resuelta": desat[f]["fraccion_resuelta"],
                      "en_set_canonico": desat[f]["en_set_canonico"]}
                  for f in TRONO},
        "heroes": {f: {"matiz_canonico": desat[f]["matiz_canonico"],
                       "croma_canonico": desat[f]["croma_canonico"],
                       "matiz_sombra": desat[f]["matiz_sombra"],
                       "croma_sombra": desat[f]["croma_sombra"],
                       "croma_desaturado": desat[f]["croma_sombra_desaturado"],
                       "fraccion_resuelta": desat[f]["fraccion_resuelta"],
                       "en_set_canonico": desat[f]["en_set_canonico"]}
                   for f in HEROES},
        "desaturacion": desat,
        "complementarios_canonico": _complementarios(hc_canon),
        "complementarios_sombra": _complementarios(hc_sombra),
        "h1_sombra_tablero": out_sombra["H1_sombra_tablero"],
    }
    print(f"{nombre}: gate={gate_pasa} mismatch={sombra_off['gate_mismatch']} | "
          f"mezcla croma canon={mezcla_hc_canon[1]} sombra={mezcla_hc_sombra[1]} "
          f"desat={mezcla_hc_sombra_desat[1]} | neut canon={neut_canon} sombra={neut_sombra} | "
          f"H1 sombra={top_s[0][0]}")
    return resumen


def main():
    hue_fn, hx_fn, _ax = _cargar_hue()
    color_fn, hexrgb_fn = _cargar_color()
    nd = _cargar_no_dup()
    eng = nd._cargar_engine()
    pl = eng.PatternLibrary(str(MOTOR_DIR / "patterns_final_v14.json"))
    fam_por_token = nd._familias_por_token(pl)
    out = {"version": VERSION, "casos": []}
    for nombre in CASOS:
        out["casos"].append(procesar_caso(nombre, nd, hue_fn, hx_fn,
                                          color_fn, hexrgb_fn, eng, pl, fam_por_token))
    Path("/home/hatch/workspace/u6-alterno/rueda_conjuncion_resumen.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print("resumen:", "/home/hatch/workspace/u6-alterno/rueda_conjuncion_resumen.json")
    return out


if __name__ == "__main__":
    main()
