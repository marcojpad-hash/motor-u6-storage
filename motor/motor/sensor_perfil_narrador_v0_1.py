#!/usr/bin/env python3
"""SENSOR_PERFIL_NARRADOR v0.1 — lectura en negativo del lente de quien escribe el input.

EXTENSIÓN de piezas existentes (no las duplica; las importa desde su ruta original, solo lectura):
  - plugin_pregunta_detras_v2 v2.3.2 (sandbox)  -> marcajes FENOMENO_CAMPO / ETIQUETA_SUJETO / MARCO_EVALUATIVO (hechos vs juicio)
  - plugin_pregunta_dirigida 0.5.0 (sandbox)    -> falacias AF/AD/CS/BC1/BC2/PQ/EQ + post_hoc + P∧O (estructura lógica)
  - plugin_polaridad_causal 1.0.0 (TRANSFER)    -> polaridad de claims causales
  - control_latencia_decimo_hombre 1.0.0        -> banda de empate ~50%: si un lente no domina -> LATENCIA (no se afirma ciego)
                                                   y décimo hombre = lectura inversa de cada lente dominante
  - plugin_guardia_no_cruce (TRANSFER)          -> valida que la salida no traiga campos probabilísticos
  - EQUIVALENCIAS_ESCALA_20260927 (matriz + puente 244) -> escala persona/grupo/Estado y polaridad empuja/frena
  - las mismas preguntas generadas se pasan por detras_v2 y dirigida como guardia anti-pregunta-dirigida.

Lo NUEVO (la brecha): medir el lente del narrador en 6 dimensiones, listar puntos ciegos LATENTES
(no hechos) y generar preguntas de opción múltiple con opciones simétricas en escala y polaridad.

Candados: can_decide_H=False · Alimenta_H=NO · no escribe patterns.json · no entra al ranking ·
no toca Engine/244/motor. No infiere escolaridad, lugar, origen ni demografía (no existen esas dimensiones).
"""
from __future__ import annotations
import sys, os, re, json, hashlib, importlib.util, unicodedata, collections, glob, datetime
sys.dont_write_bytecode = True  # no dejar __pycache__ en carpetas ajenas

VERSION = "SENSOR_PERFIL_NARRADOR_V0_1"
HERE = os.path.dirname(os.path.abspath(__file__))
T = "/workspace/pred_hist_bio_in/TRANSFER_V15_1"
SB = f"{T}/MOTOR_V_SUPUTAMADRE_SANDBOX"
EQ = "/workspace/EQUIVALENCIAS_ESCALA_20260927"
PIEZAS = {
    "detras_v2": (f"{SB}/plugin_pregunta_detras_v2.py", "f0b1a92b23b5744b"),
    "dirigida": (f"{SB}/plugin_pregunta_dirigida.py", "19f59a1de859fa0b"),
    "polaridad": (f"{T}/plugin_polaridad_causal.py", "534ae6366b525f51"),
    "latencia": (f"{T}/control_latencia_decimo_hombre.py", "ff03241d42d7770c"),
    "guardia": (f"{T}/plugin_guardia_no_cruce.py", "27759007f33abe57"),
}
DATOS = {
    "matriz": (f"{EQ}/MATRIZ_EQUIVALENCIAS_ESCALA.json", None),
    "puente": (f"{EQ}/PUENTE_244_FAMILIAS.json", None),
    "patterns": (f"{T}/patterns_final_v14.json", "d827dcc3882634ec"),
}
sys.path.insert(0, HERE)
import lexico_narrador_v0_1 as LX  # noqa: E402

def _sha16(p):
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()[:16]

def _load(alias, path):
    spec = importlib.util.spec_from_file_location(alias, path)
    m = importlib.util.module_from_spec(spec); sys.modules[alias] = m; spec.loader.exec_module(m); return m

