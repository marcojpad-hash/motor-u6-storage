# No duplicación con latencia — verificación (2026-11-12)

Lateral: `motor/reconexion_v2a1/no_duplicacion_latencia.py`
(resultado JSON: `motor/reconexion_v2a1/no_duplicacion_resultado.json`)
No se tocó Engine, ni 244, ni correr_estandar, ni RESULT/entradas.
Solo lectura de RESULTs sellados + entradas + catálogo.

## La puerta de cordura: PASA

Con la regla APAGADA, el tablero sombra reproduce los P_FULL_244
sellados **exacto: 0 valores distintos, diferencia máxima 0.0** en los
5 casos (7 cortes × 3 ejes × 244 familias = 25.620 valores por caso).
La maquinaria es fiel; lo que cambia con la regla encendida es solo
la regla. El `p_azar_t` no se inventó: se recuperó del RESULT sellado
por intersección de intervalos sobre las 244 familias (ancho máximo
del intervalo 0.00035).

## Tabla por caso (H1 sombra = mayor p_final sombra en el corte Z, nivel tablero)

| Caso | H1 canónico | H1 sombra | p | Factor duplicación | Frentes latencia |
|---|---|---|---|---|---|
| Juana | gobernante | 36_pérdida_de_los_seres_queridos | 0.8011 | 2.42 → 0.38 | 23 (0 resueltos) |
| Tubman | gobernante | schwartz_02_benevolencia | 0.8124 | 2.01 → 0.43 | 18 (0 resueltos) |
| Mandela | rey | frye_mythos_romance | 0.7285 | 2.42 → 0.31 | 22 (0 resueltos) |
| Semmelweis | sabio | **arquetipo_el_heroe** | 0.8122 | 1.74 → 0.48 | 20 (1 resuelto) |
| Kolbe | 20_sacrificio | **arquetipo_el_heroe** | 0.8123 | 1.67 → 0.51 | 19 (1 resuelto) |

Eventos de apoyo (favor): Juana 203→32, Tubman 169→36, Mandela
203→26, Semmelweis 146→40, Kolbe 140→43. Eventos contra:
70→13, 62→12, 78→13, 61→10, 68→8.

## Qué cambia

- **El trono muere en los 5.** El gobernante cae a ~0.51 (rango
  74–75) y el rey a ~0.51 (rango 168–171). El H1 canónico queda en
  el piso del tablero sombra en todos los casos. La trampa del trono
  era el peso duplicado de autoridad (×13) y liderazgo (×6): sin
  duplicar, nunca encuentran compañía discriminante y se van a
  latencia.
- **El héroe corona en los 2 casos limpios.** En Semmelweis y Kolbe
  el H1 sombra es arquetipo_el_heroe (0.8122 / 0.8123), con `heroe`
  en 3er lugar (0.6764 / 0.7934). Ahí la entrada sí trae valentía +
  defensa_debil: la defensa es discriminante (solo alimenta a
  arquetipo_el_heroe) y la valentía se le asigna por compañía con
  ella. En Semmelweis la latencia funcionó una vez: valentía abrió
  frente en C6 y se resolvió en C7 hacia arquetipo_el_heroe.
- **El héroe NO corona en los 3 líderes.** Juana, Tubman y Mandela
  quedan con las tres familias héroe en el piso (~0.51). Su único
  token héroe es el sacrificio (×9 familias) y nunca encuentra
  compañía discriminante — el valor no aparece en sus entradas — así
  que se va a latencia en todos los cortes. El H1 cae entonces a lo
  que queda con tokens discriminantes: la pérdida, la benevolencia,
  el romance. Son lecturas con sentido, pero no son el héroe.

## El costo (honesto)

- **El tablero se queda con hambre.** Solo el 31–51% de las
  ocurrencias de tokens llega a aplicarse a alguna familia. El resto
  se va a latencia y casi nunca vuelve: **de 102 frentes abiertos en
  los 5 casos, solo 2 se resolvieron** (valentía en Semmelweis,
  rutina en Kolbe). La latencia, como está diseñada, es más un
  sumidero que un aplazamiento: la compañía que faltaba en un corte
  suele seguir faltando en los siguientes, porque los compañeros
  discriminantes son tokens raros que casi no aparecen.
- **El contra casi desaparece.** Los eventos contra caen de ~70 a
  ~10 por caso: los tokens contra también se van a latencia. El
  tablero sombra queda casi solo a favor, y por eso sus valores
  máximos (0.8124) superan el techo canónico (0.8013).
- **El H1 sombra es por p_final, no por rank_fusion.** El
  rank_fusion del motor no se reimplementó (no es importable
  limpio). La comparación es a nivel tablero. La caída del trono
  al piso y la coronación del héroe en los limpios son robustas a
  eso; el H1 exacto en los 3 líderes (pérdida, benevolencia,
  romance) es lectura de tablero, no veredicto del motor.

## Decisiones de diseño (por cercanía al código del Engine)

- Contra: una ocurrencia cuenta una sola vez. Si el token tiene
  favor, la asignación es por compañía favor y el contra de esa
  ocurrencia se suprime. Si solo tiene contra, se asigna por
  compañía contra (misma lógica) o va a latencia.
- Compañía: sobre TODO el corte (P+A+C), no solo el eje del token.
  Peso de compañía = peso de entrada del compañero (máximo si
  aparece en varios ejes). La decisión es por (token, corte).
- delta_min, sigma y p_azar se calculan sobre la lista completa de
  marcadores del eje, como los ve el Engine; lo único que cambia es
  a qué familia apoya cada token.
- Cuello top-5: verificado no-op (todas las entradas traen ≤5
  tokens por eje). Cuarentena: suma 0 en todos los casos (ningún
  token de entrada está en la lista de cuarentena).

## Veredicto

La regla sola **no corona al héroe**. Lo que hace es **matar el
trono en los 5 casos** y coronar al héroe **donde la entrada ya
trae sus tokens discriminantes** (valentía + defensa_debil en
Semmelweis y Kolbe). Donde el héroe solo tiene un token compartido
sin compañía (sacrificio en los 3 líderes), la regla lo deja en el
piso y el H1 cae a otra familia. La regla es necesaria para quitar
la trampa, pero no suficiente: el héroe necesita sus propios tokens
discriminantes en la entrada, o la latencia necesita resolver de
verdad (hoy resuelve 2 de 102 frentes). El siguiente paso, si se
quiere, es ese: que la latencia resuelva por persistencia y no solo
por compañía en el corte.
