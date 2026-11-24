# 2026-11-24 — ChatGPT: contexto enunciativo

## Qué cambió
Se clonó la capacidad de observación enunciativa en U6 sin retirar la implementación del motor y se conectó al paquete de guardianes posterior al predictor.

## Antes → ahora (por archivo / función)
- `motor/motor/lateral_contexto_enunciativo_v1.py` — antes no existía → ahora contiene la copia funcional adaptada del lateral agnóstico.
  sha256 antes: N/A | sha256 después: se registra en manifiesto regenerado por CI.
- `motor/motor/guardianes_control_v1.py::correr_guardianes` — antes no invocaba el lateral → ahora añade `CONTEXTO_ENUNCIATIVO` y adjunta referencias contextuales a guardianes hermanos sin modificar sus banderas.
  sha256 antes: consultar base `alterno/cameo-pesos` | sha256 después: se registra en manifiesto regenerado por CI.
- `motor/tests/test_runner_json_contract.py` — antes no tenía casos del lateral → ahora incluye CTX-01 (carga reiterada/asimetría/enunciador) y CTX-02 (input neutro).
  sha256 antes: consultar base `alterno/cameo-pesos` | sha256 después: se registra en manifiesto regenerado por CI.
- `motor/LATERAL_CONTEXTO_ENUNCIATIVO_V1.md` — antes no existía → ahora documenta contrato y cableado.

## Hashes canónicos verificados (motor y catálogo)
No se modificaron Engine V5 canónico ni patterns_final_v14.json. Sus hashes de referencia permanecen: Engine `665c39a2861e58772522e91272563260d980908b1d4ab9f7092d3413d0c36082`; catálogo `d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1`. La corrida CI regenerará manifiestos para comprobar el estado real.

## Pruebas: 2 casos de integración añadidos; ejecución CI pendiente de resultado observable.
