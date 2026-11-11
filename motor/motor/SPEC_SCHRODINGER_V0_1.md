# SPEC_SCHRODINGER_V0_1 — Puente de Schrödinger del motor U6 (V0_1)

**Estado:** PROPUESTA para aprobación de Mj (Marco Juárez). No es verdad canónica.
Lo que aquí se marca como "decisión de Pecas" queda abierto a su corrección.
**Implementación:** `motor/motor/schrodinger_transport_v0_1.py` (ESTADO `V0_1_IMPLEMENTADO`)
y `motor/motor/schrodinger_transport_v0_2.py` (ESTADO `V0_2_IMPLEMENTADO`, §9).
Sustituyen al esqueleto `schrodinger_transport_esqueleto_v0_1.py` (que queda intacto
como registro de la propuesta original; en él `costo()`, `sinkhorn()` y
`memento_inversa()` eran `NotImplementedError`).
**Contrato:** `Alimenta_H=NO`, `writes_H=False`. No importa Engine ni 244.
No decide H, no escribe H, no toca el catálogo. Es un lateral/sensor.

---

## §1 Objetivo: que la trayectoria oscile menos

La **trayectoria** es el camino marcado por donde va la vectorización del
movimiento del eje geométrico. Término de Mj: **trayectoria** (la línea dinámica
/ eje vial / camino marcado; NO una traza ni una línea conductual).
En el plano de la trayectoria, el eje Tusi (x) es la progresión y el eje
transversal (y) es la oscilación: la trayectoria sube y baja en y mientras
avanza en x (la onda de un ciclo). El puente de Schrödinger debe dar **menos
probabilidad de oscilamiento** en esa trayectoria: una trayectoria regularizada
que oscile menos que la cruda.

**Qué se mide (oscilación de la transversal y):**
- **Variación total** `TV = Σ |y(t+1) − y(t)|` (cuánto se mueve y en total).
- **Amplitud pico-valle** `A = max(y) − min(y)` (de cuánto es el vaivén).
- Secundarios: cruces de la media y cambios de dirección (picos/valles).

**Resultado medido (V0_1, 10 cortes Z90, ver §7):**
| caso | TV antes | TV después | reducción | Amplitud antes | Amplitud después | reducción |
|---|---|---|---|---|---|---|
| Mozart | 0.8550 | 0.7300 | **−14.6%** | 0.3838 | 0.3650 | **−4.9%** |
| Napoleón | 1.1570 | 0.9782 | **−15.5%** | 0.5506 | 0.4870 | **−11.6%** |

La trayectoria cruda del puente (exceso con signo, §2) reproduce la forma de la
del CSV (`tabla_coordenadas.py`): la diferencia entre ambas es un desplazamiento
constante (Mozart −0.3374, Napoleón −0.3948), así que TV y amplitud coinciden.
Los extremos quedan anclados (C1 y Cn no se mueven); el puente suaviza el interior.

---

## §2 μ_t (medida por corte)

**Adoptado verbatim del esqueleto** (la definición propuesta que ya funcionaba):
```
μ_t(f) = max(0, p_f(t) − 0.5) / Z_t^+ ,   Z_t^+ = Σ_f max(0, p_f(t) − 0.5)
```
Es la medida de las familias **activas** en el corte t (exceso positivo sobre 0.5).

**Añadido en V0_1 (decisión de Pecas, abierta a corrección): la medida de déficit**
```
μ_t^−(f) = max(0, 0.5 − p_f(t)) / Z_t^− ,   Z_t^− = Σ_f max(0, 0.5 − p_f(t))
```
Sin ella la trayectoria pierde la mitad de la señal: la posición en el plano es
el **exceso con signo** `pos(t) = Z_t^+·m^+(t) − Z_t^−·m^−(t)`, donde `m^+` y `m^−`
son las medias de las coordenadas (§3) bajo μ_t^+ y μ_t^−. Con solo μ_t (el lado
positivo) la trayectoria media no reproduce la del CSV (correlación en y de 0.39
en Mozart); con los dos lados, la forma coincide exactamente (desplazamiento
constante, §1). El transporte corre en los dos lados (dos planes por transición).

