# SPEC — Lateral Teoría del Color v1 (pauta para replicar)
Lateral: solo lee el RESULT. No decide H. No toca motor ni patterns.
1. Ejes: interno = P_FULL_244[H], externo = A_FULL_244[H], situación = C_FULL_244[H], de motor.cuts[] (C1..C10).
2. Hueco: si motor.cuts[k].n_tokens[dim]==0, ese eje en ese corte NO es dato (el 0.5 es valor por defecto) → se omite, no se rellena.
3. Color de H por corte: tono_e = v_e / suma(v de ejes con dato). Intensidad (valor) = raíz(media de v²). Pureza = tono máximo. Saturación = tono máx − tono mín. Entropía = −Σ t·ln t / ln 3.
4. Color de H global: promedio por eje de v sobre cortes con dato, luego paso 3.
5. Pesos: w_H = rank_fusion_H / Σ rank_fusion (predictor.candidates).
6. Mezcla (corte o final) = Σ w_H · tono_H por eje (renormalizada vía paso 3).
7. Eje que mueve C_k→C_k+1 = eje con mayor |Δtono| de la mezcla.
8. Pigmento idéntico = mismos vectores P/A/C en todos los cortes.
9. Hex ilustrativo: R=interno, G=externo, B=situación, escalado a máx=255.
10. Rueda: matiz = atan2(Σ t_i·sin(120°i), Σ t_i·cos(120°i)) (0°=interno,120°=externo,240°=situación); croma = longitud de esa proyección (0 gris). Neutralización = 1 − croma_mezcla / Σ w_H·croma_H. Complementarios: 150°≤|Δmatiz|≤210°.
Todo redondeado a 6 decimales, determinista, ningún número >1.
