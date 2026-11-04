# Análisis comparativo de la recomposición operativa en U6

**Fecha:** 2026-11-04  
**Repositorio:** marcojpad-hash/motor-u6-storage  
**Rama:** main  
**HEAD observado al iniciar:** 6389360b89a7a36e718276a8cb7a8c39cb8d5983  
**Alcance:** comparación mecanismo por mecanismo entre el camino ejecutable de U6 y antecedentes de mantenimiento de creencias, argumentación, razonamiento probabilístico, descubrimiento de verdad, seguimiento de hipótesis, razonamiento temporal, geometría de trayectorias y procedencia de datos.  
**Tipo de trabajo:** inspección documental y de código; no se ejecutó una corrida predictiva nueva ni se modificaron archivos de código.

## 1. Pregunta y criterio de comparación

La pregunta no es si U6 inventó Bayes, geometría, actualización temporal, ranking o conjuntos de hipótesis. Es si la forma en que los adapta, les asigna una función, los conecta mediante contratos y usa sus resultados constituye una recomposición operativa diferenciable de los antecedentes.

Se comparan cinco capas:

1. **Operador matemático:** qué ecuación o procedimiento se ejecuta.
2. **Objeto de aplicación:** sobre qué datos se aplica.
3. **Transposición funcional:** qué función desempeña dentro de U6, distinta o no de su uso de origen.
4. **Contrato:** qué condiciones regulan su entrada, transformación, salida y autoridad posterior.
5. **Efecto arquitectónico:** qué operación posterior depende del resultado y qué cambia si se retira.

La distinción central es entre cambiar una fórmula y cambiar su función. U6 no necesita alterar una ecuación para alterar el papel que desempeña: puede conservar la operación matemática, sustituir el objeto al que se aplica, cambiar la interpretación admisible del resultado y conectarlo a una etapa posterior distinta.

Esto se denomina aquí **transposición operativa**. Es una categoría descriptiva de este análisis, no un término académico establecido ni una afirmación de novedad.

## 2. Base documental y verificación del estado

Se siguió el gate de arranque del repositorio: FEEDME, INICIO_SESION, instrucciones de continuidad, sidecar, protocolo de ejecución, README, contratos de carpetas, mapa de versiones, CEB, reglas de avances y auditoría previa.

Se recuperaron además los tres estudios que ya existían en el repositorio:

- docs/ESTUDIO_COMPARATIVO_NOVEDAD_ARQUITECTURA_U6_2026-11-03.md
- docs/AUDITORIA_FORMALISMOS_MATEMATICOS_REINTERPRETADOS_U6_2026-11-03.md
- docs/GENEALOGIA_TECNICA_Y_HUECOS_REALES_U6_2026-11-03.md

Este documento no los reemplaza. Los actualiza y corrige en los puntos donde las afirmaciones generales de arquitectura deben ajustarse al camino de código actualmente inspeccionado.

### Código y contratos revisados

- motor/CONTRATO_ENTRADA_LLM.txt
- motor/REGLAS.md
- motor/motor/Engine_V5_CANONICO_SOLO.py
- motor/motor/MOTOR_V15_3_NATIVO_V0_9_UNICO.py
- motor/motor/MOTOR_V15_3_UNICO_20260927.py
- motor/motor/predictibilidad_set_021.py
- motor/motor/hipotesis_trayectoria_abierta_v1.py
- motor/motor/sidecar_trazabilidad_temporal.py
- motor/motor/geometria_multicapa/sidecar_latentes_v1.py
- motor/motor/geometria_multicapa/v153_convergencia_multinivel_v0_3.py
- motor/motor/geometria_multicapa/adaptador_convergencia_real_v1.py
- motor/motor/geometria_multicapa/teseracto_recursivo_geometria_v0_4.py
- motor/motor/v153_lateral_metrics_v1_1.py
- motor/motor/ceb_runtime_v0_6_flow.py
- motor/correr_estandar.py
- motor/STINKBOX_CONTRATO_PERSISTENCIA.md
- motor/CONTRATO_HIPOTESIS_ABIERTAS_GEOMETRIA_TRABAJO_20261020.md
- motor/motor/Corpus_Final_Unificado_17_Formulas.txt

