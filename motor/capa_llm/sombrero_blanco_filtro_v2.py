#!/usr/bin/env python3
"""sombrero_blanco_filtro_v2.py — Sombrero blanco v2 (2026-11-17). Filtro de admisión del input.

Implementa la especificación funcional de orquestador-central
`docs/filtros_operativos/SOMBRERO_BLANCO.md` v1.1 (función manual del
14-sep-2026, `FILTRO_TRAZA_BRUTO`): por cada frase del input, parte en
unidades observables (QUIÉN / QUÉ / DÓNDE / EN QUÉ ORDEN / relación
observable), aparta el juicio como ruido tipado (moral, estético, figura,
etiqueta, dicho atribuido, intención, conclusión disfrazada), traza cada
unidad al fragmento exacto del texto fuente (offset + cita literal), no
borra el ruido (lo anota aparte) y no decide veredicto
(`can_decide_H=False`, `feeds_predictor=False`, `llamadas_llm=0`).

No es un diccionario de palabras prohibidas: la unidad de control es la
FUNCIÓN que cumple cada fragmento en la frase (predicativo = juicio; cita
atribuida = dicho; comparación = figura). El nombre del método
("sombrero blanco") nunca es ruido. Un texto que diga literalmente
"juicio estético" no se tira entero: el filtro nunca descarta texto, solo
anota. Las clases de adjetivo (moral / estético) solo sirven para tipar
el adjetivo cuando está en posición predicativa (ser/estar + adjetivo);
el mismo adjetivo fuera de esa función no se marca.

`compuerta(case, modo)` replica la interfaz de
`filtro_entrada_dirigida_017.compuerta`: devuelve (caso, traza).
Modos: "activo" (defecto: el caso que sigue lleva solo los hechos
admitidos; el texto original y el ruido quedan en la traza, no se
borran), "traza" (analiza sin modificar el caso), "off" (apagado).
"""
from __future__ import annotations

import copy
import re
from typing import Any, Dict, List, Optional, Tuple

VERSION = "SOMBRERO_BLANCO_FILTRO_V2_20261117"
CONTRATO = "SOMBRERO_BLANCO_SPEC_V1.1"

# Campos de texto humano de un corte (los mismos canales que lee el
# sidecar v1: hecho / narracion / facts / texto). La pregunta va aparte.
CAMPOS_TEXTO = ("hecho", "narracion", "facts", "texto")

# Copulas (ser/estar) en las formas que aparecen en los textos del motor.
COPULAS = {
    "es", "era", "eran", "son", "fue", "fueron", "sea", "sean",
    "sería", "serian", "ser", "está", "esta", "estaba", "estaban",
    "están", "estan", "estuvo", "estuvieron", "estar",
}
INTENSIFICADORES = {"muy", "tan", "más", "mas", "bastante", "demasiado"}

# Clases de adjetivo para tipar el juicio CUANDO está en posición
# predicativa (ser/estar + adjetivo). No son una lista de palabras
# prohibidas: fuera de esa función no se marca nada.
JUICIO_MORAL = {
    "cruel", "malvado", "malvada", "bueno", "buena", "malo", "mala",
    "inmundo", "inmunda", "execrable", "perverso", "perversa", "vil",
    "noble", "justo", "justa", "injusto", "injusta", "culpable",
    "inocente", "santo", "santa", "diabólico", "diabólica",
    "execración", "execracion",
}
JUICIO_ESTETICO = {
    "bonito", "bonita", "feo", "fea", "hermoso", "hermosa", "horrible",
    "bello", "bella", "precioso", "preciosa", "lindo", "linda",
    "horrendo", "horrenda", "espantoso", "espantosa", "maravilloso",
    "maravillosa", "precioso",
}
# "estético" y "moral" son los NOMBRES de las categorías, no juicios:
# nunca se tipan como ruido. (Guarda del criterio de aceptación 2.)
CATEGORIAS_NO_RUIDO = {"estético", "estetico", "moral", "morales", "estéticos", "esteticos"}

