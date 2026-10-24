#!/usr/bin/env python3
"""Pruebas U4_todos_tokens: cuello top-5 (no borrado), validador sin MAS_DE_5, clases de movimiento de fondo, contrato lateral."""
import importlib.util, json, random, sys, copy
from pathlib import Path
M = Path(__file__).resolve().parents[1] / "motor"
def load(n, f):
    s = importlib.util.spec_from_file_location(n, str(M / f)); m = importlib.util.module_from_spec(s); sys.modules[n] = m; s.loader.exec_module(m); return m
nat = load("nat_t", "MOTOR_V15_3_NATIVO_V0_9_UNICO.py"); mf = load("mf_t", "movimiento_de_fondo_u4.py")
lib, canon = nat.load_canonical(); C = sorted(canon)
ok = 0
def check(name, cond):
    global ok
    print(("[PASS] " if cond else "[FAIL] ") + name); ok += bool(cond)
    if not cond: raise SystemExit(1)
# 1) <=5: identidad exacta (regresión)
rows = [[C[0], 0.70], [C[1], 0.84], [C[2], 0.60]]
sel, lg = nat.cuello_top_k("X", "P", rows, canon)
check("<=5 tokens: pasan tal cual y sin log", sel == rows and lg is None)
# 2) >5: 5 al Engine, catálogo primero, peso desc, posición desempata; nada se pierde
rows = [["NO_EXISTE_EN_244", 0.84], [C[3], 0.84], [C[4], 0.70], [C[5], 0.84], [C[6], 0.62], [C[7], 0.84], [C[8], 0.84], [C[9], 0.84]]
sel, lg = nat.cuello_top_k("X", "A", rows, canon)
check("cuello: 5 al Engine", len(sel) == 5)
check("cuello: primero catálogo, luego peso, desempate por posición", [t for t, _ in sel] == [C[3], C[5], C[7], C[8], C[9]])
check("cuello: al_engine + fuera = entrada (no borra)", sorted([x[0] for x in lg["al_engine"]] + [x["token"] for x in lg["quedan_fuera_del_engine"]]) == sorted(t for t, _ in rows))
check("cuello: determinista", nat.cuello_top_k("X", "A", rows, canon) == (sel, lg))
# 3) validador: ya no lanza MAS_DE_5; peso fuera de contrato sigue lanzando
big = [[C[i], 0.70] for i in range(12)]
h = nat.validar_corte("X", big, big[:3], big[:5], canon)
check("validador: 12 tokens por eje no lanza; registra cuello", h["P"] == 0 and h["cuello_top5"]["P"] == {"n_entrada": 12, "n_al_engine": 5})
try:
    nat.validar_corte("X", [[C[0], 0.90]], [], [], canon); r = False
except RuntimeError as e:
    r = "PESO_FUERA" in str(e)
check("validador: peso fuera de 0.60–0.84 sigue rechazado (no se recorta en silencio)", r)
# 4) clases
F = mf.FAM; T = mf.TOK
check("PICO", mf.clasificar([0.0, 0.01, 0.01, 0.09, 0.09], [True] * 5, F)["clase"] == "PICO")
check("MESETA", mf.clasificar([0.05, 0.055, 0.06, 0.058, 0.06], [True] * 5, F)["clase"] == "MESETA")
check("ASCENSO_LENTO", mf.clasificar([0.01, 0.025, 0.04, 0.052, 0.065], [True] * 5, F)["clase"] == "ASCENSO_LENTO")
check("DESCENSO", mf.clasificar([0.08, 0.07, 0.06, 0.05, 0.04], [True] * 5, F)["clase"] == "DESCENSO")
check("LATENTE_DORMIDO (token)", mf.clasificar([0.7, 0.0, 0.0, 0.72, 0.7], [True, False, False, True, True], T)["clase"] == "LATENTE_DORMIDO")
check("token aislado = PICO", mf.clasificar([0.0, 0.8, 0.0], [False, True, False], T)["clase"] == "PICO")
# 5) contrato lateral sobre una corrida real (si existe) — no muta result, RNG restaurado
rp = Path("/workspace/UNIFICADO_20261011/TRABAJO/results/U4/SELLADOS/CIEGO_13_MUSK/RESULT_CIEGO_13_MUSK_run1.json")
ip = Path("/workspace/UNIFICADO_20261011/TRABAJO/inputs_sellados/IN_CIEGO_13_MUSK.json")
if rp.is_file() and ip.is_file():
    res = json.load(open(rp)); case = json.load(open(ip)); pat = json.load(open(M / "patterns_final_v14.json"))
    snap = json.dumps({k: res.get(k) for k in ("predictor", "cierre_final", "hipotesis_necesarias_suficientes")}, sort_keys=True)
    random.seed(123); st = random.getstate()
    out = mf.run(case, res, M, pat, nat, monte_carlo=True, seed=0, p021=load("p021_t", "predictibilidad_set_021.py"))
    check("lateral: can_decide_H=False y no reordena", out["can_decide_H"] is False and out["reordena"] is False)
    check("lateral: no muta predictor/cierre/set", snap == json.dumps({k: res.get(k) for k in ("predictor", "cierre_final", "hipotesis_necesarias_suficientes")}, sort_keys=True))
    check("lateral: estado RNG restaurado", random.getstate() == st)
    check("traza completa: serie de cada token del input", set(out["series_tokens"]) == {t for c in case["cuts"] for e in "PAC" for t, _ in c[e]})
    check("sin null en el bloque", "null" not in json.dumps(out))
print(f"OK {ok}")
