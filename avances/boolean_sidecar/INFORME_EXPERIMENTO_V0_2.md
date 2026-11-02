# Informe experimental — motor lateral Booleano v0.2

Fecha: 2026-11-02
Rama: `experiment/boolean-sidecar-20261102`
Corrida GitHub Actions: [41418489348](https://github.com/marcojpad-hash/motor-u6-storage/actions/runs/41418489348)
Artefacto: `boolean-sidecar-resultados`, SHA-256 `7b4bc90898cae162f41d4bbb82f34f8664f2d2dfa991b5f12d9fcbc9d7fd6185`
Código probado en esa corrida: commit `214c8f7bc070ab43c61a43c352736f67c4d90d51`.

## Diseño
Una variable booleana por cada una de las 244 familias. La CNF exige al menos una familia compatible y añade una cláusula unitaria negativa cuando un token observado en P/A/C supera tanto el piso experimental 0.60 como el umbral `tokens_contra` de la familia. El prototipo no produce ranking ni probabilidad: solo una lista de compatibilidad lógica.

## Muestra comparable
- 40 casos con corrida sellada y `returncode=0`, F001–F005.
- 5 casos pausados/no sellados se excluyeron de la comparación.
- F006 no se cuenta como caso independiente: es la reevaluación de Courbet de F005.
- F007 no se ejecutó: su archivo de destinos aporta destino personal, pero no las familias de desenlace exigidas por el contrato; la compuerta corregida rechaza la preparación sin esos datos.

## Resultados
- Catálogo: 244 familias.
- Casos comparables: 40.
- Cobertura de casos: 40/40 (100%); al menos una familia real sellada sobrevivió al filtro en cada caso.
- Reducción media de candidatas: 5.96%; mediana: 5.33%.
- Candidatas compatibles restantes: 229.47 de 244 en promedio.
- Etiquetas de familia reales selladas: 158; etiquetas reales excluidas: 11 (6.96%).
- En 9 de 40 casos se excluyó al menos una etiqueta real, aunque quedó otra etiqueta real compatible.

### Motor base en esos mismos 40 casos
| Métrica | Aciertos | Tasa |
|---|---:|---:|
| H1 | 8/40 | 20.0% |
| H2 | 5/40 | 12.5% |
| Set abierto | 12/40 | 30.0% |
| Apuesta de escenario principal | 10/40 | 25.0% |

## Lectura
El filtro Booleano conservó al menos una familia real en los 40 casos, pero solo redujo el espacio de candidatas alrededor de 6%. Además, eliminó 11 etiquetas reales (aunque no dejó ningún caso sin cobertura). Por tanto, el resultado actual no demuestra mejora predictiva ni una ganancia operativa suficiente para integrarlo al motor. Es un filtro lateral débil y potencialmente riesgoso si se usa para descartar familias.

La comparación es descriptiva, no una evaluación ciega independiente: usa la misma muestra histórica ya utilizada para calibración y los umbrales del catálogo, cuyos pesos de contradicción no están calibrados empíricamente.

## Decisión técnica
**No integrar al motor principal.** Mantener aislado como experimento. La siguiente prueba válida, si se continúa, requiere reglas de incompatibilidad justificadas independientemente y un lote ciego nuevo; no ajustar umbrales sobre estos 40 casos y volver a presentarlos como validación.

## Integridad
La corrida del experimento verificó los SHA-256 de:
- `motor/motor/Engine_V5_CANONICO_SOLO.py`: `665c39a2861e58772522e91272563260d980908b1d4ab9f7092d3413d0c36082`
- `motor/motor/patterns_final_v14.json`: `d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1`

No se modificaron el motor canónico ni el catálogo de 244 patrones.
