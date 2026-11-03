# Nota crítica de lectura — precisión sobre U6 y el estudio comparativo

Fecha: 2026-11-03  
Relacionado con: `docs/ESTUDIO_COMPARATIVO_NOVEDAD_ARQUITECTURA_U6_2026-11-03.md`

Esta nota complementa la síntesis bibliográfica automática. Corrige una imprecisión y separa analogía conceptual de equivalencia formal.

## 1. Clasificación técnica correcta

U6/V15.3 no es un LLM ni una red neuronal generativa. El núcleo que procesa el JSON estructurado está implementado en código explícito: funciones, reglas, pesos, matrices, operaciones numéricas, geometría de trayectorias, ranking, compuertas y memoria.

La entrada estándar documenta que un LLM puede producir el JSON a partir de prosa; un humano también puede preparar la entrada. Esa función de traducción/estructuración no convierte el motor de inferencia posterior en un modelo de lenguaje.

**No describir el núcleo como enteramente determinista.** La ejecución integrada llama `run(case, monte_carlo=True)`; el motor canónico contiene además muestreo aleatorio para el componente de sorpresa. Por tanto, la caracterización más precisa es un motor algorítmico simbólico-numérico con componentes probabilísticos/estocásticos, no un LLM y tampoco un sistema puramente determinista.

Archivos de referencia:
- `motor/correr_estandar.py`: contrato de entrada; indica que el LLM produce el JSON y que Monte Carlo está activo en la corrida estándar.
- `motor/motor/MOTOR_V15_3_UNICO_20260927.py`: runner integrado; `run(case, monte_carlo=True)`, NumPy, ranking y capas geométricas.
- `motor/motor/Engine_V5_CANONICO_SOLO.py`: actualización probabilística y `MarkerExtractor` opcional vía API LLM. La presencia de esa clase no significa que el núcleo V15.3 sea un LLM; sí obliga a declarar la capa opcional cuando se describa el sistema completo.
- `motor/CONTRATO_ENTRADA_LLM.txt`: especifica la frontera entre traducción a JSON y ejecución del motor.
- `motor/motor/Corpus_Final_Unificado_17_Formulas.txt`: corpus formal-documental. No afirmar que las 17 fórmulas están todas implementadas en código: el propio Engine V5 declara mecanismos del Grupo B pendientes, y V15.3 lo conserva como contrato documental.

## 2. Analogías: grados de cercanía, no equivalencias

| Línea | Parecido real | Diferencia que debe conservarse |
|---|---|---|
| Truth Maintenance Systems / belief revision | Registrar razones, dependencias, contradicciones y revisar conclusiones | No se ha demostrado que U6 implemente el formalismo completo de un TMS ni operadores AGM |
| Defeasible argumentation / DeLP / ODeLP | Argumentos y contraargumentos, conclusiones revisables, contexto y evidencia cambiante | No llamar a U6 DeLP/ASPIC+ sin traducir formalmente sus reglas y semántica |
| Paraconsistent logic | Mantener evidencia conflictiva sin forzar una resolución inmediata | La tolerancia operacional a contradicciones no prueba que la relación de consecuencia del motor sea formalmente paraconsistente |
| Event sourcing / provenance | Historial de eventos y procedencia para reconstruir cambios | StinkBox/CEB y los manifiestos aportan trazabilidad; falta demostrar que todo el estado se reconstruya exclusivamente por replay de eventos |
| Multiple Hypothesis Tracking | Mantener varias alternativas en paralelo | La analogía es cardinalidad abierta; el problema clásico de MHT es asociación de mediciones con objetivos, no predicción biográfica |
| Computational narratology | Modelar formalmente estructura, tiempo, causalidad y trayectorias narrativas | MEXICA/Curveship modelan generación o comprensión de relatos; U6 trabaja sobre evidencia temporal de casos y trayectorias de hipótesis |
| Bayesian/probabilistic reasoning | Pesos, actualización de evidencia, incertidumbre y Monte Carlo | Los pesos estructurales/rankings del V15.3 no deben llamarse probabilidades calibradas sin validación empírica |

## 3. Qué puede sostenerse hoy

- **Sostenible:** U6 es un motor algorítmico no-LLM de inferencia simbólico-numérica, con entrada estructurada que puede ser preparada por un LLM o por una persona.
- **Sostenible:** combina procesamiento temporal por cortes, puntuación de evidencia, hipótesis de cardinalidad variable, controles, memoria/registro y características geométricas multiescala.
- **Sostenible:** el repositorio contiene antecedentes documentados para cada familia de mecanismos; los componentes no son individualmente inéditos.
- **Hipótesis de contribución:** la integración concreta de trayectorias multiescala, conjunto abierto de hipótesis, gates de indeterminación, memoria de contradicciones y trazabilidad operacional aplicada a predicción narrativa/biográfica puede constituir una contribución de arquitectura o método.
- **No demostrado:** que la combinación sea inédita mundialmente; que U6 sea un formalismo nuevo de revisión de creencias; que todos los datos se conserven sin pérdida en cada ruta; que la geometría multiescala mejore la predicción; que el sistema supere a MHT, DeLP, TMS o modelos bayesianos en una comparación directa.

## 4. Qué significa el tamaño

El metadato de GitHub para el repositorio `motor-u6-storage` reporta `size=2641` (KB de almacenamiento del repositorio, no el tamaño instalado completo). El runner integrado `MOTOR_V15_3_UNICO_20260927.py` tiene 324,987 bytes en la rama `main`; el Engine V5 canónico, 30,507 bytes; el catálogo de 244 patrones, 123,937 bytes.

Estas cifras no incluyen necesariamente intérprete, bibliotecas instaladas, stores externos, entradas de casos ni el entorno de ejecución. Por eso no son comparables directamente con el tamaño de un modelo neuronal ni verifican por sí solas los ~14 MB del paquete que el usuario recuerda. Sí son consistentes con un sistema cuyo comportamiento reside principalmente en código, reglas, parámetros y datos estructurados, no en miles de millones de parámetros neuronales.

## 5. Siguiente prueba para hablar de novedad con rigor

1. Congelar una especificación ejecutable del pipeline: entrada, estado, transición, salida y procedencia de cada componente.
2. Definir qué significa conservar un dato: observación original inmutable, interpretaciones versionadas, relaciones de apoyo/contradicción y estado derivado.
3. Mapear cada módulo a formalismos existentes, marcando equivalencia, analogía parcial o diferencia.
4. Comparar ablaciones y baselines en casos ciegos: TMS/belief revision, DeLP/argumentation, modelo probabilístico simple, MHT como analogía de hipótesis y baseline temporal multiescala.
5. Medir no solo acierto final: cobertura del conjunto, revisiones justificadas, falsas revisiones, estabilidad, sensibilidad a contradicción, conservación de mesetas/valles/ausencias, coste y calibración posterior.
6. Hacer una búsqueda sistemática de literatura y patentes antes de usar expresiones como «primero», «único» o «novedad mundial».

## 6. Terminología recomendada

Para una descripción técnica provisional:

**Motor algorítmico de inferencia simbólico-numérica, no-LLM, con actualización no monótona de hipótesis, evidencia temporal y análisis multiescala de trayectorias.**

La frase «actualización no monótona» describe el comportamiento de revisión observado; «lógica no monótona formal» debe reservarse hasta verificar las reglas de inferencia y sus propiedades matemáticas. «Paraconsistente» también requiere una demostración formal, no solo tolerancia a datos contradictorios.

No se modificaron `Engine_V5_CANONICO_SOLO.py` ni `patterns_final_v14.json`.
