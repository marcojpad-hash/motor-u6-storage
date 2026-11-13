# Auditoría dirigida de activación — laterales, plugins y componentes U6

Fecha: 2026-11-12 ~21:05–21:30 CST. Caso de evidencia: Semmelweis
(`RESULT_SEMMELWEIS_HEROE_SIN_TRONO_20261112.json`, recibo
`RESULT_SEMMELWEIS_HEROE_SIN_TRONO_20261112_RECIBO_EJECUCION.json`,
run dir `runs/ESTANDAR__SEMMELWEIS_HEROE_SIN_TRONO_20261112/`).
Copia de trabajo: `~/workspace/u6-alterno/motor-cameo/`. Solo lectura.
No se propone activar nada: esto es auditoría, las decisiones son de Marco.

## Resumen

219 filas en total (120 archivos `.py` del barrido + 99 entradas del
`registro_componentes` del RESULT y del `INVENTARIO_COMPONENTES_UNICO.json`
que no tienen archivo propio en el barrido: votos del hub, filas
verificadas, piezas estáticas).

| Clase | Total (219) | Solo archivos .py (120) | Qué significa |
|---|---|---|---|
| (a) ACTIVO | 71 | 19 | Corre y su salida se usa |
| (b) DIAGNÓSTICO POR DISEÑO | 98 | 65 | Corre, observa, no decide — NO es un fallo |
| (c) CABLEADO PERO NO ACTIVADO | 18 | 18 | Cargado/registrado pero no corre, o corre y nadie lee su salida, o su regla está en no/false/PROPUESTA/sin autorizar |
| (d) NO CABLEADO | 20 | 6 | No está cableado |
| (e) DESCONOCIDO | 12 | 12 | No se puede determinar desde código+RESULT |

Lectura corta: **la mayoría de lo que parece apagado no está apagado:
está en (b)**. Los laterales no deciden por contrato (`can_decide_H=False`
en 20 archivos), y muchos corren mudos en este caso porque el caso no trae
señal para ellos (0 luces, gatillo None, sin tokens de cuerpo, pregunta
neutral). **El patrón que denunció Marco existe, pero no es general:
son 18 piezas en (c)**, y la más importante es la que ya se conoce
(la no-duplicación).

Contraste con el registro propio del motor (`registro_componentes`,
140 filas en el RESULT): ACTIVA 82, ACTIVA_MUDA 37, SUPERADA 11,
FUERA_DEL_MOTOR 2, ACTIVA_DIAGNOSTICA 2, MARCAJE 1, GUARDIAN_FILTRO 1,
NO_CORRE 1, PROHIBIDA 1. La diferencia con mis clases: el registro cuenta
"corre" (ACTIVA=82); mi clase (a) cuenta "corre Y su salida se usa" (71).
Solo 7 filas del registro tienen `alimenta_H=True`, y solo 12 componentes
llegan a H como señal lateral según `estado_verificado`.

Evidencia de ejecución del run: recibo COMPLETED, 65.852 s, 18 stages.
CEB: 77 stages, todos started/ended salvo `UNSCOPED_RUNTIME` (0/0);
1 con salida vacía (`plugin_pregunta_dirigida#1`, output_empty=1).
Recibo: `consulta_dirigida` NO_CONFIGURADO (modo off, 0 preguntas);
`gate_z90` RECHAZADO_DIAGNOSTICO (11 errores R1/R3: el caso no declara
disciplina Z90; diagnóstico, no bloquea); `unification_manifest_check`
DRIFT_WARNED; `filtro_entrada_dirigida_017` TRAZA_SIN_MODIFICACION
(0 aplicadas); `candado_plugins` OK (112 verificados, 0 fallos).

## (c) CABLEADO PERO NO ACTIVADO — 18 piezas, con su freno exacto

