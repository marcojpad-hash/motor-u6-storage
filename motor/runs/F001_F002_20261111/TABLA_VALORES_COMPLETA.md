# Tabla completa de valores — corridas F001 y F002 (2026-11-11)

Todas las corridas con `ok:true` y recibo `COMPLETED`. El motor sigue NO_CALIBRADO (sin desenlaces sellados por caso para calibrar probabilidad); los valores son soporte estructural, no probabilidad calibrada.

## CAL_F001_01_NAPOLEON (F001)

- ok: True · recibo: COMPLETED · segundos: 33.703
- entrada sha256: `e05645ddb3eab1601992b86037b8ef530c6b27413575241b6bf0e3860e66b046` · RESULT completo sha256: `680aa443bf393313630c5066b56c7f89bb0a0fbbdfd107b700830d1497f5b153` (6771381 bytes)
- grado: **AJUSTADA** · mezcla: H1_DOMINANTE — 31_conflicto_con_un_dios domina; 30_ambicion es rival distinto (margen 2.148795 >= 1.0 y afinidad 0.246217 < 0.5)

### H1: 31_conflicto_con_un_dios

- porcentaje_relleno: 64.01 · predictibilidad_estructural_pct: 60.37 · peso_relativo: 0.128799
- desglose_relleno_por_grupo_pct:
  - acoplamiento: 60
  - booker: 56.6667
  - dynamis: 60
  - estructura: 100
  - frye: 51.6667
  - geometria_inercia: 50
  - greimas: 72.5
  - otras_dimensiones: 49.4444
  - puente_lateral: 73.8397
  - trayectoria_estado: 66

### H2: 30_ambicion

- porcentaje_relleno: 52.59 · predictibilidad_estructural_pct: 56.46 · peso_relativo: 0.119154
- desglose_relleno_por_grupo_pct:
  - acoplamiento: 10
  - booker: 50
  - dynamis: 83
  - estructura: 55
  - frye: 51.6667
  - geometria_inercia: 40
  - greimas: 50
  - otras_dimensiones: 61.1111
  - puente_lateral: 51.0753
  - trayectoria_estado: 74

### Conjunto abierto (5 hipótesis, cardinalidad_fija: False)

- **H_001** 31_conflicto_con_un_dios · rol: eje · rank_fusion: 28.6956 · soporte_estructural_relativo: 0.244117
  - trazabilidad_geometrica: régimen=CONTINUIDAD_ASCENDENTE · señal_multiescala=0.395201 · micro=0.782813 · meso=0.654995 · macro=0.654995 · aceleración=0.782813 · divergencia_entre_escala=0.127818 · n_cortes_observados=3
- **H_002** 30_ambicion · rol: componente · rank_fusion: 26.5468 · soporte_estructural_relativo: 0.225837
  - trazabilidad_geometrica: régimen=MESeta_O_ESTABILIZACION · señal_multiescala=0.016618 · micro=0.515995 · meso=0.504467 · macro=0.504467 · aceleración=0.52305 · divergencia_entre_escala=0.011528 · n_cortes_observados=3
- **H_003** arquetipo_el_gobernante · rol: componente · rank_fusion: 26.106 · soporte_estructural_relativo: 0.222087
  - trazabilidad_geometrica: régimen=CONTINUIDAD_ASCENDENTE · señal_multiescala=0.161471 · micro=0.484671 · meso=0.628768 · macro=0.628768 · aceleración=0.235676 · divergencia_entre_escala=0.144096 · n_cortes_observados=3
- **H_004** bbk_01_aventurero · rol: componente · rank_fusion: 19.05 · soporte_estructural_relativo: 0.162061
  - trazabilidad_geometrica: régimen=CONTINUIDAD_ASCENDENTE · señal_multiescala=0.203854 · micro=0.658721 · meso=0.57353 · macro=0.57353 · aceleración=0.673194 · divergencia_entre_escala=0.085191 · n_cortes_observados=3
- **H_005** social_04_rogers_difusion_innovaciones · rol: componente · rank_fusion: 17.15 · soporte_estructural_relativo: 0.145897
  - trazabilidad_geometrica: régimen=MESeta_O_ESTABILIZACION · señal_multiescala=0.064575 · micro=0.463266 · meso=0.566798 · macro=0.566798 · aceleración=0.303222 · divergencia_entre_escala=0.103532 · n_cortes_observados=3

### Apuesta principal: CONTINUIDAD_ASCENDENTE (soporte_estructural_agregado: 0.628265) · hipótesis que convergen: 31_conflicto_con_un_dios, arquetipo_el_gobernante, bbk_01_aventurero
- calibración: NO_CALIBRADA_SIN_DESENLACES_POSTERIORES_SELLADOS
- monte_carlo: status=None · total_simulations=None · converged=None/None · nonconverged=None
- predictive_validation: NOT_CALIBRATED_NO_CASE_LEVEL_OUTCOMES · hay una referencia histórica de acierto Top-1/Top-3 del predictor lateral, pero faltan scores y desenlaces sellados por caso para ajustar/calibrar una probabilidad del motor actual; no se sustituyen p

### Input en prosa (entrada.json)

- pregunta: ¿Qué trayectoria sigue Napoleón al invadir Rusia con la Grande Armée?
- person: Napoleón Bonaparte · tipo_sujeto: politico · freeze: 1812-06-24 · random_seed: 20261024
- corte C1_1799: fecha=1799-11-09 · hecho=Golpe del 18 de brumario; se convierte en Primer Cónsul.
- corte C2_1805: fecha=1805-12-02 · hecho=Emperador desde 1804; victoria en Austerlitz sobre Austria y Rusia.
- corte C3_1812: fecha=1812-06-24 · hecho=Rusia abandona el Bloqueo Continental; Napoleón cruza el Niemen con unos 600 000 hombres.

## CAL_F001_02_TESLA (F001)

- ok: True · recibo: COMPLETED · segundos: 18.813
- entrada sha256: `be89b315b99b09cb06f0cd46a5eb823aefd4e1b9681fea0279d8803128137635` · RESULT completo sha256: `3308d1c0d07ffd26ddf63b6e2f2627a0d5b4e068a469b269c93fab88707df237` (6738984 bytes)
- grado: **FRAGIL** · mezcla: H1_CON_COMPONENTES_DE_H2 — 22_todo_sacrificado_por_una_pasion con componentes de 30_ambicion (margen 0.46185 < GATE_SEPARATION 1.0)

### H1: 22_todo_sacrificado_por_una_pasion

- porcentaje_relleno: 67.93 · predictibilidad_estructural_pct: 59.29 · peso_relativo: 0.144477
- desglose_relleno_por_grupo_pct:
  - acoplamiento: 87.5
  - booker: 60.4167
  - dynamis: 63.75
  - estructura: 93.75
  - frye: 50
  - geometria_inercia: 50
  - greimas: 75
  - otras_dimensiones: 48.8636
  - puente_lateral: 67.9947
  - resolucion: 100
  - trayectoria_estado: 50

### H2: 30_ambicion

- porcentaje_relleno: 56.93 · predictibilidad_estructural_pct: 58.51 · peso_relativo: 0.142253
- desglose_relleno_por_grupo_pct:
  - acoplamiento: 12.5
  - booker: 50
  - dynamis: 87.5
  - estructura: 68.75
  - frye: 50
  - geometria_inercia: 50
  - greimas: 54.1667
  - otras_dimensiones: 68.1818
  - puente_lateral: 41.3353
  - resolucion: 62.5
  - trayectoria_estado: 81.25

### Conjunto abierto (7 hipótesis, cardinalidad_fija: False)

- **H_001** 22_todo_sacrificado_por_una_pasion · rol: eje · rank_fusion: 29.9945 · soporte_estructural_relativo: 0.178276
  - trazabilidad_geometrica: régimen=CONTINUIDAD_ASCENDENTE · señal_multiescala=0.332852 · micro=0.741619 · meso=0.62883 · macro=0.62883 · aceleración=0.741619 · divergencia_entre_escala=0.112789 · n_cortes_observados=3
- **H_002** 30_ambicion · rol: componente · rank_fusion: 29.5327 · soporte_estructural_relativo: 0.175531
  - trazabilidad_geometrica: régimen=CONTINUIDAD_ASCENDENTE · señal_multiescala=0.157553 · micro=0.6244 · meso=0.555965 · macro=0.555965 · aceleración=0.638055 · divergencia_entre_escala=0.068436 · n_cortes_observados=3
- **H_003** utopia_mentalidad_liberal · rol: componente · rank_fusion: 26.0744 · soporte_estructural_relativo: 0.154976
  - trazabilidad_geometrica: régimen=MESeta_O_ESTABILIZACION · señal_multiescala=0.086419 · micro=0.471631 · meso=0.578999 · macro=0.578999 · aceleración=0.296393 · divergencia_entre_escala=0.107369 · n_cortes_observados=3
- **H_004** schwartz_10_autodireccion · rol: complementaria_trazabilidad_geometrica · rank_fusion: 23.5379 · soporte_estructural_relativo: 0.1399
  - trazabilidad_geometrica: régimen=MESeta_O_ESTABILIZACION · señal_multiescala=0.016349 · micro=0.463001 · meso=0.530761 · macro=0.530761 · aceleración=0.367505 · divergencia_entre_escala=0.06776 · n_cortes_observados=3
- **H_005** tainter_04_colapso_por_simplificacion_forzada · rol: complementaria_trazabilidad_geometrica · rank_fusion: 23.4206 · soporte_estructural_relativo: 0.139203
  - trazabilidad_geometrica: régimen=MESeta_O_ESTABILIZACION · señal_multiescala=-0.038025 · micro=0.47695 · meso=0.483007 · macro=0.483007 · aceleración=0.487869 · divergencia_entre_escala=0.006057 · n_cortes_observados=3
- **H_006** social_04_rogers_difusion_innovaciones · rol: componente · rank_fusion: 17.875 · soporte_estructural_relativo: 0.106242
  - trazabilidad_geometrica: régimen=CONTINUIDAD_ASCENDENTE · señal_multiescala=0.120167 · micro=0.474688 · meso=0.602781 · macro=0.602781 · aceleración=0.261768 · divergencia_entre_escala=0.128093 · n_cortes_observados=3
- **H_007** frye_mythos_romance · rol: componente · rank_fusion: 17.8125 · soporte_estructural_relativo: 0.105871
  - trazabilidad_geometrica: régimen=CONTINUIDAD_ASCENDENTE · señal_multiescala=0.138683 · micro=0.486936 · meso=0.610544 · macro=0.610544 · aceleración=0.268208 · divergencia_entre_escala=0.123608 · n_cortes_observados=3

### Apuesta principal: CONTINUIDAD_ASCENDENTE (soporte_estructural_agregado: 0.56592) · hipótesis que convergen: 22_todo_sacrificado_por_una_pasion, 30_ambicion, social_04_rogers_difusion_innovaciones, frye_mythos_romance
- calibración: NO_CALIBRADA_SIN_DESENLACES_POSTERIORES_SELLADOS
- monte_carlo: status=None · total_simulations=None · converged=None/None · nonconverged=None
- predictive_validation: NOT_CALIBRATED_NO_CASE_LEVEL_OUTCOMES · hay una referencia histórica de acierto Top-1/Top-3 del predictor lateral, pero faltan scores y desenlaces sellados por caso para ajustar/calibrar una probabilidad del motor actual; no se sustituyen p