**Soporte:** las familias con `p ≠ 0.5` en el corte (`candidatos()`, heredado del
esqueleto). Para cada transición el soporte común es la unión de los soportes de
los dos cortes.

---

## §3 Coordenadas: dónde vive cada familia en el plano

Cada familia tiene una coordenada `(τ, υ)` en el plano de la trayectoria:
- `τ` = eje Tusi (progresión), `υ` = transversal (oscilación).
- Se calculan igual que en `tabla_coordenadas.py`: matriz P (cortes × familias),
  centrada por familia, SVD; PC1 → Tusi, PC2 → transversal; rotación para que el
  diámetro C1→Cn quede horizontal.
- La posición cruda del corte t es `pos(t)` (§2). Su forma coincide con la del
  PCA salvo desplazamiento constante.

Escala medida (Mozart/Napoleón): `τ` y `υ` en [−0.31, +0.34], desviación típica
~0.064; la diferencia típica `|υ_i − υ_j|` es ~0.04. Esta escala es la que fija
el `epsilon` (§4).

---

## §4 Parámetros

`PARAMS_DEFAULT = {alpha: 1.0, beta: 1.0, gamma: 1.0, delta: 0.1, lam: 1.0, epsilon: 0.05}`

| parámetro | qué pesa | por defecto |
|---|---|---|
| `alpha` | diferencia de polaridad transversal `\|υ_i − υ_j\|` | 1.0 |
| `beta` | salto en el eje de progresión `\|τ_i − τ_j\|` | 1.0 |
| `gamma` | diferencia de activación `\|e_i(t) − e_j(t+1)\|` | 1.0 |
| `delta` | cruce de eje (signo de υ distinto) | **0.1** (ver corrección) |
| `lam` | fuerza del puente: 1.0 = totalmente la posición transportada; 0.0 = la cruda | 1.0 |
| `epsilon` | regularización entrópica de Sinkhorn (a mayor eps, plan más difuso) | 0.05 |

**Corrección medida de `delta` (decisión de Pecas, abierta a Mj):** el
pre-registro del esqueleto traía `delta=1.0`, pero un cruce de eje costaba 1.0 =
20×epsilon y el kernel quedaba casi bloque-diagonal: Sinkhorn **no convergía en
5000 iteraciones** en la transición Napoleón C5→C6 (error marginal 8.6e-05).
Con `delta=0.2` converge en 3080 iteraciones y con `delta=0.1` (el cruce cuesta
2×epsilon, en la escala de los demás términos) en <1000. Se adopta `delta=0.1`.
`epsilon=0.05` se mantiene: con el costo en escala O(0.1), `C/eps` es O(2–20) y
el kernel no se desborda ni se anula.

---

## §5 Costo de transición

```
C(i,j) = alpha·|υ_i − υ_j| + beta·|τ_i − τ_j| + gamma·|e_i(t) − e_j(t+1)|
         + delta·[signo(υ_i) ≠ signo(υ_j) y ambos ≠ 0]
```
`ctx` lleva `polaridad` (υ), `tusi` (τ), `exceso_t` y `exceso_t1` (el exceso del
lado que se transporta: positivo para μ^+, déficit para μ^−).

**Por qué penaliza la oscilación:** el término `alpha` y el término `delta`
penalizan el transporte de masa entre familias de polaridad transversal
opuesta. Ese cruce de eje (masa que pasa de empujar la trayectoria hacia arriba
a empujarla hacia abajo, o al revés) es lo que hace oscilar la trayectoria. El
plan óptimo, entonces, acopla en lo posible familias de la misma polaridad y
solo cruza el eje la masa que las marginales obligan a cruzar. El término `beta`
penaliza saltos grandes en la progresión y `gamma` mover masa entre
activaciones muy distintas.

**Transparencia (propiedad matemática, no un fallo):** con marginales fijas, la
**media** del punto medio del puente es independiente del plan:
`mid(t) = (pos(t) + pos(t+1))/2` siempre. El plan (costo + epsilon) determina el
**acople** (qué familias se emparejan) y la **dispersión** de la medida
interpolada, no la media. Por eso el suavizado de la trayectoria media viene de
la interpolación de desplazamiento del puente (el camino del puente), y el costo
moldea el acople y la dispersión. Medido: la dispersión transversal de la medida
interpolada es mayor que la del acople independiente (el plan conserva la
estructura de polaridad en vez de difuminarla hacia la media); eso es la señal
de que el costo está activo, no un fallo.