def cargar_piezas():
    reg = {}
    if SB not in sys.path: sys.path.append(SB)  # dirigida resuelve su propio plugin_polaridad_causal
    mods = {}
    for k, (p, exp) in list(PIEZAS.items()) + list(DATOS.items()):
        s = _sha16(p); reg[k] = {"ruta": p, "sha16": s, "sha_esperado": exp, "coincide": (exp is None or s == exp)}
        if exp and s != exp: raise RuntimeError(f"PIEZA_CAMBIO_HASH {k}: {s} != {exp}")
    for k in PIEZAS: mods[k] = _load(f"pn_{k}", PIEZAS[k][0])
    with open(DATOS["matriz"][0], encoding="utf-8") as fh:
        mods["matriz"] = json.load(fh)
    with open(DATOS["puente"][0], encoding="utf-8") as fh:
        mods["puente"] = json.load(fh)
    with open(DATOS["patterns"][0], encoding="utf-8") as fh:
        mods["patterns"] = json.load(fh)
    return mods, reg

def norm(s):
    s = unicodedata.normalize("NFKD", str(s or "").lower())
    return "".join(ch for ch in s if not unicodedata.combining(ch))

def contar(texto_n, lista):
    return sum(len(re.findall(r"(?<![a-z0-9])" + re.escape(w) + r"(?![a-z0-9])", texto_n)) for w in lista)

def reparto(cnt, orden):
    tot = sum(cnt.get(k, 0) for k in orden)
    return tot, {k: (round(cnt.get(k, 0) / tot, 4) if tot else 0.0) for k in orden}

def estado_lente(cnt, orden, M, umbral_dom=0.60, n_min=6):
    """DOMINANTE / REPARTIDO / LATENCIA_EMPATE / SIN_DATO. La banda de empate es la del control de latencia."""
    tot, prop = reparto(cnt, orden)
    if tot < n_min: return {"estado": "SIN_DATO", "n": tot, "proporciones": prop, "dominante": None}
    rk = sorted(orden, key=lambda k: (-cnt.get(k, 0), orden.index(k)))
    a, b = cnt.get(rk[0], 0), cnt.get(rk[1], 0)
    par = a / (a + b) if (a + b) else 0.5
    if M["latencia"].en_banda_empate(par):
        return {"estado": "LATENCIA_EMPATE", "n": tot, "proporciones": prop, "dominante": None,
                "empate_entre": rk[:2], "regla": "control_latencia_decimo_hombre.en_banda_empate",
                "ausentes": [k for k in orden if cnt.get(k, 0) == 0],
                "minoritarios": [k for k in orden if 0 < prop[k] <= 0.10]}
    est = "DOMINANTE" if prop[rk[0]] >= umbral_dom else "REPARTIDO"
    return {"estado": est, "n": tot, "proporciones": prop, "dominante": rk[0], "segundo": rk[1],
            "ausentes": [k for k in orden if cnt.get(k, 0) == 0],
            "minoritarios": [k for k in orden if 0 < prop[k] <= 0.10]}

