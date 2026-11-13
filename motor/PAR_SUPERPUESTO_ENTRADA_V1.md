# PAR_SUPERPUESTO_ENTRADA_V1 — El empate se unifica en el input (dos-pasadas)

## Idea (Marco, 2026-11-13)

Cuando dos familias quedan empatadas (margen < GATE_SEPARATION 1.0), el empate
se traduce DENTRO del mismo input y se unifica: el motor ya no lee dos
patrones simples que compiten, sino una sola cosa con dos caras. Eso da mejor
entendimiento que el ranking de competencia.

Es la superposición (SUPERPOSICION_H1_H2_V1) movida del final al principio:
el lateral de superposición la lee a la salida; este par la declara a la entrada.

## Mecánica (dos-pasadas)

1. Primera pasada: se corre el caso normal. El RESULT trae H1/H2 y el margen.
2. Pre-paso: si el margen < 1.0, se escribe una variante de entrada con el campo
   `par_superpuesto_entrada`:
   ```json
   "par_superpuesto_entrada": {
     "par": ["arquetipo_el_gobernante", "30_ambicion"],
     "origen": "empate_detectado_en_corrida_previa",
     "corrida_origen": "NAPOLEON_10CORTES_SIN_PUENTE",
     "margen": 0.914454,
     "umbral": 1.0
   }
   ```
   La entrada original NO se toca. Solo se añade el campo a la variante.
3. Segunda pasada: se corre la variante. El lateral
   `lateral_par_superpuesto_entrada_v1.py` (sensor, `can_decide_H = False`)
   lee el par declarado y verifica que coincide con H1/H2, y mide la
   superposición por corte (ambas familias >= 0.7), la simetría y si el par
   quedó adyacente en los dos primeros puestos del ranking.

## Reglas

- El lateral es SOLO observación: no toca H1/H2, no toca el ranking, no toca
  Engine ni el catálogo 244.
- Si el input no trae el campo, el lateral reporta `ACTIVA_MUDA` y no hace nada.
- El par se declara solo cuando hay empate verificado en una corrida previa
  (margen < 1.0). No se inventa el par.
- La primera pasada y la segunda usan el mismo StinkBox y el mismo motor;
  el delta entre ambas es solo el par declarado.
