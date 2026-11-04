# Reconstrucción funcional de U6: qué representa, cómo opera y qué no implementa

**Fecha:** 2026-11-04  
**Rama inspeccionada:** main  
**HEAD observado al iniciar la revisión:** d7bb1d7c087f56c8b8606f8cd32d8a9c10b2ebae  
**Alcance:** reconstrucción funcional del camino central ejecutable, sus contratos, la biblioteca de patrones, el conjunto de hipótesis, los módulos geométricos, la memoria/CEB y la línea conceptual MCT. No se ejecutó una corrida nueva ni se modificaron archivos canónicos.

## 1. Corrección de la pregunta

El nombre «motor» aparece en el repositorio y en nombres de archivos, pero no describe adecuadamente el conjunto. Para esta reconstrucción se usa **U6** como nombre del sistema y **Engine V5** únicamente para el componente canónico concreto.

La descripción funcional provisional más ajustada es:

> **U6 es una arquitectura computacional de análisis longitudinal de evidencia estructural: recibe observaciones ya interpretadas y organizadas en P/A/C, las compara contra una biblioteca heterogénea de patrones, construye trayectorias vectoriales, ordena candidatas mediante fusión de señales y conserva un conjunto variable de hipótesis y escenarios.**

No es, en el camino central revisado, un sistema que lea por sí solo la realidad en bruto, descubra los roles P/A/C, aprenda automáticamente una teoría de 244 patrones o simule causalmente el mundo futuro. Su frontera con la realidad está en la preparación de los datos: alguien o algún modelo convierte observaciones en tokens, pesos, cortes y ejes.

P/A/C significa Protagonista, Antagonista y Contexto. En la implementación nativa son tres dimensiones paralelas de observación, no tres niveles jerárquicos.

## 2. Camino central comprobado en código

Archivos principales inspeccionados:

- motor/motor/Engine_V5_CANONICO_SOLO.py
- motor/motor/MOTOR_V15_3_NATIVO_V0_9_UNICO.py
- motor/motor/MOTOR_V15_3_UNICO_20260927.py
- motor/correr_estandar.py
- motor/CONTRATO_ENTRADA_LLM.txt
- motor/motor/patterns_final_v14.json
- motor/motor/predictibilidad_set_021.py
- motor/motor/hipotesis_trayectoria_abierta_v1.py

### 2.1 Entrada: representación previa, no prosa cruda

El contrato de entrada exige JSON con case_id, pregunta, fecha Z y cortes. Cada corte lleva listas P, A y C con pares token/peso. El contrato dice expresamente que el sistema no recibe prosa cruda: el LLM o una persona prepara los datos estructurados.

La implementación nativa confirma esa frontera: en _board() reemplaza extract_from_text por una función que convierte los pares token/peso ya suministrados en objetos Marker. Por tanto, en este camino el sistema no realiza la extracción semántica desde el texto original. La clase MarkerExtractor del Engine V5 conserva una ruta opcional de extracción LLM, pero no es la ruta usada por el adaptador nativo revisado.

**Consecuencia:** la identificación de qué observación corresponde a Protagonista, Antagonista o Contexto, y qué token la representa, ocurre antes del cálculo central. U6 procesa esa interpretación; no debe atribuírsele automáticamente haberla descubierto.

### 2.2 Biblioteca: 244 familias y un vocabulario heterogéneo

El catálogo cargado contiene 244 familias/patrones. El recuento directo del JSON encontró 703 tokens únicos entre tokens_favor y tokens_contra. Ciento cuarenta y seis tokens aparecen como favor en unas familias y como contra en otras; no se encontró solapamiento favor/contra dentro de una misma familia.

El catálogo reúne familias de procedencias y escalas distintas: situaciones dramáticas, arquetipos, MBTI, monomito, teorías sociales e históricas, trayectorias, modelos de desarrollo y otros marcos. No es una teoría única ni un conjunto de 244 categorías homogéneas.

Conteo del campo evidence_status a nivel de familia:
- secondary_verified: 163
- primary_verified: 23
- unverified: 32
- contestado_academicamente: 24
- outdated: 1
- contradicted_partial: 1

