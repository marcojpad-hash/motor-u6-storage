# Reporte — Transición Histórica/Social Anonimizada #1 (corte Z90)

**Fecha:** 2026-11-13 ~02:13 CST
**Caso:** TRANSICION1_Z90_20261113
**Entrada:** `~/workspace/u6-alterno/motor-cameo/casos/precedentes/TRANSICION1_Z90_20261113/entrada.json`
**Resultado:** `~/workspace/u6-alterno/motor-cameo/motor/RESULT_TRANSICION1_Z90_20261113.json`
**Recibo:** COMPLETED, 72.632 s, exit 0
**Tipo:** colectivo (primera vez que se corre un fenómeno histórico/social y no una persona).

## Respuesta del motor (en palabras)

El motor lee a un **creador** que inventó algo nuevo y lo ve cayendo. Es la primera vez que el creador queda de H1. Tiene sentido: aquí el que crea no es una persona, es el colectivo que inventó los instrumentos, el mercado y la burbuja misma. El sabio queda segundo. El destino es **caída**, la primera caída en todos los ejercicios ciegos. Hasta ahora todos eran auge. Aquí el balance favorable-adverso se empeora, lo adverso domina y sube, y el eje se apaga. El balance del último tramo es negativo, el único negativo hasta ahora.

La apuesta principal es **meseta**: diez hipótesis contra cuatro. El motor ve el fenómeno atascado, en espera de que el tribunal decida. Pero el destino dice caída. Hay una tensión: por temas se queda, por balance cae.

## Lo que se encendió y lo que no (la pregunta de Marco)

Marco pidió ver si se encienden Minsky, Kondratiev, Tainter y contagio colectivo.

| Bloque | ¿Se encendió? | Dónde |
|---|---|---|
| **Tainter** | **Sí** | tainter_03_vulnerabilidad_sistemica es la primera familia de caída en Z (0.0818). |
| **Kondratiev** | **Sí** | kondratiev_04_invierno_recesion está en caída en Z (0.0311). |
| **Contagio colectivo** | **Sí** | social_04_rogers_difusion_innovaciones es #12 y la primera familia de auge en Z (0.1063); social_14_overton_ventana es #11. |
| **Minsky** | **No** | Las tres etapas existen en el catálogo (minsky_01_cobertura, minsky_02_especulativa, minsky_03_ponzi) pero **ninguna** está en el top 14 ni en las familias activas en Z. |

El hallazgo es Minsky. Este es el caso de manual de Minsky (cobertura → especulativa → Ponzi → colapso) y las tres etapas no se encendieron. Es el mismo patrón que con las sustancias: el bloque existe en el catálogo, pero no se activa. Probablemente es un problema de tokens: las familias Minsky necesitan tokens específicos que no estaban en la entrada. Habría que revisar qué tokens alimentan a minsky_01/02/03 y meterlos en la traducción, como se hizo con consumo_sustancias.

## H1 y H2

| Puesto | Familia | Grado | rank_fusion | Peso | Relleno |
|---|---|---|---|---|---|
| H1 | arquetipo_el_creador | AJUSTADA | 29.254985 | 0.077072 | 62.65% |
| H2 | arquetipo_el_sabio | AJUSTADA | 27.855961 | 0.073386 | 64.47% |

- Mezcla: H1_DOMINANTE. Margen H1–H2: 1.399024 (mayor que el umbral 1.0). Afinidad: 0.173367.
- Relleno H1 por grupo (%): geometría/inercia 86.11, greimas 85.19, puente lateral 84.01, otras 66.92, trayectoria/estado 61.67, estructura 52.78, frye 51.85, booker 49.07, acoplamiento 44.44, dynamis 44.44.
- Relleno H2 por grupo (%): estructura 100.0, dynamis 94.44, greimas 90.74, trayectoria/estado 82.78, otras 78.03, booker 62.96, geometría/inercia 58.33, puente lateral 36.67, frye 35.19, acoplamiento 5.56.

## Top 14 hipótesis (rank_fusion)

