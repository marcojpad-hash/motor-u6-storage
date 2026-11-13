# Reporte — Biografía #3, versión 2 (con token consumo_sustancias)

**Fecha:** 2026-11-13 ~02:00 CST
**Caso:** ANONIMO3_Z90_20261113_v2
**Entrada:** `~/workspace/u6-alterno/motor-cameo/casos/precedentes/ANONIMO3_Z90_20261113_v2/entrada.json`
**Resultado:** `~/workspace/u6-alterno/motor-cameo/motor/RESULT_ANONIMO3_Z90_20261113_v2.json`
**Recibo:** COMPLETED, 75.051 s, exit 0
**Cambio respecto a v1:** se agregó el token `consumo_sustancias` a C6 (0.74) y C7 (0.78), los dos cortes donde la dependencia química es explícita.

## El resultado que no esperábamos

Agregar el token directo de consumo **bajó** a las sustancias, no las subió.

| | v1 (sin el token) | v2 (con el token) |
|---|---|---|
| sustancias_03_severo, lugar | #7 | #12 |
| sustancias_03_severo, rank_fusion | 23.40 | 19.47 |
| H1 | 20_sacrificio (28.16) | 20_sacrificio (28.07) |
| H2 | sabio (27.56) | erizo (27.16) |
| Grado | FRAGIL (margen 0.597) | FRAGIL (margen 0.912) |
| Hipótesis en el conjunto | 13 | 15 |
| Apuesta MESETA | 0.733 | 0.642 |
| Apuesta ASCENDENTE | 0.267 | 0.358 |

El H1 sigue siendo el sacrificio y sigue frágil, aunque el margen se acercó al umbral (0.912 contra 1.0). La meseta sigue siendo la apuesta principal, pero más débil. Lo que cambió es que aparecieron dos familias nuevas — trayectoria de músicos populares (#7) y trayectoria de escritores creativos (#8) — y las sustancias cayeron cinco lugares.

## Lo que esto dice de la "censura"

El token no está censurado en el sentido de que el motor lo rechace: lo acepta y sí activa cosas (las dos trayectorias nuevas llegaron por él). Pero la familia de sustancias no se beneficia de su propio token más fuerte. Al revés: cuando el token entra, la familia baja. Eso cuadra con lo que notaste en José José y en los otros casos: el consumo está en los tokens del motor, aparece en las secciones laterales del resultado, pero en el ranking principal no sube como debería. No es que el motor borre el token; es que la familia no lo convierte en lugar. Hay algo estructural ahí que hay que revisar, no es solo el traductor.

## H1 y H2 (v2)

| Puesto | Familia | Grado | rank_fusion | Peso | Relleno |
|---|---|---|---|---|---|
| H1 | 20_sacrificio_por_un_ideal | FRAGIL | 28.070326 | 0.072614 | 58.15% |
| H2 | berlin_01_erizo | FRAGIL | 27.158257 | 0.070255 | 64.52% |

## Top 15 hipótesis (v2)

| # | Familia | rank_fusion | Régimen |
|---|---|---|---|
| 1 | 20_sacrificio_por_un_ideal | 28.070326 | CONTINUIDAD_ASCENDENTE |
| 2 | berlin_01_erizo | 27.158257 | CONTINUIDAD_ASCENDENTE |
| 3 | arquetipo_el_sabio | 26.836431 | MESETA_O_ESTABILIZACION |
| 4 | schwartz_10_autodireccion | 26.7313 | MESETA_O_ESTABILIZACION |
| 5 | arquetipo_el_creador | 26.330211 | MESETA_O_ESTABILIZACION |
| 6 | utopia_mentalidad_liberal | 23.949291 | MESETA_O_ESTABILIZACION |
| 7 | trayectoria_musicos_populares | 23.323529 | CONTINUIDAD_ASCENDENTE |
| 8 | trayectoria_escritores_creativos | 23.0 | CONTINUIDAD_ASCENDENTE |
| 9 | monomito_01_mundo_ordinario | 22.376559 | MESETA_O_ESTABILIZACION |
| 10 | 36_perdida_de_los_seres_queridos | 21.900449 | MESETA_O_ESTABILIZACION |
| 11 | kwml_01_rey | 19.823529 | MESETA_O_ESTABILIZACION |
| 12 | sustancias_03_severo | 19.470588 | CONTINUIDAD_ASCENDENTE |
| 13 | social_14_overton_ventana | 17.117647 | MESETA_O_ESTABILIZACION |
| 14 | ttm_01_precontemplacion | 15.970588 | MESETA_O_ESTABILIZACION |
| 15 | arquetipo_el_gobernante | 15.654945 | MESETA_O_ESTABILIZACION |

## Apuesta (v2)

- **Apuesta principal: MESETA_O_ESTABILIZACION** — 10 hipótesis, soporte 0.64164107.
- **CONTINUIDAD_ASCENDENTE** — 5 hipótesis (20_sacrificio, erizo, trayectoria_musicos_populares, trayectoria_escritores_creativos, sustancias_03_severo), soporte 0.35835892.

## Destino personal (v2)

- **Veredicto: auge** — "el balance mejora y lo favorable domina en Z".
- Serie favorable (auge): [0.0383, 0.0704, 0.1613, 0.3068, 0.2929, 0.2783, 0.3651].
- Serie adverso total: [0.0332, 0.0318, 0.0302, 0.243, 0.2307, 0.2182, 0.2192].
- Serie adverso ruptura: [0.0, 0.0, 0.0, 0.0582, 0.0553, 0.0522, 0.0489].
- Familias activas en Z — auge: social_04_rogers (0.0743), monomito_12_regreso_con_el_elixir (0.0676), jaldun_01_asabiyyah (0.0676), eterno_retorno_02_cosmizacion (0.0676), 9_audaz_empresa (0.0554), duelo_bonanno_02_comun_recuperacion (0.0326). Caída: 36_perdida (0.0968), tainter_03 (0.0326), sistema_domiciano (0.0246), duelo_bonanno_03_cronico (0.0163). Ruptura: eterno_retorno_01_caos (0.0489).

## Hashes

- Entrada v2: 0c59532d8ce1963ae226935ce196b421606a7e00ce056468e5dcbd061abf39b6
- Salida v2: 178816a04a53487244ff94256c2f0a31a41a3024b0cafa38efb957f0a0a5ece3
- Engine: 665c39a2861e58772522e91272563260d980908b1d4ab9f7092d3413d0c36082
- Catálogo: d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1

## Nota

- Sin NameError: la corrida terminó limpia (exit 0, recibo COMPLETED).
- Monte Carlo: 21 observaciones, 13,167 simulaciones, todas convergieron.
