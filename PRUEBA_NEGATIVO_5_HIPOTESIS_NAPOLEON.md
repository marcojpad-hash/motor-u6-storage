# Prueba del negativo con 5 hipótesis — Napoleón (F001_01)

Fecha: 2026-11-11. Corrida base: `RESULT_CAL_F001_01_NAPOLEON.json` (F001, 3 cortes).
Método: top 5 candidatos por `predictor.candidates` (rank_fusion) y lectura por
negativo según `motor/motor/lectura_negativo_ricci_vs_billar_v0_1.py` (cuadrantes
§2.3 del contrato). Billar por familia: `n_conv` de la feature embebida.
Ricci por familia: media de Ric_F de las aristas incidentes, calculada corriendo
`ricci_forman_coocurrencia_v0_1.correr_cuts` sobre los cortes del RESULT (50 aristas).

## Top 5 hipótesis

| # | Familia | rank_fusion | Billar n_conv | Ricci media | Cuadrante | Señal |
|---|---------|-------------|---------------|-------------|-----------|-------|
| 1 | 31_conflicto_con_un_dios | 28.6956 | 3 (sí) | +0.0678 (5 aristas, 0 neg) | SOLO_BILLAR | SE_SOSTIENE |
| 2 | 30_ambicion | 26.5468 | 3 (sí) | +0.0438 (20 aristas, 0 neg) | SOLO_BILLAR | SE_SOSTIENE |
| 3 | arquetipo_el_gobernante | 26.106 | 2 (sí) | +0.0438 (20 aristas, 0 neg) | SOLO_BILLAR | SE_SOSTIENE |
| 4 | bbk_01_aventurero | 19.05 | 0 (no) | sin aristas (no viva en Ricci) | SIN_RICCI | LATENTE |
| 5 | anacyclosis_01_monarquia | 18.35 | 0 (no) | sin aristas (no viva en Ricci) | SIN_RICCI | LATENTE |

## Resultado: 5 → 5. Cero descartados.

El negativo NO reduce el número de hipótesis en esta corrida.

Por qué:
1. **No hay ninguna arista con Ric_F < 0.** De las 50 aristas, 0 son negativas
   (rango 0.0199 a 0.0678, todas positivas). La señal de "Ricci negativo" nunca
   se dispara, así que ningún candidato puede caer en SOLO_RICCI (DESCARTE) ni
   en AMBOS (TENSION_LATENTE).
2. Las 2 familias sin convergencia de billar (bbk_01_aventurero,
   anacyclosis_01_monarquia) tampoco están vivas en Ricci, así que quedan
   LATENTE, no se descartan.
3. **Las dos lentes están por debajo del nulo:** billar z = 0.825 y ricci
   z = 1.3885, ambas < Z_MIN = 2.0. Aunque hubiera señal, iría marcada
   _BAJO_NULO (se reporta, no se promueve).

## Lectura

El proxy actual (`TEMPORAL_WEIGHT_DRIFT_PROXY_NOT_EXACT_FORMAN`,
`forman_ricci_verified: False`) no produce curvatura negativa en esta corrida:
es tanh de diferencias de medias, y en este caso todas salen positivas. Sin
negativo no hay descarte. Esto es coherente con el contrato §7: el "Ricci" de
hoy es otro Richie, una creación porque no se encontraba el extraviado. Para
que el negativo pueda reducir hipótesis, la curvatura tiene que poder ser
negativa de verdad (la primitiva exacta sobre un grafo validado), no solo un
proxy que en la práctica nunca baja de cero.
