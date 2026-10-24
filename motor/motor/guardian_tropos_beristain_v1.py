#!/usr/bin/env python3
"""guardian_tropos_beristain_v1.py — GUARDIÁN DE TROPOS (Beristáin) · control siempre-on · 2026-09-27

Qué hace
  Revisa la pregunta y los textos del input y marca dónde hay lenguaje figurado, para que
  NO se lea literal como evidencia o como perfil. No decide nada del motor:
  can_decide_H=False, no escribe H, no escribe patterns, no reordena candidatos.

Ancla
  Helena Beristáin, Diccionario de retórica y poética (OCR 1995, TRANSFER_V15_1/_ref_beristain_djvu.txt).
  Inventario: PARA_CLAUDE_BERISTAIN_PLUGIN_20260919/INVENTARIO_BERISTAIN_TROPOS.json (familias,
  líneas OCR y fronteras). Specs: SPEC_ARQUITECTURA_PLUGIN_PREGUNTA_CAPAS (salida estructurada,
  metáfora como transferencia de dominio, NO_RESUELTO), SPEC_BERISTAIN_TROPOS_BOLSITAS y
  SPEC_TROPOS_BOLSITAS_ARQUETIPOS (bolsitas → estante PERFIL / PREGUNTA_SESGO / CAMPO / LOGICA).

Código previo reutilizado (no se reescribió)
  - plugin_pregunta_detras_v2.py v2.3.2: reglas de lítote e hipérbole (marco_litotes /
    marco_hiperbole). Aquí se llaman tal cual y se suman estructuras nuevas.
  - plugin_pregunta_dirigida (registrar_sinecdoque): el hook parte→todo caso a caso. Aquí el
    equivalente es registrar_parte_todo(); también acepta el mapa del caso (case["tropos_mapa_caso"]).
  Ninguna otra pieza con código de tropos existía (búsqueda en disco, zips anidados y Notion).

Reglas de método (de las specs)
  - Palabra suelta ≠ tropo: cada regla pide una construcción (sujeto + cópula + término de otro
    dominio, sustantivo + adjetivo de otro sentido, etc.).
  - Fronteras sin evidencia → subtipo NO_RESUELTO (IRONÍA↔SARCASMO, METONIMIA↔SINÉCDOQUE,
    PROSOPOPEYA↔METONIMIA, HIPÁLAGE↔PROSOPOPEYA, ANTÍTESIS↔PARADOJA, HIPÉRBOLE↔literal…).
  - Ironía: en el inventario está DESCARTADO_FP. Solo se registra la posibilidad, siempre
    NO_RESUELTO, nunca se invierte el sentido ni se elige ironía vs sarcasmo.
  - Disfemismo (extensión del modelo de Mj): rasgo de registro → estante PERFIL, regularizado;
    no es veredicto de hostilidad.
  - Catacresis (metáfora lexicalizada: "cuello de botella", "pata de la mesa") se reconoce para
    NO marcarla como figura viva (corrige a la regla de metáfora).
"""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

VERSION = "1.0.0-20260927"
HERE = Path(__file__).resolve().parent
FUENTE = "Beristáin, Diccionario de retórica y poética (OCR 1995)"
CANDADOS = {"can_decide_H": False, "escribe_H": False, "escribe_patterns": False, "reordena_candidatos": False,
            "siempre_on": True, "funcion": "impedir que lenguaje figurado se lea literal como evidencia/perfil"}

# --------------------------------------------------------------------------- catálogo (inventario)
CATALOGO: Dict[str, Dict[str, Any]] = {
    "METAFORA":     {"familia": "METASEMEMA", "ocr_line": 12696, "codigo": "VIVO_v1", "estante": "PERFIL",
                     "def": "traslado de un nombre que designa una cosa a la designación de otra (transferencia de dominio)"},
    "METONIMIA":    {"familia": "METASEMEMA", "ocr_line": 18285, "codigo": "VIVO_v1_estructuras_cerradas+mapa_caso", "estante": "PREGUNTA_SESGO",
                     "def": "sustitución por relación existencial (causa/efecto, continente/contenido, lugar/institución, autor/obra)"},
    "SINECDOQUE":   {"familia": "METASEMEMA", "ocr_line": 18299, "codigo": "VIVO_v1_estructuras_cerradas+mapa_caso", "estante": "PREGUNTA_SESGO",
                     "def": "parte↔todo, género↔especie, materia↔obra, singular↔plural"},
    "HIPALAGE":     {"familia": "METASEMEMA", "ocr_line": 14448, "codigo": "VIVO_v1", "estante": "PERFIL",
                     "def": "adjetivo ligado a un sustantivo al que ni sintáctica ni semánticamente corresponde"},
    "OXIMORON":     {"familia": "METASEMEMA", "ocr_line": 21932, "codigo": "VIVO_v1", "estante": "PERFIL",
                     "def": "dos términos contradictorios en el mismo sintagma"},
    "SINESTESIA":   {"familia": "METASEMEMA", "ocr_line": 27576, "codigo": "VIVO_v1", "estante": "PERFIL",
                     "def": "asociar sensaciones de distintos registros sensoriales (tipo de metáfora)"},
    "CATACRESIS":   {"familia": "METASEMEMA", "ocr_line": None, "codigo": "VIVO_v1_como_descarte", "estante": "CAMPO",
                     "def": "metáfora lexicalizada; se reconoce para NO leerla como figura viva"},
    "METALEPSIS":   {"familia": "METASEMEMA", "ocr_line": 18287, "codigo": "PENDIENTE_DE_REGLA", "estante": None,
                     "def": "metonimia del antecedente por el consecuente"},
    "ANTONOMASIA":  {"familia": "METASEMEMA", "ocr_line": None, "codigo": "VIVO_v1", "estante": "PERFIL",
                     "def": "nombre propio por común (un Judas) o epíteto por nombre propio (el Libertador)"},
    "IMAGEN":       {"familia": "METASEMEMA", "ocr_line": 11531, "codigo": "PENDIENTE_DE_REGLA", "estante": None,
                     "def": "figura por adición; sin regla determinista fiable"},
    "LITOTE":       {"familia": "METALOGISMO", "ocr_line": 17754, "codigo": "VIVO_v2.3.2(detras)+v1", "estante": "PERFIL",
                     "def": "se dice menos para significar más; negación de lo contrario"},
    "HIPERBOLE":    {"familia": "METALOGISMO", "ocr_line": 12029, "codigo": "VIVO_v2.3.2(detras)+v1", "estante": "PERFIL",
                     "def": "intensificación; decir más para significar menos"},
    "IRONIA":       {"familia": "METALOGISMO", "ocr_line": 15844, "codigo": "SOLO_POSIBILIDAD_NO_RESUELTO", "estante": "PERFIL",
                     "def": "oponer el significado a la forma; sarcasmo remite a ironía"},
    "ANTITESIS":    {"familia": "METALOGISMO", "ocr_line": 776, "codigo": "VIVO_v1_observacion", "estante": "CAMPO",
                     "def": "contraposición de ideas; el contenido puede ser literal"},
    "PARADOJA":     {"familia": "METALOGISMO", "ocr_line": 22346, "codigo": "VIVO_v1", "estante": "PERFIL",
                     "def": "ideas opuestas que serían absurdas al pie de la letra"},
    "ALUSION":      {"familia": "METALOGISMO", "ocr_line": 1746, "codigo": "VIVO_v1_lista_cerrada", "estante": "PERFIL",
                     "def": "decir algo para que se entienda otra cosa evocada"},
    "ELIPSIS":      {"familia": "FIGURA_CONSTRUCCION", "ocr_line": 3275, "codigo": "VIVO_v1", "estante": "PREGUNTA_SESGO",
                     "def": "omisión recuperable por contexto"},
    "ASINDETON":    {"familia": "FIGURA_CONSTRUCCION", "ocr_line": 4297, "codigo": "PENDIENTE_DE_REGLA", "estante": None,
                     "def": "series sin nexos; en entradas de tokens da falsos positivos"},
    "ZEUGMA":       {"familia": "FIGURA_CONSTRUCCION", "ocr_line": 16614, "codigo": "PENDIENTE_DE_REGLA", "estante": None,
                     "def": "figura por supresión"},
    "PERIFRASIS":   {"familia": "FIGURA_CONSTRUCCION", "ocr_line": 22879, "codigo": "VIVO_v1_lista_cerrada", "estante": "CAMPO",
                     "def": "frase para decir lo que diría una palabra (la ciudad de los palacios)"},
    "EUFEMISMO":    {"familia": "ESTRATEGIA_REGISTRO", "ocr_line": 11926, "codigo": "VIVO_v1", "estante": "CAMPO",
                     "def": "sustituir lo duro por lo suave"},
    "DISFEMISMO":   {"familia": "ESTRATEGIA_REGISTRO", "ocr_line": None, "codigo": "VIVO_v1_ruteo_perfil", "estante": "PERFIL",
                     "def": "extensión de Mj: pareja del eufemismo; rasgo regularizado de perfil"},
    "COMPARACION":  {"familia": "COMPARACION_LIMITE", "ocr_line": 2217, "codigo": "VIVO_v1", "estante": "PERFIL",
                     "def": "símil con nexo (como, igual que, parecía)"},
    "ALEGORIA":     {"familia": "COMPARACION_LIMITE", "ocr_line": 1493, "codigo": "VIVO_v1_derivada", "estante": "PERFIL",
                     "def": "metáfora continuada (≥2 metáforas del mismo dominio de origen en un texto)"},
    "PROSOPOPEYA":  {"familia": "COMPARACION_LIMITE", "ocr_line": 19034, "codigo": "VIVO_v1", "estante": "PERFIL",
                     "def": "atribuir cualidades o acciones humanas a lo abstracto o inanimado"},
}

