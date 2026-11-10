# Entrega — Mozart A/B V15.3 — 2026-11-10

## Estado
Corrida A/B ejecutada con éxito en GitHub Actions. Los dos RAW, trazas, recibos, manifiestos, comparación diferencial y hashes quedaron guardados en esta rama. No se modificó `main`, el motor canónico ni el catálogo de 244 patrones.

- Rama: `work/mozart-ab-20261110`
- Workflow: [ejecución 42926720289](https://github.com/marcojpad-hash/motor-u6-storage/actions/runs/42926720289)
- Entrada: 10 cortes recuperados de `MOZART_FRESH_WEB_BIO_V04_20260930_RESULT.json`; el input fuente independiente no apareció en Library. La procedencia queda marcada como recuperada, no como original.
- Z90: 1788-05-04.
- Caldero A: runner genérico + búsqueda estática explícita con siete fuentes históricas; se excluyó src8 por contener un evento del 7 de mayo de 1788, posterior a Z90.
- Caldero B: conjunto Caldero desactivado en la copia aislada del run: búsqueda, runner genérico, memoria de vecinos, Monomito/Q1-Q4, zoom-out y Polti-Caldero. Los demás plugins se conservan.
- Monte Carlo: ON en ambas.

## Resultado
- H1 A/B: `schwartz_10_autodireccion` / `schwartz_10_autodireccion`.
- H2 A/B: `utopia_mentalidad_liberal` / `utopia_mentalidad_liberal`.
- H1 y H2 no cambian.
- Top-1 rank_fusion: A 28.316281; B 27.316281.
- Top-2 rank_fusion: A 24.135121; B 23.889397.
- Top-3 rank_fusion: A 22.563198; B 21.346090.
- Top-4 rank_fusion: A 21.172956; B 19.923495.

## Incidencia
A registró un error en `geometria_multicapa_integrada_working_v1`: eje A vacío, matriz (3,0), cuando el plugin esperaba al menos una dimensión. Se conserva el error en la traza; no se rellenaron datos. B no registró errores. Los estados de componentes se conservan íntegros en cada traza de plugins.

## Archivos de entrada y ejecución
- [Input Mozart de diez cortes](input_mozart_z90.json)
- [Input Caldero II y siete fuentes](caldero_II_input.json)
- [Script reproducible A/B](run_mozart_ab.py)
- [Workflow GitHub Actions](../../.github/workflows/mozart-ab-20261110.yml)

## Corrida A — con Caldero
- [RAW completo](resultados/A_CON_CALDERO/RESULT_RAW.json)
- [RAW de Caldero II runner genérico](resultados/A_CON_CALDERO/CALDERO_II_RAW.json)
- [Traza del núcleo](resultados/A_CON_CALDERO/TRAZA_NUCLEO.json)
- [Traza de plugins y features](resultados/A_CON_CALDERO/TRAZA_PLUGINS.json)
- [Manifiesto](resultados/A_CON_CALDERO/run_manifest.json)
- [Recibo de ejecución](resultados/A_CON_CALDERO/RESULT_RAW_RECIBO_EJECUCION.json)
- [Ledger CEB](resultados/A_CON_CALDERO/RESULT_RAW_CEB_LEDGER_1.jsonl)
- [Manifiesto del ledger CEB](resultados/A_CON_CALDERO/RESULT_RAW_CEB_LEDGER_MANIFIESTO.json)
- [Input efectivo](resultados/A_CON_CALDERO/input_efectivo.json)
- [stdout](resultados/A_CON_CALDERO/stdout.log) · [stderr](resultados/A_CON_CALDERO/stderr.log)
- [stdout Caldero runner](resultados/A_CON_CALDERO/caldero_runner.stdout.log) · [stderr Caldero runner](resultados/A_CON_CALDERO/caldero_runner.stderr.log)

## Corrida B — sin Caldero
- [RAW completo](resultados/B_SIN_CALDERO/RESULT_RAW.json)
- [Traza del núcleo](resultados/B_SIN_CALDERO/TRAZA_NUCLEO.json)
- [Traza de plugins y features](resultados/B_SIN_CALDERO/TRAZA_PLUGINS.json)
- [Manifiesto](resultados/B_SIN_CALDERO/run_manifest.json)
- [Recibo de ejecución](resultados/B_SIN_CALDERO/RESULT_RAW_RECIBO_EJECUCION.json)
- [Estado Caldero II OFF](resultados/B_SIN_CALDERO/CALDERO_II_ESTADO.json)
- [Input efectivo](resultados/B_SIN_CALDERO/input_efectivo.json)
- [stdout](resultados/B_SIN_CALDERO/stdout.log) · [stderr](resultados/B_SIN_CALDERO/stderr.log)

## Comparación y verificación
- [Comparación diferencial JSON](resultados/COMPARACION_DIFERENCIAL.json)
- [Comparación diferencial legible](resultados/COMPARACION_DIFERENCIAL.md)
- [SHA-256 de los artefactos](resultados/SHA256SUMS.txt)
- [Paquete ZIP de evidencia del workflow](https://github.com/marcojpad-hash/motor-u6-storage/actions/runs/42926720289/artifacts/13813404039)