### Input en prosa (entrada.json)

- pregunta: ¿Qué ocurre con Tesla y su proyecto de transmisión inalámbrica financiado por J. P. Morgan?
- person: Nikola Tesla · tipo_sujeto: cientifico · freeze: 1901-03-01 · random_seed: 20261024
- corte C1_1884: fecha=1884-06-06 · hecho=Llega a Nueva York, trabaja para Edison y renuncia al poco tiempo por un desacuerdo de pago.
- corte C2_1893: fecha=1893-05-01 · hecho=Sus patentes de corriente alterna, licenciadas a Westinghouse (1888), iluminan la Exposición de Chicago.
- corte C3_1901: fecha=1901-03-01 · hecho=Morgan acepta financiar con 150 000 dólares una torre de transmisión inalámbrica (Wardenclyffe).

## CAL_F001_03_WILDE (F001)

- ok: True · recibo: COMPLETED · segundos: 18.255
- entrada sha256: `54247ffa2a4f5f1478ed253f5ae6f7c73fa947a3f991a979e12dc7a8ba4e9df8` · RESULT completo sha256: `01c2b35a181c874dc3db38054932e3ef2bade1eb78647eff15577f0ee881fe55` (6314968 bytes)
- grado: **AJUSTADA** · mezcla: H1_DOMINANTE — 31_conflicto_con_un_dios domina; schwartz_08_hedonismo es rival distinto (margen 3.371846 >= 1.0 y afinidad 0.199955 < 0.5)

### H1: 31_conflicto_con_un_dios

- porcentaje_relleno: 64.39 · predictibilidad_estructural_pct: 60.79 · peso_relativo: 0.140969
- desglose_relleno_por_grupo_pct:
  - acoplamiento: 77.7778
  - booker: 59.2593
  - dynamis: 58.8889
  - estructura: 88.8889
  - frye: 50
  - geometria_inercia: 44.4444
  - greimas: 69.4444
  - otras_dimensiones: 60.4938
  - puente_lateral: 72.5261
  - trayectoria_estado: 62.2222

### H2: schwartz_08_hedonismo

- porcentaje_relleno: 54.26 · predictibilidad_estructural_pct: 54.75 · peso_relativo: 0.124594
- desglose_relleno_por_grupo_pct:
  - acoplamiento: 33.3333
  - booker: 51.8519
  - dynamis: 81.1111
  - estructura: 55.5556
  - frye: 50
  - geometria_inercia: 50
  - greimas: 43.0556
  - otras_dimensiones: 43.2099
  - puente_lateral: 56.6661
  - trayectoria_estado: 77.7778

### Conjunto abierto (7 hipótesis, cardinalidad_fija: False)

- **H_001** 31_conflicto_con_un_dios · rol: eje · rank_fusion: 29.0273 · soporte_estructural_relativo: 0.191359
  - trazabilidad_geometrica: régimen=CONTINUIDAD_ASCENDENTE · señal_multiescala=0.365089 · micro=0.763169 · meso=0.642232 · macro=0.642232 · aceleración=0.763169 · divergencia_entre_escala=0.120937 · n_cortes_observados=3
- **H_002** schwartz_08_hedonismo · rol: componente · rank_fusion: 25.6555 · soporte_estructural_relativo: 0.169131
  - trazabilidad_geometrica: régimen=MESeta_O_ESTABILIZACION · señal_multiescala=0.114824 · micro=0.586844 · meso=0.542696 · macro=0.542696 · aceleración=0.588911 · divergencia_entre_escala=0.044148 · n_cortes_observados=3
- **H_003** 29_un_enemigo_amado · rol: componente · rank_fusion: 22.4217 · soporte_estructural_relativo: 0.147812
  - trazabilidad_geometrica: régimen=MESeta_O_ESTABILIZACION · señal_multiescala=-0.026038 · micro=0.484405 · meso=0.488269 · macro=0.488269 · aceleración=0.492267 · divergencia_entre_escala=0.003864 · n_cortes_observados=3
- **H_004** monomito_08_la_odisea_o_prueba_suprema · rol: componente · rank_fusion: 21.0556 · soporte_estructural_relativo: 0.138806
  - trazabilidad_geometrica: régimen=CONTINUIDAD_ASCENDENTE · señal_multiescala=0.300613 · micro=0.719584 · meso=0.615668 · macro=0.615668 · aceleración=0.719584 · divergencia_entre_escala=0.103916 · n_cortes_observados=3
- **H_005** arquetipo_el_creador · rol: componente · rank_fusion: 19.8163 · soporte_estructural_relativo: 0.130636
  - trazabilidad_geometrica: régimen=MESeta_O_ESTABILIZACION · señal_multiescala=0.066571 · micro=0.471763 · meso=0.564046 · macro=0.564046 · aceleración=0.322713 · divergencia_entre_escala=0.092283 · n_cortes_observados=3
- **H_006** frye_mythos_romance · rol: componente · rank_fusion: 16.8889 · soporte_estructural_relativo: 0.111338
  - trazabilidad_geometrica: régimen=CONTINUIDAD_ASCENDENTE · señal_multiescala=0.136463 · micro=0.483606 · meso=0.610544 · macro=0.610544 · aceleración=0.263007 · divergencia_entre_escala=0.126938 · n_cortes_observados=3
- **H_007** arquetipo_el_bufon · rol: componente · rank_fusion: 16.8251 · soporte_estructural_relativo: 0.110917
  - trazabilidad_geometrica: régimen=CONTINUIDAD_ASCENDENTE · señal_multiescala=0.138806 · micro=0.488136 · meso=0.610037 · macro=0.610037 · aceleración=0.270938 · divergencia_entre_escala=0.121901 · n_cortes_observados=3

### Apuesta principal: CONTINUIDAD_ASCENDENTE (soporte_estructural_agregado: 0.552421) · hipótesis que convergen: 31_conflicto_con_un_dios, monomito_08_la_odisea_o_prueba_suprema, frye_mythos_romance, arquetipo_el_bufon
- calibración: NO_CALIBRADA_SIN_DESENLACES_POSTERIORES_SELLADOS
- monte_carlo: status=None · total_simulations=None · converged=None/None · nonconverged=None
- predictive_validation: NOT_CALIBRATED_NO_CASE_LEVEL_OUTCOMES · hay una referencia histórica de acierto Top-1/Top-3 del predictor lateral, pero faltan scores y desenlaces sellados por caso para ajustar/calibrar una probabilidad del motor actual; no se sustituyen p

### Input en prosa (entrada.json)

- pregunta: ¿Qué ocurre con Oscar Wilde al denunciar por difamación al marqués de Queensberry?
- person: Oscar Wilde · tipo_sujeto: artista · freeze: 1895-03-01 · random_seed: 20261024
- corte C1_1891: fecha=1891-06-01 · hecho=Publica El retrato de Dorian Gray en libro y conoce a Lord Alfred Douglas.
- corte C2_1895A: fecha=1895-02-14 · hecho=Estreno triunfal de La importancia de llamarse Ernesto en Londres.
- corte C3_1895B: fecha=1895-03-01 · hecho=Queensberry le deja una tarjeta insultante en su club; Wilde obtiene orden de arresto contra él por difamación.

## CAL_F001_04_DISNEY (F001)

- ok: True · recibo: COMPLETED · segundos: 18.204
- entrada sha256: `d546c10647b235bfffdc1d309ffcef91de4e2050302eff86614ad4938e61b014` · RESULT completo sha256: `5031353d8ade84a931b8d4d55af12d7dac78ac07c5378434fe42651feec2a733` (6277945 bytes)
- grado: **AJUSTADA** · mezcla: H1_DOMINANTE — schwartz_10_autodireccion domina; 30_ambicion es rival distinto (margen 6.727394 >= 1.0 y afinidad 0.2 < 0.5)

### H1: schwartz_10_autodireccion

- porcentaje_relleno: 64.41 · predictibilidad_estructural_pct: 66.3 · peso_relativo: 0.187276
- desglose_relleno_por_grupo_pct:
  - acoplamiento: 14.2857
  - booker: 54.7619
  - dynamis: 62.8571
  - estructura: 100
  - frye: 45.2381
  - geometria_inercia: 50
  - greimas: 67.8571
  - otras_dimensiones: 77.7778
  - puente_lateral: 82.9134
  - resolucion: 78.5714
  - trayectoria_estado: 74.2857

### H2: 30_ambicion

- porcentaje_relleno: 56.82 · predictibilidad_estructural_pct: 54.26 · peso_relativo: 0.149219
- desglose_relleno_por_grupo_pct:
  - acoplamiento: 100
  - booker: 69.0476
  - dynamis: 82.8571
  - estructura: 57.1429
  - frye: 52.381
  - geometria_inercia: 71.4286
  - greimas: 21.4286
  - otras_dimensiones: 61.9048
  - puente_lateral: 50.228
  - resolucion: 14.2857
  - trayectoria_estado: 44.2857

### Conjunto abierto (5 hipótesis, cardinalidad_fija: False)

- **H_001** schwartz_10_autodireccion · rol: eje · rank_fusion: 33.1051 · soporte_estructural_relativo: 0.287735
  - trazabilidad_geometrica: régimen=CONTINUIDAD_ASCENDENTE · señal_multiescala=0.273173 · micro=0.664215 · meso=0.622773 · macro=0.622773 · aceleración=0.589428 · divergencia_entre_escala=0.041442 · n_cortes_observados=3
- **H_002** 30_ambicion · rol: componente · rank_fusion: 26.3777 · soporte_estructural_relativo: 0.229263
  - trazabilidad_geometrica: régimen=MESeta_O_ESTABILIZACION · señal_multiescala=-0.023817 · micro=0.491734 · meso=0.48627 · macro=0.48627 · aceleración=0.510932 · divergencia_entre_escala=0.005464 · n_cortes_observados=3
- **H_003** social_04_rogers_difusion_innovaciones · rol: componente · rank_fusion: 22.7857 · soporte_estructural_relativo: 0.198043
  - trazabilidad_geometrica: régimen=CONTINUIDAD_ASCENDENTE · señal_multiescala=0.30326 · micro=0.72141 · meso=0.61674 · macro=0.61674 · aceleración=0.72141 · divergencia_entre_escala=0.10467 · n_cortes_observados=3
- **H_004** tainter_01_inversion_complejidad_productiva · rol: componente · rank_fusion: 17.4286 · soporte_estructural_relativo: 0.151481
  - trazabilidad_geometrica: régimen=CONTINUIDAD_ASCENDENTE · señal_multiescala=0.148153 · micro=0.5 · meso=0.611115 · macro=0.611115 · aceleración=0.288229 · divergencia_entre_escala=0.111115 · n_cortes_observados=3
- **H_005** minsky_03_ponzi · rol: componente · rank_fusion: 15.3571 · soporte_estructural_relativo: 0.133478
  - trazabilidad_geometrica: régimen=MESeta_O_ESTABILIZACION · señal_multiescala=-0.008355 · micro=0.500133 · meso=0.493667 · macro=0.493667 · aceleración=0.51293 · divergencia_entre_escala=0.006466 · n_cortes_observados=3