Los archivos canónicos permanecen protegidos. El SHA de fetch de GitHub es un blob SHA y no debe confundirse con el SHA-256 físico del archivo. Las huellas canónicas de autoridad siguen siendo las registradas en docs/MAPA_VERSIONES_Y_AUTORIDAD.md: Engine V5 = 665c39a2861e58772522e91272563260d980908b1d4ab9f7092d3413d0c36082; catálogo 244 = d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1.

**Estado:** CÓDIGO INSPECCIONADO. No se afirma ejecución nueva ni validación predictiva nueva.

## 3. Reconstrucción de la cadena operativa relevante

La cadena comprobada no es una fórmula única. Es una secuencia de filtros, representaciones, puntuaciones y compuertas:

1. Una persona o un LLM prepara cortes JSON con tokens y pesos en P/A/C. El contrato de entrada dice expresamente que el Engine no recibe prosa cruda.
2. El adaptador nativo valida los cortes y registra tokens fuera del catálogo.
3. Si un eje/corte contiene más de cinco tokens, el cuello CUELLO_K=5 selecciona los que pasan al Engine. Prioriza pertenencia al catálogo, peso y, en empates, frecuencia previa, racha de presencia y apoyo en otros ejes. Los restantes quedan registrados como fuera del Engine canónico, no se borran del input.
4. Se crean tres instancias de TracingEngine, una por P, A y C. Cada instancia calcula puntuaciones para las 244 familias usando los tokens que recibió.
5. Cada tablero conserva las puntuaciones completas de 244 familias. Sin embargo, la lista de candidatas que avanza se limita a las primeras tres familias que alcanzan p_final >= 0.65 por eje y corte.
6. Se concatenan los tableros completos P|A|C en R732; se calculan diferencias entre cortes, normas de desplazamiento, cosenos entre desplazamientos y kappa direccional.
7. El predictor integrado construye el universo de candidatas como la unión de las familias que sobrevivieron al top-3 en algún eje/corte.
8. Se calculan características por candidata. Se excluyen dimensiones no numéricas, constantes y duplicadas; las dimensiones restantes se convierten a rangos fraccionales con tratamiento de empates. Se suman esos rangos.
9. Las señales laterales que logran mapearse a una candidata y discriminan entre candidatas pueden entrar individualmente a la fusión. No todos los laterales llegan a H ni todos los que se ejecutan discriminan.
10. Una pasada de resolución puede agregar dimensiones micro/meso/macro y recalcular el ranking.
11. SET 021 selecciona un conjunto por cobertura de evidencia. El módulo de hipótesis abiertas conserva sus miembros y puede agregar candidatas con al menos dos enlaces de trazabilidad geométrica.
12. Las hipótesis se agrupan en regímenes de trayectoria. La apuesta se produce después de formar el conjunto; no es obligatorio que el desenlace futuro sea una hipótesis individual.
13. El cierre y el runner pueden bloquear la decisión terminal o dejarla reanudable. El CEB registra flujo de ejecución; StinkBox mantiene un registro persistente de tokens/eventos, no una memoria epistemológica completa.

Esta cadena contiene dos restricciones tempranas diferentes: el cuello de cinco tokens de entrada por eje/corte y el top-3 de familias por tablero/corte. El conjunto abierto posterior es variable, pero su universo de partida no equivale a las 244 familias completas. La expresión universo_candidatas_completo se refiere al universo de candidatas observadas por el predictor, no a todas las familias del catálogo.

## 4. Matriz de transposición operativa

