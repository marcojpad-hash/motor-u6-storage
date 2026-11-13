# Rueda de conjunción v1 — verificación (2026-11-12)

Lateral: `motor/laterales/teoria_color/rueda_conjuncion.py`
No se tocó Engine, ni 244, ni correr_estandar, ni teoria_color.py,
ni equivalencias.py, ni ningún RESULT/entrada/COLOR sellado.
Solo lectura. La matemática de color() y hue() es la misma de los
laterales existentes (color()/hexrgb() importadas de teoria_color.py;
hue()/hx() extraídas por AST de equivalencias.py, byte por byte — el
archivo es un script sin guarda `__main__` y no se puede importar
sin ejecutarlo).

## Artefactos

- Tableros sombra por corte (P/A/C): `motor/reconexion_v2a1/sombra_tableros_<caso>.json` (5)
- Colores sombra: `motor/COLOR_SOMBRA_<caso>.json` (5, mismo esquema que COLOR_RESULT)
- Ruedas: `motor/laterales/teoria_color/RUEDA_CONJUNCION_<caso>_canonico.png` y `..._sombra.png` (10)
- Resumen JSON: `~/workspace/u6-alterno/rueda_conjuncion_resumen.json`

## Puerta de cordura: PASA

Con la regla apagada, el tablero sombra reproduce los FULL_244
sellados exacto: 0 valores distintos, diferencia máxima 0.0, en los
5 casos (7 cortes × 3 ejes × 244 familias = 5.124 valores por caso;
25.620 en total). Verificación cruzada: los H1 sombra reproducen
exacto los del lateral de no duplicación (Juana → 36_pérdida,
Tubman → benevolencia, Mandela → romance, Semmelweis/Kolbe →
arquetipo_el_heroe).

## La mezcla sigue gris (canónico vs sombra)

| Caso | croma mezcla canon | croma mezcla sombra | croma mezcla desat | saturación canon → sombra | neutralización canon → sombra |
|---|---|---|---|---|---|
| Juana | 0.020 | 0.009 | 0.002 | 0.020 → 0.010 | 0.818 → 0.632 |
| Tubman | 0.022 | 0.013 | 0.004 | 0.024 → 0.015 | 0.766 → 0.626 |
| Mandela | 0.048 | 0.007 | 0.001 | 0.053 → 0.008 | 0.592 → 0.517 |
| Semmelweis | 0.040 | 0.014 | 0.004 | 0.042 → 0.016 | 0.553 → 0.601 |
| Kolbe | 0.026 | 0.023 | 0.010 | 0.028 → 0.025 | 0.665 → 0.445 |

La mezcla NO deja de ser gris en la sombra: se vuelve MÁS gris.
El matiz de la mezcla sombra (308°, 344°, 278°, 329°, 349°) es
ruido: con croma ~0.01 el ángulo no apunta a ningún lado. La
neutralización BAJA en 4 de 5 (la mezcla pierde menos croma porque
hay menos croma que perder); solo sube en Semmelweis (0.553→0.601).

## (a) El clúster héroe: un color con tres nombres (canónico, casos limpios)

En Semmelweis y Kolbe, donde las tres familias héroe están en el set
canónico, sus tonos medios son el mismo: interno ~0.40, externo
~0.30, situación ~0.30. Matices canónicos: heroe 0°, arquetipo_heroe
0°, arquetipo_el_heroe 1.9° (Semmelweis) y 5.8° (Kolbe). Diferencias
de matiz ≤6°: son análogos (≤30°) con holgura. NO son pigmentos
idénticos: 0 grupos idénticos en el canónico (las trayectorias por
corte difieren; solo el tono medio coincide).

En los 3 líderes las familias héroe NO están en el set canónico y
sus matices canónicos (calculados desde los tableros sellados) son
ruido: heroe 0°, arquetipo_heroe 116.6°, arquetipo_el_heroe 116.6°–
180°, con cromas 0.0–0.11. Con croma ~0 el matiz no significa nada:
el héroe es GRIS en el canónico de los líderes, no tiene color.

