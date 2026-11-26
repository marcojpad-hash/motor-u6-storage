# Versión Unificada 7 (V7) — Motor U6

Fecha: 2026-11-25. Rama: `alterno/version-unificada-7` (pendiente de
fusionar en `alterno/cameo-pesos`; NO fusionada todavía).

## Qué contiene

V7 es la versión unificada del motor. Contiene:

- **Base `53ea887`** (`alterno/cameo-pesos`): lotes de cableado #16–#36
  fusionados. #16 Copi, #17 Beristáin, #18 Pregunta detrás v2, #20 Pregunta
  dirigida + post hoc/falacias, #21 Polaridad causal, #22 Sherlock/rigor,
  #23 Décimo hombre/latencia, #24 Modo estricto, #25 Esteroides, #26
  Verificador consistencia, #27 Autoevidencia, #28 respuesta_humana, #29
  Hombre de acero, #30 Sombrero blanco puerta de entrada, #31 Z90, #32
  Sombrero absorbido, #33 Contratos alineados, #34 Traducción salida, #35
  Coordinador agnóstico, #36 Contratos traductor. **PR #19 se cerró sin
  fusionar: su contenido entró por PR #20.**
- **Lateral enunciativo (PR #38):** guardián observacional de contexto
  enunciativo (Bühler/Jakobson/Halliday), cableado en `guardianes_control_v1.py`
  tras el predictor, con interruptor `CONTEXTO_ENUNCIATIVO_GUARDIAN=off` y
  sección "Dirección y propósito" en el contrato.
- **Lateral del orquestador (PR #10):** el mismo lateral en versión
  agnóstica, con ruta condicional (`debe_observar()`) y adaptador
  `runtime/diagnostics/ruta_contexto_enunciativo.py`. Fusionado en main del
  orquestador (merge `8253eaf`).
- **Reparaciones de la auditoría V7 (P0/P1 + P2):** ver "Reparaciones" abajo.
  Cada una con su test de ejecución.

## La línea alterna queda absorbida en V7

La rama `alterno/cameo-pesos` se tenía aparte para los movimientos y la
experimentación. Funcionó y ayudó. **Ya entra en V7. NO habrá una rama
alterna 2.0 después: V7 absorbe la línea alterna y es la línea unificada en
adelante.** Todo trabajo nuevo sale de V7 (o de ramas hijas de V7 que se
fusionan en ella). `main` sigue siendo SOLO_CONSULTA: nunca se fusiona ahí.

## Dirección y propósito (dame huevos)

El motor U6 es una máquina de **decidir qué hipótesis explica mejor un caso
histórico/biográfico con la evidencia que el caso sí trae, y decirlo con el
grado de confianza que esa evidencia sostiene** — ni más ni menos.

- **Qué hace:** toma un caso (cortes con protagonistas/antagonistas/contexto,
  pregunta, fecha de trabajo Z) y devuelve H1/H2 (las dos hipótesis que
  mejor explican los cortes), una apuesta (H1 frente a H2, con margen y
  grado FIRME/AJUSTADA/FRÁGIL) y las objeciones que le ponen los guardianes.
- **Para qué sirve:** para que una decisión sobre el pasado no se tome por
  intuición ni por el relato más bonito, sino por el apoyo medible de la
  evidencia — y para que, cuando la evidencia no alcanza, el motor lo diga
  (FRÁGIL, LATENTE, NO_RESUELTO) en vez de inventar certeza.
- **Qué NO hace:** no predice el futuro; no decide por ti; no toca el Engine
  V5 ni el catálogo 244 (son canónicos y están protegidos); no calibra (sigue
  NOT_CALIBRATED); no sustituye las fuentes primarias (F007 sigue bloqueado
  hasta que las tenga).
- **Cómo lo hace:** el predictor propone (rank_fusion sobre el catálogo 244)
  y los guardianes objetan (lógica, retórica, temporalidad, consistencia,
  contexto enunciativo). Los guardianes **no escriben H**: solo gradúan y
  objetan. Si un guardián calla, no es que esté de acuerdo: es que no tiene
  nada que objetar en ese corte. Cada guardián tiene bypass visible por
  variable de entorno (apagado marcado NO_CONFIGURADO/APAGADA_POR_FLAG en el
  recibo); excepciones sin bypass por diseño: Z90 y sombrero absorbido.

## Evidencia acumulada por módulo

Cada módulo tiene su veredicto EJECUTA con su prueba de ejecución y su
smoke. El detalle está en `docs/CONTRATOS_OPERATIVOS_V7.md` (contrato por
contrato, nodo por nodo, con su función, sus entradas, sus fuentes y su
evidencia).

Lo que las evaluaciones ya demuestran (posición de Marco, y es verdad):

- **Los módulos funcionan.** Cada capa que se cableó tiene una prueba que
  falla si no ejecuta, y un smoke que lo demuestra en una corrida real. No se
  ha encontrado retroceso en la investigación ni en la maniobralidad de los
  datos: cada capa suma a su modo, un poco, y poco a poco construye la
  fiabilidad del motor.
- **El predictor lateral Grupo B:** top-1 64.46%, top-3 97.52% en 121
  predicciones (leave-one-out, 15 biografías). **Cita histórica, no evidencia
  V7** (ver "Lo que NO está demostrado"): el txt fuente no está en el repo y
  no hay script LOO.
- **El smoke canónico (Themistocles):** H1 `arquetipo_el_gobernante`
  (63.43% relleno, rank_fusion 32.986716, predictibilidad 61.08%), H2
  `13_enemistad_de_parientes` (57.35%, rank_fusion 30.99436, 57.92%), H3
  `30_ambicion`, H4 sombra, H5 `eterno_retorno_02_cosmizacion_fundacion`.
  Grado AJUSTADA, mezcla H1_DOMINANTE, set SET_EXPLICA_TODOS_LOS_CORTES.
  La base y V7 dan las mismas H (idénticas).
- **La suite:** (números al cierre de V7 — ver "Verificación final" abajo).

## Lo que SÍ está demostrado y lo que NO (sin suavizar)

**SÍ está demostrado:**
- Cada módulo cableado ejecuta en una corrida real (test de ejecución + smoke).
- Los hashes canónicos están intactos (Engine V5 y catálogo 244).
- El lateral enunciativo y el lateral del orquestador están integrados y
  funcionan (PR #38 y PR #10 fusionados, pruebas en verde).
- Las reparaciones de la auditoría V7 están probadas (P0/P1 + P2).
- El candado operativo V7 verifica que los hashes coinciden con el motor
  actualizado, y que el runner antiguo NO pasa ese candado.

**NO está demostrado (y no se declara):**
- **Calibración.** El motor completo está NOT_CALIBRATED. Una sola corrida
  (ni diez) no calibra nada. F007 sigue bloqueado (faltan 3 cortes por caso,
  fuentes primarias, separar preparador/custodio y un runner en alterno que
  no publique en main).
- **El 64.46% / 97.52% del predictor Grupo B como evidencia V7.** Es una cita
  histórica sin su fuente en el repo (ver CONTRATOS_OPERATIVOS_V7.md, C-F2).
- **El coordinador agnóstico #35 como parte integrada del motor.** Tiene 29
  tests en aislamiento y cero llamadores en el motor (C-F9: decisión de
  diseño pendiente de Marco).
- **El bloqueo real de la compuerta de cierre.** El `review_pending` real es
  un stub (C-F8 resto).
- **Que el motor sea fiable en general.** Lo que hay es fiabilidad por
  módulo, probada una a una. La fiabilidad del conjunto se construye capa a
  capa; V7 es un paso, no la meta.

## Reparaciones de la auditoría V7

Auditoría exhaustiva por nodo (3 informes en `~/workspace/u6-wiring/verify-v7/`:
`auditoria_A.md`, `auditoria_B.md`, `auditoria_C.md`). Hallazgos graves y su
cierre:

### P0/P1 (reparaciones de código)
- **A-F1 (grave):** `verificar_salida_llm` tenía cero llamadores. Cableada
  en `correr_estandar.py` (tras TRADUCCION_SALIDA); deja
  `verificacion_salida_llm` en el recibo. Bug de nulos encontrado y reparado
  (`None` → `"NO_APLICA"`; la rama SIN_PROSA usa `"ok": "NO_VERIFICABLE"`).
- **A-F2:** `correr_estandar.py` llamaba a `responder()`; ahora llama a
  `observar()` (el envoltorio real).
- **C-F5 (grave):** U7 B5 leía `H1_sellada` (inexistente en el RESULT real);
  ahora lee `H1_sellada_compatibilidad`. B5 pasa de 0.0 a 0.5 en Themistocles.
  Además `correr_estandar.py:646` (ruta `--t1`) levantaba `KeyError`; ahora
  usa el campo real.
- **A-F5:** fila histórica `feeds_predictor=True` en laterales → `False`.
- **A-F3:** docstring del filtro 017 ("activo" por defecto) → `"traza"` (el
  default real).
- **Dorados:** `SHA_UNICO` actualizado (cambio intencional del lateral +
  P2); `p_momento` 0.6522 → 0.6584 (deriva pre-V7; base y V7 coinciden).
- **SHA_ESPERADO:** 3 entradas actualizadas por los docstrings editados
  (latencia, detrás v2, rigor) + prefijos en tests + tabla de cabecera.
- **Cierres documentales:** B-H3 (funciones no cableadas marcadas
  `NO_CABLEADO`), B-H6 (`polaridad_con_latencia` puente LEGACY), B-H4
  esteroides (`orthogonal_residual_analysis` NOT_IMPLEMENTED por diseño),
  B-H5 (4 figuras fuera de cobertura), B-H2 (Holmes/Schopenhauer del plugin
  = plantilla manual). Docstrings obsoletos corregidos (detrás v2, modo
  estricto).

### P2 (cableados reales)
- **C-F4:** candado de plugins al inicio de `run()` (antes solo en
  `correr_estandar`). Un plugin corrupto o que importe el Engine ABORTA la
  corrida. Cacheado por proceso (~2.3 s por 115 archivos).
- **C-F3:** los dos except que convierten un fallo de guardián/cierre en
  bloque ERROR adjuntan su plan de contorno (`contornar`). Nota: no existe
  `aplicar_protocolo` en `control_flujo_soluciones.py`; la función real es
  `contornar`.
- **B-H4 opt B:** las violaciones del verificador de consistencia llegan al
  cierre como objeciones (`_cierre_final_016` y `_cierre_final_016_lineaA`;
  `_cierre_final_020` las reutiliza).
- **B-H1 opt B:** las dos señales fuertes del lateral (asimetría valorativa,
  cierre discursivo) llegan al cierre como objeción trazable (sin retener
  el cierre). CTX-01 actualizado: el cierre queda LATENTE con 1 motivo.
- **A-F4 resto:** gate Z90 completo en `run()` cuando el caso declara
  `gate_z` o `z_trabajo+modo_z` (carga por ruta explícita).
- **C-F1:** filtro de identidad zoom devuelve sus descartes al Caldero
  (tokens_neighbors podado solo si ninguna otra fuente sostiene el token).
  La identidad sale de `_case_identity` (person del caso).

### Causas exactas (lo que NO se cierra con código)
Ver `docs/CONTRATOS_OPERATIVOS_V7.md`, sección 11: C-F2 (Grupo B sin fuente
en el repo), C-F9 (coordinador #35: decisión de diseño), C-F8 resto
(`review_pending` stub), A-F4 resto (Z90 sin disciplina: decisión de
diseño).

## U7 — confianza de la apuesta: cableado a la ruta (cierre V7)

El U7 (`motor/u7/confianza_apuesta_u7.py`) existía pero **nadie lo
ejecutaba**: ningún archivo de `motor/*.py` lo llamaba. En V7 queda
cableado, no solo reparado:

- **Cableado:** `correr_estandar.py` lo invoca después de construir y sanear
  el RESULT (`_confianza_apuesta_u7`), y adjunta su puntaje + detalle B1-B6
  a `result["confianza_apuesta_u7"]` como observación, más una etapa
  `confianza_apuesta_u7` en el recibo (S, confianza, bloques, `calibrada`).
  **No toca H1/H2, la decisión ni los hashes**: solo lee el RESULT. El
  smoke Themistocles da las mismas H que la base (32.986716 / 30.99436).
  Interruptor visible: `U7_CONFIAZA_APUESTA=off` lo desactiva y queda
  registrado como NO_EJECUTADO con su motivo; si falla, también queda
  NO_EJECUTADO con el motivo. Nunca pasa en silencio.
- **B5 de punta a punta:** el productor `efectividad_corte_retenido` SÍ
  escribe `tops_t1` (10 ítems) y `H1_sellada_compatibilidad` en el RESULT
  real (verificado en el smoke: `30_ambicion`, B5 0.5 por estar en el set).
  Segunda mitad de B5 (hallazgo de ChatGPT, verificado en código):
  `retenido_usable` solo se registraba, nunca condicionaba b5 — con hs None
  daba 0.0 y castigaba H1 por una evaluación que no corrió. Ahora, sin
  `tops_t1`, b5 = 0.5 neutral (patrón B4 con el acero). Test:
  `test_b5_sin_tops_t1_es_neutral_05`.
- **NOT_CALIBRATED (declarado, no calibrado):** los pesos W son los seis en
  1 (B1-B6 iguales, fijados a priori, sin ajuste a desenlaces). Son un
  placeholder documentado, no una calibración: no hay datos para
  calibrarlos y no se inventan pesos. El puntaje S y la confianza son una
  observación, no una probabilidad calibrada; el campo `calibrada` es
  `False`. Para calibrarlo harían falta pares de puntajes U7 contra
  desenlaces reales, con n suficiente, y un ajuste explícito con su
  validación. Declarado en el docstring del módulo y aquí.
- **Cobertura en CI:** `motor/tests/test_confianza_apuesta_u7.py` NO estaba
  en ningún workflow. Ahora está en `test-motor-contracts.yml` (lista de
  pytest + triggers de push y PR), junto con `motor/u7/confianza_apuesta_u7.py`.
- **Prueba de ejecución:** `motor/tests/test_cableado_confianza_apuesta_u7.py`
  (estática + helper + corrida completa Themistocles: RESULT con puntaje,
  recibo con la etapa, B5 con datos reales, H idénticas).

## Candado operativo V7

`motor/CANDADO_OPERATIVO_V7.json`: registra los hashes operativos de V7
(runner V15.3 en V7, cada módulo cableado, lateral enunciativo, adaptador
del orquestador, herramienta U7) linkeados a los canónicos (Engine V5 y
catálogo 244, que NO cambian) y al commit base de V7. **Generado y
verificado el 2026-11-25** con `scripts/verificar_candado_v7.py`:
(a) los 33 hashes coinciden con los archivos de V7 y los 2 canónicos
están intactos; (b) el runner antiguo (53ea887,
`473f56cc…`) NO pasa el candado V7 (runner V7: `89062ad0…`). RESULTADO: OK.

## Verificación final

Verificado el 2026-11-25 (cierre):

- **Suite pre-reparaciones (coordinador):** 429 pasadas, **8 fallidas**,
  2 saltadas, en 2507.44 s (exit 1). Diagnóstico: 2 dorados SHA viejos
  (esteroides, modo estricto), 1 acero inestable, 5 de hipótesis de
  trayectoria abierta (ledger CEB cerrado por plan_contorno).
- **Reparaciones de los 8:** dorados actualizados (SHA_ESTEROIDES
  `1fa9b779` → `5f494ace`, SHA_ESTRICTO `c0fe7fbd` → `9143a098`,
  verificados por sha256sum; los SHA viejos en `casos/HISTORIAL_HASHES.json`
  son historia y NO se tocan); C-F3 reparado en
  `motor/motor/ceb_runtime_v0_6_flow.py` (`call()` ejecuta sin traza si el
  ledger está cerrado; `close()` limpia el global obsoleto); acero
  inestable sin cambio de código. Verificación dirigida 11/11 en verde.
- **Suite tras reparaciones (sin B5/U7):** **437 pasadas, 0 fallidas**,
  2 saltadas, en 1945.74 s (exit 0).
- **Suite final con B5 + cableado U7:** 434 pasadas, **7 fallidas**,
  2 saltadas, en 4656.64 s (exit 1). Las 7 son corridas reales por
  subprocess (sombrero absorbido ×2, sombrero blanco ×2, verificador ×2,
  z90 ×1) que fallan con el mismo error: TIMEOUT de 90 s del subprocess
  primario (`correr_estandar.py:857`, preexistente, no tocado por V7)
  porque la celda (1.5 CPU) corría renders ffmpeg de CAPCOT en paralelo
  (load 6.89–14.89). Re-corrido 3 veces: las 7 fallan con el mismo
  TIMEOUT; el test del verificador pasó una vez en re-corrido. El hook U7
  corre después del motor y no puede causarlas; el smoke con el mismo
  input pasa. **La fusión queda pendiente de una suite verde en ventana
  tranquila (sin renders en paralelo).** No es un defecto de V7: es
  saturación de CPU del entorno.
- **Tests U7:** 10/10 en verde (7 del archivo U7 + 3 del cableado,
  incluida la corrida completa Themistocles).
- **Smoke canónico final (Themistocles, THEMISTOCLES_V7_FINAL2):** exit 0,
  recibo COMPLETED, H idénticas a la base (H1 gobernante 32.986716, H2
  enemistad 30.99436), U7 EJECUTADA (S 0.7428, confianza 63.9,
  `calibrada: False`), B5 con datos reales (tops_t1 10,
  `H1_sellada_compatibilidad` = `30_ambicion`), 0 nulos.
- **Hashes canónicos intactos:** el smoke corrió con Engine V5
  `665c39a2861e…` y catálogo 244 `d827dcc38826…` (los mismos de la base).
- **Rama:** `alterno/version-unificada-7` (pusheada a origin; fusión en
  `alterno/cameo-pesos` PENDIENTE de suite verde en ventana tranquila).
