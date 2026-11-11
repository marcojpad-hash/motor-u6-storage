# Ejercicios Z90 — 11 de noviembre de 2026

Generado 2026-11-11T03:28:28.052173-06:00 (America/Mexico_City). Rama `alterno/cameo-pesos`; base `3cf21d59e65f77d65e71e627fc2c0cd188c1442b`.

**Resultado global: FALLO de calibración conforme; cinco ejecuciones diagnósticas con recibo COMPLETED, exit 0, MC EXECUTED y ledger preservado. No se presenta ningún fallo ni atajo como OK.**

Sí existe movimiento geométrico y de familias en los cinco inputs. Esto no demuestra capacidad predictiva, ni prueba que tres cortes fueran la única causa de las corridas antiguas. No se tocaron ni se usaron F001–F007.

## Tabla de salidas selladas

| Caso | Pre / apartados >Z | Z90 / último cierre pre | H1 | H2 | Apuesta temática principal | Destino 022 | GRANDE | dX_norm min–max |
|---|---:|---|---|---|---|---|---:|---|
| [CHE](CHE/VALIDACION.json) | 9 / 0 | 1963-11-03 / 1963-11-03 | dumezil_f2_fuerza | monomito_02_llamado_a_la_aventura | MESeta_O_ESTABILIZACION | auge | 0.0676 | 0.4994–1.1101 |
| [GALILEO_20260924](GALILEO_20260924/VALIDACION.json) | 10 / 0 | 1634-03-26 / 1634-03-25 | arquetipo_el_creador | utopia_mentalidad_liberal | MESeta_O_ESTABILIZACION | auge | 0.0755 | 0.2405–0.6934 |
| [HAWKING](HAWKING/VALIDACION.json) | 6 / 1 | 2010-08-01 / 2000-12-31 | arquetipo_el_sabio | mentor | MESeta_O_ESTABILIZACION | meseta | 0.05 | 0.3020–0.6243 |
| [MLK](MLK/VALIDACION.json) | 8 / 0 | 1964-05-03 / 1964-05-03 | eterno_retorno_02_cosmizacion_fundacion | 24_rivalidad_de_superior_e_inferior | MESeta_O_ESTABILIZACION | caida | 0.0592 | 0.5309–1.0114 |
| [MOZART_ORIGINAL_20260915](MOZART_ORIGINAL_20260915/VALIDACION.json) | 7 / 3 | 1788-05-04 / 1788-05-04 | schwartz_10_autodireccion | 30_ambicion | MESeta_O_ESTABILIZACION | caida | 0.0548 | 0.3916–0.4913 |

Todas las apuestas temáticas principales siguen siendo `MESeta_O_ESTABILIZACION`, aunque las series sí cambian. **Más cortes no bastaron para diversificar esa salida.**

## Cotejo con el desenlace (cualitativo, no probabilidad de acierto)

Los rótulos siguientes son compatibilidad temática retrospectiva. No había criterios observables pre-registrados, y se conocen las biografías: **no es doble ciego ni una tasa de acierto validada**. La columna de destino distingue la actividad/posición del sujeto del mero hecho de morir. Los fallos de protocolo invalidan cualquier uso como calibración certificada.

| Caso | H1 | H2 | Apuesta temática | Destino 022 | Origen de validación |
|---|---|---|---|---|---|
| CHE | HIT | PARCIAL | MISS | MISS | fuente pública posterior al sello |
| GALILEO_20260924 | HIT | PARCIAL | PARCIAL | MISS | fuente pública posterior al sello |
| HAWKING | HIT | HIT | PARCIAL | PARCIAL | fuente pública posterior al sello |
| MLK | PARCIAL | HIT | PARCIAL | PARCIAL | fuente pública posterior al sello |
| MOZART_ORIGINAL_20260915 | HIT | HIT | PARCIAL | PARCIAL | C8–C10 originales; T1 produjo HIT_HIPOTESIS_SET pero terminó en error |

Los motivos y fuentes están en cada `VALIDACION.json` y, cuando corresponde, `DESENLACE_PUBLICO_POST_SELLO.json`. El T1 mecánico compara un set amplio; su HIT no predice una muerte, una obra ni una fecha concreta. No se inventaron tokens para los desenlaces públicos.

## Movimiento observado

Cada carpeta incluye una gráfica estática `MOVIMIENTO_H1_H2.svg`. Sus escalas Y se adaptan al caso; el gráfico es descriptivo, no probabilidad.

