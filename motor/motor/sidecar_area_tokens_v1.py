#!/usr/bin/env python3
"""AREA DE TOKENS (PATCH 010a): registro taxonomy-ready de familias de tokens dispersas en plugins
+ activación por corte desde input real + coactivaciones. Solo lectura. can_decide_H=False. No toca el 244.

Diseño taxonómico (Mj 2026-10-06 03:35/03:38):
  matriz superior de patrones por MATERIA (económico, histórico, político, psicológico, biológico/salud,
  ocupacional, narrativo...) -> familias con tokens + reglas de interrelación, alimentada por StinkBox;
  los 244 se derivan de ella y alimentan Caldero; Caldero corre junto a la geometría sobre los cortes hasta
  la Z (freeze = Z de trabajo); luego inercia/traza -> hipótesis y apuesta.
  Regla LUCES: una familia activa ILUMINA familias relacionadas (pauta / sube su prior de atención) pero NO
  las enciende. Los EJES (social, político, histórico, físico, biológico, mental) se mantienen separados.
Cada familia registrada aquí trae: familia_id, origen (archivo+símbolo), tokens, reino/familia propuestos,
materia, ejes, ilumina (con regla), canales de activación. Migrar el 244 a la taxonomía = MOVER estas
entradas, no reescribirlas. Este módulo NO cambia el catálogo: las familias "vista_244" leen sus tokens del
catálogo cargado en tiempo de ejecución.

Canales de activación (todos trazables, nada inventado):
  PAC_exacto   : token del corte (P/A/C del input) == token de la familia.
  alias_texto  : plugin_alias_reactivacion.ALIAS (palabra completa) sobre TEXTOS ADMITIDOS por el sombrero
                 blanco de entrada (hecho/narracion; nunca source_note).
  texto_raiz   : SOLO familia cuerpo_arco: raíces explícitas (tabla RAICES_CUERPO) sobre textos admitidos,
                 con negación local y separación muerte propia / muerte ajena.
"""
from __future__ import annotations
import re
import unicodedata
from collections import defaultdict
from typing import Any, Dict, List

VERSION = "AREA_TOKENS_V1_PATCH010"
EJES = ("social", "politico", "historico", "fisico", "biologico", "mental")

# --------------------------------------------------------------------------- canal texto_raiz (cuerpo_arco)
RAICES_CUERPO = {
    "cuerpo_enfermedad": r"\b(enferm\w*|dolencia\w*|padeci\w*)",
    "cuerpo_herida": r"\b(herid[oa]s?|lesionad[oa]s?|lesi[oó]n)\b",
    "cuerpo_agonia": r"\b(agon[ií]a\w*|agoniza\w*|lecho\s+de\s+muerte)",
    "cuerpo_muerte_propia": r"\b(muere|muri[oó]|muerte|fallece\w*|falleci\w*)\b",
    "cuerpo_desgaste": r"\b(desgast\w*|agotamiento|extenuad\w*|exhaust\w*)",
    "salud_recuperacion": r"\b(se\s+recupera\w*|recuperaci[oó]n)\b",
}
NEG_RE = re.compile(r"(?i)\b(no|sin|nunca|jam[aá]s)\s+(\w+\s+){0,2}$")
# "muerte de Anna Maria ..."/"muere su padre" = muerte AJENA (no es cuerpo_muerte_propia del sujeto)
AJENA_RE = re.compile(r"(?i)^\s*(de\s+(su|sus|la|el|los|las)?\s*[A-ZÁÉÍÓÚÑa-záéíóúñ]|su\s+(padre|madre|hij|espos|herman|mujer|marido))")


def _fold(s: str) -> str:
    return "".join(ch for ch in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(ch) != "Mn")


def _clausulas(texto: str) -> List[str]:
    return [x.strip() for x in re.split(r"[;\.\n]", texto or "") if x.strip()]