# Cualidades observables (color, tamaño, forma, material): un adjetivo de
# esta clase en posición atributiva ("sombrero blanco", "bicicleta azul")
# es un hecho, no un juicio.
CUALIDAD_OBSERVABLE = {
    "blanco", "blanca", "negro", "negra", "azul", "rojo", "roja", "verde",
    "amarillo", "amarilla", "gris", "grande", "pequeño", "pequeña",
    "alto", "alta", "bajo", "baja", "largo", "larga", "corto", "corta",
    "redondo", "redonda", "cuadrado", "cuadrada", "triangular",
}

# Sustantivos de persona (actor). Todo lo demás es objeto/cosa.
PERSONA = {
    "niño", "niña", "hombre", "mujer", "narrador", "narradora",
    "víctima", "victima", "actor", "actriz", "adulta", "adulto",
    "padre", "madre", "jornalero", "jornalera", "obrero", "obrera",
    "hijo", "hija", "hermano", "hermana", "señor", "señora",
    "gente", "grupo", "compañero", "compañera", "compañeros",
    "niños", "hombres", "mujeres",
}

# Pronombres/demostrativos: no son sustantivos, no son hechos.
PRONOMBRES = {
    "mismo", "misma", "mismos", "mismas", "esto", "eso", "este", "esta",
    "ese", "esa", "aquello", "aquella", "otro", "otra", "otros", "otras",
}

# Verbos de atribución (decir): lo citado se registra como dicho, no como
# hecho del mundo. Verbos de comparación: lo comparado es figura.
VERBOS_ATRIBUCION = {
    "afirma", "dice", "dice que", "afirma que", "describe", "menciona",
    "repite", "llama", "asegura", "sostiene", "cuenta", "narra",
    "pregunta", "responde", "afirman", "dicen", "describen",
}
VERBOS_COMPARACION = {"compara", "comparan", "describe como", "como"}

MARCADORES_SECUENCIA = {
    "después", "despues", "luego", "entonces", "antes", "cuando",
    "mientras", "al final", "primero", "después de",
}
PREPOSICIONES_LUGAR = {
    "en", "a", "hacia", "por", "desde", "hasta", "sobre", "bajo",
    "entre", "frente a",
}
ETIQUETAS_GENERO = {
    "vanguardia", "melodrama", "tragedia", "comedia", "realismo",
    "naturalismo", "alegoría", "alegoria",
}

_RX_ORACION = re.compile(r"[^.!?\n]+(?:[.!?]+|$)")
_RX_CITA = re.compile(r"[«\"']([^«\"']+)[»\"']")
_RX_ARTICULO_SUST = re.compile(
    r"\b(el|la|los|las|un|una|unos|unas)\s+(?:(?:mismo|misma|mismos|mismas)\s+)?([A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+)",
    re.IGNORECASE,
)
_RX_ROL = re.compile(r"\b[A-ZÁÉÍÓÚÑ_]{2,}\b")
_RX_PALABRA = re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+")
_RX_VERBO = re.compile(
    r"\b([a-záéíóúñ]+(?:ar|er|ir|ando|iendo|ado|ada|ados|adas|aba|ía|ó|aron|an|en|a|e|o|as|es|amos|áis|áis))\b",
    re.IGNORECASE,
)
_RX_LUGAR = re.compile(
    r"\b(en|a|hacia|desde|hasta|sobre|bajo|entre)\s+((?:el|la|los|las|un|una)\s+)?(?:(?:mismo|misma|mismos|mismas)\s+)?([a-záéíóúñ]+)",
    re.IGNORECASE,
)
_STOP_VERBO = {
    "el", "la", "los", "las", "un", "una", "de", "en", "a", "con", "por",
    "para", "que", "y", "o", "se", "su", "sus", "es", "era", "son",
    "fue", "está", "estaba", "este", "esta", "esto", "ese", "esa",
    "eso", "al", "del", "lo", "le", "les", "me", "te", "nos", "os",
    "mi", "tu", "si", "no", "ni", "pero", "como", "cuando", "donde",
    "qué", "quién", "cual", "muy", "más", "tan", "ya", "también",
    "hacia", "desde", "hasta", "sobre", "bajo", "entre", "sin", "con",
}