# ------------------------------------------------------------------ capa TOKENS
def capa_tokens(case, M):
    puente = M["puente"]["tokens"]
    por_palabra = collections.defaultdict(list)
    for t in puente:
        for tier in ("alta", "media"):
            for w in t["palabras_244"][tier]: por_palabra[w].append(t)
    disponibles = collections.Counter(t["escala"] for t in puente)
    disp_celda = collections.Counter((t["dinamica"], t["escala"]) for t in puente)
    nat, loc, tie, ejes = collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter()
    no_clas, por_corte, intens = set(), [], []
    esc_occ, pol_occ, fam_occ, celda_occ = collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter()
    lat_activos = set()
    for c in case["cortes"]:
        pc = {"id": c["id"], "naturaleza": collections.Counter(), "locus": collections.Counter(), "tiempo": collections.Counter(), "escala": collections.Counter()}
        for e in ("P", "A", "C"):
            for tok, w in c.get(e) or []:
                ejes[e] += 1; intens.append(float(w))
                lx = LX.TOKENS.get(tok)
                if lx is None: no_clas.add(tok)
                else:
                    nat[lx[0]] += 1; loc[lx[1]] += 1; tie[lx[2]] += 1
                    pc["naturaleza"][lx[0]] += 1; pc["locus"][lx[1]] += 1; pc["tiempo"][lx[2]] += 1
                for lt in por_palabra.get(tok, []):
                    esc_occ[lt["escala"]] += 1; pol_occ[lt["polaridad"]] += 1; fam_occ[lt["familia"]] += 1
                    celda_occ[(lt["dinamica"], lt["escala"])] += 1; pc["escala"][lt["escala"]] += 1
                    lat_activos.add((lt["familia"], lt["token"], lt["escala"]))
        por_corte.append(pc)
    act_por_escala = collections.Counter(e for _, _, e in lat_activos)
    tasa_escala = {e: round(act_por_escala.get(e, 0) / disponibles[e], 4) for e in ("micro", "meso", "macro")}
    # familias 244 (por prefijo) tocadas por algún token del input
    toks_in = {t for c in case["cortes"] for e in "PAC" for t, _ in (c.get(e) or [])}
    grupos = collections.defaultdict(lambda: [0, 0])
    for name, pat in M["patterns"].items():
        g = "polti_numerados" if name[0].isdigit() else re.sub(r"_?\d.*$", "", name)
        g = "arquetipo_el" if g.startswith("arquetipo_el_") else ("mbti" if g.startswith("mbti") else g)
        v = set(pat.get("tokens_favor") or {}) | set(pat.get("tokens_contra") or {})
        grupos[g][0] += 1; grupos[g][1] += int(bool(v & toks_in))
    fams = sorted({t["familia"] for t in puente})
    fechas = [c.get("date") for c in case["cortes"] if c.get("date")]
    conc = None
    if len(fechas) >= 3:
        ys = [int(str(f)[:4]) for f in fechas]; lo, hi = min(ys), max(ys)
        if hi > lo:
            ter = [(y - lo) / (hi - lo) for y in ys]
            conc = {"prop_cortes_primer_tercio": round(sum(x < 1 / 3 for x in ter) / len(ter), 4),
                    "prop_cortes_ultimo_tercio": round(sum(x > 2 / 3 for x in ter) / len(ter), 4), "anio_min": lo, "anio_max": hi}
    return {
        "n_tokens": sum(ejes.values()), "n_tokens_distintos": len(toks_in), "ejes": dict(ejes),
        "naturaleza": dict(nat), "locus": dict(loc), "tiempo": dict(tie), "no_clasificados": sorted(no_clas),
        "escala_ocurrencias": dict(esc_occ), "escala_laterales_activos": dict(act_por_escala),
        "escala_laterales_disponibles": dict(disponibles), "escala_tasa_activacion": tasa_escala,
        "polaridad_ocurrencias": dict(pol_occ), "familias_laterales_ocurrencias": {f: fam_occ.get(f, 0) for f in fams},
        "familias_laterales_no_tocadas": [f for f in fams if fam_occ.get(f, 0) == 0],
        "celdas_dinamica_escala": {f"{d}|{e}": {"disponibles": disp_celda[(d, e)], "ocurrencias": celda_occ.get((d, e), 0)}
                                   for (d, e) in sorted(disp_celda)},
        "grupos_244_tocados": {g: {"patrones": v[0], "patrones_con_token_del_input": v[1]} for g, v in sorted(grupos.items())},
        "grupos_244_no_tocados": sorted(g for g, v in grupos.items() if v[1] == 0),
        "intensidad_codificada": {"media": round(sum(intens) / len(intens), 4) if intens else None,
                                  "prop_alta_ge_0_78": round(sum(x >= 0.78 for x in intens) / len(intens), 4) if intens else None,
                                  "prop_baja_le_0_64": round(sum(x <= 0.64 for x in intens) / len(intens), 4) if intens else None},
        "concentracion_temporal_cortes": conc, "por_corte": por_corte,
    }

