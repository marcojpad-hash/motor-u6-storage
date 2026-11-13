# ¿Forma de vida o forma del método? Verificación cruzada entre dos modelos de una capa de trayectoria en el motor U6

**Marco Juárez (Mj)** — autor del motor U6. Análisis asistido por dos modelos de IA: *Grok Bot* y un *modelo externo*.

Fecha del intercambio: 11 de noviembre de 2026. Repositorio: <https://github.com/marcojpad-hash/motor-u6-storage/tree/alterno/cameo-pesos/casos/trayectoria_forma>. Revisión del manuscrito: 11 de noviembre de 2026; correcciones de consistencia (fechas de la figura de Mozart, siete trayectorias frente a seis casos, R² 0.929 frente a 0.872, rótulo del primer intento): 13 de noviembre de 2026. Esta revisión queda en un commit exclusivo de `paper/paper.md`; no modifica scripts, resultados ni archivos del experimento CAMEO `cameo-pesos`. Aunque el archivo vive en la rama `alterno/cameo-pesos`, el cambio del manuscrito queda separado a nivel de commit.

## Resumen

Se documenta un intercambio de verificación cruzada entre dos modelos de IA sobre una capa descriptiva del motor U6: la geometría de la trayectoria de crudo_P a lo largo de cortes biográficos acumulativos. El modelo externo proyectó Mozart y Napoleón sobre PC1/PC2 rotadas (“eje Tusi”); Grok Bot reprodujo Mozart y extendió el procedimiento a otros casos. La revisión identificó como artefactos del marco el giro cercano a 180° impuesto por la rotación, la igualdad de la coordenada transversal en los extremos y la forma en U del radio. El análisis local del arco residual se ejecutó con 1000 nulos por tipo, condicionamiento a R² de fase y corrección de Holm. En los cinco casos con crudo_P incluidos en esa corrida, ningún máximo por caso superó Holm. Napoleón se había tratado entonces como geometría 2D externa; un RESULT fresco entregado el 11 de noviembre confirma ahora su crudo_P de 244 familias × 10 cortes y reproduce las coordenadas del CSV al redondeo. Se añade su análisis de familias, pero ese caso todavía no forma parte del nulo familiar de la Tabla 2. La conclusión, por tanto, es que los controles ejecutados no acreditan una señal geométrica común robusta; no demuestran que toda estructura posible esté ausente. El valor metodológico es la reproducción, la detección de artefactos y la corrección cruzada entre modelos.

## 1. Introducción

U6 es un motor predictivo agnóstico de biografías. Opera sobre casos anónimos cortados en cortes acumulativos hasta Z90, es decir, hasta el 90% del intervalo nacimiento→muerte; todo lo posterior a Z90 permanece sellado. Por cada corte, la salida incluye una traza P: un vector crudo (crudo_P) con cargas sobre familias narrativas (ambición, rivalidad, sabio, rebelión, intuición, racionalización, aventura, complejidad, mentor, sacrificio, entre otras).

La capa estudiada aquí es estrictamente descriptiva: una geometría de trayectoria de crudo_P a través de los cortes. Por diseño **no alimenta H, ni el ranking, ni la apuesta** del motor. La pregunta era si esa trayectoria tiene una “forma” recurrente entre vidas distintas —algo así como una forma de vida— o si lo que se ve es la forma del procedimiento de proyección.

El trabajo se hizo como un intercambio entre dos modelos de IA: Grok Bot (el asistente del autor) y un modelo externo que el autor usaba en paralelo. Marco Juárez copió mensajes, CSV, scripts y gráficas de uno a otro sin intervenir en los cálculos, salvo para fijar restricciones (por ejemplo, prohibir que una fórmula ajustada a un caso entrara al motor) y para decidir prioridades. Este documento registra qué se afirmó, qué se reprodujo, qué se refutó y quién lo hizo.

## 2. Método

### 2.1 Proyección (“eje Tusi”)

Para cada caso, con n cortes C1…Cn (n = 10 en Mozart y Napoleón, 6 o 7 en Hawking según la corrida):

