# Auditoría de formalismos matemáticos y reinterpretaciones en U6
**Fecha:** 2026-11-03  
**Repositorio:** `marcojpad-hash/motor-u6-storage`, rama `main`  
**Base revisada:** `ec8d5949a31afd99751c0a15abf1061325acebd7`  
**Alcance:** árbol completo del repositorio (732 entradas; 194 archivos Python y 66 JSON bajo `motor/`), corpus de 17 fórmulas, catálogo canónico de 244 patrones, matriz lateral de 171 tokens y revisión dirigida de los módulos matemáticos, geométricos, probabilísticos, temporales y narrativos. No equivale a una demostración formal ni a una revisión línea por línea de los 194 archivos Python.

## 1. Dictamen

U6 contiene una mezcla de:
1. formalismos matemáticos implementados de forma reconocible;
2. adaptaciones o proxies que conservan parte de la estructura matemática pero cambian el objeto;
3. patrones semánticos inspirados en teorías matemáticas, sin ejecutar sus ecuaciones;
4. esqueletos que todavía no ejecutan el método anunciado.

Por tanto, no es correcto describir el motor como si implementara íntegramente Markov, SINDy, Ricci–Forman, Souriau o Schrödinger. Tampoco es correcto reducirlo a un catálogo de analogías: el motor canónico sí ejecuta una actualización bayesiana binaria, y varios laterales ejecutan cálculos geométricos y estadísticos concretos.

La conclusión más útil para el desarrollo es que U6 ya posee una **capa matemática heterogénea**. Lo pendiente no es sumar nombres de teorías, sino especificar qué objeto matemático toma cada módulo, qué transformación aplica, qué propiedades conserva y qué puede concluir legítimamente.

## 2. El caso que señalaste: P, Q, P||Q, P→Q e INUS

Archivo: `motor/motor/geometria_multicapa/sidecar_latentes_v1.py`.

La tabla denominada en comentarios `(p || q)` no implementa una implicación. El código la interpreta como disyunción inclusiva:
- cuenta las cuatro combinaciones: p y q, p y no q, no p y q, no p y no q;
- calcula `p_o_q_observado` contando filas donde p **o** q es verdadero;
- calcula por separado `p_entonces_q_laplace`.

La construcción de cada fila es temporal:
- `p = q_at(j-1)`: estado de la familia en el corte anterior;
- `q = q_at(j)`: estado de la misma familia en el corte siguiente;
- `cond`: tokens presentes en el corte anterior.

Así que la expresión secuencial que buscas está más cerca de **P en t → Q en t+1**, y el campo `p_entonces_q_laplace` estima una frecuencia condicional suavizada. No prueba que P cause Q ni que P implique lógicamente Q.

La regla usada es:
```
Laplace(s,n) = (s + 1) / (n + 2)
```
recortada al intervalo [0.05, 0.95]. El propio archivo aclara que es la regla de sucesión de Laplace y que no viene del motor canónico.

### INUS

En el mismo módulo se buscan conjuntos de 2 o 3 condiciones que:
- aparezcan en al menos dos transiciones;
- sean suficientes en las filas observadas;
- no contengan subconjuntos ya suficientes;
- tengan miembros individualmente insuficientes y no redundantes;
- no sean necesarios para todos los casos de Q.

El código los etiqueta prudentemente como `INUS_LIKE`. Es una operacionalización inspirada en la idea de Mackie de una parte insuficiente pero no redundante de una condición suficiente que no es necesaria. No constituye por sí sola inferencia causal: trabaja sobre transiciones observadas, no sobre intervenciones contrafactuales. Aunque el bloque se titula “tabla contrafactual”, su tabla 2×2 es observacional; el propio módulo advierte que no prueba causalidad.

**Esto es importante para tu propuesta dramática:** el motor ya tiene una primera gramática formal de antecedentes, condiciones, suficiencia contextual, necesidad y transición entre estados. No habría que inventarla desde cero; habría que extenderla a acontecimientos y relaciones entre acontecimientos, preservando la diferencia entre asociación y causalidad.

