#!/usr/bin/env python3
"""Heroes sin trono (7 cortes c/u): Semmelweis y Kolbe.

Prueba limpia: NINGUN token de trono (sin liderazgo, autoridad, poder,
vision, reconocimiento, estatus). Tokens del heroe: valentia,
defensa_debil, valor, sacrificio, persecucion — los favor de
heroe / arquetipo_el_heroe en el catalogo. Si el motor sigue coronando
gobernante/rey sin esos tokens, la trampa es estructural; si corona
al heroe, era el peso de los tokens.

Excepcion declarada (Kolbe): su acto heroico cae en el ultimo 10% de
su vida (ofrecerse en julio de 1941, muere agosto 1941). Se incluye
igual porque la pregunta es de tokens->H1, no de prediccion ciega.
Semmelweis si respeta Z90 (su acto es de 1847, muere 1865).
"""
import json
from pathlib import Path

BASE = Path("/home/hatch/workspace/u6-alterno/motor-cameo/casos/precedentes")

CASOS = {
    "SEMMELWEIS_HEROE_SIN_TRONO_20261112": {
        "case_id": "SEMMELWEIS_HEROE_SIN_TRONO_20261112",
        "sujeto": "Ignaz Semmelweis",
        "tipo": "cientifico",
        "z_work": "C7_1861", "freeze": "1861-06-01",
        "desenlace_sellado": "Internado en un asilo en 1865; muere el 13-ago-1865 por infeccion de una herida. Reivindicado tras su muerte (Lister, teoria germinal): 'salvador de las madres'. Heroe tragico, generativo tras la muerte.",
        "cortes": [
            ("C1_1831", "1831-01-01", "Nace en 1818 en Buda, Hungria. Estudia medicina en Viena y en 1846 se vuelve asistente en la clinica de maternidad del Hospital General de Viena.",
             ["aprendizaje", "conocimiento", "curiosidad_abstracta", "logro_escolar", "oportunidad"],
             ["reflexion", "claridad", "busqueda_identidad"],
             ["rutina", "cotidiano", "estabilidad", "identidad_impuesta"]),
            ("C2_1846", "1846-06-01", "Nota que la primera clinica, atendida por medicos, tiene mucha mas mortalidad materna por fiebre puerperal que la segunda, atendida por parteras. Empieza a investigar la diferencia.",
             ["busqueda_verdad", "conocimiento", "analisis", "analisis_objetivo", "curiosidad_abstracta"],
             ["reflexion", "conciencia_problema", "claridad"],
             ["incertidumbre", "obstaculo", "preocupacion_futuro", "estabilidad"]),
            ("C3_1847", "1847-05-01", "Descubre que el lavado de manos con solucion de cal clorada antes de atender partos baja la mortalidad de alrededor de 18% a alrededor de 2%. Lo impone en su clinica.",
             ["hallazgo", "valor", "valentia", "defensa_debil", "generacion_ideas"],
             ["creatividad", "esfuerzo_sostenido_reciente", "transmision_saber"],
             ["resistencia_cambio", "obstaculo", "exposicion_trauma_ajeno", "crisis_abrupta"]),
            ("C4_1849", "1849-01-01", "Presenta sus resultados ante el estamento medico, que lo rechaza y se burla. Pierde su puesto en 1849 y deja Viena. Sigue defendiendo el lavado de manos por escrito.",
             ["valentia", "defensa_debil", "compromiso", "busqueda_verdad", "frustracion"],
             ["oposicion", "injusticia", "conciencia_problema"],
             ["ira_institucional", "prohibicion", "restriccion_iniciativa", "bloqueo"]),
            ("C5_1852", "1852-01-01", "Vuelve a Budapest y trabaja en el hospital de San Roque. Sigue con el lavado de manos y la mortalidad se mantiene baja. Escribe cartas a medicos de Europa defendiendo su metodo.",
             ["esfuerzo_sostenido_reciente", "compromiso", "defensa_debil", "transmision_saber", "generatividad"],
             ["reflexion", "mentoria_activa", "claridad"],
             ["rutina", "cotidiano", "estabilidad", "discrecion"]),
            ("C6_1858", "1858-01-01", "Publica su libro en 1861, 'La etiologia, el concepto y la profilaxis de la fiebre puerperal'. El estamento lo ridiculiza. Se amarga, escribe cartas furiosas y se aisla cada vez mas.",
             ["valentia", "compromiso", "busqueda_verdad", "sacrificio", "frustracion"],
             ["reflexion", "incertidumbre", "preocupacion_futuro"],
             ["ira_institucional", "bloqueo", "restriccion_iniciativa", "rivalidad_profesional"]),
            ("C7_1861", "1861-06-01", "Aislado y con la salud mental deteriorada tras anos de rechazo. Su libro no cambia nada en vida. Es el punto final de su lucha publica por el lavado de manos.",
             ["sacrificio", "valentia", "defensa_debil", "persecucion", "duelo"],
             ["reflexion", "claridad", "conciencia_problema"],
             ["cronicidad_sintomatica", "vulnerabilidad", "bloqueo", "discrecion"]),
        ],
    },
    "KOLBE_HEROE_SIN_TRONO_20261112": {
        "case_id": "KOLBE_HEROE_SIN_TRONO_20261112",
        "sujeto": "Maximiliano Kolbe",
        "tipo": "politico",
        "z_work": "C7_1941", "freeze": "1941-08-01",
        "desenlace_sellado": "Canonizado en 1982 ('martir de la caridad'); Gajowniczek sobrevive a la guerra. Heroe tragico, generativo tras la muerte.",
        "cortes": [
            ("C1_1904", "1904-01-01", "Nace en 1894 en Zdunska Wola, Polonia. A los 16 anos entra en los franciscanos. Estudia en Roma y se ordena sacerdote en 1918.",
             ["aprendizaje", "conocimiento", "curiosidad_abstracta", "logro_escolar", "oportunidad"],
             ["reflexion", "claridad", "busqueda_identidad"],
             ["rutina", "cotidiano", "estabilidad", "identidad_impuesta"]),
            ("C2_1918", "1918-01-01", "En 1917 funda la Milicia de la Inmaculada, un movimiento de evangelizacion por la prensa. Se ordena sacerdote en 1918 y vuelve a Polonia.",
             ["compromiso", "proposito_claro", "generacion_ideas", "transmision_saber", "creatividad"],
             ["claridad", "reflexion", "alianza"],
             ["estabilidad", "rutina", "incertidumbre", "oportunidad"]),
            ("C3_1927", "1927-01-01", "Funda el monasterio de Niepokalanow en 1927, un centro editorial catolico que crece hasta unos setecientos frailes. Publica revistas y libros.",
             ["esfuerzo_sostenido_reciente", "compromiso", "generatividad", "transmision_saber", "cuidado_cercanos"],
             ["creatividad", "mentoria_activa", "reflexion"],
             ["estabilidad", "rutina", "cotidiano", "estabilidad_ocupacional"]),
            ("C4_1933", "1933-01-01", "Hace obra misionera en Japon entre 1930 y 1936 y vuelve a Polonia. Niepokalanow sigue creciendo como centro de fe y de prensa.",
             ["compromiso", "generatividad", "sabiduria_compartida", "cuidado_cercanos", "empatia"],
             ["reflexion", "transmision_saber", "mentoria_activa"],
             ["estabilidad", "rutina", "cotidiano", "estabilidad_ocupacional"]),
            ("C5_1941_02", "1941-02-01", "Segunda Guerra Mundial: la Gestapo lo arresta en febrero de 1941 y en mayo lo mandan a Auschwitz como prisionero 16670. Trabaja y reza entre los presos.",
             ["persecucion", "injusticia", "vulnerabilidad", "compromiso", "cuidado_cercanos"],
             ["oposicion", "conciencia_problema", "reflexion"],
             ["amenaza_central", "crisis_abrupta", "prohibicion", "bloqueo"]),
            ("C6_1941_07", "1941-07-01", "En Auschwitz un prisionero escapa y las SS eligen a diez hombres para morir de hambre. Kolbe se ofrece a tomar el lugar de Franciszek Gajowniczek, padre de familia.",
             ["sacrificio", "valor", "valentia", "defensa_debil", "compromiso"],
             ["reflexion", "claridad", "conciencia_problema"],
             ["amenaza_central", "crisis_abrupta", "exposicion_trauma_ajeno", "carga_familiar"]),
            ("C7_1941", "1941-08-01", "Pasa dos semanas en el bunker de hambre, rezando con los demas condenados. Lo matan con una inyeccion letal el 14 de agosto de 1941.",
             ["sacrificio", "valentia", "defensa_debil", "persecucion", "duelo"],
             ["reflexion", "claridad", "conciencia_problema"],
             ["vulnerabilidad", "cronicidad_sintomatica", "bloqueo", "amenaza_central"]),
        ],
    },
}

