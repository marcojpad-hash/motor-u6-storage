# Cosecha del StinkBox — lateral (NO va al catálogo 244)

Orden de Marco (2026-11-13 ~03:50 CST): el StinkBox está diseñado para
acumular casos y que, al ejecutarlos, se activen tokens y familias que no
habíamos visto. Lo que faltaba era el regreso: que lo juntado se meta
como material sin que nadie tenga que buscarlo token por token. Esta
cosecha es ese regreso.

## Qué hace

`cosecha.py` lee el índice de casos resueltos
(`STINKBOX_STORAGE/resolved_cases_index.json`, 160 entradas) y los RESULT
disponibles en `motor/`, y escribe la propuesta
`COSECHA_YYYYMMDD.json` con cada candidato y su evidencia (caso, lugar,
rank_fusion, valor, contexto). Por caso cosecha:

- **familia_top15**: las hipótesis del conjunto abierto
  (`salida_interpretable.conjunto_hipotesis_abiertas`), con lugar,
  rank_fusion y regimen de trazabilidad. El motor no siempre deja 15
  abiertas: trae 13–23 por caso (la Revolución dejó 23).
- **familia_en_Z**: las familias activas en Z
  (`apuesta_destino_personal.familias_activas_en_Z`: auge / caída /
  ruptura, con su valor). Una familia que es top-15 Y está en Z sale una
  sola vez (como top-15, con la evidencia en Z guardada).
- **token_sin_familia**: tokens de la entrada (P/A/C de todos los cortes)
  que NO están en los 703 del catálogo. Un token sin familia es inerte
  (vector cero): el motor no lo puede prender. Son los candidatos nuevos
  de verdad.
- **token_delta_version**: tokens que entraron en una versión _v2 (o _vN)
  y no estaban en la _v1 del mismo caso.

## Qué encontró (corrida 2026-11-13, COSECHA_20261113.json, 467 KB)

99 casos cosechados (unión de índice, RESULT y entradas). 1,249
candidatos: 692 familias del conjunto, 538 en Z, 13 tokens sin familia
y 6 tokens delta.

Tokens sin familia (4 distintos, 13 apariciones): **arte, deuda,
enfermedad** (Rembrandt, Elvis v1/v2, Tulipán v1/v2) y **riesgo**
(Tubman). Tokens delta (6): **consumo_sustancias** (Elvis v2) y los 5
de Minsky en Tulipán v2 (busqueda_riesgo, cautela, codicia,
negacion_problema, optimismo).

18 casos del índice no tienen RESULT todavía (entre ellos los 10 de
F005, que no se ha corrido) y 28 no tienen entrada en la copia de
trabajo. Quedan anotados en el JSON, no se inventa nada por ellos.

## Puerta

`puerta.py` — **PASA** (2026-11-13). G1: catálogo 244/703, índice 160
entradas, manual 13. G2: reproduce los 13 descubrimientos del archivo
manual (`STINKBOX_PERSISTENTE/tokens_descubiertos_ciegos_z90_20261113.json`,
mismos casos, mismas familias, mismo lugar, mismo rank_fusion y mismo
regimen; para las de Z, mismo valor). G3: encuentra los de los 4 casos
que faltaban en el manual (Tulipán v1/v2, Revolución, Che), con los
top-1 conocidos (Tulipán v1: creador 29.25; Revolución: tainter_01
30.89; Che: gobernante 35.22).

Detalle: el regimen del RESULT trae `MESeta_O_ESTABILIZACION` (caja
mezclada del motor); el manual lo normalizó a `MESETA_O_ESTABILIZACION`.
La puerta compara sin caja. La cosecha guarda el valor crudo del RESULT.

## Qué NO hace

- No toca el Engine (MOTOR_V15_3_UNICO) ni el catálogo 244: solo lee.
- No decide H (`can_decide_H = False`) y no activa nada. La propuesta
  es material de lateral, como las 10 familias geopolíticas: Marco
  decide cuáles candidatos se activan como análogos.
- No reescribe el archivo manual: lo usa solo como referencia de la
  puerta. La cosecha nueva vive en `COSECHA_YYYYMMDD.json` y se vuelve
  a correr cuando crezca el StinkBox.

## Cómo se corre

```bash
cd ~/workspace/u6-alterno/motor-cameo
python3 motor/laterales/cosecha_stinkbox/cosecha.py [--fecha YYYYMMDD]
python3 motor/laterales/cosecha_stinkbox/puerta.py   # PUERTA PASA / RECHAZADA
```
