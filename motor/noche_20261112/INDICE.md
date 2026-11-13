# ÍNDICE — Noche 2026-11-12: cableados y ejercicios del motor U6

**Rama:** `alterno/reconexion-2a1` (rama reserva/laterales).
**Fecha:** 2026-11-12 (CST). **Motor:** Engine `665c39a2…`, catálogo 244 `d827dcc3…`
(canónicos, NO tocados). **Nada de esto toca el Engine ni el 244 ni
`correr_estandar.py`.** Todo es lateral o diagnóstico (`can_decide_H: False`),
o entradas nuevas. Sin merge, sin PR: lo decide Marco.

**Por qué está aquí:** regla de reproducibilidad de Marco — si un modelo no
encuentra algo en el repo, es que no está guardado; las carpetas de la VM no
cuentan. Este índice es el punto de entrada para que otro modelo le explique
a Marco lo que se hizo esta noche.

## Cómo se reproduce una corrida (base de todo lo de abajo)

```bash
cd <copia-de-trabajo-del-motor>   # p. ej. motor-cameo/
STINKBOX_HOME=$PWD/STINKBOX_PERSISTENTE STINKBOX_STORAGE_ROOT=$PWD/STINKBOX_STORAGE \
  python3 motor/correr_estandar.py casos/precedentes/<CASO>/entrada.json <NOMBRE_CORRIDA>
```

Los laterales se auto-ejecutan desde la copia de trabajo y regeneran su
` *_resultado.json` (`python3 <lateral>.py`). Ojo: algunos tienen rutas
locales fijas a la copia de trabajo (constantes al inicio del archivo);
para reproducir desde otra ruta, ajustar esas constantes.

## 1. No-duplicación: un token no suma dos veces, activa la latencia

Verificado en código: el Engine aplica cada token a TODAS las familias que
lo tienen en favor (autoridad ×13 familias, sacrificio ×9). Medido en 5
casos: 140–203 eventos de apoyo por 84 ocurrencias de token (×1.67–×2.42).
La regla SÍ existe escrita (`capa_integracion_semantica_v1_2.py`) pero su
estado es PROPUESTA y el tablero nunca la toca.

- `motor/reconexion_v2a1/no_duplicacion_latencia.py` — lateral. Tablero sombra
  que recomputa p_final aplicando cada token UNA sola vez, a la familia que
  perfila por su compañía en el corte; sin compañía → frente de latencia.
  Reproduce: `python3 motor/reconexion_v2a1/no_duplicacion_latencia.py`
  (escribe `no_duplicacion_resultado.json`).
- `motor/reconexion_v2a1/no_duplicacion_resultado.json` — puerta PASA 5/5:
  con la regla apagada el tablero sombra reproduce los P_FULL_244 sellados
  exacto (0 diferencias). Con la regla encendida el trono muere en los 5
  (gobernante y rey caen a ~0.51); en Semmelweis y Kolbe el H1 sombra es
  `arquetipo_el_heroe`. Costo honesto: solo 31–51% de las ocurrencias llega
  a aplicarse; de 102 frentes solo 2 se resolvieron.
- `motor/reconexion_v2a1/sombra_tableros_<CASO>.json` (5: Juana, Tubman,
  Mandela, Semmelweis, Kolbe) — tableros sombra por corte que alimentan la
  rueda y la vinculación.
- `motor/noche_20261112/NO_DUPLICACION_VERIFICACION_20261112.md` — reporte.

## 2. Rueda de conjunción (teoría del color): el héroe es un solo color

La teoría del color v1 ya corría en las 5 corridas; la mezcla final es GRIS
en todos los casos. La rueda nunca se había dibujado para los héroes.

- `motor/laterales/teoria_color/rueda_conjuncion.py` — lateral. Dibuja la
  rueda polar (matiz = dirección PAC, croma = distancia al gris) en el
  tablero canónico y en el tablero sombra, y detecta pares complementarios,
  análogos y pigmentos idénticos.
  Reproduce: `python3 motor/laterales/teoria_color/rueda_conjuncion.py`
  (escribe `rueda_conjuncion_resumen.json`).
