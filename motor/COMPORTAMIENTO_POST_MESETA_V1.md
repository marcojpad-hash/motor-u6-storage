# COMPORTAMIENTO_POST_MESETA_V1 — Contrato

## Idea (Marco, 2026-11-13)
No es leer nada más el fondo. Una vez que la medición SE ESTABILIZA
(régimen `MESeta_O_ESTABILIZACION`), se ve el COMPORTAMIENTO: cómo se mueve
TODO en general (no solo abajo). Eso da trazabilidad y puede hacer emerger un
punto que antes no se había considerado. Y se tiene que MENCIONAR tal cual en
la salida, porque si no los modelos que traducen el motor no lo ven: su
entrenamiento es ver los top, entonces no ven lo que pasa abajo.

Equivalente a cuando se encontró el eje que se armaba con las fórmulas
después de ver la hélice: la estabilización revela el comportamiento.

## Regla
- **Disparador:** el régimen dominante es `MESeta_O_ESTABILIZACION`.
- **Lectura (una vez estabilizado):**
  - `comportamiento`: cómo se mueve todo — resumen de clases del fondo
    (LATENTE_DORMIDO / PICO / DESCENSO / ASCENSO_LENTO / MESETA), cuántas
    familias bajo el top5 suben de rango, qué se cocina abajo (familias y
    tokens), y las formas de picos/mesetas por familia.
  - `lo_que_emerge`: familias/tokens con `emergente: True` del fondo,
    ordenados por pendiente (peso). Superposición: se activan en conjunto
    según la carga semántica, sin deduplicación ni doble peso.
  - `punto_no_considerado`: lo que emerge (o sube de rango) y NO está en el
    top que ven los modelos (H1/H2 + top5 del 020). Es el punto que antes no
    se había considerado y que los modelos no ven por mirar solo el top.
  - `trazabilidad`: régimen + micro/meso/macro + aceleración + divergencia
    entre escalas + n_cortes (el eje geométrico en meseta).
  - `lectura`: una frase en humano con el comportamiento.
- **Si NO hay meseta:** el lateral queda mudo (`en_meseta: False`).

## Contrato duro
- `can_decide_H = False`. SENSOR, solo observa. No toca H1/H2, ranking,
  Engine ni catálogo 244. No reordena. No escribe canónico.
- No es una matriz rígida: la activación es conceptual según el contexto
  (la regla de activación de tokens de Marco, 2026-11-13).

## Fuentes (ya existen, el lateral solo las lee)
- `movimiento_de_fondo_u4.py` (pedido de Marco, 11-oct): EMERGE, clases,
  `lo_que_se_cocina_abajo`, `familias_bajo_top5_subiendo_de_rango`.
- `plugin_picos_mesetas.py`: curvas por familia (serie, deltas, forma).
- `trazabilidad_geometrica` de las candidatas (régimen, micro/meso/macro).

## Cableado
- El fondo corre DESPUÉS de `post_predictor` en el motor
  (MOTOR_V15_3_UNICO_20260927.py:3322, post_predictor en :3061). Por eso el
  lateral tiene dos entradas:
  - `observar(case, motor, pred)` para `post_predictor`: lee el régimen de
    pred; si hay meseta, deja constancia y remite a la lectura completa.
  - `leer_resultado(result)` para post-corrida: lee el RESULT completo
    (fondo + picos + régimen) y produce la lectura completa.
- La lectura completa va en `laterales_unico.post.comportamiento_post_meseta`
  (cuando se corre post-corrida) y queda en el repo junto al RESULT.

## Gravedad (Marco, 2026-11-13) — `leer_gravedad(result)`
NO es gravedad terrestre. Es inercia de gravedad como un cometa que arrastra,
o como el sol jalando a todos los cuerpos celestes dentro de su casa (la Vía
Láctea). Se mide sobre los NUDOS que se movieron (las familias bajo el top5
subiendo de rango) y se busca PROPORCIONALIDAD.

- **SOL:** la familia más pesada (H1), el atractor central. Todo es jalado
  hacia su peso (P_FULL_244 en Z).
