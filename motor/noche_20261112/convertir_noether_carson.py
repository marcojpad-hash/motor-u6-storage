#!/usr/bin/env python3
"""Convertir los dos casos ciegos sellados del checkpoint de septiembre
(Noether y Carson, 7 cortes c/u) al formato de entrada actual (CAL) y
correrlos desde cero con el motor vigente (alterno/cameo-pesos).

Origen: Drive de Marco, CHECKPOINT_MOTOR_CLONABLE_20260914.zip,
09_CIEGOS_Z90_SELLADOS/ARCHIVO_CIEGO_{NOETHER,CARSON}_Z90_20260914/
_cuts_ciego_Z90(_B)_run.json. Los hechos y tokens se copian TAL CUAL;
las fechas de corte son APROXIMADAS (punto medio del rango del hecho)
y se marcan como tales en source_notes. Sin puente Caldero placeholder
(leccion de Napoleon: el placeholder lo rechaza el Engine por diseno).
Desenlaces sellados conocidos (para comparar, NO van en la entrada):
- Noether: HIT (H1>H2); post-Z: expulsion 1933, exilio, muere 1935 tras cirugia.
- Carson: HIT (H1>H2); post-Z: Silent Spring 1962, cancer, muere 1964.
"""
import json
from pathlib import Path

BASE = Path("/home/hatch/workspace/u6-alterno")
CHECK = BASE / "biblioteca/checkpoint/CHECKPOINT_MOTOR_CLONABLE_20260914/09_CIEGOS_Z90_SELLADOS"
DEST = BASE / "motor-cameo/casos/precedentes"
PATTERNS = json.load(open(BASE / "motor-cameo/motor/motor/patterns_final_v14.json"))
# patterns_final_v14.json: lista de dicts con 'id'/'familia' o dict por nombre.
if isinstance(PATTERNS, list):
    CAT = {p.get("id") or p.get("familia") or p.get("name") for p in PATTERNS}
elif isinstance(PATTERNS, dict):
    CAT = set(PATTERNS.keys())
else:
    CAT = set()
print("familias en catalogo:", len(CAT))

CASOS = {
    "NOETHER": {
        "case_id": "NOETHER_CIEGO_Z90_20260914",
        "question": "¿Qué configuración dinámica se perfila en Emmy Noether a partir de una selección de hitos biográficos, usando solo evidencia hasta Z90 (~1932)?",
        "person": "Emmy Noether",
        "tipo_sujeto": "cientifico",
        "freeze": "1932-06-01",
        "z_work_kind": "CASE_CUTOFF",
        "z_work_date": "C7_1932",
        "source_notes": "CHECKPOINT_MOTOR_CLONABLE_20260914.zip (Drive de Marco), 09_CIEGOS_Z90_SELLADOS/ARCHIVO_CIEGO_NOETHER_Z90_20260914/_cuts_ciego_Z90_run.json; hechos y tokens copiados tal cual; fechas de corte APROXIMADAS (punto medio del rango del hecho). Desenlace sellado conocido: HIT (H1>H2); post-Z: expulsion 1933, exilio a EE.UU., muere 1935 tras cirugia.",
        "fechas": ["1891-01-01", "1903-01-01", "1911-01-01", "1917-01-01",
                   "1923-01-01", "1930-01-01", "1932-06-01"],
        "archivo": CHECK / "ARCHIVO_CIEGO_NOETHER_Z90_20260914/_cuts_ciego_Z90_run.json",
    },
    "CARSON": {
        "case_id": "CARSON_CIEGO_Z90_20260914",
        "question": "¿Qué configuración dinámica se perfila en Rachel Carson a partir de una selección de hitos biográficos, usando solo evidencia hasta Z90 (~1962)?",
        "person": "Rachel Carson",
        "tipo_sujeto": "cientifico",
        "freeze": "1962-09-01",
        "z_work_kind": "CASE_CUTOFF",
        "z_work_date": "C7_1962",
        "source_notes": "CHECKPOINT_MOTOR_CLONABLE_20260914.zip (Drive de Marco), 09_CIEGOS_Z90_SELLADOS/ARCHIVO_CIEGO_CARSON_Z90_20260914/_cuts_ciego_Z90_B_run.json; hechos y tokens copiados tal cual; fechas de corte APROXIMADAS (estimadas del hecho, sin fecha explicita en el original). Desenlace sellado conocido: HIT (H1>H2); post-Z: Silent Spring 1962, cancer de mama, muere 1964.",
        "fechas": ["1915-01-01", "1929-01-01", "1936-01-01", "1941-01-01",
                   "1951-01-01", "1958-01-01", "1962-09-01"],
        "archivo": CHECK / "ARCHIVO_CIEGO_CARSON_Z90_20260914/_cuts_ciego_Z90_B_run.json",
    },
}

for nombre, meta in CASOS.items():
    crudo = json.load(open(meta["archivo"]))
    desconocidos = set()
    cortes = []
    for c, fecha in zip(crudo, meta["fechas"]):
        for lado in ("P", "A", "C"):
            for tok, _w in c.get(lado) or []:
                if tok not in CAT:
                    desconocidos.add(tok)
        anio = fecha[:4]
        cid = f"{c['id']}_{anio}"
        cortes.append({
            "id": cid, "corte": cid, "cut_id": cid,
            "date": fecha, "fecha_corte": fecha,
            "hecho": c.get("hecho", ""),
            "P": [list(x) for x in (c.get("P") or [])],
            "A": [list(x) for x in (c.get("A") or [])],
            "C": [list(x) for x in (c.get("C") or [])],
        })
    entrada = {
        "case_id": meta["case_id"],
        "question": meta["question"],
        "person": meta["person"],
        "tipo_sujeto": meta["tipo_sujeto"],
        "freeze": meta["freeze"],
        "random_seed": 20261112,
        "z_work_kind": meta["z_work_kind"],
        "z_work_date": meta["z_work_date"],
        "cuts": cortes,
        "source_notes": meta["source_notes"],
    }
    outdir = DEST / meta["case_id"]
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "entrada.json").write_text(
        json.dumps(entrada, ensure_ascii=False, indent=2), encoding="utf-8")
    print(nombre, "->", outdir / "entrada.json", "| cortes:", len(cortes),
          "| tokens desconocidos:", sorted(desconocidos) or "ninguno")