def _oraciones(texto: str) -> List[Tuple[int, int, str]]:
    """Parte el texto en oraciones conservando el offset de cada una."""
    out = []
    for m in _RX_ORACION.finditer(texto):
        frag = m.group(0)
        if frag.strip():
            out.append((m.start(), m.end(), frag))
    return out


def _es_rol(token: str) -> bool:
    return bool(_RX_ROL.fullmatch(token)) and token not in {"Y", "O", "A", "EL", "LA", "DE", "EN"}


def _clase_sustantivo(sust: str) -> str:
    return "quién (actor)" if sust.lower() in PERSONA or _es_rol(sust) else "qué (objeto)"


def filtrar(texto: str) -> Dict[str, Any]:
    """Aplica el sombrero blanco a un texto. Devuelve el formato mínimo
    de la spec: hechos (con traza) y ruido (tipado, con traza).

    El filtro nunca descarta texto: no hay ruta de rechazo. Lo que no es
    hecho queda anotado como ruido y el texto admitido es la unión de los
    hechos.
    """
    texto = texto or ""
    hechos: List[Dict[str, Any]] = []
    ruido: List[Dict[str, Any]] = []
    banderas: List[str] = []
    vistos_hechos = set()
    vistos_ruido = set()
    # Intervalos [inicio, fin) del texto original que son ruido. El texto
    # admitido es el original menos esos intervalos: se conserva la
    # redacción observable y se quitan el juicio, la figura y el dicho.
    spans_ruido: List[Tuple[int, int]] = []

    def _hecho(unidad: str, clase: str, traza: str, offset: int) -> None:
        clave = (unidad.lower(), clase, offset)
        if clave in vistos_hechos:
            return
        vistos_hechos.add(clave)
        hechos.append({"unidad": unidad, "clase": clase, "traza": traza, "offset": offset})

    def _ruido(fragmento: str, tipo: str, traza: str, offset: int, fin: Optional[int] = None) -> None:
        clave = (fragmento.lower(), tipo, offset)
        if clave in vistos_ruido:
            return
        vistos_ruido.add(clave)
        ruido.append({"fragmento": fragmento, "tipo": tipo, "traza": traza, "offset": offset})
        spans_ruido.append((offset, fin if fin is not None else offset + len(traza)))

    for ini_o, fin_o, oracion in _oraciones(texto):
        # Sustantivos ya extraídos en esta oración (para no confundirlos
        # con verbos en el paso 7: "niño" no es una acción).
        sustantivos_oracion = set()
        # 1. Citas: lo citado se registra como dicho (o figura si se
        # compara), nunca como hecho del mundo. Se quitan de la oración
        # antes de extraer unidades observables.
        resto = oracion
        for m in list(_RX_CITA.finditer(oracion)):
            contenido = m.group(1).strip()
            if not contenido:
                continue
            inicio_cita = ini_o + m.start()
            contexto_orig = oracion[: m.start()]
            contexto = contexto_orig.lower()
            es_comparacion = any(
                v in contexto for v in ("compara", "comparan", "como", "cual")
            ) or "como" in contenido.lower().split()[:2]
            if es_comparacion:
                _ruido(contenido, "figura retórica", m.group(0), inicio_cita)
            else:
                _ruido(contenido, "dicho atribuido", m.group(0), inicio_cita)
                # Quien dice: el actor que atribuye (rol o sustantivo antes
                # del verbo de atribución) es un hecho observable.
                for tok in _RX_ROL.finditer(contexto_orig):
                    _hecho(tok.group(0), "quién (actor)", tok.group(0), ini_o + tok.start())
                    break
                else:
                    for tok in _RX_PALABRA.finditer(contexto_orig):
                        palabra = tok.group(0)
                        if palabra.lower() in PERSONA:
                            _hecho(
                                palabra,
                                "quién (actor)",
                                palabra,
                                ini_o + tok.start(),
                            )
                            break
            resto = resto.replace(m.group(0), " ", 1)

        resto_l = resto.lower()
        palabras = [(m.group(0), ini_o + m.start()) for m in _RX_PALABRA.finditer(resto)]

        # 2. Roles en mayúsculas (NARRADOR, VICTIMA, ACTOR_A...) = actores.
        # Se usa _RX_ROL (con guion bajo) para capturar el rol entero.
        for m in _RX_ROL.finditer(resto):
            _hecho(m.group(0), "quién (actor)", m.group(0), ini_o + m.start())

        # 3. Artículo + sustantivo = actor u objeto, con su traza literal.
        for m in _RX_ARTICULO_SUST.finditer(resto):
            sust = m.group(2)
            if sust.lower() in CATEGORIAS_NO_RUIDO or sust.lower() in PRONOMBRES:
                continue
            sustantivos_oracion.add(sust.lower())
            _hecho(sust, _clase_sustantivo(sust), m.group(0), ini_o + m.start())
            # Adjetivo observable pegado al sustantivo ("sombrero blanco",
            # "bicicleta azul") = cualidad observable, hecho.
            despues = resto[m.end(): m.end() + 24]
            m_adj = re.match(r"\s+([a-záéíóúñ]+)", despues)
            if m_adj and m_adj.group(1).lower() in CUALIDAD_OBSERVABLE:
                _hecho(
                    m_adj.group(1),
                    "cualidad observable",
                    m.group(0) + " " + m_adj.group(1),
                    ini_o + m.end() + (len(despues) - len(despues.lstrip())),
                )
            # Material ("de trapo", "de vidrio") = cualidad observable.
            m_mat = re.match(r"\s+de\s+([a-záéíóúñ]+)", despues)
            if m_mat:
                _hecho(
                    "de " + m_mat.group(1),
                    "cualidad observable",
                    m.group(0) + " de " + m_mat.group(1),
                    ini_o + m.end(),
                )

        # 4. Copula + adjetivo valorativo = juicio (moral o estético).
        # Es la FUNCIÓN predicativa la que lo hace juicio, no la palabra
        # sola: el mismo adjetivo fuera de aquí no se marca.
        for m in re.finditer(
            r"\b(es|era|eran|son|fue|fueron|está|esta|estaba|estaban|están|estan)\b"
            r"(?:\s+(muy|tan|más|mas|bastante|demasiado))?\s+([a-záéíóúñ]+)",
            resto,
            re.IGNORECASE,
        ):
            adj = m.group(3).lower()
            if adj in CATEGORIAS_NO_RUIDO:
                continue
            frag = m.group(0).strip()
            off = ini_o + m.start()
            if adj in JUICIO_MORAL:
                _ruido(frag, "juicio moral", frag, off, ini_o + m.end())
            elif adj in JUICIO_ESTETICO:
                _ruido(frag, "juicio estético", frag, off, ini_o + m.end())

        # 5. Comparación explícita fuera de citas ("como", "cual") = figura.
        for m in re.finditer(r"\b(como|cual|parece|semejante)\b\s+([^,.;]+)", resto, re.IGNORECASE):
            frag = m.group(0).strip()
            _ruido(frag, "figura retórica", frag, ini_o + m.start(), ini_o + m.end())

        # 6. Lugar observable ("en la escuela", "en el mismo paso").
        for m in _RX_LUGAR.finditer(resto):
            sust_lugar = m.group(3)
            if sust_lugar.lower() in PRONOMBRES:
                continue
            _hecho(sust_lugar, "dónde", m.group(0).strip(), ini_o + m.start())
        for marcador in MARCADORES_SECUENCIA:
            idx = resto_l.find(marcador)
            if idx >= 0:
                _hecho(marcador, "en qué orden", marcador, ini_o + idx)

        # 7. Acciones: verbo no copulativo que sigue de cerca a un actor
        # (el actor o, como mucho, un adjetivo después del actor). Precisión
        # antes que exhaustividad: un sustantivo no es una acción, y un
        # verbo sin actor cerca no se registra.
        indices_actor = {
            i
            for i, (palabra, _off) in enumerate(palabras)
            if _es_rol(palabra) or palabra.lower() in PERSONA
        }
        for i, (palabra, off) in enumerate(palabras):
            bajo = palabra.lower()
            if bajo in COPULAS or bajo in _STOP_VERBO:
                continue
            if bajo in sustantivos_oracion or bajo in PERSONA:
                continue
            if bajo in CUALIDAD_OBSERVABLE or bajo in JUICIO_MORAL or bajo in JUICIO_ESTETICO:
                continue
            if bajo in CATEGORIAS_NO_RUIDO or bajo in PRONOMBRES:
                continue
            if _es_rol(palabra):
                continue
            if palabra[:1].isupper():
                continue
            if i >= 1 and (i - 1 in indices_actor or i - 2 in indices_actor):
                if _RX_VERBO.fullmatch(palabra) and len(palabra) > 2:
                    _hecho(palabra, "qué (acción)", palabra, off)

        # 8. Etiquetas de género/escuela = bandera, no hecho.
        for etiqueta in ETIQUETAS_GENERO:
            if re.search(r"\b" + re.escape(etiqueta) + r"\b", resto_l):
                bandera = f"etiqueta de género/escuela: {etiqueta}"
                if bandera not in banderas:
                    banderas.append(bandera)

    hechos.sort(key=lambda h: h["offset"])
    ruido.sort(key=lambda r: r["offset"])
    admitido = _texto_admitido(texto, spans_ruido)
    return {
        "version": VERSION,
        "contrato": CONTRATO,
        "hechos": hechos,
        "ruido": ruido,
        "banderas": banderas,
        "texto_admitido": admitido,
        "n_hechos": len(hechos),
        "n_ruido": len(ruido),
        "can_decide_H": False,
        "feeds_predictor": False,
        "llamadas_llm": 0,
    }


