#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""filtro_relleno_013.py — PATCH 013 (2026-10-06). Filtro de tokens de relleno en el vocabulario de vecinos.

Un token del vocabulario de vecinos (memoria Caldero persistente, luces persistentes del bus y vecinos de la
corrida actual) NO vota ni entra a los insumos del acero si es:
  1) stopword de las listas Snowball (las mismas que usa NLTK) en español e inglés:
       https://snowballstem.org/algorithms/spanish/stop.txt
       https://snowballstem.org/algorithms/english/stop.txt
     (transcritas literalmente el 2026-10-06; las líneas comentadas con '|' en el original NO se incluyen)
  2) id de fuente: prefijo 'src_' (src_bio_1, src_web_3, ...);
  3) numérico puro (años calendario: '1882', '1899', '3');
  4) de menos de 3 caracteres;
  5) PATCH 015: palabra de año (años/anos/año/ano/year/years) — el motor es agnóstico a tiempo léxico;
     quedan como traza `anos_015` (además del conteo por motivo en filtrados_013).
Los tokens filtrados quedan visibles como traza (conteos `filtrados_013` por motivo).

Contrato: no escribe nada, no decide H, no toca listas favor/contra de familias, patterns ni el catálogo 244.
"""
from __future__ import annotations
from typing import Any, Dict, Iterable, List, Set, Tuple

VERSION = "FILTRO_RELLENO_013_20261006+ANOS_015_20261006"
FUENTE_LISTAS = ("snowballstem.org/algorithms/spanish/stop.txt", "snowballstem.org/algorithms/english/stop.txt")
MIN_LEN = 3
PREFIJOS_FUENTE = ("src_",)

# PATCH 015: palabras de año (además de numéricos puros ya filtrados en 013).
PALABRAS_ANO = frozenset({"años", "anos", "año", "ano", "year", "years"})

STOP_ES = frozenset("""
de la que el en y a los del se las por un para con no una su al lo como más pero sus le ya o este sí porque esta
entre cuando muy sin sobre también me hasta hay donde quien desde todo nos durante todos uno les ni contra otros
ese eso ante ellos e esto mí antes algunos qué unos yo otro otras otra él tanto esa estos mucho quienes nada muchos
cual poco ella estar estas algunas algo nosotros
mi mis tú te ti tu tus ellas nosotras vosotros vosotras os mío mía míos mías tuyo tuya tuyos tuyas suyo suya suyos
suyas nuestro nuestra nuestros nuestras vuestro vuestra vuestros vuestras esos esas
estoy estás está estamos estáis están esté estés estemos estéis estén estaré estarás estará estaremos estaréis
estarán estaría estarías estaríamos estaríais estarían estaba estabas estábamos estabais estaban estuve estuviste
estuvo estuvimos estuvisteis estuvieron estuviera estuvieras estuviéramos estuvierais estuvieran estuviese estuvieses
estuviésemos estuvieseis estuviesen estando estado estada estados estadas estad
he has ha hemos habéis han haya hayas hayamos hayáis hayan habré habrás habrá habremos habréis habrán habría habrías
habríamos habríais habrían había habías habíamos habíais habían hube hubiste hubo hubimos hubisteis hubieron hubiera
hubieras hubiéramos hubierais hubieran hubiese hubieses hubiésemos hubieseis hubiesen habiendo habido habida habidos
habidas
soy eres es somos sois son sea seas seamos seáis sean seré serás será seremos seréis serán sería serías seríamos
seríais serían era eras éramos erais eran fui fuiste fue fuimos fuisteis fueron fuera fueras fuéramos fuerais fueran
fuese fueses fuésemos fueseis fuesen siendo sido
tengo tienes tiene tenemos tenéis tienen tenga tengas tengamos tengáis tengan tendré tendrás tendrá tendremos
tendréis tendrán tendría tendrías tendríamos tendríais tendrían tenía tenías teníamos teníais tenían tuve tuviste
tuvo tuvimos tuvisteis tuvieron tuviera tuvieras tuviéramos tuvierais tuvieran tuviese tuvieses tuviésemos tuvieseis
tuviesen teniendo tenido tenida tenidos tenidas tened
""".split())

STOP_EN = frozenset("""
i me my myself we our ours ourselves you your yours yourself yourselves he him his himself she her hers herself
it its itself they them their theirs themselves what which who whom this that these those
am is are was were be been being have has had having do does did doing would should could ought
i'm you're he's she's it's we're they're i've you've we've they've i'd you'd he'd she'd we'd they'd i'll you'll
he'll she'll we'll they'll isn't aren't wasn't weren't hasn't haven't hadn't doesn't don't didn't won't wouldn't
shan't shouldn't can't cannot couldn't mustn't let's that's who's what's here's there's when's where's why's how's
a an the and but if or because as until while of at by for with about against between into through during before
after above below to from up down in out on off over under again further then once here there when where why how
all any both each few more most other some such no nor not only own same so than too very
""".split())


def _norm(t: Any) -> str:
    return str(t if t is not None else "").strip().casefold()


def motivo(tok: Any) -> str | None:
    """Motivo de filtrado o None si el token puede votar."""
    t = _norm(tok)
    if not t:
        return "vacio"
    if any(t.startswith(p) for p in PREFIJOS_FUENTE):
        return "id_fuente_src"
    if t.replace(".", "").replace(",", "").isdigit():
        return "numerico"
    if t in PALABRAS_ANO:
        return "palabra_ano_015"
    if len(t) < MIN_LEN:
        return "menos_de_3"
    if t in STOP_ES:
        return "stopword_es"
    if t in STOP_EN:
        return "stopword_en"
    return None


def filtrar(tokens: Iterable[Any]) -> Tuple[Set[str], Dict[str, Any]]:
    """Devuelve (tokens_que_votan, traza filtrados_013 con conteos por motivo + anos_015)."""
    ok: Set[str] = set(); por: Dict[str, int] = {}; n = 0; anos: List[str] = []
    for tok in tokens or []:
        t = _norm(tok)
        m = motivo(t)
        if m is None:
            ok.add(t)
        elif m != "vacio":
            por[m] = por.get(m, 0) + 1; n += 1
            if m == "palabra_ano_015" and t not in anos:
                anos.append(t)
    return ok, {"n": n, "por_motivo": dict(sorted(por.items())),
                "anos_015": {"n": len(anos), "tokens": sorted(anos),
                             "efecto": "palabra de año: solo traza, no vota (motor agnóstico a tiempo léxico)"}}