### Apuesta principal: CONTINUIDAD_ASCENDENTE (soporte_estructural_agregado: 0.637259) · hipótesis que convergen: schwartz_10_autodireccion, social_04_rogers_difusion_innovaciones, tainter_01_inversion_complejidad_productiva
- calibración: NO_CALIBRADA_SIN_DESENLACES_POSTERIORES_SELLADOS
- monte_carlo: status=None · total_simulations=None · converged=None/None · nonconverged=None
- predictive_validation: NOT_CALIBRATED_NO_CASE_LEVEL_OUTCOMES · hay una referencia histórica de acierto Top-1/Top-3 del predictor lateral, pero faltan scores y desenlaces sellados por caso para ajustar/calibrar una probabilidad del motor actual; no se sustituyen p

### Input en prosa (entrada.json)

- pregunta: ¿Qué trayectoria sigue Walt Disney tras perder los derechos de Oswald y a la mayoría de sus animadores?
- person: Walt Disney · tipo_sujeto: empresario · freeze: 1928-03-01 · random_seed: 20261024
- corte C1_1923: fecha=1923-10-16 · hecho=Tras la quiebra de Laugh-O-Gram en Kansas City funda con su hermano Roy el estudio Disney Brothers en Los Ángeles.
- corte C2_1927: fecha=1927-09-05 · hecho=Oswald the Lucky Rabbit, producido para Universal vía Charles Mintz, tiene éxito.
- corte C3_1928: fecha=1928-03-01 · hecho=En Nueva York, Mintz se queda con Oswald (los derechos eran de Universal) y contrata a casi todos sus animadores.

## CAL_F001_05_TURING (F001)

- ok: True · recibo: COMPLETED · segundos: 17.224
- entrada sha256: `1ac92339557934c04d1be9827344a1bc0f06e9d4299a05646890ae941cdd314a` · RESULT completo sha256: `5215d381913180dfc406455fe2ed776d65fae1d8f0eecde803921820fe21d207` (5231852 bytes)
- grado: **FRAGIL** · mezcla: H1_CON_COMPONENTES_DE_H2 — utopia_mentalidad_liberal con componentes de arquetipo_el_sabio (margen 0.54443 < GATE_SEPARATION 1.0)

### H1: utopia_mentalidad_liberal

- porcentaje_relleno: 42.68 · predictibilidad_estructural_pct: 51.5 · peso_relativo: 0.18706
- desglose_relleno_por_grupo_pct:
  - acoplamiento: 20
  - booker: 40
  - dynamis: 40
  - estructura: 20
  - frye: 50
  - geometria_inercia: 50
  - greimas: 46.6667
  - otras_dimensiones: 57.7778
  - puente_lateral: 75
  - resolucion: 30
  - trayectoria_estado: 40

### H2: arquetipo_el_sabio

- porcentaje_relleno: 40.06 · predictibilidad_estructural_pct: 50.48 · peso_relativo: 0.182689
- desglose_relleno_por_grupo_pct:
  - acoplamiento: 0
  - booker: 46.6667
  - dynamis: 20
  - estructura: 40
  - frye: 50
  - geometria_inercia: 70
  - greimas: 26.6667
  - otras_dimensiones: 57.7778
  - puente_lateral: 71.5557
  - resolucion: 10
  - trayectoria_estado: 48

### Conjunto abierto (5 hipótesis, cardinalidad_fija: False)

- **H_001** utopia_mentalidad_liberal · rol: eje · rank_fusion: 23.3 · soporte_estructural_relativo: 0.214062
  - trazabilidad_geometrica: régimen=MESeta_O_ESTABILIZACION · señal_multiescala=0.080481 · micro=0.475619 · meso=0.572551 · macro=0.572551 · aceleración=0.314377 · divergencia_entre_escala=0.096932 · n_cortes_observados=3
- **H_002** arquetipo_el_sabio · rol: complementaria_trazabilidad_geometrica · rank_fusion: 22.7556 · soporte_estructural_relativo: 0.209061
  - trazabilidad_geometrica: régimen=MESeta_O_ESTABILIZACION · señal_multiescala=-0.022462 · micro=0.468708 · meso=0.4988 · macro=0.4988 · aceleración=0.440024 · divergencia_entre_escala=0.030092 · n_cortes_observados=3
- **H_003** 5_persecucion · rol: componente · rank_fusion: 21.7626 · soporte_estructural_relativo: 0.199938
  - trazabilidad_geometrica: régimen=CONTINUIDAD_ASCENDENTE · señal_multiescala=0.352892 · micro=0.755075 · meso=0.637131 · macro=0.637131 · aceleración=0.755075 · divergencia_entre_escala=0.117944 · n_cortes_observados=3
- **H_004** spengler_02_verano_otono_racionalizacion · rol: componente · rank_fusion: 21.0883 · soporte_estructural_relativo: 0.193743
  - trazabilidad_geometrica: régimen=MESeta_O_ESTABILIZACION · señal_multiescala=-0.041574 · micro=0.483872 · meso=0.476883 · macro=0.476883 · aceleración=0.513996 · divergencia_entre_escala=0.006989 · n_cortes_observados=3
- **H_005** 7_caer_victima · rol: componente · rank_fusion: 19.9403 · soporte_estructural_relativo: 0.183196
  - trazabilidad_geometrica: régimen=CONTINUIDAD_ASCENDENTE · señal_multiescala=0.259524 · micro=0.690886 · meso=0.5992 · macro=0.5992 · aceleración=0.690886 · divergencia_entre_escala=0.091686 · n_cortes_observados=3

### Apuesta principal: MESeta_O_ESTABILIZACION (soporte_estructural_agregado: 0.616866) · hipótesis que convergen: utopia_mentalidad_liberal, arquetipo_el_sabio, spengler_02_verano_otono_racionalizacion
- calibración: NO_CALIBRADA_SIN_DESENLACES_POSTERIORES_SELLADOS
- monte_carlo: status=None · total_simulations=None · converged=None/None · nonconverged=None
- predictive_validation: NOT_CALIBRATED_NO_CASE_LEVEL_OUTCOMES · hay una referencia histórica de acierto Top-1/Top-3 del predictor lateral, pero faltan scores y desenlaces sellados por caso para ajustar/calibrar una probabilidad del motor actual; no se sustituyen p

### Input en prosa (entrada.json)

- pregunta: ¿Qué ocurre con Alan Turing tras su condena por 'indecencia grave'?
- person: Alan Turing · tipo_sujeto: cientifico · freeze: 1952-03-31 · random_seed: 20261024
- corte C1_1936: fecha=1936-11-12 · hecho=Publica 'On Computable Numbers', base de la teoría de la computación.
- corte C2_1950: fecha=1950-10-01 · hecho=Tras su trabajo secreto en Bletchley Park (OBE 1946), publica 'Computing Machinery and Intelligence'.
- corte C3_1952: fecha=1952-03-31 · hecho=Condenado por 'indecencia grave'; acepta tratamiento hormonal en vez de prisión y pierde su acceso al trabajo criptográfico con GCHQ.

## CAL_F002_01_GALILEI (F002)

- ok: True · recibo: COMPLETED · segundos: 32.926
- entrada sha256: `7774f41d9de12c7130c70919fa93422d73b68acec3071b71916c20db2d37e799` · RESULT completo sha256: `a193210df2460819790e3e8257e40c65a765835e00836ef446633877fafa0a3f` (5507528 bytes)
- grado: **AJUSTADA** · mezcla: H1_DOMINANTE — arquetipo_el_sabio domina; kwml_03_mago es rival distinto (margen 6.247334 >= 1.0 y afinidad 0.387389 < 0.5)

### H1: arquetipo_el_sabio

- porcentaje_relleno: 63.68 · predictibilidad_estructural_pct: 64 · peso_relativo: 0.205139
- desglose_relleno_por_grupo_pct:
  - acoplamiento: 50
  - booker: 63.8889
  - dynamis: 55
  - estructura: 100
  - frye: 47.2222
  - geometria_inercia: 41.6667
  - greimas: 52.0833
  - otras_dimensiones: 64.1667
  - puente_lateral: 99.4839
  - trayectoria_estado: 63.3333

### H2: kwml_03_mago

- porcentaje_relleno: 55.07 · predictibilidad_estructural_pct: 53 · peso_relativo: 0.164394
- desglose_relleno_por_grupo_pct:
  - acoplamiento: 83.3333
  - booker: 58.3333
  - dynamis: 45
  - estructura: 41.6667
  - frye: 50
  - geometria_inercia: 58.3333
  - greimas: 43.75
  - otras_dimensiones: 50
  - puente_lateral: 65.2543
  - trayectoria_estado: 55

### Conjunto abierto (5 hipótesis, cardinalidad_fija: False)

- **H_001** arquetipo_el_sabio · rol: eje · rank_fusion: 31.4536 · soporte_estructural_relativo: 0.27322
  - trazabilidad_geometrica: régimen=CONTINUIDAD_ASCENDENTE · señal_multiescala=0.250874 · micro=0.593809 · meso=0.641251 · macro=0.641251 · aceleración=0.4008 · divergencia_entre_escala=0.047443 · n_cortes_observados=3
- **H_002** 9_audaz_empresa · rol: componente · rank_fusion: 22.811 · soporte_estructural_relativo: 0.198147
  - trazabilidad_geometrica: régimen=CONTINUIDAD_ASCENDENTE · señal_multiescala=0.342327 · micro=0.748005 · meso=0.632742 · macro=0.632742 · aceleración=0.748005 · divergencia_entre_escala=0.115262 · n_cortes_observados=3
- **H_003** candidato_trayectoria_arte_prestigio · rol: componente · rank_fusion: 22.25 · soporte_estructural_relativo: 0.193273
  - trazabilidad_geometrica: régimen=CONTINUIDAD_ASCENDENTE · señal_multiescala=0.352107 · micro=0.64309 · meso=0.692536 · macro=0.692536 · aceleración=0.390217 · divergencia_entre_escala=0.049446 · n_cortes_observados=3
- **H_004** 30_ambicion · rol: componente · rank_fusion: 21.4406 · soporte_estructural_relativo: 0.186243
  - trazabilidad_geometrica: régimen=CONTINUIDAD_ASCENDENTE · señal_multiescala=0.170217 · micro=0.477615 · meso=0.638855 · macro=0.638855 · aceleración=0.210818 · divergencia_entre_escala=0.16124 · n_cortes_observados=3
- **H_005** social_14_overton_ventana · rol: componente · rank_fusion: 17.1667 · soporte_estructural_relativo: 0.149117
  - trazabilidad_geometrica: régimen=CONTINUIDAD_ASCENDENTE · señal_multiescala=0.15943 · micro=0.623399 · meso=0.557873 · macro=0.557873 · aceleración=0.632495 · divergencia_entre_escala=0.065526 · n_cortes_observados=3

