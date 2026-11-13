# Napoleón sin puente — re-corrida y verificación (2026-11-13)

Orden de Marco (2026-11-13 ~13:41 CST): correr Napoleón de nuevo sin el puente
placeholder, pero NO eliminarlo.

## Qué se hizo

- Se crearon variantes de entrada SIN el campo `caldero_search_bridge`:
  - `NAPOLEON_CIEGO_C9_entrada_sin_puente.json` (case_id NAPOLEON_CIEGO_C9, 9 cortes)
  - `NAPOLEON_10CORTES_entrada_sin_puente.json` (case_id NAPOLEON_FRESH_Z90_U6_20261111, 10 cortes)
- Las entradas ORIGINALES con el puente (`status NOT_EXECUTED`, `origin none`)
  quedan INTACTAS en local (`casos/precedentes/NAPOLEON_CIEGO_C9/entrada.json`
  y `casos/precedentes/NAPOLEON_10_CORTES/entrada.json`). No se borró el puente.
- Se re-corrieron ambas con el corredor estándar (motor-cameo, StinkBox real):
  - `NAPOLEON_CIEGO_C9_SIN_PUENTE` — 84.2 s
  - `NAPOLEON_10CORTES_SIN_PUENTE` — 88.4 s

## Verificación (por ejecución, no por lectura)

Antes (con puente), la etapa del Caldero fallaba en ambas:
`features/caldero_busqueda_arquetipos` = `OPTIONAL_STAGE_FAILED`,
error `RuntimeError:SEARCH_BRIDGE_INVALID_PROVENANCE`.

Después (sin puente), la etapa CORRE en ambas:
- error: ninguno
- `tokens_neighbors`: 67 en cada corrida (búsqueda libre; fuentes Wikipedia,
  p. ej. `https://es.wikipedia.org/wiki/Napole%C3%B3n_Bonaparte`)
- La persistencia ya no queda en `SEARCH_NOT_EXECUTED` por el puente.

## Resultados

- Ciega: H1 `arquetipo_el_gobernante` / H2 `30_ambicion`, grado AJUSTADA,
  Monte Carlo 13,830 simulaciones (27/27 convergidas).
- Completa: H1 `arquetipo_el_gobernante` / H2 `30_ambicion`, grado FRAGIL
  (margen 0.914 < 1.0, H1 con componentes de H2),
  Monte Carlo 15,585 simulaciones (30/30 convergidas).
- Calibración en ambas: `PARCIAL_CON_DESENLACES_SIN_REGLA_PRE_REGISTRADA`.

Nota: el recibo marca `INCOMPLETE_OUTPUT_DATA` por el path ausente
`$.efectividad_corte_retenido.previo_error`, pre-existente en corridas
estándar y no relacionado con el puente. El RESULT se escribió completo.

## Archivos

- `NAPOLEON_CIEGO_C9_entrada_sin_puente.json` (variante sin puente, ciega)
- `NAPOLEON_10CORTES_entrada_sin_puente.json` (variante sin puente, completa)
- `RESULT_NAPOLEON_CIEGO_C9_SIN_PUENTE.json.gz` + recibo `.gz`
- `RESULT_NAPOLEON_10CORTES_SIN_PUENTE.json.gz` + recibo `.gz`
