# Cómo correr el Motor U6 (runbook)

Entrada estándar: `motor/correr_estandar.py`. No depende de `/workspace/TIRADA`
ni de `CONSOLIDADO`. Monte Carlo: ON (solo se apaga con `--no-mc`).

## Uso

```bash
cd motor
pip install -r ../requirements.txt   # una vez: numpy + pytest
python3 correr_estandar.py ../casos/fabrica/cola/CAL_F001_01_NAPOLEON/entrada.json CAL_F001_01_NAPOLEON
```

Salida en `motor/`:
- `RESULT_<caso>.json` — resultado completo (H1/H2, apuesta, Monte Carlo).
- `RESULT_<caso>_RECIBO_EJECUCION.json` — recibo con hashes, stages y status.
- `RESULT_<caso>_CEB_LEDGER_1.jsonl` — copia del ledger de auditoría CEB.
- `RESULT_<caso>_CEB_LEDGER_MANIFIESTO.json` — manifiesto del ledger (origen, sha256).

## Qué significa el código de salida

| Código | Significado |
|---|---|
| 0 | Artefacto limpio y completo. |
| 3 | Motor corrió y el resultado está completo, pero la **búsqueda externa (Caldero) falló** (etapa requerida). Es el código normal sin red o sin clave Exa. |
| 4 | Salida con datos incompletos / no finitos. |
| 5 | Completado con hueco de metadatos. |
| 6 | Corrida pausada reanudable (checkpoint `_CHECKPOINT_REANUDABLE.json`). |

El recibo (`RECIBO_EJECUCION.json`) es la constancia: `status`,
`duration_seconds`, `input_sha256`, `output_sha256`,
`canonical_engine_sha256` y `patterns_sha256` (deben coincidir con el
Engine canónico y el catálogo 244; si difieren, el runner bloquea).

## El ledger CEB y el disco lento (importante)

El CEB (`motor/motor/ceb_runtime_v0_6_flow.py`) escribe un ledger de auditoría
de ~12 MB por corrida en miles de appends pequeños. En disco lento (btrfs con
writeback) eso dejaba el motor atorado minutos: el proceso quedaba en estado D
(disk sleep, `btrfs_btree_wait_writeback_range`) y el runner lo mataba a los
90 s sin salida. Con el ledger en tmpfs (RAM) la misma corrida termina en
~14 s.

**El runner ya lo resuelve solo**: `_run_internal_case_isolated()` pone
`CEB_ROOT` en `/dev/shm/ceb_runs` o `/tmp/ceb_runs` (tmpfs) cuando `CEB_ROOT`
no está fijado. Un `CEB_ROOT` explícito (env) o `case["ceb_root"]` siempre gana.
El ledger se copia junto al resultado (`preservar_ledger_ceb`), así que la
evidencia queda en disco aunque el original viva en RAM.

Si el ledger en tmpfs no es opción (p. ej. `/dev/shm` y `/tmp` no son tmpfs),
fijar `CEB_ROOT` a un directorio rápido, o aceptar que la corrida tarde
varios minutos y subir el timeout del runner.

`/tmp` y `/dev/shm` se limpian al reiniciar; los ledgers ahí son desechables
(la copia junto al `RESULT_*.json` es la que se conserva). Limpiar
`/dev/shm/ceb_runs` y `/tmp/ceb_runs` de vez en cuando si se corren muchos casos.

## Búsqueda externa (Caldero)

La búsqueda de arquetipos es una etapa **requerida**. Sin red o sin clave,
el recibo queda en `INCOMPLETE_REQUIRED_EXTERNAL_SEARCH` y el exit es 3,
pero el resultado del motor (H1/H2, Monte Carlo, apuesta) está completo.

- Sin red/clave: `CALDERO_BUSCADOR=offline SEARCH_PROVIDER=offline` (falla rápido).
- Con clave Exa: `EXA_API_KEY=...` (el sidecar prueba Exa/OpenAI/OpenRouter/
  Tavily/web; timeouts 20–60 s por proveedor).

## Tests

```bash
python3 -m pytest motor/tests/ tests/ -q
```

- 175 passed, 2 skipped (2026-11-08, VM). Los 2 skips son intencionales
  (fixtures históricos no presentes; no se inventa la línea base).
- Contratos del workflow (6 archivos): 39 passed.

## Fábrica / calibración

