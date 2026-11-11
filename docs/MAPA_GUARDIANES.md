# Mapa de guardianes del motor U6

Fecha de este mapa: 2026-11-10 (America/Mexico_City).  
Repo: `marcojpad-hash/motor-u6-storage`.  
Commit leído (HEAD de `main` al documentar): `37e03e103973b7e4a79e23dd721728b81ba7d4a6` (`audit: snapshot de corridas Actions`).

Este documento describe **solo** las piezas de *este* repositorio que vigilan, filtran, juzgan o bloquean. No describe las que generan hipótesis ni las que ejecutan el motor. Polti, Souriau y Propp no son guardianes (son familias o lentes narrativas); no hay en este repo un guardián cuya función sea vigilarlos. En este repo **no hay** un paquete `guardia/` agnóstico ni un archivo llamado Cancerbero; el control de flujo vigente es `control_flujo_soluciones.py`.

Cómo se verificó: se recorrió el árbol de `main`, se buscó por nombre y por llamadas (`guardian`, `guardia`, `sombrero`, `sherlock`, `copi`, `beristain`, `candado`, `compuerta`, `decimo`, `veto`, `filtro`, `validador`, `control_`), y se leyó el cableado en `MOTOR_V15_3_UNICO_20260927.py`, `laterales_unico_v1.py`, `correr_estandar.py` y `casos/fabrica/fabrica.py`. Lo que no se ejecutó en una corrida en vivo se marca como “leído en código, no reproducido en esta sesión”.

## Cómo se orquestan

El motor activo de corrida es `motor/motor/MOTOR_V15_3_UNICO_20260927.py`. El Engine canónico (`motor/Engine_V5_CANONICO_SOLO.py`, 30507 bytes, sha `665c39a2…`) y el catálogo `patterns_final_v14.json` (244 patrones, sha `d827dcc3…`) están candados aparte: ningún guardián de contenido debe escribirlos.

La fábrica (`casos/fabrica/fabrica.py`) no llama al motor en crudo: copia `motor/`, corre `calibracion/arnes_calibracion.py`, y el arnés llama `correr_estandar.py`, que a su vez llama a UNICO.

Hay tres orquestadores de control:

1. **`guardianes_control_v1.py`** (`VERSION = GUARDIANES_CONTROL_V1_2_UNICO_20260927`). UNICO lo llama *después* del predictor, sobre copias, vía `_ceb_stage("guardianes_control_v1", ...)`. Corre, en este orden: décimo hombre / latencia, pregunta detrás v2, pregunta dirigida + post hoc, falacias, Copi, polaridad, hombre de acero, Sherlock/rigor, y al final Beristáin (que se corrige con los vecinos lógicos). Banderas de bloque: `LIMPIO | MARCA | NO_RESUELTO | LATENTE | ERROR`. Contrato: `can_decide_H=False`; no escriben H ni `patterns`. Si hay `NO_RESUELTO` o `DOBLE_NEGACION_LITOTE` (o un cierre en banda de empate), `ruta_cierre_latente()` pone `estado_cierre=LATENTE`, lo registra en `control_latencia_decimo_hombre` y UNICO corre tortugas y escribe un evento de latencia en StinkBox. **H1/H2/top1 no cambian** (UNICO lo verifica con hash antes/después).
2. **`laterales_unico_v1.py`**. UNICO lo llama en `pre_predictor` (algunos filtros sí llegan a votos laterales) y en `post_predictor` (sombrero de salida y verificación CEB de piezas).
3. **Compuertas de fábrica y CEB**. El runtime (`ceb_runtime_v0_6_flow.py`) observa la corrida. Las compuertas de lote viven en `fabrica.py` y pueden salir con código 9.

Los SHA esperados que declara `guardianes_control_v1.py` para cinco piezas (`control_latencia_decimo_hombre.py`, `plugin_pregunta_detras_v2.py`, `plugin_polaridad_causal.py`, `plugin_metodo_rigor.py`, `sidecar_ablacion_hombre_acero.py`) **coinciden** con los archivos actuales de `main` (verificado el 2026-11-10).

---

## 1. Capa de entrada

### 1.1 Sombrero blanco (filtro de entrada y de salida)

No hay otros “sombreros” (negro, etc.) en el código de este repo. El sombrero blanco son tres piezas distintas, no una sola.

**A. `motor/motor/sidecar_sombrero_blanco_filtro_v1.py`** (`SOMBRERO_BLANCO_FILTRO_V1_PATCH010`)

- Qué vigila: en entrada, tokens fuera de catálogo, ruido de protocolo (`PROTOCOL_NOISE_RE`), campos probabilísticos prohibidos en cortes, y qué textos son hechos observables (`hecho`/`narracion`/`facts`/`texto`) frente a metadato (`source_note`/`nota`). En salida, que top10/H1/H2 y su evidencia propia sean del catálogo y no traigan ruido de protocolo.
- Entrada → salida: dict de entrada con `textos_admitidos`, `textos_excluidos`, `fuera_catalogo`, etc.; dict de salida con `salida_limpia` (bool) y listas de violaciones. `can_decide_H=False`, `feeds_predictor=False`.
- ¿Bloquea o solo marca? Marca. No modifica el input ni la salida. Sí tiene efecto colateral: los canales de texto del hub (`cuerpo_arco`, `area_tokens`) **solo leen** `textos_admitidos`.
- Dónde se llama: `laterales_unico_v1.pre_predictor` (`sombrero_blanco_entrada`) y `post_predictor` (`sombrero_blanco_salida`). UNICO sí llama al hub. Conectado.
- Atado a U6: sí (catálogo 244, agujeros `motor.holes`, familias, H1/H2).