def _texto_admitido(texto: str, spans_ruido: List[Tuple[int, int]]) -> str:
    """El texto admitido es el original menos los intervalos de ruido
    (juicio, figura, dicho). Re-aplicar el filtro al texto admitido da el
    mismo texto: ya no hay ruido que quitar y los hechos observables
    conservan su redacción original (idempotencia, necesaria para la red
    de seguridad de run())."""
    if not spans_ruido:
        return texto
    spans = sorted(spans_ruido)
    fusionados: List[List[int]] = []
    for ini, fin in spans:
        if fusionados and ini <= fusionados[-1][1]:
            fusionados[-1][1] = max(fusionados[-1][1], fin)
        else:
            fusionados.append([ini, fin])
    partes = []
    cursor = 0
    for ini, fin in fusionados:
        partes.append(texto[cursor:ini])
        cursor = fin
    partes.append(texto[cursor:])
    admitido = "".join(partes)
    admitido = re.sub(r"\s+", " ", admitido)
    admitido = re.sub(r"\s+([,.;:])", r"\1", admitido)
    while ",," in admitido:
        admitido = admitido.replace(",,", ",")
    admitido = re.sub(r",\s*,", ",", admitido)
    admitido = admitido.strip(" ,;")
    # Al quitar una cita queda a veces el conector colgando ("dice que
    # VICTIMA, y que", "sostiene que y que."): se limpia el "y que" / "que"
    # que queda sin contenido antes de puntuación o de fin de texto.
    admitido = re.sub(r"\s+y que(?=[,.;]|$)", "", admitido)
    admitido = re.sub(r"\s+que(?=[,.;]|$)", "", admitido)
    admitido = admitido.strip(" ,;")
    return admitido.strip()


