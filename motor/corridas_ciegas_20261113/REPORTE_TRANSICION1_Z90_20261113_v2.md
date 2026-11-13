# Reporte — Transición Histórica #1, versión 2 (con tokens Minsky)

**Fecha:** 2026-11-13 ~02:19 CST
**Caso:** TRANSICION1_Z90_20261113_v2
**Entrada:** `~/workspace/u6-alterno/motor-cameo/casos/precedentes/TRANSICION1_Z90_20261113_v2/entrada.json`
**Resultado:** `~/workspace/u6-alterno/motor-cameo/motor/RESULT_TRANSICION1_Z90_20261113_v2.json`
**Recibo:** COMPLETED, 76.096 s, exit 0
**Cambio respecto a v1:** se agregaron los tokens Minsky exactos en progresión direccional (C1 cautela; C2 busqueda_riesgo; C3 busqueda_riesgo+optimismo; C4 busqueda_riesgo+codicia; C5 busqueda_riesgo+negacion_problema+codicia).

## Minsky sí se encendió

| | v1 (sin tokens Minsky) | v2 (con tokens Minsky) |
|---|---|---|
| minsky_03_ponzi, lugar | No estaba en el top 14 | **H2 (#2)** |
| minsky_03_ponzi, rank_fusion | — | 26.873889 |
| minsky_03_ponzi en Z (caída) | No estaba | **#1 en caída (0.091)** |
| H1 | creador (29.25, AJUSTADA) | sabio (27.26, FRAGIL) |
| Grado | AJUSTADA (margen 1.399) | FRAGIL (margen 0.385) |
| Hipótesis en el conjunto | 14 | 15 |
| Apuesta MESETA | 0.678 | 0.715 |
| Apuesta ASCENDENTE | 0.322 | 0.285 |
| Destino | caída | caída |

A diferencia de Elvis v2 (donde agregar consumo_sustancias bajó a las sustancias), aquí agregar los tokens Minsky **sí** encendió a la familia: minsky_03_ponzi saltó de no estar a ser H2 y la primera familia de caída en Z. El cuello de botella era el diccionario de traducción, como diagnosticó Marco.

## H1 y H2 (v2)

| Puesto | Familia | Grado | rank_fusion | Peso | Relleno |
|---|---|---|---|---|---|
| H1 | arquetipo_el_sabio | FRAGIL | 27.259345 | 0.061742 | 62.67% |
| H2 | minsky_03_ponzi | FRAGIL | 26.873889 | 0.060869 | 59.61% |

- Mezcla: H1_CON_COMPONENTES_DE_H2. Margen H1–H2: 0.385456 (menor que el umbral 1.0). El motor no separa H1 de H2.
- Relleno H1 por grupo (%): estructura 100.0, dynamis 95.0, greimas 85.0, trayectoria/estado 83.0, otras 78.18, resolución 75.0, booker 62.5, geometría/inercia 57.5, frye 33.33, puente lateral 14.84, acoplamiento 5.0.
- Relleno H2 por grupo (%): dynamis 90.0, acoplamiento 70.0, puente lateral 73.49, estructura 65.0, geometría/inercia 60.0, greimas 58.33, booker 54.17, frye 51.67, resolución 47.5, otras 47.05, trayectoria/estado 38.5.

## Top 15 hipótesis (v2)

| # | Familia | rank_fusion | Régimen |
|---|---|---|---|
| 1 | arquetipo_el_sabio | 27.259345 | CONTINUIDAD_ASCENDENTE |
| 2 | minsky_03_ponzi | 26.873889 | MESETA_O_ESTABILIZACION |
| 3 | arquetipo_el_creador | 26.152694 | MESETA_O_ESTABILIZACION |
| 4 | dumezil_f2_fuerza | 24.253027 | MESETA_O_ESTABILIZACION |
| 5 | 20_sacrificio_por_un_ideal | 24.24418 | CONTINUIDAD_ASCENDENTE |
| 6 | berlin_01_erizo | 23.869784 | CONTINUIDAD_ASCENDENTE |
| 7 | 9_audaz_empresa | 23.22419 | MESETA_O_ESTABILIZACION |
| 8 | utopia_mentalidad_liberal | 22.336862 | MESETA_O_ESTABILIZACION |
| 9 | bbk_01_aventurero | 22.309929 | MESETA_O_ESTABILIZACION |
| 10 | schwartz_09_estimulacion | 20.855983 | MESETA_O_ESTABILIZACION |
| 11 | kwml_01_rey | 20.75 | MESETA_O_ESTABILIZACION |
| 12 | 6_desastre | 19.736797 | CONTINUIDAD_ASCENDENTE |
| 13 | social_04_rogers_difusion_innovaciones | 17.487149 | MESETA_O_ESTABILIZACION |
| 14 | turner_01_fase_liminal | 17.35 | MESETA_O_ESTABILIZACION |
| 15 | arquetipo_el_gobernante | 17.244565 | MESETA_O_ESTABILIZACION |

Nuevas en v2: minsky_03_ponzi (#2), schwartz_09_estimulacion (#10), 6_desastre (#12). Salieron del top: social_14_overton_ventana (era #11), distopia_agotamiento_ambiental (era #10).

## Apuesta (v2)

- **Apuesta principal: MESETA_O_ESTABILIZACION** — 11 hipótesis (minsky_03_ponzi, creador, dumezil_f2_fuerza, 9_audaz_empresa, mentalidad_liberal, bbk_01_aventurero, schwartz_09_estimulacion, kwml_01_rey, social_04_rogers, turner_01_fase_liminal, gobernante), soporte 0.7151952.
- **CONTINUIDAD_ASCENDENTE** — 4 hipótesis (sabio, 20_sacrificio, erizo, 6_desastre), soporte 0.2848048.

## Destino personal (v2)

- **Veredicto: caída** — "el balance favorable-adverso empeora / lo adverso domina y sube / el eje del sujeto se apaga". Igual que en v1.
- Serie favorable (auge): [0.0653, 0.1649, 0.2199, 0.1935, 0.237, 0.3227, 0.3946].
- Serie adverso total: [−0.0052, 0.1529, 0.2735, 0.3461, 0.5325, 0.5831, 0.6443] — empieza negativa y sube a 0.6443, mucho más fuerte que en v1 (0.4654).
- Serie adverso caída: [−0.0052, 0.0947, 0.1763, 0.2538, 0.3279, 0.3218, 0.3649].
- Serie adverso ruptura: [0.0, 0.0582, 0.0972, 0.0923, 0.2046, 0.2613, 0.2794] — igual que en v1.
- Señales: balance último tramo 0.0107 (positivo, era −0.004 en v1); salto ruptura 0.0181; salto adverso 0.0612; eje sabio; caída del eje vs máximo previo 0.0244.

## Familias activas en Z (v2)

- **Ruptura:** 6_desastre (0.0979), predictivo_01_markov_estado_absorbente (0.0931), eterno_retorno_01_caos_primordial (0.0884).
- **Caída:** minsky_03_ponzi (0.091), jaldun_03_entropia_y_perdida_de_cohesion (0.0879), tainter_03_vulnerabilidad_sistemica (0.0818), 7_caer_victima (0.0485), kondratiev_04_invierno_recesion (0.0311), sistema_domiciano_maiestas (0.0246).
- **Auge:** social_04_rogers (0.1063), 9_audaz_empresa (0.0952), monomito_12_regreso_con_el_elixir (0.0933), eterno_retorno_02_cosmizacion (0.0933), kondratiev_02_verano_auge (0.0247), kondratiev_01_primavera_expansion (0.009).

Nuevas en Z: minsky_03_ponzi (#1 en caída), jaldun_03_entropia_y_perdida_de_cohesion (#2 en caída), kondratiev_01_primavera_expansion y kondratiev_02_verano_auge (en auge). Ahora hay tres estaciones Kondratiev activas (primavera y verano en auge, invierno en caída): el ciclo completo se ve.

## La idea de Marco: los tokens específicos no son sesgo, son necesidad

Marco señaló que el diccionario de traducción, al hacer el ejercicio ciego, neutraliza palabras para no revelar la identidad, y esa neutralización le quita al motor justo los tokens que necesita. Lo que parece una "inclinación de sesgo" por parte del input — usar ciertas palabras, adjetivos o sustantivos específicos — no es necesariamente sesgo. Son tokens específicos, y son una necesidad, no una pérdida.

Las dos versiones 2 lo confirman, cada una a su manera:
- **Elvis v2:** agregar consumo_sustancias no sesgó el resultado hacia las sustancias; al revés, las bajó y activó otras familias (las trayectorias). El token no fuerza la respuesta, cambia la lectura completa.
- **Tulipán v2:** agregar los tokens Minsky en progresión sí encendió a minsky_03_ponzi como H2, pero también cambió el H1 (de creador a sabio), trajo a jaldun_03 y completó el ciclo Kondratiev. El token no es un atajo a la respuesta; es el vocabulario que el motor necesita para leer el fenómeno.

El ciego no debe quitar el vocabulario específico; debe quitar la identidad (el nombre, la fecha, el lugar). La palabra que nombra el fenómeno — consumo, riesgo, codicia, negación — es el token, no la pista que delata.

## Hashes

- Entrada v2: f37231bd8d73d2ae63132e4f3e29d0c77a8feb87ab46cb44fef6e0d3d0b5fc1f
- Salida v2: da87983cfeb48a9561549984b20e1b006bc709b52c41c2602f9221429f826d0f
- Engine: 665c39a2861e58772522e91272563260d980908b1d4ab9f7092d3413d0c36082
- Catálogo: d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1

## Nota

- Sin NameError: la corrida terminó limpia (exit 0, recibo COMPLETED).
- Monte Carlo: 21 observaciones, 12,562 simulaciones, todas convergieron.
- El trono no se activa: gobernante último (#15).
