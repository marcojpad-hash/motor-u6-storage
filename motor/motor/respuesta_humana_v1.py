"""respuesta_humana_v1.py — respuesta en prosa a LA pregunta de la persona.

Proyecto inputs-humanos (gh-issue-48, agente-cero-costo, 2026-11-11, Puta3 a
Grok; objetivo de Mj): ida y vuelta con input humano. Humano pregunta en
prosa -> traducción al JSON del motor -> motor -> respuesta en prosa humana
CONCORDANTE con lo que preguntó. Sombrero blanco vigila ambos lados.

Este módulo es la pieza (2) del issue: resultado -> respuesta en prosa.
No es el traductor de salida (lateral_traduccion_salida_v1.py v2.8), que es
una LECTURA (descripción de estados con plantillas fijas). Esto es una
RESPUESTA: contesta LA pregunta hecha.

Reglas (gh-issue-48 + correcciones de Marco):
  (a) Responde LA pregunta hecha: si pregunta "¿qué va a pasar?" responde
      escenarios/apuesta; si "¿por qué?" responde hipótesis y evidencia;
      si "¿qué hago?" lo dice como condicionado. Si la pregunta es ambigua,
      lo dice y da la lectura principal.
  (b) Porcentajes desde valores 0.01-0.999 (x100) como SOPORTE estructural,
      nunca como probabilidad y nunca rank_fusion crudo.
  (c) No cambia H1/H2/margen/grado. No decide H. No reescribe el RESULT.
      El módulo es una función pura sobre el RESULT sellado + la entrada.
  (d) Dice el grado (firme/ajustada/frágil) y qué cortes quedan sin explicar.
  (e) La evidencia se CITA en las palabras de la persona y en orden
      cronológico (método del traductor 021: texto real del corte, sin
      re-narrar ni coser fragmentos con "eso de que"). Sin etiquetas del
      catálogo y sin vocabulario de física del motor.
  (f) Guardia de CONCORDANCIA: tipo de pregunta <-> tipo de respuesta; la
      respuesta cita la evidencia del result y no inventa hechos;
      FALLO_CONCORDANCIA con motivo.
  (g) Verificación de fidelidad + narratividad: cada afirmación rastreable
      a un corte o al result; se lee como historia en orden.

Bypass: RESPUESTA_HUMANA=0 apaga el módulo con estado visible
APAGADA_POR_FLAG (nunca en silencio). Por defecto activo.

Puente post-corrida: observar(case, motor, pred) -> responder(pred, case).
El runner (correr_estandar.py) lo llama después de que run() sella el
RESULT; el módulo solo lee el RESULT y la entrada, no escribe H.

Contrato: CONTRATO_SALIDA_LLM.txt
VERSION = "v1.0_20261117"
"""

import json
import os
import re
import unicodedata

VERSION = "v1.0_20261117"
CONTRATO = "CONTRATO_SALIDA_LLM"

_CATALOGO = None


def esta_activa():
    """True salvo que RESPUESTA_HUMANA=0 (apagado visible, no silencioso)."""
    return os.environ.get("RESPUESTA_HUMANA", "1") != "0"


def _cargar_catalogo(path=None):
    global _CATALOGO
    if _CATALOGO is not None:
        return _CATALOGO
    if path is None:
        base = os.path.dirname(os.path.abspath(__file__))
        for cand in (os.path.join(base, "patterns_final_v14.json"),
                     os.path.join(os.path.dirname(base), "patterns_final_v14.json")):
            if os.path.isfile(cand):
                path = cand
                break
    if path is None or not os.path.isfile(path):
        _CATALOGO = {}
        return _CATALOGO
    with open(path, encoding="utf-8") as f:
        _CATALOGO = json.load(f)
    return _CATALOGO


def _norm(s):
    """Minúsculas sin acentos, para clasificar sin depender de la ortografía."""
    return "".join(ch for ch in unicodedata.normalize("NFD", str(s).lower())
                   if unicodedata.category(ch) != "Mn")


_PREFIJOS_TECNICOS = (
    "subtipo:",
    "patron inspirado en la idea de ",
    "patron inspirado en ",
)
_COLGADAS = {"sin", "pero", "el", "de", "y", "que", "con", "para", "por",
             "un", "una", "los", "las", "se", "su", "al", "del", "en", "a"}


