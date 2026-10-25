# -*- coding: utf-8 -*-
"""COMPUERTA Z_TRABAJO (2026-10-24): nada posterior al corte de trabajo entra al motor.

Z_trabajo = el corte en el que se "para" el caso (no es un año biográfico tipo 90 % de vida). En una pregunta
de hoy, Z_trabajo es la fecha de hoy. Se aplica ANTES del motor: casos/fabrica/fabrica.py preparar (falla el lote) y
calibracion/arnes_calibracion.py correr (rechaza el caso) si la entrada trae "gate_z" o FABRICA_GATE_Z90=1.

Campos de la entrada:
  z_trabajo            AAAA-MM-DD (si falta se usa freeze)
  modo_z               "historico" (Z en el pasado, el final ya existe) | "vivo" (Z = ahora, pregunta abierta)
  preparacion_ciega    {"preparador_entrada": str, "custodio_destino": str, "vio_destino": false}
  cuts[i].evidencia    lista de {"afirmacion", "source_url", "source_date", "claim_date", "tipo_fuente": primaria|secundaria,
                                 "conocido_en_Z": "sí", "snapshot_date" (secundarias en modo vivo)}

Reglas (cualquier violación = RECHAZO):
  R1 z_trabajo válido. Fechas parciales cuentan como el ÚLTIMO día del periodo (peor caso).
  R2 fecha de cada corte <= Z.
  R3 cada afirmación con URL, source_date, claim_date <= Z, tipo_fuente y conocido_en_Z == "sí".
  R4 primaria: source_date <= Z (contemporánea).
     secundaria, modo vivo: copia congelada <= Z: web.archive.org/web/<AAAAMMDD...> con fecha <= Z, o permalink
       (oldid=/revision) con snapshot_date <= Z. Nunca Wikipedia en vivo.
     secundaria, modo historico: solo con preparación ciega (preparador != custodio y vio_destino == false).
  R5 ningún texto de la entrada menciona un año > año de Z.
  R6 ninguna palabra de la lista negra del sujeto (vive FUERA de entrada.json, junto al destino sellado).
  R7 sin lenguaje de futuro o predicción en hechos/notas/afirmaciones (será, va a, terminará, probablemente, will, ...).
"""
from __future__ import annotations
import re
import unicodedata

VERSION = "GATE_Z_TRABAJO_20261024"
_FECHA = re.compile(r"^\d{4}(-\d{2}(-\d{2})?)?$")
_ANIO = re.compile(r"(?<!\d)(1[0-9]{3}|20[0-9]{2})(?!\d)")
_ARCHIVO = re.compile(r"web\.archive\.org/web/(\d{8})")
_FUTURO = ["sera", "seran", "va a", "van a", "terminara", "acabara", "llegara", "morira", "caera", "probablemente",
           "seguramente", "en el futuro", "mas tarde", "anos despues", "despues moriria", "luego seria", "finalmente",
           "acabaria", "terminaria", "will", "would later", "later became", "eventually", "went on to", "predic", "pronostic"]


def _norm(s) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", str(s).lower()) if unicodedata.category(c) != "Mn")


def _peor(f: str) -> str:
    p = (str(f) + "-99-99").split("-")
    return f"{p[0]}-{p[1]}-{p[2]}"


def _textos(e: dict):
    yield "question", e.get("question") or ""
    yield "source_notes", e.get("source_notes") or ""
    for c in e.get("cuts") or []:
        cid = c.get("id") or c.get("cut_id")
        yield f"{cid}.hecho", c.get("hecho") or ""
        for i, x in enumerate(c.get("evidencia") or []):
            yield f"{cid}.evidencia[{i}]", " ".join(str((x or {}).get(k) or "") for k in ("afirmacion", "nota"))


def _hay(w, blob):
    return re.search(r"(?<!\w)" + re.escape(_norm(w)) + r"(?!\w)", blob) is not None


