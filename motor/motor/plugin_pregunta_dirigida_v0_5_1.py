#!/usr/bin/env python3
"""
plugin_pregunta_dirigida.py — PROPUESTA SIDECAR unificada (no cableado al limpio)

Capas (se complementan; no pelean):

1) FUGA_EN_CORPUS — tokens/hechos del corte solo tienen sentido con T+k.
2a) Señal estructural P∧O — premisa consumada + pedido de onset (barata, local).
2b) Cotejo contra sellado_post_Z — el *objeto* que la pregunta da por sentado
    vs lo sellado del caso (con sinónimos). Generaliza sin lexicón global de tragedia.
2c) Soft "final genérico" — alude al cierre sin nombrar el sellado concreto.

Extractor de objeto:
- Heurístico local (default) — no atasca el tubo.
- Opcional LLM: pasa `extraer_objeto_fn(pregunta) -> str|list[str]` si hay modelo.
  Si falla/ausente, cae al heurístico. Nunca bloquea la corrida 5x3 por eso.

Candados:
- NO toca Engine_V5 / 244.
- NO inventa H1/H2/H3.
- Bandera = intencionalidad/sesgo de la *pregunta*, distinto del sesgo de tokens.
- Soft no lanza excepción; hard tampoco para el tubo limpio por defecto
  (raise_on_hard=False). El investigador decide reformular + comparar_boards.

Estado: PROPUESTA_0.4.1 / PENDIENTE de autorización al ON del limpio.
0.5.1_GUARDIANES (2026-09-27): falacias estructurales (AF/AD por forma condicional con
    átomos por raíz, no solo frase escolar), CS "cada vez que", PQ pregunta compleja y circular,
    post hoc biográfico (después de/tras/desde que + causal). Base 0.5.0 sha 19f59a1d intacta abajo.
0.5.0_SANDBOX: +detectar_falacias (AF/AD/CS/BC1/BC2/PQ/EQ) vecinos de post_hoc.
0.4.1: post_hoc respeta polaridad (no dispara si la causalidad está NEGADA).
0.4.2-cierre: doble negación/litote NO es negación simple (plugin_polaridad_causal); solo marca; H intacto.
0.4.0: +detectar_post_hoc (POST_HOC_TEMPORAL); hook sinecdoque en _SINONIMOS.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import asdict, dataclass, field
from typing import Any, Callable, Dict, List, Optional, Sequence, Set, Tuple, Union

VERSION = "PROPUESTA_0.5.1_GUARDIANES"
PLUGIN = "plugin_pregunta_dirigida"

# Tipo: LLM u otro extractor. Devuelve 1+ objetos nominalizados.
ExtraerObjetoFn = Callable[[str], Union[str, Sequence[str]]]


class PreguntaDirigidaError(RuntimeError):
    """Bandera dura opcional. No cierra H. No debe usarse para atascar el limpio."""


# ---------------------------------------------------------------------------
# Utils
# ---------------------------------------------------------------------------

def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", s.lower()).strip()


def _frag(q: str, *spans) -> str:
    parts = []
    for m in spans:
        if m:
            parts.append(m.group(0))
    return " | ".join(parts) if parts else (q or "")[:120]


# ---------------------------------------------------------------------------
# Sinónimos / expansión para cotejo con sellado_post_Z
# ---------------------------------------------------------------------------
# Clave canónica -> variantes. El sellado del caso aporta las claves reales;
# esto solo ayuda a matchear redacción distinta al mismo hecho sellado.

_SINONIMOS: Dict[str, Set[str]] = {
    "suicidio": {
        "suicidio", "suicidios", "suicidarse", "suicido", "se suicido", "se suicido",
        "propia mano", "por su propia mano", "quitarse la vida", "se quito la vida",
        "se iba a suicidar", "termino suicidandose", "suicidandose", "autolisis",
    },
    "muerte": {"muerte", "morir", "murio", "fallecio", "deceso"},
    "fama global": {"fama global", "fama", "celebridad", "exito masivo", "estrellato"},
    "nevermind": {"nevermind", "smells like teen spirit", "breakthrough album"},
    "in utero": {"in utero"},
    "crucifixion": {
        "crucifixion", "crucificado", "cruz", "morir en la cruz", "muerte en cruz",
        "calvario", "golgota",
    },
    "asesinato": {"asesinato", "asesinado", "lo mataron", "conjura", "conspiracion"},
    "tirania": {"tirania", "tirano", "despotismo"},
}

# ---------------------------------------------------------------------------
# Sinecdoque / metonimia (caso a caso) — NO auto-detect genérico
# ---------------------------------------------------------------------------
# Part-for-whole maps are CASE-SPECIFIC. Register here when a dossier names
# a part that stands for a sealed whole (e.g. "la pistola" → suicidio_1994).
# Do NOT invent generic synecdoche detection; empty until investigator fills.
#
# plugin_pregunta_detras_v2: synecdoche is NOT MARCO_EVALUATIVO — see this hook.

def registrar_sinecdoque(canon: str, variantes: Sequence[str]) -> None:
    """Hook vacío/utilitario: suma variantes a _SINONIMOS[canon] (crea clave si hace falta).

    Solo para mapas parte→todo del caso. No es detector automático.
    """
    key = _norm(canon) if canon else ""
    if not key:
        return
    bucket = _SINONIMOS.setdefault(key, set())
    bucket.add(key)
    for v in variantes or []:
        nv = _norm(str(v))
        if nv:
            bucket.add(nv)


# tokens genéricos de "el final" sin objeto concreto -> soft
_FINAL_GENERICO = re.compile(
    r"\b(desenlace|el final|lo que (paso|sucedio) al final|cierre (del|de la) (arco|historia)|"
    r"era inevitable|tenía que pasar|tenia que pasar|espiral)\b",
    re.I,
)


def _expand_sellado(sellado: Sequence[str]) -> List[Tuple[str, Set[str]]]:
    """[(etiqueta_sellado, set_norm_variantes), ...]"""
    out = []
    for item in sellado or []:
        raw = str(item)
        n = _norm(raw)
        variants = {n}
        # años / números sueltos
        for m in re.findall(r"\d{4}", n):
            variants.add(m)
        # palabras > 3
        for w in re.findall(r"[a-z0-9]{4,}", n):
            variants.add(w)
        # si alguna clave de sinonimos aparece en el sellado, suma el grupo
        for canon, group in _SINONIMOS.items():
            if canon in n or any(g in n for g in group):
                variants |= {_norm(x) for x in group}
                variants.add(canon)
        out.append((raw, variants))
    return out


# ---------------------------------------------------------------------------
# Extracción de objeto (heurístico + hook LLM)
# ---------------------------------------------------------------------------

_RX_OBJETO_HEUR = [
    re.compile(
        r"se\s+iba\s+a\s+(suicid\w+|morir|matar(?:se)?)",
        re.I,
    ),
    re.compile(
        r"termin[oó]\s+(suicid\w*éndose|suicid\w*endose|\w+)",
        re.I,
    ),
    re.compile(
        r"mur[ií][oó]\s+por\s+su\s+propia\s+mano|por\s+su\s+propia\s+mano",
        re.I,
    ),
    re.compile(
        r"\b(suicid\w*|overdose|sobredosis|asesinat\w*)\b",
        re.I,
    ),
    re.compile(
        r"desenlace\s+(?:era|fue|es)\s+inevitable|el\s+desenlace\s+era\s+inevitable",
        re.I,
    ),
]


def extraer_objetos_heuristico(pregunta: str) -> List[str]:
    """Barato. No es NER; suficiente para demos + sellado tipico."""
    if not pregunta:
        return []
    found: List[str] = []
    for rx in _RX_OBJETO_HEUR:
        m = rx.search(pregunta)
        if not m:
            continue
        g = m.group(0)
        ng = _norm(g)
        if "suicid" in ng or "propia mano" in ng or "quitar" in ng:
            found.append("suicidio")
        elif "cruz" in ng or "crucif" in ng:
            found.append("crucifixion")
        elif "inevitable" in ng or ("desenlace" in ng and "inevitable" in _norm(pregunta)):
            found.append("desenlace_generico")
        elif "morir" in ng or "murio" in ng or "muerte" in ng:
            found.append("muerte")  # NO mapear ciego a suicidio del sujeto
        else:
            found.append(ng)
    nq = _norm(pregunta)
    if ("crucifix" in nq or "crucific" in nq or "en la cruz" in nq or re.search(r"\bcruz\b", nq)):
        if "crucifixion" not in found:
            found.append("crucifixion")
    # Terceros frecuentes en bios (padre/madre/hermano...) — no son el sellado del sujeto
    terceros = bool(re.search(
        r"\b(padre|madre|mama|papa|hermano|hermana|hijo|hija|esposa|esposo|"
        r"amigo|amiga|tio|tia|abuelo|abuela|biologico|biologica|"
        r"emilia|edmund|de\s+su\s+padre|de\s+su\s+madre)\b",
        nq,
    ))
    sujeto_ref = bool(re.search(
        r"\b(el\s+sujeto|el\s+biografiado|protagonista|el\s+mismo|"
        r"se\s+suicid|su\s+propia\s+mano|se\s+iba\s+a\s+suicid|"
        r"termino\s+suicid)\b",
        nq,
    ))
    # solo si muerte + (propia mano / suicidio / sujeto) y NO terceros → ligar a suicidio
    if (
        ("muerte" in found or re.search(r"\b(muerte|murio|morir)\b", nq))
        and not terceros
        and (sujeto_ref or re.search(r"propia\s+mano|suicid", nq))
    ):
        if "suicidio" not in found:
            found.append("suicidio")
    # años (cualquier era, no solo 19xx)
    for y in re.findall(r"\b((?:1[0-9]|20)\d{2})\b", pregunta):
        found.append(y)
    # años bajos tipo "año 30" / "el 33" opcionales vía digitos 2-digit near muerte? skip
    seen = set()
    out = []
    for x in found:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def extraer_objetos(
    pregunta: str,
    extraer_objeto_fn: Optional[ExtraerObjetoFn] = None,
) -> Dict[str, Any]:
    """Unifica heurístico + LLM opcional. Nunca lanza por fallo del LLM."""
    heur = extraer_objetos_heuristico(pregunta)
    llm_objs: List[str] = []
    llm_error = None
    if extraer_objeto_fn is not None:
        try:
            raw = extraer_objeto_fn(pregunta)
            if isinstance(raw, str):
                llm_objs = [raw] if raw.strip() else []
            else:
                llm_objs = [str(x) for x in (raw or []) if str(x).strip()]
        except Exception as e:  # noqa: BLE001 — no atascar
            llm_error = f"{type(e).__name__}: {e}"
    # merge: LLM primero (más semántico), luego heur
    merged: List[str] = []
    seen = set()
    for x in llm_objs + heur:
        k = _norm(x)
        if k and k not in seen:
            seen.add(k)
            merged.append(x)
    return {
        "objetos": merged,
        "fuente_heuristico": heur,
        "fuente_llm": llm_objs,
        "llm_usado": extraer_objeto_fn is not None,
        "llm_error": llm_error,
    }


def cotejar_contra_sellado(
    objetos: Sequence[str],
    sellado_post_Z: Sequence[str],
) -> Dict[str, Any]:
    """Match objeto nominalizado vs sellado del caso (con sinónimos)."""
    expanded = _expand_sellado(sellado_post_Z)
    matches = []
    for obj in objetos:
        if obj == "desenlace_generico":
            continue  # eso es soft aparte
        on = _norm(obj)
        # expand objeto via sinonimos
        ovars = {on}
        for canon, group in _SINONIMOS.items():
            if on == canon or on in {_norm(g) for g in group}:
                ovars |= {_norm(x) for x in group}
                ovars.add(canon)
        for etiqueta, variants in expanded:
            if ovars & variants:
                matches.append({"objeto": obj, "sellado": etiqueta})
                break
            # substring soft: objeto dentro de sellado o viceversa
            if any(len(v) >= 4 and (v in _norm(etiqueta) or _norm(etiqueta) in v) for v in ovars):
                matches.append({"objeto": obj, "sellado": etiqueta, "via": "substring"})
                break
    return {
        "sellado_post_Z": list(sellado_post_Z or []),
        "matches": matches,
        "hay_match": bool(matches),
    }


# ---------------------------------------------------------------------------
# Señal estructural P∧O (capa 2a, de 0.2)
# ---------------------------------------------------------------------------

_RX_PREMISA = re.compile(
    r"(?:"
    r"sabemos\s+que|dado\s+que|puesto\s+que|"
    r"como\s+(?:ya\s+)?(?:sabemos|termin|mur|suicid)|"
    r"termin[oó]\s+\w*i[eé]ndose|termin[oó]\s+suicid|se\s+suicid\w*|"
    r"mur[ií][oó]\s+por\s+su\s+propia\s+mano|mur[ií][oó]\s+en\s+\d{4}|"
    r"el\s+desenlace\s+(?:era|fue|es)\s+inevitable|"
    r"era\s+inevitable|ten[ií]a\s+que\s+pasar|"
    r"se\s+iba\s+a\s+(?:suicid|morir|matar)|"
    r"por\s+su\s+propia\s+mano|propia\s+mano"
    r")",
    re.I,
)

_RX_ONSET = re.compile(
    r"(?:"
    r"a\s+partir\s+de\s+cu[aá]ndo|desde\s+cu[aá]ndo|"
    r"en\s+qu[eé]\s+corte|en\s+qu[eé]\s+momento|qu[eé]\s+corte|"
    r"d[oó]nde\s+arranca|d[oó]nde\s+empieza|cu[aá]ndo\s+arranca|"
    r"inicio\s+de\s+(?:esa|la)\s+\w+|primer\s+indicio|"
    r"cu[aá]ndo\s+se\s+(?:ve[ií]a|notaba|perfilaba)|"
    r"marca\s+el\s+inicio|arranca\s+el\s+patr[oó]n|"
    r"cu[aá]l\s+fue\s+el\s+primer"
    r")",
    re.I,
)

_RX_DESENLACE = re.compile(
    r"(?:"
    r"suicid\w*|matar(?:se)?|morir|muerte|asesinat\w*|overdose|sobredosis|"
    r"desenlace|espiral|patr[oó]n\s+final|final\s+tr[aá]gico|"
    r"inevitable|propia\s+mano|se\s+iba\s+a\s+\w+"
    r")",
    re.I,
)

_RX_COMPLEJA_CLASICA = re.compile(
    r"(?:a\s+partir\s+de\s+cu[aá]ndo|desde\s+cu[aá]ndo|cu[aá]ndo\s+se\s+ve[ií]a)"
    r".{0,120}?"
    r"(?:se\s+iba\s+a|que\s+\w+\s+(?:se\s+)?(?:suicid|morir|matar)|morir\s+en\s+la\s+cruz|crucific\w*|desenlace|inevitable)",
    re.I | re.S,
)


@dataclass
class HallazgoPregunta:
    tipo: str
    POSIBLE_PREGUNTA_DIRIGIDA: bool
    fragmento: str
    patron: str
    recomendacion: str
    severidad: str = "hard"  # hard | soft
    pregunta_original: str = ""
    corte_id: Optional[str] = None
    estructura: Optional[Dict[str, Any]] = None
    intencionalidad: str = (
        "sesgo_de_pregunta / premisa dada por sentada — distinto de sesgo de tokens del corpus"
    )


@dataclass
class ResultadoGuardiaPregunta:
    plugin: str = PLUGIN
    version: str = VERSION
    ok: bool = True
    hallazgos: List[Dict[str, Any]] = field(default_factory=list)
    pregunta_neutral_sugerida: Optional[str] = None
    accion_obligatoria: Optional[str] = None
    atencion_intencionalidad: Optional[str] = None
    H1: None = None
    H2: None = None
    H3: None = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def detectar_estructura_PO(pregunta: str) -> List[HallazgoPregunta]:
    """Capa 2a: P∧O estructural (no lista de frases fijas de muerte)."""
    if not pregunta or not pregunta.strip():
        return []
    q = pregunta.strip()
    premisa = _RX_PREMISA.search(q)
    onset = _RX_ONSET.search(q)
    desenlace = _RX_DESENLACE.search(q)
    compleja = _RX_COMPLEJA_CLASICA.search(q)
    razones = []
    if premisa and onset:
        razones.append("P∧O")
    if compleja:
        razones.append("compleja_clasica")
    if onset and desenlace and re.search(
        r"\b(inevitable|desenlace|espiral|propia\s+mano|suicid|mur)", q, re.I
    ):
        if "P∧O" not in razones:
            razones.append("desenlace_dado+onset")
    if not razones:
        return []
    return [
        HallazgoPregunta(
            tipo="FUGA_EN_PREGUNTA",
            POSIBLE_PREGUNTA_DIRIGIDA=True,
            severidad="hard",
            fragmento=_frag(q, premisa, onset, desenlace, compleja),
            patron="estructural_2a: P∧O | compleja | desenlace+onset",
            recomendacion=(
                "Reformular neutral; re-correr misma foto; comparar_boards. No inventar H2."
            ),
            pregunta_original=q,
            estructura={
                "capa": "2a_PO",
                "premisa": bool(premisa),
                "onset": bool(onset),
                "razones": razones,
            },
        )
    ]


def detectar_contra_sellado(
    pregunta: str,
    sellado_post_Z: Sequence[str],
    *,
    extraer_objeto_fn: Optional[ExtraerObjetoFn] = None,
) -> List[HallazgoPregunta]:
    """Capa 2b hard (match sellado) + 2c soft (final genérico)."""
    if not pregunta or not pregunta.strip():
        return []
    q = pregunta.strip()
    out: List[HallazgoPregunta] = []
    ext = extraer_objetos(q, extraer_objeto_fn=extraer_objeto_fn)
    cot = cotejar_contra_sellado(ext["objetos"], sellado_post_Z)

    if cot["hay_match"]:
        out.append(
            HallazgoPregunta(
                tipo="FUGA_EN_PREGUNTA",
                POSIBLE_PREGUNTA_DIRIGIDA=True,
                severidad="hard",
                fragmento=str(cot["matches"]),
                patron="capa_2b: objeto_nominalizado ∩ sellado_post_Z",
                recomendacion=(
                    "La pregunta nombra un hecho de sellado_post_Z. "
                    "Reformular sin ese hecho; re-correr; comparar_boards."
                ),
                pregunta_original=q,
                estructura={
                    "capa": "2b_sellado",
                    "extraccion": ext,
                    "cotejo": cot,
                },
            )
        )

    # soft: final genérico sin match concreto a sellado
    if _FINAL_GENERICO.search(q) and not cot["hay_match"]:
        out.append(
            HallazgoPregunta(
                tipo="FUGA_EN_PREGUNTA",
                POSIBLE_PREGUNTA_DIRIGIDA=True,
                severidad="soft",
                fragmento=_FINAL_GENERICO.search(q).group(0),
                patron="capa_2c: final_generico_sin_objeto_sellado",
                recomendacion=(
                    "Señal suave: alude al cierre sin nombrar el sellado. Revisar; "
                    "no bloquear el tubo. Preferible reformular."
                ),
                pregunta_original=q,
                estructura={"capa": "2c_soft_final", "extraccion": ext},
            )
        )
    # soft: extrajo desenlace_generico
    if "desenlace_generico" in ext["objetos"] and not cot["hay_match"]:
        if not any(h.severidad == "soft" for h in out):
            out.append(
                HallazgoPregunta(
                    tipo="FUGA_EN_PREGUNTA",
                    POSIBLE_PREGUNTA_DIRIGIDA=True,
                    severidad="soft",
                    fragmento="desenlace_generico",
                    patron="capa_2c: objeto=desenlace_generico",
                    recomendacion="Señal suave — revisar intencionalidad; no atascar.",
                    pregunta_original=q,
                    estructura={"capa": "2c_soft_obj", "extraccion": ext},
                )
            )
    return out



# ---------------------------------------------------------------------------
# Post-hoc temporal → causal (capa POST_HOC)
# ---------------------------------------------------------------------------
# Detecta lectura causal *después* del orden temporal. Highlight only.
# Geometría (κ/dX/persist) es diagnóstica: si aparece como SUJETO de claim
# causal, siempre bandera (no es causa; es lectura del campo).

_RX_TEMPORAL_PH = re.compile(
    r"(?:"
    r"antes\s+de|"
    r"ya\s+en\s+c\d+|"
    r"desde\s+el\s+corte|"
    r"en\s+c\d+|"
    r"tras\s+el\s+corte|"
    r"despu[eé]s\s+de\s+c|"
    r"primero\b.{0,60}?\bluego\b|"
    r"pas[oó]\s+antes|"
    r"antes\b|"
    r"cay[oó]\s+en\s+c\d+|"
    r"en\s+c\d+"
    r")",
    re.I | re.S,
)

_RX_CAUSAL_PH = re.compile(
    r"(?:"
    r"por\s+eso|"
    r"\bentonces\b|"  # conclusión causal (contexto post-hoc)
    r"esto\s+explica|"
    r"esto\s+predijo|"
    r"esto\s+demuestra|"
    r"ya\s+(?:sab[ií]amos|sabiamos)|"
    r"por\s+lo\s+tanto|"
    r"as[ií]\s+que|"
    r"predec[ií]a|"
    r"predijo|"
    r"caus[oó]|"
    r"provoc[oó]"
    r")",
    re.I,
)

# κ/kappa/persist/dX como sujeto de claim causal (geometría ≠ causa)
_RX_GEOM_CAUSAL = re.compile(
    r"(?:"
    r"(?:(?:la|el)\s+)?"
    r"(?:ca[ií]da|bajada|salto|subida|pico|valor|caida)\s+(?:de\s+)?"
    r"(?:κ|kappa|persist|dx_norm|dx)\b|"
    r"\b(?:κ|kappa|persist|dx_norm|dx)\s+"
    r"(?:cay[oó]|subi[oó]|salt[oó]|baj[oó]|persist(?:i[oó]|e)?|ca[ií]da)"
    r")"
    r".{0,100}?"
    r"(?:"
    r"caus[oó]|provoc[oó]|predec[ií]a|predijo|por\s+eso|"
    r"explica|demuestra|ya\s+sab[ií]amos|por\s+lo\s+tanto|as[ií]\s+que"
    r")",
    re.I | re.S,
)

_RX_OUTCOME_POSTHOC = re.compile(
    r"\b(desenlace|ruptura|suicid\w*|muerte|asesinat\w*|crucifix\w*|sobredosis|overdose)\b",
    re.I,
)

# Pregunta legítima de campo: no es claim causal post-hoc
_RX_PREGUNTA_CAMPO_OK = re.compile(
    r"(?:"
    r"qu[eé]\s+papel\s+(?:tuvo|tiene|jug[oó])|"
    r"qu[eé]\s+(?:hizo|hace|ocurri[oó]|pas[oó])\s+(?:con|en)|"
    r"c[oó]mo\s+(?:evolucion|se\s+movi[oó]|aparec)|"
    r"analizar|medir|observar|trazar"
    r")",
    re.I,
)


def _oraciones_adyacentes(texto: str) -> List[str]:
    """Partición barata en oraciones (., ?, !, ;, saltos)."""
    parts = re.split(r"(?<=[.?!;])\s+|\n+", texto or "")
    return [p.strip() for p in parts if p and p.strip()]


def _ventana_pares(oraciones: Sequence[str]) -> List[str]:
    """Oración sola + pares adyacentes (misma ventana temporal-causal)."""
    out: List[str] = []
    for i, o in enumerate(oraciones):
        out.append(o)
        if i + 1 < len(oraciones):
            out.append(o + " " + oraciones[i + 1])
    return out


def _causalidad_negada(texto: str) -> bool:
    """True si el claim causal está NEGADO de forma SIMPLE.

    Doble negación / litote («no es que no…») NO cuenta como negación simple.
    Delegado a plugin_polaridad_causal (cierre T5 · 2026-09-20).
    Solo marca; no mueve H1/H2.
    """
    try:
        from plugin_polaridad_causal import causalidad_negada_simple
        return causalidad_negada_simple(texto)
    except Exception:
        # fallback mínimo si el módulo no está en path
        if not texto:
            return False
        n = _norm(texto)
        if re.search(r"\bno\s+es\s+que\s+no\b", n, re.I):
            return False
        if re.search(
            r"(?:^|\b)(?:pero\s+)?(?:eso|esto|aquello|lo\s+anterior)?\s*"
            r"(?:no|nunca|tampoco)\s+"
            r"(?:explica|explican|explicaba|explico|"
            r"predijo|predecia|predecía|predice|"
            r"demuestra|demostró|demostro|"
            r"causo|causó|causa|"
            r"provoco|provocó|provoca|"
            r"por\s+eso)",
            n,
            re.I,
        ):
            return True
        if re.search(r"\bno\s+(?:es\s+que\s+)?(?:por\s+eso|entonces)\b", n):
            return True
        if re.search(r"\bsin\s+que\s+(?:eso|esto)?\s*(?:explique|cause|demuestre|prediga)", n):
            return True
        return False





def detectar_post_hoc(
    texto: str,
    sellado_post_Z: Optional[Sequence[str]] = None,
) -> List[HallazgoPregunta]:
    """Detecta lectura causal post-hoc del orden temporal.

    Estructura (no lista fija de frases):
      1) cue temporal cerca de cue causal/certeza (misma oración o adyacentes)
      2) κ/kappa/persist/dX como SUJETO de claim causal → siempre bandera

    Severidad:
      hard — nombra outcome sellado (sellado_post_Z / _SINONIMOS) o
             desenlace/ruptura claramente como lo "causado/predicho"
      soft — estructura temporal-causal sin nombrar sellado

    Acción: bandera, no bloquea. Reformular como observación (quitar
    por eso / esto predijo; dejar solo la secuencia descrita).
    """
    if not texto or not str(texto).strip():
        return []
    q = str(texto).strip()
    nq = _norm(q)

    # Pregunta de campo legítima sin claim causal → no fire
    if _RX_PREGUNTA_CAMPO_OK.search(q) and not _RX_CAUSAL_PH.search(q):
        # "¿Qué papel tuvo la caída de kappa en C6?" — FENOMENO_CAMPO
        if not re.search(r"por\s+eso|caus[oó]|predec|predijo|provoc[oó]|explica|demuestra", nq):
            return []

    hallazgos: List[HallazgoPregunta] = []
    fired_geom = False
    fired_struct = False
    frag_parts: List[str] = []
    razones: List[str] = []

    # Polaridad: si TODO el texto niega la causalidad, no hay post-hoc afirmado
    # (sigue pudiendo haber ventanas afirmativas en textos mixtos — se filtra abajo)

    # (2) geometría como sujeto causal — solo si la causalidad NO está negada
    m_geom = _RX_GEOM_CAUSAL.search(q) or _RX_GEOM_CAUSAL.search(nq)
    if m_geom and not _causalidad_negada(m_geom.group(0)) and not _causalidad_negada(q):
        # si el match geom incluye el verbo pero el texto niega ese verbo → no fire
        fired_geom = True
        frag_parts.append(m_geom.group(0)[:120])
        razones.append("geom_sujeto_causal")
    elif m_geom and (_causalidad_negada(m_geom.group(0)) or _causalidad_negada(q)):
        # hallazgo geométrico anulado por polaridad negativa
        razones.append("geom_causal_NEGADA_skip")

    # (1) temporal ∩ causal en misma oración o adyacentes
    for ventana in _ventana_pares(_oraciones_adyacentes(q)):
        nv = _norm(ventana)
        if _causalidad_negada(ventana):
            continue  # rechaza la causalidad → no es post-hoc afirmado
        mt = _RX_TEMPORAL_PH.search(ventana) or _RX_TEMPORAL_PH.search(nv)
        mc = _RX_CAUSAL_PH.search(ventana) or _RX_CAUSAL_PH.search(nv)
        if mt and mc:
            # el match causal aislado tampoco debe estar negado localmente
            # (cubre "explica" dentro de "no explica" si el RX_CAUSAL no lo evita)
            span_c = mc.group(0)
            # mirar 20 chars antes del match en la ventana
            i0 = max(0, (ventana.lower().find(span_c.lower()) if span_c else 0) - 24)
            ctx = ventana[i0 : i0 + 24 + len(span_c)]
            if _causalidad_negada(ctx) or _causalidad_negada(ventana):
                continue
            fired_struct = True
            frag_parts.append(f"{mt.group(0)} | {mc.group(0)}")
            razones.append("temporal_cerca_causal")
            break

    if not fired_geom and not fired_struct:
        return []

    # Severidad: ¿nombra outcome sellado / desenlace / ruptura?
    hard = False
    outcome_hit = None
    m_out = _RX_OUTCOME_POSTHOC.search(q)
    if m_out:
        # outcome como lo causado/predicho (cerca de causal)
        # "por eso ... ruptura" / "predecía el desenlace"
        hard = True
        outcome_hit = m_out.group(0)

    sellado_match = None
    if sellado_post_Z:
        # objetos nominalizados del texto vs sellado
        objs = extraer_objetos_heuristico(q)
        # también palabras del outcome genérico ya cubiertas
        cot = cotejar_contra_sellado(objs, sellado_post_Z)
        if cot["hay_match"]:
            hard = True
            sellado_match = cot["matches"]
        else:
            # substring: alguna variante de sellado aparece junto a causal
            expanded = _expand_sellado(sellado_post_Z)
            for etiqueta, variants in expanded:
                for v in variants:
                    if len(v) >= 4 and v in nq:
                        hard = True
                        sellado_match = [{"sellado": etiqueta, "via": "post_hoc_substr"}]
                        break
                if sellado_match:
                    break

    sev = "hard" if hard else "soft"
    tip = "POST_HOC_TEMPORAL"
    rec = (
        "Bandera post-hoc: reformular como observación (quitar 'por eso'/'esto predijo'; "
        "dejar solo la secuencia descrita). Geometría (κ/dX) es diagnóstica, no causa. "
        "Investigador decide si hay causa real o solo orden temporal. No bloquea el tubo."
    )
    hallazgos.append(
        HallazgoPregunta(
            tipo=tip,
            POSIBLE_PREGUNTA_DIRIGIDA=True,
            severidad=sev,
            fragmento=" | ".join(frag_parts)[:200] or q[:120],
            patron="post_hoc: temporal∩causal | geom_sujeto_causal",
            recomendacion=rec,
            pregunta_original=q,
            estructura={
                "capa": "post_hoc",
                "razones": razones,
                "geom_sujeto_causal": fired_geom,
                "temporal_cerca_causal": fired_struct,
                "outcome_hit": outcome_hit,
                "sellado_match": sellado_match,
                "accion": "bandera_no_bloquea",
            },
            intencionalidad=(
                "lectura causal post-hoc del orden temporal — sesgo de pregunta/narración; "
                "distinto de sesgo de tokens del corpus"
            ),
        )
    )
    return hallazgos



# ---------------------------------------------------------------------------
# FALACIAS_SIDECAR (sandbox) — deformaciones; highlight only; no 244
# Vecinos de post_hoc. Estructura + polaridad. NO_RESUELTO si no alcanza.
# ---------------------------------------------------------------------------

_RX_COND = re.compile(
    r"\b(?:si|cuando)\b(.{5,120}?)\b(?:entonces|luego|,)\s+(.{5,120}?)(?:\.|$)",
    re.I | re.S,
)
_RX_SI_SOLO = re.compile(
    r"\b(?:si\s+y\s+solo\s+si|entonces\s+y\s+solo\s+entonces|equivale\s+a|"
    r"condici[oó]n\s+necesaria\s+y\s+suficiente|nss)\b",
    re.I,
)
_RX_NECESARIO = re.compile(r"\b(?:necesario|necesaria|hace\s+falta|requisito)\b", re.I)
_RX_SUFICIENTE = re.compile(r"\b(?:suficiente|basta(?:\s+con)?|alcanza\s+con)\b", re.I)
_RX_AF = re.compile(
    # (P→Q), Q ⊢ P  — afirmó el entonces y concluye el si
    r"(?:entonces|luego|por\s+tanto|por\s+eso).{0,80}?"
    r"(?:por\s+lo\s+tanto|luego|entonces|as[ií]\s+que|ergo).{0,40}?"
    r"(?:era|fue|es|hab[ií]a|deb[ií]a\s+ser|ten[ií]a\s+que\s+ser|se\s+trata\s+de)",
    re.I | re.S,
)
_RX_AF2 = re.compile(
    r"\b(?:pas[oó]|ocurri[oó]|se\s+cumpli[oó]|hubo)\b.{0,60}?"
    r"\b(?:entonces|luego|por\s+eso|por\s+tanto)\b.{0,60}?"
    r"\b(?:la\s+causa\s+era|era\s+porque|se\s+deb[ií]a\s+a|prueba\s+de\s+que)\b",
    re.I | re.S,
)
_RX_AD = re.compile(
    # (P→Q), ¬P ⊢ ¬Q
    r"\bsi\b.{5,120}?\b(?:entonces|luego)\b.{5,160}?"
    r"(?:como\s+no|como\s+nunca|al\s+no|no\s+llov\w*|no\s+hubo|no\s+se\s+dio)"
    r".{0,100}?"
    r"(?:entonces\s+no|luego\s+no|por\s+tanto\s+no|no\s+puede(?:\s+estar)?|imposible)",
    re.I | re.S,
)
_RX_CS = re.compile(
    r"\b(?:al\s+mismo\s+tiempo|junto\s+con|acompañado\s+de|correlacion|"
    r"mientras\s+(?:tanto\s+)?(?:que\s+)?|en\s+paralelo)\b.{0,100}?"
    r"\b(?:por\s+eso|caus[oó]|provoc[oó]|debido\s+a|gracias\s+a|culpa\s+de)\b",
    re.I | re.S,
)
_RX_PQ = re.compile(
    r"\b(?:sabemos\s+que|dado\s+que|puesto\s+que|ya\s+que\s+es\s+claro|obviamente|"
    r"es\s+evidente\s+que|sin\s+duda)\b.{5,120}?"
    r"(?:\?|¿|por\s+qu[eé]|cu[aá]ndo|d[oó]nde|c[oó]mo)",
    re.I | re.S,
)
_RX_EQ = re.compile(
    # misma raíz usada en dos sentidos burdos: "poder" político vs capacidad — soft heuristic
    r"\b(poder|libertad|pueblo|justicia|verdad|crisis)\b.{20,160}?\b\1\b",
    re.I | re.S,
)


def _negacion_local(texto: str) -> bool:
    n = _norm(texto)
    return bool(re.search(
        r"\bno\s+(?:es|era|fue|prueba|demuestra|implica|sigue|concluye)|"
        r"\bno\s+por\s+eso|\bsin\s+que\s+eso|\bno\s+equivale",
        n,
    ))


def detectar_falacias(texto: str) -> List[HallazgoPregunta]:
    """FALACIAS_SIDECAR: AF/AD/CS/BC1/BC2/PQ/EQ. Highlight only.

    Cada hallazgo: familia, estructura, evidencia, estado DETECTADA|POSIBLE.
    Polaridad: si niega la inferencia, no dispara.
    """
    if not texto or not str(texto).strip():
        return []
    q = str(texto).strip()
    nq = _norm(q)
    out: List[HallazgoPregunta] = []

    def add(tipo: str, sev: str, frag: str, patron: str, razones: List[str], rec: str):
        out.append(
            HallazgoPregunta(
                tipo=tipo,
                POSIBLE_PREGUNTA_DIRIGIDA=True,
                severidad=sev,
                fragmento=frag[:200],
                patron=patron,
                recomendacion=rec,
                pregunta_original=q,
                estructura={
                    "capa": "falacias_sidecar",
                    "familia": tipo,
                    "razones": razones,
                    "estado": "DETECTADA" if sev == "hard" else "POSIBLE",
                    "accion": "bandera_no_bloquea",
                },
                intencionalidad=(
                    "falacia de transición en pregunta/narración — ruido/sesgo de enunciación; "
                    "no patrón 244 ni HIT de tubo"
                ),
            )
        )

    # AF — afirmar el consecuente
    if not _negacion_local(q):
        m = _RX_AF2.search(q) or _RX_AF.search(q)
        # también forma explícita escolar
        m2 = re.search(
            r"\bsi\b.{5,80}\bentonces\b.{5,100}"
            r"(?:se\s+cumpl[ií][oó]|pas[oó]|ocurri[oó]|hubo).{0,60}"
            r"(?:por\s+tanto|luego|entonces|as[ií]\s+que).{0,40}"
            r"(?:la\s+causa|el\s+antecedente|era\s+porque|deb[ií]a\s+ser)",
            q, re.I | re.S,
        )
        if m2 or m:
            frag = (m2 or m).group(0)[:160]
            if not _negacion_local(frag):
                add(
                    "AF_AFIRMAR_CONSECUENTE",
                    "hard" if m2 else "soft",
                    frag,
                    "falacia: (P→Q), Q ⊢ P",
                    ["afirmar_consecuente"],
                    "Bandera AF: pasó el 'entonces' no prueba el 'si'. Reformular sin invertir la flecha.",
                )

    # AD — negar el antecedente
    m = _RX_AD.search(q)
    if not m:
        # forma escolar explícita en dos oraciones
        if (
            re.search(r"\bsi\b.{5,80}\b(?:entonces|luego)\b", q, re.I | re.S)
            and re.search(r"\b(?:como\s+no|no\s+llov\w*|no\s+hubo|no\s+se\s+dio)\b", q, re.I)
            and re.search(r"\b(?:entonces\s+no|luego\s+no|por\s+tanto\s+no|no\s+puede|imposible)\b", q, re.I)
        ):
            class _M:
                def group(self, _=0):
                    return q[:160]
            m = _M()
    if m and not _negacion_local(m.group(0)):
        add(
            "AD_NEGAR_ANTECEDENTE",
            "soft",
            m.group(0)[:160],
            "falacia: (P→Q), ¬P ⊢ ¬Q",
            ["negar_antecedente"],
            "Bandera AD: que no se dé el 'si' no tumba el 'entonces'. Revisar la inferencia.",
        )

    # CS — cum hoc / correlación ≠ causa
    m = _RX_CS.search(q)
    if m and not _negacion_local(m.group(0)):
        add(
            "CS_CUM_HOC",
            "soft",
            m.group(0)[:160],
            "falacia: correlación/co-ocurrencia leída como causa",
            ["cum_hoc"],
            "Bandera CS: juntos en el tiempo ≠ causa. Dejar como co-ocurrencia hasta prueba.",
        )

    # BC1 — vender → como ↔
    if _RX_SI_SOLO.search(q):
        # si afirma "si y solo si" pero solo argumenta una dirección
        una_flecha = re.search(
            r"\b(?:si)\b.{5,80}\b(?:entonces)\b(?!.{0,80}(?:solo\s+si|necesari))",
            q, re.I | re.S,
        )
        # explícito: dice "si y solo si" + solo muestra una vía
        add(
            "BC1_BICONDICIONAL_INCOMPLETO",
            "soft",
            (_RX_SI_SOLO.search(q).group(0) + " …")[:160],
            "falacia: vender → como ↔",
            ["bicondicional_incompleto"],
            "Bandera BC1: 'si y solo si' exige ambas direcciones. Marcar NO_RESUELTO si solo hay una.",
        )
    elif re.search(r"\b(?:equivale\s+a|es\s+lo\s+mismo\s+que)\b", nq) and re.search(r"\bsi\b", nq):
        if not _negacion_local(q):
            add(
                "BC1_BICONDICIONAL_INCOMPLETO",
                "soft",
                q[:120],
                "falacia: equivale/si leído como ↔ sin doble vía",
                ["equivale_como_bicondicional"],
                "Bandera BC1: 'equivale' puede ser ↔ incompleto. Pedir ambas direcciones.",
            )

    # BC2 — necesario ↔ suficiente
    if _RX_NECESARIO.search(q) and _RX_SUFICIENTE.search(q):
        # confusión explícita
        if re.search(r"\b(?:necesario).{0,40}(?:suficiente)|(?:suficiente).{0,40}(?:necesario)\b", nq):
            if re.search(r"\b(?:es\s+lo\s+mismo|equivale|da\s+igual|o\s+sea)\b", nq):
                add(
                    "BC2_NECESARIO_SUFICIENTE",
                    "soft",
                    q[:140],
                    "falacia: confundir necesario con suficiente",
                    ["necesario_vs_suficiente"],
                    "Bandera BC2: necesario ≠ suficiente. Separar las dos condiciones.",
                )
    elif _RX_NECESARIO.search(q) and re.search(r"\b(?:basta|con\s+eso\s+alcanza|suficiente)\b", nq):
        if not _negacion_local(q):
            add(
                "BC2_NECESARIO_SUFICIENTE",
                "soft",
                q[:140],
                "falacia: tratar necesario como si bastara",
                ["necesario_como_suficiente"],
                "Bandera BC2: 'necesario' no implica 'basta'.",
            )

    # PQ — petitio / circular (refuerzo; 2a ya cubre parte)
    m = _RX_PQ.search(q)
    if m and not _negacion_local(m.group(0)):
        add(
            "PQ_PETITIO",
            "soft",
            m.group(0)[:160],
            "falacia: premisa consumada + pregunta (circularidad)",
            ["petitio_premisa_dada"],
            "Bandera PQ: la pregunta asume lo que debería probar. Neutralizar la premisa.",
        )

    # EQ — equivocación (heurística suave; fácil FP → soft siempre)
    m = _RX_EQ.search(q)
    if m:
        # no fire en poesía/lista si es solo repetición retórica corta sin claim
        if re.search(r"\b(?:por\s+tanto|luego|entonces|significa|prueba|demuestra|causa)\b", nq):
            add(
                "EQ_EQUIVOCACION",
                "soft",
                m.group(0)[:160],
                "falacia: misma palabra, posible sentido distinto",
                ["equivocacion_lexema", m.group(1).lower()],
                "Bandera EQ (POSIBLE): mismo lexema dos veces cerca de inferencia. Verificar si cambia de sentido.",
            )

    return out


def detectar_pregunta_dirigida(
    pregunta: str,
    sellado_post_Z: Optional[Sequence[str]] = None,
    *,
    extraer_objeto_fn: Optional[ExtraerObjetoFn] = None,
) -> List[HallazgoPregunta]:
    """API unificada Señal 2: 2a ∪ 2b ∪ 2c ∪ post_hoc ∪ falacias. Dedup por severidad máxima."""
    hall: List[HallazgoPregunta] = []
    hall.extend(detectar_estructura_PO(pregunta))
    if sellado_post_Z is not None:
        hall.extend(
            detectar_contra_sellado(
                pregunta, sellado_post_Z, extraer_objeto_fn=extraer_objeto_fn
            )
        )
    hall.extend(detectar_post_hoc(pregunta, sellado_post_Z=sellado_post_Z))
    hall.extend(detectar_falacias(pregunta))
    # si hay hard, no hace falta listar soft duplicado de POSIBLE...
    return hall


def sugerir_pregunta_neutral(
    pregunta: str, sujeto: str = "", z_foto: str = "Z_foto"
) -> str:
    quien = f" de {sujeto}" if (sujeto or "").strip() else ""
    _ = pregunta
    return (
        f"¿Qué señales tempranas de riesgo, crisis o aislamiento aparecen{quien} "
        f"en la traza hasta {z_foto or 'Z_foto'}, sin presuponer un desenlace concreto?"
    )


# ---------------------------------------------------------------------------
# Señal 1 — corpus
# ---------------------------------------------------------------------------

TOKENS_FUGA_SOFT: Set[str] = {"autodestruccion", "crisis_existencial"}
TOKENS_FUGA_DEFAULT: Set[str] = {
    "suicidio",
    "sacrificio_final",
    "overdose",
    "sobredosis",
} | set(TOKENS_FUGA_SOFT)


@dataclass
class HallazgoCorpus:
    tipo: str
    corte_id: str
    eje: str
    token: str
    severidad: str
    nota: str


def detectar_fuga_corpus(
    cuts: Sequence[Dict[str, Any]],
    *,
    hard: Optional[Set[str]] = None,
    soft: Optional[Set[str]] = None,
) -> List[HallazgoCorpus]:
    hard = hard if hard is not None else set(TOKENS_FUGA_DEFAULT) - set(TOKENS_FUGA_SOFT)
    soft = soft if soft is not None else set(TOKENS_FUGA_SOFT)
    hallazgos: List[HallazgoCorpus] = []
    for raw in cuts:
        cid = str(raw.get("id") or raw.get("corte") or "?")
        for eje in ("P", "A", "C"):
            for item in raw.get(eje) or []:
                if isinstance(item, (list, tuple)) and item:
                    tok = str(item[0])
                elif isinstance(item, dict):
                    tok = str(item.get("token") or item.get("t") or "")
                else:
                    continue
                if tok in hard:
                    hallazgos.append(
                        HallazgoCorpus(
                            tipo="FUGA_EN_CORPUS",
                            corte_id=cid,
                            eje=eje,
                            token=tok,
                            severidad="hard",
                            nota="Token típico de T+k en foto que debería estar ciega.",
                        )
                    )
                elif tok in soft:
                    hallazgos.append(
                        HallazgoCorpus(
                            tipo="FUGA_EN_CORPUS",
                            corte_id=cid,
                            eje=eje,
                            token=tok,
                            severidad="soft",
                            nota="Posible anticipación; revisar sin spoiler.",
                        )
                    )
    return hallazgos


# ---------------------------------------------------------------------------
# Comparar boards
# ---------------------------------------------------------------------------

def comparar_boards(
    board_dirigida: Dict[str, float],
    board_neutral: Dict[str, float],
    *,
    top_k: int = 5,
) -> Dict[str, Any]:
    def top(b: Dict[str, float]) -> List[Tuple[str, float]]:
        return sorted(b.items(), key=lambda kv: -kv[1])[:top_k]

    t_d, t_n = top(board_dirigida), top(board_neutral)
    same_top1 = bool(t_d and t_n and t_d[0][0] == t_n[0][0])
    names_d, names_n = {n for n, _ in t_d}, {n for n, _ in t_n}
    overlap = len(names_d & names_n) / max(1, len(names_d | names_n))
    if same_top1 and overlap >= 0.6:
        lectura = "Board neutral parecido → señal puede ser de la foto. Investigador congela H."
    else:
        lectura = "Board neutral diverge → la pregunta empujaba. No aceptar 'desde C7' sobre premisa no probada."
    return {
        "top_dirigida": t_d,
        "top_neutral": t_n,
        "same_top1": same_top1,
        "overlap_topk": round(overlap, 4),
        "lectura": lectura,
        "H1": None,
        "H2": None,
        "nota": "comparar_boards no inventa hipótesis.",
    }


# ---------------------------------------------------------------------------
# API principal
# ---------------------------------------------------------------------------

def auditar(
    *,
    pregunta: str = "",
    pregunta_ciega: str = "",
    cuts: Optional[Sequence[Dict[str, Any]]] = None,
    sellado_post_Z: Optional[Sequence[str]] = None,
    extraer_objeto_fn: Optional[ExtraerObjetoFn] = None,
    raise_on_hard: bool = False,
) -> Dict[str, Any]:
    """Audita sin atascar el motor.

    raise_on_hard=False por defecto: bandera roja de *intencionalidad de pregunta*,
    no un stop del tubo 5x3. El investigador reformula cuando corresponda.
    """
    res = ResultadoGuardiaPregunta()
    q = (pregunta_ciega or pregunta or "").strip()

    # 2a∪2b∪2c∪post_hoc vía detectar_pregunta_dirigida (raise_on_hard=False default)
    for h in detectar_pregunta_dirigida(
        q, sellado_post_Z=sellado_post_Z, extraer_objeto_fn=extraer_objeto_fn
    ):
        if h.severidad == "hard":
            res.ok = False
        res.hallazgos.append(asdict(h))

    if cuts:
        for h in detectar_fuga_corpus(cuts):
            if h.severidad == "hard":
                res.ok = False
            res.hallazgos.append(asdict(h))

    hard = [h for h in res.hallazgos if h.get("severidad") == "hard"]
    soft = [h for h in res.hallazgos if h.get("severidad") == "soft"]

    if hard or soft:
        res.pregunta_neutral_sugerida = sugerir_pregunta_neutral(q)
        res.atencion_intencionalidad = (
            "ATENCION: esto es sesgo/intencionalidad de la PREGUNTA (premisa dada), "
            "no el mismo fenómeno que sesgo de tokens del corpus. "
            "Bandera roja = revisar y reformular; no atascar el motor ni fabricar H."
        )
    if hard:
        res.accion_obligatoria = (
            "1) Reformular sin hechos de sellado_post_Z. "
            "2) Re-correr misma foto. "
            "3) comparar_boards. "
            "4) Investigador congela H — este plugin no."
        )
    elif soft:
        res.accion_obligatoria = (
            "Señal suave: revisar redacción; preferible neutralizar. "
            "No bloquear corrida. Soft ≠ hard."
        )

    out = res.to_dict()
    out["POSIBLE_PREGUNTA_DIRIGIDA"] = any(
        h.get("POSIBLE_PREGUNTA_DIRIGIDA") for h in res.hallazgos
    )
    out["n_hard"] = len(hard)
    out["n_soft"] = len(soft)
    out["sellado_post_Z"] = list(sellado_post_Z or []) if sellado_post_Z is not None else None

    if raise_on_hard and hard:
        raise PreguntaDirigidaError(
            f"{PLUGIN}: hard={hard[0].get('tipo')} sev={hard[0].get('severidad')} "
            f"frag={hard[0].get('fragmento')}"
        )
    return out


# ---------------------------------------------------------------------------
# Demo / tests
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json

    SELLADO = ["Nevermind 1991", "fame global", "In Utero", "suicidios 1994"]

    cases = [
        ("demo", "¿A partir de cuándo se veía que Cobain se iba a suicidar?", True),
        ("2orac", "Sabemos que terminó suicidándose. ¿Qué corte marca el inicio de esa espiral?", True),
        ("dado", "Dado que murió por su propia mano en 1994, ¿dónde arranca el patrón?", True),
        ("inev", "¿Cuál fue el primer indicio de que el desenlace era inevitable?", True),  # soft o hard via PO
        ("grammy", "¿Desde cuándo se veía que iba a ganar el Grammy?", False),  # sin sellado grammy → solo PO?
        ("neutral", "¿Qué señales tempranas de riesgo aparecen hasta Z_foto?", False),
    ]

    rows = []
    for cid, q, _ in cases:
        r = auditar(pregunta=q, sellado_post_Z=SELLADO, raise_on_hard=False)
        rows.append({
            "id": cid,
            "ok": r["ok"],
            "n_hard": r["n_hard"],
            "n_soft": r["n_soft"],
            "capas": [h.get("estructura", {}).get("capa") or h.get("patron") for h in r["hallazgos"]],
            "atencion": bool(r.get("atencion_intencionalidad")),
        })

    # LLM hook demo (fake)
    def fake_llm(q: str):
        # simula LLM: objeto nominalizado sin importar redacción
        ql = q.lower()
        if "1994" in ql or "muerte" in ql or "suicid" in ql or "propia mano" in ql:
            return ["suicidio", "1994"]
        return []

    r_llm = auditar(
        pregunta="¿En qué corte empieza el camino hacia lo que pasó en 1994 con su muerte?",
        sellado_post_Z=SELLADO,
        extraer_objeto_fn=fake_llm,
    )

    print(json.dumps({
        "version": VERSION,
        "casos": rows,
        "demo_llm_hook": {
            "n_hard": r_llm["n_hard"],
            "hallazgos": r_llm["hallazgos"],
        },
        "candados": "H null; soft no atasca; intencionalidad ≠ sesgo tokens",
    }, ensure_ascii=False, indent=2))


# ===========================================================================
# 0.5.1_GUARDIANES — capa estructural añadida (la 0.5.0 queda intacta arriba)
# Motivo: con su batería propia de 5 falacias la 0.5.0 solo detectaba BC1,
# porque sus regex exigían la redacción escolar exacta. Aquí se reconoce la
# FORMA lógica: condicional (si A, B) + premisa menor + conclusión marcada,
# comparando átomos por raíz de palabra. Solo marca; nunca decide H.
# ===========================================================================
_detectar_falacias_050 = detectar_falacias
_detectar_post_hoc_050 = detectar_post_hoc

_STOP = set("""el la los las un una unos unas de del al a en y o u que se su sus lo le les es son fue era ser
esta este esto eso ese esa con por para como mas muy ya tambien pero sino si no ni the a an of to in and or
is are was were be it he she they his her its that this so then if not""".split())
_RX_NEG_TOK = re.compile(r"\b(?:no|nunca|jamas|tampoco|not|never|n't|nadie|ningun\w*)\b", re.I)
_RX_COND_ES_EN = re.compile(
    r"^\s*(?:si|if)\s+(?P<a>.+?)(?:\s*,\s*(?:entonces|then)?\s*|\s+(?:entonces|then)\s+)(?P<b>.+)$",
    re.I | re.S)
_RX_CONCL = re.compile(
    r"(?:,|;|\.)?\s*\b(?:as[ií]\s+que|por\s+lo\s+tanto|por\s+tanto|luego|por\s+eso|en\s+consecuencia|"
    r"de\s+modo\s+que|ergo|so|therefore|hence|thus)\b\s*,?\s*",
    re.I)


def _raices(txt: str) -> Set[str]:
    ws = re.findall(r"[a-zñ]+", _norm(txt))
    return {w[:3] for w in ws if len(w) >= 3 and w not in _STOP}


def _negado(txt: str) -> bool:
    return bool(_RX_NEG_TOK.search(_norm(txt).replace("n't", " not")))


def _mismo_atomo(x: str, y: str) -> bool:
    a, b = _raices(x), _raices(y)
    if not a or not b:
        return False
    inter = len(a & b)
    return inter >= max(1, int(0.5 * min(len(a), len(b)) + 0.5))


def _oraciones(texto: str) -> List[str]:
    return [s.strip() for s in re.split(r"(?<=[.?!])\s+|\n+", texto or "") if s.strip()]


def analizar_forma_condicional(texto: str) -> List[Dict[str, Any]]:
    """Devuelve argumentos condicionales encontrados con su forma:
    MP (válido) · MT (válido) · AF (falacia) · AD (falacia) · NO_RESUELTO."""
    ors = _oraciones(texto)
    out: List[Dict[str, Any]] = []
    for i, o in enumerate(ors):
        m = _RX_COND_ES_EN.match(o.rstrip(".;"))
        if not m:
            continue
        a, b = m.group("a").strip(), m.group("b").strip(" .;")
        resto = " ".join(ors[i + 1:i + 3])
        if not resto:
            continue
        mc = _RX_CONCL.search(resto)
        if not mc:
            continue
        menor, concl = resto[:mc.start()].strip(" ,;."), resto[mc.end():].strip(" ,;.")
        if not menor or not concl:
            continue
        # quita marcadores de premisa ("como no ...")
        menor_l = re.sub(r"^(?:como|dado\s+que|puesto\s+que|since|as)\s+", "", menor, flags=re.I)
        forma = "NO_RESUELTO"
        if _mismo_atomo(menor_l, b) and not _negado(menor_l) and _mismo_atomo(concl, a) and not _negado(concl):
            forma = "AF"
        elif _mismo_atomo(menor_l, a) and _negado(menor_l) and _mismo_atomo(concl, b) and _negado(concl):
            forma = "AD"
        elif _mismo_atomo(menor_l, a) and not _negado(menor_l) and _mismo_atomo(concl, b) and not _negado(concl):
            forma = "MP"
        elif _mismo_atomo(menor_l, b) and _negado(menor_l) and _mismo_atomo(concl, a) and _negado(concl):
            forma = "MT"
        out.append({"antecedente": a, "consecuente": b, "premisa_menor": menor, "conclusion": concl,
                    "forma": forma, "fragmento": (o + " " + resto)[:200]})
    return out


_RX_CS2 = re.compile(
    r"\b(?:cada\s+vez\s+que|siempre\s+que|coincid\w+\s+con|whenever|every\s+time|at\s+the\s+same\s+time)\b.{3,140}?"
    r"\b(?:provoc\w*|caus\w*|hace\s+que|trae|explica|causes?|brings?|makes?|leads?\s+to)\b",
    re.I | re.S)
_RX_PQ_COMPLEJA = re.compile(
    r"(?:¿\s*)?\b(?:por\s+qu[eé]|why)\b\s+(?:\w+\s+){0,3}?(?:siempre|nunca|jam[aá]s|always|never)\b[^?]{3,}\?",
    re.I)
_RX_PORQUE = re.compile(r"(?P<x>[^,;.]+?)\s+\b(?:porque|because)\b\s+(?P<y>[^,;.]+)", re.I)
_RX_TEMP_BIO = re.compile(
    r"\b(?:despu[eé]s\s+de|tras|luego\s+de|desde\s+que|a\s+ra[ií]z\s+de|after|since|following)\b", re.I)
_RX_CAUS_BIO = re.compile(
    r"\b(?:provoc[oó]|caus[oó]|llev[oó]\s+a|hizo\s+que|origin[oó]|desencaden[oó]|por\s+eso|"
    r"caused|led\s+to|triggered|that'?s\s+why|because\s+of\s+(?:it|that))\b", re.I)


def _hallazgo(tipo, sev, frag, patron, razones, rec, q, extra=None):
    est = {"capa": "falacias_sidecar_0_5_1", "familia": tipo, "razones": razones,
           "estado": "DETECTADA" if sev == "hard" else "POSIBLE", "accion": "bandera_no_bloquea"}
    if extra:
        est.update(extra)
    return HallazgoPregunta(tipo=tipo, POSIBLE_PREGUNTA_DIRIGIDA=True, severidad=sev, fragmento=frag[:200],
                            patron=patron, recomendacion=rec, pregunta_original=q, estructura=est,
                            intencionalidad="falacia de transición en texto — ruido/sesgo de enunciación; no patrón 244 ni HIT")


def detectar_falacias(texto: str) -> List[HallazgoPregunta]:
    """0.5.0 (intacta) ∪ capa estructural 0.5.1. Dedup por tipo."""
    base = _detectar_falacias_050(texto)
    if not texto or not str(texto).strip():
        return base
    q = str(texto).strip()
    tipos = {h.tipo for h in base}
    extra: List[HallazgoPregunta] = []
    for arg in analizar_forma_condicional(q):
        if arg["forma"] == "AF" and "AF_AFIRMAR_CONSECUENTE" not in tipos:
            extra.append(_hallazgo("AF_AFIRMAR_CONSECUENTE", "hard", arg["fragmento"], "falacia: (P→Q), Q ⊢ P",
                                   ["afirmar_consecuente", "forma_condicional"],
                                   "Bandera AF: que se cumpla el consecuente no prueba el antecedente.", q, {"argumento": arg}))
            tipos.add("AF_AFIRMAR_CONSECUENTE")
        elif arg["forma"] == "AD" and "AD_NEGAR_ANTECEDENTE" not in tipos:
            extra.append(_hallazgo("AD_NEGAR_ANTECEDENTE", "hard", arg["fragmento"], "falacia: (P→Q), ¬P ⊢ ¬Q",
                                   ["negar_antecedente", "forma_condicional"],
                                   "Bandera AD: que no se dé el antecedente no niega el consecuente.", q, {"argumento": arg}))
            tipos.add("AD_NEGAR_ANTECEDENTE")
    if "CS_CUM_HOC" not in tipos:
        m = _RX_CS2.search(q)
        if m and not _negacion_local(m.group(0)) and not _causalidad_negada(m.group(0)):
            extra.append(_hallazgo("CS_CUM_HOC", "soft", m.group(0), "falacia: co-ocurrencia leída como causa",
                                   ["cum_hoc", "co_ocurrencia_repetida"],
                                   "Bandera CS: que ocurran juntos no prueba causa.", q))
            tipos.add("CS_CUM_HOC")
    if "PQ_PETITIO" not in tipos:
        m = _RX_PQ_COMPLEJA.search(q)
        if m:
            extra.append(_hallazgo("PQ_PETITIO", "soft", m.group(0), "falacia: pregunta compleja (presupone lo que pregunta)",
                                   ["pregunta_compleja_siempre_nunca"],
                                   "Bandera PQ: la pregunta da por hecho un 'siempre/nunca'. Preguntar primero si ocurre.", q))
            tipos.add("PQ_PETITIO")
        else:
            pares = [(mm.group("x"), mm.group("y")) for mm in _RX_PORQUE.finditer(q)]
            for k in range(len(pares)):
                for j in range(k + 1, len(pares)):
                    (x1, y1), (x2, y2) = pares[k], pares[j]
                    if _mismo_atomo(x1, y2) and _mismo_atomo(y1, x2):
                        extra.append(_hallazgo("PQ_PETITIO", "soft", q[:200], "falacia: razonamiento circular (A porque B, B porque A)",
                                               ["circular_porque_reciproco"],
                                               "Bandera PQ: la razón y la conclusión se sostienen una a la otra.", q))
                        tipos.add("PQ_PETITIO")
                        break
                if "PQ_PETITIO" in tipos:
                    break
    return base + extra


def detectar_post_hoc(texto: str, sellado_post_Z: Optional[Sequence[str]] = None) -> List[HallazgoPregunta]:
    """0.5.0 (intacta) ∪ post hoc biográfico: marca temporal + verbo causal en la misma
    oración o en la siguiente, con polaridad no negada."""
    base = _detectar_post_hoc_050(texto, sellado_post_Z=sellado_post_Z)
    if base or not texto or not str(texto).strip():
        return base
    q = str(texto).strip()
    for ventana in _ventana_pares(_oraciones_adyacentes(q)):
        mt, mc = _RX_TEMP_BIO.search(ventana), _RX_CAUS_BIO.search(ventana)
        if mt and mc and mt.start() < mc.start() and not _causalidad_negada(ventana) and not _negacion_local(ventana):
            return [_hallazgo("POST_HOC_TEMPORAL", "soft", f"{mt.group(0)} | {mc.group(0)} :: {ventana[:150]}",
                              "post_hoc: secuencia temporal leída como causa", ["temporal_biografico_causal"],
                              "Bandera post hoc: 'después de' no prueba 'por causa de'. Dejar como secuencia.", q,
                              {"capa": "post_hoc_0_5_1"})]
    return base