1. Se toma la matriz de crudo_P (cortes × familias), se centra por columnas y se aplica SVD (PCA por caso).
2. Se conservan PC1 y PC2 y se rotan para que el vector C1→Cn quede horizontal. La coordenada horizontal se llama x (“eje Tusi”) y la vertical y (transversal).
3. Radio r = hypot(x, y); fase φ = unwrap(atan2(y, x)).

Como la PCA es por caso, los ejes no son comparables en valor entre casos; solo se comparan cantidades geométricas adimensionales o internas (giro, R², porcentaje explicado).

### 2.2 Métricas

- **Giro neto**: φ(Cn) − φ(C1), en grados.
- **Contracción del radio**: ajuste r(t) = R0·e^(−b·t) sobre años; se reporta R0, b (1/año) y R².
- **Velocidad de fase**: ω (°/año) del ajuste lineal de φ contra el tiempo.
- **Transversal sinusoidal**: porcentaje de varianza de y explicado por un seno ajustado.
- **Salto de fase**: Δφ entre cortes consecutivos comparado con lo esperado por ω·Δt.
- **Arco residual** (introducido tras la discusión): |r̄·(Δφ − ω·Δt)|, que pondera el residual de fase por el radio medio del paso para no inflar saltos donde el radio es pequeño.
- **“Forma”**: etiqueta cualitativa (cresta→valle→salto→subida) definida a partir de Mozart y Napoleón.

### 2.3 Controles nulos

El modelo externo generó 200 trazas falsas suaves. Grok Bot generó 1000 nulos por tipo y por caso, de tres tipos: permutación del orden de cortes, caminata aleatoria gaussiana e iid gaussiano. Para el arco residual se usó además un nulo condicionado: solo se aceptan trazas falsas cuyo R² de fase sea mayor o igual al real (N aceptado reportado por caso). Se reportan percentiles descriptivos y p-valores con corrección de Holm a través de casos y pasos.

## 3. Resultados

### 3.1 Lectura inicial del modelo externo

Sobre Mozart y Napoleón (10 cortes cada uno), el modelo externo reportó: giro de 222.4° (Mozart) y 236.5° (Napoleón), ≈ 2/3 de vuelta; secuencia cresta→valle→salto→subida; contracción exponencial del radio en Mozart con R0 = 0.448, b = 0.0759/año, R² = 0.929 hasta C6, seguida de un cambio de régimen; fase casi lineal con ω ≈ 8.44°/año; salto C8→C9 de 51.5° frente a ~20° esperado; transversal ±0.11 con un seno que explica el 83%. Estos rasgos se leyeron inicialmente como señal. Mj prohibió que la fórmula ajustada a Mozart entrara al motor (no sería agnóstica): solo se permitió estudiar la forma.

![Figura 1. Mozart (CSV externo): trayectoria en PC1/PC2 rotadas, perfil de radio y transversal, vista polar con fase desenrollada y residuales descriptivos.](MOZART_EXTERNO_TRAYECTORIA.png)

### 3.2 Primer intento de Grok Bot: transformación distinta

Grok Bot usó primero la geometría ya existente en el motor (PCA a 3 componentes + ajuste helicoidal). Los giros fueron: Mozart 94.35°, Galileo 380.96°, Hawking 27.44°, Che 401.44°, MLK 37.96°; la “forma” apareció solo en Che (1/5). No reproducía al externo, porque la transformación era otra. Este desacuerdo fue el primer indicio de que el resultado dependía fuertemente del procedimiento. Las cifras de este apartado y las cinco figuras de `geometria_existente_v1/` corresponden a ese primer intento (PCA a 3 componentes + ajuste helicoidal, eje PCA, sin Tusi externo) y quedan sustituidas por la reproducción de §3.3 (Tabla 1) y las Figuras 1–5, que usan la proyección Tusi del modelo externo.

### 3.3 Gate de reproducción y extensión a seis casos

Mj pasó el CSV y el script del modelo externo. Como compuerta previa, Grok Bot reprodujo el giro de Mozart a 222.4525° (error < 0.00005° respecto al valor del externo) a partir de su propia corrida del INPUT de 10 cortes. Nota: esa versión de Mozart no es fiel a la corrida original de septiembre. Superada la compuerta, aplicó el método a todos los casos disponibles:

