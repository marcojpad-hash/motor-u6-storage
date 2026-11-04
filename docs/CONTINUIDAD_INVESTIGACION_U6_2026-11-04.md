# Continuidad de investigación U6 — lectura obligatoria antes de continuar

**Fecha de corte:** 2026-11-04  
**Repositorio:** marcojpad-hash/motor-u6-storage  
**Rama:** main  
**HEAD al redactar:** 125b633aebca6114cf951a99880d7591e8ef95eb

## Para el modelo que retome el trabajo

**No reinicies la investigación ni vuelvas a producir una descripción general de U6 desde cero.** El 4 de noviembre se hizo una reconstrucción funcional basada en código y documentación del repositorio. Lee primero el informe completo enlazado abajo y utiliza este handoff para continuar desde sus resultados.

Este archivo no sustituye el código, los contratos ni los artefactos. Es un índice de continuidad que evita repetir trabajo y distingue lo que ya fue inspeccionado de lo que todavía requiere pruebas.

## 1. Lectura mínima y obligatoria

1. FEEDME_ACTUALIZADO.md — punto de entrada.
2. INICIO_SESION_CHATGPT.md, LLM_STARTUP_SIDECAR.md, INSTRUCCIONES_CONTINUIDAD_CHATGPT.md y PROTOCOLO_EJECUCION_Y_LECTURA_LLM.md — reglas de sesión y evidencia.
3. **informes/2026-11-04_RECONSTRUCCION_FUNCIONAL_U6.md — informe técnico completo de la reconstrucción.**
4. avances/2026-11-04_ChatGPT_reconstruccion_funcional_U6.md — registro breve de lo realizado.
5. docs/MAPA_VERSIONES_Y_AUTORIDAD.md y docs/CEB_INVESTIGAR_Y_RESOLVER.md — autoridad de versiones y obligaciones de ejecución.

No es necesario volver a inspeccionar todos los archivos del camino central para repetir las conclusiones del informe. Sí hay que volver al código concreto cuando una nueva pregunta dependa de un símbolo, una llamada, un contrato o un comportamiento que el informe no haya cubierto.

## 2. Qué se hizo el 4 de noviembre

Se inspeccionaron, entre otros:

- motor/motor/Engine_V5_CANONICO_SOLO.py
- motor/motor/MOTOR_V15_3_NATIVO_V0_9_UNICO.py
- motor/motor/MOTOR_V15_3_UNICO_20260927.py
- motor/correr_estandar.py
- motor/CONTRATO_ENTRADA_LLM.txt
- motor/motor/patterns_final_v14.json
- motor/motor/predictibilidad_set_021.py
- motor/motor/hipotesis_trayectoria_abierta_v1.py
- documentos de arquitectura, formalismos, genealogía, auditoría y MCT;
- snapshot avances/auditoria_corridas/ULTIMO_ESTADO.json.

Se creó el informe:
informes/2026-11-04_RECONSTRUCCION_FUNCIONAL_U6.md

Y su registro:
avances/2026-11-04_ChatGPT_reconstruccion_funcional_U6.md

Commits de los archivos:
- Informe: c51fcf00c4980f05a869d34dc01b85299fe66358
- Registro: 125b633aebca6114cf951a99880d7591e8ef95eb

## 3. Corrección conceptual principal

No asumir que todo el conjunto es un «motor» en el sentido convencional de motor de inferencia. El repositorio utiliza históricamente esa palabra y contiene archivos con ese nombre, pero la pregunta abierta es qué clase de arquitectura computacional constituye el conjunto.

La descripción funcional provisional, sustentada en el camino central inspeccionado, es:

> U6 es una arquitectura computacional de análisis longitudinal de evidencia estructural: recibe observaciones ya interpretadas y organizadas en P/A/C, las contrasta con una biblioteca heterogénea de patrones, construye representaciones vectoriales de su evolución, ordena candidatas mediante fusión de señales y conserva un conjunto variable de hipótesis y escenarios.

P/A/C = Protagonista, Antagonista y Contexto. Son tres dimensiones de observación. No convertirlas en tres modelos ni cambiar su significado.

