"""Lateral TRADUCCION_SALIDA_V2 (021) — el traductor de SALIDA del motor U6.

Regla de Marco (2026-11-13 ~22:17 CST): la salida viene en LA MISMA PROSA
del input que se le da. Nunca "el token que salió y en qué porcentaje".

Corrección de Marco (2026-11-13 ~23:26 CST): la v1 era demasiado ambigua,
sonaba a horóscopo donde todo puede ser posible. La salida tiene que estar
CALIBRADA entre el input que da la persona y lo que se le regresa: cada frase
tiene que estar anclada en un momento concreto que la persona contó (un hecho)
y en cómo se mueve un tema concreto (sube, se fija, se resiste, aparece).
Si la lectura se le pudiera decir a cualquiera, está mal.

Corrección de Marco (2026-11-14 ~15:34 CST): la v2.1 seguía sonando a
oráculo de internet. El traductor encuentra QUÉ token está detrás de los
sustantivos que la persona usó, pero la lectura no se lo regresaba: nombraba
los temas con las etiquetas del catálogo ("ausencia total de limites...") en
vez de con las palabras de la persona, y la dirección era una sopa de
etiquetas sin nada en específico. La v2.2 devuelve cada tema con las
palabras de la persona (el sustantivo que ella usó en el hecho donde el tema
apareció o saltó) y dice hacia dónde va en concreto, con esos mismos
sustantivos. Y habla en la MISMA PERSONA del input (si la persona cuenta en
primera persona, la lectura es en primera persona): la v2.1 mezclaba el "yo"
de los hechos citados con el "te" del marco. Además cada hecho largo se usa
una sola vez: lo que se repite es el nombre corto, no el hecho entero.

Corrección de Marco (2026-11-14 ~15:49 CST): la v2.2 "suena poco natural".
"hacia el limbo" no se entiende: el limbo es donde la persona YA ESTÁ, no
hacia dónde va. El cierre no debe nombrar el tema central como destino
("hacia X") sino como lo que CRECE y se traga lo demás: los nudos se cierran
y el tema central se va haciendo más grande. Y falta la parte del Caldero:
la búsqueda de arquetipos SÍ está cableada y corrió (en LIMBO: 8 fuentes,
122 tokens vecinos, recibo EXECUTED), pero la parte de LLM no dio pistas
(llm: False, 0 hints); y la `entrega` del RESULT dice "traducir caminos y
luces con el input", cosa que el traductor no hacía. La v2.3 incluye esa
parte: los arquetipos que se prenden (las luces arquetipo/monomito de la
entrega) y los caminos abiertos (dónde está y hacia dónde pudiera estar).
Los caminos se nombran con los mismos nombres que ya usa la lectura.

Por eso la v2.8 tiene dos salidas separadas:
  - `lectura`: prosa en la persona y las palabras del input, CALIBRADA.
    Cada tema se nombra con el sustantivo de la persona; cada afirmación
    trae su ancla (el hecho donde apareció o saltó); el cierre dice el
    crecimiento del tema central, no un destino. Sin nombres de familias,
    sin tokens, sin
    porcentajes, sin pesos, sin grados, sin IDs de corte, sin "H1"/"H2",
    sin nombres, fechas ni lugares. La ambigüedad que queda es solo la del
    futuro (no se predice un evento ni una fecha), no la del pasado (todo
    lo que se dice viene de lo que la persona contó).
  - `anexo`: todos los números (H1, H2, pesos, proporciones, giro, cometa,
    caminos y arquetipos del Caldero con sus IDs). Va al repo, NUNCA a la
    persona.

Corrección de Marco (2026-11-14 ~16:56 CST): la v2.4 "no se entiende en lo
mínimo": "El sabio se me prendió" no le dice nada a la persona — ¿él qué
sabe de estas cosas? No sirve decirle qué se prendió ni qué parte del
motor se manejó; el usuario no tiene por qué saber las partes (ni el
backend ni el front end). Él contó una historia y se le devuelve la
historia: qué está pasando, qué va a pasar y hacia dónde se perfila, en
sus palabras ("debido a lo que estás contando, si las cosas siguen así,
se perfila a que pasen este tipo de cosas"). La v2.5 QUITA las frases de
arquetipos de la lectura: las luces van solo al anexo. La lectura solo
lleva lo que la persona dijo (sus sustantivos y sus hechos) más la
dirección. Nada de etiquetas del catálogo ni vocabulario del motor.

Corrección de Marco (2026-11-14 ~16:59 CST): la v2.5 "no se entiende
nada". Revisada frase por frase: los verbos son del motor, no verbos
humanos. "Lo que me jala es el limbo" trata un estado como fuerza que
jala; "eso se me va acercando / se me resiste / se me van cerrando"
no le dice nada a la persona (¿acercándose a qué?, ¿resistiéndose a
qué?); "mi tema ya se fijó" no es nada que alguien diga de su vida;
"los tres siguen abiertos" no dice qué está abierto. La v2.6 cambia
los verbos: el tema central es un ESTADO ("estoy en el limbo"), el
salto es "se hizo más fuerte cuando...", los nudos "me siguen
pesando" o "no se me quitan", el cometa "todo se me vino encima
cuando...", el régimen "esto ya no es de un día: ya se quedó así", y
el cierre es la proyección en la fórmula de Marco: "si las cosas
siguen así, se perfila a que...". Los caminos del Caldero también
salen de la lectura (van solo al anexo): la proyección la dice el
cierre. La lectura solo dice qué está pasando, qué va a pasar y hacia
dónde se perfila, en las palabras de la persona, con verbos que
alguien diría de su vida.

Corrección de Marco (2026-11-14 ~20:25 CST): la v2.6 "no me gustó".
"Estás en el limbo" no dice qué es el limbo en sentido normal: para
nosotros es estar a la mitad, en el umbral. "Se hizo más fuerte" no
dice qué se hizo más fuerte ni qué significa. Y sigue siendo mucha
explicación que no tiene sentido, asumiendo que el usuario sabe cómo
lo ve el motor por dentro. La v2.7 cambia la FORMA: la lectura es
CORTA y en SEGUNDA persona (el que lee le habla a la persona), con la
fórmula de Marco: "Basado en lo que me contaste, te perfilas a...;
estás a la mitad, en el umbral: [desempaque]; a través de estas
situaciones: [H2, nudos]; muy probablemente [nuevo] te pegue más
fuerte, junto con todo eso; y eso puede ir creciendo con el tiempo si
las cosas siguen así". El cometa y el régimen ya no se narran en la
lectura (van solo al anexo). Los nombres se pasan a segunda persona
por diccionario de formas exactas; lo que no se reconoce queda como
está (palabra de la persona, no invento).

Corrección de Marco (2026-11-14 ~20:31 CST): la v2.7 "tiene más
sentido, pero no dijiste nada". La forma ya está bien (la fórmula, la
segunda persona, el limbo a la mitad y en el umbral), pero la lectura
repite lo que él ya sabe: se salió, ella estaba distante, fue culero,
ella ya no lo quería. No dice nada que él no sepa. La v2.8 añade los
HALLAZGOS del motor, cada uno con su evidencia: el tema central
creció y está en su punto más alto en el último corte ("el limbo
creció: antes no estaba así de grande"); lo nuevo no estaba antes
("el duelo no estaba antes: apareció apenas ahorita" — antes no había
duelo, solo distancia y enojo); y la alerta de cometa de la proyección
("se perfila a que te venga otra oleada como aquella vez que ya no te
quería" — en el último corte llegó un pulso de masa en 2+ nudos, se
perfila otra oleada en los siguientes 1-3 cortes). La proyección se
lee de proyectar_gravedad; la alerta va también al anexo.

Contrato: motor/TRADUCCION_SALIDA_V1.md
VERSION = "v2.8_20261114"
"""

