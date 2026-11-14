# Relación de los factores: por qué se puede hacer proporcional — 2026-11-13

## Pregunta (Marco)
Encontrar la relación de los factores para ver si por eso lo podemos hacer
proporcional.

## Método
55 casos del archivo (F001-F004, ciegos, transiciones, héroes, Napoleón,
Mozart, Bolívar, Curie, Churchill). Para cada caso se midió el peso de H1
(Sol) en Z y los factores: n_cortes, n_tokens del input, tokens por corte,
masa_favor total de H1, activación de H1 en Z.

## Correlaciones con el peso de H1 (Sol)
| Factor | Correlación |
|--------|-------------|
| tokens por corte | **0.485** |
| masa_favor total de H1 | **0.439** |
| n_tokens del input | 0.423 |
| n_cortes | 0.385 |
| activación de H1 en Z | 0.303 |

## La relación
El peso del Sol es PROPORCIONAL a la riqueza del input:
- **Tokens por corte** (el factor más fuerte, 0.485): más tokens por corte
  -> Sol más fuerte. Los 5 más bajos tienen 3-36 tokens; los 5 más altos
  37-346.
- **Masa_favor de H1** (0.439): la evidencia directa que apoya al Sol.
  Los 5 con menor masa_favor H1 (0.70-0.75: Faraday, Tesla, Coolidge,
  Pedro II, Bach) tienen peso 0.5-0.70. Los 5 con mayor masa (7.04-10.42:
  Anónimo2, Anónimo, Bolívar, Semmelweis, Mozart) tienen peso 0.786-0.816.
- **N_cortes** (0.385): el piso sube con más cortes. 3 cortes: media 0.724,
  min 0.5. 6 cortes: media 0.778, min 0.746. 7 cortes: media 0.787, min
  0.734. 10 cortes: media 0.787, min 0.754. Con más cortes el Sol es más
  confiablemente fuerte.

## Por qué se puede hacer proporcional
El Sol (la masa que jala) es proporcional a la evidencia: a más tokens por
corte, más masa_favor de H1 y más cortes, más fuerte el Sol (más cerca de
0.80) y más fuerte el tirón. A menos evidencia, Sol más débil (0.5-0.7) y
tirón más débil. Por eso la FUERZA de la predicción se puede escalar con
estos factores: la confianza y la velocidad de convergencia hacia el Sol son
proporcionales a la riqueza del input. Un caso rico predice fuerte; un caso
flaco predice débil. La constante ~0.79-0.80 es el techo al que llega el Sol
cuando la evidencia es suficiente.

## Archivos
- `motor/FACTORES_PESO_SOL_20261113.json` (factores por caso).
- `motor/FACTORES_PESO_SOL_V2_20261113.json` (con masa_favor y activación de H1).