def tokens_cuerpo_desde_texto(texto: str) -> List[Dict[str, Any]]:
    out = []
    for cl in _clausulas(texto):
        tiene_cuerpo = any(re.search(rx, cl, re.I) for k, rx in RAICES_CUERPO.items() if k != "salud_recuperacion")
        for tok, rx in RAICES_CUERPO.items():
            for m in re.finditer(rx, cl, re.I):
                if NEG_RE.search(cl[:m.start()]):
                    out.append({"token": tok, "descartado": "negacion_local", "cita": cl[:160]}); continue
                if tok == "salud_recuperacion" and not tiene_cuerpo:
                    out.append({"token": tok, "descartado": "recuperacion_sin_contexto_corporal", "cita": cl[:160]}); continue
                if tok == "cuerpo_muerte_propia" and AJENA_RE.match(cl[m.end():]):
                    out.append({"token": "muerte_ajena", "descartado": "muerte_de_otra_persona (no es muerte propia; ilumina duelo)", "cita": cl[:160]}); continue
                out.append({"token": tok, "match": m.group(0), "cita": cl[:160]})
                break
    return out


def tokens_alias_desde_texto(texto: str, alias: Dict[str, str]) -> List[Dict[str, Any]]:
    out, f = [], _fold(texto or "")
    for needle, canon in sorted(alias.items()):
        if re.search(r"\b" + re.escape(_fold(needle)) + r"\b", f):
            i = re.search(r"\b" + re.escape(_fold(needle)) + r"\b", f).start()
            out.append({"token": canon, "alias": needle, "cita": (texto or "")[max(0, i - 60): i + 60]})
    return out


# --------------------------------------------------------------------------- registro taxonomy-ready
def _vista(cat, pid, reino, familia, materia, ejes, escala):
    pv = (cat or {}).get(pid) or {}
    return {"familia_id": f"{familia}.{pid}", "origen": {"tipo": "vista_244", "archivo": "patterns_final_v14.json", "simbolo": pid,
                                                        "nota": "tokens leídos del catálogo en ejecución (el 244 NO se modifica)"},
            "tokens_favor": dict(pv.get("tokens_favor") or {}), "tokens_contra": dict(pv.get("tokens_contra") or {}),
            "reino_propuesto": reino, "familia_propuesta": familia, "materia": materia, "ejes": list(ejes), "escala": escala,
            "presente_en_catalogo": bool(pv), "ilumina": [], "canales": ["PAC_exacto", "alias_texto"]}