# ------------------------------------------------------------------ capa TEXTO
def capa_texto(case, M):
    fun, hall, pol = collections.Counter(), collections.Counter(), collections.Counter()
    mk = collections.Counter(); n_pal = 0; nominales = 0; n_tx = 0
    for t in case["textos"]:
        tx = t["texto"]; tn = norm(tx); n_tx += 1; n_pal += len(re.findall(r"[a-z0-9]+", tn))
        for m in M["detras_v2"].filtrar(tx)["marcajes"]:
            fun[m["funcion"]] += 1
        for h in M["dirigida"].detectar_pregunta_dirigida(tx):
            hall[h.tipo] += 1
        pol[M["polaridad"].clasificar_polaridad_causal(tx)["etiqueta"]] += 1
        for e, lst in LX.ESCALA_TEXTO.items(): mk["escala_" + e] += contar(tn, lst)
        mk["emocion"] += contar(tn, LX.EMOCION_TEXTO); mk["certeza_alta"] += contar(tn, LX.CERTEZA_ALTA)
        mk["certeza_baja"] += contar(tn, LX.CERTEZA_BAJA); mk["futuro"] += contar(tn, LX.FUTURO_TEXTO)
        mk["pasado"] += contar(tn, LX.PASADO_TEXTO); va = contar(tn, LX.VERBO_ACCION_SUJETO); mk["verbo_accion_sujeto"] += va
        pi = len(re.findall(LX.PASIVA_IMPERSONAL_RX, tn)); mk["pasiva_impersonal"] += pi
        mk["anios_citados"] += len(re.findall(r"\b(1[0-9]{3}|20[0-9]{2})\b", tn))
        if t["origen"] != "question" and va == 0 and pi == 0 and len(tn.split()) <= 10: nominales += 1
    n_notas = sum(1 for t in case["textos"] if t["origen"] != "question")
    return {"n_textos": n_tx, "n_palabras": n_pal, "suficiente": n_pal >= 30,
            "detras_v2_funciones": dict(fun), "dirigida_hallazgos": dict(hall), "polaridad_causal": dict(pol),
            "marcadores": dict(mk), "frases_nominales_sin_agente": nominales, "n_textos_no_pregunta": n_notas}

