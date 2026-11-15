# Revisión ChatGPT — reproducción independiente Mozart Z90 (2026-11-13)

Fecha de revisión: 2026-11-15  
Repositorio: `marcojpad-hash/motor-u6-storage`  
Rama revisada: `alterno/reconexion-2a1`  
PR de corrección: [#14](https://github.com/marcojpad-hash/motor-u6-storage/pull/14)  
Merge: `f478d032f1cf303e8115be10dccc47369d7a97db`  
Último commit de endurecimiento del verificador: `a182c73d35c378a6b0feb8542bc9e7c23a351f66`

## Dictamen ejecutivo

**Las cinco correcciones están corroboradas en el código fusionado y la re-corrida final 22/22 está documentada. No certifico una reproducción independiente completa ejecutada por mí.** Sí leí íntegramente el RESULT original y comprobé en el código publicado las correcciones. La ejecución del motor y del verificador que se describe abajo procede de la bitácora/recibo publicados, no de una ejecución propia en este entorno.

La diferencia importa: el resultado corregido completo no está versionado en esta rama; lo que está publicado es el código, el input, el verificador, la nota y un recibo de ejecución. Por tanto, no es correcto afirmar que aquí volví a ejecutar el motor ni que inspeccioné el JSON completo de la re-corrida.

## Integridad y existencia del archivo de revisión

Antes de escribir, consulté en la rama `alterno/reconexion-2a1` las dos rutas solicitadas:
- `motor/REVISION_CHATGPT_MOZART_20261113.md`: no existe (GitHub 404).
- `REVISION_CHATGPT_MOZART_20261113.md`: no existe (GitHub 404).

No había archivo previo que preservar o sobrescribir.

## Evidencia primaria inspeccionada por mí

1. Leí el blob completo de `motor/RESULT_MOZART_CON_TEXTO_Z90_20261113.json` (blob SHA `e5e27ecf6df0791eaa40c990329bc207ace39318`; contenido recuperado: 8,265,542 caracteres). No me limité al resumen de la nota.
2. Leí `motor/correr_estandar.py`, `motor/motor/ceb_runtime_v0_6_flow.py`, `motor/motor/laterales_unico_v1.py`, `motor/motor/geometria_multicapa/adaptador_convergencia_real_v1.py`, el input congelado, el verificador y la nota de corrección.
3. Leí `motor/RESULT_MOZART_CON_TEXTO_Z90_20261114_RECIBO_EJECUCION.json`.
4. Verifiqué el commit de merge `f478d03`, el commit de endurecimiento `a182c73` y el inventario de archivos del PR #14.

## Los cinco hallazgos frente al RESULT original y al código fusionado

### 1. Reproducción interna fallida por el token `creatividad`

**Lo que muestra el RESULT original:** `efectividad_corte_retenido.estado = INTERNAL_T1_RUN_FAILED`; `previo_status = COMPLETED_ISOLATED_SUBPROCESS`; `visto_status = ERROR`; el traceback termina en `KeyError: 'FAIL_UNKNOWN_TOKEN:creatividad'`. El corte retenido C10 incluye `creatividad` con intensidad 0.84 en sus activaciones externas.

**Corrección inspeccionada:** en `motor/correr_estandar.py`, el caso para el corte retenido se construye ahora como copia completa del caso (`visto_case = _plain_json_copy(case)`) y luego se sustituye `cuts` por el corte retenido. Esto conserva la configuración/taxonomía del caso, en vez de reconstruir un objeto reducido que perdía `external_lights`. La llamada del retenido usa timeout de 90 segundos. La nota atribuye el KeyError al runner que descartaba esa taxonomía, no al token ni al motor de interrelación.

**Estado:** corrección estructural corroborada por inspección del código fusionado. El estado exitoso de la re-corrida está reportado en la nota, no ejecutado por mí.

### 2. `previo_error` sin clasificación real

**Lo que muestra el RESULT original:** el proceso previo figura como completado, pero `previo_error` vale `DATO_AUSENTE_REQUIERE_CLASIFICACION`; `auditoria_salida_json` detecta un faltante en `$.efectividad_corte_retenido.previo_error`.

**Corrección inspeccionada:** `correr_estandar.py` asigna `SIN_ERROR_CORRIDA_PREVIA_COMPLETADA` o `SIN_ERROR_CORRIDA_RETENIDA_COMPLETADA` cuando el subproceso correspondiente termina con `COMPLETED_ISOLATED_SUBPROCESS`; si falla, conserva el `stderr_tail`. También se completa el contrato del camino de éxito de `efectividad_corte_retenido`, que antes no emitía esos campos.

**Endurecimiento del verificador:** el verificador exige que `previo_error` y `visto_error` sean cadenas no vacías, no el placeholder; y rechaza clasificar como `SIN_ERROR` una corrida que no terminó. Esto evita aprobar cadenas vacías o errores tipados incorrectamente.

**Estado:** corrección estructural corroborada por código. La nota registra pruebas con mutantes sintéticos para las tres condiciones; no las ejecuté aquí.

### 3. CEB incompleto

**Lo que muestra el RESULT original:** hay 77 etapas registradas, pero el estado agregado es `INCOMPLETE`. La distribución es 62 `EXECUTED_AND_CONNECTED`, 13 `OUTPUT_NO_OBSERVED_CONSUMER`, 1 `OUTPUT_PERSISTED_WITHOUT_CONSUMER` y 1 `UNKNOWN`. También aparece una anomalía `RUNTIME_WARNING` en `UNSCOPED_RUNTIME` por `All-NaN slice encountered`, y una etapa de geometría reportada como ejecutada pero no observada.

**Correcciones inspeccionadas:**
- `ceb_runtime_v0_6_flow.py` clasifica `UNSCOPED_RUNTIME` como `DIAGNOSTIC_BUCKET`, fuera de las etapas malas.
- El adaptador de geometría trata explícitamente el caso de todos los valores NaN, evitando el aviso de `nanmedian` sin fabricar una mediana.
- El motor envuelve la llamada de geometría en una etapa CEB observada.
- Se registran como terminales los sumideros legítimos y se declaran las aristas `FLOW_CONSUMED` para consumos directos que el ledger no observa automáticamente.

**Endurecimiento del verificador:** la comprobación 3e exige exactamente 77 etapas y que las 77 estén individualmente en `EXECUTED_AND_CONNECTED`. `VERIFIED_FLOW` es el estado agregado del CEB, no el valor individual de cada etapa; el código del runtime confirma esa distinción.

**Estado:** el contraste del original y las correcciones del código están corroborados. La nota documenta 77/77 conectadas y cero anomalías en la re-corrida final; no he inspeccionado un RESULT corregido completo ni ejecutado el runtime para reproducirlo.

### 4. Fixture del Caldero clasificado como fallo

**Lo que muestra el RESULT original:** `sidecar_caldero_busqueda_arquetipos.py` aparece como `SIMULADO_FIXTURE`, con `incumplimiento = true`, severidad `FALLO_EJECUCION` y alerta “FALLO DE EJECUCIÓN / A INVESTIGAR: SIMULADO_FIXTURE”. El recibo original identifica `provider = static_fixture`, `required = false` y diez resultados congelados.

**Corrección inspeccionada:** `laterales_unico_v1.py` incorpora el argumento `fixture_autorizado`; cuando el input autoriza el fixture y el recibo confirma el proveedor fixture, la clasificación pasa a `INFO_FIXTURE_AUTORIZADO`. La ruta no autorizada conserva `FALLO_EJECUCION`. Esto corrige la clasificación, no convierte el fixture en búsqueda en vivo.

**Estado:** corrección estructural corroborada por código. La nota reporta `INFO_FIXTURE_AUTORIZADO` en la re-corrida y `llm_neighbor_hints_n = 0`; no afirmo que se haya ejecutado búsqueda externa en vivo.

### 5. Falta el campo contractual de semántica de estados

**Lo que muestra el RESULT original:** no contiene la clave `semantica_estados`. El RESULT sí contiene `estado_final`, `predictor` y `compuerta_cierre` como capas distintas.

**Corrección inspeccionada:** `correr_estandar.py` agrega `semantica_estados` al contrato de salida, con el contrato `SEMANTICA_ESTADOS_TERMINALES_V1`, los valores de `estado_final`, `predictor_status` y `compuerta_cierre_decision`, más la regla de consistencia que explica por qué no son estados contradictorios.

**Estado:** corrección estructural corroborada por código. La nota reporta el campo presente en la re-corrida; no he inspeccionado un RESULT corregido completo.

## Re-corrida y verificador: qué está demostrado y por quién

### Evidencia publicada de ejecución (no es ejecución mía)

El recibo versionado `motor/RESULT_MOZART_CON_TEXTO_Z90_20261114_RECIBO_EJECUCION.json` registra:
- `status = COMPLETED`, duración 88.737 s.
- Comprobación de hash del motor canónico y de patterns: `MATCH`.
- Monte Carlo activo: 30 observaciones, 16,938 simulaciones, 30 convergidas y 0 no convergidas.
- Resolución terminal con H1 `utopia_autonomia_atenas` y H2 `utopia_mentalidad_liberal`.
- Resultado escrito con SHA-256 `88bb0dcc96237eb16d114bc472ff92fc9d7a74a10f68069645709e8128235fd1`.

La nota de corrección documenta la secuencia de re-corridas, las correcciones del verificador y la reproducción final REPRO4: return code 0, recibo COMPLETED, sin rutas faltantes y verificador endurecido **22/22, exit 0**. También registra que el verificador sigue fallando contra el RESULT original en los puntos donde debe fallar. El último endurecimiento está en `a182c73`; ese commit actualiza el verificador y la nota. El merge `f478d03` incorpora el conjunto de 11 archivos del PR.

### Límite de la evidencia disponible en la rama

No está versionado el RESULT corregido completo. La nota documenta que el JSON de unos 8.4 MB no pudo subirse por HTTP 413 y que el comprimido fue rechazado por no ser UTF-8. El recibo sí está versionado, pero es metadato de ejecución y no sustituye al resultado. Tampoco encontré en la rama:
- `motor/RESULT_MOZART_CON_TEXTO_Z90_20261113_AUDITADO.json`;
- `motor/RESULT_MOZART_POST_FIX5_REPRO4.json` (ni el RESULT corregido equivalente).

El hash del recibo (`88bb…`) no coincide con los hashes de las reproducciones desde clones/rutas distintas; la nota explica que el JSON incluye rutas absolutas del checkout. Por eso la reproducibilidad byte a byte depende de la ruta, mientras que las invariantes y resultados comparados se reportan iguales. No presento esos hashes como equivalentes.

## Clasificación final de la revisión

| Elemento | Resultado de esta revisión |
|---|---|
| RESULT original completo | Leído y analizado por mí |
| Cinco fallos originales | Confirmados en el RESULT original |
| Cinco correcciones en código fusionado | Inspeccionadas y corroboradas |
| Verificador endurecido de 22 checks | Código inspeccionado; 22/22 consta en la bitácora de ejecución |
| Re-corrida final | Documentada por nota/recibo; no ejecutada por mí |
| Comparación íntegra RESULT corregido vs original | No verificable desde la rama: falta el RESULT corregido completo |
| Reproducción independiente propia | No completada; no afirmo haberla ejecutado |

**Conclusión:** el PR #14 contiene correcciones coherentes con los cinco hallazgos y la documentación registra una re-corrida final satisfactoria de 22/22. La evidencia de código y del RESULT original sí fue comprobada directamente en esta revisión. Queda pendiente únicamente la certificación independiente de la salida corregida completa mediante una ejecución propia o acceso al artefacto íntegro de esa re-corrida. No se debe describir este documento como una reproducción independiente completa ya ejecutada.
