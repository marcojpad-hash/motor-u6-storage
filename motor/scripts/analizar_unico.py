#!/usr/bin/env python3
"""Análisis A CIEGAS de la tirada del MOTOR ÚNICO: no lee lo registrado (OBJETIVOS). Compara contra ACTUAL y ESTRICTO
de la tirada estricta (solo sus salidas del motor). Escribe tablas/TABLA_UNICO.json/.md y raw_compacto/."""
import json, hashlib, re
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
TE = Path("/workspace/TIRADA_ESTRICTA_20260927/raw")
CASOS = ["BEZOS", "G0924", "G0926", "GCAL", "JOBS", "M35A", "MUSK"]; MODOS = ["FULL", "PREFIX"]
VOLATIL = re.compile(r"(^ts$|_ts$|hora|time|timestamp|fecha_corrida|seconds|elapsed|run_dir|event_id|inputs_sha16)", re.I)

def limpio(o):
    if isinstance(o, dict): return {k: limpio(v) for k, v in o.items() if not VOLATIL.search(str(k))}
    if isinstance(o, list): return [limpio(x) for x in o]
    if isinstance(o, str) and "/runs/" in o: return re.sub(r"/runs/[^/'\"\s]+", "/runs/X", o)
    return o
h = lambda o: hashlib.sha256(json.dumps(o, sort_keys=True, ensure_ascii=False, default=str).encode()).hexdigest()

def cands(r): return [c.get("family") for c in (r.get("predictor") or {}).get("candidates") or []]
def cierre(r):
    # PATCH 016: estado_cierre -> estado_motor_durante_corrida; estado_cierre_estricto -> estado_estricto_durante_corrida (fallback a nombres viejos)
    return ((r.get("estado_motor_durante_corrida") or r.get("estado_cierre") or {}).get("valor"),
            (r.get("estado_estricto_durante_corrida") or r.get("estado_cierre_estricto") or {}).get("valor"))

