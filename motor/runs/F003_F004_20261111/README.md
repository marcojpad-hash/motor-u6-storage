# Entrega de corridas F003 y F004 — 2026-11-11

20 corridas del motor U6 (lotes de calibración F003: 10 casos, F004: 10 casos), ejecutadas el 2026-11-11 en la copia alterna con `motor/correr_estandar.py` (Engine `665c39a2…`, patrones `d827dcc3…`). Recibo COMPLETED en los 20. El motor sigue NO_CALIBRADO.

## Contenido por caso (`<CASO>_...`)

- `<CASO>_INTERPRETABLE.json` — resultado interpretable completo: `salida_interpretable` íntegra (H1/H2 con desglose, mezcla, grado, conjunto abierto con trazabilidad geométrica, apuesta), `monte_carlo`, `predictive_validation` y la entrada. Sin recortes.
- `<CASO>_RECIBO_EJECUCION.json` — recibo de ejecución (status, hashes, etapas, resolución terminal).
- `<CASO>_entrada.json` — input en prosa (pregunta, cortes con fecha/hecho) y tokens P/A/C, para repetir la corrida.

## Archivos generales

- `TABLA_VALORES_COMPLETA.md` — todos los valores por caso: H1/H2 (desglose por grupo, predictibilidad, peso), trazabilidad geométrica de cada hipótesis del conjunto abierto (régimen, señal multiescala, micro, meso, macro, aceleración, divergencia), grado, mezcla, apuesta, Monte Carlo, validación y el input en prosa.
- `MANIFIESTO.json` — SHA-256 de cada RESULT completo y de cada entrada, con estado y segundos.
- `REVISION.md` — revisión de los 20: hallazgos sistemáticos y por caso.

## Nota sobre el protocolo — reconciliación documental 2026-11-13

La forma de almacenamiento adoptada el 2026-11-11 ya está reflejada en `casos/REGLAS.md`, `CONTRATO_CARPETAS.md`, `casos/fabrica/README.md` y `CONTRATO_GUARDAR_CORRIDAS.md`: resumen de una línea en `casos/resultados/resultados.jsonl` y corrida completa interpretable, recibo y entrada en `motor/runs/<LOTE>_<FECHA>/`. Esta entrega no es una excepción.

**Advertencia de evidencia:** `LECTURA.json` conserva descripciones y SHA-256 de las versiones anteriores de los tres documentos subordinados. Tras su actualización, esa evidencia quedó obsoleta y debe regenerarse/revalidarse mediante el procedimiento autorizado antes de ejecutar `scripts/candado_entrega.py`. No se modificó `LECTURA.json` ni se ejecutó el candado en esta revisión documental. La revisión de los recibos y la corrección de su interpretación constan en `REVISION.md`.

## Nota sobre el tamaño

Los RESULT completos suman ~160 MB (3.3–8 MB c/u) y el snapshot de push-files admite 16 MiB en total, así que no se suben los RESULT crudos. Se sube el resultado interpretable completo (que es lo revisable) + recibo + entrada, y el SHA-256 de cada RESULT completo queda en `MANIFIESTO.json`. Los RESULT crudos están en la copia alterna (`motor/RESULT_CAL_F003_*.json`, `RESULT_CAL_F004_*.json`).