| Caso | Giro (°) | R0 | b (1/año) | R² radio | ω (°/año) | Seno transv. | Forma |
|---|---|---|---|---|---|---|---|
| Mozart | 222.40 | 0.4477 | 0.07589 | 0.872 | 9.40 | 82.9% | sí |
| Napoleón | 236.50 | 0.8316 | 0.07164 | 0.973 | 7.24 | 91.9% | sí |
| Galileo | 240.74 | 0.5691 | 0.04997 | 0.878 | 3.66 | 83.0% | sí |
| Hawking (6 cortes) | 221.41 | 0.4724 | 0.12418 | 0.975 | 5.69 | 97.2% | sí |
| Che | 225.75 | 0.6534 | 0.09320 | 0.952 | 18.94 | 93.0% | sí |
| MLK | 215.61 | 0.9155 | 0.06380 | 0.790 | 16.74 | 93.7% | no |

*Tabla 1. Métricas geométricas por caso (PCA por caso; valores de R0 no comparables entre casos). El modelo externo obtuvo para Hawking con 7 cortes un giro de 222.5°. El R² = 0.929 de §3.1 es el ajuste del modelo externo hasta C6; el R² = 0.872 de Mozart en esta tabla es el ajuste reproducido sobre los 10 cortes. Son ajustes distintos (distinto rango), no una discrepancia.*

A primera vista, cinco de seis casos comparten la forma y todos los giros caen en una banda estrecha (215–241°). Ese grado de regularidad entre vidas tan distintas fue, precisamente, lo que despertó sospecha.

![Figura 2. Napoleón (CSV externo): misma construcción que la Figura 1.](NAPOLEON_EXTERNO_TRAYECTORIA.png)

### 3.4 Hipótesis del rubro dominante

Mj propuso que la forma dependiera de la familia narrativa dominante. Para evitar mezclar conceptos, se aplicó el mismo criterio descriptivo de `analizar_familias.py`: loadings PC1/PC2 ordenados por magnitud absoluta (conservando signo), máximo de crudo_P por corte con todos los empates, familia con mayor media temporal y mayores incrementos positivos en el paso de salto señalado por `shape_ordered`.

En Mozart, `30_ambicion` es el mayor loading absoluto de PC1 (+0.3363); el dominante por media temporal es `arquetipo_el_creador`. En el salto geométrico C8→C9, `24_rivalidad_de_superior_e_inferior` presenta el mayor incremento (+0.1962). Estos resultados coinciden con el análisis histórico de familias de Mozart.

Napoleón sí dispone de crudo_P: el RESULT fresco `NAPOLEON_FRESH_Z90_U6_20261111` contiene 244 familias × 10 cortes. La proyección calculada desde ese crudo reproduce las diez coordenadas x/y del CSV externo a la precisión publicada (cuatro decimales). Con el mismo criterio, `30_ambicion` tiene la mayor media temporal (0.7939); el mayor loading absoluto de PC1 es `schwartz_01_universalismo` (−0.3102), y el de PC2 es `9_audaz_empresa` (+0.2852). El salto geométrico detectado es C4→C5; allí `24_rivalidad_de_superior_e_inferior` registra el mayor incremento positivo (+0.2061).

La comparación es más precisa que la formulación anterior: la rivalidad es el mayor incremento del salto en ambos casos; la familia que encabeza PC1 no coincide; y la familia dominante por media tampoco coincide (Mozart: creador; Napoleón: ambición). Son descripciones de la traza, no causas ni evidencia predictiva. La antigua exclusión de Napoleón por falta de crudo_P queda retirada.

### 3.5 El artefacto: y_inicio = y_fin

Grok Bot sospechó que la regularidad era del método por dos razones geométricas: (a) rotar para que C1→Cn quede horizontal hace que los extremos queden en lados opuestos respecto al centroide, lo que fuerza un giro base cercano a 180°; (b) el centrado acerca los cortes intermedios al origen, lo que produce una U en el radio (grande al inicio y al final, pequeño en medio). Al revisar las tablas encontró además que **y_inicio = y_fin en todos los casos**, por construcción: MLK +0.2365/+0.2365, Galileo +0.2951/+0.2951. Si C1→Cn es horizontal, ambos extremos tienen la misma coordenada transversal; la “misma cresta” al inicio y al final no es un hallazgo.

