#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lectura_negativo_ricci_vs_billar_v0_1.py  — PROPUESTA (no cableado, no tubo)

Lectura por negativo (corrección Mj 2026-09-27): comparar Ricci–Forman vs Billar
por familia/candidato: lo que uno detecta y el otro no.

Contrato: CONTRATO_ENFOQUE_CORPUS17_BILLAR_NEGATIVO_20260923.md
  - Billar = cuello de ruido: "qué pares no convergen / qué región se vació" -> resta candidatos.
  - El negativo es descarte, no letrero. No elige H. Alimenta_H = NO. writes_H = False.
  - Si la lente no tiene señal vs nulo -> LATENTE (no "no hay caso", no inventar).

Señales por familia f:
  billar_conv(f) := n_conv_v0_2(f) > 0         (convergencias billar v0.2, tau del run)
  billar_conv_vivo(f) := #conv con both_present_vivo (diagnóstico estricto; informativo)
  ricci_neg(f)  := mean(Ric_F de aristas incidentes a f) < 0   (nodo en región "abre")
                   None si f no es familia viva para Ricci.

Cuadrantes (converge billar × curvatura negativa Ricci) y señal de descarte PROPUESTA:
  SOLO_BILLAR  (conv=sí, neg=no) -> 0 señales negativas -> SE_SOSTIENE (no resta)
  AMBOS        (conv=sí, neg=sí) -> discordancia: billar junta órbita, Ricci abre -> TENSION_LATENTE
  NINGUNO      (conv=no, neg=no) -> discordancia: billar no ve convergencia, Ricci cohesiona -> DESCARTE_DEBIL_LATENTE
  SOLO_RICCI   (conv=no, neg=sí) -> 2 señales negativas (no converge + abre) -> DESCARTE (resta candidato)
  SIN_RICCI    (f no viva en Ricci) -> solo billar informa -> LATENTE
Variante ESTRICTA (reportada al lado): billar_conv := n_conv con both_present_vivo > 0;
  ricci_neg := fracción de aristas incidentes con Ric_F<0 >= 0.5.
Nivel PAR: ambas lentes son por pares; se cruza convergencia billar del par vs signo Ric_F de la arista.
Gating por nulo: si |z| < Z_MIN en una lente, su señal se marca "sin_señal_vs_nulo" y
la etiqueta final lleva sufijo _BAJO_NULO (se reporta, no se promueve).

Uso:
  python3 lectura_negativo_ricci_vs_billar_v0_1.py --run-dir <UNIFICADO_V0_16_RUN_20260926> \
      --casos 0926,0924,CAL --out <dir>
