# Lectura de comportamiento post-meseta y gravedad — Paper reproducible

**Versión:** v3_20261113
**Fecha:** 2026-11-13
**Autor de la idea:** Marco Antonio Juárez
**Implementación:** Pecas (lateral `lateral_comportamiento_post_meseta_v1.py`)
**Contrato:** `COMPORTAMIENTO_POST_MESETA_V1.md`
**Repositorio:** marcojpad-hash/motor-u6-storage, rama `alterno/reconexion-2a1`

**Cambios v3 (revisión de DeepSeek, 2026-11-13):** (1) la lectura DEGRADA la
proporcionalidad si es BAJA_MUESTRA ("NO CONCLUYENTE", no hallazgo); (2) el
cometa lleva la nota "salto no separable del pulso de input" (11-19% de toda
la masa_favor llega en el corte del cometa); (3) el Sol nunca es nudo y la
distancia negativa se documenta; (4) pendiente y distancia son unidades
distintas (la correlación es solo de signo, no de elasticidad); (5) el punto
no considerado de Napoleón entró por respaldo (rango 23 > 20), no por EMERGE;
(6) versiones, régimen canónico, tipos de Tesla y desv/spread corregidos.
Los números NO cambian. DeepSeek acertó en 9 de 10 puntos; el único que no
aplicaba era salida.version (ya estaba en v2 en el JSON).

Este documento permite que CUALQUIER modelo de lenguaje (DeepSeek, Gemini,
ChatGPT, Grok) reproduzca la lectura en CUALQUIER caso, a partir de un RESULT
completo del motor U6. No necesita el código del motor: solo el RESULT (JSON)
y las fórmulas de abajo.

---

## 1. La idea

No es leer nada más el fondo. Una vez que la medición SE ESTABILIZA (régimen
`MESeta_O_ESTABILIZACION`), se ve el COMPORTAMIENTO: cómo se mueve TODO en
general (no solo abajo). Eso da trazabilidad y puede hacer emerger un punto
que antes no se había considerado. Y se tiene que MENCIONAR tal cual en la
salida, porque si no los modelos que traducen el motor no lo ven: su
entrenamiento es ver los top, entonces no ven lo que pasa abajo.

Equivalente a cuando se encontró el eje que se armaba con las fórmulas
después de ver la hélice: la estabilización revela el comportamiento.

La gravedad NO es gravedad terrestre. Es inercia de gravedad como un cometa
que arrastra, o como el sol jalando a todos los cuerpos celestes dentro de su
casa (la Vía Láctea). Se mide sobre los NUDOS que se movieron y se busca
PROPORCIONALIDAD.

---

## 2. Entradas (lo que necesitas)

Un RESULT completo del motor U6 (JSON). Debe traer estas secciones:

| Sección | Para qué |
|---------|----------|
| `salida_interpretable.H1` / `H2` (familia) | El top que ven los modelos |
| `salida_interpretable.conjunto_hipotesis_abiertas.hipotesis[].trazabilidad_geometrica` | Régimen (meseta o no) + micro/meso/macro |
| `salida_interpretable.apuesta_multiescenario.apuesta_principal.escenario` | Régimen (respaldo) |
| `movimiento_de_fondo.resumen_clases` | Clases del fondo (tokens y familias) |
| `movimiento_de_fondo.lo_que_se_cocina_abajo` | Familias que se cocinan abajo |
| `movimiento_de_fondo.tokens_que_se_cocinan_abajo` | Tokens que se cocinan abajo |
| `movimiento_de_fondo.familias_bajo_top5_subiendo_de_rango[]` | Los NUDOS (familia, rango_en_Z, pendiente, clase, primera_aparicion) |
| `movimiento_de_fondo.series_familias[familia].masa_favor_por_corte[]` | Masa de favor por corte (los pulsos) |
| `movimiento_de_fondo.series_familias[familia].serie_activacion[]` | Activación por corte |
| `features.plugin_picos_mesetas.py.curvas[familia].forma` | Forma de picos/mesetas por familia |
| `motor.cuts[].P_FULL_244[familia]` | Peso de cada familia por corte (para distancia y Sol) |

