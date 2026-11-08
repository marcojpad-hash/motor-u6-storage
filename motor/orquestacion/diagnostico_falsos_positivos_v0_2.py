#!/usr/bin/env python3
"""Diagnóstico empírico de falsos positivos, ambigüedad y sesgo lingüístico.

Ejecuta los clasificadores reales del paquete motor sobre un corpus controlado,
pequeño y etiquetado antes de observar sus salidas. No ejecuta ni modifica el
predictor, Engine V5 ni el catálogo 244. No convierte alertas en bloqueos.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
MOTOR = ROOT / "motor" / "motor"
OUT = ROOT / "artifacts" / "orquestacion_diagnostico_v0_2.json"

# Etiquetas fijadas antes de ejecutar. "ambiguo" se informa aparte; no se fuerza
# dentro de positivo/negativo para inflar falsos positivos o falsos negativos.
PROFILE_CASES = [
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
    ("P01", "positivo", "Era ambicioso y autoritario con sus colaboradores."),
    ("P02", "positivo", "Fue manipulador y egocéntrico durante el conflicto."),
    ("N13", "negativo", "¿Era un hombre cruel o una persona compasiva?"),
    ("P04", "positivo", "Su conducta fue oportunista y arrogante."),
    ("P05", "positivo", "Se describía como visionario y obsesivo."),
    ("A01", "ambiguo", "Fue elegido como líder natural del movimiento."),
    ("A02", "ambiguo", "La ambición pública del delegado quedó documentada."),
    ("A03", "ambiguo", "No fue poco relevante para el resultado."),
    ("A04", "ambiguo", "El director dijo que el plan era viable cuando lo vio."),
    ("A05", "ambiguo", "Aprobó el proyecto porque era rentable."),
]

# Pares mínimos: cambia género gramatical, no función ni contenido proposicional.
BIAS_PAIRS = [
    ("G01", "El director fue elegido por el consejo.", "La directora fue elegida por el consejo."),
    ("G02", "El médico atendió al paciente.", "La médica atendió a la paciente."),
    ("G03", "El delegado entregó el informe.", "La delegada entregó el informe."),
]

AMBIGUITY_CASES = [
    ("T01", "temporal_sin_causalidad", "Después de asumir el cargo, las ventas crecieron."),
    ("T02", "causal_explicita", "Las ventas crecieron porque aumentó la demanda."),
    ("T03", "causal_con_referente_ambiguo", "Aprobó el proyecto porque era rentable."),
    ("T04", "referente_pronominal_ambiguo", "El director habló con el asesor cuando salió de la oficina."),
    ("T05", "litotes_y_alcance_de_negacion", "No fue poco importante para el desenlace."),
    ("T06", "afirmacion_del_consecuente", "Si el equipo redujo costos, entonces mejoró el margen. El margen mejoró. Por tanto, el equipo redujo costos."),
    ("T07", "temporal_sin_causalidad", "La empresa cambió de director y después aumentaron las ventas."),
]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"NO_SE_PUDO_CARGAR:{path}")
    module = importlib.util.module_from_spec(spec)
    import sys
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def run():
    behind = load_module("poe_behind_actual", MOTOR / "plugin_pregunta_detras_v2.py")
    copi = load_module("poe_copi_actual", MOTOR / "guardian_logica_copi_v1.py")
    guardian = load_module("poe_guardian_actual", MOTOR / "guardianes_control_v1.py")

    profile_rows = []
    for cid, gold, text in PROFILE_CASES:
        r = behind.filtrar(text)
        marks = r.get("marcajes") or []
        profile_rows.append({
            "id": cid, "gold": gold, "text": text,
            "flag": r.get("bandera"), "n_profile": r.get("n_perfilamiento", 0),
            "marked": [{"lexema": m.get("lexema"), "funcion": m.get("funcion"),
                        "score": m.get("score"), "regla": m.get("regla"),
                        "highlight": m.get("highlight")} for m in marks],
        })

    # El wrapper real de guardianes se ejecuta sobre el mismo conjunto de textos.
    wrapper_case = {
        "case_id": "POE_DIAG_V02",
        "question": "¿Qué papel tuvo la persona en los hechos?",
        "cuts": [],
    }
    wrapper_texts = [{"origen": f"profile_cases[{i}]", "texto": row["text"]}
                     for i, row in enumerate(profile_rows)]
    behind_block = guardian.g_detras(MOTOR, wrapper_case["question"], wrapper_texts)

    # Métricas binarias solo para etiquetas claras. Los ambiguos se mantienen en
    # una columna aparte y no se puntúan como FP/FN.
    clear = [x for x in profile_rows if x["gold"] != "ambiguo"]
    negatives = [x for x in clear if x["gold"] == "negativo"]
    positives = [x for x in clear if x["gold"] == "positivo"]
    flagged = lambda x: bool(x["flag"])
    fp = sum(flagged(x) for x in negatives)
    tp = sum(flagged(x) for x in positives)
    fn = len(positives) - tp
    tn = len(negatives) - fp

    bias_rows = []
    for pid, masc, fem in BIAS_PAIRS:
        a, b = behind.filtrar(masc), behind.filtrar(fem)
        bias_rows.append({
            "id": pid, "masculine": masc, "feminine": fem,
            "masculine_flag": a.get("bandera"), "feminine_flag": b.get("bandera"),
            "masculine_n": a.get("n_perfilamiento", 0),
            "feminine_n": b.get("n_perfilamiento", 0),
            "different": (a.get("bandera"), a.get("n_perfilamiento")) !=
                         (b.get("bandera"), b.get("n_perfilamiento")),
        })

    ambiguity_rows = []
    for cid, gold_issue, text in AMBIGUITY_CASES:
        r = copi.analizar_texto([text])
        profile = behind.filtrar(text)
        ambiguity_rows.append({
            "id": cid, "gold_issue": gold_issue, "text": text,
            "profile_flag": profile.get("bandera"),
            "profile_marks": profile.get("marcajes", []),
            "copi_ambiguity_marked": any("AMBIGUO" in m.get("tipo", "") for m in r.get("marcas", [])),
            "causals": r.get("causales", []),
            "arguments": r.get("argumentos", []),
            "marks": r.get("marcas", []),
            "ambiguous_atoms": [m for m in r.get("marcas", []) if "AMBIGUO" in m.get("tipo", "")],
            "consistent": r.get("consistentes"),
        })

    # Muestra también la salida de Copi sobre cada oración perfilada: una
    # objeción no se interpreta automáticamente como falsedad del texto.
    copi_profile = []
    for cid, gold, text in PROFILE_CASES:
        r = copi.analizar_texto([text])
        copi_profile.append({"id": cid, "gold": gold, "marks": r.get("marcas", []),
                             "ambiguous_atoms": [m for m in r.get("marcas", []) if "AMBIGUO" in m.get("tipo", "")]})

    report = {
        "protocol": "POE-U6_DIAGNOSTICO_LINGUISTICO_V0.2",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "clasificadores lingüísticos reales; no predictor ni evaluación de desenlaces",
        "versions": {"pregunta_detras": behind.VERSION, "copi": copi.VERSION,
                     "guardianes": guardian.VERSION},
        "profile_detection": {
            "n_total": len(profile_rows), "n_clear": len(clear),
            "n_negative": len(negatives), "n_positive": len(positives),
            "n_ambiguous_excluded_from_binary_metrics": len(profile_rows) - len(clear),
            "tp": tp, "fp": fp, "tn": tn, "fn": fn,
            "precision": tp / (tp + fp) if tp + fp else None,
            "recall": tp / (tp + fn) if tp + fn else None,
            "false_positive_rate": fp / (fp + tn) if fp + tn else None,
            "rows": profile_rows,
        },
        "actual_guardian_wrapper": behind_block,
        "gender_counterfactuals": {
            "n_pairs": len(bias_rows),
            "n_different": sum(x["different"] for x in bias_rows),
            "pairs": bias_rows,
        },
        "ambiguity_and_argumentation": {
            "n_cases": len(ambiguity_rows), "cases": ambiguity_rows,
            "copi_profile_crosscheck": copi_profile,
        },
        "interpretation_rules": [
            "Las etiquetas gold se fijaron antes de observar salidas.",
            "Los casos ambiguos no se cuentan como FP ni FN.",
            "Una marca no equivale a falsedad ni activa bloqueo por sí sola.",
            "Las diferencias de pares mínimos se reportan como asimetrías observadas, no como prueba automática de sesgo.",
            "Las métricas describen este corpus controlado, no toda la lengua ni toda la población de casos.",
        ],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "artifact": str(OUT),
        "versions": report["versions"],
        "profile_metrics": {k: report["profile_detection"][k] for k in
                            ("n_total", "n_clear", "n_negative", "n_positive",
                             "n_ambiguous_excluded_from_binary_metrics", "tp", "fp", "tn", "fn",
                             "precision", "recall", "false_positive_rate")},
        "gender_pairs_different": report["gender_counterfactuals"]["n_different"],
        "ambiguity_cases": len(ambiguity_rows),
        "guardian_wrapper_flag": behind_block.get("bandera"),
    }, ensure_ascii=False, indent=2))
    return report


if __name__ == "__main__":
    run()
