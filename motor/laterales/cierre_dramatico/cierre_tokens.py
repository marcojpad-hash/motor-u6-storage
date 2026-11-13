#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cierre_tokens.py — Lateral: cierres en estructuras dramáticas.

Pedido de Mj (2026-11-12 ~21:02 CST): hay que ver los toques de cierre en
estructuras dramáticas, que esas son las que nos faltan, por eso estábamos
con Polti. Matiz de Mj (~21:03): posiblemente ahí también faltan TOKENS
que vayan hacia los cierres, porque no hacen falta reglas más allá de las
que ya tenemos, que se activan dependiendo de la carga semántica de los
mismos tokens. O sea: el trabajo es de TOKENS, no de reglas nuevas.

Qué hace este lateral (NO toca Engine, ni 244, ni correr_estandar, ni los
RESULT/entradas sellados; solo los LEE; can_decide_H=False):
  1. Inventario de tokens de cierre en el 244: por token, en qué familias
     está como favor y en cuáles como contra, con su peso.
  2. Auditoría por caso: qué tokens de cierre implica el desenlace sellado
     (dos capas: catálogo — tokens de cierre en el favor de las familias
     del desenlace registrado en la matriz; prosa — lectura de la nota de
     desenlace de la entrada, solo cuando el texto enuncia literalmente
     el concepto, con la cita) frente a cuáles trae realmente la entrada.
  3. Tabla Polti -> tokens de cierre, derivada SOLO de desenlaces sellados
     de casos que tienen la situación como H1 o en el desenlace. Sin caso
     => SIN CASO, no se inventa nada.
  4. Medición sombra (cota superior): si los tokens de cierre faltantes
     APLICABLES (existen como favor en el 244) hubieran estado en la
     entrada, ¿se mueven monomito_12 o heroe? Todos los faltantes
     aplicables se añaden al corte final (C7 = Z) en el eje P, a peso de
     contrato 0.72 (sensibilidad 0.60 y 0.84), simulando el cuello top-5
     (soltar el de menor peso). Se re-corre el tablero sombra reutilizando
     correr_tablero_sombra de no_duplicacion_latencia.py (importado, no
     copiado) en dedup=True (corregido) y dedup=False (canon), cada variante
     contra SU PROPIA base del mismo dedup, más un CONTROL solo-cuello
     (mismos soltados, sin tokens de cierre) para separar el efecto del
     cuello del efecto del cierre. La puerta de cordura se corre sobre la
     entrada SIN modificar (debe reproducir el tablero sellado).

Hallazgos que este lateral deja medidos (ver reporte):
  - 11 tokens de cierre NO EXISTEN en el 244 (ni favor ni contra):
    cierre, desenlace, anagnorisis, peripeteia, regreso, elixir, legado,
    testamento, despedida, culminacion, clausura. redencion, reconocimiento
    y perdon existen SOLO como contra (favor 0).
  - En las 81 entradas de la copia de trabajo (241 tokens distintos) solo
    aparecen TRES tokens de cierre: proposito_claro, reconocimiento,
    sabiduria_compartida. retorno, resolucion, catarsis, reconciliacion,
    restauracion_equilibrio NO aparecen en NINGUNA entrada. Semmelweis
    (todas sus variantes) NINGUNO.
  - La tabla Polti está casi vacía: 19 de 36 situaciones SIN CASO; de las
    17 con caso, solo 2 tienen algún token de cierre (5_persecucion y
    20_sacrificio_por_un_ideal, vía heroe/monomito_12 en los desenlaces).
  - Sombra (dedup=True, peso 0.72): el token de cierre mueve 'heroe' a H1
    sombra (empatado) en Semmelweis (+0.138) y Kolbe (+0.022), y a
    monomito_12 a H1 sombra (empatado) en Tubman (+0.012); en Juana y
    Mandela no mueve nada (token compartido -> latencia, sin compañía).
    A peso 0.60 el cuello top-5 suelta los propios tokens de cierre: no
    entran nunca. monomito_12 NO se mueve en Semmelweis/Kolbe/Juana/
    Mandela (ningún faltante aplicable lo alimenta ahí).