Si falta `movimiento_de_fondo`, la lectura de gravedad no se puede hacer.
Si el régimen no es meseta, la lectura queda muda (ver §3).

---

## 3. Fórmula 1 — ¿Está en meseta?

```
regimen = salida_interpretable.apuesta_multiescenario.apuesta_principal.escenario
  (si está vacío, usar trazabilidad_geometrica.regimen de la primera hipótesis)

en_meseta = (regimen == "MESeta_O_ESTABILIZACION")
```

**Régimen canónico (v3):** el valor canónico es el string largo
`"MESeta_O_ESTABILIZACION"` (así sale del motor). En la tabla de comparación
(§12) y en `comparacion_casos[]` del JSON se usa la abreviatura de display
`"MESETA"` para el mismo régimen; NO es un valor distinto y NO se usa en la
fórmula. Un reproductor debe comparar contra el string largo.

Si `en_meseta` es falso, la salida es:

```json
{"en_meseta": false, "regimen": "<regimen>", "lectura": "no estabilizado en meseta: no hay lectura de comportamiento post-meseta"}
```

No se fuerza la lectura. (Ejemplo: Tesla F001_02, régimen
CONTINUIDAD_ASCENDENTE, queda mudo.)

---

## 4. Fórmula 2 — Comportamiento (qué se mueve)

```
resumen = movimiento_de_fondo.resumen_clases
  # {"tokens": {"LATENTE_DORMIDO": n, "DESCENSO": n, "PICO": n, ...},
  #  "familias": {"LATENTE_DORMIDO": n, "PICO": n, "SIN_FORMA_CLARA": n, ...}}

n_fams_subiendo = len(movimiento_de_fondo.familias_bajo_top5_subiendo_de_rango)
n_cocina_fams = len(movimiento_de_fondo.lo_que_se_cocina_abajo)
n_cocina_toks = len(movimiento_de_fondo.tokens_que_se_cocinan_abajo)
formas = {familia: curvas[familia].forma for familia in features.plugin_picos_mesetas.py.curvas}
```

Clases del fondo (definidas en `movimiento_de_fondo_u4.py`):
ASCENSO_LENTO, MESETA, LATENTE_DORMIDO, PICO, DESCENSO, SIN_FORMA_CLARA,
SIN_SENAL. La fórmula EMERGE es: rango_Z > 5, rango_Z ≤ 20,
pendiente_min 0.005, fracción de pasos que suben ≥ 0.5, sin caídas mayores
a EPS.

---

## 5. Fórmula 3 — Lo que emerge (con peso)

```
emergentes = []
para cada f en movimiento_de_fondo.familias_bajo_top5_subiendo_de_rango:
    si f.emergente == True:
        emergentes.append({
            "familia": f.familia,
            "rango_en_Z": f.rango_en_Z,
            "pendiente_rango_por_corte": f["pendiente_rango_por_corte_(+sube)"],
            "clase": f.clase,
        })
ordenar emergentes por pendiente_rango_por_corte descendente
```

---

## 6. Fórmula 4 — Punto no considerado

El top que ven los modelos que traducen el motor:

```
top = {H1, H2} ∪ {familia de cada hipótesis en conjunto_hipotesis_abiertas}
```

El punto no considerado es el primer emergente (o, si no hay emergentes,
la primera familia subiendo de rango) que NO está en `top`:

```
punto_no_considerado = primer e en emergentes (o en familias_bajo_top5_subiendo)
                       tal que e.familia no está en top
```

**Respaldo vs EMERGE (v3):** el punto no considerado puede entrar por dos
vías. Si entra por EMERGE (rango_Z ≤ 20 y resto de umbrales de §5), es un
emergente. Si NO califica como emergente pero es la primera familia subiendo
que no está en el top, entra por RESPALDO. El caso de Napoleón es respaldo:
`dumezil_f2_fuerza` tiene rango Z 23 (> 20), así que NO es emergente
(emergentes=0) y entra por respaldo. El JSON lo marca bien; el paper lo
aclara aquí y en §11.

Es el punto que antes no se había considerado y que los modelos no ven por
mirar solo el top.

---

## 7. Fórmula 5 — Trazabilidad (el eje geométrico en meseta)