# ------------------------------------------------------------------ lentes
DESC_ESC = {"micro": "persona", "meso": "grupo u organización", "macro": "Estado o instituciones amplias"}
def lentes(ct, cx, M):
    L = {}
    # 1 escala: tasa de activación normalizada por disponibilidad (evita sesgo de base 81/54/36)
    tasa = ct["escala_tasa_activacion"]; base = {k: int(round(v * 1000)) for k, v in tasa.items()}
    L["escala"] = {**estado_lente(base, ["micro", "meso", "macro"], M, n_min=1),
                   "medida": "tasa de laterales activados por escala (x1000) vía puente 244 alta+media",
                   "tasas": tasa, "ocurrencias": ct["escala_ocurrencias"],
                   "texto": {k: cx["marcadores"].get("escala_" + k, 0) for k in ("micro", "meso", "macro")}}
    tx = L["escala"]["texto"]; ttot = sum(tx.values())
    tdom = max(("micro", "meso", "macro"), key=lambda k: (tx[k], -["micro", "meso", "macro"].index(k))) if ttot >= 3 else None
    kdom = max(("micro", "meso", "macro"), key=lambda k: tasa[k])
    L["escala"]["divergencia_capas"] = {"escala_mayor_en_tokens": kdom, "escala_mayor_en_texto": tdom,
        "diverge": bool(tdom and tdom != kdom),
        "lectura": ("quien codificó los tokens y quien escribió las notas miran a escalas distintas" if (tdom and tdom != kdom) else
                    ("texto insuficiente para comparar" if not tdom else "misma escala en ambas capas"))}
    # 2 hechos vs interior
    n = ct["naturaleza"]
    obs = {"observable": n.get("EVENTO", 0) + n.get("RELACION", 0),
           "atribuido_al_interior": n.get("ESTADO_INTERNO", 0) + n.get("RASGO", 0) + n.get("COGNICION", 0)}
    L["hechos_vs_interior"] = {**estado_lente(obs, ["observable", "atribuido_al_interior"], M),
                               "detalle_tokens": n,
                               "texto": {"fenomeno_campo": cx["detras_v2_funciones"].get("FENOMENO_CAMPO", 0),
                                         "etiqueta_o_marco": sum(cx["detras_v2_funciones"].get(k, 0) for k in ("ETIQUETA_SUJETO", "MARCO_EVALUATIVO")),
                                         "emocion": cx["marcadores"].get("emocion", 0)}}
    L["emocion_vs_rasgo_vs_cognicion"] = estado_lente(n, ["ESTADO_INTERNO", "RASGO", "COGNICION"], M)
    # 3 agencia
    loc = {k: v for k, v in ct["locus"].items() if k != "INDETERMINADO"}
    L["agencia"] = {**estado_lente(loc, ["SUJETO", "OTROS_PERSONAS", "GRUPO_INSTITUCION", "CIRCUNSTANCIA", "COMPARTIDA"], M),
                    "indeterminado": ct["locus"].get("INDETERMINADO", 0),
                    "texto": {"verbo_accion_sujeto": cx["marcadores"].get("verbo_accion_sujeto", 0),
                              "pasiva_impersonal": cx["marcadores"].get("pasiva_impersonal", 0),
                              "frases_nominales_sin_agente": cx["frases_nominales_sin_agente"],
                              "de_n_textos": cx["n_textos_no_pregunta"]}}
    # 4 tiempo
    L["foco_temporal"] = {**estado_lente(ct["tiempo"], ["PASADO", "PRESENTE", "FUTURO"], M),
                          "neutros": ct["tiempo"].get("NEUTRO", 0),
                          "prop_tokens_con_tiempo": round(1 - ct["tiempo"].get("NEUTRO", 0) / max(1, sum(ct["tiempo"].values())), 4),
                          "texto": {"pasado": cx["marcadores"].get("pasado", 0), "futuro": cx["marcadores"].get("futuro", 0)},
                          "concentracion_cortes": ct["concentracion_temporal_cortes"]}
    # 5 certeza
    ca, cb = cx["marcadores"].get("certeza_alta", 0), cx["marcadores"].get("certeza_baja", 0)
    if not cx["suficiente"]: est = "SIN_DATO"
    elif ca + cb == 0: est = "SIN_MARCADORES"
    else: est = estado_lente({"alta": ca, "baja": cb}, ["alta", "baja"], M, n_min=1)["estado"]
    L["certeza"] = {"estado": est, "texto": {"certeza_alta": ca, "certeza_baja": cb},
                    "intensidad_codificada": ct["intensidad_codificada"],
                    "nota": "las intensidades vienen acotadas por contrato 0.60-0.84; se reporta su reparto, no se interpreta como verdad"}
    # 6 polaridad
    L["polaridad"] = estado_lente(ct["polaridad_ocurrencias"], ["empuja", "frena"], M)
    # 7 cobertura
    celdas_vacias = [k for k, v in ct["celdas_dinamica_escala"].items() if v["disponibles"] > 0 and v["ocurrencias"] == 0 and not k.startswith(("K0", "otra"))]
    L["cobertura"] = {"familias_laterales_no_tocadas": ct["familias_laterales_no_tocadas"],
                      "grupos_244_no_tocados": ct["grupos_244_no_tocados"],
                      "celdas_dinamica_escala_sin_ocurrencia": celdas_vacias,
                      "tokens_no_clasificados": ct["no_clasificados"]}
    return L

# ------------------------------------------------------------------ puntos ciegos (latentes)
def _corte_mas_marcado(ct, dim, cat):
    best, bid = -1.0, None
    for pc in ct["por_corte"]:
        c = pc[dim]; tot = sum(c.values())
        if tot and c.get(cat, 0) / tot > best: best, bid = c.get(cat, 0) / tot, pc["id"]
    return bid

