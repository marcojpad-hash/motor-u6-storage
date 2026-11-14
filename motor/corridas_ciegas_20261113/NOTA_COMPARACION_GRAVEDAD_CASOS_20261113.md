# Comparación de gravedad entre casos — 2026-11-13

Métrica: `lateral_comportamiento_post_meseta_v1.leer_resultado` (gravedad:
sol / nudos / cometa / proporcionalidad). Solo lee cuando el régimen es
MESeta_O_ESTABILIZACION; si no, queda muda.

## Tabla

| Caso | Régimen | Sol (H1) | Peso Sol Z | Nudos | Capturados | Jalados | Resisten | Cometa | Proporc. |
|------|---------|----------|-----------|-------|-----------|---------|----------|--------|----------|
| NAPOLEON_FINAL27 | MESETA | gobernante | 0.7813 | 7 | 2 | 3 | 1 (dumezil_desequilibrio) | C9 (3, 0.32) | +0.568 |
| MOZART_Z90 | MESETA | autonomia_atenas | 0.7985 | 6 | 0 | 1 | 1 (dumezil_f3_fecundidad) | C6 (6, 0.482) | **-0.777** |
| TESLA_F001_02 | CONTINUIDAD_ASCENDENTE | — | — | 0 | 0 | 0 | 0 | — | — |
| TRANSICION1_Z90 | MESETA | creador | 0.8006 | 20 | 0 | 12 | 2 (schwartz_10, dumezil_desequilibrio) | C7_1448 (8, 0.651) | +0.295 |
| MANDELA_HEROE | MESETA | kwml_01_rey | 0.8013 | 16 | 1 (anacyclosis_01_monarquia) | 9 | 1 (dialectica_01_tesis) | C3_1961 (10, 1.077) | +0.078 |

## Lo que se ve al comparar

- **La proporcionalidad cambia de signo.** Napoleón +0.568 (lejos del sol =
  sube más rápido, como caer hacia el sol). Mozart **-0.777** (cerca del sol
  = sube más rápido, la gravedad clásica: el tirón es más fuerte cerca).
  Son dos regímenes gravitatorios distintos. Mandela ~0 (0.078, sin patrón
  claro) y Transición1 débil (+0.295).
- **El cometa cambia de tamaño y momento.** Napoleón C9 (3 nudos, 0.32).
  Mozart C6 (6 nudos, 0.482). Mandela C3_1961 (10 nudos, salto 1.077, el
  más grande). Transición1 C7_1448 (8 nudos, 0.651).
- **Tesla no está en meseta** (CONTINUIDAD_ASCENDENTE): la métrica queda
  muda, como debe ser. No se fuerza la lectura.
- **El que resiste se repite.** `dumezil_desequilibrio_f2_come_al_resto`
  resiste en Napoleón Y en Transición1 (en ambos, lejos del sol y lento).
  En Mandela resiste `dialectica_01_tesis_estabilidad_hegemonica`; en Mozart
  `dumezil_f3_fecundidad`.
- **Punto no considerado por caso:** Napoleón dumezil_f2_fuerza; Mozart
  situacion_dramatica_ambicion; Transición1 schwartz_09_estimulacion;
  Mandela arquetipo_el_cuidador.

## Archivos
- `motor/COMPARACION_GRAVEDAD_CASOS_20261113.json` (la tabla completa).
- Casos leídos: RESULT_NAPOLEON_10CORTES_FINAL27, RESULT_MOZART_CON_TEXTO_Z90_20261113,
  RESULT_CAL_F001_02_TESLA, RESULT_TRANSICION1_Z90_20261113,
  RESULT_MANDELA_HEROE_20261112 (todos en motor-cameo, motor/).