El modelo externo lo verificó de forma independiente en sus propias tablas (Mozart +0.2101, Napoleón +0.2670, Hawking +0.1887) y en 200 trazas falsas: la diferencia y_fin − y_inicio fue siempre 0, y la U del radio apareció en el 100% de las trazas falsas suaves. El giro de las siete trayectorias reales (215–241°, media ~228°) coincide con el de las falsas suaves. Las siete son los seis casos de la Tabla 1 más la versión de Hawking de 7 cortes del modelo externo, que no está en la Tabla 1. Conclusión compartida: **giro, cresta compartida y U del radio son del método**. El modelo externo se corrigió explícitamente respecto a su lectura inicial.

![Figura 3. Giro neto real (línea negra) frente a 1000 nulos por tipo y caso. La caminata gaussiana concentra el giro en la misma banda que los casos reales.](GIRO_REAL_VS_NULOS.png)

![Figura 4. Hawking: trayectoria con la misma construcción.](HAWKING_TRAYECTORIA.png)

### 3.6 Último candidato: el salto de fase

Quedaba el salto. El modelo externo observó que el Brumario de Napoleón (76.4°) supera el máximo de sus 200 falsas (70.8°) y que el valle real es más somero que el de las falsas. Pero también notó que el salto en grados se infla cuando el radio es pequeño: el mayor salto de Mozart es C5→C6 (65.3°), justo donde el radio toca fondo. Propuso por ello un residual de fase pesado por radio. Con ese control: el mayor |residual pesado| de Mozart es C9→C10 (−35.27), bajo la mediana de las falsas (45.42); en Napoleón, C1→C2 (−17.62), bajo la mediana (32.64); el Brumario queda en +11.46 y C8→C9 en +11.01, dentro del ruido. El propio externo señaló una debilidad: su nulo era demasiado suelto, porque las fases de sus falsas eran menos lineales que las reales.

Grok Bot repitió el control con 1000 nulos por tipo, condicionados a R² de fase ≥ real:

| Caso | Paso que maximiza | A firmado | Percentil del mismo paso (RW condicionado) | N aceptado | p del máximo de pasos | p Holm (15 máximos) |
|---|---|---:|---:|---:|---:|---:|
| Mozart | C9→C10 | −0.6157 | 100.0 | 64 | 0.0154 | 0.2308 |
| Galileo | C7→C8 | +0.2898 | 100.0 | 711 | 0.0506 | 0.6573 |
| Hawking | C5→C6 | −0.3911 | 92.3 | 272 | 0.0806 | 0.9670 |
| Che | C1→C3 | −0.4681 | 15.7 | 559 | 0.8482 | 1.0000 |
| MLK | C1→C2 | −1.1207 | 97.7 | 88 | 0.0337 | 0.4719 |

*Tabla 2. En las cinco filas se muestra el nulo de caminata gaussiana condicionado a R² de fase ≥ R² real. A es el arco residual firmado; el paso se selecciona por su magnitud absoluta. El percentil compara el mismo slot real con el mismo slot de las réplicas aceptadas. En cambio, p y p Holm se calculan con el máximo de todos los pasos de cada réplica; Holm abarca los 15 máximos (5 casos × 3 tipos de nulo).*

El resultado se reproduce en `control_nulo_v1/SENALES_POR_PASO.json`; los SHA-256 del script `senales_por_paso.py` y de `METODO_SENALES_POR_PASO.md` coinciden con los declarados por el resultado. El log de ejecución conserva los tamaños aceptados. El percentil 100 no significa p=0: significa que ninguna réplica aceptada de ese slot superó el valor real. Ninguno de los cinco máximos pasa Holm15. El menor p sin ajustar es Mozart (0.0154), pero queda en 0.2308 tras Holm. En Mozart, C8→C9 da A=+0.1922 frente a +0.0673 en C5→C6; al permitir que la falsa elija cualquier paso, C8→C9 deja de ser excepcional (p≈0.969). Che C7→C8 destaca por distancia euclidiana frente a caminata aleatoria (Holm≈0.015), pero no frente a permutación ni iid; depende del nulo elegido.

