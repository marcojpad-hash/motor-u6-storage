# Revisión — corridas F001/F002 (2026-11-11)

Casos revisados: 15. Recibo COMPLETED en los 15. result_missing_paths y result_nonfinite_paths vacíos en los 15. null_values y nonfinite_values en 0 en los 15. continuidad NO_PAUSADA en los 15.

## Hallazgos sistemáticos (en los 15 casos)

- Recibo incompleto: `receipt_missing_paths` = `['$.stages[8].adaptador', '$.stages[8].verificacion_no_escribe_H']` en los 15. El runner no registra el adaptador ni la verificación de que no escribe H en la etapa 8.
- Sin tabla de mortalidad: `huellas_declaradas_ausentes` = `matriz_mortalidad_z90.data_table_sha256: NO_APLICA_SIN_TABLA` en los 15. Ningún input trae mortality_statistics; ausencia declarada, no hash inventado. (Es el pendiente de construir la mortalidad.)
- Motor NO_CALIBRADO en los 15 (`predictive_validation: NOT_CALIBRATED_NO_CASE_LEVEL_OUTCOMES`). Los valores son soporte estructural, no probabilidad calibrada.
- Resolución terminal `RESUELTO_OPERACIONALMENTE` en los 15, con la nota: 'la incertidumbre se conserva en grado/objeciones; el estado terminal es una decisión operacional, no verdad validada'.
- Búsqueda de arquetipos `EXECUTED_WITH_SOURCES_NO_LLM_HINTS` en los 15; `llm_neighbor_hints_n = 0` en los 15.

## Patrón limpio (no anomalía, pero verificado)

- Los 6 casos FRAGIL son exactamente los 6 con `estado_durante_corrida: RESOLUCION_REQUERIDA` (TESLA, TURING, PASTEUR, ARBUCKLE, BACH, CATALINA). Los 9 AJUSTADA son exactamente los 9 con `EVIDENCIA_SEPARADA`. Correlación perfecta, sin excepciones.

## Hallazgos por caso

- **CAL_F001_02_TESLA**: grado FRAGIL (mezcla: H1_CON_COMPONENTES_DE_H2).
- **CAL_F001_05_TURING**: grado FRAGIL (mezcla: H1_CON_COMPONENTES_DE_H2).
- **CAL_F002_01_GALILEI**: tortugas_ejecutado=False (no se ejecutó la prueba de tortugas en este caso); casos_semejantes_consultados=1 (único caso con un caso semejante consultado).
- **CAL_F002_02_PASTEUR**: grado FRAGIL (mezcla: H1_CON_COMPONENTES_DE_H2).
- **CAL_F002_03_ARBUCKLE**: grado FRAGIL (mezcla: MEZCLA_H1_H2_SIN_SEPARACION).
- **CAL_F002_04_BACH**: grado FRAGIL (mezcla: MEZCLA_H1_H2_SIN_SEPARACION); H1 y H2 prácticamente empatados en rank_fusion (24.9 vs 24.898185, diff 0.0018).
- **CAL_F002_07_CATALINA**: grado FRAGIL (mezcla: H1_CON_COMPONENTES_DE_H2).
- **CAL_F002_09_ROCKEFELLER**: tortugas_ejecutado=False (no se ejecutó la prueba de tortugas en este caso).

## Nota de entrega
Los RESULT completos (~90 MB en total, 3.3–7.1 MB c/u) no se suben por el límite de 16 MiB del snapshot de push-files; se sube el resultado interpretable completo (salida_interpretable íntegra, sin recortes) + recibo + entrada, y el SHA-256 de cada RESULT completo queda en MANIFIESTO.json.