def _descripcion_llana(familia, catalogo):
    """La descripción del catálogo, limpia para usar en prosa (como 021/v2.8).

    Primera frase, sin prefijos técnicos, sin terminar a media frase.
    Es descripción llana, no etiqueta: nunca se devuelve el ID de familia.
    Si no hay catálogo o no hay descripción, devuelve "".
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
        return ""
    return d[:1].lower() + d[1:]


def _registro(entrada):
    """Persona del input: 'primera' si cuenta en primera persona, si no 'tercera'."""
    hechos = []
    if entrada:
        for c in entrada.get("cuts", []):
            hechos.append(c.get("hecho", "") or c.get("narracion", "") or "")
    texto = " ".join(hechos).lower()
    if any(w in texto for w in (" yo ", " me ", "estaba", "me pasó", "me paso")):
        return "primera"
    return "tercera"


def _hecho_del_corte(entrada, cut_id):
    if not entrada:
        return ""
    for c in entrada.get("cuts", []):
        if c.get("id") == cut_id or c.get("corte") == cut_id or c.get("cut_id") == cut_id:
            return c.get("hecho", "") or c.get("narracion", "") or c.get("texto", "") or ""
    return ""


def _cita_corta(entrada, cut_id, max_chars=160):
    """El hecho de un corte, citado como está: primera oración, recortada.

    Método 021: texto REAL del corte, sin re-narrar. Se toma solo la primera
    oración (el hecho puede traer varias) y se recorta a max_chars sin
    partir una palabra. Con minúscula inicial porque se embebe en la
    respuesta. Cada corte se cita una sola vez.
    """
    h = _hecho_del_corte(entrada, cut_id)
    if not h:
        return ""
    h = h.strip()
    partes = re.split(r"\.\s+(?=[A-ZÁÉÍÓÚÑ])", h)
    primera = (partes[0] if partes else h).strip()
    if len(partes) > 1:
        primera = primera.rstrip(".") + "."
    if len(primera) > max_chars:
        primera = primera[:max_chars].rsplit(" ", 1)[0].rstrip(".,;:") + "..."
    if primera:
        primera = primera[:1].lower() + primera[1:]
    return primera


_SEGUNDA = {
    "yo": "", "me": "te", "mi": "tu", "mis": "tus", "mí": "ti",
    "opté": "optaste", "junté": "juntaste", "salí": "saliste",
    "fui": "fuiste", "dije": "dijiste", "vi": "viste",
    "golpeé": "golpeaste", "saqué": "sacaste", "traté": "trataste",
    "hice": "hiciste", "tuve": "tuviste", "pude": "pudiste",
    "quise": "quisiste", "supe": "supiste", "vine": "viniste",
    "puse": "pusiste", "di": "diste", "estuve": "estuviste",
    "dejé": "dejaste", "llegué": "llegaste", "empecé": "empezaste",
    "pasé": "pasaste", "viví": "viviste", "sentí": "sentiste",
    "quedé": "quedaste", "volví": "volviste", "tomé": "tomaste",
    "siento": "sientes", "estoy": "estás", "tengo": "tienes",
    "quiero": "quieres", "sé": "sabes", "puedo": "puedes",
    "voy": "vas", "digo": "dices", "hago": "haces", "veo": "ves",
    "creo": "crees", "salgo": "sales", "sigo": "sigues",
    "llevo": "llevas", "aprendo": "aprendes", "quedo": "quedas",
    "arriesgo": "arriesgas", "duermo": "duermes", "pienso": "piensas",
    "busco": "buscas", "trabajo": "trabajas", "estudio": "estudias",
    "vivo": "vives", "como": "comes", "bebo": "bebes",
    "leo": "lees", "escribo": "escribes", "hablo": "hablas",
    "miro": "miras", "escucho": "escuchas", "pregunto": "preguntas",
    "respondo": "respondes", "ayudo": "ayudas", "necesito": "necesitas",
    "encuentro": "encuentras", "entiendo": "entiendes", "conozco": "conoces",
    "uso": "usas", "compro": "compras", "vendo": "vendes",
    "pago": "pagas", "gano": "ganas", "pierdo": "pierdes",
    "empiezo": "empiezas", "termino": "terminas", "abro": "abres",
    "cierro": "cierras", "entro": "entras", "llego": "llegas",
    "vuelvo": "vuelves", "regreso": "regresas", "recuerdo": "recuerdas",
    "olvido": "olvidas", "amo": "amas", "odio": "odias",
    "extraño": "extrañas", "prefiero": "prefieres", "intento": "intentas",
    "logro": "logras", "consigo": "consigues", "dejo": "dejas",
    "pongo": "pones", "traigo": "traes", "sueño": "sueñas",
    "pregunté": "preguntaste", "dormí": "dormiste", "comí": "comiste",
    "escribí": "escribiste", "leí": "leíste", "pedí": "pediste",
    "seguí": "seguiste", "conseguí": "conseguiste", "anduve": "anduviste",
    "traje": "trajiste", "conocí": "conociste", "terminé": "terminaste",
    "abrí": "abriste", "cerré": "cerraste", "entré": "entraste",
    "regresé": "regresaste", "soñé": "soñaste", "recordé": "recordaste",
    "olvidé": "olvidaste", "amé": "amaste", "odié": "odiaste",
    "extrañé": "extrañaste", "preferí": "preferiste", "intenté": "intentaste",
    "logré": "lograste", "busqué": "buscaste", "trabajé": "trabajaste",
    "estudié": "estudiaste", "hablé": "hablaste", "miré": "miraste",
    "escuché": "escuchaste", "respondí": "respondiste", "ayudé": "ayudaste",
    "necesité": "necesitaste", "encontré": "encontraste", "entendí": "entendiste",
    "usé": "usaste", "compré": "compraste", "vendí": "vendiste",
    "pagué": "pagaste", "gané": "ganaste", "perdí": "perdiste",
    "salirme": "salirte", "juntarme": "juntarte", "irme": "irte",
    "sentirme": "sentirte", "quedarme": "quedarte", "verme": "verte",
    "llevarme": "llevarte",
}


def _a_segunda_persona(txt):
    """Pasa un texto en primera persona a segunda (tú), por diccionario.

    Lo que no se reconoce queda como está (sigue siendo palabra de la
    persona, no invento). Solo se usa cuando la respuesta va en segunda.
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