### Apuesta principal: CONTINUIDAD_ASCENDENTE (soporte_estructural_agregado: 1) · hipótesis que convergen: arquetipo_el_sabio, 9_audaz_empresa, candidato_trayectoria_arte_prestigio, 30_ambicion, social_14_overton_ventana
- calibración: NO_CALIBRADA_SIN_DESENLACES_POSTERIORES_SELLADOS
- monte_carlo: status=None · total_simulations=None · converged=None/None · nonconverged=None
- predictive_validation: NOT_CALIBRATED_NO_CASE_LEVEL_OUTCOMES · hay una referencia histórica de acierto Top-1/Top-3 del predictor lateral, pero faltan scores y desenlaces sellados por caso para ajustar/calibrar una probabilidad del motor actual; no se sustituyen p

### Input en prosa (entrada.json)

- pregunta: ¿Qué trayectoria sigue Galileo Galilei tras imprimir en Florencia, con licencia eclesiástica, su Diálogo sobre los dos máximos sistemas del mundo?
- person: Galileo Galilei · tipo_sujeto: cientifico · freeze: 1632-03-31 · random_seed: 20261024
- corte C1_1610: fecha=1610-03-13 · hecho=Publicó el Sidereus Nuncius con sus observaciones telescópicas, dedicado a Cosme II de Médici; llamó estrellas mediceas a las lunas de Júpiter que había descubierto, y el gesto le ayudó a obtener el puesto de matemático y filósofo principal de los Médici.
- corte C2_1623: fecha=1623-10 · hecho=Tras un decreto eclesiástico de 1616 que suspendió el libro de Copérnico hasta su corrección, el cardenal Maffeo Barberini, amigo y admirador suyo que se había opuesto a la amonestación de Galileo, fue elegido papa Urbano VIII en 1623; en octubre de 1623 Galileo publicó en Roma El ensayador, dedicado al nuevo papa y recibido con amplio aplauso.
- corte C3_1632: fecha=1632-02-22 · hecho=Publicó el Diálogo sobre los dos máximos sistemas del mundo, que comparaba el sistema copernicano con el ptolemaico, con autorización formal de la Iglesia y permiso papal; la obra estaba dedicada a Fernando II de Médici, que recibió el primer ejemplar impreso el 22 de febrero de 1632.

## CAL_F002_02_PASTEUR (F002)

- ok: True · recibo: COMPLETED · segundos: 34.037
- entrada sha256: `53fc65d239ad4c25dae1c7e70c8abf6099a7bfe04f4e5a2824a0d37c400eb59b` · RESULT completo sha256: `a8712c9b696f80c8b758ed6af36325433c922722887f629f408ca6d2502cc8d8` (6131616 bytes)
- grado: **FRAGIL** · mezcla: H1_CON_COMPONENTES_DE_H2 — 9_audaz_empresa con componentes de arquetipo_el_sabio (margen 0.783237 < GATE_SEPARATION 1.0)

### H1: 9_audaz_empresa

- porcentaje_relleno: 64.53 · predictibilidad_estructural_pct: 56.72 · peso_relativo: 0.15344
- desglose_relleno_por_grupo_pct:
  - acoplamiento: 57.1429
  - booker: 54.7619
  - dynamis: 54.0816
  - estructura: 100
  - frye: 50
  - geometria_inercia: 57.1429
  - greimas: 90.4762
  - otras_dimensiones: 64.2857
  - puente_lateral: 23.3224
  - resolucion: 85.7143
  - trayectoria_estado: 72.8571

### H2: arquetipo_el_sabio

- porcentaje_relleno: 57.95 · predictibilidad_estructural_pct: 55.3 · peso_relativo: 0.149026
- desglose_relleno_por_grupo_pct:
  - acoplamiento: 71.4286
  - booker: 69.0476
  - dynamis: 35.7143
  - estructura: 85.7143
  - frye: 50
  - geometria_inercia: 50
  - greimas: 52.381
  - otras_dimensiones: 57.1429
  - puente_lateral: 68.8891
  - resolucion: 35.7143
  - trayectoria_estado: 61.4286

### Conjunto abierto (5 hipótesis, cardinalidad_fija: False)

- **H_001** 9_audaz_empresa · rol: eje · rank_fusion: 27.2229 · soporte_estructural_relativo: 0.231149
  - trazabilidad_geometrica: régimen=CONTINUIDAD_ASCENDENTE · señal_multiescala=0.412684 · micro=0.686771 · meso=0.716128 · macro=0.716128 · aceleración=0.430323 · divergencia_entre_escala=0.029356 · n_cortes_observados=3
- **H_002** arquetipo_el_sabio · rol: componente · rank_fusion: 26.4397 · soporte_estructural_relativo: 0.224498
  - trazabilidad_geometrica: régimen=CONTINUIDAD_ASCENDENTE · señal_multiescala=0.124803 · micro=0.576592 · meso=0.555306 · macro=0.555306 · aceleración=0.543225 · divergencia_entre_escala=0.021286 · n_cortes_observados=3
- **H_003** social_01_asch_conformidad · rol: componente · rank_fusion: 24.2143 · soporte_estructural_relativo: 0.205602
  - trazabilidad_geometrica: régimen=CONTINUIDAD_ASCENDENTE · señal_multiescala=0.301236 · micro=0.720014 · meso=0.61592 · macro=0.61592 · aceleración=0.720014 · divergencia_entre_escala=0.104094 · n_cortes_observados=3
- **H_004** 30_ambicion · rol: componente · rank_fusion: 23.6097 · soporte_estructural_relativo: 0.200469
  - trazabilidad_geometrica: régimen=CONTINUIDAD_ASCENDENTE · señal_multiescala=0.184612 · micro=0.48707 · meso=0.644924 · macro=0.644924 · aceleración=0.214659 · divergencia_entre_escala=0.157854 · n_cortes_observados=3
- **H_005** bbk_03_individualista · rol: componente · rank_fusion: 16.2857 · soporte_estructural_relativo: 0.138281
  - trazabilidad_geometrica: régimen=CONTINUIDAD_ASCENDENTE · señal_multiescala=0.139373 · micro=0.609656 · meso=0.549702 · macro=0.549702 · aceleración=0.620766 · divergencia_entre_escala=0.059954 · n_cortes_observados=3

### Apuesta principal: CONTINUIDAD_ASCENDENTE (soporte_estructural_agregado: 1) · hipótesis que convergen: 9_audaz_empresa, arquetipo_el_sabio, social_01_asch_conformidad, 30_ambicion, bbk_03_individualista
- calibración: NO_CALIBRADA_SIN_DESENLACES_POSTERIORES_SELLADOS
- monte_carlo: status=None · total_simulations=None · converged=None/None · nonconverged=None
- predictive_validation: NOT_CALIBRATED_NO_CASE_LEVEL_OUTCOMES · hay una referencia histórica de acierto Top-1/Top-3 del predictor lateral, pero faltan scores y desenlaces sellados por caso para ajustar/calibrar una probabilidad del motor actual; no se sustituyen p

### Input en prosa (entrada.json)

- pregunta: ¿Qué trayectoria sigue Louis Pasteur tras presentar ante la Academia de Ciencias sus ensayos de inmunización contra la rabia en perros?
- person: Louis Pasteur · tipo_sujeto: cientifico · freeze: 1885-06-30 · random_seed: 20261024
- corte C1_1862: fecha=1862 · hecho=Sus experimentos contra la generación espontánea, repetidos con Claude Bernard el 20 de abril de 1862, le valieron ese año el premio Alhumbert de 2500 francos de la Academia de Ciencias.
- corte C2_1881: fecha=1881-06-02 · hecho=En Pouilly-le-Fort inoculó ovejas y cabras con cultivos atenuados de carbunco el 5 y el 17 de mayo de 1881, expuso a todos los animales al agente virulento el 31 de mayo y el 2 de junio, ante más de 200 espectadores, todos los animales inoculados habían sobrevivido, a diferencia del grupo de control.
- corte C3_1884: fecha=1884-06-15 · hecho=En notas a la Academia de Ciencias de febrero y mayo de 1884 informó que la virulencia del agente de la rabia cambiaba al pasar por distintos animales (el mono la atenuaba; el conejo y el cobayo la aumentaban) y el 19 de mayo de 1884 expuso un método de inoculación preventiva en perros; se nombró una comisión de control para verificar los experimentos.

## CAL_F002_03_ARBUCKLE (F002)

- ok: True · recibo: COMPLETED · segundos: 18.289
- entrada sha256: `f737feea7743992fcf2e3a7b2ae0855c88070faee55e08de44093f00848f8e78` · RESULT completo sha256: `7166b3d87433130d242b198f69fb4582ec635da893a6c6869fbf49ec846b21a6` (6248893 bytes)
- grado: **FRAGIL** · mezcla: MEZCLA_H1_H2_SIN_SEPARACION — schwartz_07_logro y schwartz_10_autodireccion en mezcla: diferencia top1-top2 0.069378 < banda 0.285714 (indistinguibles a la resolución del motor)

### H1: schwartz_07_logro

- porcentaje_relleno: 52.85 · predictibilidad_estructural_pct: 52.94 · peso_relativo: 0.138426
- desglose_relleno_por_grupo_pct:
  - acoplamiento: 71.4286
  - booker: 47.619
  - dynamis: 80
  - estructura: 28.5714
  - frye: 50
  - geometria_inercia: 50
  - greimas: 38.0952
  - otras_dimensiones: 57.1429
  - puente_lateral: 48.5214
  - resolucion: 57.1429
  - trayectoria_estado: 52.8571

### H2: schwartz_10_autodireccion

- porcentaje_relleno: 51.15 · predictibilidad_estructural_pct: 52.81 · peso_relativo: 0.138044
- desglose_relleno_por_grupo_pct:
  - acoplamiento: 0
  - booker: 33.3333
  - dynamis: 48.5714
  - estructura: 85.7143
  - frye: 50
  - geometria_inercia: 42.8571
  - greimas: 71.4286
  - otras_dimensiones: 48.4127
  - puente_lateral: 65.2109
  - resolucion: 71.4286
  - trayectoria_estado: 45.7143

### Conjunto abierto (5 hipótesis, cardinalidad_fija: False)

- **H_001** schwartz_07_logro · rol: eje · rank_fusion: 25.1526 · soporte_estructural_relativo: 0.229345
  - trazabilidad_geometrica: régimen=CONTINUIDAD_ASCENDENTE · señal_multiescala=0.17441 · micro=0.632866 · meso=0.564374 · macro=0.564374 · aceleración=0.63904 · divergencia_entre_escala=0.068492 · n_cortes_observados=3
- **H_002** schwartz_10_autodireccion · rol: componente · rank_fusion: 25.0833 · soporte_estructural_relativo: 0.228713
  - trazabilidad_geometrica: régimen=CONTINUIDAD_ASCENDENTE · señal_multiescala=0.171533 · micro=0.471365 · meso=0.642967 · macro=0.642967 · aceleración=0.196887 · divergencia_entre_escala=0.171603 · n_cortes_observados=3
- **H_003** tainter_04_colapso_por_simplificacion_forzada · rol: complementaria_trazabilidad_geometrica · rank_fusion: 22.2474 · soporte_estructural_relativo: 0.202855
  - trazabilidad_geometrica: régimen=CONTINUIDAD_ASCENDENTE · señal_multiescala=0.138806 · micro=0.488136 · meso=0.610037 · macro=0.610037 · aceleración=0.270938 · divergencia_entre_escala=0.121901 · n_cortes_observados=3