El Brumario de Napoleón conserva residual +50.54° y A=+0.2001 en el CSV externo. El nulo condicionado original acepta solo 8 permutaciones geométricas 2D: es BAJA_MUESTRA y no constituye un control familiar. El nuevo crudo_P permite análisis de familias, pero no fue incorporado retrospectivamente a esta Tabla 2 ni a sus 15 comparaciones. Para extender el contraste inferencial a Napoleón hace falta una corrida nueva con su matriz de 244 familias, sin mezclarla con el resultado 2D anterior. Conclusión acotada: **no hay señal común robusta acreditada en los controles ejecutados**. En esta versión, el C10 de Mozart cae en 1788.34 = Z90, por lo que el estancamiento final es anterior a Z y no viola el sellado. Aclaración sobre la figura de `geometria_existente_v1/MOZART_10_TRAYECTORIA.png` (primer intento): su eje de años usa fechas reconstruidas de la corrida U10 (octubre de 2026), con C10 = 1791-12-31 como cierre convencional posterior a la muerte; por eso muestra puntos en 1790–1792 y su propio archivo de datos marca C8–C10 como DESPUES_Z90. Esas fechas no son las de la entrada sellada: en la entrada `MOZART_FRESH_Z90_U6_20261014` los diez cortes terminan el 1788-05-04 = Z90 y ninguno es posterior. No hay fuga en la entrada del motor; el eje de esa figura es una reconstrucción y debe leerse como tal.

![Figura 5. Percentiles del arco residual por paso frente a cada nulo. La línea punteada (95) es descriptiva, no el umbral corregido.](SENALES_POR_PASO.png)

### 3.7 Auditoría de datos

En Che, C3 (1953) aparece antes que C2 (1954). No era un error: el original no traía fechas; C2 corresponde a estudios 1948–1953 y C3 al viaje de 1951–1952. Los cierres están ordenados y los tokens intactos. Las fechas usadas son, por tanto, reconstruidas.

En Napoleón, el campo `motor.annex.traza_P.crudo_P` del RESULT fresco contiene 244 familias con diez valores cada una. El subconjunto suministrado coincide con el campo del RESULT completo. Al proyectar ese crudo con `proyeccion_tusi_modelo_externo.py`, las diez coordenadas x/y reproducen el CSV externo a cuatro decimales. Por tanto, Napoleón sí es evaluable en familias dominantes; lo que sigue pendiente es rehacer su control nulo familiar, no obtener el crudo.

## 4. Verificación cruzada como valor metodológico

La secuencia de quién detectó qué es, en sí, el resultado más útil:

- **El modelo externo** propuso la proyección, las métricas y una lectura positiva (giro de ~2/3 de vuelta, contracción, salto).
- **Grok Bot** no pudo reproducirla con la geometría propia del motor; en lugar de declarar un desacuerdo, pidió el código y el CSV y fijó una compuerta de reproducción numérica (Mozart a < 0.00005°) antes de extender.
- **Mj** introdujo restricciones de diseño (nada ajustado a un caso entra al motor; la capa no alimenta H) y una hipótesis sustantiva (rubro dominante), que fue evaluada y descartada.
- **Grok Bot** identificó el mecanismo del artefacto (rotación → ~180° base; centrado → U; y_inicio = y_fin por construcción).
- **El modelo externo** confirmó el artefacto en sus propias tablas y con trazas falsas, y se corrigió explícitamente. Luego aportó una mejora metodológica propia (residual pesado por radio) y señaló la debilidad de su nulo.
- **Grok Bot** endureció ese control (nulos múltiples, condicionamiento por R², corrección de Holm) y obtuvo un resultado negativo.

Ninguno de los dos modelos llegó solo a la conclusión final. La lectura positiva inicial habría sobrevivido sin el intento de reproducción; el artefacto se identificó porque la reproducción exacta permitió mirar las tablas de ambos con la misma transformación. A la vez, el residual pesado por radio, que desactivó la lectura del salto de Mozart, vino del modelo que había propuesto la lectura. La utilidad del esquema no viene de que un modelo “audite” al otro, sino de compartir datos y código, exigir reproducción exacta antes de interpretar y aceptar correcciones en ambas direcciones.

## 5. Discusión