| Operación de U6 | Antecedente más próximo | Qué conserva | Qué transpone U6 | Límite / diferencia |
|---|---|---|---|---|
| Actualización binaria de apoyo por patrón | Bayes binario; actualización de creencias | Forma reconocible de condicionamiento con likelihood | Usa pesos de tokens como likelihood de una familia estructural, no como observación de una variable aleatoria de un modelo causal completo | No es red bayesiana ni posterior calibrada de un desenlace |
| Masa residual hacia 0.5 y mezcla de indeterminación/azar | Modelos de incertidumbre y mezcla probabilística | La operación de mezcla y el margen de indeterminación | Inserta un piso de desconocimiento en la puntuación de cada patrón y combina el resultado con un término aleatorio local | La salida no hereda automáticamente la semántica de una probabilidad posterior estándar; Monte Carlo estima P_azar, no futuros completos |
| Biblioteca de 244 familias | Sistemas basados en conocimiento, ontologías, reglas y repertorios de patrones | Conocimiento previo explícito, no aprendido desde cero durante la corrida | Convierte marcos de procedencias heterogéneas en familias comparables bajo el mismo formato de puntuación P/A/C | No prueba equivalencia teórica entre los marcos ni activación semántica por pregunta; get_patterns_for_question devuelve todas las familias |
| Tres tableros P/A/C y R732 | Representaciones multivariadas y análisis de series temporales | Vectores, diferencias, normas, cosenos y medidas de cambio | Define un espacio de puntuaciones de patrones con tres perspectivas interpretativas y calcula su evolución longitudinal | El espacio es abstracto y depende de la preparación P/A/C; no representa coordenadas físicas ni la realidad sin mediación |
| Geometría multiescala aplicada a puntuaciones | Análisis geométrico y dinámico de series | PCA/SVD, mínimos cuadrados, distancia, curvatura/desplazamiento, permutaciones y ajuste descriptivo | Utiliza diagnósticos geométricos para caracterizar trayectorias de familias y, en algunos caminos, aportar señales o enlaces para el ranking y la selección de hipótesis | Los diagnósticos no demuestran causalidad ni validez física; su aporte predictivo requiere ablación emparejada |
| Fusión de dimensiones mediante rangos fraccionales | Agregación ordinal, Borda/rank aggregation y decisión multicriterio | Comparación relativa de alternativas por varios criterios | Construye una fusión dinámica: solo dimensiones numéricas, variables y no duplicadas; empates comparten rango; laterales discriminantes se agregan por separado; resolución puede añadir una segunda pasada | El score depende del universo de candidatas y de las dimensiones activas. No es una probabilidad ni es necesariamente comparable entre casos |
| SET 021 por cobertura | Set cover, selección de explicaciones y cobertura de evidencia | Selección de subconjuntos que cubren elementos relevantes | Usa tokens/cortes explicados y cobertura marginal para formar un conjunto con umbral 0.90 y roles de eje/componentes | El rótulo «necesario y suficiente» no es una demostración lógica formal; depende del universo de candidatas que llegó al módulo |
| Hipótesis abiertas y escenarios por régimen | ATMS, ABA, DeLP, MHT y sistemas de escenarios | Mantener alternativas, tratar evidencia temporal y no reducir todo a una única salida | La cardinalidad de hipótesis varía; se conserva el set 021 y se agregan complementarias por enlaces geométricos; después se agrupan por régimen micro/meso/macro | No implementa la semántica formal de ATMS/ABA/DeLP ni la asociación de objetivos de MHT. El set está condicionado por los filtros previos |
| Contradicción contextual | TMS/ATMS, argumentación y lógicas tolerantes a inconsistencias | No tratar automáticamente toda evidencia contraria como borrado del dato favorable | El Engine registra marcadores favorables/contrarios y condiciones contextuales asociadas a contradicciones; laterales exploran transiciones y conjuntos de condiciones | No hay demostración de una lógica paraconsistente formal ni de una relación de ataque/derrota entre argumentos |
| Persistencia de tokens | Event sourcing, registros append-only y memoria de eventos | Conservación histórica, deduplicación y procedencia de eventos | StinkBox mantiene tokens, caso/corte/fuente, recurrencia, artefactos y hashes; no incorpora automáticamente tokens al catálogo | No conserva por sí sola toda observación original, toda interpretación P/A/C ni cada justificación de cada hipótesis |
| CEB de flujo | Data lineage, workflow provenance y auditoría de ejecución | Etapas, lecturas/escrituras, productores/consumidores, identidad y hashes de artefactos | Instrumenta diccionarios observables, etapas y flujo real del programa para detectar piezas mudas, cortocircuitos y fallos | La procedencia de ejecución no equivale a explicación semántica de por qué una observación apoya una hipótesis |
| FREEZE, compuertas y evaluación posterior | Separación train/test, evaluación prospectiva y control de procesos | Separación temporal entre predicción y revelado | Sella la entrada hasta Z, separa contraste post-H y futuro, y puede bloquear el cierre ante latencia/empate/fallos | El protocolo no demuestra por sí solo ausencia total de leakage; debe verificarse en cada runner y caso |

