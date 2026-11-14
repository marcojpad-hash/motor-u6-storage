# Genios de niño — cortes de infancia (2026-11-13)

## Pregunta de Marco
"Arma con cortes de niños... nadie nace a los cuarenta años." Las entradas de adultos empiezan a los ~32 años y la dirección se sabía en el corte 3, a los ~43 años. ¿Se ve lo nacido desde la infancia (5-10 años) o de veras aparece a los 43?

## Entradas (13, todas _NINO_7C, 7 cortes, tokens solo vocabulario CAL 197, pesos 0.60-0.84)
PAGANINI (C1 6 años), MENDELSSOHN (4), CHOPIN (6), LISZT (9), MENUHIN (4), ALKAN (6), BELLINI (3), PURCELL (5), PASCAL (11), SIDIS (1), KRIPKE (6), PICASSO (7), MOZART-niño (4). Hechos reales verificados por búsqueda web; correcciones de fechas documentadas en los reportes de cada tanda (ej. Pascal C1 a los 11 no a los 8; Sidis conferencia a los 11 no a los 9; Paganini nace 1782 no 1784).

## Corridas (13/13, RESULT + RECIBO)
Las 13 completaron. Cada corrida llegó al timeout de 120 s del script (exit=124) DESPUÉS de escribir RESULT (10-11 MB) y RECIBO completos — el proceso se queda colgado en algo posterior; el RESULT es completo (H1, H2, 7 cortes, movimiento_de_fondo). Un reinicio del runtime mató el script en PICASSO; se re-corrieron PICASSO y MOZART a mano.

## Gravedad (10/13 en meseta; 8 con prop)
| caso | H1 | Sol | nudos | prop | cometa |
|---|---|---|---|---|---|
| PAGANINI | 9_audaz_empresa | — | 0 | — | — (CONTINUIDAD_ASCENDENTE) |
| MENDELSSOHN | 30_ambicion | — | 0 | — | — (CONTINUIDAD_ASCENDENTE) |
| CHOPIN | 9_audaz_empresa | — | 0 | — | — (CONTINUIDAD_ASCENDENTE) |
| LISZT | frye_mythos_romance | 0.7786 | 2 | — | C4_1824 (1, 0.077) |
| MENUHIN | arquetipo_el_creador | 0.6702 | 5 | +0.685 BAJA | C3_1926 (1, 0.127) |
| ALKAN | arquetipo_el_creador | 0.6611 | 7 | −0.093 BAJA | C4_1826 (5, 0.416) |
| BELLINI | 30_ambicion | 0.7958 | 6 | −0.145 BAJA | C5_1819 (5, 0.459) |
| PURCELL | schwartz_07_logro | 0.6997 | 8 | +0.127 MEDIA | C3_1673 (2, 0.136) |
| PASCAL | arquetipo_el_creador | 0.7591 | 5 | +0.711 BAJA | C3_1639 (2, 0.199) |
| SIDIS | arquetipo_el_creador | 0.6381 | 2 | — | C2_1906 (0, 0.0) |
| KRIPKE | spengler_02 | 0.7952 | 7 | +0.484 BAJA | C2_1949 (2, 0.179) |
| PICASSO | arquetipo_el_creador | 0.82 | 7 | −0.687 BAJA | C5_1900 (1, 0.154) |
| MOZART-niño | arquetipo_el_creador | 0.7511 | 10 | +0.095 MEDIA | C3_1763 (7, 0.61) |

- arquetipo_el_creador es H1 en 6 casos (Menuhin, Alkan, Pascal, Sidis, Picasso, Mozart-niño).
- Los 3 sin meseta (Paganini, Mendelssohn, Chopin) no estabilizan su tema central antes de los 20-24 años: CONTINUIDAD_ASCENDENTE.
- Cometas tempranos: Mozart C3 (7 nudos, 0.61, el más grande de los 13), Alkan C4 (5, 0.416), Bellini C5 (5, 0.459).

## ¿Lo nacido se ve de niño? SÍ — a los ~13 años, no a los 43
Matriz binaria NINO (10 en meseta, 121 familias): siempre jala 0, siempre aleja 73, mixtas 33; fijas 60% (adultos: 76%).
- Primera aparición: lo que siempre se aleja aparece en el corte 3.3 de media, a los **12.7 años** (adultos: corte 2.6, 42.5 años). Las mixtas: corte 3.5, 13.1 años.
- Momento en que la dirección ya se sabe: corte 3.7 de media (mediana 3), a los **13.8 años** (adultos: corte 3, 43.6 años); 52% ya en el corte 3.
- **La constante es el NÚMERO DE CORTE (3), no la edad.** Con cortes de niño, lo nacido se ve a los ~13 años; con cortes de adulto, a los ~43. El 43 era un artefacto de entradas que empiezan a los 32 años. Nadie nace a los cuarenta años.

## Lo que se jala es cosa de adultos
En niños NO hay ninguna familia que siempre se jale (0 vs 9 en adultos: sabio, monomito_08, minsky_01, trayectorias...). El núcleo de atracción (siempre jalado) es un fenómeno adulto: en la infancia todo es o siempre repelido (73) o mixto (33).

## La clase nacido/hecho depende de la ventana de vida
45 de 89 familias comunes cambian de clase entre adultos y niños (ej. arquetipo_el_sabio: adultos=1 → niños=mixta; minsky_01_cobertura: 1 → 0; sustancias_03: 1 → 0; predictivo_02: 0 → mixta; schwartz_07_logro: 0 → mixta). El reparto nacido/hecho no es fijo por familia: depende de la ventana de la vida que se mira.

## El giro se sostiene en niños
Giro helicoidal v1 (PCA 2 comp., P_FULL_244): media 233.8°, 10/13 en banda 217–252° (Paganini 214.4°, Picasso 216.5° apenas abajo; Liszt 266.3° arriba). Mozart-niño 222.9° (el adulto 224.2°). La constante geométrica no depende de la edad de los cortes.

## Tablas
- motor/GRAVEDAD_NINO_7C_20261113.json (gravedad de las 13)
- motor/MATRIZ_BINARIA_NINO_20261113.json (121 familias × 10 en meseta)
- motor/GIRO_NINO_7C_20261113.json (giro de las 13)