## 3. Formalismos probabilísticos y de calibración

### 3.1 Bayes: implementado en el motor canónico

Archivo: `motor/motor/Engine_V5_CANONICO_SOLO.py`.

La actualización de hipótesis usa:
```
p' = (p · lh) / (p · lh + (1-p) · (1-lh))
```
con `lh` limitado a [0.001, 0.999]. Es una actualización bayesiana binaria bajo una parametrización simétrica de la verosimilitud. La evidencia favorable usa el peso como `lh`; la contradicción usa `1-lh`.

No equivale a una red bayesiana general ni a un modelo causal completo. Pero sí es una operación bayesiana real, no una mera metáfora.

### 3.2 Masa residual de incertidumbre

El mismo motor ejecuta:
```
p ← (1-ε) · p + ε · 0.5
```
Es una mezcla con un estado de indeterminación. La fórmula 3 del corpus sí tiene correspondencia directa en el código.

### 3.3 Incertidumbre dinámica y Monte Carlo

Se calcula:
- incertidumbre media de marcadores como `1-confidence`;
- dispersión de esas incertidumbres mediante desviación estándar poblacional;
- `delta_min` dependiente de la incertidumbre media;
- `p_azar` mediante una variable aleatoria acotada;
- una estimación Monte Carlo de su media, con criterio de error estándar.

La salida mezcla la probabilidad interna, el componente de indeterminación y el azar. Es una construcción híbrida propia del motor; no debe confundirse con una posterior bayesiana estándar.

### 3.4 Laplace y calibración

La regla de Laplace aparece en:
- `sidecar_latentes_v1.py`, para frecuencias condicionales y soportes de condiciones;
- `motor/calibracion/arnes_calibracion.py`, para tasas de acierto suavizadas;
- reportes y evaluaciones de calibración.

No encontré una transformada integral de Laplace. En estos lugares, “Laplace” significa suavizado/regla de sucesión.

### 3.5 Brier, log-loss, ECE y Platt

`calibracion_predictiva_v1.py` implementa evaluación de probabilidades mediante Brier, log-loss, error de calibración esperado y ajuste Platt con sigmoide. Es un bloque estadístico real, sujeto a contar con probabilidades y desenlaces del mismo objetivo y horizonte.

## 4. Markov, MDP, Cox, SIR, FTA y SINDy

### Markov / MDP / Cox / SIR / FTA

El catálogo `patterns_final_v14.json` contiene:
- `predictivo_01_markov_estado_absorbente`;
- `predictivo_02_mdp_politica_optima`;
- `predictivo_03_cox_survival_riesgo`;
- `predictivo_04_caos_bifurcacion_critica`;
- `predictivo_05_sir_contagio_conductual`;
- `predictivo_06_ingenieria_arbol_fallas`.

Las descripciones son explícitas:
- Markov no calcula matriz de transición real;
- MDP no implementa función de recompensa ni política óptima;
- Cox no calcula función de riesgo;
- SIR no ejecuta ecuaciones diferenciales;
- el patrón de catástrofe/caos no calcula un sistema dinámico;
- FTA funciona como vocabulario de fallos concatenados, no como árbol cuantitativo de probabilidades.

Son analogías estructurales codificadas como patrones de tokens, no esos modelos matemáticos ejecutados.

### SINDy

La búsqueda en el código del repositorio no encontró una implementación identificable de SINDy ni una biblioteca de regresores dispersos equivalente. Hay regresión por mínimos cuadrados, pendientes por ajuste lineal y análisis de diferencias, pero eso no basta para llamar SINDy a un módulo.

Para reconocer una implementación SINDy esperaríamos, al menos:
1. una matriz de datos de estados;
2. estimación de derivadas o diferencias temporales;
3. biblioteca explícita de funciones candidatas no lineales;
4. ajuste disperso de coeficientes (umbral iterativo, LASSO u otro método);
5. validación del sistema identificado sobre datos no usados en el ajuste.