# --- Clasificación de la pregunta (determinista, sin LLM) ---

_PAT_QUE_VA_A_PASAR = (
    r"que va a pasar|que pasara|que podria pasar|que puede pasar|que sigue|"
    r"que viene|despues de esto|hacia donde|que va a ocurrir|que ocurrira|"
    r"que me espera|que sigue despues|que va a ser de|que pasara con"
)
_PAT_QUE_HAGO = (
    r"que hago|que debo hacer|que deberia hacer|que me conviene|me cambio|"
    r"me quedo|que decision|que harias|me voy o me quedo|que es mejor|"
    r"que me recomiendas|debo quedarme|debo irme|debo cambiar"
)
_PAT_POR_QUE = (
    r"por que|porque|cual es el tema|que significa|que ocurre|que paso|"
    r"que es|de que se trata|por que paso|cual es la razon|que quiere decir|"
    r"que esta pasando|que hay detras"
)
_PAT_RUIDO_META = (
    r"ignora|olvida|no hagas caso|haz de cuenta|dime que|di que|finge|"
    r"actua como|ignora el motor|ignora todo|no le hagas caso|"
    r"olvida el motor|sin el motor|aunque el motor diga"
)


def _clasificar_pregunta(pregunta):
    """Devuelve (tipo, ruido_meta, detalle_ruido).

    Tipos: QUE_VA_A_PASAR, POR_QUE, QUE_HAGO, AMBIGUA. El orden es por
    especificidad: lo de "qué va a pasar" gana sobre "qué es" (una pregunta
    como "¿qué es lo que podría pasar?" es de futuro, no de tema).
    El ruido/meta (instrucción de ignorar el motor o de decir otra cosa)
    se detecta y se registra, pero no cambia el tipo: se clasifica la
    pregunta de fondo y la instrucción inyectada se ignora.
    """
    q = _norm(pregunta or "")
    ruido = None
    m = re.search(_PAT_RUIDO_META, q)
    if m:
        ruido = m.group(0)
    if re.search(_PAT_QUE_VA_A_PASAR, q):
        return "QUE_VA_A_PASAR", ruido, ruido
    if re.search(_PAT_QUE_HAGO, q):
        return "QUE_HAGO", ruido, ruido
    if re.search(_PAT_POR_QUE, q):
        return "POR_QUE", ruido, ruido
    return "AMBIGUA", ruido, ruido


# --- Descripción llana de escenarios (sin vocabulario del motor) ---

_ESCENARIO_LLANO = {
    "MESETA_O_ESTABILIZACION": "que las cosas se queden así",
    "CONTINUIDAD_ASCENDENTE": "que siga subiendo lo que apenas apareció",
    "MESeta_O_ESTABILIZACION": "que las cosas se queden así",
}


