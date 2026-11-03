# Genealogía técnica, continuaciones y huecos reales de U6

Fecha: 2026-11-03  
Ámbito: contraste de U6/V15.3 con líneas de investigación anteriores y revisión directa del código disponible en `main`.  
Regla: similitud no equivale a identidad formal; ejecución documentada no equivale a validación predictiva.

## Veredicto ejecutivo

**No existe una sola línea histórica que alguien haya iniciado y luego abandonado exactamente donde empieza U6. Hay varias genealogías que se separaron y resolvieron partes distintas del problema.** La revisión encuentra, sin embargo, antecedentes mucho más cercanos que una simple coincidencia de vocabulario:

1. Doyle (1979) creó un mecanismo que registra justificaciones y revisa creencias cuando aparecen contradicciones.
2. De Kleer (1986) amplió el enfoque a conjuntos de supuestos, información inconsistente y exploración simultánea de varias soluciones.
3. D'Ambrosio (1988), Laskey y Lehner (1989), y Provan (1989) combinaron ATMS con Dempster-Shafer: integración simbólica-numérica, gestión de dependencias y cálculo de incertidumbre. **Esto anticipa directamente la idea general de combinar alternativas justificadas con soporte numérico.**
4. Lee, Park, Park y Kim (2000) señalaron una carencia explícita del ATMS: no manejaba correctamente datos y relaciones temporales. Propusieron una extensión temporal modificando etiquetas, propagación y manejo de contradicciones.
5. En otra rama, DeLP (2004) y sus extensiones temporales t-DeLP (2011/2013), l-DeLP (2012) y pt-DeLP (2012) desarrollaron argumentos rebatibles sobre procesos que cambian y persisten en el tiempo, añadiendo después pesos de incertidumbre.
6. En ramas paralelas, AGM y la revisión iterada formalizaron cómo cambia un estado de creencias; la procedencia de datos formalizó cómo rastrear qué datos y transformaciones produjeron un resultado; y la narratología computacional modeló estructuras y evolución de relatos.

**Por tanto, no sería correcto decir que U6 inventó la revisión de creencias, el conjunto abierto de alternativas, la combinación simbólico-numérica, la temporalidad o la trazabilidad. Tampoco es correcto reducirlo a “alguien ya hizo lo mismo”.** Los antecedentes resuelven subproblemas con representaciones, semánticas y objetivos distintos. El hueco potencial está en la integración operativa de: observaciones longitudinales por cortes; estados positivos, negativos, ausentes y contradictorios; hipótesis abiertas; trayectorias multiescala; memoria histórica de tokens/eventos; procedencia de ejecución; y una compuerta que impida cerrar cuando faltan condiciones. Esa integración concreta todavía no está demostrada como inédita ni como superior.

## 1. Genealogía A: mantener razones, contradicciones y alternativas

### 1979 — Doyle: Truth Maintenance System (TMS)

Jon Doyle, “A Truth Maintenance System”, *Artificial Intelligence* 12 (1979), 231–272. DOI: https://doi.org/10.1016/0004-3702(79)90008-0

Problema que resolvió: un programa de razonamiento necesita poder asumir cosas, registrar por qué cree algo y revisar esas creencias cuando un descubrimiento contradice una suposición. El TMS mantiene las razones/dependencias y permite explicar decisiones y hacer retroceso dirigido por dependencias.

Límite que dejó: el TMS es un subsistema de mantenimiento de razones; no es por sí mismo una teoría completa de cómo decidir racionalmente entre todas las revisiones posibles. La elección de qué suposición retirar depende de la arquitectura de resolución que lo utiliza.

### 1986 — De Kleer: ATMS

Johan de Kleer, “An assumption-based TMS”, *Artificial Intelligence* 28 (1986), 127–162. DOI: https://doi.org/10.1016/0004-3702(86)90080-9

Qué añadió: en vez de manipular únicamente justificaciones activas, conserva conjuntos de supuestos bajo los que una conclusión se sostiene. Permite trabajar con información inconsistente, cambiar de contexto y explorar varias soluciones potenciales en paralelo. Es un antecedente directo de la idea de no forzar una única hipótesis demasiado pronto.

La misma entrega histórica incluye dos trabajos complementarios de De Kleer:
- “Extending the ATMS”, pp. 163–196, DOI: https://doi.org/10.1016/0004-3702(86)90081-0: amplía el tratamiento de defaults y disyunciones.
- “Problem solving with the ATMS”, pp. 197–224, DOI: https://doi.org/10.1016/0004-3702(86)90082-2: explica la interfaz necesaria entre el ATMS y el solucionador que lo utiliza.