import json
import os
import re

VERSION = "v2.8_20261114"
CONTRATO = "TRADUCCION_SALIDA_V1"

_CATALOGO = None


def _cargar_catalogo(path=None):
    global _CATALOGO
    if _CATALOGO is not None:
        return _CATALOGO
    if path is None:
        base = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base, "patterns_final_v14.json")
    with open(path, encoding="utf-8") as f:
        _CATALOGO = json.load(f)
    return _CATALOGO


_PREFIJOS_TECNICOS = (
    "subtipo:",
    "patron inspirado en la idea de ",
    "patron inspirado en ",
)
_COLGADAS = {"sin", "pero", "el", "de", "y", "que", "con", "para", "por",
             "un", "una", "los", "las", "se", "su", "al", "del", "en", "a"}


def _descripcion_llana(familia, catalogo):
    """La descripción del catálogo, limpia para usar en prosa.

    Quita prefijos técnicos del catálogo ("Subtipo:", "Patron inspirado en
    la idea de...", "Mannheim N:"). Se toma la primera frase; si es una
    lista con comas y es larga, la primera cláusula; si sigue larga, la
    parte antes de los dos puntos. Nunca termina a media frase.
    En v2.2 solo es respaldo (cuando no hay hecho que ancle el tema) y
    para nombrar lo nuevo en Z cuando es una palabra llana.
    """
    d = (catalogo.get(familia) or {}).get("description") or ""
    d = d.split("(")[0].strip()
    d = d.split(".")[0].strip()
    bajo = d.lower()
    for pref in _PREFIJOS_TECNICOS:
        if bajo.startswith(pref):
            d = d[len(pref):].strip()
            bajo = d.lower()
            break
    d = re.sub(r"^mannheim \d+:\s*", "", d, flags=re.IGNORECASE)
    if len(d) > 60 and "," in d:
        primera = d.split(",")[0].strip()
        if len(primera) >= 20:
            d = primera
    if len(d) > 90 and ":" in d:
        antes = d.split(":")[0].strip()
        if len(antes) >= 20:
            d = antes
    if len(d) > 90:
        d = d[:90].rsplit(" ", 1)[0]
    while d.split() and d.split()[-1].lower().strip(".,") in _COLGADAS:
        d = " ".join(d.split()[:-1])
    if not d:
        return "algo que se mueve en tu vida"
    return d[:1].lower() + d[1:]