- `motor/COLOR_SOMBRA_<CASO>.json` (5) — colores del tablero sombra.
- `motor/noche_20261112/RUEDA_CONJUNCION_VERIFICACION_20261112.md` — reporte.
- `motor/noche_20261112/rueda_conjuncion_resumen.json` — resumen por caso.
- Lo que conjuga: en el canónico limpio las tres familias héroe son un solo
  color con tres nombres (Δmatiz ≤6°); el trono es el polo complementario
  canónico y en la sombra la oposición muere (0–1 pares); la latencia
  desatura y funde todo lo que perdió su evidencia en UN pigmento gris
  idéntico por caso. Lo que NO conjuga: la mezcla sigue gris y el RADIO
  (ruptura del margen) no tiene dimensión en el plano cromático — esa
  conjunción sigue pendiente.
- Las 10 figuras PNG de las ruedas NO se subieron: `push_files` solo acepta
  UTF-8; quedan en la copia de trabajo
  (`motor/laterales/teoria_color/RUEDA_CONJUNCION_<CASO>_{canonico,sombra}.png`).

## 3. Cuartos del monomito

Los cuartos Q1–Q4 son ETIQUETAS sobre una rejilla de 12 etapas, no familias
(no existe ninguna familia separacion/descenso/ordeal/cuadrante/ciclo en el
244). Los tokens flotan libres en el tiempo: el cuarto no cambia lo que el
token significa.

- `motor/laterales/teoria_color/cuartos_monomito.py` — marca los cuartos en
  la rueda. Reproduce:
  `python3 motor/laterales/teoria_color/cuartos_monomito.py --color motor/COLOR_SOMBRA_SEMMELWEIS_HEROE_SIN_TRONO_20261112.json --result motor/RESULT_SEMMELWEIS_HEROE_SIN_TRONO_20261112.json --out <reporte>.md`
- `motor/noche_20261112/CUARTOS_MONOMITO_SEMMELWEIS_20261112.md` — reporte.

## 4. Cierres en estructuras dramáticas: trabajo de TOKENS, no de reglas

- `motor/laterales/cierre_dramatico/cierre_tokens.py` — lateral. Inventario
  de 26 tokens de cierre contra el catálogo y contra 81 entradas.
  Reproduce: `python3 motor/laterales/cierre_dramatico/cierre_tokens.py`
  (escribe `cierre_tokens_resultado.json`).
- `motor/laterales/cierre_dramatico/cierre_tokens_resultado.json`
- `motor/noche_20261112/CIERRE_DRAMATICO_VERIFICACION_20261112.md` — reporte.
- Hallazgo: 11 tokens de cierre NO EXISTEN en ningún lado (cierre,
  desenlace, anagnorisis, peripeteia, regreso, elixir, legado, testamento,
  despedida, culminacion, clausura); `reconocimiento` es un token al revés
  (el más presente, 44/81 entradas, y no favorece a nadie, pero 6 de 7
  desenlaces sellados lo piden como favor). 19 de 36 situaciones Polti SIN
  CASO. Veredicto PROPUESTA: lado catálogo, añadir como favor `legado`,
  `reconocimiento`, `cierre`/`desenlace` (decide Marco, toca el 244); lado
  entrada, que el LM emita los tokens de cierre que ya existen como favor
  cuando los hechos lo ameriten (cambio a `CONTRATO_ENTRADA_LLM.txt`).

## 5. Vinculación de tokens: la ecuación del desplazamiento

- `motor/laterales/vinculacion_tokens/vinculacion.py` — lateral. Contrato V1:
  token↔token por familias compartidas y co-ocurrencia; token↔familia
  resuelto por compañía o en SUPERPOSICIÓN (eso ES el frente de latencia);
  desplazamiento Δ = L(c+1) − L(c), dirección = la familia que más vínculo
  gana; registro de retornos, reapariciones y vínculos recuperados.
  Reproduce: `python3 motor/laterales/vinculacion_tokens/vinculacion.py`
  (escribe `vinculacion_resultado.json`).
