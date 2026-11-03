# 2026-11-03 — Mediciones de orquestación epistémica U6

## Estado general

**Auditoría retrospectiva ejecutada; cinco comparaciones causales no completadas.** Se analizaron el artefacto de ejecución F006 TRAZA V2 R7 (JSON de salida, recibo y ledger CEB), el CSV de calibración acumulada, los compromisos de lotes F001–F005, el informe de auditoría del 31-oct y los contratos del repositorio.

No se lanzó una corrida nueva del motor. Las entradas de los casos sellados no están almacenadas en el repositorio (se conservan hashes y compromisos) y las reglas de custodia impiden reutilizarlas como si fueran casos independientes. No se inventaron inputs ni controles contrafactuales.

Engine V5 canónico y catálogo 244: los artefactos F006 registran hashes coincidentes:
- Engine: `665c39a2861e58772522e91272563260d980908b1d4ab9f7092d3413d0c36082`
- Catálogo: `d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1`

## Base de evidencia

- Corrida F006: `CAL_F005_01_COURBET`, input SHA-256 `a81708648e0fe77f5a12ef24eb3a26553fa82cb427068de9b3530fe0dd638b5c`.
- Es una reevaluación del caso F005 Courbet; no suma un caso independiente.
- Recibo: `COMPLETED`, returncode 0, duración 20.562 s.
- Monte Carlo: 9 llamadas, 6,310 simulaciones, 9 convergentes, 0 no convergentes.
- Ledger CEB: 23,420 líneas; 304 archivos en manifiesto, sin deriva ni ausentes; 108 candados de plugins verificados, 0 fallos.
- Artefacto ZIP recuperado: SHA-256 declarado en el registro `0ef1887f395e229e77f1ea6b37ae9025fc23d63c6e3789fedfa7489913871ffb`.
- Archivo de calibración: `casos/fabrica/calibracion_acumulada.csv`, 50 filas, 45 case_id únicos, 40 casos sellados independientes y 5 no sellados. Las 5 filas adicionales son reevaluaciones F001_D022 de los mismos cinco inputs F001.

## 1. Guardianes: con vs. sin guardianes

**Medición disponible: parcial; no hay corrida emparejada sin guardianes.**

En F006:
- Se ejecutaron 9 guardianes.
- 2 tuvieron bandera distinta de LIMPIO: `PREGUNTA_DETRAS_V2=MARCA` y `LOGICA_COPI=NO_RESUELTO`.
- Se registraron 5 marcas en total: 3 marcajes de perfilamiento, 1 objeción lógica y 1 observación de fragilidad de H1 por el guardián de hombre de acero.
- El hash del predictor antes/después fue idéntico; H1/H2 y catálogo permanecieron iguales.
- La etapa `guardianes_control_v1#1` duró 172.52 ms (0.84 % del tiempo total de la corrida).

La objeción de Copi fue `NO_RESUELTO_TOP1_NO_ES_TOP_DE_NINGUN_CORTE`: H1 surgió de la fusión, aunque no encabezaba ningún corte individual. Es un hecho descriptivo, pero no demuestra por sí mismo un error: una fusión entre cortes puede producir una candidata que no fue primera en ninguno de ellos.

**Control de falsos positivos:** los tres marcajes de `PREGUNTA_DETRAS_V2` recayeron en palabras de una descripción factual (`elegido`, `delegado`, `pública`). En este contexto parecen falsos positivos léxicos probables, no evidencia de manipulación. No existe etiqueta humana independiente para convertirlos en una tasa confirmada. La observación de fragilidad de H1 no se clasifica como falso positivo.

**Resultado:** está demostrada la ejecución y la preservación del predictor; no está demostrado que los guardianes mejoren exactitud, reduzcan errores o produzcan más aciertos que la configuración sin ellos.

## 2. Compuerta de cierre: activa vs. desactivada

**Medición disponible: parcial; no hay corrida emparejada sin compuerta ni caso con pendiente contradictorio cargado en esta ejecución.**

En F006:
- La compuerta se ejecutó y decidió `CIERRE_PERMITIDO`.
- Pendientes vivos cargados: 0; pendientes revisados: 0; contradicciones que impedían cerrar: 0.
- La etapa duró 0.605 ms.
- La compuerta aparece antes de la etapa de guardianes en el ledger CEB. Por tanto, en esta corrida no revisó la objeción nueva de Copi producida después.
- La salida final conserva dos objeciones (Copi y modo estricto), grado `AJUSTADA`, sin cambiar H1/H2.

