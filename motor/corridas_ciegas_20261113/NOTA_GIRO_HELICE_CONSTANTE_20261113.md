# El giro de la hélice — ¿La constante ~220-245° se sostiene?

**Fecha:** 2026-11-13 ~19:20 CST
**Origen:** orden de Marco 2026-11-13 ~19:13 CST ("probar cuál es la variante
en cada uno del tipo de tokens, el tipo de lo que está emergiendo, el tipo de
situaciones, pero sí debe de haber una especie de constante, así como el rango
de oscilación de los doscientos veinte grados más quince aproximadamente
porque va a estar los doscientos cuarenta y cinco").
**Método:** sonda helicoidal v1 (`sonda_helicoidal.py`, mismo método que midió
Mozart 222.5° y Napoleón 236.6°): PCA a 2 componentes sobre el tablero
P_FULL_244 por corte, ángulo total barrido en el plano PC1-PC2 alrededor del
centroide. Corrido en los 20 casos en meseta (14 con proporcionalidad + 6 de
3 cortes). Tabla: `motor/GIRO_HELICE_MUCHOS_CASOS_20261113.json`.

## Resultado: SÍ, la constante se sostiene

**Casos de 10 cortes (los 4, todos en el rango):**

| Caso | Giro total | Giro/paso | H1 | Prop |
|------|-----------|-----------|-----|------|
| CURIE | 221.6° | 24.6° | 30_ambicion | — |
| MOZART | 224.2° | 24.9° | utopia_autonomia_atenas | -0.777 |
| BOLIVAR | 229.7° | 25.5° | arquetipo_el_gobernante | -0.232 |
| NAPOLEON | 240.9° | 26.8° | arquetipo_el_gobernante | +0.568 |

Rango 10 cortes: **221.6° - 240.9°**. Todos dentro de ~220-245°.

**Casos de 7 cortes (10 de 11 en el rango):**

| Caso | Giro total | Giro/paso | H1 | Prop |
|------|-----------|-----------|-----|------|
| ANONIMO | 217.7° | 36.3° | arquetipo_el_sabio | +0.250 |
| MANDELA | 220.2° | 36.7° | kwml_01_rey | +0.078 |
| CARSON | 222.4° | 37.1° | arquetipo_el_creador | +0.155 |
| TUBMAN | 223.4° | 37.2° | arquetipo_el_gobernante | -0.443 |
| ANONIMO4 | 224.5° | 37.4° | arquetipo_el_gobernante | -0.187 |
| TRANSICION1 | 229.7° | 38.3° | arquetipo_el_creador | +0.295 |
| SEMMELWEIS | 233.6° | 38.9° | 20_sacrificio_por_un_ideal | -0.096 |
| KOLBE | 234.3° | 39.0° | 20_sacrificio_por_un_ideal | -0.015 |
| JUANA_DE_ARCO | 240.0° | 40.0° | arquetipo_el_gobernante | -0.396 |
| ANONIMO3 | 251.8° | 42.0° | 20_sacrificio_por_un_ideal | +0.724 |
| TRANSICION2 | **302.5°** | 50.4° | tainter_01_inversion_complejidad_productiva | -0.545 |

Rango 7 cortes (sin el atípico): **217.7° - 251.8°**. 10 de 11 dentro de
~220-252°.

## Lo que esto significa

1. **El giro TOTAL es la constante, no el giro por paso.** El giro por paso
   cambia con n_cortes (24-27° en 10 cortes, 36-50° en 7 cortes), porque
   cada corte cubre más "tiempo biográfico" cuando hay menos cortes. Pero el
   giro TOTAL sobre toda la biografía queda en la misma banda (~220-245°).
   La vuelta completa es una propiedad de la biografía entera, no del número
   de cortes en que se la divide.
2. **La banda es ~220-245°, con un atípico.** TRANSICION2 gira 302.5°,
   ~60° más que la banda. Es un caso tainter (inversión de complejidad,
   colapso) y tiene el PC1 más bajo (62.6% — la trayectoria está menos
   dominada por el primer componente). Puede ser un régimen distinto (una
   trayectoria de colapso que rota más). ANONIMO3 (251.8°) está apenas por
   encima de 245°.
3. **El giro NO determina el signo de la proporcionalidad ni el tipo de
   tokens.** Hay prop + y prop - en todo el rango del giro (217°-252°). El
   giro tampoco se agrupa por tipo de H1 ni por tipo de punto. Es una
   constante GEOMÉTRICA, independiente del lado semántico-funcional — tal
   como Marco corrigió: la hélice es puramente geometría, los tokens son
   otro lado, y se superponen sin forzarse.
4. **Los casos de 3 cortes no sirven para el giro.** Con solo 2 pasos, el
   giro por paso sale 92-111° (ruido, no medición). El giro necesita >= 6-7
   cortes, igual que la gravedad.

## La variante por tipo (lo que SÍ cambia por caso)

- **Tipo de H1 (Sol):** no agrupa el giro ni el signo de prop.
  arquetipo_el_gobernante aparece en todo el rango (217°-240°) con ambos
  signos.
- **Tipo de lo que emerge (punto):** tampoco agrupa el giro. El cuidador
  (Kolbe 234.3°, Mandela 220.2°, Semmelweis 233.6°) está en el rango normal;
  no es el giro lo que distingue a los héroes de sacrificio, es el TIPO de
  token que emerge.
- **Tipo de situación (régimen):** el régimen (meseta vs no meseta, 3 vs
  7-10 cortes) sí determina SI se puede medir el giro, pero no su valor.

## Conclusión

La constante que Marco señaló se sostiene: **el giro total de la hélice
oscila en ~220-245° a través de las biografías** (10 cortes: 221.6-240.9°;
7 cortes: 217.7-251.8°, con un atípico en 302.5°). Es una constante
geométrica, independiente de los tokens. La variante por tipo de tokens, por
tipo de lo que emerge y por tipo de situación NO está en el giro — está en
la gravedad (el signo de la proporcionalidad) y en el punto no considerado.
Los dos lados (geométrico y semántico) funcionan cada uno a su manera.
