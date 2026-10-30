# Resuelto — consistencia del historial PAC en predicción y ablación

Fecha: 2026-10-30
Caso de validación: `CAL_F005_01_COURBET`
Lote: `F006_TRAZA_V2_R7`

## Incidencia original
La predicción principal construía el historial de candidatas con la unión de los ejes P/A/C, pero la ablación adversarial `token_core` lo reconstruía únicamente desde `P_candidatos_0a3`. Por tanto, el contrafactual evaluaba un universo distinto y podía eliminar familias respaldadas por A o C antes de calcular su ranking.

## Causa raíz
Dos implementaciones independientes del mismo contrato de historial:
- Ruta principal: unión PAC.
- Ruta contrafactual: P únicamente.

## Cambio aplicado
Commit motor: `04a00e0d13e012e317d548e0a8826842884f8e67`.

Se extrajo `_candidate_history_for_cut(cut)` como constructor único de historial por corte. La ruta principal y la ablación `token_core` llaman ahora al mismo helper. La función deduplica por familia y conserva la procedencia `ejes`. También se añadió `_candidate_histories_from_cuts` para probar la construcción por lote.

Commit de pruebas: `9be120e6af166c8a41313f85c333b3f917a55b7b`.

## Prueba ejecutada
Suite `Traza campo 244`: 10 passed, 0 failed.
https://github.com/marcojpad-hash/motor-u6-storage/actions/runs/41082009895

Suite `Traza Campo 244 V2 specs`: success.
https://github.com/marcojpad-hash/motor-u6-storage/actions/runs/41082009804

Las regresiones verifican:
1. Las familias que aparecen solo en A o C no desaparecen del universo.
2. Las familias repetidas se deduplican y conservan todos sus ejes de origen.
3. La ruta principal y la ablación `token_core` usan el helper compartido.

## Corrida real
Fábrica R7: success, código 0, recibo completado.
https://github.com/marcojpad-hash/motor-u6-storage/actions/runs/41081591816

Artefacto: `12989457446`.
SHA-256 del artefacto: `0ef1887f395e229e77f1ea6b37ae9025fc23d63c6e3789fedfa7489913871ffb`.

Entrada original preservada:
`a81708648e0fe77f5a12ef24eb3a26553fa82cb427068de9b3530fe0dd638b5c`.

Candados antes y después: Engine canónico y catálogo de 244 patrones = `true`.

## Resultado predictivo (separado del cierre técnico)
- H1: fallo.
- H2: fallo.
- Conjunto: acierto.
- Apuesta multiescenario: acierto.
- Destino: fallo (ruptura real; auge pronosticado).

La incidencia de consistencia PAC queda resuelta con prueba y corrida real. La predicción individual H1/H2 y el destino no quedan resueltos por este cambio; permanecen como fallos predictivos medidos, no como fallos de ejecución.

## Hashes canónicos
Engine: `665c39a2861e58772522e91272563260d980908b1d4ab9f7092d3413d0c36082`.
Catálogo: `d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1`.
