# 2026-10-29 — ChatGPT — sidecar de arranque LLM

## Qué cambió
Se agregó un punto de entrada explícito para asistentes que trabajan con Motor U6. El sidecar reutiliza el contrato de ejecución y el CEB existentes; no crea otro recibo ni reemplaza piezas del motor.

## Antes → ahora (por archivo / función)
- `LLM_STARTUP_SIDECAR.md` — antes no existía un sidecar de arranque unificado → ahora contiene la secuencia de lectura, verificación de recibos, actuación ante `FALLO_EJECUCION`, preservación del campo completo y bloque de instrucciones persistentes.
  sha256 antes: N/A (archivo nuevo) | blob SHA después: `7b5aa55b83bc64f22cb00b908e42b993fab46a54`
- `INICIO_SESION_CHATGPT.md` — antes no existía una secuencia única de inicio → ahora contiene el orden obligatorio de lectura y el texto para instrucciones persistentes.
  sha256 antes: N/A (archivo nuevo) | blob SHA después: verificado por commit `f988141e41d6004e010712c49bcadaac0fae169a`; lectura de vuelta pendiente de registrar.
- `README.md` — antes enlazaba el contrato de ejecución, pero no el sidecar → ahora enlaza ambos puntos de entrada.
  blob SHA antes: `8091ec7c136709068643da12e267ad7e7256c6ca` | blob SHA después: `fa0c8b052d458a26d2debec98badb7576537b357`
- `INSTRUCCIONES_CONTINUIDAD_CHATGPT.md` — antes no referenciaba el punto de entrada → ahora lo exige al comienzo de cada tarea.
  blob SHA antes: `5e2a95178084831ecde9d95924189a09a1a1920e` | commit de cambio: `29637cd547ad703fd6f8f378b4cdb42d70680132`

## Hashes canónicos verificados (motor y catálogo)
No se modificaron ni recalcularon el motor canónico ni el catálogo de patrones en esta tarea.

## Pruebas
- Creación/actualización de documentación vía GitHub API: completada.
- Lectura de vuelta del sidecar: confirmada.
- Ejecución de motor o pruebas del motor: no aplican a estos cambios de documentación.
- Persistencia automática en las instrucciones internas de ChatGPT: no disponible mediante las herramientas de configuración conectadas; no se declara completada.
