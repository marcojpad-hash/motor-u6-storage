# AUDITORÍA — Respuestas de Grok y ChatGPT al paquete Oráculo / Parábola / Cableado

Fecha: 2026-11-12 ~04:42–04:52 CST. Auditora: Pecas.
Contexto: el 2026-11-12 ~03:33 CST se envió a Grok y a ChatGPT el paquete
(oráculo externo v1, parábola por familia, cableado de la multicapa).
Ambos contestaron y ambas respuestas se entregaron a Marco. Marco pidió
auditar qué alucinaron o infirieron mal, como si fuera una historia, en vez
de revisar el motor. Esta auditoría se hizo LEYENDO EL MOTOR (código y
RESULTs sellados), no de memoria. Cada punto trae su evidencia: archivo,
líneas y valores exactos.

Copia de trabajo: `~/workspace/u6-alterno/motor-cameo/`
Archivos base:
- `motor/RESULT_MOZART_CIEGO_C9.json` (ciego, C1..C9)
- `motor/RESULT_MOZART_Z90_PRECEDENTE.json` (completo, C1..C10)
- `motor/RESULT_NAPOLEON_CIEGO_C9.json` (ciego, C1..C9)
- `motor/RESULT_NAPOLEON_Z90_10CORTES.json` (completo, C1..C10)
- `motor/motor/plugin_circulo_monomito_v2.py` (el plugin del cuadrante)
- `motor/motor/observador_externo_v1.py` (el observador)

## 1. La "inestabilidad" del cuadrante — INVENTADO (diagnóstico equivocado)

Afirmación de ambos modelos: el cuadrante del mismo corte cambia entre
corridas (Mozart C9: ciega Q2, completa Q1) y eso es inestabilidad que hay
que estabilizar repitiendo corridas idénticas.

Lo que dice el motor:

(a) El cuadrante NO es función solo de los tokens del corte. En
`plugin_circulo_monomito_v2.py:61-153` (`posicion_por_corte`), los tokens de
resolución son `tokens_base + caldero_neighbors` (líneas ~74-77): los tokens
del corte MÁS los vecinos del Caldero que se inyectan EN ESA CORRIDA. El
docstring lo dice: "Resolve Q1-Q4 with the frozen cut tokens plus CURRENT
Caldero neighbors" y "Caldero memory is not treated as current evidence
merely because it persists". La inyección de vecinos es POR DISEÑO
dependiente de la corrida.

(b) Mozart C9 tiene los MISMOS tokens en las dos corridas (leído del
`features/plugin_circulo_monomito/posicion_monomito_por_corte` de ambos
RESULTs):
- tokens_corte: ['rebeldia', 'desafio_autoridad', 'independencia',
  'creatividad', 'ambicion'] — idénticos en ciega y completa.
- Ciega: caldero_neighbors_actuales = ['aprendizaje'],
  caldero_inyectado_en_resolucion = True → cuadrante_activo = ['Q2'].
- Completa: caldero_neighbors_actuales = [],
  caldero_inyectado_en_resolucion = False → cuadrante_activo =
  ['Q1', 'Q2'] (EMPATE en el máximo de solapamiento).

(c) El empate lo colapsa el observador: `observador_externo_v1.py` toma
`activos[0]`. En la completa, Q2 SIGUE AHÍ, segundo en la lista. El
"cambio de Q2 a Q1" es en parte obra del observador al tomar el primero
de un empate.

(d) En Napoleón el cuadrante es ESTABLE entre corridas:
- C9 ciega: ['Q2'] solo. C9 completa: ['Q2'] solo. C10 completa: ['Q2'] solo.
- No hay empate, no hay cambio. Los modelos generalizaron de UN caso
  (Mozart C9) a "inestabilidad" general.

