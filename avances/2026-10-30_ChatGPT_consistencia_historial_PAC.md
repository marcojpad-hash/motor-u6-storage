# 2026-10-30 — ChatGPT — consistencia PAC en ablaciones

## Qué cambió
Se unificó la construcción del historial de candidatas PAC para que la predicción principal y la ablación adversarial por eliminación de token trabajen con el mismo universo de familias y la misma procedencia por eje. Se añadieron pruebas de regresión a la suite que ya ejecuta GitHub Actions. No se modificaron el Engine canónico ni el catálogo de 244 patrones.

## Antes → ahora (por archivo / función)
- `motor/motor/MOTOR_V15_3_UNICO_20260927.py::_candidate_history_for_cut` — antes la corrida principal unía P/A/C dentro del bucle y la ablación `token_core` reconstruía el historial solo desde P; ahora ambas rutas usan el mismo helper PAC y conservan `ejes`.
- `tests/test_traza_campo_244_v2.py` — antes cubría ocho condiciones de traza; ahora añade dos regresiones: candidata exclusiva de A/C no descartada y procedencia PAC deduplicada.

## Commits
- Motor: `04a00e0d13e012e317d548e0a8826842884f8e67`
- Suite CI (corrección de importación sin NumPy): `9be120e6af166c8a41313f85c333b3f917a55b7b`
- Documentación: `6663fd3bb1fb1d6dba3813c6b73e7a957e5a21d5`

## Hashes canónicos verificados
Engine: `665c39a2861e58772522e91272563260d980908b1d4ab9f7092d3413d0c36082`.
Catálogo 244: `d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1`.
No se modificaron.

## Pruebas
10 pruebas aprobadas, 0 fallidas. Workflow `Traza campo 244`: https://github.com/marcojpad-hash/motor-u6-storage/actions/runs/41082009895. Workflow `Traza Campo 244 V2 specs`: https://github.com/marcojpad-hash/motor-u6-storage/actions/runs/41082009804. La fábrica real también terminó correctamente tras el cambio del motor: https://github.com/marcojpad-hash/motor-u6-storage/actions/runs/41081591816. Resultado sellado R7: H1/H2 siguen sin acierto; el conjunto y la apuesta multiescenario sí aciertan (1); el destino sigue fallando (ruptura real frente a auge pronosticado). Este cambio corrige consistencia del universo de candidatas en las ablaciones; no se atribuye una mejora causal de predicción a esa corrección. Artefacto: `12989457446` (SHA-256 `0ef1887f395e229e77f1ea6b37ae9025fc23d63c6e3789fedfa7489913871ffb`).
