# Cuartos del monomito en la rueda — SEMMELWEIS_HEROE_SIN_TRONO_20261112

Fuentes: `COLOR_SOMBRA_SEMMELWEIS_HEROE_SIN_TRONO_20261112.json` (COLOR_SOMBRA) y `RESULT_SEMMELWEIS_HEROE_SIN_TRONO_20261112.json` (RESULT sellado).
Plugin de cuartos: `plugin_circulo_monomito_v2.py` (leído)
H1: arquetipo_el_sabio | H2: 20_sacrificio_por_un_ideal

## Familias monomito_* con color en la rueda (tablero sombra)

| familia | etapa | cuarto | mapeo | eje dominante | saturación sombra |
|---|---|---|---|---|---|
| monomito_01_mundo_ordinario | 1 | Q1_Separacion_1_3 | directo por numero y slug | situacion | 0.0978 |
| monomito_05_cruce_del_primer_umbral | 5 | Q2_Descenso_4_6 | por numero; slug difiere (familia 'cruce_del_primer_umbral' vs etapa 'cruce_primer_umbral') | interno | 0.0941 |
| monomito_06_pruebas_aliados_y_enemigos | 6 | Q2_Descenso_4_6 | directo por numero y slug | situacion | 0.0904 |

## Cuadrante activo por corte (RESULT, plugin_circulo_monomito)

- C1_1831: cuadrante activo Q2_Descenso_4_6 | hilos (ninguno) | caldero inyectado: False
- C2_1846: cuadrante activo (ninguno) | hilos (ninguno) | caldero inyectado: False
- C3_1847: cuadrante activo (ninguno) | hilos (ninguno) | caldero inyectado: False
- C4_1849: cuadrante activo (ninguno) | hilos hilo_sombra_consumo | caldero inyectado: False
- C5_1852: cuadrante activo Q4_Retorno_10_12 | hilos (ninguno) | caldero inyectado: False
- C6_1858: cuadrante activo (ninguno) | hilos hilo_sombra_consumo | caldero inyectado: False
- C7_1861: cuadrante activo Q3_Ordeal_7_9 | hilos hilo_vinculo | caldero inyectado: False

## Por cuarto de cada familia: cortes donde ese cuarto estuvo activo

- monomito_01_mundo_ordinario (etapa 1, Q1_Separacion_1_3): cortes con Q1_Separacion_1_3 activo: (ningún corte con este cuarto activo).
- monomito_05_cruce_del_primer_umbral (etapa 5, Q2_Descenso_4_6): cortes con Q2_Descenso_4_6 activo: C1_1831.
- monomito_06_pruebas_aliados_y_enemigos (etapa 6, Q2_Descenso_4_6): cortes con Q2_Descenso_4_6 activo: C1_1831.

## Puente Caldero → cuartos (en este RESULT)

- current_neighbors mapeados al vocabulario monomito: []
- vecinos crudos: 74 | ignorados sin mapear: 74
- injected_cut: None | mapping: exact_existing_monomito_vocab_only

## Lectura honesta

- Familias monomito_* con color: 3; con cuarto mapeable: 3.
- El puente Caldero NO aportó ningún vecino al vocabulario monomito en esta corrida: los cuadrantes por corte salen solo de los tokens de los cortes, no de los vecinos.
- El cuadrante activo por corte lo decide el plugin por coocurrencia de tokens del corte con tokens_candidatos del cuarto, NO por el índice del corte: un C1 puede salir en Q2 y un C5 en Q4. El cuarto de la familia (por su número de etapa) y el cuadrante activo del corte son dos cosas distintas; la tabla de arriba las cruza sin confundirlas.
