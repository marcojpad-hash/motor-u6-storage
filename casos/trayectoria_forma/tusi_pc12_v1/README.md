# Trayectorias PC1/PC2 rotadas — seis casos

**Éste es el informe vigente.** Plano correcto del script de Mj: `motor.annex.traza_P.crudo_P`, familias ordenadas, centrado, SVD (`scores=U*S`), PC1/PC2 y rotación para C1→Cn horizontal. Generalizado a n cortes. El ejercicio anterior que daba 94.35° a Mozart retiraba el eje axial de una hélice: era OTRO plano y no sirve para comparar estas coordenadas.

Modo **TRAYECTORIA retrospectiva**, no predicción. **PCA por caso: solo forma comparable, no valores de ejes.** No se crean pesos ni se alimenta H, ranking o apuesta. Los loadings con signo son coeficientes geométricos externos, no pesos ni probabilidades del Engine. Engine/244 y `motor/motor/*.py` intactos.

## Gate Mozart

No existía el RESULT exacto del otro modelo. Se corrió el estándar sobre la copia byte-a-byte de `casos/precedentes/MOZART_10_CORTES/INPUT_FROZEN.json`, sin `--no-mc`, con StinkBox y CEB aislados localmente.

**Gate geométrico PASA al redondeo publicado del CSV:**
- Giro de la nueva traza: **222.452500°**; diferencia frente a restar los extremos redondeados del CSV (222.4°): **+0.052500°**.
- Máximo error x/y/r: **0.00004952**; fase: **0.04885°**; año: **0.004470**. Son menores a la media unidad de impresión del script original: coordenadas/radio .4f, fase .1f, año .2f.
- Se verifica toda la tabla, no solo un giro parecido. La generalización produce los mismos cinco arrays que la función `load()` del script fiel, a tolerancia 1e-12 en las pruebas.
- También coincide la forma operacional del CSV y del rerun: cresta→valle→salto C8→C9→subida.

**La corrida estándar NO es una corrida limpia aprobada:** el motor y Monte Carlo sí ejecutaron (30 observaciones, 17,918 simulaciones, 30 convergidas), pero el runner terminó **exit 4 / INCOMPLETE_OUTPUT_DATA**, por `$.efectividad_corte_retenido.previo_error` ausente. No se lo oculta, no se declara calibración predictiva válida y no se alteró el runner para convertirlo en OK. La traza cruda completa basta para esta comparación matemática y efectivamente reproduce el CSV. Recibos, ledger y RESULT comprimido en `gate_mozart/`.

**Mozart externo es la versión de diez cortes NO FIEL al original de septiembre**, como ya indica el aviso del precedente. Sus diez cortes llegan hasta Z90; no son los C1–C10 históricos que antes llegaban a 1791. No se mezclan sus cronologías.

Napoleón queda **solo con CSV externo**. No hay RESULT ni crudo_P fuente: se miden sus coordenadas, pero no se certifica su transformación ni se inventan loadings o familias.

## Método común y transparencia

Ver [METODO_PREDECLARADO.md](METODO_PREDECLARADO.md). Es **exploratorio**, no un pre-registro independiente. Para describir la contracción inicial se usa en LOS SEIS el prefijo no creciente desde C1 hasta el primer aumento, mínimo tres cortes. Esta revisión se explicitó al constatar que la regla vieja máximo global→mínimo posterior dejaba sin tramo a Mozart/Che por tener máximo terminal; no se seleccionaron tramos por R². La regla vieja se conserva en el script para reproducir el diagnóstico anterior. No se trasladan parámetros de un sujeto a otro.

Fase lineal sobre TODOS los cortes; seno por cuadrícula de 2048 frecuencias, dentro de muestra. R² radio y R² log-radio se separan: nuestro **R² log≈0.928** es cercano al ≈0.929 citado antes para Mozart, mientras en escala de radio da ≈0.872. No se conoce la escala exacta usada para aquel R² original. Nuestro omega global es 9.40°/año, no 8.44°/año; no se cambia el tramo o criterio para forzar aquel número.

Forma: cresta antes del mínimo global transversal; primer salto posterior al valle de longitud≥1.5×mediana que cruce x=0 o y=0; subida posterior. La misma definición se aplica a los seis y no utiliza el giro para elegir el salto.

## Tabla comparativa