**B. `motor/motor/plugin_sombrero_blanco_token.py`**

- Qué vigila: tokens `fuera_catalogo` de la corrida. No los canoniza; los acumula en `stinkbox_tokens_descubiertos.json`.
- Salida: `status=EXECUTED`, `can_decide_H=False`, conteos de la corrida y del StinkBox.
- ¿Bloquea o solo marca? Marca y escribe el store de StinkBox. No veta la corrida.
- Dónde se llama: UNICO, *después* de la apuesta, vía CEB (`plugin_sombrero_blanco_token`). Conectado. El sidecar de filtro **no** llama a `revisar()` (lo dice el propio docstring).
- Problema evidente: el laterales aún anota que una fila histórica de UNICO declaraba `feeds_predictor=True` (falso; se corrigió en 010b, la llamada actual declara `False`).

**C. Sombrero absorbido en UNICO (`_protocol_quality` dentro de `_run_transversal_guards`)**

- Qué vigila: la misma regex de ruido de protocolo y campos prohibidos, sobre la pregunta y la forma de los cortes, *antes* del predictor.
- Salida: siempre `status=PASS`, con banderas `protocol_noise_in_question` y `no_probabilistic_fields_in_input`. `sombrero_blanco=ENFORCED` es una etiqueta, no un veto.
- ¿Bloquea o solo marca? Solo marca. Aunque haya ruido, el status sigue siendo `PASS`.
- Conectado (absorción en UNICO). Atado a U6 (cortes P/A/C).

### 1.2 `guardian_entrada_autoevidencia_v1.py`

- Qué vigila: tokens de entrada P/A/C que son nombres de familia del catálogo (circularidad entrada→salida) o que *parecen* etiqueta de familia (`FORMA_FAMILIA`).
- Salida: `status=EXECUTED` o `EXECUTED_WITH_FINDINGS`; `bandera` bool; `accion=SOLO_BANDERA`; `can_decide_H=False`.
- ¿Bloquea o solo marca? Solo marca. El motor no quita esos tokens.
- Dónde se llama: `laterales_unico_v1.pre_predictor` (`guardian_entrada_autoevidencia`). Conectado.
- Atado a U6: sí (nombres de familia del 244).

### 1.3 `capa_llm/filtro_entrada_dirigida_017.py`

- Qué vigila: datos “dirigidos” en el payload (identidad, obra, calendario, futuro post-Z, autoetiquetas de familia, teleología, sesgo de consultor, meta-protocolo, etc.).
- Salida: banderas con `tipo`, `accion` (`neutralize`/`strip`/`warn`/`reject-cut`/`move_to_sidecar`/`info`) y `severidad`. También hay `verificar_salida_llm` para el cierre.
- ¿Bloquea o solo marca? Depende del modo. El módulo documenta modo en vivo por defecto `activo` (aplica neutralize/strip solo a IDENTIDAD_NOMBRE, IDENTIDAD_OBRA y CALENDARIO). **UNICO, en cambio, defaulta `FILTRO_017=traza`**: analiza sin modificar el caso. Si el módulo falta o falla, la corrida sigue con el caso crudo. No es compuerta de decisión de H.
- Dónde se llama: UNICO al entrar a `run()` (`_aplicar_filtro_017`) y también `correr_estandar.py`. Conectado. La consulta dirigida *no* se cablea dentro de `run()` (vive en `correr_estandar`).
- Atado a U6: sí (catálogo, Z90, tokens P/A/C, sujetos).
- Problema evidente: desacuerdo de default (`activo` en el docstring del módulo vs `traza` en UNICO).

### 1.4 Compuerta Z_trabajo (`motor/calibracion/gate_z90.py`)

- Qué vigila: que nada posterior al corte de trabajo entre al motor (reglas R1–R7: fechas, evidencia, archivo web, años posteriores, lista negra, lenguaje de futuro).
- Salida: lista de errores; cualquier violación = rechazo.
- ¿Bloquea o solo marca? **Bloquea**. En `fabrica.preparar_z`, una violación tumba el lote y no escribe nada. En `fabrica.correr`, si la entrada trae `gate_z`, revalida y sale con código 8. El arnés también rechaza el caso si hay `gate_z` o `FABRICA_GATE_Z90=1`.
- Conectado en fábrica/arnés. No es un filtro interno de cada `run()` de UNICO salvo que la entrada ya venga con `gate_z`.
- Atado a U6: sí (freeze, Z, desenlace sellado, modo histórico/vivo).

La propia `fabrica.preparar()` (sin Z) también valida vocabulario 244, pesos 0,60–0,84, ausencia de campos de desenlace y hashes no duplicados, y **bloquea** el lote si falla. Es una compuerta de armado, no un guardián de corrida.

---

## 2. Capa de lógica y razonamiento

Todas las de 2.1–2.7 corren dentro de `correr_guardianes()` (UNICO, post-predictor, copias). Un fallo de un guardián no detiene la corrida: sale `ERROR` en ese bloque.

### 2.1 Décimo hombre / latencia — `control_latencia_decimo_hombre.py`

