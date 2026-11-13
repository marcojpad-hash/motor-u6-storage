#!/usr/bin/env python3
"""Ejercicio piloto de predictibilidad (reserva 2.A.1): F001, 5 casos.

Para cada caso: carga el _PRIMARY_RESULT.json de la corrida, corre la
predictibilidad ORIGINAL y la AJUSTADA (reconexión: DH + cuadrante) con el
archivo modificado de la reserva, y compara contra el desenlace sellado:
¿la familia del desenlace real queda más arriba con la ajustada que con la
original? ¿H1 (rank_fusion) coincide con el desenlace?

Salida: JSON con el ranking original vs ajustado por caso y la posición del
desenlace en cada uno.
"""
import importlib.util
import json
import sys
from pathlib import Path

ALT = Path("/home/hatch/workspace/u6-alterno/motor-cameo")
BASE = ALT / "motor" / "motor"          # contiene Engine_V5_CANONICO_SOLO.py
MOD = Path("/home/hatch/workspace/reconexion-2a1-staging2/motor/motor/predictibilidad_set_021.py")

spec = importlib.util.spec_from_file_location("pred021_2a1", str(MOD))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

LOTE = sys.argv[1] if len(sys.argv) > 1 else "F001"
runs_dir = ALT / "motor" / "runs"
cola = ALT / "casos" / "fabrica" / "cola"

casos = sorted(p.name for p in cola.iterdir() if p.name.startswith(f"CAL_{LOTE}_"))
out = {"lote": LOTE, "casos": []}

for case_id in casos:
    run_dir = runs_dir / f"ESTANDAR__{case_id}"
    res_path = run_dir / "_PRIMARY_RESULT.json"
    ent_path = cola / case_id / "entrada.json"
    des_path = cola / case_id / "desenlace_sellado.json"
    if not (res_path.exists() and ent_path.exists() and des_path.exists()):
        out["casos"].append({"case_id": case_id, "error": "faltan archivos"})
        continue
    result = json.loads(res_path.read_text())
    case = json.loads(ent_path.read_text())
    desenlace = json.loads(des_path.read_text()).get("familias") or []
    escala = mod.escala_predictibilidad(result, case, BASE)
    por_h = escala.get("por_hipotesis") or {}
    # ranking por original y por ajustada (solo familias con ambas)
    orig = sorted(por_h.items(), key=lambda kv: -kv[1]["predictibilidad_estructural_0_1"])
    ajus = sorted(por_h.items(), key=lambda kv: -kv[1]["predictibilidad_estructural_ajustada_0_1"])
    rank_orig = {fam: i + 1 for i, (fam, _) in enumerate(orig)}
    rank_ajus = {fam: i + 1 for i, (fam, _) in enumerate(ajus)}
    h1 = (result.get("H1") or {}).get("family") or (result.get("apuesta") or {}).get("H1")
    fila = {"case_id": case_id, "H1_rank_fusion": h1,
            "H1_en_desenlace": bool(h1 and h1 in desenlace),
            "desenlace_familias": desenlace,
            "top5_original": [f for f, _ in orig[:5]],
            "top5_ajustado": [f for f, _ in ajus[:5]],
            "posicion_desenlace": {}}
    for fam in desenlace:
        fila["posicion_desenlace"][fam] = {
            "original": rank_orig.get(fam),
            "ajustada": rank_ajus.get(fam),
            "p_orig": (por_h.get(fam) or {}).get("predictibilidad_estructural_0_1"),
            "p_ajus": (por_h.get(fam) or {}).get("predictibilidad_estructural_ajustada_0_1"),
        }
    out["casos"].append(fila)

print(json.dumps(out, indent=2, ensure_ascii=False))
