#!/usr/bin/env python3
"""Construye las 3 entradas heroe (7 cortes c/u) en formato CAL actual.

Juana de Arco (heroe tragico), Harriet Tubman (heroe generativo),
Nelson Mandela (heroe generativo). Hechos de la biografia establecida;
fechas de corte aproximadas (punto medio del rango del hecho).
Tokens crudos del vocabulario ya validado en las entradas vigentes
(Napoleon/Noether/Carson). SIN puente Caldero placeholder.
El desenlace va SOLO en source_notes, nunca en la entrada.
"""
import json
from pathlib import Path

BASE = Path("/home/hatch/workspace/u6-alterno/motor-cameo/casos/precedentes")

CASOS = {
    "JUANA_DE_ARCO_HEROE_20261112": {
        "case_id": "JUANA_DE_ARCO_HEROE_20261112",
        "sujeto": "Juana de Arco",
        "z_work": "C7_1430", "freeze": "1430-12-01",
        "desenlace_sellado": "Juicio en Ruan; condenada por herejia y quemada el 30-may-1431. Rehabilitada 1456; canonizada 1920. Final tragico.",
        "cortes": [
            ("C1_1418", "1418-01-01", "Nace hacia 1412 en Domremy (Lorena), hija de campesinos acomodados. Infancia en el campo: cuida el ganado, reza, trabaja en casa. Hacia los 13 anos empieza a oir voces que identifica con santos.",
             ["aprendizaje", "conocimiento", "curiosidad_abstracta", "rutina", "cotidiano"],
             ["creatividad", "reflexion", "claridad"],
             ["identidad_impuesta", "autoridad", "jerarquia", "estabilidad"]),
            ("C2_1429_02", "1429-02-01", "En 1428-1429 viaja a Vaucouleurs y convence a Robert de Baudricourt de llevarla ante el delfin. Llega a Chinon en febrero de 1429 y se encuentra con Carlos, a quien reconoce entre la corte.",
             ["audacia", "desafio_autoridad", "independencia", "proposito_claro", "oportunidad"],
             ["liderazgo", "reflexion", "vision"],
             ["autoridad", "jerarquia", "restriccion_iniciativa", "incertidumbre"]),
            ("C3_1429_05", "1429-05-08", "En mayo de 1429 levanta el sitio de Orleans en nueve dias, con el ejercito frances. Es herida por una flecha en el cuello y vuelve al combate. La ciudad la celebra.",
             ["victoria", "liderazgo", "audacia", "logro_personal", "reconocimiento"],
             ["creatividad", "esfuerzo_sostenido_reciente", "generacion_ideas"],
             ["amenaza_central", "crisis_abrupta", "exposicion_trauma_ajeno", "obstaculo"]),
            ("C4_1429_07", "1429-07-17", "En junio-julio de 1429 gana en Jargeau y Patay. El 17 de julio de 1429 Carlos VII es coronado en Reims con Juana a su lado con el estandarte. Es el punto mas alto de su mision.",
             ["victoria", "reconocimiento", "poder", "logro_personal", "estatus_social"],
             ["liderazgo", "vision", "redes_prestigio"],
             ["autoridad", "jerarquia", "estabilidad", "popularidad"]),
            ("C5_1429_11", "1429-11-01", "En septiembre de 1429 fracasa el asalto a Paris; es herida en el muslo. En los meses siguientes dirige campanas menores y la corte empieza a apartarla de las decisiones.",
             ["frustracion", "obstaculo", "bloqueo", "esfuerzo_sostenido_reciente", "resistencia_cambio"],
             ["reflexion", "incertidumbre", "preocupacion_futuro"],
             ["restriccion_iniciativa", "rivalidad_profesional", "ira_institucional", "discrecion"]),
            ("C6_1430_05", "1430-05-23", "El 23 de mayo de 1430 es capturada en Compiegne por tropas borgoñonas al intentar levantar el sitio. La venden a los ingleses, que la trasladan a Ruan para juzgarla.",
             ["persecucion", "vulnerabilidad", "perdida_familiar", "duelo", "sacrificio"],
             ["oposicion", "injusticia", "conciencia_problema"],
             ["prohibicion", "amenaza_central", "crisis_abrupta", "bloqueo"]),
            ("C7_1430", "1430-12-01", "Prisionera en Ruan durante el otoño de 1430. Comienza el proceso eclesiastico en su contra, dirigido por el obispo Cauchon, con interrogatorios sobre sus voces, su ropa de hombre y su mision.",
             ["persecucion", "injusticia", "sacrificio", "busqueda_verdad", "compromiso"],
             ["reflexion", "claridad", "conciencia_problema"],
             ["autoridad", "jerarquia", "prohibicion", "demanda_psicosocial_institucional"]),
        ],
    },
    "TUBMAN_HEROE_20261112": {
        "case_id": "TUBMAN_HEROE_20261112",
        "sujeto": "Harriet Tubman",
        "z_work": "C7_1902", "freeze": "1904-01-01",
        "desenlace_sellado": "Muere el 10-mar-1913 en Auburn, honrada por el ejercito y por el pais; su obra (el ferrocarril subterraneo, la lucha por la libertad) perdura. Final generativo.",
        "cortes": [
            ("C1_1833", "1833-01-01", "Nace hacia 1822 esclavizada en el condado de Dorchester, Maryland. Infancia de trabajo forzado en el campo y en casas; de adolescente sufre un golpe en la cabeza que le deja secuelas de por vida. Hacia 1844 se casa con John Tubman, hombre libre.",
             ["aprendizaje", "conocimiento", "curiosidad_abstracta", "rutina", "cotidiano"],
             ["resistencia_cambio", "reflexion", "claridad"],
             ["identidad_impuesta", "autoridad", "jerarquia", "restriccion_iniciativa"]),
            ("C2_1849", "1849-09-01", "En septiembre de 1849, tras la muerte de su amo, huye sola a Filadelfia. Decide volver al sur a rescatar a su familia, aunque la Ley de Esclavos Fugitivos hace la huida mas peligrosa.",
             ["audacia", "independencia", "proposito_claro", "sacrificio", "oportunidad"],
             ["liderazgo", "vision", "reflexion"],
             ["amenaza_central", "crisis_abrupta", "incertidumbre", "obstaculo"]),
            ("C3_1853", "1853-01-01", "Entre 1850 y 1857 se vuelve conductora del Ferrocarril Subterraneo: hace unos trece viajes al sur y rescata a unas setenta personas. Gana el apodo de Moises; nunca pierde un pasajero.",
             ["liderazgo", "logro_personal", "reconocimiento", "esfuerzo_sostenido_reciente", "victoria"],
             ["creatividad", "generacion_ideas", "transmision_saber"],
             ["amenaza_central", "exposicion_trauma_ajeno", "riesgo", "obstaculo"]),
            ("C4_1859", "1859-01-01", "En 1858 conoce a John Brown y lo apoya. Sigue rescatando gente; la Ley de Esclavos Fugitivos de 1850 la obliga a llevar a los fugados hasta Canada. Su red se extiende y su nombre se vuelve legendario.",
             ["audacia", "liderazgo", "reconocimiento", "alianza", "proposito_claro"],
             ["vision", "apoyo_activo", "reflexion"],
             ["autoridad", "prohibicion", "amenaza_central", "injusticia"]),
            ("C5_1862", "1862-06-01", "Durante la Guerra Civil sirve a la Union como enfermera, cocinera y espia. En junio de 1863 guia la incursion del rio Combahee, que libera a unas setecientas personas esclavizadas.",
             ["victoria", "liderazgo", "sacrificio", "logro_personal", "reconocimiento"],
             ["creatividad", "transmision_saber", "esfuerzo_sostenido_reciente"],
             ["crisis_abrupta", "exposicion_trauma_ajeno", "amenaza_central", "carga_familiar"]),
            ("C6_1875", "1875-01-01", "Despues de la guerra se instala en una granja en Auburn, Nueva York. Lucha por el sufragio femenino junto a Susan B. Anthony y dedica su vida a cuidar a pobres, ancianos y huerfanos.",
             ["compromiso", "cuidado_cercanos", "generatividad", "sabiduria_compartida", "mentoria_activa"],
             ["reflexion", "estabilidad", "transmision_saber"],
             ["estabilidad_ocupacional", "estabilidad_ingreso_formal", "rutina", "cotidiano"]),
            ("C7_1902", "1902-01-01", "Anciana en Auburn, hacia 1902 vive reconocida por su comunidad, sigue cuidando a quienes llegan a su casa y prepara un hogar para ancianos e indigentes. Su salud declina pero su autoridad moral crece.",
             ["sabiduria_compartida", "generatividad", "reconocimiento", "cuidado_cercanos", "estabilidad"],
             ["reflexion", "mentoria_activa", "transmision_saber"],
             ["cronicidad_sintomatica", "rutina", "cotidiano", "estabilidad"]),
        ],
    },
    "MANDELA_HEROE_20261112": {
        "case_id": "MANDELA_HEROE_20261112",
        "sujeto": "Nelson Mandela",
        "z_work": "C7_1997", "freeze": "2004-01-01",
        "desenlace_sellado": "Muere el 5-dic-2013 en Johannesburgo, con funeral de Estado y duelo mundial; su legado (reconciliacion, fin del apartheid) perdura. Final generativo.",
        "cortes": [
            ("C1_1931", "1931-01-01", "Nace el 18 de julio de 1918 en Mvezo, Transkei, del clan thembu. Estudia en Fort Hare, de donde es expulsado por protestar. Se muda a Johannesburgo, se hace abogado y en 1944 se une al Congreso Nacional Africano y funda su Liga Juvenil.",
             ["aprendizaje", "conocimiento", "curiosidad_abstracta", "logro_escolar", "oportunidad"],
             ["reflexion", "claridad", "busqueda_identidad"],
             ["autoridad", "jerarquia", "identidad_impuesta", "restriccion_iniciativa"]),
            ("C2_1948", "1948-01-01", "Entre 1944 y 1952 lidera la Campana de Desafio contra las leyes injustas y es acusado en el Juicio por Traicion (1956-1961), del que sale absuelto. Se vuelve el rostro de la resistencia no violenta.",
             ["liderazgo", "desafio_autoridad", "audacia", "reconocimiento", "proposito_claro"],
             ["vision", "reflexion", "alianza"],
             ["autoridad", "prohibicion", "injusticia", "amenaza_central"]),
            ("C3_1961", "1961-01-01", "Tras la masacre de Sharpeville (1960) concluye que la resistencia pacifica ya no basta y funda Umkhonto we Sizwe, el brazo armado. En 1962 es arrestado y condenado a cinco anos.",
             ["audacia", "desafio_autoridad", "sacrificio", "liderazgo", "ruptura_barrera"],
             ["vision", "generacion_ideas", "oposicion"],
             ["crisis_abrupta", "amenaza_central", "prohibicion", "ira_institucional"]),
            ("C4_1964", "1964-06-01", "En el Juicio de Rivonia (1963-1964) es condenado a cadena perpetua. En su discurso declara estar dispuesto a morir por el ideal de una sociedad democratica y libre. Lo trasladan a Robben Island.",
             ["sacrificio", "compromiso", "busqueda_verdad", "proposito_claro", "persecucion"],
             ["reflexion", "claridad", "conciencia_problema"],
             ["autoridad", "jerarquia", "prohibicion", "crisis_abrupta"]),
            ("C5_1973", "1973-01-01", "Pasa dieciocho anos en Robben Island picando piedra y rompiendo caliza. Estudia, escribe, organiza a los presos y se convierte en la figura moral del movimiento, mientras afuera su nombre crece.",
             ["esfuerzo_sostenido_reciente", "sacrificio", "aprendizaje", "resistencia_cambio", "estabilidad"],
             ["reflexion", "transmision_saber", "mentoria_activa"],
             ["restriccion_iniciativa", "rutina", "cotidiano", "bloqueo"]),
            ("C6_1986", "1986-01-01", "En 1982 lo trasladan a Pollsmoor. Desde ahi inicia negociaciones secretas con el gobierno. El 11 de febrero de 1990 sale libre ante las camaras del mundo, despues de 27 anos preso.",
             ["victoria", "liderazgo", "reconocimiento", "alianza", "vision"],
             ["reflexion", "generacion_ideas", "claridad"],
             ["incertidumbre", "preocupacion_futuro", "oportunidad", "estabilidad"]),
            ("C7_1997", "1997-01-01", "Negocia el fin del apartheid, gana el Premio Nobel de la Paz en 1993 y es elegido presidente en 1994, el primero por voto universal. Gobierna hasta 1999, se retira y se vuelve anciano estadista mundial.",
             ["victoria", "liderazgo", "reconocimiento", "generatividad", "poder"],
             ["vision", "transmision_saber", "sabiduria_compartida"],
             ["estabilidad", "rutina", "popularidad", "estabilidad_ocupacional"]),
        ],
    },
}