"""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

VERSION = "CIERRE_TOKENS_V1_20261112"
BASE = Path("/home/hatch/workspace/u6-alterno/motor-cameo")
MOTOR_DIR = BASE / "motor" / "motor"
ND_PATH = BASE / "motor" / "reconexion_v2a1" / "no_duplicacion_latencia.py"
MATRIZ_PATH = Path("/home/hatch/workspace/u6-alterno/matriz_finales_arquetipo.json")

CIERRE_TOKENS = [
    "cierre", "desenlace", "retorno", "reconciliacion", "resolucion",
    "catarsis", "redencion", "reconocimiento", "anagnorisis", "peripeteia",
    "regreso", "elixir", "paz_interior", "sabiduria_compartida",
    "proposito_claro", "restauracion_equilibrio", "perdon", "reintegracion",
    "sacrificio_final", "superacion_miedo_raiz", "cambio_identidad",
    "legado", "testamento", "despedida", "culminacion", "clausura",
]

HEROES7 = [
    "JUANA_DE_ARCO_HEROE_20261112",
    "TUBMAN_HEROE_20261112",
    "MANDELA_HEROE_20261112",
    "SEMMELWEIS_HEROE_SIN_TRONO_20261112",
    "KOLBE_HEROE_SIN_TRONO_20261112",
    "NOETHER_CIEGO_Z90_20260914",
    "CARSON_CIEGO_Z90_20260914",
]

HEROES5 = HEROES7[:5]

# Prosa -> token de cierre, SOLO cuando el texto del desenlace sellado
# (source_notes) enuncia literalmente el concepto. Lectura del auditor,
# revisable: cada entrada lleva su cita.
PROSA_MAP: Dict[str, List[Tuple[str, str]]] = {
    "JUANA_DE_ARCO_HEROE_20261112": [
        ("reconocimiento", "Rehabilitada 1456; canonizada 1920"),
        ("sacrificio_final", "condenada por herejia y quemada el 30-may-1431"),
    ],
    "TUBMAN_HEROE_20261112": [
        ("reconocimiento", "honrada por el ejercito y por el pais"),
        ("legado", "su obra (el ferrocarril subterraneo, la lucha por la libertad) perdura"),
    ],
    "MANDELA_HEROE_20261112": [
        ("reconocimiento", "funeral de Estado y duelo mundial"),
        ("reconciliacion", "su legado (reconciliacion, fin del apartheid) perdura"),
        ("legado", "su legado (reconciliacion, fin del apartheid) perdura"),
    ],
    "SEMMELWEIS_HEROE_SIN_TRONO_20261112": [
        ("reconocimiento", "Reivindicado tras su muerte (Lister, teoria germinal)"),
        ("restauracion_equilibrio", "'salvador de las madres'"),
        ("legado", "generativo tras la muerte"),
    ],
    "KOLBE_HEROE_SIN_TRONO_20261112": [
        ("reconocimiento", "Canonizado en 1982 ('martir de la caridad')"),
        ("sacrificio_final", "Canonizado en 1982 ('martir de la caridad')"),
        ("restauracion_equilibrio", "Gajowniczek sobrevive a la guerra"),
    ],
    "NOETHER_CIEGO_Z90_20260914": [
        ("legado", "sigue la teoria (post-Z: ensena en Bryn Mawr)"),
    ],
    "CARSON_CIEGO_Z90_20260914": [
        ("reconocimiento", "Silent Spring 1962, atencion mundial"),
    ],
}

# Faltantes APLICABLES por caso (de la auditoría): existen como favor en el
# 244 y el desenlace sellado los implica, pero la entrada no los trae.
FALTANTES_APLICABLES: Dict[str, List[str]] = {
    "JUANA_DE_ARCO_HEROE_20261112": ["sacrificio_final"],
    "TUBMAN_HEROE_20261112": ["paz_interior", "resolucion"],
    "MANDELA_HEROE_20261112": ["reconciliacion"],
    "SEMMELWEIS_HEROE_SIN_TRONO_20261112": ["restauracion_equilibrio"],
    "KOLBE_HEROE_SIN_TRONO_20261112": ["restauracion_equilibrio", "sacrificio_final"],
}

OBJETIVO = ["monomito_10_el_camino_de_regreso", "monomito_11_la_resurreccion",
            "monomito_12_regreso_con_el_elixir",
            "heroe", "arquetipo_heroe", "arquetipo_el_heroe"]


def cargar_catalogo() -> Dict[str, Any]:
    return json.loads((MOTOR_DIR / "patterns_final_v14.json")
                      .read_text(encoding="utf-8"))


def inventario_cierre(cat: Dict[str, Any]) -> Dict[str, Any]:
    """Tarea 1: token -> {favor: {fam: peso}, contra: {fam: peso}}."""
    out = {}
    for tok in CIERRE_TOKENS:
        favor, contra = {}, {}
        for fam, d in cat.items():
            if tok in (d.get("tokens_favor") or {}):
                favor[fam] = (d["tokens_favor"] or {})[tok]
            if tok in (d.get("tokens_contra") or {}):
                contra[fam] = (d["tokens_contra"] or {})[tok]
        out[tok] = {"favor": favor, "contra": contra}
    return out


def tokens_en_entrada(entrada: Dict[str, Any]) -> Dict[str, List[Tuple[str, str, float]]]:
    out: Dict[str, List[Tuple[str, str, float]]] = {}
    for cut in entrada.get("cuts", []):
        for eje in ("P", "A", "C"):
            for t, w in (cut.get(eje) or []):
                out.setdefault(t, []).append((cut.get("id"), eje, float(w)))
    return out


def limpiar_familia(s: Optional[str]) -> Optional[str]:
    s = (s or "").strip()
    if "(" in s:
        s = s[: s.index("(")].strip()
    return s or None


def implicados_catalogo(familias_desenlace: List[str],
                        cat: Dict[str, Any]) -> Dict[str, List[Tuple[str, float]]]:
    """Tokens de cierre en el favor de las familias del desenlace sellado."""
    out: Dict[str, List[Tuple[str, float]]] = {}
    for fam in familias_desenlace:
        fam = limpiar_familia(fam)
        if not fam or fam not in cat:
            continue
        for tok, peso in (cat[fam].get("tokens_favor") or {}).items():
            if tok in CIERRE_TOKENS:
                out.setdefault(tok, []).append((fam, peso))
    return out


def cargar_matriz() -> Dict[str, Any]:
    matriz = json.loads(MATRIZ_PATH.read_text(encoding="utf-8"))
    por_caso = {}
    for h1, casos in matriz.items():
        for c in casos:
            por_caso[c["caso"]] = {"h1": h1, "h2": c.get("H2"),
                                   "fatalidad": c.get("fatalidad"),
                                   "desenlace": c.get("desenlace") or []}
    return por_caso


def auditar_caso(nombre: str, cat: Dict[str, Any], inv: Dict[str, Any],
                 desenlace_matriz: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Tarea 2 para un caso con prosa: implicado vs presente -> faltantes."""
    entrada = json.loads(
        (BASE / "casos" / "precedentes" / nombre / "entrada.json")
        .read_text(encoding="utf-8"))
    presentes = tokens_en_entrada(entrada)
    presentes_cierre = {t: v for t, v in presentes.items() if t in CIERRE_TOKENS}
    fams_des = (desenlace_matriz or {}).get("desenlace") or []
    impl_cat = implicados_catalogo(fams_des, cat)
    impl_prosa = {t: cita for t, cita in PROSA_MAP.get(nombre, [])}
    impl_todos = set(impl_cat) | set(impl_prosa)
    faltantes = sorted(t for t in impl_todos if t not in presentes_cierre)
    return {
        "caso": nombre,
        "h1_matriz": (desenlace_matriz or {}).get("h1"),
        "presentes_cierre": {t: v for t, v in presentes_cierre.items()},
        "desenlace_familias": fams_des,
        "implicados_catalogo": {t: v for t, v in impl_cat.items()},
        "implicados_prosa": impl_prosa,
        "faltantes": faltantes,
        "faltantes_aplicables": sorted(t for t in faltantes if inv[t]["favor"]),
        "faltantes_inexistentes": sorted(
            t for t in faltantes if not inv[t]["favor"] and not inv[t]["contra"]),
        "faltantes_solo_contra": sorted(
            t for t in faltantes if not inv[t]["favor"] and inv[t]["contra"]),
    }