def _descripcion_escenario(escenario, hipotesis, catalogo):
    """El escenario en palabras llanas, sin el nombre técnico del motor.

    Los dos escenarios conocidos del motor tienen frase fija. Para uno
    desconocido se usa la descripción llana de su primera hipótesis que
    converge; si no hay nada, una frase neutra. Nunca se devuelve el ID
    del escenario en la respuesta.
    """
    if not escenario:
        return "que siga como va"
    clave = str(escenario).strip()
    if clave in _ESCENARIO_LLANO:
        return _ESCENARIO_LLANO[clave]
    if clave.upper() in _ESCENARIO_LLANO:
        return _ESCENARIO_LLANO[clave.upper()]
    for fam in (hipotesis or []):
        d = _descripcion_llana(fam, catalogo)
        if d:
            return "que %s se haga más presente" % d
    return "que las cosas cambien de rumbo"


def _normalizar(result, entrada):
    """Extrae del RESULT lo que la respuesta necesita, en una sola forma.

    Acepta el RESULT con H1/H2/apuesta a nivel superior (lo que lee
    traducir()) y el INTERPRETABLE con todo anidado bajo
    salida_interpretable. No muta el result. Devuelve un dict con H1, H2,
    grado, grado_inverso, escenarios (con soporte), peso_en_par, y los
    cortes sin explicar si el result los trae (predictibilidad_021 inversa
    o lista explícita).
    """
    si = {}
    if isinstance(result, dict):
        si = result.get("salida_interpretable") if isinstance(
            result.get("salida_interpretable"), dict) else {}
    def _h(campo):
        v = result.get(campo) if isinstance(result, dict) else None
        if isinstance(v, dict) and v.get("familia"):
            return v.get("familia")
        if isinstance(v, str) and v:
            return v
        v2 = si.get(campo)
        if isinstance(v2, dict) and v2.get("familia"):
            return v2.get("familia")
        if isinstance(v2, str) and v2:
            return v2
        return ""
    h1 = _h("H1")
    h2 = _h("H2")
    grado = (si.get("grado") or (result.get("grado") if isinstance(result, dict) else "") or "").strip().upper()
    grado_inverso = (si.get("grado_inverso_set") or (result.get("grado_inverso_set") if isinstance(result, dict) else "") or "").strip()
    apuesta = si.get("apuesta_multiescenario") or (result.get("apuesta_multiescenario") if isinstance(result, dict) else None) or {}
    escenarios = []
    for e in (apuesta.get("escenarios") or []):
        soporte = e.get("soporte_estructural_agregado")
        if soporte is None:
            soporte = e.get("soporte")
        try:
            soporte = float(soporte)
        except (TypeError, ValueError):
            continue
        if not (0.0 <= soporte <= 1.0):
            continue
        escenarios.append({
            "escenario": e.get("escenario", ""),
            "soporte": soporte,
            "soporte_pct": int(round(soporte * 100)),
            "n_hipotesis": e.get("n_hipotesis") or len(e.get("hipotesis_que_convergen") or []),
            "hipotesis": list(e.get("hipotesis_que_convergen") or []),
            "es_probabilidad": bool(e.get("es_probabilidad", False)),
        })
    escenarios.sort(key=lambda x: -x["soporte"])
    mezcla = si.get("mezcla") or {}
    peso_par = {
        "H1": mezcla.get("peso_H1_en_par"),
        "H2": mezcla.get("peso_H2_en_par"),
    }
    # Cortes sin explicar: solo una lista EXPLÍCITA a nivel de set. Las
    # listas por_hipotesis del paso inverso 021 son POR HIPÓTESIS, no del
    # set: un corte está sin explicar por el SET solo si ninguna hipótesis
    # lo explica, y por_hipotesis mezcla hipótesis del set con otras que
    # no lo son, así que su unión NO es la lista del set (para THEMISTOCLES
    # daba C1/C2 aunque el grado_inverso del set dice que explica todos los
    # cortes). Si no hay lista explícita, responder() decide por el
    # grado_inverso: explica todos, o hay cortes sin explicar sin inventar
    # cuáles. Nunca se inventa la lista.
    sin_explicar = []
    if isinstance(result, dict) and isinstance(result.get("cortes_sin_explicar"), list):
        sin_explicar = [str(c) for c in result.get("cortes_sin_explicar")]
    ent = entrada or {}
    if not isinstance(ent, dict):
        ent = {}
    if not ent and isinstance(result, dict) and isinstance(result.get("entrada"), dict):
        ent = result.get("entrada")
    return {
        "H1": h1, "H2": h2, "grado": grado, "grado_inverso": grado_inverso,
        "escenarios": escenarios, "peso_en_par": peso_par,
        "cortes_sin_explicar": sin_explicar, "entrada": ent,
    }