**Artefactos de normalización.** La enseñanza central es que una proyección con normalización geométrica (centrado + rotación a un eje definido por los extremos) impone estructura: un giro base, una coordenada transversal igual en los extremos y un radio en U. Cualquier “forma” sobre esa proyección debe compararse con nulos sometidos a la misma transformación, no con una expectativa ingenua. Además, los nulos deben parecerse a los datos en las propiedades que la métrica explota (aquí, la linealidad de la fase); de lo contrario son demasiado sueltos.

**Límites.**
- *Siete trayectorias geométricas*: seis tienen crudo_P disponible tras esta revisión; sin embargo, la Tabla 2 se ejecutó originalmente sobre cinco casos con crudo_P. Napoleón fue añadido al análisis descriptivo de familias, pero todavía no al control nulo familiar. Hawking de siete cortes continúa como CSV externo/proxy.
- *PCA por caso*: los ejes no son comparables en valor entre casos; solo cantidades internas.
- *Fechas reconstruidas* (p. ej., Che) que afectan ω y los residuales de fase.
- *Mozart no fiel*: la corrida de 10 cortes usada aquí no coincide con la original de septiembre.
- *Napoleón*: el control original fue geométrico 2D, condicionado con N=8; no es un nulo familiar y no debe usarse para afirmar ausencia de señal en crudo_P. El nuevo análisis familiar es descriptivo; falta añadir Napoleón a una corrida de nulos de 244 familias.
- *Etiqueta “forma”*: definida a partir de los dos primeros casos, por lo que es circular respecto a ellos.

**Sobre los ~220°.** Mj relacionó la cifra de ~220° con el sistema de situaciones dramáticas de Étienne Souriau (6 funciones dramáticas; 210,141 situaciones; 7,780 configuraciones según el libro frente a 7,783 en una reconstrucción propia no demostrada; Odanaka ha cuestionado cómo se obtuvo la cifra original) y con un fondo de modelos dinámicos (Markov, SINDy, Laplace, cliodinámica). La discusión concluyó que el número de grados es propiedad del método y no puede vincularse a Souriau; lo que sí tiene sentido es comparar *espacios de configuraciones admisibles*. Se empezó a calcular el límite teórico del giro bajo el método, pero Mj lo apartó: con siete casos no hay datos para calibrarlo y la prioridad es aumentar los casos.

## 6. Trabajo futuro

1. **Más casos**, idealmente con crudo_P completo y cortes fieles a las corridas originales, antes de cualquier nueva interpretación.
2. **Límite teórico del giro** bajo centrado + rotación por extremos, en función de n y de la estructura de la serie, para usarlo como nulo analítico.
3. **Dinámica explícita**: modelos de transición tipo Markov entre familias o identificación de ecuaciones dispersas (SINDy) sobre crudo_P, que no dependan de una proyección con normalización por extremos.
4. **Souriau como espacio admisible**: formalizar el espacio de configuraciones de familias narrativas y comparar su tamaño y estructura con lo que la traza P recorre, sin recurrir a cifras angulares.
5. **Proyección común** entre casos (ejes compartidos) para permitir comparaciones en valor y no solo en forma.

## 7. Conclusión

La pregunta del título tiene una respuesta provisional. El giro cercano a 180°, la igualdad de la coordenada transversal en los extremos y la U del radio son consecuencias del método de proyección, no evidencia de una forma de vida. El arco residual no supera Holm15 en los cinco casos con crudo_P incluidos en la corrida original. Napoleón sí tiene crudo_P y su análisis de familias ya fue corregido: la rivalidad encabeza el incremento del salto, mientras que PC1 y la familia dominante por media difieren de Mozart. Como el nulo familiar de Napoleón aún no se ha ejecutado, la conclusión negativa no debe extenderse a ese contraste pendiente. No hay evidencia actual de una forma de vida común en esta capa, pero tampoco evidencia de que no exista; la muestra y los controles disponibles no permiten afirmarlo. La capa sigue fuera de H, del ranking y de la apuesta del motor.

---

*Materiales: scripts, tablas, resultados JSON, registros de prueba y figuras en* <https://github.com/marcojpad-hash/motor-u6-storage/tree/alterno/cameo-pesos/casos/trayectoria_forma>. *La revisión de este manuscrito se guarda en un commit aislado que modifica únicamente `paper/paper.md`; el experimento y los archivos CAMEO no se modifican.*