def puntos_ciegos(L, ct, M):
    out = []
    def add(dim, ausente, dom, lect, evid, marcado, corte=None):
        out.append({"id": f"PC{len(out)+1:02d}", "dimension": dim, "no_mirado": ausente, "lente_dominante": dom,
                    "estado": "LATENTE", "es_hecho": False, "marcado": marcado, "corte_de_referencia": corte,
                    "lectura_inversa_decimo_hombre": lect, "evidencia_de_ausencia": evid})
    e = L["escala"]
    if e["estado"] in ("DOMINANTE", "REPARTIDO", "LATENCIA_EMPATE"):
        top = max(("micro", "meso", "macro"), key=lambda k: e["tasas"][k])
        dom = e["dominante"] or ("empate " + "/".join(e.get("empate_entre", [])))
        for k in ("micro", "meso", "macro"):
            if k == top or k in e.get("empate_entre", []): continue
            if e["tasas"][k] <= 0.5 * e["tasas"][top]:
                add("escala", k, dom,
                    f"Leer la trayectoria como si el nivel {DESC_ESC[k]} moviera el cambio y el nivel {DESC_ESC[top]} solo lo registrara.",
                    {"tasa_no_mirado": e["tasas"][k], "tasa_mayor": e["tasas"][top], "marcadores_texto": e["texto"].get(k, 0)},
                    "ALTO" if e["tasas"][k] == 0 or e["tasas"][k] <= 0.25 * e["tasas"][top] else "MEDIO")
    h = L["hechos_vs_interior"]
    if h["estado"] == "DOMINANTE":
        k = "atribuido_al_interior" if h["dominante"] == "observable" else "observable"
        cat = "EVENTO" if h["dominante"] == "observable" else "RASGO"
        add("hechos_vs_interior", k, h["dominante"],
            "Leer los mismos cortes pidiendo solo lo filmable." if k == "observable" else "Leer los mismos cortes preguntando qué estado interno acompaña cada hecho.",
            {"proporciones": h["proporciones"]}, "ALTO" if h["proporciones"][k] <= 0.2 else "MEDIO",
            _corte_mas_marcado(ct, "naturaleza", cat))
    ag = L["agencia"]
    if ag["estado"] in ("DOMINANTE", "REPARTIDO", "LATENCIA_EMPATE"):
        if ag["dominante"] is None: ag = {**ag, "dominante": "empate " + "/".join(ag["empate_entre"])}
        for k in ag.get("ausentes", []) + ag.get("minoritarios", []):
            add("agencia", k, ag["dominante"],
                f"Releer cada corte suponiendo que la agencia principal está en {k.lower().replace('_', ' ')}, no en {ag['dominante'].lower().replace('_', ' ').replace('/', ' ni ')}.",
                {"proporciones": ag["proporciones"]}, "ALTO" if ag["proporciones"][k] == 0 else "MEDIO",
                _corte_mas_marcado(ct, "locus", ag["dominante"].split(" ")[-1].split("/")[0]))
    tf = L["foco_temporal"]
    if tf["estado"] in ("DOMINANTE", "REPARTIDO", "LATENCIA_EMPATE"):
        if tf["dominante"] is None: tf = {**tf, "dominante": "empate " + "/".join(tf["empate_entre"])}
        debil = tf["prop_tokens_con_tiempo"] < 0.25
        for k in tf.get("ausentes", []) + tf.get("minoritarios", []):
            add("foco_temporal", k, tf["dominante"], f"Buscar lo que el input deja en el {k.lower()}.",
                {"proporciones": tf["proporciones"], "neutros": tf["neutros"], "prop_tokens_con_tiempo": tf["prop_tokens_con_tiempo"]},
                "BAJO" if debil else ("ALTO" if tf["proporciones"][k] == 0 else "MEDIO"),
                _corte_mas_marcado(ct, "tiempo", tf["dominante"].split(" ")[-1].split("/")[0]))
    if L["certeza"]["estado"] in ("SIN_MARCADORES", "DOMINANTE") and L["certeza"]["texto"]["certeza_baja"] == 0:
        add("certeza", "duda_o_fuente_no_declarada", "afirmacion_sin_matiz",
            "Tratar cada corte como inferencia de quien codificó hasta ver la fuente.",
            {"certeza_alta": L["certeza"]["texto"]["certeza_alta"], "certeza_baja": 0}, "MEDIO")
    po = L["polaridad"]
    if po["estado"] == "DOMINANTE":
        k = "frena" if po["dominante"] == "empuja" else "empuja"
        add("polaridad", k, po["dominante"], f"Releer los cortes buscando lo que {k} la trayectoria.",
            {"proporciones": po["proporciones"]}, "ALTO" if po["proporciones"][k] <= 0.2 else "MEDIO")
    desc = M["matriz"]["reglas"]["dinamicas"]
    vacias = L["cobertura"]["celdas_dinamica_escala_sin_ocurrencia"]
    for cel in vacias:
        d, esc = cel.split("|")
        add("cobertura_dinamica", cel, None, f"Buscar «{desc[d]}» a nivel {DESC_ESC[esc]}.",
            {"tokens_disponibles_en_matriz": ct["celdas_dinamica_escala"][cel]["disponibles"], "ocurrencias": 0}, "BAJO")
    return out

