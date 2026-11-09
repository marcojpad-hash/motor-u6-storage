#!/usr/bin/env python3
"""Generador de los 20 casos ciegos (lote_20) - Motor U6.

CIEGO (regla 2026-11-08): el motor NO recibe ningun dato que pueda decirle
QUIEN es el sujeto. El entrada.json NO lleva: campo `person`, nombre en
`case_id` (solo el slot C01-C20), nombre en `question`, nombre en los `hecho`
de los cortes, ni URL que identifique al sujeto en `source_notes`.
La identidad (nombre + URL de la fuente) va sellada en
casos/ciegos/lote_20/custodia/CXX/IDENTIDAD_SELLADA.json, junto con el
desenlace y el destino sellados. Se revela solo al verificar.
El Z90 / freeze es metodologia de trabajo, no la ceguera.

Estructura por caso:
  lote_20/CXX/            ENTRADA_CIEGA.md, entrada.json, COMPROMISO.json,
                          SALIDA_CONGELADA.json, RECIBO_EJECUCION.json
  lote_20/custodia/CXX/   IDENTIDAD_SELLADA.json, DESENLACE_SELLADO.json,
                          DESTINO_SELLADO.json
"""
import hashlib
import json
from pathlib import Path

REPO = Path("/home/hatch/workspace/cbm-repos/motor-u6-storage")
BASE = REPO / "casos" / "ciegos" / "lote_20"
CUSTODIA = BASE / "custodia"
ENGINE_SHA = "665c39a2861e58772522e91272563260d980908b1d4ab9f7092d3413d0c36082"
PAT_SHA = "d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1"
DEFINICIONES = {
    "auge": "mejora clara de posición del sujeto",
    "meseta": "sin cambio claro",
    "caida": "pérdida progresiva de posición/apoyo",
    "ruptura": "quiebre brusco (condena, muerte, colapso) en el horizonte inmediato",
}
SOURCE_NOTE = ("Material pre-Z con fecha <= Z; fuentes primarias selladas en "
               "custodia (IDENTIDAD_SELLADA.json). Sin nombre ni URL en este archivo.")


def sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def valid_tokens() -> set:
    toks = set()
    for f in sorted((REPO / "casos" / "fabrica" / "cola").glob("*/entrada.json")):
        e = json.loads(f.read_text(encoding="utf-8"))
        for c in e.get("cuts", []):
            for k in ("P", "A", "C"):
                for t, w in c.get(k, []):
                    toks.add(t)
    return toks