El ledger CEB marca `compuerta_cierre_latencia_v0_16_4` y `ruta_cierre_latente_guardianes` como `OUTPUT_NO_OBSERVED_CONSUMER`; el JSON final sí contiene sus estados. Esto es una brecha de trazabilidad del ledger, no prueba suficiente de que el resultado no se utilice.

**Resultado:** se midió una ejecución sin pendientes que bloquearan. No se midió la capacidad de la compuerta para impedir un cierre incorrecto ni su efecto frente a una versión apagada.

## 3. Hipótesis única vs. conjunto abierto

**Medición descriptiva ejecutada sobre la calibración; no es todavía una ablación causal del mismo runner.**

Se deduplicaron las filas por `case_id`/input SHA antes de calcular H1, H2, set y escenario. Resultado sobre 40 casos sellados independientes:

| Métrica | Aciertos | Tasa |
|---|---:|---:|
| H1 | 8/40 | 20.0 % |
| H2 | 5/40 | 12.5 % |
| Set abierto | 12/40 | 30.0 % |
| Apuesta/escenario principal | 10/40 | 25.0 % |

El set abierto supera la cobertura de H1 en 10 puntos porcentuales y la de H2 en 17.5 puntos. Es una señal favorable de cobertura, no una prueba de utilidad global: no se registró el tamaño medio del set para todos los casos ni una métrica de precisión/penalización por hipótesis sobrantes.

En F006, el conjunto abierto emitió 5 hipótesis y conservó 2 alternativas fuera del set necesario-suficiente. El desenlace sellado intersectó el conjunto; H1 y H2 individuales fallaron. Esta reevaluación de Courbet no se suma al denominador independiente.

**Control de falsos positivos:** no se puede calcular precisión del set sin cardinalidad y pertenencia completa por caso en el registro agregado. Una mayor cobertura puede venir acompañada de más hipótesis irrelevantes.

**Resultado:** la cobertura del set es superior a H1 en la muestra independiente disponible. No se ha demostrado que el beneficio compense el tamaño del conjunto.

## 4. Memoria desactivada vs. persistencia

**Medición disponible: ejecución y persistencia confirmadas; efecto causal no medido.**

En F006:
- `cierre_memoria_operativa.status=EJECUTADO`.
- Se escribieron 2 entradas históricas; quedaron 0 frentes activos.
- Índice entre corridas: `PERSISTIDO`.
- El registro persistente reportó 193 tokens únicos tras la ingestión final y 4 cadenas nuevas en esa fase.
- En la importación del mismo artefacto se omitió 1 duplicado por SHA y no se añadieron eventos ni tokens.
- La ruta CEB de transporte y bus StinkBox observada sumó aproximadamente 141.32 ms entre las etapas registradas.

**Control de falsos positivos/contaminación:** la deduplicación por SHA funcionó en la repetición observada. Eso no demuestra que la memoria nunca introduzca tokens irrelevantes, contaminación entre casos o recuperación espuria.

**Resultado:** persistencia, escritura e idempotencia parcial demostradas en una corrida. No hay comparación sin memoria para medir cambios en aciertos, errores, recuperación o costo total.

## 5. Pipeline fijo vs. resolución adaptativa

**Medición disponible: ejecución adaptativa confirmada; no hay baseline fijo emparejado.**

En F006:
- La objeción de Copi disparó TORTUGAS desde la ruta de guardianes.
- Se pasó de 3 cortes originales a 4 cortes finos.
- Se hicieron 6 remediciones micro/meso/macro.
- Solo 1 de 3 niveles sostuvo H1; meso mantuvo empate entre 7 candidatas y macro favoreció otra candidata.
- Veredicto: `TORTUGAS_NO_SEPARA_TOP1`.
- H1/H2 no fueron reescritas por los guardianes.
- El cierre final quedó `RESUELTO_OPERACIONALMENTE`, grado `AJUSTADA`, conservando 2 objeciones.

**Control de falsos positivos:** la activación se debió a una objeción real según la regla codificada, pero su valor como señal de error no está adjudicado. No se puede afirmar que la ronda extra haya corregido un error; no separó el top1.

**Control de costo:** el tiempo de TORTUGAS no está separado de forma suficientemente limpia en el recibo para calcular su costo incremental frente al pipeline fijo.

