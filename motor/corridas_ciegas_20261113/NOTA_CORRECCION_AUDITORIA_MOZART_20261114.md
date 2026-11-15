# Corrección de los 5 hallazgos de la auditoría de ChatGPT sobre Mozart
## Orden de Marco 2026-11-14: solucionar, no solo reportar. Verificación por ejecución.

Caso: MOZART_CON_TEXTO_Z90_U6_20261113
RESULT: motor-u6-storage, rama alterno/reconexion-2a1, motor/RESULT_MOZART_CON_TEXTO_Z90_20261113.json
  (8,272,163 B, commit a57e2c3). Copia de trabajo: ~/workspace/u6-alterno.
Entrada de reproducción: motor-cameo/motor/runs/ESTANDAR__MOZART_CON_TEXTO_Z90_20261113/_PRIMARY_INPUT.json
  (idéntica a _INPUT.json; INPUT_FROZEN.json de mozart/ es otro caso más viejo, NO usar).

## Diagnóstico (verificado por lectura + ejecución, no solo por lectura)
1. INTERNAL_T1_RUN_FAILED / KeyError FAIL_UNKNOWN_TOKEN:creatividad — CAUSA RAÍZ: el
   `visto_case` que construye correr_estandar.py main() lleva SOLO {cuts:[retenido],
   case_id, question, random_seed, _internal_analysis_no_external_search}: SIN
   external_lights. La corrida primaria SÍ tenía 12 luces, incluida creatividad
   (branch hecho_narracion_verificado, stereotype con_texto_20261113, axes [trajectory]).
   El corte retenido C10 activa creatividad PRIMERO (strength 0.84) → run_external
   levanta KeyError. Es un bug del runner (pierde la taxonomía al re-envolver el
   corte retenido), no del motor de interrelación ni del dato.
2. previo_error = DATO_AUSENTE_REQUIERE_CLASIFICACION — CAUSA RAÍZ: la rama de fallo
   pone `sello.get("stderr_tail")`; el previo COMPLETÓ, así que no tiene stderr_tail
   → None → _sanitize_json_contract lo convierte en el placeholder. El previo no
   tuvo error; el campo miente por construcción. (Solape con Issue #64: ChatGPT
   tenía asignado este hueco y no lo entregó; se corrige aquí.)
3. CEB INCOMPLETE (77 etapas) — por analizar desde d['ceb'].
4. Caldero SIMULADO_FIXTURE — por analizar (component_status[28], laterales_unico).
5. estado_final RESUELTO_OPERACIONALMENTE vs predictor LATENCIA_INFORMACIONAL y
   compuerta SIN_CIERRE_PROPUESTO_LATENCIA_PREVIA — por reconciliar/documentar.

## Bitácora
- 2026-11-14 ~16:45 CST: diagnóstico 1 y 2 confirmado. Reproducción pre-fix lanzada
  (RESULT_MOZART_REPRO_PRE_FIX.json, run ESTANDAR__MOZART_CON_TEXTO_Z90_20261113_REPRO).
- 2026-11-14 ~16:52 CST: REPRODUCCIÓN PRE-FIX CONFIRMA EL FALLO por ejecución (exit 4):
  efectividad_corte_retenido.estado=INTERNAL_T1_RUN_FAILED, visto_status=ERROR,
  previo_error=DATO_AUSENTE_REQUIERE_CLASIFICACION, auditoria_salida_json con 1
  faltante ($.efectividad_corte_retenido.previo_error). H1/H2 del recibo coinciden
  con el original (utopia_autonomia_atenas / utopia_mentalidad_liberal).