- Qué vigila: si hay datos suficientes para resolver, o hay que esperar. No es un sidecar de contenido; es control estructural de cierre.
- Entrada: `p_momento` + tokens. Estados del expediente: `LATENCIA | DESEMPATE_DECIMO | ALMACENADO_ESPERANDO_DATOS | RESUELTO | OFF`. Si `p` cae en la banda 0,45–0,55, hace una re-tirada determinista; si sigue el empate, almacena y no cierra. Acciones: `LATENCIA_ACUMULAR_TOKENS`, `ESPERAR_MAS_TOKENS`, `SEGUIR_CON_P_DESEMPATADA`, etc. `Alimenta_H=NO`.
- En el bloque `DECIMO_HOMBRE_LATENCIA`, `guardianes_control` calcula `p = 0.5 + 0.5·tanh(gap/σ)` por corte y en el cierre. Bandera: `LATENTE` si el cierre queda en banda, si no `MARCA` o `LIMPIO`.
- ¿Bloquea o solo marca? Marca de proceso. No escribe H. Si el cierre queda latente, alimenta `ruta_cierre_latente` (retiene el *estado* de cierre).
- Conectado (vía `guardianes_control`). El store por caso se borra al terminar el bloque.
- Atado a U6: sí (tablero 244, top1/top2, case_id).

### 2.2 Pregunta detrás v2 — `plugin_pregunta_detras_v2.py`

- Qué vigila: perfilamiento y tropos en la pregunta y los textos (lítote, hipérbole, etc.).
- Salida del plugin: `bandera=RED_FLAG_POSIBLE_PERFILAMIENTO | MARCAJE_PERFILAMIENTO | None`; el bloque del orquestador la traduce a `MARCA` o `LIMPIO`. Acción del plugin: `continuar_con_highlight` o `continuar`.
- ¿Bloquea o solo marca? Solo marca.
- Conectado. SHA verificado. Atado a U6 en el uso (textos del caso), el plugin en sí es más léxico.

### 2.3 Pregunta dirigida + post hoc, y falacias — `plugin_pregunta_dirigida_v0_5_1.py`

Dos bloques:

- `PREGUNTA_DIRIGIDA_POST_HOC`: P∧O / pregunta dirigida en la pregunta, y post hoc en cada texto.
- `FALACIAS`: clasificador 0.5.1 (`AF`, `AD`, `CS`, `BC1`, `BC2`, `PQ`, `EQ`) en cada texto.

Estados de marca: `DETECTADA` (severidad `hard`) o `POSIBLE` (`soft`). Bandera del bloque: `MARCA` o `LIMPIO` (o `ERROR` si falta el archivo).

¿Bloquea o solo marca? Solo marca (son vecinos de Beristáin). Conectado.

### 2.4 Copi — `guardian_logica_copi_v1.py` (`LOGICA_COPI`, v1.0.1)

- Qué vigila: consistencia lógica al estilo Copi (9 reglas de inferencia + 10 de reemplazo + falacias espejo). Tres adaptadores: (a) condicionales/causales del texto, (b) la regla de cierre del motor (`DETERMINADO` / latencia / compuerta), (c) cadena del top1 por corte (non sequitur, subdeterminación H1/H2).
- Bandera: `MARCA` si hay `DETECTADA`; `NO_RESUELTO` si solo hay marcas no resueltas (átomo ambiguo, conclusión con átomo nuevo, top1 que no encabeza ningún corte, subdeterminación); `LIMPIO` si no hay marcas.
- ¿Bloquea o solo marca? Marca. Un `NO_RESUELTO` puede retener el cierre vía `ruta_cierre_latente`.
- Conectado. Muy atado a U6 en (b) y (c) (`compuerta_cierre`, `information_state`, cadena 244). El núcleo proposicional es genérico.

### 2.5 Polaridad causal — `plugin_polaridad_causal.py`

- Qué vigila: polaridad del claim causal en cada texto (negación simple vs lítote).
- Etiquetas que levantan marca: `NIEGA` (`DETECTADA`) y `DOBLE_NEGACION_LITOTE` (`LATENTE`). Bandera: `LATENTE` si hay lítote, si no `MARCA` o `LIMPIO`.
- ¿Bloquea o solo marca? Marca. La lítote entra en `ruta_cierre_latente`.
- Conectado. SHA verificado.

### 2.6 Hombre de acero — `guardian_acero_rival_v1.py` + `sidecar_ablacion_hombre_acero.py`

- Qué vigila: si el top1 sobrevive a la mejor versión honesta de los rivales (steelman: empates ≤10 % del rango a favor del rival; `EPS=0.25`). Veredictos por rival: `SOBREVIVE | NO_RESUELTO | CAE`. La ablación de pilares de H1 es observación (casi siempre sale “frágil”; no levanta la bandera por sí sola).
- Bandera del bloque: `MARCA` si algún rival deja al top1 en `CAE`; `NO_RESUELTO` si empata; `LIMPIO` si sobrevive (ignorando las OBS de ablación).
- ¿Bloquea o solo marca? Marca. `NO_RESUELTO` puede retener el cierre. Modo estricto sí usa el steelman como criterio C2 del cierre estricto.
- Conectado. Muy atado a U6 (fusión por rangos, dimensiones del predictor, top10).