```
tg = trazabilidad_geometrica de la primera hipótesis (H1)
trazabilidad = {
    "regimen": tg.regimen,
    "micro": tg.micro, "meso": tg.meso, "macro": tg.macro,
    "aceleracion": tg.aceleracion,
    "divergencia_entre_escala": tg.divergencia_entre_escala,
    "n_cortes_observados": tg.n_cortes_observados,
}
```

---

## 8. Fórmula 6 — Gravedad (sol, nudos, cometa, proporcionalidad)

### 8.1 Sol

```
sol_familia = H1 (familia)
peso_sol_Z = motor.cuts[Z].P_FULL_244[sol_familia]   # Z = último corte
```

El Sol es el atractor central. Todo es jalado hacia su peso.

**El Sol nunca es nudo (v3, DeepSeek):** los nudos vienen de
`familias_bajo_top5_subiendo_de_rango` (familias BAJO el top5) y H1 es el
rango 1, así que está excluido por definición. Verificado en los 5 casos +
Bolívar: H1 nunca aparece como nudo. El cometa mide el salto simultáneo de
los NUDOS, no del Sol. El salto propio de H1 en el corte del cometa es
pequeño (Napoleón -0.003, Mozart -0.012, Bolívar +0.012, Transición1 +0.029)
o moderado (Mandela +0.108, ~10x menor que el salto total de los nudos,
1.077). La metáfora no se rompe: el Sol no es el que salta, son los nudos
los que son jalados.

**Distancia negativa (v3, DeepSeek):** distancia_al_sol = peso_sol_Z -
peso_Z. Si un nudo tuviera más peso que H1 en Z, la distancia sería
negativa. No ocurre en los casos verificados (0 distancias negativas en 5
casos + Bolívar, porque H1 es el máximo de P_FULL_244 en Z). Si ocurriera,
la regla lo cubre: distancia <= 0.01 marca CAPTURADO, así que un nudo por
encima del Sol se trata como capturado por definición.

### 8.2 Nudos

Para cada familia `f` en
`movimiento_de_fondo.familias_bajo_top5_subiendo_de_rango`:

```
peso_Z = motor.cuts[Z].P_FULL_244[f.familia]
distancia_al_sol = peso_sol_Z - peso_Z
pendiente = f["pendiente_rango_por_corte_(+sube)"]

estado =
    "CAPTURADO"      si distancia_al_sol <= 0.01
    "SIENDO_JALADO"  si distancia_al_sol > 0.05 y pendiente >= 0.5
    "ACERCANDOSE"    si distancia_al_sol > 0.05 y 0.2 <= pendiente < 0.5
    "RESISTE"        si distancia_al_sol > 0.05 y pendiente < 0.2
    "EN_TRANSITO"    en cualquier otro caso (cerca del Sol: 0.01 < distancia <= 0.05)
```

- CAPTURADO: ya llegó al peso del Sol.
- SIENDO_JALADO: sube hacia el Sol, proporcional a su distancia.
- ACERCANDOSE (v2): lejos del Sol pero sube a velocidad media. Antes estos
  nudos caían en EN_TRANSITO aunque estuvieran lejos del Sol, contradiciendo
  su definición ("cerca del Sol"). En Mozart 2 nudos cambian a este estado.
- RESISTE: lejos del Sol pero no sube (su propia gravedad, posible atractor rival).
- EN_TRANSITO: cerca del Sol (0.01 < distancia <= 0.05), aún no capturado,
  a cualquier velocidad.

### 8.3 Cometa

El corte donde varios nudos saltan a la vez (un arrastre):

```
para cada corte i (de 1 a n_cortes-1):
    saltos = [P_FULL_244[f][i] - P_FULL_244[f][i-1] for f in nudos]
    nudos_que_suben = contar(salto > 0.05)
    salto_total = suma(saltos)
cometa = el corte con mayor (nudos_que_suben, salto_total)
```

**Desempate (v2):** si dos cortes empatan en (nudos_que_suben, salto_total),
gana el corte más temprano (primera ocurrencia). La comparación es estricta
(`>`), así que el primer corte con el mejor valor se queda.