def tabla_polti(cat: Dict[str, Any],
                por_caso: Dict[str, Any]) -> Dict[str, Any]:
    """Tarea 3: por situación de Polti, tokens de cierre de sus desenlaces
    sellados (solo casos que la tienen como H1 o en el desenlace)."""
    polti_ids = sorted([k for k in cat if k.split("_")[0].isdigit()],
                       key=lambda x: int(x.split("_")[0]))
    tabla = {}
    for pid in polti_ids:
        casos_rel, toks = [], {}
        for caso_nombre, d in por_caso.items():
            fams_limpias = [limpiar_familia(f) for f in d["desenlace"]]
            if d["h1"] == pid or pid in fams_limpias:
                casos_rel.append(caso_nombre)
                for t, org in implicados_catalogo(d["desenlace"], cat).items():
                    toks.setdefault(t, []).extend(org)
        tabla[pid] = {"casos": casos_rel, "tokens_cierre": toks}
    return tabla


def _cargar_no_dup():
    spec = importlib.util.spec_from_file_location("nd_cierre", str(ND_PATH))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _cuello_top5(rows, nuevos):
    todas = list(rows) + [(t, w) for t, w in nuevos]
    if len(todas) <= 5:
        return todas, []
    orden = sorted(range(len(todas)),
                   key=lambda i: (-todas[i][1], 0 if i >= len(rows) else 1))
    keep = sorted(orden[:5])
    soltados = [todas[i] for i in orden[5:]]
    return [todas[i] for i in keep], soltados


