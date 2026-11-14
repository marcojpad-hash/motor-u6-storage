# Corrida completa Napoleón con 27 familias cableadas — 2026-11-13

## Corrida
`NAPOLEON_10CORTES_FINAL27` — entrada `casos/precedentes/NAPOLEON_10_CORTES/entrada_sin_puente.json`
(10 cortes), 65.174 s, RESULT `motor/RESULT_NAPOLEON_10CORTES_FINAL27.json` (9.7 MB).
Recibo: `RESULT_NAPOLEON_10CORTES_FINAL27_RECIBO_EJECUCION.json`.
Returncode 4 / INCOMPLETE_OUTPUT_DATA por el path pre-existente
`$.efectividad_corte_retenido.previo_error` (no es fallo de esta corrida; el RESULT
está completo).

## Resultado
- **H1: arquetipo_el_gobernante (53.57) / H2: 30_ambición (55.39), grado FRAGIL,
  margen 0.914454** — IDÉNTICOS a la corrida base sin puente. Las 27 familias
  laterales NO mueven H1/H2 (correcto: can_decide_H False, no deciden H).
- Mezcla: H1_CON_COMPONENTES_DE_H2 ("gobernante con componentes de ambición").
  6 hipótesis abiertas, convergencia MESeta_O_ESTABILIZACION.
  Apuesta: APUESTA_MULTIESCENARIO_SELLABLE.
- **Monte Carlo: EXECUTED, 15,585 simulaciones, 30/30 convergidas.**
- **Laterales en el RESULT: 27 familias** en `laterales_unico.pre.familias_tokens_EXPERIMENTAL`;
  las 11 cableadas (10 taxonomía + Black Mirror) presentes 11/11; Black Mirror 18 tokens.
  Voto puente: ACTIVA_MUDA en este caso (sin solape de palabras con Napoleón).
- Caldero: corre (schema caldero_archetype_search_sidecar_v1).
- par_superpuesto_entrada: declarado False (esta corrida usó la entrada sin puente,
  sin el campo par; el lateral quedó mudo, como debe ser).
- StinkBox: OK, unique_tokens_total 4445.

## Contexto
Corrida pedida por Marco 2026-11-13 ~17:57 CST para ver cómo funciona el motor ya
con las familias cableadas (taxonomía geopolítica + Black Mirror), la estabilización
vectorial y los puentes laterales. A diferencia de los dos intentos previos
(NAPOLEON_10CORTES_TAXGEO), que llegaron al timeout interno de 90 s, esta corrida
completó en 65.174 s.
