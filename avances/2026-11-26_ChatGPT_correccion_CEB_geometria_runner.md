# 2026-11-26 — ChatGPT — corrección de trazabilidad CEB y runner exploratorio

## Qué cambió

Se corrigió una discrepancia observada en dos corridas reales de Motor U7: geometría multicapa declaraba ejecución y producía salida, pero no tenía una etapa registrada en el ledger CEB. También se corrigió el selector de entrada del workflow para que procese el JSON realmente modificado, y se amplió la evidencia preservada por el artefacto.

## Antes → ahora (por archivo / función)

- `motor/motor/MOTOR_V15_3_UNICO_20260927.py` — antes: `_run_geometria_multicapa_working(result, case)` se invocaba directamente y quedaba fuera de `FlowTracer`; ahora: se ejecuta mediante `_ceb_stage("geometria_multicapa_integrada_working_v1", ...)`, registrando inicio, salida y fin de la etapa.
  - Git blob SHA antes: `2c7d7f9b964264c5bdfd0c632ca43340803185c8`
  - Git blob SHA después: `e80e14bf709bddb3ce2d93b68508f43c077dcc1b`
  - Commit: `1969b4e873b3d9cf2ccbca0404184a8edb794f2a`

- `.github/workflows/ejecutar-caso-exploratorio-u7.yml` — antes: el evento push elegía el último archivo por orden alfabético entre todos los casos `ZZZ_z_RETRY_*.json`; ahora: obtiene los JSON modificados entre `GITHUB_EVENT_BEFORE` y `GITHUB_SHA` y exige exactamente uno. Antes: no preservaba el ledger CEB ni regeneraba los manifiestos; ahora: copia el ledger CEB y los tres manifiestos al artefacto, regenera los manifiestos y persiste los cambios en la rama operativa.
  - Git blob SHA antes: `d981713a96222b9b1332fe58fb623bfcb1eef71c`
  - Git blob SHA después: `1bacbb626628e6108dea4f54204b91b5fc2b4cf1`
  - Commit de configuración final: `4f7ec97dd45edb0cb379842f2a35bacbfc02619d`

## Hashes canónicos verificados

- Engine V5: `665c39a2861e58772522e91272563260d980908b1d4ab9f7092d3413d0c36082`
- Catálogo 244: `d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1`
- Ambos coincidieron en las dos corridas originales; no se modificaron.

## Pruebas

- Evidencia de partida: Demis Hassabis, run `45864696050`; Fei-Fei Li, run `45864948542`. En ambas, `geometria_multicapa.status=EXECUTED`, pero `ceb.status=INCOMPLETE` con `REPORTED_EXECUTED_NOT_OBSERVED` para `geometria_multicapa_integrada_working_v1`.
- Reproducción técnica preparada y subida: `ZZZ_z_RETRY_CEB_REPLAY_DEMIS_V2_20261126`, commit `ef0e1aefdf786daeb25b6fb46295024f3c07e714`. Se reutilizan los mismos cortes congelados solo como regresión técnica; no es un caso ciego ni cuenta para calibración.
- Suite: no hay resultado de Actions verificable disponible en esta sesión para el commit de replay. La corrección de código está subida; la verificación de la nueva etapa CEB queda sin confirmar hasta leer el artefacto de esa corrida.
