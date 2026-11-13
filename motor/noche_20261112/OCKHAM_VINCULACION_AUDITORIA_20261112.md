# NAVAJA DE OCKHAM — AUDITORÍA DE LA VINCULACIÓN + CHEQUEO SHERLOCK

**Orden de Mj (2026-11-12 ~21:38 CST):** meter la navaja de Ockham en
la regla operativa y aplicarla una vez. Antes se quejó de que la
vinculación se estaba complicando de más y pidió aplicar Sherlock.

**Documentos:** la regla está en
`motor/REGLA_OPERATIVA_OCKHAM_20261112.md`. Esto es su primera
aplicación, a la vinculación.

**Método (solo lectura, salvo este reporte):** se leyeron los dos
laterales (`motor/laterales/vinculacion_tokens/vinculacion.py` y
`motor/reconexion_v2a1/no_duplicacion_latencia.py`) y sus JSON de
resultado; se ejecutó la forma mínima importando la maquinaria de
los laterales (sin modificarlos) y se comparó su veredicto contra el
de la vinculación. Nada al repo, nada al canon, nada a entradas ni
RESULT sellados.

---

## 1. Lo que no-duplicación YA mide (las lecturas existentes)

- **_asignar** (por token y corte): resuelto (unica / por_compania) o
  latencia (sin_compania / empate) o sin_familia. Esta ES la
  vinculación token↔familia resuelta.
- **Tableros sombra P/A/C** (`correr_tablero_sombra`): p_final por
  familia y corte, H1 sombra por p_final en Z, frentes, factor de
  duplicación, eventos favor/contra, ocurrencias.
- **Frentes de latencia (102: 23/18/22/20/19, 2 resueltos):** qué
  token, en qué corte se abre, en qué corte se resuelve y a qué
  familia. El frente ES el estado de superposición: un token en
  latencia es un token en dos o más estados a la vez.
- **p_final como stock:** la probabilidad acumulada por familia y
  corte; el stock recuerda lo que el flujo olvida (Juana y Tubman:
  el H1 sombra es rango 1 en ganancia de p_final C5→C7).

---

## 2. Auditoría Ockham de la vinculación, pieza por pieza

### Criterio 1 — Grafo token↔token: SE CORTA

82 aristas en total; 4 cortes sin ninguna arista (Juana C3 y C5,
Tubman C3 y C5); vínculo más fuerte `autoridad`↔`liderazgo` 1.30
en 3 de 5 casos. El grafo no lo lee la pauta: el desplazamiento se
calcula solo con los vectores token→familia, nunca con las aristas.
Y sus vínculos más fuertes vuelven a decir la estructura de compañía
que `_asignar` ya usa (el par del trono, ya conocido por los conteos
de duplicación; `análisis`↔`búsqueda_verdad` en Semmelweis es la
compañía del sabio). Medido pero no usado por ninguna decisión.
**Veredicto: se corta del mecanismo.** Como mucho queda como
despliegue derivado de la asignación, no como mecanismo.

### Criterio 2 — Vector de vínculo con masa conservada: SE CORTA EL REPARTO

Lo que el vector aporta de nuevo es el reparto de la superposición:
un token en latencia reparte su masa proporcional a los pesos favor
del catálogo. Ese reparto es una SUPOSICIÓN, no una medición: los
pesos vienen del catálogo, no del caso. El tablero sombra ya dice lo
que la superposición ES: el token no cuenta para nadie ese corte.
La navaja (criterio 4: números no inventados) corta el reparto.
**Veredicto: se corta el reparto proporcional.** Se queda la
asignación (resuelto vs latencia), que es la medición real.

### Criterio 3 — Desplazamiento Δ + argmax: SOBREVIVE (en forma mínima)

Es la única lectura nueva: el flujo de vínculo entre cortes. Se
mueve cuando la p está saturada (Semmelweis: el H1 solo puede ganar
+0.0058 en p, rango 63; el flujo gana +1.26 en la última transición).
Acierta 3 de 5 en dos transiciones, 1 de 5 en una. **Veredicto:
sobrevive**, pero solo en la forma mínima (§3).

### Criterio 4 — Lo cíclico: SE CORTA como criterio aparte