def _top_movers(base_p, var_p, n=5):
    mov = sorted(((abs(var_p.get(f, 0) - base_p.get(f, 0)), f,
                   base_p.get(f), var_p.get(f))
                  for f in set(base_p) | set(var_p)), reverse=True)
    return [{"familia": f, "p_base": b, "p_var": v, "delta": round(v - b, 4)}
            for _, f, b, v in mov[:n]]


def contrafactual_cierre(nd, eng, pl, fam_por_token,
                         nombre: str, faltantes: List[str]) -> Dict[str, Any]:
    """Tarea 4 para un caso: cota superior del efecto de los tokens de
    cierre faltantes aplicables, añadidos al C7 en P a peso de contrato."""
    entrada = json.loads(
        (BASE / "casos" / "precedentes" / nombre / "entrada.json")
        .read_text(encoding="utf-8"))
    resultado = json.loads(
        (BASE / "motor" / f"RESULT_{nombre}.json").read_text(encoding="utf-8"))
    bases = {}
    for dedup in (True, False):
        s = nd.correr_tablero_sombra(entrada, resultado, eng, pl,
                                     fam_por_token, dedup=dedup)
        final_p = s["boards"]["P"][-1]
        top = sorted(final_p.items(), key=lambda kv: -kv[1])
        bases[dedup] = {"board": final_p,
                        "rango": {f: i + 1 for i, (f, _) in enumerate(top)},
                        "h1": top[0][0], "p_h1": top[0][1]}
    gate_off = nd.correr_tablero_sombra(entrada, resultado, eng, pl,
                                        fam_por_token, dedup=False)
    gate_ok = (gate_off["gate_mismatch"] == 0
               and gate_off["gate_max_diff"] <= 1e-6)
    caso = {"caso": nombre, "faltantes": faltantes, "gate_pasa": gate_ok,
            "base_dedup_true": {"h1_sombra": bases[True]["h1"],
                                "p_h1": bases[True]["p_h1"]},
            "base_dedup_false": {"h1_sombra": bases[False]["h1"],
                                 "p_h1": bases[False]["p_h1"]},
            "variantes": {}}
    for peso in (0.60, 0.72, 0.84):
        c7 = entrada["cuts"][-1]
        rows_p = [(str(t), float(w)) for t, w in c7["P"]]
        nuevas, soltados = _cuello_top5(rows_p, [(t, peso) for t in faltantes])
        cut_pesos = {}
        for eje in ("P", "A", "C"):
            for t, w in (c7.get(eje) or []):
                cut_pesos[t] = max(cut_pesos.get(t, 0.0), float(w))
        for t in faltantes:
            cut_pesos[t] = max(cut_pesos.get(t, 0.0), peso)
        asignacion = {t: nd._asignar(t, cut_pesos, fam_por_token)
                      for t in faltantes}
        for dedup in (True, False):
            for modo in ("cierre", "control_solo_cuello"):
                mod = copy.deepcopy(entrada)
                c7m = mod["cuts"][-1]
                if modo == "cierre":
                    c7m["P"] = [[t, w] for t, w in nuevas]
                else:
                    keep = [r for r in rows_p
                            if (r[0], r[1]) not in
                            [(s[0], s[1]) for s in soltados]]
                    c7m["P"] = [[t, w] for t, w in keep]
                sombra = nd.correr_tablero_sombra(
                    mod, resultado, eng, pl, fam_por_token, dedup=dedup)
                final_p = sombra["boards"]["P"][-1]
                top = sorted(final_p.items(), key=lambda kv: -kv[1])
                rango = {f: i + 1 for i, (f, _) in enumerate(top)}
                base = bases[dedup]
                clave = f"peso_{peso}_dedup_{dedup}_{modo}"
                caso["variantes"][clave] = {
                    "soltados_cuello": [list(s) for s in soltados],
                    "asignacion_cierre": ({t: list(a) for t, a in asignacion.items()}
                                          if modo == "cierre" else {}),
                    "h1_sombra": top[0][0], "p_h1_sombra": top[0][1],
                    "deltas": {f: {"p": final_p.get(f),
                                   "rango": rango.get(f),
                                   "delta_p": round(final_p.get(f, 0)
                                                    - base["board"].get(f, 0), 4)}
                               for f in OBJETIVO},
                    "top_movers": _top_movers(base["board"], final_p),
                    "frentes": len(sombra["frentes"]),
                }
    return caso