Engine V5 transforma los pesos originales hacia 0.5 según el estado de evidencia. Es un control de calidad incorporado al peso, pero la etiqueta de estado no equivale por sí sola a una revisión independiente y actualizada de cada afirmación del catálogo.

### 2.3 Discrepancia importante: la pregunta no activa un subconjunto

El corpus conceptual describe activación de un campo semántico por la pregunta. Sin embargo, PatternLibrary.get_patterns_for_question(question), en Engine V5, devuelve directamente list(self.patterns.keys()). Es decir, **esa función devuelve todas las familias del catálogo e ignora el contenido de la pregunta**.

En el camino revisado, las tres instancias P/A/C arrancan con la misma biblioteca completa. La activación selectiva por campo semántico que se describe en el corpus no está implementada en esa función. No se debe afirmar que la pregunta reduce allí el universo de patrones.

### 2.4 Transformación por cortes: tres tableros y R732

MOTOR_V15_3_NATIVO crea tres instancias separadas de TracingEngine: una para P, otra para A y otra para C. Cada una procesa los tokens del eje en cada corte y produce una puntuación p_final para cada una de las 244 familias.

Por corte:
- tablero P: 244 puntuaciones;
- tablero A: 244 puntuaciones;
- tablero C: 244 puntuaciones;
- concatenación P|A|C: vector de 732 componentes, R732.

El código apila los vectores por corte, calcula diferencias sucesivas dX, norma de cada desplazamiento, coseno entre desplazamientos consecutivos (persist_cos) y un indicador angular kappa_dir. Estas magnitudes describen cómo cambia la representación de apoyo a patrones a través de los cortes.

**R732 no es una coordenada física ni una medición directa del estado real de la persona o sistema observado.** Es un vector de puntuaciones de patrones distribuidas en tres ejes interpretativos.

### 2.5 El núcleo de actualización no equivale a un modelo bayesiano general

Engine V5 mantiene una probabilidad binaria por familia y actualiza con una regla de tipo Bayes usando el peso del token como likelihood. Aplica además una masa residual hacia 0.5, limita los extremos y calcula p_final mezclando el estado actualizado con indeterminación y un término aleatorio P_azar.

Monte Carlo estima la media del término aleatorio P_azar para esa observación. No simula 6,310 futuros posibles del caso, ni 6,310 mundos autónomos, ni la evolución completa de las hipótesis. En F006, las 6,310 simulaciones registradas corresponden a este componente de azar/incertidumbre.

La actualización es bayesiana en una operación local reconocible, pero no constituye por sí misma una red bayesiana completa, un modelo causal ni una distribución calibrada de resultados futuros.

## 3. De los tableros a las hipótesis

### 3.1 Filtro temprano de candidatas

MOTOR_V15_3_NATIVO define:
- P_MIN_CANDIDATO = 0.65
- MAX_CANDIDATOS = 3

En cada corte y eje conserva como candidatas las tres primeras familias que alcancen al menos 0.65. El predictor integrado forma el universo observado como la unión de P_candidatos_0a3, A_candidatos_0a3 y C_candidatos_0a3 a través de los cortes.

Por tanto, aunque los tableros completos conservan 244 puntuaciones por eje, **la fase posterior de hipótesis no evalúa necesariamente las 244 familias**. Trabaja sobre la unión de candidatas que sobrevivieron al filtro top-3/umbral en al menos un eje y corte.

Esto deja una pregunta experimental importante: ¿qué ocurre con una familia que nunca entra en el top 3 de un eje/corte, pero cuya evidencia débil y distribuida podría resultar relevante al combinar cortes? La arquitectura actual puede excluirla antes de la fusión. No afirmo que el filtro sea incorrecto; señalo una restricción estructural que requiere ablación.

### 3.2 Fusión de rangos, no probabilidad

El predictor calcula características por candidata: estado, continuidad, recencia, delta, convergencia entre P/A/C, alineación de tokens, señales estructurales, geometría y señales laterales, entre otras.

Las dimensiones numéricas discriminantes se convierten en puntuaciones ordinales fraccionales y se suman en rank_fusion. Algunas señales laterales se agregan por separado. La posición final depende del conjunto de candidatas que compite en esa corrida.

