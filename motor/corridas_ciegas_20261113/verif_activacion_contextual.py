#!/usr/bin/env python3
"""Confirmación: la activación de tokens laterales es CONCEPTUAL y depende del CONTEXTO,
no de una matriz rígida. (Marco 2026-11-13 ~16:49/17:46 CST.)

Mismo candidato (30_ambicion), mismo motor, misma función
(laterales_unico_v1.voto_familias_tokens). Solo cambia el contexto del caso:
  - Contexto B: los cortes recientes traen 'retiro_voluntario', token del 244 que
    está en los tokens propios de ambición Y en las palabras de una entrada del
    puente (separacion_fundador_gestion_madurez, familia ciclo_vida_organizacional_adizes).
    -> estado ACTIVA, voto ambición = 1.0, gobernante = 0.0
  - Contexto A: los cortes traen 'cooperacion', que NO está en los tokens propios
    de ambición. -> estado ACTIVA_MUDA, voto 0.0 / 0.0

No hay tabla fija que diga "ambición siempre activa X": la activación depende de
qué tokens trae el caso. Superposición, sin deduplicación ni doble peso.
"""
import json, sys
from pathlib import Path

BASE = Path("motor/motor")
sys.path.insert(0, str(BASE))
import laterales_unico_v1 as lu

patterns = json.loads((BASE / "patterns_final_v14.json").read_text(encoding="utf-8"))

def voto_para(cortes, candidatos):
    case = {"cuts": cortes, "case_id": "TEST_CTX"}
    motor = {"cuts": [{"P_candidatos_0a3": [{"familia": c} for c in candidatos]} for _ in cortes]}
    return lu.voto_familias_tokens(BASE, case, motor, patterns)

cands = ["30_ambicion", "arquetipo_el_gobernante"]
cortes_B = [{"id": f"C{i}", "P": [["retiro_voluntario", 0.75 + 0.02 * i]], "A": [], "C": []} for i in (1, 2, 3)]
cortes_A = [{"id": f"C{i}", "P": [["cooperacion", 0.75 + 0.02 * i]], "A": [], "C": []} for i in (1, 2, 3)]

estB, _, votoB, infoB = voto_para(cortes_B, cands)
estA, _, votoA, infoA = voto_para(cortes_A, cands)
print("CONTEXTO B (retiro_voluntario):", estB, votoB.get("por_familia"))
print("CONTEXTO A (cooperacion):      ", estA, votoA.get("por_familia"))
assert estB == "ACTIVA" and votoB["por_familia"]["30_ambicion"]["score"] == 1.0
assert estA == "ACTIVA_MUDA" and votoA["por_familia"]["30_ambicion"]["score"] == 0.0
print("CONFIRMADO: la activación depende del contexto, no de una matriz rígida.")