filas = []
for c in CASOS:
    for m in MODOS:
        f = {k: None for k in ()}
        r1 = json.loads((ROOT / f"raw/RESULT_UNICO__{c}__{m}__r1.json").read_text())
        r2 = json.loads((ROOT / f"raw/RESULT_UNICO__{c}__{m}__r2.json").read_text())
        rc = r1["reporte_caso"]; cu = cands(r1)
        prev = {}
        for v in ("ACTUAL", "ESTRICTO"):
            p = TE / f"RESULT_{v}__{c}__{m}__r1.json"
            if p.exists():
                rp = json.loads(p.read_text()); cp = cands(rp)
                prev[v] = {"top1": cp[0] if cp else None, "top2": cp[1] if len(cp) > 1 else None, "top10": cp[:10],
                           "cierre_vigente": cierre(rp)[0], "cierre_estricto": cierre(rp)[1]}
        det_full = h(limpio(r1)) == h(limpio(r2))
        det_nuc = h([cands(r1), r1.get("H1"), r1.get("H2"), rc]) == h([cands(r2), r2.get("H1"), r2.get("H2"), r2["reporte_caso"]])
        lu = r1.get("laterales_unico") or {}
        fam = ((r1.get("features") or {}).get("familias_tokens_puente") or {}).get("por_familia") or {}
        neg = ((r1.get("features") or {}).get("negativo_ricci_vs_billar") or {}).get("por_familia") or {}
        aqf = (r1.get("features") or {}).get("aquiles_h") or {}
        fila = {"caso": c, "modo": m, "top1": cu[0] if cu else None, "top2": cu[1] if len(cu) > 1 else None, "top10": cu[:10],
                "H1": rc.get("H1"), "H2": rc.get("H2"),
                "cierre_vigente": rc.get("estado_durante_corrida_vigente", rc.get("cierre_vigente")), "motivos_vigente": rc.get("motivos_durante_corrida_vigente", rc.get("motivos_vigente")),
                "cierre_estricto": rc.get("estado_durante_corrida_estricto", rc.get("cierre_estricto")), "motivos_estricto": rc.get("motivos_durante_corrida_estricto", rc.get("motivos_estricto")),
                "cierre_final": {k: (r1.get("cierre_final") or {}).get(k) for k in ("H1", "H2", "margen", "grado", "n_objeciones")},  # PATCH 016
                "guardianes": rc.get("guardianes"),
                "negativo_top1": rc.get("negativo_top1"), "negativo_top2": rc.get("negativo_top2"),
                "voto_negativo_discrimina": len(set(v.get("score") for v in neg.values())) > 1,
                "voto_familias_top1": (fam.get(cu[0]) or {}).get("score") if cu else None,
                "voto_familias_top2": (fam.get(cu[1]) or {}).get("score") if len(cu) > 1 else None,
                "aquiles_features_estado": aqf.get("estado"), "aquiles_remuestreo_ganador": rc.get("aquiles_ganador_remuestreo"),
                "aquiles_remuestreo_coincide_top1": rc.get("aquiles_coincide_top1"),
                "convergencia_lateral": rc.get("convergencia_lateral"),
                "memento_nucleo_en_favor_top1": ((lu.get("post") or {}).get("memento_vs_top1") or {}).get("nucleo_en_favor_de_top1"),
                "perfil_narrador": {k: ((lu.get("post") or {}).get("perfil_narrador") or {}).get(k) for k in ("n_puntos_ciegos", "n_preguntas")},
                "catalogo": {k: (r1.get("catalogo_patrones") or {}).get(k) for k in ("sha256", "n_patrones", "es_default_v14")},
                "validacion_puentes": ((r1.get("catalogo_patrones") or {}).get("validacion_puentes") or {}).get("estado"),
                "H_intacto": lu.get("verificacion_H_intacto"),
                "registro_componentes_conteo": (r1.get("registro_componentes") or {}).get("conteo"),
                "determinista_r1_r2_json_completo": det_full, "determinista_r1_r2_nucleo": det_nuc,
                "sha_nucleo": h([cands(r1), r1.get("H1"), r1.get("H2"), rc])[:16],
                "previas": prev}
        for v, p in prev.items():
            fila[f"vs_{v}"] = {"top1_igual": p["top1"] == fila["top1"], "top2_igual": p["top2"] == fila["top2"], "top10_igual": p["top10"] == fila["top10"],
                               "cierre_vigente_igual": p["cierre_vigente"] == fila["cierre_vigente"], "cierre_estricto_igual": p["cierre_estricto"] == fila["cierre_estricto"]}
        filas.append(fila)
        comp = {k: r1.get(k) for k in ("version", "catalogo_patrones", "reporte_caso", "estado_cierre", "estado_cierre_estricto", "estado_motor_durante_corrida", "estado_estricto_durante_corrida", "cierre_final", "registro_componentes")}
        comp["top10"] = cu[:10]; comp["laterales_unico"] = {k: lu.get(k) for k in ("registro_piezas", "convergencia_lateral", "verificacion_H_intacto")}
        (ROOT / "raw_compacto").mkdir(exist_ok=True)
        (ROOT / f"raw_compacto/COMPACTO_UNICO__{c}__{m}.json").write_text(json.dumps(comp, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
(ROOT / "tablas/TABLA_UNICO.json").write_text(json.dumps(filas, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
L = ["| caso | modo | top1 | top2 | cierre vigente | cierre estricto | Aquiles remuestreo = top1 | conv. lateral (t1/t2/emp) | r1=r2 | top1 vs ACTUAL | top1 vs ESTRICTO |", "|" + "---|" * 11]
for f in filas:
    cv = f["convergencia_lateral"] or {}
    L.append(f"| {f['caso']} | {f['modo']} | {f['top1']} | {f['top2']} | {f['cierre_vigente']} | {f['cierre_estricto']} | {'sí' if f['aquiles_remuestreo_coincide_top1'] else 'no'} | {cv.get('top1')}/{cv.get('top2')}/{cv.get('empate')} | {'sí' if f['determinista_r1_r2_nucleo'] else 'NO'}{'' if f['determinista_r1_r2_json_completo'] else ' (núcleo)'} | {'igual' if f.get('vs_ACTUAL',{}).get('top1_igual') else 'cambia'} | {'igual' if f.get('vs_ESTRICTO',{}).get('top1_igual') else 'cambia'} |")
(ROOT / "tablas/TABLA_UNICO.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print("\n".join(L))
for f in filas:
    for v in ("ACTUAL", "ESTRICTO"):
        d = f.get(f"vs_{v}") or {}
        dif = [k for k, x in d.items() if not x]
        if dif: print(f["caso"], f["modo"], v, dif, "prev:", f["previas"][v]["top1"], f["previas"][v]["top2"], f["previas"][v]["cierre_vigente"], f["previas"][v]["cierre_estricto"])