**Sinkhorn:** algoritmo de Sinkhorn-Knopp (escalado iterativo) en el dominio
lineal, con piso en las marginales para evitar 0/0. `max_iter=5000`, `tol=1e-9`
(error marginal L1). Con `delta=0.1` todas las transiciones de Mozart y
Napoleón convergen (la más lenta, ~1000 iteraciones). Devuelve el plan y su
diagnóstico (iteraciones, error marginal, costo total, convergencia).

**V0_2 (implementado, §9):** un OT no balanceado (marginales suaves, con
penalización KL `rho`) deja que el costo encoja directamente la media hacia
el eje. En V0_1 las marginales son duras y el suavizado de la media es la
interpolación; en V0_2 el costo mueve la media (medido, §9.4).

---

## §6 memento_inversa (orden de recuperación)

`memento_inversa(estado, orden=("P","A","C"))` devuelve el estado recuperado en
el orden dado, con las claves faltantes reportadas (sin romper si falta alguna).
**Orden por defecto: P → A → C (decisión de Pecas, abierta a corrección).**
P primero porque la trayectoria se define por P; A y C están planos en 0.5 en
las corridas actuales y no aportan señal. `orden` debe ser una permutación (o
subconjunto) de `("P","A","C")`; si no, levanta `ValueError` con el orden
recibido.

---

## §7 Salida y consumo

**Lo que produce el transporte** (`transportar_trayectoria(cortes, prm)`):
- `trayectoria_cruda`: posición por corte (exceso con signo, §2).
- `trayectoria_regularizada`: extremos anclados, interior por el puente
  (con `lam`, §4). Es la trayectoria que oscila menos.
- `trayectoria_pca_referencia`: la del PCA (para verificar que la cruda tiene
  la misma forma).
- `puntos_medios_puente`: el punto medio del puente por transición.
- `transiciones`: por transición y por lado (+/−), el diagnóstico del plan
  (iteraciones, error marginal, costo total, convergencia) y la dispersión
  transversal de la medida interpolada (y su control independiente).
- `oscilacion`: TV y amplitud (transversal y Tusi) antes/después, y las
  reducciones. `singulares_pca` (verificación de que PC1/PC2 dominan).
- Si hay menos de 3 cortes: `estado=SIN_TRAYECTORIA` con la nota (con 2 no hay
  interior que suavizar). No rompe: el sensor degrada a ACTIVA_MUDA.

**Cómo lo consume `laterales_unico_v1.py` (sensor `schrodinger`):**
- Carga `schrodinger_transport_v0_1.py` (antes el esqueleto), calcula μ_t por
  corte (como antes) y corre `transportar_trayectoria(mcuts)`.
- `anillos_para_transporte` pasa a `"consumido": True` (antes False por
  costo/sinkhorn NotImplemented), con el resumen del transporte; los anillos
  siguen como contexto por corte.
- El sensor reporta la trayectoria regularizada y la oscilación antes/después,
  y su estado pasa a **ACTIVA** (emite la trayectoria regularizada como señal)
  cuando el transporte corre; si no puede correr (menos de 3 cortes, sin numpy)
  queda **ACTIVA_MUDA** con el motivo, sin romper el resto de laterales.
- La salida del puente (`salida()`) lleva `Alimenta_H=NO`, `writes_H=False`.

**Verificación (esta V0_1):** `probar_puente_schrodinger.py` (en el área de trabajo,
`~/workspace/u6-alterno/mozart/`, Mozart y Napoleón, RESULT + CSV) y el test
sintético `motor/tests/test_schrodinger_v0_1.py` (en el repo, PASS). Además,
corrida completa del motor (Napoleón Z90 10 cortes) con el sensor cableado: el
RESULT trae el sensor `schrodinger` en ACTIVA con la trayectoria regularizada.
(Ese RESULT vive en la copia alterna de trabajo,
`~/workspace/u6-alterno/motor-cameo/motor/RESULT_NAPOLEON_SCHRODINGER_V01.json`,
no en el repo: es un artefacto de corrida, no un archivo fuente.)