# --------------------------------------------------------------------------- normalización con spans
_TR = str.maketrans("áéíóúüñÁÉÍÓÚÜÑàèìòù", "aeiouunAEIOUUNaeiou")


def _n(s: str) -> str:
    """minúsculas sin tildes, misma longitud (los spans sirven sobre el original)."""
    return s.translate(_TR).lower()


_STOP = set("""el la los las un una unos unas de del al a y o e u que en con por para su sus mi mis tu tus se lo le les
me te nos es era fue son eran ser sido esta este estos estas ese esa esos esas no ni mas muy ya como pero sin sobre entre
hasta desde cuando donde porque the of and to in a an is was be it that for on with as by""".split())
_EN_STOP = {"the", "of", "and", "to", "in", "is", "was", "with", "his", "her", "their", "from", "by", "for", "on", "shows", "he", "she",
            "will", "him", "has", "have", "are", "been", "this", "that", "which", "it", "its", "they", "were"}
_ES_STOP = {"el", "la", "los", "las", "de", "del", "que", "y", "en", "un", "una", "por", "con", "se", "su", "es", "fue", "era"}


def idioma(texto: str) -> str:
    w = re.findall(r"[a-záéíóúñ]+", texto.lower())
    en = sum(1 for x in w if x in _EN_STOP)
    es = sum(1 for x in w if _n(x) in _ES_STOP) + (2 if re.search(r"[áéíóúñ¿¡]", texto) else 0)
    if en > es:
        return "en"
    if es > 0:
        return "es"
    return "desconocido"


def _oraciones(texto: str) -> List[Tuple[int, int]]:
    out, ini = [], 0
    for m in re.finditer(r"[.;!?¿¡\n]+", texto):
        if m.start() > ini:
            out.append((ini, m.start()))
        ini = m.end()
    if ini < len(texto):
        out.append((ini, len(texto)))
    return [(a, b) for a, b in out if texto[a:b].strip()]


def _palabras(s: str) -> List[str]:
    return re.findall(r"[a-zñ]+", _n(s))


def _set(txt: str) -> set:
    return set(txt.split())


# --------------------------------------------------------------------------- léxicos (normalizados, sin tildes)
HUMANO_N = _set("""hombre mujer padre madre hijo hija jefe jefa lider presidente presidenta ministro ministra nino nina
hermano hermana esposo esposa marido socio socia amigo amiga abuelo abuela tio tia profesor profesora maestro maestra rey
reina general soldado director directora empresario empresaria gerente candidato candidata persona tipo senor senora papa
mama companero companera fundador fundadora cientifico cientifica autor autora dueno duena alumno alumna vecino vecina
entrenador jugador jugadora artista inventor inventora hombres mujeres""")
PRONOMBRE_HUMANO_ORIG = re.compile(r"\b(él|Él|ella|Ella|yo|Yo|tú|Tú|usted|Usted|nosotros|ellos|ellas)\b")
CAP_NO_NOMBRE = _set("el la los las un una su sus mi mis ese esa este esta aquel aquella en de y pero como cuando si no es era fue que lo le se ya hoy ayer hay nunca siempre todo toda tras desde con por para al del")

DOMINIOS_NOMBRE: Dict[str, str] = {}
for _dom, _ws in {
    "ANIMAL": "leon leona lobo loba zorro zorra tiburon serpiente vibora perro perra aguila burro burra cerdo cerda toro gallina rata oveja cordero tigre tigresa hiena buitre pulpo camaleon mula gusano halcon paloma bestia fiera",
    "NATURALEZA": "volcan tormenta huracan roca montana rio fuego hielo rayo terremoto sol torbellino tornado ola piedra tempano oceano mar muralla",
    "MAQUINA_OBJETO": "maquina motor muro pared tanque bomba torre robot iman ancla faro brujula tren cohete pilar columna tapete",
    "MINERAL": "acero hierro oro diamante plomo",
    "PLANTA": "roble flor rosa espina arbol junco cactus",
    "SOBRENATURAL": "angel demonio diablo santo bruja hada monstruo titan gigante",
}.items():
    for _w in _ws.split():
        DOMINIOS_NOMBRE[_w] = _dom
RASGO_PROBABLE = {"leon": "valentía/fiereza", "zorro": "astucia", "zorra": "astucia", "lobo": "depredación/soledad", "tiburon": "agresividad en negocios",
                  "serpiente": "traición", "vibora": "maledicencia", "roca": "firmeza", "muro": "resistencia", "muralla": "resistencia",
                  "maquina": "rendimiento incansable", "motor": "impulso", "volcan": "explosividad", "tormenta": "turbulencia",
                  "huracan": "fuerza arrolladora", "hielo": "frialdad", "angel": "bondad", "demonio": "maldad", "santo": "virtud",
                  "pilar": "sostén", "columna": "sostén", "acero": "dureza", "oro": "valor", "diamante": "dureza/valor",
                  "titan": "grandeza", "gigante": "grandeza", "burro": "torpeza/terquedad", "aguila": "visión", "faro": "guía"}
ORGANO_FUNCION = _set("cerebro corazon alma cabeza")

ABSTRACTO_ORG = _set("""carrera empresa proyecto negocio relacion matrimonio economia gobierno reputacion fama idea plan sueno amistad
campana trayectoria imperio compania marca startup gestion mandato alianza sociedad fortuna""")
VERBO_DOMINIO = [
    (r"floreci\w*|se\s+marchit\w*|muri\w*|agoniz\w*|se\s+desangr\w*|germin\w*|echo\s+raices|respir\w*|renaci\w*", "BIOLOGICO"),
    (r"naufrag\w*|se\s+hundi\w*|zarp\w*|a\s+la\s+deriva|encall\w*", "NAUTICO"),
    (r"despeg\w*|aterriz\w*|en\s+picada|se\s+estrell\w*", "AERONAUTICO"),
    (r"se\s+derrumb\w*|se\s+desmoron\w*|se\s+resquebraj\w*|se\s+tambale\w*", "CONSTRUCCION"),
]
COMPLEMENTO_ABSTRACTO = _set("""dudas deudas problemas criticas lagrimas ideas emociones mentiras preguntas quejas errores oportunidades
conocimiento sabiduria amor odio miedo esperanza tristeza soledad poder rumores insultos elogios aplausos contradicciones
sentimientos recuerdos datos informacion obstaculos burocracia intrigas""")
CUANTIF_METAF = _set("mar oceano lluvia montana ola avalancha torrente alud diluvio nube mina pozo laberinto jaula tunel semilla raiz cancer veneno")

CATACRESIS = [
    r"patas?\s+de\s+la\s+(?:mesa|silla|cama)", r"brazos?\s+del?\s+(?:sillon|sofa|mar|rio)", r"cuellos?\s+de\s+botella",
    r"bocas?\s+del?\s+(?:metro|rio|tunel|estomago)", r"ojo\s+de\s+la\s+aguja", r"pie\s+de\s+pagina", r"dientes?\s+de\s+ajo",
    r"hojas?\s+de\s+(?:papel|afeitar)", r"lomo\s+del\s+libro", r"falda\s+de\s+la\s+montana|falda\s+del\s+cerro",
    r"alas?\s+del\s+(?:edificio|hospital|palacio)", r"realidad\s+virtual", r"cabeza\s+de\s+familia", r"bottleneck",
]

ANTONOMASIA_TIPO = _set("judas quijote casanova einstein hercules adonis neron maquiavelo mesias sanson goliat narciso celestina lazarillo frankenstein matusalen salomon tenorio")
ANTONOMASIA_EPITETO = {"el libertador": "Simón Bolívar", "el manco de lepanto": "Cervantes", "el bardo": "Shakespeare",
                       "la dama de hierro": "Margaret Thatcher", "el rey sol": "Luis XIV", "el fenix de los ingenios": "Lope de Vega",
                       "el padre de la patria": "(según país)", "el divo de juarez": "Juan Gabriel"}
ALUSION = {r"talon\s+de\s+aquiles": "Aquiles (mito): punto débil", r"caja\s+de\s+pandora": "Pandora (mito): males liberados",
           r"cruz\w*\s+el\s+rubicon": "César: decisión sin retorno", r"victoria\s+pirrica": "Pirro: victoria que arruina",
           r"canto\s+de\s+(?:las\s+)?sirenas?": "Odisea: tentación engañosa", r"(?:trabajo|tarea|esfuerzo)\s+de\s+sisifo": "Sísifo: esfuerzo inútil",
           r"\bsu\s+waterloo\b": "Waterloo: derrota definitiva", r"caballo\s+de\s+troya": "Troya: engaño infiltrado",
           r"espada\s+de\s+damocles": "Damocles: amenaza suspendida", r"nudo\s+gordiano": "Alejandro: problema cortado de tajo",
           r"hilo\s+de\s+ariadna": "Ariadna: guía para salir", r"se\s+lav\w*\s+las\s+manos": "Pilato: desentenderse",
           r"beso\s+de\s+judas": "Judas: traición", r"manzana\s+de\s+la\s+discordia": "Eris/Paris: origen de disputa",
           r"vend\w*\s+su\s+alma\s+al\s+diablo": "Fausto: pacto ruinoso", r"huevo\s+de\s+colon": "Colón: solución obvia a posteriori"}
PERIFRASIS = {r"ciudad\s+de\s+los\s+palacios": "Ciudad de México", r"astro\s+rey": "el sol", r"rey\s+de\s+la\s+selva": "el león",
              r"ciudad\s+eterna": "Roma", r"septimo\s+arte": "el cine", r"mejor\s+amigo\s+del\s+hombre": "el perro",
              r"tierra\s+del\s+sol\s+naciente": "Japón", r"gran\s+manzana": "Nueva York", r"viejo\s+continente": "Europa",
              r"ciudad\s+(?:de\s+la\s+)?luz": "París", r"planeta\s+rojo": "Marte", r"oro\s+negro": "petróleo",
              r"el\s+que\s+(?:esto\s+)?escribe\s+estas\s+lineas": "yo (el autor)"}
