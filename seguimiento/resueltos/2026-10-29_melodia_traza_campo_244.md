# Resolución de la melodía/traza del campo 244 — 2026-10-29

## Estado
**Implementación alternativa creada; integración con la fábrica y ejecución de una corrida real pendientes de verificación.** No se modifica el motor canónico ni el catálogo 244.

## Qué encontré
El módulo anterior `motor/motor/traza_campo_244.py` sustituye una hipótesis ausente por `0.5` al construir series y calcular `Δ`. Eso fabrica movimientos que no fueron observados. Además, asigna rango de cola a hipótesis que no aparecen en un corte. La lectura de la “melodía” puede entonces mezclar movimiento real con imputación.

## Qué cambié
Se creó `motor/traza_campo_244_v2.py` como alternativa aislada:
- conserva la unión de hipótesis de todos los cortes;
- no imputa valores ausentes; los representa como `null`;
- calcula `Δ` y cambio de rango solo cuando ambos extremos están observados;
- entrega, por tramo, número de deltas observados y número de datos ausentes;
- calcula correlación solo con tramos compartidos observados;
- evita que `origenes_renovables` declare una señal a partir de un valor ausente;
- incluye autoprueba para comprobar que una hipótesis ausente no se convierte en un falso `Δ`.

## Interpretación correcta
La melodía no es el ranking de H: es la trayectoria de cada hipótesis a través de los cortes (P, Δ, cambio de rango y co-movimiento posible). La co-correlación es indicio de movimiento conjunto, no identidad ni causalidad. Una hipótesis ausente es **dato faltante**, no probabilidad 0.5, desaparición ni evidencia de estabilidad.

## Prueba y límite
La autoprueba está incluida en el archivo alternativo, pero **no se ha ejecutado en el entorno del repositorio** ni se ha conectado la versión V2 a la fábrica/runner. Por contrato, esto no se marca como ejecución confirmada. Siguiente paso técnico: correr el self-test y el smoke de un caso, comprobar el recibo real y comparar V1/V2 antes de cambiar el cableado.

## Artefactos
- Alternativa: `motor/traza_campo_244_v2.py`
- Este informe: `seguimiento/resueltos/2026-10-29_melodia_traza_campo_244.md`
- Registro de avance: `avances/2026-10-29_melodia_traza_campo_244.md`

## Integridad
No se modificaron `motor/Engine_V5_CANONICO_SOLO.py` ni `motor/patterns_final_v14.json`. La V1 queda intacta para comparación y reversión.
