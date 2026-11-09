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
| 0 | Artefacto limpio y completo. La búsqueda externa es opcional: si no hay red ni clave, la corrida completa offline con exit 0. |
| 3 | Fallo duro: falta Engine o patterns, o falló el subprocesso primario del motor. **Ya no se usa para la búsqueda** (antes: exit 3 por búsqueda faltante). |
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

## El motor es AGNÓSTICO: no depende de Exa ni de ningún proveedor

**Regla (Marco, 2026-11-08): el motor no puede irse a una sola cosa ni depender
de un solo proveedor ni estar viciado por él.** La búsqueda externa de
arquetipos (Caldero) es una etapa **opcional** de evidencia lateral: nunca
escribe H1/H2 y nunca es puerta de la corrida.

- **Orden de proveedores** (`motor/motor/caldero_buscadores.py`, `ORDEN_AUTO`):
  libres primero — ddgs, ddg, bing, searx, wiki, google — y solo después, si
  hay clave, exa, brave, serper, tavily. **Exa es un proveedor opcional más,
  nunca un requisito.** Se usa el primer motor libre que responda.
- **Sin red ni clave**: la corrida corre en modo offline y **completa con
  exit 0**. El recibo registra la búsqueda como `FAILED_OPTIONAL_STAGE`
  (`required: false`), sin marcar la corrida como incompleta. Antes de este
  arreglo la búsqueda se marcaba como etapa requerida y el recibo quedaba en
  `INCOMPLETE_REQUIRED_EXTERNAL_SEARCH` con exit 3; eso estaba mal y se corrigió
  en el motor (`MOTOR_V15_3_UNICO_20260927.py`: `required: False` en el intento
  Caldero) y en el runner (`correr_estandar.py`: la búsqueda nunca es puerta).
- **Con clave Exa** (opcional): `EXA_API_KEY=...` (el sidecar prueba
  Exa/OpenAI/OpenRouter/Tavily/web; timeouts 20–60 s por proveedor). No es
  necesaria para que el motor corra ni para que la corrida complete.

## Búsqueda externa (Caldero)

La búsqueda de arquetipos es una etapa **opcional** (ver la sección
agnóstica arriba). Sin red o sin clave, la corrida completa con exit 0 y
el resultado del motor (H1/H2, Monte Carlo, apuesta) está completo; el
recibo solo registra la búsqueda como `FAILED_OPTIONAL_STAGE`.

- Sin red/clave: `CALDERO_BUSCADOR=offline SEARCH_PROVIDER=offline` (falla rápido).
- Con clave Exa (opcional, nunca requisito): `EXA_API_KEY=...` (el sidecar
  prueba Exa/OpenAI/OpenRouter/Tavily/web; timeouts 20–60 s por proveedor).

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

La fábrica ya no exige búsqueda viva por defecto
(`FABRICA_CALDERO_REQUERIDO=0`; el motor es agnóstico y la búsqueda es
opcional). Para exigirla explícitamente: `FABRICA_CALDERO_REQUERIDO=1`.
Sin ella el lote queda `FALLO_EJECUCION_CALDERO` solo si se pide explícita.
La fábrica sincroniza a StinkBox por defecto (`FABRICA_SYNC=1`); para no
sincronizar: `FABRICA_SYNC=0`.
Su `CORRIDAS` por defecto es `/workspace/FABRICA_CORRIDAS` (no existe fuera
del box original); fijar `FABRICA_CORRIDAS=<dir>` fuera del repo.

## Logger / runtime / watchdog: qué hay de verdad

Lo que hace un motor es: correr casos, Monte Carlo, recibo y hashes. El
logger y el watchdog sirven a eso, nada más. No meten capacidades que no
son del motor ni reescriben el runner ni el Engine; envuelven la ejecución.

### Logger estructurado — `motor/logger_u6.py`

