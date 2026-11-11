# Candidatos locales: arco residual y valle, no artefactos globales

**No se tratan como señal giro total, y_inicio=y_fin ni radio en U.** Aquí se mide innovación de fase × radio medio y desplazamiento cartesiano, frente al nulo por **cada slot**, y valle frente al nulo. Nada entra al Engine/H/ranking/apuesta. Todo es retrospectivo y exploratorio. PCA por caso: ejes y magnitudes absolutas NO son comparables entre casos; se contrasta cada real solo con sus propios nulos.

## Definición exacta

OLS por cada real y falsa sobre todos sus cortes: phi=a+omega·t. epsilon_i=delta_phi_i−omega·delta_t_i; rmedio_i=(r_i+r_{i+1})/2. Se conserva **A_i=rmedio_i·epsilon_i**, firmado (radianes×unidad PC12), y se compara **|A_i|** con falsas del mismo slot. Negativo=menos avance que la tendencia, no movimiento euclidiano grande. También distancia=hypot(delta_x,delta_y). Este arco residual no es la distancia real del paso ni una velocidad.

El omega es OLS propio, **no** giro neto/duración: Mozart≈9.3967°/año, Napoleón CSV≈7.2447°/año. Por eso la expectativa puede diferir de cifras antiguas calculadas con otro estimador. La ponderación no es un peso del motor.

Se comparan 1000 falsas por nulo/caso, mismas semillas del control original. Para el nulo más estricto se **seleccionan** de ese pool las falsas con R² de fase >= al real. Se informa cuántas sobreviven: NO son otras1000. No se empareja omega. Esto evalúa si el residual sigue siendo raro entre fases al menos tan lineales, no entre historias necesariamente equivalentes.

## Los cinco casos: valle y máximo arco residual

P/RW/IID=permutación/caminata/iid. P profundidad es rango de −min(y), mayor=más profundo; el min_y firmado y su percentil están también en JSON (rangos complementarios). El máximo se refiere a |A| de todo el caso, no al salto de la forma operacional anterior.

| Caso | R² fase real | min_y | P profundidad P / RW / IID | Paso máximo | A firmado | P de ese slot RW | P RW condicionado (n) | p máximo RW condicionado / Holm15 |
|---|---:|---:|---|---|---:|---:|---|---|
| MOZART10 | 0.9537 | -0.1736 | 7.3 / 4.3 / 2.4 | C9→C10 | -0.6157 | 89.8 | 100.0 (64) | 0.0154 / 0.2308 |
| GALILEO | 0.9181 | -0.2185 | 45.0 / 37.9 / 14.0 | G_C7→G_C8 | +0.2898 | 99.8 | 100.0 (711) | 0.0506 / 0.6573 |
| HAWKING6 | 0.9247 | -0.2518 | 30.6 / 67.9 / 30.0 | C5→C6 | -0.3911 | 77.1 | 92.3 (272) | 0.0806 / 0.9670 |
| CHE | 0.9475 | -0.4282 | 41.4 / 71.1 / 34.2 | C1→C3 | -0.4681 | 11.4 | 15.7 (559) | 0.8482 / 1.0000 |
| MLK | 0.9118 | -0.4386 | 58.0 / 68.1 / 33.0 | C1→C2 | -1.1207 | 91.2 | 97.7 (88) | 0.0337 / 0.4719 |

No hay valle excepcionalmente más profundo: los rangos de profundidad son ordinarios o bajos, con Mozart más somero, no más profundo. La handedness SVD es arbitraria: por eso el JSON incluye además max(abs(y)), invariante a reflexión. Ningún máximo de arco residual condicionado supera Holm15 .05. Esto no prueba ausencia de toda estructura, solo que aquí no se acreditó una anomalía robusta entre esos generadores.

## Focos que pidió Mj

| Caso/paso | Delta fase° | Esperado OLS° | Residual° | Radio medio | A firmado | Distancia PC12 |
|---|---:|---:|---:|---:|---:|---:|
| MOZART10 C5→C6 | 65.32 | 42.58 | +22.74 | 0.16971 | +0.0673 | 0.1876 |
| MOZART10 C8→C9 | 51.50 | 22.45 | +29.05 | 0.37913 | +0.1922 | 0.3863 |
| MOZART10 C9→C10 | 1.04 | 64.90 | -63.86 | 0.55234 | -0.6157 | 0.1227 |
| NAPOLEON_CSV C1→C2 | 19.20 | 46.15 | -26.95 | 0.65365 | -0.3074 | 0.3650 |
| NAPOLEON_CSV C4→C5 | 76.40 | 25.86 | +50.54 | 0.22685 | +0.2001 | 0.3037 |

