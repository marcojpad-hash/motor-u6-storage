# Contrato operativo vigente — Motor U7

Fecha de consolidación: 2026-11-26. Repositorio: `marcojpad-hash/motor-u6-storage` (slug histórico conservado). Rama operativa: `alterno/cameo-pesos`. Base verificada: `dbb60e7` (PR #39 integrado). Este archivo es la **única autoridad contractual operativa**. Los contratos anteriores se conservan en `antecedentes_motor/historial_contratos/` y no gobiernan la ejecución.

El nombre operativo es **Motor U7**. Los nombres U6/V15.3 que permanecen en rutas, módulos, hashes o formatos son identificadores históricos/de compatibilidad; no designan un segundo motor.


Cada contrato dice **con qué trabaja** el módulo (entradas, fuentes de datos,
dependencias, herramientas) y **qué produce**. Los veredictos son
CABLEADO / INTEGRADO / FUNCIONAL, con su evidencia (prueba de ejecución,
smoke, recibo). Escritos desde el código real, no inventados.

**Cómo leer un veredicto:**
- **CABLEADO** — el módulo es invocado en una ruta real (run() o
  correr_estandar.py), no solo existe en disco.
- **INTEGRADO** — su salida llega a otra parte del motor (recibo, cierre,
  predictor, otro guardián); no es un callejón sin salida.
- **FUNCIONAL** — una prueba de ejecución y/o un smoke real lo demuestran
  (el test falla si el módulo no ejecuta).

**Regla de oro (Marco):** nada en el motor es adorno. Si un módulo no está
cableado, integrado o funcional, V7 lo repara o lo reporta con su causa
exacta. No hay "pendiente de valoración" sin causa nombrada.

---

## 1. Capa de entrada

### 1.1 Sombrero blanco — puerta de entrada (A / B / absorbido / v2)
- **Función:** filtrar la entrada antes de que toque el motor: sacar del
  tablero lo que no pertenece al catálogo 244 (fuera de catálogo → StinkBox),
  sin inventar ni reescribir nada.
- **Entradas:** el caso (cortes P/A/C, pregunta, z90_date).
- **Fuentes de datos:** `motor/patterns_final_v14.json` (244, canónico).
- **Dependencias:** `plugin_sombrero_blanco_token.py`, `guardianes_control_v1.py`
  (sombrero absorbido), `correr_estandar.py` (puerta principal, antes de
  escribir `_INPUT.json`).
- **Produce:** caso filtrado + traza en el recibo
  (`execution.component_status`, fila `plugin_sombrero_blanco_token`).
- **Veredicto:** CABLEADO / INTEGRADO / FUNCIONAL. Evidencia:
  `test_cableado_sombrero_blanco.py` (fila token: `feeds_predictor` corregido
  a `False`, A-F5), `test_cableado_sombrero_absorbido.py` (SHA Engine +
  catálogo + UNICO), smoke Themistocles (H intacta).

### 1.2 Autoevidencia (stores 011)
- **Función:** huella del input congelado (sin rutas del runner) para
  procedencia e idempotencia de stores (StinkBox/vecinos).
- **Entradas:** el caso congelado.
- **Fuentes de datos:** el propio input (sha_entrada).
- **Dependencias:** `autoevidencia_stores_011.py`, cargado en run().
- **Produce:** `input_sha_011` en `_RUN_CTX`; bandera en el recibo.
- **Veredicto:** CABLEADO / INTEGRADO / FUNCIONAL (parcial por diseño: solo
  bandera, no bloquea). Evidencia: `test_cableado_autoevidencia.py`.

### 1.3 Filtro de entrada dirigida 017
- **Función:** detectar y marcar pregunta dirigida / post hoc / falacias en la
  entrada; verificar la salida del LLM contra el cierre (A-F1).
- **Entradas:** el caso (entrada) y `cierre_final` + `respuesta_humana` +
  `traduccion_salida` (salida).
- **Fuentes de datos:** el catálogo 244 (etiquetas por familia, para nombrar
  las violaciones de forma legible).
- **Dependencias:** `capa_llm/filtro_entrada_dirigida_017.py`,
  `verificar_salida_llm` (en el mismo módulo).
- **Produce:** traza de entrada (`_f017_traza`); en salida,
  `result["verificacion_salida_llm"]` (status EJECUTADA, huella, violaciones
  por salida: H1/H2 no mencionadas, grado no declarado, objeciones no
  declaradas).
- **Veredicto:** CABLEADO / INTEGRADO / FUNCIONAL. Evidencia:
  - Entrada: `test_cableado_017.py` (el default real es `traza`, no `activo`
    — A-F3 corrigió el docstring; cambiar a `activo` es decisión de producto
    de una línea en los dos defaults).
  - Salida: **A-F1 cerrado en V7** — `verificar_salida_llm` tenía cero
    llamadores (hallazgo grave); ahora corre en `correr_estandar.py` tras el
    bloque TRADUCCION_SALIDA y deja su verificación en el recibo. Prueba:
    `test_verificar_salida_llm_detecta_h1_h2_invertidas`,
    `test_verificar_salida_llm_texto_limpio_pasa`,
    `test_runner_verifica_salida_llm` (vivo, Themistocles: RH violaciones
    [H2_NO_MENCIONADA, OBJECIONES_NO_DECLARADAS]; TR [GRADO_NO_DECLARADO,
    OBJECIONES_NO_DECLARADAS]; huella `bb902cd556fc5c2b`).

### 1.4 Z90 (compuerta temporal)
- **Función:** que ningún dato posterior a Z (fecha de trabajo) entre en la
  corrida; que los cortes sean crecientes y con evidencia fechada.
- **Entradas:** el caso (z90_date, z_work_date, cuts con date y evidencia,
  fecha_nacimiento/fecha_muerte en biografía cerrada).
- **Fuentes de datos:** `calibracion/gate_z90.py` (R1–R8).
- **Dependencias:** `_validate_case` (en run(), solo fechas) +
  `calibracion/gate_z90.py` (gate completo).
- **Produce:** bloqueo (ValueError / exit 3) o recibo con `gate_z90`.
- **Veredicto:** CABLEADO / INTEGRADO / FUNCIONAL. Evidencia:
  `test_cableado_z90.py` (neutro, límite, post-Z90, corrida bloqueada).
  - **A-F4 resto cerrado en V7** — el gate completo solo vivía en
    `correr_estandar`; ahora corre en run() cuando el caso declara `gate_z`
    o `z_trabajo+modo_z` (`_aplicar_gate_z90`, carga por ruta explícita).
    Prueba: `test_gate_z90_caso_valido_pasa`,
    `test_gate_z90_sin_declaracion_no_hay_compuerta`,
    `test_run_bloquea_caso_con_gate_sin_evidencia` (R3).
  - Queda como decisión de diseño documentada: el gate NO se impone a casos
    que no lo declaran (el comportamiento anterior — solo fechas — sigue
    intacto para ellos).

---

## 2. Capa de lógica

### 2.1 Décimo hombre / latencia (control_latencia_decimo_hombre.py)
- **Función:** si todos están de acuerdo, el décimo hombre disiente: mide la
  latencia (p_momento) y registra los frentes que no se resolvieron.
- **Entradas:** el predictor (candidatos, rank_fusion) y los cortes.
- **Fuentes de datos:** el propio expediente de latencia (persistido).
- **Dependencias:** `guardianes_control_v1.py` (ruta_cierre_latente).
- **Produce:** `p_momento`, estado LATENTE, expediente de latencia.
- **Veredicto:** CABLEADO / INTEGRADO / FUNCIONAL. Evidencia:
  `test_cableado_decimo_hombre.py` (corrida real; dorado `p_momento` 0.6584,
  deriva pre-V7 — base y V7 dan el mismo valor, H y ranks idénticos).
  - **B-H6:** `polaridad_con_latencia()` es un puente declarado, no usado en
    la ruta de guardianes; el consumo vivo es `ruta_cierre_latente()`. Marcado
    LEGACY en el módulo.

### 2.2 Pregunta detrás v2 (plugin_pregunta_detras_v2.py)
- **Función:** preguntar qué hay detrás de la pregunta (la pregunta que la
  pregunta esconde).
- **Entradas:** la pregunta y los textos de entrada.
- **Fuentes de datos:** el input.
- **Dependencias:** `guardianes_control_v1.py`.
- **Produce:** bloque PREGUNTA_DETRAS_V2 con marcas.
- **Veredicto:** CABLEADO / INTEGRADO / FUNCIONAL. Evidencia: tests de
  cableado de detrás v2. (El docstring "PROPUESTA. No cablear" era obsoleto:
  está CABLEADO, OK de Marco 25-nov-2026.)

### 2.3 Pregunta dirigida / post hoc / falacias (plugin_pregunta_dirigida_v0_5_1.py)
- **Función:** detectar direccionamiento del input, post hoc y falacias.
- **Entradas:** la pregunta y los textos.
- **Fuentes de datos:** el input + el catálogo 244 (etiquetas).
- **Dependencias:** `guardianes_control_v1.py`.
- **Produce:** bloque PREGUNTA_DIRIGIDA_POST_HOC y FALACIAS con marcas.
- **Veredicto:** CABLEADO / INTEGRADO / FUNCIONAL. Evidencia: tests de
  cableado de dirigida/falacias.
  - **B-H3:** `detectar_fuga_corpus`, `comparar_boards` y
    `sugerir_pregunta_neutral` no tienen llamador en la ruta real. Marcadas
    `NO_CABLEADO` en la cabecera del módulo (son utilidades, no parte del
    tubo; si se necesitan, se cablean con su test).

### 2.4 Lógica Copi (guardian_logica_copi_v1.py)
- **Función:** revisar la lógica del input con las reglas de Copi
  (validez, falacias formales).
- **Entradas:** los textos de entrada.
- **Fuentes de datos:** el input.
- **Dependencias:** `guardianes_control_v1.py`.
- **Produce:** bloque LOGICA_COPI con marcas.
- **Veredicto:** CABLEADO / INTEGRADO / FUNCIONAL. Evidencia: tests de
  cableado de Copi.

### 2.5 Polaridad causal (plugin_polaridad_causal.py)
- **Función:** polaridad causal (qué causa qué, en qué dirección).
- **Entradas:** los textos y los cortes.
- **Fuentes de datos:** el input.
- **Dependencias:** `guardianes_control_v1.py`.
- **Produce:** bloque POLARIDAD_CAUSAL con marcas.
- **Veredicto:** CABLEADO / INTEGRADO / FUNCIONAL. Evidencia: tests de
  cableado de polaridad.

### 2.6 Hombre de acero (sidecar_ablacion_hombre_acero.py + guardian_acero_rival_v1.py)
- **Función:** steelman del rival: ablación de pilares de H para ver si el
  rival sobrevive; si no lo descarta, el cierre no es FIRME.
- **Entradas:** el predictor (candidatos) y los cortes.
- **Fuentes de datos:** el propio motor (ablación).
- **Dependencias:** `guardianes_control_v1.py`, modo estricto C2.
- **Produce:** veredicto SOBREVIVE/CAE por rival; alimenta C2 y el grado.
- **Veredicto:** CABLEADO / INTEGRADO / FUNCIONAL. Evidencia:
  `test_cableado_acero.py` (SHA del sidecar verificado).

### 2.7 Sherlock / método de rigor (plugin_metodo_rigor.py)
- **Función:** rigor holmesiano: qué hipótesis explica los hechos, qué
  sobra, qué falta.
- **Entradas:** los textos, el tablero de tokens, `cadena_top1`.
- **Fuentes de datos:** el input + el catálogo.
- **Dependencias:** `guardianes_control_v1.py` (g_rigor).
- **Produce:** bloque SHERLOCK_RIGOR con marcas y salida del plugin
  (METODO_RIGOR, cadena_top1, auto).
- **Veredicto:** CABLEADO / INTEGRADO / FUNCIONAL. Evidencia:
  `test_cableado_sherlock.py` (unit + corrida real; H intacta;
  `verificacion_H_intacto` predictor_igual y H1_H2_igual).
  - **B-H2:** en la ruta real solo viven Hécate y los dos checks del
    orquestador. Holmes (literales "es kant/freud/monroe") y Schopenhauer
    (`inverso`, que nunca se pasa) son plantilla manual del plugin, no
    ejecución viva. Marcado en el módulo.
  - Prueba nueva: `test_rigor_solo_hecate_con_hipotesis_de_catalogo`.

### 2.8 Modo estricto (modo_estricto_v1.py)
- **Función:** criterios duros C0–C4 (top1 encabeza un corte, acero descarta
  al rival, H1/H2 distinguibles, Aquiles estable).
- **Entradas:** el predictor y los guardianes.
- **Fuentes de datos:** el propio resultado parcial.
- **Dependencias:** `_cierre_final_016` (consume C1–C4 como objeciones).
- **Produce:** `modo_estricto` (criterios + motivos) → objeciones del cierre.
- **Veredicto:** CABLEADO / INTEGRADO / FUNCIONAL. Evidencia:
  `test_cableado_modo_estricto.py`. (Docstring corregido: citaba un runner
  que no es el activo; ahora cita `MOTOR_V15_3_UNICO_20260927.py`.)

### 2.9 Décimo hombre con esteroides (decimo_hombre_esteroides_mayeutica_v1.py)
- **Función:** capa adversarial iterativa/mayéutica después del cierre:
  audita y reabre preguntas con contrafactuales; nunca reescribe H/apuesta.
- **Entradas:** el resultado sellado y el caso.
- **Fuentes de datos:** el propio resultado (contrafactuales recalculan el
  predictor sobre copias).
- **Dependencias:** run() (después del cierre), bypass `ESTEROIDES_GUARDIAN=off`.
- **Produce:** auditoría adversarial en el recibo.
- **Veredicto:** CABLEADO / INTEGRADO / FUNCIONAL. Evidencia:
  `test_cableado_esteroides.py`.
  - **B-H4 (esteroides):** `orthogonal_residual_analysis` es
    `NOT_IMPLEMENTED` por declaración propia y por diseño (no hay
    implementación ortogonal; la mayéutica es por contrafactuales). Marcado
    en el módulo.

### 2.10 Verificador de consistencia adversarial (plugin_verificador_consistencia_adversarial.py)
- **Función:** auditar el resultado contra invariantes explícitos
  (TIE_NO_WINNER, PATTERNS_HASH_DECLARATION_MISMATCH,
  FORMULA_CORPUS_MISSING, RESOLUTION_BEFORE_CLOSE, LATERAL_NO_H). Solo
  control; nunca alimenta H.
- **Entradas:** el resultado completo (information_state, predictor,
  component_status, patterns_sha256 declarado).
- **Fuentes de datos:** el propio resultado + `patterns_final_v14.json`
  (hash real, solo lectura).
- **Dependencias:** run() (después del predictor), bypass
  `VERIFICADOR_CONSISTENCIA=off`.
- **Produce:** `result["consistency_adversarial"]` (status PASS/FAIL,
  violations) + paquete LLM (`CONSISTENCY_ADVERSARIAL_LLM_PACKET.json`).
- **Veredicto:** CABLEADO / INTEGRADO / FUNCIONAL. Evidencia:
  `test_cableado_verificador.py` (8 fixtures, paquete y auditoría).
  - **B-H4 opt B cerrado en V7** — antes el paquete LLM no lo leía nadie y
    las violaciones no las consumía nadie. Ahora `_cierre_final_016` (y
    `_cierre_final_016_lineaA`; `_cierre_final_020` las reutiliza porque
    llama a 016) convierte cada violación en una objeción
    (`fuente: verificador_consistencia`). Prueba:
    `test_cableado_verificador_cierre.py` (violaciones llegan a objeciones;
    sin violaciones no hay objeción; H no se reescribe).
  - Si no se hubiera cableado, el paquete quedaría como artefacto para
    revisión humana externa, sin dueño registrado. No es el caso: está
    cableado.

---

## 3. Retórica

### 3.1 Tropos de Beristáin (guardian_tropos_beristain_v1.py)
- **Función:** lenguaje figurado que no debe leerse literal (lítote,
  hipérbole, sinecdoque, etc.); corrige con vecinos.
- **Entradas:** los textos de entrada y los vecinos (tokens).
- **Fuentes de datos:** el input + `registrar_sinecdoque` (reutilizado).
- **Dependencias:** `guardianes_control_v1.py` (g_tropos_beristain),
  `_anotar_vecinos` (anota correcciones en FALACIAS/COPI/POST HOC/POLARIDAD).
- **Produce:** bloque TROPOS_BERISTAIN con marcas y correcciones de vecinos.
- **Veredicto:** CABLEADO / INTEGRADO / FUNCIONAL. Evidencia: tests de
  cableado de Beristáin.
  - **B-H5:** 4 figuras están fuera de cobertura (`PENDIENTE_DE_REGLA`:
    METALEPSIS, IMAGEN, ASINDETON, ZEUGMA). Marcado en el módulo: no se
    detectan porque no hay regla escrita para ellas, no porque se haya
    olvidado cablearlas.

---

## 4. Investigación

### 4.1 Pistas LLM — Caldero (sidecar_caldero_busqueda_arquetipos.py)
- **Función:** buscar arquetipos análogos (búsqueda ciega, sin identidad en
  el query) para orientar antes de H y contrastar después.
- **Entradas:** los cortes (activos), las pistas LLM (filtradas por el
  guardián), la fecha de corte Z.
- **Fuentes de datos:** proveedor de búsqueda (offline/fixture en tests;
  en vivo, el adaptador configurado) + `caldero_llm_neighbor_hints`.
- **Dependencias:** `guardian_pistas_llm_caldero_v1.py` (filtra las pistas
  por identidad/futuro/calendario ANTES del sidecar), `SelfMatchFilter`,
  `caldero_zoomout_acero_v0_1.py`.
- **Produce:** `features["caldero_busqueda_arquetipos"]` (tokens_neighbors,
  audit con raw_sources_before_self_match, discarded_by_self_match).
- **Veredicto:** CABLEADO / INTEGRADO / FUNCIONAL. Evidencia:
  `test_caldero_buscadores_offline.py`, smoke Themistocles (3 fuentes,
  72 tokens_neighbors).

### 4.2 Identidad zoom (filtro_identidad_zoom_out_zoom_in.py)
- **Función:** descartar las fuentes que SON el sujeto del caso
  (misma_identidad_zoom_in) para que no alimenten los tokens del Caldero
  (el Caldero busca analogías, no al sujeto mismo).
- **Entradas:** las fuentes crudas (`raw_sources_before_self_match`) y la
  identidad del caso (`_case_identity`: person + fechas).
- **Fuentes de datos:** el input (person/birth_date/death_date).
- **Dependencias:** `_do_caldero` en run() (vía `_aplicar_filtro_zoom_caldero`).
- **Produce:** `audit["zoom_identity"]` (status, descartadas, n_tokens
  antes/después) + `tokens_neighbors` podado.
- **Veredicto:** CABLEADO / INTEGRADO / FUNCIONAL. Evidencia:
  `test_cableado_zoom_caldero.py` (unit: fuente misma identidad podada,
  token sostenido por otra fuente se conserva, token sin refs se conserva;
  sin identidad → ACTIVA_MUDA; vivo Themistocles: EXECUTED, 0 descartadas,
  72/72 tokens, H intacta).
  - **C-F1 cerrado en V7** — antes el zoom corría pero no devolvía
    descartes al Caldero. La causa raíz (nadie llena `caldero_identity`)
    queda acotada: la identidad sale de `_case_identity` (person del caso),
    no hace falta `caldero_identity` en el input.

### 4.3 Relleno 013 (filtro_relleno_013.py)
- **Función:** rellenar huecos del tablero con lo que el caso sí trae.
- **Entradas:** los cortes y el tablero.
- **Fuentes de datos:** el input.
- **Dependencias:** run().
- **Produce:** tablero rellenado (traza en el recibo).
- **Veredicto:** CABLEADO / INTEGRADO / FUNCIONAL. Evidencia: tests de
  cableado de relleno 013.

### 4.4 Tokens arquetipos v2
- **Función:** tokens de arquetipos (v2) para el predictor y los vecinos.
- **Entradas:** los cortes.
- **Fuentes de datos:** el catálogo 244.
- **Dependencias:** run(), predictor.
- **Produce:** tokens_neighbors / tokens de arquetipos.
- **Veredicto:** CABLEADO / INTEGRADO / FUNCIONAL. Evidencia: tests de
  cableado de tokens.

---

## 5. Ejecución y flujo

### 5.1 CEB runtime (ceb_runtime)
- **Función:** registrar cada etapa de la corrida (ledger) con sus
  dependencias, para que el flujo sea verificable (qué corrió, en qué orden,
  con qué entradas).
- **Entradas:** cada etapa del runner (vía `_ceb_stage`).
- **Fuentes de datos:** el propio flujo de ejecución.
- **Dependencias:** `motor/ceb_runtime/`; ledgers en `/dev/shm/ceb_runs`.
- **Produce:** ledger CEB + `FlowVerifier` (verifica el flujo con anomalías).
- **Veredicto:** CABLEADO / INTEGRADO / FUNCIONAL. Evidencia:
  `test_ceb_closed_audit_hook.py` (nuevo test: FlowVerifier con ledger
  sintético → `OUTPUT_NO_OBSERVED_CONSUMER` + `VERIFIED_FLOW_WITH_ANOMALIES`
  + anomalía `FEEDS_OUTPUT_NOT_CONSUMED`).
  - **C-F7:** la única anomalía viva en V7 es `neighbor_store` con
    `OUTPUT_NO_OBSERVED_CONSUMER` (el store escribe vecinos que nadie lee
    en esta corrida). Es una anomalía registrada, no un fallo: el flujo está
    verificado CON anomalías, y la anomalía tiene nombre.

### 5.2 Alertas y compuertas
- **Función:** alertar cuando una etapa se sale de lo esperado; compuertas
  que paran o gradúan.
- **Entradas:** el estado de cada etapa.
- **Fuentes de datos:** el propio flujo.
- **Dependencias:** CEB runtime.
- **Produce:** alertas en el recibo.
- **Veredicto:** CABLEADO / INTEGRADO / FUNCIONAL. Evidencia: tests CEB.

### 5.3 Compuerta de cierre (compuerta_cierre)
- **Función:** si hay frentes pendientes que contradicen el cierre, el cierre
  queda BLOQUEADO (no se emite H como cerrada).
- **Entradas:** los frentes pendientes (StinkBox) y el cierre propuesto.
- **Fuentes de datos:** `StinkBox.review_pending` + `pending_fronts`.
- **Dependencias:** run() (después del predictor), `motor/stinkbox_transport_v0_2.py`.
- **Produce:** `compuerta_cierre` (PERMITIDO / BLOQUEADO) en el predictor.
- **Veredicto:** CABLEADO / INTEGRADO / FUNCIONAL (con causa exacta en el
  límite). Evidencia: `test_cableado_compuerta_cierre.py` (nuevo: bloqueo
  con caja falsa, permiso sin contradicción, y documentación de que el
  `review_pending` real nunca contradice).
  - **C-F8 resto:** el `StinkBox.review_pending` real
    (`stinkbox_transport_v0_2.py:274`) es un stub que SIEMPRE devuelve
    `contradicen_cierre: []` — el camino `CIERRE_BLOQUEADO_LATENCIA` es
    inalcanzable en producción hasta que alguien implemente la evaluación
    real de contradicciones. La compuerta está cableada y probada con caja
    falsa; el bloqueo real espera esa implementación. Causa nombrada, no
    pendiente sin más.

### 5.4 Guardia no cruce (plugin_guardia_no_cruce.py)
- **Función:** que los datos no crucen donde no deben (guardia de
  separación entre espacios).
- **Entradas:** los datos que cruzan.
- **Fuentes de datos:** el propio flujo.
- **Dependencias:** run() (archivo) + absorción (sombrero blanco).
- **Produce:** guardia en el recibo.
- **Veredicto:** CABLEADO / INTEGRADO / FUNCIONAL. Evidencia: tests de
  cableado. (La duplicación archivo vs absorción está documentada en el mapa:
  son dos mecanismos distintos, no un error.)

### 5.5 Control de flujo (control_flujo_soluciones.py)
- **Función:** cuando algo se traba (una piedra), dar contornos
  (soluciones) en formato PIEDRA/CONTORNO/SIGUIENTE/EVIDENCIA. "Soluciones,
  no problemas. El obstáculo informa el contorno; no detiene el río."
- **Entradas:** la piedra (qué trabó, 1 línea) + contexto.
- **Fuentes de datos:** `CONTORNOS` (tabla de piedras → contornos).
- **Dependencias:** UNICO (`_plan_contorno` en errores de cierre 017/016) y `motor/correr_estandar.py` (adaptador estándar + guardia final de excepciones).
- **Produce:** plan estructurado con tipo de piedra, contornos, prohibiciones y formato PIEDRA/CONTORNO/SIGUIENTE/EVIDENCIA. En fallo del subproceso primario también produce RESULT de fallo y `_RECIBO_EJECUCION.json` con el contorno.
- **Veredicto:** CABLEADO / INTEGRADO / FUNCIONAL en la ruta estándar. Evidencia automatizada: `motor/tests/test_cableado_plan_contorno.py` y `motor/tests/test_control_flujo_runner.py`.
  - UNICO adjunta planes a los errores de cierre operativo 017 y cierre final 016 sin cambiar H.
  - El runner estándar adjunta planes a fallos del subproceso primario y de módulos de salida; toda excepción no controlada pasa por `_main_with_control_flujo` y devuelve JSON estructurado con exit code 3.
  - El runner verifica Engine V5 y catálogo 244 contra sus hashes canónicos de forma independiente del manifiesto opcional; un manifiesto ausente no degrada el candado. Las discrepancias o archivos ausentes de Engine/244, FREEZE o Z90 se convierten en PARADA_DURA: el plan permite diagnóstico y tareas independientes, pero prohíbe BYPASS_HASH_CAMBIO y cualquier ejecución sustitutiva. El bloqueo Z90 deja el plan en RESULT y RECIBO. No modifica input, predictor, H1/H2 ni hashes.
  - `aplicar_protocolo` no existe como API en este módulo; la API implementada y llamada es `contornar(piedra_o_error, contexto=None)`.
  - **CI verificado:** run [#45860926469](https://github.com/marcojpad-hash/motor-u6-storage/actions/runs/45860926469), job `runner-contract` SUCCESS, 94 pruebas aprobadas en 41.30 s. Incluye la validación del hash canónico independiente del manifiesto y la parada dura Z90.

### 5.6 Protocolo kernel (protocolo_kernel_motor.py, orden 0)
- **Función:** arrancar la matriz y clasificar la pregunta antes de todo.
- **Entradas:** el caso (pregunta).
- **Fuentes de datos:** el propio kernel.
- **Dependencias:** run() (`_protocolo_orden0`, antes de todo).
- **Produce:** `protocolo_orden0` (status EXECUTED, versión, arranque,
  clasificación de la pregunta).
- **Veredicto:** CABLEADO / INTEGRADO / FUNCIONAL. Evidencia: smoke (el
  recibo lleva `protocolo_orden0` EXECUTED en cada corrida).

### 5.7 Candado de plugins (candado_plugins.py)
- **Función:** que ningún plugin esté corrupto ni importe el Engine
  canónico directamente (los plugins leen outputs, no importan el motor).
- **Entradas:** cada `.py` de `motor/` (salvo el Engine canónico).
- **Fuentes de datos:** el propio árbol de archivos.
- **Dependencias:** run() (vía `_verificar_candado_plugins_run`) y
  `correr_estandar.py` (preflight).
- **Produce:** `result["candado_plugins"]` (status OK, verificados, fallos);
  un plugin corrupto o que importe el Engine ABORTA la corrida.
- **Veredicto:** CABLEADO / INTEGRADO / FUNCIONAL. Evidencia:
  `test_cableado_candado_plugins_run.py` (nuevo: helper OK con 115
  verificados; plugin corrupto en BASE temporal → PluginCorruptoError;
  vivo Themistocles: candado OK en el recibo, H intacta).
  - **C-F4 cerrado en V7** — antes el candado solo corría si se usaba
    `correr_estandar`; una llamada directa a run() lo saltaba. Ahora corre
    al inicio de run() (cacheado por proceso: compilar 115 archivos cuesta
    ~2.3 s). Los cambios de hash no bloquean (BYPASS_HASH_CAMBIO; eso lo
    gestiona `registrar_o_comparar`, que no corre aquí).

### 5.8 Candado Engine V5 / catálogo 244 (CANDADO_ENGINE.json + _verify_patterns_contract)
- **Función:** que el Engine V5 y el catálogo 244 sean los canónicos y no
  hayan cambiado (muro: si cambian, no hay corrida).
- **Entradas:** `motor/Engine_V5_CANONICO_SOLO.py` y
  `motor/patterns_final_v14.json`.
- **Fuentes de datos:** los hashes canónicos (Engine `665c39a2…`,
  catálogo `d827dcc3…`).
- **Dependencias:** run() (`_verify_patterns_contract` al inicio) y
  `correr_estandar.py`.
- **Produce:** `hash_candado` / `patterns_sha256` / `integridad_contrato` en
  el recibo.
- **Veredicto:** CABLEADO / INTEGRADO / FUNCIONAL. Evidencia: cada smoke y
  cada test de SHA (Engine `665c39a2861e58772522e91272563260d980908b1d4ab9f7092d3413d0c36082`,
  catálogo `d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1`,
  intactos tras V7).

---

## 6. Salida

### 6.1 Respuesta humana (respuesta_humana)
- **Función:** dar la respuesta en lenguaje humano (no solo el recibo
  técnico).
- **Entradas:** el resultado (H1/H2, grado, objeciones).
- **Fuentes de datos:** el propio resultado.
- **Dependencias:** `correr_estandar.py` (tras el cierre).
- **Produce:** `result["respuesta_humana"]` (status OK).
- **Veredicto:** CABLEADO / INTEGRADO / FUNCIONAL. Evidencia:
  `test_cableado_respuesta_humana.py` (ahora llama a `observar()`, A-F2 —
  antes llamaba a `responder()`, que era un alias muerto en producción;
  `observar` es el envoltorio de `responder(pred, case)`).

### 6.2 Traductor de salida (traducción salida)
- **Función:** traducir la salida (lectura) sin tocar H.
- **Entradas:** el resultado.
- **Fuentes de datos:** el propio resultado.
- **Dependencias:** `correr_estandar.py` (bloque TRADUCCION_SALIDA, bypass
  `TRADUCCION_SALIDA=0` visible).
- **Produce:** `result["traduccion_salida"]` (lectura).
- **Veredicto:** CABLEADO / INTEGRADO / FUNCIONAL. Evidencia:
  `test_runner_enchufa_traduccion_salida`, smoke (TR status OK).

### 6.3 Verificar salida LLM (verificar_salida_llm)
- Ver 1.3 (filtro 017). **A-F1 cerrado en V7** (cero llamadores → cableado
  en `correr_estandar.py`).

---

## 7. Lateral de contexto enunciativo (PR #38, integrado en V7)

- **Función:** observar (no decidir) el contexto enunciativo del input:
  registra juicios, funciones de Bühler/Jakobson/Halliday,
  fragmento/procedencia/enunciador; entrega observaciones a Sherlock, Hécate,
  Schopenhauer, Falacias, Copi y Beristáin sin imponer conclusiones. Es
  perfilamiento de la intencionalidad del input, no de la persona.
- **Entradas:** los textos de entrada (con enunciador / atribuido_a).
- **Fuentes de datos:** el input + `lateral_contexto_enunciativo_v1.py`
  (señales: CARGA_VALORATIVA_REITERADA, ASIMETRIA_VALORATIVA_ENTRE_ACTORES,
  ENMARCADO_ADVERSARIAL, CIERRE_DISCURSIVO_DE_ALTERNATIVAS,
  ATRIBUCION_CAUSAL_O_INTENCIONAL, FUNCION_POETICA_OBSERVADA).
- **Dependencias:** `guardianes_control_v1.py` (g_contexto_enunciativo),
  bypass visible `CONTEXTO_ENUNCIATIVO_GUARDIAN=off`.
- **Produce:** bloque CONTEXTO_ENUNCIATIVO (marcas OBSERVACION, detalle con
  senales, rutas_controles) + `detalle.contexto_lateral_enunciativo` en
  SHERLOCK_RIGOR, FALACIAS, LOGICA_COPI y TROPOS_BERISTAIN.
- **Veredicto:** CABLEADO / INTEGRADO / FUNCIONAL. Evidencia:
  `test_runner_json_contract.py` (CTX-01, CTX-02; el lateral marca y no
  cambia decisiones), 80 pruebas en verde en PR #38, smoke V7 (H intacta).
  - **B-H1 opt B cerrado en V7** — antes el lateral no tenía consumidor:
    cero lectores de `detalle.contexto_lateral_enunciativo` en todo `motor/`,
    y `ruta_cierre_latente` ignoraba sus marcas `OBSERVACION` por
    construcción. Ahora `ruta_cierre_latente` convierte las dos señales
    fuertes (ASIMETRIA_VALORATIVA_ENTRE_ACTORES,
    CIERRE_DISCURSIVO_DE_ALTERNATIVAS) en motivo trazable del cierre
    (objeción, sin retener el cierre ni tocar H). Prueba: CTX-01 (el test
    cambió su aserción: el cierre queda LATENTE con 1 motivo del lateral).
  - Reglas de diseño (fijadas por Marco): ruta condicional; perfilamiento
    acotado (solo datos del contexto del input); arquetipos secundarios y
    subeditados; no duplicación; círculos de Venn (trayectoria de
    iluminación); trazabilidad ≠ predicción; candados de sesgos operativos
    (también al UCIS).

---

## 8. Lateral del orquestador (PR #10, integrado en V7)

- **Función:** el mismo lateral enunciativo, en versión agnóstica, para
  coordinación operativa general (cualquier input en cualquier tarea).
- **Entradas:** el input que se coordina.
- **Fuentes de datos:** el input + `lateral_contexto_enunciativo.py` (copia
  general) + `ruta_contexto_enunciativo.py` (adaptador con estados
  ACTIVA/SIN_ACTIVACION).
- **Dependencias:** `runtime/diagnostics/ruta_contexto_enunciativo.py`,
  `debe_observar()` (ruta condicional: filtros rígidos siempre, otros según
  el input).
- **Produce:** observaciones del lateral en el diagnóstico del orquestador.
- **Veredicto:** CABLEADO / INTEGRADO / FUNCIONAL. Evidencia: PR #10
  fusionado en main del orquestador (merge `8253eaf`); 14 pruebas en verde
  tras el merge (5 fallos iniciales eran `ModuleNotFoundError: jsonschema`
  del venv, no regresión).

---

## 9. Capa U7 — confianza de apuesta post-corrida

- **Función:** observación de robustez de la apuesta, separada de la decisión del predictor. Evalúa seis bloques B1–B6 sobre el RESULT ya construido; no decide ni reescribe H1/H2.
- **Entradas:** RESULT de la corrida (cierre, predictor, señales laterales, acero, efectividad del corte retenido y candidatos emergentes).
- **Fuentes de datos:** el RESULT primario y `motor/u7/confianza_apuesta_u7.py`.
- **Dependencias:** `motor/correr_estandar.py::_confianza_apuesta_u7`, invocado en la ruta estándar antes de escribir el RESULT; el detalle queda en `result["confianza_apuesta_u7"]` y la etapa resumida en el recibo.
- **Produce:** puntaje y desglose B1–B6. Estado actual `calibrada=false`: los seis pesos iguales son placeholder, no pesos aprendidos ni probabilidad calibrada.
- **Veredicto:** CABLEADO / INTEGRADO / FUNCIONAL como observador post-corrida; no altera el predictor. Evidencia: `motor/tests/test_confianza_apuesta_u7.py` y `motor/tests/test_cableado_confianza_apuesta_u7.py`.
  - **C-F5 cerrado en V7** — B5 leía `H1_sellada`, pero el RESULT real trae
    `H1_sellada_compatibilidad`, así que B5 puntuaba 0.0 siempre en RESULTs
    reales (solo pasaba en su fixture). Ahora lee el campo real. Verificado
    en el RESULT real de Themistocles: B5 pasa de 0.0 a 0.5 (H1 sin último
    corte `30_ambicion`, en el set de hipótesis; el 1.0 que el informe
    esperaba suponía que el H1 retenido igualara al H1 completo, lo cual no
    es el caso en estos datos — el valor correcto es 0.5). Además
    `correr_estandar.py:646` (ruta `--t1`) hacía `score["H1_sellada"]` y
    levantaba `KeyError`; ahora usa el campo real.

---

## 10. Coordinador agnóstico (PR #35)

- **Función:** coordinar (agnóstico) la ejecución entre modelos/rutas.
- **Entradas:** la tarea a coordinar.
- **Fuentes de datos:** el propio coordinador.
- **Dependencias:** motor (adaptador declarado "documentación ejecutable").
- **Produce:** recibo de coordinación.
- **Veredicto:** CABLEADO (en su propio paquete) / **INTEGRADO: NO** en el
  motor / FUNCIONAL (en aislamiento: 29 tests).
  - **C-F9 — causa exacta:** el coordinador #35 tiene 29 tests en
    aislamiento y cero llamadores en el motor; su adaptador está declarado
    como "documentación ejecutable". No queda demostrado por el cableado actual porque
    es una decisión de diseño: o se cablea un adaptador real U6 con recibo,
    o se declara explícitamente como biblioteca de referencia. Esa decisión
    está pendiente de Marco. No queda como "pendiente de valoración" sin
    más: la causa y las dos opciones están nombradas aquí.

---

## 11. Límites reales que no deben confundirse con cableado

- **C-F2 (predictor Grupo B, 64.46% / 97.52%):** el número es cita de un txt
  (`PROPUESTA_GRUPO_B_V0_1_PRUEBA_2026-09-06.txt`) que **no existe en el
  repo**, sin script LOO y sin productor de `estado_monomito` en la ruta de
  fábrica (V7: `SIN_PREFIJO_EN_INPUT`). Los 64.46/97.52% quedan como cita
  histórica, no como evidencia V7. Para convertirlos en evidencia hace falta
  el script LOO y el txt fuente, que no están en el repo.
- **C-F9 (coordinador #35):** ver sección 10.
- **C-F8 resto (compuerta de cierre):** ver 5.3 — el `review_pending` real es
  stub; el bloqueo real espera la evaluación de contradicciones.
- **A-F4 resto (Z90 sin disciplina):** decisión de diseño documentada (ver
  1.4) — el gate solo se impone a casos que lo declaran.
- **B-H4 verificador (si no se cablea):** no aplica — se cableó (ver 2.10).
- **F3/F7:** cerrados como diseño con causa (ver 1.3 y 5.1).
- **F5 (fila histórica `feeds_predictor=True` en laterales):** corregida en
  V7 (A-F5: la fila del plugin token ahora dice `feeds_predictor=False`).


## 12. Lectura funcional agnóstica post-corrida

- **Función:** comprobar si el artefacto final cumple el propósito observable definido por el contrato de tarea y si su relación con la entrada y la evidencia puede reconstruirse.
- **Criterios:** los define cada contrato; no se codifican criterios editoriales de CAPCOT ni una lista universal de checks.
- **Entradas:** contrato de tarea, extractos mínimos de input, artefacto final, evidencia seleccionada y revisión emitida por otro modelo.
- **Dependencias:** motor/lectura_funcional_v1.py (prepare / apply), motor/LECTURA_FUNCIONAL_REVIEW_V1.schema.json, docs/SKILL_LECTURA_FUNCIONAL_AGNOSTICA_V1.md.
- **Produce:** sidecar FUNCTIONAL_GATE_RESULT_V1 con PASS / FAIL / INDETERMINATE y ALLOWED / BLOCKED / NOT_GATING. No modifica RESULT, RECIBO, H1/H2, ranking, pesos ni evidencia.
- **Punto de integración:** post-corrida, antes del handoff. El revisor necesita el RESULT final y su hash; por eso no se invoca dentro del predictor. El orquestador debe ejecutar prepare, solicitar revisión independiente y ejecutar apply antes de liberar el artefacto.
- **Veredicto inicial:** CABLEADO_POSTRUN. La integración automática en correr_estandar.py no está hecha; la revisión externa todavía requiere otro modelo. CI verificado: run 46106989385, 134 pruebas aprobadas en 50.30 s.
- **Independencia:** el validador exige modelos y run_id distintos, pero la identidad real no está autenticada; el sidecar informa DECLARED_ONLY.
- **Límite:** no es un predictor, no recalibra U7 y no resuelve C-F8. review_pending de StinkBox conserva su bloqueo documentado.

