"""Filtro de tokens StinkBox / Caldero arquetipos v2 (A5 2026-11-07).

Superconjunto estricto de v1: todo lo que v1 descarta, v2 lo descarta; además:

- con_digitos: cualquier dígito en el token, salvo allowlist explícita
  (formula10, r732). v1 solo descartaba dígitos sin racha de >=4 letras, así
  que pasaban `ciencia2024` o `abcd123`.
- ingles_generico: lista cerrada de genéricos en inglés observados en el
  StinkBox (knowledge, science, development, influence, ...).
- generico_es: lista cerrada de genéricos en español observados
  (obra, ejemplo, documento, ...).
- mes_calendario: meses ES/EN (enero, february, ...).
- prefijo_procedencia: tokens que empiezan por src_ / src- (src_brit, src_notion).

Exención de catálogo primero: si el token (normalizado) está en el vocabulario
del catálogo 244 (+ familias_tokens, solo lectura), se conserva aunque caiga en
una lista. Ninguna de las palabras basura observadas está en el catálogo
(verificado contra patterns_final_v14.json, 947 tokens), así que la exención
no neutraliza las listas nuevas; protege contenido real (sacrificio,
rivalidad_poder).

Decisiones documentadas (no olvidos):
- muy_corto se mantiene en <4 (v1): NO se endurece a <5 porque descartaría
  contenido real de 4 letras que el test de v1 conserva (dios, amor, arte).
- Nombres propios (mozart, viena): NO se detectan en v2 (fase 2). Detectarlos
  exigiría una lista curada: tras el casefold se pierde la mayúscula y
  adivinar por forma confundiría contenido real con nombres.
- No hay detección de idioma por modelo: las listas cerradas cubren los casos
  observados; un detector exigiría dependencias fuera de stdlib.

No toca Engine ni catálogo 244 (solo lectura). Determinista, stdlib.
"""
from __future__ import annotations
import re
from pathlib import Path

import filtro_tokens_arquetipos_v1 as _v1

VERSION = "FILTRO_TOKENS_ARQUETIPOS_V2_20261107"

# Genéricos en inglés observados en stinkbox/tokens.jsonl y su reporte
# (knowledge 37 casos, science, development, influence) + cercanos obvios.
GENERICO_EN = frozenset("""
knowledge science development influence history example document research
information content data general various different multiple several important
major main central public social cultural natural human actual work life
people person world study case thing way part form time year years group
society culture nature power
""".split())

# Genéricos en español observados (obra 33/35, ejemplo, documento) + cercanos.
# (v1 ya cubre como stopwords: caso, cosa, forma, parte, tipo, vez, gran,
# nuevo, mejor, mayor, cierto, mismo, todo, varios, diversos, distintos,
# diferentes; aquí solo van los que v1 NO cubre.)
GENERICO_ES = frozenset("""
obra ejemplo documento trabajo vida historia mundo persona personas gente
tema temas aspecto aspectos elemento elementos proceso procesos sistema
sistemas resultado resultados estudio estudios informacion contenido datos
cultural natural humano humana humanos humanas actual actuales principal
principales importante importantes
""".split())

MESES = frozenset("""
enero febrero marzo abril mayo junio julio agosto septiembre setiembre octubre
noviembre diciembre january february march april may june july august
september october november december
""".split())

# Tokens con dígitos que son contenido real y se conservan.
ALLOWLIST_DIGITOS = frozenset({"formula10", "r732"})

_VOCAB = None


def _vocab() -> dict:
    """Vocabulario del catálogo 244 (+ familias_tokens), cargado una vez.

    Si no se puede leer (uso standalone sin el pack), la exención se omite y
    el filtro sigue aplicando todas las demás reglas.
    """
    global _VOCAB
    if _VOCAB is None:
        try:
            _VOCAB = _v1.vocabulario_catalogo(Path(__file__).resolve().parent)
        except Exception:
            _VOCAB = {}
    return _VOCAB


def _en_catalogo(token: str) -> bool:
    a = _v1._sin_acentos(_v1.normalizar(token)).replace(" ", "_")
    voc = _vocab()
    return a in voc or _v1._sin_acentos(_v1.normalizar(token)) in voc


def motivo_descarte(token) -> str | None:
    """None si se conserva; si no, la razón del descarte."""
    t = _v1.normalizar(token)
    if not t:
        return "vacio"
    a = _v1._sin_acentos(t)
    # Allowlist explícita de tokens con dígitos: antes que v1, porque v1
    # descarta 'r732' por numero_o_puntuacion antes de llegar a con_digitos.
    if a in ALLOWLIST_DIGITOS:
        return None
    # Exención de catálogo primero: el catálogo manda sobre las listas.
    if _en_catalogo(t):
        return None
    # Base v1 (stopwords, boilerplate, urls, números, cortes de guion, ...).
    m = _v1.motivo_descarte(token)
    if m is not None:
        return m
    # Dígitos: cualquier dígito descarta, salvo allowlist explícita.
    if re.search(r"\d", t):
        return "con_digitos"
    # Procedencia: prefijos de origen de la fuente, no contenido.
    if a.startswith(("src_", "src-", "src ")):
        return "prefijo_procedencia"
    partes = [p for p in re.split(r"[\s_]+", a) if p]
    if len(partes) == 1:
        if a in MESES:
            return "mes_calendario"
        if a in GENERICO_EN:
            return "ingles_generico"
        if a in GENERICO_ES:
            return "generico_es"
    else:
        _ruido = set(_v1.STOPWORDS) | set(_v1.BOILERPLATE) | set(GENERICO_EN) | set(GENERICO_ES) | set(MESES)
        if all(p in _ruido or len(p) < 3 for p in partes):
            return "frase_sin_contenido"
    return None


def conservar(token) -> bool:
    return motivo_descarte(token) is None


def filtrar(tokens):
    return [t for t in tokens if conservar(t)]


# Re-exportos de v1 (misma firma; la v2 solo endurece conservar/motivo).
brechas = _v1.brechas
vocabulario_catalogo = _v1.vocabulario_catalogo
normalizar = _v1.normalizar