R0 al primer corte; b en 1/año; ω en grados/año; giro = cambio NETO de fase, no suma de todos los movimientos. Los años reconstruidos de los casos de calibración limitan la precisión.

| Caso | N | Giro ° | Forma completa | Tramo radio | R0 | b/año | R² radio / log | ω °/año | Seno % | Régimen | Ruptura fase |
|---|---:|---:|---|---|---:|---:|---|---:|---:|---|---|
| MOZART_EXTERNO | 10 | 222.40 | SÍ | C1→C6 | 0.4477 | 0.07589 | 0.872 / 0.928 | 9.40 | 82.9 | C7 antes | C4 antes |
| NAPOLEON_EXTERNO | 10 | 236.50 | SÍ | C1→C5 | 0.8316 | 0.07164 | 0.973 / 0.933 | 7.24 | 91.9 | C7 antes | C5 antes |
| GALILEO | 10 | 240.74 | SÍ | G_C1→G_C4 | 0.5691 | 0.04997 | 0.878 / 0.866 | 3.66 | 83.0 | G_C5 antes | G_C6 antes |
| HAWKING | 6 | 221.41 | SÍ | C1→C3 | 0.4724 | 0.12418 | 0.975 / 0.977 | 5.69 | 97.2 | C4 antes | C6 antes |
| CHE | 9 | 225.75 | SÍ | C1→C5 | 0.6534 | 0.09320 | 0.952 / 0.950 | 18.94 | 93.0 | C6 antes | C3 antes |
| MLK | 8 | 215.61 | NO | C1→C5 | 0.9155 | 0.06380 | 0.790 / 0.791 | 16.74 | 93.7 | C6 antes | C2 antes |

Todas las banderas listadas caen ANTES de sus Z90 de control. Para CSV con años a dos decimales se usa Z90 a esa misma resolución; no se afirma precisión diaria. — significa sin bandera bajo este criterio, no ausencia demostrada de ruptura.

| Caso | Cresta | Valle | Salto elegido | Cruza x=0 / y=0 | Subida |
|---|---|---|---|---|---|
| MOZART_EXTERNO | C1 | C5 | C8→C9 | no / sí | sí |
| NAPOLEON_EXTERNO | C1 | C4 | C4→C5 | sí / no | sí |
| GALILEO | G_C1 | G_C7 | G_C7→G_C8 | no / sí | sí |
| HAWKING | C1 | C4 | C4→C5 | no / sí | sí |
| CHE | C1 | C6 | C7→C8 | no / sí | sí |
| MLK | C1 | C4 | — | no / no | no |

## ¿Se repite la forma?

**Sí, bajo esta formalización exploratoria: 5/6**, Mozart, Napoleón, Galileo, Hawking y Che; MLK no cumple el salto posterior al valle que cruce un eje bajo el umbral fijado. Los giros van de 215.6° a 240.7°, ≈0.60–0.67 vueltas, INCLUSO MLK. No significa que el motor prediga desenlaces ni que esos giros tengan probabilidad de ocurrencia.

**Cautela importante de construcción:** centrar fija media y=0; alinear C1→Cn horizontal obliga y1=yn. Si ambos extremos y son positivos, DEBE haber algún y negativo en medio. Por tanto parte de cresta→valle→subida y la semejanza del giro puede venir de la proyección, no del rubro ni de una ley universal. Ver [CONSTRUCCION_GEOMETRICA.json](CONSTRUCCION_GEOMETRICA.json). Falta un control nulo independiente; no se presenta como validación de forma universal.

Los porcentajes del seno son DENTRO de muestra, con frecuencia ajustada y solo 6–10 puntos (Hawking: 6). Las banderas de régimen/fase son avisos descriptivos por umbral, no tests de cambio estructural ni pronósticos.

## Hipótesis de Mj: ¿depende de ambición/rivalidad?

Se examinó como hipótesis, sin crear pesos. Se distingue **familia que carga más la variación de PC1/PC2** de **familia con mayor crudo_P absoluto/medio**: no son lo mismo.