Por eso rank_fusion es una agregación de rangos/soporte relativo, no una probabilidad absoluta ni una estimación calibrada de la frecuencia del desenlace.

### 3.3 El conjunto necesario-suficiente es un criterio de cobertura

predictibilidad_set_021.py fija THETA_COBERTURA = 0.90. Parte de las candidatas del predictor, conserva el eje y las casi empatadas, agrega familias por cobertura marginal de tokens explicados hasta alcanzar al menos 90% de la masa explicada por el universo candidato, cubre cortes que de otro modo quedarían sin explicación y poda miembros redundantes.

Es un procedimiento de cobertura/set-cover sobre la evidencia observada. El nombre «necesario y suficiente» no debe confundirse con una demostración lógica formal de necesidad y suficiencia.

### 3.4 Hipótesis abiertas y escenarios

hipotesis_trayectoria_abierta_v1.py toma las candidatas ya producidas por el predictor. Conserva los miembros de SET 021 y puede añadir candidatas con al menos dos enlaces explícitos de trazabilidad geométrica. Si falla el módulo de set, conserva todas las candidatas observadas disponibles.

La cardinalidad no está fijada en dos: H1/H2 son alias históricos. Cada hipótesis lleva rank_fusion, soporte estructural relativo y características de trayectoria. El código declara expresamente que ese soporte no es probabilidad.

Después agrupa hipótesis por régimen de trayectoria: continuidad ascendente, continuidad descendente, meseta/estabilización o giro/divergencia multiescala. Que varias hipótesis compartan régimen significa que sus trayectorias clasificadas tienen ese comportamiento; no significa que predigan el mismo acontecimiento concreto.

### 3.5 Proyección longitudinal

La proyección posterior a Z usa la regla:
x(Z+k) = x(Z) + k * (x(Z) - x(Z-1)).

Es una extrapolación lineal del último cambio observado, etiquetada como proyección no fijada y no como hecho. El módulo se declara post-freeze y no puede reescribir H ni la apuesta sellada. No es una simulación causal de la evolución futura.

## 4. Memoria, trazabilidad y obligación de resolver

- StinkBox conserva tokens y eventos asociados con procedencia; no equivale a una memoria completa de todas las observaciones, interpretaciones, hipótesis y dependencias epistémicas.
- CEB registra etapas, lecturas/escrituras, productores/consumidores, artefactos y estados de ejecución. Permite auditar si una pieza corrió y qué objetos movió. No demuestra por sí solo que la conclusión sea verdadera ni que cada hipótesis tenga una justificación semántica completa hasta cada fuente original.
- La Brújula de obligación de búsqueda y resolución está documentada como diseño. El handoff de 31-oct la describe como documento, no como patch aplicado. No debe afirmarse que U6 ya tiene autonomía completa para investigar hasta resolver y corregirse sin intervención de un agente externo.

## 5. La línea MCT: no confundirla con la geometría actual de U6

El documento docs/AUDITORIA_EVENTO_CANONICO_CONVERGENCIA_VECTORIAL_MCT_2026-11-03.md formula un requisito distinto: trayectorias de realidades independientes, con condiciones y desarrollos propios, deben poder compararse para detectar un mismo vector-evento esencial aunque varíen detalles periféricos.

La auditoría del propio repositorio concluye que U6 ya compara tableros P/A/C, patrones y relaciones dentro de una ejecución, pero no implementa:
- mundos/realidades autónomas;
- aislamiento entre mundos durante la exploración;
- vector-evento común con dimensiones esenciales/periféricas;
- comparador transversal entre resultados de mundos independientes;
- control anti-fuga que demuestre que las conclusiones no se transfirieron entre mundos.

Esto es una línea conceptual adicional, no una capacidad ya presente en el sistema ejecutable. El acrónimo MCT no se expande en el documento inspeccionado; no se le asigna aquí una expansión inventada.

La idea general de que trayectorias distintas pueden llegar a un mismo estado tiene antecedente conocido en la teoría general de sistemas: equifinalidad. La posible contribución específica sería convertir esa intuición en un procedimiento computacional verificable de equivalencia de eventos, con mundos aislados, vectores esenciales, tolerancias explícitas, no-convergencias y controles anti-leakage. La idea general no es nueva por sí sola; esa implementación específica aún no está demostrada.