W = {"P": [0.80, 0.78, 0.76, 0.74, 0.70], "A": [0.70, 0.68, 0.66], "C": [0.72, 0.70, 0.68, 0.66]}
# Verificacion: ningun token de trono en las entradas.
TRONO = {"liderazgo", "autoridad", "poder", "vision", "reconocimiento", "estatus_social", "popularidad", "redes_prestigio", "jerarquia"}
for dirname, c in CASOS.items():
    cuts = []
    for cid, date, hecho, p, a, cc in c["cortes"]:
        for t in p + a + cc:
            assert t not in TRONO, f"token de trono {t} en {cid}"
        cuts.append({
            "id": cid, "date": date, "hecho": hecho,
            "P": [[t, W["P"][i]] for i, t in enumerate(p)],
            "A": [[t, W["A"][i]] for i, t in enumerate(a)],
            "C": [[t, W["C"][i]] for i, t in enumerate(cc)],
        })
    entrada = {
        "case_id": c["case_id"],
        "person": c["sujeto"],
        "question": "¿Qué configuración dinámica se perfila en %s a partir de una selección de hitos biográficos, usando solo evidencia hasta Z90?" % c["sujeto"],
        "tipo_sujeto": c["tipo"],
        "z_work_kind": "CASE_CUTOFF",
        "z_work_date": c["z_work"],
        "freeze": c["freeze"],
        "random_seed": 20261112,
        "source_notes": (
            "Heroe sin trono (matriz de finales por arquetipo, orden de Marco 2026-11-12). "
            "7 cortes; fechas aproximadas (punto medio del rango del hecho). "
            "SIN tokens de trono (sin liderazgo/autoridad/poder/vision/reconocimiento/estatus). "
            "Desenlace sellado (NO en la entrada, solo aqui): " + c["desenlace_sellado"]),
        "cuts": cuts,
    }
    d = BASE / dirname
    d.mkdir(parents=True, exist_ok=True)
    (d / "entrada.json").write_text(json.dumps(entrada, ensure_ascii=False, indent=2), encoding="utf-8")
    print("escrita:", d / "entrada.json", "| cortes:", len(cuts), "| sin trono: OK")
