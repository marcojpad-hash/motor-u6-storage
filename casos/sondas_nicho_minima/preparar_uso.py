#!/usr/bin/env python3
"""Preparación de la entrada para las etapas de USO (motor-autorizado).

Las piezas autorizadas se USAN en la entrada que lee el motor, no solo
se observan como traza. La entrada original se conserva (el archivo de
origen no se toca; la preparada se escribe en otro archivo).

Etapas (acumulativas, por partes):
  U2 alias:   los tokens que el alias agregaría entran en la entrada.
              Se añaden al eje P de cada corte (el tablero donde vive
              la trayectoria; A y C suelen estar planos). El alias solo
              añade tokens que no están en ningún eje.
  U3 embudo:  las etiquetas se APLICAN como marca en los cortes. Un corte
              RUIDO_ALIAS no cuenta como perfil completo: sus tokens
              clínicos (sin co-token) son ruido y se quitan de la entrada.
              Un corte PERFIL_VENTANA sí cuenta: se deja como está.
              La etiqueta queda marcada en el corte ("embudo": ...).
  U4 fix:     el caso preparado ES la entrada. Sobre U3 se aplica el
              remapeo ambicion->autonomia (si cero conquista) POR CORTE,
              como está escrito. El alias y el embudo del fix ya están
              activos desde U2/U3; aplicar preparar_caso sobre la entrada
              cruda re-añadiría el ruido que U3 quitó, por eso el remap
              se aplica sobre U3. El fix como pieza queda USADO en U4
              (su remap está en la entrada).

U0/U1 no tocan la entrada (U1 usa el nicho en el ranking, vía el hub).

Los plugins se importan del motor (motor/motor/). No se modifica el
Engine ni el 244. El alias es ciego a negaciones ("sin carretera"
dispara carretera): hallazgo documentado, no corregido aquí.
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

MOTOR = Path(__file__).resolve().parents[2] / "motor" / "motor"
sys.path.insert(0, str(MOTOR))

from plugin_alias_reactivacion import traducir  # noqa: E402
from plugin_embudo_clinico import etiquetar, CLINICO  # noqa: E402
from plugin_fix_entrada import remapeo_ambicion  # noqa: E402

EJES = ("P", "A", "C")


def _hechos(corte: dict) -> str:
    return " ".join(x for x in (str(corte.get("hecho") or ""),
                                str(corte.get("source_note") or "")) if x)


def _plano(corte: dict):
    """P+A+C como lista plana [(token, peso, eje)]."""
    out = []
    for eje in EJES:
        for t, v in (corte.get(eje) or []):
            out.append((str(t), float(v), eje))
    return out


def _a_ejes(plano, nuevos_en_p=()):
    """Reconstruye P/A/C desde el plano; los tokens nuevos van a P."""
    ejes = {e: [] for e in EJES}
    vistos = set()
    for t, v, eje in plano:
        if t in vistos:
            continue
        vistos.add(t)
        ejes[eje].append([t, v])
    for t, v in nuevos_en_p:
        if t not in vistos:
            ejes["P"].append([t, v])
            vistos.add(t)
    return ejes


def aplicar_alias(entrada: dict) -> tuple[dict, dict]:
    """U2: añade a P los tokens del alias (texto de ESA ventana)."""
    ent = copy.deepcopy(entrada)
    reporte = {"por_corte": [], "total_agregados": 0}
    for c in ent.get("cuts") or []:
        plano = _plano(c)
        nombres = {t for t, _, _ in plano}
        salida = traducir([(t, v) for t, v, _ in plano], hechos=_hechos(c))
        agregados = [(t, v) for t, v in salida if t not in nombres]
        ejes = _a_ejes(plano, nuevos_en_p=agregados)
        for e in EJES:
            c[e] = ejes[e]
        reporte["por_corte"].append({
            "corte": str(c.get("id") or c.get("corte") or "?"),
            "agregados": [{"token": t, "peso": v} for t, v in agregados]})
        reporte["total_agregados"] += len(agregados)
    return ent, reporte


def aplicar_embudo(entrada: dict) -> tuple[dict, dict]:
    """U3: marca cada corte con su etiqueta; en RUIDO_ALIAS quita los
    tokens clínicos (ruido sin co-token). PERFIL_VENTANA se deja."""
    ent = copy.deepcopy(entrada)
    cortes = []
    for c in ent.get("cuts") or []:
        toks = [(str(t), float(v)) for t, v, _ in _plano(c)]
        cortes.append((str(c.get("id") or c.get("corte") or "?"), toks))
    et = etiquetar(cortes)
    reporte = {"global": et.get("global"), "sosten_max": et.get("sosten_max"),
               "por_corte": []}
    for c, fila in zip(ent.get("cuts") or [], et.get("cortes") or []):
        etiqueta = fila.get("etiqueta")
        c["embudo"] = etiqueta
        quitados = []
        if etiqueta == "RUIDO_ALIAS":
            plano = _plano(c)
            resto = [(t, v, e) for t, v, e in plano if t not in CLINICO]
            quitados = sorted({t for t, _, _ in plano if t in CLINICO})
            ejes = _a_ejes(resto)
            for e in EJES:
                c[e] = ejes[e]
        reporte["por_corte"].append({
            "corte": fila.get("corte"), "etiqueta": etiqueta,
            "clinico": fila.get("clinico"), "co_oficio": fila.get("co_oficio"),
            "quitados": quitados})
    return ent, reporte


def aplicar_remap(entrada: dict) -> tuple[dict, dict]:
    """U4: remapeo ambicion->autonomia si cero conquista, POR CORTE."""
    ent = copy.deepcopy(entrada)
    reporte = {"por_corte": [], "total_remapes": 0}
    for c in ent.get("cuts") or []:
        plano = _plano(c)
        antes = {t for t, _, _ in plano}
        # remapeo_ambicion conserva orden y longitud: el token remapeado
        # conserva el eje del original en esa posición (no por nombre,
        # porque autonomia podría ya existir en otro eje).
        salida = remapeo_ambicion([(t, v) for t, v, _ in plano])
        nuevo_plano = [(t, v, plano[i][2]) for i, (t, v) in enumerate(salida)]
        # si autonomia ya estaba en el corte, _a_ejes deduplica por token
        # (conserva la primera aparición en orden P+A+C).
        ejes = _a_ejes(nuevo_plano)
        for e in EJES:
            c[e] = ejes[e]
        despues = {t for t, _, _ in nuevo_plano}
        remap = ("ambicion" in antes and "ambicion" not in despues
                 and "autonomia" in despues)
        reporte["por_corte"].append({
            "corte": str(c.get("id") or c.get("corte") or "?"),
            "remap_ambicion_a_autonomia": bool(remap)})
        reporte["total_remapes"] += int(bool(remap))
    return ent, reporte


def preparar(entrada: dict, etapa: str) -> tuple[dict, dict]:
    """Prepara la entrada hasta la etapa pedida (acumulativa).
    U0/U1: sin cambio. U2: alias. U3: alias+embudo. U4: alias+embudo+remap."""
    reportes = {}
    ent = copy.deepcopy(entrada)
    if etapa in ("U2", "U3", "U4"):
        ent, reportes["alias"] = aplicar_alias(ent)
    if etapa in ("U3", "U4"):
        ent, reportes["embudo"] = aplicar_embudo(ent)
    if etapa == "U4":
        ent, reportes["remap"] = aplicar_remap(ent)
    return ent, reportes


if __name__ == "__main__":
    src, etapa, dst = sys.argv[1], sys.argv[2], sys.argv[3]
    entrada = json.loads(Path(src).read_text(encoding="utf-8"))
    ent, reportes = preparar(entrada, etapa)
    Path(dst).parent.mkdir(parents=True, exist_ok=True)
    Path(dst).write_text(json.dumps(ent, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"etapa": etapa, "reportes": reportes}, ensure_ascii=False, indent=1))