**Resultado:** el mecanismo adaptativo se activó y aumentó resolución; en este caso no resolvió la separación entre candidatas. Su beneficio neto sigue sin demostrarse.

## Tres controles transversales

### A. Falsos positivos

- Hay 3 activaciones léxicas de perfilamiento que parecen falsas alarmas en el contexto observado.
- Hay una objeción de Copi cuya verdad descriptiva no equivale automáticamente a un error de predicción.
- No existe un conjunto etiquetado por evaluadores independientes para estimar precisión, recall o tasa de falsos positivos de los guardianes.
- No se puede declarar aprobado este control.

### B. Costo computacional

| Elemento observado en F006 | Tiempo |
|---|---:|
| Corrida completa | 20.562 s |
| Guardianes | 172.52 ms |
| Compuerta de cierre | 0.605 ms |
| Ruta de cierre latente | 0.704 ms |
| Transporte + bus StinkBox, etapas CEB observadas | 141.32 ms |

El costo de guardianes equivale a 0.84 % del tiempo total en esta corrida. No es una diferencia incremental causal porque falta el mismo caso corrido sin guardianes. Tampoco se debe sumar etapas anidadas como si fueran necesariamente tiempos independientes.

### C. Generalización

La calibración contiene 40 casos sellados independientes, todos biográficos, distribuidos entre categorías de políticos, científicos, artistas, empresarios y gobernantes. El registro de fábrica identifica Grok Bot como modelo de generación. No hay prueba de generalización a tareas no biográficas ni comparación entre LLM distintos.

Los cuatro casos ciegos históricos B-01/N-02/C-03/H-01 no cuentan como corridas del motor U6; el plan C01–C20 sigue pendiente. Por tanto, generalización entre dominios y entre modelos: **no medida**.

## Hallazgo de integridad de calibración

`casos/fabrica/CALIBRACION_ACUMULADA.md` publica 45 evaluaciones para H1/H2/set/apuesta. El CSV contiene 50 filas, pero cinco son reevaluaciones F001_D022 de los mismos cinco inputs F001, con los mismos input SHA. No deben incrementar el denominador de esas métricas.

Al deduplicar por caso:
- H1 pasa de 9/45 a 8/40 (la tasa queda en 20 %).
- H2 pasa de 5/45 a 5/40 (12.5 %, no 11.1 %).
- Set pasa de 13/45 a 12/40 (30 %, no 28.9 %).
- Apuesta pasa de 10/45 a 10/40 (25 %, no 22.2 %).

Los indicadores de destino sí pueden usar 40 registros: F001_D022 introduce el pronóstico de destino, ausente en las cinco filas originales F001. Sus tasas permanecen 15/40 (37.5 %) y 27/40 (67.5 %).

Esta corrección no altera predicciones ni casos; corrige el denominador estadístico para no contar el mismo input dos veces.

## Dictamen

1. La ejecución de guardianes, compuerta, memoria y resolución adaptativa está demostrada en F006.
2. La cobertura del conjunto abierto es superior a H1/H2 en la muestra histórica deduplicada, aunque su precisión y tamaño medio no están medidos.
3. No se ha demostrado causalmente que guardianes, compuerta, memoria o resolución adaptativa mejoren el rendimiento frente a sus versiones apagadas.
4. El costo observado de guardianes es pequeño en esta corrida (0.84 %), pero falta una comparación emparejada.
5. Falsos positivos y generalización siguen sin estar validados.
6. La base estadística de H1/H2/set/apuesta debe leerse con 40 casos independientes, no 45.

## Qué falta para completar las cinco comparaciones

Se necesitan casos nuevos e independientes, cada uno con input congelado y desenlace separado, y corridas emparejadas con semillas y entorno constantes:
- guardianes ON/OFF;
- compuerta ON/OFF con pendientes contradictorios predefinidos;
- conjunto abierto vs. salida única, midiendo cobertura, precisión y cardinalidad;
- memoria vacía vs. memoria persistente, con controles de contaminación;
- resolución fija vs. adaptativa, midiendo acierto, número de operaciones y tiempo.

Los casos deben ser nuevos; no reutilizar Courbet ni los inputs sellados existentes. Las etiquetas de falsos positivos deben adjudicarse independientemente y el lote debe incluir al menos una tarea no biográfica y más de un modelo para probar generalización.