| # | Familia | rank_fusion | Régimen |
|---|---|---|---|
| 1 | arquetipo_el_creador | 29.254985 | MESETA_O_ESTABILIZACION |
| 2 | arquetipo_el_sabio | 27.855961 | CONTINUIDAD_ASCENDENTE |
| 3 | berlin_01_erizo | 25.335662 | CONTINUIDAD_ASCENDENTE |
| 4 | utopia_mentalidad_liberal | 24.294805 | MESETA_O_ESTABILIZACION |
| 5 | 20_sacrificio_por_un_ideal | 23.413495 | CONTINUIDAD_ASCENDENTE |
| 6 | dumezil_f2_fuerza | 21.681657 | MESETA_O_ESTABILIZACION |
| 7 | bbk_01_aventurero | 21.559608 | MESETA_O_ESTABILIZACION |
| 8 | 9_audaz_empresa | 20.475472 | MESETA_O_ESTABILIZACION |
| 9 | kwml_01_rey | 19.277778 | MESETA_O_ESTABILIZACION |
| 10 | distopia_agotamiento_ambiental | 18.805556 | CONTINUIDAD_ASCENDENTE |
| 11 | social_14_overton_ventana | 16.820044 | MESETA_O_ESTABILIZACION |
| 12 | social_04_rogers_difusion_innovaciones | 16.18 | MESETA_O_ESTABILIZACION |
| 13 | turner_01_fase_liminal | 15.861111 | MESETA_O_ESTABILIZACION |
| 14 | arquetipo_el_gobernante | 15.601326 | MESETA_O_ESTABILIZACION |

## Apuesta (multiescenario)

- **Apuesta principal: MESETA_O_ESTABILIZACION** — 10 hipótesis (creador, mentalidad_liberal, dumezil_f2_fuerza, bbk_01_aventurero, 9_audaz_empresa, kwml_01_rey, social_14_overton, social_04_rogers, turner_01_fase_liminal, gobernante), soporte 0.6781206.
- **CONTINUIDAD_ASCENDENTE** — 4 hipótesis (sabio, erizo, 20_sacrificio, distopia_agotamiento_ambiental), soporte 0.32187941.
- Estado: APUESTA_MULTIESCENARIO_SELLABLE. Calibración: NO_CALIBRADA_SIN_DESENLACES_POSTERIORES_SELLADOS.

## Destino personal

- **Veredicto: caída** — "el balance favorable-adverso empeora / lo adverso domina y sube / el eje del sujeto se apaga". Primera caída en los ejercicios ciegos.
- Serie favorable (auge) por corte: [0.0763, 0.1753, 0.2035, 0.2242, 0.2973, 0.392, 0.4586] — sube.
- Serie adverso total por corte: [0.0332, 0.1288, 0.1978, 0.1879, 0.3336, 0.3948, 0.4654] — sube y **rebasa a lo favorable en Z** (0.4654 contra 0.4586).
- Serie adverso caída: [0.0332, 0.0706, 0.1006, 0.0956, 0.129, 0.1335, 0.186].
- Serie adverso ruptura: [0.0, 0.0582, 0.0972, 0.0923, 0.2046, 0.2613, 0.2794] — sube fuerte, llega a 0.2794 en Z, la ruptura más alta de todos los ejercicios ciegos.
- Señales: balance último tramo **−0.004 (negativo, el único negativo hasta ahora)**; salto ruptura 0.0181; salto adverso 0.0706; eje creador; caída del eje vs máximo previo 0.0.

## Familias activas en Z

- **Ruptura:** 6_desastre (0.0979), predictivo_01_markov_estado_absorbente (0.0931), eterno_retorno_01_caos_primordial (0.0884).
- **Caída:** tainter_03_vulnerabilidad_sistemica (0.0818), 7_caer_victima (0.0485), kondratiev_04_invierno_recesion (0.0311), sistema_domiciano_maiestas (0.0246).
- **Auge:** social_04_rogers (0.1063), 9_audaz_empresa (0.0952), monomito_12_regreso_con_el_elixir (0.0933), eterno_retorno_02_cosmizacion (0.0933), jaldun_01_asabiyyah (0.0705).

## Matrices nuevas que emergieron

- **dumezil_f2_fuerza** — #6. La segunda función de Dumézil (la fuerza, el guerrero). Nueva.
- **bbk_01_aventurero** — #7. El aventurero. Nueva.
- **distopia_agotamiento_ambiental** — #10. Distopía de agotamiento. Captura el agotamiento del sistema. Nueva.
- **turner_01_fase_liminal** — #13. La fase liminal de Turner (el umbral, el estar entre dos estados). Cuadra con los tribunales colapsados y la comisión que decide. Nueva.
- **social_14_overton_ventana** — #11. Otra vez (estaba en Elvis). La ventana de lo tolerable.
- **social_04_rogers_difusion_innovaciones** — #12 y primera de auge en Z. La difusión/contagio.

## La entrada (para repetir la corrida)

