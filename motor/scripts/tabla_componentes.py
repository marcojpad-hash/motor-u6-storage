#!/usr/bin/env python3
"""Tabla completa de componentes: estado por corrida (28 corridas de la línea base) y aporte."""
import json, glob, collections
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
agg = collections.OrderedDict()
for f in sorted(glob.glob(str(ROOT / "raw/RESULT_UNICO__*__r[12].json"))):
    r = json.loads(Path(f).read_text())
    for x in r["registro_componentes"]["filas"]:
        k = (x.get("fuente"), x.get("pieza"))
        a = agg.setdefault(k, {"fuente": x.get("fuente"), "pieza": x.get("pieza"), "estados": collections.Counter(), "motivos": collections.Counter(), "alimenta_predictor": x.get("alimenta_predictor")})
        a["estados"][x.get("estado")] += 1; a["motivos"][str(x.get("motivo") or "")[:140]] += 1
rows = []
for a in agg.values():
    rows.append({"fuente": a["fuente"], "pieza": a["pieza"], "estados": dict(a["estados"]), "aporte_mas_frecuente": a["motivos"].most_common(1)[0][0], "alimenta_predictor": a["alimenta_predictor"]})
(ROOT / "tablas/COMPONENTES_UNICO.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
L = ["| fuente | pieza | estado (n corridas de 28) | aporte / motivo (más frecuente) |", "|---|---|---|---|"]
for r in rows:
    est = ", ".join(f"{k} {v}" for k, v in r["estados"].items())
    L.append(f"| {r['fuente']} | {r['pieza']} | {est} | {r['aporte_mas_frecuente'].replace('|', '/')} |")
(ROOT / "tablas/COMPONENTES_UNICO.md").write_text("\n".join(L) + "\n", encoding="utf-8")
c = collections.Counter()
for r in rows:
    for k in r["estados"]: c[k] += 1
print(len(rows), dict(c))
