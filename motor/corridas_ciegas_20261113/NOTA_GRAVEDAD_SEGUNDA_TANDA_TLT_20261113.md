# Gravedad en otros apartados — segunda tanda: Tesla, Lincoln, Trotsky (7 cortes)

Fecha: 2026-11-13. Rama: alterno/reconexion-2a1. Lateral v3. Sonda helicoidal v1.

## Entradas

Extendidas de 3 a 7 cortes (tokens solo del vocabulario CAL, pesos 0.60–0.84, validados por script: 0 fuera de vocabulario/rango):

- `entrada_CAL_F001_02_TESLA_7C.json` — C4_1906 (Wardenclyffe abandonado, Morgan retira el dinero), C5_1915 (Nobel que no llega, rechaza compartirlo con Edison), C6_1926 (hoteles de Nueva York, alimenta palomas), C7_1943 (muere solo en el hotel New Yorker).
- `entrada_CAL_F003_07_LINCOLN_7C.json` — C4_1860 (gana la presidencia, se separa el sur), C5_1863 (Emancipación, Gettysburg), C6_1864 (reelegido en guerra), C7_1865 (termina la guerra, asesinado en el Ford).
- `entrada_CAL_F003_06_TROTSKY_7C.json` — C4_1927 (expulsado, deportado a Turquía), C5_1936 (juicios de Moscú), C6_1938 (funda la Cuarta Internacional), C7_1940 (asesinado en Coyoacán por Mercader).

## Corridas

Las 3 completaron con recibo COMPLETED (returncode 0, ~70 s c/u, en secuencia).
RESULTs: `RESULT_TESLA_7C.json`, `RESULT_LINCOLN_7C.json`, `RESULT_TROTSKY_7C.json`.

## Resultados

| caso | H1 3 cortes | H1 7 cortes | H2 7c | grado | Sol | nudos | prop | conf | cometa | punto | giro |
|---|---|---|---|---|---|---|---|---|---|---|---|
| TESLA | 22_todo_sacrificado | 22_todo_sacrificado | 30_ambicion | FRAGIL | 0.7551 | 9 (0c 5j 2a 1r) | −0.223 | MEDIA | C6_1926 (3, 0.304) | mbti_factor_introversion_i | 221.0° |
| LINCOLN | 12_obtencion | 3_venganza_del_crimen | 12_obtencion | FRAGIL | 0.7871 | 6 (1c 2j 2a 0r) | −0.123 | BAJA_MUESTRA | C2_1856 (2, 0.212) | situacion_dramatica_ambicion | 236.1° |
| TROTSKY | 24_rivalidad | mauss_01_intercambio_agonistico | dumezil_f2_fuerza | AJUSTADA | 0.6837 | 11 (2c 5j 4a 0r) | +0.316 | MEDIA | C3_1923 (2, 0.123) | trayectoria_escritores_creativos | 226.0° |

## Lecturas nuevas