## 6. Comparación con líneas existentes

| Línea | Coincidencia real | Diferencia respecto a U6 |
|---|---|---|
| TMS / ATMS | Justificaciones, supuestos, contradicciones y alternativas | U6 no implementa la semántica formal de etiquetas, supuestos y nogoods de un ATMS |
| ATMS temporal (Lee et al., 2000) | Mantener información y relaciones que cambian en el tiempo | Su formalismo temporal modifica etiquetas y propagación; no es el vectorizado P/A/C de U6 |
| t-DeLP | Argumentos derrotables con tiempo, persistencia y conflicto | U6 usa puntuación de patrones y ranking; no árboles de argumentos y relación formal de derrota |
| Multiple Hypothesis Tracking | Mantener y ordenar varias hipótesis a través de múltiples observaciones | MHT resuelve asociación de mediciones/objetivos en tracking; no equivale al set estructural de U6 |
| Narratología computacional | Representar trayectorias narrativas y comparar formas a través del tiempo | Rathje (2026) usa embeddings de secuencias textuales y ejes semánticos; U6 usa tokens/patrones predefinidos, P/A/C y ranking de hipótesis |
| Equifinalidad / sistemas abiertos | Diferentes condiciones y caminos pueden alcanzar un mismo estado final | MCT plantea una especificación vectorial y computacional de equivalencia entre mundos independientes, aún no implementada |

Fuentes consultadas:
- De Kleer, “An assumption-based TMS” (1986), DOI 10.1016/0004-3702(86)90080-9.
- Lee et al., “A Temporal Data Maintenance Method in an ATMS” (2000), https://globals.ieice.org/en_transactions/information/10.1587/e83-d_2_295/_p
- Pardo y Godo, “t-DeLP” (2013), https://www.iiia.csic.es/media/filer_public/c3/f9/c3f9f8c2-90ff-4035-b20a-41179b5a372f/4261.pdf
- Chong, Mori y Reid, “Forty Years of Multiple Hypothesis Tracking” (2019), https://isif.org/files/isif/2024-01/02-022019-0012R1_LR.pdf
- Rathje, “Computational narratology with transformer embeddings” (publicado 2-jun-2026), DOI 10.1017/chr.2026.10035, https://www.cambridge.org/core/journals/computational-humanities-research/article/computational-narratology-with-transformer-embeddings/309869B5FFC16D051E0ABE738DF09A59
- Montfort y Pérez y Pérez, “Computational Models for Understanding Narrative” (2023), DOI 10.34619/gnzq-r7ri.
- Richardson, “Methodological Implications of Complex Systems Approaches to Sociality” (2002), https://jasss.soc.surrey.ac.uk/5/2/6.html; describe equifinalidad como distintas trayectorias hacia un mismo estado y advierte sobre la validación y transferencia de modelos.

## 7. Estado empírico y de ejecución: no confundir actividad de auditoría con corridas

El informe del 2026-11-03 reporta 40 casos biográficos sellados independientes después de deduplicar cinco reevaluaciones:
- H1: 8/40 (20%)
- H2: 5/40 (12.5%)
- set abierto: 12/40 (30%)
- escenario principal: 10/40 (25%)

El set abierto tuvo mayor cobertura que H1/H2, pero no se midieron de forma suficiente la cardinalidad media ni la penalización por hipótesis irrelevantes. No hay ablaciones emparejadas que demuestren el beneficio causal de guardianes, compuerta, memoria o resolución adaptativa. La generalización a tareas no biográficas y a otros modelos no está medida.

La lectura de avances/auditoria_corridas/ULTIMO_ESTADO.json (ventana de siete días) encontró 99 ejecuciones de GitHub Actions. Las 47 ejecuciones más recientes del workflow “Auditoría de corridas Motor U6” son snapshots de auditoría, no corridas predictivas del sistema. El último snapshot registrado terminó correctamente el 2026-11-04 a la 01:31 CDMX. En esa misma ventana, el último “Fabrica real - smoke CEB traza 244” registrado (2026-11-02) falló; las cuatro ejecuciones de “Fabrica lote diario (Grok / dispatch)” de la ventana también terminaron en failure. Esto no descarta corridas locales no registradas en Actions, pero impide presentar los éxitos del auditor como nuevas ejecuciones predictivas.