# --- Verificación (negativa + positiva, como xains/SymGen) ---

_PROHIBIDOS_RESPUESTA = (
    r"\bH1\b", r"\bH2\b", r"\btoken\b", r"\bpeso\b", r"rank_fusion",
    r"oleada", r"pulso de masa", r"\bcometa\b", r"\bnudo\b", r"\bmeseta\b",
    r"eso de que", r"\bC\d+_", r"subtipo:", r"mannheim",
)


def _verificar_respuesta(respuesta):
    """Violaciones de forma: etiquetas del catálogo, tokens, física del motor.

    No se verifican las citas (palabras de la persona) por separado: la
    verificación corre sobre la respuesta completa, pero las plantillas del
    módulo no usan ninguno de estos términos, así que una violación es un
    fallo del módulo, no de la persona.
    """
    viol = []
    bajo = (respuesta or "").lower()
    for pat in _PROHIBIDOS_RESPUESTA:
        if re.search(pat, bajo):
            viol.append(pat)
    return viol


def _verificar_concordancia(tipo, respuesta, citas, normalizado, pregunta):
    """FALLO_CONCORDANCIA si la respuesta no responde a su tipo de pregunta,
    si no cita evidencia del result, o si cita algo que no está en la entrada.
    """
    r = (respuesta or "")
    if tipo == "QUE_VA_A_PASAR":
        if "soporte" not in r.lower() or "%" not in r:
            return {"status": "FALLO_CONCORDANCIA",
                    "motivo": "pregunta de futuro sin escenarios con soporte"}
        if "preguntaste" not in r.lower() and "despues de esto" not in _norm(r):
            return {"status": "FALLO_CONCORDANCIA",
                    "motivo": "no nombra la pregunta de futuro que responde"}
    elif tipo == "POR_QUE":
        if "lo que manda" not in r.lower() and "lo que se ve" not in r.lower():
            return {"status": "FALLO_CONCORDANCIA",
                    "motivo": "pregunta de tema sin H1/H2 con evidencia"}
    elif tipo == "QUE_HAGO":
        if "si " not in r.lower() or "la decision es tuya" not in _norm(r):
            return {"status": "FALLO_CONCORDANCIA",
                    "motivo": "pregunta de acción sin condicionado ni decisión de la persona"}
    elif tipo == "AMBIGUA":
        if "no es especifica" not in _norm(r):
            return {"status": "FALLO_CONCORDANCIA",
                    "motivo": "pregunta ambigua sin decir que es ambigua"}
    if not citas:
        return {"status": "FALLO_CONCORDANCIA",
                "motivo": "la respuesta no cita evidencia de los cortes"}
    # Cada cita debe ser texto real de la entrada (no invento). Las citas
    # van en la persona de la respuesta (2a si el input es 1a), así que la
    # comprobación usa la cita ORIGINAL (como está en el hecho), no la
    # convertida: una cita convertida no coincide letra por letra con el
    # hecho y no es invento por eso.
    entrada = normalizado.get("entrada") or {}
    hechos = []
    for c in entrada.get("cuts", []):
        hechos.append(_norm(c.get("hecho", "") or c.get("narracion", "") or ""))
    for item in citas:
        cid = item[0]
        cita_orig = item[2] if len(item) > 2 else item[1]
        nc = _norm(cita_orig).strip(" .")
        if len(nc) < 8:
            continue
        # La cita es la primera oración del hecho (o su recorte): debe
        # aparecer como prefijo de algún hecho, o el hecho debe contenerla.
        ok = any(nc[:40] in h or h[:60] in nc for h in hechos if h)
        if not ok:
            return {"status": "FALLO_CONCORDANCIA",
                    "motivo": "cita inventada: %s no está en la entrada" % cid}
    return {"status": "OK", "motivo": ""}