- case_id: TRANSICION1_Z90_20261113. Persona: "Transición anónima". Tipo: colectivo. 7 cortes, sin región, sin siglo y sin nombres de productos (fechas neutras 1401–1448). Freeze 1451-01-01. z_work_date C7_1448. Semilla 20261113. P/A/C como listas de pares.
- C1_1401 (expansión): potencia marítima y mercantil, rutas comerciales de larga distancia, monopolios privados respaldados por el Estado, entrada sostenida de capitales, excedente de liquidez sin precedentes. P: logro_personal 0.78, reconocimiento 0.76, oportunidad 0.74, conocimiento 0.70, independencia 0.68. A: autoridad 0.68, jerarquia 0.64. C: oportunidad 0.72, estabilidad 0.70, busqueda_identidad 0.66, estatus_social 0.62.
- C2_1411 (mentalidad e innovación): éxito rápido desplaza austeridad, mercados financieros abiertos a cualquier ciudadano con ahorros mínimos, crédito flexible, contratos a futuro, compra con pago diferido pagando una fracción. P: aprendizaje 0.78, creatividad 0.76, audacia 0.74, conocimiento 0.72, independencia 0.70. A: resistencia_cambio 0.70, reflexion 0.68, claridad 0.66. C: oportunidad 0.72, estabilidad 0.70, restriccion_iniciativa 0.68, incertidumbre 0.66.
- C3_1420 (especulación): bien de lujo por rareza estética y prestigio, contratos sobre cosechas futuras inexistentes, precio desconectado de costo/utilidad, hipotecar propiedades/talleres/tierras/herramientas para financiar contratos en cadena. P: audacia 0.80, independencia 0.78, logro_personal 0.76, reconocimiento 0.74, creatividad 0.72. A: liderazgo 0.70, vision 0.68, reflexion 0.66. C: crisis_abrupta 0.72, deuda 0.70, incertidumbre 0.68, estabilidad 0.66.
- C4_1425 (contagio): narrativa de enriquecimiento sin esfuerzo por tabernas/gremios/plazas, prudentes vistos como rezagados, entrada masiva retroalimenta subida exponencial. P: logro_personal 0.78, reconocimiento 0.76, audacia 0.74, creatividad 0.72, independencia 0.70. A: reflexion 0.70, vision 0.68, claridad 0.66. C: oportunidad 0.72, reconocimiento 0.70, crisis_abrupta 0.68, estabilidad 0.66.
- C5_1430 (euforia máxima): un contrato por varias veces el ingreso anual de un trabajador especializado, intermediarios sin respaldo, autoridades al tanto pero sin intervenir (miedo al pánico / perder ingresos fiscales), flujo de compradores nuevos desacelera, vencimientos de deuda a corto plazo sobre base estrecha de capital real. P: audacia 0.80, logro_personal 0.78, reconocimiento 0.76, independencia 0.74, proposito_claro 0.72. A: resistencia_cambio 0.70, reflexion 0.68, claridad 0.66. C: crisis_abrupta 0.72, deuda 0.70, ruina 0.68, incertidumbre 0.66.
- C6_1438 (pánico): subasta ordinaria, oferta clave sin compradores, noticia en horas, liquidación simultánea, contratos caen más de 90% en días, deudores atrapados, cadena de incumplimientos cruzados, crédito cotidiano congelado. P: sacrificio 0.78, reflexion 0.76, proposito_claro 0.74, independencia 0.72, audacia 0.70. A: reflexion 0.70, vision 0.68, claridad 0.66. C: crisis_abrupta 0.72, ruina 0.70, deuda 0.68, amenaza_central 0.66.
- C7_1448 (conflicto legal): vendedores exigen cumplimiento forzoso, compradores alegan contratos nulos por apuestas/manipulación, panfletos y sermones condenan codicia y señalan especuladores, tribunales colapsados por miles de demandas, gobierno suspende cobros mientras comisión decide anular o convertir en multas parciales. P: sacrificio 0.78, reflexion 0.76, proposito_claro 0.74, independencia 0.72, creatividad 0.70. A: reflexion 0.70, vision 0.68, claridad 0.66. C: amenaza_central 0.72, injusticia 0.70, crisis_abrupta 0.68, ruina 0.66.

## Hashes

- Entrada: 3be38f04a05112194f3788f646f52799f9da54db6112b9afa18e081f6e515ca8
- Salida: cb7ac346a28d7d3d0c8596566656a30aa398f9a4f284e7803c1a2d63f99b1c77
- Engine: 665c39a2861e58772522e91272563260d980908b1d4ab9f7092d3413d0c36082
- Catálogo: d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1
- Hash de control de Marco (sellado): 9f2e4b8a1c6d3075e8a2f4c9b1d70365a8e2c4f9b1d60375e9a2c4f8b1d70364

## Nota

- Sin NameError: la corrida terminó limpia (exit 0, recibo COMPLETED).
- Monte Carlo: 21 observaciones, 12,875 simulaciones, todas convergieron.
- El trono no se activa: gobernante último (#14), rey #9.