### 2.7 Sherlock / método de rigor — `plugin_metodo_rigor.py` (bloque `SHERLOCK_RIGOR`)

El plugin suelto es una alarma corta (Hecate: el letrero no cambió en 4 cortes; Holmes: la hipótesis nombra apellido; Schopenhauer: “como yo dije”). El bloque en `guardianes_control` lo envuelve con la cadena top1 por corte, tokens de hecho del top1 (`HOLMES_TOP1_SIN_TOKENS_DE_HECHO`) y masa a favor vs en contra (`SCHOPENHAUER_TABLERO_EN_CONTRA`).

- Bandera: `MARCA` o `LIMPIO` (o `ERROR`).
- ¿Bloquea o solo marca? Solo marca. No escribe H. `can_decide_H=False`.
- Conectado vía `correr_guardianes`. También hay una llamada pre en laterales (`plugin_metodo_rigor (alimentado)`), como sensor, no como decisor. SHA verificado.
- Atado a U6 (cadena por corte, `own_evidence`).

### 2.8 Modo estricto — `modo_estricto_v1.py`

- Qué vigila: cierre estricto con *todos* estos criterios: C0 la ruta de guardianes no quedó `LATENTE`; C1 el top1 encabeza al menos un corte; C2 el acero descarta al rival más fuerte (`SOBREVIVE`, `dif_acero > 0.25`); C3 H1≠H2 distinguibles y fuera de banda de empate; C4 Aquiles estable. Si falla alguno → `estado_cierre_estricto=LATENTE` con todos los motivos.
- ¿Bloquea o solo marca? Retiene el *estado de cierre estricto*. No cambia H1/H2/top1/predictor/patterns (UNICO lo verifica). Se apaga con `MODO_ESTRICTO=0` (por defecto está on).
- Conectado en UNICO, después de los guardianes. Atado a U6.

### 2.9 Décimo hombre con esteroides — `decimo_hombre_esteroides_mayeutica_v1.py` (v1.1.0)

- Qué vigila: contrafactuales reales y mayéutica *después* del cierre. Consume candidatas y dimensiones del predictor. No interpreta un ataque registrado como prueba ejecutada. Entrega una conclusión adversarial aparte. Diagnostica Copi/Sherlock si vinieron vacíos, en vez de un PASS falso.
- ¿Bloquea o solo marca? Marca / auditoría. No altera predictor, H ni la apuesta original.
- Conectado en UNICO (con recuperaciones PATCH05 si falla). Atado a U6, pero el módulo evita nombres de casos concretos.

### 2.10 Verificador de consistencia adversarial — `plugin_verificador_consistencia_adversarial.py`

- Qué vigila: invariantes de contrato en la corrida real (empate exacto 0.0 no puede producir H, cierre solo si se agotó la resolución, laterales no escriben H, freeze, inmutabilidad del canon, etc.) más fixtures adversariales y un paquete para revisión LLM (sin hipótesis deseada).
- Salida: `status=PASS` o hallazgos; `violations` (p. ej. `TIE_NO_WINNER`, `RESOLUTION_BEFORE_CLOSE`, `PATTERNS_HASH_DECLARATION_MISMATCH`). `FEEDS_H=False`.
- ¿Bloquea o solo marca? Solo marca. UNICO lo registra como `EXECUTED` o `EXECUTED_WITH_FINDINGS`.
- Conectado (post-predictor en UNICO). Atado a U6 (Engine, 244, Caldero, freeze).

---

## 3. Capa de retórica / tropos

### 3.1 Beristáin — `guardian_tropos_beristain_v1.py` (`TROPOS_BERISTAIN`, v1.0.0)

- Qué vigila: lenguaje figurado en pregunta y textos para que **no se lea literal** como evidencia o perfil (metáfora, metonimia, sinécdoque, lítote, hipérbole, ironía solo como `NO_RESUELTO`, etc.). Palabra suelta ≠ tropo. Corre después de falacias, Copi, post hoc y polaridad, y `corregir_con_vecinos()` anota (sin cambiar las banderas ajenas) cuando una marca lógica se apoya en una figura.
- Bandera: `NO_RESUELTO` si alguna marca lo es; `MARCA` si hay `DETECTADA` o `POSIBLE`; `LIMPIO` si no. `can_decide_H=False`.
- ¿Bloquea o solo marca? Marca. `NO_RESUELTO` puede retener el cierre. También señala `TOKEN_POSIBLEMENTE_FIGURADO_EN_TABLERO` si un token del 244 se parece al fragmento figurado; eso no saca el token del tablero.
- Conectado (último bloque de `correr_guardianes`). El catálogo de tropos es de Beristáin; el acoplamiento al tablero 244 y a los vecinos sí es U6.
- Cobertura: varias figuras del inventario siguen `PENDIENTE_DE_REGLA` (metalepsis, imagen, …), documentado en el propio módulo.

---

## 4. Capa de investigación (fuentes, vecinos, Caldero, StinkBox)

### 4.1 Guardián de pistas LLM del Caldero — `guardian_pistas_llm_caldero_v1.py`

