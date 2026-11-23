# Fábrica de casos

Estado al 2026-10-31: F006_TRAZA_V2_R7 está archivado como reevaluación del caso CAL_F005_01_COURBET, no como caso independiente. Ver `lotes/F006_TRAZA_V2_R7_RESUMEN.json`, `lotes/F006_TRAZA_V2_R7_MANIFIESTO_ARTIFACTO.json`, `CALIBRACION_ACUMULADA.md` y `PLAN_SIGUIENTE_LOTE_INDEPENDIENTE.md`.
 (calibración en muestra grande)

Arma, sella, corre y califica casos nuevos con el **mismo formato** de los lotes cerrados (CAL_LOTE01) y el arnés
existente `motor/calibracion/arnes_calibracion.py`. No cambia el protocolo, no toca Engine ni catálogo, no usa LLM.

## Flujo
1. **Semillas** (`semillas_lote_XXXX.py`): por sujeto real, cortes P/A/C acumulativos y variables según la biografía; no existe un número universal. En biografías cerradas, el primer corte cierra exactamente en la fecha de nacimiento y el último termina exactamente en Z90; en preguntas vivas, Z es la fecha actual. Añadir cortes ante cambios de rol, crisis, decisiones irreversibles o cambios de dirección del vector; detenerse cuando el siguiente corte no cambie la trayectoria por debajo del umbral de saturación registrado. Cada corte debe declarar fecha, motivo y evidencia con fuentes, usando solo información conocida hasta su cierre. Tokens del vocabulario de los 244 y pesos 0,60–0,84. Las familias/destino quedan separados y sellados por custodio independiente.
2. **Preparador: usar exclusivamente la ruta entry-only JSON.** `fabrica.py preparar` es legado y escribe desenlaces. `fabrica.py preparar-z` importa `SEMILLAS_Z` y `DESTINOS` en el mismo proceso y escribe entrada, desenlace y, si existe, destino; sigue prohibido desde el preparador. La nueva ruta `python3 casos/fabrica/preparar_entrada_solo.py casos/fabrica/semillas_entrada/<lote>.json` acepta JSON, valida Z90, fuentes primarias, tokens/pesos y unicidad contra entradas visibles; las identidades selladas de C01–C20 requieren comprobación del custodio, y escribe solo `entrada.json` + `entrada.sha256` en `entradas_solo/`. No carga destinos, no ejecuta el motor ni incrementa n. No invocar `preparar-z` ni `correr` desde el preparador; la ruta entry-only tampoco se ejecuta con F007 actual.
3. `python3 casos/fabrica/fabrica.py correr --lote XXXX --n 5`
   - verifica Engine `665c39a2…` y patrones `d827dcc3…`;
   - escribe `lotes/XXXX_COMPROMISO.json` con el sha256 de cada entrada y cada desenlace **antes** de correr;
   - corre el motor en una copia temporal de `motor/` (búsqueda viva `CALDERO_BUSCADOR=auto`, sin claves);
   - vuelve a verificar los candados (repo y copia);
   - el comando actual `correr` todavía abre los desenlaces para evaluar: solo el custodio independiente puede ejecutarlo y hacer el unblinding; el preparador no debe invocarlo ni leer esos archivos. ChatGPT preparador solo escribe semillas y verifica su entrada. Separar ejecución sin unblinding y evaluación por custodio sigue siendo trabajo pendiente.
   - agrega filas a `calibracion_acumulada.csv` y regenera `CALIBRACION_ACUMULADA.md`.
   El resumen de una línea por corrida va en `resultados/resultados.jsonl`; la corrida completa va en `motor/runs/<LOTE>_<FECHA>/` para el historial, gobernada por `CONTRATO_GUARDAR_CORRIDAS.md` y verificada por el candado `scripts/candado_entrega.py` con `LECTURA.json`. La copia local de trabajo queda en `/workspace/FABRICA_CORRIDAS/<lote>/`.

## Calificación (0/1 por caso)
- `acierto_H1`, `acierto_H2`: la familia está entre las del desenlace.
- `acierto_set`: alguna hipótesis abierta está entre las del desenlace.
- `acierto_apuesta`: alguna hipótesis que converge en el escenario principal está entre las del desenlace (regla del arnés).
- Casos que el motor pausa (exit 6, TORTUGAS) quedan como NO_SELLADO y no cuentan.

## Uso diario
**Estado actual:** existe una ruta entry-only JSON aislada, pero todavía no existe un proceso custodial independiente verificable. El preparador no ejecuta `preparar-z` ni `correr`. La nueva ruta no debe ejecutarse con F007 actual: sus referencias son secundarias y no hay cohorte sellada independiente. Cada sujeto nuevo necesita fuente primaria apta, Z congelado antes de H1/H2 y separación de destino.
El custodio independiente debe crear y sellar los destinos fuera del entorno del preparador. La ejecución y evaluación requieren un runner que produzca RESULT/RECIBO/CEB/manifiesto ligados al input y no abra destinos antes de congelar la salida. La implementación actual de `correr` abre desenlaces, por lo que solo el custodio puede realizar el unblinding. No contar casos como independientes sin fuentes primarias, Z90 válido, custodia separada y recibos.

## Apuesta de destino personal (PATCH 022)
Además de H1, set y apuesta temática, cada corrida trae `apuesta_destino_personal`: auge | meseta | caida | ruptura.
- Por cada sujeto, en `cola/<ID>/destino_sellado.json` (aparte de la entrada y del desenlace): `{"destino": ..., "porque": ..., "fuente": ...}`.
  Su sha256 entra en el COMPROMISO antes de correr; si cambia, la fábrica no evalúa (DESTINO_ALTERADO).