| Caso/paso | Nulo | P | P condicionado R²fase≥real | N condicionado | p vs máximo de pasos nulo condicionado |
|---|---|---:|---:|---:|---:|
| MOZART10 C5→C6 | permutacion | 9.8 | 25.0 | 4 | 1.0000 |
| MOZART10 C5→C6 | caminata_gaussiana | 55.4 | 70.3 | 64 | 1.0000 |
| MOZART10 C5→C6 | iid_gaussiano | 14.5 | 33.3 | 3 | 1.0000 |
| MOZART10 C8→C9 | permutacion | 24.6 | 25.0 | 4 | 1.0000 |
| MOZART10 C8→C9 | caminata_gaussiana | 93.8 | 100.0 | 64 | 0.9692 |
| MOZART10 C8→C9 | iid_gaussiano | 28.4 | 33.3 | 3 | 1.0000 |
| MOZART10 C9→C10 | permutacion | 56.7 | 75.0 | 4 | 1.0000 |
| MOZART10 C9→C10 | caminata_gaussiana | 89.8 | 100.0 | 64 | 0.0154 |
| MOZART10 C9→C10 | iid_gaussiano | 74.0 | 100.0 | 3 | 0.5000 |
| NAPOLEON_CSV C1→C2 | permutacion_geometria2D | 29.7 | 50.0 | 8 | 1.0000 |
| NAPOLEON_CSV C4→C5 | permutacion_geometria2D | 25.4 | 25.0 | 8 | 1.0000 |

**Mozart:** C8→C9 tiene menor giro angular que C5→C6 (51.50° vs65.32°), pero mayor innovación ponderada (0.1922 vs0.0673) por mayor radio. Frente a RW condicionado ambos C8→C9 y C9→C10 dan percentil100, **NO** probabilidad cero. Para C8→C9, al permitir cualquier paso de la falsa, p≈.969: no es raro encontrar algún residual así. El estancamiento final C9→C10 es el mayor |A|=0.6157, negativo; entre64 RW suficientemente lineales no hay un máximo mayor (p +1≈.0154), pero Holm15≈.2308. Es candidato exploratorio, no señal robusta acreditada. Contra permutación/iid no condicionados esos slots no son extremos, y sus condicionados tienen solo4/3 falsas: BAJA_MUESTRA.

**Napoleón:** Brumario C4→C5 sí tiene76.4° brutos, pero residual+50.54° y A=+0.2001. C1→C2 tiene solo19.2° brutos, residual−26.95° y **mayor magnitud ponderada** A=−0.3074. Brumario no es más extraordinario por ese criterio. Solo hay CSV: permutación geométrica2D (1000), no familias; el condicionado acepta **8**, BAJA_MUESTRA. Rangos condicionados25/50 son meramente descriptivos y no sostienen significancia. No se inventó un RW de familias de Napoleón.

## Todos los pasos reales, sin seleccionar solo los favorables

P en magnitud de arco residual; E=percentil de distancia euclidiana. Se conservan signos y tiempos en JSON.