### 1988–1989 — el límite computacional y la fusión simbólico-numérica

Esta es la parte que no se puede omitir al comparar U6.

- Gregory Provan, “The Computational Complexity of Assumption-Based Truth Maintenance Systems”, UBC Technical Report TR-88-11 (1988): calcular soportes mínimos puede ser exponencial en el número de supuestos; generar expresiones mínimas es NP-hard. El coste de etiquetas puede hacer inviable el enfoque en problemas medianos sin reestructuración.
- Bruce D’Ambrosio, “A hybrid approach to reasoning under uncertainty”, *International Journal of Approximate Reasoning* 2 (1988), 29–45. DOI: https://doi.org/10.1016/0888-613X(88)90004-7. Combina técnicas simbólicas ATMS con métodos numéricos Dempster-Shafer.
- Kathryn Blackmond Laskey y Paul E. Lehner, “Assumptions, beliefs and probabilities”, *Artificial Intelligence* 41 (1989), 65–77. DOI: https://doi.org/10.1016/0004-3702(89)90078-7. Demuestran una equivalencia formal entre redes de creencia Dempster-Shafer y ATMS con cálculo de probabilidades sobre supuestos; abordan dependencias y conflictos.
- Provan, “An Analysis of ATMS-Based Techniques for Computing Dempster-Shafer Belief Functions”, IJCAI 1989, pp. 1115–1119: estudia la complejidad del híbrido y propone aproximaciones porque el cálculo exacto puede ser intratable.

**Conclusión de esta secuencia:** la unión de razonamiento simbólico, alternativas justificadas y soporte numérico ya estaba desarrollada formalmente en 1988–1989. No es novedad intrínseca de U6. El problema que aquella línea identificó con claridad fue la escalabilidad/complejidad.

### 1990–1993 — formalización y relación con AGM

- Kean y Tsiknis, “Assumption Based Reasoning and Clause Management Systems”, UBC TR-90-09 (1990), formalizan el razonamiento basado en supuestos.
- Dixon y Foo, “Connections Between the ATMS and AGM Belief Revision”, IJCAI 1993, pp. 534–538, muestran cómo simular comportamiento ATMS mediante AGM y ordenamientos de atrincheramiento epistémico.

Esto confirma que TMS/ATMS no fue una ocurrencia aislada: tuvo una continuación formal hacia teoría de revisión de creencias y razonamiento basado en supuestos.

## 2. Genealogía B: incorporar tiempo al mantenimiento de creencias

### El antecedente directo que cambia la comparación — 2000

Min Suk Lee, Yeung Gyu Park, Choong Shik Park y Jaihie Kim, “A Temporal Data Maintenance Method in an ATMS”, *IEICE Transactions on Information and Systems* E83-D(2), 295–298 (2000). Registro editorial: https://globals.ieice.org/en_transactions/information/10.1587/e83-d_2_295/_p

Este trabajo dice explícitamente que el ATMS convencional no tenía mecanismo para manejar datos temporales ni relaciones temporales de eventos. Propone extenderlo para mantener información que cambia a lo largo del tiempo, modificando:
- la representación de etiquetas;
- la simplificación de conjunciones y disyunciones durante la propagación;
- el manejo de nogoods/contradicciones.

Esto es mucho más cercano a la pregunta de U6 que citar únicamente Doyle. La idea “mantenimiento de creencias + contradicciones + evolución temporal” ya fue formulada e implementada como extensión de ATMS en 2000.

**¿Quién continuó exactamente ese artículo?** En las búsquedas bibliográficas realizadas no apareció una cadena de citas extensa y verificable que permita afirmar que ese artículo concreto originó una familia sostenida de sistemas posteriores. Eso no demuestra que nadie lo haya citado o continuado; significa que no hay evidencia suficiente para declarar una continuidad directa. La investigación posterior sí continuó el problema por otras ramas, especialmente revisión temporal de creencias, argumentación temporal y monitoreo temporal de estados de creencia.

### 2002–2011 — revisión temporal y extrapolación de creencias