La existencia de `np.linalg.lstsq`, `np.polyfit` o `np.diff` no satisface esos requisitos. Sí son piezas que podrían servir como infraestructura para una futura implementación, pero no son SINDy.

## 5. Geometría, dinámica y topología

### 5.1 P/A/C, R732 y métricas de trayectoria

Los módulos geométricos usan vectores de 732 dimensiones construidos como P/A/C, con 244 dimensiones por eje. Ejecutan diferencias entre cortes, normas euclidianas, productos punto, cosenos, aceleraciones discretas y correlaciones de diferencias.

`v153_lateral_metrics_v1_1.py` calcula, entre otras cosas:
- primera diferencia `ΔX`;
- segunda diferencia `Δ²X`;
- norma de velocidad;
- persistencia direccional por coseno;
- indicadores de curvatura direccional y externa;
- distancias entre patrones en coordenadas locales P/A/C;
- correlación de diferencias P entre patrones.

Son operaciones matemáticas ejecutadas. Su interpretación sigue siendo descriptiva: P/A/C son puntuaciones abstractas, no coordenadas físicas.

### 5.2 PCA, SVD, mínimos cuadrados y jerarquía

`adaptador_convergencia_real_v1.py` y `v153_convergencia_multinivel_v0_3.py` implementan:
- PCA mediante SVD;
- ajuste de mapas afines por mínimos cuadrados;
- evaluación de residuos en cortes reservados;
- comparación de trayectorias y contracción de distancias.

`teseracto_recursivo_geometria_v0_4.py` añade:
- distancias euclidianas;
- agrupamiento jerárquico Ward;
- ajuste geométrico de hélice mediante mínimos cuadrados y regresión lineal;
- controles por permutación del orden temporal.

Esto no equivale a descubrir leyes dinámicas. La propia documentación califica la hélice y la jerarquía como diagnósticos descriptivos y advierte sobre pocos cortes y proyecciones engañosas.

### 5.3 Ricci–Forman: dos implementaciones que no deben confundirse

Hay una diferencia crítica:

**A.** `forman_ricci_weighted_graph.py` implementa una fórmula de curvatura de Forman–Ricci para un grafo ponderado explícito de dimensión 1. El grafo y sus pesos deben venir dados. El módulo declara que no está integrado a P/A/C ni a H.

**B.** `ricci_forman_coocurrencia_v0_1.py` construye aristas implícitas entre candidatos P de cortes consecutivos y calcula:
```
curv = tanh(media_peso_local - media_peso_anterior)
```
Su propio resultado declara:
- `TEMPORAL_WEIGHT_DRIFT_PROXY_NOT_EXACT_FORMAN`;
- `forman_ricci_verified = False`;
- no implementa la fórmula de curvatura ponderada de Forman.

Por tanto, el nombre “Ricci–Forman” del segundo módulo es una analogía/proxy temporal. La fórmula exacta existe en otro archivo, pero no está conectada al flujo de P/A/C.

### 5.4 Billar circular y Poincaré

`billar_circular_convergencia_v0_1.py` transforma las variaciones de puntuación de cada familia en incrementos angulares:
```
ω_t = 2π · (p_t - p_{t-1})
φ_t = (φ_{t-1} + ω_t) mod 2π
z_t = (cos φ_t, sin φ_t)
```
Después compara distancias entre puntos de fase y contrasta las convergencias con permutaciones de las series.

Es una transformación matemática concreta y un mapa circular construido por el módulo. No es automáticamente una sección de Poincaré derivada de un flujo físico subyacente; la interpretación como billar/Poincaré es analógica.

### 5.5 Par de Tusi

`tusi_par_indice_exploratorio_v0_1.py` y el adaptador geométrico comparan pares de series de incrementos y calculan un índice de contrarrotación con un control nulo por permutación. Es exploratorio y no alimenta H.

