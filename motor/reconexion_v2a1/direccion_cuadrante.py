#!/usr/bin/env python3
"""Reconexión v2.A.1 (reserva), parte 2: cuadrante del monomito -> dirección.

El cuadrante solo se contaba (cuántos cortes tienen cuadrante activo) y nunca se
usaba para dirección. Aquí se reconecta: la dirección es el próximo cuadrante
en el ciclo Q1->Q2->Q3->Q4, y cada candidata del top 5 se mide contra él con
datos (no con mapeo subjetivo): su P media en los cortes del cuadrante siguiente
vs su P media en los cortes del cuadrante actual. Si crece hacia el cuadrante
siguiente, está alineada con la dirección (hacia dónde se va a desarrollar el
héroe). Si no, no. Sin tocar Engine ni catálogo.
"""
import json

R_PATH = 'motor/RESULT_NAPOLEON_Z90_10CORTES.json'
r = json.load(open(R_PATH))
mono = r['features']['plugin_circulo_monomito']['posicion_monomito_por_corte']
cp = r['motor']['annex']['traza_P']['crudo_P']

ORDEN = ['Q1_Separacion_1_3', 'Q2_Descenso_4_6', 'Q3_Ordeal_7_9', 'Q4_Retorno_10_12']

# cuadrante por corte (C1..C10)
q_por_corte = []
for f in mono:
    q = (f.get('cuadrante_activo') or [None])[0]
    q_por_corte.append(q)
print("Cuadrante por corte:", " -> ".join(q or "-" for q in q_por_corte))

# secuencia sin huecos
seq = [q for q in q_por_corte if q]
actual = seq[-1]
siguiente = ORDEN[(ORDEN.index(actual) + 1) % 4] if actual in ORDEN else None
# ¿progresa o oscila? contar transiciones
trans = sum(1 for a, b in zip(seq, seq[1:]) if a != b)
retro = sum(1 for a, b in zip(seq, seq[1:]) if ORDEN.index(b) < ORDEN.index(a)) if all(x in ORDEN for x in seq) else 0
print(f"Cuadrante actual (C10): {actual}")
print(f"Cuadrante siguiente (dirección): {siguiente}")
print(f"Transiciones: {trans}, retrocesos (vuelve atrás): {retro} -> {'OSCILA, no progresa a Q4' if retro else 'progresa'}")

# P media por candidata en cortes del cuadrante actual vs siguiente
idx_actual = [i for i, q in enumerate(q_por_corte) if q == actual]
idx_sig = [i for i, q in enumerate(q_por_corte) if q == siguiente]
print(f"\nCortes en {actual}: {[i+1 for i in idx_actual]} | Cortes en {siguiente}: {[i+1 for i in idx_sig]}")

ph = r.get('predictibilidad_021', {}).get('predictibilidad', {}).get('por_hipotesis', {})
top5 = sorted(ph.items(), key=lambda kv: kv[1].get('rank_fusion', 0), reverse=True)[:5]
dh = r.get('decimo_hombre_esteroides', {}).get('contador_supervivencia', {})

print("\n=== DIRECCIÓN POR CUADRANTE (top 5) ===")
out = {"caso": "NAPOLEON_Z90_10CORTES", "cuadrante_actual": actual,
       "cuadrante_siguiente": siguiente, "oscila": retro > 0, "filas": []}
for fam, vals in top5:
    ps = cp.get(fam, [])
    if not ps or not idx_actual or not idx_sig:
        print(f"{fam}: sin datos para medir dirección")
        continue
    m_act = sum(ps[i] for i in idx_actual) / len(idx_actual)
    m_sig = sum(ps[i] for i in idx_sig) / len(idx_sig)
    delta = m_sig - m_act
    alineada = "ALINEADA_CON_DIRECCION" if delta > 0 else "NO_ALINEADA"
    s = dh.get(fam, 0)
    print(f"{fam} (rf {vals.get('rank_fusion'):.2f}, DH {s}/53): "
          f"P en {actual} {m_act:.3f} vs P en {siguiente} {m_sig:.3f} (delta {delta:+.3f}) -> {alineada}")
    out["filas"].append({"familia": fam, "rank_fusion": vals.get('rank_fusion'),
                         "supervivencia_dh": s, "p_cuadrante_actual": round(m_act, 4),
                         "p_cuadrante_siguiente": round(m_sig, 4), "delta": round(delta, 4),
                         "alineacion_direccion": alineada})
json.dump(out, open('DIRECCION_CUADRANTE_NAPOLEON_10CORTES.json', 'w'), indent=1, ensure_ascii=False)
print("\nguardado: DIRECCION_CUADRANTE_NAPOLEON_10CORTES.json")
print("Lectura: Napoleón oscila Q2<->Q3 (Descenso<->Ordeal), no progresa a Q4 (Retorno).")
print("La dirección es Q3; las candidatas que crecen hacia Q3 están alineadas con ella.")
