# Cierres en estructuras dramáticas — verificación 2026-11-12

**Orden de Marco (~21:02 CST):** hay que ver los toques de cierre en estructuras
dramáticas, que esas son las que nos faltan, por eso estábamos con Polti.
**Matiz de Marco (~21:03):** posiblemente ahí también faltan TOKENS que vayan
hacia los cierres, porque no hacen falta reglas más allá de las que ya tenemos,
que se activan dependiendo de la carga semántica de los mismos tokens.
O sea: el trabajo es de TOKENS, no de reglas nuevas.

**Lateral:** `motor/laterales/cierre_dramatico/cierre_tokens.py`
(`CIERRE_TOKENS_V1_20261112`), resultado JSON en
`motor/laterales/cierre_dramatico/cierre_tokens_resultado.json`.
Solo LEE catálogo, entradas, matriz y RESULTs. No toca Engine, 244,
correr_estandar, teoria_color, equivalencias, no_duplicacion_latencia,
rueda_conjuncion ni ninguna entrada/RESULT sellado. `can_decide_H=False`.

**La compuerta_cierre del motor NO es esto.** Verificado en código
(`MOTOR_V15_3_UNICO_20260927.py:1575`): es una compuerta propia que re-revisa
los pendientes vivos del StinkBox antes de cerrar y solo puede RETENER el
cierre, nunca elegir H. No es una firma de cierre dramático. Lo que falta es
la firma: qué tokens cierran cada estructura.

---

## 1. Inventario de tokens de cierre en el 244

26 tokens revisados. Por token: familias que lo tienen como favor (con peso)
y como contra (con peso).

| token | favor | contra |
|---|---|---|
| cierre | — (0) | — (0) |
| desenlace | — (0) | — (0) |
| retorno | monomito_10 (0.8) | 10_rapto (0.6) |
| reconciliacion | cliodinamica_04 (0.8), frye_mythos_comedia (0.8) | situacion_dramatica_venganza (0.65), dialectica_02 (0.8), frye_mythos_tragedia (0.7), frye_mythos_ironia_satira (0.6) |
| resolucion | monomito_12 (0.9), cliodinamica_04 (0.8), dialectica_03 (0.8), frye_mythos_comedia (0.7) | frye_mythos_ironia_satira (0.7), predictivo_01_markov (0.75) |
| catarsis | monomito_08 (0.8), monomito_11 (0.9), eterno_retorno_03 (0.9) | — (0) |
| redencion | — (0) | sombra (0.6) |
| reconocimiento | — (0) | crisis_vocacional (0.65), 19_asesinato_de_un_pariente_no_reconocido (0.7) |
| anagnorisis | — (0) | — (0) |
| peripeteia | — (0) | — (0) |
| regreso | — (0) | — (0) |
| elixir | — (0) | — (0) |
| paz_interior | monomito_12 (0.8), cliodinamica_04 (0.7), dialectica_03 (0.7) | dialectica_02 (0.9) |
| sabiduria_compartida | monomito_12 (0.8) | — (0) |
| proposito_claro | monomito_12 (0.7), eterno_retorno_02 (0.7), berlin_01_erizo (0.75) | berlin_02_zorro (0.55) |
| restauracion_equilibrio | heroe (0.7) | — (0) |
| perdon | — (0) | situacion_dramatica_venganza (0.7), 3_venganza_del_crimen (0.8), 15_adulterio_homicida (0.6) |
| reintegracion | monomito_10 (0.7) | — (0) |
| sacrificio_final | monomito_11 (0.8), strauss_howe_04 (0.8), eterno_retorno_03 (0.8) | — (0) |
| superacion_miedo_raiz | monomito_11 (0.8), frye_mythos_romance (0.6) | — (0) |
| cambio_identidad | monomito_11 (0.7), strauss_howe_04 (0.7) | — (0) |
| legado | — (0) | — (0) |
| testamento | — (0) | — (0) |
| despedida | — (0) | — (0) |
| culminacion | — (0) | — (0) |
| clausura | — (0) | — (0) |

