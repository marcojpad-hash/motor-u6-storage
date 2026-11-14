# ¿Es real la constante del Sol ~0.79-0.80? — 2026-11-13

## Pregunta (Marco)
El dato es muy bueno. Si es que es real. ¿El peso del Sol ~0.79-0.80 es una
constante real o un artefacto?

## Verificación: peso de H1 en Z en 55 casos
Se corrió la lectura de gravedad en 55 RESULT del archivo (F001-F004, ciegos,
transiciones, héroes, Napoleón, Mozart, Bolívar, Curie, Churchill) y se midió
el peso de H1 en el último corte (P_FULL_244, salida del Engine, sin tope
forzado a 0.8 en el código).

| Grupo | n | Media | Mediana | Min | Max | En 0.77-0.82 | <0.75 | =0.5 |
|-------|---|-------|---------|-----|-----|--------------|-------|------|
| En meseta | 23 | 0.759 | 0.781 | 0.500 | 0.816 | 15/23 (65%) | 7/23 | 1/23 |
| No meseta | 32 | 0.735 | 0.748 | 0.500 | 0.815 | 14/32 (44%) | 16/32 | 2/32 |
| Todos | 55 | 0.745 | 0.772 | 0.500 | 0.816 | 29/55 (53%) | 23/55 | 3/55 |

## Veredicto: REAL pero CONDICIONAL, no universal
- SÍ es real: en las biografías fuertes y completas que estabilizan en meseta
  (Napoleón 0.781, Mozart 0.799, Transición1 0.801, Mandela 0.801, Bolívar
  0.816, Kolbe 0.801, Semmelweis 0.786-0.801, Tubman 0.772-0.786), el Sol se
  asienta en ~0.77-0.82. No hay tope forzado en el código: es la salida del
  Engine para una familia fuertemente apoyada.
- NO es universal: en ~35% de los casos en meseta y ~47% de todos, H1 queda
  en 0.5-0.75 (Bach 0.5, Coolidge 0.5, Trotsky 0.5, Pasteur 0.647, Mendel
  0.671, Turing 0.701, Faraday 0.697). Ahí H1 está débilmente apoyado y el
  Sol no llega a 0.79.
- Por eso la lectura predictiva (proyección hacia el Sol en ~0.79) vale para
  biografías fuertes y completas, no para todos los casos. La constante es
  una propiedad de los casos fuertes, no una ley del motor.

## Archivo
- `motor/VERIF_PESO_SOL_MUCHOS_CASOS_20261113.json` (los 55 casos).