1. **Tesla es el primer H1 que NO cambia al extender.** En las 6 anteriores (Arbuckle, Wilde, Rockefeller, Pasteur, Lincoln, Trotsky) el H1 cambió al dar más cortes. Tesla se queda en 22_todo_sacrificado_por_una_pasion. La estabilidad del H1 no es la norma: es la excepción (1 de 7).
2. **Lincoln voltea a lo oscuro.** De 12_obtencion (3 cortes) a 3_venganza_del_crimen (7 cortes), con 12_obtencion como H2. El asesinato final pesa más que la obtención cuando se cuenta la vida entera. Es el H1 más distinto de su apartado original.
3. **Trotsky: el H1 es una familia lateral.** mauss_01_intercambio_agonistico es de familias_tokens (no del 244) y llega a H1 con grado AJUSTADA — el grado más fuerte de esta tanda. Y su H2 es dumezil_f2_fuerza, el que más resiste en Napoleón. El par mauss+dumezil es el que más se jala y el que más resiste, juntos en el top.
4. **Trotsky tiene el Sol más débil medido: 0.6837.** Por debajo de Arbuckle (0.7092) y Wilde (0.6959). El Sol débil no impide la meseta ni la lectura (11 nudos, prop MEDIA).
5. **Utopia por primera vez RESISTE y por primera vez AUSENTE.** En Tesla, utopia_mentalidad_socialista RESISTE (pend 0.1071) — la primera utopia que resiste en 7 tandas. En Lincoln hay 0 nudos utopia — el primer caso sin utopia en los nudos. La regla "utopia siempre se jala" tiene sus primeras excepciones.
6. **Cometas tempranos.** Lincoln C2_1856 y Trotsky C3_1923 son cometas dentro del rango original de 3 cortes — el pulso grande llega antes de que se complete la vida. En los casos anteriores el cometa llegaba en C5–C9.
7. **El giro se sostiene en las 3: 221.0°, 236.1°, 226.0°.** Con las 4 anteriores (218–236°), ya son 7 casos a 7 cortes en la banda 218–236°. La constante ~220–245° aguanta en 17 de 18 casos en meseta con 7–10 cortes (solo TRANSICION2 fuera, 302.5°).

## Estado

- 7 biografías extendidas a 7 cortes en total (Arbuckle, Wilde, Rockefeller, Pasteur, Tesla, Lincoln, Trotsky): 7/7 en meseta, 7/7 con giro en banda, 6/7 con H1 cambiado, 1/7 con H1 estable (Tesla).
- Apartados cubiertos ahora: 22_todo_sacrificado (Tesla, estable), 12_obtencion (Lincoln → 3_venganza), 24_rivalidad (Trotsky → mauss_01).
- Quedan sin extender a 7 cortes: 36_perdida (Coolidge), anacyclosis_06_oclocracia (Caravaggio), tainter_03 (Pedro II), arquetipo_el_explorador (Luis XVI), schwartz_10_autodireccion (Disney), schwartz_07_logro (Carnegie, Durant, Dickens, Lavoisier, Lay, Ludwig II, McCarthy, Truman), 31_conflicto_con_un_dios (Catalina, David, Fouquet, Galilei, Khrushchev, Lesseps), 9_audaz_empresa (Chanel, Mendel, Wagner), 30_ambicion (Law, Pedro II).

## De dónde se alimentan los nudos: ¿sujeto o contexto? (pregunta de Marco, 2026-11-13 ~19:53 CST)

Hipótesis de Marco: los cometas/nudos/polvo tienen que ver con los tokens del CONTEXTO (C), no del sujeto (P) — las circunstancias, y por eso dan las posibilidades de en qué puede terminar.

Medición (proxy): para cada nudo, se suman los tokens de entrada que son favor de esa familia, por lado (P/A/C), ponderados por peso del token × peso favor en el catálogo 244. 7 casos, 51 nudos:

| caso | P (sujeto) | A (antagonista) | C (contexto) |
|---|---|---|---|
| ARBUCKLE | 41% | 39% | 20% |
| WILDE | 5% | 13% | **82%** |
| ROCKEFELLER | 44% | 39% | 17% |
| PASTEUR | **0%** | 58% | 42% |
| TESLA | **65%** | 11% | 25% |
| LINCOLN | 45% | 29% | 26% |
| TROTSKY | 27% | 12% | **61%** |
| **TOTAL** | **36.1%** | **28.1%** | **35.9%** |

Lectura: la hipótesis NO se confirma tal cual — en total los tres lados alimentan casi por igual (C ≈ P). PERO el reparto cambia por caso y es en sí una huella: Wilde y Trotsky sí son contexto (82%, 61%); Tesla y Rockefeller son sujeto (65%, 44%); Pasteur tiene CERO del sujeto (sus nudos vienen solo de A y C). Las posibilidades no vienen solo del contexto ni solo del sujeto: vienen de la MEZCLA P+A+C, y la mezcla es distinta en cada vida.

