# 2026-10-29 — ChatGPT — FeedMe actualizado y seguimiento

## Qué cambió
Se creó un punto de entrada único FeedMe y un espacio de seguimiento para dudas técnicas, bloqueos, decisiones del creador y resoluciones verificadas. Se enlazó desde README e instrucciones de continuidad.

## Antes → ahora (por archivo / función)
- `FEEDME_ACTUALIZADO.md` — antes no existía un índice único para arrancar y registrar dudas → ahora dirige al contrato, sidecar, CEB y carpetas de seguimiento.
  sha antes: N/A (archivo nuevo) | blob SHA después: verificado por lectura de vuelta.
- `seguimiento/dudas/README.md` — antes no existía carpeta de entrada para dudas técnicas → ahora define registro, comprobaciones previas y formato de cierre.
  sha antes: N/A (archivo nuevo) | commit: `4e5d2239ac36ac257d1c6b2c411bc2b082a599a3`
- `seguimiento/bloqueos/README.md` — antes no existía carpeta de bloqueos → ahora obliga a investigar causa raíz, reparar y volver a probar cuando sea posible.
  sha antes: N/A (archivo nuevo) | commit: `d83fa78ea477ca6c2a0db941775d1523b241658e`
- `seguimiento/decisiones/README.md` — antes no existía carpeta separada para decisiones del creador → ahora limita su uso a decisiones que no se pueden resolver con evidencia.
  sha antes: N/A (archivo nuevo) | commit: `26ece21040a995ca33fc7510704abbeeabed4269`
- `seguimiento/resueltos/README.md` — antes no existía carpeta para cierres verificados → ahora exige causa raíz, commit, prueba y evidencia.
  sha antes: N/A (archivo nuevo) | commit: `b5bcdc6f0acef950ffbe4cc07479fca98ae1865c`
- `README.md` — antes priorizaba el inicio de sesión y sidecar por separado → ahora declara FeedMe como punto de entrada principal.
  blob SHA antes: `fa0c8b052d458a26d2debec98badb7576537b357` | blob SHA después: `41a69936658eda91f5fa9ef5c5250afcd6786938`
- `INSTRUCCIONES_CONTINUIDAD_CHATGPT.md` — antes comenzaba por inicio de sesión → ahora exige FeedMe y revisión del seguimiento primero.
  blob SHA antes: `74eca36a687f22057977dcd350bae4c7acb5190b` | commit después: `50ac2217e98d95aa6e67deeb5900213e23280d37`

## Hashes canónicos verificados (motor y catálogo)
No se modificaron el motor canónico ni el catálogo 244.

## Pruebas
- Escritura por GitHub API: completada.
- Lectura de vuelta de FeedMe y carpeta de seguimiento: verificada.
- Pruebas del motor: no aplican; no se modificó código del motor.
- Notion: la creación del skill se rechazó porque el workspace alcanzó el límite de bloques del plan gratuito; no se creó contenido allí. La alternativa ejecutada es el FeedMe versionado en GitHub.