def _verificar_fidelidad(respuesta, normalizado):
    """Cada porcentaje y el grado de la respuesta deben ser los del result."""
    r = (respuesta or "")
    for m in re.finditer(r"(\d+)%", r):
        pct = int(m.group(1))
        if not any(e["soporte_pct"] == pct for e in normalizado.get("escenarios", [])):
            return {"status": "FALLO_FIDELIDAD",
                    "motivo": "porcentaje %d%% sin soporte en la apuesta" % pct}
    grado = (normalizado.get("grado") or "").lower()
    if grado in ("firme", "ajustada", "fragil"):
        if grado not in _norm(r):
            return {"status": "FALLO_FIDELIDAD",
                    "motivo": "el grado %s del result no está en la respuesta" % grado}
    for fam in (normalizado.get("H1", ""), normalizado.get("H2", "")):
        if fam and fam.lower() in r.lower():
            return {"status": "FALLO_FIDELIDAD",
                    "motivo": "ID de familia %s colado en la respuesta" % fam}
    return {"status": "OK", "motivo": ""}


def _verificar_narratividad(respuesta, citas_orden, entrada):
    """Se lee como historia en orden: citas en orden cronológico, más de
    dos frases, sin costura de plantilla, y nombra la pregunta que responde.
    """
    r = (respuesta or "")
    if len([s for s in re.split(r"[.!?]\s+", r.strip()) if s.strip()]) < 3:
        return {"status": "FALLO_NARRATIVIDAD",
                "motivo": "la respuesta tiene menos de tres frases"}
    if "eso de que" in r.lower():
        return {"status": "FALLO_NARRATIVIDAD",
                "motivo": "costura de plantilla 'eso de que'"}
    if "preguntaste" not in r.lower() and "tu pregunta" not in r.lower():
        return {"status": "FALLO_NARRATIVIDAD",
                "motivo": "no nombra la pregunta que responde"}
    # Las citas deben ir en el mismo orden cronológico que los cortes de la
    # entrada (no basta con que aparezcan: el orden de los IDs debe ser el
    # de la entrada, no el inverso ni uno mezclado).
    orden_entrada = []
    for c in (entrada or {}).get("cuts", []):
        cid = c.get("id") or c.get("corte") or c.get("cut_id") or ""
        if cid:
            orden_entrada.append(cid)
    indices = []
    for item in citas_orden:
        cid = item[0] if item else ""
        if cid in orden_entrada:
            indices.append(orden_entrada.index(cid))
    if indices != sorted(indices):
        return {"status": "FALLO_NARRATIVIDAD",
                "motivo": "la evidencia no va en orden cronológico"}
    return {"status": "OK", "motivo": ""}


# --- Construcción de la respuesta ---

_GRADO_LLANO = {"FIRME": "firme", "AJUSTADA": "ajustada", "FRAGIL": "frágil"}


def _limites_txt(normalizado):
    """El grado y qué cortes quedan sin explicar (regla d)."""
    grado = (normalizado.get("grado") or "").upper()
    g = _GRADO_LLANO.get(grado, "")
    if g:
        base = "Es una lectura %s" % g
        if g != "firme":
            base += ", no firme"
        base += "."
    else:
        base = "No se registró el grado de la lectura."
    gi = normalizado.get("grado_inverso") or ""
    sin = normalizado.get("cortes_sin_explicar") or []
    if sin:
        base += " Los cortes que quedan sin explicar son: %s." % ", ".join(sin)
    elif gi == "SET_EXPLICA_TODOS_LOS_CORTES":
        base += " El set explica todos los cortes."
    elif gi == "SET_CON_CORTES_SIN_EXPLICAR":
        base += " Hay cortes que el set no explica del todo."
    elif gi:
        base += " El set deja cortes sin explicar."
    return base


def _evidencia_txt(entrada, segunda):
    """Los hechos en orden cronológico, citados en palabras de la persona.

    Una cita corta por corte, una sola vez cada hecho, en el orden de la
    entrada. Devuelve (texto, citas) donde citas es [(cut_id, cita, cita_original)]:
    cita es la que va en la respuesta (en la persona de la respuesta) y
    cita_original es la que está en el hecho (para verificar que no es invento).
    """
    cortes = (entrada or {}).get("cuts", []) or []
    citas = []
    for c in cortes:
        cid = c.get("id") or c.get("corte") or c.get("cut_id") or ""
        cita_orig = _cita_corta(entrada, cid)
        if not cita_orig:
            continue
        cita = _a_segunda_persona(cita_orig) if segunda else cita_orig
        citas.append((cid, cita, cita_orig))
    if not citas:
        return "", []
    # Cada cita como frase propia, en orden.
    frases = []
    for _, cita, _ in citas:
        t = cita.strip()
        if not t.endswith(".") and not t.endswith("..."):
            t += "."
        frases.append(t[:1].upper() + t[1:] if t else t)
    return " ".join(frases), citas