- **H_004** arquetipo_el_bufon · rol: componente · rank_fusion: 19.0873 · soporte_estructural_relativo: 0.17404
  - trazabilidad_geometrica: régimen=CONTINUIDAD_ASCENDENTE · señal_multiescala=0.188106 · micro=0.64529 · meso=0.568434 · macro=0.568434 · aceleración=0.656078 · divergencia_entre_escala=0.076856 · n_cortes_observados=3
- **H_005** arquetipo_el_creador · rol: componente · rank_fusion: 18.1009 · soporte_estructural_relativo: 0.165046
  - trazabilidad_geometrica: régimen=MESeta_O_ESTABILIZACION · señal_multiescala=0.05452 · micro=0.463929 · meso=0.558925 · macro=0.558925 · aceleración=0.318068 · divergencia_entre_escala=0.094995 · n_cortes_observados=3

### Apuesta principal: CONTINUIDAD_ASCENDENTE (soporte_estructural_agregado: 0.834954) · hipótesis que convergen: schwartz_07_logro, schwartz_10_autodireccion, tainter_04_colapso_por_simplificacion_forzada, arquetipo_el_bufon
- calibración: NO_CALIBRADA_SIN_DESENLACES_POSTERIORES_SELLADOS
- monte_carlo: status=None · total_simulations=None · converged=None/None · nonconverged=None
- predictive_validation: NOT_CALIBRATED_NO_CASE_LEVEL_OUTCOMES · hay una referencia histórica de acierto Top-1/Top-3 del predictor lateral, pero faltan scores y desenlaces sellados por caso para ajustar/calibrar una probabilidad del motor actual; no se sustituyen p

### Input en prosa (entrada.json)

- pregunta: ¿Qué trayectoria sigue Roscoe 'Fatty' Arbuckle tras firmar con Paramount un contrato de un millón de dólares al año y pasar de los cortos cómicos a los largometrajes?
- person: Roscoe 'Fatty' Arbuckle · tipo_sujeto: artista · freeze: 1921-08-31 · random_seed: 20261024
- corte C1_1913: fecha=1913-06 · hecho=Tras empezar en el cine con Selig Polyscope en julio de 1909, entró en 1913 en Keystone, el estudio de Mack Sennett, donde se volvió figura de la comedia; en junio de 1913 se estrenó A Noise from the Deep, con el pastelazo en la cara más antiguo que se conoce en el cine.
- corte C2_1917: fecha=1917-04-23 · hecho=Fundó con Joseph Schenck la productora Comique, con control creativo propio; su primer corto ahí, The Butcher Boy, estrenado el 23 de abril de 1917, que escribió, dirigió y protagonizó, marcó el debut en el cine de Buster Keaton y fue reseñado por Variety.
- corte C3_1920: fecha=1920 · hecho=En 1918 cedió a Keaton su participación en Comique y aceptó la oferta de Paramount de 3 millones de dólares por hasta 18 largometrajes en tres años; en 1920 firmó con Paramount un contrato de un millón de dólares al año y pasó de los cortos a los largometrajes.

## CAL_F002_04_BACH (F002)

- ok: True · recibo: COMPLETED · segundos: 20.856
- entrada sha256: `805d719d412f057b567efe41f969b93fc58ebf3e4aa49f9181346eabf6e8222f` · RESULT completo sha256: `748513abf09b58c6083ec3d94c52f87cc38762bfca44f18e380cbc091972f583` (7117152 bytes)
- grado: **FRAGIL** · mezcla: MEZCLA_H1_H2_SIN_SEPARACION — tainter_01_inversion_complejidad_productiva y schwartz_10_autodireccion en mezcla: diferencia top1-top2 0.001815 < banda 0.25 (indistinguibles a la resolución del motor)

### H1: tainter_01_inversion_complejidad_productiva

- porcentaje_relleno: 64.48 · predictibilidad_estructural_pct: 54.5 · peso_relativo: 0.11039
- desglose_relleno_por_grupo_pct:
  - acoplamiento: 45
  - booker: 50
  - dynamis: 85
  - estructura: 90
  - frye: 50
  - geometria_inercia: 95
  - greimas: 68.75
  - otras_dimensiones: 67.5
  - puente_lateral: 0
  - resolucion: 95
  - trayectoria_estado: 63

### H2: schwartz_10_autodireccion

- porcentaje_relleno: 48.82 · predictibilidad_estructural_pct: 54.5 · peso_relativo: 0.110382
- desglose_relleno_por_grupo_pct:
  - acoplamiento: 20
  - booker: 40
  - dynamis: 50
  - estructura: 30
  - frye: 50
  - geometria_inercia: 35
  - greimas: 45
  - otras_dimensiones: 53.5
  - puente_lateral: 77.4773
  - resolucion: 65
  - trayectoria_estado: 71

### Conjunto abierto (7 hipótesis, cardinalidad_fija: False)

- **H_001** tainter_01_inversion_complejidad_productiva · rol: eje · rank_fusion: 24.9 · soporte_estructural_relativo: 0.172366
  - trazabilidad_geometrica: régimen=CONTINUIDAD_ASCENDENTE · señal_multiescala=0.301859 · micro=0.720444 · meso=0.616172 · macro=0.616172 · aceleración=0.720444 · divergencia_entre_escala=0.104272 · n_cortes_observados=3
- **H_002** schwartz_10_autodireccion · rol: componente · rank_fusion: 24.8982 · soporte_estructural_relativo: 0.172353
  - trazabilidad_geometrica: régimen=MESeta_O_ESTABILIZACION · señal_multiescala=0.048498 · micro=0.490268 · meso=0.541239 · macro=0.541239 · aceleración=0.399264 · divergencia_entre_escala=0.050972 · n_cortes_observados=3
- **H_003** 9_audaz_empresa · rol: componente · rank_fusion: 24.3266 · soporte_estructural_relativo: 0.168397
  - trazabilidad_geometrica: régimen=MESeta_O_ESTABILIZACION · señal_multiescala=-0.020442 · micro=0.490668 · meso=0.489335 · macro=0.489335 · aceleración=0.502667 · divergencia_entre_escala=0.001333 · n_cortes_observados=3
- **H_004** 10_rapto · rol: componente · rank_fusion: 20.462 · soporte_estructural_relativo: 0.141644
  - trazabilidad_geometrica: régimen=MESeta_O_ESTABILIZACION · señal_multiescala=-0.017598 · micro=0.494134 · meso=0.489735 · macro=0.489735 · aceleración=0.508799 · divergencia_entre_escala=0.004399 · n_cortes_observados=3
- **H_005** 36_perdida_de_los_seres_queridos · rol: componente · rank_fusion: 18.0235 · soporte_estructural_relativo: 0.124764
  - trazabilidad_geometrica: régimen=CONTINUIDAD_ASCENDENTE · señal_multiescala=0.187077 · micro=0.491867 · meso=0.644374 · macro=0.644374 · aceleración=0.222032 · divergencia_entre_escala=0.152507 · n_cortes_observados=3
- **H_006** 24_rivalidad_de_superior_e_inferior · rol: componente · rank_fusion: 16.4 · soporte_estructural_relativo: 0.113526
  - trazabilidad_geometrica: régimen=CONTINUIDAD_DESCENDENTE · señal_multiescala=-0.31078 · micro=0.283006 · meso=0.375412 · macro=0.375412 · aceleración=0.30131 · divergencia_entre_escala=0.092406 · n_cortes_observados=3
- **H_007** aliado · rol: componente · rank_fusion: 15.45 · soporte_estructural_relativo: 0.10695
  - trazabilidad_geometrica: régimen=CONTINUIDAD_ASCENDENTE · señal_multiescala=0.142119 · micro=0.493867 · meso=0.609656 · macro=0.609656 · aceleración=0.280739 · divergencia_entre_escala=0.115789 · n_cortes_observados=3

### Apuesta principal: MESeta_O_ESTABILIZACION (soporte_estructural_agregado: 0.482394) · hipótesis que convergen: schwartz_10_autodireccion, 9_audaz_empresa, 10_rapto
- calibración: NO_CALIBRADA_SIN_DESENLACES_POSTERIORES_SELLADOS
- monte_carlo: status=None · total_simulations=None · converged=None/None · nonconverged=None
- predictive_validation: NOT_CALIBRATED_NO_CASE_LEVEL_OUTCOMES · hay una referencia histórica de acierto Top-1/Top-3 del predictor lateral, pero faltan scores y desenlaces sellados por caso para ajustar/calibrar una probabilidad del motor actual; no se sustituyen p

### Input en prosa (entrada.json)

- pregunta: ¿Qué trayectoria sigue Johann Sebastian Bach tras dejar la corte de Köthen y asumir el cargo de cantor de Santo Tomás y director musical de Leipzig?
- person: Johann Sebastian Bach · tipo_sujeto: artista · freeze: 1723-06-01 · random_seed: 20261024
- corte C1_1717: fecha=1717-12-02 · hecho=Al insistir con terquedad en que la corte de Weimar lo dejara ir, fue detenido el 6 de noviembre de 1717 y liberado el 2 de diciembre con un despido desfavorable; ese año el príncipe Leopoldo de Anhalt-Köthen, también músico, lo había contratado como maestro de capilla, con buen sueldo y amplia libertad.
- corte C2_1721: fecha=1721-12-03 · hecho=En Köthen se dedicó sobre todo a la música instrumental; el 7 de julio de 1720 perdió de forma repentina a su esposa Maria Barbara; el 24 de marzo de 1721 dedicó seis conciertos al margrave Christian Ludwig de Brandemburgo y el 3 de diciembre de 1721 se casó con la soprano Anna Magdalena Wilcke.
- corte C3_1723: fecha=1723-05-30 · hecho=El concejo de Leipzig le ofreció el puesto de cantor de Santo Tomás después de que Telemann y Graupner lo rechazaran; asumió en 1723 la preparación del coro de Santo Tomás para cuatro iglesias luteranas y la música de los actos de la ciudad, y el 30 de mayo de 1723, su primer domingo en el cargo, estrenó la cantata BWV 75 en la Nikolaikirche.

## CAL_F002_05_MCCARTHY (F002)

- ok: True · recibo: COMPLETED · segundos: 39.319
- entrada sha256: `a84c20ef8b32c2c09b1ca351f95628f8db81b3670194518dd09f96682db42ecb` · RESULT completo sha256: `885167f0191c9fbe04aa6893dccfbd86a5dcb3f5b26d20f8d9aeacbc589ce0ab` (5976663 bytes)
- grado: **AJUSTADA** · mezcla: H1_DOMINANTE — schwartz_07_logro domina; 30_ambicion es rival distinto (margen 1.661299 >= 1.0 y afinidad 0.287722 < 0.5)

### H1: schwartz_07_logro

- porcentaje_relleno: 56.52 · predictibilidad_estructural_pct: 61.46 · peso_relativo: 0.156892
- desglose_relleno_por_grupo_pct:
  - acoplamiento: 0
  - booker: 37.5
  - dynamis: 85
  - estructura: 37.5
  - frye: 50
  - geometria_inercia: 93.75
  - greimas: 58.3333
  - otras_dimensiones: 78.125
  - puente_lateral: 75
  - trayectoria_estado: 50

