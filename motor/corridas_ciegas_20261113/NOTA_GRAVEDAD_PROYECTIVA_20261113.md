# Gravedad proyectiva — 2026-11-13

## Pedido (Marco)
Encontramos una forma de medir de forma retrospectiva. Analizar cómo funciona
para ver si se puede hacer de forma proyectiva ahora. NO se elimina la
retrospectiva: ayuda para comparación e ingeniería inversa para seguir afinando.

## Análisis del mecanismo (Napoleón FINAL27)
La retrospectiva mide sobre la corrida completa: distancia final al Sol,
pendiente total, corte del salto simultáneo (cometa), correlación.

- **masa_favor** llega en PULSOS (no continuo): dumezil_f2_fuerza 0.82 en C5,
  1.58 en C9; utopia 0.82 en C5, 0.78 en C9. El salto del cometa lo causa un
  pulso nuevo que llega con el contenido del corte (tokens nuevos del input).
- **Distancia al Sol**: se ABRE C1-C4 (el sol sube más rápido), queda PLANA
  C5-C8 (~0.28) para los tardíos, y se PARTE a la mitad en C9 (0.281->0.141).
  Los capturados (predictivo_02, situacion_ambicion) la cierran a 0 en C5-C6.
- **Mozart** confirma el patrón de pulsos (C6 0.74 -> C9-C10 0.68) pero su
  distancia OSCILA (no cierra monótona): la captura no es proyectable ahí.

## Qué sí es proyectivo y qué no
- SÍ: extrapolar la captura cuando la distancia se cierra monótona
  (Napoleón C5 predice predictivo_02/situacion_ambicion en C7; real C6, a 1 corte).
- SÍ: alerta temprana cuando entra un pulso (C8: 3 nudos con pulso -> cometa
  real en C9, a 1 corte). La proporcionalidad ya es estable desde C4 (0.675).
- NO: el corte exacto ni el tamaño del salto del cometa antes de que el pulso
  llegue, porque eso sería predecir el contenido del siguiente corte.
  Las alertas de C4/C5 llegaron antes (el cometa vino a los 4-5 cortes, no 1-3).

## Pieza
`proyectar_gravedad(result, hasta_corte)` en
`motor/motor/lateral_comportamiento_post_meseta_v1.py` (ADICIÓN; la
retrospectiva `leer_gravedad` queda intacta). Verificación: hasta C4, C5 y C8
en FINAL27 (ver contrato COMPORTAMIENTO_POST_MESETA_V1.md).
