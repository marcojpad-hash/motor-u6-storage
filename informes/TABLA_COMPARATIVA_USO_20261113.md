# TABLA COMPARATIVA — piezas autorizadas USADAS (U0–U4)

Fecha: 2026-11-13. Rama: `alterno/motor-autorizado` (base 6909a2a, observación).
Orden de Marco 2026-11-13 ~05:23 CST: las piezas NO son de adorno; hay que USARLAS,
no solo observarlas. Añadido ~05:24 CST: medir si las GRÁFICAS se vuelven más
estables cuando la pieza se USA.

## Método (por partes, acumulativo)

- U0 observación (baseline: las 4 piezas solo como traza, can_decide_H False).
- U1 nicho USADO (voto nicho_campo alimenta rank_fusion; `USO_NICHO=1`).
- U2 + alias USADO (tokens del alias en la entrada, eje P).
- U3 + embudo USADO (RUIDO_ALIAS quita los clínicos; PERFIL_VENTANA deja).
- U4 + fix USADO (la entrada ES el caso preparado: alias + remap
  ambicion→autonomia por corte + embudo).
- 8 casos por etapa: 5 sondas mínimas (Monroe, Alejandro, José A, José E-F,
  Freud C) + Napoleón F001 (3 cortes) + 2 largos (Mozart 10, Napoleón 10).
- StinkBox reseteado por etapa (vacío al arrancar cada etapa). Los casos corren
  en el mismo orden en todas las etapas.
- Corredor: `casos/sondas_nicho_minima/correr_uso.py <ETAPA>`.
  Preparación: `casos/sondas_nicho_minima/preparar_uso.py`.
  Estabilidad: `casos/sondas_nicho_minima/estabilidad.py`.
- Resúmenes: `motor/runs_uso/U0/RESUMEN_U0.json` … `U4/RESUMEN_U4.json`.
  RESULT completos en la copia de trabajo: `motor/RESULT_U<ETAPA>_<CASO>.json`
  (no se suben por tamaño; el RESUMEN trae H1/H2 + estabilidad extraída).
- exit=4 en los largos = INCOMPLETE_OUTPUT_DATA pre-existente
  (`$.efectividad_corte_retenido.previo_error`); el RESULT se escribe completo.

## Lo que NO cambió

- **F no se tocó.** El nicho alimenta el ranking por la vía lateral existente
  (voto `nicho_campo` en el hub, recogido por el puente de nombres como señal
  lateral normalizada 0..1). No se multiplicó dentro de F. NO es V6.
- **Engine canónico intacto**: sha256
  `665c39a2861e58772522e91272563260d980908b1d4ab9f7092d3413d0c36082`.
- **Catálogo 244 intacto**: sha256
  `d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1`,
  244 familias, 703 tokens distintos.
- **Suite**: `pytest motor/tests/` = **148 passed / 2 skipped** (igual que en
  la etapa de observación). Nada roto.
- Único archivo de código cambiado vs 6909a2a:
  `motor/motor/laterales_unico_v1.py` (+49 líneas: helper `_voto_nicho` y
  enganche `USO_NICHO=1` en `pre_predictor`, antes de `return votos, det, reg`).
  Sin la variable, el nicho sigue siendo solo traza (comportamiento U0).

## 1. Delta POR PIEZA en H1/H2 (observación vs usado)

Margen = rank_fusion top1 − top2 del predictor (H1−H2). `=` = sin cambio.