# ------------------------------------------------------------------ preguntas
POL = [("empuja", "impulsa"), ("frena", "frena")]
def _grid(filas):
    ops = []
    for f in filas:
        for _, verbo in POL: ops.append(f"{f} — lo {verbo}")
    return ops

def preguntas(ciegos, case, M, max_n=8):
    ids = [c["id"] for c in case["cortes"]]; ini, fin = ids[0], ids[-1]
    orden = {"ALTO": 0, "MEDIO": 1, "BAJO": 2}
    sel = sorted(ciegos, key=lambda c: (orden[c["marcado"]], c["id"]))
    # una pregunta por (dimensión, corte); escala y polaridad comparten la misma pregunta de nivel×dirección;
    # cobertura: una por dinámica, máximo 3
    grupos, llave_de = collections.OrderedDict(), {}
    for c in sel:
        d = c["dimension"]
        if d in ("escala", "polaridad"): llave = ("nivel_direccion",)
        elif d == "cobertura_dinamica": llave = ("cob", c["no_mirado"].split("|")[0])
        else: llave = (d, c.get("corte_de_referencia"))
        grupos.setdefault(llave, []).append(c)
    sel2, ncov = [], 0
    for llave, cs in grupos.items():
        if llave[0] == "cob":
            if ncov >= 3: continue
            ncov += 1
        c0 = dict(cs[0]); c0["_ids"] = [x["id"] for x in cs]; sel2.append(c0)
    niveles = ["la persona", "un grupo u organización", "el Estado o instituciones amplias"]
    out = []
    for c in sel2[:max_n]:
        cx = c.get("corte_de_referencia") or fin
        d = c["dimension"]
        if d in ("escala", "polaridad"):
            q = f"Entre {ini} y {fin}, ¿desde qué nivel actuó el factor de mayor efecto sobre la trayectoria y en qué dirección?"
            ops = _grid(niveles) + ["ninguno registrable", "no determinable con el input"]
        elif d == "agencia":
            q = f"En {cx}, ¿quién produjo el cambio de mayor efecto y en qué dirección?"
            ops = _grid(["la persona", "otras personas", "un grupo u organización", "el Estado o instituciones amplias", "circunstancias sin agente"]) + ["no determinable con el input"]
        elif d == "hechos_vs_interior":
            q = f"En {cx}, ¿qué tipo de elemento sostiene el registro y en qué dirección?"
            ops = _grid(["un hecho observable", "un estado interno", "una relación con otros"]) + ["no determinable con el input"]
        elif d == "foco_temporal":
            q = f"Para {cx}, ¿en qué tramo está el antecedente o la consecuencia de mayor efecto y en qué dirección?"
            ops = _grid([f"antes de {ini}", f"entre {ini} y {fin}", f"después de {fin}"]) + ["no determinable con el input"]
        elif d == "certeza":
            q = f"Para {cx}, ¿cómo consta el elemento principal del corte?"
            ops = ["documentado en fuente — sostiene la lectura", "documentado en fuente — la contradice",
                   "inferido por quien codificó — sostiene la lectura", "inferido por quien codificó — la contradice",
                   "no consta", "no determinable con el input"]
        else:
            dd, esc = c["no_mirado"].split("|"); desc = M["matriz"]["reglas"]["dinamicas"][dd]
            q = f"Entre {ini} y {fin}, ¿aparece la dinámica «{desc}» y, si aparece, en qué nivel y en qué dirección?"
            ops = _grid(niveles) + ["no aparece", "no determinable con el input"]
        # guardia con las piezas existentes: la pregunta no debe ser dirigida ni perfilar
        g1 = M["detras_v2"].filtrar(q); g2 = M["dirigida"].detectar_pregunta_dirigida(q)
        out.append({"id": f"Q{len(out)+1:02d}", "dirigida_a": c["_ids"], "dimension": d, "pregunta": q,
                    "opciones": [f"{chr(65+i)}) {o}" for i, o in enumerate(ops)],
                    "simetria": "cada nivel aparece con las dos direcciones; orden fijo, no depende del lente dominante",
                    "guardia_detras_v2": g1["bandera"], "guardia_dirigida": [h.tipo for h in g2],
                    "estado_guardia": "PASA" if not g1["bandera"] and not g2 else "REFORMULAR"})
    return out

