# Delegaciones Motor U6

Tablero vivo del callback del motor. Quien delega escribe aquí. Quien recibe lee aquí.

Este tablero es del Motor U6 (repo `motor-u6-storage`, rama de trabajo `alterno/cameo-pesos`). El motor es un proyecto aparte y no lleva delegaciones en el tablero de CAPCOT (`capcot-capsulas-imaginantes/ajustes_entre_modelos/DELEGACIONES.md`), que lo dice así expresamente. Las órdenes por el bus viven como issues "[BUS] indicacion - <modelo>" en `agente-cero-costo`; este tablero es el espejo legible en el repo del motor.

Reglas: protocolo de ejecución y lectura en `PROTOCOLO_EJECUCION_Y_LECTURA_LLM.md`; arranque en `INICIO_SESION_CHATGPT.md`; custodia independiente; gate Z90 vigente; no tocar Engine V5 ni patterns 244; no calibrar con n=1; PRs sin fusionar sin Marco.

## Pendientes

### 1. Orden permanente — corridas diarias del Motor U6 por ChatGPT
- DE: Pecas (por orden de Marco, dueño, 2026-11-16)
- PARA: ChatGPT (cuenta marco.jp@live.com.mx)
- QUÉ: ejecutar ejercicios/corridas del Motor U6, meta ~30 corridas/día de casos NUEVOS e independientes asignados por el protocolo (lotes nuevos F007+), con reporte por corrida en el repo; preparar la verificación de la cohorte C01–C20 sin abrir la custodia (la abre Pecas); además búsqueda/investigación/programación cuando se pida por la misma vía. Sin cambiar pesos, sin tocar Engine V5 ni el catálogo de 244, sin declarar calibración, con custodia independiente y gate Z90 vigente. Retoma las órdenes abiertas de la reasignación Grok→ChatGPT del 2026-11-12: #36, #37, #38, #47, #48, #49, #50, #63, #64.
- ORDEN: issue "[BUS] indicacion - ChatGPT" en `agente-cero-costo`, #465 — https://github.com/marcojpad-hash/agente-cero-costo/issues/465
- PARA CUÁNDO: permanente, desde 2026-11-16; acuse diario al cierre del día
- ESTADO: PENDIENTE
- NOTA: C01–C20 ya están corridos (lote_20, 2026-11-08); no re-correrlos para inflar n. Fecha blanda: créditos ChatGPT caducan ~2026-11-24 (sin verificar). Límite honesto: el cuello de botella es la preparación de casos nuevos con fuentes y custodia, no la ejecución (~14–23 s por corrida).

## En progreso

(nada)

## Hechas

(nada)


## Seguimiento ChatGPT — 2026-11-20

La orden permanente del issue agente-cero-costo #465 sigue **PENDIENTE** en su objetivo principal de corridas nuevas e independientes. No se declara corrida nueva ni se incrementa n.

- Se preparó la tabla de predicciones congeladas C01–C20 en `casos/ciegos/lote_20/PREPARACION_UNBLINDING_CHATGPT.md` (commit `2668a0b9fd8419cbc6c8c3b9a0199dae61afd6a3`; lectura de vuelta blob `4366c717fd340112eadd52a343152fa3ae0dbc55`). Contiene 20/20 slots, H1/H2, escenario y destino personal predicho desde `SALIDA_CONGELADA.json`. **No se leyó `custodia/`, no se consultaron desenlaces y no se calculó HIT/MISS.** El unblinding sigue reservado a Pecas/custodio independiente.
- Revisión de F007: `semillas_lote_F007.py` contiene ocho sujetos con dos cortes por sujeto y referencias secundarias de Wikipedia; `destinos_lote_F007.py` lo identifica como ensayo metodológico del mismo actor. No acredita independencia de custodia ni un lote F007 preparado; la cola de fábrica visible contiene solo F001–F005. No se ejecutó ni se contó como casos independientes.
- Siguiente operación válida: preparar sujetos nuevos con fuentes primarias y cortes Z verificables; enviar el material de destino a custodio independiente; solo después ejecutar runner real y guardar RESULT/RECIBO/CEB/manifiesto. No reejecutar C01–C20.


## Seguimiento de órdenes reasignadas — 20-nov-2026, run operador

La orden permanente #465 continúa **PENDIENTE** en su objetivo principal: no se declaró ninguna corrida F007+ ni se incrementó n.

### Issue #64 — guardián Z90 en correr_estandar

