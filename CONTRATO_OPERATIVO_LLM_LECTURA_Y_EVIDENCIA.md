# CONTRATO OPERATIVO DE LECTURA Y EVIDENCIA PARA MODELOS LLM
Fecha: 2026-11-02. Aplicable a ChatGPT, Grok, Claude y cualquier agente que trabaje con Motor U6.

## Regla principal
Ningún modelo puede afirmar qué tiene, qué hace, qué no tiene, qué ejecutó o qué necesita el motor basándose únicamente en memoria conversacional, entrenamiento o nombres de componentes. Antes de cada análisis o modificación del motor, debe volver a leer los archivos pertinentes en la rama y commit vigentes. Si no tiene acceso, declara NO VERIFICADO y no diseña reemplazos.

## Arranque obligatorio en cada sesión/tarea
1. Identificar repositorio, rama y commit; anotar fecha de inspección.
2. Leer README.md, FEEDME_ACTUALIZADO.md, CONTRATO_CARPETAS.md, PROTOCOLO_EJECUCION_Y_LECTURA_LLM.md, docs/MAPA_VERSIONES_Y_AUTORIDAD.md y este contrato.
3. Leer motor/README_MOTOR.md, el punto de entrada efectivo, selección de motor, catálogo y las piezas específicas relacionadas con la tarea.
4. Consultar la bitácora y los resultados de corridas antes de decir que una funcionalidad existe, funciona o falta.
5. Identificar implementaciones equivalentes y antecedentes antes de proponer una pieza nueva.
6. Registrar rutas, símbolos, SHA/commit, evidencia y limitaciones. Sin evidencia, marcar NO VERIFICADO.

## Inventario mínimo a reconstruir desde código, no desde recuerdos
- Engine V5 canónico protegido y catálogo de 244 patrones; runner V15.3, selección de motor y puntos de entrada.
- Corpus_Final_Unificado_17_Formulas.txt: listar las 17 fórmulas por nombre, función, uso real y ubicación de llamada; distinguir documentación de ejecución.
- P/A/C, cortes temporales, vectorización, fusión, hipótesis abiertas, ranking, compuertas de información, latencia y cierre.
- Guardianes y sidecars: Copi, falacias, décimo hombre, polaridad, Beristáin, hombre de acero, Sherlock, Aquiles, Memento, Caldero, Souriau/Polti y demás componentes presentes.
- Orquestación, workflows, casos F001–F007, sellos, fixtures, recibos, artefactos y stores.
Por cada pieza: ruta, versión, entrada, salida, invocador, condiciones de activación, permisos de decisión, prueba y estado comprobado.

## Estados de evidencia (no intercambiables)
- CODIGO_PRESENTE: archivo y símbolo inspeccionados.
- CABLEADO_VERIFICADO: se inspeccionó la llamada efectiva y su condición.
- EJECUTADO_VERIFICADO: run, log, artefacto y SHA/commit identificables.
- PROBADO: prueba con aserciones pertinentes y resultado disponible.
- HISTORICO: solo evidencia anterior, sin vigencia actual garantizada.
- DOCUMENTADO_NO_VERIFICADO: contrato o README lo declara pero no se comprobó.
- BLOQUEADO: causa concreta y evidencia.
- NO_VERIFICADO: falta acceso o evidencia.
No convertir CODIGO_PRESENTE en EJECUTADO_VERIFICADO.

## Regla de interpretación
No normalizar nombres o términos del usuario por similitud fonética. 'Copi' se resuelve contra guardian_logica_copi_v1.py y guardianes_control_v1.py antes de hablar de lógica proposicional. 'Lean' es un asistente de pruebas formales; la investigación ETH/#SAT debe contrastarse con el alcance real de Copi y del motor, sin confundir prueba de satisfacibilidad, conteo de modelos, validez deductiva, consistencia y predicción ponderada.

## Regla de no duplicación
Antes de implementar: búsqueda de archivos y símbolos, lectura del contrato, comparación de entradas/salidas y pruebas. Si ya existe, primero diagnosticar si está cableado y ejecutado. Una propuesta nueva requiere diferencia funcional demostrada, métrica, hipótesis falsable y aislamiento experimental. No modificar Engine V5 ni patterns_final_v14.json.

## Bitácora obligatoria por tarea
Registrar: fecha; repositorio/rama/commit; solicitud; documentos y código leídos; componentes existentes; afirmaciones verificadas con rutas; corridas y artefactos; cambios con commits; pruebas; pendientes; incertidumbres; decisión y siguiente paso. Si no hubo cambios, decirlo expresamente.

## Criterio de salida
La respuesta operativa debe separar HECHOS VERIFICADOS, INFERENCIAS, CAMBIOS EJECUTADOS, PRUEBAS y PENDIENTES. Ningún modelo debe declarar validación experimental sin ejecución trazable ni utilizar datos posteriores al corte Z para formar hipótesis.

## Investigación Lean/ETH (estado documental)
Existe docs/INVESTIGACION_LEAN_ETH_Y_APLICACION_MOTOR_U6.md; debe releerse junto al código de Copi y los casos antes de decidir si aporta algo. La existencia de Copi NO demuestra que U6 implemente el algoritmo de conteo #SAT del preprint. Tampoco demuestra que Lean mejore el predictor. Comparar formulaciones, capacidades, costes y pruebas antes de afirmar utilidad o redundancia.

Este contrato complementa, no reemplaza, los contratos existentes. Si hay conflicto, documentar el conflicto y consultar la autoridad de versiones; no resolverlo por intuición.