---

## §8 Qué NO hace

- No alimenta H ni escribe H (`Alimenta_H=NO`, `writes_H=False`).
- No toca `Engine_V5_CANONICO_SOLO.py` ni `patterns_final_v14.json` (canónicos).
- No decide H ni reordena candidatos ni escribe el catálogo.
- No sustituye la trayectoria cruda: la reporta junto a la regularizada.
- No es una ley: es un lateral/sensor que regulariza la trayectoria medida.
  La reducción de oscilación es un hecho medido en dos casos (§1), no una
  garantía general.

---

## §9 V0_2: marginales suaves — el costo mueve la media

**Decisión de Mj (2026-11-11): AMBOS.** El V0_1 se queda porque estabiliza,
y el V0_2 se construye porque transforma. Su razón: para que algo sea, también
tuvo que dejar de ser — uno estabiliza y el otro transforma. Es la misma
dualidad que la tríada billar / Poincaré / Forman-Ricci del motor
(`billar_circular_convergencia_v0_1.py`: el billar circular en el borde ES
rotación de Poincaré; `ricci_forman_coocurrencia_v0_1.py` y el hub
'negativo_ricci_vs_billar': el voto negativo de Ricci-Forman vs billar).
Forman-Ricci es la "lectura del negativo" (Marco): no dice qué es, dice qué
no es — si hay 5–6 opciones, elimina 1–2 porque no eran. El V0_2 hace lo
mismo con la masa: no afirma qué es la trayectoria, elimina (destruye) la
masa que no debe cruzar el eje.

**Transparencia (revisión de Grok del V0_1, 2026-11-11):** en el V0_1 la
reducción de la media es principalmente interpolación de desplazamiento, no
efecto directo del costo — con marginales fijas, el punto medio es siempre
`(pos(t)+pos(t+1))/2` y el costo solo mueve el acople y la dispersión. Eso
queda explícito aquí. En el V0_2 el costo SÍ mueve la media (medido, §9.4).

### §9.1 Formulación: transporte óptimo NO balanceado

