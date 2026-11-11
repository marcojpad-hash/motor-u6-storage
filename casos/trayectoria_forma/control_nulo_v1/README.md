# Control nulo de PC12 rotadas

> **Actualización pedida por Mj:** giro global, y_inicio=y_fin y radio en U se consideran artefactos del método, **NO señal**. Los candidatos vigentes son innovación de fase × radio medio y profundidad transversal: [SENALES_POR_PASO.md](SENALES_POR_PASO.md). Incluye nulo de fase al menos tan lineal, focos Mozart/Napoleón y auditoría de fechas Che. Las tablas de giro/forma debajo quedan como diagnóstico histórico, no criterio de señal.
>
> Hallazgo local: Mozart C9→C10 A=−0.6157, P100 entre64 RW de fase suficientemente lineal, pero p máximo=.0154 y Holm15=.2308. C8→C9 A=+.1922 frente C5→C6 +.0673; su rareza desaparece al permitir buscar cualquier paso (p≈.969). Napoleón Brumario A=+.2001, menor en magnitud que C1→C2 −.3074; su condicionado geométrico acepta8 y es insuficiente. Valles no excepcionalmente profundos. Che fechas son reconstruidas/ordenadas por cierre; 1953/1954 en tabla son redondeos de1952-12-31/1953-12-31.

**Ejecutado:** cinco casos con crudo_P, 1000 permutaciones +1000 caminatas gaussianas +1000 iid por caso: **15,000 réplicas emparejadas en N/244 familias**. Sin Engine nuevo, sin pesos, H/ranking/apuesta. Se conserva la transformación y las métricas del experimento PC12 previo. Seed maestro 202611110503; seeds por celda y hashes en RESULTADOS.json. No se reintentaron muestras para mejorar resultados.

## Resultado principal

**El giro alrededor de dos tercios de vuelta NO distingue los casos del nulo.** Los giros reales ocupan percentiles medios de permutación/iid; las caminatas sin biografía generan de por sí un pico alrededor de 220–240°. No existe una cota matemática universal ≥180°: solo ≈59–63% de permutación/iid supera 180°, frente a 98–100% de caminatas. Por tanto la semejanza del giro es compatible con un efecto de geometría y suavidad temporal; no es evidencia de una ley biográfica ni aísla causalmente cada paso sin una ablación adicional.

La forma completa del criterio anterior aparece en4/5 reales, frente a3.5–30.2% por caso en estos nulos. Se conserva como diagnóstico histórico; no se usa ese compuesto, que incluye artefactos geométricos, para sostener señal. Casos y criterio post-hoc, sin validación independiente.

P=permutación de filas completas, RW=caminata gaussiana por familia, IID=ruido gaussiano independiente. Percentil midrank, no probabilidad del futuro.

| Caso | N | Giro real° | Percentil giro P / RW / IID | %nulos forma P / RW / IID | Forma real |
|---|---:|---:|---|---|---|
| MOZART10 | 10 | 222.45 | 54.9 / 29.8 / 44.6 | 15.2 / 26.3 / 8.4 | SÍ |
| GALILEO | 10 | 240.74 | 47.8 / 76.0 / 50.1 | 16.2 / 30.2 / 9.9 | SÍ |
| HAWKING6 | 6 | 221.41 | 52.2 / 33.2 / 51.9 | 5.2 / 10.1 / 3.5 | SÍ |
| CHE | 9 | 225.75 | 55.4 / 32.2 / 49.7 | 12.3 / 20.1 / 8.0 | SÍ |
| MLK | 8 | 215.61 | 58.1 / 5.8 / 46.9 | 11.7 / 17.9 / 6.9 | NO |

## Todas las métricas: percentil del valor real en cada nulo

b y R² se informan **solo entre ajustes de radio identificables** (prefijo no creciente, al menos 3 cortes); se incluye el % de ajuste válido para no ocultar esa selección. El radio no es fit universal. Los percentiles de seno son dentro de muestra con frecuencia elegida sobre la misma grilla2048 tanto en reales como nulos.