| Caso | Forma | Dominante por media de crudo_P | Mayor magnitud loading PC1 | Familias que más suben en el salto (hasta tres) |
|---|---|---|---|---|
| MOZART_EXTERNO | SÍ | arquetipo_el_creador | 30_ambicion | 24_rivalidad_de_superior_e_inferior +0.1962; utopia_mentalidad_milenarista +0.1121; schwartz_07_logro +0.0969 |
| NAPOLEON_EXTERNO | SÍ | N/D | N/D | N/D |
| GALILEO | SÍ | arquetipo_el_sabio | 8_rebelion | 8_rebelion +0.2803; anacyclosis_05_democracia +0.1141; utopia_autonomia_atenas +0.0189 |
| HAWKING | SÍ | mbti_factor_intuicion_n | spengler_02_verano_otono_racionalizacion | arquetipo_el_gobernante +0.1730; monomito_12_regreso_con_el_elixir +0.1730; kwml_01_rey +0.1441 |
| CHE | SÍ | monomito_02_llamado_a_la_aventura | tainter_04_colapso_por_simplificacion_forzada | eterno_retorno_02_cosmizacion_fundacion +0.2984; tainter_01_inversion_complejidad_productiva +0.2984; utopia_oficio_roma +0.2180 |
| MLK | NO | mentor, monomito_04_encuentro_con_el_mentor | 20_sacrificio_por_un_ideal | N/D |

**Resultado:** en Mozart, `30_ambicion` sí es el mayor loading de PC1; rivalidad aparece fuerte en PC2 y es el mayor aumento C8→C9. Eso es compatible con la intuición LOCAL de Mj, pero la mayor media absoluta es `arquetipo_el_creador`, no ambición. Los otros casos CON forma no comparten esa familia dominante: Galileo=el sabio/rebelión, Hawking=intuición/racionalización, Che=llamado a la aventura/colapso-complejidad. MLK SIN forma=mentor/sacrificio. No hay una separación simple ambición/rivalidad frente a no-ambición en estos datos. Napoleón no puede comprobarse por familia sin crudo_P: no se afirma que esté dominado por ambición solo porque su biografía lo sugiera.

Los top3 loadings de PC1 y PC2 con signo, dominantes de CADA corte conservando empates y TODAS las familias que suben en el salto están en [FAMILIAS.md](FAMILIAS.md) y [FAMILIAS.json](FAMILIAS.json). No se ocultan empates ni se fuerza un ganador.

## Límites temporales

- Los cuatro casos de calibración usan todos los cortes ya presentes: no se inventan trazas pos-Z90.
- Hawking termina en 2000, no en Z90 de 2010: el período ausente sigue ausente.
- MLK tiene C7/C8 con igual fecha reconstruida: ese salto no recibe velocidad temporal ni bandera de ruptura física.
- Che conserva C1,C3,C2,..., el orden realmente ejecutado; no se reordena por etiqueta.
- Galileo termina un día antes de su Z90 exacta de control.
- Ninguna fecha del sobre se envía a un análisis predictivo nuevo; los años solo ordenan/gráfican esta descripción externa.

## Reproducción y archivos

```bash
PYTHONDONTWRITEBYTECODE=1 python3 casos/trayectoria_forma/medir_trayectorias.py --manifest casos/trayectoria_forma/tusi_pc12_v1/MANIFIESTO.json
PYTHONDONTWRITEBYTECODE=1 python3 casos/trayectoria_forma/analizar_familias.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s casos/trayectoria_forma -p test_medir_trayectorias.py -v
```

- `../coordenadas_modelo_externo/`: dos CSV y script fiel recibido, sin cambiar sus coordenadas.
- `../proyeccion_tusi_modelo_externo.py`: generalización a n cortes; conserva exactamente la transformación y el año decimal original.
- `entradas/`: crudo_P fiel de los cuatro RESULT, con fuentes y hashes; control temporal separado.
- `RESULTADOS.json`, `EJECUCION.log`, seis PNG: 3D con año, perfil, polar y residuales.
- `gate_mozart/`: input exacto, RESULT/ledger comprimidos, recibos, proyección y comparación completa por columna.
- `FAMILIAS.json/.md`: loadings, dominantes por corte, aumentos en el salto; Napoleón N/D.
- `TESTS.log`: **14 pruebas OK**, incluyendo equivalencia con el script fiel y gate real Mozart. Los archivos canónicos y los Python del motor permanecen intactos en la comprobación SHA y el diff.

Sin push, PR ni comentarios. Todo se deja en commit local, conforme a la última instrucción.
