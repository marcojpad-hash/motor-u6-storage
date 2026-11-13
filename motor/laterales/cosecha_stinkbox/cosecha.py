#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosecha.py — Cosecha del StinkBox (lateral, contrato COSECHA_V2_1_20261113).

La v1 (COSECHA_V1_20261113) juntaba lo activado y lo dejaba como
propuesta para que Marco decidiera. La v2 cambia el diseño por orden de
Marco (2026-11-13): EL MOTOR DECIDE POR PROXIMIDAD, no Marco, y el
StinkBox es REPOSITORIO DE HALLAZGOS NUEVOS, no basurero.

Parche v2.1 (2026-11-13, corrección de Marco): la v2 solo leía nombres,
raíces y co-activación; nunca leía la EVIDENCIA, que es donde vive la
salud (DSM, muerte, hospital) y donde vive la hostelería (sidecar, no
en el 244). La v2.1 añade el componente de evidencia (CAMPOS_EVIDENCIA)
y las fichas sidecar de trayectoria al ranking de proximidad.

Regla (Marco): SI YA LO TENEMOS, SE OMITE — ningún token duplicado
entra al StinkBox. El dedupe es por identidad de TOKEN: un token que
ya está en el catálogo o ya fue cosechado no vuelve a entrar, aunque
aparezca en más casos; la omisión queda registrada con el motivo
"ya existe". Las cosechas sirven para MOSTRAR las familias de tokens
que nos hacen falta (arte, deuda, enfermedad, riesgo), para saber que
hay que meterlas: son la evidencia de lo que falta, no un relleno.

Lo que hace la v2, por token sin familia:
  1. DUPLICADO -> RECHAZADO. El token es casi el mismo que uno del
     catálogo 244 (mismo token, variante cercana por distancia de
     edición, o misma raíz con poca diferencia de largo). Regla de
     no-duplicación: no se activa lo que ya mide otra cosa.
  2. Si no es duplicado, se mide su PROXIMIDAD a cada familia del 244
     (y a las fichas sidecar de trayectoria, marcadas sidecar=True)
     con cuatro componentes deterministas (sin LLM, sin azar):
       nombre: 1 si el token es un componente del nombre de la familia
               (el nombre se parte por "_"; "arte" en
               candidato_trayectoria_arte_prestigio).
       raiz:   1 si algún token de la familia contiene al token como
               subcadena (o al revés): misma raíz ("deuda" en
               "deuda_de_sangre", "riesgo" en "busqueda_riesgo").
       coact:  fracción de las apariciones del token (caso, corte, eje)
               en las que algún token de la familia está en el mismo
               (caso, corte, eje) de la misma entrada.
       evidencia: 0 / 0.5 / 1.0 según cuántos términos distintos del
               campo del token aparecen en el texto de evidencia de la
               familia (description + fuente): 0 = no habla del campo,
               0.5 = una mención, 1.0 = dos o más (la evidencia habla
               del campo). La salud vive ahí: DSM en sustancias, muerte
               en musicos, hospital en operativo_salud, consumo /
               desgaste / turno en el sidecar de hostelería.
     puntaje = min(1.0, 0.5*nombre + 0.3*raiz + 0.2*coact + 0.3*evidencia).
     La co-activación sola nunca alcanza: las familias genéricas
     (monomito_01_mundo_ordinario) co-activan con todo y no dicen nada.
     La evidencia nunca decide duplicados (eso sigue siendo por
     nombre/raíz/similaridad).
  3. ACTIVADO como análogo de la familia más cercana si puntaje >= 0.50
     Y es la única en el mejor puntaje (margen > 0). Una ficha sidecar
     nunca es objetivo de activación (no está en el 244).
     PENDIENTE si puntaje < 0.50 y el campo está documentado en varias
     familias empatadas arriba (campo_general_varias_familias: el
     concepto abarca varias familias del campo, sin análogo único);
     si puntaje < 0.50 y no es ese caso (lejos_de_todas: necesita
     familia nueva, no análogo); si hay empate en el mejor puntaje
     >= 0.50 (ambiguo: la medida no puede elegir y no se fuerza la
     activación); o si lo más cercano es solo un sidecar (solo_sidecar:
     el campo vive en un sidecar, no en el 244).

REGISTRO (REGISTRO_COSECHA.json): los casos se registran por IDENTIDAD
de caso (sin los sufijos _SIN_ULTIMO/_RETENIDO del índice) y los TOKENS
por identidad de token. Una vez cosechado un caso, sus variantes no
aportan nada: en cada re-corrida se saltan los casos ya cosechados y
solo se procesan los NUEVOS o los que CAMBIARON de evidencia (p. ej.
un caso que no tenía RESULT y ahora sí lo tiene, como los 10 de F005
cuando se corran). Y una vez cosechado un token, no vuelve a entrar:
si reaparece en más casos se omite con el motivo "ya existe". Los
tokens sin familia quedan en el registro con sus apariciones acumuladas
hasta tener decisión (activado o rechazado); los pendientes no se
pierden entre corridas y se re-evalúan cuando llega evidencia nueva.

MATICES DE VINCULACIÓN: un token ya conocido solo vale la pena
registrarlo si tiene matices, y el matiz vive en LA VINCULACIÓN, no en
meter el token otra vez. Cuando un token sin familia co-activa con un
token del catálogo en el mismo (caso, corte, eje), ese par es un
VÍNCULO candidato para el lateral VINCULACION_TOKENS_V1_20261112 (hoy
V=0 porque el token sin familia es inerte, vector cero; el vínculo se
activa cuando el token tenga familia, análogo). Los vínculos se
deduplean por par: un vínculo ya registrado no se vuelve a reportar.

NO toca el Engine (MOTOR_V15_3_UNICO) ni el catálogo 244: solo lee.
can_decide_H = False (la cosecha decide activación de ANÁLOGOS, nunca H).
No re-corre el motor. Salidas:
  motor/laterales/cosecha_stinkbox/COSECHA_YYYYMMDD_V2.json
  motor/laterales/cosecha_stinkbox/REGISTRO_COSECHA.json

Uso:
  python3 motor/laterales/cosecha_stinkbox/cosecha.py [--fecha YYYYMMDD]
  python3 motor/laterales/cosecha_stinkbox/puerta.py   # PUERTA PASA / RECHAZADA
