# SPEC_SCHRODINGER_V0_1 — Puente de Schrödinger del motor U6 (V0_1)

**Estado:** PROPUESTA para aprobación de Mj (Marco Juárez). No es verdad canónica.
Lo que aquí se marca como "decisión de Pecas" queda abierto a su corrección.
**Implementación:** `motor/motor/schrodinger_transport_v0_1.py` (ESTADO `V0_1_IMPLEMENTADO`).
Sustituye al esqueleto `schrodinger_transport_esqueleto_v0_1.py` (que queda intacto
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

**Abierto (V0_2, no en este spec):** un OT no balanceado (marginales suaves, con
penalización KL) dejaría que el costo encogiera directamente la media hacia el
eje. En V0_1 las marginales son duras y el suavizado de la media es la
interpolación. Si Mj quiere que el costo mueva la media, eso es V0_2.

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

**Verificación (esta V0_1):** `probar_puente_schrodinger.py` (Mozart y Napoleón,
RESULT + CSV). Además, corrida completa del motor (Napoleón Z90 10 cortes) con
el sensor cableado: el RESULT trae el sensor `schrodinger` en ACTIVA con la
trayectoria regularizada. (Ver el recibo de la corrida en el repo.)

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

## Decisiones abiertas (para Mj)

1. `μ_t^−` (medida de déficit, §2): añadida por Pecas para que la trayectoria
   tenga los dos lados. Si Mj quiere solo μ_t, la trayectoria cambia.
2. `delta=0.1` en vez del pre-registro 1.0 (§4): corrección medida por
   convergencia de Sinkhorn.
3. Extremos anclados (§7): C1 y Cn no se mueven. Si Mj quiere que también se
   suavicen los extremos, se cambia.
4. `lam=1.0` (§4): totalmente la posición transportada. Un `lam` menor mezcla
   la cruda con la transportada.
5. Orden de recuperación P→A→C (§6).
6. V0_2 con marginales suaves (§5): que el costo encoja directamente la media
   hacia el eje.