### H2: 30_ambicion

- porcentaje_relleno: 61.54 · predictibilidad_estructural_pct: 58.28 · peso_relativo: 0.147414
- desglose_relleno_por_grupo_pct:
  - acoplamiento: 62.5
  - booker: 66.6667
  - dynamis: 72.5
  - estructura: 87.5
  - frye: 50
  - geometria_inercia: 56.25
  - greimas: 41.6667
  - otras_dimensiones: 67.1875
  - puente_lateral: 51.1088
  - trayectoria_estado: 60

### Conjunto abierto (6 hipótesis, cardinalidad_fija: False)

- **H_001** schwartz_07_logro · rol: eje · rank_fusion: 27.5 · soporte_estructural_relativo: 0.236639
  - trazabilidad_geometrica: régimen=CONTINUIDAD_ASCENDENTE · señal_multiescala=0.177735 · micro=0.63497 · meso=0.565816 · macro=0.565816 · aceleración=0.640515 · divergencia_entre_escala=0.069155 · n_cortes_observados=3
- **H_002** 30_ambicion · rol: componente · rank_fusion: 25.8387 · soporte_estructural_relativo: 0.222343
  - trazabilidad_geometrica: régimen=MESeta_O_ESTABILIZACION · señal_multiescala=0.004978 · micro=0.500133 · meso=0.503667 · macro=0.503667 · aceleración=0.492934 · divergencia_entre_escala=0.003533 · n_cortes_observados=3
- **H_003** monomito_08_la_odisea_o_prueba_suprema · rol: componente · rank_fusion: 21.375 · soporte_estructural_relativo: 0.183933
  - trazabilidad_geometrica: régimen=CONTINUIDAD_ASCENDENTE · señal_multiescala=0.333981 · micro=0.641742 · meso=0.679614 · macro=0.679614 · aceleración=0.416263 · divergencia_entre_escala=0.037872 · n_cortes_observados=3
- **H_004** 9_audaz_empresa · rol: componente · rank_fusion: 16.8721 · soporte_estructural_relativo: 0.145185
  - trazabilidad_geometrica: régimen=MESeta_O_ESTABILIZACION · señal_multiescala=-0.038026 · micro=0.481741 · meso=0.48061 · macro=0.48061 · aceleración=0.502267 · divergencia_entre_escala=0.001132 · n_cortes_observados=3
- **H_005** schwartz_06_poder · rol: componente · rank_fusion: 12.875 · soporte_estructural_relativo: 0.11079
  - trazabilidad_geometrica: régimen=CONTINUIDAD_ASCENDENTE · señal_multiescala=0.124351 · micro=0.481475 · meso=0.602526 · macro=0.602526 · aceleración=0.272839 · divergencia_entre_escala=0.121051 · n_cortes_observados=3
- **H_006** mbti_factor_extraversion_e · rol: componente · rank_fusion: 11.75 · soporte_estructural_relativo: 0.101109
  - trazabilidad_geometrica: régimen=MESeta_O_ESTABILIZACION · señal_multiescala=0.040755 · micro=0.473359 · meso=0.543887 · macro=0.543887 · aceleración=0.362314 · divergencia_entre_escala=0.070528 · n_cortes_observados=3

### Apuesta principal: CONTINUIDAD_ASCENDENTE (soporte_estructural_agregado: 0.531362) · hipótesis que convergen: schwartz_07_logro, monomito_08_la_odisea_o_prueba_suprema, schwartz_06_poder
- calibración: NO_CALIBRADA_SIN_DESENLACES_POSTERIORES_SELLADOS
- monte_carlo: status=None · total_simulations=None · converged=None/None · nonconverged=None
- predictive_validation: NOT_CALIBRATED_NO_CASE_LEVEL_OUTCOMES · hay una referencia histórica de acierto Top-1/Top-3 del predictor lateral, pero faltan scores y desenlaces sellados por caso para ajustar/calibrar una probabilidad del motor actual; no se sustituyen p

### Input en prosa (entrada.json)

- pregunta: ¿Qué trayectoria sigue el senador Joseph McCarthy tras llevar sus investigaciones anticomunistas al Ejército de Estados Unidos y enfrentarse en audiencia al general Ralph Zwicker?
- person: Joseph McCarthy · tipo_sujeto: politico · freeze: 1954-02-28 · random_seed: 20261024
- corte C1_1950: fecha=1950-02-09 · hecho=En un discurso en Wheeling, Virginia Occidental, mostró un papel que según dijo contenía una lista de comunistas conocidos que trabajaban en el Departamento de Estado; el discurso le dio notoriedad nacional.
- corte C2_1953: fecha=1953-01 · hecho=Al iniciar su segundo mandato en enero de 1953 pasó a presidir la Comisión de Operaciones Gubernamentales del Senado, que incluía el Subcomité Permanente de Investigaciones, cuyo mandato flexible usó para sus propias investigaciones sobre comunistas en el gobierno.
- corte C3_1954: fecha=1954-02-18 · hecho=El subcomité citó el 30 de enero de 1954 al mayor del Ejército Irving Peress, que se acogió a la Quinta Enmienda; el 18 de febrero de 1954 interrogó al general Ralph Zwicker, su comandante, que por consejo del Ejército se negó a responder algunas preguntas, y McCarthy le dijo que no era apto para vestir ese uniforme.

## CAL_F002_06_COOLIDGE (F002)

- ok: True · recibo: COMPLETED · segundos: 9.265
- entrada sha256: `ce093eb238f160061a8c9d7e9f427c930d45a15b057ca0fbaee5665cdec446f1` · RESULT completo sha256: `dcf197a9f594ea99fe19543bf0c91fa1ddc64db27e17ad767f00e298b219f0e4` (3345639 bytes)
- grado: **AJUSTADA** · mezcla: H1_DOMINANTE — 36_perdida_de_los_seres_queridos domina; frye_mythos_romance es rival distinto (margen 4.0 >= 1.0 y afinidad 0.2 < 0.5)

### H1: 36_perdida_de_los_seres_queridos

- porcentaje_relleno: 61.47 · predictibilidad_estructural_pct: 55.6 · peso_relativo: 0.556314
- desglose_relleno_por_grupo_pct:
  - acoplamiento: 0
  - booker: 50
  - dynamis: 100
  - estructura: 100
  - frye: 50
  - geometria_inercia: 50
  - greimas: 100
  - otras_dimensiones: 42.8571
  - puente_lateral: 100
  - resolucion: 50
  - trayectoria_estado: 33.3333

### H2: frye_mythos_romance

- porcentaje_relleno: 38.53 · predictibilidad_estructural_pct: 44.4 · peso_relativo: 0.425416
- desglose_relleno_por_grupo_pct:
  - acoplamiento: 100
  - booker: 50
  - dynamis: 0
  - estructura: 0
  - frye: 50
  - geometria_inercia: 50
  - greimas: 0
  - otras_dimensiones: 57.1429
  - puente_lateral: 0
  - resolucion: 50
  - trayectoria_estado: 66.6667

### Conjunto abierto (3 hipótesis, cardinalidad_fija: False)

- **H_001** 36_perdida_de_los_seres_queridos · rol: eje · rank_fusion: 17 · soporte_estructural_relativo: 0.556314
  - trazabilidad_geometrica: régimen=CONTINUIDAD_ASCENDENTE · señal_multiescala=0.387135 · micro=0.7776 · meso=0.651552 · macro=0.651552 · aceleración=0.7776 · divergencia_entre_escala=0.126048 · n_cortes_observados=3
- **H_002** frye_mythos_romance · rol: componente · rank_fusion: 13 · soporte_estructural_relativo: 0.425416
  - trazabilidad_geometrica: régimen=CONTINUIDAD_ASCENDENTE · señal_multiescala=0.299521 · micro=0.71883 · meso=0.615226 · macro=0.615226 · aceleración=0.71883 · divergencia_entre_escala=0.103604 · n_cortes_observados=3
- **H_003** bbk_05_flecha_recta · rol: componente · rank_fusion: 0.5583 · soporte_estructural_relativo: 0.01827
  - trazabilidad_geometrica: régimen=MESeta_O_ESTABILIZACION · señal_multiescala=0 · micro=0.5 · meso=0.5 · macro=0.5 · aceleración=0.5 · divergencia_entre_escala=0 · n_cortes_observados=3

### Apuesta principal: CONTINUIDAD_ASCENDENTE (soporte_estructural_agregado: 0.98173) · hipótesis que convergen: 36_perdida_de_los_seres_queridos, frye_mythos_romance
- calibración: NO_CALIBRADA_SIN_DESENLACES_POSTERIORES_SELLADOS
- monte_carlo: status=None · total_simulations=None · converged=None/None · nonconverged=None
- predictive_validation: NOT_CALIBRATED_NO_CASE_LEVEL_OUTCOMES · hay una referencia histórica de acierto Top-1/Top-3 del predictor lateral, pero faltan scores y desenlaces sellados por caso para ajustar/calibrar una probabilidad del motor actual; no se sustituyen p

### Input en prosa (entrada.json)

- pregunta: ¿Qué trayectoria sigue Calvin Coolidge tras ganar la elección presidencial de 1924 e iniciar su primer mandato completo como presidente de Estados Unidos?
- person: Calvin Coolidge · tipo_sujeto: politico · freeze: 1925-03-05 · random_seed: 20261024
- corte C1_1919: fecha=1919-09 · hecho=Como gobernador de Massachusetts enfrentó la huelga de la policía de Boston iniciada el 9 de septiembre de 1919 y respondió por telegrama a Samuel Gompers que no existía el derecho a la huelga contra la seguridad pública; la firmeza le dio fama nacional.
- corte C2_1923: fecha=1923-08-03 · hecho=Vicepresidente de Warren Harding desde 1921, al quedar vacante la presidencia juró el cargo a las 2:47 de la madrugada del 3 de agosto de 1923 en el salón de la casa familiar, ante su padre, notario público, a la luz de una lámpara de queroseno.
- corte C3_1925: fecha=1925-03-04 · hecho=En julio de 1924 perdió a su hijo Calvin Jr., de 16 años, por una septicemia originada en una ampolla; en la elección de noviembre de 1924 obtuvo 382 votos electorales y el 54 % del voto popular, y su investidura del 4 de marzo de 1925 fue la primera transmitida por radio.

## CAL_F002_07_CATALINA (F002)

- ok: True · recibo: COMPLETED · segundos: 20.55
- entrada sha256: `267264ce64257c224f7d68041ee924cb519a72de3959cb3a9a141f976a2d5ec5` · RESULT completo sha256: `5256e8878cc26dfddc1a46bebca33fd2459686b13f61b2d943206ba1967f2bbb` (6733219 bytes)
- grado: **FRAGIL** · mezcla: H1_CON_COMPONENTES_DE_H2 — schwartz_07_logro con componentes de 12_obtencion (margen 0.805673 < GATE_SEPARATION 1.0; afinidad 0.633333 >= 0.5)

### H1: schwartz_07_logro