EUFEMISMO = {r"pas\w*\s+a\s+mejor\s+vida": "murió", r"descans\w*\s+en\s+paz": "murió", r"ya\s+no\s+esta\s+(?:entre|con)\s+nosotros": "murió",
             r"\binvidente\b": "ciego", r"tercera\s+edad": "vejez", r"adultos?\s+mayor(?:es)?": "anciano(s)",
             r"interrupcion\s+(?:voluntaria\s+)?del\s+embarazo": "aborto",
             r"(?:reajuste|ajuste|reestructuracion|recorte)\s+de\s+(?:plantilla|personal)|desvinculaci\w+|salida\s+de\s+personal": "despidos",
             r"danos\s+colaterales": "víctimas no buscadas", r"crecimiento\s+negativo": "caída", r"en\s+vias\s+de\s+desarrollo": "pobre",
             r"problemas\s+con\s+(?:la\s+bebida|el\s+alcohol)": "alcoholismo", r"estado\s+de\s+buena\s+esperanza|en\s+estado\s+interesante": "embarazo",
             r"neutraliz\w*\s+al?\s+(?:objetivo|sospechoso)": "matar/abatir", r"centro\s+de\s+readaptacion": "cárcel"}
EUFEMISMO_EN = {r"passed\s+away": "died", r"collateral\s+damage": "unintended victims", r"\bdownsizing\b": "layoffs"}
EUFEMISMO_AMBIGUO = {r"\bnos\s+dejo\b": ("murió", r"muri|funeral|velorio|entierro|sepelio|descans|luto|cenizas"),
                     r"(?:tras|despues\s+de)\s+una\s+larga\s+enfermedad": ("enfermedad no nombrada", None)}
# Disfemismo: semilla corta y revisable (SPEC_TROPOS_BOLSITAS §F). Registro, no juicio.
DISFEMISMO = {r"estir\w*\s+la\s+pata": "murió", r"se\s+petate\w*": "murió", r"\bla\s+palm\w*": "murió",
              r"valio\s+madre": "se arruinó", r"\bpinche\b": "(intensificador despectivo)", r"\bpendejada\b": "tontería/error",
              r"\bmatasanos\b": "médico", r"\bloquero\b": "psiquiatra", r"\bpicapleitos\b": "abogado", r"\bcarcacha\b": "coche viejo"}
HIPERBOLE_EXTRA = [
    (r"\b(?:mil|cien|un\s+millon\s+de|millones\s+de|infinitas)\s+veces\b", "cuantificador desmedido"),
    (r"\buna\s+eternidad\b", "duración desmedida"),
    (r"\b(?:me\s+muero|se\s+moria|se\s+muere|nos\s+morimos|muert[oa]s?)\s+de\s+(?:hambre|risa|miedo|sed|sueno|ganas|verguenza|frio|calor|cansancio)\b", "estado exagerado"),
    (r"\bmas\s+viej[oa]\s+que\s+matusalen\b", "comparación desmedida"),
    (r"\bllor\w*\s+(?:rios|mares)\b", "cantidad desmedida"),
    (r"\btodo\s+el\s+mundo\s+(?:sabe|sabia|dice|decia|conoce|conocia|lo\s+sabe)\b", "universal desmedido"),
    (r"\bnadie\s+en\s+el\s+mundo\b", "universal desmedido"),
    (r"\b(?:el|la)\s+(?:mejor|peor)\s+del\s+mundo\b|\b(?:el|la)\s+(?:mas|menos)\s+\w+\s+del\s+mundo\b", "superlativo absoluto"),
    (r"\bno\s+cab\w+\s+(?:ni\s+)?un\s+alma\b", "cantidad desmedida"),
]
HIPERBOLE_EN = r"\bof\s+all\s+time\b|\bunprecedented\b|\bnever\s+before\s+seen\b|\bthe\s+greatest\s+\w+\s+in\s+history\b|\ba\s+million\s+times\b|\beveryone\s+knows\b"
CUE_LITERAL_RANKING = r"campeon|ranking|clasificaci|medalla|record|primer\s+lugar|titulo\s+mundial|olimpi|mundial\s+de|world\s+champion"
LITOTE_EXTRA = [
    r"\bno\s+(?:es|era|fue|esta|estaba|son|eran|parece|parecia)\s+(?:nada\s+|precisamente\s+)?(?:tont[oa]s?|fe[oa]s?|mal[oa]s?|mal|despreciables?|desdenables?|pequen[oa]s?|escas[oa]s?|facil|faciles|sencill[oa]|rar[oa]|cualquier\s+cosa|torpe|inutil)\b",
    r"\bno\s+carec\w*\s+de\b", r"\bnada\s+(?:mal|despreciable|desdenable|tonto|facil)\b",
    r"\bno\s+le\s+falt\w+\s+(?:razon|talento|merito|valor|ingenio)\b", r"\bno\s+sin\s+(?:esfuerzo|merito|dificultad|razon)\b",
]
DOBLE_NEG = r"\bno\s+es\s+que\s+no\b|\bno\s+(?:es|era|fue)\s+(?:in|des)[a-z]{4,}\b"
IRONIA_CUES = [
    (r"[\"“«']\s*(?:brillante|genial|excelente|magnific[oa]|maravillos[oa]|inteligente|list[oa]|gran|genio|heroe|exito|triunfo)\s*[\"”»']", "adjetivo evaluativo entre comillas"),
    (r"¡\s*que\s+(?:list[oa]|genio|inteligente|maravilla|bonito|bien|suerte)\s*!", "exclamación evaluativa"),
    (r"\bsi\s*,?\s+claro\b|\bsi\s*,?\s+como\s+no\b|\bclaro\s*,\s*como\s+no\b", "asentimiento marcado"),
]
IRONIA_CONTRASTE = r"fracas|perdi|quiebra|error|desastre|ruina|peor|arruin|hundi"
ANTONIMOS = [
    ("vida vivir vivo viva vivio", "muerte morir muerto muerta murio muero"), ("amor amar", "odio odiar"),
    ("luz luminoso luminosa", "sombra oscuridad oscuro oscura"), ("rico rica ricos", "pobre pobres"),
    ("joven jovenes", "viejo vieja viejos"), ("guerra", "paz"), ("principio comienzo", "fin final"),
    ("todo", "nada"), ("siempre", "nunca"), ("cielo", "infierno"), ("dia", "noche"), ("corto corta", "largo larga"),
    ("ganar gano gana gane", "perder perdio pierde perdi"), ("grande", "pequeno pequena"), ("fuerte", "debil"),
    ("alegria", "tristeza"), ("reir rie", "llorar llora lloro"), ("nacer nacio nace", "morir murio muere"),
    ("mucho mucha", "poco poca"), ("exito", "fracaso"), ("verdad", "mentira"), ("libre", "preso esclavo"),
    ("ascenso subir subio", "caida caer cayo"),
]
MERISMO_IDIOMA = r"de\s+principio\s+a\s+fin|dia\s+y\s+noche|noche\s+y\s+dia|blanco\s+y\s+negro|todo\s+o\s+nada|mas\s+o\s+menos|ni\s+mas\s+ni\s+menos|de\s+vida\s+o\s+muerte|tarde\s+o\s+temprano|ricos\s+y\s+pobres|grandes\s+y\s+pequenos|jovenes\s+y\s+viejos"
OXIMORON_PARES = [("silencio", "atronador ensordecedor ruidoso elocuente estruendoso sonoro"), ("soledad", "sonora poblada"),
                  ("fuego", "helado"), ("hielo", "abrasador ardiente"), ("luz", "oscura negra"), ("oscuridad", "luminosa brillante radiante"),
                  ("muerto", "viviente"), ("calma", "tensa agitada"), ("dulce", "tormento amargura"), ("instante", "eterno"),
                  ("orden", "caotico"), ("caos", "ordenado organizado"), ("ruido", "silencioso callado"), ("ignorancia", "sabia docta"),
                  ("amarga", "dulzura")]
SENTIDO_N = {"color": "VISTA", "colores": "VISTA", "luz": "VISTA", "mirada": "VISTA", "voz": "OIDO", "sonido": "OIDO", "musica": "OIDO",
             "silencio": "OIDO", "grito": "OIDO", "melodia": "OIDO", "nota": "OIDO", "sabor": "GUSTO", "olor": "OLFATO", "aroma": "OLFATO",
             "perfume": "OLFATO", "textura": "TACTO"}
SENTIDO_A: Dict[str, str] = {}
for _s, _ws in {"OIDO": "chillon chillona estridente ruidoso ruidosa sonoro sonora", "GUSTO": "dulce amargo amarga acido acida agrio agria salado salada",
                "TACTO": "aspero aspera suave aterciopelado aterciopelada calido calida frio fria rugoso rugosa",
                "VISTA": "brillante luminoso luminosa oscuro oscura opaco opaca", "OLFATO": "fragante perfumado perfumada apestoso"}.items():
    for _w in _ws.split():
        SENTIDO_A[_w] = _s
SINESTESIA_LEXICALIZADA = {("voz", "suave"), ("voz", "dulce"), ("color", "calido"), ("colores", "calidos"), ("color", "frio"), ("colores", "frios"),
                           ("mirada", "fria"), ("musica", "suave"), ("voz", "calida")}