- 2026-11-14 ~17:05 CST: las 5 correcciones aplicadas en los archivos canónicos
  (motor-cameo/motor/, NO en la copia del run):
  1. correr_estandar.py: visto_case = copia completa del caso con cuts=[retenido]
     (antes: caso pelado sin external_lights → KeyError creatividad, primera
     activación de C10). El previo ya se construía así; el visto no.
  2. correr_estandar.py: previo_error/visto_error = SIN_ERROR_CORRIDA_*_COMPLETADA
     explícito cuando la corrida completó; solo la fallida lleva su stderr_tail.
     (Solape con Issue #64 de agente-cero-costo: ChatGPT tenía asignado este
     hueco —clasificar previo_error— y no lo entregó; se corrige aquí.)
  3. CEB: (a) ceb_runtime_v0_6_flow.py: UNSCOPED_RUNTIME (cubeta de avisos sin
     etapa) ya no es UNKNOWN → DIAGNOSTIC_BUCKET, fuera de `bad`; execution_integrity
     marcada terminal también en éxito. (b) adaptador_convergencia_real_v1.py:
     guarda explícita del all-NaN en radius_cv_mediana (rama degenerada: la
     mediana no existe; se deja nota, no se inventa número; el dato queda igual
     que antes —la rama queda sin la clave— pero sin el RuntimeWarning).
     (c) MOTOR_V15_3_UNICO_20260927.py: _run_geometria_multicapa_working envuelto
     en _ceb_stage("geometria_multicapa_integrada_working_v1") (antes llamada
     directa: la declaración EXECUTED no tenía etapa observada).
     (d) MOTOR: 12 sumideros verificados marcados terminal al final de run()
     (execution_integrity, plugin_guardia_no_cruce.absorbed, protocolo_transversal_
     absorbido, compuerta_cierre_latencia_v0_16_4, metacognition pre/post,
     plugin_sombrero_blanco_token, analogos_fase, plugin_entrega_luces,
     ruta_cierre_latente_guardianes, predictibilidad_set_021, movimiento_de_fondo_u4)
     + 3 aristas FLOW_CONSUMED explícitas para consumos que el CEB no observa
     (proyeccion_longitudinal→metacognition post_h por argumento directo;
     autoevidencia_stores_011→filtro_relleno_013 vía _RUN_CTX["vecinos_011"];
     geometria_multicapa→hipotesis_trayectoria_abierta vía construir()).
     Verificación unitaria del verificador nuevo sobre el ledger ORIGINAL:
     INCOMPLETE → VERIFIED_FLOW_WITH_ANOMALIES (bad vacío; quedan las 2 anomalías
     que corrige la re-corrida completa).
  4. laterales_unico_v1.py: alerta_ejecucion(..., fixture_autorizado=True) →
     INFO_FIXTURE_AUTORIZADO en vez de FALLO_EJECUCION, solo cuando el input
     autoriza el fixture (allow_static_search_fixture) y el recibo confirma
     proveedor fixture. Sin autorización sigue siendo FALLO (verificado por
     ejecución). No se cableó búsqueda en vivo: el contrato (PATCH10) la hace
     OPCIONAL y la corrida sellada debe ser reproducible offline desde el repo;
     las fuentes del fixture son las 10 fuentes congeladas del caso, no datos
     inventados. Pistas LLM siguen en 0.
  5. correr_estandar.py: bloque semantica_estados en el RESULT (contrato de
     salida): estado_final / predictor.status / compuerta_cierre.decision con su
     significado y la regla de consistencia (capas distintas, no contradicción).
- 2026-11-14 ~17:10 CST: re-corrida post-fix lanzada (RESULT_MOZART_POST_FIX.json,
  run ESTANDAR__MOZART_CON_TEXTO_Z90_20261113_FIX). Verificador:
  corridas_ciegas_20261113/verificar_correccion_mozart.py.
