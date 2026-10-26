#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""laterales_unico_v1.py — HUB de laterales y sensores del MOTOR ÚNICO V15.3 (27-sep-2026).

Contrato para TODO lo que corre aquí: can_decide_H=False, no escribe H1/H2, no reordena candidatos,
no escribe el catálogo de patrones (solo lectura), no toca Engine_V5.
Dos tipos de salida:
  * VOTO (entra al ranking solo como UN módulo más del puente de nombres del predictor, acotado por
    lateral_contribution; nunca escribe H):  negativo Ricci–Forman vs billar, familias de tokens (EXPERIMENTAL).
  * SENSOR (se reporta; no entra al ranking): todo lo demás.
Cada pieza reporta estado: ACTIVA | ACTIVA_MUDA (corre pero no tiene con qué mapear/no emite señal) |
NO_CORRE (motivo) | SUPERADA (otra versión más completa ya corre) | APAGADA_POR_FLAG.
Todo se puede apagar por flag de entorno LAT_<NOMBRE>=0; por defecto todo ON.
"""
from __future__ import annotations
import copy, hashlib, importlib.util, json, math, os, random, sys, traceback, unicodedata, re
from pathlib import Path
from typing import Any, Dict, List

VERSION = "LATERALES_UNICO_V1_20260927"
SCORE_NEGATIVO = {"SE_SOSTIENE": 1.0, "TENSION_LATENTE": 0.5, "DESCARTE_DEBIL_LATENTE": 0.25, "DESCARTE": 0.0, "LATENTE": 0.5}


def _sha(p: Path):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest() if Path(p).is_file() else None


def _load(base: Path, fn: str, alias: str):
    p = Path(base) / fn
    if not p.is_file():
        return None, {"archivo": fn, "presente": False}
    if str(base) not in sys.path:
        sys.path.insert(0, str(base))
    spec = importlib.util.spec_from_file_location(alias, p)
    m = importlib.util.module_from_spec(spec)
    sys.modules[alias] = m
    spec.loader.exec_module(m)
    return m, {"archivo": fn, "presente": True, "sha256": _sha(p)}



# CEB_HONESTIDAD_CALDERO (20261025): "presente" != búsqueda externa real. Estados alineados con correr_estandar.search_performed.
_PROV_FIXTURE = ("provided_fixture", "static_fixture")
_GATED = ("SKIPPED_INTERNAL_ANALYSIS",)


def _recibo_caldero(rc, cal):
    rc = rc if isinstance(rc, dict) else {}
    cal = cal if isinstance(cal, dict) else {}
    pr = (cal.get("audit") or {}).get("provider_receipt") or {}
    return {"provider": rc.get("provider") or pr.get("provider"), "attempt_status": rc.get("status"),
            "query_count": int(rc.get("query_count", 0) or 0), "result_count": int(rc.get("result_count", 0) or 0),
            "cal_status": cal.get("status"), "error": rc.get("error") or cal.get("error")}


def estado_honesto_caldero(cb):
    cb = cb or {}
    st, prov = cb.get("attempt_status"), cb.get("provider")
    if st in _GATED or cb.get("cal_status") in _GATED:
        return "OMITIDO_POR_CONDICION"
    if st == "EXECUTED_FIXTURE" or prov in _PROV_FIXTURE:
        return "SIMULADO_FIXTURE"
    if st == "EXECUTED" and prov not in (None, "", "auto", "none") and int(cb.get("query_count") or 0) >= 1 and int(cb.get("result_count") or 0) >= 1:
        return "EJECUTADO"
    if st in (None, "NOT_RUN") and not cb.get("presente"):
        return "NO_INVOCADO"
    if st == "FAILED" and cb.get("error") == "sidecar_missing" and not cb.get("presente"):
        return "NO_INVOCADO"
    return "INTENTADO_FALLIDO"

# REGLA_MJ_20261025: las herramientas existen para EJECUTARSE. El CEB explica el fallo, no lo justifica.
# Todo estado != EJECUTADO es un INCUMPLIMIENTO a investigar, salvo omisión documentada en contrato
# (hoy solo: SKIPPED_INTERNAL_ANALYSIS de la subcorrida interna T1, required=False en el motor).
_CAUSA = {"SIMULADO_FIXTURE": "usó fixture/grabación en vez de buscar en vivo: averiguar por qué no se buscó de verdad",
          "NO_INVOCADO": "el sidecar ni siquiera se llamó: averiguar qué rama del motor lo saltó",
          "INTENTADO_FALLIDO": "se intentó y falló o trajo 0 resultados: revisar error/proveedor/red",
          "OMITIDO_POR_CONDICION": "omitido por compuerta: válido solo si el contrato lo permite"}


def alerta_ejecucion(estado, contrato_permite_omision=False, error=None):
    if estado == "EJECUTADO":
        return {"debe_ejecutarse": True, "incumplimiento": False, "severidad": "OK", "accion": "ninguna"}
    if estado == "OMITIDO_POR_CONDICION" and contrato_permite_omision:
        return {"debe_ejecutarse": False, "incumplimiento": False, "severidad": "INFO_OMISION_CONTRACTUAL",
                "accion": "omisión permitida por contrato (subcorrida interna)"}
    return {"debe_ejecutarse": True, "incumplimiento": True, "severidad": "FALLO_EJECUCION",
            "alerta": f"FALLO DE EJECUCIÓN / A INVESTIGAR: {estado}", "accion": _CAUSA.get(estado, "averiguar por qué no corrió"),
            **({"error": error} if error else {})}


# REGLA_MJ_20261025 (generalizada a TODAS las piezas): ninguna pieza está de adorno. El CEB localiza DÓNDE no corrió
# para que el modelo investigue POR QUÉ y lo RESUELVA. Clasificación del estado de ejecución (no toca predicción).
_EST_OK = {"ACTIVA", "MARCAJE", "GUARDIAN_FILTRO", "EJECUTADO", "CADENA_COMPLETA", "PERSISTED", "EXECUTED"}
_EST_CORRIO_SIN_SENAL = {"ACTIVA_MUDA"}  # corrió; no aportó/no llegó a H en este caso -> INFO, no fallo de ejecución
_EST_INFO_CONTRATO = {"SUPERADA": "pieza histórica sustituida (contrato: ya no debe correr)",
                      "ABSORBIDO_EN_GUARDIA_TRANSVERSAL": "absorbida por otra pieza (contrato)",
                      "NOT_APPLICABLE": "no aplica por contrato"}
_EST_FALLO = {"NO_CORRE": "la pieza lanzó excepción: leer 'aporte'/trace, corregir el import/datos/código y re-correr smoke",
              "APAGADA_POR_FLAG": "apagada por variable LAT_*=0: en fábrica no se apaga; quitar el flag o documentar contrato",
              "API_PENDING": "adaptador/API sin conectar: cablear la API (credencial/endpoint) o el proveedor y re-correr",
              "NO_INVOCADO": "no se llamó: buscar qué rama del motor/laterales la saltó",
              "SIN_EJECUCION": "no corrió (dependencia previa no corrió): resolver primero la pieza de la que depende",
              "NO_ENCONTRADO_EN_STORE": "corrió la búsqueda pero no persistió en el store: revisar ruta del store/escritura",
              "SKIPPED": "saltada sin contrato que lo permita: averiguar la condición",
              "FAILED": "falló: leer error y corregir", **_CAUSA}


def alerta_pieza(estado, contrato_permite_omision=False, error=None):
    """Marco Caldero (debe_ejecutarse/incumplimiento/severidad/accion) para CUALQUIER pieza."""
    e = str(estado or "").split()[0] if estado else ""
    if e in _EST_OK:
        return {"debe_ejecutarse": True, "incumplimiento": False, "severidad": "OK", "accion": "ninguna"}
    if e in _EST_CORRIO_SIN_SENAL:
        return {"debe_ejecutarse": True, "incumplimiento": False, "severidad": "INFO_CORRIO_SIN_SENAL",
                "accion": "corrió pero no aportó/no llegó a H en este caso: revisar 'motivo' si se repite en todos los casos"}
    if e in _EST_INFO_CONTRATO or contrato_permite_omision:
        return {"debe_ejecutarse": False, "incumplimiento": False, "severidad": "INFO_OMISION_CONTRACTUAL",
                "accion": _EST_INFO_CONTRATO.get(e, "omisión permitida por contrato (required=False)")}
    if e in _EST_FALLO:
        return {"debe_ejecutarse": True, "incumplimiento": True, "severidad": "FALLO_EJECUCION",
                "alerta": f"FALLO DE EJECUCIÓN / A INVESTIGAR: {e}", "accion": _EST_FALLO[e], **({"error": error} if error else {})}
    return {"debe_ejecutarse": None, "incumplimiento": True, "severidad": "REQUIERE_CONTRATO",
            "alerta": f"estado '{e or '(vacío)'}' sin contrato de ejecución definido", "accion": "definir contrato (¿debe correr en fábrica?) antes de darlo por OK"}


def aplicar_alertas(reg, filas=()):
    """Añade el marco de alerta a cada fila (sin sobrescribir el de Caldero) y devuelve el resumen de fallos."""
    fallos = {}
    for r in list(reg) + list(filas):
        if not isinstance(r, dict): continue
        nombre = r.get("pieza") or r.get("componente")
        est = r.get("estado_verificado") or r.get("estado_ejecucion") or r.get("estado")
        if "severidad" not in r:
            dec = str(r.get("declarado_UNICO") or "")
            if est == "ACTIVA_MUDA" and dec.startswith("API_PENDING"):
                est = "API_PENDING"
            r.update(alerta_pieza(est, contrato_permite_omision=r.get("required") is False))
        if r.get("severidad") in ("FALLO_EJECUCION", "REQUIERE_CONTRATO"):
            fallos[str(nombre).replace("verificado:", "")] = {"estado": est, "severidad": r["severidad"], "accion": r.get("accion")}
    return {"version": "CEB_ALERTAS_MULTIPIEZA_20261025", "n_filas": len(reg) + len(filas), "fallos": fallos,
            "veredicto": "OK" if not fallos else "FALLO_EJECUCION_PIEZAS"}


def flag_on(nombre: str) -> bool:
    return os.environ.get(f"LAT_{nombre.upper()}", "1") != "0"


def _pieza(nombre, archivo, rol, fn, base, reg, **extra):
    """Corre fn() y registra estado. fn devuelve (estado, aporte, salida)."""
    if not flag_on(nombre):
        reg.append({"pieza": nombre, "archivo": archivo, "rol": rol, "estado": "APAGADA_POR_FLAG", "aporte": f"LAT_{nombre.upper()}=0", **extra})
        return None
    try:
        estado, aporte, salida = fn()
    except Exception as e:
        estado, aporte, salida = "NO_CORRE", f"error {type(e).__name__}: {str(e)[:160]}", {"trace": traceback.format_exc()[-800:]}
    sha = _sha(Path(base) / archivo) if archivo and (Path(base) / archivo).is_file() else None
    reg.append({"pieza": nombre, "archivo": archivo, "sha256": sha, "rol": rol, "estado": estado, "aporte": aporte,
                "can_decide_H": False, **extra})
    return salida


def _textos(case):
    out = [{"origen": "question", "corte": None, "texto": str(case.get("question", ""))}]
    for c in case.get("cuts") or []:
        if c.get("source_note"):
            out.append({"origen": "source_note", "corte": c.get("id"), "texto": str(c["source_note"])})
    for s in case.get("caldero_search_sources") or []:
        out.append({"origen": "fuente_snippet", "corte": None, "texto": f"{s.get('title', '')}. {s.get('snippet', '')}"})
    return out


def _tok(c):
    return [str(t) for e in ("P", "A", "C") for t, _ in (c.get(e) or [])]


def _candidatos(motor):
    s = set()
    for c in motor.get("cuts") or []:
        s.update(x.get("familia") for x in (c.get("P_candidatos_0a3") or []))
    s.discard(None)
    return sorted(s)


# ======================================================================= catálogo
def validar_catalogo(base, patterns_path, patterns, motor, features):
    """Valida los puentes de laterales contra el catálogo CARGADO (no asume 244)."""
    fams = set(patterns) if isinstance(patterns, dict) else set()
    vocab = set()
    for pv in (patterns.values() if isinstance(patterns, dict) else []):
        vocab |= set((pv.get("tokens_favor") or {})) | set((pv.get("tokens_contra") or {}))
    out = {"ruta": str(patterns_path), "sha256": _sha(patterns_path), "n_patrones": len(fams), "n_vocabulario": len(vocab)}
    # tableros del motor: claves deben coincidir con el catálogo
    cuts = motor.get("cuts") or []
    if cuts:
        k = set((cuts[-1].get("P_FULL_244") or {}).keys())
        out["tablero_vs_catalogo"] = {"n_claves_tablero": len(k), "en_tablero_no_en_catalogo": sorted(k - fams)[:20],
                                      "en_catalogo_no_en_tablero": sorted(fams - k)[:20], "ok": k == fams}
    # puente de familias de tokens
    pz = Path(base) / "PUENTE_244_FAMILIAS.json"
    if pz.is_file():
        P = json.loads(pz.read_text(encoding="utf-8"))
        words, pats_ref, pats_touch = set(), set(), set()
        for t in P.get("tokens") or []:
            for tier in ("alta", "media", "baja"):
                words |= set((t.get("palabras_244") or {}).get(tier) or [])
            pats_ref |= set(t.get("patrones_explicitos") or []) | set(t.get("patrones_244_explicitos") or [])
            pats_touch |= set(t.get("patrones_por_palabra_alta_media") or []) | set(t.get("patrones_extra_por_palabra_baja") or []) | set(t.get("patrones_tocados") or [])
        out["puente_familias"] = {"sha_catalogo_con_que_se_construyo": P.get("patterns_sha256"),
                                  "construido_con_este_catalogo": P.get("patterns_sha256") == out["sha256"],
                                  "palabras_puente": len(words), "palabras_que_no_existen_en_catalogo": sorted(words - vocab)[:30],
                                  "n_palabras_inexistentes": len(words - vocab),
                                  "patrones_referidos_inexistentes": sorted((pats_ref | pats_touch) - fams)[:30],
                                  "n_patrones_mapeados": len(fams & (pats_touch | pats_ref)),
                                  "n_patrones_sin_ningun_token_lateral": len(fams - pats_touch - pats_ref),
                                  "patrones_sin_ningun_token_lateral": sorted(fams - pats_touch - pats_ref)[:40],
                                  "n_mapeos_a_patrones_inexistentes": len((pats_ref | pats_touch) - fams),
                                  "accion_si_cambia_catalogo": "regenerar con EQUIVALENCIAS_ESCALA_20260927/construir_equivalencias.py apuntando al catálogo nuevo"}
    # registros JSON de laterales que citan tokens/patrones del catálogo (capa2, luces, amantes, matriz de escalas)
    def _refs(o, acc):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in ("pinchos_favor", "pinchos_contra", "tokens_favor", "tokens_contra", "tokens_244", "tokens_canonicos"):
                    acc |= set(v if isinstance(v, list) else (v.keys() if isinstance(v, dict) else []))
                else:
                    _refs(v, acc)
        elif isinstance(o, list):
            for x in o: _refs(x, acc)
        return acc
    regs = {}
    for fn in ("catalogo_capa2_familias_semilla.json", "registro_luces_gemini_packs.json", "registro_sidecar_amantes_arquetipos.json", "MATRIZ_EQUIVALENCIAS_ESCALA.json"):
        fp = Path(base) / fn
        if not fp.is_file():
            regs[fn] = {"estado": "FALTA_ARCHIVO"}; continue
        try:
            d = json.loads(fp.read_text(encoding="utf-8"))
        except Exception as e:
            regs[fn] = {"estado": f"ERROR {type(e).__name__}"}; continue
        refs = {x for x in _refs(d, set()) if isinstance(x, str)}
        falt = sorted(refs - vocab - fams)
        regs[fn] = {"refs": len(refs), "n_no_existen_en_catalogo": len(falt), "no_existen_en_catalogo": falt[:25],
                    "sha_catalogo_declarado": d.get("patterns_sha256") if isinstance(d, dict) else None}
        pz244 = d.get("puente_244") if isinstance(d, dict) else None
        if isinstance(pz244, dict):
            mapa = pz244.get("mapa") or {}
            dest = set()
            for v in mapa.values():
                dest |= set(v if isinstance(v, list) else (v.keys() if isinstance(v, dict) else [v]))
            regs[fn]["puente_244"] = {"estado": pz244.get("estado"), "n_entradas": len(mapa),
                                      "destinos_inexistentes": sorted(str(x) for x in dest if x not in vocab and x not in fams)[:20]}
    # MATRIZ de escalas: ¿se construyó con los mismos archivos de familias que se cargan hoy?
    mz = Path(base) / "MATRIZ_EQUIVALENCIAS_ESCALA.json"
    if mz.is_file():
        try:
            M = json.loads(mz.read_text(encoding="utf-8")); dif = []
            for fam, info in (M.get("familias") or {}).items():
                fp = Path(base) / "familias_tokens" / (fam + ".json")
                if fp.is_file() and info.get("sha256_archivo") and _sha(fp) != info.get("sha256_archivo"): dif.append(fam)
            regs.setdefault("MATRIZ_EQUIVALENCIAS_ESCALA.json", {})["familias_con_archivo_distinto"] = dif
        except Exception as e:
            regs.setdefault("MATRIZ_EQUIVALENCIAS_ESCALA.json", {})["familias_con_archivo_distinto"] = f"ERROR {type(e).__name__}"
    out["registros_laterales"] = regs
    # traza nativa (traza_P / tableros P_FULL_244) sale del catálogo cargado: validada en tablero_vs_catalogo
    # léxicos laterales que dicen usar 'solo tokens del 244'
    lex = {}
    for mod_fn, attr in (("plugin_otto_numinoso.py", "OTTO"), ("plugin_trayectoria_hosteleria.py", "PATRON"), ("plugin_embudo_clinico.py", "CLINICO")):
        m, _ = _load(base, mod_fn, "cat_" + mod_fn.replace(".", "_"))
        if m is None or not hasattr(m, attr):
            continue
        obj = getattr(m, attr); ts = set()
        if isinstance(obj, dict):
            for v in obj.values():
                if isinstance(v, dict):
                    ts |= set(v.get("tokens_favor") or {}) | set(v.get("tokens_contra") or {})
            ts |= set(obj.get("tokens_favor") or {}) | set(obj.get("tokens_contra") or {}) if "tokens_favor" in obj else set()
        elif isinstance(obj, (set, list, tuple)):
            ts = set(obj)
        lex[mod_fn] = {"tokens": len(ts), "no_existen_en_catalogo": sorted(ts - vocab)[:15], "n_inexistentes": len(ts - vocab)}
    dyn = Path(base) / "tokens_laterales/dynamis_dramatica_sistemica_v0_1.json"
    if dyn.is_file():
        d = json.loads(dyn.read_text(encoding="utf-8")); ts = set()
        def walk(o):
            if isinstance(o, dict):
                for k, v in o.items():
                    if k in ("tokens_favor", "tokens_contra") and isinstance(v, dict): ts.update(v)
                    else: walk(v)
            elif isinstance(o, list):
                for v in o: walk(v)
        walk(d)
        lex["dynamis_catalogo"] = {"tokens": len(ts), "n_inexistentes": len(ts - vocab), "no_existen_en_catalogo": sorted(ts - vocab)[:15]}
    out["lexicos_laterales"] = lex
    marcas = []
    if out.get("tablero_vs_catalogo", {}).get("ok") is False: marcas.append("tablero≠catálogo")
    pf = out.get("puente_familias") or {}
    if pf and not pf.get("construido_con_este_catalogo"): marcas.append("puente de familias construido con otro catálogo: regenerar")
    if pf.get("n_palabras_inexistentes"): marcas.append(f"puente: {pf['n_palabras_inexistentes']} palabras no existen en el catálogo")
    if pf.get("patrones_referidos_inexistentes"): marcas.append("puente: mapea a patrones inexistentes")
    if pf.get("n_patrones_sin_ningun_token_lateral"): marcas.append(f"info: {pf['n_patrones_sin_ningun_token_lateral']} patrones del catálogo sin ningún token lateral del puente (no votan en familias)")
    for fn, r in (out.get("registros_laterales") or {}).items():
        if r.get("n_no_existen_en_catalogo"): marcas.append(f"info: {fn}: {r['n_no_existen_en_catalogo']} tokens citados no están en el catálogo cargado (tokens propios del registro o catálogo cambiado)")
        if r.get("sha_catalogo_declarado") and r["sha_catalogo_declarado"] != out["sha256"]: marcas.append(f"{fn}: construido con otro catálogo: regenerar")
    _fd = ((out.get("registros_laterales") or {}).get("MATRIZ_EQUIVALENCIAS_ESCALA.json") or {}).get("familias_con_archivo_distinto")
    if _fd: marcas.append(f"MATRIZ de escalas construida con otra versión de familias {_fd}: regenerar")
    if (lex.get("dynamis_catalogo") or {}).get("n_inexistentes"): marcas.append("info: dynamis usa tokens laterales propios (fuera del catálogo, por diseño)")
    out["marcas"] = marcas
    duras = [m for m in marcas if not m.startswith("info:")]
    out["marcas_duras"] = duras
    out["estado"] = "OK" if not duras else "REVISAR"
    return out


# ======================================================================= VOTOS pre-predictor
def voto_negativo(base, motor, features, case_id):
    est, _ = _load(base, "modo_estricto_v1.py", "lu_estricto")
    view = {"features": features, "H1": None, "H2": None}
    neg = est.negativo_ricci_billar(Path(base), motor, {"candidates": []}, view, case_id)
    if neg.get("status") != "EJECUTADO":
        return "NO_CORRE", neg.get("status"), None, neg
    filas = (neg.get("detalle_comparador") or {}).get("filas") or []
    por = {}
    for f in filas:
        s = f.get("senal_descarte") or "LATENTE"
        base_s = s.replace("_BAJO_NULO", "")
        sc = 0.5 if s.endswith("_BAJO_NULO") else SCORE_NEGATIVO.get(base_s, 0.5)
        por[f["familia"]] = sc
    for c in _candidatos(motor):
        por.setdefault(c, 0.5)
    voto = {"lens": "negativo_ricci_vs_billar_v0_1", "Alimenta_H": "NO", "writes_H": False, "can_decide_H": False,
            "regla_score": "SE_SOSTIENE 1.0 · TENSION_LATENTE 0.5 · DESCARTE_DEBIL_LATENTE 0.25 · DESCARTE 0.0 · SIN_RICCI/_BAJO_NULO/sin dato 0.5 (latente, no se promueve)",
            "por_familia": {f: {"score": round(v, 4)} for f, v in sorted(por.items())}}
    cuad = {}
    for f in filas: cuad[f["cuadrante"]] = cuad.get(f["cuadrante"], 0) + 1
    aporte = f"{len(filas)} familias leídas; cuadrantes {cuad}; lentes bajo nulo: {neg.get('lentes_sin_senal_vs_nulo')}"
    return "ACTIVA", aporte, voto, {k: neg.get(k) for k in ("z_billar_v0_2", "z_ricci_media", "lentes_sin_senal_vs_nulo", "resumen_pares", "consistencia_embebida_vs_standalone", "piezas")} | {"filas": filas}


def _cargar_puente(base, tiers=("alta", "media")):
    P = json.loads((Path(base) / "PUENTE_244_FAMILIAS.json").read_text(encoding="utf-8"))
    toks = []
    for t in P["tokens"]:
        w = set()
        for tier in tiers: w |= set(t["palabras_244"][tier])
        toks.append({"familia": t["familia"], "token": t["token"], "D": t["dinamica"], "E": t["escala"], "pol": t["polaridad"], "words": w})
    return toks


def voto_familias_tokens(base, case, motor, patterns):
    """EXPERIMENTAL. UN solo voto por candidato: nº de tokens laterales (11 familias, puente alta+media) encendidos
    por palabras del patrón PROPIO del candidato que aparecen en los 3 últimos cortes (lente del README de equivalencias §4)."""
    toks = _cargar_puente(base)
    fam_dir = Path(base) / "familias_tokens"
    fams_norm = {}
    for f in sorted(fam_dir.glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        fams_norm[d.get("id", f.stem)] = {"sha256": _sha(f), "n_favor": len(d.get("tokens_favor") or {}), "n_contra": len(d.get("tokens_contra") or {}),
                                         "tokens": set(d.get("tokens_favor") or {}) | set(d.get("tokens_contra") or {})}
    puente_tok = {t["token"] for t in toks}
    cobertura = {k: {"sha256": v["sha256"][:16], "tokens": len(v["tokens"]), "en_puente": len(v["tokens"] & puente_tok)} for k, v in fams_norm.items()}
    cuts = case.get("cuts") or []
    recent = set()
    for c in cuts[-3:]: recent |= set(_tok(c))
    por, detalle = {}, {}
    for cand in _candidatos(motor):
        pv = patterns.get(cand, {}) if isinstance(patterns, dict) else {}
        own = set(pv.get("tokens_favor") or {}) | set(pv.get("tokens_contra") or {})
        lit = [t for t in toks if t["words"] & own & recent]
        por[cand] = len(lit)
        if lit:
            detalle[cand] = {"n": len(lit), "empuja": sum(1 for t in lit if t["pol"] == "empuja"), "frena": sum(1 for t in lit if t["pol"] == "frena"),
                             "familias": sorted({t["familia"] for t in lit})}
    vals = list(por.values())
    constante = (max(vals) - min(vals)) == 0 if vals else True
    voto = {"lens": "familias_tokens_puente_v1_EXPERIMENTAL", "EXPERIMENTAL": True, "Alimenta_H": "NO", "writes_H": False, "can_decide_H": False,
            "un_voto_por_candidato": True, "por_familia": {f: {"score": float(v)} for f, v in sorted(por.items())}}
    # matriz de escalas y coactivación por corte (coactivacion_escalas.analizar_corte tal cual)
    co, _ = _load(base, "coactivacion_escalas.py", "lu_coact")
    DS = ["D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8"]
    matriz = {D: {"micro": 0, "meso": 0, "macro": 0} for D in DS + ["K0"]}
    coact = []
    for c in cuts:
        obs = {}
        for e in ("P", "A", "C"):
            for t, w in c.get(e) or []:
                obs[str(t)] = max(obs.get(str(t), 0.0), float(w))
        r = co.analizar_corte(obs, toks)
        for D in DS + ["K0"]:
            for E in r[D]["escalas_encendidas"]:
                matriz[D][E] += 1
            if r[D]["estado"].startswith("coactivacion"):
                coact.append({"corte": c.get("id"), "dinamica": D, "escalas": r[D]["escalas_encendidas"], "tipo": r[D]["estado"],
                              "palabras": sorted({w for E in r[D]["detalle"].values() for w in E["palabras_empuja"]})})
    info = {"EXPERIMENTAL": True, "familias_normalizadas": cobertura, "n_familias": len(fams_norm),
            "candidatos_con_senal": len(detalle), "voto_constante_en_este_caso": constante,
            "nota_constante": "si el voto es constante, la guardia de dimensiones del puente lo saca (no discrimina)",
            "detalle_por_candidato_top": dict(sorted(detalle.items(), key=lambda kv: -kv[1]["n"])[:12]),
            "matriz_escalas_cortes_encendidos": matriz,
            "coactivacion": {"n_independiente": sum(1 for x in coact if x["tipo"] == "coactivacion_independiente"),
                             "n_trivial": sum(1 for x in coact if x["tipo"] == "coactivacion_trivial"), "eventos": coact,
                             "nota": "sin nulo por corrida (el nulo de 2000 permutaciones es de EQUIVALENCIAS_ESCALA: p=0.45/0.76, no supera al azar)"}}
    aporte = f"EXPERIMENTAL; {len(detalle)} candidatos con señal; voto {'CONSTANTE (sale por guardia)' if constante else 'varía'}; coactivación indep {info['coactivacion']['n_independiente']}, trivial {info['coactivacion']['n_trivial']}"
    return ("ACTIVA" if not constante else "ACTIVA_MUDA"), aporte, voto, info


# ======================================================================= SENSORES pre-predictor
def sensores_pre(base, case, motor, features, reg, ctx=None):
    out = {}
    ctx = ctx or {}
    cuts = case.get("cuts") or []
    mcuts = motor.get("cuts") or []
    textos = _textos(case)
    hechos = " ".join(t["texto"] for t in textos)
    pinchos = {str(c.get("id")): _tok(c) for c in cuts}
    last_P = dict((mcuts[-1].get("P_FULL_244") or {})) if mcuts else {}

    def memento():
        m, _ = _load(base, "sidecar_corte_memento.py", "lu_memento")
        cin = [{"id": c.get("id"), "P": c.get("P") or [], "A": c.get("A") or [], "C": c.get("C") or []} for c in cuts]
        r = m.corte_memento(last_P, cuts=cin, r732=motor.get("R732"))
        proto = r.get("proto_hipotesis") or {}
        cad = r.get("cadena_atras") or {}
        return "ACTIVA", f"proto-H {proto.get('proto_H') or proto.get('familia') or proto.get('nucleo_tokens')}; se sostiene: {cad.get('se_sostiene', cad.get('veredicto'))}", {
            "proto_hipotesis": proto, "cadena_atras": cad, "hombre_de_acero": r.get("hombre_de_acero"), "candados": r.get("candados")}
    out["memento"] = _pieza("memento", "sidecar_corte_memento.py", "SENSOR Bus Capa 2 (PRE, antes de H)", memento, base, reg)

    def matriz_ctrl():
        m, _ = _load(base, "matriz_corrida.py", "lu_matriz")
        r = m.correr_matriz(pinchos, hechos_extra=[t["texto"] for t in textos], texto_polaridad=case.get("texto_polaridad") or hechos[:2000], clave=f"unico::{case.get('case_id')}")
        return "ACTIVA", f"claves: {sorted(r)[:8]}", _compacto(r)
    out["matriz_corrida_control"] = _pieza("matriz_corrida", "matriz_corrida.py", "CONTROL checkpoint 20 (kernel+flujo+latencia+capa2)", matriz_ctrl, base, reg)

    def luces():
        m, _ = _load(base, "sidecar_luces_gemini_packs.py", "lu_luces")
        r = m.leer(pinchos, registro_path=str(Path(base) / "registro_luces_gemini_packs.json"), hechos_extra=[t["texto"] for t in textos])
        act = r.get("activos") or r.get("luces") or r.get("ids_activos")
        return ("ACTIVA" if act else "ACTIVA_MUDA"), f"luces activas: {len(act) if act else 0}", _compacto(r)
    out["luces_gemini_packs"] = _pieza("luces_gemini_packs", "sidecar_luces_gemini_packs.py", "SENSOR (bus Capa 2)", luces, base, reg)

    def amantes():
        m, _ = _load(base, "sidecar_amantes_arquetipos.py", "lu_amantes")
        r = m.leer(pinchos, hechos=[t["texto"] for t in textos], registro_path=str(Path(base) / "registro_sidecar_amantes_arquetipos.json"))
        g = r.get("gatillo") if isinstance(r, dict) else None
        return ("ACTIVA" if g else "ACTIVA_MUDA"), f"gatillo: {g}", _compacto(r)
    out["amantes_arquetipos"] = _pieza("amantes_arquetipos", "sidecar_amantes_arquetipos.py", "SENSOR (bus Capa 2, solo con gatillo)", amantes, base, reg)

    geo_traza = {}
    geo_full = {}

    def marco_geometria():
        # PATCH 009 (decisión Mj 2026-10-06): marco_7783 = parte GEOMÉTRICA de la trazabilidad.
        # Puente por corte: seis funciones Souriau (marco_funciones_souriau.distribuir -> marco_7783.zona_de, puro)
        # + cuadrante Caldero II (features.plugin_circulo_monomito, ya calculado por UNICO) + Polti activas
        # (features.polti_caldero, ya calculado por UNICO) + anillos (fase/ω/intersecciones) leídos por billar v0_2.
        # NO llama marco_7783.visitar (no escribe zonas_7783.json); calor en memoria por caso. can_decide_H=False.
        mk, _ = _load(base, "marco_7783.py", "lu_marco_7783")
        mf, _ = _load(base, "marco_funciones_souriau.py", "lu_marco_fn_geo")
        pz, _ = _load(base, "puente_souriau_caldero_polti_v1.py", "lu_puente_scp")
        if mk is None or mf is None or pz is None:
            return "NO_CORRE", "falta marco_7783.py / marco_funciones_souriau.py / puente_souriau_caldero_polti_v1.py", None
        # Guardia de store: zonas_7783.json heredado en el directorio del run (copiado desde motor/) contaminaría el
        # calor de UNICO (marco_7783.visitar, que corre DESPUÉS del hub). Si el run está bajo runs/, se aparta (solo en la copia del run).
        guard = {"store_path": str(Path(base) / "zonas_7783.json"), "heredado": False, "accion": "ninguna"}
        st = Path(base) / "zonas_7783.json"
        if st.is_file():
            guard.update({"heredado": True, "sha256_heredado": _sha(st)})
            if Path(base).resolve().parent.name == "runs":
                dest = Path(base) / "zonas_7783.HEREDADO_PRE_RUN.json"
                st.replace(dest); guard["accion"] = f"apartado a {dest.name} (store por run)"
            else:
                guard["accion"] = "solo bandera: run fuera de runs/ (no se toca el store del pack)"
        dist = mf.distribuir(cuts)
        mono = (features or {}).get("plugin_circulo_monomito") or {}
        pol = (features or {}).get("polti_caldero") or {}
        r = pz.construir(dist, mk, mono, pol)
        b1, _ = _load(base, "billar_circular_convergencia_v0_1.py", "lu_billar1_geo")
        tau = float(getattr(b1, "TAU", 0.35)) if b1 is not None else 0.35
        r["anillos"] = pz.anillos(r, tau)
        b2, _ = _load(base, "billar_circular_convergencia_v0_2.py", "lu_billar2_geo")
        if b2 is not None and hasattr(b2, "convergencias_v2"):
            ev, diag = b2.convergencias_v2(pz.tray_para_billar(r["anillos"]), [c["corte"] for c in r["por_corte"]], tau)
            r["billar_v0_2_sobre_anillos"] = {"lector": "billar_circular_convergencia_v0_2.convergencias_v2 (sin editar; adaptador de trayectorias en el hub)",
                                              "n_convergencias": len(ev), "diag": diag,
                                              "convergencias": [{"corte": e["corte"], "anillos": e["familias"], "distancia": e["distancia"]} for e in ev]}
        cp, _ = _load(base, "zri_coupling_v0_2.py", "lu_zri2_geo")
        r["anillos"]["helice"] = pz.helice(r["anillos"], cp, str(case.get("case_id")))
        geo_full.update({"helice": r["anillos"]["helice"]})
        r["store_guard"] = guard
        r["fuentes"] = {"funciones": "marco_funciones_souriau.distribuir(cuts) modo=" + str(dist.get("modo")), "zona": "marco_7783.zona_de",
                        "cuadrante": "features.plugin_circulo_monomito" if mono else None, "polti": "features.polti_caldero" if pol else None}
        r["destinos"] = ["laterales_unico.sensores_pre.marco_7783_geometria (detalle)",
                         "laterales_unico.sensores_pre.trazabilidad_temporal.capa_geometrica_souriau_caldero_polti (aditivo)",
                         "laterales_unico.sensores_pre.schrodinger.anillos_para_transporte (contexto; costo/Sinkhorn NotImplemented)",
                         "laterales_unico.sensores_pre.zri.anillos_helice_zri (Z-RI v0.2 couple_at_cut sobre anillos)",
                         "laterales_unico.sensores_pre.tusi.anillos_tusi (fórmula Tusi sobre ω de anillos)"]
        geo_traza.update(pz.compacto_para_traza(r))
        rs = r["resumen"]; an = r["anillos"]
        vivo = rs["n_cortes"] and (rs["n_transiciones_zona"] or an["n_intersecciones"] or rs["cortes_con_cuadrante"] or rs["cortes_con_polti"])
        motivo = (f"PATCH009: zonas {rs['zonas_visitadas']} ({rs['n_transiciones_zona']} transiciones, {rs['n_revisitas_zona']} revisitas); "
                  f"discrepancia media {rs['discrepancia_media']}; cúmulos {rs['cumulos_total']}; cuadrante en {rs['cortes_con_cuadrante']}/{rs['n_cortes']}; "
                  f"Polti en {rs['cortes_con_polti']}/{rs['n_cortes']}; intersecciones de anillos {an['n_intersecciones']} en {an['iteraciones_con_interseccion']}; "
                  f"mapeo seis funciones->7783 PENDIENTE regla Mj (solo 729 alcanzables)")
        if not vivo:
            motivo = "PATCH009: sin variación de zona, sin cuadrante/Polti y sin intersecciones en este caso; " + motivo
        return ("ACTIVA" if vivo else "ACTIVA_MUDA"), motivo, r
    out["marco_7783_geometria"] = _pieza("marco_7783_geometria", "puente_souriau_caldero_polti_v1.py",
                                         "LATERAL GEOMÉTRICO de trazabilidad (marco_7783 + Caldero Q1-Q4 + Polti; no escribe H)", marco_geometria, base, reg,
                                         alimenta=["trazabilidad_temporal (aditivo)", "billar_v0_2 sobre anillos (hub)", "zri_v0_2 (hélice)", "tusi (ω anillos)", "schrodinger (contexto)"],
                                         entra_al_ranking=False)

    def traz():
        m, _ = _load(base, "sidecar_trazabilidad_temporal.py", "lu_traz")
        cin = [{"id": c.get("id"), "P": c.get("P") or [], "A": c.get("A") or [], "C": c.get("C") or []} for c in cuts]
        # PATCH 009: la capa geométrica (marco_7783_geometria) entra como campo aditivo; sin ella, salida idéntica.
        r = m.analizar_temporal(cin, geometria=dict(geo_traza)) if geo_traza else m.analizar_temporal(cin)
        ce = r.get("conteo_estados") or {}
        n = len(r.get("tokens") or [])
        rc = _compacto(r)
        if r.get("capa_geometrica_souriau_caldero_polti"):
            rc["capa_geometrica_souriau_caldero_polti"] = r["capa_geometrica_souriau_caldero_polti"]  # sin truncar
        return ("ACTIVA" if n else "ACTIVA_MUDA"), f"PATCH004 lee P/A/C: {n} tokens trazados; estados {ce}" + ("; PATCH009 capa geométrica Souriau/Caldero/Polti adjunta" if geo_traza else ""), rc
    out["trazabilidad_temporal"] = _pieza("trazabilidad_temporal", "sidecar_trazabilidad_temporal.py", "SENSOR", traz, base, reg)

    def integ():
        m, _ = _load(base, "capa_integracion_semantica_v1_2.py", "lu_integ")
        capas = []
        for c in cuts:
            capas.append({"id": c.get("id"), "capas": {e: [t for t, _ in (c.get(e) or [])] for e in ("P", "A", "C")}})
        r = m.integrar(capas)
        return "ACTIVA", f"{len(r.get('configuraciones') or r.get('cortes') or [])} configuraciones", _compacto(r)
    out["integracion_semantica"] = _pieza("integracion_semantica", "capa_integracion_semantica_v1_2.py", "SENSOR", integ, base, reg)

    def interrel():
        m, _ = _load(base, "capa_interrelacion_tokens.py", "lu_interrel")
        cs = []
        for i, c in enumerate(mcuts):
            act = [{"familia": f, "peso": float(p)} for f, p in (c.get("P_top5_ANEXO") or [])]
            ctx = [{"token": t, "peso": float(w)} for e in ("P", "A", "C") for t, w in (cuts[i].get(e) or [])] if i < len(cuts) else []
            cs.append({"id": c.get("corte"), "activaciones": act, "context_tokens": ctx})
        r = m.analizar_cortes(cs)
        return "ACTIVA", "relación por corte entre familias activas (top5 P) y contexto", _compacto(r)
    out["interrelacion_tokens"] = _pieza("interrelacion_tokens", "capa_interrelacion_tokens.py", "SENSOR", interrel, base, reg)

    def cuerpo():
        # PATCH 010a-4: el sidecar lee SOLO cut["tokens"]; antes se le pasaban P/A/C sin "tokens" -> salida constante
        # (VACIO falta_enfermedad_o_herida en 5/5). Ahora recibe tokens cuerpo_* del área de tokens: P/A/C exactos +
        # canal texto_raiz sobre textos ADMITIDOS por el sombrero de entrada (hecho/narracion, nunca source_note).
        m, _ = _load(base, "sidecar_cuerpo_arco__BUG_A_SIN_CONFIRMAR.py", "lu_cuerpo")
        cc = (ctx.get("area") or {}).get("cuerpo_cuts")
        if cc is None:
            return "ACTIVA_MUDA", "área de tokens no disponible: sin tokens cuerpo_* que pasar", None
        r = m.analizar_cuerpo(cc)
        cad = dict(r.get("cadena") or {})
        if cad.get("estado") == "HIT":
            cad["estado"] = "CADENA_COMPLETA"  # etiqueta del módulo traducida (regla Mj: sin vocabulario HIT/MISS)
        r["cadena"] = cad
        con = [c for c in cc if c["tokens"]]
        if not con:
            return "ACTIVA_MUDA", "sin tokens de cuerpo/salud en P/A/C ni en textos admitidos (ninguna enfermedad/herida/agonía/muerte en el input)", {
                "cuerpo_cuts": cc, "cadena": cad}
        return "ACTIVA", (f"tokens cuerpo en {[(c['id'], c['tokens']) for c in con]}; cadena={cad.get('estado')} {cad.get('motivo') or ''}; "
                          f"caldero_cuerpo={[(v['corte_muerte'], v['voto']) for v in (r.get('caldero') or {}).get('votos') or []]}; "
                          f"h1_prohibido={r.get('h1_prohibido')}"), {"cuerpo_cuts": cc, "salida": _compacto(r),
                          "citas": [{"corte": x["corte"], "token": a["token"], "canal": a["canal"], "cita": a.get("cita")} for x in (ctx.get("area") or {}).get("por_corte") or []
                                    for a in x.get("activaciones") or [] if a.get("familia") == "cuerpo_arco"]}
    out["cuerpo_arco"] = _pieza("cuerpo_arco", "sidecar_cuerpo_arco__BUG_A_SIN_CONFIRMAR.py", "FAMILIA DE TOKENS cuerpo/muerte (área de tokens; EXPERIMENTAL)", cuerpo, base, reg,
                                feeds_predictor=False)

    def alias():
        m, _ = _load(base, "plugin_alias_reactivacion.py", "lu_alias")
        prop = {}
        for c in cuts:
            for e in ("P", "A", "C"):
                orig = [(t, float(w)) for t, w in (c.get(e) or [])]
                tr = m.traducir(orig, hechos=str(c.get("source_note") or ""))
                if len(tr) > len(orig): prop[f"{c.get('id')}:{e}"] = tr[len(orig):]
        fl = m.faltaron(hechos, last_P)
        return ("ACTIVA" if (prop or fl) else "ACTIVA_MUDA"), f"alias propuestos {len(prop)}; faltaron {fl}", {"alias_propuestos_no_aplicados": prop, "faltaron": fl,
                "nota": "propuestas sobre copia; NO se aplican al input (cambiar el input es decisión de Mj)"}
    out["alias_reactivacion"] = _pieza("alias_reactivacion", "plugin_alias_reactivacion.py", "SENSOR (dry-run sobre el input)", alias, base, reg)

    def fix():
        m, _ = _load(base, "plugin_fix_entrada.py", "lu_fix")
        cortes = [(str(c.get("id")), [(t, float(w)) for e in ("P", "A", "C") for t, w in (c.get(e) or [])], str(c.get("source_note") or "")) for c in cuts]
        r = m.preparar_caso(copy.deepcopy(cortes))
        return "ACTIVA", "remapeo propuesto (no aplicado)", {"propuesta_no_aplicada": _compacto(r)}
    out["fix_entrada"] = _pieza("fix_entrada", "plugin_fix_entrada.py", "SENSOR (dry-run; no cambia el input)", fix, base, reg)

    def gloria():
        m, _ = _load(base, "plugin_familias_gloria_sacro.py", "lu_gloria")
        extra = getattr(m, "EXTRA", {})
        obs = set(t for c in cuts for t in _tok(c))
        hits = {k: sorted(set((v.get("tokens_favor") or {})) & obs) for k, v in extra.items()}
        return "ACTIVA_MUDA", "familias fuera del catálogo cargado (fusionar() escribiría patterns: prohibido); solo se reportan tokens observados", {"familias": list(extra), "tokens_observados_por_familia": hits}
    out["familias_gloria_sacro"] = _pieza("familias_gloria_sacro", "plugin_familias_gloria_sacro.py", "SENSOR sin mapeo al catálogo", gloria, base, reg)

    def _funciones_souriau_derivadas():
        # PATCH 007: extractor de las seis funciones YA presente en el pack (marco_funciones_souriau.distribuir,
        # deriva león/marte/sol/tierra/balanza/luna de los tokens P/A/C). Antes la lente y v1_4 no lo recibían.
        mf, _ = _load(base, "marco_funciones_souriau.py", "lu_marco_fn")
        return mf.distribuir(cuts) if mf is not None and hasattr(mf, "distribuir") else None

    def souriau():
        m, _ = _load(base, "sidecar_lente_souriau.py", "lu_souriau")
        seq = [" ".join(_tok(c)) for c in cuts]
        dist = _funciones_souriau_derivadas()
        if dist:
            # PATCH 007: la lente es agnóstica y exige un mapping con los focos ya extraídos (no un string).
            maps = [{f: {"valor": (pc.get("funciones") or {}).get(f) or None, "evidencia": "marco_funciones_souriau.distribuir" + (" (personajes_016)" if dist.get("modo") == "personajes_016" else "")}
                     for f in ("sol", "tierra", "balanza", "luna")} for pc in dist.get("por_corte") or []]
            focos = [m.asignar_focos_por_corte(maps[i], seq, corte_actual=i) for i in range(len(maps))]
        else:
            focos = [m.asignar_focos_por_corte(seq[i], seq, corte_actual=i) for i in range(len(seq))]
        vivos = sum(1 for f in focos for v in f.values() if isinstance(v, dict) and v.get("valor"))
        return ("ACTIVA" if vivos else "ACTIVA_MUDA"), f"focos con valor: {vivos}", {"focos_por_corte": focos[-3:]}
    out["lente_souriau"] = _pieza("lente_souriau", "sidecar_lente_souriau.py", "SENSOR", souriau, base, reg)

    def souriau14():
        m, _ = _load(base, "plugin_souriau_210141.py", "lu_souriau14")
        # PATCH 007: antes gate fijo NO_CORRE sin intentar. Las funciones NO se piden en el input: se derivan de
        # los tokens con marco_funciones_souriau (pieza del pack) y v1_4 emite las relaciones entre las seis
        # funciones (co_presence + group_membership = un mismo token ocupando varias funciones).
        dist = _funciones_souriau_derivadas()
        if not dist:
            return "NO_CORRE", "marco_funciones_souriau.py ausente: sin extractor de funciones", None
        recs = []
        for i, pc in enumerate(dist.get("por_corte") or []):
            fx = pc.get("funciones") or {}
            _ev016 = "derivado_personajes_corte_016:marco_funciones_souriau" if dist.get("modo") == "personajes_016" else "derivado_tokens_PAC:marco_funciones_souriau"
            funcs = {f: ({"valor": list(fx.get(f)), "estado": "observado", "evidencia": _ev016, "corte": i}
                         if fx.get(f) else {"estado": "no_observado", "corte": i}) for f in m.FUNCTIONS}
            grupos = [sorted(set(fns)) for _t, fns in sorted((pc.get("cumulo") or {}).items())]
            recs.append({"case_id": f"{case.get('case_id')}:{pc.get('corte')}", "corte": i, "funciones": funcs, "agrupacion": grupos,
                         "source": "derivado_personajes_corte_016" if dist.get("modo") == "personajes_016" else "derivado_tokens_PAC", "evidence_status": "derivado_no_declarado"})
        ing = m.ingest(recs, expected_count=None, corte_actual=len(recs) - 1 if recs else None)
        em = m.emit_for_integration(ing)
        pares = {}
        for r in em.get("relations") or []:
            if r.get("type") == "co_presence":
                k = f"{r['a']}~{r['b']}"; pares[k] = pares.get(k, 0) + 1
        configs = sorted({"".join("1" if (u["payload"]["funciones"][j]["estado"] == "observado") else "0" for j in range(6)) for u in em.get("units") or []})
        return ("ACTIVA" if em.get("relations") else "ACTIVA_MUDA"), \
            f"PATCH007: {len(em.get('units') or [])} situaciones por corte, {len(em.get('relations') or [])} relaciones entre funciones; funciones DERIVADAS (no declaradas)", \
            {"relaciones_co_presencia_por_par": pares, "configuraciones_6_funciones": configs, "n_units": len(em.get("units") or []),
             "temporal_cut": em.get("temporal_cut"), "decision_layer": em.get("decision_layer"),
             "advertencia_spec_v1_4": ("PATCH 016: funciones derivadas de personajes por corte (ids de rol neutros; León = protagonista/faceta, no P). 3783 NO implementado: ver RASTREO_PIEZAS_ZIPS_VIEJOS_20261006.md"
                                       if dist.get("modo") == "personajes_016" else
                                       "el SPEC v1.4 §3 prohíbe León==P; marco_funciones_souriau usa leon=P[:5], marte=A[:5] (heurística del pack, no declarada). 3783 NO implementado: ver RASTREO_PIEZAS_ZIPS_VIEJOS_20261006.md"),
             "modo_funciones_016": dist.get("modo"),
             "can_decide_H": False}
    out["souriau_v1_4"] = _pieza("souriau_v1_4", "plugin_souriau_210141.py", "MARCAJE", souriau14, base, reg)
    # PATCH 009 — decisión Mj 2026-10-06: la aritmética Souriau 210141 (= 7783·27) es MARCAJE, no trazabilidad.
    # Sigue corriendo (no se quitan piezas en silencio), pero no aporta nada a fusión/predictor/peso de traza.
    if reg and reg[-1].get("pieza") == "souriau_v1_4":
        _r = reg[-1]
        _r["estado_ejecucion"] = _r.get("estado")
        if _r.get("estado") in ("ACTIVA", "ACTIVA_MUDA"):
            _r["estado"] = "MARCAJE"
        _r.update({"rol": "MARCAJE (marcador; no trazabilidad)", "marcaje": True, "aporta_a_fusion": False, "aporta_a_predictor": False,
                   "peso_traza": 0.0, "motivo_marcaje": "decisión Mj 2026-10-06: aritmética Souriau 210141 = marcaje, no trazabilidad"})
        _r["aporte"] = "MARCAJE — decisión Mj 2026-10-06: aritmética Souriau 210141 = marcaje, no trazabilidad | " + str(_r.get("aporte"))
    if isinstance(out.get("souriau_v1_4"), dict):
        out["souriau_v1_4"]["marcaje"] = {"es_marcaje": True, "aporta_a_fusion": False, "aporta_a_predictor": False, "peso_traza": 0.0,
                                          "motivo": "decisión Mj 2026-10-06: aritmética Souriau 210141 = marcaje, no trazabilidad"}

    def zri():
        e, _ = _load(base, "zri_experience_v0_1.py", "lu_zri1")
        cp, _ = _load(base, "zri_coupling_v0_2.py", "lu_zri2")
        names = sorted((mcuts[0].get("P_FULL_244") or {}).keys()) if mcuts else []
        seals, per_cut = [], []
        run_hash = hashlib.sha256(json.dumps([c.get("corte") for c in mcuts]).encode()).hexdigest()[:16]
        for c in mcuts:
            ih = hashlib.sha256(json.dumps({k: c.get(k) for k in ("corte", "n_tokens")}, sort_keys=True).encode()).hexdigest()[:16]
            top5 = tuple(x[0] for x in (c.get("P_top5_ANEXO") or [])[:5])
            if len(top5) == 5:
                s = e.CutSeal(str(case.get("case_id")), c["corte"], ih, top5, top5[0], run_hash); s.assert_valid()
                seals.append({"corte": c["corte"], "H_top1": top5[0]})
            pts = [cp.TracePoint(str(case.get("case_id")), c["corte"], ax, ih, run_hash, tuple(float((c.get(f"{ax}_FULL_244") or {}).get(n, 0.5)) - 0.5 for n in names)) for ax in "PAC"]
            per_cut.append(cp.convergence_summary(cp.couple_at_cut(str(case.get("case_id")), c["corte"], pts)))
        sal = {"v0_1_sellos": seals, "v0_2_por_corte": per_cut}
        if geo_full.get("helice"):
            # PATCH 009: aditivo — Z-RI v0.2 acopla los anillos (Caldero/Polti/Souriau) como capas 3D (hélice) por corte.
            sal["anillos_helice_zri"] = geo_full["helice"].get("zri_acople")
        return "ACTIVA", f"v0.1: {len(seals)} sellos; v0.2: acople P/A/C en {len(per_cut)} cortes; E_n no se calcula (no hay resultado liberado)" + ("; PATCH009 + acople de anillos" if geo_full.get("helice") else ""), sal
    out["zri"] = _pieza("zri_v0_1_v0_2", "zri_coupling_v0_2.py", "SENSOR (Z-RI v0.1 sellos + v0.2 acople)", zri, base, reg)

    def tusi():
        b1, _ = _load(base, "billar_circular_convergencia_v0_1.py", "lu_billar1")
        ids, series = b1.extraer_series_p(copy.deepcopy(mcuts))
        def dps(s): return [None if (a is None or b is None) else (b - a) for a, b in zip(s, s[1:])]
        def tu(da, db):
            pares = [(x, y) for x, y in zip(da, db) if x is not None and y is not None and (x != 0 or y != 0)]
            if len(pares) < 2: return None, len(pares)
            num = abs(sum(2 * math.pi * (x + y) for x, y in pares)); den = sum(2 * math.pi * (abs(x) + abs(y)) for x, y in pares)
            return (1 - num / den if den else None), len(pares)
        D = {f: dps(series[f]) for f in series}; fams = sorted(series); rng = random.Random(20260921); filas = []
        for i, a in enumerate(fams):
            for b in fams[i + 1:]:
                t, n = tu(D[a], D[b])
                if t is None: continue
                nul = []
                for _ in range(200):
                    db = D[b][:]; rng.shuffle(db); tn, _n = tu(D[a], db)
                    if tn is not None: nul.append(tn)
                mu = sum(nul) / len(nul) if nul else None
                sd = (sum((x - mu) ** 2 for x in nul) / len(nul)) ** 0.5 if nul else None
                filas.append({"par": [a, b], "tusi": round(t, 4), "n_pasos_vivos": n, "z_vs_nulo": None if not sd else round((t - mu) / sd, 3)})
        filas.sort(key=lambda r: -r["tusi"])
        sal = {"top_pares": filas[:10], "nota": "fórmula replicada de tusi_par_indice_exploratorio_v0_1.py (ese script lee argv al importarse)"}
        if geo_full.get("helice"):
            # PATCH 009: aditivo — misma fórmula sobre las ω de los anillos (no cambia top_pares de familias).
            sal["anillos_tusi"] = geo_full["helice"].get("tusi_anillos")
        return ("ACTIVA" if filas else "ACTIVA_MUDA"), f"{len(filas)} pares con índice de Tusi", sal
    out["tusi"] = _pieza("tusi_par", "tusi_par_indice_exploratorio_v0_1.py", "SENSOR EXPLORATORIO", tusi, base, reg)

    def schro():
        m, _ = _load(base, "schrodinger_transport_esqueleto_v0_1.py", "lu_schro")
        mus = []
        for c in mcuts:
            K = m.candidatos(c, None, [])
            mu = m.mu_t(c, K); top = sorted(mu.items(), key=lambda kv: -kv[1])[:3]
            mus.append({"corte": c.get("corte"), "n_soporte": len(K), "mu_top3": [(k, round(v, 4)) for k, v in top]})
        sal = {"salida": m.salida_vacia(str(case.get("case_id"))), "mu_t": mus}
        if geo_traza.get("anillos"):
            # PATCH 009: contexto aditivo (fases/ω/intersecciones por corte). NO consumido: costo() y sinkhorn() son NotImplemented.
            sal["anillos_para_transporte"] = {"por_corte": geo_traza["anillos"].get("por_corte"), "consumido": False,
                                              "motivo": "schrodinger_transport_esqueleto_v0_1: costo/sinkhorn NotImplemented (pendiente Mj SPEC §5)"}
        return "ACTIVA_MUDA", "esqueleto: μ_t por corte calculado; costo y Sinkhorn NO_VERIFICADO (NotImplemented por diseño)", sal
    out["schrodinger"] = _pieza("schrodinger_transport", "schrodinger_transport_esqueleto_v0_1.py", "SENSOR (esqueleto)", schro, base, reg)

    def caldero_cuadrantes():
        # PATCH 006: Caldero II sin escaleta lineal externa = cuadrantes circulares Q1-Q4 (plugin_circulo_monomito_v2,
        # ya ejecutado por UNICO antes del hub; aquí solo se registra su salida real). caldero_run.py = SUPERADA.
        mono = (features or {}).get("plugin_circulo_monomito") or {}
        filas = mono.get("posicion_monomito_por_corte") or []
        if not filas:
            return "ACTIVA_MUDA", "circulo_monomito_v2 sin salida en este run", None
        qs = [{"corte": f.get("corte"), "cuadrante_activo": f.get("cuadrante_activo"), "huecos": sorted(f.get("huecos") or []), "r4_nuevo_ciclo": f.get("r4_nuevo_ciclo")} for f in filas]
        vivos = sum(1 for q in qs if q["cuadrante_activo"])
        return ("ACTIVA" if vivos else "ACTIVA_MUDA"), f"Q1-Q4 derivados de tokens del corte: {vivos}/{len(qs)} cortes con cuadrante; puente Caldero={bool((mono.get('caldero_bridge') or {}).get('current_neighbors'))}", \
            {"cuadrantes_por_corte": qs, "linea_mas_avanzada_actual": mono.get("linea_mas_avanzada_actual"), "caldero_bridge": mono.get("caldero_bridge"),
             "falta": "apuesta t+1 de MOVIMIENTO de cuadrante (HIT/MISS Q→Q) no implementada en ningún archivo en disco"}
    out["caldero_ii_cuadrantes"] = _pieza("caldero_ii_cuadrantes", "plugin_circulo_monomito_v2.py", "SENSOR (Caldero II circular; sustituye escaleta)", caldero_cuadrantes, base, reg)
    reg.append({"pieza": "caldero_run.py", "archivo": "caldero_run.py", "sha256": None, "rol": "Caldero II escaleta lineal (histórico)", "estado": "SUPERADA",
                "aporte": "PATCH 006: escaleta lineal sustituida por cuadrantes circulares (caldero_ii_cuadrantes / plugin_circulo_monomito_v2)", "can_decide_H": False,
                "nota_U6": "registro histórico, no se carga. MAPA_NOMBRES dice caldero_run.py = caldero_II_runner_generico.py (runner CLI canónico, existe en motor/); este registro lo trata como la escaleta lineal SUPERADA. Discrepancia documentada, no resuelta aquí"})

    def vecinos_pref():
        m, _ = _load(base, "predictor_vecinos_prefijo_v1.py", "lu_vecpref")
        # PATCH 005: el corpus (15 biografías) va dentro del predictor; falta solo el prefijo del caso.
        # Se intenta con el input real; sin inferir etapas desde cuadrantes ni sinónimos.
        voc = {str(x).casefold(): x for seq in getattr(m, "BIOGRAFIAS", {}).values() for x in seq}
        pref, det = [], []
        for i, c in enumerate(cuts):
            exp = next((c.get(k) for k in ("estado_monomito", "monomito", "etapa_monomito", "stage") if c.get(k)), None)
            if exp is not None and str(exp).casefold() in voc:
                pref.append(voc[str(exp).casefold()]); det.append({"corte": c.get("id"), "estado": pref[-1], "fuente": "clave_explicita"}); continue
            hits = sorted({voc[t.strip().casefold()] for t in _tok(c) if t.strip().casefold() in voc})
            if len(hits) == 1:
                pref.append(hits[0]); det.append({"corte": c.get("id"), "estado": hits[0], "fuente": "token_exacto_PAC"}); continue
            det.append({"corte": c.get("id"), "estado": None, "fuente": "ambiguo" if hits else "sin_estado", "candidatos": hits}); break
        if not pref:
            return "ACTIVA_MUDA", "PATCH005 intentado: ningún corte inicial trae estado monomítico exacto (sin prefijo; no se rellena)", {"prefijo_detalle": det}
        r = m.predict_next(pref, top_n=5)
        return "ACTIVA", f"prefijo k={len(pref)}: voto t+1 lateral (no probabilidad poblacional)", {"prefijo": pref, "prefijo_detalle": det, "resultado": _compacto(r)}
    out["predictor_vecinos_prefijo"] = _pieza("predictor_vecinos_prefijo", "predictor_vecinos_prefijo_v1.py", "SENSOR", vecinos_pref, base, reg)

    def filtro_id():
        m, _ = _load(base, "filtro_identidad_zoom_out_zoom_in.py", "lu_filtroid")
        src = case.get("caldero_search_sources") or []
        # PATCH19: aceptar los resultados del puente ya validado por el motor principal.
        # No realiza otra búsqueda; el filtro solo examina las fuentes registradas.
        if not src:
            bridge = case.get("caldero_search_bridge") or {}
            if isinstance(bridge, dict) and bridge.get("status") == "EXECUTED" and bridge.get("origin") == "connected_tool_call":
                src = bridge.get("results") or []
        if not src:
            return "ACTIVA_MUDA", "sin fuentes de búsqueda verificables (caldero_search_sources o puente conectado ausentes): nada que filtrar", None
        ident = case.get("caldero_identity") or case.get("identity") or {}
        if not ident:
            return "ACTIVA_MUDA", f"{len(src)} fuentes pero sin caldero_identity en el input: el filtro no tiene identidad contra la cual comparar", None
        # PATCH 010a-6: antes se cargaba y nunca se llamaba. Llamada real, solo lectura (no entra al Caldero ni a H).
        kept, discarded = m.ZoomIdentityFilter(ident).filter([s for s in src if isinstance(s, dict)])
        cal = ((features or {}).get("caldero_busqueda_arquetipos") or {}).get("audit") or {}
        n_cal = len(cal.get("discarded_by_self_match") or []) if isinstance(cal, dict) else None
        return "ACTIVA", f"{len(src)} fuentes: conservadas {len(kept)}, descartadas por misma identidad {len(discarded)} (SelfMatchFilter del Caldero descartó {n_cal})", {
            "n_fuentes": len(src), "conservadas": [k.url for k in kept], "descartadas": [{"url": d["url"], "decision": d["decision"]} for d in discarded],
            "caldero_self_match_descartadas": n_cal, "can_decide_H": False}
    out["filtro_identidad"] = _pieza("filtro_identidad_zoom", "filtro_identidad_zoom_out_zoom_in.py", "SENSOR (identidad de fuentes)", filtro_id, base, reg)
    return out


def _compacto(o, depth=0, maxlist=12):
    if depth > 5:
        return "…"
    if isinstance(o, dict):
        return {str(k): _compacto(v, depth + 1, maxlist) for k, v in list(o.items())[:40]}
    if isinstance(o, (list, tuple)):
        return [_compacto(v, depth + 1, maxlist) for v in list(o)[:maxlist]]
    if isinstance(o, (set, frozenset)):
        return sorted(str(x) for x in o)[:maxlist]
    if isinstance(o, (str, int, float, bool)) or o is None:
        return o
    return str(o)[:200]


def _dedupe_traza_campo_244(features, reg, det):
    """PATCH 010a-1: UNICO guarda la MISMA salida de traza_P dos veces en features ("traza_campo_244" por
    _store_traza y "traza_campo_244.py" por run()); el puente de nombres recorre ambas y la señal suma 2 veces
    en rank_fusion. Se conserva "traza_campo_244" y la copia "traza_campo_244.py" se reemplaza por un ALIAS
    explícito (sin nombres de familia => el puente le da 0; no se borra nada en silencio: queda la fila).
    Si las dos copias NO son idénticas no se toca nada y se reporta."""
    a, b = "traza_campo_244", "traza_campo_244.py"
    if not (isinstance(features, dict) and a in features and b in features):
        det["dedupe_traza_campo_244"] = {"accion": "ninguna", "motivo": "no hay doble copia en features"}
        reg.append({"pieza": "traza_campo_244_dedupe", "archivo": "traza_campo_244.py", "sha256": None, "rol": "CONTROL de doble conteo (PATCH 010a)",
                    "estado": "ACTIVA_MUDA", "aporte": "sin doble copia en features (nada que deduplicar)", "can_decide_H": False})
        return
    va, vb = features.get(a), features.get(b)
    ja = json.dumps(va, sort_keys=True, ensure_ascii=False, default=str); jb = json.dumps(vb, sort_keys=True, ensure_ascii=False, default=str)
    sha = hashlib.sha256(ja.encode("utf-8")).hexdigest()
    if ja != jb:
        det["dedupe_traza_campo_244"] = {"accion": "ninguna", "motivo": "las dos copias difieren: no se deduplica", "sha_a": sha,
                                         "sha_b": hashlib.sha256(jb.encode("utf-8")).hexdigest()}
        reg.append({"pieza": "traza_campo_244_dedupe", "archivo": "traza_campo_244.py", "sha256": None, "rol": "CONTROL de doble conteo (PATCH 010a)",
                    "estado": "ACTIVA_MUDA", "aporte": "copias distintas: no se deduplica (revisar UNICO)", "can_decide_H": False})
        return
    features[b] = {"alias_de": a, "dedupe": "PATCH010a", "sha256_contenido": sha, "can_decide_H": False,
                   "motivo": "misma salida que features['traza_campo_244'] (annex.traza_P); se deja una sola copia para que la señal entre UNA vez al puente de nombres"}
    det["dedupe_traza_campo_244"] = {"accion": "alias", "conservada": a, "aliasada": b, "sha256_contenido": sha}
    reg.append({"pieza": "traza_campo_244_dedupe", "archivo": "traza_campo_244.py", "sha256": None, "rol": "CONTROL de doble conteo (PATCH 010a)",
                "estado": "ACTIVA", "aporte": f"features['{b}'] = alias de '{a}' (contenido idéntico sha {sha[:12]}); la señal traza entra 1 vez al rank (antes 2)",
                "can_decide_H": False})


def pre_predictor(case, motor, features, base, patterns_path, patterns):
    """Devuelve (votos: dict para features, detalle: dict, registro: list)."""
    reg: List[Dict[str, Any]] = []
    votos, det = {}, {}
    _dedupe_traza_campo_244(features, reg, det)
    det["catalogo"] = validar_catalogo(base, patterns_path, patterns, motor, features)

    def sombrero_entrada():
        # PATCH 010a-3: sombrero blanco = GUARDIAN/FILTRO de ENTRADA (antes del predictor); solo lectura.
        m, _ = _load(base, "sidecar_sombrero_blanco_filtro_v1.py", "lu_sombrero_filtro")
        vocab = set()
        for pv in (patterns.values() if isinstance(patterns, dict) else []):
            vocab |= set((pv.get("tokens_favor") or {})) | set((pv.get("tokens_contra") or {}))
        r = m.entrada(case, motor, vocab)
        det["sombrero_blanco_entrada"] = r
        n_marcas = r["n_fuera_catalogo"] + len(r["ruido_protocolo_textos"]) + len(r["campos_probabilisticos_prohibidos"]) + len(r["textos_excluidos"]) + int(r["ruido_protocolo_pregunta"])
        est = "ACTIVA" if n_marcas else "ACTIVA_MUDA"
        return est, (f"fuera_catalogo={r['n_fuera_catalogo']} ruido_protocolo={len(r['ruido_protocolo_textos'])}+preg:{r['ruido_protocolo_pregunta']} "
                     f"prohibidos={len(r['campos_probabilisticos_prohibidos'])} textos admitidos/excluidos={len(r['textos_admitidos'])}/{len(r['textos_excluidos'])}"
                     if n_marcas else "entrada limpia: sin fuera_catalogo, sin ruido de protocolo, sin campos prohibidos, sin textos meta (nada que filtrar)"), None
    _pieza("sombrero_blanco_entrada", "sidecar_sombrero_blanco_filtro_v1.py", "GUARDIAN/FILTRO de entrada (antes del predictor)", sombrero_entrada, base, reg,
           feeds_predictor=False)

    def neg():
        e, a, v, d = voto_negativo(base, motor, features, case.get("case_id"))
        if v: votos["negativo_ricci_vs_billar"] = v
        det["negativo_ricci_vs_billar"] = d
        return e, a, None
    _pieza("negativo_ricci_vs_billar", "lectura_negativo_ricci_vs_billar_v0_1.py", "VOTO lateral (convergencia/ranking; no gatea cierre)", neg, base, reg)

    def fam():
        if os.environ.get("FAMILIAS_TOKENS", "1") == "0":
            return "APAGADA_POR_FLAG", "FAMILIAS_TOKENS=0", None
        e, a, v, d = voto_familias_tokens(base, case, motor, patterns)
        votos["familias_tokens_puente"] = v
        det["familias_tokens_EXPERIMENTAL"] = d
        return e, a, None
    _pieza("familias_tokens_puente", "PUENTE_244_FAMILIAS.json", "VOTO lateral EXPERIMENTAL (1 voto por candidato)", fam, base, reg)
    ctx = {"sombrero": det.get("sombrero_blanco_entrada") or {}}

    def area_tokens():
        # PATCH 010a-4: AREA DE TOKENS taxonomy-ready (cuerpo_arco, oficio_riesgo/hostelería, trayectorias de riesgo,
        # sustancias, muerte/duelo, arquetipos dinámicos) + activación por corte + coactivación (coactivacion_escalas).
        a, _ = _load(base, "sidecar_area_tokens_v1.py", "lu_area")
        hot, _ = _load(base, "plugin_trayectoria_hosteleria.py", "lu_area_hot")
        cue, _ = _load(base, "sidecar_cuerpo_arco__BUG_A_SIN_CONFIRMAR.py", "lu_area_cue")
        arq, _ = _load(base, "plugin_arquetipos_dinamicos.py", "lu_area_arq")
        ali, _ = _load(base, "plugin_alias_reactivacion.py", "lu_area_ali")
        co, _ = _load(base, "coactivacion_escalas.py", "lu_area_co")
        regf = a.construir_registro(patterns if isinstance(patterns, dict) else {}, getattr(hot, "PATRON", None) if hot else None, cue,
                                    getattr(arq, "ARQUETIPOS_DINAMICOS", None) if arq else None)
        r = a.activar(regf, case.get("cuts") or [], motor.get("cuts") or [], ctx["sombrero"].get("textos_admitidos") or [],
                      getattr(ali, "ALIAS", {}) if ali else {}, _cargar_puente(base), co)
        ctx["area"] = r; ctx["registro_area"] = regf
        det["area_tokens"] = {"version": a.VERSION, "can_decide_H": False, "feeds_predictor": False, "ejes": list(a.EJES),
                              "diseno_taxonomia": a.__doc__.split("Canales")[0].strip(), "registro_familias": regf,
                              "por_corte": r["por_corte"], "resumen_por_familia": r["resumen_por_familia"], "migrar_despues": a.MIGRAR_DESPUES}
        act = r["resumen_por_familia"]
        return ("ACTIVA" if act else "ACTIVA_MUDA"), (f"{len(regf)} familias registradas; activas: " + "; ".join(f"{f}@{v['cortes']}:{v['tokens']}" for f, v in act.items())
                                                      if act else f"{len(regf)} familias registradas; ningún token de esas familias en el input"), None
    _pieza("area_tokens", "sidecar_area_tokens_v1.py", "AREA DE TOKENS (registro taxonomy-ready + coactivación; no decide)", area_tokens, base, reg, feeds_predictor=False)
    det["sensores_pre"] = sensores_pre(base, case, motor, features, reg, ctx)

    def venn_sistemas():
        # PATCH 010a-5: Venn por corte (Souriau / Polti / Caldero Q / CAMEO / memoria Caldero / área de tokens). No decide.
        v, _ = _load(base, "sidecar_venn_sistemas_v1.py", "lu_venn")
        ie, _ = _load(base, "motor_interrelacion_extensible_v0_1.py", "lu_venn_ie")
        mono, _ = _load(base, "plugin_circulo_monomito_v2.py", "lu_venn_mono")
        fview = {k: (features or {}).get(k) for k in ("polti_caldero", "plugin_circulo_monomito", "cameo_703_lateral", "interrelation")}
        fs = (features or {}).get("funciones_souriau")
        if not fs:
            # UNICO calcula funciones_souriau DESPUÉS del hub; misma función pura y mismo input (marco_funciones_souriau.distribuir(case.cuts)).
            mf, _ = _load(base, "marco_funciones_souriau.py", "lu_venn_mf")
            fs = mf.distribuir(case.get("cuts") or []) if mf else {}
        fview["funciones_souriau"] = fs
        r = v.venn(case.get("cuts") or [], fview, patterns if isinstance(patterns, dict) else {}, getattr(mono, "ESTRUCTURAS_CANDIDATAS", {}),
                   (ctx.get("area") or {}).get("por_corte") or [], ie)
        det["venn_sistemas"] = r
        con = [x for x in r["por_corte"] if x["intersecciones_por_par"] and any(p["interseccion"] for p in x["intersecciones_por_par"])]
        nuc = [(x["corte"], x["nucleo_3_o_mas_sistemas"]) for x in r["por_corte"] if x["nucleo_3_o_mas_sistemas"]]
        return ("ACTIVA" if con else "ACTIVA_MUDA"), (f"{len(r['por_corte'])} cortes; {len(con)} con intersección entre sistemas; núcleo ≥3 sistemas en {nuc[:6]}; "
                                                      f"vacíos en todo el caso: {r['sistemas_vacios_en_todo_el_caso']}" if con else
                                                      f"sin intersecciones entre sistemas; vacíos en todo el caso: {r['sistemas_vacios_en_todo_el_caso']}"), None
    _pieza("venn_sistemas", "sidecar_venn_sistemas_v1.py", "INTERRELACION/VENN por corte (alimenta motor_interrelacion_extensible.venn; no decide)", venn_sistemas, base, reg,
           feeds_predictor=False)

    def hosteleria():
        # PATCH 010a-4: UNICO do_hotel intersecta PATRON con P/A/C (fila ACTIVA aunque la intersección sea vacía).
        fid = next((r["familia_id"] for r in ctx.get("registro_area") or [] if r["familia_id"].startswith("oficio_riesgo.trayectoria_hosteleria")), None)
        res = ((ctx.get("area") or {}).get("resumen_por_familia") or {}).get(fid) if fid else None
        oc = {f: v for f, v in ((ctx.get("area") or {}).get("resumen_por_familia") or {}).items() if f.startswith(("oficio_riesgo.", "consumo_sustancias."))}
        if res:
            return "ACTIVA", f"tokens hostelería activos {res['tokens']} en {res['cortes']}; familias de oficio/sustancias activas: {sorted(oc)}", {"hosteleria": res, "oficio_y_sustancias": oc}
        return "ACTIVA_MUDA", (f"ningún token de la familia (consumo_sustancias, turno_atipico_nocturno, desgaste_psicosocial, desgaste_cambaceo_itinerante, aislamiento_social) "
                               f"en P/A/C ni por alias en textos admitidos; otras familias de oficio/sustancias activas: {sorted(oc) or 'ninguna'}"), {"oficio_y_sustancias": oc}
    det["sensores_pre"]["trayectoria_hosteleria"] = _pieza("trayectoria_hosteleria", "plugin_trayectoria_hosteleria.py", "FAMILIA DE TOKENS ocupacional (área de tokens)", hosteleria, base, reg,
                                                         feeds_predictor=False)

    def arq_din():
        # PATCH 010a-4: UNICO llama info() (catálogo estático, constante). Aquí: tokens observados por arquetipo.
        res = {f: v for f, v in ((ctx.get("area") or {}).get("resumen_por_familia") or {}).items() if f.startswith("arquetipos_dinamicos.")}
        if res:
            return "ACTIVA", f"arquetipos dinámicos con tokens observados: {res}", res
        return "ACTIVA_MUDA", "info() es catálogo estático; ningún token favor/contra de los 3 arquetipos dinámicos aparece en P/A/C", None
    det["sensores_pre"]["arquetipos_dinamicos"] = _pieza("plugin_arquetipos_dinamicos", "plugin_arquetipos_dinamicos.py", "FAMILIA DE TOKENS arquetipos (área de tokens)", arq_din, base, reg,
                                                       feeds_predictor=False)

    def rigor_pre():
        # PATCH 010a-4: UNICO llama rigor(motor) -> motor no tiene "cadena_top1" -> salida constante. Lectura PRE con la cadena real
        # (top1 del tablero por corte); la llamada post-H correcta ya existe en guardianes SHERLOCK_RIGOR.
        m, _ = _load(base, "plugin_metodo_rigor.py", "lu_rigor_pre")
        cadena = [((c.get("P_top5_ANEXO") or [[None]])[0][0]) for c in motor.get("cuts") or []]
        r = m.rigor({"cadena_top1": " → ".join(str(x) for x in cadena)}, hipotesis="")
        return ("ACTIVA" if r.get("auto") else "ACTIVA_MUDA"), (f"alarmas PRE: {r.get('auto')}" if r.get("auto") else
                                                               "cadena top1 por corte sin 4 cortes iguales seguidos (sin alarma HECATE); HOLMES/SCHOPENHAUER requieren hipótesis/inverso (post-H, guardianes)"), {"auto": r.get("auto"), "cadena_top1": r.get("cadena_top1")}
    det["sensores_pre"]["metodo_rigor_pre"] = _pieza("plugin_metodo_rigor (alimentado)", "plugin_metodo_rigor.py", "CONTROL de rigor PRE (cadena top1 real)", rigor_pre, base, reg,
                                                   feeds_predictor=False)

    def pregunta():
        m, _ = _load(base, "plugin_pregunta_dirigida.py", "lu_qdir")
        q = str(case.get("question", case.get("case_id", "")))
        h = m.detectar_pregunta_dirigida(q)
        es_id = q == str(case.get("case_id")) or (" " not in q.strip())
        if h:
            return "ACTIVA", f"{len(h)} hallazgos de pregunta dirigida", {"hallazgos": _compacto([getattr(x, "__dict__", x) for x in h])}
        return "ACTIVA_MUDA", ("la pregunta es un identificador (sin lenguaje natural): nada que analizar" if es_id else
                               "pregunta neutral: ninguna estructura dirigida detectada"), {"pregunta": q}
    det["sensores_pre"]["pregunta_dirigida"] = _pieza("plugin_pregunta_dirigida (verificado)", "plugin_pregunta_dirigida.py", "GUARDIAN de pregunta (entrada)", pregunta, base, reg,
                                                    feeds_predictor=False)

    def orden0():
        k, _ = _load(base, "protocolo_kernel_motor.py", "lu_orden0")
        q = str(case.get("question", ""))
        clas = k.clasificar_para_protocolo(q) if hasattr(k, "clasificar_para_protocolo") else None
        return "ACTIVA_MUDA", (f"constante por diseño: arranque_matriz es un contrato fijo y clasificar_para_protocolo clasifica OBSTÁCULOS de ejecución "
                               f"(aquí '{clas}' por defecto); el input no trae obstáculo -> no es un sensor del caso"), {"clasificacion": clas}
    det["sensores_pre"]["protocolo_orden0"] = _pieza("protocolo_orden0 (verificado)", "protocolo_kernel_motor.py", "CONTROL de arranque (orden 0)", orden0, base, reg,
                                                   feeds_predictor=False)

    def guardian_entrada():
        # PATCH 008: guardián de entrada — SOLO BANDERA de auto-evidencia (token de entrada = nombre de familia).
        g, _ = _load(base, "guardian_entrada_autoevidencia_v1.py", "lu_guard_entrada")
        r = g.evaluar(case.get("cuts") or [], patterns if isinstance(patterns, dict) else {})
        det["guardian_entrada_autoevidencia"] = r
        est = "ACTIVA" if r.get("bandera") else "ACTIVA_MUDA"
        return est, f"bandera={r.get('bandera')} autoevidencia={r.get('n_autoevidencia')} familias={r.get('familias_autoevidenciadas')}", None
    _pieza("guardian_entrada_autoevidencia", "guardian_entrada_autoevidencia_v1.py", "GUARDIAN (solo bandera; can_decide_H=False)", guardian_entrada, base, reg)
    # PATCH 010a-6: foto mínima (solo lectura) de salidas UNICO que el post necesita para el estado verificado.
    f = features or {}
    cal = f.get("caldero_busqueda_arquetipos") or {}
    det["_foto_estado_010"] = {
        "features_presentes": sorted(str(k) for k in f.keys()),
        "caldero_busqueda": {"presente": bool(cal), "status": cal.get("status") if isinstance(cal, dict) else None,
                             "tokens_neighbors": len(((cal.get("caldero_input") or {}).get("tokens_neighbors") or [])) if isinstance(cal, dict) else 0,
                             "query_exact": ((cal.get("audit") or {}).get("query_exact") if isinstance(cal, dict) else None),
                             # CEB_HONESTIDAD_CALDERO: recibo real del intento (lo escribe UNICO en features).
                             **_recibo_caldero(f.get("external_archetype_search_receipt"), cal)},
        "pre_h": {k: (f.get("pre_h_analogical_search") or {}).get(k) for k in ("status", "adapter", "reason", "tokens_neighbors", "raw_source_count")},
        "cameo_lateral": {k: (f.get("cameo_lateral") or {}).get(k) for k in ("status", "feeds_H", "discriminates", "selected_code_count")},
        "cameo_legacy": ((f.get("cameo_legacy_adapter_audit") or {}).get("audit") or {}),
        "cameo_703": {"status": (f.get("cameo_703_lateral") or {}).get("status"), "n_eventos": len((f.get("cameo_703_lateral") or {}).get("events") or [])},
        "dynamis_presente": bool(f.get("dynamis_dramatica_sistemica")),
        "store_root_vecinos": str(case.get("caldero_neighbor_store_root") or (Path(base) / "vecinos_caldero")),
    }
    det["n_piezas_pre"] = len(reg)
    return votos, det, reg


# ======================================================================= post-predictor
def post_predictor(case, motor, pred, result_view, base, reg):
    out = {}
    cands = pred.get("candidates") or []
    top1 = cands[0]["family"] if cands else None

    def aq():
        est, _ = _load(base, "modo_estricto_v1.py", "lu_estricto2")
        r = est.aquiles(Path(base), motor, pred, top1)
        ganador = (r.get("ganador_remuestreo_ultimas_ventanas") or [None])[-1]
        r["ganador_remuestreo_final"] = ganador
        r["ganador_remuestreo_coincide_con_top1"] = (ganador == top1) if ganador else None
        return "ACTIVA", f"estado {r.get('estado_H')} N_min {r.get('N_min')}; ganador remuestreo {ganador} {'=' if ganador == top1 else '≠'} top1", r
    out["aquiles_bootstrap"] = _pieza("aquiles_bootstrap", "plugin_aquiles_h.py", "SENSOR (C4 del modo estricto; claves p_H/n correctas)", aq, base, reg)

    def ancla():
        m, _ = _load(base, "plugin_aquiles_ancla_estricto.py", "lu_ancla")
        # PATCH 010a-6: llamada REAL (antes se cargaba y no se llamaba). COMPLETO = primer y último texto ADMITIDO por el sombrero
        # (hechos crudos). eje_candidato=None a propósito: el módulo prohíbe fabricarlo (bigrama/top1/sujeto) -> NO_VERIFICADO honesto.
        adm = (((result_view.get("_det_pre") or {}).get("sombrero_blanco_entrada") or {}).get("textos_admitidos")) or []
        if len(adm) < 2:
            return "ACTIVA_MUDA", "sin dos textos de hecho admitidos (inicio/final) en el input: COMPLETO no construible; el bootstrap de Aquiles sí corre", None
        try:
            comp = m.build_completo(adm[0]["texto"], adm[-1]["texto"])
        except Exception as e:
            return "ACTIVA_MUDA", f"build_completo rechazó el texto: {str(e)[:120]}", None
        r = m.evaluar_ancla(comp, replicar_fn=None, eje_candidato=None, sujeto=str(case.get("person") or ""))
        return "ACTIVA_MUDA", f"llamada real: estado_H={r.get('estado_H')} motivo='{r.get('motivo')}' (sin eje_candidato con cita en el input; prohibido fabricarlo)", {
            "estado_H": r.get("estado_H"), "motivo": r.get("motivo"), "ancla_ok": r.get("ancla_ok"), "completo_cortes": [adm[0]["corte"], adm[-1]["corte"]],
            "falta_para_anclar": "eje_candidato (tokens con cita) declarado en el input + replicar_fn del motor"}
    out["aquiles_ancla_estricto"] = _pieza("aquiles_ancla_estricto", "plugin_aquiles_ancla_estricto.py", "SENSOR", ancla, base, reg)

    def perfil():
        s, _ = _load(base, "sensor_perfil_narrador_v0_1.py", "lu_perfil")
        B = str(base)
        s.PIEZAS = {"detras_v2": (f"{B}/plugin_pregunta_detras_v2.py", None), "dirigida": (f"{B}/plugin_pregunta_dirigida_v0_5_1.py", None),
                    "polaridad": (f"{B}/plugin_polaridad_causal.py", None), "latencia": (f"{B}/control_latencia_decimo_hombre.py", None),
                    "guardia": (f"{B}/plugin_guardia_no_cruce.py", None)}
        s.DATOS = {"matriz": (f"{B}/MATRIZ_EQUIVALENCIAS_ESCALA.json", None), "puente": (f"{B}/PUENTE_244_FAMILIAS.json", None),
                   "patterns": (str(result_view.get("_patterns_path") or f"{B}/patterns_final_v14.json"), None)}
        M, regp = s.cargar_piezas()
        caso = {"caso": str(case.get("case_id")), "case_id": case.get("case_id"), "textos": _textos(case),
                "cortes": [{"id": c.get("id"), "date": c.get("date"), "P": c.get("P") or [], "A": c.get("A") or [], "C": c.get("C") or []} for c in case.get("cuts") or []]}
        r = s.correr_caso(caso, M, regp)
        ciegos = [p for p in (r.get("puntos_ciegos") or []) if str(p.get("nivel", p.get("prioridad", ""))).upper() == "ALTO"]
        return "ACTIVA", f"{len(r.get('puntos_ciegos') or [])} puntos ciegos ({len(ciegos)} ALTO); {len(r.get('preguntas') or [])} preguntas", {
            "lentes": r.get("lentes"), "puntos_ciegos": r.get("puntos_ciegos"), "preguntas": r.get("preguntas"), "piezas_usadas": r.get("piezas_usadas"),
            "can_decide_H": False, "entra_al_ranking": False}
    out["perfil_narrador"] = _pieza("perfil_narrador", "sensor_perfil_narrador_v0_1.py", "SENSOR siempre-on fuera de H", perfil, base, reg)

    def contrato():
        m, _ = _load(base, "formular_h_apuesta.py", "lu_formular")
        r = m.formular(copy.deepcopy(motor), copy.deepcopy(case.get("cuts") or []))
        h1 = (r.get("H1") or {}).get("family") if isinstance(r.get("H1"), dict) else r.get("H1")
        return "ACTIVA", f"línea contrato propone H1={h1} (contraste; el motor NO lo usa)", {"H1_contrato": h1, "H2_contrato": (r.get("H2") or {}).get("family") if isinstance(r.get("H2"), dict) else r.get("H2"),
                                                                                             "coincide_con_top1_motor": h1 == top1, "salida": _compacto(r)}
    out["contrato_formular_h"] = _pieza("formular_h_apuesta", "formular_h_apuesta.py", "SENSOR de contraste (línea contrato organic)", contrato, base, reg)

    mem = ((result_view.get("_det_pre") or {}).get("sensores_pre") or {}).get("memento") or {}
    ph = (mem.get("proto_hipotesis") or {})
    nuc = list(ph.get("nucleo_tokens") or [])
    try:
        cat = json.loads(Path(result_view.get("_patterns_path")).read_text(encoding="utf-8"))
        fav = set(((cat.get(top1) or {}).get("tokens_favor") or {})); con = set(((cat.get(top1) or {}).get("tokens_contra") or {}))
    except Exception:
        fav, con = set(), set()
    def sombrero_salida():
        # PATCH 010a-3: sombrero blanco = GUARDIAN/FILTRO de SALIDA (después del predictor); solo lectura.
        m, _ = _load(base, "sidecar_sombrero_blanco_filtro_v1.py", "lu_sombrero_filtro2")
        try:
            cat = json.loads(Path(result_view.get("_patterns_path")).read_text(encoding="utf-8"))
        except Exception:
            cat = {}
        ent = (result_view.get("_det_pre") or {}).get("sombrero_blanco_entrada")
        r = m.salida(pred, motor, cat, ent)
        return ("ACTIVA_MUDA" if r["salida_limpia"] else "ACTIVA"), (
            f"salida limpia: {r['n_top10_revisados']} candidatos del catálogo, evidencia solo con vocabulario del catálogo, sin ruido de protocolo (nada que filtrar)"
            if r["salida_limpia"] else f"marcas de salida: fuera_catalogo={r['familias_fuera_de_catalogo']} ev_fuera_vocab={sorted(r['evidencia_top10_fuera_vocabulario'])} ruido={r['ruido_protocolo_en_etiquetas']}"), r
    out["sombrero_blanco_salida"] = _pieza("sombrero_blanco_salida", "sidecar_sombrero_blanco_filtro_v1.py", "GUARDIAN/FILTRO de salida (después del predictor)", sombrero_salida, base, reg,
                                           feeds_predictor=False)
    reg.append({"pieza": "plugin_sombrero_blanco_token (declaración)", "archivo": "plugin_sombrero_blanco_token.py", "sha256": _sha(Path(base) / "plugin_sombrero_blanco_token.py"),
                "rol": "GUARDIAN/FILTRO (StinkBox de tokens fuera de catálogo; post-apuesta en UNICO)", "estado": "ACTIVA" if (motor.get("sombrero_blanco") or {}).get("n_esta_corrida") else "ACTIVA_MUDA",
                "aporte": f"n_esta_corrida={(motor.get('sombrero_blanco') or {}).get('n_esta_corrida')}; feeds_predictor VERIFICADO=False (la fila UNICO declara True; corrige 010b)",
                "feeds_predictor": False, "can_decide_H": False})

    try:
        out["estado_verificado"] = estado_verificado(case, motor, pred, result_view, base, reg)
    except Exception as e:
        out["estado_verificado"] = {"status": "ERROR", "error": f"{type(e).__name__}: {e}"}

    out["memento_vs_top1"] = {"proto_H1_configuracion": ph.get("H1_candidata"), "nucleo_tokens": nuc, "top1": top1,
                              "nucleo_en_favor_de_top1": [t for t in nuc if t in fav], "nucleo_en_contra_de_top1": [t for t in nuc if t in con],
                              "lectura": "cuántos tokens del núcleo Memento (PRE, sin mirar top1) pertenecen al patrón top1; sensor, no decide H"}
    return out


# ======================================================================= PATCH 010a-6: estado verificado
# Mapa componente UNICO -> clave que recorre el puente de nombres / dimensiones del vector (mismo mapa que la auditoría runner 2026-10-06).
_V_BRIDGE = {"plugin_cameo_institucional.py": "cameo_lateral", "cameo_to_703_lateral_v1.py": "cameo_703_lateral",
             "sidecar_caldero_busqueda_arquetipos.py": "caldero_busqueda_arquetipos", "plugin_circulo_monomito_v2.py": "plugin_circulo_monomito",
             "motor_interrelacion_extensible_v0_1.py": "interrelation", "plugin_arcos_emocionales_laterales.py": "arcos_emocionales_laterales",
             "cameo_to_244_adapter_v1.py": "cameo_legacy_adapter_audit", "metacognition_v0_1.py": "metacognition",
             "negativo_ricci_vs_billar (voto hub)": "negativo_ricci_vs_billar", "familias_tokens_puente (voto hub)": "familias_tokens_puente"}
_V_RUN = ["geometria", "polti_caldero", "traza_campo_244", "traza_campo_244.py", "plugin_reporte_3d", "otto_numinoso", "embudo_clinico", "trayectoria_hosteleria",
          "estabilidad_vectorial", "aquiles_h", "billar_circular_v0_2", "ricci_forman_v0_1", "lateral_metrics_v1_1", "acero_zoomout", "capa2_antecedentes",
          "plugin_picos_mesetas.py", "plugin_arco_field_snyder_mckee.py", "plugin_sesgo_lectura.py", "plugin_pregunta_detras", "plugin_metodo_rigor",
          "plugin_arquetipos_dinamicos", "plugin_pregunta_dirigida"]
_V_DIMS = {"motor_interrelacion_extensible_v0_1.py": ["relational_activity", "relational_alignment"],
           "stinkbox_to_light_bus_v1": ["relational_activity", "relational_alignment"],
           "sidecar_caldero_busqueda_arquetipos.py": ["caldero_neighbor_activity", "caldero_neighbor_alignment"],
           "vecinos_caldero/neighbor_store.py": ["caldero_neighbor_memory", "caldero_neighbor_alignment"],
           "stinkbox_transport_v0_2.py": ["stinkbox_support"], "pre_h_analogical_search(V0.18)": ["analog_alignment"],
           "plugin_cameo_institucional.py": ["cameo_activity", "cameo_profile_activity"],
           "dynamis_dramatica_sistemica": ["dynamis_shared_evidence", "dynamis_prosecution", "dynamis_success_limit_loop", "dynamis_load_shift_loop", "dynamis_diversion",
                                           "dynamis_emotional_oscillation", "dynamis_commons_attrition", "dynamis_avoidance_resistance", "dynamis_homeostatic_reason",
                                           "dynamis_guardian_attenuation", "dynamis_skeptical_guardrails", "dynamis_sigma_balance", "dynamis_acceleration", "dynamis_containment",
                                           "dynamis_structural_contribution"]}
_V_MOTIVO_FIJO = {
    "matriz_clases": "registro de PRESENCIA de MATRIZ_EQUIVALENCIAS_ESCALA.json / PUENTE_244_FAMILIAS.json / familias_tokens (inventario; no depende del caso). Su salida no trae nombres de candidato: no entra al ranking",
    "plugin_guardia_no_cruce.py": "absorbido: la lógica corre en GuardiaNoCruce dentro de _run_transversal_guards (protocol_controls); el archivo se carga como artefacto, no como API",
    "cameo_to_244_adapter_v1.py": "el adaptador CAMEO->244 (legado, solo auditoría) devuelve NOT_APPLICABLE porque falta el mapping aprobado cameo_to_244.json; UNICO sobrescribe su salida a AUDIT_ONLY antes de guardarla (por eso features dice AUDIT_ONLY y la fila NOT_APPLICABLE). No alimenta H por diseño",
    "protocolo_orden0": "constante por diseño (contrato de arranque + clasificación de obstáculos de ejecución)",
    "plugin_sombrero_blanco_token.py": "GUARDIAN/FILTRO post-apuesta (tokens fuera de catálogo -> StinkBox). No alimenta al predictor",
}


def estado_verificado(case, motor, pred, result_view, base, reg):
    det = result_view.get("_det_pre") or {}
    foto = det.get("_foto_estado_010") or {}
    nbm = ((pred.get("name_bridge") or {}).get("modules")) or {}
    lsr = {r.get("signal"): r for r in (pred.get("lateral_signal_registry") or [])}
    dims = set(pred.get("dimensions") or [])
    dg = pred.get("dimension_guard") or {}
    excl = set(dg.get("excluded_constant") or []) | {x.get("dimension") for x in (dg.get("excluded_duplicate") or []) if isinstance(x, dict)}
    filas = []

    def llegada(comp, bk=None):
        lleg, motivo = [], []
        if bk:
            nb = nbm.get(bk)
            if bk in lsr:
                lleg.append("H(rank_fusion:señal_lateral)")
            elif nb is None:
                motivo.append(f"'{bk}' no lo recorre el puente de nombres (excluido o ausente en features)")
            elif nb.get("reaches_candidates") and not nb.get("discriminates"):
                motivo.append("el puente llega a candidatos pero no discrimina (mismo valor para todos)")
            elif not nb.get("reaches_candidates"):
                motivo.append("su salida no nombra ningún candidato del top: el puente no llega")
        for dm in _V_DIMS.get(comp, []):
            if dm in dims:
                lleg.append(f"H(dim:{dm})")
        dx = [dm for dm in _V_DIMS.get(comp, []) if dm in excl]
        if dx and not any(x.startswith("H(dim") for x in lleg):
            motivo.append(f"dimensiones {dx} excluidas por dimension_guard (constantes/duplicadas entre candidatos)")
        return lleg, motivo

    def fila(comp, declarado, estado, lleg, motivo, **kw):
        filas.append({"componente": comp, "declarado_UNICO": declarado, "estado_verificado": estado, "llega_a_H": bool([x for x in lleg if x.startswith("H(")]),
                      "llega": lleg, "feeds_predictor_verificado": bool(lleg), "motivo": "; ".join(motivo) if isinstance(motivo, list) else motivo,
                      "can_decide_H": False, **kw})

    for comp in _V_RUN:
        lleg, mot = llegada(comp, comp)
        fila(comp, "EXECUTED feeds_predictor=True (run() lo pone a todos)", "ACTIVA" if lleg else "ACTIVA_MUDA", lleg,
             mot or (["llega a H"] if lleg else ["salida sin vía al ranking"]))
    for comp, bk in sorted(_V_BRIDGE.items()):
        if comp in ("cameo_to_244_adapter_v1.py", "sidecar_caldero_busqueda_arquetipos.py", "plugin_cameo_institucional.py"):
            continue  # filas propias más abajo (con motivo específico)
        lleg, mot = llegada(comp, bk)
        fila(comp, "(ver component_status)", "ACTIVA" if lleg else "ACTIVA_MUDA", lleg, mot or (["llega a H"] if lleg else ["sin vía al ranking"]))
    lv = [k for k in ("negativo_ricci_vs_billar", "familias_tokens_puente") if k in lsr]
    fila("laterales_unico_v1.py(pre)", "EXECUTED feeds_predictor=True", "ACTIVA" if lv else "ACTIVA_MUDA", [f"H(rank_fusion:{k})" for k in lv],
         "votos del hub que llegan al rank: " + (", ".join(lv) if lv else "ninguno discrimina en este caso") + "; los sensores del hub no alimentan al predictor")
    # sin fila en UNICO: dynamis / votos hub
    lleg, mot = llegada("dynamis_dramatica_sistemica")
    fila("dynamis_dramatica_sistemica", "(sin fila en component_status)", "ACTIVA" if lleg else "ACTIVA_MUDA", lleg,
         mot or ["corre en UNICO (l.~1703) y sus dims dynamis_* entran al vector de candidato"], fila_nueva=True, presente=foto.get("dynamis_presente"))
    for comp in ("negativo_ricci_vs_billar", "familias_tokens_puente"):
        f = next((x for x in filas if x["componente"].startswith(comp)), None)
        if f:
            f["fila_nueva"] = True; f["declarado_UNICO"] = "(sin fila en component_status; voto del hub guardado en features)"
    # filas mudas sin motivo (auditoría): motivo real
    for comp in ("matriz_clases", "plugin_guardia_no_cruce.py", "cameo_to_244_adapter_v1.py", "protocolo_orden0", "plugin_sombrero_blanco_token.py"):
        mot = _V_MOTIVO_FIJO[comp]
        if comp == "matriz_clases":
            pres = [n for n in ("MATRIZ_EQUIVALENCIAS_ESCALA.json", "PUENTE_244_FAMILIAS.json") if (Path(base) / n).is_file()]
            mot += f" (presentes: {pres})"
        if comp == "cameo_to_244_adapter_v1.py":
            mot += f" (cameo_to_244.json presente en el pack: {(Path(base) / 'cameo_to_244.json').is_file()})"
        fila(comp, {"matriz_clases": "PRESENTE", "plugin_guardia_no_cruce.py": "ABSORBIDO_EN_GUARDIA_TRANSVERSAL", "cameo_to_244_adapter_v1.py": "NOT_APPLICABLE",
                    "protocolo_orden0": "(sin fila)", "plugin_sombrero_blanco_token.py": "EXECUTED feeds_predictor=True"}[comp],
             "GUARDIAN_FILTRO" if comp == "plugin_sombrero_blanco_token.py" else "ACTIVA_MUDA", [], mot,
             **({"feeds_predictor_declarado": True, "feeds_predictor_corregido": False} if comp == "plugin_sombrero_blanco_token.py" else {}))
    ph = foto.get("pre_h") or {}
    lleg, mot = llegada("pre_h_analogical_search(V0.18)")
    fila("pre_h_analogical_search(V0.18)", ph.get("status"), "ACTIVA" if lleg else ("ACTIVA_MUDA" if ph.get("status") == "API_PENDING" else ("ACTIVA" if ph.get("tokens_neighbors") else "ACTIVA_MUDA")), lleg,
         ([f"API_PENDING: {ph.get('adapter')}"] if ph.get("status") == "API_PENDING" else
          [f"status={ph.get('status')}; fuentes={ph.get('raw_source_count')}; tokens analógicos={ph.get('tokens_neighbors')} (alimentan StinkBox y analog_alignment)"]) + mot)
    cb = foto.get("caldero_busqueda") or {}
    lleg, mot = llegada("sidecar_caldero_busqueda_arquetipos.py", "caldero_busqueda_arquetipos")
    est_cal = estado_honesto_caldero(cb)
    fila("sidecar_caldero_busqueda_arquetipos.py", est_cal, "ACTIVA" if lleg else "ACTIVA_MUDA", lleg,
         [f"{est_cal}: provider={cb.get('provider')} intento={cb.get('attempt_status')} resultados={cb.get('result_count')} consultas={cb.get('query_count')}; {cb.get('tokens_neighbors')} tokens vecinos"] + mot,
         estado_busqueda_externa=est_cal, search_performed=(est_cal == "EJECUTADO"),
         **alerta_ejecucion(est_cal, contrato_permite_omision=(est_cal == "OMITIDO_POR_CONDICION" and cb.get("required") is False) or cb.get("cal_status") == "SKIPPED_INTERNAL_ANALYSIS", error=cb.get("error")))
    # neighbor_store: la persistencia se adjunta a una COPIA (ceb.call envuelve la salida) -> no aparece en RESULT. Se lee el evento del store (solo lectura).
    ns = {"status": "SIN_EJECUCION", "motivo": "sin búsqueda Caldero en este caso (nada que persistir)"}
    if cb.get("presente"):
        ev = Path(foto.get("store_root_vecinos") or "") / "neighbor_events.jsonl"
        last = None
        if ev.is_file():
            for line in ev.read_text(encoding="utf-8").splitlines():
                try:
                    o = json.loads(line)
                except Exception:
                    continue
                if str(o.get("case_id")) == str(case.get("case_id")) and str(o.get("query", "")) == str(cb.get("query_exact") or ""):
                    last = o
        ns = {"status": "PERSISTED" if last else "NO_ENCONTRADO_EN_STORE", "store": str(ev),
              "evento": {k: v for k, v in (last or {}).items() if k not in ("tokens_neighbors",)}, "n_tokens_neighbors": len((last or {}).get("tokens_neighbors") or []),
              "nota": "UNICO escribe caldero_search['persistence'] en la copia que devuelve ceb.call; features guarda otra copia -> invisible en RESULT (corrige 010b)"}
    lleg, mot = llegada("vecinos_caldero/neighbor_store.py")
    fila("vecinos_caldero/neighbor_store.py", (f"{est_cal} feeds_H=True" if cb.get("presente") else f"{est_cal} (sin fila)"), "ACTIVA" if ns["status"] == "PERSISTED" else "ACTIVA_MUDA", lleg,
         mot or ([ns.get("motivo")] if ns.get("motivo") else []), persistencia=ns, feeds_H_verificado=bool([x for x in lleg if x.startswith("H(")]))
    # cameo: feeds_H coherente (salida del módulo dice True siempre; fila = discriminates)
    cl = foto.get("cameo_lateral") or {}
    lleg, mot = llegada("plugin_cameo_institucional.py", "cameo_lateral")
    fila("plugin_cameo_institucional.py (coherencia feeds_H)", f"fila feeds_H={bool(cl.get('discriminates'))} / salida feeds_H={cl.get('feeds_H')}",
         "ACTIVA" if lleg else "ACTIVA_MUDA", lleg, mot or ["llega a H"], feeds_H_verificado=bool([x for x in lleg if x.startswith("H(")]),
         nota="valor único verificado: feeds_H_verificado (sale de la llegada real al rank, no de la declaración)")
    # stinkbox
    for comp in ("stinkbox_transport_v0_2.py", "stinkbox_to_light_bus_v1"):
        lleg, mot = llegada(comp)
        fila(comp, "EXECUTED feeds_H=True", "ACTIVA" if lleg else "ACTIVA_MUDA", lleg, mot or ["llega a H"])
    n_pre = det.get("n_piezas_pre")
    resumen = {"n_piezas_pre_declarado_en_component_status": n_pre, "n_piezas_post_hasta_ahora": len(reg) - (n_pre or 0), "n_piezas_total_registro": len(reg),
               "explicacion": "UNICO cuenta n_piezas=len(registro) al terminar el PRE; el POST añade sus piezas a la MISMA lista después -> el registro final tiene más filas. No falta ninguna."}
    reg.append({"pieza": "n_piezas (verificado)", "archivo": "laterales_unico_v1.py", "sha256": None, "rol": "CONTROL de registro", "estado": "ACTIVA_MUDA",
                "aporte": f"control de conteo (constante por diseño entre casos): pre={n_pre} + post={resumen['n_piezas_post_hasta_ahora']} (+esta fila) = {len(reg) + 1}; el n_piezas de component_status es solo el PRE",
                "can_decide_H": False})
    for f in filas:
        if f.get("fila_nueva") or f["componente"] in _V_MOTIVO_FIJO or f["componente"] in ("pre_h_analogical_search(V0.18)", "sidecar_caldero_busqueda_arquetipos.py",
                                                                                          "vecinos_caldero/neighbor_store.py", "plugin_cameo_institucional.py (coherencia feeds_H)"):
            reg.append({"pieza": f"verificado:{f['componente']}", "archivo": None, "sha256": None, "rol": "ESTADO VERIFICADO (PATCH 010a)", "estado": f["estado_verificado"],
                        "aporte": f"declarado={f['declarado_UNICO']} | llega={f['llega'] or 'no'} | {f['motivo']}", "feeds_predictor": f["feeds_predictor_verificado"], "can_decide_H": False})
    falsos = [f["componente"] for f in filas if "feeds_predictor=True" in str(f["declarado_UNICO"]) and not f["feeds_predictor_verificado"]]
    alertas = aplicar_alertas(reg, filas)
    return {"version": "ESTADO_VERIFICADO_PATCH010a", "filas": filas, "registro_resumen": resumen, "alertas_ejecucion": alertas,
            "declarado_feeds_predictor_sin_llegada": falsos,
            "nota": "010a no puede reescribir component_status (vive en UNICO): aquí está el estado verificado al lado; 010b lo aplica en la fuente"}