def _registro(entrada):
    """Persona del input: 'primera' si cuenta en primera persona, si no 'tercera'.

    La salida va en LA MISMA PERSONA del input (regla de Marco). La v2.1
    usaba segunda persona ("te") con hechos citados en primera ("yo") y
    eso mezclaba las voces.
    """
    hechos = []
    if entrada:
        for c in entrada.get("cuts", []):
            hechos.append(c.get("hecho", ""))
    texto = " ".join(hechos).lower()
    if any(w in texto for w in (" yo ", " me ", "estaba", "me pasó", "me paso")):
        return "primera"
    return "tercera"


def _hecho_del_corte(entrada, cut_id):
    if not entrada:
        return ""
    for c in entrada.get("cuts", []):
        if c.get("id") == cut_id or c.get("corte") == cut_id:
            return c.get("hecho", "")
    return ""


def _hecho_corto(entrada, cut_id, max_chars=140):
    """El hecho de un corte, recortado a una sola frase corta.

    Se toma solo la primera oración (el hecho puede traer varias) y se
    recorta a max_chars. Con minúscula inicial porque se embebe tras
    "cuando".
    """
    h = _hecho_del_corte(entrada, cut_id)
    if not h:
        return ""
    h = re.split(r"\.\s+(?=[A-ZÁÉÍÓÚÑ])", h.strip())
    if not h:
        return ""
    primera_oracion = h[0].strip()
    if len(h) > 1:
        # Se tomó solo la primera oración: se le devuelve su punto.
        primera_oracion = primera_oracion.rstrip(".") + "."
    h = primera_oracion
    if len(h) > max_chars:
        h = h[:max_chars].rsplit(" ", 1)[0] + "..."
    if h:
        h = h[:1].lower() + h[1:]
    return h


def _nombre_propio(hecho):
    """El sustantivo de la persona para un tema: la última cláusula del hecho.

    Toma la última oración del hecho y, dentro de ella, la última cláusula
    (tras la última coma). Si dice "como en X" o "ya no X", se queda con X.
    Es el nombre que la persona misma usó, no la etiqueta del catálogo.
    Ejemplos: "me siento como en el limbo" -> "el limbo";
    "me dijo que ya tenía mucho tiempo que ya no me quería" -> "ya no me quería".
    Conservador: si la última cláusula no parece un sustantivo claro (empieza
    con dígito, trae paréntesis, es fragmento o es demasiado larga), devuelve
    "" para que el llamador use la descripción llana del catálogo.
    """
    if not hecho:
        return ""
    h = hecho.strip()
    oraciones = [p.strip() for p in re.split(r"\.\s+(?=[A-ZÁÉÍÓÚÑ])", h) if p.strip()]
    if not oraciones:
        return ""
    ult = oraciones[-1]
    claus = [c.strip() for c in ult.split(",") if c.strip()]
    c = claus[-1] if claus else ult
    m = re.search(r"como en (.+)$", c)
    if m:
        c = m.group(1).strip()
    else:
        m = re.search(r"(ya no .+)$", c)
        if m:
            c = m.group(1).strip()
    c = re.sub(r"^yo\s+", "", c)
    if len(c) > 45:
        # No recortar a las últimas palabras (sale fragmento): probar la
        # primera cláusula de la última oración; si tampoco sirve, nada.
        c = claus[0] if claus else ""
        if len(c) > 45:
            return ""
    if not c or len(c) < 8:
        return ""
    if c[0].isdigit() or "(" in c or ")" in c:
        return ""
    c = c.rstrip(".;:")
    if not c:
        return ""
    return c[:1].lower() + c[1:]


def _como_nombre(nombre):
    """El nombre como sujeto de frase: 'el limbo' tal cual, lo demás con 'eso de que'."""
    if not nombre:
        return "eso"
    if nombre.split()[0] in ("el", "la", "los", "las", "un", "una", "eso", "esto"):
        return nombre
    return "eso de que " + nombre