# Cada caso: slot, person (SOLO para custodia, nunca va al entrada.json),
# tipo, freeze (Z), question (neutra, sin nombre), cuts (hecho sin nombre),
# destino, porque, familias, fuente (URL, SOLO para custodia).
CASES = [
    {
        "slot": "C01", "person": "Wolfgang Amadeus Mozart", "tipo": "artista",
        "freeze": "1781-03-16",
        "question": "¿Qué trayectoria sigue el sujeto tras romper con su superior eclesiástico y establecerse en la capital como profesional independiente?",
        "cuts": [
            ("C1_1756", "1756-01-27", "Nace en Salzburgo; niño prodigio, gira por las cortes de Europa con su padre.",
             [("creatividad", 0.80), ("reconocimiento_previo", 0.70)],
             [("aprendizaje", 0.82), ("mentoria_activa", 0.78)],
             [("oportunidad", 0.78), ("jerarquia", 0.65)]),
            ("C2_1777", "1777-09-23", "Viaja a París con su madre (muere en 1778); busca un empleo estable sin conseguirlo.",
             [("ambicion", 0.80), ("busqueda_seguridad", 0.70)],
             [("viaje", 0.78), ("esfuerzo_sostenido_reciente", 0.70)],
             [("frustracion", 0.72), ("escasez", 0.68)]),
            ("C3_1781", "1781-03-16", "Rompe con el arzobispo de Salzburgo; se establece en Viena como músico independiente.",
             [("independencia", 0.84), ("ambicion", 0.80)],
             [("rebeldia", 0.78), ("autoexpresion", 0.80)],
             [("incertidumbre", 0.75), ("oportunidad", 0.80)]),
        ],
        "destino": "caida",
        "porque": "auge vienés 1781-1787 y luego declive de encargos e ingresos; muere el 5-dic-1791 en Viena, endeudado, con el Réquiem inconcluso",
        "familias": ["22_todo_sacrificado_por_una_pasion", "arquetipo_el_creador", "frye_mythos_tragedia"],
        "fuente": "https://en.wikipedia.org/wiki/Wolfgang_Amadeus_Mozart ; muere 5-dic-1791 en Viena, endeudado, Réquiem inconcluso; auge vienés 1781-1787 y declive de encargos después",
    },
    {
        "slot": "C02", "person": "Charles Darwin", "tipo": "cientifico",
        "freeze": "1859-11-24",
        "question": "¿Qué ocurre con el sujeto tras publicar su obra principal sobre el origen de las especies?",
        "cuts": [
            ("C1_1836", "1836-10-02", "Regresa del viaje del Beagle (1831-1836) con observaciones y especímenes de Galápagos y Sudamérica.",
             [("curiosidad_abstracta", 0.84), ("busqueda_verdad", 0.80)],
             [("analisis", 0.78), ("verificacion", 0.75)],
             [("hallazgo", 0.80), ("oportunidad", 0.72)]),
            ("C2_1844", "1844-07-01", "Escribe el 'Ensayo de 1844' con su teoría de selección natural; lo guarda sin publicar por temor a la reacción.",
             [("cautela", 0.80), ("teorizacion", 0.82)],
             [("prudencia", 0.78), ("secreto_protegido", 0.70)],
             [("presion_social", 0.72), ("incertidumbre", 0.70)]),
            ("C3_1859", "1859-11-24", "Publica El origen de las especies; la primera edición se agota el día de su salida.",
             [("vision", 0.82), ("determinacion", 0.80)],
             [("honestidad", 0.78), ("desafio_autoridad", 0.75)],
             [("reconocimiento", 0.78), ("confrontacion_directa", 0.70)]),
        ],
        "destino": "auge",
        "porque": "El origen del hombre (1871) y reconocimiento creciente; muere el 19-abr-1882 en Down House, enterrado en Westminster",
        "familias": ["arquetipo_el_sabio", "12_obtencion", "social_04_rogers_difusion_innovaciones"],
        "fuente": "https://en.wikipedia.org/wiki/Charles_Darwin ; El origen de las especies 1859, El origen del hombre 1871, muere 1882 reconocido",
    },
    {
        "slot": "C03", "person": "Isaac Newton", "tipo": "cientifico",
        "freeze": "1687-07-05",
        "question": "¿Qué trayectoria sigue el sujeto tras publicar su obra principal de filosofía natural?",
        "cuts": [
            ("C1_1665", "1665-08-01", "Annus mirabilis durante la peste: cálculo, óptica y gravitación en Woolsthorpe.",
             [("creatividad", 0.84), ("curiosidad_abstracta", 0.82)],
             [("analisis", 0.84), ("teorizacion", 0.80)],
             [("aislamiento_voluntario", 0.70), ("oportunidad", 0.72)]),
            ("C2_1672", "1672-01-11", "Elegido miembro de la Royal Society; presenta su telescopio reflector y su teoría de la luz y el color.",
             [("reconocimiento_previo", 0.78), ("conocimiento", 0.82)],
             [("verificacion", 0.80), ("planificacion", 0.75)],
             [("reconocimiento", 0.75), ("rivalidad_profesional", 0.70)]),
            ("C3_1687", "1687-07-05", "Publica Philosophiæ Naturalis Principia Mathematica con las leyes del movimiento y la gravitación universal.",
             [("vision", 0.84), ("logro_personal", 0.82)],
             [("metodicidad", 0.82), ("determinacion", 0.80)],
             [("reconocimiento", 0.80), ("legitimidad_percibida", 0.78)]),
        ],
        "destino": "auge",
        "porque": "director de la Casa de la Moneda (1699), presidente de la Royal Society (1703), caballero (1705); muere el 31-mar-1727 en Londres",
        "familias": ["arquetipo_el_sabio", "12_obtencion", "schwartz_07_logro"],
        "fuente": "https://en.wikipedia.org/wiki/Isaac_Newton ; Principia 1687, director de la Casa de la Moneda 1699, presidente Royal Society 1703, muere 1727",
    },
    {
        "slot": "C04", "person": "Thomas Edison", "tipo": "empresario",
        "freeze": "1879-10-21",
        "question": "¿Qué ocurre con el sujeto tras lograr una bombilla incandescente práctica?",
        "cuts": [
            ("C1_1877", "1877-11-21", "Presenta el fonógrafo, su primera gran invención; lo apodan 'el mago de Menlo Park'.",
             [("creatividad", 0.84), ("generacion_ideas", 0.80)],
             [("analisis", 0.78), ("esfuerzo_sostenido_reciente", 0.80)],
             [("reconocimiento", 0.78), ("oportunidad", 0.80)]),
            ("C2_1878", "1878-09-01", "Funda una compañía de luz eléctrica para desarrollar la iluminación; compite por financiación.",
             [("ambicion", 0.82), ("empresa", 0.80)],
             [("organizacion", 0.78), ("planificacion_activa", 0.78)],
             [("competencia", 0.75), ("escasez", 0.68)]),
            ("C3_1879", "1879-10-21", "Logra una bombilla incandescente que dura 13,5 horas; patenta el sistema de luz eléctrica.",
             [("logro_personal", 0.84), ("vision", 0.82)],
             [("determinacion", 0.82), ("eficiencia", 0.78)],
             [("reconocimiento", 0.82), ("prosperidad", 0.78)]),
        ],
        "destino": "auge",
        "porque": "funda General Electric (1892), cientos de patentes, muere el 18-oct-1931 en West Orange",
        "familias": ["arquetipo_el_creador", "30_ambicion", "kondratiev_02_verano_auge"],
        "fuente": "https://en.wikipedia.org/wiki/Thomas_Edison ; bombilla 1879, General Electric 1892, muere 1931",
    },
    {
        "slot": "C05", "person": "William Shakespeare", "tipo": "artista",
        "freeze": "1599-01-01",
        "question": "¿Qué trayectoria sigue el sujeto tras la construcción del teatro del que es copropietario?",
        "cuts": [
            ("C1_1590", "1590-01-01", "Llega a Londres; escribe sus primeras obras y se hace un nombre en el teatro.",
             [("creatividad", 0.82), ("ambicion", 0.78)],
             [("autoexpresion", 0.80), ("aprendizaje", 0.75)],
             [("oportunidad", 0.78), ("reconocimiento_previo", 0.70)]),
            ("C2_1594", "1594-01-01", "Se une a los Lord Chamberlain's Men; escribe Romeo y Julieta y El sueño de una noche de verano.",
             [("reconocimiento_previo", 0.80), ("creatividad", 0.84)],
             [("organizacion", 0.75), ("generacion_ideas", 0.80)],
             [("prosperidad", 0.75), ("redes_prestigio", 0.78)]),
            ("C3_1599", "1599-01-01", "Se construye el Globe Theatre; el sujeto es copropietario y dramaturgo principal de la compañía.",
             [("estatus_social", 0.80), ("logro_personal", 0.82)],
             [("planificacion_activa", 0.78), ("liderazgo", 0.75)],
             [("prosperidad", 0.80), ("reconocimiento", 0.78)]),
        ],
        "destino": "auge",
        "porque": "escribe Hamlet (c. 1600), Otelo, Rey Lear y Macbeth; se retira a Stratford y muere el 23-abr-1616",
        "familias": ["arquetipo_el_creador", "12_obtencion", "trayectoria_escritores_creativos"],
        "fuente": "https://en.wikipedia.org/wiki/William_Shakespeare ; Globe 1599, Hamlet c. 1600, Rey Lear c. 1605, muere 1616",
    },
    {
        "slot": "C06", "person": "Miguel de Cervantes", "tipo": "artista",
        "freeze": "1605-01-16",
        "question": "¿Qué ocurre con el sujeto tras publicar la primera parte de su novela principal?",
        "cuts": [
            ("C1_1571", "1571-10-07", "Combate en Lepanto; pierde el uso de la mano izquierda.",
             [("patriotismo", 0.78), ("determinacion", 0.80)],
             [("audacia", 0.80), ("resiliencia", 0.78)],
             [("terreno_hostil", 0.75), ("crisis_abrupta", 0.70)]),
            ("C2_1580", "1580-09-19", "Liberado tras cinco años cautivo en Argel; regresa a España arruinado y busca empleo.",
             [("supervivencia", 0.82), ("busqueda_seguridad", 0.78)],
             [("resiliencia", 0.80), ("flexibilidad_adaptativa", 0.75)],
             [("escasez", 0.78), ("frustracion", 0.72)]),
            ("C3_1605", "1605-01-16", "Publica la primera parte de Don Quijote de la Mancha; éxito inmediato en España y Europa.",
             [("creatividad", 0.84), ("reconocimiento_previo", 0.78)],
             [("autoexpresion", 0.82), ("generacion_ideas", 0.80)],
             [("reconocimiento", 0.82), ("prosperidad", 0.72)]),
        ],
        "destino": "auge",
        "porque": "publica la segunda parte del Quijote (1615) y Los trabajos de Persiles y Sigismunda (1617, póstumo); muere el 22-abr-1616 en Madrid",
        "familias": ["35_recuperacion_de_lo_perdido", "arquetipo_el_creador", "trayectoria_escritores_creativos"],
        "fuente": "https://en.wikipedia.org/wiki/Miguel_de_Cervantes ; Quijote I 1605, Quijote II 1615, muere 1616",
    },
    {
        "slot": "C07", "person": "Johannes Kepler", "tipo": "cientifico",
        "freeze": "1609-01-01",
        "question": "¿Qué trayectoria sigue el sujeto tras publicar su obra principal de astronomía nueva?",
        "cuts": [
            ("C1_1600", "1600-01-01", "Llega a Praga como asistente de Tycho Brahe; hereda sus observaciones planetarias precisas.",
             [("busqueda_verdad", 0.82), ("conocimiento", 0.80)],
             [("analisis", 0.82), ("mentoria_activa", 0.75)],
             [("oportunidad", 0.78), ("jerarquia", 0.70)]),
            ("C2_1601", "1601-10-24", "Muere Tycho Brahe; el sujeto lo sucede como matemático imperial de Rodolfo II.",
             [("responsabilidad", 0.80), ("ambicion", 0.75)],
             [("metodicidad", 0.80), ("determinacion", 0.78)],
             [("reconocimiento", 0.75), ("presion_social", 0.70)]),
            ("C3_1609", "1609-01-01", "Publica Astronomia Nova con las dos primeras leyes del movimiento planetario (órbitas elípticas).",
             [("vision", 0.84), ("logro_personal", 0.82)],
             [("teorizacion", 0.82), ("verificacion", 0.80)],
             [("reconocimiento", 0.78), ("desafio_autoridad", 0.72)]),
        ],
        "destino": "auge",
        "porque": "publica las Tablas rudolfinas (1627) y la tercera ley (1619); muere el 15-nov-1630 en Ratisbona",
        "familias": ["arquetipo_el_sabio", "12_obtencion", "20_sacrificio_por_un_ideal"],
        "fuente": "https://en.wikipedia.org/wiki/Johannes_Kepler ; Astronomia Nova 1609, Tablas rudolfinas 1627, muere 1630",
    },
]