- `motor/laterales/vinculacion_tokens/vinculacion_resultado.json`
- `motor/noche_20261112/VINCULACION_TOKENS_VERIFICACION_20261112.md` — reporte.
- Veredicto: da pauta, no ley — 3 de 5 en dos transiciones, 1 de 5 en una.
  Falla cuando el H1 es un pulso que ya salió (Juana) o cuando domina un
  cambio de signo (Tubman). Lo cíclico, medido: 215 retornos, 185
  reapariciones, 638 cambios de sentido, 35 vínculos resueltos recuperados.

## 6. Navaja de Ockham en la regla operativa

("Vaca de ojama" era navaja de Ockham, dictado deformado.) Verificado: cero
menciones de Ockham/navaja en todo el motor y el workspace antes de esto.

- `motor/REGLA_OPERATIVA_OCKHAM_20261112.md` — la navaja como regla
  operativa (sin tocar el RUTEO sellado de 2026-09-14): no multiplicar
  mecanismos más allá de lo necesario; si una lectura existente ya mide lo
  que el mecanismo nuevo mediría, el nuevo no se construye; si dos lecturas
  empatan, se queda la más simple; todo lateral nuevo debe nombrar qué mide
  que nada existente mida. Cinco criterios operativos. Conectada con el
  RUTEO y con Sherlock.
- `motor/noche_20261112/OCKHAM_VINCULACION_AUDITORIA_20261112.md` — auditoría
  Ockham de la vinculación + chequeo Sherlock. Se corta: el grafo
  token↔token (82 aristas, la pauta nunca lo lee), el reparto proporcional
  de la superposición (suposición, no medición), lo cíclico como criterio
  aparte, la reimplementación de frentes. Sobrevive solo el desplazamiento
  Δ + argmax. Prueba ejecutada: la forma mínima reproduce el veredicto
  exacto 3/5, mismo argmax, mismos deltas. Forma mínima = PROPUESTA, no
  implementada. Sherlock humano: auto LIMPIO en los 5, pero la línea humana
  levanta una alarma que el auto no ve — en Kolbe `monomito_05` cuatro
  cortes seguidos (C3–C6) y el auto solo mira los primeros 4 tops.
  Sigue en cuaderno: sí.

## 7. Auditoría de activación de laterales

- `motor/noche_20261112/AUDITORIA_ACTIVACION_LATERALES_20261112.md` +
  `auditoria_activacion_laterales.json` (219 filas) +
  `auditoria_activacion_evidencia.json` — qué está activo, en diagnóstico
  por diseño, cableado pero no activado, no cableado o desconocido.
  Resumen: (a) activos 71, (b) diagnóstico por diseño 98, (c) cableados
  pero no activados 18, (d) no cableados 20, (e) desconocidos 12. La
  mayoría de lo que parece apagado no está apagado — está en (b).
  Pregunta abierta: `plugin_pregunta_detras_v2` dice "No cablear al limpio
  sin OK de Marco" pero el motor lo carga y lo llama — ¿existe el OK?
- `motor/noche_20261112/auditoria_activacion.py` y
  `clasificar_auditoria.py` — scripts de la auditoría.
  Reproduce: `python3 auditoria_activacion.py` (desde la copia de trabajo).

## 8. Cadena Caldero con pistas (por su hilo, el contrato de entrada)

- `motor/noche_20261112/CADENA_CALDERO_PISTAS_VERIFICACION_20261112.md` —
  reporte. Las 5 pistas de Gemini pasan el guardián 5/5; H1 se voltea
  sabio→sacrificio por el lateral de vecinos, NO por el desempate del
  cierre (en modo 020 las `llm_hint_scores` son traza lateral). Vecinos
  74→91 (86 web + 5 pistas); la web sigue inerte (0/86 mapea al 244).
  `current_neighbors` [] en las dos corridas. Predictor 0 candidatos en
  las dos. **La variante de tres campos NO corre: `external_lights` en la
  forma del contrato ROMPE la corrida (KeyError: 'branch' en interrelación,
  MOTOR:2451) — la reparación mínima sería `"branch": "capa2"`, decisión
  de Marco.** `caldero_search_sources` no las lee el sidecar. "Qué suele
  suceder" (prosa del LM) no tiene consumidor en el motor.

## 9. Sondas helicoidales, mortalidad, presupuesto y perfiles de quema