- La evaluación agrega `acierto_destino` (etiqueta exacta) y `acierto_destino_polaridad` (auge/meseta frente a caida/ruptura).
- `python3 casos/fabrica/fabrica.py correr --lote X --rehacer ID1,ID2` vuelve a correr casos ya evaluados con sus mismos sellos (sirve para un parche nuevo, nunca para reetiquetar).
- En las semillas de lotes nuevos, fija el destino ANTES de correr.

## Compuerta Z_trabajo + preparación ciega (obligatoria para lotes nuevos)
- Lotes nuevos: el preparador entrega solo `semillas_lote_X.py`; el custodio independiente crea y sella `destinos_lote_X.py` fuera del entorno del preparador. No ejecutar `preparar-z` desde el preparador: la implementación actual importa ambos módulos en el mismo proceso y escribe entrada, desenlace y destino. La ruta entry-only JSON existe desde 2026-11-23; preparar-z sigue prohibido y la nueva ruta no sustituye la custodia independiente.
- Protocolo biográfico: `motor/PROTOCOLO_BIOGRAFICO_Z90.md`. Biografía cerrada: Z_trabajo = Z90 (90 % del intervalo nacimiento→muerte); ventanas acumulativas desde nacimiento; el primer cierre debe ser exactamente nacimiento y el último exactamente Z90. Pregunta viva: Z = hoy. No fijar número de cortes. La gate `motor/calibracion/gate_z90.py` calcula Z90, valida ventanas y cierres, exige el primer corte en nacimiento y en modo histórico rechaza fuentes secundarias fechadas después del corte. La integración de la gate en `motor/correr_estandar.py` está en la rama activa `alterno/cameo-pesos`; PR #8 permanece OPEN/NOT MERGED y no se fusiona sin autorización. CI de la rama: 62 pruebas pasaron tras la corrección de límites; la custodia independiente sigue sin verificarse.
- Una sola violación rechaza el lote entero. `correr` vuelve a pasar la compuerta antes del motor; el arnés también la aplica si la entrada trae `gate_z`.
- El `preparar` viejo queda bloqueado (código 7) salvo `FABRICA_PERMITIR_SIN_GATE=1`, solo para lotes ya sellados como F001.
- La regla que se califique se congela con su sha256 ANTES de abrir destinos, y conviene probarla en sujetos que quien la diseñó no ha visto.
- Cómo escribir semillas: `PROMPT_SEMILLAS_Z.md`.

## Revalidación Z90 — 2026-11-21

`motor/calibracion/gate_z90.py` ahora contiene la revisión `Z90_BIRTH_DEATH_WINDOWS_V1_20261121`: calcula Z90 desde nacimiento/muerte, exige `z_trabajo = z90_date = Z90`, valida `window_start` desde nacimiento en todos los cortes, cierres crecientes y último cierre en Z90. También compara `claim_date` y la fecha de fuente primaria con el cierre individual.

Esto no resuelve la separación de funciones: `preparar-z` continúa bloqueado porque importa entradas y destinos en el mismo proceso; tampoco convierte F007 en cohorte independiente ni integra automáticamente `correr_estandar`. No ejecutar ni contar corridas hasta que exista ruta entry-only y custodia independiente.


## Ruta entry-only JSON — 2026-11-23

- Script: `casos/fabrica/preparar_entrada_solo.py`.
- Entrada local: `casos/fabrica/semillas_entrada/<lote>.json`, formato `{"cases": [...]}`; esquema: `semillas_entrada/entrada_schema_v1.json`.
- Salida local y excluida de Git: `casos/fabrica/entradas_solo/<case_id>/entrada.json` y `entrada.sha256` exclusivamente.
- El CLI acepta solo JSON dentro de `semillas_entrada/`; no acepta ruta de destinos ni módulos Python. Rechaza campos de destino/desenlace/H1/H2, fuentes secundarias, sujetos/case_id repetidos, pesos fuera de 0.60–0.84 y errores de la gate.
- La función importa solo definiciones/helper locales de `fabrica.py`; no llama `preparar_z`, `correr`, ni carga módulos de destinos. No crea `desenlace_sellado.json` ni `destino_sellado.json`.
- La salida no constituye una corrida, no crea RESULT/RECIBO/CEB, no incrementa n y no prueba independencia del custodio. El custodio debe crear y sellar los destinos en un proceso separado antes de cualquier ejecución.
- Las semillas JSON y las entradas generadas están en `.gitignore`; no se versionan en este repositorio mientras persista la discrepancia de privacidad.


## Índice de entradas previas — 2026-11-23

- preparar_entrada_solo.py indexa case_id y sujetos visibles desde resultados.jsonl, casos/ciegos/**/entrada.json (excluyendo cualquier ruta custodia), semillas JSON previas, entradas entradas_solo y los literales id/person de SEMILLAS_Z en F007 mediante AST, sin importar ni ejecutar el módulo.
- Reserva los IDs de directorio C01–C20 sin abrir SALIDA_CONGELADA ni custodia. Si un archivo de entrada previo es ilegible o malformado, falla cerrado y no escribe ninguna entrada.
- Límite deliberado: los nombres de los sujetos C01–C20 permanecen sellados y no se leen. El custodio debe verificar la unicidad de sujetos contra su índice privado antes de aceptar o sellar una cohorte.
- CI de alterno/cameo-pesos: run #45172870551 SUCCESS, 78 pruebas pasaron. El run #45172749593 falló por un literal de salto de línea en un fixture AST; el fixture se corrigió en el commit 9f99f15de4bef42544157865ff8881c0f41f225e y el run posterior pasó.
- No se creó ningún JSON de semillas ni entrada staged; no hubo ejecución, RESULT, RECIBO, CEB ni incremento de n. F007 continúa no apto por fuentes secundarias y ausencia de Z90 válido/custodia independiente.