(e) La propuesta de ChatGPT ("repetir corridas idénticas y comprobar que el
cuadrante no cambie") no detectaría esto: ciega y completa NO son corridas
idénticas (distinto Z, distinta lista de cortes, distinta búsqueda del
Caldero). Repetir idénticas daría lo mismo.

VEREDICTO: el diagnóstico de "inestabilidad" es inventado. Lo real es:
la inyección de vecinos hace el cuadrante dependiente de la corrida, y el
empate se colapsa a un solo valor. El pasado (los tokens del corte) NO
cambia. La afirmación de ChatGPT "si el pasado cambia entre corridas no
hay base estable para proyectar" es FALSA: los tokens de C9 son idénticos
en ambas corridas.

## 2. La regla de Grok: "al menos tres cortes de velocidad positiva" — REFUTADA por medición

Afirmación de Grok: la iluminación (dos subidas seguidas) no bastó; hace
falta al menos tres cortes de velocidad positiva o un umbral de magnitud.

Medición (traza `motor.annex.traza_P.crudo_P`, velocidades por corte):

Napoleón — las 5 iluminadas en el ciego:
- dumezil_f3_fecundidad: v67=-0.0081, v78=+0.0206, v89=+0.0157 → NO 3 seguidas → C10 BAJÓ (-0.0207)
- minsky_02_especulativa: v67=-0.0045, v78=+0.0163, v89=+0.0146 → NO 3 seguidas → C10 BAJÓ (-0.0126)
- 19_asesinato_de_un_pariente_no_reconocido: v67=-0.0430, v78=+0.0089, v89=+0.0192 → NO 3 seguidas → C10 BAJÓ (-0.0023)
- utopia_abundancia_sybaris: v67=-0.0027, v78=+0.0105, v89=+0.0097 → NO 3 seguidas → C10 BAJÓ (-0.0075)
- dumezil_f1_soberania_magica: v67=+0.0029, v78=+0.0057, v89=+0.0052 → 3 SEGUIDAS → C10 SUBIÓ (+0.0055)

En Napoleón la regla habría funcionado: habría dejado solo a la que subió.

Mozart — las 5 iluminadas en el ciego (las 5 SUBIERON en C10):
- utopia_principio_mercado: v67=-0.0063, v78=+0.0420, v89=+0.0391 → NO 3 seguidas → SUBIÓ (+0.0350)
- dumezil_desequilibrio_f3_come_al_resto: v67=-0.0042, v78=+0.0242, v89=+0.0453 → NO 3 seguidas → SUBIÓ (+0.0418)
- situacion_dramatica_ambicion: v67=-0.0042, v78=+0.0242, v89=+0.0453 → NO 3 seguidas → SUBIÓ (+0.0418)
- utopia_autonomia_atenas: v67=+0.0146, v78=+0.0478, v89=+0.0107 → 3 SEGUIDAS → SUBIÓ (+0.0027)
- 30_ambicion: v67=-0.0099, v78=+0.0174, v89=+0.0003 → NO 3 seguidas → SUBIÓ (+0.0027)

En Mozart la regla habría roto lo que funcionaba: 4 de las 5 que subieron
tenían solo 2 subidas y la regla las habría descartado (el 5/5 se vuelve
1/1). Además, en toda la traza solo 1 de 42 familias activas tiene 3
subidas seguidas en cada caso.

VEREDICTO: la regla es demasiado estricta. Arregla Napoleón rompiendo
Mozart. Grok la inventó sin medirla.

## 3. ChatGPT: "el Oráculo observa lo que los laterales le entregan, no todo lo que ocurre en el motor" — MAL UBICADO

El oráculo lee el RESULT sellado completo: `motor.annex.traza_P.crudo_P`
tiene las 244 familias × cortes. El observador tiene los datos de TODAS
las familias, incluidas las planas; su criterio es el que solo reporta las
que suben. El Creador no se vio porque:
- la ENTRADA nunca lo activó: plano en 0.5 en los 9 cortes del ciego,
  sube a 0.6691 en C10 (verificado en crudo_P de ambos RESULTs);
- el criterio de iluminación solo mira familias con velocidad positiva
  en los dos últimos pasos.

El hueco está en la entrada y en el criterio, no en lo que le entregan los
laterales. La clasificación de ChatGPT en tres situaciones es correcta
para el Creador: (a) no anticipada porque no había señal previa — límite
legítimo. Pero la ubicación del hueco ("lo que le entregan los laterales")
es equivocada.

## 4. Lo que SÍ es verdad (no lo inventaron los modelos)

- La parábola por familia no predice el corte siguiente (medido por Pecas,
  script `~/workspace/u6-alterno/parabola_ciega.py`): cinemática
  (x(t+1)=x(t)+v(t)+½a(t), últimos 3 cortes) dirección correcta 19/43
  (Napoleón) y 22/42 (Mozart); mínimos cuadrados (9 cortes) 24/43 y 25/42.
  Top-5 predicho vs observado: 0 en común en Napoleón, 3 en Mozart.
  Los 2 giros predichos en Mozart FALLARON.
- El cuadrante no progresa Q1→Q2→Q3→Q4: oscila Q2↔Q3 en ambos casos;
  C10 = Q2 en ambos.
- Las dos alimentaciones del Caldero no llegan (verificado en los RESULTs):
  arquetipos_dinamicos_estado = MEDIDA_O_ESTADO_NO_EMITIDO en las dos
  corridas; neighbor_persistence = SEARCH_NOT_EXECUTED en Napoleón
  (PERSISTED en Mozart). PENDIENTE: por qué no emiten (no revisado aún).
- La multicapa reparada recuperó 20 familias de soporte de traza
  (candidate_trace_support, antes 0) sin cambiar H1/H2 (verificado por
  corrida completa del motor tras el parche).

## 5. Propuestas sin medir (ni verdad ni mentira: no son mediciones)

- Grok: "siguiente más frecuente en la traza" para el cuadrante. Sin medir;
  los datos de transiciones son demasiado pocos para una regla de frecuencia.
- Grok: "umbral de magnitud" para la iluminación. Sin medir.
- ChatGPT: cinco estados explícitos por alimentación
  (EXECUTED, EMPTY_VALID, NOT_EMITTED, NOT_EXECUTED, ERROR). Propuesta
  razonable, no es una medición.
- ChatGPT: comparación de la parábola del estado completo contra cuatro
  referencias (persistencia, extrapolación del último movimiento, parábola
  por familia, parábola del estado completo). Diseño experimental razonable,
  no es un resultado.
- ChatGPT: prueba específica del par antagónico 24_rivalidad /
  milgram_obediencia. Hipótesis razonable, sin probar. (El par mismo es un
  hallazgo medido: mismo par que movió el Brumario C4→C5 en Napoleón,
  milgram −0.206 y 24_rivalidad +0.206; y mayor impulso en ambos ciegos.)

## 6. Por qué alucinan (respuesta a Marco)

Los modelos no tienen el motor. Solo tienen el reporte de Pecas. Cuando
les falta un dato para contestar, lo rellenan con lo que suena plausible
de su entrenamiento: eso es la alucinación. Están hechos para dar una
respuesta completa y segura, no para decir "no tengo el dato". Razonan
sobre el reporte como si fuera el motor: sobre la historia, no sobre los
datos detrás de las palabras.

El motor es demasiado grande para meterlo en un chat y que otro modelo lo
analice directo. La única vía es el puente: Pecas lee el motor, mide, y
los modelos opinan sobre las mediciones. Sus palabras son hipótesis hasta
que se miden contra el motor. Lo que se midió, se midió: las corridas, el
ledger y el repo son el suelo.

## 7. Lo que falta que mida el oráculo (no que funja de otra forma)

Los modelos quieren que el oráculo FUNJA (de predictor, de juez de
fiabilidad) en lugar de OBSERVAR los datos, verlos y entenderlos para
medirlos. El oráculo mide; el que decide es el motor (H1/H2, la apuesta).
Lo que falta no es que funcione de otra forma, es que MIDA más:
- las familias planas (el Creador estaba plano y subió);
- los empates de cuadrante (no colapsar a un solo valor);
- los vecinos del Caldero inyectados por corte (qué vecino, en qué corrida).

## 8. Por qué no llegan las dos alimentaciones del Caldero (resuelto 2026-11-12 ~05:0x CST, leído en el motor)

(a) arquetipos_dinamicos_estado — NO EXISTE. El observador
(`observador_externo_v1.py:154`) busca `sensores.get("arquetipos_dinamicos_estado")`,
una llave que ningún componente del motor emite. El plugin sí existe
(`plugin_arquetipos_dinamicos.py`, cargado en MOTOR_V15_3_UNICO_20260927.py:507-508
y 3665; laterales_unico_v1.py:939) pero su estado en el motor es
"ACTIVA_MUDA_SIN_MAPEO" (línea 667): info() devuelve 3 claves PROPUESTAS
fuera del 244, sin valor por caso. Cero ocurrencias de "arquetipos_dinamicos"
en los RESULTs ciegos de Napoleón y Mozart. El error es DEL OBSERVADOR
(la expectativa, no el motor): pide un nombre que no existe, y el plugin
de todos modos no produce valor por caso.

(b) neighbor_persistence en Napoleón — la búsqueda del Caldero falla por
la ENTRADA, no por el motor. En `RESULT_NAPOLEON_CIEGO_C9.json`:
`features/caldero_busqueda_arquetipos = {"status": "OPTIONAL_STAGE_FAILED",
"error": "RuntimeError:SEARCH_BRIDGE_INVALID_PROVENANCE"}`. La puerta de
proveniencia (`MOTOR_V15_3_UNICO_20260927.py:2255-2258`) solo acepta un
puente con `status == "EXECUTED"` y `origin == "connected_tool_call"`.
El puente de la entrada de Napoleón (ciega Y completa, el mismo) es un
placeholder construido por Pecas sin Exa: `status: NOT_EXECUTED, origin:
none, reason: "construido por Pecas sin herramienta Exa; fuentes =
cronología pública citada arriba; no se fabrican resultados de búsqueda",
provider: none, query_count: 0, results: []`. El Engine lo rechaza POR
DISEÑO y la etapa falla; la persistencia queda en su valor por defecto
SEARCH_NOT_EXECUTED (`MOTOR_V15_3_UNICO_20260927.py:2228`) y ningún corte
recibe vecinos. Mozart sí trae un puente real de Exa
(`bridge_id: MOZART_U6_R2_BLIND_SEARCH_EXA_20261014`, con
blind_query_sha256 y submitted_query) y por eso persiste (PERSISTED,
evento 27104423..., tokens incluidos 'aprendizaje' — el vecino inyectado
en C9). Consecuencia: en Napoleón el cuadrante se calcula solo con los
tokens del corte, sin vecinos. El arreglo no está en el motor: es (1)
corregir la llave que pide el observador y (2) conseguirle a Napoleón un
puente real de Exa, o aceptar que no tiene vecinos.