- Cobo y Falappa, “Revisión temporal: algunos postulados” (2004), señalan que la información temporal no había sido tratada suficientemente en muchos formalismos de revisión de creencias.
- Bonanno, “Axiomatic characterization of the AGM theory of belief revision in a temporal logic”, *Artificial Intelligence* 171 (2007), 144–160. DOI: https://doi.org/10.1016/j.artint.2006.12.001. Formaliza postulados AGM en lógica temporal de ramificación.
- Dupin de Saint-Cyr y Lang, “Belief extrapolation (or how to reason about observations and unpredicted change)”, *Artificial Intelligence* 175 (2011), 760–790. DOI: https://doi.org/10.1016/j.artint.2010.11.002. Trabaja con observaciones en distintos momentos y trata la extrapolación como una forma de revisión de creencias con marcas temporales.

La línea, por tanto, no se detuvo en el artículo de 2000: el problema siguió, aunque no necesariamente bajo la etiqueta ATMS.

## 3. Genealogía C: argumentos rebatibles que evolucionan en el tiempo

Esta es otra continuación importante porque trata evidencia a favor y en contra, conclusiones derrotables y procesos temporales.

- García y Simari, “Defeasible logic programming: an argumentative approach”, *Theory and Practice of Logic Programming* 4 (2004), 95–138. DOI: https://doi.org/10.1017/S1471068403001674. DeLP construye argumentos a favor y en contra de una conclusión; una conclusión se acepta si el argumento queda sin derrotar tras el análisis dialéctico.
- Pardo y Godo, “t-DeLP: a temporal extension of the defeasible logic programming argumentative framework” (trabajo de 2011; versión de revista en *Annals of Mathematics and Artificial Intelligence* 69, 2013). DOI: https://doi.org/10.1007/s10472-013-9334-1. Añade parámetros temporales a hechos y reglas durativas para razonar sobre procesos, persistencia y estados futuros.
- “An approach for Temporal Argumentation Using Labeled Defeasible Logic Programming (l-DeLP)” (2012): añade intervalos de disponibilidad temporal para cláusulas y argumentos.
- Godo, Marchioni y Pardo, “Extending a Temporal Defeasible Argumentation Framework with Possibilistic Weights” (2012): identifica que t-DeLP no ordenaba reglas temporales por preferencia o certeza y añade pesos de posibilidad.

**Qué resolvieron:** argumentos derrotables, contradicción, tiempo, persistencia y grados cualitativos de incertidumbre.

**Qué no resuelven por sí mismos:** no equivalen a una memoria operacional append-only de cada observación original; tampoco son análisis geométrico multiescala de trayectorias P/A/C. Su objeto formal es la aceptabilidad de argumentos bajo reglas y ataques.

## 4. Genealogía D: procedencia y linaje de datos

Esta familia no empezó en TMS. Se desarrolló principalmente en bases de datos, workflows científicos y auditoría.

- La procedencia en bases de datos distingue, entre otras cosas, *why-provenance* (qué entradas justifican un resultado), *how-provenance* (qué operaciones lo produjeron) y *where-provenance* (de qué ubicación/atributo procede).
- Cheney, Chiticariu y Tan, “Provenance in Databases: Why, How, and Where”, *Foundations and Trends in Databases* 1(4) (2009), pp. 379–474. DOI: https://doi.org/10.1561/1900000006.
- “A Primer on Provenance” (2014) explica el problema de reconstruir desde un resultado las condiciones, parámetros y transformaciones que lo produjeron.
- Pan, Stakhanova y Ray, “Data Provenance in Security and Privacy”, *ACM Computing Surveys* 55 (2023), DOI: https://doi.org/10.1145/3593294, revisa procedencia para análisis histórico, atribución y auditoría.

**Hueco histórico entre familias:** un sistema puede saber de dónde vino un dato y qué transformación lo procesó sin tener una teoría de cómo revisar una hipótesis contradictoria. A la inversa, un TMS puede saber por qué sostiene una conclusión sin ser un almacén completo e inmutable de todos los eventos originales. Son problemas relacionados, pero distintos.

## 5. Genealogía E: narrativas y trayectorias

- Pérez y Pérez y Sharples, “MEXICA: A computer model of a cognitive account of creative writing”, *Journal of Experimental & Theoretical Artificial Intelligence* 13 (2001), 119–139. DOI: https://doi.org/10.1080/09528130010029820.
- MEXICA utiliza una dinámica de engagement/reflection para construir y revisar historias; MINSTREL, BRUTUS y otros sistemas representan otras líneas de generación narrativa.
- Montfort y Pérez y Pérez, “Computational Models for Understanding Narrative” (2023), DOI: https://doi.org/10.34619/gnzq-r7ri, revisan MEXICA y Curveship y explican cómo los modelos computacionales pueden servir para investigar procesos narrativos. Distinguen estos modelos de los LLM.

