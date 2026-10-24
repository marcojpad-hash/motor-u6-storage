#!/usr/bin/env python3
"""Monitoreo simple: compara recibos U5 de un mismo caso (mismo input sha y mismo modo de consulta) y marca deriva.
Uso: python3 u5/u5_monitor.py RECIBO_U5.json ... [--out MONITOR.json]
Compara: H1/H2/grado/cierre, eje y set 021, top-10 y rank_fusion (tolerancia 1e-6), señales laterales que discriminan,
hashes de módulos/catálogos no mutables, conjunto de archivos con llamadas y llamadas por archivo."""
import sys, json
from pathlib import Path
from collections import defaultdict

def clave(r): return (r["case_id"], r["hash_input"], (r.get("entorno") or {}).get("CONSULTA_DIRIGIDA"))

def comparar(a, b):
    d = []
    for k in ("H1", "H2", "grado_H1", "eje_set_021"):
        if a["H"][k] != b["H"][k]: d.append({"campo": "H." + k, "a": a["H"][k], "b": b["H"][k], "sev": "CRITICA" if k == "H1" else "ALTA"})
    if [tuple(x) for x in a["H"]["set_021"]] != [tuple(x) for x in b["H"]["set_021"]]: d.append({"campo": "H.set_021", "a": a["H"]["set_021"], "b": b["H"]["set_021"], "sev": "MEDIA"})
    for k in ("estado_final", "grado", "metodo_terminal"):
        if a["cierre"][k] != b["cierre"][k]: d.append({"campo": "cierre." + k, "a": a["cierre"][k], "b": b["cierre"][k], "sev": "ALTA"})
    ta = [(c["family"], c["rank_fusion"]) for c in a["rank_fusion"]["candidatas_top"]]; tb = [(c["family"], c["rank_fusion"]) for c in b["rank_fusion"]["candidatas_top"]]
    if [x[0] for x in ta] != [x[0] for x in tb]: d.append({"campo": "orden_top", "a": [x[0] for x in ta], "b": [x[0] for x in tb], "sev": "ALTA"})
    else:
        dif = [(f, x, y) for (f, x), (_, y) in zip(ta, tb) if x is not None and y is not None and abs(x - y) > 1e-6]
        if dif: d.append({"campo": "rank_fusion_valores", "dif": dif, "sev": "MEDIA"})
    sa = sorted(s["signal"] for s in a["rank_fusion"]["senales_laterales"] if s["discriminates"]); sb = sorted(s["signal"] for s in b["rank_fusion"]["senales_laterales"] if s["discriminates"])
    if sa != sb: d.append({"campo": "senales_que_discriminan", "a": sa, "b": sb, "sev": "MEDIA"})
    def hs(r): return {x.get("fuente_en_pack") or x["path"]: x["sha256"] for x in r["archivos_cargados"] if x.get("sha256") and x["clase"] != "estado_mutable"}
    ha, hb = hs(a), hs(b)
    ch = sorted(k for k in set(ha) & set(hb) if ha[k] != hb[k])
    if ch: d.append({"campo": "hash_modulos", "cambian": ch, "sev": "ALTA"})
    solo = sorted(set(ha) ^ set(hb))
    if solo: d.append({"campo": "modulos_cargados_distintos", "solo_en_uno": solo, "sev": "MEDIA"})
    ca = {x["basename"]: x["n_llamadas"] for x in a["ejecutado_instrumentado"]}; cb = {x["basename"]: x["n_llamadas"] for x in b["ejecutado_instrumentado"]}
    if set(ca) != set(cb): d.append({"campo": "archivos_ejecutados", "solo_a": sorted(set(ca) - set(cb)), "solo_b": sorted(set(cb) - set(ca)), "sev": "ALTA"})
    dl = {k: (ca[k], cb[k]) for k in set(ca) & set(cb) if ca[k] != cb[k]}
    if dl: d.append({"campo": "llamadas_por_archivo", "n_archivos_distintos": len(dl), "muestra": dict(sorted(dl.items())[:8]), "sev": "INFO"})
    return d

def monitorear(paths):
    rs = [json.loads(Path(p).read_text(encoding="utf-8")) for p in paths]
    g = defaultdict(list)
    for p, r in zip(paths, rs): g[clave(r)].append((p, r))
    out = []
    for (c, h, m), lst in sorted(g.items(), key=lambda x: str(x[0])):
        base_p, base = lst[0]
        for p, r in lst[1:]:
            d = comparar(base, r)
            out.append({"case_id": c, "input_sha256": h, "consulta": m, "a": base["run_id"], "b": r["run_id"],
                        "deriva": [x for x in d if x["sev"] != "INFO"], "info": [x for x in d if x["sev"] == "INFO"],
                        "estable": not [x for x in d if x["sev"] != "INFO"]})
        if len(lst) == 1: out.append({"case_id": c, "input_sha256": h, "consulta": m, "a": base["run_id"], "b": None, "estable": None, "nota": "una sola corrida: sin comparación"})
    return out

if __name__ == "__main__":
    a = sys.argv[1:]; o = None
    if "--out" in a: i = a.index("--out"); o = a[i + 1]; a = a[:i] + a[i + 2:]
    res = monitorear(a); s = json.dumps(res, ensure_ascii=False, indent=1, default=str)
    if o: Path(o).write_text(s, encoding="utf-8")
    for x in res: print(x["case_id"], x.get("consulta"), "ESTABLE" if x["estable"] else ("SIN_PAR" if x["estable"] is None else "DERIVA " + str([d["campo"] for d in x["deriva"]])))