**El cometa no es separable del pulso de input (v3, DeepSeek):** el salto del
cometa coincide con un pulso de masa_favor (masa nueva que entra con los
tokens del corte). Medido en los casos verificados, la fracción de TODA la
masa_favor del run que llega en el corte del cometa es: Napoleón 16% (C9),
Mozart 11% (C6), Transición1 18% (C7_1448), Mandela 19% (C3_1961). Los nudos
saltan porque entró masa nueva en ese corte. El cometa es un evento real y
medible (el salto simultáneo), pero su causa es el pulso de input, no una
dinámica gravitatoria pura. Por eso los cometas de Transición1 y Mandela
llevan esta nota: "salto no separable del pulso de input".

### 8.4 Proporcionalidad

Correlación de Pearson entre la pendiente y la distancia al Sol, sobre los
nudos (mínimo 3 nudos):

```
proporcionalidad = corr(pendiente, distancia_al_sol)
```

- Positiva (+): lejos del Sol = sube más rápido (como caer hacia el Sol,
  convergencia).
- Negativa (-): cerca del Sol = sube más rápido (gravedad clásica, el tirón
  es más fuerte cerca, consolidación).
- ~0: sin patrón claro.

**Varianza cero (v2):** si todos los nudos tienen la misma distancia al Sol
o la misma pendiente (varianza cero en una de las dos variables), la
correlación es indefinida (división por cero) y la proporcionalidad es
`null`, no un número.

**Unidades heterogéneas (v3, DeepSeek):** la pendiente es cambio de RANGO Z
por corte y la distancia es diferencia de PESO (P_FULL_244). Son dos
cantidades distintas. Pearson es invariante a escala, así que el número es
válido, pero la lectura es SOLO DE SIGNO (convergencia + / consolidación -),
no de elasticidad. No se puede leer "cuánto más rápido sube por cada unidad
de distancia" porque las unidades no son las mismas.

**Confianza según n (v2, revisión de Gemini):** con pocos nudos un solo
valor atípico puede invertir el signo y cambiar la lectura de convergencia
a consolidación. Por eso la proporcionalidad siempre va acompañada de su n
y de esta etiqueta:

```
confianza_proporcionalidad =
    "BAJA_MUESTRA"  si n < 8
    "MEDIA"         si 8 <= n < 12
    "ALTA"          si n >= 12
```

**Degradar la lectura si es BAJA_MUESTRA (v3, DeepSeek):** la etiqueta no
basta; la lectura debe degradarse. Si la confianza es BAJA_MUESTRA, la
lectura dice "proporcionalidad NO CONCLUYENTE (n=..., BAJA_MUESTRA)": el
número se reporta pero NO se presenta como hallazgo. En los casos
comparados: Napoleón (+0.568, n=7) y Mozart (-0.777, n=6) son NO
CONCLUYENTES — el signo es frágil y hay que leerlo con esa advertencia.
Transición1 (n=20) y Mandela (n=16) son ALTA. Bolívar (n=11) es MEDIA.

### 8.5 Lectura de gravedad

```
"sol {sol_familia} (peso Z {peso_sol_Z}); capturados: {n}; siendo jalados: {n};
 resisten: {n}; cometa en {corte} ({n} nudos suben); proporcionalidad
 pendiente~distancia: {proporcionalidad}"
```

---

## 9. Fórmula 7 — Proyectivo (sin eliminar lo retrospectivo)

Lo retrospectivo (§3-§8) NO se elimina: queda como referencia para
comparación e ingeniería inversa. Lo proyectivo es una ADICIÓN que lee solo
los cortes hasta un corte `k` y proyecta hacia adelante.

### 9.1 Captura prevista

```
distancias = [peso_sol[i] - peso_fam[i] for i en últimos 3 cortes hasta k]
si distancias es monótona decreciente (cada una <= la anterior):
    pendiente_m = pendiente de la recta (mínimos cuadrados) sobre esos 3 puntos
    si pendiente_m < 0:
        pasos_hasta_0 = distancias[-1] / (-pendiente_m)
        captura_prevista = corte k + ceil(pasos_hasta_0)
si no: NO_PROYECTABLE
```

### 9.2 Pulso / alerta de cometa

