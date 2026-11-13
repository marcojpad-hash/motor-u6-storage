# Revisión — corridas F003/F004 (2026-11-11)

Casos revisados: 20. Recibo COMPLETED en 20. Grados: 1 FRAGIL, 16 AJUSTADA y 3 FIRME (CAL_F003_08_LAW, CAL_F004_03_OPPENHEIMER, CAL_F004_10_LUDWIG_II).

## Hallazgos sistemáticos

- En los 20, la etapa `consulta_dirigida` existe pero queda `NO_CONFIGURADO`/`off`, con `n_preguntas=0` y `required=false`; `adaptador` y `verificacion_no_escribe_H` contienen el marcador `DATO_AUSENTE_REQUIERE_CLASIFICACION`. El sanitizador los señala en `receipt_missing_paths`; no son claves físicamente ausentes. Esto sigue incumpliendo el contrato del Issue #50, que exige consulta LLM obligatoria antes de H.
- Sin tabla de mortalidad en los 20: huellas declaradas ausentes: ["[{'path': '$.matriz_mortalidad_z90.data_table_sha256', 'valor': 'NO_APLICA_SIN_TABLA', 'motivo': 'no existe mortality_statistics.jsonl.gz ni mortality_statistics.json ni filas mortality_statistics/mor"]
- Motor NO_CALIBRADO en los 20 (`predictive_validation`: ['NOT_CALIBRATED_NO_CASE_LEVEL_OUTCOMES']). Los valores son soporte estructural, no probabilidad calibrada.
- Resolución terminal en los 20: ['RESUELTO_OPERACIONALMENTE'].

## Patrón FRÁGIL vs estado durante corrida (verificado)

- Casos con `estado_durante_corrida: RESOLUCION_REQUERIDA`: 1 (CAL_F003_01_CARAVAGGIO).
- Casos con `estado_durante_corrida: EVIDENCIA_SEPARADA`: 19 (CAL_F003_02_DICKENS, CAL_F003_03_LAVOISIER, CAL_F003_04_FARADAY, CAL_F003_05_FOUQUET, CAL_F003_06_TROTSKY, CAL_F003_07_LINCOLN, CAL_F003_08_LAW, CAL_F003_09_CARNEGIE, CAL_F003_10_PEDRO_II, CAL_F004_01_WAGNER, CAL_F004_02_DAVID, CAL_F004_03_OPPENHEIMER, CAL_F004_04_MENDEL, CAL_F004_05_KHRUSHCHEV, CAL_F004_06_TRUMAN, CAL_F004_07_CHANEL, CAL_F004_08_LESSEPS, CAL_F004_09_LAY, CAL_F004_10_LUDWIG_II).
- Excepciones EVIDENCIA_SEPARADA que NO son AJUSTADA: ['CAL_F003_08_LAW', 'CAL_F004_03_OPPENHEIMER', 'CAL_F004_10_LUDWIG_II'].

## Hallazgos por caso

- **CAL_F003_01_CARAVAGGIO**: grado FRAGIL (mezcla: H1_CON_COMPONENTES_DE_H2).
- **CAL_F003_04_FARADAY**: tortugas_ejecutado=False (no se ejecutó la prueba de tortugas en este caso).
- **CAL_F003_08_LAW**: tortugas_ejecutado=False (no se ejecutó la prueba de tortugas en este caso).
- **CAL_F004_04_MENDEL**: tortugas_ejecutado=False (no se ejecutó la prueba de tortugas en este caso).

## Nota de entrega
Los RESULT completos no se suben por el límite de 16 MiB del snapshot de push-files; se sube el resultado interpretable completo (salida_interpretable íntegra, sin recortes) + recibo + entrada, y el SHA-256 de cada RESULT completo queda en MANIFIESTO.json.

## Errata de auditoría — 2026-11-13

- **Grados:** el resumen inicial omitía tres casos FIRME. El recuento completo de `TABLA_VALORES_COMPLETA.md` es 1 FRAGIL, 16 AJUSTADA y 3 FIRME.
- **Monte Carlo:** la tabla interpretable presenta `status=None` y `total_simulations=None` en los 20 casos; sin embargo, los recibos de Caravaggio, Dickens y Oppenheimer contienen sección `monte_carlo` ejecutada. La tabla no refleja fielmente los recibos; no debe usarse para concluir que Monte Carlo no se ejecutó.
- **MANIFIESTO:** `H1_rank_fusion` aparece null en los 20 casos aunque la tabla interpretable sí contiene valores numéricos de `rank_fusion` para H1. La extracción de ese campo al manifiesto está incompleta.
- **LECTURA y candado:** `LECTURA.json` conserva los SHA-256 de las versiones de documentos leídas el 11-nov. Las versiones actuales de `casos/REGLAS.md`, `CONTRATO_CARPETAS.md` y `casos/fabrica/README.md` ya reflejan el acuerdo de guardar corridas completas en `motor/runs/`. El candado compara el SHA declarado contra el archivo actual (criterio D4), por lo que esta lectura histórica no pasará D4. No se reescribe el registro original ni se declara candado aprobado; haría falta una relectura posterior identificada como tal o una validación fijada a commit histórico.
- **Ejecución del candado:** no hay recibo de ejecución del candado para este paquete. La entrega no se considera validada por candado.