| Caso | Paso | A firmado | P P / RW / IID | E P / RW / IID | P RW condicionado |
|---|---|---:|---|---|---:|
| MOZART10 | C1→C2 | +0.0177 | 1.7 / 19.3 / 2.3 | 14.8 / 68.3 / 13.7 | 20.3 |
| MOZART10 | C2→C3 | +0.0566 | 6.4 / 33.4 / 8.3 | 10.4 / 27.2 / 8.6 | 56.2 |
| MOZART10 | C3→C4 | -0.1144 | 14.1 / 28.7 / 23.7 | 18.4 / 72.5 / 24.0 | 53.1 |
| MOZART10 | C4→C5 | -0.0223 | 3.4 / 20.8 / 3.1 | 5.1 / 9.4 / 3.9 | 28.1 |
| MOZART10 | C5→C6 | +0.0673 | 9.8 / 55.4 / 14.5 | 16.2 / 70.6 / 16.7 | 70.3 |
| MOZART10 | C6→C7 | +0.0339 | 3.3 / 8.8 / 4.6 | 1.2 / 4.0 / 2.0 | 20.3 |
| MOZART10 | C7→C8 | -0.0215 | 2.9 / 7.1 / 2.1 | 2.9 / 6.6 / 3.5 | 14.1 |
| MOZART10 | C8→C9 | +0.1922 | 24.6 / 93.8 / 28.4 | 36.4 / 100.0 / 59.6 | 100.0 |
| MOZART10 | C9→C10 | -0.6157 | 56.7 / 89.8 / 74.0 | 8.1 / 54.4 / 6.6 | 100.0 |
| GALILEO | G_C1→G_C2 | -0.0856 | 12.2 / 24.6 / 11.8 | 37.2 / 99.7 / 58.1 | 27.4 |
| GALILEO | G_C2→G_C3 | +0.0265 | 2.8 / 8.4 / 3.5 | 26.5 / 88.3 / 31.6 | 10.4 |
| GALILEO | G_C3→G_C4 | +0.0144 | 1.7 / 13.4 / 2.5 | 13.7 / 26.6 / 8.1 | 16.2 |
| GALILEO | G_C4→G_C5 | -0.0586 | 8.4 / 50.7 / 11.5 | 8.0 / 7.1 / 3.5 | 55.1 |
| GALILEO | G_C5→G_C6 | -0.0985 | 12.4 / 76.9 / 20.6 | 3.1 / 1.9 / 1.2 | 81.9 |
| GALILEO | G_C6→G_C7 | -0.0485 | 5.2 / 34.0 / 6.1 | 0.9 / 1.3 / 0.2 | 33.6 |
| GALILEO | G_C7→G_C8 | +0.2898 | 34.8 / 99.8 / 45.5 | 32.2 / 99.3 / 51.8 | 100.0 |
| GALILEO | G_C8→G_C9 | +0.0551 | 8.6 / 37.8 / 6.3 | 20.8 / 53.7 / 12.2 | 43.6 |
| GALILEO | G_C9→G_C10_Z90 | -0.0150 | 2.0 / 12.3 / 1.9 | 10.6 / 45.9 / 5.8 | 13.8 |
| HAWKING6 | C1→C2 | +0.0033 | 0.7 / 2.1 / 0.3 | 16.8 / 40.9 / 14.7 | 3.3 |
| HAWKING6 | C2→C3 | +0.1112 | 8.1 / 31.7 / 10.4 | 11.1 / 28.8 / 15.7 | 51.8 |
| HAWKING6 | C3→C4 | +0.1153 | 13.7 / 61.0 / 15.8 | 22.8 / 69.7 / 24.2 | 71.0 |
| HAWKING6 | C4→C5 | -0.0511 | 5.8 / 22.6 / 9.8 | 30.9 / 90.1 / 38.1 | 30.9 |
| HAWKING6 | C5→C6 | -0.3911 | 37.6 / 77.1 / 57.6 | 2.4 / 12.5 / 3.9 | 92.3 |
| CHE | C1→C3 | -0.4681 | 31.3 / 11.4 / 42.7 | 9.2 / 27.5 / 5.0 | 15.7 |
| CHE | C3→C2 | -0.1246 | 8.8 / 66.4 / 9.3 | 1.4 / 0.1 / 0.5 | 69.9 |
| CHE | C2→C4 | +0.0235 | 1.8 / 4.6 / 3.0 | 13.4 / 5.1 / 6.4 | 5.5 |
| CHE | C4→C5 | -0.0430 | 2.8 / 33.6 / 3.3 | 14.4 / 12.0 / 5.8 | 36.9 |
| CHE | C5→C6 | +0.2055 | 16.1 / 94.9 / 23.3 | 33.4 / 96.3 / 33.4 | 97.5 |
| CHE | C6→C7 | -0.0353 | 1.9 / 9.4 / 3.7 | 6.0 / 1.7 / 3.4 | 9.5 |
| CHE | C7→C8 | +0.2188 | 13.2 / 15.9 / 23.2 | 48.7 / 100.0 / 83.9 | 20.8 |
| CHE | C8→C9 | -0.2512 | 19.7 / 91.4 / 19.1 | 4.3 / 17.5 / 2.8 | 95.2 |
| MLK | C1→C2 | -1.1207 | 56.3 / 91.2 / 73.9 | 5.8 / 13.6 / 2.0 | 97.7 |
| MLK | C2→C3 | -0.1140 | 6.2 / 62.2 / 10.1 | 25.1 / 56.4 / 22.4 | 67.0 |
| MLK | C3→C4 | +0.5362 | 35.3 / 99.6 / 43.9 | 41.5 / 99.7 / 51.9 | 100.0 |
| MLK | C4→C5 | -0.0702 | 4.7 / 4.0 / 9.5 | 32.9 / 99.3 / 38.2 | 21.6 |
| MLK | C5→C6 | -0.0156 | 1.5 / 0.3 / 1.5 | 2.0 / 0.0 / 0.4 | 1.1 |
| MLK | C6→C7 | -0.0199 | 2.9 / 3.4 / 1.2 | 12.0 / 4.0 / 5.1 | 3.4 |
| MLK | C7→C8 | +0.1490 | 16.1 / 46.0 / 9.9 | 10.4 / 16.5 / 3.6 | 64.8 |