En la sombra, las tres familias héroe colapsan al MISMO matiz en
los 5 casos (Δmatiz = 0° en los líderes; ≤15° en los limpios) — pero
en los líderes es trivial: las tres son el mismo gris plano (croma
0.003–0.007). En los limpios se separan POR CROMA, no por matiz
(ver desaturación abajo).

## (b) El trono: polo complementario que se vuelve gris

Canónico: el trono es el polo opuesto de la rueda. Hay 15 pares
complementarios en Juana, 9 en Tubman, 21 en Mandela, 7 en
Semmelweis, 7 en Kolbe — casi todos con el gobernante o el rey a
~180° de otras familias. Matiz/croma canónicos del gobernante:
206.9°/0.024 (Juana), 337.3°/0.025 (Tubman), 302.2°/0.115 (Mandela);
del rey: 93.6°/0.101, 57.8°/0.095, 24.8°/0.102.

Sombra (líderes): gobernante y rey caen al mismo matiz que todo lo
demás (254.0°, 309.8°, 319.7°) con croma 0.003–0.007 y croma
desaturado 0.0: su evidencia (8/5, 6/6, 8/8 ocurrencias favor
canónicas) se fue entera a latencia. Los pares complementarios
mueren: 0 en Juana, 1 en Tubman, 0 en Mandela, 0 en Semmelweis, 0
en Kolbe. La rueda pierde su oposición.

Sombra (limpios): el trono nunca fue alimentado (0 ocurrencias
canónicas). Su croma es ~0.003–0.004 y su fracción resuelta es 1.0
POR REGLA (sin evidencia canónica), NO porque se haya resuelto
nada. No leer ese 1.0 como "resuelto".

## (c) Pigmentos idénticos: la sombra funde todo en un gris

Canónico: 0 grupos de pigmentos idénticos en los 5 casos.
Sombra: UN grupo gigante por caso — 13 familias idénticas en Juana,
11 en Tubman, 15 en Mandela, 12 en Semmelweis, 10 en Kolbe — con la
MISMA secuencia de vectores por corte (el piso ~0.51 en los tres
ejes). Todo lo que perdió su evidencia se vuelve EL MISMO pigmento.
La rueda sombra no separa familias: las funde.

## (d) Latencia como desaturación (por familia de interés)

Fracción resuelta = ocurrencias asignadas en la sombra / ocurrencias
canónicas (favor+contra, por ocurrencia de marcador). El croma
desaturado = croma sombra × fracción. "Sin evidencia" = 0
ocurrencias canónicas (fracción 1.0 por regla, no es resolución).

| Caso | familia | canon favor/contra | fracción | croma sombra → desaturado |
|---|---|---|---|---|
| Juana | heroe | 2/0 | 0.000 | 0.003 → 0.000 |
| Juana | arquetipo_heroe | 0/0 sin evidencia | 1.000 | 0.003 → 0.003 |
| Juana | arquetipo_el_heroe | 0/1 | 0.000 | 0.003 → 0.000 |
| Juana | gobernante / rey | 8/0, 5/0 | 0.000 | 0.003 → 0.000 |
| Tubman | heroe | 2/0 | 0.000 | 0.003 → 0.000 |
| Tubman | arquetipo_heroe | 0/0 sin evidencia | 1.000 | 0.003 → 0.003 |
| Tubman | arquetipo_el_heroe | 0/0 sin evidencia | 1.000 | 0.003 → 0.003 |
| Tubman | gobernante / rey | 6/0, 6/0 | 0.000 | 0.003 → 0.000 |
| Mandela | heroe | 3/0 | 0.000 | 0.007 → 0.000 |
| Mandela | arquetipo_heroe | 0/0 sin evidencia | 1.000 | 0.007 → 0.007 |
| Mandela | arquetipo_el_heroe | 0/0 sin evidencia | 1.000 | 0.007 → 0.007 |
| Mandela | gobernante / rey | 8/0, 8/0 | 0.000 | 0.007 → 0.000 |
| Semmelweis | heroe | 3/0 | 0.333 | 0.083 → 0.028 |
| Semmelweis | arquetipo_heroe | 4/0 | 0.000 | 0.003 → 0.000 |
| Semmelweis | arquetipo_el_heroe | 8/1 | 0.778 | 0.124 → 0.096 |
| Semmelweis | gobernante / rey | 0/0 sin evidencia | 1.000 | 0.003 → 0.003 |
| Kolbe | heroe | 3/0 | 0.667 | 0.056 → 0.037 |
| Kolbe | arquetipo_heroe | 2/0 | 0.000 | 0.004 → 0.000 |
| Kolbe | arquetipo_el_heroe | 4/2 | 0.667 | 0.054 → 0.036 |
| Kolbe | gobernante / rey | 0/0 sin evidencia | 1.000 | 0.004 → 0.004 |

