# 2026-11-21 — ChatGPT

## Qué cambió
Se reconciliaron dos instrucciones operativas obsoletas con el estado verificado de la compuerta biográfica Z90. La compuerta de fábrica ya calcula Z90 desde nacimiento/muerte y valida ventanas acumulativas, cierres y evidencia por corte; la integración en el runner estándar sigue pendiente en PR #8, OPEN/NOT MERGED. No se ejecutó el motor ni se habilitó F007.

## Antes → ahora (por archivo / función)
- `INSTRUCCIONES_CONTINUIDAD_CHATGPT.md` — antes decía que la gate no calculaba Z90; ahora distingue la gate implementada de la integración pendiente en `motor/correr_estandar.py`.
  sha256 antes: 22c07ea2a7691e2695959b76d0adb7a8b8e554b6f53e2f273d3e1140d173c9a2 | sha256 después: 4623c16557d297917def335b09cb949580dc40d7814c13eea37662b315a3fdd5
- `motor/CONTRATO_ENTRADA_LLM.txt` — antes decía que la gate no validaba nacimiento/muerte ni ventanas; ahora registra el cálculo implementado, el límite de `_validate_case` y el estado de PR #8.
  sha256 antes: 12704aa096b0066362fd440aff461044289428881df4a88ddcd909e5275bad1c | sha256 después: f46e8e3b70f701cb977dd79bcf3c056d7a05a03d610b2e38da4561a9b97754cd

## Hashes canónicos verificados (motor y catálogo)
- `motor/Engine_V5_CANONICO_SOLO.py`: `665c39a2861e58772522e91272563260d980908b1d4ab9f7092d3413d0c36082` (manifiesto `motor/SHA256SUMS_MOTOR.txt`).
- `motor/patterns_final_v14.json`: `d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1` (mismo manifiesto).
- Ambos archivos permanecieron sin cambios; no se recalcularon ni modificaron.

## Pruebas: 53 passed, 0 skipped, 0 failed (¿pasaron? sí)
CI de código verificado antes de esta actualización documental: run [#44965583777](https://github.com/marcojpad-hash/motor-u6-storage/actions/runs/44965583777), commit `9a5297ba11729d654ee3f3e54de7a85318a0c991`; log: `53 passed in 0.29s`. Esta actualización solo cambia documentación; no se ejecutaron pruebas nuevas.

## Estado de ejecución
- F007 revalidado: ocho sujetos, dos cortes por sujeto, fuentes secundarias Wikipedia, sin campos biográficos completos ni custodia independiente acreditada.
- `preparar_z` sigue importando semillas y destinos en el mismo proceso; no se ejecutó.
- No se abrieron destinos ni custodias, no se reejecutaron C01–C20, no se incrementó n y no se modificó `main`, motores canónicos, patrones, pesos, candados ni evidencia congelada.
- PR #8 permanece OPEN / NOT MERGED. La ruta estándar sigue sin invocar la gate completa.