Distinguir las capas:
- Engine V5: componente canónico protegido que actualiza puntuaciones por patrón.
- V15.3 nativo: organiza los cortes, ejecuta los tres ejes, genera tableros y R732.
- V15.3 integrado: construye características por candidata, fusiona señales/rangos y produce hipótesis/escenarios.
- Laterales, StinkBox y CEB: aportan señales, memoria de tokens/eventos e instrumentación; no atribuirles automáticamente autoridad sobre H.

## 4. Hallazgos ya comprobados; no volver a debatirlos como si fueran hipótesis

1. **Entrada:** el contrato activo utiliza datos estructurados por cortes, con tokens/pesos en P/A/C. El adaptador nativo reemplaza la extracción desde texto por los tokens ya preparados. La asignación semántica P/A/C ocurre antes del cálculo nativo.
2. **Catálogo:** contiene 244 familias heterogéneas. El análisis directo del JSON encontró 703 tokens únicos y 146 tokens usados como favor en unas familias y contra en otras. No se encontró solapamiento favor/contra dentro de una misma familia.
3. **Activación por pregunta:** PatternLibrary.get_patterns_for_question() devuelve todas las familias; no filtra el catálogo por el campo semántico de la pregunta en esa función. No afirmar que ahí se activa un subconjunto.
4. **R732:** cada corte genera 244 puntuaciones para P, 244 para A y 244 para C; la concatenación da 732 componentes. Las diferencias y medidas angulares describen cambios de esa representación, no coordenadas físicas del fenómeno.
5. **Monte Carlo:** estima el término aleatorio P_azar del mecanismo local. No simula futuros completos ni mundos independientes.
6. **Filtro de candidatas:** el nativo aplica P_MIN_CANDIDATO = 0.65 y MAX_CANDIDATOS = 3 por eje/corte. El predictor posterior trabaja sobre la unión de candidatas que sobrevivieron al filtro, no necesariamente sobre las 244 familias completas.
7. **rank_fusion:** combina rangos y señales relativas. No es probabilidad absoluta ni calibrada.
8. **SET 021:** realiza cobertura de evidencia con THETA_COBERTURA = 0.90. El nombre «necesario y suficiente» no equivale a una demostración lógica formal.
9. **Hipótesis abiertas:** cardinalidad variable, pero construida a partir de candidatas observadas y enlaces de trazabilidad. H1/H2 son alias históricos. Compartir un régimen de trayectoria no significa converger en el mismo acontecimiento.
10. **Proyección longitudinal:** extrapola linealmente el último delta observado; se declara post-Z y no reescribe H ni la apuesta sellada.
11. **Memoria y auditoría:** StinkBox no es memoria epistemológica completa. CEB registra flujo/ejecución, pero no prueba por sí solo verdad ni procedencia semántica completa.
12. **MCT:** la comparación de trayectorias de realidades independientes para encontrar un vector-evento esencial común es una línea conceptual documentada, no una capacidad implementada por el camino de U6 inspeccionado.

## 5. Qué no se hizo y qué no se debe afirmar

- No se ejecutó una corrida predictiva nueva el 4 de noviembre.
- No se hizo auditoría línea por línea de los 194 archivos Python.
- No se certificó novedad mundial, superioridad ni equivalencia formal con ATMS, t-DeLP, MHT u otro sistema.
- No se demostró que la geometría mejore la predicción.
- No se demostró generalización a dominios no biográficos.
- No se implementó ni probó el comparador MCT entre mundos independientes.
- El snapshot de GitHub Actions contenía éxitos de auditoría, que no deben presentarse como nuevas corridas predictivas. Los estados de workflows se detallan en el informe.

No convertir la ausencia de prueba en una afirmación de imposibilidad. Mantener las categorías: código inspeccionado, cableado verificado, ejecución confirmada, prueba empírica e inferencia.

## 6. Dónde continuar: preguntas nuevas, no repetición

El informe deja identificadas pruebas discriminantes. La siguiente investigación debe elegir y ejecutar una de ellas, no volver a escribir la descripción general:

