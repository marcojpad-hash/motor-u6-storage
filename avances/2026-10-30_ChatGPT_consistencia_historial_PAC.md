# 2026-10-30 — ChatGPT — consistencia PAC en ablaciones

## Qué cambió
Se unificó la construcción del historial de candidatas PAC para que la predicción principal y la ablación adversarial por eliminación de token trabajen con el mismo universo de familias y la misma procedencia por eje. Se añadieron pruebas de regresión a la suite que ya ejecuta GitHub Actions. No se modificaron el Engine canónico ni el catálogo de 244 patrones.

## Antes → ahora (por archivo / función)
- `motor/motor/MOTOR_V15_3_UNICO_20260927.py::_candidate_history_for_cut` — antes la corrida principal unía P/A/C dentro del bucle y la ablación `token_core` reconstruía el historial solo desde P; ahora ambas rutas usan el mismo helper PAC y conservan `ejes`.
- `tests/test_traza_campo_244_v2.py` — antes cubría ocho condiciones de traza; ahora añade dos regresiones: candidata exclusiva de A/C no descartada y procedencia PAC deduplicada.
- `tests/test_predictor_pac_history.py` — añade cuatro pruebas unitarias independientes del helper PAC.

## Commits
- Motor: `04a00e0d13e012e317d548e0a8826842884f8e67`
- Pruebas independientes: `5536e0c6959237e9431a5ac9aff0361fa9c31162`
- Suite CI: `36f188e19e1e1f476eafc061cf8842e4d7cd4721`

## Hashes canónicos verificados
Engine: `665c39a2861e58772522e91272563260d980908b1d4ab9f7092d3413d0c36082`.
Catálogo 244: `d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1`.
No se modificaron.

## Pruebas
La ejecución CI fue activada por el commit de pruebas. Resultado pendiente de confirmación al momento de crear esta entrada; no se declara aprobada hasta leer el resultado de Actions.
