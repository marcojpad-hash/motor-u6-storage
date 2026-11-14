# Re-corrida en 52 casos — Regímenes y la fórmula constante

**Fecha:** 2026-11-13 ~19:15 CST
**Origen:** orden de Marco 2026-11-13 ~19:09 CST ("revísalo de nuevo, córrelo
otra vez, hasta pulirlo; encontrar la fórmula constante de cómo se aplica,
porque no va a ser la misma fórmula a todos los casos").
**Método:** lateral v3 (`lateral_comportamiento_post_meseta_v1.py`, VERSION
v3_20261113) corrido sobre 52 RESULT distintos (un representante por caso,
sin duplicados). Tabla completa:
`motor/TABLA_GRAVEDAD_MUCHOS_CASOS_20261113.json`.

## Resultado general

- **20 en meseta, 32 mudos** (sin meseta, no hay lectura).
- De los 20 en meseta, 14 tienen proporcionalidad medible (los otros 6 son
  casos de 3 cortes con 0-2 nudos, sin suficientes pares para Pearson).

## Los regímenes (particularidades medibles)

### Régimen 0 — Sin meseta (mudo). La fórmula no aplica.
- 32/52 casos. Casi todos son de **3 cortes** (F001-F004).
- Condición medible: n_cortes = 3 → casi siempre CONTINUIDAD_ASCENDENTE.
- La fórmula necesita trayectoria para trabajar.

### Régimen 1 — Meseta con 3 cortes. La lectura existe pero está vacía.
- 6 casos (BACH, CHURCHILL, CURIE, FARADAY, OPPENHEIMER, TURING).
- Sol 0.5-0.75, nudos 0-2, proporcionalidad = None (menos de 3 pares).
- Hay meseta pero no hay suficiente movimiento para medir gravedad.

### Régimen 2 — Meseta con 7-10 cortes. La gravedad funciona.
- 14 casos. Aquí trabaja el instrumento.
- Sol 0.73-0.8155 (la constante ~0.79-0.80 en los fuertes).
- Siempre hay cometa y siempre hay punto no considerado.
- Pero el signo de la proporcionalidad se parte: **6 positivos, 7 negativos,
  1 ~0 (Kolbe -0.015)**.

## El signo de la proporcionalidad NO se predice con una sola variable

Correlaciones con el valor de prop (n=14, todas débiles o moderadas):

| Variable | Corr con prop |
|----------|---------------|
| frac_masa_nudos (fracción de masa en los nudos) | **+0.446** |
| n_acercandose | -0.477 |
| frac_masa_H1 | -0.378 |
| peso_sol_Z | +0.332 |
| masa_favor_H1 | -0.33 |
| dist_media | +0.204 |
| frac_lejos | +0.179 |
| n_cortes | -0.131 |
| cometa_salto | -0.135 |
| n_nudos | +0.095 |

- **El tipo de H1 NO determina el signo:** arquetipo_el_gobernante sale +
  en Napoleón y - en Bolívar, Juana, Tubman y Anónimo4. 20_sacrificio sale +
  en Anónimo3 y - en Kolbe y Semmelweis.
- **La distribución de distancias NO lo determina:** Mozart y Napoleón
  tienen frac_lejos = 0.00 los dos y signos opuestos (-0.777 vs +0.568).
  Anónimo3 (frac_lejos 0.69, +0.724) y Anónimo4 (frac_lejos 0.68, -0.187)
  tienen casi la misma distribución y signos opuestos.
- **La posición del cometa NO lo determina:** hay cometas tempranos y
  tardíos en ambos signos.

**Conclusión honesta:** el signo es una propiedad EMERGENTE de la
configuración específica de tokens de cada caso. No se reduce a una sola
variable. Se mide por caso, no se predice por fórmula.

## Las particularidades que SÍ distinguen (medibles)

1. **n_cortes — el umbral más fuerte.** Con 3 cortes no hay lectura de
   gravedad (mudo o vacío). Con 7-10 cortes, la lectura funciona. Umbral:
   n_cortes >= 6-7.
2. **Peso del Sol — la constante.** ~0.79-0.80 en biografías fuertes y
   completas (7-10 cortes). 0.5-0.75 en casos débiles o de 3 cortes. Es la
   constante en la inercia que Marco buscaba.
3. **El tipo del punto no considerado — depende de la biografía.**
   - `arquetipo_el_cuidador` en Kolbe, Mandela y Semmelweis: los 3 son
     héroes de sacrificio. El cuidador emerge desde abajo en biografías de
     sacrificio. Es un patrón real e interpretable.
   - `weber_02_autoridad_carismatica` en Bolívar (el Libertador).
   - `situacion_dramatica_ambicion` en Mozart.
   - `dumezil_f2_fuerza` en Napoleón.
   - `sombra` en Anónimo, `7_caer_victima` en Juana de Arco.
4. **frac_masa_nudos — la señal más fuerte del signo (+0.446).** Cuando los
   nudos (las familias que suben) llevan más fracción de la masa total, la
   prop tiende a positiva (convergencia). Cuando H1 concentra la masa, tiende
   a negativa. Es moderada, no decisiva, pero es la mejor pista.
5. **La pendiente es por corte.** Los casos de 7 cortes tienen pendientes
   medias más altas (3-12) que los de 10 cortes (0.4-1.1), porque el mismo
   ascenso total se comprime en menos cortes. La pendiente NO es comparable
   directamente entre casos con distinto n_cortes.

## La fórmula constante (lo que NO cambia) vs lo que varía

**Constante (la fórmula en su forma):**
- La estructura: Sol + nudos + cometa + proporcionalidad + punto. Siempre
  presente en Régimen 2.
- La condición: solo en meseta, solo con >= 6-7 cortes.
- El Sol ~0.79-0.80 en biografías fuertes (la constante en la inercia).
- El cometa siempre existe y siempre va con un pulso de input (11-19% de
  la masa total en un corte).
- El punto no considerado siempre existe y siempre es una familia que sube
  y no está en el top.

**Variable (las particularidades por caso):**
- El signo de la proporcionalidad (+ convergencia / - consolidación):
  emergente, se mide por caso.
- El tamaño y la posición del cometa.
- El tipo específico del punto (depende de la biografía).
- El peso del Sol (fuerte ~0.79-0.80 vs débil 0.5-0.75).

**La fórmula constante no es una ecuación que prediga el signo. Es la
estructura + las condiciones de aplicación. El signo es lo que se mide, no
lo que se predice.**

## Tabla (14 casos con proporcionalidad)

| Caso | Cortes | Sol | Nudos | Prop | Conf | Cometa | Punto |
|------|--------|-----|-------|------|------|--------|-------|
| ANONIMO | 7 | 0.8013 | 17 | +0.250 | ALTA | C6_1852 (11, 0.951) | sombra |
| ANONIMO3 | 7 | 0.8006 | 16 | +0.724 | ALTA | C4_1925 (7, 0.776) | mbti_introvertido |
| ANONIMO4 | 7 | 0.7701 | 19 | -0.187 | ALTA | C7_1648 (9, 0.821) | anacyclosis_01_monarquia |
| BOLIVAR | 10 | 0.8155 | 11 | -0.232 | MEDIA | C5 (9, 1.045) | weber_02_autoridad_carismatica |
| CARSON | 7 | 0.8006 | 9 | +0.155 | MEDIA | C3_1936 (4, 0.455) | schwartz_10_autodireccion |
| JUANA_DE_ARCO | 7 | 0.7336 | 16 | -0.396 | ALTA | C6_1430_05 (8, 1.248) | 7_caer_victima |
| KOLBE | 7 | 0.8013 | 13 | -0.015 | ALTA | C6_1941_07 (6, 0.676) | arquetipo_el_cuidador |
| MANDELA | 7 | 0.8013 | 16 | +0.078 | ALTA | C3_1961 (10, 1.077) | arquetipo_el_cuidador |
| MOZART | 10 | 0.7985 | 6 | -0.777 | BAJA_MUESTRA | C6 (6, 0.482) | situacion_dramatica_ambicion |
| NAPOLEON | 10 | 0.7813 | 7 | +0.568 | BAJA_MUESTRA | C9 (3, 0.32) | dumezil_f2_fuerza |
| SEMMELWEIS | 7 | 0.8013 | 13 | -0.096 | ALTA | C6_1858 (6, 0.511) | arquetipo_el_cuidador |
| TRANSICION1 | 7 | 0.8006 | 20 | +0.295 | ALTA | C7_1448 (8, 0.651) | schwartz_09_estimulacion |
| TRANSICION2 | 7 | 0.7768 | 19 | -0.545 | ALTA | C5_1530 (8, 0.913) | schwartz_06_poder |
| TUBMAN | 7 | 0.7719 | 13 | -0.443 | ALTA | C3_1853 (5, 0.398) | erikson_07_generatividad_vs_estancamiento |
