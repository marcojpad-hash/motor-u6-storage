#!/usr/bin/env python3
"""Diff U5 vs U6 por caso (run1 off): H1/H2, grado, eje y set 021, top-5, A1, empates (A9), anomalías por tipo y severidad.
Uso: python3 u6/u6_diff.py ANOMALIAS_U5.json ANOMALIAS_U6.json RESULTS_U5_DIR RESULTS_U6_DIR OUT.json"""
import sys, json, glob
from pathlib import Path
from collections import Counter
a5, a6, r5, r6, outp = sys.argv[1:6]
def idx(p):
    A = json.loads(Path(p).read_text(encoding="utf-8")); out = {}
    for d in A["por_corrida"]:
        rid = Path(d["recibo"]).name
        if "_run1_off" in rid: out[Path(d["recibo"]).parent.name] = d
    return out
def top5(rec):
    c = rec["rank_fusion"]["candidatas_top"]
    c = sorted(c, key=lambda x: (x.get("operational_rank") is None, x.get("operational_rank") or 0)) if any(x.get("operational_rank") is not None for x in c) else c
    return [x["family"] for x in c[:5]]
def cuello(res):
    cu = ((res.get("motor") or {}).get("cuello_top5_engine") or {}).get("cortes") or []
    pos = ev = 0; fuera = set()
    for c in cu:
        d6 = c.get("desempate_U6")
        for f in c.get("quedan_fuera_del_engine") or []: fuera.add((c["corte"], c["eje"], f["token"]))
        if d6: pos += (d6.get("decididos_por") or {}).get("posicion", 0); ev += sum(v for k, v in (d6.get("decididos_por") or {}).items() if k != "posicion")
        else:
            wk = c.get("peso_corte"); pos += sum(1 for r in c.get("al_engine") or [] if r[1] == wk) * sum(1 for r in c.get("quedan_fuera_del_engine") or [] if r.get("w") == wk and r.get("en_catalogo"))
    return pos, ev, fuera
I5, I6 = idx(a5), idx(a6); filas = []
for case in sorted(set(I5) & set(I6)):
    d5, d6 = I5[case], I6[case]
    rec5 = json.loads(Path(glob.glob(f"{r5}/{case}/RESULT_{case}_run1_off_RECIBO_U5.json")[0]).read_text())
    rec6 = json.loads(Path(glob.glob(f"{r6}/{case}/RESULT_{case}_run1_off_RECIBO_U5.json")[0]).read_text())
    res5 = json.loads(Path(glob.glob(f"{r5}/{case}/RESULT_{case}_run1_off.json")[0]).read_text())
    res6 = json.loads(Path(glob.glob(f"{r6}/{case}/RESULT_{case}_run1_off.json")[0]).read_text())
    c5, c6 = Counter(x["tipo"] for x in d5["anomalias"]), Counter(x["tipo"] for x in d6["anomalias"])
    p5, e5, f5 = cuello(res5); p6, e6, f6 = cuello(res6)
    fila = {"caso": case,
            "H1": [rec5["H"]["H1"], rec6["H"]["H1"]], "H2": [rec5["H"]["H2"], rec6["H"]["H2"]],
            "grado": [rec5["H"]["grado_H1"], rec6["H"]["grado_H1"]], "eje_021": [rec5["H"]["eje_set_021"], rec6["H"]["eje_set_021"]],
            "set_021": [[x[0] for x in rec5["H"]["set_021"]], [x[0] for x in rec6["H"]["set_021"]]],
            "top5": [top5(rec5), top5(rec6)],
            "A1_declarado_sin_aporte": [c5.get("A1_DECLARADO_ACTIVO_APORTE_CERO", 0), c6.get("A1_DECLARADO_ACTIVO_APORTE_CERO", 0)],
            "A1_cableada_sin_senal_INFO": [c5.get("A1_CABLEADA_SIN_SENAL_EN_CASO", 0), c6.get("A1_CABLEADA_SIN_SENAL_EN_CASO", 0)],
            "dims_constantes": [len(rec5["rank_fusion"]["excluidas_constantes"] or []), len(rec6["rank_fusion"]["excluidas_constantes"] or [])],
            "senales_laterales": [[s["signal"] for s in rec5["rank_fusion"]["senales_laterales"] if s["discriminates"]], [s["signal"] for s in rec6["rank_fusion"]["senales_laterales"] if s["discriminates"]]],
            "A9_empates_peso_input": [c5.get("A9_EMPATE_PESO_EN_EJE", 0), c6.get("A9_EMPATE_PESO_EN_EJE", 0)],
            "cuello_pares_por_posicion": [p5, p6], "cuello_pares_por_evidencia": [e5, e6],
            "cuello_tokens_fuera_cambiados": len(f5 ^ f6),
            "A10_CEB": [sum(v for k, v in c5.items() if k.startswith("A10")), sum(v for k, v in c6.items() if k.startswith("A10"))],
            "A6_no_canonicos_MEDIA": [c5.get("A6_TOKENS_NO_CANONICOS", 0), c6.get("A6_TOKENS_NO_CANONICOS", 0)],
            "A7_ausentes": [c5.get("A7_ARCHIVO_REFERENCIADO_AUSENTE", 0), c6.get("A7_ARCHIVO_REFERENCIADO_AUSENTE", 0)],
            "A8": [sum(v for k, v in c5.items() if k.startswith("A8")), sum(v for k, v in c6.items() if k.startswith("A8"))],
            "A11_sin_llamadas": [len(next((x.get("modulos") for x in d5["anomalias"] if x["tipo"] == "A11_MODULO_EN_MOTOR_SIN_LLAMADAS"), []) or []),
                                 len(next((x.get("modulos") for x in d6["anomalias"] if x["tipo"] == "A11_MODULO_EN_MOTOR_SIN_LLAMADAS"), []) or [])],
            "A11_modulos_U6": next((x.get("modulos") for x in d6["anomalias"] if x["tipo"] == "A11_MODULO_EN_MOTOR_SIN_LLAMADAS"), []),
            "severidad": [d5["conteo_severidad"], d6["conteo_severidad"]],
            "anomalias_U6_por_tipo": dict(c6)}
    fila["cambia"] = [k for k in ("H1", "H2", "grado", "eje_021", "set_021", "top5") if fila[k][0] != fila[k][1]]
    filas.append(fila)
Path(outp).write_text(json.dumps({"diff": "U5_vs_U6_run1_off", "filas": filas}, ensure_ascii=False, indent=1), encoding="utf-8")
for f in filas: print(f["caso"], f["cambia"], f["A1_declarado_sin_aporte"], f["cuello_pares_por_posicion"], f["cuello_pares_por_evidencia"], f["dims_constantes"])
