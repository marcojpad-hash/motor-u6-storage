# VINCULACIÓN DE TOKENS — verificación 2026-11-12

**Orden de Marco (~21:17 CST):** encontrar la forma en la que se vinculan los
tokens. Los tokens flotan: a veces un token es una cosa y a veces otra, o está
superpuesto en dos estados al mismo tiempo; todo es cíclico, así que al final
van a seguir estando allá; lo que falta es la forma de la vinculación para que
haya entendimiento. La ecuación o el contrato de cómo se vinculan, de qué
manera y bajo qué criterios, como el de no-duplicación, en relación a los
tokens de la familia con la que interactúan, y que dé pauta hacia dónde se
podría desplazar la trayectoria.

**Lateral:** `motor/laterales/vinculacion_tokens/vinculacion.py`
(`VINCULACION_TOKENS_V1_20261112`), resultado JSON en
`motor/laterales/vinculacion_tokens/vinculacion_resultado.json`.
Reutiliza `_asignar` y `_familias_por_token` de
`no_duplicacion_latencia.py` por importación (no copiados) y el catálogo
por lectura. No toca Engine, 244, correr_estandar, teoria_color,
equivalencias, no_duplicacion_latencia, rueda_conjuncion, cierre_tokens
ni ninguna entrada/RESULT sellado (mtimes intactos del 7-nov).
`can_decide_H=False`. El JSON es reproducible: dos corridas seguidas dan
el mismo JSON (los empates se resuelven alfabéticamente, no por hash).

---

## 1. El contrato (V1) — en palabras y en fórmula

Sea t un token, c un corte, w(t,c) su peso de entrada en c (máximo sobre
P/A/C), F(t) sus familias favor, C(t) sus familias contra, y w_f(t,f) /
w_c(t,f) los pesos favor/contra del catálogo.

**Criterio 1 — VINCULACIÓN token↔token en un corte c:**

```
V(t1,t2,c) = Σ_{f ∈ F(t1)∩F(t2)} mín(w_f(t1,f), w_f(t2,f))   si t1,t2 ∈ c
           = 0                                              si no co-ocurren
```

Existe vínculo ⇔ V > 0. Un vínculo sin familia compartida no existe; un
vínculo sin co-ocurrencia en el corte no se activa ese corte (aunque el
solape estructural J = |F(t1)∩F(t2)| / |F(t1)∪F(t2)| sea > 0: J es
estructural, V es lo que se activa). Solo favor: el contra no vincula
tokens entre sí en esta versión.

**Criterio 2 — VINCULACIÓN token↔familia:**

- Estructural: t→f para todo f ∈ F(t) (favor) y t→f para todo f ∈ C(t)
  (contra, signo opuesto).
- RESUELTO en c: la asignación por compañía del lateral de
  no-duplicación da (f, "favor") o (f, "contra"): el vínculo t↔f se
  resuelve en c (motivos "unica" o "por_compania").
- SUPERPOSICIÓN en c: la asignación da latencia: el token queda en
  SUPERPOSICIÓN sobre F(t) (o C(t)): está vinculado a varias familias
  a la vez, en dos o más estados al mismo tiempo. ESO ES el frente de
  latencia.
- Vector de vínculo del token en c (masa conservada: la masa total del
  token en c es w(t,c); no se crea ni se destruye vínculo, se reparte
  o se transfiere):

```
L_t(c)[f] = +w(t,c)                              si resuelto favor a f
          = -w(t,c)                              si resuelto contra a f
          = +w(t,c)·w_f(t,f)/Σ_{g∈F(t)} w_f(t,g)  si superposición favor
          = -w(t,c)·w_c(t,f)/Σ_{g∈C(t)} w_c(t,g)  si superposición contra
          = 0                                    en otro caso
```

Un token sin familia es inerte (vector cero), igual que en el canónico.
El vector de vínculo NO es evidencia: la no-duplicación mide evidencia
aplicada (el token cuenta una vez o no cuenta); la vinculación mide a
dónde apunta el token, resuelto o en superposición.

**Criterio 3 — DESPLAZAMIENTO entre cortes:**

```
L(c)    = Σ_t L_t(c)                  (vector agregado del corte)
Δ(c→c+1) = L(c+1) − L(c)
Dirección sobre un tramo T = argmáx_f Σ_{c→c+1 ∈ T} Δ[f]
```

La pauta: si en los últimos cortes un token (o un grupo) gana vínculo
con la familia F, la trayectoria se desplaza hacia F. El desplazamiento
es FLUJO (cambio de masa de vínculo), no stock (p_final): incluye que
un token entre o salga del corte.

**Criterio 4 — CÍCLICO:** un vínculo puede volver. Para cada par (t,f)
se registra la serie L_t(c)[f] por corte:

- RETORNO: cambio de sentido pérdida→ganancia en Δ_t[f].
- REAPARICIÓN: L_t(c)[f] = 0 y L_t(c+1)[f] ≠ 0 habiendo sido ≠ 0 antes.
- VÍNCULO RESUELTO RECUPERADO: t resuelto a f, luego deja de estarlo,
  luego vuelve a resolverse a f.

