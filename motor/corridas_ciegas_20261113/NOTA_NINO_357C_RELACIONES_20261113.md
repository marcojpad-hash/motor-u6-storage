# Niños 3C vs 5C vs 7C — todas las relaciones

**Fecha:** 2026-11-14 ~02:40 CST
**Orden de Marco (2026-11-13 ~22:02 CST):** «Mídelo para encontrar todas las relaciones.»
**Datos:** 13 genios de niño, cada uno corrido con 3, 5 y 7 cortes (39 RESULTs).
Tabla: `motor/TABLA_NINO_357C_20261113.json`.
Método: H1/H2/grado del RESULT; meseta y gravedad con lateral v3 (`leer_resultado`);
giro con sonda v1 (PCA 2 componentes sobre P_FULL_244, ángulo total barrido).

## 1. El Sol NO se fija temprano, ni en niños ni en adultos

| Comparación | Iguales |
|---|---|
| H1 3C → 5C | 4/13 |
| H1 5C → 7C | 3/13 |
| H1 3C → 7C | 3/13 (solo Alkan estable en los tres; Chopin y Pascal vuelven al H1 de 3C) |

En adultos pasaba lo mismo (H1 cambió del corte 3 al 7 en 6 de 7). El Sol no se fija
con 3 cortes ni con 5. Se fija (si se fija) con 7.

## 2. El H1 temprano no desaparece: baja a H2

- H1 de 3C = H2 de 7C en 5 casos: Mendelssohn, Menuhin, Bellini, Sidis, Kripke.
- H1 de 3C sigue en el top 2 a 7C (como H1 o H2) en **8/13**.
- H1 de 5C sigue en el top 2 a 7C en 5/13.

Esto encaja con la idea original de Marco: H2 no es la rival que perdió, es un
segundo vector más adelante. El tema de la infancia no se borra: pasa a segundo
plano y queda como H2. En adultos esto pasa menos (2/7: Tesla se queda como H1,
Lincoln baja a H2); en niños el tema temprano sobrevive más.

## 3. La meseta necesita 5 cortes como mínimo, y usualmente 7

| Cortes | En meseta |
|---|---|
| 3C | **0/13** (nadie) |
| 5C | 6/13 (Liszt, Menuhin, Bellini, Purcell, Sidis, Mozart) |
| 7C | 10/13 |

Los 4 que ganan la meseta entre 5C y 7C: Alkan, Pascal, Kripke, Picasso.
Los 3 que nunca llegan: Paganini, Mendelssohn, Chopin (CONTINUIDAD_ASCENDENTE).
**Sin 5 cortes no hay meseta; sin meseta no hay lectura de gravedad.**

## 4. El giro solo se asienta con 7 cortes

| Cortes | Giro medio | Rango | En banda 217–252° |
|---|---|---|---|
| 3C | 209.2° | 198.3–218.5 | 1/13 (12/13 por debajo de 217) |
| 5C | 234.9° | 205.3–307.6 | 6/13 (7 fuera; Menuhin 283.6°, Mozart 307.6°) |
| 7C | 233.8° | 214.4–266.3 | 10/13 |

La media a 5C (234.9°) ya es igual a la de 7C (233.8°), pero la dispersión a 5C
es enorme (outliers hasta 307°). A 3C el giro es sistemáticamente bajo (~209°).
**La banda 217–252° solo vale con 7+ cortes.** Con 3 cortes el giro no sirve;
con 5, la media sirve pero el caso individual no.

## 5. El peso del Sol a 5C todavía no está en la constante

Sol (peso Z) en los 6 en meseta a 5C y a 7C:

| Caso | 5C | 7C | Delta |
|---|---|---|---|
| Liszt | 0.738 | 0.7786 | +0.041 |
| Menuhin | 0.7083 | 0.6702 | −0.038 |
| Bellini | 0.6546 | 0.7958 | +0.141 |
| Purcell | 0.7915 | 0.6997 | −0.092 |
| Sidis | 0.6536 | 0.6381 | −0.015 |
| Mozart | 0.8145 | 0.7511 | −0.063 |

A 5C solo Purcell y Mozart están en la constante ~0.79–0.80; los demás están
abajo (0.65–0.74). El peso se mueve en los dos sentidos al agregar cortes
(Bellini sube +0.141, Purcell baja −0.092). **No se puede leer el Sol con 5 cortes.**

## 6. La proporcionalidad no existe a 5C; el cometa sí se fija temprano

- A 5C, prop es None en 4 de 6 casos en meseta (muy pocos nudos para Pearson).
  Solo Purcell (−0.099, MEDIA) y Mozart (−0.092, BAJA) tienen prop.
- A 7C, 8 de 10 casos en meseta tienen prop.
- **El corte del cometa es el mismo a 5C y a 7C en 5 de 6 casos**
  (Menuhin C3_1926, Bellini C5_1819, Purcell C3_1673, Sidis C2_1906, Mozart C3_1763).
  Lo que cambia es su tamaño (Mozart: 5 nudos/0.427 → 7 nudos/0.61;
  Bellini: 1/0.113 → 5/0.459). El cometa se fija temprano; crece con los cortes.
- El punto no considerado cambia de 5C a 7C en 5 de 6 casos (solo Liszt lo conserva:
  distopia_agotamiento_ambiental).

## 7. El H1 de 3C en niños es el creador

H1 a 3C: arquetipo_el_creador en 5/13 (Paganini, Liszt, Alkan, Bellini, Pascal);
30_ambicion en 3; 9_audaz_empresa en 2; social_04 en 2; utopia_liberal en 1.
A 7C el creador es H1 en 6/13. El creador es el tema por defecto del prodigio
infantil: con 3 cortes casi todos son «el creador», y solo con más cortes se
separan.

## Resumen en una frase

Con 3 cortes no hay meseta, el giro sale bajo y el Sol no está fijo; con 5
cortes la media ya es la buena pero el caso individual todavía se mueve (el Sol
sube o baja, la prop no existe); con 7 cortes se asientan la meseta, el giro y
la prop — y el tema de la infancia, cuando cambia, no se borra: baja a H2.
