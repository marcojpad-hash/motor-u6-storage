# Avance — POE-U6 provisional v0.1 (2026-11-03)

## Antes
- Había una auditoría retrospectiva de cinco componentes con evidencia incompleta de ablación causal.
- El diseño de la Brújula de obligación de búsqueda no estaba implementado como controlador general.
- No había un contrato único que fijara el orden de guardianes, resolución adaptativa, compuerta y persistencia para comparaciones ON/OFF.

## Después
- Se creó `docs/PROTOCOLO_ORQUESTACION_EPISTEMICA_PROVISIONAL_V0_1.md`.
- Se creó `tests/test_orquestacion_epistemica_provisional.py`, modelo de referencia aislado.
- Se creó `informes/2026-11-03_PRUEBAS_PROTOCOLO_ORQUESTACION_EPISTEMICA.md`.
- Se ejecutó la suite con Python 3.13.5: 14 passed, 0 failed.
- Las pruebas cubren E1–E5 y C1–C3 en fixtures sintéticos.
- La compuerta queda formalmente después de guardianes y remediciones.
- Guardianes y memoria quedan restringidos a roles no decisores.
- El resolutor adaptativo queda acotado por presupuesto, criterio de progreso y parada.

## Hashes locales de artefactos de protocolo
- Protocolo: SHA-256 `c7d0b88e2c0773a80f0e4582fbb4b56f6430c9f6c249fc8ef7c03bfd9ac755ca`.
- Pruebas: SHA-256 `39c24b4e19dfc2a5504ff4ed04594eda3e47c59f181f1eed4fbe8adfb9e878b9`.

## Alcance de ejecución
Estas 14 pruebas verifican un modelo de referencia del protocolo. No ejecutan Engine V5/V15.3 ni los guardianes reales. No son evidencia de mejora predictiva, tasa real de falsos positivos ni generalización entre LLM. Las cinco ablaciones reales siguen pendientes de casos nuevos, entradas congeladas y desenlaces sellados.

## Integridad
- No se modificó `motor/Engine_V5_CANONICO_SOLO.py`.
- No se modificó `motor/patterns_final_v14.json`.
- El trabajo se guardó en rama experimental `experiment/protocolo-orquestacion-epistemica-v0.1`, no en main.
- Commit inicial de la rama basado en main; commits de artefactos: `62b713afb40062e81b3bc85af997c4449848a638`, `cf50c5f86aee64bc170fa71e436b3f51e42513c4`, `6adf672cb6938e50ef2c5c48ef57d9459a0cda56`. Este avance documenta los artefactos; el commit que lo contiene se añade al final.