`casos/fabrica/fabrica.py correr --lote <LOTE> --n <N>` corre los casos
pendientes de `casos/fabrica/cola/` (los que aún no están en
`casos/fabrica/calibracion_acumulada.csv`) y acumula filas en ese CSV.
Al 2026-11-08 los 45 casos de la cola ya están evaluados (lotes
F001–F005), así que `correr` dice "sin casos pendientes en cola/".
Para re-correr casos ya evaluados: `--rehacer CAL_F001_01_NAPOLEON,...`
(agrega filas duplicadas al CSV; preferir el runner directo para
re-verificar sin tocar la calibración).

La fábrica exige búsqueda viva por defecto (`FABRICA_CALDERO_REQUERIDO=1`);
sin ella el lote queda `FALLO_EJECUCION_CALDERO`. Para correr sin red:
`FABRICA_CALDERO_REQUERIDO=0`. La fábrica sincroniza a StinkBox por
defecto (`FABRICA_SYNC=1`); para no sincronizar: `FABRICA_SYNC=0`.
Su `CORRIDAS` por defecto es `/workspace/FABRICA_CORRIDAS` (no existe fuera
del box original); fijar `FABRICA_CORRIDAS=<dir>` fuera del repo.

## Logger / runtime / watchdog: qué hay de verdad

- **No existe ningún archivo llamado `logger` ni `watchdog` en el repo.**
  Lo que hay:
  - **Registro**: el recibo JSON del runner (`*_RECIBO_EJECUCION.json`) con
    hashes, stages, duración y status. Es la constancia de ejecución.
  - **Runtime**: `motor/motor/ceb_runtime_v0_6_flow.py` (CEB v0.6.3) — ledger
    de auditoría por corrida y hook de auditoría de I/O. No es un
    demonio ni un supervisor; es un registro que corre dentro del motor.
  - **Auditoría horaria**: `.github/workflows/auditar-corridas-actions.yml`
    (revisa corridas en Actions). No hay un watchdog local que vigile
    procesos ni reinicie nada.
- **Falta para correr solo a diario**: un cron/workflow que ejecute el runner
  (o la fábrica) y avise si algo falla; hoy el lote diario es manual.
  Ver `~/workspace/motor-piezas-faltantes.md` (P0) para la lista completa.

## Rutas hardcodeadas `/workspace/` (no bloquean el runner)

Están en scripts/tests periféricos, no en la ruta de ejecución del runner
(el motor solo importa stdlib + numpy):
- `motor/motor/coactivacion_escalas.py:23`
- `motor/tests/run_tests_unico.py:8`, `motor/tests/test_u4_todos_tokens.py:44-45`
- `motor/scripts/analizar_unico.py:7`, `comparar_con_registrado_unico.py:8`,
  `construir_equivalencias_ORIGINAL.py:15`, `ensamblar_piezas.py:7`,
  `orquestador_unico.py:15,18,25`
- `casos/fabrica/fabrica.py`: `FABRICA_CORRIDAS` por defecto
  `/workspace/FABRICA_CORRIDAS` (sobreescribible por env).

## Evidencia (VM, 2026-11-08)

Corridas con el runner (H1 reproduce el CSV de calibración en los 4):

| Caso | H1 | Duración | Recibo |
|---|---|---|---|
| CAL_F001_01_NAPOLEON | 31_conflicto_con_un_dios (66.07%) | 14.554 s | `INCOMPLETE_REQUIRED_EXTERNAL_SEARCH` (búsqueda offline) |
| CAL_F001_02_TESLA | 22_todo_sacrificado_por_una_pasion (66.25%) | 14.078 s | idem |
| CAL_F001_03_WILDE | 31_conflicto_con_un_dios (64.85%) | 13.847 s | idem |
| CAL_F001_04_DISNEY | schwartz_10_autodireccion | 13.979 s | idem (con el default tmpfs, sin fijar `CEB_ROOT`) |

Nota: en NAPOLEON el H2 salió `30_ambicion` y el CSV dice
`arquetipo_el_gobernante` (margen pequeño, 24.55 vs 23.41 en rank_fusion);
la búsqueda externa —que aquí falló— alimenta ese ranking. H1 coincide en
los 4 casos.

## No tocar

- `motor/motor/Engine_V5_CANONICO_SOLO.py` y `patterns_final_v14.json`
  (canónicos, protegidos por hash; el runner bloquea si difieren).
- No modificar el motor U6 desde CAPCOT.
