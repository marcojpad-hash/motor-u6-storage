#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""filtro_entrada_dirigida_017.py — PATCH 017 (2026-10-07). Filtro anti-«datos dirigidos» (entrada) + chequeo de salida.

Contrato: CONTRATO_TRADUCCION_LLM_017 (md + schema json en la raíz del pack).
  LLM_ENTRADA (investiga + traduce) -> PAYLOAD agnóstico -> MOTOR (patrones/operaciones) -> cierre_final -> LLM_SALIDA.
Este módulo es DETERMINISTA, sin llamadas LLM, sin red, sin escribir archivos ni stores. can_decide_H=False.
No toca Engine, patterns ni el 244 (solo LEE patterns_final_v14.json para conocer las etiquetas de familia).

Reglas (cada bandera: tipo, regla, motivo, corte, campo, span, inicio, fin, accion, accion_en_vivo, severidad):
  IDENTIDAD_NOMBRE   nombres propios: veto 015 (TABLA/PREFIJOS de sujetos_014 + person/caldero_identity del caso)
                     + heurística de mayúscula (secuencia capitalizada fuera de inicio de oración; conectores de/di/von...;
                     numerales romanos). En el payload -> 'neutralize' (NP<k>, o PROTAGONISTA si es el sujeto del caso).
  IDENTIDAD_OBRA     títulos de obra detectables: tras verbo de autoría (compone/estrena/escribe/publica/pinta...) o
                     secuencia capitalizada con partículas de otra lengua (die/der/aus/dem/fan/di/il...). -> 'neutralize'.
  CALENDARIO         años 1000-2099, rangos y fechas ISO, 'd de <mes> (de aaaa)', '<mes> de aaaa', 'd <mes-abrev> aaaa',
                     'siglo X', 'mediados de <mes>'. -> 'neutralize' ('(fecha)'; prefijo 'aaaa-aaaa:' se quita).
  IDENTIDAD_EN_SOBRE / CALENDARIO_EN_SOBRE   person, caldero_identity, case_id, birth/death/z90, cuts[].date, random_seed
                     con forma de fecha: campos de CONTROL que hoy lee el motor (014 auto-exclusión, guardia Z90); no votan
                     (015). -> 'warn' (deben migrar al sidecar sellado; pendiente).
  FUENTE_EN_PAYLOAD  source_note / provenance_note / source_basis (citas) dentro del payload. -> 'move_to_sidecar' (warn en vivo).
  FUTURO_POST_Z      el corte declara estar después de Z ('tras el punto Z90') -> ese corte y los siguientes: 'reject-cut' (warn en vivo).
  FUTURO_RANGO       el texto del corte nombra años posteriores a la fecha del corte. -> 'warn' (re-cortar en LLM_ENTRADA).
  FUTURO_MARCADOR    'finalmente', 'más tarde', 'posterior(mente)', 'terminaría', 'lo que llevaría a', 'sentaría las bases'... -> 'warn'.
  FUTURO_DESENLACE   anuncio de desenlace/valoración de resultado ('éxito', 'fracaso', 'se desvanece', 'culmina'...) -> 'warn'.
  FUTURO_MUERTE_NO_FINAL  muerte/fallecimiento del protagonista en un corte que no es el último -> 'warn'.
  RETRO_FAMA         lenguaje de fama retrospectiva ('legendario', 'genio', 'prodigio', 'extraordinario', 'el mayor'...) -> 'strip'.
  DIRIGIDO_ETIQUETA_TEXTO  etiqueta de familia/arquetipo/rasgo evaluativo en texto ('gobernante', 'creador', 'ambicioso'...) -> 'warn'.
  DIRIGIDO_TOKEN_AUTOETIQUETA  token P/A/C (o tokens_activos) = lema de una familia del catálogo y además está en los
                     tokens_favor de esa familia (vota por la familia que nombra). fuerte -> 'warn' (copia F3: 'strip').
                     Lema sin voto propio -> débil ('warn').
  DIRIGIDO_ID_FAMILIA  token = id literal de familia (misma regla que guardian_entrada_autoevidencia_v1, 008). -> 'warn'.
  DIRIGIDO_TELEOLOGIA  juicio teleológico ('destinado a', 'su destino', 'vocación de', 'predestinado'...) -> 'warn'.
  SESGO_CONSULTOR    la pregunta trae etiquetas/evaluativos, o 3+ palabras seguidas de la pregunta aparecen copiadas en el payload. -> 'warn'.
  META_PROTOCOLO     marcas de protocolo en el payload ('punto Z90', 'ejercicio blanco', notion, patch...). -> 'strip'.
  SIN_TEXTO_CORTE    el corte no trae hecho/narracion (016 no puede derivar personajes). -> 'info'.
