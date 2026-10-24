# 2026-10-24 — Grok Bot — PATCH 022: apuesta de destino personal

**Qué cambió:** campo nuevo `apuesta_destino_personal` (auge/meseta/caida/ruptura), calculado con el balance entre familias a favor y en contra del sujeto, corte por corte (movimiento_de_fondo). H1/H2 y la apuesta temática no cambian. Arnés y fábrica califican el destino contra `destino_sellado.json`. Detalle en motor/PARCHES/PATCH_022_APUESTA_DESTINO_PERSONAL.md.

**Antes → ahora (F001, mismos sellos, lote F001_D022):**

| Caso | Destino real | Apuesta temática (vieja) | Destino 022 | ¿Acierta? |
|---|---|---|---|---|
| Napoleón 1812 | caida | CONTINUIDAD_ASCENDENTE | caida | sí |
| Tesla 1901 | caida | MESeta_O_ESTABILIZACION | auge | no |
| Wilde 1895 | ruptura | CONTINUIDAD_ASCENDENTE | ruptura | sí |
| Disney 1928 | auge | CONTINUIDAD_ASCENDENTE | auge | sí |
| Turing 1952 | ruptura | MESeta_O_ESTABILIZACION | caida | no (polaridad sí) |

Apuesta vieja: 0/5. Destino exacto: 3/5; polaridad: 4/5. H1 igual: 1/5. Muestra mínima; los polos se escribieron conociendo F001, así que esto no valida la regla.

**Hashes canónicos:** Engine 665c39a2…c36082 y patterns_final_v14 d827dcc3…6667a1 OK antes y después (repo y copia temporal). Regla 022 sha256 4252fd45…49b302.

**Pruebas:** tests/test_arnes_calibracion.py 7/7; corrida F001_D022 sin errores, `H_y_apuesta_tematica_intactos=true` en los 5 casos.