def responder(result, entrada=None, pregunta=None, catalogo=None):
    """Resultado + pregunta en prosa -> respuesta en prosa (gh-issue-48).

    result: dict RESULT del motor (H1/H2/apuesta/grado a nivel superior o
    bajo salida_interpretable). entrada: dict con cuts (hecho) y question.
    pregunta: la pregunta en prosa; si no se da, se usa entrada[question].
    Devuelve un dict con respuesta, tipo_pregunta, escenarios, grado,
    cortes_sin_explicar, concordancia, fidelidad, narratividad, anexo y
    violaciones. No muta result ni entrada. No decide H.
    """
    if catalogo is None:
        catalogo = _cargar_catalogo()
    if not esta_activa():
        return {"status": "APAGADA_POR_FLAG", "respuesta": "", "tipo_pregunta": "",
                "escenarios": [], "grado": "", "cortes_sin_explicar": [],
                "concordancia": {"status": "APAGADA_POR_FLAG", "motivo": "RESPUESTA_HUMANA=0"},
                "fidelidad": {"status": "APAGADA_POR_FLAG", "motivo": ""},
                "narratividad": {"status": "APAGADA_POR_FLAG", "motivo": ""},
                "anexo": {}, "violaciones": [], "ruido_meta": False,
                "version": VERSION, "contrato": CONTRATO}
    if not isinstance(result, dict) or not result:
        return {"status": "FALLO_SIN_RESULTADO", "respuesta": "",
                "tipo_pregunta": "", "escenarios": [], "grado": "",
                "cortes_sin_explicar": [],
                "concordancia": {"status": "FALLO_SIN_RESULTADO",
                                 "motivo": "sin RESULT sellado no hay respuesta"},
                "fidelidad": {"status": "FALLO_SIN_RESULTADO", "motivo": ""},
                "narratividad": {"status": "FALLO_SIN_RESULTADO", "motivo": ""},
                "anexo": {}, "violaciones": [], "ruido_meta": False,
                "version": VERSION, "contrato": CONTRATO}
    norm = _normalizar(result, entrada)
    ent = norm["entrada"]
    if pregunta is None:
        pregunta = (ent.get("question") or "")
    pregunta = str(pregunta or "").strip()
    tipo, ruido, _det = _clasificar_pregunta(pregunta)
    registro = _registro(ent)
    segunda = registro == "primera"
    h1 = norm["H1"]
    h2 = norm["H2"]
    escenarios = norm["escenarios"]
    grado = norm["grado"]
    g_llano = _GRADO_LLANO.get(grado, "")

    def _a_persona(txt):
        return _a_segunda_persona(txt) if segunda else txt

    # --- Evidencia (una cita por corte, en orden cronológico) ---
    evidencia, citas = _evidencia_txt(ent, segunda)
    intro_evidencia = ("Esto se perfila así por lo que contaste, en orden: "
                       if segunda else
                       "Esto se perfila así por lo que se cuenta, en orden: ")

    # --- Nombres llanos de H1/H2 (descripción del catálogo, no el ID) ---
    nombre_h1 = _descripcion_llana(h1, catalogo) if h1 else ""
    nombre_h2 = _descripcion_llana(h2, catalogo) if h2 and h2 != h1 else ""

    # --- Descripciones llanas de los escenarios ---
    def _desc_esc(e):
        return _descripcion_escenario(e["escenario"], e.get("hipotesis"), catalogo)

    frases = []
    if tipo == "QUE_VA_A_PASAR":
        if escenarios:
            principal = escenarios[0]
            frases.append("Preguntaste qué podría pasar después de esto. "
                          "Lo que más se perfila, con el %d%% del soporte, es %s."
                          % (principal["soporte_pct"], _desc_esc(principal)))
            if len(escenarios) > 1:
                otro = escenarios[1]
                frases.append("La otra posibilidad, con el %d%% del soporte, es %s."
                              % (otro["soporte_pct"], _desc_esc(otro)))
        else:
            frases.append("Preguntaste qué podría pasar después de esto.")
        if evidencia:
            frases.append(intro_evidencia + evidencia)
        frases.append(_limites_txt(norm))
    elif tipo == "POR_QUE":
        if nombre_h1 and nombre_h2:
            frases.append("Preguntaste cuál es el tema central. Lo que manda es %s, "
                          "y lo segundo es %s." % (nombre_h1, nombre_h2))
        elif nombre_h1:
            frases.append("Preguntaste cuál es el tema central. Lo que manda es %s."
                          % nombre_h1)
        else:
            frases.append("Preguntaste cuál es el tema central.")
        if evidencia:
            frases.append(intro_evidencia + evidencia)
        frases.append(_limites_txt(norm))
    elif tipo == "QUE_HAGO":
        if escenarios:
            principal = escenarios[0]
            frases.append("Preguntaste qué hacer. Esto no es una orden, es lo que "
                          "se perfila. Si las cosas siguen como van, lo que más se "
                          "perfila, con el %d%% del soporte, es %s."
                          % (principal["soporte_pct"], _desc_esc(principal)))
            if len(escenarios) > 1:
                otro = escenarios[1]
                frases.append("Si se mueve hacia lo otro, con el %d%% del soporte, es %s."
                              % (otro["soporte_pct"], _desc_esc(otro)))
        else:
            frases.append("Preguntaste qué hacer. Esto no es una orden, es lo que se perfila.")
        if evidencia:
            frases.append(intro_evidencia + evidencia)
        frases.append(_limites_txt(norm))
        frases.append("La decisión es tuya: el motor no decide por ti.")
    else:  # AMBIGUA
        if escenarios:
            principal = escenarios[0]
            frases.append("Tu pregunta no es específica, así que te doy lo que más "
                          "se perfila. Lo que manda es %s, y lo que más se perfila, "
                          "con el %d%% del soporte, es %s."
                          % (nombre_h1 or "lo que se ve en los cortes",
                             principal["soporte_pct"], _desc_esc(principal)))
        elif nombre_h1:
            frases.append("Tu pregunta no es específica, así que te doy lo que más "
                          "se perfila. Lo que manda es %s." % nombre_h1)
        else:
            frases.append("Tu pregunta no es específica.")
        if evidencia:
            frases.append(intro_evidencia + evidencia)
        frases.append(_limites_txt(norm))
        frases.append("Si quieres, pregúntame qué va a pasar, por qué, o qué hacer.")

    respuesta = " ".join(frases)
    # --- Guardias ---
    viol = _verificar_respuesta(respuesta)
    concordancia = _verificar_concordancia(tipo, respuesta, citas, norm, pregunta)
    fidelidad = _verificar_fidelidad(respuesta, norm)
    narratividad = _verificar_narratividad(respuesta, citas, ent)
    status = "OK"
    if viol:
        status = "FALLO_VERIFICACION"
    elif concordancia["status"] != "OK":
        status = concordancia["status"]
    elif fidelidad["status"] != "OK":
        status = fidelidad["status"]
    elif narratividad["status"] != "OK":
        status = narratividad["status"]

    anexo = {
        "H1": h1,
        "H2": h2,
        "grado": grado,
        "grado_inverso": norm["grado_inverso"],
        "escenarios": [{"escenario": e["escenario"], "soporte": e["soporte"],
                        "soporte_pct": e["soporte_pct"],
                        "n_hipotesis": e["n_hipotesis"],
                        "es_probabilidad": e["es_probabilidad"]} for e in escenarios],
        "cortes_sin_explicar": norm["cortes_sin_explicar"],
        "registro": registro,
        "tipo_pregunta": tipo,
        "ruido_meta": bool(ruido),
        "ruido_meta_detalle": ruido or "",
        "version": VERSION,
        "contrato": CONTRATO,
    }
    # Sin None en el anexo: el sanitizador del runner los contaría como
    # faltantes. Solo se incluyen los pesos en par si el result los trae.
    if norm["peso_en_par"].get("H1") is not None:
        anexo["peso_H1_en_par"] = norm["peso_en_par"]["H1"]
    if norm["peso_en_par"].get("H2") is not None:
        anexo["peso_H2_en_par"] = norm["peso_en_par"]["H2"]
    return {"status": status, "respuesta": respuesta, "tipo_pregunta": tipo,
            "escenarios": anexo["escenarios"], "grado": grado,
            "cortes_sin_explicar": norm["cortes_sin_explicar"],
            "concordancia": concordancia, "fidelidad": fidelidad,
            "narratividad": narratividad, "anexo": anexo,
            "violaciones": viol, "ruido_meta": bool(ruido),
            "version": VERSION, "contrato": CONTRATO}


def observar(case, motor, pred):
    """Puente post-predictor: responde la pregunta sobre el RESULT sellado.

    case: la entrada original (cuts + question). motor: no se usa (el
    módulo no decide H ni reescribe nada). pred: el RESULT sellado.
    No decide H.
    """
    return responder(pred, case)