## 6. Souriau, Schrödinger y otros formalismos

### Souriau

`souriau_momentum_so3.py` calcula el mapa de momento:
```
J(q,p) = q × p
```
para vectores explícitos de tres componentes. Esa operación es matemáticamente válida para el contrato SO(3) declarado.

Pero `marco_funciones_souriau.py` aclara que su asignación de personajes/funciones es narrativa y que el mapa matemático de momento no está implementado por ese módulo. Tampoco calcula órbitas coadjuntas ni deriva q/p de los tokens P/A/C.

Por tanto hay dos cosas distintas con el mismo apellido: una primitiva matemática SO(3) aislada y un módulo de asignación narrativa que no la ejecuta.

### Schrödinger

`schrodinger_transport_esqueleto_v0_1.py` declara `PROPOSAL`, `Alimenta_H=NO`, y contiene funciones `NotImplementedError` para costo, Sinkhorn y reconstrucción inversa. Es una interfaz/esqueleto, no una implementación de transporte.

### Needleman–Wunsch

`predictor_vecinos_prefijo_v1.py` sí implementa programación dinámica de alineamiento de secuencias con costos de inserción/eliminación y sustitución. Compara prefijos del mismo largo y consulta la etapa siguiente después de seleccionar vecinos. No es Markov; es alineamiento óptimo de secuencias.

## 7. Correspondencia entre el corpus de 17 fórmulas y el código

El archivo `motor/motor/Corpus_Final_Unificado_17_Formulas.txt` es una especificación conceptual/documental. No todas sus fórmulas son ecuaciones ejecutables ni todas están implementadas literalmente.

| Fórmula del corpus | Correspondencia observada |
|---|---|
| 1, estado actualizado | Principio general; actualización real aparece en el motor |
| 2, inferencia probabilística | Implementación bayesiana binaria relacionada, no la ecuación completa escrita en el corpus |
| 3, masa residual ε | Implementada en `Hypothesis.apply_epsilon` |
| 4 y 6, estados acumulativos | Implementados como flujo/actualización, con diferencias entre versiones |
| 5, dependencia condicional | Relacionada con tabla temporal P/Q y frecuencia condicional; no causalidad |
| 7, memoria latente | Hay almacenamiento/reactivación y trazabilidad, con alcance parcial |
| 8, vector multidimensional | P/A/C y R732 lo concretan en la arquitectura actual |
| 9 y 17, flujo general | Descripción de proceso, no fórmula matemática |
| 10, contradicción contextual | El motor guarda condiciones junto a contradicciones; no identifica automáticamente causas |
| 11, pesos dinámicos | Parcial; el corpus semántico P(Token|N_Q) se documenta como pendiente en el motor canónico |
| 12, convergencia evidencial | Principio conceptual con varios indicadores laterales; no una función única validada |
| 13, falsación/divergencia | Se conservan señales contrarias y condiciones; no equivale a falsación causal formal |
| 14, Décimo Hombre | Implementación parcial de controles, incertidumbre y objeciones |
| 15, estabilidad de régimen | Hay módulos de estabilidad/mesetas y trayectorias; no una única función universal |
| 16, transición por umbral | Hay detectores por umbral y cambios de régimen descriptivos |
| 22, mezcla de salida | El motor canónico documenta una mezcla de evidencia, indeterminación y azar; revisar la referencia de numeración |

**Inconsistencia documental a corregir en una futura pasada:** el motor canónico menciona “Fórmula 22 del documento de 17 fórmulas”, aunque el corpus visible enumera 17 fórmulas y deja la mezcla final en el anexo. `predictibilidad_set_021.py` también llama “Fórmula 22” a una variante que sustituye la magnitud de entrada por rank_fusion. Debe normalizarse la referencia y distinguir la salida bayesiana canónica de la predictibilidad estructural lateral.

## 8. Implicaciones para la representación matemática de situaciones dramáticas