# ------------------------------------------------------------------ validación de salida
PROHIBIDOS_REC = {"probability", "probabilidad", "weight", "peso", "confidence", "confianza", "prob", "score", "p_final", "likelihood"}
DEMOGRAFIA = re.compile(r"(escolaridad|educacion_formal|nivel_educativo|lugar_de_origen|origen_geografico|nacionalidad|genero_del|edad_del|socioeconomic|clase_social|etnia|religion_del)", re.I)
def validar(salida, M):
    def rec(o, ruta=""):
        if isinstance(o, dict):
            for k, v in o.items():
                if str(k).lower() in PROHIBIDOS_REC: raise ValueError(f"CAMPO_PROHIBIDO {ruta}.{k}")
                if DEMOGRAFIA.search(str(k)): raise ValueError(f"DIMENSION_DEMOGRAFICA {ruta}.{k}")
                rec(v, f"{ruta}.{k}")
        elif isinstance(o, list):
            for i, x in enumerate(o): rec(x, f"{ruta}[{i}]")
    rec(salida)
    M["guardia"].GuardiaNoCruce({}, corte_id="perfil_narrador").validar_output_lente(salida)
    return True

def correr_caso(case, M, reg):
    ct = capa_tokens(case, M); cx = capa_texto(case, M); L = lentes(ct, cx, M)
    pcs = puntos_ciegos(L, ct, M); qs = preguntas(pcs, case, M)
    sal = {"sensor": VERSION, "can_decide_H": False, "Alimenta_H": "NO", "escribe_patterns": False,
           "entra_al_ranking": False, "infiere_demografia": False, "caso": case["caso"], "case_id": case["case_id"],
           "piezas_usadas": reg, "lentes": L, "puntos_ciegos": pcs, "preguntas": qs,
           "capa_tokens": {k: v for k, v in ct.items() if k != "por_corte"}, "capa_texto": cx,
           "regla": "Perfil del narrador = cómo está escrito el input. Los puntos ciegos son LATENTES: señalan dónde no miró el texto, no afirman que ahí haya algo."}
    validar(sal, M)
    return sal

def main(argv):
    M, reg = cargar_piezas()
    indir = argv[1] if len(argv) > 1 else os.path.join(HERE, "..", "casos_texto")
    outdir = argv[2] if len(argv) > 2 else os.path.join(HERE, "..", "salidas")
    os.makedirs(outdir, exist_ok=True); res = {}
    for f in sorted(glob.glob(os.path.join(indir, "*.json"))):
        if os.path.basename(f).startswith("_"): continue
        with open(f, encoding="utf-8") as fh:
            case = json.load(fh)
        s = correr_caso(case, M, reg)
        p = os.path.join(outdir, f"PERFIL_NARRADOR_{case['caso']}.json")
        json.dump(s, open(p, "w"), ensure_ascii=False, indent=1, sort_keys=True)
        res[case["caso"]] = hashlib.sha256(open(p, "rb").read()).hexdigest()[:16]
    print(json.dumps(res, indent=1))

if __name__ == "__main__": main(sys.argv)