INANIMADO_HIPALAGE = _set("cigarro cigarrillo noche tarde manana camino calle silla cama ventana puerta mesa taza copa pluma reloj habitacion cuarto pasos humo")
ADJ_MENTAL = _set("pensativo pensativa insomne melancolico melancolica nervioso nerviosa angustiado angustiada ansioso ansiosa distraido distraida orgulloso orgullosa sonoliento sonolienta perezoso perezosa")
ABSTRACTO_PROSOP = _set("tiempo historia destino muerte vida silencio suerte fortuna verdad naturaleza justicia hechos datos memoria")
COLECTIVO_PROSOP = _set("mercado mercados ciudad pais pueblo empresa gobierno prensa calle nacion mundo opinion")
VERBO_HUMANO = r"(?:dira|diran|juzgara|juzgaran|juzgo|hablara|hablan|habla|hablaron|sonrie|sonrio|lloro|llora|castigo|castiga|premio|premia|perdona|perdono|decidio|decidira|grita|gritan|susurra|ensena|enseno|traiciono|traiciona|abrazo|besa|miente|mintio|se\s+burl\w+|llamo\s+a\s+su\s+puerta)"
VERBO_HUMANO_EN = r"(?:will\s+judge|judged|will\s+tell|speak|speaks|spoke|decided|smiled|punished|betrayed)"
ABSTRACTO_PROSOP_EN = r"(?:history|time|fate|the\s+facts|facts|destiny|fortune|truth)"
LUGAR_INSTITUCION = ["casa blanca", "kremlin", "vaticano", "los pinos", "palacio nacional", "moncloa", "downing street", "wall street",
                     "hollywood", "bruselas", "pentagono", "scotland yard", "san lazaro", "santa sede"]
VERBO_DECLARA = r"(?:anuncio|anuncia|decidio|decide|respondio|responde|advirtio|advierte|condeno|condena|rechazo|rechaza|aprobo|aprueba|exige|exigio|prohibio|ordeno|reacciono|reacciona|confirmo|confirma|nego|niega|dijo|dice|declaro|sanciono|said|announced|reacted|denied|warned)"
SIMBOLO_AMBIGUO = {r"\bla\s+corona\b": "corona (símbolo del reino o parte de la regalía)", r"\bel\s+trono\b": "trono (símbolo del poder o parte del palacio)",
                   r"\bla\s+(?:mejor|gran)\s+pluma\b": "pluma (instrumento por escritor)",
                   r"\b(?:\d+|mil|cien|diez\s+mil|miles\s+de)\s+(?:espadas|lanzas|fusiles|bayonetas)\b": "arma (instrumento por soldado)"}
GENTILICIO_GENERICO = _set("mexicano mexicana espanol espanola argentino argentina frances francesa aleman alemana ingles inglesa italiano italiana chino china japones japonesa ruso rusa americano americana norteamericano latino latina campesino obrero politico")
PERSONA_GENERICO = _set("hombre mujer joven artista cientifico")

_REG_PARTE_TODO: Dict[str, Dict[str, Any]] = {}


def registrar_parte_todo(canon: str, variantes: Sequence[str], relacion: Optional[str] = None) -> None:
    """Hook caso a caso (equivalente a plugin_pregunta_dirigida.registrar_sinecdoque).
    relacion ∈ {'SINECDOQUE', 'METONIMIA', None}. None → subtipo NO_RESUELTO al detectar."""
    key = _n(canon).strip()
    if not key:
        return
    d = _REG_PARTE_TODO.setdefault(key, {"variantes": set(), "relacion": None})
    if relacion in ("SINECDOQUE", "METONIMIA"):
        d["relacion"] = relacion
    for v in variantes or []:
        nv = _n(str(v)).strip()
        if nv:
            d["variantes"].add(nv)


def limpiar_registro() -> None:
    _REG_PARTE_TODO.clear()


# --------------------------------------------------------------------------- reutilizar detras v2 (lítote/hipérbole)
_DETRAS: Any = None


def _detras():
    global _DETRAS
    if _DETRAS is None:
        try:
            if "g_detras_v2" in sys.modules:
                _DETRAS = sys.modules["g_detras_v2"]
            else:
                spec = importlib.util.spec_from_file_location("gtropos_detras_v2", str(HERE / "plugin_pregunta_detras_v2.py"))
                mod = importlib.util.module_from_spec(spec)
                sys.modules["gtropos_detras_v2"] = mod  # dataclasses lo necesita registrado antes de ejecutar
                spec.loader.exec_module(mod)
                _DETRAS = mod
        except Exception:
            _DETRAS = False
    return _DETRAS or None


# --------------------------------------------------------------------------- hallazgo estructurado
def _h(tropo: str, texto: str, origen: str, span: Tuple[int, int], regla: str, *, confianza: float, estado: Optional[str] = None,
       subtipo: Optional[str] = None, nivel: Sequence[str] = ("lexico", "sintactico", "semantico"), senales: Sequence[str] = (),
       ambiguedad: Optional[str] = None, transferencia: Optional[Dict[str, Any]] = None, bloquea: bool = True,
       equivalente: Optional[str] = None, extra: Optional[Dict[str, Any]] = None, familia_frontera: Optional[str] = None) -> Dict[str, Any]:
    cat = CATALOGO.get(tropo, {})
    if estado is None:
        estado = "NO_RESUELTO" if subtipo == "NO_RESUELTO" else ("DETECTADA" if confianza >= 0.7 else "POSIBLE")
    h = {"tropo_detectado": estado in ("DETECTADA", "POSIBLE"), "tropo": tropo,
         "familia": familia_frontera or cat.get("familia"), "subtipo": subtipo or tropo, "estado": estado,
         "nivel": list(nivel), "confianza": round(float(confianza), 2), "ambiguedad": ambiguedad,
         "fuente": f"{FUENTE}, entrada {tropo}" + (f" (línea OCR {cat['ocr_line']})" if cat.get("ocr_line") else " (sin lema en el OCR; inventario)"),
         "forzado": False, "estante": cat.get("estante"),
         "bloquea_lectura_literal": bool(bloquea),
         "evidencia": {"origen": origen, "fragmento": texto[span[0]:span[1]], "span": [span[0], span[1]], "regla": regla,
                       "senales": list(senales)}}
    if transferencia:
        h["transferencia"] = transferencia
    if equivalente:
        h["lectura_literal_equivalente"] = equivalente
    if extra:
        h.update({k: v for k, v in extra.items() if v is not None})
    return h


def _solapa(a: Sequence[int], b: Sequence[int]) -> bool:
    return a[0] < b[1] and b[0] < a[1]


def _sujeto_humano(orig_pre: str, norm_pre: str) -> Optional[str]:
    """Sujeto del tramo previo a la cópula. None = elidido; 'NO_HUMANO' si hay un sustantivo que no es persona."""
    if PRONOMBRE_HUMANO_ORIG.search(orig_pre):
        return "pronombre"
    ws = _palabras(norm_pre)
    if any(w in HUMANO_N for w in ws):
        return "sustantivo_humano"
    for m in re.finditer(r"\b([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)\b", orig_pre):
        if _n(m.group(1)) not in CAP_NO_NOMBRE:
            return "nombre_propio"
    if [w for w in ws if w not in _STOP and len(w) > 2]:
        return "NO_HUMANO"
    return None