def construir_registro(cat: Dict[str, Any], hotel_patron: Dict[str, Any] | None, cuerpo_mod, arq_din: Dict[str, Any] | None) -> List[Dict[str, Any]]:
    R: List[Dict[str, Any]] = []
    # ---- reino cuerpo_salud_muerte
    if cuerpo_mod is not None:
        tc = dict(getattr(cuerpo_mod, "TOKENS_CODIGO", {}))
        fams = list(getattr(cuerpo_mod, "FAMILIAS", ()))
        R.append({"familia_id": "cuerpo_arco", "origen": {"tipo": "plugin", "archivo": "sidecar_cuerpo_arco__BUG_A_SIN_CONFIRMAR.py", "simbolo": "TOKENS_CODIGO/FAMILIAS",
                                                          "otras_funciones_en_codigo": ["analizar_cadena (desgaste→enfermedad|herida→agonía→muerte_propia)", "voto_caldero_cuerpo (RUIDO si cuerpo t-1 vacío)",
                                                                                         "monomito_etiqueta (Q3/Q4 laterales, suma_a_p=False)", "aquiles_sensibilidad (¿cae el eje de oficio sin cuerpo?)",
                                                                                         "h1_prohibido (muerte_propia nunca H1)"]},
                  "tokens_favor": {k: v for k, v in tc.items() if k not in getattr(cuerpo_mod, "CONTRA", set())},
                  "tokens_contra": {k: v for k, v in tc.items() if k in getattr(cuerpo_mod, "CONTRA", set())},
                  "subfamilias_propuestas": {fams[0] if fams else "cuerpo_desgaste_agente": ["cuerpo_desgaste", "cuerpo_enfermedad", "cuerpo_herida"],
                                             fams[1] if len(fams) > 1 else "cuerpo_inhabilita": ["cuerpo_agonia", "cuerpo_muerte_propia"],
                                             "salud_aparte": ["salud_recuperacion"], "salud_contra": ["salud_estable"]},
                  "nota_subfamilias": "el sidecar declara las 2 familias pero no asigna tokens a cada una: asignación = PROPUESTA",
                  "reino_propuesto": "cuerpo_salud_muerte", "familia_propuesta": "cuerpo_arco", "materia": "biologico_salud", "ejes": ["biologico", "fisico"], "escala": "micro",
                  "en_vocabulario_244": {k: False for k in tc}, "ilumina": [], "canales": ["PAC_exacto", "texto_raiz"]})
    for pid in sorted(k for k in (cat or {}) if k.startswith("sustancias_")):
        R.append(_vista(cat, pid, "cuerpo_salud_muerte", "consumo_sustancias", "biologico_salud", ["biologico", "mental"], "micro"))
    for pid in sorted(k for k in (cat or {}) if k.startswith("duelo_bonanno_") or k == "candidato_trayectoria_supervivencia_actuarial"):
        R.append(_vista(cat, pid, "cuerpo_salud_muerte", "muerte_duelo", "psicologico" if pid.startswith("duelo") else "biologico_salud",
                        ["mental", "social"] if pid.startswith("duelo") else ["biologico", "social"], "micro"))
    # ---- reino ocupacional (trayectorias de riesgo tipo arquetipo)
    if hotel_patron:
        R.append({"familia_id": "oficio_riesgo." + str(hotel_patron.get("id", "trayectoria_hosteleria")),
                  "origen": {"tipo": "plugin", "archivo": "plugin_trayectoria_hosteleria.py", "simbolo": "PATRON", "nota": "docstring: misma familia que musicos / policia / trailer"},
                  "tokens_favor": dict(hotel_patron.get("tokens_favor") or {}), "tokens_contra": dict(hotel_patron.get("tokens_contra") or {}),
                  "reino_propuesto": "ocupacional", "familia_propuesta": "oficio_riesgo", "materia": "ocupacional_sociolaboral", "ejes": ["social", "biologico", "mental"], "escala": "meso",
                  "presente_en_catalogo": hotel_patron.get("id") in (cat or {}), "ilumina": [], "canales": ["PAC_exacto", "alias_texto"]})
    for pid in sorted(k for k in (cat or {}) if k.startswith("trayectoria_") or re.match(r"candidato_(alto_)?riesgo_", k)):
        R.append(_vista(cat, pid, "ocupacional", "oficio_riesgo", "ocupacional_sociolaboral", ["social", "biologico", "mental"], "meso"))
    # ---- reino arquetipos (plugin disperso)
    for pid, pv in sorted((arq_din or {}).items()):
        R.append({"familia_id": f"arquetipos_dinamicos.{pid}", "origen": {"tipo": "plugin", "archivo": "plugin_arquetipos_dinamicos.py", "simbolo": f"ARQUETIPOS_DINAMICOS[{pid}]"},
                  "tokens_favor": dict(pv.get("tokens_favor") or {}), "tokens_contra": dict(pv.get("tokens_contra") or {}),
                  "reino_propuesto": "arquetipos", "familia_propuesta": str(pv.get("subapendice") or "arquetipos_dinamicos"), "materia": "psicologico_narrativo",
                  "ejes": ["mental", "social"], "escala": "meso", "presente_en_catalogo": pid in (cat or {}), "ilumina": [], "canales": ["PAC_exacto"]})
    # ---- vocabulario e ILUMINA (regla de luces: pauta, no encendido)
    voc = set()
    for pv in (cat or {}).values():
        voc |= set(pv.get("tokens_favor") or {}) | set(pv.get("tokens_contra") or {})
    favor = {r["familia_id"]: set(r["tokens_favor"]) for r in R}
    ids = [r["familia_id"] for r in R]
    explicit = {
        "cuerpo_arco": ["muerte_duelo.*", "consumo_sustancias.*", "oficio_riesgo.trayectoria_sedentarismo_cardiovascular", "oficio_riesgo.trayectoria_sobrecarga_horas_karoshi",
                        "oficio_riesgo.candidato_riesgo_operativo_salud_y_medicos"],
        "oficio_riesgo.trayectoria_hosteleria_turno_sustancias": ["oficio_riesgo.trayectoria_musicos_populares", "oficio_riesgo.trayectoria_policia_alcohol_ptds",
                                                                    "oficio_riesgo.trayectoria_transportistas_turno_nocturno", "consumo_sustancias.*"],
    }
    for r in R:
        r["en_vocabulario_244"] = {t: (t in voc) for t in sorted(set(r["tokens_favor"]) | set(r["tokens_contra"]))}
        il = []
        for pat in explicit.get(r["familia_id"], []):
            for j in ids:
                if j != r["familia_id"] and (j == pat or (pat.endswith(".*") and j.startswith(pat[:-1]))):
                    il.append({"familia": j, "regla": "explicita_en_codigo_o_propuesta_Mj"})
        for j in ids:
            if j != r["familia_id"] and favor[r["familia_id"]] & favor[j] and not any(x["familia"] == j for x in il):
                il.append({"familia": j, "regla": "comparten_token_favor", "tokens": sorted(favor[r["familia_id"]] & favor[j])})
        r["ilumina"] = sorted(il, key=lambda x: x["familia"])
    return R