**11 tokens NO EXISTEN en el 244** (ni favor ni contra): cierre, desenlace,
anagnorisis, peripeteia, regreso, elixir, legado, testamento, despedida,
culminacion, clausura.

**3 tokens existen SOLO como contra** (favor 0): redencion (contra de sombra),
reconocimiento (contra de crisis_vocacional y 19_asesinato), perdon (contra
de venganza ×3).

**El cierre del viaje (monomito 10–12) sí tiene favor rico:** monomito_10
{retorno, reintegracion, urgencia_regreso, miedo_recaida}, monomito_11
{sacrificio_final, catarsis, superacion_miedo_raiz, cambio_identidad},
monomito_12 {paz_interior, sabiduria_compartida, proposito_claro, resolucion}.

---

## 2. Faltantes por caso: lo que implica el desenlace sellado vs lo que trae la entrada

Dos capas. **Catálogo:** tokens de cierre en el favor de las familias del
desenlace registrado en la matriz. **Prosa:** lectura de la nota de desenlace
de la entrada, solo cuando el texto enuncia literalmente el concepto, con la
cita. Ambas capas son auditables; la de prosa es lectura del auditor.

### Los 7 casos con prosa

| caso | trae en la entrada | implica el desenlace | FALTANTES (aplicables / inexistentes / solo-contra) |
|---|---|---|---|
| Juana | proposito_claro, reconocimiento | prosa: reconocimiento ("Rehabilitada 1456; canonizada 1920"), sacrificio_final ("condenada por herejia y quemada el 30-may-1431"). Catálogo: ninguno (sus fams de desenlace no traen favor de cierre) | **sacrificio_final** / — / — |
| Tubman | proposito_claro, reconocimiento, sabiduria_compartida | catálogo: paz_interior, sabiduria_compartida, proposito_claro, resolucion (favor de monomito_12 en el desenlace). Prosa: reconocimiento ("honrada por el ejercito y por el pais"), legado ("su obra perdura") | **paz_interior, resolucion** / **legado** / — |
| Mandela | reconocimiento, proposito_claro, sabiduria_compartida | prosa: reconocimiento ("funeral de Estado y duelo mundial"), reconciliacion ("su legado (reconciliacion, fin del apartheid) perdura"), legado (misma cita). Catálogo: ninguno | **reconciliacion** / **legado** / — |
| Semmelweis | **NINGUNO** | catálogo: restauracion_equilibrio (favor de heroe en el desenlace). Prosa: reconocimiento ("Reivindicado tras su muerte"), restauracion_equilibrio ("'salvador de las madres'"), legado ("generativo tras la muerte") | **restauracion_equilibrio** / **legado** / **reconocimiento** |
| Kolbe | proposito_claro, sabiduria_compartida | catálogo: restauracion_equilibrio (favor de heroe). Prosa: reconocimiento ("Canonizado en 1982"), sacrificio_final ("'martir de la caridad'"), restauracion_equilibrio ("Gajowniczek sobrevive a la guerra") | **restauracion_equilibrio, sacrificio_final** / — / **reconocimiento** |
| Noether | reconocimiento, proposito_claro, sabiduria_compartida | prosa: legado ("sigue la teoria"). Catálogo: ninguno (su desenlace en la matriz es texto libre, no familias) | — / **legado** / — |
| Carson | reconocimiento, proposito_claro, sabiduria_compartida | prosa: reconocimiento ("Silent Spring 1962, atencion mundial"). Catálogo: ninguno | — (sin faltantes) / — / — |

**Lecturas que importan:**

- **Semmelweis es el caso vacío:** ninguna entrada suya trae un solo token de
  cierre, y su desenlace implica tres (uno aplicable, uno solo-contra, uno
  inexistente).