| Caso | Nulo | %ajuste radio válido | Pct giro | Pct b | Pct R² radio | Pct seno |
|---|---|---:|---:|---:|---:|---:|
| MOZART10 | P | 17.0 | 54.9 | 1.8 | 32.4 | 93.7 |
| MOZART10 | RW | 76.2 | 29.8 | 31.4 | 58.7 | 43.4 |
| MOZART10 | IID | 15.3 | 44.6 | 3.9 | 45.1 | 94.9 |
| GALILEO | P | 16.8 | 47.8 | 64.3 | 37.5 | 95.1 |
| GALILEO | RW | 69.4 | 76.0 | 87.8 | 17.9 | 34.0 |
| GALILEO | IID | 13.7 | 50.1 | 51.8 | 40.9 | 95.6 |
| HAWKING6 | P | 18.2 | 52.2 | 86.8 | 65.9 | 84.7 |
| HAWKING6 | RW | 82.1 | 33.2 | 66.0 | 72.7 | 85.9 |
| HAWKING6 | IID | 15.5 | 51.9 | 51.6 | 76.8 | 90.3 |
| CHE | P | 16.0 | 55.4 | 21.2 | 42.5 | 97.8 |
| CHE | RW | 92.4 | 32.2 | 5.1 | 87.6 | 39.7 |
| CHE | IID | 16.1 | 49.7 | 8.1 | 70.2 | 99.4 |
| MLK | P | 16.4 | 58.1 | 39.0 | 20.7 | 97.2 |
| MLK | RW | 91.2 | 5.8 | 10.1 | 32.2 | 94.1 |
| MLK | IID | 18.8 | 46.9 | 14.9 | 43.6 | 96.8 |

- La contracción inicial identificable aparece en ≈69–92% de caminatas sin historia, frente a ≈14–19% de permutaciones/iid. Además b>0 está condicionado por elegir un prefijo no creciente: no es un hallazgo independiente de contracción.
- Los R² de radio reales no son extremos altos de los nulos condicionados al ajuste; un buen R² con tres puntos y dos parámetros puede salir sin señal biográfica.
- El seno de varios casos sí queda alto frente a destruir el orden/iid (≈94–99 percentiles), pero resulta ordinario frente a caminatas, salvo MLK relativamente alto. Señala suavidad/orden temporal frente a iid, no identifica una hélice especial ni predictibilidad.
- Permutaciones preservan estados y covarianza entre familias; RW/iid solo medias y varianzas esperadas por familia, no covarianza. No son hipótesis nulas equivalentes. Los cocientes medios de varianza simulada/observada van de .992 a 1.005; permutación=1 exacto.
- Hawking6 admite solo 6!=720 órdenes posibles; 1000 réplicas con reemplazo no equivalen a 1000 órdenes diferentes. Los conteos únicos están guardados por caso.

## ¿Son informativos el corte y la familia del salto?

Salto y familia se eligen con la MISMA regla en cada réplica. Fuerza=longitud del salto/mediana de longitudes; subida familiar=max(delta/sigma_observada) entre TODAS las familias del salto. Los percentiles y colas de salto/subida se condicionan a las réplicas con salto operacional, no se convierten ausencias en cero; `salto_pct` y los denominadores válidos están en JSON. Se conserva el mayor incremento crudo y todos sus empates para identidad. Hay 12 contrastes principales por estadístico (4 casos con salto×3 nulos); p superiores corregidos por Holm por separado.

| Caso | Slot real del salto | Familia(s) con mayor delta crudo |
|---|---|---|
| MOZART10 | C8→C9 | 24_rivalidad_de_superior_e_inferior |
| GALILEO | G_C7→G_C8 | 8_rebelion |
| HAWKING6 | C4→C5 | arquetipo_el_gobernante, monomito_12_regreso_con_el_elixir |
| CHE | C7→C8 | eterno_retorno_02_cosmizacion_fundacion, tainter_01_inversion_complejidad_productiva |
| MLK | — | N/D: sin salto operacional |