# --------------------------------------------------------------------------- activación + coactivación
def activar(registro, case_cuts, motor_cuts, textos_admitidos, alias, puente_toks, coact_mod) -> Dict[str, Any]:
    textos_por_corte = defaultdict(list)
    for t in textos_admitidos or []:
        textos_por_corte[str(t.get("corte"))].append(t.get("texto") or "")
    p5 = {str(c.get("id") or c.get("corte")): [x[0] if isinstance(x, (list, tuple)) else (x.get("familia") if isinstance(x, dict) else x)
                                             for x in (c.get("P_top5_ANEXO") or [])] for c in motor_cuts or []}
    tok_fam = defaultdict(set)
    for r in registro:
        for t in set(r["tokens_favor"]) | set(r["tokens_contra"]):
            tok_fam[t].add(r["familia_id"])
    esc = {r["familia_id"]: r.get("escala", "meso") for r in registro}
    por_corte, cuerpo_cuts, resumen = [], [], defaultdict(lambda: {"cortes": [], "tokens": set()})
    for c in case_cuts or []:
        cid = str(c.get("id"))
        obs = {}
        for e in ("P", "A", "C"):
            for t, w in c.get(e) or []:
                obs[str(t)] = max(obs.get(str(t), 0.0), float(w))
        acts, descartes = [], []
        for t in sorted(obs):
            for f in sorted(tok_fam.get(t, ())):
                acts.append({"familia": f, "token": t, "canal": "PAC_exacto", "polaridad": "favor" if t in next(r for r in registro if r["familia_id"] == f)["tokens_favor"] else "contra"})
        txt = " ".join(textos_por_corte.get(cid, []))
        for a in tokens_alias_desde_texto(txt, alias or {}):
            for f in sorted(tok_fam.get(a["token"], ())):
                if not any(x["familia"] == f and x["token"] == a["token"] for x in acts):
                    acts.append({"familia": f, "token": a["token"], "canal": "alias_texto", "alias": a["alias"], "cita": a["cita"], "polaridad": "favor"})
        cuerpo_toks = []
        for a in tokens_cuerpo_desde_texto(txt):
            if a.get("descartado"):
                descartes.append(a); continue
            cuerpo_toks.append(a["token"])
            if not any(x["token"] == a["token"] for x in acts):
                acts.append({"familia": "cuerpo_arco", "token": a["token"], "canal": "texto_raiz", "match": a["match"], "cita": a["cita"],
                             "polaridad": "contra" if a["token"] == "salud_estable" else "favor"})
        cuerpo_toks += [t for t in obs if t.startswith(("cuerpo_", "salud_")) and t not in cuerpo_toks]
        cuerpo_cuts.append({"id": c.get("id"), "tokens": sorted(set(cuerpo_toks)), "caldero_cuerpo": sorted(set(cuerpo_toks))})
        fams_act = sorted({a["familia"] for a in acts})
        for a in acts:
            resumen[a["familia"]]["cortes"].append(cid); resumen[a["familia"]]["tokens"].add(a["token"])
        # coactivación con la maquinaria existente (coactivacion_escalas.analizar_corte, tal cual):
        # PUENTE (11 familias) + familias del área como dinámica "otra/propia" con su escala.
        obs_aug = dict(obs)
        for a in acts:
            obs_aug.setdefault(a["token"], 0.78)
        area_toks = [{"familia": "AREA:" + a["familia"], "token": a["token"], "D": "otra/propia", "E": esc.get(a["familia"], "meso"),
                      "pol": "empuja" if a["polaridad"] == "favor" else "frena", "words": {a["token"]}} for a in acts]
        co = coact_mod.analizar_corte(obs_aug, list(puente_toks) + area_toks) if coact_mod is not None else {}
        puente_lit = sorted({k.split(":")[0] for D, r in co.items() for E in (r.get("detalle") or {}).values()
                             for k in list(E["tokens_empuja"]) + list(E["tokens_frena"]) if not k.startswith("AREA:")})
        coact_area = [{"dinamica": D, "estado": r["estado"], "escalas": r["escalas_encendidas"]} for D, r in co.items() if r.get("estado") != "apagada"]
        pares = sorted({(a, b) for i, a in enumerate(fams_act) for b in fams_act[i + 1:]})
        il = []
        for f in fams_act:
            reg = next(r for r in registro if r["familia_id"] == f)
            for x in reg["ilumina"]:
                pid = x["familia"].split(".", 1)[-1]
                il.append({"desde": f, "ilumina": x["familia"], "regla": x["regla"], "familia_en_P_top5_del_corte": pid in p5.get(cid, []),
                           "encendida_en_area": x["familia"] in fams_act, "efecto": "pauta (no enciende)"})
        por_corte.append({"corte": cid, "activaciones": acts, "descartes_texto": descartes, "familias_area_activas": fams_act,
                          "coactivacion_area_x_area": [list(p) for p in pares],
                          "coactivacion_escalas": coact_area, "familias_puente_encendidas_en_el_corte": puente_lit,
                          "familias_P_top5_del_corte": p5.get(cid, []), "iluminacion": il})
    return {"por_corte": por_corte, "cuerpo_cuts": cuerpo_cuts,
            "resumen_por_familia": {f: {"cortes": sorted(set(v["cortes"]), key=lambda x: [int(s) if s.isdigit() else s for s in re.split(r"(\d+)", x)]),
                                        "tokens": sorted(v["tokens"])} for f, v in sorted(resumen.items())}}


