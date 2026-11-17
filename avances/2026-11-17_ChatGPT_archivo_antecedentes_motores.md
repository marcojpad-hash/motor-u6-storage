# 2026-11-17 — ChatGPT: archivo de antecedentes de motores

## Qué cambió

Se creó `antecedentes_motor/` como archivo de consulta y se añadieron copias exactas de los tres componentes enumerados en el handoff de continuidad U6 del 2026-11-04. Los archivos fuente permanecen intactos.

## Antes → ahora (por archivo / función)

- `antecedentes_motor/Engine_V5_CANONICO_SOLO.py` — antes: copia no archivada en esta carpeta → ahora: copia idéntica del fuente `motor/motor/Engine_V5_CANONICO_SOLO.py`.
  blob SHA antes/fuente: `9f332bd799b3f32e5d16665d187c066e5b0311d3` | blob SHA después/copia: `9f332bd799b3f32e5d16665d187c066e5b0311d3`.
- `antecedentes_motor/MOTOR_V15_3_NATIVO_V0_9_UNICO.py` — antes: copia no archivada en esta carpeta → ahora: copia idéntica del fuente `motor/motor/MOTOR_V15_3_NATIVO_V0_9_UNICO.py`.
  blob SHA antes/fuente: `c0702138f51bef49348bc558b6c96b5bf0a6fce5` | blob SHA después/copia: `c0702138f51bef49348bc558b6c96b5bf0a6fce5`.
- `antecedentes_motor/MOTOR_V15_3_UNICO_20260927.py` — antes: copia no archivada en esta carpeta → ahora: copia idéntica del fuente `motor/motor/MOTOR_V15_3_UNICO_20260927.py`.
  blob SHA antes/fuente: `9aed52a83069447163969836f7c61666de1d5173` | blob SHA después/copia: `9aed52a83069447163969836f7c61666de1d5173`.
- `antecedentes_motor/README.md` — creado como índice, explica procedencia, uso histórico y autoridad.

## Hashes canónicos verificados (motor y catálogo)

- `ACTIVE_ENGINE_SELECTION.json` y `CANDADO_ENGINE.json` leídos: Engine V5 canónico SHA-256 `665c39a2861e58772522e91272563260d980908b1d4ab9f7092d3413d0c36082`.
- Catálogo canónico de 244 patrones: SHA-256 `d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1`.
- Los SHA anteriores proceden de los manifiestos/selección existentes; los SHA de blob Git consignados arriba verifican la identidad exacta de cada copia respecto a su fuente.
- No se modificó el motor canónico, el catálogo, la selección ni el candado.

## Pruebas

- Verificación de lectura posterior de los cuatro archivos archivados: PASS.
- Igualdad de blob SHA fuente/copia para los tres motores: PASS (3/3).
- Suite pytest / ejecución del motor: NO EJECUTADAS; esta tarea fue archivística y no altera código operativo.