## ¿Hay repulsión? Núcleos que se alejan del Sol (pregunta de Marco, 2026-11-13 ~20:03 CST)

Pregunta: ¿hay nodos que se REPELEN? ¿Núcleos de familias que generan repelencia?

Método: para cada familia bajo top5 en los 7 casos 7C, pendiente de rango por corte (negativa = baja de rango, se aleja) y distancia de activación al Sol (primer vs último corte). 107 familias distintas bajo top5.

Resultado: **la repulsión es la MAYORÍA, no la excepción.** Por caso, 62–82% de las familias bajo top5 tienen pendiente negativa (Arbuckle 80%, Wilde 62%, Rockefeller 63%, Pasteur 82%, Tesla 69%, Lincoln 64%, Trotsky 65%). ~70% se aleja, ~17% se deja jalar (los nudos), el resto queda plano. La distancia al Sol de las repelidas CRECE (ej. 0.0 → 0.109). El Sol no jala todo: selecciona unas pocas y el resto se va.

Núcleo de REPULSIÓN (pend negativa en ≥3 de 7 casos, siempre que aparece):
- minsky_02_especulativa 5/5, social_01_asch_conformidad 5/5, social_14_overton_ventana 5/5, utopia_autonomia_atenas 5/5
- bbk_03_individualista 4/4, spengler_02_verano_otono_racionalizacion 4/4, weber_02_autoridad_carismatica 4/4, predictivo_02_mdp_politica_optima 4/4
- 12_obtencion 3/3, cliodinamica_04 3/3, mbti_factor_sensacion_s 3/3, monomito_02_llamado 3/3, monomito_06_pruebas 3/3, arquetipo_el_heroe 3/3, kwml_01_rey 3/3, utopia_principio_libertades 3/3
- dumezil (f3_fecundidad 4/6, desequilibrio_f2 3/5, desequilibrio_f3 3/5, f2_fuerza 3/5, f1_soberania 3/4) y utopia en general (abundancia_sybaris 4/5, mentalidad_liberal 3/4, principio_identidad_grupo 3/4, principio_mercado 3/5, principio_naturaleza 3/4, mentalidad_socialista 3/5, oficio_roma 3/4, principio_estado 3/4)

Núcleo de ATRACCIÓN (del análisis de tipos, siempre que aparece como nudo): utopia_mentalidad_milenarista, mauss_01, sombra, sistema, arquetipo_el_cuidador, jaldun_01, heroe.

Lectura: **utopia es el tipo más POLARIZADO: es el que más se jala (82% de sus nudos) y también uno de los que más se repele** (10 de sus familias en el núcleo de repulsión). O se acerca o se aleja, no se queda en medio. Dumezil igual: resiste como nudo y repele como no-nudo. La ley de atracción es SELECTIVA: el Sol captura unas pocas familias y el resto se aleja. Caveat honesto: la medición muestra que se alejan; si es repulsión activa o solo falta de combustible (sus tokens no están en la entrada) no lo resuelve esta medición sola.

## Matriz binaria atracción/repulsión (Marco 2026-11-13 ~20:20 CST: "suena a algún tipo de matriz binaria")

Construida: `motor/MATRIZ_BINARIA_ATRACCION_REPULSION_20261113.json` — 107 familias × 7 casos. Valor: 1 = atraída (es nudo en ese caso), 0 = repelida (pendiente de rango negativa), null = plana/ausente. Se excluye el Sol y el top5 de cada caso.

