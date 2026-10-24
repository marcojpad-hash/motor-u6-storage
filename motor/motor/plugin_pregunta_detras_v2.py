#!/usr/bin/env python3
"""PLUGIN_PREGUNTA_DETRAS v2.3.2 — lente semántica + calibrador morfosintáctico + tropos.

PROPUESTA. No cablear al limpio sin OK de Marco.
No toca Engine_V5 / F / p / 244. No inventa H. No activa tokens.

v1 = lista de frases (TRAMPAS).
v2 = función del lexema (campo vs etiqueta vs marco).
v2.2 = marco sintáctico reforzado (medible/objetivo vs adjetival) +
  clasificador/calibrador apoyado en:
  - marcos sintácticos de la oración
  - morfología (sustantivo de fenómeno vs adjetivo de perfil)
  - concordancia de género y número (lo que venden los correctores
    de estilo como “género y número” — nombre feo: análisis
    morfosintáctico / concordancia gramatical)
v2.2.2 = tilde fix: _rol_sintactico busca SIEMPRE en nq=_norm(q) (se mantiene).
v2.3.2 = sintaxis CORRIGE léxico: N+Adj atributivo ("hombre ambicioso")
  → MODIFICADOR_ATRIBUTIVO (trazable, NO cuenta a red_flag/perfil).
  Predicativo (era/fue ambicioso; era un N adj; su N fue adj) sí puede ir a ETIQUETA.
v2.3.0 = tropos estructurales en MARCO_EVALUATIVO:
  - lítotes (no + adj/adv que invierte a afirmación fuerte)
  - hipérbole (superlativo absoluto + exclusividad temporal)
  NO ironía/sarcasmo. Sinecdoque NO va aquí — ver
  plugin_pregunta_dirigida._SINONIMOS / registrar_sinecdoque (caso a caso).

Highlight only. Nunca bloquea.

Uso:
  from plugin_pregunta_detras_v2 import filtrar
  filtrar("¿Era ambicioso?")
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import asdict, dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

VERSION = "PROPUESTA_v2.3.3"  # 2.3.3 (27-sep): "esta/este/estos/estas" sin tilde tras preposición = demostrativo, no cópula
# (falso positivo 2.3.2: "en esta prueba", "en esta calibración" leídos como etiqueta del sujeto). Resto = 2.3.2 (f0b1a92b).
PLUGIN = "plugin_pregunta_detras_v2"
UMBRAL_ACUMULACION = 2
UMBRAL_SCORE_ETIQUETA = 0.55  # calibración: score ≥ esto cuenta como marcaje

ClasificarFn = Callable[[str], Any]


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", s.lower()).strip()


def _strip_punct(s: str) -> str:
    return re.sub(r"[¿?¡!;,:.\"“”‘’()\[\]]+", " ", s)


# ---------------------------------------------------------------------------
# Morfología ligera (no diccionario de conceptos: tipología de FORMA)
# ---------------------------------------------------------------------------

# Sustantivo abstracto típico de fenómeno/proceso
_RX_N_FENOMENO = re.compile(
    r"^[a-záéíóúñ]{2,}(cion|sion|dad|tad|ancia|encia|ismo|ura|aje|mento|miento)$",
    re.I,
)
# Adjetivo / gentilicio de perfil (forma)
_RX_ADJ_PERFIL = re.compile(
    r"^[a-záéíóúñ]{3,}(oso|osa|icos|icas|ico|ica|ivo|iva|able|ible|ista|ales|al)$",
    re.I,
)
# Participio / -ado -ido como etiqueta predicativa
_RX_PART = re.compile(r"^[a-záéíóúñ]{3,}(ado|ada|ados|adas|ido|ida|idos|idas)$", re.I)

_NO_LEXEMA = {
    "que", "quien", "como", "cuando", "donde", "cual", "este", "esta", "ese", "esa",
    "uno", "una", "muy", "mas", "tan", "solo", "bien", "mal", "asi",
    "todo", "toda", "poco", "mucho", "otro", "otra", "mismo", "misma",
    "era", "fue", "es", "sera", "ser", "estar", "estaba", "estuvo", "siendo",
    "su", "sus", "el", "la", "los", "las", "un", "de", "del", "al", "en", "con",
    "por", "para", "sin", "sobre", "hasta", "desde", "entre",
}


def _genero_numero(forma: str) -> Dict[str, str]:
    """Aproximación de género/número por terminación (concordancia)."""
    f = _norm(forma)
    if f.endswith(("as", "os")) and len(f) > 3:
        return {"genero": "f" if f.endswith("as") else "m", "numero": "pl", "forma": f}
    if f.endswith("a") and not f.endswith(("ista", "isma", "encia", "ancia", "ura", "dad", "tad")):
        # heurística: muchos adj -a = f sg; sustantivos -ción ya capturados aparte
        if _RX_ADJ_PERFIL.match(f) or _RX_PART.match(f):
            return {"genero": "f", "numero": "sg", "forma": f}
    if f.endswith("o") and (_RX_ADJ_PERFIL.match(f) or _RX_PART.match(f)):
        return {"genero": "m", "numero": "sg", "forma": f}
    if f.endswith(("es",)) and len(f) > 4:
        return {"genero": "?", "numero": "pl", "forma": f}
    return {"genero": "?", "numero": "sg", "forma": f}


def _clase_morfo(forma: str) -> str:
    f = _norm(forma)
    if _RX_ADJ_PERFIL.match(f) or _RX_PART.match(f):
        return "ADJ_PERFIL"
    if _RX_N_FENOMENO.match(f):
        return "N_FENOMENO"
    return "OTRO"


# ---------------------------------------------------------------------------
# Rol sintáctico: medible/objetivo vs adjetival/predicativo
# ---------------------------------------------------------------------------

def _rol_sintactico(pregunta: str, lexema: str, span_start: int = -1) -> Dict[str, Any]:
    """Clasifica el USO del lexema en la oración (no su significado de diccionario).

    Roles:
      OBJETO_MEDIBLE   — núcleo nominal medible (la X, su X, con X, papel de X)
      PREDICATIVO      — complemento de ser/estar / atributo del sujeto
      ADJETIVAL        — modifica a un nombre (oración/grupo adjetival)
      ADVERBIO_MARCO   — evaluativo de enunciación
      AMBIGUO
    """
    q = pregunta or ""
    nq = _norm(q)
    # BUGFIX v2.2.2: lex ya viene sin tilde; buscar SIEMPRE en nq (re.I no quita acentos)
    lex = _norm(lexema)
    # ventana local alrededor del lexema
    idx = nq.find(lex) if span_start < 0 else -1
    if idx < 0:
        # fallback: buscar lex ya normalizado (nunca q acentuada + lex sin tilde)
        m = re.search(re.escape(lex), nq, re.I)
        idx = nq[: m.start()].rfind(" ") if m else -1
        frag = nq
    else:
        frag = nq

    # predicativo PRIMERO: ser/estar + (art)? + lex  (gana sobre det+N)
    if re.search(
        rf"\b(?:es|era|fue|sera|siendo|parece|parecia|estar|estaba|esta|estuvo)\s+"
        rf"(?:(?:un|una|el|la)\s+)?{re.escape(lex)}\b",
        nq,
        re.I,
    ):
        return {
            "rol": "PREDICATIVO",
            "medible": False,
            "adjetival": True,
            "nota": "atributo/predicado del sujeto (uso adjetival o de etiqueta)",
        }

    # "era un hombre de X" / "es gente de Y" — predicativo de perfil, no objeto medible
    if re.search(
        rf"\b(?:es|era|fue)\s+(?:un|una)\s+{re.escape(lex)}\s+de\s+",
        nq,
        re.I,
    ):
        return {
            "rol": "PREDICATIVO",
            "medible": False,
            "adjetival": True,
            "nota": "era un N de X = etiqueta de perfil",
        }

    # patrones de objeto medible (determinante + N; prep + N; verbo de medición)
    # NO contar "un/una N" si viene tras ser/estar (ya cubierto arriba)
    medible_pats = [
        rf"\b(?:la|el|su|sus)\s+{re.escape(lex)}\b",  # sin un/una sueltos
        rf"\b(?:con|sobre|durante|ante|mediante)\s+(?:la|el|su)?\s*{re.escape(lex)}\b",
        rf"\b(?:papel|efecto|rol|peso|lugar|ventana|etapa)\s+(?:de|del|de\s+la|que\s+tuvo|que\s+tiene)\s+(?:la|el|su)?\s*{re.escape(lex)}\b",
        rf"\b{re.escape(lex)}\s+(?:aparece|surge|entra|ocurre|aumenta|baja|persiste)\b",
        rf"\b(?:analizar|medir|trazar|observar|situar|mapear)\s+(?:la|el|su)?\s*{re.escape(lex)}\b",
        rf"\bqu[eé]\s+(?:hizo|hace|papel)\b.*\b{re.escape(lex)}\b",
        # "la/el N en su trayectoria/ventana" = medible
        rf"\b(?:la|el|su)\s+{re.escape(lex)}\s+(?:en|durante)\s+(?:su|la|el)?\s*(?:trayectoria|etapa|ventana|periodo|oficio|campo)\b",
    ]
    for p in medible_pats:
        if re.search(p, nq, re.I):
            return {
                "rol": "OBJETO_MEDIBLE",
                "medible": True,
                "adjetival": False,
                "nota": "núcleo nominal / objeto de medición en el campo",
            }

    # por qué + ser + lex / por qué su lex
    if re.search(rf"\bpor\s+qu[eé]\s+(?:era|fue|es).{{0,20}}{re.escape(lex)}\b", nq, re.I):
        return {
            "rol": "PREDICATIVO",
            "medible": False,
            "adjetival": True,
            "nota": "por qué + predicado = perfilamiento",
        }
    if re.search(rf"\bpor\s+qu[eé]\s+(?:su|sus)\s+{re.escape(lex)}\b", nq, re.I):
        return {
            "rol": "PREDICATIVO",
            "medible": False,
            "adjetival": True,
            "nota": "posesivo explicativo del sujeto",
        }

    # grupo adjetival: N + lex (lex modifica al nombre)  p.ej. "hombre ambicioso"
    m_adj = re.search(rf"\b([a-záéíóúñ]{{3,}})\s+{re.escape(lex)}\b", nq, re.I)
    if m_adj and _clase_morfo(lex) == "ADJ_PERFIL":
        cabeza = _norm(m_adj.group(1))
        if cabeza not in {
            "era", "fue", "es", "sera", "seria", "parece", "parecia",
            "esta", "estaba", "estar", "ser", "siendo", "resulta", "resultaba",
        }:
            return {
                "rol": "ADJETIVAL",
                "medible": False,
                "adjetival": True,
                "nota": "modifica a un nombre (grupo adjetival)",
            }

    # oración de relativo adjetiva aproximada: "que era X" / "que fue un X"
    if re.search(rf"\bque\s+(?:era|fue|es|result[oó])\s+(?:un|una)?\s*{re.escape(lex)}\b", nq, re.I):
        return {
            "rol": "ADJETIVAL",
            "medible": False,
            "adjetival": True,
            "nota": "relativa/atributiva (uso adjetival de la cláusula)",
        }

    return {"rol": "AMBIGUO", "medible": False, "adjetival": False, "nota": "sin marco claro"}


def _aplicar_rol_a_hips(pregunta: str, hips: List[HipotesisLexema]) -> List[HipotesisLexema]:
    """Recalibra función/score con rol sintáctico medible vs adjetival."""
    out = []
    for h in hips:
        if h.lexema in (
            "marco_veredicto", "marco_mira", "confirmacion", "premisa_dada",
            "marco_litotes", "marco_hiperbole",
        ):
            h.apoyo = {**h.apoyo, "rol_sintactico": "ADVERBIO_MARCO", "medible": False}
            out.append(h)
            continue
        rol = _rol_sintactico(pregunta, h.lexema)
        h.apoyo = {**h.apoyo, **rol}
        if rol["rol"] == "OBJETO_MEDIBLE":
            # no pisar predicativos/adjetivales ya marcados por marco
            if h.funcion == "ETIQUETA_SUJETO" and (
                "predicado" in h.regla or "era_un" in h.regla or "adjetival" in h.regla or "por_que" in h.regla
            ):
                h.apoyo = {**h.apoyo, "rol_override": "predicado_gana_a_detN"}
            elif h.funcion == "ETIQUETA_SUJETO":
                h.funcion = "FENOMENO_CAMPO"
                h.score = max(0.75, min(0.95, h.score))
                h.regla = h.regla + "+rol_medible"
            else:
                h.funcion = "FENOMENO_CAMPO"
                h.score = max(h.score, 0.8)
        elif rol["rol"] in ("PREDICATIVO", "ADJETIVAL"):
            # Sintaxis ya clasificó N+Adj atributivo como MODIFICADOR: NO subir a ETIQUETA
            # (corrige el punto ciego: "hombre ambicioso" ≠ perfil forzado).
            if h.funcion == "MODIFICADOR_ATRIBUTIVO":
                h.apoyo = {**h.apoyo, "rol_override": "modificador_atributivo_se_mantiene"}
                out.append(h)
                continue
            if h.funcion == "FENOMENO_CAMPO":
                h.funcion = "ETIQUETA_SUJETO"
                h.regla = h.regla + "+rol_adjetival"
            h.funcion = "ETIQUETA_SUJETO" if h.funcion != "MARCO_EVALUATIVO" else h.funcion
            h.score = max(h.score, 0.78)
            if rol["rol"] == "ADJETIVAL":
                h.score = min(0.99, h.score + 0.05)
        out.append(h)
    return out


# ---------------------------------------------------------------------------
# Marcos sintácticos (estructura de la oración)
# ---------------------------------------------------------------------------

@dataclass
class HipotesisLexema:
    lexema: str
    funcion: str
    fragmento: str
    regla: str
    score: float
    apoyo: Dict[str, Any] = field(default_factory=dict)


_PREP_DEMOSTRATIVO = {"en", "de", "a", "con", "por", "para", "sobre", "desde", "hasta", "hacia", "entre", "sin", "tras", "ante", "bajo", "segun", "durante", "mediante", "y", "o"}


def _marcos_sintacticos(pregunta: str) -> List[HipotesisLexema]:
    q = pregunta or ""
    nq = _norm(q)
    out: List[HipotesisLexema] = []

    def add(lex, funcion, frag, regla, score, **apoyo):
        if _norm(lex) in _NO_LEXEMA or len(_norm(lex)) < 3:
            return
        out.append(
            HipotesisLexema(
                lexema=_norm(lex),
                funcion=funcion,
                fragmento=(frag or "")[:160],
                regla=regla,
                score=float(score),
                apoyo=apoyo,
            )
        )

    # Predicado: ser/estar + (un/una)? + X  → etiqueta si X es adj/perfil
    for m in re.finditer(
        r"\b((?:es|era|fue|sera|siendo|parece|parecia|resulta|resultaba|estaba|esta|estuvo))\s+"
        r"(?:(un|una|el|la)\s+)?([a-záéíóúñ]{3,})\b",
        q,
        re.I,
    ):
        cop, art, pred = m.group(1), m.group(2), m.group(3)
        # 2.3.3: "esta" sin tilde es demostrativo (la cópula lleva tilde: "está"). Si va después de una
        # preposición o determinante ("en esta prueba", "de esta calibración") no es predicado del sujeto.
        if cop.lower() == "esta":
            previa = re.findall(r"([a-záéíóúñ]+)\s*$", q[:m.start()], re.I)
            if previa and _norm(previa[-1]) in _PREP_DEMOSTRATIVO:
                continue
        clase = _clase_morfo(pred)
        gn = _genero_numero(pred)
        # concordancia artículo–predicado (género)
        conc = None
        if art:
            art_n = _norm(art)
            if art_n in ("un", "el") and gn["genero"] in ("m", "?"):
                conc = "ok_aprox" if gn["genero"] == "m" else "debil"
            elif art_n in ("una", "la") and gn["genero"] in ("f", "?"):
                conc = "ok_aprox" if gn["genero"] == "f" else "debil"
            else:
                conc = "choque" if gn["genero"] in ("m", "f") else "debil"
        score = 0.35
        funcion = "AMBIGUO"
        if clase == "ADJ_PERFIL" or art:
            funcion = "ETIQUETA_SUJETO"
            score = 0.82 if clase == "ADJ_PERFIL" else 0.72
            if conc == "ok_aprox":
                score += 0.08  # calibración por concordancia
            elif conc == "choque":
                score -= 0.05
        elif clase == "N_FENOMENO" and not art:
            # "era ambición" raro; si aparece sin art, ambiguo bajo
            funcion = "AMBIGUO"
            score = 0.4
        add(
            pred,
            funcion,
            m.group(0),
            "marco_predicado_ser",
            score,
            copula=_norm(cop),
            articulo=_norm(art) if art else None,
            clase_morfo=clase,
            concordancia=conc,
            genero_numero=gn,
        )

    # ¿Por qué era/es X?
    for m in re.finditer(
        r"\bpor\s+qu[eé]\s+(?:era|fue|es|result[oó])\s+(?:tan\s+)?(?:un|una)?\s*([a-záéíóúñ]{3,})\b",
        q,
        re.I,
    ):
        pred = m.group(1)
        clase = _clase_morfo(pred)
        score = 0.88 if clase == "ADJ_PERFIL" else 0.75
        add(
            pred,
            "ETIQUETA_SUJETO",
            m.group(0),
            "marco_por_que_era",
            score,
            clase_morfo=clase,
            genero_numero=_genero_numero(pred),
        )

    # ¿Por qué su N? → N como propiedad explicativa del sujeto
    for m in re.finditer(r"\bpor\s+qu[eé]\s+(?:su|sus)\s+([a-záéíóúñ]{3,})\b", q, re.I):
        lex = m.group(1)
        add(
            lex,
            "ETIQUETA_SUJETO",
            m.group(0),
            "marco_por_que_su_N",
            0.7,
            clase_morfo=_clase_morfo(lex),
            nota="posesivo+N como propiedad del sujeto",
        )

    # Coordinación de predicados: era A y B y un C
    for m in re.finditer(
        r"\b(?:es|era|fue)\s+(?:un|una)?\s*[a-záéíóúñ]{3,}"
        r"(?:\s*(?:y|,)\s*(?:un|una)?\s*[a-záéíóúñ]{3,})+",
        q,
        re.I,
    ):
        chunk = m.group(0)
        parts = re.findall(
            r"(?:^|(?:es|era|fue)\s+|(?:y|,)\s*)(?:un|una)?\s*([a-záéíóúñ]{3,})",
            chunk,
            flags=re.I,
        )
        for lex in parts:
            if _norm(lex) in _NO_LEXEMA:
                continue
            clase = _clase_morfo(lex)
            add(
                lex,
                "ETIQUETA_SUJETO",
                chunk,
                "marco_predicados_coordinados",
                0.8 if clase == "ADJ_PERFIL" else 0.68,
                clase_morfo=clase,
                acumulacion_local=True,
            )

    # Campo: qué papel / qué hizo con / aparece / durante etapa
    for m in re.finditer(
        r"\bqu[eé]\s+papel\s+(?:tuvo|tiene|jug[oó]|juega)\s+(?:la|el|su)?\s*([a-záéíóúñ]{3,})\b",
        q,
        re.I,
    ):
        lex = m.group(1)
        add(lex, "FENOMENO_CAMPO", m.group(0), "marco_que_papel", 0.85, clase_morfo=_clase_morfo(lex))

    for m in re.finditer(
        r"\bqu[eé]\s+(?:hizo|hace)\s+con\s+(?:su|la|el)?\s*([a-záéíóúñ]{3,})\b",
        q,
        re.I,
    ):
        lex = m.group(1)
        add(lex, "FENOMENO_CAMPO", m.group(0), "marco_que_hizo_con", 0.85, clase_morfo=_clase_morfo(lex))

    for m in re.finditer(
        r"\b(?:la|el|su|sus)?\s*([a-záéíóúñ]{3,})\s+(?:aparece|aparecio|surge|surgio|entra|entro)\b",
        q,
        re.I,
    ):
        lex = m.group(1)
        clase = _clase_morfo(lex)
        score = 0.9 if clase == "N_FENOMENO" else 0.7
        add(lex, "FENOMENO_CAMPO", m.group(0), "marco_aparece", score, clase_morfo=clase)

    for m in re.finditer(
        r"\b(?:la|el|su|sus)\s+([a-záéíóúñ]{3,})\s+(?:durante|en)\s+(?:su|la|el)\s+"
        r"(?:etapa|periodo|ventana|fase|corte)\b",
        q,
        re.I,
    ):
        lex = m.group(1)
        add(lex, "FENOMENO_CAMPO", m.group(0), "marco_N_durante_etapa", 0.88, clase_morfo=_clase_morfo(lex))

    for m in re.finditer(
        r"\b(?:analizar|medir|trazar|observar|situar)\s+(?:la|el|su)?\s*([a-záéíóúñ]{3,})\b",
        q,
        re.I,
    ):
        lex = m.group(1)
        add(lex, "FENOMENO_CAMPO", m.group(0), "marco_objeto_analisis", 0.8, clase_morfo=_clase_morfo(lex))

    # Marco evaluativo / veredicto (frases fijas — se mantienen)
    if re.search(r"\b(?:a\s+huevo|obviamente|claramente|sin\s+duda)\s+.*\b(?:era|fue|es)\b", q, re.I):
        add("marco_veredicto", "MARCO_EVALUATIVO", "a huevo/obviamente+era", "marco_veredicto_moral", 0.9)
    if re.search(r"\b(?:mira|fijate|fíjate|date\s+cuenta)\s+(?:qué|que)\b", q, re.I):
        add("marco_mira", "MARCO_EVALUATIVO", "mira qué…", "marco_evaluativo_mira", 0.75)
    if re.search(r"\b(?:confirm[ae]|dime\s+si|no\s+es\s+cierto\s+que)\s+(?:que\s+)?(?:era|fue|es)\b", q, re.I):
        add("confirmacion", "MARCO_EVALUATIVO", "confirma que era…", "marco_pedir_confirmacion", 0.8)
    if re.search(r"\b(?:sabemos|es\s+sabido|dado\s+que|puesto\s+que)\s+que\b", q, re.I):
        add("premisa_dada", "MARCO_EVALUATIVO", "sabemos/dado que…", "marco_premisa_consumada", 0.7)

    # Tropos estructurales → MARCO_EVALUATIVO (v2.3; NO ironía; sinecdoque ≠ aquí)
    # Lítotes: no + adj/adv que invierte a afirmación fuerte
    m_lit = re.search(
        r"\b(?:"
        r"no\s+poco|"
        r"no\s+fue\s+ajeno\s+a|"
        r"no\s+menor|"
        r"no\s+insignificante|"
        r"nada\s+desdenable|"
        r"nada\s+desde[nñ]able|"
        r"no\s+poca|"
        r"no\s+(?:es|era|fue|fueron|eran|son|esta|estaba|estuvo)\s+"
        r"(?:tan\s+)?(?:poco|poca|pocos|pocas|menor|menores|insignificante|insignificantes|ajeno|ajena)(?:\s+a)?"
        r")\b",
        nq,
        re.I,
    )
    if not m_lit:
        m_lit = re.search(
            r"\b(?:"
            r"no\s+poco|"
            r"no\s+fue\s+ajeno\s+a|"
            r"no\s+menor|"
            r"no\s+insignificante|"
            r"nada\s+desde[nñ]able|"
            r"no\s+poca|"
        r"no\s+(?:es|era|fue|fueron|eran|son|esta|estaba|estuvo)\s+"
        r"(?:tan\s+)?(?:poco|poca|pocos|pocas|menor|menores|insignificante|insignificantes|ajeno|ajena)(?:\s+a)?"
            r")\b",
            q,
            re.I,
        )
    if m_lit:
        add(
            "marco_litotes",
            "MARCO_EVALUATIVO",
            m_lit.group(0),
            "marco_litotes",
            0.82,
            tropo="litotes",
            nota="negación atenuada → afirmación fuerte (evaluativo)",
        )

    # Hipérbole: superlativo absoluto + exclusividad temporal
    m_hip = re.search(
        r"\b(?:"
        r"el\s+mas\s+\w+\s+de\s+la\s+historia|"
        r"la\s+mas\s+\w+\s+de\s+la\s+historia|"
        r"jamas\s+visto|"
        r"sin\s+precedentes|"
        r"nunca\s+antes|"
        r"el\s+(?:peor|mejor)\s+de\s+todos\s+los\s+tiempos|"
        r"la\s+(?:peor|mejor)\s+de\s+todos\s+los\s+tiempos"
        r")\b",
        nq,
        re.I,
    )
    if not m_hip:
        m_hip = re.search(
            r"\b(?:"
            r"el\s+m[aá]s\s+\w+\s+de\s+la\s+historia|"
            r"la\s+m[aá]s\s+\w+\s+de\s+la\s+historia|"
            r"jam[aá]s\s+visto|"
            r"sin\s+precedentes|"
            r"nunca\s+antes|"
            r"el\s+(?:peor|mejor)\s+de\s+todos\s+los\s+tiempos|"
            r"la\s+(?:peor|mejor)\s+de\s+todos\s+los\s+tiempos"
            r")\b",
            q,
            re.I,
        )
    if m_hip:
        add(
            "marco_hiperbole",
            "MARCO_EVALUATIVO",
            m_hip.group(0),
            "marco_hiperbole",
            0.85,
            tropo="hiperbole",
            nota="superlativo absoluto / exclusividad temporal (evaluativo)",
        )

    # Se le considera / lo llaman
    for m in re.finditer(
        r"\b(?:se\s+le\s+considera|lo\s+consideran|la\s+consideran|lo\s+llaman|la\s+llaman)\s+"
        r"(?:un|una|el|la)?\s*([a-záéíóúñ]{3,})\b",
        q,
        re.I,
    ):
        add(m.group(1), "ETIQUETA_SUJETO", m.group(0), "marco_se_le_considera", 0.85, clase_morfo=_clase_morfo(m.group(1)))

    # Grupo adjetival: (un/una)? N + Adj_perfil  — "hombre ambicioso", "empresa audaz"
    for m in re.finditer(
        r"\b(?:un|una|el|la)?\s*([a-záéíóúñ]{3,})\s+([a-záéíóúñ]{3,})\b",
        q,
        re.I,
    ):
        nhead, adj = m.group(1), m.group(2)
        if _norm(nhead) in _NO_LEXEMA or _norm(adj) in _NO_LEXEMA:
            continue
        # no tratar copula / cuantificadores como nucleo ("nada desdeñable" ≠ N+Adj de perfil)
        if _norm(nhead) in {
            "era", "fue", "es", "sera", "seria", "parece", "parecia",
            "esta", "estaba", "estar", "ser", "siendo", "resulta", "resultaba",
            "nada", "algo", "todo", "todos", "todas", "muy", "mas", "menos",
            "tan", "poco", "poca", "pocos", "pocas", "otro", "otra",
        }:
            continue
        if _clase_morfo(adj) != "ADJ_PERFIL":
            continue
        # no si es ser+adj (ya cubierto)
        if re.search(rf"\b(?:es|era|fue)\s+(?:un|una)?\s*{re.escape(adj)}\b", q, re.I):
            continue
        # no si ya es predicativo "era/fue un N Adj" (camino distinto; evita doble marca)
        if re.search(
            rf"\b(?:es|era|fue|seria|sera)\s+(?:un|una)\s+{re.escape(nhead)}\s+{re.escape(adj)}\b",
            q,
            re.I,
        ):
            continue
        # adj de marco temporal/espacial del campo ≠ perfil del sujeto
        # ("etapa empresarial", "periodo colonial", "ventana critica")
        _N_CAMPO = {
            "etapa", "periodo", "ventana", "fase", "corte", "trayectoria",
            "oficio", "campo", "contexto", "momento", "epoca", "ciclo",
            "empresa", "industria", "sector", "region", "zona",
        }
        if _norm(nhead) in _N_CAMPO:
            continue
        # Capa sintaxis corrige léxico (Marco): N+Adj atributivo NO es red flag
        # ni ETIQUETA de perfil por sí solo. Queda trazable como modificador.
        # Predicativos (era/fue + adj; era un N adj; su N fue adj) van por otras reglas.
        add(
            adj,
            "MODIFICADOR_ATRIBUTIVO",
            m.group(0),
            "marco_grupo_adjetival",
            0.55,
            clase_morfo="ADJ_PERFIL",
            nucleo_nombre=_norm(nhead),
            nota=(
                "Adj atributivo de N: trazable, NO perfil/red_flag por palabra. "
                "Capa sintaxis corrige alerta léxica."
            ),
        )

    # Predicativo: "su/la/el N fue/era Adj_perfil" — caracteriza N (camino distinto a N+Adj atributivo)
    for m in re.finditer(
        r"\b(?:su|la|el|una|un)\s+([a-záéíóúñ]{3,})\s+(?:fue|era|es|seria|sera)\s+([a-záéíóúñ]{3,})\b",
        q,
        re.I,
    ):
        nhead, adj = m.group(1), m.group(2)
        if _clase_morfo(adj) != "ADJ_PERFIL":
            continue
        add(
            adj,
            "ETIQUETA_SUJETO",
            m.group(0),
            "marco_su_N_fue_adj",
            0.83,
            clase_morfo="ADJ_PERFIL",
            nucleo_nombre=_norm(nhead),
            nota="predicado: su/el N fue Adj — caracteriza el N (≠ modificador atributivo suelto)",
        )

    # Predicativo: "era/fue/es un/una N Adj" — "era un hombre ambicioso"
    for m in re.finditer(
        r"\b(?:es|era|fue|seria|sera)\s+(?:un|una)\s+([a-záéíóúñ]{3,})\s+([a-záéíóúñ]{3,})\b",
        q,
        re.I,
    ):
        nhead, adj = m.group(1), m.group(2)
        if _clase_morfo(adj) != "ADJ_PERFIL":
            continue
        add(
            adj,
            "ETIQUETA_SUJETO",
            m.group(0),
            "marco_era_un_N_adj",
            0.86,
            clase_morfo="ADJ_PERFIL",
            nucleo_nombre=_norm(nhead),
            nota="predicado: era un N Adj — perfil del sujeto (≠ 'el N Adj' atributivo)",
        )

    # "era un N de X" → etiqueta sobre N o sobre el marco
    for m in re.finditer(
        r"\b(?:es|era|fue)\s+(?:un|una)\s+([a-záéíóúñ]{3,})\s+de\s+([a-záéíóúñ]{3,})\b",
        q,
        re.I,
    ):
        nhead, comp = m.group(1), m.group(2)
        add(
            nhead,
            "ETIQUETA_SUJETO",
            m.group(0),
            "marco_era_un_N_de",
            0.84,
            complemento=_norm(comp),
            nota="predicado de perfil (un N de X), no objeto medible",
        )

    # "la/el N en su trayectoria" sin verbo de aparecer — medible
    for m in re.finditer(
        r"\b(?:la|el|su)\s+([a-záéíóúñ]{3,})\s+(?:en|durante)\s+(?:su|la|el)?\s*"
        r"(?:trayectoria|etapa|ventana|periodo|oficio|campo)\b",
        q,
        re.I,
    ):
        lex = m.group(1)
        add(lex, "FENOMENO_CAMPO", m.group(0), "marco_N_en_trayectoria", 0.8, clase_morfo=_clase_morfo(lex))

    return out


def _calibrar(hips: List[HipotesisLexema]) -> List[HipotesisLexema]:
    """Fusiona hipótesis del mismo lexema+función y ajusta score por apoyos.

    Morfología por sufijos (-oso/-ción/…) es APROXIMACIÓN BARATA, no analizador
    real: no debe inflar score como certeza. El marco sintáctico manda.
    """
    bucket: Dict[Tuple[str, str], HipotesisLexema] = {}
    for h in hips:
        # si el score vino casi solo de clase_morfo sin rol sintáctico fuerte, cap
        apoyo = h.apoyo or {}
        rol = apoyo.get("rol")
        solo_morfo = (
            apoyo.get("clase_morfo") in ("ADJ_PERFIL", "N_FENOMENO", "OTRO")
            and rol in (None, "AMBIGUO")
            and "marco_predicado" not in h.regla
            and "marco_que_" not in h.regla
            and "marco_aparece" not in h.regla
            and "marco_N_" not in h.regla
            and "marco_por_que" not in h.regla
            and "marco_era_un" not in h.regla
            and "marco_grupo" not in h.regla
            and "marco_veredicto" not in h.regla
            and "marco_premisa" not in h.regla
            and "marco_litotes" not in h.regla
            and "marco_hiperbole" not in h.regla
        )
        if solo_morfo:
            h.score = min(h.score, 0.55)
            h.apoyo = {**apoyo, "morfo_sufijo": "APROX", "score_capped": True}
        elif apoyo.get("clase_morfo") and rol in ("PREDICATIVO", "ADJETIVAL", "OBJETO_MEDIBLE"):
            # sintaxis confirma: ok mantener score, pero etiquetar morfo como apoyo débil
            h.apoyo = {**apoyo, "morfo_sufijo": "APROX_apoyo", "sintaxis_manda": True}

        key = (h.lexema, h.funcion)
        if key not in bucket:
            bucket[key] = h
            continue
        prev = bucket[key]
        prev.score = min(0.99, max(prev.score, h.score) + 0.05)
        prev.apoyo = {**prev.apoyo, **h.apoyo, "marcos_multiples": True}
        if len(h.fragmento) > len(prev.fragmento):
            prev.fragmento = h.fragmento
            prev.regla = h.regla
    etiquetas = [h for h in bucket.values() if h.funcion == "ETIQUETA_SUJETO"]
    if len(etiquetas) >= 2:
        for h in etiquetas:
            h.score = min(0.99, h.score + 0.06)
            h.apoyo = {**h.apoyo, "acumulacion_etiquetas": len(etiquetas)}
    return list(bucket.values())


@dataclass
class Marcaje:
    lexema: str
    funcion: str
    fragmento: str
    regla: str
    highlight: bool
    score: float = 0.0
    apoyo: Dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _hips_a_marcajes(hips: List[HipotesisLexema]) -> List[Marcaje]:
    out = []
    for h in hips:
        if h.funcion == "AMBIGUO" and h.score < UMBRAL_SCORE_ETIQUETA:
            continue
        hl = h.funcion in ("ETIQUETA_SUJETO", "MARCO_EVALUATIVO") and h.score >= UMBRAL_SCORE_ETIQUETA
        # campo siempre se reporta si score ok
        if h.funcion == "FENOMENO_CAMPO" and h.score < 0.5:
            continue
        if h.funcion == "MODIFICADOR_ATRIBUTIVO":
            # trazabilidad sí; perfil/red_flag no (highlight=False)
            if h.score < 0.45:
                continue
            hl = False
        elif h.funcion in ("ETIQUETA_SUJETO", "MARCO_EVALUATIVO") and h.score < UMBRAL_SCORE_ETIQUETA:
            continue
        out.append(
            Marcaje(
                lexema=h.lexema,
                funcion=h.funcion,
                fragmento=h.fragmento,
                regla=h.regla,
                highlight=hl,
                score=round(h.score, 3),
                apoyo=h.apoyo,
            )
        )
    return out


def _protocolo() -> Dict[str, str]:
    return {
        "unidad": "función del lexema en la pregunta (no la palabra)",
        "apoyo": "marco sintáctico manda; concordancia g/n; morfología por sufijos=APROX (no certeza)",
        "FENOMENO_CAMPO": "objeto/acto/hecho situado → pasa normal",
        "ETIQUETA_SUJETO": "atributo/perfil del sujeto (predicativo/marco) → marcaje",
        "MODIFICADOR_ATRIBUTIVO": "N+Adj atributivo → trazable; NO cuenta a red_flag",
        "MARCO_EVALUATIVO": "enunciación de veredicto → marcaje",
        "calibracion": f"score≥{UMBRAL_SCORE_ETIQUETA} + acumulación≥{UMBRAL_ACUMULACION} → RED_FLAG",
        "efecto": "highlight only; no bloquea; no enciende tokens; no inventa H",
        "analogia": "sombrero blanco medible ≠ 'qué bonito el color'",
    }


def filtrar(
    pregunta: str,
    *,
    umbral: int = UMBRAL_ACUMULACION,
    umbral_score: float = UMBRAL_SCORE_ETIQUETA,
    clasificar_fn: Optional[ClasificarFn] = None,
) -> Dict[str, Any]:
    global UMBRAL_SCORE_ETIQUETA
    # umbral_score local
    saved = UMBRAL_SCORE_ETIQUETA
    UMBRAL_SCORE_ETIQUETA = umbral_score
    try:
        hips = _calibrar(_aplicar_rol_a_hips(pregunta, _marcos_sintacticos(pregunta)))
        if clasificar_fn is not None:
            try:
                hook = clasificar_fn(pregunta)
                items = hook if isinstance(hook, (list, tuple)) else [hook]
                for it in items:
                    if isinstance(it, dict):
                        fun = str(it.get("funcion") or "AMBIGUO")
                        hips.append(
                            HipotesisLexema(
                                lexema=_norm(str(it.get("lexema") or "(hook)")),
                                funcion=fun,
                                fragmento=str(it.get("fragmento") or "")[:160],
                                regla="clasificar_fn",
                                score=float(it.get("score") or 0.8),
                                apoyo={"fuente": "hook"},
                            )
                        )
                    elif isinstance(it, str):
                        hips.append(
                            HipotesisLexema(
                                lexema="(hook)",
                                funcion=it,
                                fragmento="",
                                regla="clasificar_fn",
                                score=0.8,
                                apoyo={"fuente": "hook"},
                            )
                        )
                hips = _calibrar(hips)
            except Exception:
                pass
        marcajes = _hips_a_marcajes(hips)
    finally:
        UMBRAL_SCORE_ETIQUETA = saved

    n_perf = sum(1 for m in marcajes if m.highlight)
    n_campo = sum(1 for m in marcajes if m.funcion == "FENOMENO_CAMPO")
    red_flag = n_perf >= umbral
    if red_flag:
        bandera = "RED_FLAG_POSIBLE_PERFILAMIENTO"
    elif n_perf >= 1:
        bandera = "MARCAJE_PERFILAMIENTO"
    else:
        bandera = None

    return {
        "plugin": PLUGIN,
        "version": VERSION,
        "superficie": pregunta,
        "marcajes": [m.as_dict() for m in marcajes],
        "n_perfilamiento": n_perf,
        "n_campo": n_campo,
        "red_flag": red_flag,
        "bandera": bandera,
        "accion": "continuar_con_highlight" if bandera else "continuar",
        "calibrador": {
            "nombre": "morfosintaxis_concordancia_genero_numero",
            "umbral_score": umbral_score,
            "umbral_acumulacion": umbral,
            "morfo_sufijos": "APROX_BARATA",
            "aviso": (
                "Terminaciones (-oso/-ico/-ción/…) NO son analizador morfológico. "
                "Falsos +/- posibles (médico N|Adj; sacrificio puede no matchear). "
                "Score≠certeza. Manda el marco sintáctico (medible vs predicativo/adjetival)."
            ),
        },
        "protocolo": _protocolo(),
        "pregunta_detras_sugerida": (
            "¿qué fuerza, en qué ventana, con qué evidencia medible — "
            "sin presuponer la etiqueta del sujeto?"
            if bandera
            else None
        ),
        "nota": (
            "Filtro capa 1 + calibrador semántico (concordancia / morfología / marcos). "
            "No perfila ni enciende tokens."
        ),
    }


def interrogar(pregunta_superficie: str, **kw) -> Dict[str, Any]:
    return filtrar(pregunta_superficie, **kw)


def _demo() -> None:
    casos = [
        ("La ambición aparece durante su etapa empresarial.", "campo"),
        ("¿Qué hizo con su ambición?", "campo"),
        ("¿Es un ambicioso?", "etiqueta"),
        ("¿Era ambicioso?", "etiqueta"),
        ("¿Qué papel tuvo la fama?", "campo"),
        ("¿Por qué era famoso?", "etiqueta"),
        ("¿Por qué su fama?", "etiqueta"),
        ("¿Era ambicioso y famoso y un genio?", "acum"),
        ("A huevo ese güey era un culero, ¿no?", "marco"),
        ("Che_Guevara_oficio_ideal_vs_fuerza", "id_limpio"),
        ("¿Era un revolucionario idealista o un hombre de fuerza?", "etiqueta"),
        ("Su papel no fue ajeno a la crisis; nada desdeñable.", "litotes"),
        ("Fue el más decisivo de la historia, jamás visto.", "hiperbole"),
    ]
    print(f"=== {PLUGIN} {VERSION} ===\n")
    for q, tag in casos:
        r = filtrar(q, umbral=2)
        print(f"[{tag}] bandera={r['bandera']} n_perf={r['n_perfilamiento']} n_campo={r['n_campo']}")
        print(f"  Q: {q}")
        for m in r["marcajes"]:
            print(
                f"    · {m['funcion']:18} «{m['lexema']}» "
                f"score={m['score']} ({m['regla']}) "
                f"apoyo={ {k:m['apoyo'][k] for k in list(m['apoyo'])[:4]} }"
            )
        print()


if __name__ == "__main__":
    _demo()
