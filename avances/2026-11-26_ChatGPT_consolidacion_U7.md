# 2026-11-26 — ChatGPT — consolidación operativa U7 y control de flujo

## Qué cambió

Se consolidó una sola autoridad contractual para Motor U7 y se amplió el cableado de `control_flujo_soluciones.py` a la ruta estándar. Los contratos previos se conservaron en historial no activo, sin borrar evidencia.

## Antes → ahora (por archivo / función)

- `motor/correr_estandar.py::_plan_contorno` — antes no había adaptador común del control de flujo en el runner estándar → ahora carga `motor/motor/control_flujo_soluciones.py` y produce un plan estructurado.
- `motor/correr_estandar.py::_main_with_control_flujo` — antes una excepción no controlada podía terminar sin contorno → ahora registra PIEDRA/CONTORNO/SIGUIENTE/EVIDENCIA en JSON y conserva exit code 3.
- `motor/correr_estandar.py::main` — antes el fallo del subproceso primario retornaba solo un mensaje → ahora escribe RESULT de fallo y `_RECIBO_EJECUCION.json` con el error y el contorno.
- Errores de respuesta humana, traducción y verificación de salida ahora incluyen plan de contorno.
- `docs/CONTRATOS_OPERATIVOS_V7.md` queda como autoridad contractual única; corrige control de flujo y describe confianza U7 post-corrida B1–B6 con `calibrada=false`.
- Los contratos anteriores se archivan bajo `antecedentes_motor/historial_contratos/`; sus rutas originales son avisos, no instrucciones activas.
- README, FeedMe y sidecars apuntan al mismo contrato y al nombre operativo Motor U7.
- El workflow de contratos incorpora las pruebas del control de flujo.

## Hashes canónicos verificados (motor y catálogo)

- Engine V5: `665c39a2861e58772522e91272563260d980908b1d4ab9f7092d3413d0c36082` (protegido; no modificado).
- Catálogo 244: `d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1` (protegido; no modificado).
- Base de trabajo: `dbb60e7248359aedc5ba4a827dbacf292b92cd48`.

## Pruebas: 92 passed, 0 skipped, 0 failed

**CI verificado:** run [#45860500437](https://github.com/marcojpad-hash/motor-u6-storage/actions/runs/45860500437), job `runner-contract` SUCCESS, 92 pruebas aprobadas en 41.81 s. Incluye las tres pruebas del adaptador del runner, el test de integración `test_cableado_plan_contorno.py`, runner JSON, Z90 y preparación entry-only. El primer run #45860284178 detectó tres fallos de carga por ruta duplicada `motor/motor/motor`; se corrigió la ruta a `motor/motor/control_flujo_soluciones.py` y la re-corrida completa pasó. No se ejecutó una corrida productiva ni se alteraron Engine V5, catálogo 244 o custodia.