Resultado: **la matriz SÍ es binaria.** 81 de 107 familias (76%) son SIEMPRE el mismo valor cuando aparecen:
- Siempre 1 (atraídas): 9 — anacyclosis_03_aristocracia, minsky_01_cobertura, arquetipo_el_sabio, monomito_08_la_odisea, sustancias_03_severo, trayectoria_escritores_creativos, trayectoria_musicos_populares, trayectoria_posgrado_academicos, trayectoria_transportistas_turno_nocturno.
- Siempre 0 (repelidas): 72 — todo el núcleo frío (minsky_02_especulativa, social_01_conformidad, predictivo_02, monomito_02_llamado, monomito_06_pruebas, 12_obtencion, 9_audaz_empresa, arquetipo_el_bufon, bbk_03_individualista, cliodinamica_04, dumezil_f3_fecundidad, etc.).
- Mixtas (1 en unos casos, 0 en otros): 23 — dumezil_f2_fuerza, dumezil_desequilibrio_f2/f3, situacion_dramatica_ambicion, y varias utopias.
- Planas/sin dato: 3.

Utopia en la matriz (fila = caso Arbuckle, Wilde, Rockefeller, Pasteur, Tesla, Lincoln, Trotsky):
- utopia_autonomia_atenas: 0,0,0,–,0,–,0 (siempre repelida)
- utopia_mentalidad_socialista: –,–,0,0,1,0,1 (mixta, polarizada)
- utopia_principio_mercado: 0,–,1,0,1,0,– (mixta, polarizada)
- utopia_principio_identidad_grupo: 0,0,–,–,–,0,1 (casi siempre repelida)
- utopia_mentalidad_milenarista: –,–,–,–,0,–,0 (en estos 7 casos no es nudo; su jalón fuerte era en los 14 casos de meseta)

Lectura: la matriz binaria existe y es 76% fija. Lo que cambia de caso en caso son solo 23 familias — y ahí están dumezil y utopia. El resto del sistema es estable: lo que se jala, se jala siempre; lo que se repele, se repele siempre.

## ¿De qué depende que se jale o se aleje? El Sol decide (pregunta de Marco, 2026-11-13 ~20:28 CST)

Pregunta: ¿de qué depende que en algunas vidas lo jale y en otras lo aleje?

Método: para cada una de las 23 mixtas, comparar los Soles (H1) de los casos donde se jala (1) vs donde se aleja (0). Si los conjuntos no se traslapan, el Sol separa perfectamente.

Resultado: **el Sol separa en 19/23.** Cada familia tiene Soles con los que se jala y Soles con los que se aleja, sin traslape. Ejemplos:
- dumezil_f2_fuerza: JALA solo bajo monomito_08 (odisea, Arbuckle+Wilde); ALEJA bajo sabio, 22_todo_sacrificado, 3_venganza.
- utopia_principio_mercado: JALA bajo predictivo_02 (Rockefeller) y 22_todo_sacrificado (Tesla); ALEJA bajo monomito_08, sabio, 3_venganza.
- utopia_oficio_roma / principio_estado / mentalidad_liberal: JALAN solo bajo predictivo_02 (Rockefeller).
- utopia_mentalidad_socialista: JALA bajo 22_todo_sacrificado (Tesla) y mauss_01 (Trotsky); ALEJA bajo predictivo_02, sabio, 3_venganza.
- situacion_dramatica_ambicion: JALA bajo predictivo_02, 22_todo_sacrificado, 3_venganza; ALEJA bajo monomito_08, sabio, mauss_01.
- mbti_introversion_i: JALA bajo monomito_08 y 22_todo_sacrificado; ALEJA bajo predictivo_02.

Las 4 excepciones (24_rivalidad, cliodinamica_02, strauss_04_the_crisis, utopia_principio_naturaleza): Arbuckle y Wilde comparten el mismo Sol (monomito_08) pero la familia se comporta distinto en cada uno — ahí el Sol solo no alcanza; decide algo más fino de la configuración (los cortes, la mezcla P/A/C).

Lectura: el que jala o aleja a un tema mixto es el Sol que brilla en esa vida. No es la familia sola ni es azar: es el par (familia, Sol). Corrección de marco: los sueños SON poder (no dos bandos) y las familias no son individuos aislados: lo que decide es la configuración, y el Sol es la parte más gruesa de esa configuración.

