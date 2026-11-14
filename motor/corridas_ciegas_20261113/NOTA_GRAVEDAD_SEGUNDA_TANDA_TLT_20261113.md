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
