# Par superpuesto en el input — Napoleón completa (2026-11-13)

Orden de Marco (2026-11-13 ~14:44 CST): si el empate se traduce en el input
y se unifica, adquiere mayor sentido que solo patrones simples que compiten.
Respuesta: sí. Se armó en Napoleón.

## Qué se hizo (dos-pasadas)

1. Primera pasada: `NAPOLEON_10CORTES_SIN_PUENTE` (margen 0.914454 < 1.0,
   empate gobernante+ambición, FRAGIL).
2. Pre-paso (`motor/dos_pasadas_par_superpuesto_v1.py`): detectó el empate y
   escribió la variante `NAPOLEON_10CORTES_entrada_par_superpuesto.json`
   con el campo `par_superpuesto_entrada` (par + origen + margen).
   La entrada original NO se tocó.
3. Segunda pasada: `NAPOLEON_10CORTES_PAR_SUPER` (84.6 s). El lateral
   `lateral_par_superpuesto_entrada_v1.py` (sensor, `can_decide_H = False`)
   lee el par declarado y lo reporta en
   `RESULT.laterales_unico.post.par_superpuesto_entrada`.

## Verificación (por ejecución, no por lectura)

- Lateral ACTIVA: par `arquetipo_el_gobernante+30_ambicion`,
  `coincide_con_H1_H2 = True`, `adyacente_top2 = True`,
  superposición 8/10 cortes, simetría 0.037, lectura "par unificado".
- Por corte, el par converge: C1 0.500/0.725, C3 0.792/0.803,
  C9 0.803/0.803, C10 0.781/0.781 (idénticos al final).
- H1/H2 IDÉNTICOS a la corrida base (sin puente): gobernante 53.57 /
  ambición 55.39, grado FRAGIL, margen 0.914454. El lateral no decide H.
- Monte Carlo 15,585 (30/30 convergidas), Caldero 67 vecinos sin error.
- Recibo `INCOMPLETE_OUTPUT_DATA` por el path `previo_error` pre-existente.

## Archivos

- `NAPOLEON_10CORTES_entrada_par_superpuesto.json` (variante con el par)
- `RESULT_NAPOLEON_10CORTES_PAR_SUPER.json.gz` + recibo `.gz`
- `motor/motor/lateral_par_superpuesto_entrada_v1.py` (sensor)
- `motor/PAR_SUPERPUESTO_ENTRADA_V1.md` (contrato)
- `motor/dos_pasadas_par_superpuesto_v1.py` (pre-paso)
- Cableado: hunk en `motor/motor/laterales_unico_v1.py`, función
  `post_predictor`, pieza `par_superpuesto_entrada` antes de `return out`
  (después de `memento_vs_top1`). Solo el hunk, nunca el archivo completo.