# --------------------------------------------------------------------------- reglas (español)
def _metaforas(texto, origen, a, so, sn, libre, H):
    # 1) copulativa: SUJETO + ser/parecer + (un|una|el|la) + N de otro dominio
    for m in re.finditer(r"\b(es|era|fue|eres|soy|sera|parece|parecia|se\s+volvio|resulto)\s+(?:todo\s+|toda\s+)?(un|una|el|la)\s+(?:verdader[oa]\s+|autentic[oa]\s+)?([a-z]+)(\s+de\s+[a-z]+)?", sn):
        n_ = m.group(3)
        sp = (a + m.start(), a + m.end() if n_ in ORGANO_FUNCION and m.group(4) else a + m.end(3))
        if not libre(sp):
            continue
        if n_ in ORGANO_FUNCION and m.group(4):
            H.append(_h("METAFORA", texto, origen, sp, "organo_por_funcion", confianza=0.5, subtipo="NO_RESUELTO", familia_frontera="METASEMEMA",
                        ambiguedad="METÁFORA ↔ METONIMIA (órgano por función): sin frontera clara",
                        senales=[f"'{n_}{m.group(4)}' aplicado a un referente"]))
            continue
        dom = DOMINIOS_NOMBRE.get(n_)
        if not dom:
            continue
        pre_o, pre_n = so[:m.start()], sn[:m.start()]
        org = [w for w in _palabras(pre_n) if w in ABSTRACTO_ORG]
        suj = "organizacion" if org else _sujeto_humano(pre_o, pre_n)
        if suj == "NO_HUMANO":
            continue
        if suj is None:
            H.append(_h("METAFORA", texto, origen, sp, "copulativa_sujeto_elidido", confianza=0.45, subtipo="NO_RESUELTO",
                        ambiguedad="sujeto elidido: no se sabe si es persona (figurado) o la cosa misma (literal)",
                        transferencia={"dominio_origen": dom, "dominio_destino": "NO_RESUELTO", "operacion": "atribucion_copulativa", "termino_origen": n_},
                        senales=[f"cópula + '{n_}' ({dom})", "sin sujeto explícito"]))
            continue
        destino = "ORGANIZACION/PROYECTO(" + org[0] + ")" if org else "PERSONA"
        H.append(_h("METAFORA", texto, origen, sp, "copulativa_referente_es_N_de_otro_dominio", confianza=0.8,
                    transferencia={"dominio_origen": dom, "dominio_destino": destino, "operacion": "atribucion_copulativa",
                                   "termino_origen": n_, "rasgo_probable": RASGO_PROBABLE.get(n_, "NO_RESUELTO"),
                                   "rasgo_es_inferencia_no_evidencia": True},
                    senales=[f"sujeto ({suj})", f"cópula '{m.group(1)}'", f"'{n_}' ∈ {dom}"]))
    # 2) genitiva cuantificadora: un mar de dudas
    for m in re.finditer(r"\b(un|una)\s+(?:verdader[oa]\s+)?([a-z]+)\s+de\s+([a-z]+)", sn):
        q, c = m.group(2), m.group(3)
        if q in CUANTIF_METAF and (c in COMPLEMENTO_ABSTRACTO or re.search(r"(dad|cion|sion|ismo|eza|encia|ancia|ura)s?$", c)):
            sp = (a + m.start(), a + m.end())
            if libre(sp):
                H.append(_h("METAFORA", texto, origen, sp, "genitiva_cuantificadora", confianza=0.75,
                            transferencia={"dominio_origen": DOMINIOS_NOMBRE.get(q, "MATERIA/ESPACIO"), "dominio_destino": "ABSTRACTO(" + c + ")",
                                           "operacion": "cuantificacion_o_estructuracion_figurada", "termino_origen": q},
                            senales=[f"'{q}' físico aplicado a '{c}' abstracto"]))
    # 3) verbal: sujeto organizacional/abstracto + verbo de otro dominio
    for vpat, vdom in VERBO_DOMINIO:
        for m in re.finditer(r"\b(?:su|la|el|una|un|esa|ese|esta|este|sus|las|los)\s+([a-z]+)\s+(?:[a-z]+\s+)?(" + vpat + r")", sn):
            if m.group(1) in ABSTRACTO_ORG:
                sp = (a + m.start(), a + m.end())
                if libre(sp):
                    H.append(_h("METAFORA", texto, origen, sp, "verbal_sujeto_abstracto_verbo_de_otro_dominio", confianza=0.7,
                                transferencia={"dominio_origen": vdom, "dominio_destino": "ORGANIZACION/PROYECTO(" + m.group(1) + ")",
                                               "operacion": "predicacion_verbal_figurada", "termino_origen": m.group(2)},
                                senales=[f"sujeto '{m.group(1)}'", f"verbo '{m.group(2)}' ({vdom})"]))
    # 4) símil (COMPARACIÓN; Beristáin: límite del tropo)
    for m in re.finditer(r"\b(como|igual\s+que|cual|parecia|parece)\s+(un|una)\s+([a-z]+)\b", sn):
        dom = DOMINIOS_NOMBRE.get(m.group(3))
        if dom:
            H.append(_h("COMPARACION", texto, origen, (a + m.start(), a + m.end()), "simil_nexo_mas_termino_de_otro_dominio", confianza=0.75,
                        transferencia={"dominio_origen": dom, "dominio_destino": "REFERENTE_DEL_ENUNCIADO", "operacion": "comparacion_explicita",
                                       "termino_origen": m.group(3)},
                        senales=[f"nexo '{m.group(1)}'", f"'{m.group(3)}' ∈ {dom}"]))


def _metasememas_otros(texto, origen, a, so, sn, H):
    # SINESTESIA
    for m in re.finditer(r"\b([a-z]+)\s+(?=([a-z]+)\b)", sn):
        n1, a1 = m.group(1), m.group(2)
        if n1 in SENTIDO_N and a1 in SENTIDO_A and SENTIDO_N[n1] != SENTIDO_A[a1]:
            sp = (a + m.start(), a + m.end(2))
            if (n1, a1) in SINESTESIA_LEXICALIZADA:
                H.append(_h("SINESTESIA", texto, origen, sp, "sinestesia_lexicalizada", confianza=0.4, estado="OBSERVACION", bloquea=False,
                            senales=[f"{SENTIDO_N[n1]}←{SENTIDO_A[a1]} (uso corriente)"]))
            else:
                H.append(_h("SINESTESIA", texto, origen, sp, "sustantivo_de_un_sentido_adjetivo_de_otro", confianza=0.75,
                            transferencia={"dominio_origen": SENTIDO_A[a1], "dominio_destino": SENTIDO_N[n1], "operacion": "transposicion_sensorial"},
                            senales=[f"'{n1}' ({SENTIDO_N[n1]})", f"'{a1}' ({SENTIDO_A[a1]})"]))
    # OXÍMORON (contrarios adyacentes, sin conjunción)
    for base, opuestos in OXIMORON_PARES:
        for op in opuestos.split():
            for pat in (rf"\b{base}\s+{op}\b", rf"\b{op}\s+{base}\b"):
                for m in re.finditer(pat, sn):
                    H.append(_h("OXIMORON", texto, origen, (a + m.start(), a + m.end()), "contrarios_en_el_mismo_sintagma", confianza=0.8,
                                senales=[f"'{base}' ⟂ '{op}' adyacentes"]))
    for m in re.finditer(r"\bmuert[oa]s?\s+en\s+vida\b", sn):
        H.append(_h("OXIMORON", texto, origen, (a + m.start(), a + m.end()), "contrarios_en_el_mismo_sintagma", confianza=0.75, senales=["muerto ⟂ vida"]))
    # HIPÁLAGE / frontera con PROSOPOPEYA
    for m in re.finditer(r"\b([a-z]+)\s+(?=([a-z]+)\b)", sn):
        if m.group(1) in INANIMADO_HIPALAGE and m.group(2) in ADJ_MENTAL:
            if so[m.start():m.end(2)][:1].isupper() and m.start() > 0:
                continue
            sp = (a + m.start(), a + m.end(2))
            resto_o = so[:m.start()] + " " + so[m.end(2):]
            resto_n = sn[:m.start()] + " " + sn[m.end(2):]
            suj = _sujeto_humano(resto_o, resto_n)
            if suj in ("pronombre", "sustantivo_humano", "nombre_propio"):
                H.append(_h("HIPALAGE", texto, origen, sp, "adjetivo_mental_en_inanimado_con_persona_en_la_frase", confianza=0.7,
                            senales=[f"'{m.group(2)}' corresponde a la persona ({suj}), no a '{m.group(1)}'"]))
            else:
                H.append(_h("HIPALAGE", texto, origen, sp, "adjetivo_mental_en_inanimado_sin_persona", confianza=0.45, subtipo="NO_RESUELTO",
                            familia_frontera="METASEMEMA", ambiguedad="HIPÁLAGE ↔ PROSOPOPEYA: no hay persona a quien devolver el adjetivo",
                            senales=[f"'{m.group(1)} {m.group(2)}'"]))
    # PROSOPOPEYA / frontera con METONIMIA
    for m in re.finditer(r"\b(el|la|los|las|su)\s+([a-z]+)\s+(?:[a-z]+\s+)?(?:(?:lo|la|le|les|nos|me|te|se)\s+)?" + VERBO_HUMANO + r"\b", sn):
        sujn = m.group(2)
        if re.search(r"todo\s+$", sn[:m.start()]):
            continue
        sp = (a + m.start(), a + m.end())
        if sujn in ABSTRACTO_PROSOP:
            H.append(_h("PROSOPOPEYA", texto, origen, sp, "sujeto_abstracto_con_accion_humana", confianza=0.75,
                        transferencia={"dominio_origen": "PERSONA", "dominio_destino": "ABSTRACTO(" + sujn + ")", "operacion": "personificacion"},
                        senales=[f"sujeto '{sujn}'", "verbo de acción humana"]))
        elif sujn in COLECTIVO_PROSOP:
            H.append(_h("PROSOPOPEYA", texto, origen, sp, "sujeto_colectivo_con_accion_humana", confianza=0.5, subtipo="NO_RESUELTO",
                        familia_frontera="COMPARACION_LIMITE", ambiguedad="PROSOPOPEYA ↔ METONIMIA: el colectivo puede estar por las personas que lo forman",
                        senales=[f"sujeto '{sujn}' (colectivo)", "verbo de acción humana"]))
    # METONIMIA: lugar por institución
    for lug in LUGAR_INSTITUCION:
        for m in re.finditer(r"\b(?:el\s+|la\s+|los\s+)?" + lug.replace(" ", r"\s+") + r"\s+(?:[a-z]+\s+)?" + VERBO_DECLARA + r"\b", sn):
            H.append(_h("METONIMIA", texto, origen, (a + m.start(), a + m.end()), "lugar_por_institucion", confianza=0.8,
                        subtipo="LUGAR_POR_INSTITUCION", senales=[f"'{lug}' + verbo de declaración/decisión"]))
    st = so.translate(_TR)  # conserva mayúsculas, quita tildes, misma longitud
    for m in re.finditer(r"\b(?:leer|leyo|leia|lee|leimos|releer|releyo|leyendo)\s+a\s+([A-Z][a-z]+)", st):
        H.append(_h("METONIMIA", texto, origen, (a + m.start(), a + m.end()), "autor_por_obra", confianza=0.8, subtipo="AUTOR_POR_OBRA",
                    senales=["verbo de lectura + nombre propio"]))
    for m in re.finditer(r"\b(?:tiene|tenia|compro|vendio|subastaron|subasto|colgo|heredo)\s+(?:un|una|dos|tres|varios|varias)\s+([A-Z][a-z]+)", st):
        H.append(_h("METONIMIA", texto, origen, (a + m.start(), a + m.end()), "autor_o_marca_por_obra_o_producto", confianza=0.75,
                    subtipo="PRODUCTOR_POR_PRODUCTO", senales=["posesión + artículo + nombre propio"]))
    for m in re.finditer(r"\b(?:se\s+)?(?:tomar|tomo|tomaron|tomamos|beber|bebio|bebimos|bebieron|echo|comio|comieron)\s+(?:un|una|unas|unos|dos|tres|varias|varios|otra|otro)\s+(?:copas?|vasos?|botellas?|tazas?|platos?)\b", sn):
        H.append(_h("METONIMIA", texto, origen, (a + m.start(), a + m.end()), "continente_por_contenido", confianza=0.75,
                    subtipo="CONTINENTE_POR_CONTENIDO", senales=["verbo de consumo + recipiente"]))
    # SINÉCDOQUE: parte por todo (estructuras cerradas)
    for pat, sen in ((r"\b(?:\d+|mil|cien|cientos\s+de|miles\s+de|varias|muchas|pocas|dos|tres|cuatro|cinco|diez|veinte)\s+cabezas\s+de\s+(?:ganado|res|reses)\b", "cabezas por animales"),
                     (r"\b[a-z]+\s+bocas\s+que\s+alimentar\b", "bocas por personas"),
                     (r"\b(?:faltan|faltaban|necesitamos|necesitan|necesitaba|hacen\s+falta|sobran)\s+(?:brazos|manos)\b", "brazos/manos por trabajadores"),
                     (r"\bbajo\s+(?:el\s+mismo|un\s+mismo|su|mi|nuestro)\s+techo\b", "techo por casa"),
                     (r"\bganar\w*\s+el\s+pan\b", "pan por sustento"),
                     (r"\b(?:\d+|mil|cien|quinientas|doscientas)\s+almas\b", "almas por personas"),
                     (r"\bcaras\s+nuevas\b", "caras por personas")):
        for m in re.finditer(pat, sn):
            H.append(_h("SINECDOQUE", texto, origen, (a + m.start(), a + m.end()), "parte_por_todo", confianza=0.8, subtipo="PARTE_POR_TODO",
                        senales=[sen]))
    m = re.match(r"\s*(el|la)\s+([a-z]+)\s+(es|son|tiene|siempre|nunca|suele)\b", sn)
    if m and (m.group(2) in GENTILICIO_GENERICO or m.group(2) in PERSONA_GENERICO):
        sp = (a + m.start(1), a + m.end())
        if m.group(2) in GENTILICIO_GENERICO:
            H.append(_h("SINECDOQUE", texto, origen, sp, "singular_generico_por_clase", confianza=0.6, subtipo="SINGULAR_POR_PLURAL",
                        senales=[f"'{m.group(1)} {m.group(2)}' + predicado general"], extra={"estante": "PERFIL", "vecino_falacias": "generalización"}))
        else:
            H.append(_h("SINECDOQUE", texto, origen, sp, "singular_generico_o_referente_concreto", confianza=0.4, subtipo="NO_RESUELTO",
                        ambiguedad="individuo concreto vs clase entera: sin contexto no se decide", senales=[f"'{m.group(1)} {m.group(2)}'"]))
    for pat, sen in SIMBOLO_AMBIGUO.items():
        for m in re.finditer(pat, sn):
            H.append(_h("METONIMIA", texto, origen, (a + m.start(), a + m.end()), "simbolo_o_instrumento_por_agente", confianza=0.55,
                        subtipo="NO_RESUELTO", familia_frontera="METASEMEMA_PARTE",
                        ambiguedad="METONIMIA ↔ SINÉCDOQUE: relación existencial o parte-todo sin frontera clara", senales=[sen]))
    # ANTONOMASIA
    for m in re.finditer(r"\b(?:un|una|el|la|todo\s+un|toda\s+una|nuevo|nueva|otro|otra)\s+(don\s+juan|robin\s+hood|[a-z]+)\b", sn):
        nm = m.group(1)
        if (nm in ANTONOMASIA_TIPO or nm in ("don juan", "robin hood")) and so[m.start(1):m.end(1)][:1].isupper():
            H.append(_h("ANTONOMASIA", texto, origen, (a + m.start(), a + m.end()), "nombre_propio_como_comun", confianza=0.8,
                        subtipo="NOMBRE_PROPIO_POR_COMUN", senales=[f"'{so[m.start(1):m.end(1)]}' usado como tipo"]))
    for m in re.finditer(r"\b(?:es|era|fue|parece|parecia|resulto)\s+(?:todo\s+)?(?:un|una)\s+([A-Z][a-z]+)\b", st):
        if _n(m.group(1)) in ANTONOMASIA_TIPO:
            continue
        H.append(_h("ANTONOMASIA", texto, origen, (a + m.start(), a + m.end()), "nombre_propio_tras_articulo_indefinido", confianza=0.5,
                    subtipo="NO_RESUELTO", familia_frontera="METASEMEMA",
                    ambiguedad="ANTONOMASIA ↔ METONIMIA (un Picasso = tipo de persona u obra del autor)", senales=[f"'un {m.group(1)}'"]))
    for ep, ref in ANTONOMASIA_EPITETO.items():
        for m in re.finditer(r"\b" + ep.replace(" ", r"\s+") + r"\b", sn):
            if so[m.start():m.end()].split()[-1][:1].isupper():
                H.append(_h("ANTONOMASIA", texto, origen, (a + m.start(), a + m.end()), "epiteto_por_nombre_propio", confianza=0.8,
                            subtipo="EPITETO_POR_NOMBRE", equivalente=ref, senales=["epíteto con mayúscula"]))