## 8. Qué se puede afirmar y qué no

**Confirmado por inspección del camino central:**
- entrada estructurada por cortes y tokens P/A/C;
- tres tableros paralelos de 244 puntuaciones y vector R732;
- actualización de patrones con soporte/contradicción y mezcla de incertidumbre;
- extracción de candidatas top-3 por eje/corte con umbral 0.65;
- fusión ordinal de múltiples características;
- conjunto de hipótesis variable, seleccionado desde candidatas observadas;
- agrupación de escenarios por régimen de trayectoria;
- geometría descriptiva sobre las puntuaciones de la representación.

**No demostrado por esta revisión:**
- que el sistema modele causalmente la realidad observada;
- que el ranking sea probabilidad calibrada;
- que el conjunto abierto explore de verdad las 244 familias sin filtro temprano;
- que las dimensiones geométricas mejoren la predicción;
- que U6 sea formalmente ATMS, t-DeLP, MHT o una lógica no monótona;
- que la integración sea inédita mundialmente;
- que MCT esté implementado en el código;
- que el sistema investigue y se repare autónomamente hasta resolver.

## 9. Próximas pruebas que realmente discriminan la arquitectura

1. **Ablación del filtro top-3:** comparar top-3/0.65 con universo más amplio o con retención por masa/cobertura. Medir qué familias desaparecen antes de rank_fusion y qué desenlaces cambia.
2. **Ablación de P/A/C:** ejecutar comparaciones emparejadas P-only, A-only, C-only, pares y P/A/C completo, sin cambiar el caso ni el freeze.
3. **Ablación de geometría:** comparar ranking y conjunto con geometría activada/desactivada; no basta con que los módulos corran.
4. **Prueba del campo semántico:** decidir si la pregunta debe activar patrones y, si sí, implementar y medir un filtro real; hoy get_patterns_for_question devuelve todo.
5. **Prueba de cobertura 021:** registrar cardinalidad, cobertura, precisión, redundancia y falsos positivos del set; verificar si el 90% es un umbral útil.
6. **Prueba de proyección:** comparar la extrapolación lineal del último delta con baselines temporales simples y con casos ciegos; medir horizonte por horizonte.
7. **Prueba de procedencia:** vincular cada token de entrada a fuente, fecha del hecho, fecha de observación, corte, responsable de interpretación y transformación.
8. **Prueba MCT separada:** crear mundos aislados con condiciones iniciales distintas; definir vector-evento esencial/periférico; comparar equivalencia exacta, tolerada, parcial, transitoria y divergencia; demostrar ausencia de transferencia de conclusiones.
9. **Validación externa:** casos nuevos, independientes, no solo biográficos y más de un preparador/modelo; custodio distinto del preparador.

## 10. Conclusión provisional

U6 no debe reducirse a «un motor que detecta patrones y predice». Es una arquitectura de representación y análisis longitudinal de evidencia estructural, con un núcleo de actualización de puntuaciones, una capa de vectorización P/A/C, un agregador ordinal de candidatas, una selección de hipótesis abiertas, escenarios por régimen, geometría descriptiva y sistemas laterales de memoria y auditoría.

Su frontera actual es importante: opera sobre una interpretación estructurada de la realidad, no sobre la realidad en bruto. Sus vectores describen la evolución de esa representación. Sus salidas son hipótesis y escenarios ordenados, todavía con validación predictiva limitada al conjunto biográfico disponible.

La línea MCT de convergencia de eventos entre realidades independientes es una pregunta distinta y más amplia. U6 contiene herramientas geométricas que podrían servirle, pero el comparador transversal y el aislamiento de mundos aún no existen en el código inspeccionado.

Esta reconstrucción sustituye la descripción simplificada anterior. Es una lectura funcional del camino central y de documentos/módulos relevantes, no una auditoría línea por línea de los 194 archivos Python del repositorio ni una certificación de novedad mundial.