Estos antecedentes trabajan con estructura, conflicto, relaciones y evolución de relatos. No son equivalentes a un motor que toma cortes temporales de evidencia sobre una trayectoria biográfica y genera hipótesis contrastables.

## 6. Geometría multiescala y trayectorias: otra rama, no una invención aislada

La geometría de trayectorias, análisis multiescala, persistencia, segmentación temporal y análisis de series son campos extensos. La geometría por sí sola no constituye una novedad. En 2025–2026 hay, por ejemplo, revisiones de análisis topológico de series temporales y de aprendizaje no supervisado de estados en series multivariadas.

La diferencia importante es de función:
- en análisis de series, la geometría puede describir estados, transiciones, persistencia o anomalías;
- en un sistema de mantenimiento de creencias, la evidencia geométrica tendría que modificar o justificar una revisión de hipótesis;
- en U6, hay una conexión explícita entre diagnósticos geométricos, enlaces de trazabilidad y selección de hipótesis complementarias. Esa conexión debe probarse por ablación; no basta con que el módulo geométrico se ejecute.

## 7. Auditoría del código U6: qué está y qué no está

### 7.1 Temporalidad de observaciones: existe, pero es parcial y lateral

Archivo: `motor/motor/sidecar_trazabilidad_temporal.py`.

El módulo registra por token:
- primera y última aparición;
- cortes en los que aparece;
- ejes P/A/C en que aparece;
- estado ON, PARPADEO, NO_APARECIDO_AUN u OFF;
- intervalos entre apariciones con una señal de recuperación.

Pero su propio encabezado declara:
- “La capa registra observaciones temporales”.
- “No decide H1/H2, no suma evidencia, no clasifica falacias”.
- `estado: CABLEADO_BUS_LATERAL`.

**Conclusión:** sí existe una capa temporal explícita, pero no equivale a una memoria universal de toda observación ni a un mecanismo de revisión de hipótesis. Registra principalmente la aparición/ausencia temporal de tokens conocidos u observados. No prueba que todo dato positivo, negativo, ausente, contradictorio, meseta, valle y anomalía viaje por esa misma ruta.

### 7.2 Hipótesis abiertas: existe en el motor de trabajo

Archivo: `motor/motor/hipotesis_trayectoria_abierta_v1.py`.

El código:
- no fija un máximo de hipótesis;
- conserva el conjunto necesario/suficiente 021;
- puede incorporar candidatos complementarios con dos o más enlaces explícitos de trazabilidad geométrica;
- diferencia hipótesis primarias, complementarias y alternativas del universo observado;
- calcula regímenes de trayectoria micro/meso/macro;
- declara expresamente que el soporte relativo no es probabilidad.

Esto es una implementación real de cardinalidad variable. Sin embargo, el ATMS ya exploraba múltiples soluciones potenciales; la cardinalidad abierta no es nueva por sí misma.

### 7.3 Geometría: se calcula, pero el propio código limita su interpretación

Archivos:
- `motor/motor/geometria_multicapa/v153_convergencia_multinivel_v0_3.py`
- `motor/motor/geometria_multicapa/adaptador_convergencia_real_v1.py`
- `motor/motor/geometria_multicapa/teseracto_recursivo_geometria_v0_4.py`

La geometría opera sobre P/A/C como coordenadas abstractas de puntuación, no como espacio físico. Hay comparaciones de trayectorias, PCA, ajuste helicoidal descriptivo, jerarquía Ward y controles nulos por permutación temporal. Los propios módulos advierten que:
- un ajuste helicoidal es descriptivo;
- la jerarquía es inferida, no ontología nativa;
- pocas observaciones hacen ambigua la fase;
- una coincidencia proyectada puede ser falso positivo;
- la geometría no demuestra por sí misma causalidad ni capacidad predictiva.

**Conclusión:** la geometría está implementada como análisis exploratorio y algunos resultados alimentan enlaces de trazabilidad. No está demostrado que mejore la selección de hipótesis o el pronóstico.

### 7.4 Trazabilidad de ejecución: CEB es más que un manifiesto, pero menos que trazabilidad semántica total

Archivo: `motor/motor/ceb_runtime_v0_6_flow.py`.

CEB instrumenta:
- etapas de ejecución;
- lecturas y escrituras de claves sobre diccionarios observables;
- productores y consumidores de objetos;
- identidad de artefactos ejecutables mediante hashes;
- eventos de flujo, advertencias, errores y salidas;
- auditoría de componentes declarados como ejecutados pero no observados.