def _con_articulo(nombre):
    """'duelo' -> 'el duelo'; deja tal cual lo que ya trae artículo o es frase.

    Solo para nombres de una palabra (los masculinos en juego: duelo, héroe).
    Las frases con varias palabras ya se valen solas.
    """
    if not nombre:
        return nombre
    if " " in nombre:
        return nombre
    if nombre.split()[0] in ("el", "la", "los", "las", "un", "una", "eso", "esto"):
        return nombre
    return "el " + nombre


_ACENTOS = {"heroe": "héroe"}


def _nombre_arquetipo(fam, catalogo=None):
    """El nombre llano de una familia arquetipo/monomito, sin el prefijo.

    "arquetipo_el_amante" -> "el amante";
    "monomito_05_cruce_del_primer_umbral" -> "cruce del primer umbral".
    Solo para familias arquetipo_/monomito_; si no lo es, devuelve "".
    Acentos correctos ("heroe" es "héroe"): sin el acento el nombre
    coincide con el ID de familia "heroe" y el guardia lo marca. Si el
    nombre todavía contiene un ID de familia (p. ej. "aliado" en "pruebas
    aliados y enemigos"), se usa la descripción llana del catálogo.
    """
    if not fam:
        return ""
    if fam.startswith("arquetipo_"):
        resto = fam[len("arquetipo_"):]
    else:
        m = re.match(r"monomito_\d+_(.+)$", fam)
        if not m:
            return ""
        resto = m.group(1)
    nombre = resto.replace("_", " ").strip()
    if not nombre:
        return ""
    nombre = " ".join(_ACENTOS.get(p, p) for p in nombre.split())
    if catalogo is not None:
        bajo = nombre.lower()
        for fid in catalogo:
            if fid.lower() in bajo:
                return _descripcion_llana(fam, catalogo)
    return _con_articulo(nombre)


def _movimiento(serie):
    """Describe el movimiento de una serie de activación en palabras.

    Devuelve (verbo, salto_corte_idx_o_None): el verbo es 'sube', 'fijo' o
    'baja'; el índice es el corte donde pegó el salto más grande (si lo hay).
    """
    if not serie or len(serie) < 2:
        return ("fijo", None)
    primero, ultimo = serie[0], serie[-1]
    saltos = [serie[i + 1] - serie[i] for i in range(len(serie) - 1)]
    idx_salto = max(range(len(saltos)), key=lambda i: saltos[i])
    salto = saltos[idx_salto]
    base = max(abs(primero), 0.01)
    if ultimo > primero * 1.5 and ultimo - primero > 0.02:
        verbo = "sube"
    elif ultimo < primero * 0.66 and primero - ultimo > 0.02:
        verbo = "baja"
    else:
        verbo = "fijo"
    # salto grande: sube más de la mitad de lo que subió en total, y es visible
    if salto > 0.02 and salto > 0.4 * max(ultimo - primero, 0.01):
        return (verbo, idx_salto + 1)
    return (verbo, None)


def _verificar_lectura(lectura, catalogo):
    """Devuelve la lista de violaciones (vacía = la lectura es limpia)."""
    viol = []
    bajo = lectura.lower()
    for fam in catalogo:
        if fam.lower() in bajo:
            viol.append(fam)
    for pat in (r"\d+%", r"\d+\.\d+", r"°", r"\bH1\b", r"\bH2\b",
                r"\bC\d+_", r"\btop\s*\d", r"\bpeso\b", r"\btoken\b"):
        if re.search(pat, lectura):
            viol.append(pat)
    return viol


_MARCADORES_ACCION = {"me", "te", "se", "nos", "os", "le", "yo", "tú", "él",
                      "ella", "nosotros", "que", "cuando", "donde", "como",
                      "fue", "era", "es", "está", "son", "están", "han", "ha"}


def _momento_corto(entrada, cut_id):
    """El momento corto de un corte, para anclar un momento sin repetir el hecho entero.

    Cadena: (1) la última cláusula de la primera oración, si parece un
    momento (tiene marca de acción: pronombre o relativo, 15-45 caracteres);
    (2) si no, el nombre propio del hecho, si parece un momento; (3) si no,
    la primera oración entera. Así "parís y Londres ante las cortes" (un
    fragmento de lugar, sin verbo) no queda como momento: se usa la oración
    completa. Sin el punto final: la frase que lo embebe pone el suyo.
    """
    hecho = _hecho_del_corte(entrada, cut_id)
    if not hecho:
        return ""
    h = hecho.strip()
    oraciones = [p.strip() for p in re.split(r"\.\s+(?=[A-ZÁÉÍÓÚÑ])", h) if p.strip()]
    if not oraciones:
        return ""
    primera = oraciones[0]
    claus = [c.strip() for c in re.split(r",\s+|\s+y\s+", primera) if c.strip()]
    c = claus[-1] if claus else primera
    c = re.sub(r"^yo\s+", "", c)
    c = c.rstrip(".;:")
    palabras = set(c.lower().split())
    if c and 15 <= len(c) <= 45 and palabras & _MARCADORES_ACCION:
        return c[:1].lower() + c[1:]
    np = _nombre_propio(hecho)
    if np and 15 <= len(np) <= 45 and set(np.lower().split()) & _MARCADORES_ACCION:
        return np
    entero = _hecho_corto(entrada, cut_id)
    if entero:
        return entero.rstrip(".")
    return ""