Modo en vivo (FILTRO_017, por defecto 'activo'): solo IDENTIDAD_NOMBRE / IDENTIDAD_OBRA / CALENDARIO se aplican (neutralize/strip)
y solo dentro del PAYLOAD (question, hecho/narracion/facts/texto, tokens, caldero_search_sources.texto, tokens_activos,
external_lights.token). Todo lo demás: warn + traza. 'traza' = solo reporta. 'off' = el motor no lo carga.
La traza que entra al resultado del motor NO lleva nombres: solo huella sha256[:8] del span (como 016).
"""
from __future__ import annotations
import copy
import hashlib
import json
import re
import unicodedata
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Set, Tuple

VERSION = "FILTRO_ENTRADA_DIRIGIDA_017_20261007"
CONTRATO = "CONTRATO_TRADUCCION_LLM_017"
BASE = Path(__file__).resolve().parent

CAMPOS_TEXTO_CORTE = ("hecho", "narracion", "facts", "texto")
CAMPOS_FUENTE = ("source_note", "provenance_note", "source_basis")
TIPOS_ACTIVOS_EN_VIVO = frozenset({"IDENTIDAD_NOMBRE", "IDENTIDAD_OBRA", "CALENDARIO"})
PLACEHOLDER_FECHA = "(fecha)"
PLACEHOLDER_SUJETO = "PROTAGONISTA"
# cabezas genéricas que se CONSERVAN delante del marcador (clase de agente, no identidad): 016 las usa para INSTITUCION
CABEZAS_GENERICAS = {"concilio", "congreso", "santa", "iglesia", "corte", "universidad", "academia", "senado", "parlamento", "consejo"}


# ------------------------------------------------------------------ utilidades
def _sa(s: str) -> str:
    """sin acentos, MISMA longitud (1 char -> 1 char) para conservar offsets."""
    return "".join((unicodedata.normalize("NFKD", ch)[:1] or ch) for ch in str(s))


def _n(s: str) -> str:
    return _sa(s).casefold()


def huella(s: str) -> str:
    return hashlib.sha256(str(s).strip().encode("utf-8")).hexdigest()[:8]


RX_PAL = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9]+")
RX_ROMANO = re.compile(r"^[IVXLC]+$")
CONECTORES = {"de", "del", "di", "da", "von", "van", "aus", "dem", "der", "la", "le", "y"}
PARTICULAS_OBRA = {"die", "der", "das", "dem", "aus", "fan", "tutte", "di", "il", "lo", "gli", "des", "von", "zu", "the", "of"}
VERBOS_OBRA = r"(?:compone|componen|estrena|estrenan|escribe|escriben|publica|publican|pinta|pintan|graba|graban|dirige|filma|esculpe)"
MESES = r"(?:enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|setiembre|octubre|noviembre|diciembre)"
MESES_AB = r"(?:ene|feb|mar|abr|may|jun|jul|ago|sep|sept|oct|nov|dic|jan|apr|aug|dec)"
_A = r"(?:1\d{3}|20\d{2})"
RX_CAL = [
    ("rango_prefijo", re.compile(r"^\s*" + _A + r"(?:-\d{2}){0,2}(?:\s*[-–]\s*" + _A + r"(?:-\d{2}){0,2})?\s*:\s*")),
    ("dia_mes_ano", re.compile(r"\b(?:el\s+)?\d{1,2}\s+de\s+" + MESES + r"(?:\s+de(?:l)?\s+" + _A + r")?\b", re.I)),
    ("dia_mesab_ano", re.compile(r"\b\d{1,2}\s+" + MESES_AB + r"\.?\s+" + _A + r"\b", re.I)),
    ("mes_ano", re.compile(r"\b(?:a\s+)?(?:mediados|principios|finales|fines)?\s*(?:de\s+)?" + MESES + r"\s+de(?:l)?\s+" + _A + r"\b", re.I)),
    ("mediados_mes", re.compile(r"\b(?:a\s+)?(?:mediados|principios|finales|fines)\s+de\s+" + MESES + r"\b", re.I)),
    ("siglo", re.compile(r"\bsiglo\s+(?:[IVXLC]+|\d{1,2})\b", re.I)),
    ("iso_rango_ano", re.compile(r"(?<![\w-])" + _A + r"(?:-\d{2}){0,2}(?:\s*[-–]\s*" + _A + r"(?:-\d{2}){0,2})?(?![\w])")),
]

FUTURO_MARCADORES = [r"\bfinalmente\b", r"\bm[aá]s\s+tarde\b", r"\bposteriormente\b", r"\bposterior\b", r"\ba\s+la\s+postre\b",
                     r"\bcon\s+el\s+tiempo\b", r"\btiempo\s+despu[eé]s\b", r"\ba[nñ]os\s+despu[eé]s\b", r"\bterminar[ií]a(n)?\b",
                     r"\bacabar[ií]a(n)?\b", r"\bllegar[ií]a(n)?\s+a\b", r"\bconvertir[ií]a(n)?\b", r"\blograr[ií]a(n)?\b",
                     r"\balcanzar[ií]a(n)?\b", r"\bmarcar[ií]a(n)?\b", r"\bllevar[ií]a(n)?\s+a\b", r"\bconducir[ií]a(n)?\s+a\b",
                     r"\bsentar[ií]a(n)?\s+las\s+bases\b", r"\bsienta\s+las\s+bases\b", r"\bpresagi\w*", r"\banticipa(ba)?\s+(su|el|la)\b",
                     r"\bpreludio\s+de\b", r"\bantes\s+de\s+(su|convertirse|llegar)\b"]
FUTURO_DESENLACE = [r"\b[eé]xito\w*", r"\bfracas\w*", r"\bse\s+desvanece\w*", r"\bculmina\w*", r"\bconsagra\w*", r"\btriunf\w*",
                    r"\bse\s+derrumba\w*", r"\bqueda\s+en\s+nada\b"]
RX_MUERTE_PROPIA = re.compile(r"\b(?:muere|fallece|muri[oó]|falleci[oó]|muerte)\b(?!\s+de\s+[A-ZÁÉÍÓÚÑ])", re.I)
RETRO_FAMA = [r"\blegendari\w*", r"\bgeni(?:o|os|al|ales|alidad)\b", r"\bprodigi\w*", r"\binmortal\w*", r"\bc[eé]lebres?\b",
              r"\bfamos[oa]s?\b", r"\bic[oó]nic\w*", r"\bvisionari\w*",
              r"\b(?:talento|talentos|capacidad|capacidades|dotes|habilidad|habilidades|don|inteligencia|memoria|precocidad)\s+(?:\w+\s+)?(?:extraordinari|excepcional)\w*",
              r"\bel\s+mayor\b", r"\bla\s+mayor\b", r"\bel\s+m[aá]s\s+grande\b", r"\buno\s+de\s+los\s+(?:m[aá]s|mayores)\b",
              r"\bobra\s+maestra\b", r"\bmagistral\w*", r"\bpioner[oa]s?\b", r"\badelantad[oa]\s+a\s+su\s+tiempo\b"]
TELEOLOGIA = [r"\bdestinad[oa]\s+a\b", r"\bsu\s+destino\b", r"\bpredestinad\w*", r"\bvocaci[oó]n\s+de\b", r"\bllamad[oa]\s+a\s+ser\b",
              r"\bnaci[oó]\s+para\b", r"\bcamino\s+hacia\s+(?:la\s+)?(?:grandeza|gloria|cima)\b"]
EVALUATIVOS_TEXTO = [r"\bambicios[oa]s?\b", r"\bcarism[aá]tic\w*", r"\brebelde\w*", r"\bmegal[oó]man\w*", r"\bnarcisist\w*",
                     r"\bheroic\w*", r"\bheroism\w*", r"\btir[aá]nic\w*", r"\bdesp[oó]tic\w*", r"\bl[ií]der\s+nat\w*", r"\bambici[oó]n\b"]
META_RX = re.compile(r"(?i)\b(punto\s+Z\s*\d*|Z90|Z\s*=|ejercicios?\s+blancos?|notion|protocolo|checkpoint|patch\s*\d+|sombrero\s+blanco|"
                     r"juicio\s+est[eé]tico|fecha\s+de\s+protocolo|recorte\s+de\s+protocolo|metadato\s+de\s+protocolo|cuerpo\s+vac[ií]o|palo\s+se\s+sostiene)\b")
RX_POST_Z = re.compile(r"(?i)\b(tras|despu[eé]s\s+de)\s+(el\s+)?(punto\s+)?Z\s*\d*\b")

# prefijos de esquema de los ids de familia -> lema (etiqueta) de la familia
_PREF_FAM = re.compile(r"^(?:\d+_|arquetipo_el_|arquetipo_|situacion_dramatica_|schwartz_\d+_|kwml_\d+_|bbk_\d+_|weber_\d+_|"
                       r"anacyclosis_\d+_|erikson_\d+_|ttm_\d+_|apego_\d+_|duelo_bonanno_\d+_|turner_\d+_|mauss_\d+_|berlin_\d+_|"
                       r"minsky_\d+_|kondratiev_\d+_|social_\d+_|predictivo_\d+_|monomito_\d+_|cliodinamica_\d+_|tainter_\d+_|"
                       r"strauss_howe_\d+_|dialectica_\d+_|jaldun_\d+_|spengler_\d+_|eterno_retorno_\d+_|frye_mythos_|mbti_factor_|"
                       r"mbti_|utopia_|distopia_|dumezil_|sustancias_\d+_|trayectoria_|candidato_)")
# familias cuyo lema es tipo de personaje/arquetipo (etiqueta evaluativa si aparece en TEXTO)
_FAM_PERSONAJE = re.compile(r"^(arquetipo_|kwml_|bbk_|berlin_|heroe$|mentor$|sombra$|aliado$|guardian_del_umbral$|heraldo$|camaleon$|picar_trickster$)")
STOP_Q = {"que", "qué", "se", "en", "de", "la", "el", "los", "las", "hasta", "del", "por", "para", "con", "una", "uno", "y", "o", "a", "al",
          "su", "sus", "es", "como", "cómo", "cual", "cuál", "corte", "caso"}


def _cargar_catalogo(catalogo: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    if catalogo:
        return dict(catalogo)
    p = BASE / "patterns_final_v14.json"
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def etiquetas_catalogo(catalogo: Mapping[str, Any]) -> Dict[str, Any]:
    lema_a_fams: Dict[str, List[str]] = {}
    personaje: Set[str] = set()
    for fam in catalogo or {}:
        lema = _PREF_FAM.sub("", fam)
        if not lema:
            continue
        lema_a_fams.setdefault(_n(lema), []).append(fam)
        if _FAM_PERSONAJE.match(fam):
            personaje.add(_n(lema).replace("_", " "))
    return {"lema_a_fams": lema_a_fams, "personaje": personaje, "ids": {f.casefold(): f for f in catalogo or {}}}


def _nombres_tabla() -> Tuple[Set[str], Dict[str, str]]:
    """Veto 015: tokens de nombres de TABLA/PREFIJOS de sujetos_014 (si está en el directorio)."""
    try:
        import importlib.util
        p = BASE / "sujetos_014.py"
        spec = importlib.util.spec_from_file_location("_s014_para_017", str(p))
        m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)  # type: ignore
        toks = {_n(t) for t in m.nombres_que_no_votan(None)}
        visibles = {cid: v[2] for cid, v in m.TABLA.items() if v[2]}
        for pref, _s, nom in m.PREFIJOS:
            visibles.setdefault("PREFIJO:" + pref, nom)
        return toks, visibles
    except Exception:
        return set(), {}


def _nombres_sujeto_caso(case: Mapping[str, Any], visibles: Mapping[str, str]) -> Set[str]:
    """tokens normalizados del nombre del sujeto de ESTE caso (person / caldero_identity / TABLA por case_id o prefijo)."""
    out: Set[str] = set()
    fuentes = [case.get("person")]
    ci = case.get("caldero_identity") or {}
    if isinstance(ci, Mapping):
        fuentes.append(ci.get("nombre_o_alias"))
    cid = str(case.get("case_id") or "")
    if cid in visibles:
        fuentes.append(visibles[cid])
    for k, v in visibles.items():
        if k.startswith("PREFIJO:") and cid.upper().startswith(k[8:]):
            fuentes.append(v)
    for f in fuentes:
        for w in RX_PAL.findall(str(f or "")):
            if len(w) >= 2 and not w.isdigit() and not w.endswith("sellado"):
                out.add(_n(w))
    out.discard("ciego"); out.discard("15"); out.discard("sellado")
    return out


# ------------------------------------------------------------------ detectores sobre un texto
def _inicio_oracion(txt: str, pos: int) -> bool:
    j = pos - 1
    while j >= 0 and txt[j] in " \t\n\"'«“(¿¡":
        if txt[j] in "¿¡":
            return True
        j -= 1
    return j < 0 or txt[j] in ".!?"


def _spans_nombre(txt: str, tabla_toks: Set[str], sujeto_toks: Set[str]) -> List[Tuple[int, int, str]]:
    ws = [(m.start(), m.end(), m.group(0)) for m in RX_PAL.finditer(txt)]
    out = []; i = 0
    while i < len(ws):
        s, e, w = ws[i]
        cap = w[:1].isupper() and not w[:1].isdigit()
        allcaps = len(w) >= 2 and w.isupper()
        if cap and not allcaps and len(w) >= 2:
            j = i + 1
            while j < len(ws):
                sj, ej, wj = ws[j]
                gap = txt[ws[j - 1][1]:sj]
                if gap.strip(" ") not in ("",):
                    break
                if (wj[:1].isupper() and not wj[:1].isdigit() and not (len(wj) >= 2 and wj.isupper() and not RX_ROMANO.match(wj))) or RX_ROMANO.match(wj):
                    j += 1; continue
                if _n(wj) in CONECTORES - {"y"} and j + 1 < len(ws) and ws[j + 1][2][:1].isupper() and txt[ej:ws[j + 1][0]].strip(" ") == "":
                    j += 1; continue
                break
            span_s, span_e = s, ws[j - 1][1]
            span = txt[span_s:span_e]
            n_pal = j - i
            nw = _n(w)
            if _inicio_oracion(txt, s) and n_pal == 1 and nw not in tabla_toks and nw not in sujeto_toks:
                i = j; continue  # palabra capitalizada sola al inicio de oración: no se trata como nombre (conservador)
            if span.strip() in (PLACEHOLDER_SUJETO,) or re.fullmatch(r"NP\d+", span.strip()):
                i = j; continue
            out.append((span_s, span_e, span))
            i = j
        elif allcaps and (_n(w) in tabla_toks or _n(w) in sujeto_toks) and len(w) >= 3:
            out.append((s, e, w)); i += 1
        else:
            # nombre del veto 015 escrito en minúscula / dentro de identificador (p.ej. 'mozart_nocturna')
            i += 1
    return out


def _spans_obra(txt: str) -> List[Tuple[int, int, str]]:
    out = []
    for m in re.finditer(r"(?i)\b" + VERBOS_OBRA + r"(?:\s+y\s+" + VERBOS_OBRA + r")?\s+", txt):
        k = m.end()
        while True:
            mm = re.match(r"([A-ZÀ-ÖØ-Þ][^;,.:()]*?)(?=\s+y\s+|,\s*|;|\.|:|\(|\s+en\s+|\s+para\s+|\s+con\s+|$)", txt[k:])
            if not mm:
                break
            out.append((k, k + len(mm.group(1)), mm.group(1)))
            k2 = k + len(mm.group(1))
            sep = re.match(r"(\s+y\s+|,\s*)(?=[A-ZÀ-ÖØ-Þ])", txt[k2:])
            if not sep:
                break
            k = k2 + len(sep.group(1))
    for m in re.finditer(r"\b(?i:producci[oó]n)\s+\w+\s+de\s+([A-ZÀ-ÖØ-Þ][\wÀ-ÿ]*(?:\s+[A-ZÀ-ÖØ-Þ][\wÀ-ÿ]*)*)", txt):
        out.append((m.start(1), m.end(1), m.group(1)))
    # secuencias capitalizadas con partículas de otra lengua (Die Entführung aus dem Serail, Così fan tutte)
    for m in re.finditer(r"\b[A-ZÀ-ÖØ-Þ][\wÀ-ÿ]*(?:\s+(?:[A-ZÀ-ÖØ-Þ][\wÀ-ÿ]*|die|der|das|dem|aus|fan|tutte|di|il|des|von|zu)\b)+", txt):
        ws = [_n(x) for x in m.group(0).split()]
        if any(w in PARTICULAS_OBRA for w in ws[1:]) or ws[0] in {"die", "der", "das", "il", "the"}:
            out.append((m.start(), m.end(), m.group(0)))
    return out


def _spans_cal(txt: str) -> List[Tuple[int, int, str, str]]:
    out = []
    for nombre, rx in RX_CAL:
        for m in rx.finditer(txt):
            if m.group(0).strip():
                g = m.group(0); ini = m.start() + (len(g) - len(g.lstrip()))
                out.append((ini, m.end(), txt[ini:m.end()], nombre))
    return out


def _fusionar(spans: List[Tuple]) -> List[Tuple]:
    """quita solapes: gana el span más largo (y el primero)."""
    spans = sorted(spans, key=lambda x: (x[0], -(x[1] - x[0])))
    out = []; fin = -1
    for sp in spans:
        if sp[0] >= fin:
            out.append(sp); fin = sp[1]
        elif sp[1] > fin and out and (sp[1] - sp[0]) > (out[-1][1] - out[-1][0]):
            out[-1] = sp; fin = sp[1]
    return out


def _rx_flags(txt: str, pats: Iterable[str]) -> List[Tuple[int, int, str]]:
    out = []
    for p in pats:
        for m in re.finditer(p, txt, re.I):
            out.append((m.start(), m.end(), m.group(0)))
    return out


# ------------------------------------------------------------------ análisis de un caso
class _Ctx:
    def __init__(self, case: Mapping[str, Any], catalogo: Mapping[str, Any]):
        self.case = case
        self.cat = catalogo
        self.et = etiquetas_catalogo(catalogo)
        self.tabla_toks, self.visibles = _nombres_tabla()
        self.sujeto_toks = _nombres_sujeto_caso(case, self.visibles)
        self.mapa: Dict[str, str] = {}   # span normalizado -> placeholder (SELLADO: no sale al motor)
        self.n = 0

    def placeholder(self, span: str) -> str:
        key = _n(span).strip()
        if key in self.mapa:
            return self.mapa[key]
        toks = {_n(w) for w in RX_PAL.findall(span) if not RX_ROMANO.match(w) or len(w) > 4}
        toks_r = {_n(w) for w in RX_PAL.findall(span)}
        if toks_r and (toks_r <= (self.sujeto_toks | {"ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x"})) and (toks & self.sujeto_toks):
            ph = PLACEHOLDER_SUJETO
        else:
            self.n += 1; ph = f"NP{self.n}"
            pal = RX_PAL.findall(span)
            if len(pal) >= 2 and _n(pal[0]) in CABEZAS_GENERICAS:
                ph = pal[0] + " " + ph
        self.mapa[key] = ph
        return ph


def _flag(tipo, regla, motivo, corte, campo, span, ini, fin, accion, sev, **kw):
    acc_vivo = accion if (tipo in TIPOS_ACTIVOS_EN_VIVO and accion in ("neutralize", "strip")) else ("info" if accion == "info" else "warn")
    d = {"tipo": tipo, "regla": regla, "motivo": motivo, "corte": corte, "campo": campo, "span": span, "inicio": ini, "fin": fin,
         "accion": accion, "accion_en_vivo": acc_vivo, "severidad": sev}
    d.update(kw)
    return d


def _flags_texto(ctx: _Ctx, txt: str, corte, campo: str, es_payload: bool, idx_corte: Optional[int], n_cortes: int,
                 fecha_corte: Optional[str]) -> List[Dict[str, Any]]:
    fl: List[Dict[str, Any]] = []
    if not isinstance(txt, str) or not txt.strip():
        return fl
    obras = _spans_obra(txt)
    cal = _spans_cal(txt)
    noms = _spans_nombre(txt, ctx.tabla_toks, ctx.sujeto_toks)
    # nombres del veto 015 dentro de identificadores/minúscula (p.ej. 'MOZART_NOCTURNA', 'mozart')
    for m in re.finditer(r"[A-Za-zÀ-ÖØ-öø-ÿ]+", txt):
        w = _n(m.group(0))
        if (w in ctx.sujeto_toks or w in ctx.tabla_toks) and len(w) >= 3 and not any(s <= m.start() < e for s, e, _ in noms):
            if not (m.group(0)[:1].isupper() and not m.group(0).isupper()):
                noms.append((m.start(), m.end(), m.group(0)))
    todos = [(s, e, sp, "OBRA") for s, e, sp in obras] + [(s, e, sp, "CAL:" + k) for s, e, sp, k in cal] + [(s, e, sp, "NOM") for s, e, sp in noms]
    for s, e, sp, k in _fusionar(todos):
        if k == "OBRA":
            fl.append(_flag("IDENTIDAD_OBRA", "R_OBRA", "título de obra detectable (identifica al sujeto)", corte, campo, sp, s, e,
                            "neutralize" if es_payload else "warn", "ALTA"))
        elif k.startswith("CAL:"):
            fl.append(_flag("CALENDARIO" if es_payload else "CALENDARIO_EN_SOBRE", "R_CAL_" + k[4:], "marcador de calendario (año/fecha)",
                            corte, campo, sp, s, e, "neutralize" if es_payload else "warn", "ALTA"))
        else:
            fl.append(_flag("IDENTIDAD_NOMBRE" if es_payload else "IDENTIDAD_EN_SOBRE",
                            "R_NOMBRE_VETO015" if (_n(sp) in ctx.tabla_toks or set(_n(sp).split()) & (ctx.tabla_toks | ctx.sujeto_toks)) else "R_NOMBRE_MAYUSCULA",
                            "nombre propio (persona/lugar/institución)", corte, campo, sp, s, e, "neutralize" if es_payload else "warn", "ALTA"))
    if not es_payload:
        return fl
    for s, e, sp in _rx_flags(txt, FUTURO_MARCADORES):
        fl.append(_flag("FUTURO_MARCADOR", "R_FUT_MARCADOR", "marcador de información posterior al corte", corte, campo, sp, s, e, "warn", "MEDIA"))
    for s, e, sp in _rx_flags(txt, FUTURO_DESENLACE):
        fl.append(_flag("FUTURO_DESENLACE", "R_FUT_DESENLACE", "anuncio/valoración de desenlace", corte, campo, sp, s, e, "warn", "MEDIA"))
    if idx_corte is not None and idx_corte < n_cortes - 1:
        for m in RX_MUERTE_PROPIA.finditer(txt):
            fl.append(_flag("FUTURO_MUERTE_NO_FINAL", "R_FUT_MUERTE", "muerte del protagonista anunciada antes del último corte", corte, campo,
                            m.group(0), m.start(), m.end(), "warn", "ALTA"))
    if fecha_corte and re.match(r"^\d{4}", str(fecha_corte)):
        fy = int(str(fecha_corte)[:4])
        anos = [int(x) for x in re.findall(r"(?<!\d)(1\d{3}|20\d{2})(?!\d)", txt)]
        tarde = sorted({a for a in anos if a > fy})
        if tarde:
            fl.append(_flag("FUTURO_RANGO", "R_FUT_RANGO", f"el texto nombra años posteriores a la fecha del corte ({fy})", corte, campo,
                            ",".join(str(a) for a in tarde), None, None, "warn", "MEDIA", n_anos_posteriores=len(tarde), max_exceso_anos=max(tarde) - fy))
    for s, e, sp in _rx_flags(txt, RETRO_FAMA):
        fl.append(_flag("RETRO_FAMA", "R_RETRO", "lenguaje de fama retrospectiva (juicio desde el futuro)", corte, campo, sp, s, e, "strip", "MEDIA"))
    for s, e, sp in _rx_flags(txt, TELEOLOGIA):
        fl.append(_flag("DIRIGIDO_TELEOLOGIA", "R_TELEO", "juicio teleológico (destino/vocación)", corte, campo, sp, s, e, "warn", "MEDIA"))
    for s, e, sp in _rx_flags(txt, EVALUATIVOS_TEXTO):
        fl.append(_flag("DIRIGIDO_ETIQUETA_TEXTO", "R_EVAL", "rasgo evaluativo en vez de acto observable", corte, campo, sp, s, e, "warn", "MEDIA"))
    tn = _n(txt)
    for lema in sorted(ctx.et["personaje"]):
        for m in re.finditer(r"\b" + re.escape(lema) + r"(?:es|s|a|as)?\b", tn):
            fl.append(_flag("DIRIGIDO_ETIQUETA_TEXTO", "R_ETIQUETA_ARQUETIPO", "etiqueta de arquetipo/tipo de personaje del catálogo en el texto",
                            corte, campo, txt[m.start():m.end()], m.start(), m.end(), "warn", "MEDIA", lema=lema))
    for m in META_RX.finditer(txt):
        fl.append(_flag("META_PROTOCOLO", "R_META", "marca de protocolo/armado del caso en el payload", corte, campo, m.group(0), m.start(), m.end(), "strip", "BAJA"))
    return fl


def _flags_tokens(ctx: _Ctx, pares, corte, campo: str) -> List[Dict[str, Any]]:
    fl = []
    for item in pares or []:
        t = item[0] if isinstance(item, (list, tuple)) and item else (item.get("token") if isinstance(item, Mapping) else item)
        if t is None:
            continue
        t = str(t); k = _n(t).strip()
        if re.fullmatch(r"(1\d{3}|20\d{2})([-_/]\d{1,2}){0,2}", k) or re.fullmatch(r"\d+", k):
            fl.append(_flag("CALENDARIO", "R_TOKEN_NUMERO", "token numérico/fecha en el payload", corte, campo, t, None, None, "strip", "ALTA"))
            continue
        if k in ctx.tabla_toks or k in ctx.sujeto_toks:
            fl.append(_flag("IDENTIDAD_NOMBRE", "R_TOKEN_NOMBRE", "token = nombre propio (veto 015)", corte, campo, t, None, None, "strip", "ALTA"))
            continue
        if k in ctx.et["ids"]:
            fl.append(_flag("DIRIGIDO_ID_FAMILIA", "R_TOKEN_ID", "token = id literal de familia del catálogo (008)", corte, campo, t, None, None,
                            "warn", "ALTA", familias=[ctx.et["ids"][k]]))
            continue
        fams = ctx.et["lema_a_fams"].get(k)
        if fams:
            propias = [f for f in fams if t in ((ctx.cat.get(f) or {}).get("tokens_favor") or {})]
            if propias:
                fl.append(_flag("DIRIGIDO_TOKEN_AUTOETIQUETA", "R_TOKEN_AUTOETIQUETA_FUERTE",
                                "token = etiqueta de familia y vota por esa misma familia (se le da a la hipótesis su propio nombre)",
                                corte, campo, t, None, None, "warn", "ALTA", familias=propias, fuerte=True, accion_copia_F3="strip"))
            else:
                fl.append(_flag("DIRIGIDO_TOKEN_AUTOETIQUETA", "R_TOKEN_AUTOETIQUETA_DEBIL", "token = etiqueta de familia (sin voto propio)",
                                corte, campo, t, None, None, "warn", "BAJA", familias=fams, fuerte=False))
    return fl


def analizar(case: Mapping[str, Any], catalogo: Optional[Mapping[str, Any]] = None, _ctx: Optional[_Ctx] = None) -> Dict[str, Any]:
    """Modo REPORTE: no modifica nada. Devuelve banderas completas (con spans: uso de la CAPA LLM / sidecar sellado)."""
    cat = _cargar_catalogo(catalogo)
    ctx = _ctx or _Ctx(case, cat)
    fl: List[Dict[str, Any]] = []
    cuts = list(case.get("cuts") or [])
    n = len(cuts)
    # sobre (campos de control / sellados)
    for k in ("person", "case_id", "birth_date", "death_date", "z90_date"):
        v = case.get(k)
        if v:
            fl += _flags_texto(ctx, str(v), None, k, False, None, n, None)
    ci = case.get("caldero_identity") or {}
    if isinstance(ci, Mapping) and ci.get("nombre_o_alias") and not str(ci.get("nombre_o_alias")).endswith("sellado"):
        fl += _flags_texto(ctx, str(ci["nombre_o_alias"]), None, "caldero_identity.nombre_o_alias", False, None, n, None)
    rs = case.get("random_seed")
    if isinstance(rs, int) and re.fullmatch(r"(19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])", str(rs)):
        fl.append(_flag("CALENDARIO_EN_SOBRE", "R_SEED_FECHA", "random_seed con forma de fecha (no se toca: cambia Monte Carlo)", None,
                        "random_seed", str(rs), None, None, "warn", "BAJA"))
    for k in CAMPOS_FUENTE:
        if case.get(k):
            fl.append(_flag("FUENTE_EN_PAYLOAD", "R_FUENTE", "cita/procedencia dentro del input: va al sidecar sellado", None, k,
                            str(case[k])[:60], None, None, "move_to_sidecar", "MEDIA"))
    # pregunta del consultor
    q = str(case.get("question") or "")
    if q:
        fl += _flags_texto(ctx, q, None, "question", True, None, n, None)
        qn = [w for w in RX_PAL.findall(_n(q)) if w not in STOP_Q and not w.isdigit() and len(w) >= 3]
        trig = {" ".join(qn[i:i + 3]) for i in range(len(qn) - 2)}
        if trig:
            for i, c in enumerate(cuts):
                for campo in CAMPOS_TEXTO_CORTE:
                    v = c.get(campo)
                    if isinstance(v, list): v = " ".join(map(str, v))
                    if not isinstance(v, str): continue
                    vn = " ".join(w for w in RX_PAL.findall(_n(v)) if w not in STOP_Q and not w.isdigit() and len(w) >= 3)
                    for t in sorted(trig):
                        if t in vn:
                            fl.append(_flag("SESGO_CONSULTOR", "R_Q_COPIA", "3+ palabras de la pregunta copiadas en el payload", c.get("id"), campo, t,
                                            None, None, "warn", "MEDIA"))
        for lema in sorted(ctx.et["personaje"]):
            if re.search(r"\b" + re.escape(lema) + r"(?:es|s|a|as)?\b", _n(q)):
                fl.append(_flag("SESGO_CONSULTOR", "R_Q_ETIQUETA", "la pregunta trae una etiqueta de hipótesis (no copiar al payload)", None,
                                "question", lema, None, None, "warn", "MEDIA"))
        for s, e, sp in _rx_flags(q, EVALUATIVOS_TEXTO + RETRO_FAMA + TELEOLOGIA):
            fl.append(_flag("SESGO_CONSULTOR", "R_Q_EVALUATIVO", "la pregunta trae juicio evaluativo/teleológico (no copiar al payload)", None,
                            "question", sp, s, e, "warn", "MEDIA"))
    # campos de nivel caso que van al motor
    for i, s in enumerate(case.get("caldero_search_sources") or []):
        if isinstance(s, Mapping):
            for campo in ("texto", "snippet", "title"):
                if s.get(campo):
                    fl += _flags_texto(ctx, str(s[campo]), None, f"caldero_search_sources[{i}].{campo}", True, None, n, None)
    cai = case.get("caldero_archetype_input") or {}
    if isinstance(cai, Mapping) and cai.get("tokens_activos"):
        fl += _flags_tokens(ctx, [[t, None] for t in cai.get("tokens_activos") or []], None, "caldero_archetype_input.tokens_activos")
        toks_cortes = {str(p[0]) for c in cuts for e in ("P", "A", "C") for p in (c.get(e) or []) if isinstance(p, (list, tuple)) and p}
        ajenos = [t for t in cai.get("tokens_activos") or [] if str(t) not in toks_cortes]
        if ajenos:
            fl.append(_flag("DIRIGIDO_SELECCION", "R_TOKENS_ACTIVOS_AJENOS", "tokens_activos que no salen de ningún corte (selección del LLM)",
                            None, "caldero_archetype_input.tokens_activos", ",".join(map(str, ajenos)), None, None, "warn", "MEDIA"))
    for i, l in enumerate(case.get("external_lights") or []):
        if isinstance(l, Mapping) and l.get("token"):
            fl += _flags_tokens(ctx, [[l.get("token"), l.get("peso")]], None, f"external_lights[{i}].token")
    # cortes
    post_z_desde = None
    for i, c in enumerate(cuts):
        cid = c.get("id")
        txt_any = False
        for campo in CAMPOS_TEXTO_CORTE:
            v = c.get(campo)
            if isinstance(v, list): v = " ".join(map(str, v))
            if isinstance(v, str) and v.strip():
                txt_any = True
                fl += _flags_texto(ctx, v, cid, campo, True, i, n, c.get("date"))
                if post_z_desde is None and RX_POST_Z.search(v):
                    post_z_desde = i
        if not txt_any:
            fl.append(_flag("SIN_TEXTO_CORTE", "R_SIN_TEXTO", "el corte no trae hecho/narracion (016 no deriva personajes; LLM_ENTRADA debe escribir 'hecho')",
                            cid, "hecho", None, None, None, "info", "BAJA"))
        if c.get("date"):
            fl += _flags_texto(ctx, str(c.get("date")), cid, "date", False, i, n, None)
        for campo in ("source_note",):
            if c.get(campo):
                fl.append(_flag("FUENTE_EN_PAYLOAD", "R_FUENTE", "cita/procedencia dentro del corte: va al sidecar sellado", cid, campo,
                                str(c[campo])[:60], None, None, "move_to_sidecar", "MEDIA"))
        for e in ("P", "A", "C"):
            fl += _flags_tokens(ctx, c.get(e), cid, e)
    if post_z_desde is not None:
        for j in range(post_z_desde, n):
            fl.append(_flag("FUTURO_POST_Z", "R_POST_Z", "corte posterior al punto Z declarado en el propio input (información posterior al congelamiento)",
                            cuts[j].get("id"), "corte", None, None, None, "reject-cut", "ALTA", declarado_en=cuts[post_z_desde].get("id")))
    return {"version": VERSION, "contrato": CONTRATO, "case_id": case.get("case_id"), "banderas": fl, "resumen": resumen(fl),
            "mapa_nombres_sellado": dict(ctx.mapa), "can_decide_H": False}


def resumen(fl: List[Dict[str, Any]]) -> Dict[str, Any]:
    por_tipo: Dict[str, int] = {}
    por_accion_vivo: Dict[str, int] = {}
    for f in fl:
        por_tipo[f["tipo"]] = por_tipo.get(f["tipo"], 0) + 1
        por_accion_vivo[f["accion_en_vivo"]] = por_accion_vivo.get(f["accion_en_vivo"], 0) + 1
    return {"n": len(fl), "por_tipo": dict(sorted(por_tipo.items())), "por_accion_en_vivo": dict(sorted(por_accion_vivo.items()))}


# ------------------------------------------------------------------ aplicar acciones
def _aplicar_texto(ctx: _Ctx, txt: str, flags: List[Dict[str, Any]], tipos: Set[str], quitar_espacios: bool, modo_fuente: bool) -> str:
    sel = [f for f in flags if f["tipo"] in tipos and f.get("inicio") is not None and f["accion"] in ("neutralize", "strip")]
    sel = sorted(sel, key=lambda f: (f["inicio"], -(f["fin"] - f["inicio"])))
    out = []; k = 0
    for f in sel:
        if f["inicio"] < k:
            continue
        out.append(txt[k:f["inicio"]])
        if f["tipo"] == "CALENDARIO":
            rep = "" if (f["regla"] == "R_CAL_rango_prefijo" or modo_fuente) else PLACEHOLDER_FECHA
        elif f["tipo"] in ("IDENTIDAD_NOMBRE", "IDENTIDAD_OBRA"):
            rep = "" if modo_fuente else ctx.placeholder(f["span"])
        else:
            rep = ""
        out.append(rep); k = f["fin"]
    out.append(txt[k:])
    r = "".join(out)
    r = re.sub(r"[ \t]{2,}", " ", r)
    r = re.sub(r"\s+([,;.:])", r"\1", r)
    r = re.sub(r"\(\s*\)", "", r)
    if modo_fuente:
        r = re.sub(r"([,;:])(\s*[,;:])+", r"\1", r)
        r = re.sub(r"\s+([,;.:])", r"\1", r)
        r = re.sub(r"^[\s,;:]+", "", r)
    return r.strip() if quitar_espacios else r


def _aplicar_identificador(ctx: _Ctx, s: str) -> str:
    """identificadores tipo case_id/question por defecto: tokens '_' -> nombres fuera, dígitos de fecha fuera."""
    partes = re.split(r"(_)", s)
    out = []
    for p in partes:
        if p == "_":
            out.append(p); continue
        k = _n(p)
        if k in ctx.sujeto_toks or k in ctx.tabla_toks:
            out.append(PLACEHOLDER_SUJETO)
        elif re.fullmatch(r"(19|20)\d{6}|(1\d{3}|20\d{2})", k):
            out.append("")
        else:
            out.append(p)
    r = re.sub(r"_+", "_", "".join(out)).strip("_")
    return r or "caso"


def aplicar(case: Mapping[str, Any], tipos: Set[str], catalogo: Optional[Mapping[str, Any]] = None,
            rechazar_post_z: bool = False, quitar_autoetiquetas: bool = False, mover_fuentes: bool = False) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Devuelve (payload, informe). No modifica `case`. `tipos`: tipos de bandera cuyas acciones neutralize/strip se aplican."""
    cat = _cargar_catalogo(catalogo)
    ctx = _Ctx(case, cat)
    rep = analizar(case, cat, _ctx=ctx)
    fl = rep["banderas"]
    out = copy.deepcopy(dict(case))
    by = {}
    for f in fl:
        by.setdefault((f["corte"], f["campo"]), []).append(f)
    aplicadas = []
    # pregunta
    q = case.get("question")
    if isinstance(q, str) and q:
        if re.fullmatch(r"[A-Za-z0-9_]+", q) and "_" in q:
            nq = _aplicar_identificador(ctx, q) if (tipos & {"IDENTIDAD_NOMBRE", "CALENDARIO"}) else q
        else:
            nq = _aplicar_texto(ctx, q, by.get((None, "question"), []), tipos, True, False)
        if nq != q:
            out["question"] = nq; aplicadas.append({"campo": "question", "huella_antes": huella(q), "huella_despues": huella(nq)})
    # fuentes de búsqueda (texto de fuente: nombres/fechas se QUITAN, no se ponen marcadores: evita tokens NP<k> en el store de vecinos)
    for i, s in enumerate(out.get("caldero_search_sources") or []):
        if isinstance(s, dict):
            for campo in ("texto", "snippet", "title"):
                if s.get(campo):
                    nv = _aplicar_texto(ctx, str(s[campo]), by.get((None, f"caldero_search_sources[{i}].{campo}"), []), tipos, True, True)
                    if nv != s[campo]:
                        aplicadas.append({"campo": f"caldero_search_sources[{i}].{campo}", "huella_antes": huella(s[campo]), "huella_despues": huella(nv)})
                        s[campo] = nv
    # tokens_activos / lights
    cai = out.get("caldero_archetype_input")
    if isinstance(cai, dict) and cai.get("tokens_activos"):
        quitar = {f["span"] for f in by.get((None, "caldero_archetype_input.tokens_activos"), [])
                  if (f["tipo"] in tipos and f["accion"] == "strip") or (quitar_autoetiquetas and f.get("fuerte"))}
        if quitar:
            cai["tokens_activos"] = [t for t in cai["tokens_activos"] if str(t) not in quitar]
            aplicadas.append({"campo": "caldero_archetype_input.tokens_activos", "quitados": sorted(quitar)})
    lights = out.get("external_lights") or []
    if lights:
        keep = []
        for i, l in enumerate(lights):
            fs = by.get((None, f"external_lights[{i}].token"), [])
            if any((f["tipo"] in tipos and f["accion"] == "strip") or (quitar_autoetiquetas and f.get("fuerte")) for f in fs):
                aplicadas.append({"campo": f"external_lights[{i}]", "quitado": True}); continue
            keep.append(l)
        out["external_lights"] = keep
    # cortes
    post_z = {f["corte"] for f in fl if f["tipo"] == "FUTURO_POST_Z"}
    nuevos = []
    for c in out.get("cuts") or []:
        cid = c.get("id")
        if rechazar_post_z and cid in post_z:
            aplicadas.append({"corte": cid, "accion": "reject-cut", "motivo": "FUTURO_POST_Z"}); continue
        for campo in CAMPOS_TEXTO_CORTE:
            v = c.get(campo)
            if isinstance(v, str) and v.strip():
                nv = _aplicar_texto(ctx, v, by.get((cid, campo), []), tipos, True, False)
                if nv != v:
                    c[campo] = nv; aplicadas.append({"corte": cid, "campo": campo, "huella_antes": huella(v), "huella_despues": huella(nv)})
        for e in ("P", "A", "C"):
            fs = by.get((cid, e), [])
            quitar = {f["span"] for f in fs if (f["tipo"] in tipos and f["accion"] == "strip") or (quitar_autoetiquetas and f.get("fuerte"))}
            if quitar and c.get(e):
                c[e] = [p for p in c[e] if not (isinstance(p, (list, tuple)) and p and str(p[0]) in quitar)]
                aplicadas.append({"corte": cid, "eje": e, "quitados": sorted(quitar)})
        if mover_fuentes and "source_note" in c:
            c.pop("source_note"); aplicadas.append({"corte": cid, "campo": "source_note", "accion": "move_to_sidecar"})
        nuevos.append(c)
    out["cuts"] = nuevos
    sellado = {}
    if mover_fuentes:
        for k in CAMPOS_FUENTE:
            if k in out:
                sellado[k] = out.pop(k); aplicadas.append({"campo": k, "accion": "move_to_sidecar"})
        sellado["source_note_por_corte"] = {c.get("id"): c.get("source_note") for c in case.get("cuts") or [] if c.get("source_note")}
    informe = {"version": VERSION, "contrato": CONTRATO, "tipos_aplicados": sorted(tipos), "rechazar_post_z": rechazar_post_z,
               "quitar_autoetiquetas": quitar_autoetiquetas, "mover_fuentes": mover_fuentes,
               "aplicadas": aplicadas, "n_aplicadas": len(aplicadas), "reporte": rep, "sidecar_sellado": {"mapa_nombres": dict(ctx.mapa), **sellado}}
    return out, informe