| caso | U0 observación | U1 nicho | U2 +alias | U3 +embudo | U4 +fix |
|---|---|---|---|---|---|
| Monroe | schwartz_10_autodireccion / tainter_04 (11.61) | = | = | = | = H1/H2; margen 11.76 |
| Alejandro | gobernante / 30_ambicion (2.24) | = H1/H2; margen 0.62 | = | = H1/H2; margen 1.34 | = H1/H2; margen 0.62 |
| José A | creador / schwartz_10 (4.18) | = | creador / **musicos_populares** (4.64) | creador / schwartz_10 (4.18) | = H1/H2; margen 3.18 |
| José E-F | schwartz_10 / creador (0.82) | = | **creador / schwartz_10** (1.95) | = U2 | = U2 |
| Freud C | sustancias_03 / mentalidad_liberal (1.63) | = | = H1/H2; margen 1.83 | = U2 | = U2 |
| Napoleón F001 | conflicto_con_un_dios / gobernante (2.79) | = H1/H2; margen 1.84 | conflicto / **30_ambicion** (1.85) | conflicto / gobernante (1.89) | conflicto / **30_ambicion** (2.04) |
| Mozart 10 | autonomia_atenas / mentalidad_liberal (4.07) | = H1/H2; margen 4.77 | = U1 | = U1 | autonomia_atenas / **schwartz_10** (7.69) |
| Napoleón 10 | gobernante / mercado (0.74) | **mercado / gobernante** (0.08) | **gobernante / 30_ambicion** (0.22) | = U2 | **autonomia_atenas / gobernante** (1.48) |

### Lectura por pieza

**U1 — nicho usado.** Entra al ranking: `nicho_campo` aparece en
`predictor.lateral_signal_registry` (discriminates True, rank_eligible True;
en Napoleón 10: mercado 0.69, gobernante 0.31, ambicion 1.0) y NO estaba en U0.
Efecto: 7/8 casos conservan H1/H2; **Napoleón 10 VOLTEA H1**
(gobernante→mercado, margen 0.74→0.08, casi empate). Alejandro y Napoleón F001
pierden margen (2.24→0.62 y 2.79→1.84: el voto empuja a 30_ambicion, H2 en
ambos). Mozart GANA margen (4.07→4.77). Monroe, José A, José E-F, Freud: sin
cambio (la traza nicho es cero para sus familias top).

**U2 — alias usado.** El alias solo dispara en 2/8 casos (total de tokens
agregados: José A 1, José E-F 2; los otros 6: 0). Directo:
- José A: alias añade `consumo_sustancias` 0.78 en C1 P → H2 pasa a
  `trayectoria_musicos_populares` (tiene consumo_sustancias 0.85 como favor).
- José E-F: alias añade `consumo_sustancias` 0.78 + `desgaste_cambaceo_itinerante`
  en C5 P → **H1/H2 SE VOLTEAN** (creador pasa a H1, margen 0.82→1.95).
- Indirecto (StinkBox, ver §3): Freud margen 1.63→1.83; Napoleón F001 H2
  gobernante→30_ambicion; Napoleón 10 H1 vuelve a gobernante y H2 pasa a
  30_ambicion. Monroe, Alejandro, Mozart 10: sin cambio.

**U3 — embudo usado.** Directo:
- José A: RUIDO_ALIAS en C1 → quita `consumo_sustancias` → **revierte a U1**
  (H2 vuelve a schwartz_10, margen 4.18). El embudo deshace el alias cuando el
  token clínico va solo, sin co-token.
- José E-F: PERFIL_VENTANA en C5 → **NO quita nada** (los 2 tokens del alias
  juntos forman par con co-token; se dejan). Se queda en U2.
- Freud: PERFIL_VENTANA en C3 (clínico original con co-token de oficio) →
  no quita nada. Sin cambio.
- Indirecto (StinkBox + marca, ver §3 y §4): Alejandro margen 0.62→1.34;
  Napoleón F001 H2 vuelve a gobernante (margen 1.89); Napoleón 10 = U2.

**U4 — fix usado (remap por corte).** Remapes aplicados: Monroe 1 (C2_1955),
Napoleón F001 1 (C3_1812), Mozart 10: 3 (C6, C9, C10), Napoleón 10: 4
(C1–C4). Alejandro, José A, José E-F, Freud: 0 remapes.
- Monroe: H1/H2 =, margen 11.61→11.76.
- Napoleón F001: H2 vuelve a 30_ambicion (2.04).
- Mozart 10: H2 pasa a `schwartz_10_autodireccion`, margen 4.77→7.69.
- **Napoleón 10: H1 pasa a `utopia_autonomia_atenas`** (margen 1.48). El remap
  convierte ambicion→autonomia en C1–C4 (antes de las conquistas) y corona
  la familia de autonomía. Con el remap, los dos casos largos coronan lo
  mismo (autonomia_atenas). Si eso es correcto o es un artefacto del remap,
  es decisión de Marco (ver §5).