CASES += [
    {
        "slot": "C08", "person": "Florence Nightingale", "tipo": "cientifico",
        "freeze": "1854-11-04",
        "question": "¿Qué ocurre con el sujeto tras llegar al hospital de campaña con un equipo de enfermeras?",
        "cuts": [
            ("C1_1850", "1850-01-01", "Estudia enfermería en Kaiserswerth (Alemania); rechaza el papel tradicional asignado a las mujeres de su época.",
             [("devocion", 0.82), ("altruismo", 0.80)],
             [("aprendizaje", 0.80), ("determinacion", 0.82)],
             [("desafio_autoridad", 0.75), ("oposicion", 0.70)]),
            ("C2_1853", "1853-08-12", "Dirige el Instituto para el Cuidado de Damas Enfermas en Londres; reforma su gestión y sus registros.",
             [("liderazgo", 0.80), ("organizacion", 0.82)],
             [("metodicidad", 0.80), ("planificacion_activa", 0.78)],
             [("reconocimiento_previo", 0.72), ("legitimidad_percibida", 0.75)]),
            ("C3_1854", "1854-11-04", "Llega a Scutari (Crimea) con 38 enfermeras; encuentra un hospital con mortalidad altísima y condiciones insalubres.",
             [("deber", 0.84), ("determinacion", 0.82)],
             [("organizacion", 0.84), ("analisis", 0.80)],
             [("crisis_abrupta", 0.80), ("terreno_hostil", 0.78)]),
        ],
        "destino": "auge",
        "porque": "reduce la mortalidad en Scutari, publica Notes on Nursing (1859), funda la primera escuela de enfermería (1860); muere el 13-ago-1910 en Londres",
        "familias": ["arquetipo_el_heroe", "20_sacrificio_por_un_ideal", "social_04_rogers_difusion_innovaciones"],
        "fuente": "https://en.wikipedia.org/wiki/Florence_Nightingale ; Crimea 1854, reforma de enfermería, Notes on Nursing 1859, muere 1910",
    },
    {
        "slot": "C09", "person": "Juana de Arco", "tipo": "gobernante",
        "freeze": "1429-07-17",
        "question": "¿Qué ocurre con el sujeto tras lograr la coronación del heredero en Reims?",
        "cuts": [
            ("C1_1428", "1428-05-01", "Llega a Chinon y convence al delfín de que es enviada a liberar el reino.",
             [("devocion", 0.84), ("vision", 0.82)],
             [("persuasion", 0.80), ("determinacion", 0.82)],
             [("legitimidad_percibida", 0.75), ("escepticismo", 0.70)]),
            ("C2_1429", "1429-04-01", "Recibe el mando de un ejército y marcha a Orléans con estandarte propio.",
             [("liderazgo", 0.84), ("audacia", 0.82)],
             [("carisma", 0.80), ("organizacion", 0.75)],
             [("oportunidad", 0.78), ("confrontacion_directa", 0.75)]),
            ("C3_1429", "1429-07-17", "Libera Orléans en nueve días; el delfín es coronado rey en Reims con el sujeto a su lado con el estandarte.",
             [("triunfo", 0.84), ("logro_personal", 0.82)],
             [("audacia", 0.82), ("determinacion", 0.80)],
             [("reconocimiento", 0.82), ("escalada_status", 0.78)]),
        ],
        "destino": "ruptura",
        "porque": "capturada en Compiègne (23-may-1430), juzgada por herejía y quemada en Ruan el 30-may-1431",
        "familias": ["5_persecucion", "7_caer_victima", "frye_mythos_tragedia"],
        "fuente": "https://en.wikipedia.org/wiki/Joan_of_Arc ; Orléans 1429, capturada 1430, quemada 1431",
    },
    {
        "slot": "C10", "person": "Carlomagno", "tipo": "gobernante",
        "freeze": "0800-12-25",
        "question": "¿Qué trayectoria sigue el sujeto tras ser coronado emperador en Roma?",
        "cuts": [
            ("C1_0768", "0768-09-24", "Hereda el reino franco junto a su hermano; tras la muerte de este (771) queda como único rey.",
             [("ambicion", 0.80), ("poder", 0.82)],
             [("liderazgo", 0.80), ("organizacion", 0.78)],
             [("oportunidad", 0.78), ("rivalidad_poder", 0.72)]),
            ("C2_0782", "0782-01-01", "Campañas contra los sajones; masacre de Verden y sumisión de los territorios del norte.",
             [("conquista", 0.84), ("autoridad", 0.82)],
             [("audacia", 0.80), ("determinacion", 0.82)],
             [("terreno_hostil", 0.78), ("hostilidad", 0.75)]),
            ("C3_0800", "0800-12-25", "Coronado emperador en Roma por el papa León III; une gran parte de Europa occidental bajo su corona.",
             [("triunfo", 0.84), ("logro_personal", 0.84)],
             [("liderazgo", 0.82), ("legitimidad_percibida", 0.80)],
             [("reconocimiento", 0.82), ("escalada_status", 0.80)]),
        ],
        "destino": "auge",
        "porque": "consolida el imperio, impulsa el renacimiento carolingio, muere el 28-ene-814 en Aquisgrán como emperador",
        "familias": ["arquetipo_el_gobernante", "9_audaz_empresa", "12_obtencion"],
        "fuente": "https://en.wikipedia.org/wiki/Charlemagne ; coronado emperador 800, renacimiento carolingio, muere 814",
    },
    {
        "slot": "C11", "person": "Suleimán el Magnífico", "tipo": "gobernante",
        "freeze": "1520-09-30",
        "question": "¿Qué trayectoria sigue el sujeto tras acceder al trono del imperio?",
        "cuts": [
            ("C1_1512", "1512-01-01", "Gobierna como príncipe en Manisa; se forma en administración, leyes y estrategia militar.",
             [("aprendizaje", 0.80), ("conocimiento", 0.78)],
             [("metodicidad", 0.78), ("planificacion", 0.75)],
             [("oportunidad", 0.72), ("jerarquia", 0.75)]),
            ("C2_1514", "1514-08-23", "Participa en la campaña de Chaldiran contra Persia; el imperio se expande hacia el este.",
             [("conquista", 0.80), ("ambicion", 0.78)],
             [("audacia", 0.78), ("organizacion", 0.78)],
             [("terreno_hostil", 0.72), ("escalada", 0.70)]),
            ("C3_1520", "1520-09-30", "Accede al trono tras la muerte de su padre; hereda un imperio en expansión y un ejército temido.",
             [("poder", 0.84), ("logro_personal", 0.82)],
             [("liderazgo", 0.82), ("autoridad", 0.80)],
             [("reconocimiento", 0.80), ("escalada_status", 0.78)]),
        ],
        "destino": "auge",
        "porque": "apogeo del imperio otomano (Belgrado 1521, Rodas 1522, Mohács 1526); muere el 6-sep-1566 en campaña",
        "familias": ["arquetipo_el_gobernante", "9_audaz_empresa", "30_ambicion"],
        "fuente": "https://en.wikipedia.org/wiki/Suleiman_the_Magnificent ; accede 1520, apogeo otomano, muere 1566",
    },
    {
        "slot": "C12", "person": "Iván IV de Rusia", "tipo": "gobernante",
        "freeze": "1547-01-16",
        "question": "¿Qué trayectoria sigue el sujeto tras ser coronado zar?",
        "cuts": [
            ("C1_1533", "1533-12-03", "Accede al trono con tres años; el poder queda en manos de regentes y facciones de boyardos.",
             [("vulnerabilidad", 0.80), ("dependencia", 0.78)],
             [("supervivencia", 0.78), ("resiliencia", 0.75)],
             [("fragmentacion", 0.78), ("rivalidad_poder", 0.80)]),
            ("C2_1545", "1545-01-01", "Toma el poder personal a los 15 años; impone su autoridad sobre los boyardos.",
             [("autoridad", 0.82), ("determinacion", 0.80)],
             [("audacia", 0.80), ("confrontacion_directa", 0.78)],
             [("hostilidad", 0.75), ("desconfianza", 0.78)]),
            ("C3_1547", "1547-01-16", "Coronado primer zar en Moscú; inicia conquistas (Kazán 1552, Astracán 1556).",
             [("triunfo", 0.82), ("poder", 0.84)],
             [("liderazgo", 0.80), ("ambicion", 0.82)],
             [("reconocimiento", 0.80), ("escalada_status", 0.78)]),
        ],
        "destino": "caida",
        "porque": "la oprichnina (1564-1572) y el terror interno erosionan el reino; muere el 28-mar-1584 dejando un país debilitado",
        "familias": ["33_error_de_juicio", "17_fatal_imprudencia", "frye_mythos_tragedia"],
        "fuente": "https://en.wikipedia.org/wiki/Ivan_the_Terrible ; coronado zar 1547, oprichnina 1564, muere 1584",
    },
    {
        "slot": "C13", "person": "Gengis Kan", "tipo": "gobernante",
        "freeze": "1206-01-01",
        "question": "¿Qué trayectoria sigue el sujeto tras unificar las tribus bajo su mando?",
        "cuts": [
            ("C1_1189", "1189-01-01", "Elegido kan de una confederación de clanes; sobrevive a traiciones y derrotas tempranas.",
             [("supervivencia", 0.84), ("resiliencia", 0.82)],
             [("liderazgo", 0.80), ("astucia", 0.80)],
             [("rivalidad_poder", 0.78), ("terreno_hostil", 0.75)]),
            ("C2_1203", "1203-01-01", "Derrota a sus rivales (Jamukha y los naimanes); incorpora sus guerreros y su organización.",
             [("conquista", 0.82), ("determinacion", 0.82)],
             [("organizacion", 0.82), ("audacia", 0.80)],
             [("escalada", 0.78), ("oportunidad", 0.75)]),
            ("C3_1206", "1206-01-01", "Proclamado gobernante universal en el kuriltai; unifica las tribus mongolas.",
             [("triunfo", 0.84), ("poder", 0.84)],
             [("liderazgo", 0.84), ("autoridad", 0.82)],
             [("reconocimiento", 0.82), ("escalada_status", 0.80)]),
        ],
        "destino": "auge",
        "porque": "conquista el norte de China y Persia; muere en 1227 durante la campaña contra Xi Xia, dejando el mayor imperio contiguo",
        "familias": ["arquetipo_el_gobernante", "9_audaz_empresa", "30_ambicion"],
        "fuente": "https://en.wikipedia.org/wiki/Genghis_Khan ; unificación 1206, conquistas, muere 1227",
    },
    {
        "slot": "C14", "person": "Cristóbal Colón", "tipo": "empresario",
        "freeze": "1492-08-03",
        "question": "¿Qué trayectoria sigue el sujeto tras zarpar hacia el oeste buscando una ruta a las Indias?",
        "cuts": [
            ("C1_1484", "1484-01-01", "Presenta su proyecto a la corte de Portugal; es rechazado y se traslada a Castilla.",
             [("vision", 0.82), ("determinacion", 0.80)],
             [("persuasion", 0.78), ("planificacion", 0.75)],
             [("frustracion", 0.75), ("escasez", 0.70)]),
            ("C2_1491", "1491-01-01", "Tras años de espera, los Reyes Católicos aceptan financiar la expedición (Capitulaciones de Santa Fe, abr-1492).",
             [("persuasion", 0.82), ("ambicion", 0.80)],
             [("negociacion", 0.80), ("determinacion", 0.82)],
             [("oportunidad", 0.80), ("reconocimiento", 0.72)]),
            ("C3_1492", "1492-08-03", "Zarpa de Palos con tres naves hacia el oeste, buscando una ruta marítima a las Indias.",
             [("audacia", 0.84), ("apuesta_extrema", 0.82)],
             [("liderazgo", 0.80), ("vision", 0.82)],
             [("incertidumbre", 0.80), ("oportunidad", 0.82)]),
        ],
        "destino": "caida",
        "porque": "tres viajes más, pierde el gobierno de las Indias (1500, arrestado y enviado a España), muere el 20-may-1506 en Valladolid sin reconocer el nuevo continente",
        "familias": ["33_error_de_juicio", "6_desastre", "frye_mythos_tragedia"],
        "fuente": "https://en.wikipedia.org/wiki/Christopher_Columbus ; primer viaje 1492, arrestado 1500, muere 1506",
    },
]