El plan P ya no está obligado a reproducir exactamente μ_t y μ_{t+1}. Minimiza:
```
F(P) = <P, C> + eps·KL(P | μ_t⊗μ_{t+1}) + rho·KL(P·1 | μ_t) + rho·KL(P^T·1 | μ_{t+1})
```
(Chizat et al. 2018, "Scaling algorithms for unbalanced optimal transport
problems"). `KL` es la KL generalizada `KL(a|b) = Σ a·log(a/b) − a + b`.
`rho` es el peso de la penalización por desviarse de las marginales: el plan
puede destruir masa (dejar de ser) y recrearla (llegar a ser) pagando `rho`
por unidad de KL. Cuando transportar masa a través del eje cuesta más que
destruirla y recrearla al otro lado, el plan la destruye — y la media de la
medida interpolada se mueve hacia el eje.

**Sinkhorn no balanceado** (exponente `q = rho/(rho+eps)`):
```
u <- μ_t / (K v)^q ;  v <- μ_{t+1} / (K^T u)^q ;  P = diag(u) K diag(v)
```
OJO: solo el denominador `(K v)` lleva el exponente `q`; μ_t queda a la
potencia 1. (Elevar también μ_t a `q` infla el plan y crea masa, M > 1:
bug encontrado y corregido por medida.) Con `rho -> ∞`, `q -> 1` y se
recupera el Sinkhorn balanceado del V0_1 (verificado: con `rho=100`,
`max|y_V0_2 − y_V0_1| = 0.0003` en Mozart y `0.0004` en Napoleón). Con
`rho -> 0`, `q -> 0` y el plan destruye masa sin freno (la trayectoria
colapsa). `tol=1e-7` (no 1e-9): la iteración no balanceada contrae más lento
cuando `rho` es grande, y el criterio es el cambio relativo del plan P
(invariante de gauge; medir el cambio de `u` y `v` es engañoso por su
libertad de gauge).

### §9.2 rho: cómo se elige

`rho` se elige por medida (barrido en `probar_puente_schrodinger_v02.py`).
La escala la fija el costo: destruir una unidad de masa cuesta ~`rho`, y
cruzar el eje una vez cuesta `delta=0.1`. **Por defecto `rho=0.1` (= delta):**
el costo de destruir masa iguala al costo de un cruce de eje — el punto de
inflexión entre estabilizar y transformar. Con `rho` menor, el plan destruye
más masa (transforma más, pero se come la señal); con `rho` mayor, se acerca
al V0_1. Decisión de Pecas, abierta a corrección de Mj.

Barrido medido (TV transversal, M = masa transportada media, KL = penalización
KL media; convergencia en todos los casos, 26–28 iteraciones a rho=0.1):

| caso | rho | TV | amplitud | media\|y\| | M | KL |
|---|---|---|---|---|---|---|
| Mozart | cruda | 0.8550 | 0.3838 | 0.3374 | — | — |
| Mozart | V0_1 | 0.7300 | 0.3650 | 0.3380 | 1.000 | 0 |
| Mozart | V0_2 0.02 | 0.2236 | 0.0837 | 0.1218 | 0.265 | 0.0163 |
| Mozart | V0_2 0.05 | 0.2698 | 0.1307 | 0.1804 | 0.439 | 0.0218 |
| Mozart | **V0_2 0.1** | **0.3846** | **0.1923** | **0.2318** | **0.603** | **0.0213** |
| Mozart | V0_2 0.2 | 0.5238 | 0.2619 | 0.2750 | 0.749 | 0.0179 |
| Mozart | V0_2 0.5 | 0.6404 | 0.3202 | 0.3107 | 0.879 | 0.0132 |
| Mozart | V0_2 1.0 | 0.6852 | 0.3426 | 0.3244 | 0.934 | 0.0097 |
| Mozart | V0_2 2.0 | 0.7078 | 0.3539 | 0.3313 | 0.965 | 0.0062 |
| Napoleón | cruda | 1.1570 | 0.5506 | 0.3948 | — | — |
| Napoleón | V0_1 | 0.9782 | 0.4870 | 0.3890 | 1.000 | 0 |
| Napoleón | V0_2 0.02 | 0.2858 | 0.1131 | 0.1335 | 0.243 | 0.0174 |
| Napoleón | V0_2 0.05 | 0.3392 | 0.1696 | 0.2021 | 0.417 | 0.0237 |
| Napoleón | **V0_2 0.1** | **0.5430** | **0.2715** | **0.2628** | **0.584** | **0.0232** |
| Napoleón | V0_2 0.2 | 0.7252 | 0.3621 | 0.3140 | 0.736 | 0.0189 |
| Napoleón | V0_2 0.5 | 0.8726 | 0.4351 | 0.3564 | 0.873 | 0.0124 |
| Napoleón | V0_2 1.0 | 0.9264 | 0.4617 | 0.3726 | 0.932 | 0.0085 |
| Napoleón | V0_2 2.0 | 0.9530 | 0.4748 | 0.3809 | 0.964 | 0.0056 |

### §9.3 Extremos

**Anclados, igual que el V0_1:** C1 y Cn no se mueven. Son las mismas
condiciones de borde, para que la comparación V0_1/V0_2 sea manzana con
manzana (el interior es lo que transforma). Verificado: el V0_2 (rho=0.1)
empieza y termina en la cruda (Mozart −0.1274/−0.1274; Napoleón
−0.1278/−0.1278).

### §9.4 Resultado medido: el costo SÍ mueve la media

Con `rho=0.1` (el default), la media se mueve hacia el eje de verdad — no es
solo interpolación:

| caso | TV cruda | TV V0_1 | TV V0_2 | TV V0_2 vs cruda | TV V0_2 vs V0_1 | media\|y\| cruda | media\|y\| V0_1 | media\|y\| V0_2 | media\|Δy\| vs V0_1 | M |
|---|---|---|---|---|---|---|---|---|---|---|
| Mozart | 0.8550 | 0.7300 | **0.3846** | **−55.0%** | **+47.3%** | 0.3374 | 0.3380 | **0.2318** | 0.1062 | 0.603 |
| Napoleón | 1.1570 | 0.9782 | **0.5430** | **−53.1%** | **+44.5%** | 0.3948 | 0.3890 | **0.2628** | 0.1262 | 0.584 |

El V0_1 deja `media|y|` casi igual que la cruda (Mozart 0.3374→0.3380:
la media no se mueve, como dijo Grok). El V0_2 la baja de verdad (Mozart
0.3374→0.2318, −31%; Napoleón 0.3948→0.2628, −33%): la trayectoria se
acerca al eje. El precio es la masa destruida (~40% a rho=0.1) y la
penalización KL (~0.02). La trayectoria transformada conserva la forma de
la onda (sigue siendo una onda, más baja), no colapsa.

### §9.5 Salida y consumo (V0_2)

`transportar_trayectoria_v02(cortes, prm)` produce lo mismo que el V0_1
(`trayectoria_cruda`, `trayectoria_pca_referencia`, `puntos_medios_puente`,
`transiciones`, `oscilacion`, `singulares_pca`), con estas diferencias:
- `trayectoria_transformada` en vez de `trayectoria_regularizada` (es la
  trayectoria cuya media el costo encogió hacia el eje).
- `desplazamiento_media`: por corte y en promedio (media y máximo de |Δy|),
  y `media|y|` antes/después (qué tan cerca del eje quedó).
- `costo_transformacion`: masa transportada media M, masa destruida media
  (1−M) y penalización KL media (el precio de mover la media).
- Por transición y lado: `masa_transportada`, `masa_destruida`,
  `penalizacion_kl`, `costo_total`, `costo_mas_penalizacion`, iteraciones y
  residuo del Sinkhorn no balanceado.
- Si hay menos de 3 cortes: `estado=SIN_TRAYECTORIA` (no rompe).

El sensor `schrodinger` de `laterales_unico_v1.py` corre AMBOS (V0_1 y V0_2)
y reporta las dos trayectorias con sus oscilaciones; si el V0_2 no puede
correr, lo reporta y se queda con el V0_1, sin romper laterales.

**Verificación (esta V0_2):** `probar_puente_schrodinger_v02.py` (en el área
de trabajo, `~/workspace/u6-alterno/mozart/`, Mozart y Napoleón, barrido de
rho) y el test sintético `motor/tests/test_schrodinger_v0_2.py` (en el repo,
PASS). Además, corrida completa del motor (Napoleón Z90 10 cortes) con el
sensor cableado: el RESULT trae el sensor `schrodinger` en ACTIVA con las
dos trayectorias (V0_1 y V0_2).

---

## Decisiones abiertas (para Mj)

1. `μ_t^−` (medida de déficit, §2): **CERRADA.** Confirmada necesaria por la
   revisión de Grok (2026-11-11) y por la medida: sin ella la correlación en
   y es 0.39 en Mozart; con ella la forma coincide. Se queda.
2. `delta=0.1` en vez del pre-registro 1.0 (§4): **CERRADA.** Confirmada por
   Grok (atajo numérico justificado) y por convergencia. Se queda.
3. Extremos anclados (§7, §9.3): **CERRADA.** C1 y Cn no se mueven en V0_1 ni
   en V0_2 (mismas condiciones de borde, para comparar). Si Mj quiere que
   también se suavicen los extremos, se cambia.
4. `lam=1.0` (§4): **CERRADA como default.** Totalmente la posición
   transportada. Un `lam` menor mezcla la cruda con la transportada (dial
   disponible, no el default).
5. Orden de recuperación P→A→C (§6): **CERRADA.** Confirmada por Grok
   (razonable, inofensiva: A y C planos en 0.5). Se queda.
6. V0_2 con marginales suaves (§5, §9): **IMPLEMENTADA** (esta sección).
   Queda abierta solo la elección de `rho`.

**Decisiones abiertas nuevas (V0_2):**
7. `rho=0.1` (§9.2): default elegido por medida (rho = delta, el punto de
   inflexión). Si Mj quiere más transformación (rho menor) o más cerca del
   V0_1 (rho mayor), se cambia.
8. Extremos del V0_2 (§9.3): anclados como el V0_1. Si Mj quiere que el V0_2
   también mueva los extremos (la posición efectiva del plan adyacente), se
   cambia.