- Indirecto: Alejandro margen vuelve a 0.62; José A margen 4.18→3.18
  (exactamente −1.0, sin cambio en su entrada: puro arrastre, ver §3).

## 2. Estabilidad de la gráfica por pieza (¿se vuelve más estable?)

persist_cos = coseno medio entre vectores R732 de cortes consecutivos.
kappa_dir = concentración direccional. dX_norm = norma media del cambio entre
cortes (R732). margenP = margen top1−top2 del tablero P por corte (media).
Hélice = PCA a 3 componentes + ajuste helicoidal (DESCRIPTIVO, no validación
física). `=` = idéntico a la etapa anterior.

### Casos largos (Napoleón 10 y Mozart 10)

| caso | etapa | persist | kappa | dX media | margenP media | hélice giro/paso | hélice radio |
|---|---|---|---|---|---|---|---|
| Napoleón 10 | U0 | 0.192 | 0.886 | 0.270 | 0.0184 | −34.47° | 0.218 |
| Napoleón 10 | U1 nicho | = | = | = | = | = | = |
| Napoleón 10 | U2 alias | = | = | = | = | = | = |
| Napoleón 10 | U3 embudo | = | = | = | = | = | = |
| Napoleón 10 | U4 fix | 0.254 | 0.875 | 0.322 | **0.0014** | −34.02° | 0.298 |
| Mozart 10 | U0 | 0.265 | 0.923 | 0.222 | 0.0215 | −37.64° | 0.170 |
| Mozart 10 | U1–U3 | = | = | = | = | = | = |
| Mozart 10 | U4 fix | 0.241 | 0.920 | 0.248 | 0.0199 | −38.59° | 0.180 |

### José E-F (única sonda con hélice, 6 cortes)

| etapa | persist | kappa | dX media | margenP media | hélice giro | hélice radio | radial_cv |
|---|---|---|---|---|---|---|---|
| U0/U1 | 0.602 | 0.611 | 0.212 | 0.0747 | 4.24° | 0.237 | 0.016 |
| U2 alias | **0.225** | 0.934 | **0.286** | 0.0635 | 74.39° | 0.129 | 0.127 |
| U3 embudo | = U2 | = U2 | = U2 | = U2 | = U2 | = U2 | = U2 |
| U4 fix | = U2 | = U2 | = U2 | = U2 | = U2 | = U2 | = U2 |

### Veredicto de estabilidad: NO, no se vuelve uniformemente más estable

- **Nicho (U1): la gráfica NO cambia en absoluto.** El voto nicho no toca el
  tablero P (no cambia ningún vector R732), así que persist, kappa, dX y la
  hélice son idénticos en los 8 casos. Solo mueve el margen final H1/H2.
- **Alias (U2): DESESTABILIZA el caso que toca.** José E-F: persist 0.60→0.23
  (la dirección deja de persistir), dX 0.21→0.29 (saltos más grandes, máx
  0.35→0.52), radio de la hélice 0.24→0.13 y radial_cv ×8 (0.016→0.127: el
  radio se vuelve mucho menos estable), giro 4°→74°. Ojo: kappa SUBE
  (0.61→0.93) mientras persist BAJA: las dos medidas de dirección no se
  mueven juntas; "estabilidad" no es un solo número. José A apenas se mueve
  (persist −0.069→−0.069, dX =), pero su margenP por corte se TRIPLICA
  (0.027→0.083: el tablero P por corte se vuelve más firme).
- **Embudo (U3): restaura a José A pero NO a José E-F.** José A vuelve a los
  valores U1 (persist, dX, margenP). José E-F se queda en los valores U2
  (el embudo no quitó sus 2 tokens porque forman PERFIL_VENTANA).
