"""U6 clone of the agnostic, observational enunciative-context lateral.

This module records linguistic evidence; it does not infer motives, diagnose speakers,
decide truth, alter factual admission, or produce a project-specific verdict.
"""
from __future__ import annotations

import re
from collections import defaultdict
from typing import Any

VERSION = "LATERAL_CONTEXTO_ENUNCIATIVO_V1_0"
CAN_DECIDE_H = False
WRITES_PREDICTION = False
CHANGES_INPUT = False

JUDGMENT_RULES = {
    "ESTETICO": (r"\b(hermos[oa]s?|bell[oa]s?|fe[oa]s?|elegante[s]?|horrible[s]?)\b", "POSITIVA_NEGATIVA"),
    "VALORATIVO": (r"\b(brillante[s]?|excelente[s]?|mediocre[s]?|bueno[s]?|malo[s]?|admirable[s]?|terrible[s]?|superior|inferior)\b", "POSITIVA_NEGATIVA"),
    "MORAL": (r"\b(cruel(?:es)?|honesto[s]?|deshonesto[s]?|corrupt[oa]s?|just[oa]s?|injust[oa]s?|ético[s]?|inmoral(?:es)?)\b", "POSITIVA_NEGATIVA"),
    "PREDICTIVO": (r"\b(seguramente|probablemente|sin duda|va[n]? a|será[n]?|terminará[n]?|provocará[n]?|conseguirá[n]?|destruirá[n]?)\b", "PROYECCION"),
    "ESPECULATIVO": (r"\b(quizá[s]?|tal vez|acaso|podría[n]?|posiblemente|supongo|imagino|parece que)\b", "POSIBILIDAD"),
    "NORMATIVO": (r"\b(debe[n]?|debería[n]?|tiene[n]? que|tendría[n]? que|hay que|es necesario)\b", "DEBER"),
    "CAUSAL": (r"\b(porque|debido a|por culpa de|causó|provocó|originó|como consecuencia)\b", "ATRIBUCION_CAUSAL"),
    "INTENCIONAL": (r"\b(quiere[n]?|pretende[n]?|busca[n]?|intenta[n]?|manipula[n]?|desea[n]?)\b", "ATRIBUCION_DE_INTENCION"),
    "EPISTEMICO": (r"\b(creo que|sé que|sabemos que|es evidente|es obvio|no hay duda|está demostrado|supuestamente)\b", "CERTEZA_O_DUDA"),
    "COMPARATIVO": (r"\b(mejor que|peor que|más que|menos que|a diferencia de|en cambio|supera a)\b", "COMPARACION"),
}
POSITIVE = {"hermoso", "hermosa", "bello", "bella", "elegante", "brillante", "excelente", "bueno", "buena", "admirable", "honesto", "honesta", "justo", "justa", "ético", "ética", "superior"}
NEGATIVE = {"feo", "fea", "horrible", "mediocre", "malo", "mala", "terrible", "cruel", "corrupto", "corrupta", "deshonesto", "deshonesta", "injusto", "injusta", "inmoral", "inferior", "enemigo", "traidor", "saboteador", "amenaza"}
ADVERSARIAL = re.compile(r"\b(enemigo[s]?|traidor(?:es)?|saboteador(?:es)?|amenaza[s]?|destructor(?:es)?|plaga[s]?)\b", re.I)
EXCLUSION = re.compile(r"\b(solo existe|no hay otra|la única opción|no existe alternativa|todos saben|nadie puede negar)\b", re.I)
METALINGUISTIC = re.compile(r"\b(significa|definición|término|palabra|concepto|se denomina)\b", re.I)
PHATIC = re.compile(r"\b(hola|buenos días|¿me escuchas\?|¿sigues ahí\?|¿estamos?)\b", re.I)
POETIC = re.compile(r"\b(es un\s+(?:monstruo|ángel|demonio|faro|roca)|como un\s+\w+)\b", re.I)
CONATIVE = re.compile(r"\b(debes|haz|mira|considera|imagina|responde|dime|compara)\b", re.I)
SUBJECT = re.compile(r"^(.{1,55}?)\s+(?:es|fue|parece|resulta|será|debe|debería)\b", re.I)
SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


def _polarity(fragment: str) -> str:
    words = set(re.findall(r"[a-záéíóúñ]+", fragment.lower()))
    pos, neg = bool(words & POSITIVE), bool(words & NEGATIVE)
    if pos and not neg:
        return "POSITIVA"
    if neg and not pos:
        return "NEGATIVA"
    if pos and neg:
        return "MIXTA"
    return "NO_CLASIFICADA"