- Qué vigila: pistas `caldero_llm_neighbor_hints` *antes* de que lleguen al sidecar. Descarta por IDENTIDAD (nombre/alias del caso), FUTURO (desenlace, muerte, éxito…), CALENDARIO (años 1000–2099) y FORMA (vacío, >60 chars, URL, sin letras). Determinista, sin red ni LLM.
- Salida: lista `kept` + auditoría (`aceptadas` / `descartadas` con huella, no el token). `can_decide_H=False`.
- ¿Bloquea o solo marca? **Filtra de verdad**: lo descartado no se anexa a los vecinos. No veta la corrida.
- Dónde se llama: autoridad del módulo; `casos/fabrica/pistas_llm_caldero_v1.py` lo carga y `fabrica._validar_pistas_llm` lo usa. El sidecar/auditoría de Caldero en UNICO también deja `guardian_pistas_llm` en el audit. Conectado.
- Atado a U6 (Caldero, identidad del caso). La lógica de motivos es extraíble.

### 4.2 Filtro de identidad zoom out → zoom in — `filtro_identidad_zoom_out_zoom_in.py`

- Qué vigila: fuentes de búsqueda del Caldero contra la identidad del caso (decisiones: `descartado_en_zoom_out`, `distinto_en_zoom_in`, `misma_identidad_zoom_in`, `sin_senal_conservar`).
- ¿Bloquea o solo marca? **Solo reporta.** Laterales sí lo llama (`ZoomIdentityFilter.filter`), pero el comentario del hub es explícito: “llamada real, solo lectura (no entra al Caldero ni a H)”. Los descartes no se devuelven al sidecar.
- Si no hay fuentes o no hay `caldero_identity`, queda `ACTIVA_MUDA`.
- Conectado como sensor, desconectado como filtro efectivo del Caldero. Atado a U6.

### 4.3 Filtro de relleno — `filtro_relleno_013.py` (incluye años / PATCH 015)

- Qué vigila: tokens de vocabulario de vecinos (memoria Caldero, luces, vecinos de la corrida) que no deben votar: stopwords ES/EN, `src_*`, numéricos puros, <3 caracteres, palabras de año.
- ¿Bloquea o solo marca? **Filtra el voto** de esos tokens (no entran a insumos del acero ni al voto de vecinos). No decide H ni toca favor/contra del catálogo. Deja traza `filtrados_013` / `anos_015`.
- Conectado en el tubo de UNICO (pieza `filtro_relleno_013.py` vía `_ceb_stage` / `_RUN_CTX`). Atado a U6 en el uso (vecinos/Caldero); las listas son genéricas.

### 4.4 Filtro de tokens de arquetipos v2 — `filtro_tokens_arquetipos_v2.py` (sobre v1)

- Qué vigila: ruido del StinkBox / tokens de arquetipos (dígitos, genéricos EN/ES, meses, prefijo `src_`, etc.). Exención: si el token está en el vocabulario del 244, se conserva.
- ¿Bloquea o solo marca? Filtra al admitir tokens en StinkBox. No forma parte del `run()` de UNICO.
- Dónde se llama: `scripts/sincronizar_storage.py` y `scripts/limpiar_tokens_stinkbox.py`. Conectado en la sync post-fábrica (`FABRICA_SYNC` por defecto on). Si el filtro no carga, la sync **no admite** tokens.
- Atado a U6 (lectura del catálogo 244).

---

## 5. Capa de ejecución y flujo

### 5.1 CEB (runtime) — `motor/motor/ceb_runtime_v0_6_flow.py` (`CEB_V0.6.3_FLOW_LINEAGE_RUNTIME_IDENTITY_PROJECTION`)

- Qué vigila: si cada etapa **corrió de verdad**, qué leyó y escribió, y si lo declarado coincide con lo observado. Piezas: `FlowLedger`, `FlowTracer`, `ObservableDict`, `FlowVerifier`, hook de auditoría, contexto por hilo.
- Estados de etapa: `FAILED`, `STARTED_NOT_CLOSED`, `REGISTERED_NOT_STARTED`, `EXECUTED_WITH_WARNINGS`, `EXECUTED_AND_CONNECTED`, `OUTPUT_PERSISTED_WITHOUT_CONSUMER`, `OUTPUT_NO_OBSERVED_CONSUMER`, `FAILED_NON_AUTHORITATIVE`.
- Anomalías (entre otras): `REPORTED_EXECUTED_NOT_OBSERVED`, `NON_AUTHORITATIVE_STAGE_FAILED`.
- Veredictos: `VERIFIED_FLOW | VERIFIED_FLOW_WITH_ANOMALIES | INCOMPLETE`.
- ¿Bloquea o solo marca? El runtime **marca** y deja ledger. No llama `exit(9)`. La decisión de tumbar un lote es de las compuertas de fábrica, con las severidades que arma laterales (ver 5.2–5.3). Documentado en `docs/CEB_INVESTIGAR_Y_RESOLVER.md`.
- Dónde se llama: UNICO carga el módulo, envuelve etapas con `_ceb_stage` / `ceb.call`, y al final `FlowVerifier(...).verify(result)`. Conectado.
- Atado a U6 en el cableado (nombres de etapa, piezas del motor); el runtime en sí (ledger, estados, veredictos) es el candidato más limpio a extraer.

### 5.2 Alertas CEB por pieza — `laterales_unico_v1.alerta_pieza` / `alerta_ejecucion` / `aplicar_alertas`

Severidades (las que usa la fábrica):

