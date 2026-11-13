# Ablación sustancias_03_severo — Elvis v1 (ANONIMO3_Z90)

Fecha: 2026-11-13 ~03:40 CST. Pedida por Claude (auditor del motor).
Recibo ablación: COMPLETED (62.9 s, returncode 0).

## Lo que se quitó

Del catálogo (`patterns_final_v14.json`), la familia `sustancias_03_severo`
tiene solo 4 tokens favor: `consumo_sustancias` 0.85, `cronicidad_sintomatica`
0.8, `estancamiento_crisis` 0.7, `aislamiento_social` 0.65.

En la entrada de Elvis v1 solo había UNO de los cuatro: `aislamiento_social`
(2 veces, eje C, peso 0.72: C6_1938 y C7_1948). No había `consumo_sustancias`,
ni `cronicidad_sintomatica`, ni `estancamiento_crisis`.

Variante: `casos/precedentes/ANONIMO3_Z90_ABLACION_20261113/entrada.json`
(case_id `ANONIMO3_Z90_ABLACION_20261113`). Solo se quitaron esos 2 pares;
todo lo demás idéntico (freeze, pregunta, fechas, resto de tokens).

## Resultado

| | Original (Elvis v1) | Ablación |
|---|---|---|
| sustancias_03_severo | **#7, rank_fusion 23.40** | **fuera del top 15** (el #15 es 17.07; cayó ≥6.3 puntos y ≥9 puestos) |
| H1 | 20_sacrificio_por_un_ideal 28.16 | arquetipo_el_sabio 27.84 |
| H2 | arquetipo_el_sabio 27.56 | 20_sacrificio_por_un_ideal 27.89 |
| Grado | FRÁGIL | FRÁGIL |
| Apuesta | MESETA 0.733 (10 hip.) | MESETA 0.805 (10 hip.) |

Mecanismo visible en el tablero: el valor C de sustancias_03 en C6/C7 era
0.6247 y 0.724 en el original (empujado por `aislamiento_social`) y quedó
en 0.5 plano en la ablación. El token era el único motor de la familia en
la entrada.

El cambio H1/H2 es un trueque dentro de la banda de indistinguibilidad
(diferencia 0.049 < 0.25): no es un cambio real. El resto del top apenas se
movió (todos dentro de ~1–2 puntos, salvo erizo 27.56 → 25.56 y gobernante
15.42 → 18.93). La apuesta siguió en MESETA.

## Corrección a los tokens que citó Claude

Claude dio como causa `crisis_abrupta`, `miedo` y `sacrificio`. Eso no
se sostiene en el catálogo:
- `crisis_abrupta` está 5 veces en la entrada y SE QUEDÓ en la ablación
  (0.68 en C6/C7), y sustancias_03 colapsó igual. Además no es favor de
  NINGUNA familia del 244: como motor directo es inerte.
- `miedo` NO está en la entrada de Elvis v1. No puede ser la causa aquí.
- `sacrificio` está 2 veces, se quedó, y es favor de 9 familias
  (20_sacrificio, heroe, cuidador…) pero NO de sustancias_03.

La causa real es la que ya estaba en el HALLAZGOS: los tokens generales
de disparo (`aislamiento_social` aquí). La lista de Claude estaba mal;
la hipótesis de fondo (falso positivo por tokens generales) queda probada.

## ¿Se generaliza? (sin correr, solo leyendo entradas)

En los otros tres casos donde sustancias_03 sale alto sin consumo real,
los únicos favor presentes son también los generales, nunca
`consumo_sustancias`:
- Rembrandt: `aislamiento_social` ×3.
- Revolución: `estancamiento_crisis` ×3.
- Che: `estancamiento_crisis` ×3 + `aislamiento_social` ×4.

Eso hace probable el mismo mecanismo, pero la prueba ejecutada es solo
la de Elvis v1. Para llamarlo "estructural" faltan las ablaciones de
esos tres casos.

## Caveat

Entre la corrida original y la ablación el StinkBox creció
(n_casos_resueltos_sellados 25 → 158 en el RESULT de la ablación), así
que el ambiente no era idéntico. El efecto igual es grande y el
mecanismo (C 0.62/0.72 → 0.5 plano) es directo, no de ambiente.

## Reproducción

- Entrada original: `casos/precedentes/ANONIMO3_Z90_20261113/entrada.json`
- Entrada ablación: `casos/precedentes/ANONIMO3_Z90_ABLACION_20261113/entrada.json`
- RESULT ablación: `motor/RESULT_ANONIMO3_Z90_ABLACION_20261113.json`
- Recibo: `motor/RESULT_ANONIMO3_Z90_ABLACION_20261113_RECIBO_EJECUCION.json` (COMPLETED)
- RESULT original: `motor/RESULT_ANONIMO3_Z90_20261113.json`
- Corredor: `STINKBOX_HOME=$PWD/STINKBOX_PERSISTENTE STINKBOX_STORAGE_ROOT=$PWD/STINKBOX_STORAGE python3 motor/correr_estandar.py casos/precedentes/ANONIMO3_Z90_ABLACION_20261113/entrada.json ANONIMO3_Z90_ABLACION_20261113`
- engine_sha 665c39a2861e, patterns_sha d827dcc38826, input_sha ablación 1e35234114e2.

## Veredicto

La causa queda probada para Elvis v1: sustancias_03_severo subía solo por
`aislamiento_social`, un token general, sin ningún consumo real en la
entrada; quitado ese token la familia se cae del top 15.