- `motor/noche_20261112/TRAZABILIDAD_HELICOIDAL_EJE_20261112.md` +
  `sonda_helicoidal_reporte.json` + `sonda_helicoidal_v2_reporte.json` —
  la vectorización del motor es PLANA (sin radio, sin ángulo, sin avance);
  la sonda v2 infiere el eje (inclinado 46.3° Mozart, 67.5° Napoleón
  respecto al PC1) y gana en todo lo geométrico, pero el top-5 de familias
  que suben sigue 0/5. Ruptura de margen en Mozart y Noether; no en
  Napoleón y Carson. La ruptura marca el final (la muerte), no su sabor.
- `motor/noche_20261112/barrido_mortalidad_reporte.json`,
  `presupuesto_tokens_reporte.json`, `perfiles_quema_reporte.json` —
  el radio crece hacia el final en 15 y se contrae en 20 (de 35 casos);
  NO hay número fijo de usos de tokens antes del final; los tres perfiles
  de quema existen (plano 18, quema al final 8, quema al inicio 9) y el
  plano trae MÁS fatalidad (11/18).
- Scripts: `sonda_helicoidal.py`, `sonda_helicoidal_v2.py`,
  `sonda_noether.py`, `barrido_mortalidad.py`, `presupuesto_tokens.py`,
  `perfiles_quema.py`. Reproduce: `python3 <script>.py` desde la copia de
  trabajo (leen los RESULT locales).
- FALTA: `sonda_carson.py` nunca se escribió en la VM; la sonda de Carson
  se corrió adaptando la de Noether. No se inventó un archivo.

## 10. Entradas (casos nuevos, 7 cortes c/u)

`casos/precedentes/<CASO>/entrada.json`. Hechos de biografía establecida,
fechas de corte aproximadas por punto medio (anotadas en `source_notes`),
desenlace SOLO en `source_notes`, SIN puente Caldero placeholder.
Formato: P/A/C como LISTA de pares [token, peso] (un diccionario es
rechazado con TOKEN_INVALIDO).

| Caso | Z (C7) | Desenlace sellado | H1 original |
|---|---|---|---|
| NOETHER_CIEGO_Z90_20260914 | 1932 | HIT + muerte 1935 | gobernante (FRÁGIL; trampa del letrero de prestigio) |
| CARSON_CIEGO_Z90_20260914 | 1962 | HIT + muerte 1964 | creador (AJUSTADA) |
| JUANA_DE_ARCO_HEROE_20261112 | 1430 | quemada 1431, trágico | gobernante |
| TUBMAN_HEROE_20261112 | 1902 | muere 1913, generativo | gobernante |
| MANDELA_HEROE_20261112 | 1997 | muere 2013, generativo | rey |
| JUANA/TUBMAN/MANDELA_HEROE_SIN_C7_20261112 | 6 cortes | mismo desenlace | gobernante en los 3 (la trampa está en C1..C6, no es artefacto del C7) |
| SEMMELWEIS_HEROE_SIN_TRONO_20261112 | 1861 | asilo 1865, muere 1865 | sabio (FRÁGIL); las 3 familias héroe en el techo 0.8013 |
| KOLBE_HEROE_SIN_TRONO_20261112 | 1941 | canonizado 1982 | 20_sacrificio (FRÁGIL) |
| SEMMELWEIS_HEROE_SIN_TRONO_CON_PISTAS_20261112 | 1861 | mismo | variante con pistas Caldero + fuentes + luces (ver §8: NO corre, KeyError 'branch') |
| SEMMELWEIS_HEROE_SIN_TRONO_SOLO_HINTS_20261112 | 1861 | mismo | variante solo con las 5 pistas (corre; H1 sacrificio) |

- `motor/noche_20261112/EVALUACION_SEMMELWEIS_20261112.json` — paquete de
  evaluación de la corrida original de Semmelweis (exit 0, recibo
  COMPLETED, 65.852 s, MC 21/21, 13,027 sims).