def _sin_punto_final(txt):
    """Quita un solo punto final ('.'), sin tocar '...'."""
    if txt and txt.endswith(".") and not txt.endswith(".."):
        return txt[:-1]
    return txt


def _estado_central(nombre, primera):
    """El tema central como ESTADO, no como fuerza que jala.

    "Estoy en el limbo", no "lo que me jala es el limbo". Si el nombre es
    una cláusula ("eso de que..."), "lo que manda es..." (eso es lo que
    manda en la vida, no una fuerza abstracta).
    """
    if not nombre:
        return "Lo que manda es lo que lleva."
    if nombre.startswith(("el ", "la ", "los ", "las ")):
        return f"Estoy en {nombre}." if primera else f"Está en {nombre}."
    if " " not in nombre:
        art = _con_articulo(nombre)
        return f"Estoy en {art}." if primera else f"Está en {art}."
    return f"Lo que manda es {_como_nombre(nombre)}."


_SEGUNDA = {
    # pronombres y posesivos
    "yo": "", "me": "te", "mi": "tu", "mis": "tus", "mí": "ti",
    # pretérito, 1a persona -> 2a
    "opté": "optaste", "junté": "juntaste", "salí": "saliste",
    "fui": "fuiste", "dije": "dijiste", "vi": "viste",
    "golpeé": "golpeaste", "saqué": "sacaste", "traté": "trataste",
    "hice": "hiciste", "tuve": "tuviste", "pude": "pudiste",
    "quise": "quisiste", "supe": "supiste", "vine": "viniste",
    "puse": "pusiste", "di": "diste", "estuve": "estuviste",
    "dejé": "dejaste", "llegué": "llegaste", "empecé": "empezaste",
    "pasé": "pasaste", "viví": "viviste", "sentí": "sentiste",
    "quedé": "quedaste", "volví": "volviste", "tomé": "tomaste",
    # presente, 1a -> 2a
    "siento": "sientes", "estoy": "estás", "tengo": "tienes",
    "quiero": "quieres", "sé": "sabes", "puedo": "puedes",
    "voy": "vas", "digo": "dices", "hago": "haces", "veo": "ves",
    "creo": "crees", "salgo": "sales", "sigo": "sigues",
    # infinitivo + me -> + te
    "salirme": "salirte", "juntarme": "juntarte", "irme": "irte",
    "sentirme": "sentirte", "quedarme": "quedarte", "verme": "verte",
    "llevarme": "llevarte",
}