- porcentaje_relleno: 53.77 · predictibilidad_estructural_pct: 54.9 · peso_relativo: 0.127994
- desglose_relleno_por_grupo_pct:
  - acoplamiento: 37.5
  - booker: 45.8333
  - dynamis: 82.5
  - estructura: 43.75
  - frye: 50
  - geometria_inercia: 50
  - greimas: 54.1667
  - otras_dimensiones: 64.5833
  - puente_lateral: 43.1571
  - resolucion: 62.5
  - trayectoria_estado: 57.5

### H2: 12_obtencion

- porcentaje_relleno: 53.35 · predictibilidad_estructural_pct: 53.44 · peso_relativo: 0.124058
- desglose_relleno_por_grupo_pct:
  - acoplamiento: 62.5
  - booker: 50
  - dynamis: 77.5
  - estructura: 25
  - frye: 50
  - geometria_inercia: 50
  - greimas: 50
  - otras_dimensiones: 55.5556
  - puente_lateral: 48.7885
  - resolucion: 62.5
  - trayectoria_estado: 55

### Conjunto abierto (7 hipótesis, cardinalidad_fija: False)

- **H_001** schwartz_07_logro · rol: eje · rank_fusion: 26.1966 · soporte_estructural_relativo: 0.170086
  - trazabilidad_geometrica: régimen=CONTINUIDAD_ASCENDENTE · señal_multiescala=0.179401 · micro=0.636946 · meso=0.566078 · macro=0.566078 · aceleración=0.643946 · divergencia_entre_escala=0.070868 · n_cortes_observados=3
- **H_002** utopia_mentalidad_liberal · rol: componente · rank_fusion: 24.0617 · soporte_estructural_relativo: 0.156225
  - trazabilidad_geometrica: régimen=CONTINUIDAD_ASCENDENTE · señal_multiescala=0.13787 · micro=0.490668 · meso=0.608068 · macro=0.608068 · aceleración=0.278269 · divergencia_entre_escala=0.117401 · n_cortes_observados=3
- **H_003** eterno_retorno_01_caos_primordial · rol: componente · rank_fusion: 23.9375 · soporte_estructural_relativo: 0.155418
  - trazabilidad_geometrica: régimen=CONTINUIDAD_ASCENDENTE · señal_multiescala=0.306055 · micro=0.723335 · meso=0.617874 · macro=0.617874 · aceleración=0.723335 · divergencia_entre_escala=0.105462 · n_cortes_observados=3
- **H_004** tainter_04_colapso_por_simplificacion_forzada · rol: complementaria_trazabilidad_geometrica · rank_fusion: 23.4037 · soporte_estructural_relativo: 0.151952
  - trazabilidad_geometrica: régimen=CONTINUIDAD_ASCENDENTE · señal_multiescala=0.143189 · micro=0.490401 · meso=0.612191 · macro=0.612191 · aceleración=0.270938 · divergencia_entre_escala=0.12179 · n_cortes_observados=3
- **H_005** arquetipo_el_ciudadano · rol: complementaria_trazabilidad_geometrica · rank_fusion: 20.3961 · soporte_estructural_relativo: 0.132425
  - trazabilidad_geometrica: régimen=MESeta_O_ESTABILIZACION · señal_multiescala=-0.019375 · micro=0.490801 · meso=0.490068 · macro=0.490068 · aceleración=0.501467 · divergencia_entre_escala=0.000733 · n_cortes_observados=3
- **H_006** social_01_asch_conformidad · rol: componente · rank_fusion: 18.7649 · soporte_estructural_relativo: 0.121834
  - trazabilidad_geometrica: régimen=MESeta_O_ESTABILIZACION · señal_multiescala=-0.027904 · micro=0.486936 · meso=0.485604 · macro=0.485604 · aceleración=0.502667 · divergencia_entre_escala=0.001332 · n_cortes_observados=3
- **H_007** 25_adulterio · rol: componente · rank_fusion: 17.2597 · soporte_estructural_relativo: 0.112061
  - trazabilidad_geometrica: régimen=CONTINUIDAD_ASCENDENTE · señal_multiescala=0.168988 · micro=0.493334 · meso=0.630074 · macro=0.630074 · aceleración=0.246308 · divergencia_entre_escala=0.13674 · n_cortes_observados=3

### Apuesta principal: CONTINUIDAD_ASCENDENTE (soporte_estructural_agregado: 0.745742) · hipótesis que convergen: schwartz_07_logro, utopia_mentalidad_liberal, eterno_retorno_01_caos_primordial, tainter_04_colapso_por_simplificacion_forzada, 25_adulterio
- calibración: NO_CALIBRADA_SIN_DESENLACES_POSTERIORES_SELLADOS
- monte_carlo: status=None · total_simulations=None · converged=None/None · nonconverged=None
- predictive_validation: NOT_CALIBRATED_NO_CASE_LEVEL_OUTCOMES · hay una referencia histórica de acierto Top-1/Top-3 del predictor lateral, pero faltan scores y desenlaces sellados por caso para ajustar/calibrar una probabilidad del motor actual; no se sustituyen p

### Input en prosa (entrada.json)

- pregunta: ¿Qué trayectoria sigue Catalina Alexéievna, consorte del emperador Pedro III, tras la llegada de su esposo al trono ruso y el creciente distanciamiento entre ambos?
- person: Catalina Alexéievna (nacida Sofía de Anhalt-Zerbst) · tipo_sujeto: gobernante · freeze: 1762-06-01 · random_seed: 20261024
- corte C1_1745: fecha=1745-08-21 · hecho=Princesa alemana llegada a Rusia en 1744 a los 15 años, se empeñó en aprender ruso y ganarse a la emperatriz Isabel; el 28 de junio de 1744 fue recibida en la Iglesia ortodoxa con el nombre de Yekaterina Alexéievna y el 21 de agosto de 1745 se casó con el gran duque Pedro.
- corte C2_1754: fecha=1754 · hecho=El matrimonio resultó infeliz; Pedro tomó una amante y ella se relacionó con otras figuras de la corte, se ganó el favor de grupos políticos poderosos opuestos a su esposo y se volvió una lectora ávida en francés; en 1754 nació su hijo Pablo, heredero de la dinastía.
- corte C3_1762: fecha=1762-05-05 · hecho=Pedro subió al trono el 5 de enero de 1762 y ella pasó a ser emperatriz consorte; admirador de Federico II, Pedro firmó el 5 de mayo de 1762 el Tratado de San Petersburgo, que cerró la guerra con Prusia y devolvió las ganancias rusas.

## CAL_F002_08_LUISXVI (F002)

- ok: True · recibo: COMPLETED · segundos: 16.225
- entrada sha256: `905cd94e3734ef2c44f6368c1e415adab41287e2208dc950be0511eac2a8ed27` · RESULT completo sha256: `38574d4726f824666a6c7c9aed15a87c8e84ac189781e19378be91fe893f477d` (4771047 bytes)
- grado: **AJUSTADA** · mezcla: H1_DOMINANTE — arquetipo_el_explorador domina; 32_celos_equivocados es rival distinto (margen 5.209343 >= 1.0 y afinidad 0.2 < 0.5)

### H1: arquetipo_el_explorador

- porcentaje_relleno: 55.73 · predictibilidad_estructural_pct: 60.45 · peso_relativo: 0.342782
- desglose_relleno_por_grupo_pct:
  - acoplamiento: 66.6667
  - booker: 50
  - dynamis: 33.3333
  - estructura: 33.3333
  - frye: 50
  - geometria_inercia: 66.6667
  - greimas: 38.8889
  - otras_dimensiones: 70.8333
  - puente_lateral: 94.2835
  - trayectoria_estado: 53.3333

### H2: 32_celos_equivocados

- porcentaje_relleno: 54.32 · predictibilidad_estructural_pct: 48.01 · peso_relativo: 0.26113
- desglose_relleno_por_grupo_pct:
  - acoplamiento: 33.3333
  - booker: 50
  - dynamis: 66.6667
  - estructura: 66.6667
  - frye: 50
  - geometria_inercia: 100
  - greimas: 61.1111
  - otras_dimensiones: 58.3333
  - puente_lateral: 7.1192
  - trayectoria_estado: 50

### Conjunto abierto (4 hipótesis, cardinalidad_fija: False)

- **H_001** arquetipo_el_explorador · rol: eje · rank_fusion: 24.376 · soporte_estructural_relativo: 0.342782
  - trazabilidad_geometrica: régimen=CONTINUIDAD_ASCENDENTE · señal_multiescala=0.297647 · micro=0.717535 · meso=0.614468 · macro=0.614468 · aceleración=0.717535 · divergencia_entre_escala=0.103067 · n_cortes_observados=3
- **H_002** 10_rapto · rol: componente · rank_fusion: 19.1667 · soporte_estructural_relativo: 0.269527
  - trazabilidad_geometrica: régimen=CONTINUIDAD_ASCENDENTE · señal_multiescala=0.362757 · micro=0.666471 · meso=0.688832 · macro=0.688832 · aceleración=0.448978 · divergencia_entre_escala=0.022362 · n_cortes_observados=3
- **H_003** 32_celos_equivocados · rol: componente · rank_fusion: 18.5695 · soporte_estructural_relativo: 0.26113
  - trazabilidad_geometrica: régimen=CONTINUIDAD_ASCENDENTE · señal_multiescala=0.348591 · micro=0.752204 · meso=0.635341 · macro=0.635341 · aceleración=0.752204 · divergencia_entre_escala=0.116862 · n_cortes_observados=3
- **H_004** social_01_asch_conformidad · rol: componente · rank_fusion: 9 · soporte_estructural_relativo: 0.126561
  - trazabilidad_geometrica: régimen=CONTINUIDAD_ASCENDENTE · señal_multiescala=0.149308 · micro=0.501733 · meso=0.611115 · macro=0.611115 · aceleración=0.291082 · divergencia_entre_escala=0.109381 · n_cortes_observados=3

### Apuesta principal: CONTINUIDAD_ASCENDENTE (soporte_estructural_agregado: 1) · hipótesis que convergen: arquetipo_el_explorador, 10_rapto, 32_celos_equivocados, social_01_asch_conformidad
- calibración: NO_CALIBRADA_SIN_DESENLACES_POSTERIORES_SELLADOS
- monte_carlo: status=None · total_simulations=None · converged=None/None · nonconverged=None
- predictive_validation: NOT_CALIBRATED_NO_CASE_LEVEL_OUTCOMES · hay una referencia histórica de acierto Top-1/Top-3 del predictor lateral, pero faltan scores y desenlaces sellados por caso para ajustar/calibrar una probabilidad del motor actual; no se sustituyen p

### Input en prosa (entrada.json)

