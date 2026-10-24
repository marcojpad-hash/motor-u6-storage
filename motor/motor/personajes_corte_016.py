#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""personajes_corte_016.py — PATCH 016 (2026-10-06). Personajes / equivalentes por corte. LATERAL DE TRAZA.

Contrato: can_decide_H=False · no escribe H1/H2 · no reordena candidatos · no escribe archivos ni stores ·
sin llamadas LLM · determinista · agnóstico (los nombres propios NUNCA salen ni votan: se mapean a ids de rol
neutros; del nombre solo queda una huella sha256[:8] para que el LLM, fuera del motor, pueda traducir de vuelta).

Fuente: SOLO el texto propio del corte. Campo `hecho`; si el corte no trae `hecho`, `narracion` (mismo papel:
texto propio del corte; criterio ya usado por el sombrero de entrada del hub: hecho/narracion, nunca source_note).
Nunca se leen source_note, question, person, caldero_* ni fuentes externas. Sin texto -> SIN_TEXTO (no se inventa).

Ids de rol (neutros): PROTAGONISTA, PROTAGONISTA_FASE_k (facetas del mismo protagonista en fases de su vida:
el niño en formación, el creador maduro, el enfermo... pueden ocupar funciones Souriau distintas), MENTOR, FAMILIA,
PAREJA, AUTORIDAD_k, INSTITUCION_k, COLECTIVO_k, ANTAGONISTA_k, CONTRAPARTE_k (agente nombrado solo por una relación),
PERSONA_k (persona nombrada sin función derivable). Si un corte no nombra otro agente, se dice (sin_otros_agentes).

Reglas (léxico español; ampliable sin tocar el motor):
  R1 modo del caso: BIOGRAFICO si en >= la mitad de los cortes con texto hay segmentos de sujeto implícito con verbo/
     acción del protagonista (nace, compone, rompe...) o facetas; si no, COLECTIVO: protagonista = agente genérico
     (institución/colectivo) más mencionado en los textos del caso (>= 3 menciones y en >= la mitad de los cortes con texto).
  R2 facetas del protagonista por léxico (FORMACION, ITINERANTE, CREADOR, CARGO, MEDIADOR, BUSCADOR, RUPTURA, AUTORIDAD,
     ENFERMEDAD_FINAL); FASE_k = orden de primera aparición en el caso. 'muerte de <Nombre>' es de OTRO, no del protagonista.
  R3 función de cada faceta: FORMACION -> tierra (y leon si no hay otra faceta agente); MEDIADOR -> balanza (y leon si sola);
     ENFERMEDAD_FINAL -> marte (fuerza opuesta interna: el otro yo enfermo); resto -> leon.
  R4 agentes: léxico de sustantivos genéricos (institución/colectivo/antagonista/familia/pareja/autoridad) + nombres propios
     SOLO con pista adyacente (título 'emperador X', 'matrimonio con X', 'formación ... de X', 'bajo X', 'muerte de X',
     'conflicto/rompe/reconciliación con X', 'presión sobre X'); nombre sin pista = no agente (lugar/obra/desconocido; solo se cuenta).
     'elegido papa (X)' = alias de rol del protagonista (no es otro agente).
  R5 función de cada agente: pista de conflicto en el mismo segmento -> marte; pista de alianza -> luna; si no, por tipo:
     MENTOR/FAMILIA/PAREJA -> luna; AUTORIDAD/INSTITUCION -> balanza; COLECTIVO -> tierra (coalición/alianza -> luna);
     ANTAGONISTA -> marte; CONTRAPARTE/PERSONA -> sin función por regla.
  R6 sol = bienes/valores nombrados en el texto (BIEN:<lema>, léxico); sin bien explícito -> sol vacío.