| # | Componente | Archivo | Freno exacto | Quién debería leerlo |
|---|---|---|---|---|
| 1 | capa_integracion_semantica_v1_2 | `motor/capa_integracion_semantica_v1_2.py` | Su propio estado es `PROPUESTA` (línea 190). El principio central está escrito (`token_es_unidad`, `reaparicion_no_duplica`) pero el Engine nunca lo aplica. El sensor del hub lo reporta tal cual. | Nadie (sensor: solo reporta). La regla de no-duplicación. |
| 2 | capa_interrelacion_tokens | `motor/capa_interrelacion_tokens.py` | Su propio estado es `PROPUESTA` (`analizar_corte`/`analizar_cortes`, líneas 151/182). `cuenta_doble_global=False`. | Nadie (sensor: solo reporta). |
| 3 | plugin_arquetipos_dinamicos | `motor/plugin_arquetipos_dinamicos.py` | Cargado (`opt_dyn`, MOTOR UNICO:507) y llamado (`dyn.info`), pero `ACTIVA_MUDA_SIN_MAPEO` (MOTOR UNICO:667): `info()` devuelve 3 claves PROPUESTAS fuera del 244, sin valor por caso. No hay puente nombre→familia. | Nadie (`llega=[]`). Falta el mapeo a familias del 244. |
| 4 | plugin_sombrero_blanco_token | `motor/plugin_sombrero_blanco_token.py` | Declarado `feeds_predictor=True` en UNICO, VERIFICADO=False en el run (`n_esta_corrida=0`). | Nadie (`llega=no`). |
| 5 | sidecar_caldero_busqueda_arquetipos | `motor/sidecar_caldero_busqueda_arquetipos.py` | EJECUTADO con 74 vecinos crudos, pero 0 mapean al 244 (`current_neighbors=[]`); `llm_neighbor_hints_n=0` (las pistas vienen de la entrada y no se pusieron). | Nadie (`llega=no`). El predictor / el puente de nombres. |
| 6 | vecinos_caldero_neighbor_store | `motor/vecinos_caldero_neighbor_store.py` | Declarado `EJECUTADO feeds_H=True`, VERIFICADO `llega=no`. Los 74 vecinos persisten al StinkBox pero no votan (0 mapeados). | Nadie. El predictor de vecinos. |
| 7 | predictor_vecinos_prefijo_v1 | `motor/predictor_vecinos_prefijo_v1.py` | Cableado y llamado, pero `MEDIDA_O_ESTADO_NO_EMITIDO`: ningún corte trae estado monomítico exacto (sin prefijo), 0 candidatos. No hay vecinos mapeados de donde predecir. | Nadie (0 candidatos). |
| 8 | filtro_identidad_zoom_out_zoom_in | `motor/filtro_identidad_zoom_out_zoom_in.py` | Cableado y llamado, pero ACTIVA_MUDA: sin fuentes de búsqueda verificables. Además el umbral zoom-out está PENDIENTE de validación independiente (línea 24). | Nadie (`filtro_identidad_estado=MEDIDA_O_ESTADO_NO_EMITIDO`). |
| 9 | matriz_mortalidad_z90_v0_2 | `motor/matriz_mortalidad_z90_v0_2.py` | `WIRED_WAITING_VERIFIED_MORTALITY_DATA`: cableada en el runner pero sin tabla (`data_table NO_APLICA_SIN_TABLA`, 0 filas aceptadas). Espera datos de mortalidad verificados. | Nadie (`feeds_H=False`; solo diagnóstico). |
| 10 | lectura_negativo_ricci_vs_billar_v0_1 | `motor/lectura_negativo_ricci_vs_billar_v0_1.py` | Cabecera: `ESTADO="PROPUESTA"`, "no cableado, no tubo" (líneas 4, 43), pero el hub SÍ lo lee como voto (`voto_negativo`). La REGLA (la lectura por negativo DESCARTA) sigue en PROPUESTA; el voto llega a H como señal lateral, el descarte no se aplica. | El hub (solo como voto, no como descarte). |
| 11 | plugin_pregunta_detras_v2 | `motor/plugin_pregunta_detras_v2.py` | Cabecera: "PROPUESTA. No cablear al limpio sin OK de Marco" (línea 4), pero MOTOR UNICO lo carga (`opt_qd`, línea 489) y lo llama (`interrogar`, línea 490) como control observacional. Su salida no altera H. Pregunta para Marco: ¿existe el OK? | Nadie (observacional; `llega=[]`). |
| 12 | schrodinger_transport_esqueleto_v0_1 | `motor/schrodinger_transport_esqueleto_v0_1.py` | `PROPUESTA / ESQUELETO. NO EJECUTA TRANSPORTE` (línea 2). El sensor schro del hub lo necesita presente para no dar NO_CORRE, pero el esqueleto no transporta nada. | Nadie. |
| 13 | schrodinger_transport_v0_2 | `motor/schrodinger_transport_v0_2.py` | Computa (sensor schro: salida `V0_2_IMPLEMENTADO`, rho=0.1) pero Marco ancló el puente en V0_1 sin V0_2 (2026-11-12: V0_2 destruyó ~40% de la masa). El núcleo del motor (MOTOR UNICO) no tiene ninguna referencia a `schrodinger`: ni V0_1 ni V0_2 alimentan el rank en esta copia. | Nadie en el núcleo (sensor: solo calcula). |
| 14 | sidecar_area_tokens_v1 | `motor/sidecar_area_tokens_v1.py` | El sidecar corre (30 familias registradas), pero la asignación de tokens a las 2 subfamilias es PROPUESTA (línea 106). | Hub `area_tokens` (solo el registro; la asignación no). |
| 15 | sidecar_trazabilidad_temporal | `motor/sidecar_trazabilidad_temporal.py` | El trazado corre (47 tokens, estados ON/PARPADEO/NO_APAGADO) pero su k empírico es `PROPUESTA_EMPIRICA` (línea 166) y el sensor reporta estado `CABLEADO_BUS_LATERAL`. | Sensor (solo traza). |
| 16 | sidecar_geometria | `motor/sidecar_geometria.py` | Corre (`u_geo`) pero su salida no nombra ningún candidato del top: el puente no llega (registro `geometria` ACTIVA_MUDA). | Nadie (el puente no llega). |
| 17 | puente_souriau_caldero_polti_v1 | `motor/puente_souriau_caldero_polti_v1.py` | Corre (`marco_7783_geometria` EXECUTED), pero el mapeo seis funciones → 7783 está PENDIENTE de la regla de Mj (líneas 21, 146: solo 729 alcanzables). | Hub `marco_7783_geometria` (solo lo alcanzable). |
| 18 | marco_funciones_souriau | `motor/marco_funciones_souriau.py` | Sub-función `mathematical_momentum_map`: `NOT_IMPLEMENTED_BY_THIS_MODULE` (líneas 102, 111). El resto corre (el sensor souriau14 deriva las funciones por PATCH 007). | Nadie (esa sub-función). |