# ------------------------------------------------------------------ compuerta en vivo (la llama el UNICO al entrar)
def traza_sin_nombres(fl: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for f in fl:
        g = {k: v for k, v in f.items() if k not in ("span",)}
        g["huella_span"] = huella(f["span"]) if f.get("span") else None
        out.append(g)
    return out


def compuerta(case: Mapping[str, Any], modo: str = "activo", catalogo: Optional[Mapping[str, Any]] = None) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """modo 'activo': aplica SOLO identidad/obra/calendario dentro del payload (neutralize/strip); el resto warn+traza.
    modo 'traza': no modifica. Devuelve (payload, traza_para_resultado) — la traza NO lleva nombres (huellas)."""
    modo = (modo or "activo").strip().lower()
    if modo == "traza":
        rep = analizar(case, catalogo)
        payload = dict(case); aplicadas = []
    else:
        payload, inf = aplicar(case, set(TIPOS_ACTIVOS_EN_VIVO), catalogo)
        rep = inf["reporte"]; aplicadas = inf["aplicadas"]
    fl = rep["banderas"]
    # A5_20261107: en modo traza no se ejecuta nada (solo se analiza): el status
    # no puede decir EXECUTED. Antes mentía igual que el recibo del Caldero.
    tr = {"version": VERSION, "contrato": CONTRATO, "modo": modo, "status": ("EXECUTED" if modo == "activo" else "TRAZA_SIN_MODIFICACION"),
          "activos_en_vivo": sorted(TIPOS_ACTIVOS_EN_VIVO) if modo == "activo" else [],
          "resumen": rep["resumen"], "n_aplicadas": len(aplicadas),
          "aplicadas": [{k: v for k, v in a.items() if k not in ("quitados",)} | ({"n_quitados": len(a["quitados"])} if "quitados" in a else {}) for a in aplicadas],
          "banderas": traza_sin_nombres(fl),
          "can_decide_H": False, "escribe_H": False, "reordena": False, "feeds_predictor": False, "llamadas_llm": 0,
          "nota": "solo huellas sha256[:8] de los spans; el mapa nombre->rol queda en la capa LLM (sidecar sellado), nunca en el motor"}
    return payload, tr


# ------------------------------------------------------------------ chequeo de SALIDA (LLM_SALIDA)
CAMPOS_INMUTABLES = ("H1", "H2", "margen", "grado", "n_objeciones")


def campos_inmutables(cf: Mapping[str, Any]) -> Dict[str, Any]:
    ap = cf.get("apuesta") or {}
    obj = [(o.get("guardian") or o.get("criterio") or "") + (":" + o["tipo"] if o.get("tipo") else "") for o in cf.get("objeciones") or []]
    return {"H1": cf.get("H1"), "H2": cf.get("H2"), "margen": cf.get("margen"), "grado": cf.get("grado"),
            "n_objeciones": cf.get("n_objeciones"), "objeciones": obj,
            "apuesta_familia": ap.get("familia_apostada"), "apuesta_frente_a": ap.get("frente_a")}


def huella_salida(cf: Mapping[str, Any]) -> str:
    return hashlib.sha256(json.dumps(campos_inmutables(cf), sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")).hexdigest()[:16]


def contrato_salida(cf: Mapping[str, Any]) -> Dict[str, Any]:
    return {"contrato": CONTRATO, "version": VERSION, "campos_inmutables": campos_inmutables(cf), "huella_salida_017": huella_salida(cf),
            "regla": "LLM_SALIDA traduce para el consultor; NO cambia H1/H2, ranking, margen, grado ni objeciones; no agrega afirmaciones; "
                     "re-adjunta nombres desde el mapa sellado de la capa LLM; debe declarar el grado y las objeciones; debe citar huella_salida_017",
            "verificador": "filtro_entrada_dirigida_017.verificar_salida_llm(texto, cierre_final, etiquetas)"}


GRADOS = ("FIRME", "AJUSTADA", "FRAGIL")


def verificar_salida_llm(texto: str, cf: Mapping[str, Any], etiquetas: Optional[Mapping[str, str]] = None,
                         catalogo: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    """Chequeo determinista del texto de LLM_SALIDA contra cierre_final. etiquetas: familia -> nombre legible usado en el texto."""
    t = str(texto or ""); tn = _n(t)
    et = dict(etiquetas or {})
    v: List[str] = []
    ci = campos_inmutables(cf)
    def menc(f):
        if not f: return False
        return (f in t) or (et.get(f) and _n(et[f]) in tn)
    for k in ("H1", "H2"):
        if not menc(ci[k]):
            v.append(f"{k}_NO_MENCIONADA:{ci[k]}")
    # orden: H1 debe aparecer antes que H2
    def pos(f):
        ps = [p for p in (t.find(f) if f else -1, tn.find(_n(et.get(f, ""))) if et.get(f) else -1) if p >= 0]
        return min(ps) if ps else -1
    if ci["H1"] and ci["H2"] and pos(ci["H1"]) >= 0 and pos(ci["H2"]) >= 0 and pos(ci["H1"]) > pos(ci["H2"]):
        v.append("ORDEN_H1_H2_INVERTIDO")
    for m in re.finditer(r"H([12])\s*[:=]\s*([A-Za-z0-9_]+)", t):
        esperado = ci["H" + m.group(1)]
        if m.group(2) != esperado and et.get(esperado, "").split()[:1] != [m.group(2)]:
            v.append(f"H{m.group(1)}_DISTINTA_EN_TEXTO:{m.group(2)}!={esperado}")
    gr = [g for g in GRADOS if re.search(r"\b" + g + r"\b", _sa(t).upper())]
    if ci["grado"] not in gr:
        v.append(f"GRADO_NO_DECLARADO:{ci['grado']}")
    otros = [g for g in gr if g != ci["grado"]]
    for g in otros:
        if re.search(r"(?i)grado\s*[:=]?\s*" + g, _sa(t)):
            v.append(f"GRADO_DISTINTO_AFIRMADO:{g}")
    for m in re.finditer(r"(?i)margen\D{0,20}?(-?\d+[\.,]\d+)", t):
        try:
            x = float(m.group(1).replace(",", "."))
            if ci["margen"] is not None and abs(x - float(ci["margen"])) > 0.0005 * max(1.0, abs(float(ci["margen"]))) + 5e-4:
                v.append(f"MARGEN_DISTINTO:{x}!={ci['margen']}")
        except Exception:
            pass
    if (ci["n_objeciones"] or 0) > 0 and not re.search(r"(?i)objeci", t):
        v.append("OBJECIONES_NO_DECLARADAS")
    if (ci["n_objeciones"] or 0) == 0 and re.search(r"(?i)\b(\d+)\s+objeciones?\b", t):
        n = int(re.search(r"(?i)\b(\d+)\s+objeciones?\b", t).group(1))
        if n != 0: v.append(f"OBJECIONES_INVENTADAS:{n}")
    cat = _cargar_catalogo(catalogo)
    if cat:
        extra = sorted({f for f in cat if f in t and f not in (ci["H1"], ci["H2"]) and re.search(r"(?i)(H1|H2|ganador|apuesta)\W{0,5}" + re.escape(f), t)})
        for f in extra:
            v.append(f"FAMILIA_AJENA_PRESENTADA_COMO_H:{f}")
    if re.search(r"\bNP\d+\b", t):
        v.append("PLACEHOLDER_SIN_TRADUCIR")
    hs = huella_salida(cf)
    cita = hs in t
    return {"ok": not v, "violaciones": v, "huella_salida_017": hs, "huella_citada": cita, "campos_inmutables": ci, "version": VERSION}


if __name__ == "__main__":  # uso CLI: python3 filtro_entrada_dirigida_017.py input.json  -> reporte
    import sys
    d = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    r = analizar(d)
    print(json.dumps({"resumen": r["resumen"], "banderas": r["banderas"]}, ensure_ascii=False, indent=1))