- **El `reconocimiento` es un token al revés:** es el token de cierre más
  presente en las entradas (44 de 81, ver abajo) y NO favorece a ninguna
  familia: solo contradice a crisis_vocacional y a 19_asesinato. Los
  desenlaces sellados lo piden como favor en 6 de 7 casos (rehabilitación,
  canonización, funeral de Estado, atención mundial, reivindicación póstuma)
  y el catálogo no se lo da a nadie.
- **La capa catálogo casi no da nada:** de los 7 casos, solo Tubman
  (monomito_12 en el desenlace) y Semmelweis/Kolbe (heroe en el desenlace)
  implican tokens de cierre por favor de sus familias de desenlace. En los
  otros 4, las familias del desenlace no traen ningún favor de cierre. Los
  cierres viven en la prosa, no en el favor del catálogo.
- **Carson es el único caso completo** por este criterio (trae los tres
  tokens que su desenlace implica).

### Los 35 casos CAL (solo capa catálogo; sus entradas no traen prosa de desenlace)

- **Implicados por catálogo: NINGUNO en los 35.** Ninguna familia de
  desenlace de ningún caso CAL trae un token de cierre en su favor.
- **Presentes en la entrada: solo `reconocimiento`, en 15 de 35**
  (F001–F004). `proposito_claro` y `sabiduria_compartida` no aparecen en
  ninguna entrada CAL. 20 de 35 no traen ningún token de cierre.

### Global (81 entradas de la copia de trabajo, 241 tokens distintos)

- **45 de 81 entradas traen al menos un token de cierre.**
- **Solo TRES tokens de cierre aparecen en alguna entrada:**
  proposito_claro, reconocimiento, sabiduria_compartida.
  `retorno, resolucion, catarsis, reconciliacion, restauracion_equilibrio`
  NO aparecen en NINGUNA entrada.
- `reconocimiento` es el único presente en entradas CAL/F005/C-series
  (18 entradas CAL F001–F005 + 14 de la serie C + Mozart/Napoleón).
  `proposito_claro` y `sabiduria_compartida` aparecen SOLO en las entradas
  de héroes/Noether/Carson (y sus variantes SIN_C7).
- Nota: un conteo previo decía "18 de 45"; lo verificado es 18 entradas CAL
  (F001–F005) con `reconocimiento`, y 45 de 81 entradas totales con al menos
  un token de cierre. Eran dos cuentas mezcladas.

---

## 3. Tabla Polti → tokens de cierre (solo desenlaces sellados)

Regla: una situación entra si algún caso la tiene como H1 o en su desenlace;
sus tokens son los de cierre en el favor de las familias de esos desenlaces.
Sin caso => SIN CASO, no se inventa nada.