Esto sí permite reconstruir parte del flujo operacional de una corrida y detectar componentes que se ejecutaron pero no alimentaron a nadie.

No demuestra todavía que cada conclusión esté enlazada, a nivel semántico, con cada observación fuente que la justifica. Las aristas por identidad de objeto, clave leída y ruta de archivo no son automáticamente una explicación lógica de la inferencia.

### 7.5 StinkBox: memoria append-only de tokens, no de toda la epistemología

Archivos: `motor/stinkbox_registry.py` y `motor/STINKBOX_CONTRATO_PERSISTENCIA.md`.

El registro conserva tokens, forma original, caso, corte, fuente, tipo de evento, fecha, recurrencia, estado de revisión y SHA del artefacto. Evita borrar tokens descartados y evita incorporarlos automáticamente al catálogo canónico.

Esto sí constituye persistencia histórica de esa clase de eventos. No es una memoria completa de cada dato de entrada, cada vector P/A/C, cada hipótesis, cada relación causal y cada decisión revisada.

### 7.6 Compuerta de cierre: existe y tiene una limitación de validación reconocida

Archivo: `motor/correr_estandar.py`; informe: `motor/INFORME_IMPLEMENTACION_CONTINUIDAD_TORTUGAS_20261024.md`.

La compuerta puede marcar la corrida como PAUSADA_REANUDABLE, conservar hipótesis provisionales y negar autorización de decisión final cuando hay latencia, empate o fallo de una etapa requerida.

La documentación reconoce que el camino real de reanudación después de un fallo de TORTUGAS todavía necesitaba una prueba de integración que provocara el fallo y verificara la reapertura. Además, la reanudación vuelve a ejecutar la entrada sellada completa; no debe describirse como reanudación incremental desde el último corte sin más.

### 7.7 Una corrida real no equivale a validación predictiva

El registro `motor/audit/CORRIDA_REAL_HIPOTESIS_ABIERTAS_20261020.json` documenta tres cortes, cuatro hipótesis, geometría ejecutada, Monte Carlo y un resultado de continuidad de conjunto T+1. Dos de las tres hipótesis selladas reaparecieron en la evidencia retenida. El propio informe aclara que esto no es calibración ni acierto del desenlace futuro.

Por tanto:
- **Sí:** el pipeline ejecutó y produjo hipótesis/diagnósticos con trazas.
- **No:** esa corrida no demuestra que la geometría mejore el pronóstico, ni que las hipótesis tengan probabilidades calibradas, ni que U6 supere a los antecedentes.

## 8. Dónde está el hueco real que merece investigación

La oportunidad no consiste en volver a inventar ATMS, DeLP, revisión temporal o procedencia. Consiste en formular y probar una arquitectura que cierre las brechas entre esas familias:

1. **Registro histórico inmutable de observaciones:** guardar cada dato original, fuente, corte, fecha, estado de medición y hash. No confundir ausencia de dato con evidencia negativa.
2. **Interpretaciones versionadas:** almacenar por separado qué hipótesis se sostuvo en cada corte y con qué evidencia, sin reescribir retrospectivamente el pasado.
3. **Dependencias inferenciales explícitas:** cada hipótesis debe tener enlaces a las observaciones concretas que la apoyan, contradicen, debilitan o dejan indeterminada.
4. **Revisión no destructiva:** cuando cambia la interpretación, preservar tanto el estado anterior como el nuevo y explicar qué evidencia provocó el cambio.
5. **Temporalidad real:** distinguir tiempo del hecho, tiempo de observación, tiempo de incorporación y tiempo de revisión.
6. **Geometría con efecto demostrable:** medir si micro/meso/macro, curvatura, persistencia e inercia mejoran selección o predicción frente a quitar esos módulos.
7. **Control de cierre:** no producir decisión terminal cuando falta evidencia, procedencia o una etapa necesaria; comprobar la reanudación bajo fallos reales.
8. **Pruebas de fuga temporal:** congelar cortes y demostrar que ninguna hipótesis usa información posterior al corte.
9. **Escalabilidad:** comparar coste de mantener todas las alternativas y trazas frente a ATMS/ABA/DeLP y baselines temporales.
10. **Prueba comparativa de integración:** ejecutar sobre los mismos casos un ATMS/ABA o aproximación reproducible, un modelo de revisión temporal, un baseline probabilístico y U6; aplicar ablaciones por módulo.