## 5. Qué antecedentes ya resolvieron partes importantes

### 5.1 TMS y ATMS: mantener razones, supuestos y alternativas

Doyle (1979) formalizó un sistema que registra las razones de las creencias y permite revisarlas cuando aparecen descubrimientos contradictorios. De Kleer (1986) amplió el enfoque mediante conjuntos de supuestos y contextos alternativos, con tratamiento explícito de inconsistencias y nogoods.

La coincidencia con U6 está en no tratar una conclusión como una etiqueta aislada y en conservar alternativas. La diferencia decisiva es formal: un ATMS mantiene etiquetas de justificación y conjuntos de supuestos bajo los que una conclusión se sostiene; U6, en el camino revisado, actualiza puntuaciones por familias, conserva evidencia favorable/contraria y selecciona candidatas. No se encontró una estructura equivalente de etiquetas ATMS, nogoods y propagación de justificaciones.

### 5.2 La combinación simbólico-numérica ya tiene antecedente directo

D'Ambrosio (1988) y, de manera especialmente clara, Laskey y Lehner (1989) conectaron ATMS con teoría de Dempster-Shafer. Laskey y Lehner demostraron una equivalencia formal entre redes de creencia Dempster-Shafer y un ATMS con cálculo de probabilidades sobre supuestos.

Por tanto, no sería defendible presentar como novedad la combinación general de estructuras simbólicas, alternativas y pesos numéricos. La posible diferencia de U6 está en qué objetos combina, qué transformaciones aplica, cómo introduce geometría temporal y cómo gobierna la autoridad de cada salida mediante contratos.

### 5.3 La temporalidad de mantenimiento de creencias también tiene antecedente

Lee, Park, Park y Kim (2000) propusieron una extensión temporal de ATMS que modifica etiquetas, propagación de conjunciones/disyunciones y manejo de nogoods para representar relaciones temporales.

Esto descarta una afirmación amplia del tipo «U6 inaugura el mantenimiento de hipótesis contradictorias a través del tiempo». La comparación útil pasa a ser más específica: ATMS temporal propaga dependencias lógicas temporales; U6 calcula trayectorias de puntuaciones de patrones, integra dimensiones ordinales y geométricas y produce conjuntos abiertos desde candidatas observadas.

### 5.4 Argumentación rebatible: coincidencia conceptual, no identidad de mecanismo

ABA y DeLP formalizan argumentos, supuestos, contrarios, ataques, derrotas y semánticas para determinar qué conjuntos de argumentos quedan justificados. U6 no implementa esa maquinaria formal en el camino revisado. Que conserve evidencia a favor y en contra no basta para llamarlo argumentación derrotables ni lógica paraconsistente.

La comparación sirve para delimitar el hueco: U6 tiene contradicción como señal y como condición contextual, pero todavía no representa una red explícita de argumentos con ataques, defensas y garantías de aceptación.

### 5.5 MHT: múltiples hipótesis, pero otro objeto