La nueva capa de acontecimiento no debería incorporar otra colección de metáforas matemáticas. Puede apoyarse en formalismos ya presentes:

- **P/Q + INUS:** condiciones previas, condiciones suficientes, rutas alternativas y transiciones observadas.
- **Bayes:** actualización de soporte de hipótesis cuando aparece evidencia nueva, sin reescribir el corte congelado.
- **Sistemas dinámicos discretos/híbridos:** evolución de estados y cambios de régimen, una vez que se definan variables y reglas de transición.
- **Grafos y curvatura:** relaciones entre acontecimientos, siempre separando la curvatura exacta del proxy de deriva temporal.
- **Geometría P/A/C:** comparación descriptiva de trayectorias y sus cambios, no identificación automática de significado dramático.
- **Memento:** reconstrucción retrospectiva que debe dejar de limitarse a presencia acumulada de tokens y representar dependencias/eventos explícitos.

El objeto de acontecimiento debe tener al menos: estado anterior, estado posterior, condiciones, fuerzas/actores, relaciones antecedentes, tipo de transición, evidencia de origen y grado de independencia de las fuentes. Las relaciones causales, temporales, simultáneas, alternativas y contradictorias deben ser tipos diferentes.

## 9. Recomendación técnica

Antes de diseñar otro módulo, crear un registro de formalismos con estas columnas:

1. nombre del formalismo de origen;
2. ecuación o definición de referencia;
3. objeto matemático original;
4. objeto que recibe U6;
5. transformación aplicada;
6. propiedades conservadas;
7. propiedades que ya no se conservan;
8. estado: EJECUTADO_EXACTO / ADAPTADO / PROXY / METAFORA_CATALOGO / ESQUELETO / NO_ENCONTRADO;
9. cableado: canónico / lateral ejecutado / lateral no cableado;
10. validación, pruebas y límites.

La prioridad inmediata debería ser aclarar la familia P/Q/INUS, la distinción entre Ricci exacto y proxy, y la relación entre la geometría de trayectorias y el nuevo objeto de acontecimiento. SINDy y Markov no deben atribuirse al motor hasta que existan implementaciones verificables.

## 10. Fuentes internas inspeccionadas

- `motor/motor/Corpus_Final_Unificado_17_Formulas.txt`
- `motor/motor/Engine_V5_CANONICO_SOLO.py`
- `motor/motor/MOTOR_V15_3_UNICO_20260927.py`
- `motor/motor/patterns_final_v14.json`
- `motor/motor/geometria_multicapa/sidecar_latentes_v1.py`
- `motor/motor/ricci_forman_coocurrencia_v0_1.py`
- `motor/motor/forman_ricci_weighted_graph.py`
- `motor/motor/billar_circular_convergencia_v0_1.py`
- `motor/motor/billar_circular_convergencia_v0_2.py`
- `motor/motor/tusi_par_indice_exploratorio_v0_1.py`
- `motor/motor/v153_lateral_metrics_v1_1.py`
- `motor/motor/geometria_multicapa/adaptador_convergencia_real_v1.py`
- `motor/motor/geometria_multicapa/v153_convergencia_multinivel_v0_3.py`
- `motor/motor/geometria_multicapa/teseracto_recursivo_geometria_v0_4.py`
- `motor/motor/souriau_momentum_so3.py`
- `motor/motor/marco_funciones_souriau.py`
- `motor/motor/schrodinger_transport_esqueleto_v0_1.py`
- `motor/motor/predictor_vecinos_prefijo_v1.py`
- `motor/motor/calibracion_predictiva_v1.py`
- `motor/motor/predictibilidad_set_021.py`
- `motor/motor/plugin_arco_field_snyder_mckee.py`
- `motor/motor/zri_coupling_v0_2.py`

**Límite de esta auditoría:** es una clasificación técnica del código y sus contratos declarados. No certifica novedad científica, equivalencia formal completa ni validez empírica de los modelos.