### Qué resultado convertiría la integración en contribución defendible

No basta con que U6 tenga más componentes. Tiene que demostrar al menos una diferencia observable:
- recupera una hipótesis que un baseline elimina prematuramente y esa hipótesis resulta correcta;
- evita una conclusión falsa porque conserva una contradicción o una ausencia;
- cambia una decisión al detectar una trayectoria multiescala que el baseline no representa;
- reconstruye exactamente qué observaciones y transformaciones produjeron una hipótesis;
- reanuda sin pérdida ni contaminación temporal tras una interrupción;
- mejora cobertura/calibración/estabilidad a coste aceptable.

Si no ocurre ninguna de esas cosas, la integración puede seguir siendo una implementación útil, pero no una mejora técnica demostrada.

## 9. Qué se puede afirmar hoy, sin inflar ni minimizar

| Pregunta | Resultado |
|---|---|
| ¿Alguien hizo mantenimiento de razones y revisión de creencias antes? | Sí: Doyle, 1979. |
| ¿Alguien mantuvo conjuntos de supuestos y alternativas simultáneas? | Sí: ATMS, De Kleer, 1986. |
| ¿Alguien combinó razonamiento simbólico y numérico con alternativas justificadas? | Sí: ATMS + Dempster-Shafer, 1988–1989. |
| ¿Alguien incorporó tiempo al mantenimiento de creencias ATMS? | Sí: Lee et al., 2000. |
| ¿Alguien combinó argumentos derrotables, contradicción y temporalidad? | Sí: t-DeLP y extensiones, 2011–2013. |
| ¿Alguien estudió la evolución temporal de estados de creencia con incertidumbre en 2026? | Sí: Subjective LTL, AAAI Spring Symposium 2026. |
| ¿Alguien desarrolló procedencia/linaje de datos? | Sí: varias décadas de investigación en bases de datos y workflows. |
| ¿U6 tiene esos mecanismos individuales como piezas operativas? | Sí, varias piezas; con alcances distintos y algunas laterales/experimentales. |
| ¿U6 es formalmente un ATMS, DeLP, lógica paraconsistente o sistema de event sourcing? | No está demostrado. |
| ¿La combinación exacta de U6 está probada como inédita? | No. La búsqueda realizada no es una revisión sistemática mundial ni de patentes. |
| ¿Está demostrada la superioridad predictiva de U6? | No. |
| ¿Hay un hueco técnico real para probar? | Sí: integración verificable de procedencia de datos, historia de interpretaciones, revisión de hipótesis, temporalidad, geometría y cierre seguro. |

## 10. Fuentes adicionales de la continuación contemporánea

- Stanford Encyclopedia of Philosophy, “Logic of Belief Revision” (revisión sustantiva 2026): https://plato.stanford.edu/entries/logic-belief-revision/
- Pardo y Godo, t-DeLP (2013): https://doi.org/10.1007/s10472-013-9334-1
- Toni, “A tutorial on assumption-based argumentation” (2014): https://doi.org/10.1080/19462166.2013.869878
- Doutre y Mailly, “Constraints and changes: A survey of abstract argumentation dynamics” (2018): https://doi.org/10.3233/AAC-180425
- Schwind et al., “On Computational Aspects of Iterated Belief Change” (IJCAI 2020): https://doi.org/10.24963/ijcai.2020/245
- Herd, Kelly y Stolle, “Temporal Monitoring of Agent Beliefs Under Uncertainty with Subjective LTL” (AAAI Spring Symposium 2026): https://doi.org/10.1609/aaaiss.v8i1.42574
- Montfort y Pérez y Pérez, “Computational Models for Understanding Narrative” (2023): https://doi.org/10.34619/gnzq-r7ri
- Pan, Stakhanova y Ray, “Data Provenance in Security and Privacy” (2023): https://doi.org/10.1145/3593294
- Overlöper, Coelho y Niggemann, “Unsupervised state-learning for multivariate time series data: a survey and practical guidelines” (2026): https://doi.org/10.1007/s10462-026-11704-5

## Nota de alcance

Esta revisión es una genealogía comparativa focalizada, no un systematic review registrado ni una búsqueda exhaustiva de patentes. Las cadenas de continuidad se han trazado cuando hay documentos verificables. Cuando no se encontró una cadena directa de citas, se dice expresamente; no se convierte la ausencia de resultados de búsqueda en prueba de que una línea murió.