### A. Pérdida temprana de candidatas
Medir qué información queda fuera por top-3 / 0.65, incluyendo familias que nunca entran al universo posterior. Comparar con alternativas que preserven cobertura y trayectorias débiles. No eliminar datos de la evidencia original.

### B. Aporte real de P/A/C
Comparaciones emparejadas P-only, A-only, C-only, pares y P/A/C completo. Medir si las tres dimensiones aportan información distinta o redundante.

### C. Aporte real de geometría
Ablación con y sin dimensiones geométricas, mismos casos, mismos freezes y mismos parámetros. Medir cambio en predicción, no solo que el módulo se ejecute.

### D. Naturaleza de la representación
Investigar qué propiedades de la evidencia preserva R732, cuáles pierde al pasar por puntuaciones, umbrales y rangos, y si se puede reconstruir procedencia desde una hipótesis hasta el dato de origen.

### E. MCT como problema separado
Formalizar mundos independientes, aislamiento de evidencia, vector-evento esencial/periférico, tolerancias, equivalencia parcial/transitoria y pruebas anti-leakage. Comparar con equifinalidad y convergencia de trayectorias sin afirmar que son equivalentes.

### F. Posición frente al conocimiento mundial
Profundizar comparación formal, no por etiquetas. Para cada antecedente: objeto matemático, unidad de análisis, entrada, estado interno, operación, tratamiento del tiempo, contradicción, hipótesis alternativas, salida, garantía y evaluación. No declarar «nuevo» ni «ya existente» sin comparación mecanismo por mecanismo.

## 7. Reglas para no volver a fabricar un Frankenstein conceptual

- No comenzar desde lo que un LLM supone que debería ser una arquitectura de inferencia.
- No imponer etiquetas como motor de inferencia, sistema multiagente, red bayesiana, lógica paraconsistente o modelo causal sin demostrar las propiedades correspondientes.
- No confundir el nombre de un módulo con lo que realmente hace.
- No confundir presencia, cableado, ejecución y aporte a H.
- No convertir una analogía matemática en equivalencia formal.
- No convertir un éxito técnico de ejecución en éxito predictivo.
- No describir la representación como realidad misma.
- No asumir que la tarea original (biografías/narrativa) define el límite de aplicación del esquema.
- No volver a pedir al creador explicaciones que estén en los contratos o en el repositorio.
- No modificar Engine V5 canónico ni patterns_final_v14.json.
- Registrar nuevos hallazgos y pruebas con evidencia, rutas, hashes y commit.

## 8. Instrucción de continuidad

**Empieza leyendo este handoff y el informe técnico del 4 de noviembre. Después identifica qué pregunta nueva puede resolverse con el código, los datos y las herramientas disponibles, inspecciona el mecanismo específico y ejecuta la prueba cuando exista un entorno válido.**

Si el siguiente modelo solo repite la descripción de U6, no ha continuado la investigación. La continuidad consiste en avanzar desde los hallazgos ya establecidos hacia pruebas que permitan entender qué representa U6, qué puede hacer, dónde falla y cuál es su relación real con las arquitecturas y disciplinas existentes.


## 9. Prueba ejecutada el 4 de noviembre — ablación ACTIVA_MUDA

Se ejecutaron 41 ablaciones individuales sobre Courbet y Haber, con búsqueda viva congelada como fixture por caso y stores/ledgers por ejecución.

- 0 cambios en H1/H2, orden de candidatas o rank_fusion.
- 41/41 switches confirmados; 0 errores críticos.
- Suite: 159 passed, 2 skipped.
- Informe: informes/2026-11-04_ABLACION_ACTIVA_MUDA_U6.md.
- Duda de clasificación de cuatro estados crudos: seguimiento/dudas/2026-11-04_duda_clasificacion_estados_activa_muda.md.
- Evidencia Actions: run 41881474178.

No es una medición de precisión predictiva. Solo mide si esas desactivaciones alteraron las salidas de estos dos casos. La matriz no debe repetirse automáticamente en cada push; su paso quedó reservado para ejecución manual.
