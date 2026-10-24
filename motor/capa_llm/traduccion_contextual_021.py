#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""traduccion_contextual_021.py — capa LLM (FUERA del motor), U3_predictibilidad 2026-10-11.

Dos funciones, ambas deterministas y sin red:
 1) ENTRADA: derivar_contexto_rol(case) -> token neutral de oficio/dominio del sujeto (p. ej. oficio=arte_composicion)
    a partir del texto propio de los cortes <= Z (léxico genérico de oficios; sin nombres ni años). Si el input ya trae
    case["contexto_rol"]["oficio"], se respeta. Se agrega al payload como case["contexto_rol"]; el motor NO lo usa para puntuar
    (el bloque 021 solo lo registra).
 2) SALIDA: traducir(result, case_sellado) -> para cada hipótesis del set necesario y suficiente, la evidencia como
    TEXTO REAL de los cortes (hecho/narracion del input sellado, con sus nombres), los tokens que la enlazan, los cortes que deja
    sin explicar, y una lectura condicionada por el oficio y el periodo del corte (sin presentismo).
    No agrega hipótesis, no cambia orden/H1/H2/margen/grado, no consulta el futuro (solo cortes que entraron al freeze).
"""
from __future__ import annotations
import json, re, sys, unicodedata
from pathlib import Path

VERSION = "TRADUCCION_CONTEXTUAL_021_20261011"

def _norm(s):
    return "".join(ch for ch in unicodedata.normalize("NFD", str(s).lower()) if unicodedata.category(ch) != "Mn")

# Léxico genérico de oficios (raíces sin acento). Ningún nombre propio ni año.
LEXICO_OFICIO = {
    "arte_composicion": ["compon", "compos", "opera", "operistic", "music", "estren", "sinfon", "concierto", "partitura", "teatral", "compos", "symphon"],
    "arte_plastica": ["pint", "escult", "lienzo", "fresco", "retablo"],
    "religion_gobierno_eclesial": ["papa", "pontific", "obisp", "cardenal", "iglesia", "clero", "conclave", "eclesi", "diocesis", "nuncio", "sacerd", "curia", "teolog", "convent", "dominic", "heret", "church", "bishop", "pope"],
    "filosofia_ciencia": ["filosof", "teor", "tratado", "cosmolog", "universidad", "catedra", "doctrina", "astronom", "matemat", "fisic", "ciencia", "ensenanza", "conferenc", "philosoph", "theor", "physic"],
    "empresa_tecnologia": ["empresa", "compania", "startup", "cohete", "inversion", "software", "ingenier", "fabrica", "mercado", "accionist", "company", "rocket", "comput", "investor", "investment", "launch", "electric", "founded", "ventur", "acquisi", "ceo"],
    "politica_estado": ["gobierno", "eleccion", "partido", "ministro", "parlamento", "presiden", "guerra", "estado", "diplomat", "government", "election"],
}

def _texto_corte(c):
    return str(c.get("hecho") or c.get("narracion") or c.get("texto") or c.get("source_note") or "")

def _textos(case):
    """id -> texto real del corte; si el corte no trae texto y el input trae source_notes alineadas 1:1 con los cortes, usa esa nota."""
    cs = case.get("cuts") or []; sn = case.get("source_notes") if isinstance(case.get("source_notes"), list) else []
    out = {}
    for i, c in enumerate(cs):
        t = _texto_corte(c)
        if not t and len(sn) == len(cs): t = str(sn[i])
        out[str(c.get("id") or f"C{i+1}")] = t
    return out

def derivar_contexto_rol(case):
    ctx = case.get("contexto_rol") if isinstance(case.get("contexto_rol"), dict) else {}
    if ctx.get("oficio"):
        return {"oficio": ctx["oficio"], "fuente": "INPUT_LLM", "evidencia": ctx.get("evidencia", [])}
    hits = {d: [] for d in LEXICO_OFICIO}
    for cid, txt in _textos(case).items():
        words = re.findall(r"[a-z0-9_]+", _norm(txt))
        for d, roots in LEXICO_OFICIO.items():
            for w in words:
                r = next((r for r in roots if w.startswith(r)), None)
                if r: hits[d].append([cid, r])
    cnt = {d: len(v) for d, v in hits.items()}
    best = max(cnt.values()) if cnt else 0
    if best == 0:
        return {"oficio": "NO_DETERMINADO", "fuente": "derivado_lexico_oficio_021", "conteos": cnt, "evidencia": []}
    top = sorted(d for d, v in cnt.items() if v == best)
    of = top[0] if len(top) == 1 else "MIXTO:" + "+".join(top)
    ev = [h for d in top for h in hits[d]]
    return {"oficio": of, "fuente": "derivado_lexico_oficio_021 (texto propio de los cortes; raíces genéricas, sin nombres ni años)",
            "conteos": cnt, "evidencia": ev[:24], "n_evidencia": len(ev)}

def agregar_contexto_rol(case):
    out = json.loads(json.dumps(case)); out["contexto_rol"] = derivar_contexto_rol(case); return out

# Familias de "impulso" (riesgo de presentismo): se detectan por sus tokens_favor en el catálogo, no por nombre.
TOKENS_IMPULSO = {"ambicion", "poder", "codicia", "sed_de_mando", "maquiavelismo", "competencia", "logro", "escalada_status", "rivalidad_poder", "conquista"}
OBJETO_POR_OFICIO = {
    "arte_composicion": "la obra y el oficio: encargos, estrenos, puestos de servicio o independencia, reconocimiento de público, corte o mecenas, volumen y ambición de la producción",
    "arte_plastica": "la obra y el taller: encargos, mecenazgo, escala y ambición de las obras",
    "religion_gobierno_eclesial": "la autoridad y la jurisdicción eclesial: gobierno de la institución, doctrina, influencia sobre poderes temporales",
    "filosofia_ciencia": "la teoría y la verdad buscada: obra escrita, cátedra, polémica y reconocimiento de pares",
    "empresa_tecnologia": "la escala de la empresa y del producto: mercado, capital, metas técnicas",
    "politica_estado": "el poder político: cargos, mando, territorio, alianzas",
}
OFICIOS_PODER_LITERAL = {"politica_estado", "religion_gobierno_eclesial", "empresa_tecnologia"}

def lectura_por_oficio(fam, patterns, oficio):
    pv = patterns.get(fam) or {}
    desc = pv.get("description", "SIN_DESCRIPCION_EN_244")
    fav = set(pv.get("tokens_favor") or {})
    imp = sorted(fav & TOKENS_IMPULSO)
    base = {"familia": fam, "descripcion_catalogo": desc, "es_familia_de_impulso": bool(imp), "tokens_impulso_en_catalogo": imp}
    of = oficio.split(":", 1)[-1].split("+")[0] if oficio else ""
    if imp and of in OBJETO_POR_OFICIO:
        base["lectura_en_oficio"] = (f"impulso cuyo objeto, en el oficio {oficio} y con los criterios del periodo de cada corte, es "
                                     f"{OBJETO_POR_OFICIO[of]}")
        if of not in OFICIOS_PODER_LITERAL:
            base["lectura_presentista_a_evitar"] = (f"leer la descripción literal ('{desc}') como ascenso social/económico o poder personal "
                                                    "con criterios actuales; en este oficio el objeto del impulso es la obra")
    elif imp:
        base["lectura_en_oficio"] = "familia de impulso sin oficio determinado: se deja la descripción del catálogo y se marca para revisión"
    else:
        base["lectura_en_oficio"] = "sin especialización por oficio (familia que no es de impulso): se usa la descripción del catálogo"
    return base

def traducir(result, case, patterns, max_chars=320):
    rol = derivar_contexto_rol(case)
    TX = _textos(case)
    hns = result.get("hipotesis_necesarias_suficientes") or {}
    inv = (((result.get("predictibilidad_021") or {}).get("paso_inverso") or {}).get("por_hipotesis") or {})
    ph = ((((result.get("predictibilidad_021") or {}).get("predictibilidad") or {}).get("por_hipotesis")) or {})
    out = []
    for m in hns.get("miembros") or []:
        fam = m["familia"]; h = inv.get(fam) or {}
        ev = []
        for f in h.get("cortes") or []:
            if f["estado"] in ("EXPLICA", "EXPLICA_CON_CONTRA"):
                t = TX.get(f["corte"], "")
                ev.append({"corte": f["corte"], "tokens": [f"{e}:{tk}({w})" for e, tk, w in f["tokens_explicados"]],
                           "en_contra": [f"{e}:{tk}({w})" for e, tk, w in f["tokens_en_contra"]],
                           "texto_del_corte": t[:max_chars] + ("…" if len(t) > max_chars else "")})
        sin = [{"corte": c, "texto_del_corte": TX.get(c, "")[:160]} for c in h.get("cortes_sin_explicar") or []]
        out.append({"familia": fam, "rol": m.get("rol"), "peso_en_set": m.get("peso_en_set"),
                    "predictibilidad_estructural_pct": (ph.get(fam) or {}).get("predictibilidad_estructural_pct"),
                    "top_componentes": (ph.get(fam) or {}).get("top_componentes", [])[:4],
                    "lectura": lectura_por_oficio(fam, patterns, rol["oficio"]),
                    "evidencia_en_contexto": ev, "cortes_que_deja_sin_explicar": sin,
                    "cortes_unicos_en_el_set": m.get("cortes_unicos", [])})
    return {"version": VERSION, "case_id": result.get("case_id"), "contexto_rol": rol, "eje": hns.get("eje"),
            "grado_inverso": (hns.get("grado_inverso") or {}).get("estado"), "set": out,
            "reglas": "solo cortes que entraron al freeze; texto real del input sellado; no agrega hipótesis ni cambia H/orden/grado; la lectura por oficio no cambia puntajes"}

if __name__ == "__main__":
    r = json.load(open(sys.argv[1])); c = json.load(open(sys.argv[2])); pat = json.load(open(sys.argv[3]))
    if isinstance(c, list): c = {"cuts": c}
    print(json.dumps(traducir(r, c, pat), ensure_ascii=False, indent=1))