| situación | casos | tokens de cierre |
|---|---|---|
| 1_suplica | 0 | SIN CASO |
| 2_salvacion | 2 (Pasteur, Wagner) | — (ninguno) |
| 3_venganza_del_crimen | 0 | SIN CASO |
| 4_venganza_de_parientes | 0 | SIN CASO |
| 5_persecucion | 12 | **restauracion_equilibrio** (vía heroe en los desenlaces de Semmelweis y Kolbe) |
| 6_desastre | 5 | — |
| 7_caer_victima | 8 | — |
| 8_rebelion | 2 | — |
| 9_audaz_empresa | 8 | — |
| 10_rapto | 0 | SIN CASO |
| 11_enigma | 0 | SIN CASO |
| 12_obtencion | 3 | — |
| 13_enemistad_de_parientes | 0 | SIN CASO |
| 14_rivalidad_de_parientes | 0 | SIN CASO |
| 15_adulterio_homicida | 0 | SIN CASO |
| 16_locura | 1 (Ludwig II) | — |
| 17_fatal_imprudencia | 8 | — |
| 18_crimenes_involuntarios_de_amor | 0 | SIN CASO |
| 19_asesinato_de_un_pariente_no_reconocido | 0 | SIN CASO |
| 20_sacrificio_por_un_ideal | 5 (los 5 héroes) | **restauracion_equilibrio** (vía heroe), **paz_interior, sabiduria_compartida, proposito_claro, resolucion** (vía monomito_12 en Tubman) |
| 21_sacrificio_por_los_parientes | 0 | SIN CASO |
| 22_todo_sacrificado_por_una_pasion | 2 | — |
| 23_necesidad_de_sacrificar_a_los_seres_queridos | 0 | SIN CASO |
| 24_rivalidad_de_superior_e_inferior | 6 | — |
| 25_adulterio | 0 | SIN CASO |
| 26_crimenes_de_amor | 0 | SIN CASO |
| 27_descubrimiento_de_la_deshonra_de_un_ser_querido | 0 | SIN CASO |
| 28_obstaculos_para_el_amor | 0 | SIN CASO |
| 29_un_enemigo_amado | 0 | SIN CASO |
| 30_ambicion | 7 | — |
| 31_conflicto_con_un_dios | 4 | — |
| 32_celos_equivocados | 0 | SIN CASO |
| 33_error_de_juicio | 14 | — |
| 34_remordimiento | 0 | SIN CASO |
| 35_recuperacion_de_lo_perdido | 2 (Disney, Truman) | — |
| 36_perdida_de_los_seres_queridos | 2 (Coolidge, Juana) | — |

**19 de 36 situaciones SIN CASO. De las 17 con caso, solo 2 tienen algún
token de cierre** (5_persecucion y 20_sacrificio_por_un_ideal), y todos
vienen de los desenlaces de los héroes (heroe y monomito_12). Las 15
restantes con caso cierran sin ningún token de cierre medible en el catálogo.
Ni siquiera 2_salvacion (2 casos) ni 35_recuperacion_de_lo_perdido (2 casos),
que son situaciones de cierre por su propio nombre, traen tokens de cierre.

---

## 4. Medición sombra: ¿se mueven monomito_12 o heroe si los tokens de cierre hubieran estado?

**Método (cota superior, declarado).** Todos los tokens de cierre faltantes
APLICABLES de cada caso se añaden al corte final (C7 = Z) en el eje P (el
tablero del que se lee el H1 sombra), a peso de contrato 0.72 (sensibilidad
0.60 y 0.84). Cuello top-5 simulado: C7-P trae 5 tokens en los 5 casos; se
suelta el de menor peso por cada token añadido. Se re-corre el tablero sombra
reutilizando `correr_tablero_sombra` de no_duplicacion_latencia.py, en
dedup=True (tablero corregido: cada token se aplica una vez, por compañía, o
va a latencia) y dedup=False (canon: cada token apoya a todas sus familias
favor). Cada variante se compara contra SU PROPIA base del mismo dedup, más
un CONTROL solo-cuello (mismos soltados, sin tokens de cierre) para separar
el efecto del cuello del efecto del cierre.

**Puerta de cordura PASA en los 5 casos** (entrada sin modificar reproduce
el tablero sellado exacto, gate_mismatch 0) y el replay reproduce el
resultado guardado de no-duplicación (mismo H1 sombra y misma p).

### Tablero corregido (dedup=True), peso 0.72

| caso | faltantes aplicados | asignación del token | qué se mueve (neto del control) | H1 sombra |
|---|---|---|---|---|
| Juana | sacrificio_final | latencia, sin compañía | NADA (Δ<0.005 en las 6 objetivo) | 36_perdida (sin cambio) |
| Tubman | paz_interior (+resolucion suelta el cuello) | paz_interior → monomito_12 por compañía (sabiduria_compartida en C7) | monomito_12 +0.0124 → 0.8143, rango 2→1 | monomito_12, **EMPATADO** con schwartz_02_benevolencia (0.8143) |
| Mandela | reconciliacion | latencia, sin compañía | NADA | frye_mythos_romance (sin cambio) |
| Semmelweis | restauracion_equilibrio | heroe, única familia | heroe +0.1382 (0.6764→0.8146), rango 3→1 | heroe, **EMPATADO** con arquetipo_el_heroe (0.8146) |
| Kolbe | restauracion_equilibrio (+sacrificio_final suelta el cuello) | restauracion_equilibrio → heroe, única; sacrificio_final no entra | heroe +0.0217 (0.7934→0.8151), rango 3→1 | heroe, **EMPATADO** con arquetipo_el_heroe (0.8151) |