Módulo propio. Cada evento es un paso de una corrida: inicio (`run_start`,
con los hashes del Engine, del catálogo y del input), etapa (`stage`) y fin
(`run_end`, con exit, duración, H1/H2 y status del recibo). Niveles
DEBUG/INFO/WARNING/ERROR y timestamp UTC en cada registro.

- Escribe a **archivo** (`motor/logs/u6_<AAAA-MM-DD>.log`, una línea JSON por
  evento) y a **consola** (línea legible, por stderr; el JSON del resultado
  sale por stdout y no se toca).
- El runner lo usa: `correr_estandar.py` registra `run_start` al leer el
  input y `run_end` al terminar. La importación es opcional: si el logger
  no se puede importar, la corrida sigue exactamente igual.
- Uso directo:

```python
from logger_u6 import get_logger
log = get_logger("C01")
log.run_start(engine_sha="...", patterns_sha="...", input_sha="...")
log.stage("motor_run", "COMPLETED", monte_carlo=True)
log.run_end(returncode=0, seconds=14.5, h1="31_conflicto_con_un_dios",
            h2="30_ambicion", receipt_status="COMPLETED")
```

Variables: `U6_LOG_LEVEL` (DEBUG|INFO|WARNING|ERROR, defecto INFO),
`U6_LOG_DIR` (defecto `motor/logs/`), `U6_LOG_CONSOLE=0` para no escribir
a consola.

### Watchdog / supervisor — `motor/watchdog_u6.py`

Vigila una corrida: corre el runner como subproceso, detecta que el proceso
murió o se atoró por timeout, lo registra con el logger y, si es seguro, lo
reintenta **una vez** con backoff de 10 s.

```bash
cd motor
python3 watchdog_u6.py ../casos/fabrica/cola/CAL_F001_01_NAPOLEON/entrada.json NAPOLEON
python3 watchdog_u6.py ../casos/ciegos/lote_20/C01/entrada.json C01 --timeout 300
```

- **Se reintenta** (una vez) si el proceso murió o se atoró (timeout) **sin
  dejar recibo**: es un fallo transitorio, el runner se cayó antes de
  completar.
- **No se reintenta** si hay recibo (la corrida completó; un exit distinto
  de 0 es un resultado, no un cuelgue) ni si el fallo es duro (hashes del
  Engine/catálogo distintos del manifiesto, preflight, entrada inválida).
  Un reintento no arregla un fallo duro.
- Al terminar verifica: exit 0, existen `RESULT_<NOMBRE>.json` y
  `RESULT_<NOMBRE>_RECIBO_EJECUCION.json`, y los hashes del Engine/catálogo
  coinciden con el manifiesto. Devuelve el exit del runner (0 si la corrida
  completó, aunque haya sido en el reintento).

Lo que sigue sin haber (y no es del motor):
  - **Runtime**: `motor/motor/ceb_runtime_v0_6_flow.py` (CEB v0.6.3) — ledger
    de auditoría por corrida y hook de auditoría de I/O. No es un
    demonio ni un supervisor; es un registro que corre dentro del motor.
  - **Auditoría horaria**: `.github/workflows/auditar-corridas-actions.yml`
    (revisa corridas en Actions).
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

Verificación agnóstica (2026-11-08, tras el arreglo): NAPOLEON en offline
(`CALDERO_BUSCADOR=offline SEARCH_PROVIDER=offline`) completa con
**exit 0**, H1 `31_conflicto_con_un_dios` 66.07% (igual que el CSV),
Monte Carlo 9/9 convergido, recibo **COMPLETED** y etapa de búsqueda
`FAILED_OPTIONAL_STAGE` con `required: false`. La tabla de arriba es de
antes del arreglo (cuando la búsqueda se marcaba como requerida).

## No tocar

- `motor/motor/Engine_V5_CANONICO_SOLO.py` y `patterns_final_v14.json`
  (canónicos, protegidos por hash; el runner bloquea si difieren).
- No modificar el motor U6 desde CAPCOT.