def _metalogismos_y_registro(texto, origen, a, so, sn, nt, H):
    # PARADOJA
    for pat, sen in ((r"\b([a-z]{3,})[a-z]*\s+sin\s+\1[a-z]*", "X sin X"), (r"\b([a-z]{3,})[a-z]*\s+porque\s+no\s+\1[a-z]*", "X porque no X"),
                     (r"\bmenos\s+es\s+mas\b", "menos es más"), (r"\bapresurate\s+lentamente\b|\bdespacio\s+que\s+tengo\s+prisa\b", "prisa lenta"),
                     (r"\bpara\s+(?:ganar|vivir|encontrar[a-z]*)\s+hay\s+que\s+(?:perder|morir)[a-z]*\b", "fin por su contrario")):
        for m in re.finditer(pat, sn):
            if sen in ("X sin X", "X porque no X"):
                w = re.findall(r"[a-z]+", m.group(0))
                w1, w2 = w[0], w[-1]
                if max(len(w1), len(w2)) > 8:  # "contrato sin contratiempos": misma raíz, no contradicción
                    continue
            H.append(_h("PARADOJA", texto, origen, (a + m.start(), a + m.end()), "contradiccion_aparente_mismo_referente", confianza=0.75, senales=[sen]))
    # ANTÍTESIS (observación) / frontera con PARADOJA
    ws = [(mm.group(0), mm.start()) for mm in re.finditer(r"[a-z]+", sn)]
    wl = [w for w, _ in ws]
    if not re.search(MERISMO_IDIOMA, sn):
        for A_, B_ in ANTONIMOS:
            sa, sb = set(A_.split()), set(B_.split())
            ia = [i for i, w in enumerate(wl) if w in sa]
            ib = [i for i, w in enumerate(wl) if w in sb]
            if not ia or not ib:
                continue
            i, j = min(ia), min(ib)
            lo, hi = min(i, j), max(i, j)
            if hi - lo <= 1:
                continue
            sp = (a + ws[lo][1], a + ws[hi][1] + len(wl[hi]))
            if any(h["tropo"] in ("PARADOJA", "OXIMORON") and _solapa(h["evidencia"]["span"], sp) for h in H):
                continue
            if re.search(r"\ba\s+la\s+vez\b|\bal\s+mismo\s+tiempo\b|\bsimultaneamente\b", sn):
                H.append(_h("ANTITESIS", texto, origen, sp, "contrarios_predicados_a_la_vez", confianza=0.5, subtipo="NO_RESUELTO",
                            familia_frontera="METALOGISMO", ambiguedad="ANTÍTESIS ↔ PARADOJA: contrarios del mismo referente al mismo tiempo",
                            senales=[f"'{wl[i]}' ⟂ '{wl[j]}'", "a la vez / al mismo tiempo"]))
            else:
                H.append(_h("ANTITESIS", texto, origen, sp, "contrarios_en_miembros_distintos", confianza=0.6, estado="OBSERVACION", bloquea=False,
                            senales=[f"'{wl[i]}' ⟂ '{wl[j]}'", "forma retórica; el contenido puede ser literal"]))
    # ALUSIÓN / PERÍFRASIS
    for pat, ref in ALUSION.items():
        for m in re.finditer(pat, sn):
            H.append(_h("ALUSION", texto, origen, (a + m.start(), a + m.end()), "alusion_lista_cerrada", confianza=0.85, equivalente=ref,
                        senales=["referente evocado, no dicho"]))
    for pat, ref in PERIFRASIS.items():
        for m in re.finditer(r"\b" + pat, sn):
            H.append(_h("PERIFRASIS", texto, origen, (a + m.start(), a + m.end()), "perifrasis_lista_cerrada", confianza=0.8, equivalente=ref,
                        senales=["frase por nombre"]))
    # EUFEMISMO / DISFEMISMO
    for pat, ref in EUFEMISMO.items():
        for m in re.finditer(pat, sn):
            H.append(_h("EUFEMISMO", texto, origen, (a + m.start(), a + m.end()), "sustitucion_suave", confianza=0.8, equivalente=ref,
                        senales=["registro suavizado; el hecho literal es el equivalente"]))
    for pat, (ref, ctx) in EUFEMISMO_AMBIGUO.items():
        for m in re.finditer(pat, sn):
            ok = bool(ctx and re.search(ctx, nt))
            H.append(_h("EUFEMISMO", texto, origen, (a + m.start(), a + m.end()), "sustitucion_suave_ambigua", confianza=0.75 if ok else 0.4,
                        subtipo=None if ok else "NO_RESUELTO", equivalente=ref,
                        ambiguedad=None if ok else "puede ser literal o el referente no está nombrado: falta contexto",
                        senales=["contexto confirma" if ok else "sin contexto que confirme"]))
    for pat, ref in DISFEMISMO.items():
        for m in re.finditer(pat, sn):
            H.append(_h("DISFEMISMO", texto, origen, (a + m.start(), a + m.end()), "registro_aspero", confianza=0.8, equivalente=ref,
                        extra={"regularizado": True, "no_es_veredicto_de_hostilidad": True,
                               "nota": "rasgo de registro del hablante → PERFIL; no cascada a agresividad/conflicto"},
                        senales=["registro áspero donde lo social sería suave"]))
    # HIPÉRBOLE (estructuras nuevas) con frontera literal por ranking
    for pat, sen in HIPERBOLE_EXTRA:
        for m in re.finditer(pat, sn):
            sp = (a + m.start(), a + m.end())
            if re.search(CUE_LITERAL_RANKING, sn):
                H.append(_h("HIPERBOLE", texto, origen, sp, "superlativo_con_contexto_de_ranking", confianza=0.45, subtipo="NO_RESUELTO",
                            familia_frontera="METALOGISMO", ambiguedad="HIPÉRBOLE ↔ afirmación literal (hay contexto de competencia/ranking)",
                            senales=[sen, "cue de ranking"]))
            else:
                H.append(_h("HIPERBOLE", texto, origen, sp, "hiperbole_estructural_v1", confianza=0.75, senales=[sen],
                            extra={"vecino_falacias": "generalización" if "universal" in sen else None}))
    # LÍTOTE (estructuras nuevas) + frontera doble negación
    for pat in LITOTE_EXTRA:
        for m in re.finditer(pat, sn):
            H.append(_h("LITOTE", texto, origen, (a + m.start(), a + m.end()), "negacion_de_lo_contrario_v1", confianza=0.75,
                        senales=["no + término negativo → afirmación atenuada"]))
    for m in re.finditer(DOBLE_NEG, sn):
        H.append(_h("LITOTE", texto, origen, (a + m.start(), a + m.end()), "doble_negacion", confianza=0.5, subtipo="NO_RESUELTO",
                    familia_frontera="METALOGISMO", ambiguedad="LÍTOTE ↔ DOBLE NEGACIÓN lógica: puede afirmar o solo atenuar",
                    senales=["negación + negación/prefijo negativo"]))
    # ELIPSIS (referente omitido)
    for m in re.finditer(r"\b(?:el|la|lo|los|las)\s+de\s+(?:antes|siempre|ayer|entonces|la\s+otra\s+vez|c\d+|corte\s+[a-z0-9]+)\b|\blo\s+que\s+ya\s+sabemos\b|\blo\s+que\s+paso\b|\b(?:eso|aquello)\s+que\s+(?:paso|sabemos|ya\s+sabes)\b", sn):
        H.append(_h("ELIPSIS", texto, origen, (a + m.start(), a + m.end()), "referente_omitido", confianza=0.6, nivel=("sintactico", "semantico"),
                    bloquea=False, extra={"referente": "NO_RECUPERABLE_EN_ESTE_TEXTO", "riesgo": "el sellado/desenlace puede quedar sobreentendido"},
                    senales=["núcleo omitido; se recupera solo por contexto"]))