**A peso 0.84** el cuadro es el mismo, más fuerte: Tubman monomito_12
+0.0194 → 0.8213 (H1 claro); Semmelweis heroe +0.1402 → 0.8166 (empatado);
Kolbe heroe +0.0282 → 0.8216 (empatado). Juana y Mandela siguen en nada.

**A peso 0.60 no se mueve NADA en ningún caso:** el cuello top-5 suelta los
propios tokens de cierre porque son los más débiles del C7-P (0.60 < 0.70).
Los tokens de cierre, al fondo del rango de contrato, no entran nunca en un
corte final lleno.

**monomito_12 NO se mueve en Semmelweis, Kolbe, Juana ni Mandela**
(Δ≈0.000): ningún faltante aplicable lo alimenta ahí. Solo se mueve en
Tubman, donde ya estaba en rango 2.

**El control es lo que separa el efecto real del artefacto:** en Tubman el
control solo-cuello NO voltea el H1 (queda schwartz_02_benevolencia, 0.8183);
el volteo a monomito_12 es del token de cierre. En Semmelweis/Kolbe el
control deja el H1 en arquetipo_el_heroe (0.819 / 0.8191); el paso a heroe
es del token de cierre. En Juana el control incluso sube el H1 más que la
variante con cierre (0.8066 vs 0.8041): el token de cierre no aporta nada
ahí.

**Por qué los compartidos van a latencia:** sacrificio_final (3 familias:
monomito_11, strauss_howe_04, eterno_retorno_03) y reconciliacion (2:
cliodinamica_04, frye_mythos_comedia) no tienen compañía discriminante en
el C7 — ninguno de los otros tokens favor de esas familias está en el corte
— así que abren un frente de latencia y no cuentan para nadie (Juana:
frentes 23→24, 0 resueltos; Mandela: 22→22 neto, porque el cuello suelta a
`poder`, que abría un frente en la base, y `reconciliacion` abre uno en su
lugar — verificado token por token). El token discriminante
(restauracion_equilibrio → heroe, una sola familia) sí se aplica siempre.

### Tablero canónico (dedup=False), peso 0.72 — para contraste

Bajo la regla canónica los tokens de cierre sí alimentan a todas sus
familias favor: monomito_11 +0.174 (Juana), cliodinamica_04 y
frye_mythos_comedia +0.175 (Mandela), cliodinamica_04 +0.116 y dialectica_03
+0.066 (Tubman). PERO 'heroe' NO se mueve más allá del control en
Semmelweis/Kolbe (Δ+0.008 vs control +0.008): en el canon ya está saturado
por el sacrificio duplicado. Y los mayores movimientos del canon NO son del
cierre sino del CUELLO: monomito_05 −0.176 (Juana, soltar `compromiso`, su
único favor), monomito_08 +0.231 (Tubman, soltar `estabilidad`, contra de
monomito_08), 36_perdida −0.231 (Semmelweis/Kolbe, soltar `duelo`, favor
0.9). En el canon, añadir un token es sobre todo una historia de lo que
desplaza.

**Dato de estructura:** reconciliacion, bajo el canon, alimenta a
frye_mythos_comedia (+0.175) y contradice a frye_mythos_tragedia (−0.117):
es el token de cierre del polo comedia, contra el polo tragedia. El cierre
tiene polo.

---

