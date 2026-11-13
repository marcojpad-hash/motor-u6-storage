#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cuartos_monomito.py — marca los cuartos del monomito en la rueda (solo lectura).

Lee:
  - un COLOR_SOMBRA (rueda de conjunción, tablero sombra) -> familias monomito_*
    con color (tono + saturación).
  - un RESULT sellado -> features.plugin_circulo_monomito.posicion_monomito_por_corte
    (cuadrante activo por corte) y caldero_bridge.

Mapeo familia -> cuarto:
  - El número que abre el nombre de la familia (monomito_NN_...) es el número de
    etapa del viaje. Se verifica contra ESTRUCTURAS_CANDIDATAS de
    plugin_circulo_monomito_v2.py (Q1: etapas 1-3, Q2: 4-6, Q3: 7-9, Q4: 10-12).
  - Si el número existe en las etapas del plugin, el mapeo es directo por número.
  - Si además el slug coincide, se anota; si el slug difiere (p. ej. la familia
    trae "_y_" y la etapa no), se anota como caveat y el mapeo sigue siendo por
    número, NO por slug.
  - Si el número no existe en ninguna etapa, la familia queda NO MAPEABLE y se
    reporta así, sin inventar cuarto.

No toca Engine, 244, correr_estandar, teoria_color, equivalencias,
no_duplicacion_latencia ni rueda_conjuncion. Solo lee y escribe el reporte.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path

CUARTOS = {
    "Q1_Separacion_1_3": (1, 2, 3),
    "Q2_Descenso_4_6": (4, 5, 6),
    "Q3_Ordeal_7_9": (7, 8, 9),
    "Q4_Retorno_10_12": (10, 11, 12),
}