W = {"P": [0.80, 0.78, 0.76, 0.74, 0.70], "A": [0.70, 0.68, 0.66], "C": [0.72, 0.70, 0.68, 0.66]}
TIPO = {"JUANA_DE_ARCO_HEROE_20261112": "politico",
        "TUBMAN_HEROE_20261112": "politico",
        "MANDELA_HEROE_20261112": "politico"}
for dirname, c in CASOS.items():
    cuts = []
    for cid, date, hecho, p, a, cc in c["cortes"]:
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
        "tipo_sujeto": TIPO[dirname],
        "z_work_kind": "CASE_CUTOFF",
        "z_work_date": c["z_work"],
        "freeze": c["freeze"],
        "random_seed": 20261112,
        "source_notes": (
            "Heroe (matriz de finales por arquetipo, orden de Marco 2026-11-12). "
            "7 cortes; fechas aproximadas (punto medio del rango del hecho). "
            "Desenlace sellado (NO en la entrada, solo aqui): " + c["desenlace_sellado"]),
        "cuts": cuts,
    }
    d = BASE / dirname
    d.mkdir(parents=True, exist_ok=True)
    (d / "entrada.json").write_text(json.dumps(entrada, ensure_ascii=False, indent=2), encoding="utf-8")
    print("escrita:", d / "entrada.json", "| cortes:", len(cuts))