### CHE
- H1 activación por corte: `[0.0, 0.0385, 0.0365, 0.0442, 0.1358, 0.2069, 0.2091, 0.2001, 0.2239]`.
- H2 activación por corte: `[0.0, 0.0861, 0.0817, 0.0789, 0.1701, 0.1601, 0.1516, 0.1441, 0.1728]`.
- Familias no constantes: 116; persist_cos -0.0535…0.0782; kappa_dir 0.9969…1.0000.
- Series completas de R732, H1/H2 y polos 022: [CHE/MOVIMIENTO.json](CHE/MOVIMIENTO.json).

### GALILEO_20260924
- H1 activación por corte: `[0.0, 0.1452, 0.2606, 0.2829, 0.2829, 0.2827, 0.2829, 0.2823, 0.2823, 0.2822]`.
- H2 activación por corte: `[0.0389, 0.1245, 0.1888, 0.2155, 0.2234, 0.2304, 0.237, 0.2424, 0.2478, 0.2525]`.
- Familias no constantes: 39; persist_cos 0.1776…0.7625; kappa_dir 0.6469…0.9841.
- Series completas de R732, H1/H2 y polos 022: [GALILEO_20260924/MOVIMIENTO.json](GALILEO_20260924/MOVIMIENTO.json).

### HAWKING
- H1 activación por corte: `[0.0188, 0.0543, 0.053, 0.0805, 0.0758, 0.085]`.
- H2 activación por corte: `[0.0, 0.0, 0.0, 0.0, 0.048, 0.1]`.
- Familias no constantes: 86; persist_cos 0.0665…0.2777; kappa_dir 0.9607…0.9978.
- Series completas de R732, H1/H2 y polos 022: [HAWKING/MOVIMIENTO.json](HAWKING/MOVIMIENTO.json).

### MLK
- H1 activación por corte: `[0.0, 0.0388, 0.0362, 0.1344, 0.1272, 0.1212, 0.1328, 0.1582]`.
- H2 activación por corte: `[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.098]`.
- Familias no constantes: 100; persist_cos -0.0938…0.0061; kappa_dir 0.9956…1.0000.
- Series completas de R732, H1/H2 y polos 022: [MLK/MOVIMIENTO.json](MLK/MOVIMIENTO.json).

### MOZART_ORIGINAL_20260915
- H1 activación por corte: `[0.0273, 0.0536, 0.0723, 0.0828, 0.0959, 0.0969, 0.1035]`.
- H2 activación por corte: `[0.0, 0.0359, 0.0663, 0.1651, 0.1557, 0.1909, 0.1951]`.
- Familias no constantes: 55; persist_cos -0.1252…0.6026; kappa_dir 0.7980…0.9998.
- Series completas de R732, H1/H2 y polos 022: [MOZART_ORIGINAL_20260915/MOVIMIENTO.json](MOZART_ORIGINAL_20260915/MOVIMIENTO.json).

## Fallos y límites que no se ocultaron

