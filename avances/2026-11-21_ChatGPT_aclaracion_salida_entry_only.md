# 2026-11-21 — ChatGPT

## Qué cambió
Se eliminó una afirmación engañosa en el README de la fábrica: antes sugería que lo único no automatizado era redactar semillas; ahora deja claro que tampoco existe una ruta entry-only segura para materializar entradas sin cargar destinos.

## Antes → ahora (por archivo / función)
- `casos/fabrica/README.md` — el preparador solo redacta/verifica semillas; no debe materializar `entrada.json` con `preparar` o `preparar-z`, ni ejecutar `correr`. La custodia y ejecución siguen separadas.
  sha256 antes: 3bd25f86c9a78dd15be895c53b3b68b85b835a185b178d29a3354e04d83c2c06 | sha256 después: bc67dbeb75ddb3355625dec9c832cb06373caf7b3598ff6c85df271d4f338ff1

## Hashes canónicos verificados (motor y catálogo)
- `motor/Engine_V5_CANONICO_SOLO.py`: `665c39a2861e58772522e91272563260d980908b1d4ab9f7092d3413d0c36082`.
- `motor/patterns_final_v14.json`: `d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1`.
- Fuente: `motor/SHA256SUMS_MOTOR.txt`. No se modificaron.

## Pruebas: 53 passed, 0 skipped, 0 failed (¿pasaron? sí)
Último CI de contratos verificado: run [#44967844378](https://github.com/marcojpad-hash/motor-u6-storage/actions/runs/44967844378), 53 passed in 0.33s. Este cambio es documental; no se ejecutó el motor ni se abrieron custodias.

## Estado
No se implementó ruta entry-only. F007 sigue rechazado por fuentes secundarias y falta de campos Z90/custodia independiente. No se ejecutó `preparar`, `preparar-z` ni `correr`; no se modificó main, motor canónico, patrones, pesos ni candados.