MHT mantiene hipótesis de asociación de mediciones/objetivos a través de múltiples escaneos o frames. U6 mantiene candidatas de familias estructurales a través de cortes temporales. Comparten la necesidad de no cerrar prematuramente una única alternativa, pero no comparten el objeto matemático ni el problema de asociación.

### 5.6 Truth Discovery: conflicto entre fuentes, no conflicto entre patrones

La literatura de Truth Discovery estudia observaciones contradictorias sobre objetos y estima hechos a partir de propiedades y confiabilidad de fuentes, incluyendo dependencia entre fuentes y evolución temporal. U6 no realiza ese problema tal como está definido: el peso y el estado de evidencia se asignan a tokens/familias del catálogo; no hay un modelo general de fiabilidad de cada fuente que estime qué observación externa es verdadera.

### 5.7 Procedencia: ejecución y justificación semántica son problemas distintos

La procedencia de datos estudia qué entradas y transformaciones producen una salida. CEB instrumenta una parte de ese problema a nivel de ejecución: etapas, claves leídas/escritas, productores, consumidores, identidad de artefactos y hashes. Pero todavía no es una prueba formal de que cada hipótesis se justifique semánticamente desde cada observación original.

StinkBox añade persistencia de eventos de tokens, no un registro completo de todos los datos, interpretaciones, hipótesis y dependencias epistémicas.

## 6. Propiedades arquitectónicas que sí emergen de la inspección

Estas propiedades están descritas como rasgos del sistema, no como afirmaciones de novedad mundial.

### P1. Transposición de operadores entre objetos distintos

U6 conserva operaciones reconocibles, pero cambia el objeto sobre el que trabajan. Bayes actualiza apoyo a familias de patrones; la geometría opera sobre puntuaciones P/A/C; el ranking agrega posiciones relativas de candidatas; el set-cover selecciona explicaciones sobre tokens/cortes.

El resultado es una cadena de operadores matemáticamente reconocibles con semánticas locales propias. El valor arquitectónico está en la composición, no en afirmar que las fórmulas originales se hayan descubierto de nuevo.

### P2. Representación común de marcos heterogéneos

Las 244 familias se someten a una estructura de puntuación común. Eso permite compararlas longitudinalmente sin afirmar que sus teorías de origen sean equivalentes.

Esta propiedad es fuerte como decisión de diseño. Su riesgo es la pérdida de semántica: dos familias pueden compartir formato numérico sin que sus conceptos, evidencia o escalas sean conmensurables. Se requiere estudiar sensibilidad a la composición del catálogo y la calidad desigual de las familias.

### P3. Perspectivas separadas con geometría conjunta

P, A y C conservan tableros separados y luego se concatenan en R732. La geometría conjunta puede caracterizar cambios de la representación completa y las diferencias entre ejes.

La operación no es equivalente a tener tres modelos independientes ni a un embedding semántico genérico. Es una geometría sobre puntuaciones de patrones previamente preparadas en tres perspectivas.

### P4. Ranking de dimensiones variables y laterales condicionados

La fusión no suma indiscriminadamente todo lo que producen los módulos. Selecciona dimensiones numéricas, excluye constantes y duplicadas, agrega rangos fraccionales y admite señales laterales solo cuando pueden mapearse a candidatas y discriminan entre ellas. La resolución puede agregar una segunda pasada.

Esta es una de las recomposiciones más específicas del código actual. También crea una dependencia del conjunto candidato y de las dimensiones activas. Hay que probar estabilidad del orden al variar el universo, el número de dimensiones, los empates y los laterales disponibles.

### P5. Hipótesis abiertas posteriores a un proceso de compresión

U6 no conserva 244 hipótesis hasta el final. Comprime primero tokens por el cuello top-5 y luego familias por top-3/umbral; el predictor trabaja sobre la unión de supervivientes. SET 021 y la capa abierta vuelven a ampliar/seleccionar ese universo, incluyendo complementarias por trazabilidad geométrica.