215 retornos, 638 cambios de sentido, 185 reapariciones, 35 vínculos
resueltos recuperados. Son descripciones de la misma serie que ya
usa el desplazamiento; los totales no alimentan ninguna decisión.
El único dato nuevo, los 35 vínculos resueltos recuperados, tampoco
lo lee nada. **Veredicto: se corta como criterio aparte.** La serie
por (token, familia) queda porque viene gratis con el desplazamiento;
los conteos agregados no son un mecanismo.

### La reimplementación de _frentes: SE CORTA

La vinculación reimplementa el conteo de frentes (~30 líneas) para
pasar la puerta contra `no_duplicacion_resultado.json`. El propósito
de la puerta (chequeo independiente) es legítimo, pero la navaja
(criterio 5: la puerta es comparación, no re-derivación) dice que
se comparen los frentes guardados, no que se vuelvan a derivar.
**Veredicto: se corta la reimplementación;** se importan los frentes.

### La prueba secundaria (flujo vs p): ES la evidencia a favor de la forma mínima

Ya muestra que Δp (ganancia de p_final del tablero sombra) le gana
a ΔL en la pregunta del H1 en Juana y Tubman (rango 1 en Δp). La
forma mínima es: Δp primero, ΔL solo donde la p está saturada.

---

## 3. La prueba medida: la forma mínima reproduce el veredicto exacto

Forma mínima: L_t(c) = +w a la familia si resuelto favor, −w si
resuelto contra, 0 si latencia o sin familia. Sin reparto, sin
grafo, sin conteos cíclicos. Calculada EJECUTANDO la maquinaria
importada de los laterales (no razonada). Tramo C5→C7:

| caso | argmax mínima | Δ H1 | rango H1 | acierta | argmax vinculación | acierta |
|---|---|---|---|---|---|---|
| Juana | 7_caer_victima +0.78 | +0.00 | — (sin masa resuelta en los extremos) | NO | 7_caer_victima +0.78 | NO |
| Tubman | monomito_01 +2.10 | +0.74 | 5 | NO | monomito_01 +2.10 | NO |
| Mandela | romance +0.80 | +0.80 | 1 | SÍ | romance +0.80 | SÍ |
| Semmelweis | arquetipo_el_heroe +0.78 | +0.78 | 1 | SÍ | arquetipo_el_heroe +0.78 | SÍ |
| Kolbe | arquetipo_el_heroe +1.54 | +1.54 | 1 | SÍ | arquetipo_el_heroe +1.54 | SÍ |

**3 de 5, mismo argmax, mismos deltas, en los 5 casos.** El reparto
de superposición aporta CERO al agregado del tramo: se telescopia
(los cortes intermedios se cancelan; solo importan los extremos, y
en los extremos los tokens que cargan la pauta están resueltos, no
en superposición). La única diferencia: en Juana el H1 sale del
ranking en la mínima (sin masa resuelta en C5 ni en C7), mismo
veredicto (NO, delta 0.00). Matiz honesto: el desglose por
transición suelta sí difiere donde hay masa en superposición en el
corte intermedio (Semmelweis C6, `valentía` en superposición); el
agregado del tramo —que es lo que usa la pauta— es idéntico.

### La forma mínima (PROPUESTA, no implementada)

- Entradas: `_asignar` (importado de no-duplicación) +
  `correr_tablero_sombra` (importado). Ningún tablero nuevo.
- L_t(c) mínima: resuelto favor → +w; resuelto contra → −w;
  latencia / sin familia → 0.
- L(c) = Σ L_t(c); Δ y argmax como en el criterio 3.
- Δp del tablero sombra como primera lectura; ΔL como segunda,
  solo donde la p está saturada.
- Se cae: el grafo, el reparto proporcional, el criterio cíclico
  como mecanismo, la reimplementación de frentes.
- Se queda: los criterios 2 (asignación) y 3 (desplazamiento), la
  puerta como comparación, el veredicto 3/5.

El lateral como está queda verificado y NO se reescribe: reescribirlo
es decisión de Mj.

---

## 4. Chequeo Sherlock a la vinculación (las 4 líneas humanas)

El auto está LIMPIO en los 5 casos (auto [] en `metodo_rigor_pre`,
bandera SHERLOCK_RIGOR LIMPIO en los 5 RESULT). El auto nunca
dispara. Lo que sigue es el chequeo humano, una línea por pregunta
y caso, con evidencia.

