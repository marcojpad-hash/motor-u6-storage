# 2026-11-24 — ChatGPT: corrección de polaridad no clasificada

## Qué cambió
Se corrigió un KeyError potencial en el lateral observacional de contexto enunciativo U6. Cuando una oración contiene un juicio lingüístico (por ejemplo, normativo o predictivo) sin vocabulario positivo/negativo, `_polarity()` devuelve `NO_CLASIFICADA`; el contador por actor no tenía esa clave y fallaba al incrementarla.

La categoría ahora existe explícitamente en el contador y conserva su recuento como observación. El total usado para detectar carga valorativa sigue sumando únicamente POSITIVA, NEGATIVA y MIXTA; por tanto, NO_CLASIFICADA no se convierte en señal valorativa ni altera decisiones.

## Antes → ahora (por archivo / función)
- `motor/motor/lateral_contexto_enunciativo_v1.py::analyze` — antes el contador solo tenía POSITIVA/NEGATIVA/MIXTA y podía lanzar `KeyError: 'NO_CLASIFICADA'`; ahora inicializa también NO_CLASIFICADA y conserva ese recuento fuera del total valorativo.
  sha256 antes: `533118199d86af887a07b53867012d4856bfd3ceedeff0827681b0b3406f3118` | sha256 después: `e778adefdc0859f037d9092c6933b1a24a10072335bd0386882bad2ca104552e`
- `motor/tests/test_runner_json_contract.py` — antes no cubría la polaridad NO_CLASIFICADA; ahora añade regresiones para las cuatro categorías (POSITIVA, NEGATIVA, MIXTA, NO_CLASIFICADA), preservación del conteo neutral, ausencia de falsa señal valorativa y entradas vacías/blancas.
  sha256 antes: `3182b0440ef48791efecc5ee557e9759dd434d20e778f587dd2ecdbb17da1f04` | sha256 después: `0b466511579ed89702580417f7ffd3ed6e31dac8deac500c3fc5487d5a1662af`

## Hashes canónicos verificados (motor y catálogo)
Engine V5 canónico y catálogo 244 no forman parte del diff del PR; no se escribieron ni actualizaron. La lista de archivos modificados del PR no incluye ninguno de los dos. Hashes de referencia del contrato: Engine `665c39a2861e58772522e91272563260d980908b1d4ab9f7092d3413d0c36082`; catálogo `d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1`.

## Pruebas: 0 passed, 0 skipped, 0 failed (no ejecutadas)
Se añadieron dos pruebas de regresión, pero esta sesión no dispone de ejecución Python sobre el checkout. El commit no tiene workflow ni status check asociado visible al momento de registrar esta entrada. Estado: código modificado y releído desde GitHub; prueba automatizada pendiente. No se ejecutó el motor ni ningún lote.