---

## 2. Puerta de cordura — PASA 5/5

La clasificación resuelto/superposición usa `_asignar` de
no-duplicación (importado); la contabilidad de frentes se reimplementa
aquí. La puerta exige reproducir los frentes de
`no_duplicacion_resultado.json` por caso:

| caso | frentes referencia | frentes reproducidos | resueltos ref. | resueltos repr. | puerta |
|---|---|---|---|---|---|
| Juana | 23 | 23 | 0 | 0 | PASA |
| Tubman | 18 | 18 | 0 | 0 | PASA |
| Mandela | 22 | 22 | 0 | 0 | PASA |
| Semmelweis | 20 | 20 | 1 | 1 | PASA |
| Kolbe | 19 | 19 | 1 | 1 | PASA |

Total: 102 frentes, 2 resueltos, reproducidos exactos.

---

## 3. La prueba de desplazamiento — 3 de 5

Pregunta: ¿el desplazamiento de las últimas dos transiciones
(C5→C6 y C6→C7) apunta al H1 sombra del C7 (del lateral de
no-duplicación)?

| caso | H1 sombra | argmax gana (últ. 2) | Δ H1 | rango H1 | acierta |
|---|---|---|---|---|---|
| Juana | 36_pérdida (0.8011) | 7_caer_victima +0.78 | 0.00 | 35 | NO |
| Tubman | benevolencia (0.8124) | monomito_01 +2.10 | +0.74 | 5 | NO |
| Mandela | romance (0.7285) | romance +0.80 | +0.80 | 1 | SÍ |
| Semmelweis | arquetipo_el_heroe (0.8122) | arquetipo_el_heroe +0.78 | +0.78 | 1 | SÍ |
| Kolbe | arquetipo_el_heroe (0.8123) | arquetipo_el_heroe +1.54 | +1.54 | 1 | SÍ |

Con UNA sola transición (C6→C7) la pauta acierta 1 de 5 (solo
Semmelweis): el flujo de un corte es demasiado ruidoso. Con dos
transiciones acierta 3 de 5.

**Los tres aciertos, y quién los lleva** (el flujo lo cargan uno o dos
tokens, no un frente amplio):

- Mandela: el romance gana +0.80 por un solo token, `victoria` (+0.80).
- Semmelweis: el héroe gana +0.78 por `valentía` (+0.78); en la última
  transición sola gana +1.26.
- Kolbe: el héroe gana +1.54 por `valentía` (+0.78) y `defensa_debil`
  (+0.76), los dos discriminantes del héroe.

**Los dos fallos, con mecanismo (no maquillados):**

- **Juana — el H1 es un pulso, no un escalón.** El H1 (36_pérdida) gana
  +1.50 en C5→C6 (es el argmax de esa transición: `duelo` +0.74 y
  `perdida_familiar` +0.76 llegan al corte) y lo pierde TODO en C6→C7
  (−1.50: los dos tokens salen del corte). Neto en las últimas dos:
  0.00. El flujo adelanta al stock por una transición: el H1 gana en
  C5→C6 y el stock (p_final) lo recuerda, pero el flujo de C6→C7 ya
  se fue a otra parte (milgram_obediencia +0.70). La pauta habría
  acertado con la ventana C5→C6 sola. El fallo es de ventana, no de
  contrato.
- **Tubman — el argmax es un cambio de signo, no una atracción nueva.**
  El mundo ordinario pasa de −0.72 en C5 (`crisis_abrupta`, contra
  único, L=−0.72) a +1.34 en C6 (`cotidiano` +0.66 y `rutina` +0.68,
  favor) y +1.38 en C7: +2.10 en las últimas dos. Es a la vez una
  liberación del contra (−0.72 que se va) y una llegada del favor
  (+1.34 que entra). El H1 (benevolencia) sí gana (+0.74, rango 5),
  pero menos que el cambio de signo. La ganancia por liberación de
  contra no es lo mismo que la ganancia por llegada de favor, y la
  pauta no las distingue.

**Prueba secundaria — flujo contra flujo (no flujo contra stock):**
¿la familia que más p_final GANA en el tablero sombra P entre C5 y C7
es la misma que el argmax del flujo? Acierta 2 de 5 (Mandela, Kolbe).
El dato que importa: en Juana y Tubman el H1 sombra ES la familia que
más p_final gana en C5→C7 (rango 1: +0.2945 y +0.2986) aunque el flujo
no lo apunte. El stock recuerda lo que el flujo olvidó: la p ganada en
C5→C6 (cuando llegaron los tokens del H1) persiste en C7 con apenas
decaimiento por épsilon, mientras el vector de vínculo de C7 ya marca
cero porque los tokens se fueron. En Semmelweis la ganancia de p no
dice nada: el H1 está saturado en el techo (0.8122) y solo puede ganar
+0.0058 (rango 63); ahí el flujo es lo único que todavía se mueve.

