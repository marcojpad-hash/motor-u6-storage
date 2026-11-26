# 2026-11-26 — ChatGPT — consolidación operativa U7 y control de flujo

## Qué cambió

Se consolidó una sola autoridad contractual para Motor U7 y se amplió el cableado de `control_flujo_soluciones.py` a la ruta estándar. Los contratos previos se conservaron en historial no activo, sin borrar evidencia.

## Antes → ahora (por archivo / función)

- `motor/correr_estandar.py::_plan_contorno` — antes no había adaptador común del control de flujo en el runner estándar → ahora carga `motor/motor/control_flujo_soluciones.py` y produce un plan estructurado.
- `motor/correr_estandar.py::_main_with_control_flujo` — antes una excepción no controlada podía terminar sin contorno → ahora registra PIEDRA/CONTORNO/SIGUIENTE/EVIDENCIA en JSON y conserva exit code 3.
- `motor/correr_estandar.py::main` — antes el fallo del subproceso primario retornaba solo un mensaje → ahora escribe RESULT de fallo y `_RECIBO_EJECUCION.json` con el error y el contorno.
- `motor/correr_estandar.py::_verificar_hashes_canonicos` — antes el hash canónico podía degradarse a aviso si faltaba el manifiesto → ahora Engine V5 y catálogo 244 se validan siempre contra sus hashes fijados, de forma independiente del manifiesto.
- Los bloqueos de Engine/244 ausentes o con hash distinto, errores de manifiesto y gate Z90 dejan un plan de PARADA_DURA; el plan prohíbe el bypass y no autoriza ejecutar ni sustituir el artefacto.
- Errores de respuesta humana, traducción y verificación de salida ahora incluyen plan de contorno.
- `docs/CONTRATOS_OPERATIVOS_V7.md` queda como autoridad contractual única; corrige control de flujo y describe confianza U7 post-corrida B1–B6 con `calibrada=false`.
- Los contratos anteriores se archivan bajo `antecedentes_motor/historial_contratos/`; sus rutas originales son avisos, no instrucciones activas.
- README, FeedMe y sidecars apuntan al mismo contrato y al nombre operativo Motor U7.
- El workflow de contratos incorpora las pruebas del control de flujo.

## Hashes canónicos verificados (motor y catálogo)

- Engine V5: `665c39a2861e58772522e91272563260d980908b1d4ab9f7092d3413d0c36082` (protegido; no modificado).
- Catálogo 244: `d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1` (protegido; no modificado).
- Base de trabajo: `dbb60e7248359aedc5ba4a827dbacf292b92cd48`.

## Pruebas: 94 passed, 0 skipped, 0 failed

**CI verificado:** run [#45860926469](https://github.com/marcojpad-hash/motor-u6-storage/actions/runs/45860926469), job `runner-contract` SUCCESS, 94 pruebas aprobadas en 41.30 s. Incluye las pruebas del adaptador, excepciones no controladas, hash canónico independiente del manifiesto, parada dura Z90, integración UNICO, runner JSON y preparación entry-only. El primer run #45860284178 detectó tres fallos de carga por una ruta duplicada `motor/motor/motor`; se corrigió a `motor/motor/control_flujo_soluciones.py` y las corridas posteriores pasaron. No se ejecutó una corrida productiva ni se alteraron Engine V5, catálogo 244 o custodia.