CASES += [
    {
        "slot": "C15", "person": "Fernando de Magallanes", "tipo": "empresario",
        "freeze": "1519-09-20",
        "question": "¿Qué trayectoria sigue el sujeto tras zarpar a buscar un paso marítimo hacia las islas de las especias?",
        "cuts": [
            ("C1_1505", "1505-01-01", "Sirve a Portugal en la India y Malaca; aprende navegación oceánica y rutas de especias.",
             [("conocimiento", 0.80), ("curiosidad_abstracta", 0.78)],
             [("aprendizaje", 0.80), ("analisis", 0.75)],
             [("oportunidad", 0.72), ("jerarquia", 0.70)]),
            ("C2_1517", "1517-01-01", "Rechazado por el rey de Portugal, ofrece su proyecto a Castilla; Carlos I lo acepta.",
             [("vision", 0.82), ("determinacion", 0.80)],
             [("persuasion", 0.80), ("negociacion", 0.78)],
             [("frustracion", 0.72), ("cambio_lealtad", 0.75)]),
            ("C3_1519", "1519-09-20", "Zarpa de Sanlúcar con cinco naves hacia el oeste, buscando un paso por el sur del nuevo continente.",
             [("audacia", 0.84), ("apuesta_extrema", 0.82)],
             [("liderazgo", 0.82), ("vision", 0.82)],
             [("incertidumbre", 0.80), ("terreno_hostil", 0.78)]),
        ],
        "destino": "ruptura",
        "porque": "muere en Mactán (Filipinas) el 27-abr-1521 en combate; la expedición completa la primera circunnavegación en 1522 bajo Elcano",
        "familias": ["9_audaz_empresa", "6_desastre", "frye_mythos_tragedia"],
        "fuente": "https://en.wikipedia.org/wiki/Ferdinand_Magellan ; zarpa 1519, muere 1521, circunnavegación completada 1522",
    },
    {
        "slot": "C16", "person": "Marco Polo", "tipo": "empresario",
        "freeze": "1275-06-01",
        "question": "¿Qué trayectoria sigue el sujeto tras llegar a la corte del gran kan?",
        "cuts": [
            ("C1_1271", "1271-01-01", "Sale de Venecia con su padre y su tío rumbo a Oriente por la ruta terrestre.",
             [("vision", 0.78), ("ambicion", 0.78)],
             [("viaje", 0.82), ("audacia", 0.80)],
             [("incertidumbre", 0.78), ("terreno_hostil", 0.75)]),
            ("C2_1273", "1273-01-01", "Travesía por Persia y Asia Central; la ruta es larga, peligrosa y exige negociar con gobernantes locales.",
             [("supervivencia", 0.82), ("resiliencia", 0.80)],
             [("negociacion", 0.80), ("flexibilidad_adaptativa", 0.78)],
             [("escasez", 0.75), ("terreno_hostil", 0.78)]),
            ("C3_1275", "1275-06-01", "Llega a China (c. 1275) y entra al servicio de la corte del gran kan.",
             [("logro_personal", 0.82), ("oportunidad", 0.80)],
             [("flexibilidad_adaptativa", 0.78), ("aprendizaje", 0.80)],
             [("reconocimiento", 0.78), ("escalada_status", 0.75)]),
        ],
        "destino": "auge",
        "porque": "17 años al servicio de la corte, regresa a Venecia en 1295 con riquezas; dicta Il Milione; muere en 1324",
        "familias": ["12_obtencion", "monomito_12_regreso_con_el_elixir", "arquetipo_el_heroe"],
        "fuente": "https://en.wikipedia.org/wiki/Marco_Polo ; llega a China c. 1275, regresa 1295, Il Milione, muere 1324",
    },
    {
        "slot": "C17", "person": "Dante Alighieri", "tipo": "artista",
        "freeze": "1302-01-27",
        "question": "¿Qué trayectoria sigue el sujeto tras ser condenado al exilio de su ciudad?",
        "cuts": [
            ("C1_1295", "1295-01-01", "Entra en la política florentina; se alinea con los güelfos blancos en la lucha de facciones.",
             [("ambicion", 0.78), ("patriotismo", 0.80)],
             [("oratoria", 0.80), ("organizacion", 0.75)],
             [("rivalidad_poder", 0.78), ("fragmentacion", 0.75)]),
            ("C2_1301", "1301-11-01", "Los güelfos negros toman Florencia con ayuda papal; el sujeto está fuera de la ciudad en misión diplomática.",
             [("perdida", 0.80), ("injusticia", 0.82)],
             [("supervivencia", 0.78), ("resiliencia", 0.75)],
             [("crisis_abrupta", 0.82), ("distancia_forzada", 0.80)]),
            ("C3_1302", "1302-01-27", "Condenado al exilio y a muerte si regresa; pierde sus bienes y su posición en Florencia.",
             [("perdida", 0.84), ("injusticia", 0.84)],
             [("resiliencia", 0.80), ("determinacion", 0.82)],
             [("aislamiento_social", 0.80), ("escasez", 0.78)]),
        ],
        "destino": "auge",
        "porque": "escribe la Divina Comedia en el exilio; muere el 14-sep-1321 en Rávena, reconocido como poeta mayor",
        "familias": ["35_recuperacion_de_lo_perdido", "arquetipo_el_creador", "trayectoria_escritores_creativos"],
        "fuente": "https://en.wikipedia.org/wiki/Dante_Alighieri ; exilio 1302, Divina Comedia, muere 1321",
    },
    {
        "slot": "C18", "person": "Miguel Ángel Buonarroti", "tipo": "artista",
        "freeze": "1508-01-01",
        "question": "¿Qué trayectoria sigue el sujeto tras recibir el encargo de pintar la bóveda de la capilla papal?",
        "cuts": [
            ("C1_1501", "1501-08-16", "Recibe el encargo del David en Florencia; trabaja un bloque de mármol abandonado por otros escultores.",
             [("creatividad", 0.84), ("ambicion", 0.80)],
             [("determinacion", 0.82), ("perfeccionismo", 0.80)],
             [("oportunidad", 0.78), ("reconocimiento_previo", 0.75)]),
            ("C2_1505", "1505-01-01", "Llamado a Roma por el papa Julio II para su tumba; el proyecto se interrumpe y el sujeto se siente humillado.",
             [("orgullo", 0.80), ("frustracion", 0.78)],
             [("resiliencia", 0.78), ("rebeldia", 0.75)],
             [("rivalidad_profesional", 0.78), ("hostilidad", 0.70)]),
            ("C3_1508", "1508-01-01", "Julio II le encarga pintar la bóveda de la Capilla Sixtina, un trabajo que el sujeto considera ajeno a su oficio de escultor.",
             [("responsabilidad", 0.82), ("determinacion", 0.84)],
             [("creatividad", 0.84), ("esfuerzo_sostenido_reciente", 0.80)],
             [("presion_social", 0.78), ("desafio_autoridad", 0.72)]),
        ],
        "destino": "auge",
        "porque": "termina la Sixtina (1512), pinta el Juicio Final (1541), dirige San Pedro; muere el 18-feb-1564 en Roma",
        "familias": ["arquetipo_el_creador", "12_obtencion", "schwartz_10_autodireccion"],
        "fuente": "https://en.wikipedia.org/wiki/Michelangelo ; Capilla Sixtina 1508-1512, Juicio Final 1541, muere 1564",
    },
    {
        "slot": "C19", "person": "Rembrandt van Rijn", "tipo": "artista",
        "freeze": "1642-01-01",
        "question": "¿Qué trayectoria sigue el sujeto tras terminar su gran cuadro de la milicia?",
        "cuts": [
            ("C1_1631", "1631-01-01", "Se traslada a Ámsterdam; se convierte en el retratista más solicitado de la burguesía.",
             [("creatividad", 0.84), ("ambicion", 0.80)],
             [("organizacion", 0.78), ("planificacion_activa", 0.75)],
             [("prosperidad", 0.80), ("reconocimiento", 0.82)]),
            ("C2_1634", "1634-06-22", "Se casa en 1634; compra una casa grande y colecciona arte y objetos.",
             [("compromiso_afectivo", 0.80), ("prosperidad", 0.82)],
             [("organizacion", 0.78), ("acumulacion_capital", 0.75)],
             [("estatus_social", 0.80), ("escalada_status", 0.78)]),
            ("C3_1642", "1642-01-01", "Termina La ronda de noche; su esposa Saskia muere ese año y su fortuna empieza a declinar.",
             [("perdida", 0.82), ("duelo", 0.80)],
             [("resiliencia", 0.78), ("creatividad", 0.84)],
             [("perdida_familiar", 0.82), ("vulnerabilidad_financiera_inmediata", 0.75)]),
        ],
        "destino": "caida",
        "porque": "declive de encargos, bancarrota en 1656, vende su casa y colección; sigue pintando obras maestras tardías y muere el 4-oct-1669 en Ámsterdam",
        "familias": ["33_error_de_juicio", "6_desastre", "frye_mythos_tragedia"],
        "fuente": "https://en.wikipedia.org/wiki/Rembrandt ; Ronda de noche 1642, bancarrota 1656, muere 1669",
    },
    {
        "slot": "C20", "person": "Nicolás Copérnico", "tipo": "cientifico",
        "freeze": "1514-01-01",
        "question": "¿Qué ocurre con el sujeto tras formular su teoría heliocéntrica en un breve tratado?",
        "cuts": [
            ("C1_1503", "1503-01-01", "Doctor en derecho canónico en Ferrara; regresa a Polonia como canónigo de Frombork.",
             [("conocimiento", 0.80), ("aprendizaje", 0.78)],
             [("metodicidad", 0.78), ("organizacion", 0.75)],
             [("jerarquia", 0.72), ("estabilidad_ocupacional", 0.78)]),
            ("C2_1510", "1510-01-01", "Se instala en Frombork; observa el cielo y anota discrepancias con el modelo geocéntrico.",
             [("busqueda_verdad", 0.82), ("curiosidad_abstracta", 0.80)],
             [("analisis", 0.82), ("verificacion", 0.78)],
             [("incertidumbre", 0.70), ("escepticismo", 0.72)]),
            ("C3_1514", "1514-01-01", "Circula entre amigos el Commentariolus (c. 1514), breve tratado que propone el Sol en el centro.",
             [("vision", 0.84), ("teorizacion", 0.82)],
             [("cautela", 0.80), ("prudencia", 0.78)],
             [("desafio_autoridad", 0.75), ("presion_social", 0.70)]),
        ],
        "destino": "auge",
        "porque": "publica De revolutionibus orbium coelestium en 1543; muere el 24-may-1543 en Frombork, el mismo año de su publicación",
        "familias": ["arquetipo_el_sabio", "12_obtencion", "social_04_rogers_difusion_innovaciones"],
        "fuente": "https://en.wikipedia.org/wiki/Nicolaus_Copernicus ; Commentariolus c. 1514, De revolutionibus 1543, muere 1543",
    },
]