- **Implementación propuesta en PR:** [PR #8](https://github.com/marcojpad-hash/motor-u6-storage/pull/8), rama `fix/issue-64-guardian-z90-correr-estandar`, head `5eda368d85851a42f6f82f069c56c93983c60da2`, destino `alterno/cameo-pesos`.
- **Evidencia:** check `runner-contract` SUCCESS, run [#43399816075](https://github.com/marcojpad-hash/motor-u6-storage/actions/runs/43399816075); ocho pruebas específicas declaradas en `motor/tests/test_guardian_z90_correr_estandar.py`.
- **Estado real al 2026-11-21:** PR abierto, sin merge; GitHub marca `mergeable=false` (`mergeable_state=dirty`), head `5eda368d85851a42f6f82f069c56c93983c60da2`, base `be98ec8645364b1330104de996fbd6339033547c` anterior al HEAD activo. El PR contiene `_guardian_z90` en `correr_estandar.py`; esta rama activa aún no lo invoca. La gate base ya calcula Z90 y valida ventanas/fechas. Clasificación: **GATE_Z90_IMPLEMENTADA_Y_PROBADA; RUNNER_CABLEADO_EN_PR_ABIERTO_CONFLICTIVO; NO_EJECUTABLE_ESTÁNDAR**.

### Issue #49 — cortes variables y Z90

- El protocolo normativo ya existe en `motor/PROTOCOLO_BIOGRAFICO_Z90.md`.
- Se corrigieron en esta rama `casos/fabrica/README.md`, `casos/fabrica/PROMPT_SEMILLAS_Z.md`, `motor/CONTRATO_ENTRADA_LLM.txt`, `INSTRUCCIONES_CONTINUIDAD_CHATGPT.md` y el docstring de `motor/calibracion/gate_z90.py`.
- Se eliminó la regla documental de tres cortes fijos; se explicitó Z90, ventanas acumulativas desde nacimiento, primer corte en nacimiento, último en Z90, número variable y separación preparador/custodio.
- **Brecha pendiente actual:** la gate implementa cálculo y validación temporal/evidencial; falta integrar y validar el guardián en el runner estándar (PR #8) y resolver la separación de funciones/custodia. No se ejecutó el motor.

Commits documentales: `c9df16250741348a1ce4bdee0814164b97d98ead`, `c27ae38f2a4b003d3ff95b0a306c579de6778cba`, `45e4abd88882a96c36439990f8ef3b80ee93681a`, `5f52acbda3553be89b01d12ee99ad86116cffb30`, `4d2ea0a06437262b9e127f6bbbe4acb1892d9484`.

### Otras órdenes #36, #37, #38, #47, #48, #50 y #63

Siguen abiertas en el bus adicional `agente-cero-costo`. Se consultaron en solo lectura. No se modificó ese repositorio ni se atribuyó avance no verificado. Sus trabajos de supervisor, Cancerbero, consulta dirigida/vecinos, sidecar histórico, inputs humanos y consulta LLM obligatoria siguen fuera de la evidencia de cierre de este run.



## Seguimiento ChatGPT — 2026-11-20, run operador 8

La orden permanente #465 sigue **PENDIENTE** en su objetivo de casos nuevos e independientes. No se ejecutó el motor, no se preparó entrada F007 y no se incrementó n. El issue #465 se mantuvo en solo lectura; el acuse diario está fijado para el cierre del día.

### Ejecuciones y registro de Actions

- Run [#44739754266](https://github.com/marcojpad-hash/motor-u6-storage/actions/runs/44739754266): el job `auditar` (job id `136300124552`) y todos sus pasos terminaron `completed/success`. Es una auditoría de Actions, **no una corrida del motor**.
- `avances/auditoria_corridas/ULTIMO_ESTADO.json` en main (blob `922087c6eab71716312434bae65b8e940b18781b`) conserva 87 registros y su más reciente es #44666733628 (2026-11-20 03:17:39Z); no incluye #44739754266. El snapshot está atrasado respecto del run observado. No se interpreta como ausencia de ejecución ni se modificó main.
- PR #8 sigue `OPEN / NOT MERGED`, `mergeable=false`, `mergeable_state=dirty`; el check `runner-contract` SUCCESS corresponde al head del 13-nov y no valida el HEAD activo ni la nueva gate por sí solo. El runner estándar de esta rama no tiene el guardián.

### Revalidación F007 y separación de funciones

- Semillas F007 (blob `850297da7a15af430ee4a7065e8579bd021b0174`): 8 sujetos, 8 cortes C1 y 8 cortes C2 (dos por sujeto); aparecen 8 referencias a Wikipedia. No constituye cohorte primaria e independiente.
- `casos/fabrica/fabrica.py` (blob `f956f4b3daa4498f790d7efe2d6623646f3589aa`), `preparar_z`: importa `SEMILLAS_Z` y `DESTINOS` en el mismo proceso; después escribe `entrada.json`, `desenlace_sellado.json` y, si el destino lo contiene, `destino_sellado.json`. No es ruta entry-only. `correr` abre los desenlaces después del compromiso. No invocar ninguno de esos comandos para F007.
- `motor/calibracion/gate_z90.py` (blob `9638f4c705c12593d38de749c68f0813cbeb405e`, revisión `Z90_BIRTH_DEATH_WINDOWS_V1_20261121`): calcula Z90 desde nacimiento/muerte; valida `z_trabajo=z90_date=Z90`, `window_start` desde nacimiento, cierres crecientes, último cierre = Z90 y evidencia no posterior a cada corte. No prueba custodia humana ni integración del runner.
- Sin ruta entry-only, runner válido, fuentes primarias y custodia independiente no se prepara ni ejecuta una cohorte. C01–C20 y sus custodias permanecen intactos.

### Riesgo de autoridad en workflows de main (solo lectura)

Los tres workflows de main inspeccionados conservan `permissions: contents: write` y operaciones que hacen push a main, pese a que el contrato de esta rama declara main `SOLO_CONSULTA`:

- `.github/workflows/fabrica-lote-diario.yml` (blob `bdcec6c6c95de6f7f49e70e78d2875c382772fe0`): `workflow_dispatch`, ejecuta `preparar-z` + `correr` y puede hacer push a main.
- `.github/workflows/fabrica-real-traza.yml` (blob `f142b7b59baf306bc8d8bda0c2a6e00fae0a0566`): `push`/dispatch sobre main; ejecuta `--rehacer CAL_F005_01_COURBET` y puede subir manifiestos a main. Ese input repetido no es un caso F007+ independiente.
- `.github/workflows/auditar-corridas-actions.yml` (blob `8e85e31ba938dd62e63787433bece6c1ea8b5c36`): cron/workflow_run, `contents: write`, commit y push de snapshots a main; run #44739754266 observado.

No se disparó ni modificó ningún workflow; no se tocaron permisos, secretos, ramas, main, motores, patrones, candados ni evidencia congelada. La incompatibilidad de autoridad queda documentada para resolución autorizada.

## Seguimiento operador único — 2026-11-21, run 11

### Gate biográfico Z90

- **EJECUTADO:** commit `fa1a73bed69d22ed4667c6ad3322f2f16542df70` en `alterno/cameo-pesos`. Actualiza `motor/calibracion/gate_z90.py`, contrato/prompt y agrega `motor/tests/test_gate_z90_biografico.py`.
- **CAMBIO:** cálculo determinista Z90 desde fechas exactas de nacimiento/muerte con truncamiento `(días * 9) // 10`; igualdad obligatoria de `z_trabajo` y `z90_date`; `window_start` igual al nacimiento en cada corte; cierres exactos, crecientes y último cierre = Z90; `claim_date` y fecha de fuente primaria no posteriores al cierre individual.
- **PRUEBA LOCAL:** 14 pruebas aisladas pasaron sobre una copia de trabajo. **CI VERIFICADO:** run [#44965447828](https://github.com/marcojpad-hash/motor-u6-storage/actions/runs/44965447828), job `runner-contract`, 53 pruebas pasaron en 0.42 s.
- **MANIFIESTOS:** el generador `motor/scripts/regenerar_manifestos_trabajo.py` ejecutó correctamente en CI y produjo 367 entradas de unificación, 368 compactas y 369 líneas SHA. Hashes impresos: gate `af15e325d0477237e3a4fb3fad892b3561b69d603f41ffdab765aaa6e602d782`; contrato `12704aa096b0066362fd440aff461044289428881df4a88ddcd909e5275bad1c`; test `6d84a5a4eb2fd89b5c99f1b12e78d3220c7e30a588b5a1c14b09683e995411c4`. Se añadió un artefacto CI de 1 día para recuperar los manifiestos completos y actualizar el repositorio; todavía no se declara la regeneración remota verificada.
- **LÍMITE:** la gate comprueba campos y fechas; no demuestra independencia humana del custodio ni acumulación semántica de vectores. La integración en `correr_estandar` continúa en PR #8, OPEN/NOT MERGED.
- **F007 revalidado:** 8 sujetos, 2 cortes por sujeto, fuentes secundarias Wikipedia, sin fecha de nacimiento/muerte ni ventana explícita desde nacimiento. No es cohorte independiente y debe fallar la nueva compuerta. No se ejecutó ni se contó ninguna corrida.

### Auditoría de autoridad de rama — workflow de Actions en main

- **EVIDENCIA:** run `44961081920`, job `137019808201`, 2026-11-21 17:17 CDMX aprox. Ejecutó `python scripts/auditar_corridas_actions.py` y publicó el commit `bac12846b184f2a7b4e0e2f3f6c7e45a` en `motor-u6-storage/main`.
- El workflow de main declara `permissions: contents: write`, hace checkout de `main` y ejecuta `git push origin HEAD:main`. Contradice la autoridad `main = SOLO_CONSULTA`.
- El snapshot de esa ejecución informa 67 corridas y 1 fallo, pero `avances/auditoria_corridas/ULTIMO_ESTADO.md` conserva como última corrida la `44930761392`: el job consulta solo runs `completed`, por lo que se excluye a sí mismo mientras está `in_progress`. El registro queda desfasado inmediatamente después de cada autoauditoría.
- **NO TOCADO:** no se revirtió el commit, no se cambió el workflow de main, no se cambiaron permisos y no se ejecutó el motor. La corrección de ese workflow requiere autorización expresa para modificar main o deshabilitarlo.


## Verificación posterior a la reconciliación documental — 2026-11-21

- Se corrigieron las afirmaciones obsoletas sobre Z90 en `INSTRUCCIONES_CONTINUIDAD_CHATGPT.md` y `motor/CONTRATO_ENTRADA_LLM.txt`: la gate de fábrica ya implementa el cálculo y la validación temporal; el cableado en `motor/correr_estandar.py` sigue pendiente en PR #8 (OPEN/NOT MERGED).
- Registro de cambios: `avances/2026-11-21_ChatGPT_aclaracion_gate_z90.md`, commit `cd84673d06cc9b810aa7c95e1673462ed3af64c2`.
- CI posterior a las dos correcciones documentales: run [#44967844378](https://github.com/marcojpad-hash/motor-u6-storage/actions/runs/44967844378), commit probado `16db5d6701dd1484b6003557a4c248d1ffc58916`, **53 passed in 0.33s**, 0 skipped, 0 failed. Manifiestos regenerados en modo read-only: 367 archivos de unificación, 368 compactos y 369 líneas SHA256. Artifact `motor-u6-manifests-44967844378`, digest `sha256:d17fdf379501f4c637bb20aeb147ce1512cf15cb26d5be4d1125fbc210351241`, vence `2026-11-23T00:41:37Z`.
- Esta prueba acredita contratos y manifiestos, no una corrida del motor ni independencia de F007. No se ejecutó el motor, no se abrió custodia, no se incrementó n y no se modificó `main`.

 
## Actualización de ejecución — 2026-11-22 — Issue #64 / Z90

- **EJECUTADO en la rama autorizada alterno/cameo-pesos:** motor/correr_estandar.py ahora llama a _guardian_z90(case) después de normalizar/filtros y antes de construir/ejecutar el motor. Si la gate rechaza, el runner escribe RESULT y _RECIBO_EJECUCION.json con BLOQUEADO_GUARDIAN_Z90 y sale con código 8. El veredicto se incorpora también al resultado y al recibo de corridas admitidas.
- **EJECUTADO:** se normalizó la salida de efectividad_corte_retenido para que previo_error y visto_error existan en éxito y fallo, sin None.
- **PRUEBAS:** se añadió motor/tests/test_guardian_z90_correr_estandar.py con siete pruebas. El fixture histórico ahora contiene fecha de nacimiento, fecha de muerte, Z90 calculada, ventanas acumulativas desde nacimiento y último corte exactamente en Z90; el fixture anterior del PR no contenía nacimiento/muerte y no era válido para probar PASS.
- **CI cableado:** .github/workflows/test-motor-contracts.yml incluye el test nuevo y se ejecuta en pushes a alterno/cameo-pesos. Run [#45002771468](https://github.com/marcojpad-hash/motor-u6-storage/actions/runs/45002771468): **60 passed in 0.86s**, job runner-contract SUCCESS. El run previo #45002766038 probó la integración sin el test nuevo (53 passed); el run #45002771468 es la evidencia que sí incluye las siete pruebas nuevas.
- Commits: runner bb6a31d9a77d43ac106f77927f9347b8bbadee7d; pruebas 1d878000c791eb108b4175c8471c5b3b3114caf6; workflow 658f3f27a61f70e16d95de916d23e3af93b5aae2. Lecturas de vuelta confirmadas.
- **Estado de alcance:** PR #8 sigue OPEN / NOT MERGED / mergeable=false; no se fusionó ni se modificó su rama. El runner activo ya tiene el cableado y CI verde, pero esto no crea cohorte independiente, no acredita custodia y no autoriza F007. No se ejecutó el motor con casos reales, no se incrementó n y no se tocaron Engine V5, patterns 244, candados, main ni custodias.


## Auditoría de workflows con escritura a main — 2026-11-22

Lectura de los ocho workflows presentes en alterno/cameo-pesos. **No se disparó ningún workflow y no se modificó main.** Riesgos confirmados en el contenido:

- .github/workflows/auditar-corridas-actions.yml: schedule cada hora y workflow_run; permissions contents:write; checkout explícito de main; hace git push origin HEAD:main cuando cambia el snapshot.
- .github/workflows/fabrica-lote-diario.yml: workflow_dispatch; contents:write; por defecto ejecuta preparar-z (carga semillas y destinos juntos) y luego correr; hace push directo a main. Está expresamente fuera de uso bajo el contrato vigente.
- .github/workflows/fabrica-real-traza.yml: workflow_dispatch y push en main; contents:write; regenera manifiestos y los empuja a main; además ejecuta un caso F006 sellado y puede modificar resultados.
- .github/workflows/update-mortality-wpp.yml: workflow_dispatch y push en main; contents:write; puede descargar y escribir datos WPP en main.
- .github/workflows/chatgpt-startup-contract.yml y traza-campo-244.yml también se activan por push a main, pero la lectura de sus triggers no muestra escritura automática a main en el fragmento revisado.
- .github/workflows/test-motor-contracts.yml ejecuta pruebas en main y alterno/cameo-pesos; es el CI de validación, no un workflow de producción.

**Decisión operativa:** mantenerlos sin ejecutar. La rama activa no debe usar fabrica-lote-diario, fabrica-real-traza, auditar-corridas-actions ni update-mortality-wpp como atajos. La corrección estructural requiere cambiar la política de escritura de esos workflows en main, pero main está en modo solo lectura y no se alterará desde esta operación. La integración Z90 y sus pruebas sí permanecen en la rama activa, con CI de contratos ya verificado en run #45002771468.

## Seguimiento operador único — 2026-11-23 — ruta entry-only e índice de casos previos

- **EJECUTADO:** se endureció casos/fabrica/preparar_entrada_solo.py para indexar case_id y sujetos visibles antes de escribir. Lee solo resultados.jsonl, entradas JSON previas, entradas staged y casos/ciegos/**/entrada.json excluyendo cualquier ruta custodia. F007 se indexa mediante AST literal; no se importa ni ejecuta semillas_lote_F007.py.
- **PROTECCIÓN:** los directorios C01–C20 reservan sus IDs sin abrir SALIDA_CONGELADA ni custodia. Un índice previo ilegible o malformado bloquea la escritura. La unicidad de sujetos contra identidades selladas C01–C20 sigue siendo responsabilidad del custodio, que debe comprobarla con su índice privado antes de sellar.
- **PRUEBAS VERIFICADAS:** el primer fixture AST falló por un salto de línea escapado; se corrigió sin tocar lógica de producción. CI run #45172870551, commit 9f99f15de4bef42544157865ff8881c0f41f225e: runner-contract SUCCESS, 78 passed in 1.09s. Run previo #45172749593 quedó como fallo de fixture y no se cuenta como verificación.
- **F007 revalidado:** ocho sujetos, dos cortes por sujeto, referencias secundarias Wikipedia y ausencia de fechas exactas de nacimiento/muerte/Z90; la gate actual lo rechaza. No se abrió destinos_lote_F007.py ni ninguna custodia.
- **ESTADO DE PREPARACIÓN:** no hay JSON de semillas nuevo en semillas_entrada ni entradas staged en entradas_solo; no se creó destino, desenlace, RESULT, RECIBO o CEB; n no aumentó. No se ejecutó el motor.
- **BLOQUEO PUNTUAL:** falta una cohorte con fuentes primarias y entrega/sello del custodio independiente. La ruta entry-only ya existe y CI la prueba; no sustituye la custodia. PR #8 continúa OPEN/NOT MERGED; main permanece SOLO_CONSULTA.
- **PRIVACIDAD:** no se añadieron sujetos, semillas, destinos ni datos operativos personales al repositorio. La discrepancia de visibilidad pública frente a la política documentada sigue sin resolver; no se cambiaron permisos ni secretos.

## Seguimiento operador único — 2026-11-24, 00:28 CDMX

- **Rama y CI:** HEAD observado de `alterno/cameo-pesos` = `315c9369a9ec941d450213b7f049a9f2174d1831`; su commit más reciente añade solo este registro documental y su padre verificado es `82a0b0dac5074d8f00955abdfa291c8752e050fb`. El último CI de contratos es run [#45173282278](https://github.com/marcojpad-hash/motor-u6-storage/actions/runs/45173282278), sobre el código `5fe3b6d6d4740597141dc8b508a513632e64ca05`: **78 passed**. No atribuir ese CI a una corrida del motor.

- **Preparación entry-only verificada:** `casos/fabrica/preparar_entrada_solo.py` (blob `891e37a482207399f9f929824e0935486b4b95b1`) acepta JSON, exige `case_id` y sujeto nuevos, `freeze=z_trabajo=z90_date`, versión exacta de `gate_z`, `z_work_kind=CASE_CUTOFF` y `z_work_date` igual al último corte. Escribe únicamente `entrada.json` y `entrada.sha256`; no crea destinos, desenlaces, RESULT ni RECIBO. `semillas_entrada/` contiene solo README y esquema; `entradas_solo/` no existe en el árbol actual: no hay entradas staged.

- **Gate Z90 verificada:** `motor/calibracion/gate_z90.py` (blob `5d4627514e7aa33500183fc395b6795bb4fb925d`) declara revisión `Z90_BIRTH_DEATH_WINDOWS_V2_20261123`; calcula Z90 desde nacimiento/muerte, exige igualdad exacta de `z_trabajo` y `z90_date`, primer inicio en nacimiento, cierres crecientes y último cierre exactamente en Z90. La gate no demuestra por sí sola independencia humana del custodio ni acumulación semántica de la evidencia. El runner estándar conserva `NO_CONFIGURADO` no bloqueante para casos genéricos sin disciplina declarada; la ruta entry-only fuerza `gate_z` y los campos temporales para los casos nuevos.

- **F007 revalidado sin abrir destinos ni custodia:** `semillas_lote_F007.py` (blob `850297da7a15af430ee4a7065e8579bd021b0174`) mantiene ocho sujetos y dos cortes por sujeto, referencias secundarias Wikipedia y ausencia de fechas de nacimiento/muerte/Z90 completas. No cumple la cohorte independiente. No se abrió `destinos_lote_F007.py`, ninguna carpeta `custodia/` ni desenlaces. No se reejecutó C01–C20.

- **Muestra y ejecución:** `CALIBRACION_ACUMULADA.md` registra 45 casos sellados/evaluados y 5 `NO_SELLADO`; F006/Courbet es reevaluación y no incrementa n. Semillas nuevas: 0; entradas staged: 0; corridas F007+: 0; incremento de n: 0; RESULT/RECIBO/CEB/manifiestos nuevos: 0. Consumo de créditos de este corte: 0; saldo restante: no observable en esta conexión.

- **Autoridad de rama:** la última auditoría automática visible en U6 `main` es run [#45300660200](https://github.com/marcojpad-hash/motor-u6-storage/actions/runs/45300660200), SUCCESS, que escribió el commit `8532017650362e0333259c375bad9361b7185701` en `main`. La escritura sigue contradiciendo `main=SOLO_CONSULTA`. No se revirtió ni se modificó el workflow, permisos, secretos o main.

- **Decisión de ejecución:** no hay cohorte con fuentes primarias, Z90 completo y sello de custodio independiente. La siguiente acción válida es recibir esa cohorte separada; entonces el preparador solo podrá escribir entradas mediante `preparar_entrada_solo.py`, y el runner requerirá RESULT/RECIBO/CEB/manifiesto y lectura de vuelta por caso. No declarar calibración ni aumentar n antes de esas evidencias.

### Corrección de CI entry-only — 2026-11-24

- **EJECUTADO:** se corrigió `.github/workflows/test-motor-contracts.yml`. La ruta `casos/fabrica/test_preparar_entrada_solo.py` había quedado fuera del comando pytest por una continuación YAML ambigua; ahora está incluida explícitamente en un bloque `run: |` con las demás suites.
- **Commit:** `03527aca1556761162a10680b78c3ac61e0f5635`; blob del workflow releído: `184472b46d66e4d442faa30dca26def35b3072bc`.
- **CI VERIFICADO:** run [#45341793466](https://github.com/marcojpad-hash/motor-u6-storage/actions/runs/45341793466), job `runner-contract` SUCCESS, **78 passed in 1.69s**. El log confirma que pytest recibió `casos/fabrica/test_preparar_entrada_solo.py`; la regeneración de manifiestos y su artifact también terminaron SUCCESS.
- La corrección valida el contrato de preparación y el runner; **no** ejecuta casos reales, no crea destinos ni demuestra custodia independiente. n permanece en 45 sellados/evaluados; 5 siguen `NO_SELLADO`; incremento de n = 0.


## 2026-11-24 22:00 CDMX — reconciliación operativa y correcciones

- Rama activa `alterno/cameo-pesos`: HEAD `2d32677b`. `main` permanece solo consulta en HEAD `5b0331f`; ese commit de main fue generado por el workflow automático de snapshot de Actions, no por esta ejecución. No se revirtió ni se escribió en main.
- **Corrección de estado técnico:** la gate Z90 está completa en la rama activa: calcula Z90 desde nacimiento/muerte, exige primer corte en nacimiento, ventanas acumulativas y último corte exactamente en Z90. `motor/correr_estandar.py` invoca el guardián. `preparar_entrada_solo.py` escribe únicamente `entrada.json` y `entrada.sha256`; no importa destinos. No ejecutar `fabrica.py preparar-z` ni `fabrica.py correr`.
- Último CI de la rama activa observado: 78 pruebas aprobadas en run 45341793466, sobre commit anterior al HEAD documental actual. No se lanzó CI manualmente en este corte.
- **F007 sigue inválido:** 8 sujetos, 2 cortes por sujeto, fuentes secundarias Wikipedia y sin campos/validación Z90 conforme al schema. No se crearon entradas ni se ejecutó el motor.
- El custodio no respondió después del comentario #465 `7146005810`. No existe cohorte sellada ni acuse independiente. No se accedió a custodia.
- **Corrección de n:** `CALIBRACION_ACUMULADA.md` reportaba 45 filas evaluadas, pero cinco filas F001_D022 reutilizan exactamente los cinco hashes de entrada de F001. Según la regla anti-duplicados, la muestra independiente es **n=40**. Recuento corregido: H1 8/40 (20.0%), H2 5/40 (12.5%), set 12/40 (30.0%), escenario 10/40 (25.0%), destino exacto 12/35 (34.3%) y polaridad 23/35 (65.7%). Se añadió reconciliación sin alterar filas históricas. F006/Courbet, filas de integración y reevaluaciones no aumentan n.
- `resultados.jsonl` tiene 62 filas y 53 case_id distintos; no se usa ese total como n experimental.
- PR #38 sigue abierto y sin merge. Su HEAD `3a6cbf6887a79fcb7c5b0c12891e1bed322a7975` tiene un CI exitoso de 82 pruebas (run 45461576292). Las pruebas comprueban el bloque de contexto y referencias estables, pero no comparan explícitamente H1/H2/top-1 antes y después; esa invariancia sigue sin prueba directa.
- `avances/2026-11-24_ChatGPT_tercera_capa_lectura_contextual.md` es una propuesta documental; no equivale a implementación. No confundirla con la rama separada de PR #38.
- Se creó `avances/2026-11-24_fuentes_primarias_candidatos_z90.md` con fuentes oficiales y cálculos provisionales para dos candidatos. La búsqueda del ledger público no encontró coincidencia exacta, pero la unicidad final depende del índice privado del custodio.
- No se modificaron motores canónicos, pesos, catálogo 244, FREEZE, salidas congeladas, secretos ni permisos. No se abrió ni cerró PR. No hubo corridas nuevas.
- **Siguiente compuerta mínima:** acuse del custodio confirmando unicidad y entregando el sellado independiente. Entonces preparar solo entradas entry-only y ejecutar con el runner real, leyendo de vuelta RESULT, RECIBO, CEB y manifiesto.


### Trazabilidad del registro 22:00
- HEAD observado al iniciar el corte: `2d32677b`.
- Commits de documentación creados en este corte: `aa8f605f` (reconciliación de muestra), `4ff0dbb7` (dossier de fuentes/Z90) y `a186358c` (este tablero).
- Estos commits actualizan solo documentación; no contienen nuevas entradas de caso ni cambios al motor.


### Corrección de candidatos — 2026-11-24, posterior al acuse
- El comentario de Marco `7146005810` es la autoridad vigente: los dos sustitutos son **Elizabeth II y Michelangelo Buonarroti**. La versión anterior del dossier que incluía Edward VII fue un error de lectura y queda supersedida por `avances/2026-11-24_fuentes_primarias_candidatos_z90.md`.
- Elizabeth II: duración recalculada con la gate: 35,204 días; 31,683 días al 90%; Z90 2013-01-17. Coincide con el cálculo del comentario del propietario.
- Michelangelo: 32,491 días; 29,241 días al 90%; Z90 1555-04-06. El cálculo coincide con el comentario del propietario.
- Michelangelo permanece **PENDIENTE_SOURCE_DATE**: la edición de 1875 declara que la copia de las `Ricordanze` es de época de Michelangelo, pero el custodio debe validar la fecha material/procedencia de esa copia para el primer corte. No preparar entrada hasta esa confirmación.
- Marie Curie queda excluida por duplicidad; Florence Nightingale queda excluida porque la copia/certificación de nacimiento disponible tiene fecha de registro posterior al nacimiento.
- No hay respuesta del custodio ni cohorte sellada. No se crean semillas ni se ejecuta el motor.


### Trazabilidad de corrección de candidatos
- Dossier actualizado para reflejar exactamente la pareja propuesta por el propietario en #465: Elizabeth II + Michelangelo. Se eliminaron los datos de Edward VII.
- El cálculo de Elizabeth II quedó corregido a 35,204 días / 31,683 días al 90% / Z90 2013-01-17. El cálculo de Michelangelo queda 32,491 / 29,241 / Z90 1555-04-06.
- La entrada de las `Ricordanze` permanece `PENDIENTE_SOURCE_DATE`; no se prepara hasta validación del custodio.
- Commit de corrección del dossier: se registra en el historial del archivo; este tablero no contiene nuevas semillas ni predicciones.


### Nota posterior — snapshot automático de main, 2026-11-24 22:14 CDMX
- U6 `main` avanzó de `5b0331f` a `c87bf6f549309601a981eac1e128b42f1f75510c` por el workflow `Auditoría de corridas Motor U6`, run [45545245246](https://github.com/marcojpad-hash/motor-u6-storage/actions/runs/45545245246), SUCCESS.
- El commit fue de `github-actions[bot]` y solo modificó `avances/auditoria_corridas/ULTIMO_ESTADO.json` y `ULTIMO_ESTADO.md`; no alteró motores ni patrones. Es una escritura automática en `main`, en tensión con `SOLO_CONSULTA`; esta ejecución no la produjo ni la revirtió.
- El snapshot no incluye el run que lo generó: el documento sigue mostrando como última auditoría la 45488723151 de las 15:12 CDMX. No tratar el snapshot como evidencia de una corrida predictiva ni como inventario completo de Actions.
- HEAD de trabajo después de los registros documentales: `f57830ed9b246a3e9f9682da80788364f0f46756`.


### 2026-11-27 — LECTURA_FUNCIONAL_AGNOSTICA_V1

- Contrato y skill agnósticos añadidos en docs; plantilla de contrato, esquema JSON, CLI post-corrida y suite sintética en motor.
- La etapa prepara un paquete mínimo por rutas declaradas y valida una revisión de otro modelo ligada a hashes. El sidecar puede ALLOWED o BLOCKED antes del handoff; no altera RESULT, RECIBO, H1/H2, ranking, pesos ni motores canónicos.
- CI: run 46106989385, success, 134 passed en 50.30 s.
- Límite explícito: la identidad del revisor es DECLARED_ONLY; no hay autenticación criptográfica ni llamada automática a otro modelo. No se declara integración automática en correr_estandar.py ni reparación de C-F8.