## 5. Veredicto (PROPUESTA para decisión de Marco — NO implementado)

Tocar el 244 canónico requiere decisión explícita de Marco. Nada de esto se
implementó. Dos vías, separadas:

### (a) Lado catálogo (toca el 244 — decide Marco)

Faltan como favor, ordenados por la evidencia de los desenlaces sellados:

1. **`legado`** — no existe en ningún lado. Lo implican 4 de 7 desenlaces
   sellados (Tubman "su obra perdura", Mandela "su legado perdura",
   Semmelweis "generativo tras la muerte", Noether "sigue la teoría"). Es el
   token de cierre más pedido por los datos y el que menos existe. Habría que
   decidir a qué familias favorece (candidatas por carga semántica:
   monomito_12, heroe, arquetipo_el_heroe — a decidir, no impuesto aquí).
2. **`reconocimiento`** — existe solo como contra, pero los desenlaces lo
   piden como favor en 6 de 7 casos (rehabilitación, canonización, funeral
   de Estado, atención mundial, reivindicación póstuma) y es el token de
   cierre más presente en las entradas (44/81). Habría que añadirle favor
   (candidatas: monomito_12, heroe — a decidir).
3. **`cierre` / `desenlace`** — los tokens genéricos de cierre no existen.
   Si el motor necesita un token que diga "este corte cierra la estructura",
   no lo tiene. (Regreso/elixir son los nombres del monomito para lo mismo y
   tampoco existen: `regreso` y `elixir` están en 0.)
4. **`redencion` y `perdon`** — existen solo como contra. Ningún desenlace
   sellado de esta auditoría los pide como favor, así que no hay evidencia
   para moverlos; se dejan como están salvo que Marco diga otra cosa.
5. **`anagnorisis` / `peripeteia`** — no existen. Son los toques de cierre
   clásicos de la estructura dramática (el reconocimiento y el giro). Ningún
   desenlace de esta auditoría los pide literalmente; quedan anotados como
   hueco del vocabulario, no como urgencia.

### (b) Lado entrada (NO toca el catálogo — es el contrato de entrada)

Los tokens de cierre que YA EXISTEN como favor y NUNCA aparecen en ninguna
entrada — retorno, resolucion, catarsis, reconciliacion,
restauracion_equilibrio, reintegracion, sacrificio_final,
superacion_miedo_raiz, cambio_identidad — no necesitan regla nueva ni
familia nueva: necesitan que el LM que arma la entrada los EMITA cuando los
hechos lo ameriten (cambio a `CONTRATO_ENTRADA_LLM.txt`, no al 244). Ese es
el trabajo de tokens del que hablaba Marco: la carga semántica ya está en el
catálogo; la entrada no la alimenta.

Y con una condición que midió la sombra: **el token de cierre compartido
solo cuenta si trae compañía en el corte.** Bajo la regla de no duplicación,
sacrificio_final y reconciliacion se van a latencia porque ningún otro token
favor de sus familias está en el C7. Para que cuenten, la entrada tiene que
ponerlos junto a sus hermanos de favor en el mismo corte (p. ej.
resolucion junto a sabiduria_compartida/proposito_claro para monomito_12;
sacrificio_final junto a catarsis/superacion_miedo_raiz para monomito_11).
Sin compañía, el token de cierre es letra muerta aunque exista en el
catálogo.

### Lo que NO se midió

- La sombra solo cubre los 5 héroes y solo el C7 en P (cota superior). No se
  midió poner los tokens de cierre en cortes anteriores ni en A/C, ni el
  efecto sobre el rank_fusion (no se reimplementa) — solo sobre el tablero P.
- La tabla Polti tiene 19 situaciones SIN CASO: sus cierres no se pueden
  derivar de nada sellado hasta que haya casos.
- La capa prosa es lectura del auditor con citas; si Marco lee otro token en
  un desenlace, la tabla cambia y hay que re-correr.