| Severidad | Significado |
|---|---|
| `OK` | Corrió (`ACTIVA`, `EXECUTED`, `GUARDIAN_FILTRO`, etc.) |
| `INFO_CORRIO_SIN_SENAL` | Corrió pero no aportó (`ACTIVA_MUDA`) |
| `INFO_OMISION_CONTRACTUAL` | El contrato permite no correr (`SUPERADA`, `ABSORBIDO_EN_GUARDIA_TRANSVERSAL`, `NOT_APPLICABLE`, `required=False`) |
| `FALLO_EJECUCION` | Debía correr y no corrió (`NO_CORRE`, `APAGADA_POR_FLAG`, `API_PENDING`, `NO_INVOCADO`, `SIN_EJECUCION`, `NO_ENCONTRADO_EN_STORE`, `SIMULADO_FIXTURE`, `INTENTADO_FALLIDO`, `OMITIDO`/`SKIPPED`/`FAILED` sin contrato) |
| `REQUIERE_CONTRATO` | Estado desconocido: no se da por OK |

Estados específicos de búsqueda Caldero: `EJECUTADO`, `OMITIDO_POR_CONDICION`, `SIMULADO_FIXTURE`, `NO_INVOCADO`, `INTENTADO_FALLIDO`, `SIN_RECIBO_CEB`.

### 5.3 Compuertas de fábrica — `casos/fabrica/fabrica.py`

**`compuerta_caldero`**: por defecto la búsqueda Caldero es opcional (`FABRICA_CALDERO_REQUERIDO` default 0). Solo marca incumplimiento si se pide explícito. Veredicto: `OK` o `FALLO_EJECUCION_CALDERO`.

**`compuerta_piezas`**: junta `FALLO_EJECUCION` y `REQUIERE_CONTRATO` de todos los casos del lote. Veredicto: `OK`, `FALLO_EJECUCION_PIEZAS` o `REQUIERE_CONTRATO`. `FABRICA_PIEZAS_REQUERIDAS=0` la deja en aviso. `REQUIERE_CONTRATO` se reporta y **no** tumba el lote.

¿Bloquea? **Sí**, al final de `correr()`: `return 9` si hay incumplimientos de Caldero (cuando es requerido) o fallos de ejecución de piezas (cuando `requerido` es verdadero). Código 3 = candado de Engine roto; 8 = Z_trabajo rechazado.

Conectado en el lote. Atado a U6 por los nombres de pieza, no por la lógica de la compuerta.

### 5.4 Compuerta de cierre del predictor — `_compuerta_cierre` en UNICO

- Qué vigila: pendientes vivos / latencia que contradicen un cierre `DETERMINADO`.
- Puede pasar `information_state` a `LATENCIA_INFORMACIONAL` (`reason=compuerta_cierre_pendientes_vivos_contradicen`). Decisiones típicas incluyen `CIERRE_BLOQUEADO_LATENCIA` (la usa Copi).
- ¿Bloquea o solo marca? **Retiene el cierre** (no corona DETERMINADO). No reescribe H. Conectado en el predictor de UNICO. Atado a U6.

### 5.5 Guardia no cruce — `plugin_guardia_no_cruce.py` y clase absorbida en UNICO

- Qué vigila: que un lente lateral no mutue el estado bayesiano/tableros ni traiga campos probabilísticos (`confianza`, `p_final`, `score`, etc.).
- Excepciones: `ContaminacionBayesianaError`, `CampoProbabilisticoProhibidoError`.
- ¿Bloquea o solo marca? La clase **levanta excepción** (bloquearía esa rama). En UNICO la lógica efectiva corre en `GuardiaNoCruce` *absorbida* dentro de `_run_transversal_guards` (snapshot de tableros P/A/C, validación de `features` antes del predictor). El archivo `plugin_guardia_no_cruce.py` se carga como artefacto y se declara `ABSORBIDO_EN_GUARDIA_TRANSVERSAL`; no se invoca como API independiente. `sensor_perfil_narrador_v0_1.py` sí instancia el archivo para validar su salida.
- Conectado (absorción). Hay dos implementaciones (archivo vs UNICO) que no son idénticas: el archivo vigila `hyp_state`; UNICO vigila tableros de anexos. Atado a U6.

### 5.6 Control de flujo (agua vs piedra) — `control_flujo_soluciones.py`

- Qué vigila: la conducta ante un obstáculo. Clasifica la “piedra” (`hash_no_identico`, `archivo_ausente`, typo de ruta, import, auth, ambigüedad, drama genérico) y devuelve contornos (siguientes acciones). `bypass_hash_cambio` permite seguir en laterales/protocolo; en Engine/244/FREEZE avisa y **no** deja correr como canon. Formato obligatorio: PIEDRA / CONTORNO / SIGUIENTE / EVIDENCIA. `Alimenta_H=NO`, `SOLO_MARCA=True`.
- ¿Bloquea o solo marca? Es una biblioteca de conducta, no un veto de corrida (salvo el candado duro de Engine en `bypass_hash_cambio`).
- ¿Conectado? **Parcial.** `protocolo_kernel_motor.py` lo usa en `aplicar_protocolo` y `verificar_hash_con_bypass`. `matriz_corrida.py` también lo importa. Pero el `_protocolo_orden0` de UNICO, que sí corre al arrancar, **solo** llama `arranque_matriz()` y `clasificar_para_protocolo(pregunta)`: no llama `aplicar_protocolo` ni `contornar`. En una corrida normal de UNICO este control no se dispara solo cuando algo falla. El motor nativo viejo (`MOTOR_V15_3_NATIVO_V0_9_UNICO.py`) sí lo importaba; no es el runner activo.
- Atado a U6 en los ejemplos y en el candado Engine/244; la metáfora y el catálogo de piedras son extraíbles.