"""
import json
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent  # motor-cameo/

CONTRATO = "COSECHA_V2_1_20261113"
CONTRATO_V2 = "COSECHA_V2_20261113"
CONTRATO_V1 = "COSECHA_V1_20261113"
can_decide_H = False

REGIMEN_Z = {"auge": "auge_en_Z", "caida": "caida_en_Z", "ruptura": "ruptura_en_Z"}

# --- Umbrales de la regla de proximidad (documentados en NOTA.md) ---
UMBRAL_SIMILITUD_DUPLICADO = 0.80   # similitud Levenshtein normalizada
UMBRAL_RAZON_LARGO_DUPLICADO = 0.60  # largo(corto)/largo(largo) en subcadena
PESO_NOMBRE = 0.5
PESO_RAIZ = 0.3
PESO_COACT = 0.2
PESO_EVIDENCIA = 0.3
UMBRAL_ACTIVAR = 0.50

# --- Mapa campo -> términos de evidencia (parche v2.1, ver NOTA.md) ---
# La salud se lee en la EVIDENCIA (description + fuente), no en los
# nombres: DSM, muerte y hospital viven ahí, y el cluster ocupacional
# (consumo / desgaste / turno) en el sidecar de hostelería. Un término
# es una raíz (sin acentos, minúsculas); hace hit si aparece como
# subcadena del texto de evidencia normalizado. El mapa es el
# vocabulario del campo, no una lista por caso: se aplica igual a
# cualquier token cuyo campo sea ese (el campo del token es el campo
# cuya lista lo contiene, o cuyo nombre es el token). Los términos
# cocina/restaurante/samhsa solo existen en la evidencia del sidecar
# de hostelería (0 hits en el 244) y se dejan documentados.
CAMPOS_EVIDENCIA = {
    "salud": ["salud", "enfermedad", "dsm", "muerte", "mortal", "hospital",
              "sintom", "clinic", "trastorn", "adicc", "suicid", "medic",
              "biolog", "dolor", "consumo", "sustancias", "abuso",
              "desgaste", "turno", "cocina", "restaurante", "samhsa"],
    "arte": ["arte", "artist", "creativ", "pintura", "musica", "obra", "estetic"],
    "deuda": ["deuda", "bancarrota", "ruina", "obligacion", "honor",
              "prestamo", "financiero", "crash", "quiebra"],
    "riesgo": ["riesgo", "peligro", "exposicion", "amenaza"],
}

ARCHIVO_V1 = HERE / "COSECHA_20261113.json"
ARCHIVO_REGISTRO = HERE / "REGISTRO_COSECHA.json"


# =====================================================================
# Parte v1 (sin cambios): lectura del catálogo, índice, RESULT, entradas
# =====================================================================

def cargar_catalogo(root=ROOT):
    """Devuelve (familias_244: set, tokens_703: set)."""
    pat = json.loads((root / "motor" / "motor" / "patterns_final_v14.json").read_text(encoding="utf-8"))
    fams = set(pat.keys())
    toks = set()
    for d in pat.values():
        toks |= set((d.get("tokens_favor") or {}).keys())
        toks |= set((d.get("tokens_contra") or {}).keys())
    return fams, toks


def cargar_patrones(root=ROOT):
    """El catálogo completo: {familia: {tokens_favor, tokens_contra}}."""
    return json.loads((root / "motor" / "motor" / "patterns_final_v14.json").read_text(encoding="utf-8"))


def cargar_indice(root=ROOT):
    """Casos distintos del índice (sin los sufijos _SIN_ULTIMO/_RETENIDO)."""
    idx = json.loads((root / "STINKBOX_STORAGE" / "resolved_cases_index.json").read_text(encoding="utf-8"))
    out = set()
    for e in idx.get("cases", []):
        cid = e.get("case_id") or ""
        cid = re.sub(r"_(SIN_ULTIMO|RETENIDO)$", "", cid)
        if cid:
            out.add(cid)
    return out, len(idx.get("cases", []))


def buscar_entrada(root, case_id):
    for base in ("casos/precedentes", "casos/fabrica/cola"):
        p = root / base / case_id / "entrada.json"
        if p.is_file():
            return p
    return None


def buscar_result(root, case_id):
    p = root / "motor" / f"RESULT_{case_id}.json"
    return p if p.is_file() else None


def tokens_de_entrada(entrada):
    """token -> {cortes, ejes, peso_max, n}."""
    out = {}
    for cut in entrada.get("cuts") or []:
        nombre = cut.get("corte") or cut.get("cut_id") or cut.get("id") or "?"
        for eje in ("P", "A", "C"):
            for par in cut.get(eje) or []:
                tok, peso = par[0], par[1]
                d = out.setdefault(tok, {"cortes": [], "ejes": [], "peso_max": 0.0, "n": 0})
                d["cortes"].append(nombre)
                d["ejes"].append(eje)
                d["peso_max"] = max(d["peso_max"], float(peso))
                d["n"] += 1
    for d in out.values():
        d["cortes"] = sorted(set(d["cortes"]))
        d["ejes"] = sorted(set(d["ejes"]))
    return out


def _top15(result):
    """Las 15 hipótesis abiertas: [(familia, lugar, rank_fusion, regimen)]."""
    h = ((result.get("salida_interpretable") or {})
         .get("conjunto_hipotesis_abiertas", {}).get("hipotesis") or [])
    out = []
    for i, x in enumerate(h, start=1):
        fam = x.get("familia")
        if not fam:
            continue
        out.append((fam, i, float(x.get("rank_fusion") or 0.0),
                    ((x.get("trazabilidad_geometrica") or {}).get("regimen"))))
    if out:
        return out, "conjunto_hipotesis_abiertas"
    # Respaldo: por_hipotesis ordenado por rank_fusion (sin regimen propio).
    ph = ((result.get("predictibilidad_021") or {})
          .get("predictibilidad", {}).get("por_hipotesis") or {})
    orden = sorted(ph.items(), key=lambda kv: -float((kv[1] or {}).get("rank_fusion") or 0.0))
    return [(f, i, float((d or {}).get("rank_fusion") or 0.0), None)
            for i, (f, d) in enumerate(orden[:15], start=1)], "por_hipotesis"


def _en_z(result):
    """[(familia, regimen_z, valor)] de familias_activas_en_Z."""
    z = ((result.get("apuesta_destino_personal") or {}).get("familias_activas_en_Z") or {})
    out = []
    for clave, regimen in REGIMEN_Z.items():
        for par in z.get(clave) or []:
            out.append((par[0], regimen, float(par[1])))
    return out


def cosechar_caso(root, case_id, tokens_703, entradas_cache=None):
    """Cosecha un caso. Devuelve (entradas, notas)."""
    entradas = []
    notas = []
    rpath = buscar_result(root, case_id)
    epath = buscar_entrada(root, case_id)
    result = None
    if rpath is not None:
        try:
            result = json.loads(rpath.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001 - un RESULT roto no tumba la cosecha
            notas.append(f"RESULT ilegible: {exc}")
    if result is not None:
        top, fuente = _top15(result)
        z = _en_z(result)
        zmap = {fam: (reg, val) for fam, reg, val in z}
        for fam, lugar, rf, regimen in top:
            e = {"tipo": "familia_top15", "caso": case_id, "familia": fam,
                 "lugar": lugar, "rank_fusion": round(rf, 6),
                 "regimen": regimen, "valor": None,
                 "contexto": f"Top 15 por rank_fusion en {case_id} (lugar {lugar} de 15, fuente {fuente}).",
                 "en_catalogo_244": True}
            if fam in zmap:
                e["regimen_z"], e["valor_z"] = zmap[fam]
                e["contexto"] += f" También activa en Z ({zmap[fam][0]}: {zmap[fam][1]})."
            entradas.append(e)
        for fam, reg, val in z:
            if fam in {x["familia"] for x in entradas}:
                continue
            entradas.append({"tipo": "familia_en_Z", "caso": case_id, "familia": fam,
                             "lugar": None, "rank_fusion": None,
                             "regimen": reg, "valor": val,
                             "contexto": f"Activa en Z en {case_id} ({reg}: {val}).",
                             "en_catalogo_244": True})
    elif rpath is None:
        notas.append("sin RESULT en motor/")
    entrada = None
    if epath is not None:
        try:
            entrada = json.loads(epath.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            notas.append(f"entrada ilegible: {exc}")
    if entrada is not None:
        toks = tokens_de_entrada(entrada)
        sin_familia = {t: d for t, d in toks.items() if t not in tokens_703}
        delta = {}
        m = re.match(r"^(.*)_v(\d+)$", case_id)
        if m:
            base_id = m.group(1)
            base_path = buscar_entrada(root, base_id)
            if base_path is not None:
                base_toks = tokens_de_entrada(json.loads(base_path.read_text(encoding="utf-8")))
                delta = {t: d for t, d in toks.items() if t not in base_toks}
        for tok, d in sorted(sin_familia.items()):
            entradas.append({"tipo": "token_sin_familia", "caso": case_id,
                             "familia": tok, "token": tok,
                             "lugar": None, "rank_fusion": None,
                             "regimen": "token_sin_familia", "valor": d["peso_max"],
                             "contexto": (f"Token en la entrada de {case_id} ({', '.join(d['cortes'])}; "
                                          f"ejes {', '.join(d['ejes'])}; peso max {d['peso_max']}) "
                                          f"sin familia en el 244: el motor no lo puede prender."),
                             "cortes": d["cortes"], "ejes": d["ejes"],
                             "n_apariciones": d["n"], "en_catalogo_244": False})
        for tok, d in sorted(delta.items()):
            entradas.append({"tipo": "token_delta_version", "caso": case_id,
                             "familia": tok, "token": tok,
                             "lugar": None, "rank_fusion": None,
                             "regimen": "token_de_entrada", "valor": d["peso_max"],
                             "contexto": (f"Token que entró en {case_id} y no estaba en la versión "
                                          f"anterior ({', '.join(d['cortes'])}; ejes {', '.join(d['ejes'])}; "
                                          f"peso max {d['peso_max']})."),
                             "cortes": d["cortes"], "ejes": d["ejes"],
                             "n_apariciones": d["n"],
                             "en_catalogo_244": tok in tokens_703})
    elif epath is None:
        notas.append("sin entrada en casos/precedentes ni casos/fabrica/cola")
    return entradas, notas


def _union_casos(root=ROOT):
    """La unión de casos: índice (distintos) + RESULT + entradas."""
    ids_indice, n_entradas_indice = cargar_indice(root)
    ids_result = set()
    for f in (root / "motor").glob("RESULT_*.json"):
        nombre = f.name[7:-5]
        if nombre.endswith("_RECIBO_EJECUCION") or nombre.endswith("_CEB_LEDGER_MANIFIESTO"):
            continue
        ids_result.add(nombre)
    ids_entrada = set()
    for base in ("casos/precedentes", "casos/fabrica/cola"):
        for d in (root / base).glob("*/entrada.json"):
            ids_entrada.add(d.parent.name)
    return sorted(ids_indice | ids_result | ids_entrada), len(ids_indice), n_entradas_indice


def _cosechar_todos_los_casos(root=ROOT):
    """Cosecha completa (sin registro): la lógica v1 tal cual.

    Devuelve (casos, candidatos, sin_result, sin_entrada, notas_por_caso).
    La puerta la usa para G2 (reproducir el manual); no escribe archivos.
    """
    _, tokens_703 = cargar_catalogo(root)
    casos, _, _ = _union_casos(root)
    candidatos = []
    sin_result = []
    sin_entrada = []
    notas_por_caso = {}
    for cid in casos:
        ents, notas = cosechar_caso(root, cid, tokens_703)
        candidatos.extend(ents)
        if buscar_result(root, cid) is None:
            sin_result.append(cid)
        if buscar_entrada(root, cid) is None:
            sin_entrada.append(cid)
        if notas:
            notas_por_caso[cid] = notas
    return casos, candidatos, sorted(sin_result), sorted(sin_entrada), notas_por_caso


def cosechar_todo(root=ROOT, fecha=None, escribir=True):
    """Cosecha todo el StinkBox (v1). Escribe COSECHA_YYYYMMDD.json."""
    fecha = fecha or date.today().strftime("%Y%m%d")
    fams_244, tokens_703 = cargar_catalogo(root)
    casos, candidatos, sin_result, sin_entrada, notas_por_caso = _cosechar_todos_los_casos(root)
    resumen = {}
    for tipo in ("familia_top15", "familia_en_Z", "token_sin_familia", "token_delta_version"):
        resumen[tipo] = sum(1 for c in candidatos if c["tipo"] == tipo)
    resumen["total"] = len(candidatos)
    _, n_distintos, n_entradas_indice = _union_casos(root)
    out = {"contrato": CONTRATO,
           "fecha": fecha,
           "can_decide_H": False,
           "fuente_indice": "STINKBOX_STORAGE/resolved_cases_index.json",
           "n_entradas_indice": n_entradas_indice,
           "n_casos_distintos_indice": n_distintos,
           "n_result_en_motor": sum(1 for c in casos if buscar_result(root, c) is not None),
           "n_entradas_disponibles": sum(1 for c in casos if buscar_entrada(root, c) is not None),
           "n_casos_cosechados": len(casos),
           "casos_sin_result": sin_result,
           "casos_sin_entrada": sin_entrada,
           "notas_por_caso": notas_por_caso,
           "resumen": resumen,
           "candidatos": candidatos}
    destino = HERE / f"COSECHA_{fecha}.json"
    if escribir:
        destino.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return out, destino


# =====================================================================
# Parte v2: regla de proximidad (determinista) y registro
# =====================================================================

def _lev(a, b):
    """Distancia de Levenshtein (determinista, sin dependencias)."""
    if a == b:
        return 0
    la, lb = len(a), len(b)
    if la == 0:
        return lb
    if lb == 0:
        return la
    prev = list(range(lb + 1))
    for i, ca in enumerate(a, 1):
        cur = [i] + [0] * lb
        for j, cb in enumerate(b, 1):
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1,
                         prev[j - 1] + (0 if ca == cb else 1))
        prev = cur
    return prev[lb]


def similitud(a, b):
    """Similitud normalizada 0..1 (1 = idénticos)."""
    m = max(len(a), len(b))
    return 1.0 - _lev(a, b) / m if m else 1.0


def es_duplicado(token, tokens_703):
    """Regla de no-duplicación. Devuelve (es_duplicado, evidencia).

    Duplicado si el token ES uno del catálogo, si es variante cercana
    (similitud >= 0.80) o si comparte raíz con poca diferencia de largo
    (subcadena con largo(corto)/largo(largo) >= 0.60). Un token general
    ("riesgo") frente a una versión calificada ("busqueda_riesgo",
    razón 0.40) NO es duplicado: mide el concepto general, no la
    versión calificada.
    """
    if token in tokens_703:
        return True, {"tipo": "exacto", "token_catalogo": token, "similitud": 1.0}
    mejor = (0.0, None)
    for u in tokens_703:
        s = similitud(token, u)
        if s > mejor[0]:
            mejor = (s, u)
    if mejor[0] >= UMBRAL_SIMILITUD_DUPLICADO:
        return True, {"tipo": "variante", "token_catalogo": mejor[1],
                      "similitud": round(mejor[0], 4)}
    for u in tokens_703:
        if token in u or u in token:
            corto, largo = (token, u) if len(token) <= len(u) else (u, token)
            razon = len(corto) / len(largo)
            if razon >= UMBRAL_RAZON_LARGO_DUPLICADO:
                return True, {"tipo": "misma_raiz", "token_catalogo": u,
                              "similitud": round(similitud(token, u), 4),
                              "razon_largo": round(razon, 4)}
    return False, {"token_mas_cercano": mejor[1], "similitud_max": round(mejor[0], 4)}


def apariciones_token(root, case_id, token):
    """[(corte, eje, peso)] donde el token aparece en la entrada del caso."""
    p = buscar_entrada(root, case_id)
    if p is None:
        return []
    entrada = json.loads(p.read_text(encoding="utf-8"))
    out = []
    for cut in entrada.get("cuts") or []:
        nombre = cut.get("corte") or cut.get("cut_id") or cut.get("id") or "?"
        for eje in ("P", "A", "C"):
            for par in cut.get(eje) or []:
                if par[0] == token:
                    out.append({"corte": nombre, "eje": eje, "peso": float(par[1])})
    return out


def _mapa_tokens_entrada(root, case_id):
    """{(corte, eje): set(tokens)} de la entrada del caso (para co-activación)."""
    p = buscar_entrada(root, case_id)
    if p is None:
        return {}
    entrada = json.loads(p.read_text(encoding="utf-8"))
    m = {}
    for cut in entrada.get("cuts") or []:
        nombre = cut.get("corte") or cut.get("cut_id") or cut.get("id") or "?"
        for eje in ("P", "A", "C"):
            for par in cut.get(eje) or []:
                m.setdefault((nombre, eje), set()).add(par[0])
    return m


def _norm_texto(s):
    """Minúsculas sin acentos (la evidencia del catálogo mezcla con/sin acento)."""
    s = unicodedata.normalize("NFKD", (s or "").lower())
    return "".join(c for c in s if not unicodedata.combining(c))


def texto_evidencia(d):
    """El texto de evidencia de una familia/ficha: description + fuente, normalizado."""
    return _norm_texto((d.get("description") or "") + " " + (d.get("fuente") or ""))


def cargar_fichas_sidecar(root=ROOT):
    """Fichas de trayectoria que viven como sidecar (NO en el catálogo 244).

    Lee motor/motor/plugin_trayectoria_*.py y toma las que definen FICHA
    y PATRON con description/fuente/tokens_favor. Hoy solo hay una:
    trayectoria_hosteleria_turno_sustancias (SAMHSA 2015; NO fusionar
    al 244 hasta Claude; se carga en memoria como sidecar). Una ficha
    sidecar participa en el ranking de proximidad (misma medida) pero
    NUNCA es objetivo de activación: activar es ser análogo de una
    familia del 244; el sidecar solo corrobora el campo y puede ser lo
    más cercano (motivo solo_sidecar). Devuelve [{ficha, description,
    fuente, tokens_favor, tokens_contra, evidence_status}] ordenado por
    ficha (determinista). Un plugin roto no tumba la cosecha: se salta.
    """
    import importlib.util
    out = []
    for ruta in sorted((root / "motor" / "motor").glob("plugin_trayectoria_*.py")):
        try:
            spec = importlib.util.spec_from_file_location(f"sidecar_{ruta.stem}", str(ruta))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            patron = getattr(mod, "PATRON", None)
            ficha = getattr(mod, "FICHA", None)
            if not isinstance(patron, dict) or not ficha:
                continue
            out.append({"ficha": ficha,
                        "description": patron.get("description") or "",
                        "fuente": patron.get("fuente") or "",
                        "tokens_favor": patron.get("tokens_favor") or {},
                        "tokens_contra": patron.get("tokens_contra") or {},
                        "evidence_status": patron.get("evidence_status") or ""})
        except Exception:
            continue
    return out


def campo_del_token(token):
    """El campo semántico del token según el mapa de evidencia.

    El token pertenece al campo cuya lista de términos lo contiene
    (exacto) o cuyo nombre es el token. Si no está en ningún campo,
    None: la evidencia no se le aplica (se comporta como en v2).
    """
    for campo, terminos in CAMPOS_EVIDENCIA.items():
        if token == campo or token in terminos:
            return campo
    return None


def evidencia_campo(texto, campo):
    """(evidencia, hits) del campo en un texto de evidencia normalizado.

    hits = términos distintos del campo que aparecen como subcadena.
    evidencia = min(1, hits/2): 0 = la evidencia no habla del campo,
    0.5 = una mención (señal parcial), 1.0 = dos o más términos distintos
    (la evidencia habla del campo). Determinista.
    """
    if campo is None:
        return 0.0, []
    hits = [t for t in CAMPOS_EVIDENCIA[campo] if t in texto]
    return min(1.0, len(hits) / 2), hits


def proximidad_familias(token, apariciones, patrones, fichas_sidecar=None, campo=None):
    """Puntaje de proximidad del token a cada familia del 244 (+ sidecar).

    Componentes deterministas (sin LLM, sin azar):
      nombre (0.5), raiz (0.3), coact (0.2) como en v2, más
      evidencia (0.3, parche v2.1): la familia habla del campo del token
      en su texto de evidencia (description + fuente). La evidencia
      puede levantar a un token que está en el campo de una familia sin
      compartir nombre ni raíz; nunca decide duplicados (eso sigue
      siendo por nombre/raíz/similaridad).
    puntaje = min(1.0, 0.5*nombre + 0.3*raiz + 0.2*coact + 0.3*evidencia).
    Las fichas sidecar se puntúan igual (misma medida) y se marcan
    sidecar=True; nunca son objetivo de activación.
    Devuelve [(puntaje, familia, nombre, raiz, coact, n_coact,
    evidencia, n_hits, hits, sidecar)] ordenado por puntaje descendente
    y familia ascendente (desempate determinista).
    """
    if campo is None:
        campo = campo_del_token(token)
    if fichas_sidecar is None:
        fichas_sidecar = cargar_fichas_sidecar()
    mapas = {}
    for ap in apariciones:
        cid = ap["caso"]
        if cid not in mapas:
            mapas[cid] = _mapa_tokens_entrada(ROOT, cid)
    n_apar = len(apariciones)

    def fila(fam, toks_fam, texto_ev, sidecar):
        nombre = 1 if token in fam.split("_") else 0
        raiz = 1 if any(token in u or u in token for u in toks_fam) else 0
        n_coact = 0
        for ap in apariciones:
            toks_corte = mapas.get(ap["caso"], {}).get((ap["corte"], ap["eje"]), set())
            if toks_fam & toks_corte:
                n_coact += 1
        coact = n_coact / n_apar if n_apar else 0.0
        ev, hits = evidencia_campo(texto_ev, campo)
        puntaje = min(1.0, PESO_NOMBRE * nombre + PESO_RAIZ * raiz
                      + PESO_COACT * coact + PESO_EVIDENCIA * ev)
        return (round(puntaje, 6), fam, nombre, raiz, round(coact, 4), n_coact,
                ev, len(hits), hits, sidecar)

    filas = []
    for fam in sorted(patrones.keys()):
        d = patrones[fam]
        toks_fam = set((d.get("tokens_favor") or {}).keys()) | set((d.get("tokens_contra") or {}).keys())
        filas.append(fila(fam, toks_fam, texto_evidencia(d), False))
    for f in sorted(fichas_sidecar, key=lambda x: x["ficha"]):
        toks_fam = set((f.get("tokens_favor") or {}).keys()) | set((f.get("tokens_contra") or {}).keys())
        filas.append(fila(f["ficha"], toks_fam, texto_evidencia(f), True))
    filas.sort(key=lambda r: (-r[0], r[1]))
    return filas


def decidir_token(token, apariciones, patrones, tokens_703, fichas_sidecar=None, campo=None):
    """Decisión determinista para un token sin familia (parche v2.1).

    Devuelve el dict de decisión con su evidencia. La decisión es
    función pura de (token, apariciones, catálogo, fichas sidecar):
    misma entrada, misma decisión (G4).
    """
    dup, ev_dup = es_duplicado(token, tokens_703)
    if dup:
        return {"token": token, "decision": "RECHAZADO",
                "motivo": "duplicado",
                "familia_mas_cercana": None, "puntaje": None,
                "evidencia_duplicado": ev_dup,
                "n_apariciones": len(apariciones),
                "casos": sorted({a["caso"] for a in apariciones}),
                "contexto": (f"'{token}' es duplicado de '{ev_dup.get('token_catalogo')}' "
                             f"({ev_dup.get('tipo')}, similitud {ev_dup.get('similitud')}). "
                             f"Regla de no-duplicación: no se activa lo que ya mide otro token.")}
    if campo is None:
        campo = campo_del_token(token)
    if fichas_sidecar is None:
        fichas_sidecar = cargar_fichas_sidecar()
    filas = proximidad_familias(token, apariciones, patrones, fichas_sidecar, campo)
    mejor_puntaje = filas[0][0] if filas else 0.0
    empatadas = [f for f in filas if f[0] == mejor_puntaje]
    top3 = [{"familia": f[1], "puntaje": f[0], "nombre": f[2], "raiz": f[3],
             "coact": f[4], "n_coact": f[5], "evidencia": f[6],
             "n_hits_evidencia": f[7], "hits_evidencia": f[8],
             "sidecar": f[9]} for f in filas[:3]]
    sidecar_mejor = None
    for f in filas:
        if f[9]:
            sidecar_mejor = {"ficha": f[1], "puntaje": f[0], "nombre": f[2],
                             "raiz": f[3], "coact": f[4], "n_coact": f[5],
                             "evidencia": f[6], "n_hits_evidencia": f[7],
                             "hits_evidencia": f[8]}
            break
    base = {"token": token, "campo": campo,
            "n_apariciones": len(apariciones),
            "casos": sorted({a["caso"] for a in apariciones}),
            "top3": top3, "sidecar_mas_cercano": sidecar_mejor}
    if mejor_puntaje >= UMBRAL_ACTIVAR and len(empatadas) == 1:
        f = empatadas[0]
        if f[9]:
            return {**base, "decision": "PENDIENTE", "motivo": "solo_sidecar",
                    "familia_mas_cercana": f[1], "puntaje": f[0],
                    "contexto": (f"'{token}' está más cerca de la ficha sidecar '{f[1]}' "
                                 f"(puntaje {f[0]}: nombre={f[2]}, raiz={f[3]}, coact={f[4]} "
                                 f"en {f[5]}/{len(apariciones)} apariciones, evidencia={f[6]} "
                                 f"({', '.join(f[8]) or 'sin hits'})), que NO está en el "
                                 f"catálogo 244: no se activa como análogo de un sidecar. "
                                 f"Necesita que la ficha entre al catálogo o un análogo del 244.")}
        segundo = filas[1][0] if len(filas) > 1 else 0.0
        return {**base, "decision": "ACTIVADO",
                "motivo": "analogo_por_proximidad",
                "familia_mas_cercana": f[1], "puntaje": f[0],
                "nombre": f[2], "raiz": f[3], "coact": f[4], "n_coact": f[5],
                "evidencia": f[6], "n_hits_evidencia": f[7], "hits_evidencia": f[8],
                "margen_sobre_segundo": round(f[0] - segundo, 6),
                "contexto": (f"'{token}' se activa como análogo de '{f[1]}' "
                             f"(puntaje {f[0]}: nombre={f[2]}, raiz={f[3]}, coact={f[4]} "
                             f"en {f[5]}/{len(apariciones)} apariciones, evidencia={f[6]} "
                             f"({', '.join(f[8]) or 'sin hits'}); "
                             f"margen {round(f[0] - segundo, 4)} sobre el 2º).")}
    if mejor_puntaje >= UMBRAL_ACTIVAR:
        return {**base, "decision": "PENDIENTE", "motivo": "ambiguo_empate",
                "familia_mas_cercana": None, "puntaje": mejor_puntaje,
                "familias_empatadas": [f[1] for f in empatadas],
                "contexto": (f"'{token}' empata en el mejor puntaje ({mejor_puntaje}) entre "
                             f"{len(empatadas)} familias: {', '.join(f[1] for f in empatadas)}. "
                             f"La medida no puede elegir y no se fuerza la activación.")}
    empatadas_con_evidencia = [f for f in empatadas if f[6] > 0]
    if len(empatadas) >= 2 and len(empatadas_con_evidencia) == len(empatadas):
        return {**base, "decision": "PENDIENTE",
                "motivo": "campo_general_varias_familias",
                "familia_mas_cercana": filas[0][1] if filas else None,
                "puntaje": mejor_puntaje,
                "familias_empatadas": [f[1] for f in empatadas],
                "contexto": (f"'{token}' es un concepto general del campo '{campo}': el campo "
                             f"está documentado en la evidencia de varias familias "
                             f"({', '.join(f[1] for f in empatadas)}, puntaje {mejor_puntaje} "
                             f"cada una) y ninguna destaca como su análogo único. "
                             f"Necesita familia nueva, no análogo forzado.")}
    return {**base, "decision": "PENDIENTE", "motivo": "lejos_de_todas",
            "familia_mas_cercana": filas[0][1] if filas else None,
            "puntaje": mejor_puntaje,
            "contexto": (f"'{token}' está lejos de todas las familias del 244 "
                         f"(mejor puntaje {mejor_puntaje}, umbral {UMBRAL_ACTIVAR}). "
                         f"Necesita familia nueva, no análogo.")}


def vinculos_token(root, token, apariciones, tokens_703):
    """Vínculos candidatos del token con tokens del catálogo (matiz).

    Para cada aparición (caso, corte, eje) del token, los tokens del
    catálogo que están en el mismo corte y eje son sus vínculos
    candidatos. Devuelve [{"token_catalogo", "n_instancias",
    "primera_vez": {caso, corte, eje}}] ordenado por token (determinista).
    Es un MATIZ DE VINCULACIÓN para el lateral VINCULACION_TOKENS_V1_20261112,
    no un token nuevo: hoy V=0 porque el token sin familia es inerte
    (vector cero); el vínculo se activa cuando el token tenga familia
    (análogo), porque V(t1,t2,c) exige familia compartida y co-ocurrencia.
    """
    pares = {}
    for ap in apariciones:
        mapa = _mapa_tokens_entrada(root, ap["caso"])
        otros = mapa.get((ap["corte"], ap["eje"]), set()) - {token}
        for otro in sorted(otros):
            if otro not in tokens_703:
                continue
            ent = pares.setdefault(otro, {"n_instancias": 0, "primera_vez": None})
            ent["n_instancias"] += 1
            if ent["primera_vez"] is None:
                ent["primera_vez"] = {"caso": ap["caso"], "corte": ap["corte"], "eje": ap["eje"]}
    return [{"token_catalogo": otro, "n_instancias": ent["n_instancias"],
             "primera_vez": ent["primera_vez"]}
            for otro, ent in sorted(pares.items())]


def _clave_vinculo(token_sin_familia, token_catalogo):
    return f"{token_sin_familia}||{token_catalogo}"

def _estado_evidencia(root, case_id):
    """(tenia_result, tenia_entrada) del caso ahora mismo."""
    return (buscar_result(root, case_id) is not None,
            buscar_entrada(root, case_id) is not None)


def _registro_vacio():
    return {"contrato": CONTRATO, "version": 2,
            "casos": {}, "tokens": {}, "vinculos": {}, "actualizado": None}


def cargar_registro():
    """Carga REGISTRO_COSECHA.json si existe, si no un registro vacío."""
    if ARCHIVO_REGISTRO.is_file():
        return json.loads(ARCHIVO_REGISTRO.read_text(encoding="utf-8"))
    return _registro_vacio()


def guardar_registro(registro):
    ARCHIVO_REGISTRO.write_text(json.dumps(registro, ensure_ascii=False, indent=1),
                                encoding="utf-8")
    return ARCHIVO_REGISTRO


def migrar_desde_v1(root=ROOT, fecha=None):
    """Siembra el registro desde la salida v1 (COSECHA_20261113.json).

    Los 99 casos de la unión quedan registrados con su evidencia y su
    número de candidatos de la v1; los 4 tokens sin familia quedan con
    sus apariciones (recalculadas de las entradas) para decidirlos.
    """
    fecha = fecha or date.today().strftime("%Y%m%d")
    registro = _registro_vacio()
    if not ARCHIVO_V1.is_file():
        return registro, "sin salida v1: registro vacío"
    v1 = json.loads(ARCHIVO_V1.read_text(encoding="utf-8"))
    n_cand_por_caso = {}
    for c in v1.get("candidatos", []):
        n_cand_por_caso[c["caso"]] = n_cand_por_caso.get(c["caso"], 0) + 1
    casos_union, _, _ = _union_casos(root)
    for cid in casos_union:
        tiene_r, tiene_e = _estado_evidencia(root, cid)
        toks = sorted({c["token"] for c in v1.get("candidatos", [])
                       if c["caso"] == cid and c["tipo"] == "token_sin_familia"})
        registro["casos"][cid] = {"fecha_cosecha": v1.get("fecha", fecha),
                                  "tenia_result": tiene_r, "tenia_entrada": tiene_e,
                                  "n_candidatos": n_cand_por_caso.get(cid, 0),
                                  "tokens_sin_familia": toks,
                                  "origen": "v1"}
    for c in v1.get("candidatos", []):
        if c["tipo"] != "token_sin_familia":
            continue
        tok = c["token"]
        aps = apariciones_token(root, c["caso"], tok)
        ent = registro["tokens"].setdefault(
            tok, {"casos": [], "apariciones": [], "peso_max": 0.0, "n_total": 0})
        if c["caso"] not in ent["casos"]:
            ent["casos"].append(c["caso"])
        for ap in aps:
            ent["apariciones"].append({"caso": c["caso"], "corte": ap["corte"],
                                       "eje": ap["eje"], "peso": ap["peso"]})
        ent["peso_max"] = max(ent["peso_max"], float(c.get("valor") or 0.0))
        ent["n_total"] += int(c.get("n_apariciones") or 0)
    for ent in registro["tokens"].values():
        ent["casos"] = sorted(ent["casos"])
    # Vínculos (matices) de los tokens migrados + constancia de lo omitido.
    # Lo que ya está en el catálogo no entra al StinkBox: los 6 tokens
    # delta de la v1 están en el 244 y las 692+538 familias candidatas
    # de la v1 son familias conocidas. Se deja constancia, no se acumulan.
    _, tokens_703 = cargar_catalogo(root)
    n_familias_conocidas_v1 = sum(
        1 for c in v1.get("candidatos", [])
        if c["tipo"] in ("familia_top15", "familia_en_Z"))
    delta_en_catalogo = sorted({c["token"] for c in v1.get("candidatos", [])
                                if c["tipo"] == "token_delta_version"
                                and c.get("token") in tokens_703})
    for tok, ent in sorted(registro["tokens"].items()):
        for v in vinculos_token(root, tok, ent["apariciones"], tokens_703):
            clave = _clave_vinculo(tok, v["token_catalogo"])
            registro["vinculos"][clave] = {
                "token_sin_familia": tok, "token_catalogo": v["token_catalogo"],
                "n_instancias": v["n_instancias"], "primera_vez": v["primera_vez"],
                "fecha": fecha, "origen": "v1"}
    registro["actualizado"] = fecha
    nota = (f"migrados {len(registro['casos'])} casos y {len(registro['tokens'])} tokens "
            f"desde v1; omitidos por ya existir: {n_familias_conocidas_v1} familias "
            f"conocidas (top15+Z) y {len(delta_en_catalogo)} tokens delta en el catálogo "
            f"({', '.join(delta_en_catalogo)})")
    registro["nota_migracion"] = nota
    return registro, nota


def filtrar_candidatos_caso(candidatos, tokens_ya_cosechados, tokens_703):
    """Dedupe por identidad de TOKEN (regla: si ya lo tenemos, se omite).

    candidatos: los de cosechar_caso para un caso.
    tokens_ya_cosechados: set de tokens sin familia ya en el registro.
    Devuelve (hallazgos_nuevos, omitidos_ya_existe, n_familias_conocidas):
      - hallazgos_nuevos: entradas token_sin_familia cuyo token NO está
        en el registro (es la primera vez que se cosecha).
      - omitidos_ya_existe: [{token, caso, motivo}] con constancia de
        cada omisión: "ya cosechado" (el token ya está en el registro)
        o "ya existe en el catálogo 244" (token delta que ya está en el
        703). Un token que vuelve a aparecer en más casos no vuelve a
        entrar: se omite y queda la constancia.
      - n_familias_conocidas: familias top15/en Z omitidas (ya están en
        el 244; son contexto, no hallazgo: no se listan una por una).
    No toca el registro: solo clasifica. La puerta la usa para G3.
    """
    hallazgos = []
    omitidos = []
    n_familias = 0
    for e in candidatos:
        tipo = e.get("tipo")
        if tipo in ("familia_top15", "familia_en_Z"):
            n_familias += 1
            continue
        tok = e.get("token")
        if tipo == "token_sin_familia":
            if tok in tokens_ya_cosechados:
                omitidos.append({"token": tok, "caso": e["caso"],
                                 "motivo": "ya existe",
                                 "detalle": "ya cosechado en una corrida anterior"})
            else:
                hallazgos.append(e)
        elif tipo == "token_delta_version":
            if tok in tokens_703:
                omitidos.append({"token": tok, "caso": e["caso"],
                                 "motivo": "ya existe",
                                 "detalle": "ya existe en el catálogo 244"})
            elif tok in tokens_ya_cosechados:
                omitidos.append({"token": tok, "caso": e["caso"],
                                 "motivo": "ya existe",
                                 "detalle": "ya cosechado en una corrida anterior"})
            else:
                hallazgos.append(e)
    return hallazgos, omitidos, n_familias


def cosechar_v2(root=ROOT, fecha=None):
    """Corrida v2: solo casos nuevos o con evidencia cambiada + decisiones.

    El StinkBox es repositorio de HALLAZGOS NUEVOS, no basurero: el
    dedupe es por identidad de TOKEN. Lo que ya está en el catálogo o
    ya fue cosechado se omite (con constancia, motivo "ya existe") y
    no vuelve a entrar aunque aparezca en más casos. La salida
    presenta las familias que faltan (los hallazgos) y los matices de
    vinculación (vínculos nuevos para el lateral VINCULACION_TOKENS),
    no una acumulación de candidatos conocidos.
    Devuelve (salida_v2, destino_v2, destino_registro).
    """
    fecha = fecha or date.today().strftime("%Y%m%d")
    patrones = cargar_patrones(root)
    _, tokens_703 = cargar_catalogo(root)
    fichas_sidecar = cargar_fichas_sidecar(root)
    casos_union, n_distintos, n_entradas_indice = _union_casos(root)
    registro = cargar_registro()
    registro["contrato"] = CONTRATO
    registro["parche_evidencia"] = {
        "contrato": CONTRATO,
        "motivo": ("La v2 solo leía nombres, raíces y co-activación; la salud vive "
                   "en la evidencia (DSM, muerte, hospital) y en el sidecar de "
                   "hostelería (no en el 244)."),
        "peso_evidencia": PESO_EVIDENCIA,
        "campos": sorted(CAMPOS_EVIDENCIA.keys()),
        "fichas_sidecar": [f["ficha"] for f in fichas_sidecar]}
    casos_registro_antes = len(registro["casos"])
    nota_migracion = None
    n_migrados = 0
    if not registro.get("casos") and ARCHIVO_V1.is_file():
        registro, nota_migracion = migrar_desde_v1(root, fecha=fecha)
        n_migrados = len(registro["casos"])
    nuevos, reprocesados, saltados = [], [], []
    vinculos_migrados = []
    if n_migrados:
        vinculos_migrados = [dict(v, origen="v1")
                             for v in registro.get("vinculos", {}).values()]
    for cid in casos_union:
        tiene_r, tiene_e = _estado_evidencia(root, cid)
        ent = registro["casos"].get(cid)
        if ent is None:
            nuevos.append(cid)
        elif (ent.get("tenia_result"), ent.get("tenia_entrada")) != (tiene_r, tiene_e):
            reprocesados.append(cid)
        else:
            saltados.append(cid)
    a_procesar = sorted(nuevos + reprocesados)
    hallazgos_nuevos = []
    omitidos_ya_existe = []
    n_familias_conocidas_omitidas = 0
    for cid in a_procesar:
        ents, _notas = cosechar_caso(root, cid, tokens_703)
        hallazgos, omitidos, n_fam = filtrar_candidatos_caso(
            ents, set(registro["tokens"].keys()), tokens_703)
        hallazgos_nuevos.extend(hallazgos)
        omitidos_ya_existe.extend(omitidos)
        n_familias_conocidas_omitidas += n_fam
        tiene_r, tiene_e = _estado_evidencia(root, cid)
        toks = sorted({e["token"] for e in hallazgos})
        registro["casos"][cid] = {"fecha_cosecha": fecha,
                                  "tenia_result": tiene_r, "tenia_entrada": tiene_e,
                                  "n_candidatos": len(ents),
                                  "tokens_sin_familia": toks,
                                  "origen": "v2"}
        for e in hallazgos:
            tok = e["token"]
            aps = apariciones_token(root, cid, tok)
            ent = registro["tokens"].setdefault(
                tok, {"casos": [], "apariciones": [], "peso_max": 0.0, "n_total": 0})
            if cid not in ent["casos"]:
                ent["casos"].append(cid)
            for ap in aps:
                ent["apariciones"].append({"caso": cid, "corte": ap["corte"],
                                           "eje": ap["eje"], "peso": ap["peso"]})
            ent["peso_max"] = max(ent["peso_max"], float(e.get("valor") or 0.0))
            ent["n_total"] += int(e.get("n_apariciones") or 0)
    for ent in registro["tokens"].values():
        ent["casos"] = sorted(ent["casos"])
    # Decisiones: se re-calculan con la evidencia acumulada del registro.
    decisiones = {}
    for tok in sorted(registro["tokens"].keys()):
        ent = registro["tokens"][tok]
        dec = decidir_token(tok, ent["apariciones"], patrones, tokens_703,
                            fichas_sidecar)
        decisiones[tok] = dec
        ent["decision"] = {"decision": dec["decision"],
                           "familia_mas_cercana": dec.get("familia_mas_cercana"),
                           "puntaje": dec.get("puntaje"),
                           "motivo": dec["motivo"], "fecha": fecha}
    # Matices de vinculación: vínculos nuevos de los tokens sin familia
    # con tokens del catálogo. Solo se reportan los que NO estaban
    # registrados (dedupe por par); el resto ya existe y se omite.
    # Los de la migración (primera corrida v2) también se reportan:
    # es la primera vez que la v2 los presenta.
    matices_nuevos = []
    for v in vinculos_migrados:
        matices_nuevos.append({
            "token_sin_familia": v["token_sin_familia"],
            "token_catalogo": v["token_catalogo"],
            "n_instancias": v["n_instancias"], "primera_vez": v["primera_vez"],
            "para_lateral": "VINCULACION_TOKENS_V1_20261112",
            "nota": ("V=0 hoy (el token sin familia es inerte, vector cero); "
                     "el vínculo se activa cuando el token tenga familia (análogo). "
                     "Presentado por primera vez por la migración desde v1.")})
    for tok in sorted(registro["tokens"].keys()):
        ent = registro["tokens"][tok]
        for v in vinculos_token(root, tok, ent["apariciones"], tokens_703):
            clave = _clave_vinculo(tok, v["token_catalogo"])
            if clave in registro.get("vinculos", {}):
                continue
            registro.setdefault("vinculos", {})[clave] = {
                "token_sin_familia": tok, "token_catalogo": v["token_catalogo"],
                "n_instancias": v["n_instancias"], "primera_vez": v["primera_vez"],
                "fecha": fecha, "origen": "v2"}
            matices_nuevos.append({
                "token_sin_familia": tok, "token_catalogo": v["token_catalogo"],
                "n_instancias": v["n_instancias"], "primera_vez": v["primera_vez"],
                "para_lateral": "VINCULACION_TOKENS_V1_20261112",
                "nota": ("V=0 hoy (el token sin familia es inerte, vector cero); "
                         "el vínculo se activa cuando el token tenga familia (análogo).")})
    registro["actualizado"] = fecha
    guardar_registro(registro)
    # Las familias que faltan: el hallazgo que presenta la cosecha.
    familias_que_faltan = []
    for tok in sorted(registro["tokens"].keys()):
        ent = registro["tokens"][tok]
        dec = decisiones[tok]
        vinc = [registro["vinculos"][k] for k in sorted(registro.get("vinculos", {}))
                if registro["vinculos"][k]["token_sin_familia"] == tok]
        familias_que_faltan.append({
            "token": tok, "decision": dec["decision"],
            "familia": dec.get("familia_mas_cercana"), "puntaje": dec.get("puntaje"),
            "motivo": dec["motivo"], "campo": dec.get("campo"),
            "top3": dec.get("top3"),
            "sidecar_mas_cercano": dec.get("sidecar_mas_cercano"),
            "casos": ent["casos"],
            "n_apariciones": len(ent["apariciones"]), "peso_max": ent["peso_max"],
            "vinculos": [{"token_catalogo": v["token_catalogo"],
                          "n_instancias": v["n_instancias"],
                          "primera_vez": v["primera_vez"]} for v in vinc],
            "contexto": dec["contexto"]})
    salida = {"contrato": CONTRATO,
              "fecha": fecha,
              "can_decide_H": False,
              "parche_evidencia": registro["parche_evidencia"],
              "n_fichas_sidecar": len(fichas_sidecar),
              "fichas_sidecar": [f["ficha"] for f in fichas_sidecar],
              "fuente_v1": "COSECHA_20261113.json",
              "nota_migracion": nota_migracion or registro.get("nota_migracion"),
              "n_casos_union": len(casos_union),
              "n_casos_distintos_indice": n_distintos,
              "n_entradas_indice": n_entradas_indice,
              "n_casos_registro_antes": casos_registro_antes,
              "n_casos_migrados_desde_v1": n_migrados,
              "n_casos_registro_ahora": len(registro["casos"]),
              "n_casos_nuevos": len(nuevos),
              "n_casos_reprocesados": len(reprocesados),
              "n_casos_saltados": len(saltados),
              "casos_nuevos": nuevos,
              "casos_reprocesados": reprocesados,
              "casos_saltados": saltados,
              "hallazgos_nuevos": hallazgos_nuevos,
              "n_hallazgos_nuevos": len(hallazgos_nuevos),
              "omitidos_ya_existe": omitidos_ya_existe,
              "n_omitidos_ya_existe": len(omitidos_ya_existe),
              "n_familias_conocidas_omitidas": n_familias_conocidas_omitidas,
              "matices_vinculacion_nuevos": matices_nuevos,
              "n_matices_vinculacion_nuevos": len(matices_nuevos),
              "n_vinculos_registrados": len(registro.get("vinculos", {})),
              "familias_que_faltan": familias_que_faltan,
              "decisiones": decisiones,
              "tokens_pendientes": sorted(t for t, d in decisiones.items()
                                          if d["decision"] == "PENDIENTE"),
              "tokens_activados": sorted(t for t, d in decisiones.items()
                                         if d["decision"] == "ACTIVADO"),
              "tokens_rechazados": sorted(t for t, d in decisiones.items()
                                          if d["decision"] == "RECHAZADO"),
              "registro": "REGISTRO_COSECHA.json"}
    destino = HERE / f"COSECHA_{fecha}_V2.json"
    destino.write_text(json.dumps(salida, ensure_ascii=False, indent=1), encoding="utf-8")
    return salida, destino, ARCHIVO_REGISTRO


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    fecha = None
    if "--fecha" in argv:
        fecha = argv[argv.index("--fecha") + 1]
    out, destino, reg = cosechar_v2(fecha=fecha)
    print(f"cosecha v2 {out['fecha']}: unión {out['n_casos_union']} casos "
          f"({out['n_casos_distintos_indice']} distintos en el índice)")
    print(f"  registro antes: {out['n_casos_registro_antes']} casos | "
          f"migrados v1: {out['n_casos_migrados_desde_v1']} | "
          f"nuevos: {out['n_casos_nuevos']} | reprocesados: {out['n_casos_reprocesados']} | "
          f"saltados: {out['n_casos_saltados']}")
    print(f"  hallazgos nuevos: {out['n_hallazgos_nuevos']} | "
          f"omitidos (ya existe): {out['n_omitidos_ya_existe']} | "
          f"familias conocidas omitidas: {out['n_familias_conocidas_omitidas']} | "
          f"matices de vinculación nuevos: {out['n_matices_vinculacion_nuevos']} "
          f"(registrados: {out['n_vinculos_registrados']})")
    print(f"  familias que faltan: {len(out['familias_que_faltan'])}")
    for tok, dec in out["decisiones"].items():
        fam = dec.get("familia_mas_cercana")
        print(f"  {tok}: {dec['decision']}"
              + (f" -> {fam} ({dec.get('puntaje')})" if fam else "")
              + f" [{dec['motivo']}]")
    print(f"  escrito: {destino}")
    print(f"  registro: {reg}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