- **NUDOS:** cada familia que se movió, con peso en Z, distancia al Sol y
  pendiente. Estados:
  - `CAPTURADO`: ya llegó al peso del Sol (distancia <= 0.01).
  - `SIENDO_JALADO`: lejos del Sol (dist > 0.05) y sube rápido (pend >= 0.5).
  - `ACERCANDOSE` (v2): lejos del Sol (dist > 0.05) y sube a velocidad media
    (0.2 <= pend < 0.5). Antes caía en EN_TRANSITO aunque estuviera lejos.
  - `RESISTE`: lejos del Sol pero no sube (pend < 0.2): su propia gravedad,
    posible atractor rival.
  - `EN_TRANSITO`: cerca del Sol (0.01 < dist <= 0.05), aún no capturado,
    a cualquier velocidad.
- **COMETA:** el corte donde varios nudos saltan a la vez (un arrastre).
  Desempate (v2): en empate de (nudos_que_suben, salto_total) gana el corte
  más temprano (primera ocurrencia).
- **PROPORCIONALIDAD:** correlación de Pearson pendiente ~ distancia al Sol
  (mínimo 3 nudos). Varianza cero (todos los nudos con la misma distancia o
  pendiente) -> null (indefinida). Siempre va con su n y su confianza (v2):
  BAJA_MUESTRA si n<8, MEDIA si 8-11, ALTA si n>=12. Con pocos nudos un solo
  valor atípico puede invertir el signo.

## Proyectivo (Marco, 2026-11-13) — `proyectar_gravedad(result, hasta_corte)`
La retrospectiva (leer_gravedad) NO se elimina: queda como referencia para
comparación e ingeniería inversa. Lo proyectivo es una ADICIÓN.

Lee solo los cortes hasta `hasta_corte` y proyecta hacia adelante:
- **Captura prevista:** si la distancia al Sol se cierra de forma monótona
  (últimos 3 cortes), se extrapola el corte en que llega a 0. Si oscila o no
  se cierra: NO_PROYECTABLE.
- **Pulso / alerta de cometa:** si en el corte llegó masa_favor (>0), un
  pulso acaba de entrar. Los pulsos se repiten a los ~3-4 cortes (Napoleón
  C5->C9, Mozart C6->C9): se advierte un posible cometa en los siguientes
  1-3 cortes (alerta, no predicción exacta).
- **Dirección:** signo de la proporcionalidad hasta ahora.

LÍMITE HONESTO: el salto del cometa lo causa un pulso nuevo de masa_favor
que llega con el contenido del corte (tokens nuevos del input). No se puede
predecir el corte exacto ni el tamaño del salto antes de que el pulso llegue,
porque eso sería predecir el contenido del siguiente corte. Lo proyectivo es
la extrapolación de la tendencia y la alerta temprana cuando el pulso ya entró.

## Verificación
- `leer_resultado` contra `RESULT_NAPOLEON_10CORTES_FINAL27.json` (2026-11-13):
  en_meseta True, 7 familias bajo el top5 suben de rango, 0 cocinando,
  0 emergentes por umbral, punto no considerado `dumezil_f2_fuerza`
  (rango Z 23, pendiente 1.0286, LATENTE_DORMIDO). Trazabilidad
  micro 0.470833 / meso 0.48587 / macro 0.528572.
- **Gravedad en FINAL27:** sol `arquetipo_el_gobernante` (peso Z 0.7813);
  capturados `predictivo_02_mdp_politica_optima` y
  `situacion_dramatica_ambicion` (peso = sol, 0.781); siendo jalados
  `dumezil_f2_fuerza`, `utopia_mentalidad_milenarista`, `frye_mythos_romance`;
  resiste `dumezil_desequilibrio_f2_come_al_resto` (el más lejos, 0.145, pero
  el más lento, 0.114 — su propia gravedad, "come al resto"); en tránsito
  `dumezil_f3_fecundidad`. Cometa en **C9** (3 nudos suben, salto total 0.32).
  Proporcionalidad pendiente~distancia: **0.568**.
- **Proyectivo en FINAL27:** hasta C5 predice captura de predictivo_02 y
  situacion_ambicion en C7 (real: C6, a 1 corte) y de dumezil_f3 en C9
  (real: 0.014 en C10, casi capturado). Hasta C8 el pulso (3 nudos) alerta
  cometa en 1-3 cortes y el cometa real es C9 (a 1 corte). La
  proporcionalidad ya es estable desde C4 (0.675) hasta C8 (0.665).