### 5.7 Protocolo kernel — `protocolo_kernel_motor.py`

- Qué hace en la corrida activa: orden 0, solo registro (clasifica la pregunta, arranca matriz, bitácora). Documenta “no para salvo candado duro”.
- No es un guardián de contenido. Es el enchufe previsto para el control de flujo, hoy subusado (ver 5.6).

### 5.8 Candado de plugins — `motor/motor/candado_plugins.py`

- Qué vigila: que cada `.py` de `motor/` **compile**, señales de corrupción (comillas curvas, dunders rotos) e imports directos al Engine canónico (`ImportProhibidoError`). Cambio de hash = `BYPASS_HASH_CAMBIO` (avisa, actualiza manifiesto, **sigue**).
- ¿Bloquea o solo marca? Bloquea si no compila o si importa el Engine. No bloquea un cambio de hash legítimo. `correr_estandar.verificar_candado_plugins` declara `bloquea=False` a nivel de corrida (avisa por stderr).
- Dónde se llama: `correr_estandar.py` (la fábrica pasa por ahí). **No** está llamado desde UNICO `run()` directamente. Si alguien invoca UNICO a mano, este candado no corre.
- Atado a U6 (lista de imports prohibidos del Engine).

### 5.9 Candado del Engine y del catálogo

Tres frentes, la misma huella:

- `motor/CANDADO_ENGINE.json` y `motor/ACTIVE_ENGINE_SELECTION.json`: Engine `665c39a2…` (30507 bytes) y patterns `d827dcc3…`.
- `fabrica.candados()`: **bloquea** el lote con código 3 si el hash no coincide antes de correr; vuelve a verificar después.
- `motor/scripts/candados.py`: escribe un JSON de aviso; `permitir_corrida=True` siempre (`BYPASS_HASH_CAMBIO` no para el tubo). Es un chequeo local de pack, más laxo que la fábrica.

`portero_engine.py` (el “mellizo” que nombra `candado_plugins.py`) **no está** en este repo.

---

## 6. Capa de salida

- El sombrero blanco de salida (1.1.A) corre en `laterales_unico_v1.post_predictor`. Solo marca `salida_limpia`.
- `filtro_entrada_dirigida_017.verificar_salida_llm` existe para revisar el texto de salida / `cierre_final`. En esta lectura no se vio una llamada equivalente a la compuerta de entrada dentro de `run()` de UNICO (la compuerta de entrada sí está cableada). No se afirma que esté desconectada del todo: puede usarla la capa LLM vía `consulta_dirigida_v1.py` en `correr_estandar`. No se abrió esa rama línea por línea en esta sesión más allá de constatar que `consulta_dirigida` carga el módulo 017.
- `ruta_cierre_latente` + `modo_estricto` + `compuerta_cierre` retienen el estado de cierre, no reescriben H1/H2. El cierre de fin de corrida va en `cierre_final`.

---

## Qué no es guardián (y se buscó)

- **Polti, Souriau, Propp**: familias o lentes. No hay un guardián dedicado a vigilarlas. El CEB sí las lista como *piezas que deben ejecutarse* si están cableadas, igual que cualquier otra.
- **`plugin_sesgo_lectura.py`**: mide solape y “carne nueva” entre cortes. El propio módulo dice que no hay etiqueta automática de “sesgo”. No es veto ni filtro.
- **`plugin_resolucion_autonoma_consistencia.py`**: control post-predictor que intenta *resolver* desajustes mecánicos del paquete. Es arreglo, no vigilancia; UNICO lo corre, pero no se trata aquí como guardián.
- No aparecen en este repo otros sombreros, ni `cancerbero`, ni un paquete `guardia/` agnóstico.

---

## Problemas evidentes

1. **Varios “filtros de entrada” no filtran en el default.** El sombrero absorbido en UNICO siempre sale `PASS`. `FILTRO_017` defaulta a `traza` (el docstring del módulo dice `activo`). El filtro de identidad zoom **corre y no devuelve** los descartes al Caldero. El sombrero de sidecar sí restringe textos del hub, y el de pistas LLM sí descarta tokens; no todos los guardianes de entrada tienen ese diente.
2. **Los guardianes de contenido casi nunca vetan; solo el estado de cierre y las compuertas de lote bloquean.** `can_decide_H=False` es el contrato. `ruta_cierre_latente` y el modo estricto pueden dejar el cierre en `LATENTE` sin tocar H1/H2. Un lote de fábrica sí puede morir con código 9 (CEB) o 3 (Engine) u 8 (Z). Eso está bien como diseño, pero se presta a leer “ENFORCED” / “GUARDIAN/FILTRO” como si cortaran el paso cuando a menudo solo anotan.
3. **`control_flujo_soluciones.py` no está en el tubo siempre-on de UNICO.** El protocolo de orden 0 no llama a `contornar` / `aplicar_protocolo`. Ante un fallo de ejecución, la corrida no aplica sola la regla PIEDRA/CONTORNO/SIGUIENTE/EVIDENCIA. Además, `GuardiaNoCruce` está duplicada (archivo vs absorción) y `candado_plugins` no corre si se llama a UNICO sin `correr_estandar`.

