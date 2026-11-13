#!/usr/bin/env python3
"""Corre una etapa (BASELINE / P1_NICHO / P2_ALIAS / P3_EMBUDO / P4_FIX) sobre las
5 sondas mínimas + Napoleón, y extrae un resumen compacto de cada RESULT.

Uso:  python3 casos/sondas_nicho_minima/correr_etapa.py <ETAPA>
Sale: motor/runs_etapas/<ETAPA>/RESUMEN_<ETAPA>.json  (compacto, ~KB)
      motor/RESULT_<ETAPA>_<CASO>.json                (completo, del runner)
No modifica el motor; solo corre y extrae.
"""
from __future__ import annotations
import json, subprocess, sys, os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]          # repo (motor-autorizado)
MOTOR = ROOT / "motor"
SONDAS = ROOT / "casos" / "sondas_nicho_minima"
CASOS = [
    ("SONDA_MONROE_TIPO", SONDAS / "SONDA_MONROE_TIPO.json"),
    ("SONDA_ALEJANDRO_TIPO", SONDAS / "SONDA_ALEJANDRO_TIPO.json"),
    ("SONDA_JOSE_A", SONDAS / "SONDA_JOSE_A.json"),
    ("SONDA_JOSE_EF", SONDAS / "SONDA_JOSE_EF.json"),
    ("SONDA_FREUD_C", SONDAS / "SONDA_FREUD_C.json"),
    ("NAPOLEON", ROOT / "casos" / "fabrica" / "cola" / "CAL_F001_01_NAPOLEON" / "entrada.json"),
]
PIEZAS = ("nicho_campo", "alias_reactivacion", "embudo_clinico", "fix_entrada")

def extraer(path: Path) -> dict:
    r = json.loads(path.read_text(encoding="utf-8"))
    si = r.get("salida_interpretable") or {}
    h1 = (si.get("H1") or {}).get("familia")
    h2 = (si.get("H2") or {}).get("familia")
    ap = si.get("apuesta_multiescenario") or {}
    lu = r.get("laterales_unico") or {}
    sp = (lu.get("sensores_pre") or {})
    # registro de piezas del hub (estados)
    reg = {}
    for e in (lu.get("pre") or {}).get("registro", []) or []:
        if isinstance(e, dict) and e.get("pieza"):
            reg[e["pieza"]] = {"estado": e.get("estado"), "aporte": str(e.get("aporte"))[:200]}
    # compactar la traza nicho (el por_corte completo vive en el RESULT)
    nc = sp.get("nicho_campo")
    nc_c = None
    if isinstance(nc, dict):
        nc_c = {"alpha": nc.get("alpha"), "cap": nc.get("cap"),
                "max_boost_pct_global": nc.get("max_boost_pct_global"),
                "foco_30_ambicion": nc.get("foco_30_ambicion"),
                "top_boosts": nc.get("top_boosts"),
                "por_corte_resumen": [{"corte": pc.get("corte"), "n_corte": pc.get("n_corte"),
                                       "n_con_campo": pc.get("n_con_campo"),
                                       "max_boost_pct": pc.get("max_boost_pct")} for pc in (nc.get("por_corte") or [])]}
    out = {
        "case_id": r.get("case_id"),
        "H1": h1, "H2": h2,
        "apuesta": (ap.get("apuesta_principal") or {}).get("escenario"),
        "sensores_pre_claves": sorted(sp.keys()),
        "piezas_registro": {p: reg.get(p) for p in PIEZAS if p in reg},
        "nicho_campo": nc_c,
        "alias_reactivacion": sp.get("alias_reactivacion"),
        "embudo_clinico": sp.get("embudo_clinico"),
        "fix_entrada": sp.get("fix_entrada"),
    }
    return out

def main():
    etapa = sys.argv[1]
    outdir = MOTOR / "runs_etapas" / etapa
    outdir.mkdir(parents=True, exist_ok=True)
    # Control: cada etapa arranca con el StinkBox VACÍO (el índice alimenta
    # al motor; sin reset, la etapa N vería los casos de la etapa N-1 y el
    # delta se contaminaría). Verificado: Napoleón 2 veces tras reset da
    # el mismo H1/H2; sin reset, H2 cambió (30_ambicion -> gobernante).
    import shutil
    for d in (ROOT / "STINKBOX_PERSISTENTE", ROOT / "STINKBOX_STORAGE"):
        shutil.rmtree(d, ignore_errors=True)
    env = os.environ.copy()
    env["STINKBOX_HOME"] = str(ROOT / "STINKBOX_PERSISTENTE")
    env["STINKBOX_STORAGE_ROOT"] = str(ROOT / "STINKBOX_STORAGE")
    resumen = {"etapa": etapa, "casos": {}}
    for nombre, entrada in CASOS:
        tag = f"{etapa}_{nombre}"
        print(f"[{etapa}] corriendo {nombre} ...", flush=True)
        p = subprocess.run(
            [sys.executable, "correr_estandar.py", str(entrada), tag],
            cwd=str(MOTOR), env=env, text=True, capture_output=True, timeout=600)
        res = MOTOR / f"RESULT_{tag}.json"
        if p.returncode != 0 or not res.is_file():
            resumen["casos"][nombre] = {"error": f"exit={p.returncode}", "stderr": p.stderr[-500:], "stdout": p.stdout[-500:]}
            print(f"[{etapa}] {nombre}: FALLO exit={p.returncode}", flush=True)
            continue
        s = extraer(res)
        s["exit"] = p.returncode
        resumen["casos"][nombre] = s
        print(f"[{etapa}] {nombre}: H1={s['H1']} H2={s['H2']}", flush=True)
    (outdir / f"RESUMEN_{etapa}.json").write_text(json.dumps(resumen, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[{etapa}] resumen en {outdir}/RESUMEN_{etapa}.json")

if __name__ == "__main__":
    main()