- 2026-11-14 ~17:25 CST: la re-corrida FIX pasó 14/18; 4 fallos eran del
  verificador/código, no del motor:
  (a) el camino de ÉXITO de efectividad_corte_retenido no emitía estado/
  previo_error (puntuar_t1 no los emite) → se añadieron al camino de éxito
  (estado=T1_COMPLETADO, previo/visto_status COMPLETED_ISOLATED_SUBPROCESS,
  previo/visto_error SIN_ERROR_*) para que el contrato sea el mismo en los
  dos caminos; (b) vecinos_caldero/neighbor_store.py quedaba sin consumidor
  en TODA re-corrida (también en la pre-fix, con el código original): su
  consumidor stinkbox_transport solo lo lee cuando hay artefactos nuevos que
  importar (io_writes>0 en la corrida original; 0 en re-corridas) → se marcó
  terminal como sumidero persistente (su salida ES el store en disco);
  (c) el invariante de la apuesta era exacto con flotantes: el agregado pasó
  de 0.99999999 a 1.0 (misma suma, redondeo distinto) y la etiqueta de
  calibración cambió ACTIVA→PARCIAL (corrección canónica del 13-nov, no de
  esta auditoría) → el verificador compara escenarios con tolerancia 1e-6
  y no compara la etiqueta.
- 2026-11-14 ~17:30 CST: re-corrida FIX2 (RESULT_MOZART_POST_FIX2.json, run
  ..._FIX2): VERIFICADOR EN VERDE, 18/18, exit 0. efectividad estado=
  T1_COMPLETADO, hit_H=HIT_HIPOTESIS_SET, previo_error=
  SIN_ERROR_CORRIDA_PREVIA_COMPLETADA; ceb VERIFIED_FLOW, 77/77
  EXECUTED_AND_CONNECTED, 0 anomalías; Caldero INFO_FIXTURE_AUTORIZADO,
  llm_neighbor_hints_n=0; semantica_estados presente; H1/H2/apuesta
  idénticos al original. Recibo COMPLETED, result_missing_paths=[].
- 2026-11-14 ~17:35 CST: DIVERGENCIA DE LA COPIA DE TRABAJO. Al comparar con
  la cabeza remota de alterno/reconexion-2a1 (258caf3) se encontró que la
  copia local trae trabajo NO publicado en esa rama: gate_z90 +
  laterales post-corrida (filogenia_mezcla/teoria_color) en
  correr_estandar.py; renombre schrodinger_transport_v0_1 +
  par_superpuesto_entrada + comportamiento_post_meseta en
  laterales_unico_v1.py; guardas degeneradas + n_canon en el adaptador.
  El PR lleva SOLO las correcciones de esta auditoría: se construyeron
  versiones limpias (base remota + solo los hunks CORRECCION_AUDITORIA,
  verificadas por diff y py_compile) y se re-corrió con ellas (FIX3) para
  que el RESULT publicado corresponda exactamente al código publicado.
  La corrida FIX2 queda como evidencia local del código sucio; sus
  diferencias con FIX3 son solo esas piezas ajenas (filas gate_z90,
  par_superpuesto, comportamiento_post_meseta, resúmenes
  filogenia/teoria_color) y el contador de casos sellados del stinkbox.
- 2026-11-14 ~17:45 CST: LA VERSIÓN LIMPIA ROMPE LA GEOMETRÍA (hallazgo
  grave, verificado por ejecución). FIX3 (código limpio = base remota +
  solo mis hunks): geometria_multicapa.status=ERROR
  ("ValueError:A: expected [T>=3,D>=1], got (3, 0)"), feeds_hypothesis_
  generation=False, sin convergencia_multinivel/teseracto; el set cae
  de 5 a 3 hipótesis (pierde las dos complementaria_trazabilidad_
  geometrica) y el verificador falla el invariante de la apuesta.
  Causa: el adaptador remoto NO tiene las guardas degeneradas (r==0,
  final/inicial 0/0, filas vacías) que sí trae el snapshot del 13-nov
  (runs/ESTANDAR__MOZART_CON_TEXTO_Z90_20261113/geometria_multicapa/
  adaptador_convergencia_real_v1.py, idéntico al local salvo mi hunk
  All-NaN): sin ellas, un par de tableros con un lado vacío (3,0)
  tumba toda la capa de geometría. Bisección FIX4 (limpio + solo el
  hunk schrodinger v0_1): el transporte SÍ corre (V0_1_IMPLEMENTADO,
  trayectoria presente, igual que FIX2) y el set sigue en 3 →
  Schrödinger NO es la causa; la causa es el adaptador. También
  verificado: los módulos schrodinger_transport_v0_1/v0_2.py NO están
  en la rama (solo el esqueleto); gate_z90.py, filogenia_mezcla y
  teoria_color SÍ están (solo faltaba la llamada en el runner remoto).
  El snapshot del 13-nov confirma que gate_z90, filogenia/teoria_color
  y el transporte schrodinger v0_1 SÍ corrieron en la corrida original
  (ORIG: gate_z90 1 mención, filogenia/teoria 1 cada una,
  laterales_post_corrida presente, geometria EXECUTED, set de 5);
  lo único post-13-nov en la copia local es par_superpuesto_entrada
  + comportamiento_post_meseta (ORIG: 0 menciones), que son sensores
  de solo lectura (verificado: no mutan pred) y NO van en el PR.