```
pulso_en_k = masa_favor_por_corte[k] > 0   (para cada nudo)
si al menos 2 nudos tienen pulso en k:
    alerta = "pulso de masa en {corte k} en {n} nudos; posible cometa en los siguientes 1-3 cortes"
```

Los pulsos se repiten a los ~3-4 cortes (Napoleón C5->C9, Mozart C6->C9).

### 9.3 Límite honesto

El salto del cometa lo causa un pulso nuevo de masa_favor que llega con el
contenido del corte (tokens nuevos del input). No se puede predecir el corte
exacto ni el tamaño del salto antes de que el pulso llegue, porque eso sería
predecir el contenido del siguiente corte. Lo proyectivo es la extrapolación
de la tendencia y la alerta temprana cuando el pulso ya entró.

---

## 10. La constante en la inercia (lo que hace predictivo al sistema)

No se necesita el momento exacto aún. Lo que hace predictivo al sistema es
una CONSTANTE en la inercia, la misma fuerza a cualquier escala (10 minutos
o 5 años).

**Verificado: el peso del Sol es constante, ~0.79-0.80, en biografías fuertes
y completas.** En 4 casos en meseta: Napoleón 0.7813, Mozart 0.7985,
Transición1 0.8006, Mandela 0.8013 (media 0.7954, spread_max_min 0.02,
desv_poblacional 0.008; ~0.28-0.30 sobre la base 0.5). Y es estable dentro
del caso: en Napoleón el Sol se queda en 0.78-0.82 desde C3 hasta C10.

**Pero es CONDICIONAL, no universal.** Verificado en 55 casos: en meseta
15/23 (65%) tienen H1 en 0.77-0.82; en todos 29/55 (53%). No hay tope forzado
en el código (P_FULL_244 es salida del Engine). Vale para biografías fuertes
y completas. No vale para casos débiles: Bach, Coolidge y Trotsky quedan en
0.5 (H1 en la base, sin apoyo); Pasteur 0.647, Mendel 0.671, Turing 0.701.

**Relación de los factores (por qué se puede hacer proporcional).** El peso
del Sol es proporcional a la riqueza del input (55 casos):
- tokens por corte: correlación **0.485** (el factor más fuerte)
- masa_favor total de H1: **0.439**
- n_tokens del input: 0.423
- n_cortes: 0.385
- activación de H1 en Z: 0.303

El piso sube con más cortes: 3 cortes media 0.724 min 0.5; 6 cortes media
0.778 min 0.746; 7 cortes media 0.787 min 0.734; 10 cortes media 0.787 min
0.754. Por eso la FUERZA de la predicción se escala con la evidencia: un
caso rico predice fuerte, un caso flaco predice débil. ~0.79-0.80 es el techo
cuando la evidencia es suficiente.

---

## 11. Ejemplo trabajado — Napoleón FINAL27

Entrada: `RESULT_NAPOLEON_10CORTES_FINAL27.json` (10 cortes).
H1 = arquetipo_el_gobernante, H2 = 30_ambicion.

| Paso | Resultado |
|------|-----------|
| Régimen | MESeta_O_ESTABILIZACION (las 6 hipótesis) |
| Comportamiento | 7 familias bajo top5 suben; 0 cocinando; 0 emergentes por umbral |
| Punto no considerado | dumezil_f2_fuerza (rango Z 23, pendiente 1.0286) — entra por RESPALDO, no por EMERGE (rango 23 > 20, ver §6) |
| Trazabilidad | micro 0.470833 / meso 0.48587 / macro 0.528572 |
| Sol | arquetipo_el_gobernante, peso Z 0.7813 |
| Capturados | predictivo_02_mdp_politica_optima, situacion_dramatica_ambicion (peso = Sol, 0.781) |
| Siendo jalados | dumezil_f2_fuerza, utopia_mentalidad_milenarista, frye_mythos_romance |
| Resiste | dumezil_desequilibrio_f2_come_al_resto (dist 0.145, pend 0.114) |
| En tránsito | dumezil_f3_fecundidad |
| Cometa | C9 (3 nudos suben, salto total 0.32) |
| Proporcionalidad | +0.568 — NO CONCLUYENTE (n=7, BAJA_MUESTRA) |
| Proyectivo hasta C5 | captura de predictivo_02 y situacion_ambicion en C7 (real: C6, a 1 corte) |
| Proyectivo hasta C8 | pulso en 3 nudos -> cometa real en C9 (a 1 corte) |

