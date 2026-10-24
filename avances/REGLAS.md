# Reglas de `avances/`

Un archivo por entrada: `AAAA-MM-DD_<modelo>_<tema>.md`. Nunca se edita una entrada vieja; las correcciones son entradas nuevas.

Formato obligatorio:

```
# <fecha AAAA-MM-DD> — <modelo: Claude | ChatGPT | Grok Bot>
## Qué cambió
## Antes → ahora (por archivo / función)
- archivo::función — antes estaba así: … → ahora quedó así: …
  sha256 antes: … | sha256 después: …
  (diff legible, solo de lo modificado)
## Hashes canónicos verificados (motor y catálogo)
## Pruebas: N passed, N skipped, N failed (¿pasaron? sí/no)
```

Solo se documentan y suben versiones modificadas. No se pegan salidas completas de corridas; se citan por hash.