**Distancia euclidiana:** Mozart C8→C9 es alto frente a RW en su slot (P100), pero el máximo de todo el caso queda P99.4, p≈.00699, Holm15≈.0979. Che C7→C8 (d≈0.8742) sí supera máximos RW con Holm15≈.0150, **no** permutación/iid. No confundirlo con el residual de fase más grande de Che (C1→C3), ni con causalidad familiar. No hay resultado robusto común a todos los nulos. La familia que aumenta y el slot elegidos post-hoc siguen sin demostrar información causal/predictiva; véase el control de subidas familiares del README histórico.

## Tamaños del nulo de fase casi lineal

| Caso | R² mínimo | Aceptadas P / RW / IID de1000 |
|---|---:|---|
| MOZART10 | 0.9537 | 4 / 64 / 3 |
| GALILEO | 0.9181 | 58 / 711 / 56 |
| HAWKING6 | 0.9247 | 26 / 272 / 62 |
| CHE | 0.9475 | 20 / 559 / 31 |
| MLK | 0.9118 | 30 / 88 / 46 |

No se siguió simulando hasta obtener un resultado favorable: se entrega lo alcanzado del pool fijo. Los pools pequeños impiden resolución fina y no justifican una afirmación fuerte. Holm de pasos114 y de máximos15 son familias separadas, también separado el condicionado del no condicionado. Con1000 falsas, un P100 significa cero excedencias empíricas y p +1 al menos1/1001, no probabilidad cero. Requerir las mismas omega u otra dinámica sería otro nulo, no algo ya validado.

## CSV externos / Hawking7

Napoleón solo admite permutación de geometría conocida. Supone que PC2/PC3 no son degeneradas (no verificable sin su raw). Arco residual y distancia son invariantes a reflexión; la profundidad min_y no lo es: percentil Napoleón acotado0–59.8 según handedness desconocida, no dar punto preciso. La serialización redondeada añade incertidumbre pequeña.

Hawking7 queda en JSON y NPZ con su n=7 y tiempo=índice, no año: permutación geométrica2D y RW/iid **PROXY de varianzas H6**; condicionado acepta51/637/73 respectivamente. No son controles familiares propios ni permiten atribución de familia. No participa en Holm de los cinco casos. Su giro no se interpreta como señal.

## Che: ¿fecha u orden incorrecto?

Auditado `casos/calibracion_z90/CHE/entrada.json`, `PREPARACION_Y_SELLO.json`, original `casos/originales_z90/inputs/001_Ernesto_Che_Guevara_9f3baec1110e/_cuts_che_run.json` y tabla PC12.

- Original: lista **C1,C2,C3,...**, **sin date**. C2 describe estudios **c.1948–1953**; C3 viaje **1951–1952**. Los periodos se solapan: IDs no son fechas de cierre.
- Preparación reconstruyó por cierre de intervalos **C3=1952-12-31**, **C2=1953-12-31**, y documentó orden de ejecución **C1,C3,C2,...**. No es un nuevo reordenamiento del gráfico, ni se ha acreditado una errata histórica.
- Al redondear los años decimales a2 decimales aparecen **1953.00** y **1954.00**; NO significan fechas civiles1953/1954. Son1952.9993 y1953.9966 aproximadamente bajo el conversor del script.
- Fechas **RECONSTRUIDAS**, días exactos no verificados. La secuencia numérica de IDs puede inducir error de lectura; no se renumeró ni se alteraron hechos, tokens o pesos. Comparación por ID confirma que todos los campos originales excepto date se conservan idénticos. Resultado y hashes en `AUDITORIA_FECHAS_CHE.json`.

## Reproducir / integridad

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 python3 casos/trayectoria_forma/control_nulo_v1/senales_por_paso.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s casos/trayectoria_forma/control_nulo_v1 -p 'test_*.py' -v
```

`SENALES_POR_PASO.json` guarda todos los valores/percentiles por paso, profundidad firmada, submuestras condicionadas, máximos y multiplicidad; `SENALES_DISTRIBUCIONES.npz` guarda todas las falsas y máscaras de selección; `SENALES_POR_PASO.png` resume los rangos de arco residual. **11 tests OK**, 135 archivos protegidos intactos, sin ejecutar Engine. Los scripts nuevos solo escriben sidecars aquí. Sin H/ranking/apuesta y sin push.

**Conclusión:** los candidatos locales no confirman una ley común. El cierre Mozart es más interesante que su salto angular bruto bajo RW de fase lineal, pero no pasa el ajuste global; Brumario tampoco queda privilegiado al ponderar radio. El contraste depende del nulo; se necesita contraste independiente y, para Napoleón/H7, su raw auténtico. No se rescatan como señal los artefactos globales.