Lectura completa:
"estabilizado en meseta: 7 familias bajo el top5 suben de rango; lo que se
cocina abajo: 0 familias / 0 tokens; emergentes: 0; punto no considerado:
dumezil_f2_fuerza (rango Z 23, pendiente 1.0286); sol arquetipo_el_gobernante
(peso Z 0.7813); capturados: 2; siendo jalados: 3; resisten: 1; cometa en C9
(3 nudos suben); proporcionalidad pendiente~distancia: 0.568 (NO CONCLUYENTE,
n=7, BAJA_MUESTRA)"

---

## 12. Comparación entre casos (para verificar la reproducción)

Valores v3. La proporcionalidad lleva ahora su confianza y la lectura se
degrada si es BAJA_MUESTRA ("NO CONCLUYENTE"). Los números de sol, cometa y
proporcionalidad son idénticos a v1/v2. La columna "Régimen" usa la
abreviatura de display "MESETA" (el canónico es "MESeta_O_ESTABILIZACION",
ver §3).

| Caso | Régimen | Sol (H1) | Peso Sol Z | Nudos | Capt. | Jal. | Acer. | Res. | Cometa | Proporc. | Confianza (n) |
|------|---------|----------|-----------|-------|-------|------|-------|------|--------|----------|---------------|
| NAPOLEON_FINAL27 | MESETA | gobernante | 0.7813 | 7 | 2 | 3 | 0 | 1 | C9 (3, 0.32) | +0.568 | NO CONCLUYENTE (7) |
| MOZART_Z90 | MESETA | autonomia_atenas | 0.7985 | 6 | 0 | 1 | **2** | 1 | C6 (6, 0.482) | **-0.777** | NO CONCLUYENTE (6) |
| TESLA_F001_02 | CONTINUIDAD_ASCENDENTE | — | — | 0 | 0 | 0 | 0 | 0 | — | — | — |
| TRANSICION1_Z90 | MESETA | creador | 0.8006 | 20 | 0 | 12 | 0 | 2 | C7_1448 (8, 0.651) * | +0.295 | ALTA (20) |
| MANDELA_HEROE | MESETA | kwml_01_rey | 0.8013 | 16 | 1 | 9 | 0 | 1 | C3_1961 (10, 1.077) * | +0.078 | ALTA (16) |

\* Cometas de Transición1 y Mandela: salto no separable del pulso de input
(18% y 19% de toda la masa_favor del run llega en ese corte, ver §8.3).

Mozart v3: la proporcionalidad -0.777 se presenta como NO CONCLUYENTE
(n=6, BAJA_MUESTRA), no como hallazgo. Con n=6 y dos nudos a 0.072 de
distancia con pendientes 0.357/0.321, el signo negativo puede ser artefacto
de que los otros 4 nudos están amontonados. Los 2 nudos que pasan a
ACERCANDOSE son `situacion_dramatica_ambicion` (dist 0.072, pend 0.3571) y
`dumezil_desequilibrio_f3_come_al_resto` (dist 0.072, pend 0.3214).

Si tu reproducción en otro caso da estos mismos números para Napoleón y
Mozart, la implementación es correcta.

---

## 13. Salida (estructura JSON)