def verificar_todo() -> Dict[str, Any]:
    """Corre tareas 1-4 y devuelve el resultado completo (JSON)."""
    cat = cargar_catalogo()
    inv = inventario_cierre(cat)
    por_caso = cargar_matriz()
    auditoria7 = {}
    for nombre in HEROES7:
        m = None
        for caso_nombre, d in por_caso.items():
            if nombre.split("_")[0].lower() in caso_nombre.lower():
                m = d
                break
        auditoria7[nombre] = auditar_caso(nombre, cat, inv, m)
    tabla = tabla_polti(cat, por_caso)
    nd = _cargar_no_dup()
    eng = nd._cargar_engine()
    pl = eng.PatternLibrary(str(MOTOR_DIR / "patterns_final_v14.json"))
    fam_por_token = nd._familias_por_token(pl)
    sombra = {}
    for nombre in HEROES5:
        sombra[nombre] = contrafactual_cierre(
            nd, eng, pl, fam_por_token, nombre, FALTANTES_APLICABLES[nombre])
        print(f"{nombre}: gate={sombra[nombre]['gate_pasa']} "
              f"H1_sombra_base(dedup=True)="
              f"{sombra[nombre]['base_dedup_true']['h1_sombra']}")
    return {"version": VERSION, "inventario": inv,
            "auditoria_7": auditoria7, "tabla_polti": tabla,
            "sombra": sombra}


if __name__ == "__main__":
    data = verificar_todo()
    out_path = Path(__file__).resolve().parent / "cierre_tokens_resultado.json"
    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2),
                        encoding="utf-8")
    print("escrito:", out_path)