| Caso | Nulo | Pct fuerza salto | p Holm salto | Pct máximo delta/σ | p Holm subida | %mismo slot entre nulos con salto | %misma familia entre nulos con salto |
|---|---|---:|---:|---:|---:|---:|---:|
| MOZART10 | P | 96.45 | 0.2593 | 8.19 | 1.0000 | 11.90 | 0.62 |
| MOZART10 | RW | 99.71 | 0.0581 | 97.96 | 0.2791 | 31.20 | 3.21 |
| MOZART10 | IID | 98.66 | 0.1224 | 6.51 | 1.0000 | 14.18 | 3.83 |
| GALILEO | P | 91.08 | 0.3625 | 2.97 | 1.0000 | 13.30 | 34.43 |
| GALILEO | RW | 95.48 | 0.2593 | 87.44 | 1.0000 | 22.36 | 21.61 |
| GALILEO | IID | 95.96 | 0.2593 | 5.66 | 1.0000 | 13.13 | 20.20 |
| HAWKING6 | P | 46.35 | 1.0000 | 11.11 | 1.0000 | 22.22 | 0.29 |
| HAWKING6 | RW | 43.50 | 1.0000 | 29.60 | 1.0000 | 42.60 | 8.07 |
| HAWKING6 | IID | 43.22 | 1.0000 | 2.20 | 1.0000 | 19.41 | 10.26 |
| CHE | P | 99.60 | 0.0581 | 26.58 | 1.0000 | 14.62 | 29.25 |
| CHE | RW | 100.00 | 0.0505 | 93.09 | 0.8073 | 47.93 | 13.36 |
| CHE | IID | 100.00 | 0.0271 | 1.36 | 1.0000 | 20.41 | 12.02 |

**Lectura:** el slot del salto aparece con frecuencia comparable bajo nulos (≈12–48% entre nulos con salto); su ubicación sola no es una rareza convincente. El salto relativo de **Che** es más grande que iid incluso con Holm (**p≈.0271**), pero no se sostiene uniformemente frente a permutación/RW (≈.0581/.0505; resolución Monte Carlo limitada). Mozart también muestra saltos altos en percentil, sin superar la corrección.

**Ninguna amplitud máxima de subida familiar supera Holm .05** (mínimo p ajustado≈.279). Algunas identidades son poco frecuentes, p.ej. rivalidad en Mozart ≈.62% de permutaciones con salto; eso NO es un p-value semántico: el nombre fue elegido tras ver qué familia ganó entre 244. No se concluye que la familia del salto aporte información causal o predictiva sobre un desenlace. Se necesitaría fijar familia/criterio antes y validar en casos nuevos. MLK no tiene salto bajo la regla: no se le inventa una familia.

## Conteo conjunto, solo exploratorio

Los reales cumplen forma en 4/5. Bajo simulaciones independientes por caso:

| Nulo | Réplicas con ≥4/5 | p superior MC +1 |
|---|---:|---:|
| P | 1/1000 | 0.0020 |
| RW | 6/1000 | 0.0070 |
| IID | 1/1000 | 0.0020 |

Este conteo es raro bajo esos generadores independientes, pero **casos/criterio post-hoc e independencia real no demostrada** impiden tratarlo como validación confirmatoria. Que el giro sea genérico no implica que todos los detalles ordenados sean ruido; que el conjunto sea raro bajo estos nulos tampoco prueba la hipótesis de ambición ni una fórmula universal.

## Hawking externo de siete cortes, sin años