Lo que se ve en los limpios: la valentía (4 ocurrencias en
Semmelweis, 2 en Kolbe) NO se reparte entre las tres familias héroe:
se la queda entera arquetipo_el_heroe (por compañía con
defensa_debil, su discriminante) y arquetipo_heroe queda en 0.000.
El clúster se separa por saturación: arquetipo_el_heroe conserva su
color (0.096/0.036), heroe conserva un tercio o dos tercios
(0.028/0.037), arquetipo_heroe lo pierde todo. En los líderes, el
sacrificio (único token héroe, 2–3 ocurrencias) se va entero a
latencia y las tres familias quedan en gris.

## Veredicto honesto

La rueda SÍ conjuga cuatro de las cinco piezas:

1. **El héroe partido en tres**: en el canónico limpio es un solo
   color con tres nombres (mismo matiz ~0°, Δ≤6°). En la sombra se
   separa por saturación, no por matiz: un solo tono, tres croma
   distintos según cuánta evidencia resolvió cada nombre.
2. **La duplicación**: el trono canónico vive del peso duplicado
   (autoridad ×13, liderazgo ×6) y es el polo complementario de la
   rueda; sin duplicar, su croma se va a 0.0.
3. **La latencia**: como desaturación, tira los puntos hacia el
   gris. El costo se ve en la rueda: solo 2–3 puntos sobreviven con
   croma; el resto es el centro.
4. **El trono**: muere en la sombra en los 5 casos (croma
   desaturado 0.0 en los líderes; sin evidencia en los limpios).

Lo que la rueda NO conjuga:

- **La mezcla sigue gris en los dos tableros.** La rueda no crea
  color donde no lo hay: croma de mezcla 0.02–0.05 canónico,
  0.007–0.023 sombra, 0.001–0.010 desaturado.
- **El matiz es ruido cuando el croma es ~0.** Las diferencias de
  matiz de 116°–180° entre las familias héroe en el canónico de los
  líderes no son direcciones: son artefactos de vectores casi
  nulos. La rueda no puede dar matiz a una familia sin color.
- **El radio NO está en esta rueda.** La ruptura del margen de
  radio (la deriva hacia el límite, 7 de 9 largos rompen en Z) no
  tiene ninguna dimensión en el plano cromático. Esa conjunción
  sigue pendiente: el radio es una magnitud de la trayectoria, no
  un color.
- **El H1 sombra es lectura de tablero** (mayor p_final en el
  corte Z), no el rank_fusion del motor. La rueda muestra hacia
  dónde apunta el tablero, no lo que el motor decide.
- **Defecto de presentación**: en las ruedas sombra las etiquetas
  del centro se solapan (muchas familias colapsan al mismo punto
  gris). Es consecuencia del colapso, no un error de trazado, pero
  las PNGs se leen peor en el centro.