La propiedad real no es «explorar sin filtro todas las posibilidades», sino **construir un conjunto variable de hipótesis después de una reducción temprana de evidencia y candidatas**. Esa arquitectura de compresión y recuperación parcial merece ser analizada experimentalmente.

### P6. Contratos de autoridad entre etapas

Los contratos determinan qué objeto recibe cada etapa, qué transformaciones se permiten y qué resultados pueden influir en H, en la apuesta o solo en diagnósticos. Ejemplos:

- el LLM/persona prepara los tokens; el camino nativo procesa datos estructurados;
- Engine V5 y catálogo 244 están protegidos;
- R732 alimenta características geométricas, pero no decide H por sí solo;
- los laterales pueden sugerir o aportar señales, pero muchos tienen can_decide_H=False;
- post-H no reescribe H ni la apuesta sellada;
- el futuro se abre después del FREEZE;
- CEB registra ejecución, pero no certifica verdad semántica.

No es solo validación de esquema: es una distribución de autoridad computacional. La comparación académica debe distinguirla de los contratos de datos convencionales y de la procedencia de workflows.

### P7. Separación entre memoria de eventos, estado de ejecución e interpretación

StinkBox, CEB y los objetos de hipótesis resuelven problemas distintos. StinkBox conserva tokens/eventos; CEB registra flujo; el predictor produce candidatas; la capa abierta produce hipótesis. No deben confundirse en una memoria única.

Esta separación puede ser una virtud arquitectónica, pero deja abierta la integración de procedencia semántica completa entre observación, tokenización, actualización, ranking e hipótesis.

## 7. Correcciones a afirmaciones demasiado amplias de la comparación previa

Los documentos comparativos del 3 de noviembre son valiosos como mapa de genealogías, pero algunas frases deben acotarse al código:

| Formulación amplia | Corrección sustentada |
|---|---|
| «Sistema paraconsistente» | No está demostrada una semántica paraconsistente formal. Se conservan señales contrarias y condiciones contextuales, pero no se encontró una lógica formal con consecuencia no explosiva. |
| «Implementa DeLP/argumentación derrotable» | No. Hay parentesco en la gestión de evidencia conflictiva y alternativas; no se encontraron estructuras de argumentos, ataques, derrotas y semántica de aceptabilidad equivalentes. |
| «Motor posterior determinista» | No en sentido estricto: el Engine incluye P_azar y Monte Carlo. Hay decisiones y desempates deterministas en partes del pipeline, pero el sistema completo no es determinista por definición. |
| «Memoria append-only de la evidencia» | StinkBox conserva eventos de tokens de forma persistente y deduplicada. No es un historial completo e inmutable de toda observación, interpretación y justificación. |
| «Explora el conjunto abierto de 244 familias» | No en el camino actual: las 244 se puntúan, pero el predictor recibe la unión de candidatas que pasan top-3/0.65 por eje/corte. |
| «Todos los tokens entran al cálculo canónico» | No: todos permanecen en el input y se registran, pero CUELLO_K=5 limita los tokens que pasan al Engine por eje/corte. |
| «La geometría gobierna la hipótesis» | Algunas dimensiones geométricas entran al ranking y los enlaces geométricos pueden añadir complementarias; no está probado que la geometría mejore la predicción. |
| «Trazabilidad completa» | CEB da trazabilidad de ejecución y flujo; StinkBox da procedencia de eventos de tokens. No equivalen a una justificación semántica completa desde fuente hasta hipótesis. |

## 8. Dónde puede estar una contribución defendible

La afirmación prudente es que U6 presenta una **recomposición operativa específica de métodos heterogéneos bajo contratos de autoridad y transformación**, con estas características verificadas:

- entrada estructurada por cortes y tres perspectivas P/A/C;
- actualización de apoyo por patrón con incertidumbre residual;
- geometría sobre la trayectoria de puntuaciones;
- filtros tempranos explícitos;
- fusión ordinal dinámica de características y señales laterales;
- selección de conjuntos por cobertura;
- hipótesis de cardinalidad variable con complementarias por trazabilidad;
- agrupación de escenarios por régimen;
- FREEZE y compuertas de cierre;
- instrumentación de ejecución y memoria persistente de tokens.