1. **Inventario demasiado permisivo:** `CONFORME` significaba Z a ±6 meses y ≥5 cortes; no certifica el protocolo estricto actual. No se corrigió ni reescribió el inventario antiguo.
2. **Hawking:** su C7 dice 2010–2011, cruza Z90=2010-08-01 y se selló entero fuera del input. Quedan 6 cortes hasta 2000-12-31: NO es corrida completa de Hawking hasta Z90. No se recortaron hechos para forzar conformidad.
3. **Galileo:** Z90 al redondear al día más próximo es 1634-03-26; la fecha original del último corte es 1634-03-25. Se conservó, no se desplazó un hecho para cerrar el hueco. Usar el día truncado del 90% daría 25: la convención de redondeo necesita fijarse explícitamente.
4. **Fechas reconstruidas:** Mozart/Che/MLK/Hawking no traen date en sus listas de cortes. Se derivaron del período descrito y markers, sin cambiar hechos ni pares token-peso. Che C3=1952 va antes de C2=1953. MLK C5/C6 se dataron por el mes de los sucesos y C7/C8 en el límite del marker. Son fechas de adaptación documentadas, no mediciones nuevas. Hay intervalos 1940s y primavera sin día exacto.
5. **Acumulación no acreditada:** los originales describen etapas; no prueban que cada corte recodifique acumulativamente todo lo previo desde nacimiento. No se duplicaron ni agregaron tokens para simularlo.
6. **Gate:** `correr_estandar.py` no llama `calibracion/gate_z90.py`. La validación nativa rechaza corte >z90_date, pero acepta birth/death ausentes, z90_date ausente y date del corte ausente (pruebas sobre su función real `_validate_case`, sin ejecutar Engine). El gate externo rechaza los cinco por evidencia documental ausente; Hawking además por “mas tarde”. No se fabricaron fuentes ni preparación ciega. Las ejecuciones son diagnósticas; NO gate-PASS. Ver `PRUEBAS_GATE.json`.
7. **Sombrero blanco:** filtro 017 quedó en su modo vigente por defecto `traza`: detectó banderas pero aplicó 0 neutralizaciones. Las consultas externas fueron por tokens, pero el corte temporal leniente conservó 8 fuentes sin fecha por caso. No queda acreditada la garantía de no-futuro de esas fuentes. No se afirma contaminación concreta del desenlace del sujeto; se registra la falta de garantía.
8. **CEB:** en los cinco: `VERIFIED_FLOW_WITH_ANOMALIES`, anomalía `REPORTED_EXECUTED_NOT_OBSERVED` para `geometria_multicapa_integrada_working_v1`. Un recibo COMPLETED no convierte esto en PASS. Consultar `AUDITORIA_COMPONENTES.json` y ledger.
9. **T1 Mozart:** se escribió score `HIT_HIPOTESIS_SET`, y H1/H2 aparecen en sus candidatas predictivas; después el runner falla con `KeyError: H1_sellada` (línea 572), exit 1. Se conservó score, traceback y ledger T1; no se reintentó ni parcheó. El sello primario no cambió.
10. **Escala:** rank_fusion sigue siendo suma cruda >0.999: `FALLO_ESCALA`, sin renormalización inventada. Geometría (normas/cosenos/curvatura), porcentajes de relleno y sumas de polos no son probabilidades.
11. **Tokens:** los cinco originales completos, incluidos los apartados, usan exclusivamente tokens exactos del vocabulario canónico de 703; 0 FALLO_TOKEN. Todos los pares están en 0.60–0.84 y se conservaron sin cambios.
12. **022 GRANDE no es fijo:** hereda `max(0.05, percentil 95 de |Δ|>0.001 de familias del caso)` de `movimiento_de_fondo.py`; por eso varía entre 0.05 y 0.0755 aquí. El 0.0624 del documento no es una constante efectiva universal. No se ajustó ningún umbral.

## Reproducibilidad y evidencias

- Por caso: `entrada.json`, `futuro_sellado.json`, `futuro_sellado.sha256`, `PREPARACION_Y_SELLO.json` (hash y registro anterior a la corrida), `run.log`, `EJECUCION_PROCESO.json`, `result_RECIBO_EJECUCION.json`, `result.json.gz`, ledger `.jsonl.gz`, manifiesto CEB, `SELLO_RESULTADO.json`, `MOVIMIENTO.json`, `GATE_Z90.json`, `AUDITORIA_COMPONENTES.json`, `VALIDACION.json`.
- SHA256SUMS y `MANIFIESTO_ARTEFACTOS.json` guardan las huellas comprimidas y de contenido descomprimido; las de recibos originales se verifican sobre ese contenido, sin editar recibo ni resultado.
- Mozart procede exclusivamente del original sha256 `a86ab3e48c235e2d50d9da4cde305ae3eb2b2b105f5122e71ad24443d9b44858`. No se usó `casos/precedentes/MOZART_10_CORTES/INPUT_FROZEN.json`.
- Engine y 244 se verificaron antes/después, intactos: `665c39a2861e58772522e91272563260d980908b1d4ab9f7092d3413d0c36082` y `d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1`.
- Cada caso tuvo StinkBox y CEB separados; T1 tuvo StinkBox aparte. No se compartieron validaciones post-Z como memoria de otra corrida.
- Los comandos exactos, fechas locales y entorno están en los recibos de proceso. Para reproducir, descomprimir `result.json.gz` antes de `--t1`, sin alterar contenido.
- No se cambió código del motor, Engine, catálogo ni lotes viejos. No PR, merge ni comentarios. La publicación remota queda pendiente de autorización explícita del usuario; este paquete se prepara como cambio local reversible.