def _load_plugin(path: Path):
    if not path.is_file():
        return None
    spec = importlib.util.spec_from_file_location("plugin_circulo_monomito_v2", str(path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules["plugin_circulo_monomito_v2"] = mod
    spec.loader.exec_module(mod)
    return mod


def _norm_slug(s: str) -> str:
    return re.sub(r"_y_", "_", s.strip().casefold())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--color", type=Path, required=True, help="COLOR_SOMBRA_*.json")
    ap.add_argument("--result", type=Path, required=True, help="RESULT_*.json sellado")
    ap.add_argument("--plugin", type=Path, default=None,
                    help="plugin_circulo_monomito_v2.py (por defecto, motor/motor/ junto al motor)")
    ap.add_argument("--out", type=Path, required=True, help="reporte .md de salida")
    args = ap.parse_args()

    color = json.loads(args.color.read_text(encoding="utf-8"))
    result = json.loads(args.result.read_text(encoding="utf-8"))

    plugin_path = args.plugin
    if plugin_path is None:
        # motor/laterales/teoria_color/ -> motor/motor/plugin_circulo_monomito_v2.py
        plugin_path = Path(__file__).resolve().parent.parent.parent / "motor" / "plugin_circulo_monomito_v2.py"
    plugin = _load_plugin(plugin_path)
    estructuras = getattr(plugin, "ESTRUCTURAS_CANDIDATAS", None) if plugin else None

    # etapa (numero, slug) -> cuarto, según el plugin; si no hay plugin, por rango numérico.
    etapa_a_cuarto: dict[int, str] = {}
    etapa_slug: dict[int, str] = {}
    if isinstance(estructuras, dict):
        for cuarto, data in estructuras.items():
            for etapa in data.get("etapas") or []:
                m = re.match(r"(\d+)[_](.+)$", str(etapa))
                if m:
                    n = int(m.group(1))
                    etapa_a_cuarto[n] = cuarto
                    etapa_slug[n] = m.group(2)
    else:
        for cuarto, nums in CUARTOS.items():
            for n in nums:
                etapa_a_cuarto[n] = cuarto

    hipotesis = (color.get("hipotesis") or {})
    mono_fams = sorted(k for k in hipotesis if k.startswith("monomito_"))
    filas = []
    for fam in mono_fams:
        entry = hipotesis[fam] or {}
        col = entry.get("color") or {}
        tono = col.get("tono") or {}
        sat = col.get("saturacion")
        m = re.match(r"monomito_(\d+)[_](.+)$", fam)
        if not m:
            filas.append({"familia": fam, "etapa": None, "cuarto": None,
                          "mapeo": "NO_MAPEABLE (nombre sin numero de etapa)",
                          "tono": tono, "saturacion": sat})
            continue
        n = int(m.group(1))
        slug = m.group(2)
        cuarto = etapa_a_cuarto.get(n)
        if cuarto is None:
            filas.append({"familia": fam, "etapa": n, "cuarto": None,
                          "mapeo": "NO_MAPEABLE (etapa fuera de 1-12)",
                          "tono": tono, "saturacion": sat})
            continue
        slug_plugin = etapa_slug.get(n)
        if slug_plugin is None:
            mapeo = "por numero (sin plugin para verificar slug)"
        elif _norm_slug(slug) == _norm_slug(slug_plugin):
            mapeo = "directo por numero y slug"
        else:
            mapeo = f"por numero; slug difiere (familia '{slug}' vs etapa '{slug_plugin}')"
        filas.append({"familia": fam, "etapa": n, "cuarto": cuarto,
                      "mapeo": mapeo, "tono": tono, "saturacion": sat})

    mono = ((result.get("features") or {}).get("plugin_circulo_monomito") or {})
    posicion = mono.get("posicion_monomito_por_corte") or []
    por_corte = []
    cuarto_a_cortes: dict[str, list[str]] = {}
    for p in posicion:
        cid = p.get("corte")
        activos = list(p.get("cuadrante_activo") or [])
        por_corte.append({"corte": cid, "cuadrante_activo": activos,
                          "hilos": list(p.get("hilos_presentes") or []),
                          "inyectado": p.get("caldero_inyectado_en_resolucion")})
        for q in activos:
            cuarto_a_cortes.setdefault(q, []).append(cid)
    bridge = mono.get("caldero_bridge") or {}
    h1 = (result.get("H1") or {}).get("family")
    h2 = (result.get("H2") or {}).get("family")

    case_id = result.get("case_id") or args.color.stem
    lineas = []
    lineas.append(f"# Cuartos del monomito en la rueda — {case_id}")
    lineas.append("")
    lineas.append(f"Fuentes: `{args.color.name}` (COLOR_SOMBRA) y `{args.result.name}` (RESULT sellado).")
    lineas.append(f"Plugin de cuartos: `{plugin_path.name}`"
                  + (" (leído)" if plugin is not None else " (NO ENCONTRADO: mapeo solo por rango numérico 1-3/4-6/7-9/10-12)"))
    lineas.append(f"H1: {h1} | H2: {h2}")
    lineas.append("")
    lineas.append("## Familias monomito_* con color en la rueda (tablero sombra)")
    lineas.append("")
    lineas.append("| familia | etapa | cuarto | mapeo | eje dominante | saturación sombra |")
    lineas.append("|---|---|---|---|---|---|")
    for f in filas:
        tono = f["tono"] or {}
        eje = max(tono, key=tono.get) if tono else "?"
        sat = f["saturacion"]
        sat_s = f"{sat:.4f}" if isinstance(sat, (int, float)) else "?"
        lineas.append(f"| {f['familia']} | {f['etapa']} | {f['cuarto'] or '—'} | {f['mapeo']} | {eje} | {sat_s} |")
    lineas.append("")
    lineas.append("## Cuadrante activo por corte (RESULT, plugin_circulo_monomito)")
    lineas.append("")
    for p in por_corte:
        act = ", ".join(p["cuadrante_activo"]) if p["cuadrante_activo"] else "(ninguno)"
        hilos = ", ".join(p["hilos"]) if p["hilos"] else "(ninguno)"
        lineas.append(f"- {p['corte']}: cuadrante activo {act} | hilos {hilos} | caldero inyectado: {p['inyectado']}")
    lineas.append("")
    lineas.append("## Por cuarto de cada familia: cortes donde ese cuarto estuvo activo")
    lineas.append("")
    for f in filas:
        cuarto = f["cuarto"]
        if cuarto is None:
            lineas.append(f"- {f['familia']}: sin cuarto mapeable; no se le asignan cortes.")
            continue
        cortes = cuarto_a_cortes.get(cuarto) or []
        cortes_s = ", ".join(cortes) if cortes else "(ningún corte con este cuarto activo)"
        lineas.append(f"- {f['familia']} (etapa {f['etapa']}, {cuarto}): cortes con {cuarto} activo: {cortes_s}.")
    lineas.append("")
    lineas.append("## Puente Caldero → cuartos (en este RESULT)")
    lineas.append("")
    lineas.append(f"- current_neighbors mapeados al vocabulario monomito: {bridge.get('current_neighbors')}")
    lineas.append(f"- vecinos crudos: {bridge.get('raw_current_neighbors')} | ignorados sin mapear: {len(bridge.get('ignored_unmapped_neighbors') or [])}")
    lineas.append(f"- injected_cut: {bridge.get('injected_cut')} | mapping: {bridge.get('mapping')}")
    lineas.append("")
    lineas.append("## Lectura honesta")
    lineas.append("")
    n_con_cuarto = sum(1 for f in filas if f["cuarto"])
    lineas.append(f"- Familias monomito_* con color: {len(filas)}; con cuarto mapeable: {n_con_cuarto}.")
    if bridge.get("current_neighbors"):
        lineas.append("- El puente Caldero aportó vecinos al vocabulario monomito en esta corrida.")
    else:
        lineas.append("- El puente Caldero NO aportó ningún vecino al vocabulario monomito en esta corrida: los cuadrantes por corte salen solo de los tokens de los cortes, no de los vecinos.")
    lineas.append("- El cuadrante activo por corte lo decide el plugin por coocurrencia de tokens del corte con tokens_candidatos del cuarto, NO por el índice del corte: un C1 puede salir en Q2 y un C5 en Q4. El cuarto de la familia (por su número de etapa) y el cuadrante activo del corte son dos cosas distintas; la tabla de arriba las cruza sin confundirlas.")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print(f"OK: {len(filas)} familias monomito, {len(por_corte)} cortes -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
