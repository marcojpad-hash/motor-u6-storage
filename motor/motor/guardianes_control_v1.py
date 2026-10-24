#!/usr/bin/env python3
"""guardianes_control_v1.py — PRUEBAS DE CONTROL ESTRUCTURAL siempre-on · 2026-09-27

Corre sobre TODA entrada, después del predictor. Cada guardián emite un bloque trazable
(qué revisó, qué marcó, evidencia) y una bandera de control:
  LIMPIO | MARCA | NO_RESUELTO | LATENTE | ERROR
Alimentan convergencia/latencia SOLO como registro. can_decide_H=False: ningún guardián
escribe H, reordena candidatos ni toca patterns_final_v14.json. El motor verifica al final
que el bloque del predictor quedó byte a byte igual (hash antes/después).

Piezas (se cargan desde la carpeta de corrida y se verifica su sha):
  control_latencia_decimo_hombre.py ff03241d (T)       → DECIMO_HOMBRE_LATENCIA
  plugin_pregunta_detras_v2.py      771cb526 (2.3.3 = SB 2.3.2 f0b1a92b + fix demostrativo) → PREGUNTA_DETRAS_V2
  plugin_pregunta_dirigida_v0_5_1.py (base SB 0.5.0 19f59a1d + capa 0.5.1) → PREGUNTA_DIRIGIDA_POST_HOC y FALACIAS
  guardian_logica_copi_v1.py        (nuevo)             → LOGICA_COPI
  plugin_polaridad_causal.py        534ae636 (T)        → POLARIDAD_CAUSAL
  sidecar_ablacion_hombre_acero.py  7db774c0 (zip CHECKPOINT_REPRODUCIBLE_20260920) + guardian_acero_rival_v1.py (nuevo) → HOMBRE_DE_ACERO
  plugin_metodo_rigor.py            a4f5659e            → SHERLOCK_RIGOR (ahora recibe cadena_top1)
  guardian_tropos_beristain_v1.py   (nuevo 27-sep)      → TROPOS_BERISTAIN (vecino de FALACIAS y LOGICA_COPI)

V1.1 (27-sep, versión TROPOS):
  - Guardián 9: TROPOS_BERISTAIN sobre la pregunta y los textos del input. Corre después de FALACIAS,
    LOGICA_COPI y POLARIDAD, y se corrige con ellos (serie de vecinos): corregir_con_vecinos().
  - Ruta de cierre latente (regla de Mj: lo que no se entiende o no se sostiene NO es cierre):
    ruta_cierre_latente() junta todo NO_RESUELTO y toda DOBLE_NEGACION_LITOTE de cualquier guardián,
    con motivo trazable (guardián, tipo, fragmento, corte), y los registra en
    control_latencia_decimo_hombre (sin re-tirada del décimo hombre: un NO_RESUELTO no es un empate
    numérico). El motor usa esta salida para poner el CIERRE en LATENTE y correr tortugas.
    H1/H2/top1 no cambian.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import re
import statistics
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

VERSION = "GUARDIANES_CONTROL_V1_2_UNICO_20260927"  # V1.2: espera detrás v2 2.3.3 (fix demostrativo); resto = V1.1 (f26f8c56)
SHA_ESPERADO = {
    "control_latencia_decimo_hombre.py": "ff03241d42d7770c2af83de60eeb41db6bdbba78a0511f7470ca65b766220345",
    "plugin_pregunta_detras_v2.py": "771cb526eafe56e10967e31d1c9320296beff77b83ef81bf76ac46114244c247",
    "plugin_polaridad_causal.py": "534ae6366b525f5114ff36217fca0760585602ff2ba513b13a642dcb1082e739",
    "plugin_metodo_rigor.py": "a4f5659e14e6aab2e40a0929a3c1f2388b89f304dcc2c9a4cb43ebe7cc332cf0",
    "sidecar_ablacion_hombre_acero.py": "7db774c0c4934260db59f0a9305e074792488e75bde1560ed7a562f1de277f60",
}
ORIGEN = {
    "control_latencia_decimo_hombre.py": "TRANSFER_V15_1/control_latencia_decimo_hombre.py (copia idéntica en SB y en MOTOR_V15_3_COMPLETO_CORRE_20260921.zip)",
    "plugin_pregunta_detras_v2.py": "MOTOR_UNICO v2.3.3 = SB 2.3.2 (f0b1a92b, en rescate/) + fix demostrativo",
    "plugin_pregunta_dirigida_v0_5_1.py": "SB/plugin_pregunta_dirigida.py 0.5.0 (19f59a1d) + capa estructural 0.5.1 añadida al final (esta entrega)",
    "plugin_polaridad_causal.py": "TRANSFER_V15_1/plugin_polaridad_causal.py",
    "plugin_metodo_rigor.py": "TRANSFER_V15_1/plugin_metodo_rigor.py (ya estaba en la carpeta de corrida)",
    "sidecar_ablacion_hombre_acero.py": "TRANSFER_V15_1/CHECKPOINT_REPRODUCIBLE_20260920.zip!03_LATERALES_VIGENTES/",
    "guardian_logica_copi_v1.py": "NUEVO (no existía código de Copi en disco, zips, transcripts ni Notion)",
    "guardian_acero_rival_v1.py": "NUEVO (steelman del rival; el sidecar v0.1 solo hacía ablación de pilares de H)",
    "guardian_tropos_beristain_v1.py": "NUEVO 27-sep (solo había lítote/hipérbole en detrás v2 y el hook registrar_sinecdoque; se reutilizan)",
}
CANDADOS = {"can_decide_H": False, "escribe_H": False, "escribe_patterns": False, "reordena_candidatos": False,
            "alimenta": "convergencia/latencia (solo registro)", "siempre_on": True}
EXCLUIR_TEXTO = {"P", "A", "C", "protocol", "case_id", "url", "caldero_neighbor_store", "random_seed", "z90_date",
                 "date", "id", "birth_date", "death_date", "person", "source_basis", "future_data_excluded_from_input",
                 "caldero_llm_neighbor_hints", "external_lights", "caldero_archetype_input", "stinkbox_root",
                 "stinkbox_pending_case_id", "stinkbox_cut_id", "consolidado_off", "external_activations"}


def _sha(p: Path) -> Optional[str]:
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None


def _cargar(base: Path, fn: str, alias: str):
    p = base / fn
    if not p.is_file():
        return None, {"archivo": fn, "presente": False}
    if str(base) not in sys.path:
        sys.path.insert(0, str(base))
    spec = importlib.util.spec_from_file_location(alias, str(p))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[alias] = mod
    spec.loader.exec_module(mod)
    sha = _sha(p)
    esp = SHA_ESPERADO.get(fn)
    return mod, {"archivo": fn, "presente": True, "sha256": sha, "sha_esperado": esp,
                 "sha_ok": (sha == esp) if esp else "sin_referencia(nuevo_o_modificado)",
                 "version": getattr(mod, "VERSION", getattr(mod, "__version__", None)), "origen": ORIGEN.get(fn)}


def textos_de_entrada(case: Dict[str, Any]) -> List[Dict[str, str]]:
    out: List[Dict[str, str]] = []

    def walk(o, path):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in EXCLUIR_TEXTO:
                    continue
                walk(v, f"{path}.{k}" if path else k)
        elif isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, f"{path}[{i}]")
        elif isinstance(o, str):
            s = o.strip()
            if len(s.split()) >= 2 and not s.startswith(("http://", "https://", "/")):
                out.append({"origen": path, "texto": s})
    walk(case, "")
    return out


def _bloque(nombre, piezas, reviso, n, marcas, bandera, extra=None):
    b = {"guardian": nombre, "piezas": piezas, "reviso": reviso, "n_revisados": n, "marcas": marcas,
         "n_marcas": len(marcas), "bandera": bandera, **CANDADOS}
    if extra:
        b["detalle"] = extra
    return b


def _h(obj) -> Dict[str, Any]:
    return json.loads(json.dumps(obj, ensure_ascii=False, default=lambda o: getattr(o, "__dict__", str(o))))


# ------------------------------------------------------------------ 1) décimo hombre / latencia
def g_decimo_hombre(base, case, motor, pred):
    lat, meta = _cargar(base, "control_latencia_decimo_hombre.py", "g_ctrl_lat")
    if lat is None:
        return _bloque("DECIMO_HOMBRE_LATENCIA", [meta], "cortes", 0, [], "ERROR", {"motivo": "archivo_ausente"})
    store = base / f"estado_latencia_guardianes__{re.sub(r'[^A-Za-z0-9_]+', '_', str(case.get('case_id')))}.json"
    if store.exists():
        store.unlink()
    clave = f"{case.get('case_id')}::trayectoria_top1"
    tokens_por_corte = {str(c.get("id")): [str(t) for e in ("P", "A", "C") for t, _ in (c.get(e) or [])] for c in case.get("cuts") or []}
    cortes, marcas = [], []
    LATENTES = {"LATENCIA", "ALMACENADO_ESPERANDO_DATOS"}
    for c in motor.get("cuts") or []:
        top = c.get("P_top5_ANEXO") or []
        full = list((c.get("P_FULL_244") or {}).values())
        sigma = statistics.pstdev(full) if len(full) > 1 else 0.0
        if len(top) < 2 or sigma <= 0:
            continue
        gap = float(top[0][1]) - float(top[1][1])
        p = 0.5 + 0.5 * math.tanh(gap / sigma)
        out = lat.actualizar_expediente(clave, tema="corte_top1_vs_top2", p_momento=p,
                                        tokens_nuevos=tokens_por_corte.get(str(c.get("corte")), []), store_path=store)
        ex = out["expediente"]
        estado = ex["estado"]
        fila = {"corte": c.get("corte"), "top1": top[0][0], "top2": top[1][0], "gap": round(gap, 6), "sigma_244": round(sigma, 6),
                "p_momento": round(p, 4), "estado_control": estado, "accion": out["accion"],
                "re_tirada_decimo_hombre": ex["n_desempates"], "LATENTE": estado in LATENTES}
        cortes.append(fila)
        if fila["LATENTE"]:
            marcas.append({"tipo": "CORTE_LATENTE", "evidencia": fila, "estado": "LATENTE"})
    # nivel H: separación top1-top2 en la fusión, normalizada por la dispersión del top10
    cands = pred.get("candidates") or []
    final = None
    if len(cands) >= 2:
        rf = [float(x["rank_fusion"]) for x in cands]
        sig = statistics.pstdev(rf) or 1.0
        gap = rf[0] - rf[1]
        p = 0.5 + 0.5 * math.tanh(gap / sig)
        out = lat.actualizar_expediente(f"{case.get('case_id')}::cierre_H", tema="cierre_top1_vs_top2", p_momento=p,
                                        tokens_nuevos=sum(tokens_por_corte.values(), []), store_path=store)
        ex = out["expediente"]
        final = {"top1": cands[0]["family"], "top2": cands[1]["family"], "gap_rank": round(gap, 6), "sigma_top10": round(sig, 6),
                 "p_momento": round(p, 4), "estado_control": ex["estado"], "accion": out["accion"],
                 "re_tirada_decimo_hombre": ex["n_desempates"], "LATENTE": ex["estado"] in LATENTES,
                 "estado_motor": (pred.get("information_state") or {}).get("state")}
        if final["LATENTE"]:
            marcas.append({"tipo": "CIERRE_LATENTE_SEGUN_DECIMO_HOMBRE", "evidencia": final, "estado": "LATENTE"})
    nat = (((motor.get("protocolo") or {}).get("latencia")) or {})
    reemplazo = {"capa_nativa_en_corrida": nat.get("capa"),
                 "respaldo_minimo_reemplazado": nat.get("capa") == "CONTROL_LATENCIA_DECIMO_HOMBRE"}
    bandera = "LATENTE" if (final and final["LATENTE"]) else ("MARCA" if marcas else "LIMPIO")
    try:
        store.unlink()
    except OSError:
        pass
    return _bloque("DECIMO_HOMBRE_LATENCIA", [meta], "separación top1/top2 por corte (z sobre el tablero 244) y en el cierre",
                   len(cortes) + (1 if final else 0), marcas, bandera,
                   {"cortes": cortes, "cortes_latentes": [f["corte"] for f in cortes if f["LATENTE"]], "cierre": final,
                    "nativo": reemplazo, "regla_p": "p = 0.5 + 0.5·tanh(gap/σ); banda de empate 0.45–0.55 → re-tirada del décimo hombre"})


# ------------------------------------------------------------------ 2) pregunta detrás v2
def g_detras(base, question, textos):
    m, meta = _cargar(base, "plugin_pregunta_detras_v2.py", "g_detras_v2")
    if m is None:
        return _bloque("PREGUNTA_DETRAS_V2", [meta], "pregunta+textos", 0, [], "ERROR")
    marcas = []
    items = [{"origen": "question", "texto": question}] + [t for t in textos if t["origen"] != "question"]
    for t in items:
        if not t["texto"]:
            continue
        r = m.filtrar(t["texto"])
        if r.get("bandera"):
            marcas.append({"tipo": r.get("bandera"), "estado": "DETECTADA",
                           "evidencia": {"origen": t["origen"], "texto": t["texto"][:200],
                                         "marcajes": [{k: (x.get(k) if isinstance(x, dict) else getattr(x, k, None)) for k in ("lexema", "funcion", "regla")}
                                                      for x in (r.get("marcajes") or [])][:6]}})
    return _bloque("PREGUNTA_DETRAS_V2", [meta], "pregunta y textos de entrada (perfilamiento/tropos)", len(items), marcas,
                   "MARCA" if marcas else "LIMPIO")


# ------------------------------------------------------------------ 3) pregunta dirigida + post hoc, 4) falacias
def g_dirigida_y_falacias(base, question, textos):
    m, meta = _cargar(base, "plugin_pregunta_dirigida_v0_5_1.py", "g_dirigida_051")
    if m is None:
        e = _bloque("PREGUNTA_DIRIGIDA_POST_HOC", [meta], "", 0, [], "ERROR")
        return e, _bloque("FALACIAS", [meta], "", 0, [], "ERROR")
    md, mf = [], []
    for h in m.detectar_pregunta_dirigida(question or ""):
        if not h.tipo.startswith(("AF_", "AD_", "CS_", "BC", "PQ_", "EQ_")):
            md.append({"tipo": h.tipo, "estado": "DETECTADA" if h.severidad == "hard" else "POSIBLE",
                       "evidencia": {"origen": "question", "fragmento": h.fragmento}})
    for t in textos:
        for h in m.detectar_post_hoc(t["texto"]):
            md.append({"tipo": h.tipo, "estado": "DETECTADA" if h.severidad == "hard" else "POSIBLE",
                       "evidencia": {"origen": t["origen"], "fragmento": h.fragmento}})
        for h in m.detectar_falacias(t["texto"]):
            mf.append({"tipo": h.tipo, "estado": "DETECTADA" if h.severidad == "hard" else "POSIBLE",
                       "evidencia": {"origen": t["origen"], "fragmento": h.fragmento, "patron": h.patron}})
    b1 = _bloque("PREGUNTA_DIRIGIDA_POST_HOC", [meta], "pregunta (P∧O, dirigida) + post hoc en cada texto", len(textos) + 1, md,
                 "MARCA" if md else "LIMPIO")
    b2 = _bloque("FALACIAS", [meta], "clasificador de falacias 0.5.1 (AF, AD, CS, BC1, BC2, PQ, EQ) en cada texto", len(textos), mf,
                 "MARCA" if mf else "LIMPIO")
    return b1, b2


# ------------------------------------------------------------------ 5) Copi
def g_copi(base, textos, motor, pred):
    m, meta = _cargar(base, "guardian_logica_copi_v1.py", "g_copi")
    if m is None:
        return _bloque("LOGICA_COPI", [meta], "", 0, [], "ERROR")
    r = m.guardian([t["texto"] for t in textos], motor, pred)
    return _bloque("LOGICA_COPI", [meta], "condicionales/causales del texto + regla de cierre del motor + cadena del top1",
                   r["n_revisados"], r["marcas"], r["bandera"], {k: v for k, v in r.items() if k not in ("marcas", "bandera", "n_revisados")})


# ------------------------------------------------------------------ 6) polaridad
def g_polaridad(base, textos):
    m, meta = _cargar(base, "plugin_polaridad_causal.py", "g_polaridad")
    if m is None:
        return _bloque("POLARIDAD_CAUSAL", [meta], "", 0, [], "ERROR")
    marcas, cuenta = [], {}
    for t in textos:
        r = m.clasificar_polaridad_causal(t["texto"])
        et = r.get("etiqueta")
        cuenta[et] = cuenta.get(et, 0) + 1
        if et in ("NIEGA", "DOBLE_NEGACION_LITOTE"):
            marcas.append({"tipo": et, "estado": "LATENTE" if et == "DOBLE_NEGACION_LITOTE" else "DETECTADA",
                           "evidencia": {"origen": t["origen"], "texto": t["texto"][:200], "motivo": r.get("motivo")}})
    bandera = "LATENTE" if any(x["estado"] == "LATENTE" for x in marcas) else ("MARCA" if marcas else "LIMPIO")
    return _bloque("POLARIDAD_CAUSAL", [meta], "polaridad del claim causal en cada texto (negación simple vs litote)", len(textos),
                   marcas, bandera, {"conteo": cuenta})


# ------------------------------------------------------------------ 7) hombre de acero
def g_acero(base, case, pred, latentes):
    orig, meta1 = _cargar(base, "sidecar_ablacion_hombre_acero.py", "g_acero_orig")
    riv, meta2 = _cargar(base, "guardian_acero_rival_v1.py", "g_acero_rival")
    marcas, det = [], {}
    if riv is not None:
        r = riv.acero_rival(pred, extra_rivales=latentes)
        det["steelman_rival"] = r
        for pr in r.get("pruebas") or []:
            if pr["veredicto_top1"] != "SOBREVIVE":
                marcas.append({"tipo": f"TOP1_{pr['veredicto_top1']}_ANTE_ACERO_DE_{pr['rival']}",
                               "estado": "DETECTADA" if pr["veredicto_top1"] == "CAE" else "NO_RESUELTO", "evidencia": pr})
    if orig is not None and riv is not None:
        piezas = riv.evidencia_pilares_H(case, pred)
        n_cuts = len(case.get("cuts") or [])
        n_persist = max(1, min(4, n_cuts - 1))
        last = (case.get("cuts") or [{}])[-1]
        ztoks = [str(t) for e in ("P", "A", "C") for t, _ in (last.get(e) or [])]
        rep = orig.ablar_hombre_acero(piezas, n_persist=n_persist, board_z_tokens=ztoks)
        det["ablacion_pilares_H"] = {"veredicto": rep.get("veredicto"), "n_persist": n_persist, "piezas": piezas,
                                     "seleccion": rep.get("seleccion"), "detalle": rep.get("veredicto_detalle")}
        if str(rep.get("veredicto", "")).startswith("fragil"):
            # Observación, no marca: con 1-3 tokens a favor la ablación sale frágil casi siempre
            # (14/14 en los 7 casos, aciertos incluidos); se registra pero no levanta la bandera.
            marcas.append({"tipo": "OBS_H1_" + str(rep.get("veredicto")).upper().replace("-", "_"), "estado": "OBSERVACION",
                           "evidencia": {"n_piezas": len(piezas), "veredicto": rep.get("veredicto_detalle")}})
    bandera = ("MARCA" if any(x["estado"] == "DETECTADA" for x in marcas)
               else ("NO_RESUELTO" if any(x["estado"] == "NO_RESUELTO" for x in marcas) else "LIMPIO"))
    if riv is None and orig is None:
        bandera = "ERROR"
    return _bloque("HOMBRE_DE_ACERO", [meta1, meta2], "mejor versión de cada rival (H2, 2 siguientes y frentes latentes) + ablación de pilares de H1",
                   len((det.get("steelman_rival") or {}).get("pruebas") or []) + (1 if "ablacion_pilares_H" in det else 0), marcas, bandera, det)


# ------------------------------------------------------------------ 8) Sherlock / método de rigor
def g_rigor(base, motor, pred):
    m, meta = _cargar(base, "plugin_metodo_rigor.py", "g_rigor")
    if m is None:
        return _bloque("SHERLOCK_RIGOR", [meta], "", 0, [], "ERROR")
    cadena = [((c.get("P_top5_ANEXO") or [[None]])[0][0]) for c in motor.get("cuts") or []]
    cands = pred.get("candidates") or []
    top1 = cands[0]["family"] if cands else ""
    r = m.rigor({"cadena_top1": " → ".join(str(x) for x in cadena)}, hipotesis=str(top1))
    marcas = [{"tipo": f.split(":")[0], "estado": "DETECTADA", "evidencia": {"linea": f, "cadena_top1": cadena}} for f in r.get("auto") or []]
    own = ((pred.get("own_evidence") or {}).get(top1) or {})
    if top1 and not own.get("favor_tokens"):
        marcas.append({"tipo": "HOLMES_TOP1_SIN_TOKENS_DE_HECHO", "estado": "DETECTADA",
                       "evidencia": {"top1": top1, "own_evidence": own}})
    def _masa(v):  # own_evidence trae masa por corte (lista) o escalar
        if isinstance(v, (list, tuple)):
            return float(sum(float(x or 0) for x in v))
        return float(v or 0)
    fm, cm = _masa(own.get("favor_mass")), _masa(own.get("contra_mass"))
    if top1 and cm > fm:
        marcas.append({"tipo": "SCHOPENHAUER_TABLERO_EN_CONTRA", "estado": "DETECTADA",
                       "evidencia": {"top1": top1, "favor_mass_total": round(fm, 4), "contra_mass_total": round(cm, 4)}})
    return _bloque("SHERLOCK_RIGOR", [meta], "cadena_top1 por corte (Hecate) + tokens de hecho del top1 (Holmes) + tablero en contra (Schopenhauer)",
                   len(cadena), marcas, "MARCA" if marcas else "LIMPIO", {"salida_plugin": r})


# ------------------------------------------------------------------ 9) tropos (Beristáin), vecino de falacias y Copi
def g_tropos(base, case, question, textos, vecinos):
    m, meta = _cargar(base, "guardian_tropos_beristain_v1.py", "g_tropos")
    if m is None:
        return _bloque("TROPOS_BERISTAIN", [meta], "", 0, [], "ERROR")
    tokens = sorted({str(t) for c in case.get("cuts") or [] for e in ("P", "A", "C") for t, _ in (c.get(e) or [])})
    r = m.guardian(textos, question=question, tokens_tablero=tokens, mapa_caso=case.get("tropos_mapa_caso"))
    corr = m.corregir_con_vecinos(r, vecinos)
    marcas = list(r["marcas"])
    for c in corr:
        if c["estado"] == "NO_RESUELTO":
            marcas.append({"tipo": f"VECINO_{c['vecino']}_SOBRE_FIGURA:{c['tropo']}", "estado": "NO_RESUELTO",
                           "evidencia": {"origen": c["origen"], "fragmento": c["fragmento"], "tipo_vecino": c["tipo_vecino"], "lectura": c["lectura"]}})
    bandera = m.bandera_de(marcas)
    det = {k: v for k, v in r.items() if k not in ("marcas", "bandera", "n_revisados")}
    det["correcciones_vecinos"] = corr
    return _bloque("TROPOS_BERISTAIN", [meta], "pregunta y textos de entrada: lenguaje figurado que no debe leerse literal (Beristáin)",
                   r["n_revisados"], marcas, bandera, det)


def _anotar_vecinos(bloques):
    """Anota (sin cambiar banderas) en FALACIAS/COPI/POST HOC/POLARIDAD la corrección que viene de TROPOS."""
    tb = next((b for b in bloques if b["guardian"] == "TROPOS_BERISTAIN"), None)
    if not tb:
        return
    for c in (tb.get("detalle") or {}).get("correcciones_vecinos") or []:
        for b in bloques:
            if b["guardian"] != c["vecino"]:
                continue
            for mv in b.get("marcas") or []:
                if mv.get("tipo") == c["tipo_vecino"]:
                    mv.setdefault("correccion_vecino_tropos", []).append({"tropo": c["tropo"], "estado": c["estado"], "lectura": c["lectura"]})


# ------------------------------------------------------------------ ruta de cierre latente (NO_RESUELTO / doble negación → LATENTE)
def _corte_de_origen(origen, motor):
    mm = re.match(r"cuts\[(\d+)\]", str(origen or ""))
    cuts = motor.get("cuts") or []
    if mm and int(mm.group(1)) < len(cuts):
        return int(mm.group(1)), str(cuts[int(mm.group(1))].get("corte"))
    return None, None


def _fragmento(ev):
    if isinstance(ev, dict):
        for k in ("fragmento", "texto", "linea"):
            if ev.get(k):
                return str(ev[k])[:200], ev.get("origen")
        resumen = {k: ev[k] for k in list(ev)[:4] if not isinstance(ev[k], (dict, list))}
        return json.dumps(resumen, ensure_ascii=False)[:200], ev.get("origen")
    if isinstance(ev, list):
        return "; ".join(str(x) for x in ev)[:200], None
    return str(ev)[:200], None


def ruta_cierre_latente(bloques, case, motor, pred, base):
    """Todo dato es un dato; lo que no se entiende o no se sostiene NO es cierre.
    Junta NO_RESUELTO (marca o bandera) y DOBLE_NEGACION_LITOTE de cualquier guardián → motivos trazables.
    Si hay motivos: estado del cierre = LATENTE (registrado en control_latencia_decimo_hombre) y lista de
    cortes a re-medir con tortugas. No toca H1/H2/top1."""
    motivos = []
    for b in bloques:
        g = b.get("guardian")
        if g == "DECIMO_HOMBRE_LATENCIA":
            # sus cortes intermedios latentes son normales y no entran; su CIERRE latente (banda de empate) sí:
            # un cierre en empate tampoco se sostiene. Ya quedó registrado en la latencia por su propio bloque.
            for mk in b.get("marcas") or []:
                if mk.get("tipo") == "CIERRE_LATENTE_SEGUN_DECIMO_HOMBRE":
                    ev = mk.get("evidencia") or {}
                    motivos.append({"guardian": g, "tipo": "CIERRE_EN_BANDA_DE_EMPATE", "estado_marca": "LATENTE",
                                    "fragmento": json.dumps({k: ev.get(k) for k in ("top1", "top2", "gap_rank", "p_momento")}, ensure_ascii=False),
                                    "origen": None, "corte_idx": None, "corte": None, "alcance": "CIERRE"})
            continue
        propias = [mk for mk in b.get("marcas") or [] if mk.get("estado") == "NO_RESUELTO" or mk.get("tipo") == "DOBLE_NEGACION_LITOTE"]
        for mk in propias:
            frag, org = _fragmento(mk.get("evidencia"))
            idx, corte = _corte_de_origen(org, motor)
            motivos.append({"guardian": g, "tipo": mk.get("tipo"), "estado_marca": mk.get("estado"), "fragmento": frag,
                            "origen": org, "corte_idx": idx, "corte": corte,
                            "alcance": "CORTE" if idx is not None else "CIERRE"})
        if not propias and b.get("bandera") == "NO_RESUELTO":
            motivos.append({"guardian": g, "tipo": "BANDERA_NO_RESUELTO", "estado_marca": "NO_RESUELTO", "fragmento": None,
                            "origen": None, "corte_idx": None, "corte": None, "alcance": "CIERRE"})
    cuts = motor.get("cuts") or []
    cortes_idx = sorted({m["corte_idx"] for m in motivos if m["corte_idx"] is not None})
    if any(m["alcance"] == "CIERRE" for m in motivos) and cuts:
        cortes_idx = sorted(set(cortes_idx) | {len(cuts) - 1})
    out = {"regla": "todo dato es un dato; lo que no se entiende o no se sostiene NO es cierre",
           "estado_cierre": "LATENTE" if motivos else "SIN_OBJECION_DE_GUARDIANES",
           "n_motivos": len(motivos), "motivos": motivos,
           "guardianes_que_objetan": sorted({m["guardian"] for m in motivos}),
           "cortes_a_remedir_idx": cortes_idx, "cortes_a_remedir": [str(cuts[i].get("corte")) for i in cortes_idx],
           "can_decide_H": False, "toca_H1_H2_top1": False}
    if not motivos:
        return out
    lat, meta = _cargar(base, "control_latencia_decimo_hombre.py", "g_ctrl_lat_cierre")
    if lat is None:
        out["latencia"] = {"status": "ERROR", "motivo": "control_latencia_decimo_hombre.py ausente"}
        return out
    store = Path(base) / f"estado_latencia_cierre_guardianes__{re.sub(r'[^A-Za-z0-9_]+', '_', str(case.get('case_id')))}.json"
    if store.exists():
        store.unlink()
    toks = [f"{m['guardian']}:{m['tipo']}" for m in motivos if m["guardian"] != "DECIMO_HOMBRE_LATENCIA"] or ["DECIMO_HOMBRE_LATENCIA:CIERRE_EN_BANDA_DE_EMPATE"]
    r = lat.actualizar_expediente(f"{case.get('case_id')}::cierre_por_guardianes", tema="cierre_no_resuelto_por_guardian",
                                  p_momento=0.5, tokens_nuevos=toks, forzar_desempate_si_empate=False, store_path=store)
    ex = {k: v for k, v in r["expediente"].items() if k != "actualizado_ts"}
    try:
        store.unlink()
    except OSError:
        pass
    out["latencia"] = {"capa": r.get("capa"), "pieza": meta, "accion": r.get("accion"), "expediente": ex,
                       "nota": "p=0.5 fijo (no se sabe) y sin re-tirada del décimo hombre: un NO_RESUELTO no es un empate numérico"}
    return out


def correr_guardianes(case: Dict[str, Any], motor: Dict[str, Any], pred: Dict[str, Any], base: Path) -> Dict[str, Any]:
    base = Path(base)
    textos = textos_de_entrada(case)
    question = str(case.get("question") or "")
    bloques = []

    def seguro(nombre, fn):
        try:
            r = fn()
            return r if isinstance(r, tuple) else (r,)
        except Exception as e:  # un guardián que truena no detiene la corrida
            return (_bloque(nombre, [], "", 0, [], "ERROR", {"error": f"{type(e).__name__}: {e}"}),)

    dh = seguro("DECIMO_HOMBRE_LATENCIA", lambda: g_decimo_hombre(base, case, motor, pred))[0]
    bloques.append(dh)
    bloques.extend(seguro("PREGUNTA_DETRAS_V2", lambda: g_detras(base, question, textos)))
    bloques.extend(seguro("PREGUNTA_DIRIGIDA_POST_HOC", lambda: g_dirigida_y_falacias(base, question, textos)))
    bloques.append(seguro("LOGICA_COPI", lambda: g_copi(base, textos, motor, pred))[0])
    bloques.append(seguro("POLARIDAD_CAUSAL", lambda: g_polaridad(base, textos))[0])
    lat_fronts = [f for f in (((pred.get("compuerta_cierre") or {}).get("latencia_escrita") or {}).get("abiertos_o_reafirmados") or [])]
    bloques.append(seguro("HOMBRE_DE_ACERO", lambda: g_acero(base, case, pred, lat_fronts))[0])
    bloques.append(seguro("SHERLOCK_RIGOR", lambda: g_rigor(base, motor, pred))[0])
    bloques = [_h(b) for b in bloques]
    vecinos = [b for b in bloques if b["guardian"] in ("FALACIAS", "PREGUNTA_DIRIGIDA_POST_HOC", "LOGICA_COPI", "POLARIDAD_CAUSAL")]
    bloques.append(_h(seguro("TROPOS_BERISTAIN", lambda: g_tropos(base, case, question, textos, vecinos))[0]))
    _anotar_vecinos(bloques)
    banderas = {b["guardian"]: b["bandera"] for b in bloques}
    acero = next((b for b in bloques if b["guardian"] == "HOMBRE_DE_ACERO"), {})
    copi = next((b for b in bloques if b["guardian"] == "LOGICA_COPI"), {})
    sug = []
    if banderas.get("DECIMO_HOMBRE_LATENCIA") == "LATENTE":
        sug.append("decimo_hombre: cierre en banda de empate")
    if any(m["tipo"].startswith("TOP1_") for m in acero.get("marcas", [])):
        sug.append("acero: el top1 no sobrevive (o empata) ante la mejor versión de un rival")
    if any("SUBDETERMINACION" in m["tipo"] for m in copi.get("marcas", [])):
        sug.append("copi: H1/H2 subdeterminados por la cadena")
    tb = next((b for b in bloques if b["guardian"] == "TROPOS_BERISTAIN"), {})
    if tb.get("bandera") == "NO_RESUELTO":
        sug.append("tropos: lenguaje figurado sin frontera clara en la pregunta o los textos")
    try:
        ruta = ruta_cierre_latente(bloques, case, motor, pred, base)
    except Exception as e:
        ruta = {"estado_cierre": "ERROR", "error": f"{type(e).__name__}: {e}", "can_decide_H": False}
    return {"version": VERSION, "tipo": "PRUEBAS_DE_CONTROL_ESTRUCTURAL", **CANDADOS, "ruta_cierre_latente": ruta,
            "n_textos_entrada": len(textos), "textos_entrada": textos, "bloques": bloques, "banderas": banderas,
            "convergencia": {"n_guardianes": len(bloques),
                             "n_con_marca": sum(1 for v in banderas.values() if v in ("MARCA", "NO_RESUELTO", "LATENTE")),
                             "cortes_latentes": (next((b for b in bloques if b["guardian"] == "DECIMO_HOMBRE_LATENCIA"), {}).get("detalle") or {}).get("cortes_latentes", []),
                             "sugerencia_control_latente": bool(sug), "motivos": sug,
                             "nota": "Sugerencia de control, no decisión: H1/H2 y el estado del motor no se tocan."}}