No se ha demostrado que esa combinación sea inédita mundialmente. Sí se ha identificado una configuración concreta que no queda descrita adecuadamente por una sola etiqueta como ATMS, DeLP, MHT, Truth Discovery, sistema bayesiano o análisis de series.

La contribución que podría defenderse no sería «una nueva matemática» ni «un nuevo tipo de inferencia» por declaración. Sería una contribución de arquitectura e integración, si se demuestra que sus contratos y recomposiciones producen un efecto que los antecedentes y baselines no obtienen.

## 9. Pruebas que pueden confirmar o refutar esa contribución

Prioridad por capacidad discriminante:

1. **Ablación del cuello top-5 y del top-3/0.65.** Comparar la cadena actual con retención más amplia, sin borrar los datos originales. Medir candidatas recuperadas, cambios de hipótesis y desenlaces.
2. **Ablación del ranking.** Mantener exactamente los mismos casos y candidatas; retirar por separado geometría, laterales, dimensiones de resolución y balance por grupos. Medir cambios de orden, cobertura, estabilidad y acierto.
3. **Prueba de dependencia del universo.** Añadir/quitar candidatas irrelevantes y medir rank reversal. La fusión ordinal puede cambiar cuando cambia el conjunto de comparación.
4. **Prueba de conmensurabilidad del catálogo.** Medir si familias de procedencias distintas producen puntuaciones comparables y si la composición/estado de evidencia del catálogo altera el ranking.
5. **Prueba de contradicción contextual.** Diseñar pares de casos idénticos salvo por la condición asociada a la contradicción. Verificar si el sistema preserva y usa esa condición, en vez de limitarse a reducir la puntuación.
6. **Prueba de procedencia semántica.** Elegir una hipótesis y reconstruir todos los datos fuente, tokens, cortes, ejes, puntuaciones, dimensiones de ranking y módulos que contribuyeron. Identificar cada pérdida de enlace.
7. **Prueba de contratos y autoridad.** Inyectar salidas de laterales no autorizados, constantes, duplicadas, vacías o con nombres ambiguos; verificar que no alteren H indebidamente.
8. **Benchmark de antecedentes.** Implementar baselines reproducibles y comparar sobre los mismos freezes: agregación simple de patrones, baseline temporal, set-cover sin geometría, ranking sin laterales y una formulación argumentativa/ATMS simplificada cuando el problema pueda traducirse sin deformarlo.

La métrica no debe limitarse a top-1. Incluir cobertura del conjunto, tamaño del conjunto, falsos positivos, Brier/log-loss/ECE cuando exista una probabilidad calibrada, estabilidad bajo perturbaciones, trazabilidad y coste computacional.

## 10. Dictamen

**Lo más distintivo que se puede sostener hoy no es una fórmula nueva, sino una composición de operaciones que cambia la función de métodos conocidos al insertarlos en una arquitectura longitudinal con tres perspectivas, filtros, geometría, ranking ordinal, selección por cobertura, hipótesis variables y contratos de autoridad.**

Los antecedentes ya contienen mantenimiento de creencias, alternativas, combinación simbólico-numérica, temporalidad, argumentación, geometría, procedencia y seguimiento de hipótesis. Por eso no se puede atribuir novedad a esos ingredientes individualmente.

Lo que queda abierto y merece una investigación propia es si la composición de U6 —en especial la relación entre contratos, fusión ordinal dinámica, geometría y conservación de hipótesis después de los filtros— produce una capacidad verificable que no se obtiene con las piezas por separado o con un baseline más sencillo.

La respuesta requiere ablaciones y comparaciones emparejadas. La arquitectura está inspeccionada; la contribución empírica de su recomposición sigue pendiente de demostración.