def _ironia(texto, origen, nt, H):
    """IRONÍA: solo la posibilidad; siempre NO_RESUELTO; nunca se invierte el sentido (texto completo: usa ¡…!)."""
    contraste = bool(re.search(IRONIA_CONTRASTE, nt))
    for pat, sen in IRONIA_CUES:
        for m in re.finditer(pat, nt):
            H.append(_h("IRONIA", texto, origen, m.span(), "marca_de_posible_ironia", confianza=0.45 if contraste else 0.35,
                        subtipo="NO_RESUELTO", familia_frontera="METALOGISMO_IRONIA",
                        ambiguedad="IRONÍA ↔ SARCASMO ↔ sentido literal: no se decide (inventario: DESCARTADO_FP)",
                        senales=[sen] + (["contraste negativo en el texto"] if contraste else []), extra={"no_invertir_sentido": True}))


def _reglas_es(texto: str, origen: str) -> List[Dict[str, Any]]:
    nt = _n(texto)
    H: List[Dict[str, Any]] = []
    cat_spans: List[Tuple[int, int]] = []
    for pat in CATACRESIS:  # primero: corrige a la regla de metáfora
        for m in re.finditer(pat, nt):
            cat_spans.append(m.span())
            H.append(_h("CATACRESIS", texto, origen, m.span(), "catacresis_lexicalizada", confianza=0.9, estado="OBSERVACION", bloquea=False,
                        senales=["metáfora muerta: se lee literal"]))

    def libre(sp):
        return not any(_solapa(sp, c) for c in cat_spans)

    for a, b in _oraciones(texto):
        so, sn = texto[a:b], nt[a:b]
        _metaforas(texto, origen, a, so, sn, libre, H)
        _metasememas_otros(texto, origen, a, so, sn, H)
        _metalogismos_y_registro(texto, origen, a, so, sn, nt, H)
    _ironia(texto, origen, nt, H)
    return H


def _reglas_en(texto: str, origen: str) -> List[Dict[str, Any]]:
    """Cobertura mínima en inglés (hay títulos/snippets en inglés en los casos)."""
    nt = _n(texto)
    H = []
    for pat in CATACRESIS:
        for m in re.finditer(pat, nt):
            H.append(_h("CATACRESIS", texto, origen, m.span(), "catacresis_lexicalizada", confianza=0.9, estado="OBSERVACION", bloquea=False))
    for m in re.finditer(r"\b" + ABSTRACTO_PROSOP_EN + r"\s+" + VERBO_HUMANO_EN + r"\b", nt):
        H.append(_h("PROSOPOPEYA", texto, origen, m.span(), "abstract_subject_human_action_EN", confianza=0.7,
                    transferencia={"dominio_origen": "PERSONA", "dominio_destino": "ABSTRACTO", "operacion": "personificacion"}))
    for m in re.finditer(r"\b(?:the\s+)?(?:white\s+house|kremlin|vatican|pentagon|wall\s+street|downing\s+street)\s+" + VERBO_DECLARA + r"\b", nt):
        H.append(_h("METONIMIA", texto, origen, m.span(), "place_for_institution_EN", confianza=0.8, subtipo="LUGAR_POR_INSTITUCION"))
    for m in re.finditer(HIPERBOLE_EN, nt):
        H.append(_h("HIPERBOLE", texto, origen, m.span(), "hyperbole_EN", confianza=0.7))
    for pat, ref in EUFEMISMO_EN.items():
        for m in re.finditer(pat, nt):
            H.append(_h("EUFEMISMO", texto, origen, m.span(), "euphemism_EN", confianza=0.8, equivalente=ref))
    return H


def _detras_tropos(texto: str, origen: str) -> List[Dict[str, Any]]:
    """Reutiliza tal cual las reglas vivas de plugin_pregunta_detras_v2 (lítote/hipérbole)."""
    d = _detras()
    if d is None:
        return []
    try:
        r = d.filtrar(texto)
    except Exception:
        return []
    nt = _n(texto)
    out = []
    for mk in r.get("marcajes") or []:
        regla = mk.get("regla") if isinstance(mk, dict) else None
        if regla not in ("marco_litotes", "marco_hiperbole"):
            continue
        frag = _n(str(mk.get("fragmento") or ""))
        i = nt.find(frag) if frag else -1
        sp = (i, i + len(frag)) if i >= 0 else (0, len(texto))
        tropo = "LITOTE" if regla == "marco_litotes" else "HIPERBOLE"
        if tropo == "HIPERBOLE" and re.search(CUE_LITERAL_RANKING, nt):
            out.append(_h(tropo, texto, origen, sp, f"detras_v2:{regla}+ranking", confianza=0.45, subtipo="NO_RESUELTO", familia_frontera="METALOGISMO",
                          ambiguedad="HIPÉRBOLE ↔ afirmación literal (contexto de ranking)", senales=["regla reutilizada de plugin_pregunta_detras_v2"]))
        else:
            out.append(_h(tropo, texto, origen, sp, f"detras_v2:{regla}", confianza=float(mk.get("score") or 0.8),
                          senales=["regla reutilizada de plugin_pregunta_detras_v2 " + str(getattr(d, "VERSION", ""))]))
    return out


