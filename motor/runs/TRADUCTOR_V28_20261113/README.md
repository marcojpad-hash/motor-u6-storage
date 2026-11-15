# Entrega de corridas — lote TRADUCTOR_V28_20261113

3 corridas del motor U6 ejecutadas el 2026-11-13 en la copia alterna con
`motor/correr_estandar.py` (Engine `665c39a2…`, patrones `d827dcc3…`). Recibo
COMPLETED en las 3. Son los 3 casos con los que se verificó por ejecución el
traductor de salida v2.8 (`motor/motor/lateral_traduccion_salida_v1.py`,
VERSION `v2.8_20261114`): LIMBO_6C, MOZART_NINO_7C y CAL_F001_02_TESLA_7C,
con 0 violaciones en los 3. El motor sigue NO_CALIBRADO.

## Contenido por caso (`<CASO>_...`)

- `<CASO>_INTERPRETABLE.json` — resultado interpretable completo: `salida_interpretable` íntegra (H1/H2 con desglose, mezcla, grado, conjunto abierto con trazabilidad geométrica, apuesta), `monte_carlo`, `predictive_validation` y la entrada. Sin recortes. El `monte_carlo` viene vacío (`{}`) porque el RESULT no trae sección Monte Carlo (su `monte_carlo` es nulo); igual que en el lote F003_F004_20261111.
- `<CASO>_RECIBO_EJECUCION.json` — recibo de ejecución (status, hashes, etapas, resolución terminal).
- `<CASO>_entrada.json` — input en prosa (pregunta, cortes con fecha/hecho) y tokens P/A/C, para repetir la corrida.

## Archivos generales

- `TABLA_VALORES_COMPLETA.md` — todos los valores por caso: H1/H2 (desglose por grupo, predictibilidad, peso), trazabilidad geométrica de cada hipótesis del conjunto abierto (régimen, señal multiescala, micro, meso, macro, aceleración, divergencia), grado, mezcla, apuesta, Monte Carlo, validación y el input en prosa.
- `MANIFIESTO.json` — SHA-256 de cada RESULT completo y de cada entrada, con estado y segundos.
- `REVISION.md` — revisión de los 3 casos: hallazgos sistemáticos y por caso.
- `LECTURA.json` — evidencia de lectura del protocolo.
- `LECTURA_LIMBO_6C_v28.json` — salida verificada del traductor v2.8 para LIMBO_6C (lectura + anexo, 0 violaciones). Las lecturas de MOZART_NINO_7C y CAL_F001_02_TESLA_7C se verificaron por ejecución con el mismo script (`motor/tests/test_traductor_v24.py`) y dieron 0 violaciones, pero sus salidas no se guardaron a archivo; la verificación consta en REVISION.md.

## Nota sobre el protocolo

La forma de almacenamiento es la adoptada el 2026-11-11 y recogida en `CONTRATO_GUARDAR_CORRIDAS.md`, `PROTOCOLO_EJECUCION_Y_LECTURA_LLM.md` (§3 recibo mínimo, §4 todo dato es un dato) y `casos/REGLAS.md` (regla 6): resumen de una línea en `casos/resultados/resultados.jsonl` y corrida completa interpretable, recibo y entrada en `motor/runs/<LOTE>_<FECHA>/`. Esta entrega no es una excepción. Los tres archivos viejos que dicen lo contrario (`casos/REGLAS.md` regla 6, `CONTRATO_CARPETAS.md`, `casos/fabrica/README.md`) siguen pendientes de actualizar; manda la forma adoptada por Marco y este contrato.

## Nota sobre el tamaño

Los RESULT completos suman ~32 MB (9.9–11.9 MB c/u) y el snapshot de push-files admite 16 MiB en total, así que no se suben los RESULT crudos. Se sube el resultado interpretable completo (que es lo revisable) + recibo + entrada, y el SHA-256 de cada RESULT completo queda en `MANIFIESTO.json` y en cada INTERPRETABLE (`result_completo_sha256`). Los RESULT crudos quedan en la copia de trabajo.
