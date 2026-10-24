#!/usr/bin/env python3
"""Pruebas U6: desempate del cuello por evidencia (sin mirar el futuro), modo legado, manifiesto en preflight, candado_plugins."""
import importlib.util, json, os, sys
from pathlib import Path
R = Path(__file__).resolve().parents[1]; M = R / "motor"
def load(n, p):
    s = importlib.util.spec_from_file_location(n, str(p)); m = importlib.util.module_from_spec(s); sys.modules[n] = m; s.loader.exec_module(m); return m
nat = load("nat_u6", M / "MOTOR_V15_3_NATIVO_V0_9_UNICO.py")
lib, canon = nat.load_canonical(); C = sorted(canon); ok = 0
def check(name, cond):
    global ok
    print(("[PASS] " if cond else "[FAIL] ") + name); ok += bool(cond)
    if not cond: raise SystemExit(1)
rows = [[C[i], 0.84] for i in range(7)]           # 7 empatados en 0.84 -> 2 quedan fuera
prev = [{"id": "A", "P": [[C[6], 0.7]], "A": [[C[5], 0.7]], "C": []}, {"id": "B", "P": [[C[6], 0.7]], "A": [], "C": []}]
cur = {"id": "C", "P": rows, "A": [[C[5], 0.7]], "C": []}
sel, lg = nat.cuello_top_k("C", "P", rows, canon, previos=prev, corte_actual=cur)
t = [x for x, _ in sel]
check("evidencia: C6 (2 cortes previos) entra", C[6] in t)
check("evidencia: C5 (1 previo + apoyo eje A) entra", C[5] in t)
check("evidencia: el que no tiene evidencia y va al final por posición queda fuera", C[4] not in t and C[3] not in t)
check("evidencia: se pasan en orden original", t == [x for x, _ in rows if x in t])
check("evidencia: log registra criterio", lg["desempate_U6"]["decididos_por"].get("frecuencia_previa", 0) > 0)
# sin futuro: la llamada del motor pasa cuts[:i]; un corte posterior que contenga C4 no puede cambiar la selección del corte C
src = (M / "MOTOR_V15_3_NATIVO_V0_9_UNICO.py").read_text(encoding="utf-8")
check("sin futuro: el núcleo pasa solo cortes previos (cuts[:_iu6])", "_prev_u6 = list(cuts[:_iu6])" in src)
os.environ["U6_DESEMPATE_CUELLO"] = "posicion"
sel3, lg3 = nat.cuello_top_k("C", "P", rows, canon, previos=prev, corte_actual=cur)
check("legado: U6_DESEMPATE_CUELLO=posicion -> primeros 5", [x for x, _ in sel3] == [x for x, _ in rows[:5]])
os.environ.pop("U6_DESEMPATE_CUELLO")
sel4, lg4 = nat.cuello_top_k("C", "P", rows, canon)
check("sin contexto: evidencia 0 -> posición (identidad con U4)", [x for x, _ in sel4] == [x for x, _ in rows[:5]])
ce = load("ce_u6", R / "correr_estandar.py")
mc = ce.verificar_manifiesto()
check("manifiesto: Engine/patterns no bloquean en el pack U6", mc["bloquea"] is False and mc["status"] in ("MATCH", "DRIFT_WARNED"))
cp = ce.verificar_candado_plugins()
check("candado_plugins: compila todo motor/*.py", cp["status"] == "OK" and cp["verificados"] > 50)
print(f"U6: {ok} PASS")
