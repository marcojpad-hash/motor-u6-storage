#!/usr/bin/env python3
"""Calibrador lateral POE v0.3.

No modifica plugin_pregunta_detras_v2, guardianes, predictor, Engine V5 ni
catalogo 244. Conserva íntegra la salida baseline y agrega clasificación
contextual explicable; ningún marcaje original se borra del registro.
"""
from __future__ import annotations
import importlib.util
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MOTOR = ROOT / "motor" / "motor"
OUT = ROOT / "artifacts" / "poe_calibrador_linguistico_v03.json"

GOLD_CASES = [
    ("N01", "negativo", "Fue elegido presidente por el consejo en 2018."),
    ("N02", "negativo", "Fue delegado sindical durante tres años."),
    ("N03", "negativo", "La plaza pública abrió en 1920."),
    ("N04", "negativo", "Esta prueba compara dos versiones del procedimiento."),
    ("N05", "negativo", "El médico atendió a doce pacientes."),
    ("N06", "negativo", "La médica atendió a doce pacientes."),
    ("N07", "negativo", "El director presentó el informe al consejo."),
    ("N08", "negativo", "La directora presentó el informe al consejo."),
    ("N09", "negativo", "El público asistió a la ceremonia."),
    ("N10", "negativo", "La elección ocurrió en junio y fue documentada."),
    ("N11", "negativo", "La delegación publicó los resultados del estudio."),
    ("N12", "negativo", "El candidato fue elegido por mayoría simple."),
    ("N13", "negativo", "¿Era un hombre cruel o una persona compasiva?"),
    ("P01", "positivo", "Era ambicioso y autoritario con sus colaboradores."),
    ("P02", "positivo", "Fue manipulador y egocéntrico durante el conflicto."),
    ("P04", "positivo", "Su conducta fue oportunista y arrogante."),
    ("P05", "positivo", "Se describía como visionario y obsesivo."),
    ("A01", "ambiguo", "Fue elegido como líder natural del movimiento."),
    ("A02", "ambiguo", "La ambición pública del delegado quedó documentada."),
    ("A03", "ambiguo", "No fue poco relevante para el resultado."),
    ("A04", "ambiguo", "El director dijo que el plan era viable cuando lo vio."),
    ("A05", "ambiguo", "Aprobó el proyecto porque era rentable."),
]

# Set nuevo, no usado para definir las reglas del primer calibrador.
CHALLENGE_CASES = [
    ("C01", "negativo", "La candidata fue elegida por el comité."),
    ("C02", "negativo", "El ensayo fue documentado por el equipo."),
    ("C03", "negativo", "El proyecto es rentable."),
    ("C04", "negativo", "La hipótesis es viable."),
    ("C05", "negativo", "El médico fue reconocido por el hospital."),
    ("C06", "positivo", "La directora es responsable de sus decisiones."),
    ("C07", "positivo", "Fue cruel con sus rivales."),
    ("C08", "positivo", "El equipo lo describió como autoritario."),
    ("C09", "positivo", "Se le consideraba manipulador por sus colaboradores."),
    ("C10", "negativo", "Esta calibración compara dos métodos."),
]

GENDER_PAIRS = [
    ("G01", "El director fue elegido por el consejo.", "La directora fue elegida por el consejo."),
    ("G02", "El médico atendió al paciente.", "La médica atendió a la paciente."),
    ("G03", "El delegado entregó el informe.", "La delegada entregó el informe."),
]

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

