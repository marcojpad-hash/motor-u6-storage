#!/usr/bin/env python3
"""Compara una tirada nueva contra la LÍNEA BASE congelada (BASE_ESTABLE_MANIFEST.json) o contra otra carpeta de raw.
Sirve para medir cambios al cambiar de catálogo de patrones, de puentes o de piezas. A ciegas: no lee lo registrado.
Uso:
  comparar_corridas.py --raw DIR [--tag TAG] [--base BASE_ESTABLE_MANIFEST.json] [--out tablas/COMPARA_<tag>.json]
  (busca DIR/RESULT_UNICO__{CASO}__{MODO}__r1[__TAG].json)
Reporta por caso: top1/top2/top10 base vs nuevo, posición del top1 base en el ranking nuevo, estados de cierre,
catálogo (sha, n) de cada lado y top1 que ya no existe en el catálogo nuevo."""
import argparse, json
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
ap = argparse.ArgumentParser(); ap.add_argument("--raw", required=True); ap.add_argument("--tag", default="")
ap.add_argument("--base", default=str(ROOT / "BASE_ESTABLE_MANIFEST.json")); ap.add_argument("--out", default=None)
a = ap.parse_args()
B = json.loads(Path(a.base).read_text())
filas = []
for b in B["linea_base"]["corridas"]:
    C, M = b["caso"], b["modo"]; suf = f"__{a.tag}" if a.tag else ""
    p = Path(a.raw) / f"RESULT_UNICO__{C}__{M}__r1{suf}.json"
    if not p.exists():
        filas.append({"caso": C, "modo": M, "estado": "FALTA_CORRIDA", "ruta": str(p)}); continue
    r = json.loads(p.read_text()); cs = [x["family"] for x in (r.get("predictor") or {}).get("candidates") or []]
    cat = r.get("catalogo_patrones") or {}
    nuevo = {"top1": cs[0] if cs else None, "top2": cs[1] if len(cs) > 1 else None, "top10": cs[:10],
             "cierre_vigente": (r.get("estado_motor_durante_corrida") or r.get("estado_cierre") or {}).get("valor"), "cierre_estricto": (r.get("estado_estricto_durante_corrida") or r.get("estado_cierre_estricto") or {}).get("valor"),  # PATCH 016: nombres nuevos con fallback
             "cierre_final_grado": (r.get("cierre_final") or {}).get("grado"),
             "catalogo_sha8": (cat.get("sha256") or "")[:8], "n_patrones": cat.get("n_patrones"),
             "validacion_puentes": (cat.get("validacion_puentes") or {}).get("estado"), "marcas_duras": (cat.get("validacion_puentes") or {}).get("marcas_duras")}
    filas.append({"caso": C, "modo": M, "base": {k: b.get(k) for k in ("top1", "top2", "top10", "cierre_vigente", "cierre_estricto")} | {"catalogo_sha8": B["catalogo"]["sha256"][:8], "n_patrones": B["catalogo"]["n_patrones"]},
                  "nuevo": nuevo, "top1_igual": nuevo["top1"] == b["top1"], "top2_igual": nuevo["top2"] == b["top2"], "top10_igual": nuevo["top10"] == b["top10"],
                  "posicion_nueva_del_top1_base": (cs.index(b["top1"]) + 1) if b["top1"] in cs else None,
                  "cierre_vigente_igual": nuevo["cierre_vigente"] == b["cierre_vigente"], "cierre_estricto_igual": nuevo["cierre_estricto"] == b["cierre_estricto"]})
res = {"base": a.base, "raw": a.raw, "tag": a.tag,
       "resumen": {k: sum(1 for f in filas if f.get(k)) for k in ("top1_igual", "top2_igual", "top10_igual", "cierre_vigente_igual", "cierre_estricto_igual")} | {"n": len(filas)},
       "filas": filas}
out = Path(a.out) if a.out else ROOT / "tablas" / f"COMPARA_{a.tag or 'SIN_TAG'}.json"
out.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps(res["resumen"], ensure_ascii=False))
for f in filas:
    if f.get("estado"): print(f["caso"], f["modo"], f["estado"]); continue
    print(f"{f['caso']:6} {f['modo']:6} top1 {f['base']['top1']} -> {f['nuevo']['top1']} | top2 {f['base']['top2']} -> {f['nuevo']['top2']} | estricto {f['base']['cierre_estricto']} -> {f['nuevo']['cierre_estricto']}")