- pregunta: ¿Qué trayectoria sigue Luis XVI, rey bajo la nueva monarquía constitucional, instalado en las Tullerías de París y tras impedírsele la salida hacia Saint-Cloud en abril?
- person: Luis XVI de Francia · tipo_sujeto: gobernante · freeze: 1791-06-01 · random_seed: 20261024
- corte C1_1789A: fecha=1789-05-05 · hecho=Ante una grave crisis fiscal convocó los Estados Generales, que se abrieron en Versalles el 5 de mayo de 1789, la primera reunión desde 1614.
- corte C2_1789B: fecha=1789-10-06 · hecho=Tras la marcha de las mujeres sobre Versalles, la multitud, con la Guardia Nacional al frente, llevó a la familia real a París el 6 de octubre de 1789 y la instaló en las Tullerías; el 14 de julio de 1790 la Fiesta de la Federación le reservó el papel de rey ciudadano de la naciente monarquía constitucional.
- corte C3_1791: fecha=1791-04 · hecho=En Semana Santa de 1791 quiso salir de las Tullerías hacia Saint-Cloud para recibir los servicios de un sacerdote no juramentado, contrario a la Constitución Civil del Clero, y no le dejaron moverse.

## CAL_F002_09_ROCKEFELLER (F002)

- ok: True · recibo: COMPLETED · segundos: 35.627
- entrada sha256: `8d817fffc938d0f56b280221eee35448556de19afa9e3623f78e0c080fd67151` · RESULT completo sha256: `7ec9787c44371a4c05bb73601e9cf8fcfc3edb97278638b3daa24ab11274b95d` (5574738 bytes)
- grado: **AJUSTADA** · mezcla: H1_DOMINANTE — 30_ambicion domina; schwartz_07_logro es rival distinto (margen 1.742494 >= 1.0 y afinidad 0.457682 < 0.5)

### H1: 30_ambicion

- porcentaje_relleno: 59.48 · predictibilidad_estructural_pct: 58.13 · peso_relativo: 0.210081
- desglose_relleno_por_grupo_pct:
  - acoplamiento: 0
  - booker: 60
  - dynamis: 68.5714
  - estructura: 100
  - frye: 33.3333
  - geometria_inercia: 50
  - greimas: 80
  - otras_dimensiones: 55
  - puente_lateral: 49.361
  - resolucion: 70
  - trayectoria_estado: 88

### H2: schwartz_07_logro

- porcentaje_relleno: 50.89 · predictibilidad_estructural_pct: 55.01 · peso_relativo: 0.197027
- desglose_relleno_por_grupo_pct:
  - acoplamiento: 80
  - booker: 60
  - dynamis: 57.1429
  - estructura: 20
  - frye: 56.6667
  - geometria_inercia: 60
  - greimas: 26.6667
  - otras_dimensiones: 67.5
  - puente_lateral: 77.7778
  - resolucion: 20
  - trayectoria_estado: 34

### Conjunto abierto (4 hipótesis, cardinalidad_fija: False)

- **H_001** 30_ambicion · rol: eje · rank_fusion: 28.0425 · soporte_estructural_relativo: 0.336056
  - trazabilidad_geometrica: régimen=CONTINUIDAD_ASCENDENTE · señal_multiescala=0.322734 · micro=0.621393 · meso=0.681354 · macro=0.681354 · aceleración=0.370735 · divergencia_entre_escala=0.05996 · n_cortes_observados=3
- **H_002** eterno_retorno_02_cosmizacion_fundacion · rol: complementaria_trazabilidad_geometrica · rank_fusion: 21.4002 · soporte_estructural_relativo: 0.256456
  - trazabilidad_geometrica: régimen=CONTINUIDAD_ASCENDENTE · señal_multiescala=0.435086 · micro=0.653909 · meso=0.74936 · macro=0.74936 · aceleración=0.285393 · divergencia_entre_escala=0.095451 · n_cortes_observados=3
- **H_003** mbti_factor_juicio_j · rol: componente · rank_fusion: 19.0031 · soporte_estructural_relativo: 0.22773
  - trazabilidad_geometrica: régimen=CONTINUIDAD_ASCENDENTE · señal_multiescala=0.266101 · micro=0.5992 · meso=0.649976 · macro=0.649976 · aceleración=0.393267 · divergencia_entre_escala=0.050776 · n_cortes_observados=3
- **H_004** tainter_01_inversion_complejidad_productiva · rol: componente · rank_fusion: 15 · soporte_estructural_relativo: 0.179757
  - trazabilidad_geometrica: régimen=CONTINUIDAD_ASCENDENTE · señal_multiescala=0.224969 · micro=0.578674 · meso=0.62939 · macro=0.62939 · aceleración=0.395432 · divergencia_entre_escala=0.050716 · n_cortes_observados=3

### Apuesta principal: CONTINUIDAD_ASCENDENTE (soporte_estructural_agregado: 1) · hipótesis que convergen: 30_ambicion, eterno_retorno_02_cosmizacion_fundacion, mbti_factor_juicio_j, tainter_01_inversion_complejidad_productiva
- calibración: NO_CALIBRADA_SIN_DESENLACES_POSTERIORES_SELLADOS
- monte_carlo: status=None · total_simulations=None · converged=None/None · nonconverged=None
- predictive_validation: NOT_CALIBRATED_NO_CASE_LEVEL_OUTCOMES · hay una referencia histórica de acierto Top-1/Top-3 del predictor lateral, pero faltan scores y desenlaces sellados por caso para ajustar/calibrar una probabilidad del motor actual; no se sustituyen p

### Input en prosa (entrada.json)

- pregunta: ¿Qué trayectoria sigue John D. Rockefeller tras constituir en Ohio la Standard Oil Company con sus socios refinadores de Cleveland?
- person: John D. Rockefeller · tipo_sujeto: empresario · freeze: 1870-01-31 · random_seed: 20261024
- corte C1_1859: fecha=1859 · hecho=Con ahorros propios y 1000 dólares prestados por su padre fundó en Cleveland con Maurice Clark y George Gardner una casa de comisiones de productos agrícolas con 4000 dólares de capital, que pasó a llamarse Clark & Rockefeller.
- corte C2_1868: fecha=1868 · hecho=En febrero de 1865 compró en subasta la parte de los hermanos Clark en la refinería por 72 500 dólares y formó Rockefeller & Andrews, día que llamó decisivo para su carrera; en 1867 entró Henry Flagler y nació Rockefeller, Andrews & Flagler, que hacia 1868 tenía dos refinerías en Cleveland y una filial comercial en Nueva York.
- corte C3_1870: fecha=1870-01-10 · hecho=El 10 de enero de 1870 disolvió la sociedad Rockefeller, Andrews & Flagler y cofundó con sus socios la Standard Oil Company de Ohio.

## CAL_F002_10_DURANT (F002)

- ok: True · recibo: COMPLETED · segundos: 39.239
- entrada sha256: `e3d8254732e64439841bdbdde8950f2d315d91f38c4bebd242c2168e4aa9b22b` · RESULT completo sha256: `f779d214ecd0428dfd48ba9c0b97962edf1a5d399c807103bb9b7279c7a97321` (5372891 bytes)
- grado: **AJUSTADA** · mezcla: H1_DOMINANTE — 12_obtencion domina; 9_audaz_empresa es rival distinto (margen 1.471763 >= 1.0 y afinidad 0.19962 < 0.5)

### H1: 12_obtencion

- porcentaje_relleno: 66.3 · predictibilidad_estructural_pct: 63.49 · peso_relativo: 0.228154
- desglose_relleno_por_grupo_pct:
  - acoplamiento: 100
  - booker: 60
  - dynamis: 76
  - estructura: 60
  - frye: 53.3333
  - geometria_inercia: 60
  - greimas: 53.3333
  - otras_dimensiones: 52.5
  - puente_lateral: 95.8681
  - trayectoria_estado: 52

### H2: 9_audaz_empresa

- porcentaje_relleno: 67.35 · predictibilidad_estructural_pct: 60.56 · peso_relativo: 0.216276
- desglose_relleno_por_grupo_pct:
  - acoplamiento: 60
  - booker: 60
  - dynamis: 40
  - estructura: 100
  - frye: 33.3333
  - geometria_inercia: 90
  - greimas: 86.6667
  - otras_dimensiones: 95
  - puente_lateral: 32.4711
  - trayectoria_estado: 76

### Conjunto abierto (3 hipótesis, cardinalidad_fija: False)

- **H_001** 12_obtencion · rol: eje · rank_fusion: 28.2695 · soporte_estructural_relativo: 0.429189
  - trazabilidad_geometrica: régimen=CONTINUIDAD_ASCENDENTE · señal_multiescala=0.204722 · micro=0.58904 · meso=0.609021 · macro=0.609021 · aceleración=0.458496 · divergencia_entre_escala=0.019981 · n_cortes_observados=3
- **H_002** 9_audaz_empresa · rol: componente · rank_fusion: 26.7977 · soporte_estructural_relativo: 0.406845
  - trazabilidad_geometrica: régimen=CONTINUIDAD_ASCENDENTE · señal_multiescala=0.315317 · micro=0.649551 · meso=0.661712 · macro=0.661712 · aceleración=0.473093 · divergencia_entre_escala=0.012161 · n_cortes_observados=3
- **H_003** social_04_rogers_difusion_innovaciones · rol: componente · rank_fusion: 10.8 · soporte_estructural_relativo: 0.163966
  - trazabilidad_geometrica: régimen=CONTINUIDAD_ASCENDENTE · señal_multiescala=0.144329 · micro=0.499467 · meso=0.608513 · macro=0.608513 · aceleración=0.291853 · divergencia_entre_escala=0.109046 · n_cortes_observados=3

### Apuesta principal: CONTINUIDAD_ASCENDENTE (soporte_estructural_agregado: 1) · hipótesis que convergen: 12_obtencion, 9_audaz_empresa, social_04_rogers_difusion_innovaciones
- calibración: NO_CALIBRADA_SIN_DESENLACES_POSTERIORES_SELLADOS
- monte_carlo: status=None · total_simulations=None · converged=None/None · nonconverged=None
- predictive_validation: NOT_CALIBRATED_NO_CASE_LEVEL_OUTCOMES · hay una referencia histórica de acierto Top-1/Top-3 del predictor lateral, pero faltan scores y desenlaces sellados por caso para ajustar/calibrar una probabilidad del motor actual; no se sustituyen p

### Input en prosa (entrada.json)

- pregunta: ¿Qué trayectoria sigue William C. Durant tras haber recuperado la presidencia de General Motors en 1916 y lanzar una gran expansión de la empresa?
- person: William C. Durant · tipo_sujeto: empresario · freeze: 1920-06-30 · random_seed: 20261024
- corte C1_1908: fecha=1908-11-12 · hecho=Tomó el control de Buick el 1 de noviembre de 1904; el 16 de septiembre de 1908 fundó General Motors como sociedad de cartera y el 12 de noviembre de 1908 compró Olds Motor Works.
- corte C2_1911: fecha=1911-11-03 · hecho=Sobreendeudado tras sumar Cadillac, Oakland y otras compañías, perdió en 1910 el control de General Motors a manos de los banqueros; el 3 de noviembre de 1911 fundó Chevrolet con el piloto Louis Chevrolet.
- corte C3_1919: fecha=1919 · hecho=Apoyado en las ventas de Chevrolet recuperó en 1916 el control de General Motors; en febrero de 1918 se anunció el plan para que GM absorbiera Chevrolet, y en 1919 GM compró la Guardian Frigerator Company, en parte propiedad de Durant, rebautizada Frigidaire, y creó la financiera General Motors Acceptance Corporation.
