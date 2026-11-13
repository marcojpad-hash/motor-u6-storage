# 2026-11-13 — ChatGPT

## Qué cambió

Se normalizó la documentación de almacenamiento de corridas en la rama vigente `alterno/cameo-pesos` y se corrigió la lectura del lote F003/F004 del 11-nov. Solo se editaron documentos; no se modificó código, motor, patrones, candados, recibos ni manifiestos.

## Antes → ahora (por archivo / función)

- `CONTRATO_GUARDAR_CORRIDAS.md` — antes §6 afirmaba que tres documentos subordinados aún prohibían guardar corridas completas y el ejemplo de `LECTURA.json` reproducía esas reglas antiguas → ahora §5 refleja las reglas actuales y §6 registra que la reconciliación documental quedó completada el 2026-11-13; también advierte que la evidencia LECTURA del lote F003/F004 está obsoleta.
  sha256 antes: 70853606ff0949eef229aa05027c9fa3b28b8ed9278fba42673cf024b1c1e4f0 | sha256 después: 9a65ef8252337bcf953e6c43aabe4c966f769e049cfcc326c51793e205906403
  commit: c0a6980c5505846dc7d14e325d935e05b9c3cb83

- `motor/runs/F003_F004_20261111/README.md` — antes clasificaba el lote como excepción y decía que los tres documentos seguían pendientes → ahora confirma que la política está normalizada y que este lote no es una excepción; señala la obsolescencia de LECTURA.
  sha256 antes: 1f0f08ea6b6f9a489ee55aa93a72fcf20a9ceeaea8e98006805d303f95c01528 | sha256 después: 20a398f20c6b1a0c0dc5da9f1d21d3574dffdefc0074d64c91fa3462455dbca1
  commit: e4e37c412c9b2c6a52f6f3488d15c14b731462c7

- `motor/runs/F003_F004_20261111/REVISION.md` — antes reportaba `receipt_missing_paths` como si faltaran dos claves → ahora añade corrección fechada: las dos claves existen en los 20 recibos, pero conservan el sentinel `DATO_AUSENTE_REQUIERE_CLASIFICACION`; el problema es semántico, no ausencia estructural.
  sha256 antes: 3792853c449f01e68254b2544f4a78a3ca32d6084f13f7b2adf6cb1a9cf05397 | sha256 después: 2cf68fc0d9cfa4d352edaa3e54f2d5cfae08ec16230a101592e4c9657acbc308
  commit: 85971f5d904819f08cd9219cfd239ad7aada1129

## Hallazgos verificados

- 20/20 recibos F003/F004: `status=COMPLETED`.
- 20/20 recibos: `stages[8]` = `consulta_dirigida`; `adaptador` y `verificacion_no_escribe_H` existen, ambos con valor `DATO_AUSENTE_REQUIERE_CLASIFICACION`. No prueban adaptador configurado ni verificación no-escritura ejecutada.
- `LECTURA.json`: SHA-256 actual frente al registrado:
  - `casos/REGLAS.md`: actual `7fed14c9baf0c32eec4298842790718e352fc4d732cdf715f1e661844fd5c08a`; registrado `9c2dec25ead4bdce43eecd7f2f7a576563a2f826e98d297706997195ca96167b` — no coincide.
  - `CONTRATO_CARPETAS.md`: actual `0af0f7622cb74e2e9d151f67a8f8d0f24924593b7a2254281c33b8f2d987fd4f`; registrado `8e5c4b164e4d869539ead0d58eeb5417227af6826a530cdad98970cefa18f506` — no coincide.
  - `casos/fabrica/README.md`: actual `9dc1bf344fc0c04eb663fc21e4e38fc7127d9dc8f925567eb2e66ef8aeecc61d`; registrado `9cc7ab20a350abddd03e93ae307119f84c0aae66a90360f3788e2ff8c428ca70` — no coincide.
- La evidencia `LECTURA.json` debe renovarse por el procedimiento de entrega/candado autorizado. No se alteró para evitar simular una lectura contemporánea de la entrega original.

## Hashes canónicos observados (no recalculados en esta revisión)

- Engine: `665c39a2861e58772522e91272563260d980908b1d4ab9f7092d3413d0c36082`.
- Catálogo 244: `d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1`.

## Pruebas: 0 passed, 0 skipped, 0 failed (¿pasaron? no: no se ejecutaron)

No se ejecutaron tests, `scripts/candado_entrega.py`, ni el motor. Revisión documental y lectura de archivos únicamente. El estado de calibración sigue `NO_CALIBRADO`.
