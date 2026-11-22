# Issue #64 — guardián Z90 integrado en runner estándar

Fecha: 2026-11-22  
Rama: alterno/cameo-pesos

## Cambio ejecutado

- motor/correr_estandar.py invoca _guardian_z90(case) después de normalizar/filtros y antes de construir/ejecutar el motor.
- Un rechazo escribe RESULT y _RECIBO_EJECUCION.json con estado BLOQUEADO_GUARDIAN_Z90 y código de salida 8; el motor no se invoca.
- El veredicto Z90 se conserva en el resultado y el recibo de corridas admitidas.
- efectividad_corte_retenido conserva previo_error, visto_error, estados y aislamiento en ambas ramas, éxito y fallo.

## Prueba corregida

Se creó motor/tests/test_guardian_z90_correr_estandar.py con siete pruebas. El fixture histórico ahora declara nacimiento y muerte exactos, calcula Z90 con floor(0.9 × días), establece z_trabajo=z90_date, usa ventanas acumulativas desde nacimiento, cierres crecientes y termina exactamente en Z90. El fixture anterior del PR no incluía nacimiento/muerte y no podía pasar la validación de biografía histórica.

## CI

El workflow .github/workflows/test-motor-contracts.yml incluye el archivo de prueba en paths y en el comando pytest; el workflow ya escucha pushes a alterno/cameo-pesos.

- Run: [#45002771468](https://github.com/marcojpad-hash/motor-u6-storage/actions/runs/45002771468)
- Job: runner-contract
- Resultado: **SUCCESS — 60 passed in 0.86s**
- Las siete pruebas nuevas se incluyen en ese run.

## Commits y blobs

- Runner commit: bb6a31d9a77d43ac106f77927f9347b8bbadee7d; blob releído: 12e1933213439880ec0c775225458e55aa135fdf.
- Tests commit: 1d878000c791eb108b4175c8471c5b3b3114caf6; blob releído: 098d331ecacd30333e4e0c1290dfb76351990a83.
- Workflow commit: 658f3f27a61f70e16d95de916d23e3af93b5aae2; blob releído: d33d2162607b78c2de5cb9a8b336ec6de320eafc.

## Límites

Esto verifica el guardián y el bloqueo del runner en pruebas; no es una corrida del motor con caso real, no genera n independiente y no valida custodia. F007 sigue sin cumplir fuentes primarias y separación de funciones. PR #8 sigue OPEN / NOT MERGED / mergeable=false; no se fusionó. No se tocaron main, Engine V5, patterns 244, custodias ni candados.
