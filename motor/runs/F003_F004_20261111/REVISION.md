# Revisión — corridas F003/F004 (2026-11-11)

Casos revisados: 20. Recibo COMPLETED en 20. Grados: 1 FRAGIL, 16 AJUSTADA.

## Hallazgos sistemáticos

- Recibo incompleto en los 20: `receipt_missing_paths` = `('$.stages[8].adaptador', '$.stages[8].verificacion_no_escribe_H')`.
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

## Corrección de lectura documental — 2026-11-13

Se releyeron individualmente los 20 archivos `*_RECIBO_EJECUCION.json` del lote (10 F003 y 10 F004). Los 20 conservan `status=COMPLETED`. En los 20, `stages[8]` es `consulta_dirigida` y contiene ambas claves `adaptador` y `verificacion_no_escribe_H`; ambas tienen el valor literal `DATO_AUSENTE_REQUIERE_CLASIFICACION`.

Por tanto, la frase anterior `receipt_missing_paths` no describe una ausencia estructural de esas claves: las rutas existen. El problema verificado es semántico y permanece abierto: ambos valores son marcadores de dato ausente que requieren clasificación; no demuestran que el adaptador esté configurado ni que la verificación de no escritura sobre H se haya realizado. No se infiere éxito de esos campos.

También se comprobó que `LECTURA.json` conserva las descripciones antiguas de `casos/REGLAS.md`, `CONTRATO_CARPETAS.md` y `casos/fabrica/README.md`. Esas descripciones ya no coinciden con el contenido actual; la evidencia de lectura está obsoleta y debe renovarse antes de ejecutar el candado. No se modificó `LECTURA.json`, no se ejecutó `scripts/candado_entrega.py`, no se ejecutaron tests ni se corrió el motor. El estado `NO_CALIBRADO` permanece.