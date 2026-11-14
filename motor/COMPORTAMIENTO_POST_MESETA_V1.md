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

## Verificación
- `leer_resultado` contra `RESULT_NAPOLEON_10CORTES_FINAL27.json` (2026-11-13):
  en_meseta True, 7 familias bajo el top5 suben de rango, 0 cocinando,
  0 emergentes por umbral, punto no considerado `dumezil_f2_fuerza`
  (rango Z 23, pendiente 1.0286, LATENTE_DORMIDO). Trazabilidad
  micro 0.470833 / meso 0.48587 / macro 0.528572.
