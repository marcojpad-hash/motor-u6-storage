# Regla de Mj (25-oct-2026): las herramientas existen para ejecutarse

- Caldero y todas las herramientas del motor **existen para correr**. No son Python de adorno.
- El CEB está para que no nos mientan, pero **explica el fallo, no lo justifica**.
- Si una herramienta no corrió (SIMULADO_FIXTURE, NO_INVOCADO, INTENTADO_FALLIDO, OMITIDO_POR_CONDICION), eso es un
  **FALLO DE EJECUCIÓN / A INVESTIGAR**, no un "OK honesto". Hay que descubrir **por qué** no corrió.
- Única excepción: que su contrato diga que solo corre bajo ciertas condiciones. Hoy la única documentada es
  `SKIPPED_INTERNAL_ANALYSIS` (subcorrida interna T1, `required=False` en el motor) → `INFO_OMISION_CONTRACTUAL`.

## Qué cambió
- `laterales_unico_v1.py`: la fila CEB de Caldero trae `debe_ejecutarse`, `incumplimiento`, `severidad`
  (`OK` / `FALLO_EJECUCION` / `INFO_OMISION_CONTRACTUAL`), `alerta` y `accion` (qué investigar).
- `casos/fabrica/fabrica.py`: compuerta Caldero. Con `CALDERO_BUSQUEDA_VIVA=1` (por defecto) cada caso debe salir `EJECUTADO`.
  Si sale fixture, no invocado, fallido o sin fila CEB (`SIN_RECIBO_CEB`): se imprime `FALLO_EJECUCION_CALDERO`, queda en
  `compuerta_caldero` del RESUMEN y el lote termina con **código 9** (no 0). El sello y las filas se guardan igual (no se borra evidencia).
  `FABRICA_CALDERO_REQUERIDO=0` lo apaga explícitamente.
- No se tocó Engine ni catálogo 244; compuertas de ceguera/Z intactas.