def _a_segunda_persona(txt):
    """Pasa un texto en primera persona a segunda (tú), lo mejor que se puede.

    Conversión por diccionario de formas exactas; lo que no se reconoce
    queda como está (sigue siendo palabra de la persona, no invento).
    Solo se usa cuando la lectura va en segunda persona.
    """
    if not txt:
        return txt

    def _conv(m):
        w = m.group(0)
        rep = _SEGUNDA.get(w.lower())
        if rep is None:
            return w
        if not rep:
            return ""
        if w[:1].isupper():
            return rep[:1].upper() + rep[1:]
        return rep

    out = re.sub(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+", _conv, txt)
    out = re.sub(r"\s{2,}", " ", out).strip()
    return out


def _primera_clausula_accion(hecho):
    """La primera cláusula del hecho que tiene verbo (para el desempaque).

    "Yo opté por salirme, sacar hoy mis cosas, me siento como en el
    limbo" -> "opté por salirme". Si la primera cláusula es solo tiempo
    ("en 1761", "con 5 años"), se busca la siguiente con verbo.
    """
    if not hecho:
        return ""
    h = hecho.strip()
    oraciones = [p.strip() for p in re.split(r"\.\s+(?=[A-ZÁÉÍÓÚÑ])", h) if p.strip()]
    if not oraciones:
        return ""
    primera = oraciones[0]
    claus = [c.strip() for c in re.split(r",\s+|\s+y\s+", primera) if c.strip()]
    for c in claus:
        c2 = re.sub(r"^yo\s+", "", c).rstrip(".;:")
        if not c2 or len(c2) < 8:
            continue
        palabras = set(c2.lower().split())
        # Verbo: marca de acción o terminación verbal.
        if palabras & _MARCADORES_ACCION or re.search(
                r"\b\w+(é|ó|í|aste|iste|aba|ía|ando|iendo|ar|er|ir)\b", c2.lower()):
            return c2[:1].lower() + c2[1:]
    return ""


def _es_estado(nombre):
    """Un nombre que es un estado (sustantivo corto), no una cláusula.

    "el limbo", "duelo": estado. "eso de que...", descripciones largas: no.
    """
    if not nombre:
        return False
    if nombre.startswith(("el ", "la ", "los ", "las ")):
        return " que " not in nombre and len(nombre.split()) <= 3
    return " " not in nombre


def traducir(result, entrada=None, catalogo=None):
    """Traduce un RESULT del motor a prosa calibrada en el registro del input.

    result: dict RESULT del motor (con H1, H2, movimiento_de_fondo).
    entrada: dict de la entrada original (para el registro y los hechos).
    Devuelve {"lectura": str, "anexo": dict, "violaciones": list}.
    """
    if catalogo is None:
        catalogo = _cargar_catalogo()
    registro = _registro(entrada)
    primera = registro == "primera"

    h1 = (result.get("H1") or {}).get("family")
    h2 = (result.get("H2") or {}).get("family")
    mf = result.get("movimiento_de_fondo") or {}
    sf = mf.get("series_familias") or {}

    grav = None
    try:
        from lateral_comportamiento_post_meseta_v1 import leer_resultado
        grav = (leer_resultado(result) or {}).get("gravedad") or {}
    except Exception:
        grav = {}

    cortes = (entrada or {}).get("cuts", [])
    n_cortes = len(cortes)
    ultimo_cut_id = cortes[-1].get("id") if cortes else None

    def serie_de(fam):
        return (sf.get(fam) or {}).get("serie_activacion", [])

    def primera_de(fam):
        return (sf.get(fam) or {}).get("primera_aparicion")

    # Cada hecho largo se usa una sola vez en la lectura; los nombres cortos
    # sí se repiten. Así un mismo momento no se cita tres veces.
    usados = set()

    def hecho_unico(cut_id):
        if not cut_id or cut_id in usados:
            return ""
        h = _hecho_corto(entrada, cut_id)
        if h:
            usados.add(cut_id)
        return h

    def ancla_de(fam):
        """(cut_id, nombre) del ancla de un tema: salto, si no primera aparición.

        El nombre sale del hecho de ese corte, en palabras de la persona,
        pero solo cuando el input es en primera persona: en un input formal
        (biografía en tercera persona) el nombre es la descripción llana del
        catálogo, que es la prosa de ese input. Si no hay hecho, respaldo:
        la descripción llana del catálogo.
        """
        _, idx_salto = _movimiento(serie_de(fam))
        cid = None
        if idx_salto is not None and cortes:
            cid = cortes[idx_salto].get("id")
        if not cid:
            cid = primera_de(fam)
        nombre = ""
        if primera and cid:
            nombre = _nombre_propio(_hecho_del_corte(entrada, cid))
        if not nombre:
            nombre = _descripcion_llana(fam, catalogo)
        return cid, nombre

    frases = []

    # v2.7: la lectura es CORTA y en SEGUNDA persona cuando el input es en
    # primera (el que lee le habla a la persona). En tercera persona
    # (biografía) se queda en tercera. Nada de recuento de partes del
    # motor, nada de "se hizo más fuerte" sin decir qué ni qué significa,
    # nada de "estás en el limbo" sin decir qué es el limbo en sentido
    # normal (a la mitad, en el umbral). La fórmula de Marco:
    #   "Basado en lo que me contaste, te perfilas a [dirección].
    #    Estás a la mitad, en el umbral: [desempaque].
    #    [Tema] creció: antes no estaba así de grande.
    #    A través de estas situaciones: [H2, nudos].
    #    [Nuevo] no estaba antes: apareció apenas ahorita.
    #    Muy probablemente [nuevo] te pegue más fuerte, junto con todo eso.
    #    Y se perfila a que te venga otra oleada como aquella vez que [cometa].
    #    Y eso puede ir creciendo con el tiempo si las cosas siguen así."
    segunda = primera

    def a_persona(txt):
        """El nombre en la persona de la lectura (2a o 3a)."""
        if segunda:
            return _a_segunda_persona(txt)
        return txt

    # --- Datos (nombres en palabras de la persona, sin frases todavía) ---
    nombre1 = ""
    cid1 = None
    if h1:
        cid1, nombre1 = ancla_de(h1)
    nombre2 = ""
    if h2 and h2 != h1:
        _, nombre2 = ancla_de(h2)
    # Lo que apareció apenas en el último momento (solo en Z).
    nuevos_z = []
    for fam, s in sf.items():
        if s.get("primera_aparicion") == ultimo_cut_id and s.get("clase") == "PICO":
            nuevos_z.append(fam)
    vistos = set()
    nuevos_txt = []
    nombre_nuevo = ""
    for fam in nuevos_z:
        d = _descripcion_llana(fam, catalogo)
        clave = d.split(",")[0].strip().lower()
        if clave in vistos:
            continue
        vistos.add(clave)
        nuevos_txt.append(d)
    if nuevos_txt:
        d0 = nuevos_txt[0]
        if len(d0.split()) <= 2:
            nombre_nuevo = d0
        else:
            nombre_nuevo = _nombre_propio(_hecho_del_corte(entrada, ultimo_cut_id)) or d0
    # Los nudos: nombres en palabras de la persona (máximo 3).
    nudos_todos = grav.get("nudos") or []
    nudos = sorted(nudos_todos, key=lambda n: abs(n.get("pendiente") or 0), reverse=True)[:3]
    nombres_nudos = []
    vistos_nudo = set()
    for n in nudos:
        fam = n.get("familia")
        if not fam:
            continue
        primera_c = n.get("primera_aparicion")
        nombre = ""
        if primera and primera_c:
            nombre = _nombre_propio(_hecho_del_corte(entrada, primera_c))
        if not nombre:
            nombre = _descripcion_llana(fam, catalogo)
        estado = n.get("estado")
        clave_nudo = (nombre, estado)
        if clave_nudo in vistos_nudo:
            continue
        vistos_nudo.add(clave_nudo)
        nombres_nudos.append(nombre)
    # El cometa y el régimen van solo al anexo (la lectura ya no los narra).
    cometa = grav.get("cometa") or {}
    en_meseta = None
    try:
        from lateral_comportamiento_post_meseta_v1 import leer_resultado as _lr
        en_meseta = (_lr(result) or {}).get("en_meseta")
    except Exception:
        en_meseta = None
    # La proyección (alerta de cometa): si en el último corte llegó un
    # pulso de masa en 2+ nudos, se perfila otra oleada en los siguientes
    # 1-3 cortes. Es la predicción del motor, no un evento ni una fecha.
    alerta_cometa = None
    try:
        from lateral_comportamiento_post_meseta_v1 import proyectar_gravedad as _pg
        alerta_cometa = ((_pg(result) or {}).get("cometa_previsto") or {}).get("alerta")
    except Exception:
        alerta_cometa = None

    # Caminos y luces del Caldero: solo van al anexo.
    entrega = result.get("entrega") or {}
    caminos = entrega.get("caminos") or []
    luces = []
    for lado in ("luces_P", "luces_A", "luces_C"):
        luces.extend(entrega.get(lado) or [])

    # --- Frases ---
    # 1. Dirección: "Basado en lo que me contaste, te perfilas a..."
    if nombre1:
        if _es_estado(nombre1):
            n1 = nombre1 if nombre1.startswith(("el ", "la ", "los ", "las ")) else _con_articulo(nombre1)
            if segunda:
                frases.append(f"Basado en lo que me contaste, te perfilas a quedarte en {n1}.")
            else:
                frases.append(f"Basado en lo que se cuenta, se perfila a quedarse en {n1}.")
        else:
            if segunda:
                frases.append(f"Basado en lo que me contaste, te perfilas a que {_como_nombre(nombre1)} se te haga más grande.")
            else:
                frases.append(f"Basado en lo que se cuenta, se perfila a que {_como_nombre(nombre1)} se le haga más grande.")
    # 2. Desempaque del tema (solo si es un estado): "Estás a la mitad,
    # en el umbral". El limbo en sentido normal es estar a la mitad, en
    # el umbral: ya te saliste, pero no llegaste a ningún lado.
    if nombre1 and _es_estado(nombre1):
        n1 = nombre1 if nombre1.startswith(("el ", "la ", "los ", "las ")) else _con_articulo(nombre1)
        claus = _primera_clausula_accion(_hecho_del_corte(entrada, cid1)) if cid1 else ""
        claus = a_persona(claus) if claus else ""
        limpia = claus and " nos " not in f" {claus} " and " me " not in f" {claus} "
        if segunda:
            if limpia:
                frases.append(f"Estás a la mitad, en el umbral: {claus}, pero sigues en {n1}.")
            else:
                frases.append(f"Estás a la mitad, en el umbral, pero sigues en {n1}.")
        else:
            if limpia:
                frases.append(f"Está a la mitad, en el umbral: {claus}, pero sigue en {n1}.")
            else:
                frases.append(f"Está a la mitad, en el umbral, pero sigue en {n1}.")
    # 3. Hallazgo: el tema central creció y está en su punto más alto
    # en el último corte (la serie sube y el último valor es el máximo).
    # "El limbo creció: antes no estaba así de grande" — con el sujeto
    # nombrado, no "se hizo más fuerte" sin decir qué.
    if nombre1:
        _s1 = serie_de(h1)
        if len(_s1) >= 2 and _s1[-1] == max(_s1) and _s1[-1] > _s1[-2]:
            _subj = _como_nombre(nombre1)
            _subj = _subj[:1].upper() + _subj[1:]
            frases.append(f"{_subj} creció: antes no estaba así de grande.")

    # 3. Situaciones: "A través de estas situaciones: H2, nudos".
    situaciones = []
    if nombre2:
        situaciones.append(a_persona(_como_nombre(nombre2)))
    for nm in nombres_nudos:
        situaciones.append(a_persona(_como_nombre(nm)))
    situaciones = list(dict.fromkeys(situaciones))
    if situaciones:
        if len(situaciones) == 1:
            frases.append(f"A través de esta situación: {situaciones[0]}.")
        else:
            lista_sit = ", ".join(situaciones[:-1]) + " y " + situaciones[-1]
            frases.append(f"A través de estas situaciones: {lista_sit}.")
    # 5. Hallazgo: lo nuevo no estaba antes (primera aparición en el
    # último corte). "El duelo no estaba antes: apareció apenas ahorita"
    # — es un hallazgo, no una etiqueta: antes no había duelo, solo
    # distancia y enojo; el duelo empezó cuando se salió.
    if nombre_nuevo:
        if " " not in nombre_nuevo:
            _nn = _con_articulo(nombre_nuevo)
        else:
            _nn = _como_nombre(nombre_nuevo)
        _nn = _nn[:1].upper() + _nn[1:]
        if segunda:
            frases.append(f"{_nn} no estaba antes: apareció apenas ahorita.")
        else:
            frases.append(f"{_nn} no estaba antes: apareció apenas al final.")
    # 6. Proyección: "Muy probablemente [nuevo] te pegue más fuerte,
    # junto con todo eso." El "junto con todo eso" solo si hay
    # situaciones nombradas a las que referirse.
    if nombre_nuevo:
        _junto = ", junto con todo eso" if situaciones else ""
        if segunda and " " not in nombre_nuevo:
            frases.append(f"Muy probablemente {_con_articulo(nombre_nuevo)} te pegue más fuerte{_junto}.")
        else:
            frases.append(f"Muy probablemente {_con_articulo(nombre_nuevo)} se haga más grande{_junto}.")
    # 7. Hallazgo: alerta de cometa (la proyección). Si en el último corte
    # llegó un pulso de masa en 2+ nudos, se perfila otra oleada como la
    # del cometa que ya pasó (el momento en que todo se le vino encima).
    if alerta_cometa:
        _mom = _momento_corto(entrada, cometa["corte"]) if cometa.get("corte") else ""
        _mom = a_persona(_mom) if _mom else ""
        if _mom:
            if segunda:
                frases.append(f"Y se perfila a que te venga otra oleada como aquella vez que {_mom}.")
            else:
                frases.append(f"Y se perfila a que le venga otra oleada como aquella vez que {_mom}.")
    # 8. Cierre: el crecimiento con el tiempo, con su condición.
    frases.append("Y eso puede ir creciendo con el tiempo si las cosas siguen así.")


    lectura = " ".join(frases)
    viol = _verificar_lectura(lectura, catalogo)
    if viol:
        lectura = ("Lo que se ve en esta vida es una dirección que se va armando "
                   "con lo que la acompaña, no con una sola cosa.")

    anexo = {
        "H1": h1,
        "H2": h2,
        "sol_peso_Z": (grav.get("sol") or {}).get("peso_Z"),
        "n_nudos": len(nudos),
        "n_capturados": len(grav.get("capturados") or []),
        "n_siendo_jalados": len(grav.get("siendo_jalados") or []),
        "n_resisten": len(grav.get("resisten") or []),
        "proporcionalidad": grav.get("proporcionalidad"),
        "alerta_cometa": bool(alerta_cometa),
        "cometa": cometa.get("corte"),
        "cometa_nudos": cometa.get("nudos_que_suben"),
        "cometa_salto": cometa.get("salto_total"),
        "punto_no_considerado": (grav.get("punto_no_considerado") or {}).get("familia"),
        "nuevos_en_Z": nuevos_z,
        "en_meseta": en_meseta,
        "registro": registro,
        "version": VERSION,
        "caminos": caminos,
        "arquetipos_luces": list(dict.fromkeys(
            fam for fam in luces if _nombre_arquetipo(fam, catalogo))),
    }
    return {"lectura": lectura, "anexo": anexo, "violaciones": viol}


def observar(case, motor, pred):
    """Puente post-predictor: traduce el RESULT sellado a prosa. No decide H."""
    return traducir(pred, case)