def _mapa_caso(texto: str, origen: str, mapa: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
    reg = {k: {"variantes": set(v["variantes"]), "relacion": v.get("relacion")} for k, v in _REG_PARTE_TODO.items()}
    for canon, spec in (mapa or {}).items():
        k = _n(canon)
        d = reg.setdefault(k, {"variantes": set(), "relacion": None})
        vs = spec.get("variantes") if isinstance(spec, dict) else spec
        if isinstance(spec, dict) and spec.get("relacion") in ("SINECDOQUE", "METONIMIA"):
            d["relacion"] = spec["relacion"]
        d["variantes"] |= {_n(str(v)) for v in vs or []}
    nt = _n(texto)
    out = []
    for canon, d in reg.items():
        for v in sorted(d["variantes"]):
            for m in re.finditer(r"\b" + re.escape(v) + r"\b", nt):
                rel = d.get("relacion")
                out.append(_h(rel or "SINECDOQUE", texto, origen, m.span(), "mapa_caso_parte_todo", confianza=0.8 if rel else 0.55,
                              subtipo=None if rel else "NO_RESUELTO", familia_frontera=None if rel else "METASEMEMA_PARTE",
                              ambiguedad=None if rel else "METONIMIA ↔ SINÉCDOQUE: el mapa del caso no dice la relación",
                              equivalente=canon, senales=[f"variante registrada de '{canon}'"]))
    return out


def _dedup(H: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Mismo tropo solapado en el mismo texto → queda el de mayor confianza. Tropos distintos conviven
    (las capas no se anulan) y un NO_RESUELTO no lo borra un DETECTADO de otro tropo."""
    out: List[Dict[str, Any]] = []
    for h in sorted(H, key=lambda h: (-h["confianza"], h["evidencia"]["span"][0])):
        if any(o["tropo"] == h["tropo"] and o["evidencia"]["origen"] == h["evidencia"]["origen"]
               and _solapa(o["evidencia"]["span"], h["evidencia"]["span"]) for o in out):
            continue
        out.append(h)
    return sorted(out, key=lambda h: (h["evidencia"]["origen"], h["evidencia"]["span"][0], h["tropo"]))


def analizar_texto(texto: str, origen: str = "texto", mapa_caso: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    lang = idioma(texto)
    H = _reglas_en(texto, origen) if lang == "en" else _reglas_es(texto, origen) + _detras_tropos(texto, origen)
    H = _dedup(H + _mapa_caso(texto, origen, mapa_caso))
    doms: Dict[str, List[Dict[str, Any]]] = {}
    for h in H:  # ALEGORÍA derivada: ≥2 figuras vivas del mismo dominio de origen
        if h["tropo"] in ("METAFORA", "COMPARACION") and h["estado"] in ("DETECTADA", "POSIBLE"):
            doms.setdefault((h.get("transferencia") or {}).get("dominio_origen"), []).append(h)
    for dom, hs in doms.items():
        if dom and len(hs) >= 2:
            sp = (min(x["evidencia"]["span"][0] for x in hs), max(x["evidencia"]["span"][1] for x in hs))
            H.append(_h("ALEGORIA", texto, origen, sp, "metafora_continuada", confianza=0.6,
                        transferencia={"dominio_origen": dom, "dominio_destino": "TEXTO_COMPLETO", "operacion": "metafora_continuada"},
                        senales=[f"{len(hs)} figuras del dominio {dom}"]))
    return {"origen": origen, "idioma": lang, "hallazgos": H,
            "reglas_aplicadas": "ES_completo+detras_v2" if lang != "en" else "EN_minimo(prosopopeya, metonimia de lugar, hipérbole, eufemismo, catacresis)"}


def _tokens_en_riesgo(h: Dict[str, Any], tokens_tablero: Sequence[str]) -> List[str]:
    if not tokens_tablero or not h.get("bloquea_lectura_literal"):
        return []
    raices = {w[:5] for w in _palabras(h["evidencia"]["fragmento"]) if w not in _STOP and len(w) >= 4}
    out = set()
    for t in tokens_tablero:
        if any(p[:5] in raices for p in re.split(r"[_\W]+", _n(str(t))) if len(p) >= 4):
            out.add(str(t))
    return sorted(out)[:10]


def guardian(textos: Sequence[Dict[str, str]], question: Optional[str] = None, tokens_tablero: Optional[Sequence[str]] = None,
             mapa_caso: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Entrada: [{'origen','texto'}] (+ pregunta aparte, opcional). Salida: bloque trazable con marcas y bandera."""
    items: List[Dict[str, str]] = []
    if question:
        items.append({"origen": "question", "texto": str(question)})
    items += [t for t in textos if not (question and t.get("origen") == "question")]
    marcas, por_texto, idiomas = [], [], {}
    for it in items:
        if not str(it.get("texto") or "").strip():
            continue
        r = analizar_texto(str(it["texto"]), it.get("origen", "texto"), mapa_caso)
        idiomas[r["idioma"]] = idiomas.get(r["idioma"], 0) + 1
        por_texto.append({"origen": r["origen"], "idioma": r["idioma"], "n_hallazgos": len(r["hallazgos"]), "reglas": r["reglas_aplicadas"]})
        for h in r["hallazgos"]:
            riesgo = _tokens_en_riesgo(h, tokens_tablero or [])
            if riesgo:
                h["tokens_tablero_en_riesgo"] = riesgo
            marcas.append({"tipo": f"TROPO_{h['tropo']}" + ("" if h["subtipo"] == h["tropo"] else f":{h['subtipo']}"),
                           "estado": h["estado"],
                           "evidencia": {"origen": h["evidencia"]["origen"], "fragmento": h["evidencia"]["fragmento"],
                                         "regla": h["evidencia"]["regla"], "span": h["evidencia"]["span"]},
                           "tropo": h})
            if riesgo and h["estado"] in ("DETECTADA", "POSIBLE", "NO_RESUELTO"):
                marcas.append({"tipo": "TOKEN_POSIBLEMENTE_FIGURADO_EN_TABLERO", "estado": "POSIBLE",
                               "evidencia": {"origen": h["evidencia"]["origen"], "fragmento": h["evidencia"]["fragmento"],
                                             "tropo": h["tropo"], "tokens": riesgo}})
    return resumen(marcas, len(items), por_texto, idiomas)


def bandera_de(marcas: Sequence[Dict[str, Any]]) -> str:
    est = [m["estado"] for m in marcas]
    if "NO_RESUELTO" in est:
        return "NO_RESUELTO"
    if any(e in ("DETECTADA", "POSIBLE") for e in est):
        return "MARCA"
    return "LIMPIO"


def resumen(marcas, n, por_texto, idiomas):
    conteo: Dict[str, Dict[str, int]] = {}
    for m in marcas:
        if "tropo" in m:
            c = conteo.setdefault(m["tropo"]["tropo"], {})
            c[m["estado"]] = c.get(m["estado"], 0) + 1
    return {"version": VERSION, "n_revisados": n, "marcas": list(marcas), "bandera": bandera_de(marcas), "por_texto": por_texto,
            "idiomas": idiomas, "conteo_por_tropo": conteo, "cobertura_inventario": {k: v["codigo"] for k, v in CATALOGO.items()},
            "pendiente_de_regla": [k for k, v in CATALOGO.items() if v["codigo"] == "PENDIENTE_DE_REGLA"], **CANDADOS}


# --------------------------------------------------------------------------- vecinos: tropos ↔ falacias ↔ Copi ↔ polaridad
VECINOS = ("FALACIAS", "PREGUNTA_DIRIGIDA_POST_HOC", "LOGICA_COPI", "POLARIDAD_CAUSAL")


def _frag_de(m: Dict[str, Any]) -> Tuple[Optional[str], str, str]:
    ev = m.get("evidencia")
    if isinstance(ev, dict):
        return ev.get("origen"), str(ev.get("fragmento") or ""), str(ev.get("texto") or "")
    if isinstance(ev, str):
        return None, ev, ""
    return None, "", ""


def corregir_con_vecinos(bloque_tropos: Dict[str, Any], bloques: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Serie de vecinos (SPEC_ARQUITECTURA §12 y §14): cada capa puede corregir a la otra.
      - falacia / post hoc / Copi sobre un fragmento figurado → NO_RESUELTO (no se juzga literal una figura);
      - polaridad NIEGA donde hay lítote → NO_RESUELTO (negación simple mal leída);
      - polaridad DOBLE_NEGACION_LITOTE + lítote → CONFIRMA (sin marca nueva);
      - en sentido inverso, la figura queda anotada como premisa lógica (vecino_logica).
    Devuelve la lista de correcciones. No cambia las banderas de los otros guardianes."""
    trop = [m for m in bloque_tropos.get("marcas") or [] if "tropo" in m and m["tropo"].get("bloquea_lectura_literal")
            and m["estado"] in ("DETECTADA", "POSIBLE", "NO_RESUELTO")]
    corr: List[Dict[str, Any]] = []
    for b in bloques:
        g = b.get("guardian")
        if g not in VECINOS:
            continue
        for mv in b.get("marcas") or []:
            org, frag, txt = _frag_de(mv)
            nf, ntx = _n(frag), _n(txt)
            if not (nf or ntx):
                continue
            for mt in trop:
                t = mt["tropo"]
                if org and t["evidencia"]["origen"] != org:
                    continue
                tf = _n(t["evidencia"]["fragmento"]).strip()
                if not tf or not ((nf and (tf in nf or nf in tf)) or (ntx and tf in ntx)):
                    continue
                base = {"vecino": g, "tipo_vecino": mv.get("tipo"), "tropo": t["tropo"], "fragmento": t["evidencia"]["fragmento"],
                        "origen": t["evidencia"]["origen"]}
                if g == "POLARIDAD_CAUSAL":
                    if t["tropo"] == "LITOTE" and mv.get("tipo") == "NIEGA":
                        corr.append({**base, "estado": "NO_RESUELTO",
                                     "lectura": "polaridad leyó negación simple donde hay lítote; el sentido puede ser afirmativo"})
                    elif t["tropo"] == "LITOTE" and mv.get("tipo") == "DOBLE_NEGACION_LITOTE":
                        corr.append({**base, "estado": "CONFIRMA", "lectura": "tropos y polaridad coinciden: lítote/doble negación"})
                    continue
                corr.append({**base, "estado": "NO_RESUELTO",
                             "lectura": f"la marca de {g} se apoya en lenguaje figurado ({t['tropo']}); su estructura lógica no puede evaluarse literal"})
                t.setdefault("vecino_logica", []).append({"guardian": g, "tipo": mv.get("tipo"),
                                                          "nota": "hay estructura lógica en el fragmento: la figura funciona como premisa, no solo como estilo"})
    return corr


if __name__ == "__main__":
    demo = ["Mi padre era un león en los negocios.", "La empresa floreció y luego se hundió.", "Nació pobre y murió rico.",
            "El Kremlin anunció sanciones.", "Pasó a mejor vida tras el accidente.", "Era médico en Monterrey.",
            "Es un león.", "La Corona decidió subir impuestos.", "¡Qué listo!, otra quiebra."]
    for t in demo:
        r = analizar_texto(t)
        print(f"{t!r:48} →", [(h["tropo"], h["subtipo"], h["estado"]) for h in r["hallazgos"]])