"""
from __future__ import annotations
import hashlib
import re
import unicodedata
from typing import Any, Dict, List, Tuple

VERSION = "PERSONAJES_CORTE_016_20261006"
CAMPOS_TEXTO = ("hecho", "narracion")
FUNCIONES = ("leon", "sol", "tierra", "marte", "balanza", "luna")


def _n(s: str) -> str:
    return unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower()


def _huella(s: str) -> str:
    return hashlib.sha256(str(s).strip().encode("utf-8")).hexdigest()[:8]


# ---------------------------------------------------------------- léxicos (normalizados: minúscula, sin acentos)
FACETAS = [  # orden = desempate
    ("FORMACION", [r"\bnace\b", r"\bnacimiento\b", r"\binfancia\b", r"\bnin[oa]s?\b", r"\bprodigio", r"\bestudi(os|a|o)\b",
                   r"\bformacion\b", r"\beducacion\b", r"\bjuventud\b", r"\bcapacidades extraordinarias\b"]),
    ("ITINERANTE", [r"\bviaj(e|es|a|o)\b", r"\bgira\b", r"\bactuaciones\b", r"\bactua\b", r"\brecorre\b"]),
    ("CREADOR", [r"\bcompon(e|en|iendo)\b", r"\bcompos(icion|itor|itiva|itivo)\w*", r"\bobras?\b", r"\bestren(a|o|os)\b",
                 r"\boperistic\w*", r"\bescribe\b", r"\bfunda\b", r"\binventa\b", r"\bproduccion musical\b"]),
    ("CARGO", [r"\bservicio\b", r"\bsecretari(o|ado)\b", r"\bobispo\b", r"\bcardenal\b", r"\btitular\b", r"\btoma ordenes\b"]),
    ("MEDIADOR", [r"\bmediacion\b", r"\bnegocia(cion)?\b", r"\bdiplomati\w*", r"\bdiplomacia\b", r"\boratoria\b"]),
    ("BUSCADOR", [r"\bbusca(ndo)?\b", r"\bbusqueda\b"]),
    ("RUPTURA", [r"\brompe\b", r"\bruptura\b", r"\bindependiente\b", r"\bse establece\b", r"\bcambio de lealtad\b", r"\bpasa a\b"]),
    ("AUTORIDAD", [r"\belegido papa\b", r"\bcoronacion\b", r"\bproclama\b", r"\bmoviliza(cion)?\b", r"\bgobierna\b", r"\bpreside\b", r"\bconvoca\b"]),
    ("ENFERMEDAD_FINAL", [r"\benferm\w*", r"\bmuere\b", r"\bfallece\b", r"\bagonia\b"]),
]
FACETA_FUNCION = {"FORMACION": "tierra", "MEDIADOR": "balanza", "ENFERMEDAD_FINAL": "marte"}
FACETAS_AGENTE = {"ITINERANTE", "CREADOR", "CARGO", "BUSCADOR", "RUPTURA", "AUTORIDAD"}
RX_MUERTE_PROPIA = re.compile(r"\b[Mm]uerte\b(?!\s+de\s+[A-ZÁÉÍÓÚÑ])")

VERBOS_PROTAGONISTA = {"nace", "entra", "pasa", "toma", "adquiere", "viaja", "proclama", "recibe", "muestra", "actua", "aumenta",
                       "compone", "rompe", "continua", "trabaja", "mantiene", "estrena", "muere", "enferma", "regresa", "funda",
                       "crea", "dirige", "gobierna", "escribe", "publica", "se", "elegido", "creado", "nombrado", "coronado",
                       "estudia", "busca", "fallece", "realiza", "consolida", "secretario", "obispo", "regreso", "viaje", "viajes",
                       "gran", "estudios", "formacion", "matrimonio", "enfermedad", "muerte", "coronacion", "reconciliacion",
                       "mediacion", "consolidacion", "busqueda", "actividad", "produccion", "relacion", "actuaciones", "titular",
                       "conflicto", "encargos", "presion", "prioridad", "tras", "luego"}
DETERMINANTES = {"el", "la", "los", "las", "un", "una", "unos", "unas", "ese", "esa", "este", "esta", "esos", "esas"}

INSTITUCION_LEX = {"concilio": "concilio", "corte": "corte", "cortes": "corte", "iglesia": "iglesia", "congreso": "congreso",
                   "estados": "estado", "gobierno": "gobierno", "consejo": "consejo", "consejos": "consejo", "oficina": "oficina",
                   "oficinas": "oficina", "centro": "centro", "tribunal": "tribunal", "tribunales": "tribunal", "imperio": "imperio",
                   "papado": "papado", "curia": "curia", "universidad": "universidad", "academia": "academia",
                   "institucion": "institucion", "instituciones": "institucion"}
INSTITUCION_NOMBRE_INICIO = {"concilio", "congreso", "santa", "iglesia", "corte", "universidad", "academia", "senado", "parlamento", "consejo"}
COLECTIVO_LEX = {"principes": "principes", "bandos": "bandos", "elite": "elite", "coaliciones": "coalicion", "coalicion": "coalicion",
                 "regiones": "regiones", "casas": "casas", "aldea": "aldeas", "aldeas": "aldeas", "gente": "gente", "pueblo": "pueblo",
                 "intermediarios": "intermediarios", "potencias": "potencias", "mercados": "mercados", "familias": "familias",
                 "foraneos": "foraneos", "sociedad": "sociedad", "figuras": "figuras", "alianzas": "alianza", "alianza": "alianza",
                 "nobleza": "nobleza", "clero": "clero"}
ANTAGONISTA_LEX = {"enemigos": "enemigos", "enemigo": "enemigos", "rivales": "rivales", "oposicion": "oposicion"}
FAMILIA_LEX = {"familia", "padre", "madre", "hermano", "hermana", "hermanos", "hermanas", "hijo", "hija", "hijos", "hijas"}
PAREJA_LEX = {"matrimonio", "esposa", "esposo", "marido", "boda"}
MENTOR_LEX = {"maestro", "mentor", "tutor", "profesor"}
AUTORIDAD_LEX = {"arzobispo": "arzobisp", "arzobispal": "arzobisp", "emperador": "emperador", "rey": "rey", "reina": "reina", "antipapa": "antipapa", "principe": "principe"}
TITULOS = {"antipapa", "papa", "emperador", "rey", "reina", "arzobispo", "principe", "duque", "conde", "cardenal", "obispo"}
KIN = {"padre", "madre", "hermano", "hermana", "hijo", "hija", "tio", "tia", "abuelo", "abuela"}
CONECTORES = {"de", "del", "di", "von", "van", "da", "aus", "dem", "la", "le", "fan"}
RX_ROMANO = re.compile(r"^[IVXLC]+$")
RX_ANTI = re.compile(r"\banti([a-z]{3,})\b")
NO_ANTI = ("antig", "anticip", "antipapa", "antiguedad")
CONFLICTO = [r"\bconflicto", r"\brompe\b", r"\bruptura\b", r"\bcontra\b", r"\benemig", r"\boposicion\b", r"\brival",
             r"\bfriccion\b", r"\bpresion sobre\b", r"\bresist", r"\bguerra\b", r"\bbatalla\b", r"\blucha\b", r"\btraicion",
             r"\bse enfrenta\b", r"\bliquidar\b", r"\bcoaccion\b"]
ALIANZA = [r"\balianza", r"\baliad", r"\bapoyo\b", r"\bayuda\b", r"\bauxilio\b", r"\breconciliacion\b", r"\bcon la familia\b", r"\bacompan"]
BIENES = {"oportunidad": "oportunidad", "oportunidades": "oportunidad", "autoridad": "autoridad", "poder": "poder", "mando": "mando",
          "reconocimiento": "reconocimiento", "exito": "exito", "independiente": "independencia", "independencia": "independencia",
          "cruzada": "cruzada", "coalicion": "coalicion", "encargos": "encargo", "obras": "obra", "obra": "obra", "recursos": "recursos",
          "obediencia": "obediencia", "plata": "plata", "prestigio": "prestigio", "legitima": "legitimidad", "legitimidad": "legitimidad",
          "estabilidad": "estabilidad", "orden": "orden", "autonomia": "autonomia", "oportunidades profesionales": "oportunidad"}


def _texto(c: Dict[str, Any]) -> Tuple[str, str]:
    for k in CAMPOS_TEXTO:
        v = c.get(k)
        if isinstance(v, str) and v.strip():
            return k, v.strip()
    return "", ""


def _segmentos(txt: str, modo_hecho: bool) -> List[str]:
    t = re.sub(r"^\s*[\d\-–/]+(\s*-\s*[\d\-–/]+)?\s*:\s*", "", txt) if modo_hecho else txt
    return [s.strip() for s in re.split(r"[;.:]\s+|[;.]$", t) if s and s.strip()]


def _hay(pats, s_norm) -> bool:
    return any(re.search(p, s_norm) for p in pats)


def _facetas(txt: str) -> List[Tuple[int, str]]:
    tn = _n(txt); out = []
    for fac, pats in FACETAS:
        pos = [m.start() for p in pats for m in re.finditer(p, tn)]
        if fac == "ENFERMEDAD_FINAL":
            pos += [m.start() for m in RX_MUERTE_PROPIA.finditer(txt)]
        if pos:
            out.append((min(pos), fac))
    return sorted(out)


def _sujeto_implicito(seg: str) -> bool:
    w = seg.split()
    if not w:
        return False
    if w[0][:1].isupper() and not w[0][:1].isdigit():
        return False  # sujeto nombrado explícito ('Figaro vuelve...')
    w0 = _n(w[0]).strip(",()")
    if w0 in DETERMINANTES:
        return False
    return w0 in VERBOS_PROTAGONISTA or w0.endswith(("ado", "ido"))


def _palabras(seg: str) -> List[Tuple[str, str]]:
    return [(m.group(0), _n(m.group(0))) for m in re.finditer(r"[A-Za-zÁÉÍÓÚÑÜáéíóúñü0-9]+", seg)]


def _spans_nombre(seg: str, es_inicio_texto: bool) -> List[Dict[str, Any]]:
    """Secuencias de palabras capitalizadas (con conectores) y la(s) palabra(s) previas como pista."""
    ws = _palabras(seg); out = []; i = 0
    while i < len(ws):
        o, n = ws[i]
        cap = o[:1].isupper() and not o[:1].isdigit()
        inicio_solo = (i == 0 and es_inicio_texto and not (i + 1 < len(ws) and ws[i + 1][0][:1].isupper()))
        if cap and not inicio_solo:
            j = i + 1
            while j < len(ws):
                oj, nj = ws[j]
                if (oj[:1].isupper() and not oj[:1].isdigit()) or RX_ROMANO.match(oj):
                    j += 1; continue
                if nj in CONECTORES and j + 1 < len(ws) and ws[j + 1][0][:1].isupper():
                    j += 1; continue
                break
            span = " ".join(x[0] for x in ws[i:j])
            prev = [x[1] for x in ws[max(0, i - 6):i]]
            out.append({"span": span, "ini": i, "prev": prev, "primera": n, "en_parentesis": bool(re.search(r"\(\s*" + re.escape(ws[i][0]), seg))})
            i = j
        else:
            i += 1
    return out


def _clasificar_nombre(sp: Dict[str, Any], seg_n: str) -> Tuple[str, str]:
    """-> (tipo, pista) ; tipo '' = no agente."""
    p = sp["prev"]; p1 = p[-1] if p else ""; p2 = " ".join(p[-2:]) if len(p) >= 2 else p1
    if sp["en_parentesis"] and re.search(r"\b(elegido|nombrado|coronado|proclamado|creado)\s+\w+\s*$", " ".join(p)):
        return "ALIAS_PROTAGONISTA", "rol_entre_parentesis"
    if sp["primera"] in INSTITUCION_NOMBRE_INICIO:
        return "INSTITUCION", "nombre_institucional"
    if p1 in TITULOS:
        return "AUTORIDAD", "titulo:" + p1
    if p1 in KIN:
        return "FAMILIA", "parentesco:" + p1
    if p1 in MENTOR_LEX:
        return "MENTOR", "maestro"
    if p2 in ("matrimonio con", "casa con", "boda con", "casarse con") or p1 in ("esposa", "esposo", "marido"):
        return "PAREJA", "matrimonio_con"
    if p1 == "de" and "formacion" in p[-6:-1]:
        return "MENTOR", "formacion_de"
    if p2 == "muerte de":
        return "PERSONA", "muerte_de"
    if p1 == "bajo":
        return "AUTORIDAD", "bajo"
    if p1 == "tras":
        return "PERSONA", "tras"
    if p1 in ("con", "sobre", "contra") and len(p) >= 2:
        rel = p[-2]
        if rel in ("conflicto", "rompe", "presion", "ruptura", "guerra") or p1 == "contra":
            return "CONTRAPARTE", "conflicto:" + rel
        if rel in ("reconciliacion", "alianza", "acuerdo"):
            return "CONTRAPARTE", "alianza:" + rel
    return "", "sin_pista"


def extraer(cuts: List[Dict[str, Any]]) -> Dict[str, Any]:
    cuts = list(cuts or [])
    textos = [_texto(c) for c in cuts]
    con_texto = [i for i, (k, t) in enumerate(textos) if t]
    # ---------- R1 modo del caso
    bio_votos = 0
    for i in con_texto:
        k, t = textos[i]
        segs = _segmentos(t, k == "hecho")
        if k == "hecho" and (any(_sujeto_implicito(s) for s in segs) or _facetas(t)):
            bio_votos += 1
    modo = "BIOGRAFICO" if con_texto and bio_votos * 2 >= len(con_texto) else ("COLECTIVO" if con_texto else "SIN_TEXTO")
    # ---------- menciones genéricas (para protagonista colectivo)
    menc: Dict[str, List[int]] = {}
    for i in con_texto:
        for o, n in _palabras(textos[i][1]):
            lem = INSTITUCION_LEX.get(n) or COLECTIVO_LEX.get(n)
            if lem:
                menc.setdefault(lem, []).append(i)
    prot_col = None
    if modo == "COLECTIVO" and menc:
        cand = sorted(((len(v), len(set(v)), -min(v), k) for k, v in menc.items()), reverse=True)
        n_m, n_c, _neg, lem = cand[0]
        if n_m >= 3 and n_c * 2 >= len(con_texto):
            prot_col = lem
    ids: Dict[Tuple[str, str], str] = {}
    cont: Dict[str, int] = {}
    tabla: List[Dict[str, Any]] = []
    fases: Dict[str, str] = {}

    def rid(tipo: str, clave: str, forma: str, corte) -> str:
        key = (tipo, clave)
        if key in ids:
            return ids[key]
        if tipo in ("MENTOR", "FAMILIA", "PAREJA"):
            cont[tipo] = cont.get(tipo, 0) + 1
            r = tipo if cont[tipo] == 1 else f"{tipo}_{cont[tipo]}"
        else:
            cont[tipo] = cont.get(tipo, 0) + 1
            r = f"{tipo}_{cont[tipo]}"
        ids[key] = r
        tabla.append({"rol": r, "tipo": tipo, "forma": forma, "clave_generica": clave if forma == "generica" else None,
                      "huella_nombre": clave if forma == "nombre_propio" else None, "primer_corte": corte})
        return r

    por_corte = []
    for i, c in enumerate(cuts):
        cid = c.get("id") if c.get("id") is not None else (c.get("corte") if c.get("corte") is not None else i)
        k, t = textos[i]
        if not t:
            por_corte.append({"corte": cid, "campo_texto": None, "estado": "SIN_TEXTO", "protagonista": {"presente": False},
                              "agentes": [], "sin_otros_agentes": None, "no_agentes_nombrados": 0, "bienes": [],
                              "nota": "el corte no trae hecho/narracion: no se derivan personajes (no se inventa)"})
            continue
        segs = _segmentos(t, k == "hecho")
        segs_n = [_n(s) for s in segs]
        agentes: List[Dict[str, Any]] = []
        vistos = set()

        def add(tipo, clave, forma, seg_idx, pista):
            r = rid(tipo, clave, forma, cid)
            sn = segs_n[seg_idx] if seg_idx is not None and seg_idx < len(segs_n) else _n(t)
            if tipo == "ANTAGONISTA" or _hay(CONFLICTO, sn):
                fn, papel = "marte", "ANTAGONISTA_EN_CORTE"
            elif _hay(ALIANZA, sn) or clave in ("coalicion", "alianza"):
                fn, papel = "luna", "AYUDANTE_EN_CORTE"
            else:
                fn = {"MENTOR": "luna", "FAMILIA": "luna", "PAREJA": "luna", "AUTORIDAD": "balanza", "INSTITUCION": "balanza",
                      "COLECTIVO": "tierra"}.get(tipo)
                papel = {"luna": "AYUDANTE", "balanza": "ARBITRO_O_DESTINADOR", "tierra": "RECEPTOR_O_AFECTADO"}.get(fn, "SIN_FUNCION_POR_REGLA")
            if (r, fn) in vistos:
                return
            vistos.add((r, fn))
            agentes.append({"rol": r, "tipo": tipo, "forma": forma, "funcion": fn, "papel_en_corte": papel, "pista": pista})

        es_hecho = k == "hecho"
        n_no_agente = 0; alias = []; tipos_np_corte = set()
        for si, seg in enumerate(segs):
            sn = segs_n[si]
            # nombres propios con pista
            cubiertos = set()
            for sp in _spans_nombre(seg, not es_hecho or si == 0):
                cubiertos.update(range(sp["ini"], sp["ini"] + len(sp["span"].split())))
                tipo, pista = _clasificar_nombre(sp, sn)
                if not tipo:
                    n_no_agente += 1; continue
                if tipo == "ALIAS_PROTAGONISTA":
                    alias.append(_huella(sp["span"])); continue
                add(tipo, _huella(sp["span"]), "nombre_propio", si, pista)
                tipos_np_corte.add(tipo)
            # genéricos
            ws = [x[1] for x in _palabras(seg)]
            for wi, w in enumerate(ws):
                if wi in cubiertos:
                    continue
                nxt = " ".join(ws[wi:wi + 3])
                if nxt.startswith("estado de excepcion"):
                    continue
                if w in INSTITUCION_LEX:
                    lem = INSTITUCION_LEX[w]
                    if prot_col and lem == prot_col:
                        continue
                    add("INSTITUCION", lem, "generica", si, "lexico:" + w)
                elif w in COLECTIVO_LEX:
                    lem = COLECTIVO_LEX[w]
                    if prot_col and lem == prot_col:
                        continue
                    add("COLECTIVO", lem, "generica", si, "lexico:" + w)
                elif w in ANTAGONISTA_LEX:
                    add("ANTAGONISTA", ANTAGONISTA_LEX[w], "generica", si, "lexico:" + w)
                elif w in AUTORIDAD_LEX and not (wi + 1 < len(ws) and _palabras(seg)[wi + 1][0][:1].isupper()):
                    add("AUTORIDAD", AUTORIDAD_LEX[w], "generica", si, "lexico:" + w)
                elif w == "papa" and wi > 0 and ws[wi - 1] in ("el", "del", "al") :
                    add("AUTORIDAD", "papa", "generica", si, "lexico:el_papa")
                elif es_hecho and w in FAMILIA_LEX and "FAMILIA" not in tipos_np_corte:
                    add("FAMILIA", "familia", "generica", si, "lexico:" + w)
                elif w in PAREJA_LEX and "PAREJA" not in tipos_np_corte:
                    add("PAREJA", "pareja", "generica", si, "lexico:" + w)
                elif w in MENTOR_LEX and "MENTOR" not in tipos_np_corte:
                    add("MENTOR", "mentor", "generica", si, "lexico:" + w)
            for m in RX_ANTI.finditer(sn):
                if m.group(0).startswith(NO_ANTI):
                    continue
                stem = re.sub(r"(as|os|a|o)$", "", m.group(1))
                add("ANTAGONISTA", "anti_" + stem, "generica", si, "prefijo_anti")
        # ---------- protagonista
        prot: Dict[str, Any] = {"presente": False}
        if modo == "BIOGRAFICO":
            fac = _facetas(t)
            impl = any(_sujeto_implicito(s) for s in segs) if es_hecho else False
            if fac or impl:
                fids = []
                for _pos, f in fac:
                    if f not in fases.values():
                        fases[f"PROTAGONISTA_FASE_{len(fases) + 1}"] = f
                    fids.append(next(r for r, ff in fases.items() if ff == f))
                prot = {"presente": True, "modo": "sujeto_implicito_biografico", "fases": [{"rol": r, "faceta": fases[r]} for r in fids],
                        "alias_de_rol_huella": alias, "sin_faceta": not fids}
        elif modo == "COLECTIVO" and prot_col:
            if prot_col in [INSTITUCION_LEX.get(w) or COLECTIVO_LEX.get(w) for w in (x[1] for x in _palabras(t))]:
                prot = {"presente": True, "modo": "colectivo_mas_mencionado", "clave_generica": prot_col, "fases": [], "sin_faceta": True}
        otros = [a for a in agentes if a["tipo"] != "ALIAS_PROTAGONISTA"]
        bienes = []
        tn = _n(t)
        for w in re.findall(r"[a-z]+", tn):
            b = BIENES.get(w)
            if b and b not in bienes:
                bienes.append(b)
        por_corte.append({"corte": cid, "campo_texto": k, "estado": "DERIVADO", "protagonista": prot, "agentes": otros,
                          "sin_otros_agentes": not otros, "no_agentes_nombrados": n_no_agente, "bienes": bienes[:4],
                          "nota": ("el corte no nombra otro agente además del protagonista" if not otros else None)})
    return {"version": VERSION, "status": "EXECUTED", "can_decide_H": False, "escribe_H": False, "llm": False,
            "fuente": "solo texto propio del corte (" + "/".join(CAMPOS_TEXTO) + "); nunca source_note/question/person",
            "modo_caso": modo, "protagonista_colectivo_clave": prot_col,
            "fases_protagonista": [{"rol": r, "faceta": f} for r, f in fases.items()],
            "tabla_roles": tabla, "por_corte": por_corte,
            "n_cortes": len(cuts), "n_cortes_con_texto": len(con_texto)}


def funciones(ext: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Seis funciones por corte a partir de los personajes (ids de rol; sol = BIEN:<lema>)."""
    out = []
    for pc in ext.get("por_corte") or []:
        fn = {f: [] for f in FUNCIONES}
        prot = pc.get("protagonista") or {}
        if prot.get("presente"):
            fs = prot.get("fases") or []
            if not fs:
                fn["leon"].append("PROTAGONISTA")
            else:
                agentes_f = [x for x in fs if x["faceta"] in FACETAS_AGENTE]
                for x in fs:
                    f = FACETA_FUNCION.get(x["faceta"], "leon")
                    fn[f].append(x["rol"])
                if not agentes_f:
                    solo = [x for x in fs if x["faceta"] in ("FORMACION", "MEDIADOR")]
                    if solo:
                        fn["leon"].append(solo[0]["rol"])
        for a in pc.get("agentes") or []:
            if a.get("funcion") in fn:
                fn[a["funcion"]].append(a["rol"])
        fn["sol"] = ["BIEN:" + b for b in (pc.get("bienes") or [])]
        fn = {f: list(dict.fromkeys(v)) for f, v in fn.items()}
        occ: Dict[str, List[str]] = {}
        for f, v in fn.items():
            for r in v:
                occ.setdefault(r, []).append(f)
        cumulo = {r: fs for r, fs in occ.items() if len(fs) > 1}
        prot_roles = [r for r in occ if r.startswith("PROTAGONISTA")]
        prot_funcs = sorted({f for r in prot_roles for f in occ[r]}, key=FUNCIONES.index)
        luna_a = [r for r in fn["leon"] if r.startswith("PROTAGONISTA")] if fn["luna"] else []
        out.append({"corte": pc.get("corte"), "funciones": fn, "cumulo": cumulo, "mismo_agente_varias_funciones": bool(cumulo),
                    "protagonista_en_varias_funciones": len(prot_funcs) > 1, "funciones_del_protagonista": prot_funcs,
                    "luna_ayuda_a": luna_a, "estado_personajes": pc.get("estado"),
                    "sin_otros_agentes": pc.get("sin_otros_agentes")})
    return out