```json
{
  "contrato": "COMPORTAMIENTO_POST_MESETA_V1",
  "version": "v3_20261113",
  "can_decide_H": false,
  "en_meseta": true,
  "regimen": "MESeta_O_ESTABILIZACION",
  "comportamiento": {
    "resumen_clases_fondo": {"tokens": {...}, "familias": {...}},
    "familias_bajo_top5_subiendo_de_rango": 7,
    "lo_que_se_cocina_abajo_n": 0,
    "tokens_que_se_cocinan_abajo_n": 0,
    "formas_picos_mesetas": {"familia": "forma", "...": "..."}
  },
  "lo_que_emerge": [{"familia": "...", "rango_en_Z": 0, "pendiente_rango_por_corte": 0.0, "clase": "..."}],
  "punto_no_considerado": {"familia": "...", "rango_en_Z": 0, "pendiente_rango_por_corte": 0.0, "clase": "..."},
  "trazabilidad": {"regimen": "...", "micro": 0.0, "meso": 0.0, "macro": 0.0, "aceleracion": 0.0, "divergencia_entre_escala": 0.0, "n_cortes_observados": 0},
  "gravedad": {
    "sol": {"familia": "...", "peso_Z": 0.0},
    "nudos": [{"familia": "...", "peso_Z": 0.0, "distancia_al_sol": 0.0, "pendiente": 0.0, "rango_Z": 0, "primera_aparicion": "...", "clase": "...", "estado": "CAPTURADO|SIENDO_JALADO|ACERCANDOSE|RESISTE|EN_TRANSITO"}],
    "cometa": {"corte": "...", "nudos_que_suben": 0, "salto_total": 0.0},
    "proporcionalidad": 0.0,
    "n_nudos_proporcionalidad": 0,
    "confianza_proporcionalidad": "BAJA_MUESTRA|MEDIA|ALTA",
    "capturados": ["..."],
    "siendo_jalados": ["..."],
    "acercandose": ["..."],
    "resisten": ["..."],
    "lectura": "..."
  },
  "lectura": "..."
}
```

La versión proyectiva (`proyectar_gravedad`) usa la misma estructura con
`"modo": "PROYECTIVO"`, `"hasta_corte": "..."`, `"proyecciones": [...]`,
`"cometa_previsto": {...}` y `"proporcionalidad_hasta_k": 0.0`.

**Si no hay meseta (v3):** cuando `en_meseta` es false, la salida es solo
`{"contrato": ..., "version": ..., "can_decide_H": false, "en_meseta": false,
"regimen": "<regimen>", "lectura": "no estabilizado en meseta: no hay lectura
de comportamiento post-meseta"}`. La clave `gravedad` NO aparece (es null /
ausente, no un objeto vacío). Las listas de estados (capturados,
siendo_jalados, acercandose, resisten) son SIEMPRE listas, nunca números:
en la tabla de comparación (§12) se muestran como conteos por brevedad,
pero en la salida del lateral son listas de familias.

---

## 14. Reglas duras

- `can_decide_H = false`. SENSOR, solo observa. No toca H1/H2, ranking,
  Engine ni catálogo 244. No reordena. No escribe canónico.
- La activación es CONCEPTUAL según el contexto, no una matriz rígida.
  Todo lo que llega al StinkBox se activa en conjunto según la carga
  semántica, sin deduplicación, sin que uno se sobreponga al otro
  (superposición), sin doble peso.
- Si no hay meseta, la lectura queda muda. No se fuerza.
- Lo retrospectivo no se elimina: queda como referencia para comparación e
  ingeniería inversa. Lo proyectivo es una adición.

---

## 15. Revisión de Gemini y cambios v2 (2026-11-13)

Gemini reprodujo el ejemplo Napoleón (todos los números coinciden) y revisó
el paper y el spec. Su veredicto: arquitectura madura, bien acotada y
empíricamente verificada contra 55 casos. Señaló 3 riesgos reales, los 3
corregidos en v2:

1. **Inestabilidad estadística en muestras pequeñas (§8.4):** Pearson con
   n=3 o n=6 es frágil; un solo valor atípico puede invertir el signo.
   Corrección: la proporcionalidad lleva ahora su n y su etiqueta de
   confianza (BAJA_MUESTRA si n<8, MEDIA si 8-11, ALTA si n>=12).
2. **Frontera rígida en los estados (§8.2):** la franja intermedia
   (0.2<=pendiente<0.5) caía en EN_TRANSITO sin importar la distancia,
   contradiciendo su definición ("cerca del Sol"). Corrección: nuevo estado
   ACERCANDOSE para nudos lejos del Sol con pendiente media; EN_TRANSITO
   queda solo para nudos cerca del Sol (0.01<dist<=0.05).
3. **Acoplamiento de formatos entre papel y código:** faltaban las reglas
   borde en el texto del spec. Corrección: desempate del cometa (gana el
   corte más temprano) y varianza cero (proporcionalidad null) documentados
   en §8.3, §8.4 y en el código.