Notas sobre (c):
- La mención de PROPUESTA dentro de `reconexion_v2a1/no_duplicacion_latencia.py`
  (línea 8) es HISTÓRICA (el estado anterior de la regla), no su propio estado;
  el lateral no está en PROPUESTA. Su DESACTIVADO aparente (línea 40, "con la
  regla APAGADA") es la puerta de cordura, no un apagado del lateral.
- `consulta_dirigida` (recibo: NO_CONFIGURADO, modo off) es la consulta LLM
  obligatoria del Caldero (orden #50 del bus): no está configurada en esta
  corrida. Es un (c) de configuración, no de código.
- La apuesta t+1 de MOVIMIENTO de cuadrante (HIT/MISS Q→Q) "no implementada
  en ningún archivo en disco" (`sensores_pre.caldero_ii_cuadrantes.falta`):
  está en (d), no en (c), porque no existe el código.

## Autodeclarados PROPUESTA en código — 10 archivos + 1 registro

Verificado línea por línea (no es grep a ciegas):

| Archivo | Línea(s) | Texto exacto |
|---|---|---|
| `motor/capa_integracion_semantica_v1_2.py` | 190 | `"estado": "PROPUESTA"` (la regla de no-duplicación) |
| `motor/capa_interrelacion_tokens.py` | 5, 151, 182 | `PROPUESTA — capa general de interrelación…`; `"estado": "PROPUESTA"` ×2 |
| `motor/lectura_negativo_ricci_vs_billar_v0_1.py` | 4, 43 | `PROPUESTA (no cableado, no tubo)`; `ESTADO = "PROPUESTA"` |
| `motor/plugin_pregunta_detras_v2.py` | 4 | `PROPUESTA. No cablear al limpio sin OK de Marco.` |
| `motor/plugin_pregunta_dirigida_v0_5_1.py` | 3, 25, 42 | `PROPUESTA SIDECAR unificada (no cableado al limpio)`; `PENDIENTE de autorización al ON del limpio` |
| `motor/schrodinger_transport_esqueleto_v0_1.py` | 2 | `PROPUESTA / ESQUELETO. NO EJECUTA TRANSPORTE.` |
| `motor/sidecar_area_tokens_v1.py` | 106 | `asignación = PROPUESTA` (solo la asignación a subfamilias) |
| `motor/sidecar_cuerpo_arco__BUG_A_SIN_CONFIRMAR.py` | 5, 6, 207 | `PROPUESTA. No se cablea al motor limpio.` |
| `motor/sidecar_trazabilidad_temporal.py` | 166 | `"k_estado": "PROPUESTA_EMPIRICA"` |
| `motor/tusi_par_indice_exploratorio_v0_1.py` | 2 | `PROPUESTA / EXPLORATORIO. Alimenta_H=NO.` |
| `motor/MOTOR_V15_3_UNICO_20260927.py` (registro) | 667 | `plugin_arquetipos_dinamicos: ("ACTIVA_MUDA_SIN_MAPEO", "info() devuelve 3 claves PROPUESTAS fuera del 244, sin valor por caso")` |

## (d) NO CABLEADO — 20

| Componente | Motivo |
|---|---|
| `normalizar_familia_tokens.py` | Nadie lo carga (0 referencias). Su propio aviso: `puente_244: PENDIENTE (sin puente la familia queda cableada pero muda)`, status `LATERAL_NORMALIZADO_PENDIENTE_CORRIDAS`. |
| `observador_externo_v1.py` | 0 referencias en todo `motor/`, `correr_estandar.py`, `laterales/`, `reconexion_v2a1/`. Módulo local de la sesión; nunca cableado al motor. |
| `plugin_pregunta_dirigida_v0_5_1.py` | PROPUESTA, PENDIENTE de autorización al ON del limpio. El motor carga `plugin_pregunta_dirigida.py` (sin versión), no la v0_5_1. |
| `no_duplicacion_latencia.py` | Lateral de esta noche; standalone por diseño (no toca Engine/244). |
| `rueda_conjuncion.py` | Lateral de esta noche; standalone por diseño. |
| `cuartos_monomito.py` | Lateral de esta noche; standalone por diseño. |
| `caldero_run.py` (×2 filas) | SUPERADA (sustituida por cuadrantes circulares Q1-Q4) y NO_CORRE (necesita lib propia y escaleta/fixture externo; los 7 casos no la traen). |
| `B9_V0_9_TORTUGA.py` | SUPERADA (motor alterno V0.9 viejo). |
| `stinkbox v0.1` | SUPERADA (contenida en StinkBox v0.2, activa con compuerta de pendientes). |
| `montecarlo_predictibilidad_semantica_v1` | FUERA_DEL_MOTOR (análisis específico del caso Jobs). |
| `sofista.py` | FUERA_DEL_MOTOR (laboratorio de red team). |
| `v153_lateral_metrics` (versiones previas) | SUPERADA (activa `lente_lateral_metrics_v1_1_galileo`). |
| `tracing_engine / V11 / V15.1 / V15.2` | SUPERADA (versiones anteriores del motor). |
| `sidecar_latencia_decimo_hombre` | SUPERADA (alias contenido en `control_latencia_decimo_hombre`, activo). |
| `plugin_pregunta_dirigida 0.4.1` | SUPERADA (reemplazada por 0.5.1). |
| `plugin_circulo_monomito v1` | SUPERADA (el motor carga primero monomito_v2; v1 queda como respaldo si falta v2). |
| `plugin_pregunta_detras_v2 2.3.2` | SUPERADA (falso positivo 'esta' corregido en 2.3.3; original en rescate/). |
| `guardianes_control_v1 V1.1` | SUPERADA (V1.2 espera detrás 2.3.3; original en rescate/). |
| `Engine falso` | PROHIBIDA (candado: nunca se copia ni se carga). |

## (e) DESCONOCIDO — 12

No se pudo determinar desde código+RESULT, con el motivo. Sin adivinar.

| Componente | Por qué no se puede determinar |
|---|---|
| `schrodinger_transport_v0_1.py` | El sensor schro lo computa (`V0_1_IMPLEMENTADO`, `alimenta_convergencia=True` según el propio sensor), pero el núcleo no tiene ninguna referencia a `schrodinger` y no se localizó el consumidor de esa "convergencia" en el árbol buscado. |
| `caldero_II_runner_generico.py` | Mencionado en `laterales_unico_v1.py` pero sin punto de llamada verificado. |
| `caldero_buscadores.py` | Mencionado en MOTOR UNICO pero sin `_load` ni presencia en RESULT. |
| `calibracion_predictiva_v1.py` | Sin `_load`, sin presencia en RESULT. |
| `filtro_tokens_arquetipos_v1.py` / `v2.py` | Sin `_load` ni presencia en RESULT; no se verificó si el filtro sombrero_blanco los usa. |
| `forman_ricci_weighted_graph.py` | Primitiva exacta (verificada por ejecución en sesión anterior: triángulo 0.0, estrella −1.0), pero sin `_load` ni presencia en este RESULT. |
| `lexico_narrador_v0_1.py` | Sin `_load` ni presencia en RESULT. |
| `plugin_polaridad_causal.py` | Mencionado en MOTOR UNICO y en `laterales_unico`, pero sin salida localizada en RESULT. |
| `sidecar_ablacion_hombre_acero.py` | Mencionado en MOTOR UNICO; sin salida localizada en RESULT. |
| `souriau_momentum_so3.py` | Sin `_load` ni presencia en RESULT. |
| `zri_experience_v0_1.py` | Mencionado en `laterales_unico`; sin fila en RESULT. |

## Hallazgos sistémicos

1. **Lo declarado no es lo verificado.** `run()` pone `feeds_predictor=True`
   a todos los componentes; la tabla `estado_verificado` del propio RESULT
   es la que distingue ACTIVA de ACTIVA_MUDA. Casos: `plugin_sombrero_blanco_token`
   (declarado True, verificado False), `vecinos_caldero/neighbor_store`
   (declarado `feeds_H=True`, verificado `llega=no`), `sidecar_caldero`
   (declarado EJECUTADO, verificado `llega=no`).
2. **La fuga del DH está cerrada en esta copia.** El `contador_supervivencia`
   SÍ lo lee ahora `predictibilidad_set_021.py:106` (factor_reconexion de la
   v2.A.1, `pred_ajustada`); alimenta la predictibilidad ajustada, no H.
   La fuga original ("nadie lo leía") ya no existe aquí.
3. **Ninguna pieza está apagada por flag.** `LAT_<NOMBRE>=0` apaga piezas
   (`laterales_unico_v1.py:144-151`), pero por defecto todo está ON
   ("por defecto todo ON", línea 13); en fábrica no se apaga nada.
4. **Los `can_decide_H=False` son contrato, no freno.** 20 archivos lo
   declaran; es la regla "los laterales no deciden". Contarlos como
   no-activados sería el mismo malentendido que con "los laterales no
   deciden" = "ignórenlo".
5. **Schrödinger: el puente no tiene consumidor en esta copia.** Ni V0_1
   ni V0_2 aparecen en MOTOR UNICO. El sensor del hub los computa a los
   dos; la decisión de Marco (V0_1 sí, V0_2 no) vive en el anclaje, no en
   un cableado visible en el núcleo.
6. **La matriz de mortalidad está cableada y esperando datos.**
   `WIRED_WAITING_VERIFIED_MORTALITY_DATA`, 0 filas aceptadas; el recibo
   declara ausente `$.matriz_mortalidad_z90.data_table_sha256`.
7. **La consulta dirigida del Caldero está en off.** Recibo:
   `consulta_dirigida` NO_CONFIGURADO (0 preguntas). Es la consulta LLM
   obligatoria (orden #50 del bus).
8. **El registro tiene filas duplicadas/solapadas** (ej. `caldero_run.py`
   dos veces, `guardianes_control_v1` y `guardianes_control_v1 V1.1`,
   `plugin_pregunta_dirigida` y `0.4.1`): el conteo 140 incluye
   duplicados; las filas únicas son 138.
9. **Falsos positivos del barrido, descartados con evidencia:**
   `no_duplicacion_latencia.py` (PROPUESTA/DESACTIVADO son históricos/de
   la puerta de cordura, no su estado); `control_flujo_soluciones.py`
   (NO_IMPLEMENTADO es una regla de su protocolo, no su estado);
   `decimo_hombre_esteroides` (NOT_IMPLEMENTED es solo el sub-análisis
   `orthogonal_residual_analysis`); `movimiento_de_fondo_u4`
   (`SIN_SENAL` es una clase de token, no el estado del módulo);
   `ceb_runtime` (`CABLEADO_NO_EJECUTADO` etc. son categorías de reclamo
   de stage, no estados de pieza).

## Método y fuentes

- Barrido de estados por grep en 120 archivos `.py`:
  `motor/motor/*.py`, `motor/laterales/**`, `motor/reconexion_v2a1/**`,
  `motor/correr_estandar.py`, `motor/geometria_multicapa/**`.
  Marcadores: PROPUESTA, EN_REVISION, NO_IMPLEMENTADO, ESPERANDO,
  PENDIENTE, DESACTIVADO, NO_CORRE, NO_DISPONIBLE, CABLEADA_SIN_SENAL,
  `can_decide_H`, `enabled/activo/habilitado/autorizado`, `"estado"`.
  Resultado: PROPUESTA en 11 archivos (1 falso positivo),
  `can_decide_H` en False en 20 archivos.
- Cableado: 64 llamadas `_load()` en MOTOR UNICO (listadas en
  `auditoria_activacion_evidencia.json`); 0 en `correr_estandar`
  (importa el motor directamente); el hub `laterales_unico_v1.py`
  carga sus sensores por su propio `_load`.
- Ejecución: RESULT + recibo + run dir de Semmelweis;
  `registro_componentes` (140 filas) y `estado_verificado` (42 filas)
  del propio RESULT como contraste; `INVENTARIO_COMPONENTES_UNICO.json`
  (13 estáticas).
- Cada fila de la tabla JSON lleva su evidencia (archivo, líneas, estado
  textual, cableado, lector, freno). Los 12 (e) quedaron en (e) a
  propósito: no se forzó ninguna clase.

## Archivos entregados

- `~/workspace/u6-alterno/AUDITORIA_ACTIVACION_LATERALES_20261112.md` (este reporte)
- `~/workspace/u6-alterno/auditoria_activacion_laterales.json` (219 filas: nombre, archivo, cableado, estado textual, clase, freno, quién lee su salida, evidencia)
- `~/workspace/u6-alterno/auditoria_activacion_evidencia.json` (barrido crudo: estados por archivo, stages CEB, features, laterales_unico)
- `~/workspace/u6-alterno/auditoria_activacion.py` (script del barrido, reproducible)
- `~/workspace/u6-alterno/clasificar_auditoria.py` (script de la clasificación, reproducible)