## ¿Qué es lo nacido y cuándo se percibe? (pregunta de Marco, 2026-11-13 ~20:31 CST)

Pregunta: ¿qué vendría siendo lo nacido? ¿En qué momento sabemos qué es lo nacido? ¿Cuándo se desenvuelve y se empieza a percibir?

Método: (a) primera aparición de cada familia (en qué corte aparece por primera vez); (b) momento en que su dirección (pendiente de activación) ya coincide con la final y se mantiene. 7 casos 7C, familias bajo top5.

Primera aparición (media):
- ALEJA siempre (lo fijo que se va): 2.6 cortes; 57% ya en C1–C2, 75% en C1–C3.
- MIXTA (lo hecho): 2.9 cortes; 54% en C1–C2, 67% en C1–C3.
- JALA siempre (lo fijo que se acerca): 4.1 cortes; solo 20% en C1–C2, 53% en C1–C3, 67% en C1–C4.

Momento en que la dirección ya se sabe (mediana 3 cortes en las tres clases):
- ALEJA siempre: 65% ya en el corte 3, 87% en el 5, 99% en el 6 (media 3.4).
- JALA siempre: 53% en el corte 3, 73% en el 5 (media 4.1).
- MIXTA: 54% en el corte 3, 75% en el 5, 97% en el 6 (media 3.8).

Lectura: **lo nacido se percibe desde el principio** — lo que se aleja siempre ya está en los dos primeros cortes (media 2.6) y su dirección se sabe en el corte 3. **Lo que se jala aparece después** (media 4.1 cortes): emerge con la trayectoria, es lo que se va haciendo. Las mixtas aparecen temprano (2.9) pero su destino (jalarse o alejarse) lo decide el Sol de esa vida. Caveat: la pendiente con 2–3 puntos es ruidosa; el "momento" es cuando el signo ya no cambia, no una certeza absoluta.

## ¿Qué edad tienen esos cortes? (pregunta de Marco, 2026-11-13 ~20:34 CST)

Edad del sujeto en cada corte (fecha del corte − año de nacimiento; nacimientos: Arbuckle 1887, Wilde 1854, Rockefeller 1839, Pasteur 1822, Tesla 1856, Lincoln 1809, Trotsky 1879):

| caso | C1 | C2 | C3 | C4 | C5 | C6 | C7 |
|---|---|---|---|---|---|---|---|
| Arbuckle | 26 | 30 | 33 | 34 | 35 | 38 | 46 |
| Wilde | 37 | 41 | 41 | 41 | 43 | 44 | 46 |
| Rockefeller | 20 | 29 | 31 | 43 | 53 | 72 | 74 |
| Pasteur | 40 | 59 | 62 | 63 | 66 | 70 | 73 |
| Tesla | 28 | 37 | 45 | 50 | 59 | 70 | 87 |
| Lincoln | 37 | 47 | 49 | 51 | 54 | 55 | 56 |
| Trotsky | 39 | 43 | 44 | 48 | 57 | 59 | 61 |
| **MEDIA** | **32.4** | **40.9** | **43.6** | **47.1** | **52.4** | **58.3** | **63.3** |

- Corte 2.6 (primera aparición media de lo que siempre se aleja = lo nacido): **42.5 años** de media, rango 30–61.
- Corte 3 (donde ya se sabe la dirección): **43.6 años** de media, rango 31–62.
- Corte 4.1 (primera aparición media de lo que siempre se jala = lo hecho): **47.7 años** de media, rango 34–63.

Lectura: lo nacido se percibe en promedio a los ~42–44 años (los primeros 40, la mitad de la vida), y lo que se hace emerge hacia los ~48. Caveat: son 7 biografías adultas (el corte 1 ya es a los 20–40 años); el rango es ancho (30–62) y depende de la vida — no es una ley universal de edad, es el promedio de estos 7.