def validar_entrada(e: dict, prohibidas=None) -> list:
    errs = []
    z = str(e.get("z_trabajo") or e.get("freeze") or "")
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", z):
        return [f"R1 z_trabajo ausente o mal formado: {z!r}"]
    modo = e.get("modo_z")
    if modo not in ("historico", "vivo"): errs.append("R1 modo_z debe ser 'historico' o 'vivo'")
    pc = e.get("preparacion_ciega") or {}
    ciega = bool(pc.get("preparador_entrada")) and bool(pc.get("custodio_destino")) and \
        _norm(pc.get("preparador_entrada")) != _norm(pc.get("custodio_destino")) and pc.get("vio_destino") is False
    Z = _peor(z); anio = int(z[:4])
    for c in e.get("cuts") or []:
        cid = c.get("id") or c.get("cut_id") or "?"
        d = str(c.get("date") or c.get("fecha_corte") or "")
        if not _FECHA.match(d): errs.append(f"R2 {cid}: fecha del corte ausente/mal formada")
        elif _peor(d) > Z: errs.append(f"R2 {cid}: corte {d} posterior a Z {z}")
        ev = c.get("evidencia")
        if not isinstance(ev, list) or not ev:
            errs.append(f"R3 {cid}: sin 'evidencia'"); continue
        for i, x in enumerate(ev):
            x = x or {}; t = f"{cid}.evidencia[{i}]"
            url, sd, cd, tf = str(x.get("source_url") or ""), str(x.get("source_date") or ""), str(x.get("claim_date") or ""), x.get("tipo_fuente")
            if not x.get("afirmacion"): errs.append(f"R3 {t}: falta 'afirmacion'")
            if not url.startswith(("http://", "https://")): errs.append(f"R3 {t}: source_url ausente o inválida")
            if not _FECHA.match(sd): errs.append(f"R3 {t}: source_date ausente o mal formada")
            if not _FECHA.match(cd): errs.append(f"R3 {t}: claim_date ausente o mal formada")
            elif _peor(cd) > Z: errs.append(f"R3 {t}: claim_date {cd} posterior a Z {z}")
            if _norm(x.get("conocido_en_Z")) not in ("si",): errs.append(f"R3 {t}: conocido_en_Z debe ser 'sí'")
            if tf == "primaria":
                if _FECHA.match(sd) and _peor(sd) > Z: errs.append(f"R4 {t}: primaria fechada {sd} después de Z")
            elif tf == "secundaria":
                if modo == "vivo":
                    m = _ARCHIVO.search(url); sn = str(x.get("snapshot_date") or "")
                    ok = (m and f"{m.group(1)[:4]}-{m.group(1)[4:6]}-{m.group(1)[6:8]}" <= z) or \
                         (("oldid=" in url or "/revision" in url) and _FECHA.match(sn) and _peor(sn) <= Z)
                    if not ok: errs.append(f"R4 {t}: secundaria en modo vivo sin copia congelada <= Z (archive.org o permalink+snapshot_date)")
                elif not ciega:
                    errs.append(f"R4 {t}: secundaria en modo histórico exige preparación ciega (preparador != custodio, vio_destino=false)")
            else:
                errs.append(f"R3 {t}: tipo_fuente debe ser primaria|secundaria")
    textos = list(_textos(e))
    for campo, tx in textos:
        for y in _ANIO.findall(tx):
            if int(y) > anio: errs.append(f"R5 {campo}: menciona el año {y} (posterior a Z)")
        n = _norm(tx)
        for w in _FUTURO:
            if _hay(w, n): errs.append(f"R7 {campo}: lenguaje de futuro/predicción {w!r}")
    blob = " ".join(_norm(t) for _, t in textos)
    for w in (prohibidas or []):
        if _norm(w) and _hay(w, blob): errs.append(f"R6 la entrada contiene palabra prohibida post-Z: {w!r}")
    return errs