- DECISIÓN (2026-11-14 ~17:50 CST): el PR publica el código del
  13-nov + mis correcciones, NO la base remota pelada: correr local
  (remoto + mis hunks + gate_z90 + filogenia/teoria_color), laterales
  bisect (remoto + mis hunks + hunk schrodinger v0_1, SIN
  par_superpuesto/comportamiento), adaptador local (remoto + mi guarda
  All-NaN + guardas degeneradas + n_canon), MOTOR y ceb locales
  (remoto + mis hunks), más schrodinger_transport_v0_1/v0_2.py
  (código del 13-nov, ausentes en la rama). La re-corrida FIX5 usa
  exactamente ese código; su RESULT es el que se publica.
- 2026-11-14 ~18:20 CST: re-corrida FIX5 (RESULT_MOZART_POST_FIX5.json,
  run ..._FIX5, código final = el publicado): VERIFICADOR EN VERDE,
  18/18, exit 0. efectividad estado=T1_COMPLETADO, hit_H=
  HIT_HIPOTESIS_SET, previo_error=SIN_ERROR_CORRIDA_PREVIA_COMPLETADA;
  ceb VERIFIED_FLOW 77/77 EXECUTED_AND_CONNECTED, 0 anomalías;
  geometria EXECUTED, feeds_hypothesis_generation=True; set de 5
  hipótesis y apuesta MESETA_O_ESTABILIZACION con 5, idénticos al
  original; Caldero INFO_FIXTURE_AUTORIZADO, llm_neighbor_hints_n=0;
  semantica_estados presente; H1/H2 idénticos. Recibo COMPLETED,
  result_missing_paths=[].
  PUBLICACIÓN (2026-11-14 ~18:35 CST): el RESULT completo NO pudo
  subirse por las herramientas MCP disponibles: el JSON de 8.4 MB da
  HTTP 413 (request body too large) y el .gz (485 KB) lo rechaza
  push-files por no ser UTF-8. Lo que SÍ quedó en la rama: el código
  corregido, la entrada, el verificador, esta nota y el recibo
  (RESULT_MOZART_CON_TEXTO_Z90_20261114_RECIBO_EJECUCION.json, sin
  comprimir) con output_sha256 88bb0dcc96237eb1... El RESULT es
  reproducible byte a byte desde la rama sola con el comando de abajo;
  el sha del recibo lo verifica. El RESULT también queda en la copia
  de trabajo (run ESTANDAR__MOZART_CON_TEXTO_Z90_20261113_FIX5 y
  /tmp/RESULT_MOZART_POST_FIX5.json). Para verificar: correr
  python3 motor/correr_estandar.py motor/corridas_ciegas_20261113/
  INPUT_MOZART_CON_TEXTO_Z90_20261113.json MOZART_CON_TEXTO_Z90_
  20261113_FIX5 <salida> y luego python3 motor/corridas_ciegas_
  20261113/verificar_correccion_mozart.py <salida> motor/
  RESULT_MOZART_CON_TEXTO_Z90_20261113.json (comparar el sha256 de
  la salida con el del recibo).
  NOTA: el stdout del runner dice "ok": false por 2 nulls que mete el
  resumen post-corrida de teoria_color (.laterales_post_corrida.
  teoria_color.tono_final.tono.externo/.situacion) — preexistente
  (FIX2 tiene los mismos 2 nulls), NO es uno de los 5 hallazgos y no
  se tocó; el RESULT tal como lo escribe el motor tiene 0 nulls.
  Tampoco va en el PR par_superpuesto_entrada +
  comportamiento_post_meseta (trabajo post-13-nov, sensores de solo
  lectura; FIX5 tiene 0 menciones de ambos, como el original).