def _texto_campo(valor: Any) -> str:
    if isinstance(valor, list):
        return " ".join(str(x) for x in valor)
    if valor is None:
        return ""
    return str(valor)


def _reponer(valor: Any, admitido: str) -> Any:
    if isinstance(valor, list):
        return [admitido]
    return admitido


def compuerta(case: Dict[str, Any], modo: str = "activo") -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Compuerta de admisión del input. Replica la interfaz de
    `filtro_entrada_dirigida_017.compuerta`: devuelve (caso, traza).

    Campos filtrados: la pregunta del caso y los campos de texto humano de
    cada corte (hecho, narracion, facts, texto). No toca P/A/C, fechas,
    ids ni ningún otro campo. El texto original queda en la traza
    (auditoría); el ruido se anota aparte; nada se borra del expediente.

    - activo: el caso que sigue lleva solo el texto admitido.
    - traza: analiza sin modificar el caso (status TRAZA_SIN_MODIFICACION).
    - off: no se ejecuta (status NO_CONFIGURADO).
    """
    modo = (modo or "activo").strip().lower()
    base: Dict[str, Any] = {
        "version": VERSION,
        "contrato": CONTRATO,
        "modo": modo,
        "status": "NO_CONFIGURADO",
        "n_hechos": 0,
        "n_ruido": 0,
        "n_campos": 0,
        "campos": [],
        "can_decide_H": False,
        "escribe_H": False,
        "reordena": False,
        "feeds_predictor": False,
        "llamadas_llm": 0,
        "payload_aplicado": False,
    }
    if modo == "off":
        base["nota"] = "SOMBRERO_BLANCO=off"
        return case, base
    payload = copy.deepcopy(case)
    campos: List[Dict[str, Any]] = []
    n_hechos = 0
    n_ruido = 0

    def _filtrar_campo(corte_id: Any, campo: str, valor: Any) -> None:
        nonlocal n_hechos, n_ruido
        texto = _texto_campo(valor)
        if not texto.strip():
            return
        res = filtrar(texto)
        n_hechos += res["n_hechos"]
        n_ruido += res["n_ruido"]
        campos.append(
            {
                "corte": corte_id,
                "campo": campo,
                "texto_original": texto,
                "texto_admitido": res["texto_admitido"],
                "hechos": res["hechos"],
                "ruido": res["ruido"],
                "banderas": res["banderas"],
            }
        )

    _filtrar_campo(None, "question", payload.get("question"))
    for corte in payload.get("cuts") or []:
        if not isinstance(corte, dict):
            continue
        for campo in CAMPOS_TEXTO:
            if campo in corte:
                _filtrar_campo(corte.get("id"), campo, corte.get(campo))

    if modo == "traza":
        base.update(
            {
                "status": "TRAZA_SIN_MODIFICACION",
                "n_hechos": n_hechos,
                "n_ruido": n_ruido,
                "n_campos": len(campos),
                "campos": campos,
                "nota": "traza: analiza sin modificar el caso",
            }
        )
        return payload, base

    # activo: el caso que sigue lleva solo lo admitido.
    for entrada in campos:
        admitido = entrada["texto_admitido"]
        if entrada["corte"] is None and entrada["campo"] == "question":
            payload["question"] = admitido
        else:
            for corte in payload.get("cuts") or []:
                if isinstance(corte, dict) and corte.get("id") == entrada["corte"]:
                    corte[entrada["campo"]] = _reponer(corte[entrada["campo"]], admitido)
                    break
    base.update(
        {
            "status": "EXECUTED",
            "n_hechos": n_hechos,
            "n_ruido": n_ruido,
            "n_campos": len(campos),
            "campos": campos,
            "payload_aplicado": True,
            "nota": "activo: el input que sigue es solo lo admitido; el texto original y el ruido quedan en la traza",
        }
    )
    return payload, base