def _subject(sentence: str) -> str | None:
    match = SUBJECT.search(sentence.strip())
    if not match:
        return None
    value = match.group(1).strip(" ,;:")
    if value.lower().startswith(("según ", "para ", "creo que ")):
        return None
    return value[:60]


def _functions(sentence: str, judgments: list[dict[str, str]]) -> dict[str, list[str]]:
    jakobson = ["REFERENCIAL"]
    halliday = ["IDEACIONAL", "TEXTUAL"]
    if judgments:
        jakobson.append("EMOTIVA")
        halliday.append("INTERPERSONAL")
    if "?" in sentence or CONATIVE.search(sentence):
        jakobson.append("CONATIVA")
        halliday.append("INTERPERSONAL")
    if PHATIC.search(sentence):
        jakobson.append("FATICA")
    if METALINGUISTIC.search(sentence):
        jakobson.append("METALINGUISTICA")
    if POETIC.search(sentence):
        jakobson.append("POETICA")
    return {"jakobson": sorted(set(jakobson)), "halliday": sorted(set(halliday))}


def analyze(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Analyze records shaped as {text, origin?, speaker?, attributed_to?}."""
    observations: list[dict[str, Any]] = []
    actor_counts: dict[str, dict[str, int]] = defaultdict(lambda: {"POSITIVA": 0, "NEGATIVA": 0, "MIXTA": 0})
    for record in records:
        if not isinstance(record, dict):
            continue
        text = str(record.get("text") or "").strip()
        if not text:
            continue
        origin = str(record.get("origin") or "INPUT")
        speaker = str(record.get("speaker") or "NO_IDENTIFICADO_EN_INPUT")
        attributed_to = record.get("attributed_to")
        for sentence in SENTENCE_SPLIT.split(text):
            sentence = sentence.strip()
            if not sentence:
                continue
            judgments = []
            for kind, (pattern, subtype) in JUDGMENT_RULES.items():
                for match in re.finditer(pattern, sentence, re.I):
                    term = match.group(0)
                    judgments.append({"tipo": kind, "subtipo": subtype, "termino": term,
                                      "polaridad": _polarity(term)})
            actor = _subject(sentence)
            polarity = _polarity(sentence) if judgments else "NO_CLASIFICADA"
            if actor and judgments:
                actor_counts[actor][polarity] += 1
            observations.append({
                "fragmento": sentence[:500], "origen": origin, "enunciador": speaker,
                "atribuido_a": attributed_to, "actor_mencionado": actor,
                "juicios": judgments, "polaridad_fragmento": polarity,
                "funciones_linguisticas": _functions(sentence, judgments),
                "marco_adversarial": bool(ADVERSARIAL.search(sentence)),
                "exclusion_de_alternativas": bool(EXCLUSION.search(sentence)),
            })

    signals = []
    for actor, counts in sorted(actor_counts.items()):
        total = counts["POSITIVA"] + counts["NEGATIVA"] + counts["MIXTA"]
        if total >= 2 and (counts["POSITIVA"] >= 2 or counts["NEGATIVA"] >= 2):
            signals.append({"tipo": "CARGA_VALORATIVA_REITERADA", "actor": actor,
                            "conteos": dict(counts), "n_observaciones": total,
                            "estado": "OBSERVACION_PARA_REVISION"})
    positive_actors = {a for a, c in actor_counts.items() if c["POSITIVA"] >= 2}
    negative_actors = {a for a, c in actor_counts.items() if c["NEGATIVA"] >= 2}
    if positive_actors and negative_actors and positive_actors != negative_actors:
        signals.append({"tipo": "ASIMETRIA_VALORATIVA_ENTRE_ACTORES",
                        "actores_valorados_positivamente": sorted(positive_actors),
                        "actores_valorados_negativamente": sorted(negative_actors),
                        "estado": "COMPARACION_REQUERIDA_NO_VEREDICTO"})
    adversarial = [o for o in observations if o["marco_adversarial"]]
    if adversarial:
        signals.append({"tipo": "ENMARCADO_ADVERSARIAL", "n_observaciones": len(adversarial),
                        "origenes": sorted({o["origen"] for o in adversarial}),
                        "estado": "OBSERVACION_PARA_REVISION"})
    exclusions = [o for o in observations if o["exclusion_de_alternativas"]]
    if exclusions:
        signals.append({"tipo": "CIERRE_DISCURSIVO_DE_ALTERNATIVAS", "n_observaciones": len(exclusions),
                        "estado": "OBSERVACION_PARA_REVISION"})
    poetic = [o for o in observations if "POETICA" in o["funciones_linguisticas"]["jakobson"]]
    if poetic:
        signals.append({"tipo": "FUNCION_POETICA_OBSERVADA", "n_observaciones": len(poetic),
                        "estado": "OBSERVACION_PARA_REVISION"})
    causal_or_intentional = [j for o in observations for j in o["juicios"]
                             if j["tipo"] in ("CAUSAL", "INTENCIONAL")]
    if causal_or_intentional:
        signals.append({"tipo": "ATRIBUCION_CAUSAL_O_INTENCIONAL",
                        "n_observaciones": len(causal_or_intentional),
                        "estado": "OBSERVACION_PARA_REVISION"})

    routes = {
        "SHERLOCK_RIGOR": ["seleccion_asimetrica", "tesis_previa_vs_hechos"],
        "HECATE": ["exclusion_de_alternativas"],
        "SCHOPENHAUER": ["atribucion_de_intencion", "certeza_o_duda"],
        "FALACIAS": ["atribucion_causal", "cierre_discursivo"],
        "LOGICA_COPI": ["comparacion_de_premisas", "atribucion_causal"],
        "TROPOS_BERISTAIN": ["marco_adversarial", "funcion_poetica"],
        "PREGUNTA_DIRIGIDA_POST_HOC": ["direccionamiento_del_input"],
    }
    return {
        "version": VERSION, "observaciones": observations, "senales": signals,
        "conteos_por_actor": {a: dict(c) for a, c in sorted(actor_counts.items())},
        "rutas_controles": routes,
        "candados": {"can_decide_H": False, "escribe_H": False, "escribe_patterns": False,
                     "reordena_candidatos": False, "modifica_input": False},
        "limites": [
            "No infiere motivaciones, personalidad ni sesgos como hechos.",
            "No detecta omisiones sin un corpus de contraste declarado.",
            "No declara favoritismo: una asimetria es una senal para comparar evidencia y contexto.",
            "Las funciones del lenguaje son etiquetas heuristicas, no analisis linguistico exhaustivo.",
        ],
    }


def attach_context(blocks: list[dict[str, Any]], report: dict[str, Any]) -> list[dict[str, Any]]:
    """Attach traceable references to sibling controls without changing their decisions."""
    refs = {
        "SHERLOCK_RIGOR": {"CARGA_VALORATIVA_REITERADA", "ASIMETRIA_VALORATIVA_ENTRE_ACTORES", "CIERRE_DISCURSIVO_DE_ALTERNATIVAS", "ATRIBUCION_CAUSAL_O_INTENCIONAL"},
        "HECATE": {"CIERRE_DISCURSIVO_DE_ALTERNATIVAS"},
        "SCHOPENHAUER": {"CARGA_VALORATIVA_REITERADA", "ASIMETRIA_VALORATIVA_ENTRE_ACTORES", "ATRIBUCION_CAUSAL_O_INTENCIONAL"},
        "FALACIAS": {"ENMARCADO_ADVERSARIAL", "CIERRE_DISCURSIVO_DE_ALTERNATIVAS", "ATRIBUCION_CAUSAL_O_INTENCIONAL"},
        "LOGICA_COPI": {"ASIMETRIA_VALORATIVA_ENTRE_ACTORES", "ATRIBUCION_CAUSAL_O_INTENCIONAL"},
        "TROPOS_BERISTAIN": {"ENMARCADO_ADVERSARIAL", "FUNCION_POETICA_OBSERVADA"},
        "PREGUNTA_DIRIGIDA_POST_HOC": {"CIERRE_DISCURSIVO_DE_ALTERNATIVAS"},
    }
    signal_types = {s["tipo"] for s in report.get("senales", [])}
    for block in blocks:
        name = block.get("guardian")
        targets = refs.get(name, set())
        matched = sorted(signal_types & targets)
        if matched:
            block.setdefault("detalle", {})
            if not isinstance(block["detalle"], dict):
                block["detalle"] = {"detalle_previo": block["detalle"]}
            block["detalle"]["contexto_lateral_enunciativo"] = {
                "senales_referenciadas": matched,
                "solo_contexto": True,
                "no_modifica_bandera_ni_salida": True,
            }
    return blocks