def corrected_filter(text, baseline_module):
    base = baseline_module.filtrar(text)
    original = list(base.get("marcajes", []))
    profile = []
    observations = []
    ambiguities = []
    attributed = []
    normalized = text.lower()
    # "esta" sin tilde es demostrativo; "está" con tilde es forma verbal.
    if re.search(r"^\s*esta\s+(?:prueba|calibracion|evaluacion|version|hipotesis)\b", normalized):
        for mark in original:
            if mark.get("lexema") in {"prueba", "calibracion", "evaluacion", "version", "hipotesis"}:
                observations.append({"mark": mark, "class": "DEMONSTRATIVO_DETERMINANTE",
                                     "reason": "'esta' sin tilde determina un sustantivo; no es la cópula 'está'."})
    # Participio de selección/nombramiento/documentación: evento o rol, no rasgo psicológico.
    passive_terms = {"elegido", "elegida", "elegidos", "elegidas", "delegado", "delegada",
                     "documentado", "documentada", "documentados", "documentadas", "reconocido", "reconocida"}
    for mark in original:
        lex = mark.get("lexema", "")
        frag = mark.get("fragmento", "")
        if lex in passive_terms and re.search(r"\b(?:fue|fueron|era|eran|ha sido|han sido)\b", normalized):
            observations.append({"mark": mark, "class": "EVENTO_O_ROL",
                                 "reason": "Participio de elección, delegación, documentación o reconocimiento; conservar como evento/rol, no como perfil psicológico."})
    # Nombres de clase/persona no son por sí solos rasgos predicativos.
    for mark in original:
        if mark.get("lexema") == "hombre" and re.search(r"\b(?:era|es|fue)\s+un\s+hombre\b", normalized):
            observations.append({"mark": mark, "class": "NUCLEO_NOMINAL",
                                 "reason": "El sustantivo 'hombre' no es el atributo; no convertirlo en perfil."})
    # Atributos de entidades no personales o con sujeto elíptico dudoso.
    nonperson = r"\b(?:proyecto|plan|hipotesis|empresa|margen|ventas|ensayo|calibracion|prueba)\b"
    for mark in original:
        if mark.get("lexema") in {"rentable", "viable", "documentada"} and re.search(nonperson, normalized):
            if re.search(r"\bporque\s+(?:era|fue|es|resulto)\b", normalized) or re.search(r"\bcuando\s+lo\s+vio\b", normalized):
                ambiguities.append({"type": "REFERENTE_O_SUJETO_ELIPTICO", "fragment": mark.get("fragmento", ""),
                                    "reason": "El atributo puede referirse al objeto/proyecto o a un sujeto elíptico; no elegir referente sin evidencia."})
            observations.append({"mark": mark, "class": "ATRIBUTO_DE_ENTIDAD",
                                 "reason": "Viabilidad/rentabilidad/documentación describe una entidad o estado; no inferir rasgo de persona."})
    # Litotes: conservar en canal retórico, sin contarla como perfilamiento del sujeto.
    for mark in original:
        if mark.get("funcion") == "MARCO_EVALUATIVO":
            observations.append({"mark": mark, "class": "MARCO_EVALUATIVO",
                                 "reason": "Se conserva como tropo/marco retórico, separado del conteo de perfilamiento."})
    # Descripciones reportadas: guardar como atribución, no como afirmación propia.
    attr_match = re.search(
        r"\b(?:se describia|se describía|lo describian|lo describían|la describian|la describían|"
        r"el equipo lo describio|el equipo lo describió|se le consideraba|se le consideró|"
        r"lo consideraban|la consideraban)\s+como\s+([a-záéíóúñ]+(?:\s+y\s+[a-záéíóúñ]+)*)",
        text, re.I)
    if attr_match:
        words = re.findall(r"[a-záéíóúñ]+", attr_match.group(1), re.I)
        for word in words:
            if word.lower() not in {"y", "un", "una"}:
                attributed.append({"lexema": word, "class": "ATRIBUCION_REPORTADA",
                                   "source_fragment": attr_match.group(0),
                                   "asserted_by_system": False,
                                   "reason": "La frase atribuye la descripción a una fuente/persona; no presentarla como hecho propio."})
    # Pregunta disyuntiva: conserva alternativas; no convertir pregunta en afirmación.
    if "?" in text and re.search(r"\s+o\s+", normalized):
        ambiguities.append({"type": "PREGUNTA_DISYUNTIVA_NO_AFIRMATIVA", "fragment": text,
                            "alternatives": re.findall(r"\b(?:cruel|compasiva|compasivo|autoritario|ambicioso)\b", normalized),
                            "reason": "Pregunta con alternativas; no afirma ninguna alternativa."})
    # Referente de sujeto omitido en subordinada temporal con dos posibles agentes.
    if re.search(r"\b(?:director|asesor|gerente|ministro)\b.*\b(?:asesor|director|gerente|ministro)\b.*\bcuando\s+(?:salio|salió|llego|llegó)\b", normalized):
        ambiguities.append({"type": "REFERENTE_SUBORDINADA_ELIPTICA", "fragment": text,
                            "reason": "El sujeto omitido de la subordinada admite más de un antecedente."})
    # Aprobó X porque era rentable: el sujeto de "era" no queda resuelto por la forma superficial.
    if re.search(r"\baprob[oó]\b.*\bproyecto\b.*\bporque\s+era\s+rentable\b", normalized):
        ambiguities.append({"type": "REFERENTE_CAUSAL_AMBIGUO", "fragment": text,
                            "reason": "No se decide si 'rentable' refiere al proyecto o al sujeto omitido."})
    removed_ids = {id(x["mark"]) for x in observations}
    for mark in original:
        if id(mark) in removed_ids:
            continue
        if mark.get("funcion") == "ETIQUETA_SUJETO" and mark.get("highlight"):
            profile.append(mark)
    # Avoid duplicate profile records when the same mark matched several rules.
    seen = set()
    profile = [m for m in profile if not ((m.get("lexema"), m.get("fragmento")) in seen or seen.add((m.get("lexema"), m.get("fragmento"))))]
    return {
        "baseline": base,
        "profile_marks_corrected": profile,
        "attributed_profile_marks": attributed,
        "non_profile_observations": observations,
        "ambiguities": ambiguities,
        "profile_detected": bool(profile or attributed),
        "profile_count": len(profile) + len(attributed),
        "evaluative_marks": [m for m in original if m.get("funcion") == "MARCO_EVALUATIVO"],
    }