## 11. Fuentes principales

### Mantenimiento de creencias, alternativas y argumentación
- Doyle, J. (1979). “A Truth Maintenance System”. Artificial Intelligence, 12(3), 231–272. https://doi.org/10.1016/0004-3702(79)90008-0
- de Kleer, J. (1986). “An assumption-based TMS”. Artificial Intelligence, 28(2), 127–162. https://doi.org/10.1016/0004-3702(86)90080-9
- D’Ambrosio, B. (1988). “A hybrid approach to reasoning under uncertainty”. International Journal of Approximate Reasoning, 2, 29–45. https://doi.org/10.1016/0888-613X(88)90004-7
- Laskey, K. B. & Lehner, P. E. (1989). “Assumptions, beliefs and probabilities”. Artificial Intelligence, 41(1), 65–77. https://doi.org/10.1016/0004-3702(89)90078-7
- Provan, G. (1989). “An Analysis of ATMS-Based Techniques for Computing Dempster-Shafer Belief Functions”. IJCAI. https://ijcai.org/proceedings/1989/179
- Lee, M. S., Park, Y. G., Park, C. & Kim, J. (2000). “A Temporal Data Maintenance Method in an ATMS”. IEICE Transactions on Information, E83-D(2), 295–298. https://globals.ieice.org/en_transactions/information/10.1587/e83-d_2_295/_p
- Toni, F. (2014). “A tutorial on assumption-based argumentation”. Argument & Computation, 5(1). https://doi.org/10.1080/19462166.2013.869878
- Pardo, P. & Godo, L. (2013). “t-DeLP: a temporal extension of the defeasible logic programming argumentative framework”. Annals of Mathematics and Artificial Intelligence, 69. https://doi.org/10.1007/s10472-013-9334-1

### Hipótesis, fuentes, grafos temporales y procedencia
- Chong, C.-Y., Mori, S. & Reid, D. B. (2019). “Forty Years of Multiple Hypothesis Tracking”. Journal of Advances in Information Fusion, 14(2), 131–151. https://isif.org/media/forty-years-multiple-hypothesis-tracking
- Wang, S. et al. (2025). “A Survey on Truth Discovery: Concepts, Methods, Applications, and Opportunities”. IEEE Transactions on Big Data, 11(2), 314–332. https://doi.org/10.1109/TBDATA.2024.3423677
- Liu, X. et al. (2024). “Overview of knowledge reasoning for knowledge graph”. Neurocomputing, 585, 127571. https://doi.org/10.1016/j.neucom.2024.127571
- Chapman, A., Lauro, L., Missier, P. & Torlone, R. (2024). “Supporting Better Insights of Data Science Pipelines with Fine-grained Provenance”. ACM Transactions on Database Systems, 49(2), Article 6. https://doi.org/10.1145/3644385
- Jiang, L., Liao, H. & De Baets, B. (2024). “A simulation study on the probabilities of rank reversal, tie making, and tie breaking for multiple criteria decision making methods”. Omega, 125, 103033. https://doi.org/10.1016/j.omega.2023.103033
- “A Survey of Knowledge Graph Reasoning on Graph Types: Static, Dynamic, and Multi-Modal” (2024). IEEE Transactions on Pattern Analysis and Machine Intelligence, 46(12), 9456–9478. https://doi.org/10.1109/TPAMI.2024.3417451
- “From data fusion to dynamic reasoning: A survey on spatio-temporal knowledge graph construction and embedding methods” (2025). Neurocomputing, 658, 131590. https://doi.org/10.1016/j.neucom.2025.131590

## 12. Límite de esta revisión

Esta es una comparación técnica focalizada, no una revisión sistemática registrada ni una búsqueda exhaustiva de patentes. Las coincidencias se han establecido por mecanismos y contratos inspeccionados; la ausencia de un antecedente idéntico en esta búsqueda no demuestra inexistencia mundial. No se ejecutaron ablaciones ni un benchmark nuevo en esta intervención.