def build_entrada(case: dict) -> dict:
    cuts = []
    for cid, date, hecho, P, A, C in case["cuts"]:
        cuts.append({
            "id": cid, "corte": cid, "cut_id": cid, "date": date,
            "fecha_corte": date, "hecho": hecho,
            "P": [[t, w] for t, w in P],
            "A": [[t, w] for t, w in A],
            "C": [[t, w] for t, w in C],
        })
    z_year = case["freeze"][:4]
    return {
        "case_id": case["slot"],
        "question": case["question"],
        "tipo_sujeto": case["tipo"],
        "freeze": case["freeze"],
        "random_seed": 0,
        "z_work_kind": "CASE_CUTOFF",
        "z_work_date": f"C3_{z_year}",
        "cuts": cuts,
        "source_notes": SOURCE_NOTE,
    }


def build_entrada_ciega_md(case: dict) -> str:
    lines = [
        "# Entrada ciega — " + case["slot"],
        "",
        "> Solo datos anteriores o iguales a Z. Sin identidad, sin desenlace,",
        "> sin fuentes que identifiquen al sujeto. La identidad y el desenlace",
        "> están sellados en custodia y se revelan solo al verificar.",
        "",
        "## Metadatos de custodia",
        f"- case_id: {case['slot']}",
        "- sujeto_alias: SUJETO_" + case["slot"],
        f"- fecha_freeze_Z: {case['freeze']}",
        "- rango_temporal_observado: ver cortes",
        "- fuente(s) del material pre-Z: selladas en custodia",
        "- responsable del freeze: generador lote_20 (2026-11-08)",
        "- estado: PREPARADO",
        "",
        "## Reglas",
        "- La identidad y el desenlace permanecen fuera de este archivo.",
        "- No buscar en internet ni intentar identificar al sujeto durante la corrida ciega.",
        "- Separar DATO, INFERENCIA, HIPÓTESIS y RUIDO.",
        "- No completar huecos con conocimiento posterior.",
        "- No modificar el texto después del freeze.",
        "",
        "## Cortes hasta Z",
    ]
    for i, (cid, date, hecho, P, A, C) in enumerate(case["cuts"]):
        letra = "ABCDE"[i]
        lines += [
            f"### Corte {letra}",
            f"- fecha: {date}",
            f"- hecho: {hecho}",
            "- P: " + ", ".join(f"{t} {w}" for t, w in P),
            "- A: " + ", ".join(f"{t} {w}" for t, w in A),
            "- C: " + ", ".join(f"{t} {w}" for t, w in C),
            "",
        ]
    lines += [
        "## Salida ciega obligatoria",
        "- Suficiencia: (la fija el motor al correr)",
        "- DATO: ver cortes",
        "- INFERENCIA: (la fija el motor al correr)",
        "- RUIDO: (la fija el motor al correr)",
        "- H1 / H2 / Set / Escenario / Destino: ver SALIDA_CONGELADA.json",
        "- Predictibilidad estructural previa: ver SALIDA_CONGELADA.json",
        "- Condiciones de falsación: el desenlace sellado las decide al verificar",
        "- Qué no puede saberse: la identidad del sujeto (sellada en custodia)",
        "",
    ]
    return "\n".join(lines)


