# Fábrica de casos

Estado al 2026-10-31: F006_TRAZA_V2_R7 está archivado como reevaluación del caso CAL_F005_01_COURBET, no como caso independiente. Ver `lotes/F006_TRAZA_V2_R7_RESUMEN.json`, `lotes/F006_TRAZA_V2_R7_MANIFIESTO_ARTIFACTO.json`, `CALIBRACION_ACUMULADA.md` y `PLAN_SIGUIENTE_LOTE_INDEPENDIENTE.md`.
 (calibración en muestra grande)

Arma, sella, corre y califica casos nuevos con el **mismo formato** de los lotes cerrados (CAL_LOTE01) y el arnés
existente `motor/calibracion/arnes_calibracion.py`. No cambia el protocolo, no toca Engine ni catálogo, no usa LLM.

## Flujo
1. **Semillas** (`semillas_lote_XXXX.py`): por sujeto real, 3 cortes P/A/C con tokens del vocabulario de los 244 y pesos 0,60–0,84,
   hechos solo hasta el freeze, con fuentes citables; y aparte las familias del desenlace + fuente. Las familias del desenlace se fijan
   **antes** de correr (juicio humano declarado).
2. `python3 casos/fabrica/fabrica.py preparar casos/fabrica/semillas_lote_XXXX.py`
   → `cola/<ID>/entrada.json` (sin desenlace) y `cola/<ID>/desenlace_sellado.json` (separado). Rechaza tokens fuera de vocabulario,
   pesos fuera de contrato, cortes posteriores al freeze, campos de desenlace y entradas duplicadas.
3. `python3 casos/fabrica/fabrica.py correr --lote XXXX --n 5`
   - verifica Engine `665c39a2…` y patrones `d827dcc3…`;
   - escribe `lotes/XXXX_COMPROMISO.json` con el sha256 de cada entrada y cada desenlace **antes** de correr;
   - corre el motor en una copia temporal de `motor/` (búsqueda viva `CALDERO_BUSCADOR=auto`, sin claves);
   - vuelve a verificar los candados (repo y copia);
   - abre los desenlaces solo si su hash coincide con el compromiso, y evalúa con el arnés;
   - agrega filas a `calibracion_acumulada.csv` y regenera `CALIBRACION_ACUMULADA.md`.
   Corridas completas quedan fuera del repo, en `/workspace/FABRICA_CORRIDAS/<lote>/`.

## Calificación (0/1 por caso)
- `acierto_H1`, `acierto_H2`: la familia está entre las del desenlace.
- `acierto_set`: alguna hipótesis abierta está entre las del desenlace.
- `acierto_apuesta`: alguna hipótesis que converge en el escenario principal está entre las del desenlace (regla del arnés).
- Casos que el motor pausa (exit 6, TORTUGAS) quedan como NO_SELLADO y no cuentan.

## Uso diario
Lo único que no se automatiza sin riesgo de inventar es **escribir las semillas**: cada sujeto necesita hechos con fuente.
Un agente (Grok Bot u otro) redacta un archivo de semillas por día con 5–10 sujetos variados (artistas, científicos, políticos,
empresarios…) y luego corre `preparar` + `correr`. Cada caso tarda ~15 s de motor.

## Apuesta de destino personal (PATCH 022)
Además de H1, set y apuesta temática, cada corrida trae `apuesta_destino_personal`: auge | meseta | caida | ruptura.
- Por cada sujeto, en `cola/<ID>/destino_sellado.json` (aparte de la entrada y del desenlace): `{"destino": ..., "porque": ..., "fuente": ...}`.
  Su sha256 entra en el COMPROMISO antes de correr; si cambia, la fábrica no evalúa (DESTINO_ALTERADO).
- La evaluación agrega `acierto_destino` (etiqueta exacta) y `acierto_destino_polaridad` (auge/meseta frente a caida/ruptura).
- `python3 casos/fabrica/fabrica.py correr --lote X --rehacer ID1,ID2` vuelve a correr casos ya evaluados con sus mismos sellos (sirve para un parche nuevo, nunca para reetiquetar).
- En las semillas de lotes nuevos, fija el destino ANTES de correr.

## Compuerta Z_trabajo + preparación ciega (obligatoria para lotes nuevos)
- Lotes nuevos: `fabrica.py preparar-z semillas.py destinos.py`. Son dos archivos separados: el preparador no conoce el final; el custodio guarda destino y lista negra.
- Validador: `motor/calibracion/gate_z90.py`, reglas R1–R7: fechas ≤ Z, evidencia por afirmación, primaria ≤ Z, secundaria congelada (modo vivo) o con preparación ciega (modo histórico), sin años posteriores a Z, sin lenguaje de futuro y sin palabras de la lista negra.
- Una sola violación rechaza el lote entero. `correr` vuelve a pasar la compuerta antes del motor; el arnés también la aplica si la entrada trae `gate_z`.
- El `preparar` viejo queda bloqueado (código 7) salvo `FABRICA_PERMITIR_SIN_GATE=1`, solo para lotes ya sellados como F001.
- La regla que se califique se congela con su sha256 ANTES de abrir destinos, y conviene probarla en sujetos que quien la diseñó no ha visto.
- Cómo escribir semillas: `PROMPT_SEMILLAS_Z.md`.