- **Fix/remap (U4): MIXTO.** Monroe MEJORA (persist 0.45→0.53, dX 0.58→0.53:
  menos saltos, dirección más persistente). Napoleón 10 MEJORA en persist
  (0.19→0.25) pero EMPEORA en dX (0.27→0.32) y **su margenP por corte
  COLAPSA (0.018→0.001: top1 y top2 casi empatados por corte)**; la hélice
  casi no se mueve (giro −34.5°→−34.0°, radio 0.22→0.30). Mozart 10 apenas se
  mueve (persist 0.27→0.24, hélice −37.6°→−38.6°, radio 0.17→0.18).
- **La hélice es lo más estable de todo.** En los largos, el giro por paso
  cambia menos de 1° entre U0 y U4 (−37.64°→−38.59° Mozart; −34.47°→−34.02°
  Napoleón). El remap no reorienta la hélice; solo cambia su radio y el
  margen. Para vectorizar el futuro, la hélice aguanta; lo que se mueve es
  el ranking y el margen por corte.

## 3. Efecto indirecto: el StinkBox arrastra (hay que leer el delta con cuidado)

El delta entre etapas NO es solo la pieza: dentro de una etapa los casos
corren en orden y cada uno deja su bóveda en el StinkBox; el siguiente caso
la lee (`features.stinkbox_transport.feeds_predictor: true`,
`stinkbox_support` es una dimensión del ranking). El motor es determinista
(el mismo caso con la misma entrada y el mismo prefijo de StinkBox da el
mismo margen al decimal: Monroe 11.6109 idéntico en U0/U1/U2/U3), así que
estos cambios son arrastre real, no ruido.

Prueba (Napoleón 10): su entrada es IDÉNTICA en U1 y U2 (sin hechos, el
alias no añade nada), pero su H1 voltea (mercado→gobernante). La causa es el
StinkBox: `stinkbox_support` de gobernante 0.8125→1.0 y de mercado 1.0→0.8125
entre U1 y U2 (las bóvedas de José A/E-F cambiaron porque el alias cambió
sus entradas). El arrastre explica también: Freud U1→U2 (margen 1.63→1.83,
entrada idéntica), Napoleón F001 U1→U2 (H2→ambicion), Alejandro U3→U4
(margen 1.34→0.62, 0 remapes en su entrada) y José A U3→U4 (margen −1.0
exacto, 0 remapes en su entrada).

Consecuencia para leer la tabla: el delta de un caso es DIRECTO (su entrada
cambió) + INDIRECTO (las bóvedas de los casos anteriores cambiaron). En §1
está marcado cuál es cuál. El orden de los casos es el mismo en todas las
etapas, así que la comparación es válida como "efecto acumulado de la pieza
en la etapa", no como "efecto aislado por caso".

## 4. Hallazgo: la marca del embudo NO es neutra (efecto colateral)

La marca `"embudo"` que `preparar_uso.py` escribe en cada corte (incluso
`"NO_APLICA"`) cambia el ranking aunque no quite ningún token. Prueba
(Alejandro U2→U3: entrada idéntica salvo el campo `"embudo": "NO_APLICA"`):
- `stinkbox_support` idéntico (gobernante 0.9444, ambicion 0.5556) y señal
  `nicho_campo` idéntica (gobernante 0.518, ambicion 0.912) y registro de
  señales laterales idéntico (las mismas 10).
- Lo que cambia es `caldero_neighbor_alignment` (gobernante 0.889→1.0,
  ambicion 0.667→0.278) y `lateral_shared_evidence`. Margen 0.62→1.34.
- Mecanismo: la marca cambia lo que el caso anterior persiste en la memoria
  de vecinos del Caldero (`persistent_neighbor_lights`), y el siguiente caso
  lee esos vecinos (`MOTOR_V15_3_UNICO_20260927.py:1349`, la alineación usa
  `current_neighbors | persisted_neighbors`).

Es decir: marcar un corte ya es intervenir (el Caldero lee la marca). Si se
quiere que el embudo SOLO filtre sin tocar el Caldero, la marca no debe ir
en la entrada que lee el motor (o el Caldero debe ignorar ese campo).
Pendiente de decisión, no se cambió nada por eso.

## 5. Veredicto de la prueba mínima (5 sondas + Napoleón, piezas USADAS)

La prueba mínima de la etapa de observación era: H1/H2 sin cambio en los 6
casos cuando las piezas solo se observaban (5/5 PASA en el sentido de que el
cableado no rompía nada). Con las piezas USADAS, el veredicto cambia:

- **Las piezas SÍ afectan el resultado (era lo pedido).** 5 de 8 casos cambian
  H1, H2 o margen en alguna etapa. Ningún test se rompe y ninguna corrida
  falla (8/8 por etapa, 40/40 en total).
- **Nicho: discrimina y puede voltear.** Voltea Napoleón 10 (H1) con margen
  casi cero (0.08). En márgenes pequeños, el voto nicho decide; en márgenes
  grandes, no mueve H1/H2.
- **Alias: estrecho y ruidoso.** Solo dispara en 2/8 casos, y en uno de ellos
  (José E-F) voltea H1/H2 y desestabiliza la trayectoria. El alias sigue
  siendo ciego a negaciones (hallazgo previo, no re-verificado aquí).
- **Embudo: filtra lo aislado, deja lo acompañado.** Quita el token clínico
  solo (José A) y deja el par (José E-F). Esa asimetría es la que deja a
  José E-F volteado y desestabilizado en U3/U4.
- **Fix/remap: el de mayor efecto en los largos.** Cambia el H1 de Napoleón
  10 a autonomia_atenas y el H2 de Mozart 10 a schwartz_10, y colapsa el
  margen por corte de Napoleón (0.001). El remap ES por corte (verificado:
  Napoleón 10 solo C1–C4; Mozart 10 solo C6/C9/C10; Monroe solo C2_1955).

**Decisiones pendientes (para Marco, no se tomaron aquí):**
1. ¿El remap debe ser POR CORTE o POR VIDA ENTERA? Con por corte, Napoleón
   corona autonomia_atenas por sus 4 primeros cortes (antes de las
   conquistas). Con por vida entera (si hay conquista en algún corte, no se
   remapa nada), Napoleón no se remaparía y su H1 seguiría siendo gobernante
   o mercado. El dato está medido; la regla, no.
2. ¿Nicho/fix deben CAMBIAR la H (sería V6)? Aquí cambian H1/H2 por la vía
   lateral (voto) y por la entrada (remap), sin tocar F. Multiplicar dentro
   de F seguiría siendo V6 y no se hizo.
3. ¿La marca del embudo debe ir en la entrada (con su efecto en el Caldero)
   o solo en el reporte? (ver §4).
4. Grupo B (¿el alias debe entrar también en el Grupo B?) y guarda de
   negación del alias: pendientes, no se tocaron.
5. ¿Se acepta que Napoleón 10 corone autonomia_atenas con el remap, o eso
   invalida el remap por corte? Es el resultado más fuerte de U4 y el que
   más necesita el ojo de Marco.

## Archivos (espejo de rutas, para subir a alterno/motor-autorizado)

- `motor/motor/laterales_unico_v1.py` (único código cambiado; +49 líneas).
- `casos/sondas_nicho_minima/preparar_uso.py` (nuevo).
- `casos/sondas_nicho_minima/correr_uso.py` (nuevo).
- `casos/sondas_nicho_minima/estabilidad.py` (nuevo).
- `casos/sondas_nicho_minima/uso/U2/*.json`, `uso/U3/*.json`, `uso/U4/*.json`
  (entradas preparadas que se corrieron; U0/U1 usan la cruda).
- `motor/runs_uso/U0/RESUMEN_U0.json` … `motor/runs_uso/U4/RESUMEN_U4.json`.
- `informes/TABLA_COMPARATIVA_USO_20261113.md` (esta tabla).
- NO se incluyen: los RESULT completos (`motor/RESULT_U*_*.json`, 40 archivos,
  ~1–8 MB c/u; quedan en la copia de trabajo), el StinkBox
  (`STINKBOX_PERSISTENTE/`, `STINKBOX_STORAGE/`, estado de corrida), ni los
  RESULT_BASELINE de la etapa anterior. El cambio pendiente en
  `fuentes_originales/202609/DOSSIER_V15_1_20260914/docs/04_READMES_CANDADOS_Y_PROTOCOLOS.txt`
  es de la etapa de observación, no de esta; no se incluye aquí.