MIGRAR_DESPUES = [
    {"plugin": "plugin_trayectoria_hosteleria.py", "simbolo": "PATRON", "destino": "ocupacional/oficio_riesgo", "registrado_010": True},
    {"plugin": "sidecar_cuerpo_arco__BUG_A_SIN_CONFIRMAR.py", "simbolo": "TOKENS_CODIGO/FAMILIAS", "destino": "cuerpo_salud_muerte/cuerpo_arco", "registrado_010": True},
    {"plugin": "plugin_arquetipos_dinamicos.py", "simbolo": "ARQUETIPOS_DINAMICOS", "destino": "arquetipos/{psicologia_caos,morfologia_trama}", "registrado_010": True},
    {"plugin": "plugin_otto_numinoso.py", "simbolo": "OTTO", "destino": "religioso_sacro/numinoso", "registrado_010": False},
    {"plugin": "plugin_embudo_clinico.py", "simbolo": "CLINICO / CO_OFICIO", "destino": "cuerpo_salud_muerte/clinico + ocupacional", "registrado_010": False},
    {"plugin": "familias_gloria_sacro (hub sensores_pre)", "simbolo": "EXTRA", "destino": "religioso_sacro/gloria", "registrado_010": False},
    {"plugin": "plugin_alias_reactivacion.py", "simbolo": "ALIAS", "destino": "capa de sinónimos texto→token (no es familia; regla de entrada)", "registrado_010": "usado como canal"},
    {"plugin": "dynamis_dramatica_sistemica (catálogo)", "simbolo": "catálogo dynamis", "destino": "dinamicas_sistemicas", "registrado_010": False},
    {"plugin": "plugin_cameo_institucional / cameo_to_703", "simbolo": "codebook CAMEO", "destino": "geopolitico/relaciones_guerra (CAMEO)", "registrado_010": False},
    {"plugin": "familias_tokens/*.json (11)", "simbolo": "tokens_favor/contra + PUENTE_244_FAMILIAS.json", "destino": "ya normalizadas: mover tal cual (D1..D8 / micro-meso-macro)", "registrado_010": "ya en PUENTE"},
    {"plugin": "arcos_emocionales / capa2 (Bus Capa 2)", "simbolo": "catálogos internos", "destino": "narrativo/arcos", "registrado_010": False},
]
