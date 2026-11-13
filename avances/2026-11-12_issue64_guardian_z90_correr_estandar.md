# Issue #64 — guardián Z90 cableado a correr_estandar + previo_error siempre presente — 2026-11-12

Issue #64 de marcojpad-hash/agente-cero-costo (punto 2 de la auditoría de trazabilidad).
Rama de trabajo: `alterno/cameo-pesos`. PR sin merge.

## Antes
- `motor/calibracion/gate_z90.py` existía, pero solo la llamaban `fabrica.py` y
  `arnes_calibracion.py`. `correr_estandar` nunca la ejecutaba: un caso con datos
  post-Z90 entraba al motor sin que nadie lo bloqueara.
- `previo_error` solo aparecía en la rama de FALLO de `efectividad_corte_retenido`;
  en éxito el campo faltaba del todo (mismo hueco del recibo: el guardián solo
  corría como diagnóstico).

## Arreglo (`motor/correr_estandar.py`, `motor/tests/test_guardian_z90_correr_estandar.py`)
- `_guardian_z90(case)`: ejecuta `validar_entrada()` y devuelve el veredicto.
  Activa SOLO cuando el caso declara disciplina Z90 (`gate_z`, o
  `z_trabajo`+`modo_z`) o `FABRICA_GATE_Z90=1` — igual que los otros dos
  llamadores. Sin esos campos queda `NO_CONFIGURADO` y corre como antes (el lote
  F001 y los ciegos no declaran disciplina; cablear sin esta condición rechazaría
  todo el catálogo existente). Fail-closed: si la compuerta falta o falla, bloquea.
  El veredicto no lleva `None` en ningún campo (un `None` se convierte en hueco
  de dato y el recibo queda `INCOMPLETE_OUTPUT_DATA`, exit 4 — regresión cazada
  por `test_interruptor_viva_offline` y corregida con marcadores `NO_DECLARADO` /
  `NO_APLICA`).
- Hook en `main()`, tras filtro 017 y consulta dirigida y ANTES de que nada entre
  al motor: si la compuerta rechaza, no se ejecuta el motor; se escribe resultado
  y recibo con `BLOQUEADO_GUARDIAN_Z90` y se sale con código 8, como la compuerta de fábrica. En éxito, el veredicto queda en `result["guardian_z90"]`, en
  el recibo (clave + etapa) y en la etapa `guardian_z90` de los stages.
- `_efectividad_corte_retenido(sello, visto, retenido)`: extrae el bloque a un
  helper testeable; `previo_error`, `visto_error`, `previo_status` y
  `visto_status` están SIEMPRE, en éxito (`False` = sin error) y en fallo
  (`stderr_tail`). Nunca `None`.
- R6 (lista negra post-Z) no se aplica aquí: la lista vive fuera de la entrada,
  junto al destino sellado.

## Verificación por ejecución (no solo lectura)
- `CAL_F002_01_GALILEI` (caso gated real del repo): exit 0, 37.2 s,
  H1 `arquetipo_el_sabio`, H2 `kwml_03_mago`, recibo COMPLETED, `guardian_z90`
  PASS (0 errores), `previo_error` `False` y `visto_error` `False` en éxito.
- Mismo caso con el corte movido a 1700 (post-Z90): exit 8,
  `BLOQUEADO_GUARDIAN_Z90`, errores R2 + R3, resultado + recibo escritos.
- Tests nuevos: 8 en `motor/tests/test_guardian_z90_correr_estandar.py`
  (NO_CONFIGURADO, PASS, rechazo post-Z, rechazo sin evidencia, previo_error en
  éxito y en fallo, sin nulos en el veredicto, e2e de bloqueo con exit 8).
- Suite completa: **192 passed, 2 skipped** (`motor/tests/` + `tests/`, 11.6 s).
- Integración: `test_interruptor_viva_offline` PASA. `test_pausa_y_reanudacion`
  FALLA también en el árbol limpio (verificado con `git stash`): preexistente,
  el harness que fuerza el fallo de TORTUGAS no dispara la pausa en este entorno;
  no es regresión de este cambio.

Engine_V5_CANONICO_SOLO.py y patterns_final_v14.json intactos (sin tocar).


## Corrección de conformidad — 2026-11-13
- El encargo original exige código de salida **8**; la primera revisión del PR usó 7. Se corrigieron el runner, el test E2E y este informe para reservar 8 a `BLOQUEADO_GUARDIAN_Z90`.
- `previo_error` y `visto_error` usan ahora `False` cuando no hay error; conservan `stderr_tail` cuando existe. Esto cumple el contrato sin introducir `null`.
- Esta corrección queda pendiente de la nueva ejecución de GitHub Actions; no se declara verde hasta recibir el check.
