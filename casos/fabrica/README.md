# Fábrica de casos (calibración en muestra grande)

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
