# 2026-11-11 — Rama alterna: cameo con pesos

Rama: `alterno/cameo-pesos` (desde `main`, commit `f18ee162`).
Para: ChatGPT, Grok, Claude y demás modelos. Esta rama es un experimento, no es `main`.

## Qué cambia

Solo 2 archivos, solo en esta rama. `main` no se tocó. Engine V5 y catálogo 244 no se tocan.

1. `motor/motor/cameo_codebook_lateral_v1.json` — los 76 códigos CAMEO ahora traen
   `peso_equivalente` y `evidence_status` por código. Los tokens, labels y raíces
   son idénticos a `main` (verificado: 0 diferencias). Pesos por raíz:
   02: 0,68 · 03: 0,62 · 04: 0,65 · 05: 0,70 · 06: 0,74 · 08: 0,66 · 09: 0,58 ·
   10: 0,74 · 11: 0,72 · 12: 0,75 · 13: 0,82 · 14: 0,76 · 15: 0,80 · 16: 0,84 ·
   17: 0,88 · 19: 0,94. Todos `unverified`.
2. `motor/motor/plugin_cameo_institucional.py` — `evaluate()` ahora devuelve por
   código `peso_equivalente`, `evidence_status` y `peso_efectivo`, con la misma
   regla del canónico: `peso_efectivo = 0,5 + (peso − 0,5) × multiplicador`
   (`unverified` → 0,4). También devuelve los promedios del lote seleccionado.
   La lógica de selección (perfiles, rootmap) no cambió.

## Evidencia (corrida en motor alterno, no en el repo)

- Caso: Napoleón (`CAL_F001_01_NAPOLEON`), corrida `NAPOLEON_CAMEO_NUEVO`,
  2026-11-11 01:16 CST, 18,04 s, exit 0, recibo COMPLETED.
- H1: `31_conflicto_con_un_dios` (rank_fusion 28,74557, igual que el original).
  H2: `arquetipo_el_gobernante`. El ranking NO se movió.
- Cameo en el resultado: perfil `institucional`, 71 de 76 códigos seleccionados,
  peso equivalente medio 0,7486, peso efectivo medio 0,5994, suma 42,56,
  0 hits explícitos.
- Monte Carlo: 9/9 convergido, 5.689 simulaciones. Hashes verificados:
  Engine 665c39a2…, patterns d827dcc3….

## Qué NO hace (todavía)

Los pesos ya viajan en la corrida, pero H no se mueve: la actividad de cameo
del motor (`cameo_activity`) se calcula por conteo (seleccionados/disponibles)
y en este caso no hubo códigos explícitos golpeados. Si se quiere que el peso
mueva el ranking, hay que cablearlo a la actividad, no solo guardarlo.
Eso queda como decisión pendiente de Mj.

## Cómo correrlo

Copiar el repo en esta rama a una carpeta aparte y correr ahí (nunca sobre
`main` ni sobre el motor canónico):
`python3 motor/correr_estandar.py casos/fabrica/cola/CAL_F001_01_NAPOLEON/entrada.json <NOMBRE_CORRIDA>`

No hacer merge a `main` sin decisión de Mj.
