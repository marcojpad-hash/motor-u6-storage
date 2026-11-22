# -*- coding: utf-8 -*-
"""COMPUERTA TEMPORAL Z_TRABAJO — protocolo biográfico Z90.

Autoridad normativa: motor/PROTOCOLO_BIOGRAFICO_Z90.md.

Biografía cerrada:
- Z90 = nacimiento + floor(0.9 * días entre nacimiento y muerte).
- La muerte solo calcula el límite; no es evidencia predictiva.
- Cada corte declara window_start = fecha_nacimiento y date = fecha de cierre.
- Los cierres son estrictamente crecientes; el último es exactamente Z90.
- z_trabajo y z90_date deben ser exactamente Z90.

Pregunta viva:
- Conserva la validación temporal/evidencial R1–R7. La fecha actual y el
  inicio del periodo de observación siguen siendo responsabilidad del contrato
  de preparación; esta gate no inventa ni sustituye esos datos.

La gate valida estructura y fechas. No puede demostrar que un custodio sea una
persona/conversación independiente ni que el contenido semántico de cada ventana
sea realmente acumulativo; esos hechos requieren evidencia externa de custodia
y revisión de los inputs.
"""
from __future__ import annotations
import datetime as dt
import re
import unicodedata

VERSION = "GATE_Z_TRABAJO_20261024"  # identificador compatible con recibos existentes
IMPLEMENTATION_REVISION = "Z90_BIRTH_DEATH_WINDOWS_V1_20261121"
_FECHA = re.compile(r"^\d{4}(-\d{2}(-\d{2})?)?$")
_FECHA_EXACTA = re.compile(r"^\d{4}-\d{2}-\d{2}$")
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


def _fecha_exacta(value):
    """Parsea exclusivamente YYYY-MM-DD; no acepta fechas parciales ni inválidas."""
    s = str(value or "")
    if not _FECHA_EXACTA.fullmatch(s):
        return None
    try:
        parsed = dt.date.fromisoformat(s)
    except ValueError:
        return None
    return parsed if parsed.isoformat() == s else None


