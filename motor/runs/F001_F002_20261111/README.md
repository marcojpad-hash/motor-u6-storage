# Entrega de corridas F001 y F002 — 2026-11-11

15 corridas del motor U6 (lotes de calibración F001: 5 casos, F002: 10 casos), ejecutadas el 2026-11-11 en la copia alterna con `motor/correr_estandar.py` (Engine `665c39a2…`, patrones `d827dcc3…`). Recibo COMPLETED en los 15. El motor sigue NO_CALIBRADO.

## Contenido por caso (`<CASO>_...`)

- `<CASO>_INTERPRETABLE.json` — resultado interpretable completo: `salida_interpretable` íntegra (H1/H2 con desglose, mezcla, grado, conjunto abierto con trazabilidad geométrica, apuesta), `monte_carlo`, `predictive_validation` y la entrada. Sin recortes.
- `<CASO>_RECIBO_EJECUCION.json` — recibo de ejecución (status, hashes, etapas, resolución terminal).
- `<CASO>_entrada.json` — input en prosa (pregunta, cortes con fecha/hecho) y tokens P/A/C, para repetir la corrida.

## Archivos generales

- `TABLA_VALORES_COMPLETA.md` — todos los valores por caso: H1/H2 (desglose por grupo, predictibilidad, peso), trazabilidad geométrica de cada hipótesis del conjunto abierto (régimen, señal multiescala, micro, meso, macro, aceleración, divergencia), grado, mezcla, apuesta, Monte Carlo, validación y el input en prosa.
- `MANIFIESTO.json` — SHA-256 de cada RESULT completo y de cada entrada, con estado y segundos.
- `REVISION.md` — revisión de los 15: hallazgos sistemáticos y por caso.

## Nota sobre el protocolo (conflicto explícito)

`casos/REGLAS.md` regla 6 y `CONTRATO_CARPETAS.md` dicen que nunca se sube la corrida completa al repo (solo un resumen en `casos/resultados/resultados.jsonl`), y `casos/fabrica/README.md` dice que las corridas completas quedan fuera del repo. Esta entrega es una excepción por orden directa de Marco (2026-11-11): las corridas se entregan en el repo para que otros modelos las puedan revisar. Si se adopta como regla, hay que actualizar esos tres archivos.

## Nota sobre el tamaño

Los RESULT completos suman ~90 MB (3.3–7.1 MB c/u) y el snapshot de push-files admite 16 MiB en total, así que no se suben los RESULT crudos. Se sube el resultado interpretable completo (que es lo revisable) + recibo + entrada, y el SHA-256 de cada RESULT completo queda en `MANIFIESTO.json`. Los RESULT crudos están en la copia alterna (`motor/RESULT_CAL_F001_*.json`, `RESULT_CAL_F002_*.json`).
