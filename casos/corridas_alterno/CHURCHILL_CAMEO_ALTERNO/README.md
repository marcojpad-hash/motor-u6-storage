# Churchill — corrida en rama alterno/cameo-pesos (2026-11-11 01:37 CST)

Entrada original idéntica a la de 2026-10-24 (sha256 5858c5de…aa79). Rama commit 6b34518. Solo corrida, sin cambios de código.

Recibo: COMPLETED, exit 0, 8,77 s. Engine MATCH 665c39a2…, patterns MATCH d827dcc3…. MC 9/9, 5.905 sims. RESUELTO_OPERACIONALMENTE, AJUSTADA, SET_EXPLICA_TODOS_LOS_CORTES. DRIFT_WARNED solo en los 2 archivos CAMEO de la rama.

| | 2026-10-24 (main) | 2026-11-11 (alterno) |
|---|---|---|
| H1 | berlin_01_erizo | berlin_01_erizo |
| H2 | 30_ambicion | 30_ambicion |
| peso_relativo H1/H2 | 0,310436 / 0,265777 | 0,11994 / 0,105695 |
| margen | 0,044659 | 0,014245 |
| relleno H1/H2 | 67,27 / 55,54 | 59,95 / 53,20 |
| rank_fusion H1/H2 | 29,21 / 25,01 | 29,91 / 26,36 |
| candidatas publicadas | 4 | 11 |

- CAMEO no movió H: feeds_H=False, cameo_activity 0,9342 (71/76) igual que en octubre, 0 hits explícitos. peso_efectivo medio 0,599 (en rango), suma 42,56 (fuera de rango, no consumida).
- La baja de peso_relativo viene de repartir entre 11 candidatas en vez de 4; la proporción del par casi no cambió (0,532/0,468 vs 0,539/0,461).
- Fuera de 0,01–0,999: rank_fusion (16,65–29,91) por suma de grupos >1 (H1: puente_lateral 6,71, otras_dimensiones 5,55, greimas 3,15, dynamis 3,0, frye 3,0). indice_fusion_relativo_0_1 = 0,598 sí en rango.
- Corrida de octubre queda SOLO_CONSULTA (ver orden BUS agente-cero-costo #47).

Archivos: entrada.json, run.log, recibo, manifiesto del ledger CEB, resultado y ledger en .gz.