**Juana** — cadena top1: monomito_01 ×2, 9_audaz ×3, 36_pérdida,
20_sacrificio.
- Holmes: de hechos — `injusticia` (C6, C7), `duelo` y
  `perdida_familiar` (C6) son tokens de la entrada, del juicio y la
  condena; la familia (7_caer_victima / 36_pérdida) es la lectura
  del catálogo.
- Hecate: no pedí más de lo mismo — el letrero cambia en cada tramo;
  el problema es el contrario, el H1 es un pulso que llega en C6 y
  se va en C7.
- Schopenhauer: leo el tablero — la pauta falla aquí y se dice; el
  argmax lo carga un solo token (`injusticia`, +0.78).

**Tubman** — cadena top1: monomito_01, sacrificio ×2, audaz,
sacrificio, monomito_12 ×2.
- Holmes: de hechos — `cotidiano`, `rutina` (C1, C6, C7) y
  `crisis_abrupta` (C2, C5) son de la vida del caso; monomito_01 es
  la lectura del catálogo.
- Hecate: incómoda — el argmax no es una atracción nueva, es un
  cambio de signo con los mismos tokens de siempre (se va el contra
  de `crisis_abrupta`, llega el favor de `cotidiano`+`rutina`).
- Schopenhauer: leo el tablero — el H1 gana +0.74 pero el argmax es
  otro; el fallo está reportado, no defendido.

**Mandela** — cadena top1: rogers, 9_audaz ×2, sacrificio ×2,
gobernante, monarquía.
- Holmes: de hechos — `victoria` (C6, C7) es token de los hechos;
  romance es la lectura del catálogo.
- Hecate: el letrero cambia cada vez, no hay "más de lo mismo";
  pero el acierto lo carga un solo token (`victoria`, +0.80).
- Schopenhauer: leo el tablero — acierta, pero con un token;
  generalizar sería defender.

**Semmelweis** — cadena top1: rogers, sabio ×3, héroe, monomito_05,
héroe.
- Holmes: de hechos — `valentía` (C3, C4, C6, C7) es token de los
  hechos (defender a las madres); arquetipo_el_heroe es la lectura
  del catálogo.
- Hecate: incómoda — `valentía` se repite en 4 de 7 cortes y el
  héroe 3 seguidos; es el mismo token y el mismo letrero repitiéndose.
- Schopenhauer: leo el tablero — aquí el flujo es lo único que se
  mueve (p saturada en el techo), pero el acierto lo carga un solo
  token.

**Kolbe** — cadena top1: rogers ×2, monomito_05 ×4 seguidos (C3–C6),
5_persecucion.
- Holmes: de hechos — `valentía` + `defensa_debil` (C6, C7) son
  tokens del acto del campo; arquetipo_el_heroe es la lectura del
  catálogo.
- Hecate: SÍ pedí más de lo mismo — `monomito_05` cuatro cortes
  seguidos y el auto NO lo ve, porque solo mira los primeros 4 tops
  (rogers, rogers, monomito_05, monomito_05: dos distintos, sin
  bandera). Esta es la alarma que solo la línea humana levanta.
- Schopenhauer: leo el tablero — el acierto es el más sólido (dos
  tokens, +1.54), pero la trayectoria estuvo 4 cortes en el umbral
  mientras la historia avanzaba.

**Sigue en cuaderno: sí.** La línea incómoda es la de Kolbe
(Hecate): el auto dice LIMPIO y el ojo humano ve cuatro cortes con
el mismo letrero. El plugin solo revisa los primeros 4 tops; un
tramo igual de 4 cortes que empieza en C3 es invisible para él.
Eso no es un fallo del caso, es un límite del auto — y es justo lo
que las 4 líneas humanas existen para atrapar.

---

## 5. Veredicto

La vinculación SOBREVIVE a la navaja solo en parte: el
desplazamiento (criterio 3) sobrevive, y la forma mínima lo
reproduce exacto (3/5, mismo argmax, mismos deltas). No sobreviven
el grafo token↔token, el reparto proporcional de la superposición,
el criterio cíclico como mecanismo aparte ni la reimplementación de
frentes: no miden nada que la asignación + los tableros sombra + Δp
no midan ya, o inventan números donde el caso no da datos.

El lateral como está queda verificado y no se toca. La forma mínima
es propuesta, no implementación: reescribir es decisión de Mj.