def calcular_z90(fecha_nacimiento: str, fecha_muerte: str):
    """Devuelve el día de Z90, truncando fracciones de día para no sobrepasar 90 %."""
    nacimiento = _fecha_exacta(fecha_nacimiento)
    muerte = _fecha_exacta(fecha_muerte)
    if nacimiento is None or muerte is None or muerte <= nacimiento:
        return None
    dias = (muerte - nacimiento).days
    return nacimiento + dt.timedelta(days=(dias * 9) // 10)


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


def _validar_estructura_biografica(e: dict, errs: list):
    nacimiento = _fecha_exacta(e.get("fecha_nacimiento"))
    muerte = _fecha_exacta(e.get("fecha_muerte"))
    if nacimiento is None:
        errs.append("R8 fecha_nacimiento ausente, inválida o no exacta (YYYY-MM-DD)")
    if muerte is None:
        errs.append("R8 fecha_muerte ausente, inválida o no exacta (YYYY-MM-DD)")
    if nacimiento is None or muerte is None:
        return None, None

    if muerte <= nacimiento:
        errs.append("R8 fecha_muerte debe ser posterior a fecha_nacimiento")
        return nacimiento, None

    z90 = calcular_z90(nacimiento.isoformat(), muerte.isoformat())
    if z90 is None:
        errs.append("R8 no se pudo calcular Z90 desde nacimiento y muerte")
        return nacimiento, None

    z_trabajo = _fecha_exacta(e.get("z_trabajo"))
    z90_field = _fecha_exacta(e.get("z90_date"))

    if z_trabajo is None:
        errs.append("R8 z_trabajo debe ser una fecha exacta YYYY-MM-DD en biografía cerrada")
    elif z_trabajo != z90:
        errs.append(f"R8 z_trabajo {z_trabajo.isoformat()} no coincide con Z90 calculado {z90.isoformat()}")

    if z90_field is None:
        errs.append("R8 z90_date ausente, inválida o no exacta en biografía cerrada")
    elif z90_field != z90:
        errs.append(f"R8 z90_date {z90_field.isoformat()} no coincide con Z90 calculado {z90.isoformat()}")

    if z_trabajo is not None and z90_field is not None and z_trabajo != z90_field:
        errs.append("R8 z_trabajo y z90_date no coinciden")

    cuts = e.get("cuts")
    if not isinstance(cuts, list) or not cuts:
        errs.append("R8 biografía cerrada requiere al menos un corte")
        return nacimiento, z90

    cierres = []
    for i, c in enumerate(cuts):
        if not isinstance(c, dict):
            errs.append(f"R8 corte[{i}] debe ser objeto")
            continue
        cid = c.get("id") or c.get("cut_id") or f"corte[{i}]"
        cierre = _fecha_exacta(c.get("date") or c.get("fecha_corte"))
        inicio = _fecha_exacta(c.get("window_start"))
        if cierre is None:
            errs.append(f"R8 {cid}: date debe ser fecha exacta YYYY-MM-DD")
        else:
            cierres.append((i, cid, cierre))
            if cierre < nacimiento:
                errs.append(f"R8 {cid}: cierre anterior al nacimiento")
            if cierre > z90:
                errs.append(f"R8 {cid}: cierre posterior a Z90")
        if inicio is None:
            errs.append(f"R8 {cid}: window_start ausente, inválido o no exacto")
        elif inicio != nacimiento:
            errs.append(f"R8 {cid}: window_start debe ser el nacimiento {nacimiento.isoformat()}")

    for prev, curr in zip(cierres, cierres[1:]):
        if curr[2] <= prev[2]:
            errs.append(f"R8 {curr[1]}: cierres no estrictamente crecientes respecto a {prev[1]}")

    if cierres and cierres[-1][2] != z90:
        errs.append(f"R8 último corte {cierres[-1][1]} termina en {cierres[-1][2].isoformat()}, no en Z90 {z90.isoformat()}")

    return nacimiento, z90


def validar_entrada(e: dict, prohibidas=None) -> list:
    errs = []
    z = str(e.get("z_trabajo") or e.get("freeze") or "")
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", z):
        return [f"R1 z_trabajo ausente o mal formado: {z!r}"]

    modo = e.get("modo_z")
    if modo not in ("historico", "vivo"):
        errs.append("R1 modo_z debe ser 'historico' o 'vivo'")

    if modo == "historico":
        _validar_estructura_biografica(e, errs)
    elif modo == "vivo":
        z90_field = _fecha_exacta(e.get("z90_date"))
        z_work = _fecha_exacta(e.get("z_trabajo"))
        if z90_field is None:
            errs.append("R8 z90_date ausente, inválida o no exacta en modo vivo")
        elif z_work is not None and z90_field != z_work:
            errs.append("R8 z_trabajo y z90_date no coinciden en modo vivo")

    pc = e.get("preparacion_ciega") or {}
    ciega = bool(pc.get("preparador_entrada")) and bool(pc.get("custodio_destino")) and \
        _norm(pc.get("preparador_entrada")) != _norm(pc.get("custodio_destino")) and pc.get("vio_destino") is False
    Z = _peor(z)
    anio = int(z[:4])

    for c in e.get("cuts") or []:
        cid = c.get("id") or c.get("cut_id") or "?"
        d = str(c.get("date") or c.get("fecha_corte") or "")
        if not _FECHA.match(d):
            errs.append(f"R2 {cid}: fecha del corte ausente/mal formada")
            cut_limit = Z
        else:
            cut_limit = _peor(d)
            if cut_limit > Z:
                errs.append(f"R2 {cid}: corte {d} posterior a Z {z}")

        ev = c.get("evidencia")
        if not isinstance(ev, list) or not ev:
            errs.append(f"R3 {cid}: sin 'evidencia'")
            continue

        for i, x in enumerate(ev):
            x = x or {}
            t = f"{cid}.evidencia[{i}]"
            url = str(x.get("source_url") or "")
            sd = str(x.get("source_date") or "")
            cd = str(x.get("claim_date") or "")
            tf = x.get("tipo_fuente")

            if not x.get("afirmacion"):
                errs.append(f"R3 {t}: falta 'afirmacion'")
            if not url.startswith(("http://", "https://")):
                errs.append(f"R3 {t}: source_url ausente o inválida")
            if not _FECHA.match(sd):
                errs.append(f"R3 {t}: source_date ausente o mal formada")
            if not _FECHA.match(cd):
                errs.append(f"R3 {t}: claim_date ausente o mal formada")
            elif _peor(cd) > cut_limit:
                errs.append(f"R3 {t}: claim_date {cd} posterior al cierre del corte {d}")
            if _norm(x.get("conocido_en_Z")) not in ("si",):
                errs.append(f"R3 {t}: conocido_en_Z debe ser 'sí'")

            if tf == "primaria":
                if _FECHA.match(sd) and _peor(sd) > cut_limit:
                    errs.append(f"R4 {t}: primaria fechada {sd} después del cierre del corte {d}")
            elif tf == "secundaria":
                if modo == "vivo":
                    m = _ARCHIVO.search(url)
                    sn = str(x.get("snapshot_date") or "")
                    ok = (m and f"{m.group(1)[:4]}-{m.group(1)[4:6]}-{m.group(1)[6:8]}" <= cut_limit) or \
                         (("oldid=" in url or "/revision" in url) and _FECHA.match(sn) and _peor(sn) <= cut_limit)
                    if not ok:
                        errs.append(f"R4 {t}: secundaria en modo vivo sin copia congelada <= fecha de cierre del corte (archive.org o permalink+snapshot_date)")
                elif not ciega:
                    errs.append(f"R4 {t}: secundaria en modo histórico exige preparación ciega (preparador != custodio, vio_destino=false)")
            else:
                errs.append(f"R3 {t}: tipo_fuente debe ser primaria|secundaria")

    textos = list(_textos(e))
    for campo, tx in textos:
        for y in _ANIO.findall(tx):
            if int(y) > anio:
                errs.append(f"R5 {campo}: menciona el año {y} (posterior a Z)")
        n = _norm(tx)
        for w in _FUTURO:
            if _hay(w, n):
                errs.append(f"R7 {campo}: lenguaje de futuro/predicción {w!r}")

    blob = " ".join(_norm(t) for _, t in textos)
    for w in (prohibidas or []):
        if _norm(w) and _hay(w, blob):
            errs.append(f"R6 la entrada contiene palabra prohibida post-Z: {w!r}")

    return errs
