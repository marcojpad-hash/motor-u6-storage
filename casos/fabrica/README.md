# Fábrica de casos

Estado al 2026-10-31: F006_TRAZA_V2_R7 está archivado como reevaluación del caso CAL_F005_01_COURBET, no como caso independiente. Ver `lotes/F006_TRAZA_V2_R7_RESUMEN.json`, `lotes/F006_TRAZA_V2_R7_MANIFIESTO_ARTIFACTO.json`, `CALIBRACION_ACUMULADA.md` y `PLAN_SIGUIENTE_LOTE_INDEPENDIENTE.md`.
 (calibración en muestra grande)

Arma, sella, corre y califica casos nuevos con el **mismo formato** de los lotes cerrados (CAL_LOTE01) y el arnés
existente `motor/calibracion/arnes_calibracion.py`. No cambia el protocolo, no toca Engine ni catálogo, no usa LLM.

## Flujo
1. **Semillas** (`semillas_lote_XXXX.py`): por sujeto real, cortes P/A/C acumulativos y variables según la biografía; no existe un número universal. En biografías cerradas, el primer corte empieza en el nacimiento y el último termina exactamente en Z90; en preguntas vivas, Z es la fecha actual. Añadir cortes ante cambios de rol, crisis, decisiones irreversibles o cambios de dirección del vector; detenerse cuando el siguiente corte no cambie la trayectoria por debajo del umbral de saturación registrado. Cada corte debe declarar fecha, motivo y evidencia con fuentes, usando solo información conocida hasta su cierre. Tokens del vocabulario de los 244 y pesos 0,60–0,84. Las familias/destino quedan separados y sellados por custodio independiente.
2. **Preparador: no ejecutar la fábrica.** `fabrica.py preparar` es legado: recibe familias dentro del módulo de semillas y escribe `desenlace_sellado.json`; no es una ruta entry-only. `preparar-z` importa `SEMILLAS_Z` y `DESTINOS` en el mismo proceso y escribe `entrada.json`, `desenlace_sellado.json` y, si existe, `destino_sellado.json`. El preparador solo entrega `semillas_lote_XXXX.py`. No invocar `preparar`, `preparar-z` ni `correr` desde el entorno del preparador hasta que exista una ruta entry-only real y custodia independiente verificada.
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
Lo único que no se automatiza sin riesgo de inventar es **escribir las semillas**: cada sujeto necesita hechos con fuente.
El preparador redacta únicamente el archivo de semillas con 5–10 sujetos variados y no ve destinos. El custodio independiente crea y sella los destinos en un entorno separado. El runner debe producir RESULT/RECIBO/CEB/manifiesto ligados al input; el unblinding y la evaluación corresponden al custodio después de congelar la salida. La implementación actual de `correr` aún abre destinos, por lo que el preparador no debe ejecutarla. No contar casos como independientes sin fuentes primarias, Z90 válido, custodia separada y recibos.

## Apuesta de destino personal (PATCH 022)
Además de H1, set y apuesta temática, cada corrida trae `apuesta_destino_personal`: auge | meseta | caida | ruptura.
- Por cada sujeto, en `cola/<ID>/destino_sellado.json` (aparte de la entrada y del desenlace): `{"destino": ..., "porque": ..., "fuente": ...}`.
  Su sha256 entra en el COMPROMISO antes de correr; si cambia, la fábrica no evalúa (DESTINO_ALTERADO).
- La evaluación agrega `acierto_destino` (etiqueta exacta) y `acierto_destino_polaridad` (auge/meseta frente a caida/ruptura).
- `python3 casos/fabrica/fabrica.py correr --lote X --rehacer ID1,ID2` vuelve a correr casos ya evaluados con sus mismos sellos (sirve para un parche nuevo, nunca para reetiquetar).
- En las semillas de lotes nuevos, fija el destino ANTES de correr.

## Compuerta Z_trabajo + preparación ciega (obligatoria para lotes nuevos)
- Lotes nuevos: el preparador entrega solo `semillas_lote_X.py`; el custodio independiente crea y sella `destinos_lote_X.py` fuera del entorno del preparador. No ejecutar `preparar-z` desde el preparador: la implementación actual importa ambos módulos en el mismo proceso y escribe entrada, desenlace y destino. No existe ruta entry-only.
- Protocolo biográfico: `motor/PROTOCOLO_BIOGRAFICO_Z90.md`. Biografía cerrada: Z_trabajo = Z90 (90 % del intervalo nacimiento→muerte); ventanas acumulativas desde nacimiento; primer corte en nacimiento y último exactamente en Z90. Pregunta viva: Z = hoy. No fijar número de cortes. La gate `motor/calibracion/gate_z90.py` ya calcula Z90 y valida ventanas, cierres y evidencia por corte. La integración en `motor/correr_estandar.py` sigue en PR #8 (OPEN/NOT MERGED), con `mergeable_state=dirty`; no declarar el runner estándar habilitado hasta verificar el cableado y la custodia independiente.
- Una sola violación rechaza el lote entero. `correr` vuelve a pasar la compuerta antes del motor; el arnés también la aplica si la entrada trae `gate_z`.
- El `preparar` viejo queda bloqueado (código 7) salvo `FABRICA_PERMITIR_SIN_GATE=1`, solo para lotes ya sellados como F001.
- La regla que se califique se congela con su sha256 ANTES de abrir destinos, y conviene probarla en sujetos que quien la diseñó no ha visto.
- Cómo escribir semillas: `PROMPT_SEMILLAS_Z.md`.

## Revalidación Z90 — 2026-11-21

`motor/calibracion/gate_z90.py` ahora contiene la revisión `Z90_BIRTH_DEATH_WINDOWS_V1_20261121`: calcula Z90 desde nacimiento/muerte, exige `z_trabajo = z90_date = Z90`, valida `window_start` desde nacimiento en todos los cortes, cierres crecientes y último cierre en Z90. También compara `claim_date` y la fecha de fuente primaria con el cierre individual.

Esto no resuelve la separación de funciones: `preparar-z` continúa bloqueado porque importa entradas y destinos en el mismo proceso; tampoco convierte F007 en cohorte independiente ni integra automáticamente `correr_estandar`. No ejecutar ni contar corridas hasta que exista ruta entry-only y custodia independiente.