- `motor/noche_20261112/RERUN_SEMMELWEIS_COMPARACION_20261112.md` — la
  re-corrida sin pistas TAMBIÉN voltea H1 a sacrificio (29.222 vs sabio
  29.099, margen 0.123): por el ambiente (84 vecinos web, StinkBox
  creció), no por las pistas. Dos caminos distintos, mismo volteo, dentro
  de lo frágil. El núcleo (tablero P, dX, color) reproduce exacto; lo que
  se mueve es la fusión, que lee estado vivo.
- `motor/noche_20261112/matriz_finales_arquetipo.json` (+ script
  `matriz_finales_arquetipo.py`) — matriz de finales por arquetipo/H1
  (22 H1 distintos, 44 casos tras los héroes).

## 11. Scripts de construcción y ejercicio

- `motor/noche_20261112/convertir_noether_carson.py` — convierte los 2
  casos ciegos sellados del checkpoint ZIP (09_CIEGOS_Z90_SELLADOS) al
  formato CAL actual.
- `motor/noche_20261112/construir_heroes.py` — construye las 3 entradas
  de héroes (Juana, Tubman, Mandela) + sus variantes SIN_C7.
- `motor/noche_20261112/construir_heroes_sin_trono.py` — construye
  Semmelweis y Kolbe sin tokens de trono (con aserción automática).
- `motor/noche_20261112/ejercicio_predictibilidad_2a1.py` — ejercicio de
  predictibilidad contra `desenlace_sellado.json`
  (`python3 ejercicio_predictibilidad_2a1.py [F001|...]`).
  Hallazgo: el cuello no es el peso de predictibilidad — solo 27 de 139
  familias del desenlace están en la lista de 11 candidatas; el problema
  está río arriba (rank_fusion).

## Qué quedó FUERA (y por qué)

- **RESULT crudos (11–13 MB c/u):** fuera por el límite de tamaño; los
  reportes ya los referencian por SHA-256 (precedente F003/F004).
- **Figuras PNG de las ruedas** (10): binarias; `push_files` solo acepta
  UTF-8. Quedan en la copia de trabajo.
- **Estado del StinkBox** (`STINKBOX_PERSISTENTE/`, `STINKBOX_STORAGE/`):
  estado vivo, no es código ni entrada; no se sube.
- **`sonda_carson.py`:** nunca existió en la VM (ver §9).
- **`__pycache__/` y `.pyc`:** nunca se suben.

## Decisión de layout

Se preservan las rutas `motor/` y `casos/precedentes/` de la copia de
trabajo. En la rama ya existía `motor/laterales/` (filogenia_mezcla,
teoria_color) y `casos/` en la raíz (35A_ESTUDIO, calibracion, ciegos,
fabrica, resultados); `casos/precedentes/` se crea nuevo bajo ese `casos/`.
Los reportes y scripts van a la carpeta nueva `motor/noche_20261112/`
(junto a los laterales), para que todo lo de esta noche quede junto y con
este índice como puerta de entrada. `motor/reconexion_v2a1/` no existía en
la rama: se crea con el lateral de no-duplicación y sus tableros sombra.

## Cableado del Caldero (subido después, 2026-11-13 ~01:15 CST)

- **CABLEADO_CALDERO_20261112.md**: por qué el Caldero "no estaba cableado" — nada se descableó, nunca se cableó completo (4 contratos contradictorios).
- **CABLEADO_CALDERO_VERIFICACION_20261112.md**: los 5 cables, puerta PASA en las 3 corridas cableadas (tablero P idéntico, Engine y 244 intactos).
- Los archivos cableados suben en esta misma entrega: `motor/correr_estandar.py` (cables 1 y 4), `motor/motor/MOTOR_V15_3_UNICO_20260927.py` (cables 2, 2b, 3 y 5), `motor/capa_llm/consulta_dirigida_v1.py` (adaptador Gemini + corrección Q_ANIO).
- **Corrección Q_ANIO (2026-11-12 ~22:58 CST, después del reporte de verificación):** la regla rechaza la entrada del dato del año, no la pregunta. La plantilla ya no mete el año ("corte C1", no "C1_1831") y el prompt tampoco lo lleva. Verificado: 28 preguntas, 0 rechazadas, 18 respuestas aceptadas; H1 sacrificio / H2 sabio, frágil.
- Queda pendiente la decisión de Marco sobre los cuartos: ¿un contra cuenta como evidencia de etapa?