Solo lectura sobre los JSON de entrada. No importa Engine ni 244.
"""
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path
from statistics import mean

VERSION = "lectura_negativo_ricci_vs_billar_v0_1"
ESTADO = "PROPUESTA"
ALIMENTA_H = "NO"
Z_MIN = 2.0
ETIQ = {
    ("si", "no"): ("SOLO_BILLAR", "SE_SOSTIENE", 0),
    ("si", "si"): ("AMBOS", "TENSION_LATENTE", 1),
    ("no", "no"): ("NINGUNO", "DESCARTE_DEBIL_LATENTE", 1),
    ("no", "si"): ("SOLO_RICCI", "DESCARTE", 2),
}
CASO_ETIQ = {"0926": "GALILEO 0926 RESOLUCION", "0924": "GALILEO 0924 NUEVO_EJERCICIO", "CAL": "GALILEO 0926 CALIBRACION"}


def sha16(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def leer(run: Path, caso: str):
    lent = run / "lentes_billar_ricci_outputs"
    pr = run / f"RESULT_G_E_V0163_D_lentes_{caso}.json"
    pb = lent / f"BILLAR_V0_2_{caso}.json"
    pk = lent / f"RICCI_V0_1_{caso}.json"
    for p in (pr, pb, pk):
        if not p.is_file():
            raise FileNotFoundError(p)
    return pr, pb, pk, json.loads(pr.read_text()), json.loads(pb.read_text()), json.loads(pk.read_text())


def analizar(run: Path, caso: str) -> dict:
    pr, pb, pk, R, B, K = leer(run, caso)
    fb, fk = R["features"]["billar_circular_v0_2"], R["features"]["ricci_forman_v0_1"]
    # consistencia: la lente embebida en variante E debe coincidir con el standalone
    consist = {
        "billar_N_real_v0_2": (fb.get("N_real_v0_2"), B["v0_2"]["N_real"]),
        "ricci_media_Ric": (fk.get("media_Ric"), K["ricci"]["media"]),
    }
    consist_ok = all(a == b for a, b in consist.values())
    z_b = B["v0_2"]["null"]["z_score"]
    z_k = K.get("z_media_Ric")
    # billar por familia
    conv = {f: 0 for f in B["familias"]}
    conv_vivo = {f: 0 for f in B["familias"]}
    for ev in B["convergencias_v0_2"]:
        for f in ev["familias"]:
            conv[f] = conv.get(f, 0) + 1
            if ev.get("both_present_vivo"):
                conv_vivo[f] = conv_vivo.get(f, 0) + 1
    # ricci por familia
    inc = {}
    for a in (K.get("ricci") or {}).get("aristas") or []:
        par = a.get("par") or ([a["a"], a["b"]] if ("a" in a and "b" in a) else [])
        ric_f = a["Ric_F"] if "Ric_F" in a else a.get("ricci_forman")
        if ric_f is None:
            continue
        for f in par:
            inc.setdefault(f, []).append(ric_f)
    vivas_k = set(K.get("familias_vivas") or [])
    if not vivas_k:
        vivas_k = set(inc.keys())
    fams = sorted(set(B["familias"]) | vivas_k)
    h1 = (R.get("H1") or {}).get("family")
    h2 = (R.get("H2") or {}).get("family")
    filas = []
    for f in fams:
        c = conv.get(f, 0)
        cb = "si" if c > 0 else "no"
        if f in vivas_k and inc.get(f):
            m = mean(inc[f]); nneg = sum(1 for x in inc[f] if x < 0)
            kn = "si" if m < 0 else "no"
            cuad, senal, nsen = ETIQ[(cb, kn)]
        else:
            m, nneg, kn = None, None, None
            cuad, senal, nsen = "SIN_RICCI", "LATENTE", None
        # variante ESTRICTA: billar solo convergencias con ambas familias vivas; Ricci = mayoría de aristas "abre"
        cbe = "si" if conv_vivo.get(f, 0) > 0 else "no"
        if f in vivas_k and inc.get(f):
            kne = "si" if (sum(1 for x in inc[f] if x < 0) / len(inc[f])) >= 0.5 else "no"
            cuad_e, senal_e, _ = ETIQ[(cbe, kne)]
        else:
            cuad_e, senal_e = "SIN_RICCI", "LATENTE"
        bajo = []
        if abs(z_b) < Z_MIN: bajo.append("billar")
        if z_k is None or abs(z_k) < Z_MIN: bajo.append("ricci")
        filas.append({
            "familia": f,
            "billar_n_conv": c, "billar_n_conv_vivo": conv_vivo.get(f, 0), "billar_converge": cb,
            "ricci_mean_inc": None if m is None else round(m, 4),
            "ricci_aristas": None if f not in inc else len(inc[f]), "ricci_aristas_neg": nneg,
            "ricci_negativa": kn,
            "cuadrante": cuad, "senal_descarte": senal + ("_BAJO_NULO" if bajo and senal != "SE_SOSTIENE" else ""),
            "n_senales_negativas": nsen,
            "cuadrante_estricto": cuad_e, "senal_descarte_estricto": senal_e,
            "lentes_sin_senal_vs_nulo": bajo,
            "es_H1": f == h1, "es_H2": f == h2,
        })
    # nivel PAR (ambas lentes son pairwise): billar converge en el par vs arista Ricci negativa
    pc, pcv = {}, {}
    for ev in B["convergencias_v0_2"]:
        k2 = tuple(sorted(ev["familias"]))
        pc[k2] = pc.get(k2, 0) + 1
        if ev.get("both_present_vivo"): pcv[k2] = pcv.get(k2, 0) + 1
    ric_e = {tuple(sorted(a["par"])): a["Ric_F"] for a in K["ricci"]["aristas"]}
    pares = []
    for k2 in sorted(set(pc) | set(ric_e)):
        cb = "si" if pc.get(k2, 0) > 0 else "no"
        rf = ric_e.get(k2)
        if rf is None:
            cuad = "SOLO_BILLAR_SIN_ARISTA"  # nunca co-vivos en Top5: billar ve convergencia de fase sin co-ocurrencia
        else:
            cuad = ETIQ[(cb, "si" if rf < 0 else "no")][0]
        pares.append({"par": list(k2), "billar_n_conv": pc.get(k2, 0), "billar_n_conv_vivo": pcv.get(k2, 0),
                      "ricci_F": rf, "cuadrante": cuad})
    resumen_pares = {}
    for x in pares: resumen_pares[x["cuadrante"]] = resumen_pares.get(x["cuadrante"], 0) + 1
    return {
        "version": VERSION, "estado": ESTADO, "Alimenta_H": ALIMENTA_H, "writes_H": False,
        "caso": caso, "caso_id": R.get("case_id"), "etiqueta": CASO_ETIQ.get(caso, caso),
        "inputs_sha16": {pr.name: sha16(pr), pb.name: sha16(pb), pk.name: sha16(pk)},
        "consistencia_E_vs_standalone": {k: list(v) for k, v in consist.items()}, "consistencia_ok": consist_ok,
        "z_billar_v0_2": z_b, "z_ricci_media": z_k, "Z_MIN": Z_MIN,
        "H1_contexto": h1, "H2_contexto": h2,
        "nota": "H1/H2 solo contexto de lectura; este módulo no escribe ni reordena H.",
        "filas": filas,
        "pares": pares, "resumen_pares": resumen_pares,
    }


def tabla_md(res: dict) -> str:
    L = [f"### {res['etiqueta']} ({res['caso_id']})",
         f"z_billar_v0_2={res['z_billar_v0_2']} · z_ricci={res['z_ricci_media']} · consistencia E↔standalone={'OK' if res['consistencia_ok'] else 'FALLA'} · H1(contexto)={res['H1_contexto']}",
         "", "| familia | billar conv (vivo) | Ricci mean inc (neg/tot) | cuadrante | señal descarte | cuadrante ESTRICTO | señal ESTRICTA |", "|---|---|---|---|---|---|---|"]
    for r in res["filas"]:
        mk = " **(H1)**" if r["es_H1"] else (" (H2)" if r["es_H2"] else "")
        ric = "—" if r["ricci_mean_inc"] is None else f"{r['ricci_mean_inc']} ({r['ricci_aristas_neg']}/{r['ricci_aristas']})"
        L.append(f"| {r['familia']}{mk} | {r['billar_n_conv']} ({r['billar_n_conv_vivo']}) | {ric} | {r['cuadrante']} | {r['senal_descarte']} | {r['cuadrante_estricto']} | {r['senal_descarte_estricto']} |")
    L.append("")
    L.append("Pares (nivel arista): " + ", ".join(f"{k}={v}" for k, v in sorted(res["resumen_pares"].items())))
    dis = [x for x in res["pares"] if x["cuadrante"] in ("SOLO_RICCI", "AMBOS", "SOLO_BILLAR_SIN_ARISTA")]
    for x in dis:
        L.append(f"- {x['cuadrante']}: {x['par'][0]} ~ {x['par'][1]} · billar {x['billar_n_conv']} ({x['billar_n_conv_vivo']}) · Ric_F {x['ricci_F']}")
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--casos", default="0926,0924,CAL")
    ap.add_argument("--out", default=".")
    a = ap.parse_args(argv)
    run, out = Path(a.run_dir), Path(a.out); out.mkdir(parents=True, exist_ok=True)
    todos, md = [], ["# Lectura por negativo — Ricci–Forman vs Billar v0.2 (variante E) — PROPUESTA", ""]
    for c in a.casos.split(","):
        r = analizar(run, c.strip()); todos.append(r); md.append(tabla_md(r))
    (out / "NEGATIVO_RICCI_VS_BILLAR_V0_1.json").write_text(json.dumps(todos, ensure_ascii=False, indent=1))
    (out / "NEGATIVO_RICCI_VS_BILLAR_V0_1.md").write_text("\n".join(md))
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    sys.exit(main())