Verificación v2 en los 5 casos: los números (sol, cometa, proporcionalidad)
son idénticos a v1. Solo Mozart reclasifica 2 nudos a ACERCANDOSE. Napoleón
y Mozart quedan en BAJA_MUESTRA; Transición1 y Mandela en ALTA.

## 16. Revisión de DeepSeek y cambios v3 (2026-11-13)

DeepSeek revisó el JSON de comparación y el paper v2. Su veredicto: la
arquitectura está bien (sensor puro, contrato versionado, verificación en 5
y 55 casos, límite honesto, revisión de Gemini incorporada); lo que fallaba
era la capa de presentación y tipos, no el motor. Acertó en 9 de 10 puntos
de su checklist; el único que no aplicaba era salida.version (ya estaba en
v2 en el JSON, sin ningún string v1).

1. **Cometas de Transición1 y Mandela no separables del pulso (a):** medido —
   18% y 19% de toda la masa_favor del run llega en el corte del cometa
   (Napoleón 16%, Mozart 11%). Los cometas llevan la nota "salto no
   separable del pulso de input" (§8.3, §12).
2. **Mozart -0.777 presentada como hallazgo (b):** ahora la lectura dice NO
   CONCLUYENTE (n=6, BAJA_MUESTRA) y el paper la presenta así (§8.4, §12).
3. **desv/spread mal etiquetados (c):** ahora desv_poblacional y
   spread_max_min (§10, JSON).
4. **n_prop coincide con nudos (d):** falsa alarma, consistente. Sin cambio.
5. **salida.version en v1 (e):** falsa alarma — el JSON ya estaba en v2
   (cero strings v1). Sin cambio en el JSON; el paper §13 sí estaba en v1
   y se corrigió a v3.
6. **§13 ejemplo en v1 (f):** corregido a v3.
7. **Fecha consistente (g):** sin cambio.
8. **Régimen con dos strings (h):** canónico definido (string largo) y la
   abreviatura "MESETA" documentada como display (§3, §12).
9. **Tesla con tipos inconsistentes (i):** contrato añadido — si no hay
   meseta, gravedad no aparece (null/ausente); las listas de estados son
   siempre listas, nunca números (§13).
10. **Sol como nudo y distancia negativa (j, k):** verificado — el Sol nunca
    es nudo (excluido por definición, bajo-top5) y hay 0 distancias
    negativas en los casos; el salto propio de H1 en el cometa es pequeño
    (y negativo en Napoleón/Mozart). Documentado (§8.1, código).
11. **Unidades heterogéneas (l):** la pendiente es rango/corte y la distancia
    es peso; la correlación es solo de signo, no de elasticidad (§8.4).
12. **Punto no considerado por respaldo (m):** dumezil_f2_fuerza (rango 23 >
    20) entró por respaldo, no por EMERGE (§6, §11).

## 17. Archivos de referencia (en el repo)

- `motor/motor/lateral_comportamiento_post_meseta_v1.py` — la implementación
  (funciones `leer_resultado`, `leer_gravedad`, `proyectar_gravedad`, `observar`).
- `motor/COMPORTAMIENTO_POST_MESETA_V1.md` — el contrato.
- `motor/corridas_ciegas_20261113/LECTURA_COMPORTAMIENTO_POST_MESETA_FINAL27.json`
  — la lectura completa de Napoleón.
- `motor/COMPARACION_GRAVEDAD_CASOS_20261113.json` — la comparación de 5 casos.
- `motor/VERIF_PESO_SOL_MUCHOS_CASOS_20261113.json` — la verificación en 55 casos.
- `motor/FACTORES_PESO_SOL_V2_20261113.json` — los factores por caso.
- `motor/corridas_ciegas_20261113/NOTA_COMPARACION_GRAVEDAD_CASOS_20261113.md`
- `motor/corridas_ciegas_20261113/NOTA_GRAVEDAD_PROYECTIVA_20261113.md`
- `motor/corridas_ciegas_20261113/NOTA_VERIF_CONSTANTE_SOL_20261113.md`
- `motor/corridas_ciegas_20261113/NOTA_RELACION_FACTORES_PROPORCIONAL_20261113.md`