## Qué es por diseño (no un fallo)
- CEB: las 12 etapas marcadas terminal son sumideros legítimos (su salida ES el
  RESULT / un checkpoint / un informe de auditoría / control puro). No se les
  inventó un consumidor.
- Caldero: el fixture es el fallback previsto; la búsqueda en vivo es opcional
  por contrato y la corrida sellada es offline y reproducible. llm_neighbor_hints_n=0
  es honesto: no hay pistas LLM en este caso.
- estado_final vs predictor/compuerta: coexisten por diseño (capas distintas).
- vecinos_caldero persistencia NO_ENCONTRADO_EN_STORE (filas[38], nota 010b):
  bug conocido aparte, NO es uno de los 5 hallazgos; no se tocó.

## Refuerzo del verificador post-re-auditoría ChatGPT (2026-11-14 ~19:00 CST)

- ChatGPT re-auditó en chat nuevo (veredicto provisional): acepta los 5 hallazgos
  como corregidos según la evidencia, pero señaló que el verificador 18/18 tiene
  pruebas más débiles que el contrato declarado: no exige expresamente
  estado=T1_COMPLETADO ni exactamente 77 etapas CEB.
- Cambio (verificar_correccion_mozart.py, sin debilitar ninguna comprobación
  existente; 18 → 20 checks): 1c exige efectividad_corte_retenido.estado ==
  T1_COMPLETADO; 3e exige exactamente 77 etapas CEB con status VERIFIED_FLOW.
- Verificación por ejecución: FIX5 reproducido desde el código de la rama sola
  (clon limpio de alterno/reconexion-2a1-correccion-auditoria-mozart, mismo
  comando de arriba, salida /tmp/RESULT_MOZART_POST_FIX5_REPRO.json, exit 0,
  recibo COMPLETED, result_missing_paths=[]): verificador reforzado 20/20,
  exit 0; H1/H2/apuesta idénticos al original.
- Corrección a la afirmación "reproducible byte a byte": el RESULT reproducido
  tiene sha256 2072afa58be53ce1... (no 88bb0dcc96237eb1... del recibo) porque el
  RESULT embebe rutas absolutas de la copia de trabajo (2.259 menciones de la
  ruta del checkout). El contenido es idéntico (verificador 20/20, invariantes
  iguales), pero el sha solo coincide si se reproduce en la misma ruta. La
  reproducibilidad byte a byte vale ruta por ruta, no entre copias.
- Gate Z90 y manifiesto (investigados, sin cambio de comportamiento): el gate
  da RECHAZADO_DIAGNOSTICO con 10 errores R3 (C1–C10 sin 'evidencia') y
  bloquea=false — preexistente (idéntico en el RESULT original del 13-nov) y
  por diseño (el runner lo define como diagnóstico: los casos de fábrica no
  traen evidencia; solo rechaza en preparación de fábrica/calibración). El
  manifiesto da DRIFT_WARNED con 22 archivos en deriva (recibo FIX5 de la
  rama), 0 ausentes, 24 fuera de manifiesto, bloquea=false, y el candado de
  plugins 116 verificaciones sin fallos — por diseño (solo Engine/patterns
  bloquean; ambos coinciden) y esperado por el contrato de tests. La deriva
  la dominan las propias correcciones de esta auditoría (5 archivos) y
  archivos de estado que mutan en cada corrida. Pendiente de decisión de
  Marco (no hecho): refrescar el manifiesto al estado actual del pack y/o
  mover los archivos de estado mutable a excluidos_estado_mutable; y si se
  quiere exigir evidencia Z90 en las entradas de los casos.
