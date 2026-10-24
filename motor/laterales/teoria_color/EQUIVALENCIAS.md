# Equivalencias teoría del color ↔ modelo (lateral, no decide H)

Croma = distancia del tono al gris (1/3,1/3,1/3) en el plano cromático, escala 0 (gris) a 1 (eje puro). Matiz = ángulo: 0°=interno(R), 120°=externo(G), 240°=situación(B).

| Regla clásica | Concepto del modelo | Estado | Fórmula | Resultado Mozart |
|---|---|---|---|---|
| Tríada primaria (R,G,B / C,M,Y) | Tríada P/A/C = interno/externo/situación | APLICABLE | Ejes del lateral | U10: 3 ejes con datos. U6: solo P (A,C hueco) |
| Mezcla aditiva RGB | Suma de evidencia por eje (FULL_244) normalizada | APLICABLE | tono_e = v_e / Σv | U10 tono final {'externo': 0.288977, 'interno': 0.390851, 'situacion': 0.320171} |
| Mezcla sustractiva CMY | Restricción (un eje que "absorbe" a otro) | NO APLICABLE | — | Los FULL_244 son activaciones ≥0 que se suman; no hay filtro que reste. Forzarlo sería inventar |
| Círculo cromático / matiz | Ángulo del tono en el plano P/A/C | APLICABLE | matiz=atan2(Σv_i sin120i, Σv_i cos120i) | U10 matiz final 342.613774°; U6 0.0° (trivial: 1 eje) |
| Saturación / croma | Pureza de la lectura (qué tan lejos del gris) | APLICABLE | croma=|proyección|; saturación=max−min | U10 croma 0.090408 (muy bajo); U6 1.0 por hueco, no por dato |
| Gris / neutralización | Mezcla plana: hipótesis que juntas pierden pureza | APLICABLE | neutralización=1−croma_mezcla/Σ(w·croma_H) | U10 0.191937; U6 0.0 |
| Complementarios | Hipótesis que se anulan en la mezcla (Δmatiz≈180°) | APLICABLE (resultado vacío) | 150°≤|Δmatiz|≤210°, croma>0.02 | U10 pares: ninguno; U6 no evaluable |
| Análogos | Hipótesis vecinas en matiz (mismo tono, distinto nombre cercano) | APLICABLE | Δmatiz≤30° | U10 7 pares análogos de 15; U6 todos (trivial) |
| Tríada armónica (3 matices a 120°) | Hipótesis que cubren los tres ejes repartidos | PARCIAL | buscar H con matiz ≈0/120/240 | U10: ninguna H cerca de 120° (externo); 4 H en ~0–14° (interno) y 2 en 267–292° (entre situación e interno): diada, no tríada |
| Valor / luminosidad | Intensidad (magnitud RMS de la activación) | APLICABLE | valor=√(Σv²/n) | U10 0.336047; U6 0.999999 (solo P) |
| Temperatura cálido/frío | interno (cálido, R) vs situación (frío, B) | PARCIAL | temp=tono_interno−tono_situación | U10 0.07068 (levemente cálido = sesgo interno). Convención arbitraria; solo ilustrativa |
| Pigmento idéntico (metamerismo) | Dos nombres con el mismo vector en todos los cortes | APLICABLE | igualdad exacta de vectores P/A/C C1..C10 | U10: ninguno exacto; casi: arquetipo_el_creador/schwartz_10/utopia_liberal tienen externo≈situación (A≈C). U6: ninguno exacto |
