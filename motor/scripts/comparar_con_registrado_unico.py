#!/usr/bin/env python3
"""PASO FINAL (después del análisis a ciegas). Único script del paquete que lee lo registrado:
CONSOLIDADO_DIAGNOSTICO_20260927/tablas/OBJETIVOS_T1.json (T5_regla_puntuar_t1).
Vocabulario: coincide / no coincide con lo registrado; sostenido (CIERRE_ESTRICTO) / latente. Sin veredictos."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent; TAB = ROOT / "tablas"
OBJ = json.loads(Path("/workspace/CONSOLIDADO_DIAGNOSTICO_20260927/tablas/OBJETIVOS_T1.json").read_text())
F = json.loads((TAB / "TABLA_UNICO.json").read_text())
ABL = {(r["caso"], r["modo"]): r for r in json.loads((TAB / "ABLACION_VOTOS_LATERALES.json").read_text())}
filas, agg = [], {}
for f in F:
    C, M = f["caso"], f["modo"]; T = set(OBJ[C]["T5_regla_puntuar_t1"])
    sost = f["cierre_estricto"] == "CIERRE_ESTRICTO"
    cls = lambda co, s: ("coincide" if co else "no-coincide") + "-" + ("sostenido" if s else "latente")
    a = ABL.get((C, M), {})
    e = a.get("ESTRICTO_tirada") or {}; f0 = a.get("UNICO_FAMILIAS_TOKENS_0") or {}
    fila = {"caso": C, "modo": M, "top1": f["top1"], "top2": f["top2"], "top1_coincide": f["top1"] in T, "top2_coincide": f["top2"] in T,
            "cierre_estricto": f["cierre_estricto"], "clase_UNICO": cls(f["top1"] in T, sost),
            "clase_ESTRICTO_tirada": cls(e.get("top1") in T, e.get("cierre_estricto") == "CIERRE_ESTRICTO") if e else None,
            "clase_UNICO_familias_0": cls(f0.get("top1") in T, f0.get("cierre_estricto") == "CIERRE_ESTRICTO") if f0 else None,
            "aquiles_remuestreo_coincide_registrado": f.get("aquiles_remuestreo_ganador") in T}
    filas.append(fila)
    for sub, ok in (("PREFIX", M == "PREFIX"), ("TODOS", True)):
        if not ok: continue
        for V in ("clase_UNICO", "clase_ESTRICTO_tirada", "clase_UNICO_familias_0"):
            d = agg.setdefault(sub, {}).setdefault(V, {"coincide-sostenido": 0, "coincide-latente": 0, "no-coincide-sostenido": 0, "no-coincide-latente": 0})
            if fila[V]: d[fila[V]] += 1
(TAB / "COMPARACION_REGISTRADO_UNICO.json").write_text(json.dumps({"filas": filas, "agregado": agg}, ensure_ascii=False, indent=1))
print(json.dumps(agg, ensure_ascii=False, indent=1))
for x in filas: print(x["caso"], x["modo"], x["top1"], x["top1_coincide"], x["top2_coincide"], x["clase_UNICO"], "| estricto:", x["clase_ESTRICTO_tirada"], "| fam0:", x["clase_UNICO_familias_0"])