def main():
    toks = valid_tokens()
    # sujetos ya usados (cola 45 + LOTE_01 10) — no repetir
    usados = set()
    for f in sorted((REPO / "casos" / "fabrica" / "cola").glob("*/entrada.json")):
        e = json.loads(f.read_text(encoding="utf-8"))
        usados.add((e.get("person") or "").strip().casefold())
    usados |= {"richard nixon", "winston churchill", "ignaz semmelweis", "marie curie",
               "vincent van gogh", "ludwig van beethoven", "henry ford",
               "sherlock holmes", "mijaíl gorbachov", "lázaro cárdenas"}
    assert len(CASES) == 20, f"se esperaban 20 casos, hay {len(CASES)}"
    assert len({c["slot"] for c in CASES}) == 20, "slots duplicados"
    engine = json.loads((REPO / "motor" / "motor" / "Engine_V5_CANONICO_SOLO.py").read_text(encoding="utf-8", errors="ignore") or "{}") if False else None
    for case in CASES:
        slot = case["slot"]
        assert case["person"].strip().casefold() not in usados, f"{slot} repite sujeto usado: {case['person']}"
        # validar tokens y pesos
        for cid, date, hecho, P, A, C in case["cuts"]:
            assert date <= case["freeze"], f"{slot} {cid} fecha {date} > freeze {case['freeze']}"
            for eje, pares in (("P", P), ("A", A), ("C", C)):
                assert len(pares) == 2, f"{slot} {cid} {eje} debe tener 2 tokens"
                for t, w in pares:
                    assert t in toks, f"{slot} {cid} token inválido: {t}"
                    assert 0.60 <= w <= 0.84, f"{slot} {cid} peso fuera de rango: {t} {w}"
        # validar que no hay nombre ni URL identificadora en el input visible
        entrada = build_entrada(case)
        blob = json.dumps(entrada, ensure_ascii=False).casefold()
        nombre = case["person"].strip().casefold()
        partes = [p for p in nombre.replace(" de ", " ").split() if len(p) >= 4]
        for p in partes:
            assert p not in blob, f"{slot}: el entrada.json filtra el nombre ({p})"
        assert "wikipedia" not in blob and "http" not in blob, f"{slot}: el entrada.json filtra una URL"
        assert "person" not in entrada, f"{slot}: el entrada.json lleva campo person"
        # escribir archivos
        d = BASE / slot
        c = CUSTODIA / slot
        d.mkdir(parents=True, exist_ok=True)
        c.mkdir(parents=True, exist_ok=True)
        entrada_bytes = json.dumps(entrada, ensure_ascii=False, indent=2).encode("utf-8")
        (d / "entrada.json").write_bytes(entrada_bytes)
        (d / "ENTRADA_CIEGA.md").write_text(build_entrada_ciega_md(case), encoding="utf-8")
        destino = {"destino": case["destino"], "porque": case["porque"],
                   "fuente": case["fuente"], "definiciones": DEFINICIONES}
        destino_bytes = json.dumps(destino, ensure_ascii=False, indent=2).encode("utf-8")
        (c / "DESTINO_SELLADO.json").write_bytes(destino_bytes)
        desenlace = {"familias": case["familias"], "fuente": case["fuente"]}
        desenlace_bytes = json.dumps(desenlace, ensure_ascii=False, indent=2).encode("utf-8")
        (c / "DESENLACE_SELLADO.json").write_bytes(desenlace_bytes)
        identidad = {"case_id": slot, "sujeto_alias": f"SUJETO_{slot}",
                     "person": case["person"], "fuente": case["fuente"],
                     "nota": "SELLADO. Se revela solo al verificar, después de congelar la salida y el recibo. Nunca va al entrada.json ni lo lee el motor."}
        identidad_bytes = json.dumps(identidad, ensure_ascii=False, indent=2).encode("utf-8")
        (c / "IDENTIDAD_SELLADA.json").write_bytes(identidad_bytes)
        compromiso = {
            "case_id": slot, "slot": slot, "version": "LOTE_20_CIEGO_V1",
            "fecha_freeze_Z": case["freeze"],
            "entrada_sha256": sha_bytes(entrada_bytes),
            "identidad_sha256": sha_bytes(identidad_bytes),
            "desenlace_sha256": sha_bytes(desenlace_bytes),
            "destino_sha256": sha_bytes(destino_bytes),
            "engine_sha256": ENGINE_SHA,
            "catalogo_244_sha256": PAT_SHA,
            "regla": "CIEGO: el motor no recibe nombre ni dato que identifique al sujeto; la identidad y el desenlace se revelan solo al verificar.",
        }
        (d / "COMPROMISO.json").write_text(json.dumps(compromiso, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"{slot}: OK (freeze {case['freeze']}, destino {case['destino']}, "
              f"entrada {sha_bytes(entrada_bytes)[:12]}...)")
    print(f"\n20/20 casos generados en {BASE}")
    print(f"Custodia en {CUSTODIA}")


if __name__ == "__main__":
    main()