CSV preservado en `../coordenadas_modelo_externo/tabla_coordenadas_hawking_7cortes.csv`: 7 puntos, giro 222.5°; el nuestro tiene 6 y 221.41°. **Con el mismo criterio estricto, el externo H7 NO cumple la forma completa**: el salto que sigue al valle no cruza un eje; no se cambió el criterio para hacerlo coincidir. El giro similar por sí solo no garantiza la misma forma operacional.

No hay crudo_P de H7 ni años. No se reconstruyeron 244 familias ni fechas:
- **Permutación geométrica2D, 1000:** el subespacio PC12 se conserva al permutar filas. Desde sus coordenadas se identifican los nulos de radio, giro absoluto y seno hasta reflexión, pero no la handedness que elegiría el SVD completo. Se reportan límites para %forma en vez de un porcentaje exacto de crudo_P. La prueba de equivalencia de subespacio/invariantes pasa sobre matrices sintéticas de dimensión completa. Supone PC2/PC3 no degeneradas: esa brecha no puede verificarse sin su crudo_P. Radios/fases externos redondeados implican aproximaciones y pueden alterar empates/percentiles finos, especialmente b; no es un gate del RESULT ausente.
- **RW/IID, 1000 cada uno:** PROXIES N=7/244 familias con varianzas de H6; no son controles emparejados propios de H7. Tiempo=índice de corte, b en 1/corte. Nada de esto sustituye su RESULT ausente.
- Familia del salto H7: N/D. No participa en Holm ni en el conteo conjunto de cinco casos.

| H7 nulo/proxy | Pct giro | Pct b | Pct R² radio | Pct seno | %forma nulo |
|---|---:|---:|---:|---:|---|
| caminata_gaussiana | 32.1 | 64.8 | 95.8 | 34.0 | 18.7 (proxy H6) |
| iid_gaussiano | 51.7 | 41.5 | 97.3 | 95.1 | 3.1 (proxy H6) |
| permutacion_geometria2D | 55.6 | 100.0 | 94.9 | 96.0 | 0.0–14.6 (límite orientación) |

## Archivos, pruebas y límites

- `control_nulo.py`: generación, proyección, métricas, percentiles, Holm, histograma; no altera fuentes.
- `METODO.md`: definiciones y limitaciones fijadas antes de simular cada variante. Varianzas Gaussianas iguales EN ESPERANZA; no se reescaló cada realización para forzar su varianza o forma.
- `RESULTADOS.json`: reales, resúmenes, seeds, fuentes/hashes, conteos de orden únicos, ajustes fallidos, identidades y p ajustados.
- `DISTRIBUCIONES.npz`: métricas de todas las muestras, NaN conservados para no-ajuste, posiciones y forma.
- `GIRO_REAL_VS_NULOS.png`: un PNG con cinco casos principales y apéndice H7.
- `TESTS.log`: **11 pruebas OK** (7 del control original y4 locales), incluyendo caché OLS vs ajuste original, invariancia de permutaciones, constantes, factor de varianza RW, midrank/Holm y equivalencia geométrica 2D.
- La caché del seno se contrastó además en cada grilla real y tres vectores independientes por caso; error <1e-7 puntos porcentuales. No se cambió la grilla de frecuencias.
- Integridad: 135 archivos protegidos intactos; Engine/244 y `motor/motor/*.py` sin cambios. No se ejecutó nuevamente el Engine. La fuente Mozart es la traza del gate reproducido; el runner de aquella corrida había quedado exit4 por un campo ausente, como ya se documentó. No se declara ahora una corrida predictiva aprobada.

Reproducir:
```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 python3 casos/trayectoria_forma/control_nulo_v1/control_nulo.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s casos/trayectoria_forma/control_nulo_v1 -p test_control_nulo.py -v
```

**Conclusión vigente:** no usar giro, y_inicio=y_fin ni radio en U como señal. El análisis local/condicionado y Che están en `SENALES_POR_PASO.md`: no se acreditó una señal común robusta a los nulos y multiplicidad. No se demostró información familiar predictiva. Sin push.