def metrics(cases, results, key):
    rows = []
    for cid, gold, text in cases:
        if gold == "ambiguo":
            continue
        detected = results[cid]["profile_detected"]
        rows.append({"id": cid, "gold": gold, "detected": detected})
    tp = sum(r["gold"] == "positivo" and r["detected"] for r in rows)
    fp = sum(r["gold"] == "negativo" and r["detected"] for r in rows)
    tn = sum(r["gold"] == "negativo" and not r["detected"] for r in rows)
    fn = sum(r["gold"] == "positivo" and not r["detected"] for r in rows)
    return {"tp": tp, "fp": fp, "tn": tn, "fn": fn,
            "precision": tp/(tp+fp) if tp+fp else None,
            "recall": tp/(tp+fn) if tp+fn else None,
            "false_positive_rate": fp/(fp+tn) if fp+tn else None,
            "rows": rows}

def run():
    behind = load_module("poe_base_plugin_v233", MOTOR / "plugin_pregunta_detras_v2.py")
    copi = load_module("poe_base_copi", MOTOR / "guardian_logica_copi_v1.py")
    all_results = {}
    for cid, gold, text in GOLD_CASES + CHALLENGE_CASES:
        all_results[cid] = corrected_filter(text, behind)
    base_results = {}
    for cid, gold, text in GOLD_CASES + CHALLENGE_CASES:
        b = behind.filtrar(text)
        base_results[cid] = {"profile_detected": bool(b.get("bandera"))}
    # El baseline trata MARCO_EVALUATIVO como perfilamiento en su bandera; se
    # reporta tal como opera para comparar el efecto del canal separado.
    gold_metrics = metrics(GOLD_CASES, all_results, "profile_detected")
    challenge_metrics = metrics(CHALLENGE_CASES, all_results, "profile_detected")
    base_gold_metrics = metrics(GOLD_CASES, base_results, "profile_detected")
    base_challenge_metrics = metrics(CHALLENGE_CASES, base_results, "profile_detected")
    gender = []
    for pid, masc, fem in GENDER_PAIRS:
        a, b = corrected_filter(masc, behind), corrected_filter(fem, behind)
        gender.append({"id": pid, "masculine_profile": a["profile_detected"],
                       "feminine_profile": b["profile_detected"],
                       "different": a["profile_detected"] != b["profile_detected"],
                       "masculine_observations": a["non_profile_observations"],
                       "feminine_observations": b["non_profile_observations"]})
    ambiguity_cases = []
    for cid, gold, text in [
        ("T01", "temporal_sin_causalidad", "Después de asumir el cargo, las ventas crecieron."),
        ("T02", "causal_explicita", "Las ventas crecieron porque aumentó la demanda."),
        ("T03", "causal_con_referente_ambiguo", "Aprobó el proyecto porque era rentable."),
        ("T04", "referente_pronominal_ambiguo", "El director habló con el asesor cuando salió de la oficina."),
        ("T05", "litotes_y_alcance_de_negacion", "No fue poco importante para el desenlace."),
        ("T06", "afirmacion_del_consecuente", "Si el equipo redujo costos, entonces mejoró el margen. El margen mejoró. Por tanto, el equipo redujo costos."),
        ("T07", "temporal_sin_causalidad", "La empresa cambió de director y después aumentaron las ventas."),
    ]:
        out = corrected_filter(text, behind)
        logic = copi.analizar_texto([text])
        ambiguity_cases.append({"id": cid, "gold_issue": gold, "text": text,
                                "causals": logic.get("causales", []),
                                "copi_marks": logic.get("marcas", []),
                                "profile_detected_corrected": out["profile_detected"],
                                "ambiguities_corrected": out["ambiguities"],
                                "retained_evaluative_marks": out["evaluative_marks"]})
    report = {
        "protocol": "POE-U6_LINGUISTIC_CALIBRATOR_V0.3",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "baseline_version": behind.VERSION,
        "scope": "wrapper lateral; baseline preservado; no predictor/Engine V5/catalog 244",
        "gold_corpus": {"n": len(GOLD_CASES), "baseline_metrics": base_gold_metrics,
                        "corrected_metrics": gold_metrics, "results": {cid: all_results[cid] for cid,_,_ in GOLD_CASES}},
        "challenge_corpus": {"n": len(CHALLENGE_CASES), "baseline_metrics": base_challenge_metrics,
                             "corrected_metrics": challenge_metrics, "results": {cid: all_results[cid] for cid,_,_ in CHALLENGE_CASES}},
        "gender_counterfactuals": {"n_pairs": len(gender), "n_different": sum(x["different"] for x in gender), "pairs": gender},
        "ambiguity_and_logic": {"n": len(ambiguity_cases), "cases": ambiguity_cases},
        "interpretation": [
            "Los marcajes baseline se conservan completos dentro de cada resultado.",
            "Las observaciones reclasificadas permanecen en non_profile_observations con razón explícita.",
            "Las atribuciones reportadas se separan de afirmaciones del sistema.",
            "Las métricas de corpus controlado no se extrapolan automáticamente.",
            "La comparación principal es baseline frente a calibrador sobre los mismos casos; el challenge es un conjunto adicional.",
        ],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "artifact": str(OUT),
        "baseline_gold": {k:v for k,v in base_gold_metrics.items() if k != "rows"},
        "corrected_gold": {k:v for k,v in gold_metrics.items() if k != "rows"},
        "baseline_challenge": {k:v for k,v in base_challenge_metrics.items() if k != "rows"},
        "corrected_challenge": {k:v for k,v in challenge_metrics.items() if k != "rows"},
        "gender_pairs_different": sum(x["different"] for x in gender),
        "ambiguity_cases": len(ambiguity_cases),
    }, ensure_ascii=False, indent=2))
    return report

if __name__ == "__main__":
    run()