Casi todos los guardianes de *contenido* están atados a nombres del U6 (244, H1/H2, Caldero, StinkBox, cortes P/A/C, Engine). Los más despegables, si se quisiera reutilizar la idea en otro lado, serían el runtime del CEB, el núcleo proposicional de Copi, el catálogo de piedras del control de flujo, y los motivos del filtro de pistas (identidad/futuro/calendario/forma). Eso no se hizo en este repo.

---

## Tabla corta

| Guardián | Archivo(s) | Capa | ¿Bloquea o marca? | ¿Conectado al motor/fábrica? |
|---|---|---|---|---|
| Sombrero blanco (filtro in/out) | `sidecar_sombrero_blanco_filtro_v1.py` | entrada / salida | Marca; restringe textos del hub | Sí, laterales vía UNICO |
| Sombrero blanco (token → StinkBox) | `plugin_sombrero_blanco_token.py` | entrada / salida | Marca + escribe StinkBox | Sí, UNICO post-apuesta |
| Sombrero absorbido | `_protocol_quality` en UNICO | entrada | Marca (`PASS` siempre) | Sí, absorbido |
| Autoevidencia de entrada | `guardian_entrada_autoevidencia_v1.py` | entrada | Solo marca | Sí, laterales pre |
| Filtro datos dirigidos 017 | `capa_llm/filtro_entrada_dirigida_017.py` | entrada (salida: ver §6) | Marca en default `traza`; filtra si `FILTRO_017=activo` | Sí, `run()` + `correr_estandar` |
| Compuerta Z_trabajo | `calibracion/gate_z90.py` | entrada | Bloquea lote/caso | Sí, fábrica/arnés si `gate_z` |
| Orquestador de guardianes | `guardianes_control_v1.py` | lógica (post-predictor) | Marca; puede retener cierre (`LATENTE`) | Sí, UNICO |
| Décimo hombre / latencia | `control_latencia_decimo_hombre.py` | lógica / flujo | Marca proceso; alimenta cierre latente | Sí, vía orquestador |
| Pregunta detrás v2 | `plugin_pregunta_detras_v2.py` | lógica | Marca | Sí, orquestador |
| Dirigida, post hoc y falacias | `plugin_pregunta_dirigida_v0_5_1.py` | lógica | Marca | Sí, orquestador |
| Copi | `guardian_logica_copi_v1.py` | lógica | Marca; `NO_RESUELTO` puede retener cierre | Sí, orquestador |
| Polaridad causal | `plugin_polaridad_causal.py` | lógica | Marca; lítote puede retener cierre | Sí, orquestador |
| Hombre de acero | `guardian_acero_rival_v1.py` + ablación | lógica | Marca; lo usa modo estricto (C2) | Sí, orquestador + modo estricto |
| Sherlock / rigor | `plugin_metodo_rigor.py` | lógica | Marca | Sí, orquestador (+ sensor pre) |
| Beristáin (tropos) | `guardian_tropos_beristain_v1.py` | retórica | Marca; `NO_RESUELTO` puede retener cierre | Sí, orquestador |
| Modo estricto | `modo_estricto_v1.py` | lógica / cierre | Retiene cierre estricto; no toca H | Sí, UNICO (flag on) |
| Décimo hombre esteroides | `decimo_hombre_esteroides_mayeutica_v1.py` | lógica / investigación | Auditoría, no toca H | Sí, UNICO post-cierre |
| Consistencia adversarial | `plugin_verificador_consistencia_adversarial.py` | lógica / contrato | Marca violaciones | Sí, UNICO |
| Pistas LLM Caldero | `guardian_pistas_llm_caldero_v1.py` | investigación | Filtra pistas (no veta la corrida) | Sí, fábrica + audit Caldero |
| Identidad zoom | `filtro_identidad_zoom_out_zoom_in.py` | investigación | Reporta; no devuelve descartes al Caldero | Llamado, efecto nulo sobre Caldero |
| Relleno 013/015 | `filtro_relleno_013.py` | investigación | Filtra votos de vecinos | Sí, UNICO |
| Tokens arquetipos v2 | `filtro_tokens_arquetipos_v2.py` | investigación / StinkBox | Filtra admisión en sync | Sí, sync; no en `run()` |
| CEB runtime | `ceb_runtime_v0_6_flow.py` | ejecución | Marca veredicto de flujo | Sí, UNICO |
| Alertas + compuertas CEB | `laterales_unico_v1.py` + `fabrica.py` | ejecución | Lote: bloquea con código 9 | Sí, fábrica |
| Compuerta de cierre | `_compuerta_cierre` en UNICO | ejecución / cierre | Retiene DETERMINADO | Sí, predictor |
| Guardia no cruce | `plugin_guardia_no_cruce.py` (absorbida) | ejecución | Excepción si hay contaminación | Absorbida en UNICO |
| Control flujo (agua/piedra) | `control_flujo_soluciones.py` | ejecución | Biblioteca; no siempre-on | Parcial (no en el tubo de `run()`) |
| Candado plugins | `candado_plugins.py` | ejecución / pack | Bloquea si no compila; hash no | Sí vía `correr_estandar`; no en `run()` solo |
| Candado Engine/244 | `CANDADO_ENGINE.json` + `fabrica.candados` | ejecución / pack | Fábrica bloquea (código 3) | Sí, fábrica |