**Veredicto de la pauta:** da pauta, no ley. 3 de 5 en dos
transiciones, 1 de 5 en una. Apunta al H1 sombra cuando los tokens del
H1 siguen vinculados al final (Mandela, Semmelweis, Kolbe); falla
cuando los tokens del H1 son un pulso que ya salió (Juana) o cuando un
cambio de signo domina la ganancia (Tubman). Y el flujo mide dónde está
el vínculo AHORA; el H1 sombra es un stock acumulado. Para predecir el
H1 hace falta el stock, no solo el flujo.

---

## 4. Lo cíclico — medido, no afirmado

| caso | retornos | cambios de sentido | reapariciones | vínculos resueltos recuperados | pares (token,familia) |
|---|---|---|---|---|---|
| Juana | 55 | 162 | 49 | 7 | 119 |
| Tubman | 56 | 156 | 51 | 7 | 97 |
| Mandela | 48 | 143 | 43 | 5 | 110 |
| Semmelweis | 38 | 110 | 33 | 13 | 94 |
| Kolbe | 18 | 67 | 9 | 3 | 82 |
| **Total** | **215** | **638** | **185** | **35** | **502** |

El vínculo vuelve: 215 retornos (pérdida→ganancia), 185 reapariciones
(salió a cero y volvió) y 35 vínculos resueltos recuperados. Ejemplos:
`defensa_debil` → arquetipo_el_heroe se recupera en Semmelweis (el
discriminante del héroe vuelve a resolverse a él); `crisis_abrupta` →
monomito_01 se recupera en Juana y en Tubman (el vínculo contra vuelve).
El token más cíclico es `autoridad` en Juana (2 retornos a tres
familias: monarquía, gobernante, tesis) y `busqueda_verdad` en
Semmelweis (2 retornos a sabio, mago y spengler). La dirección del
vínculo cambia de sentido 638 veces en 5 casos: la trayectoria no es
una línea recta, oscila.

---

## 5. El grafo y la superposición — por corte

Superposición (tokens en dos o más estados a la vez) por caso:
Juana 39 ocurrencias (23 distintos), Tubman 35 (18), Mandela 45 (22),
Semmelweis 34 (20), Kolbe 33 (19). Total 186 ocurrencias. Por corte
entre 2 y 9 tokens en superposición; la superposición es lo normal, no
la excepción.

Grafo token↔token (solo favor compartido): 82 aristas en total
(Juana 18, Tubman 12, Mandela 18, Semmelweis 19, Kolbe 15). El grafo
es RALO: 4 cortes no tienen NINGUNA arista (Juana C3 y C5, Tubman C3
y C5: ningún par de tokens del corte comparte familia favor). Los
vínculos más fuertes: `autoridad`↔`liderazgo` 1.30 en Juana, Tubman y
Mandela (familias compartidas: anaciclosis monarquía y gobernante — el
par del trono, otra vez); `analisis`↔`busqueda_verdad` 1.50 en
Semmelweis (sabio y spengler); `cronicidad_sintomatica`↔`duelo` 1.20
en Kolbe.

---

## 6. Veredicto

- El contrato está formalizado (criterios 1–4, ecuación explícita) y
  verificado: la puerta reproduce los 102 frentes de no-duplicación
  exactos, y el JSON es reproducible entre corridas.
- La vinculación SÍ da pauta de desplazamiento, pero parcial: 3 de 5
  en dos transiciones, 1 de 5 en una, 2 de 5 contra la ganancia de p.
  No es ley.
- Lo cíclico queda medido: 215 retornos, 185 reapariciones, 35
  vínculos resueltos recuperados. El vínculo vuelve, como dijo Marco.
- Qué falta (no implementado, para decidir):
  1. Una ventana que atrape pulsos: el H1 de Juana gana en C5→C6 y
     la pauta de las últimas dos lo promedia a cero. Falta medir el
     desplazamiento por transición suelta y por ventana, no solo el
     agregado de las últimas dos.
  2. Distinguir la ganancia por llegada de favor de la ganancia por
     liberación de contra (el cambio de signo de Tubman): hoy las dos
     suman igual en Δ.
  3. El flujo no ve el stock: para apuntar al H1 sombra hace falta
     combinar el vector de vínculo actual con la p acumulada, no usar
     el flujo solo.
  4. El desplazamiento lo cargan 1–2 tokens: un solo token que sale
     (`perdida_familiar`) borra el flujo del H1. Falta medir la
     robustez del argmax (¿cuánto cambia si se quita el token que
     más aporta?).

Caveats: la prueba es solo en los 5 héroes (7 cortes c/u). La
superposición se reparte proporcional a los pesos favor del catálogo
(decisión de diseño, documentada en el código). El contra no vincula
tokens entre sí en esta versión. El desplazamiento se mide solo sobre
el tablero P (el H1 sombra es de tablero P).
