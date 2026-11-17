# 2026-11-17 — ChatGPT

## Qué cambió

Se renovó la evidencia de lectura del paquete F003/F004 porque `LECTURA.json` conservaba SHA-256 y descripciones de versiones documentales anteriores. Se agregó una nota en `REVISION.md` que cita los cuatro documentos y distingue renovación documental de ejecución del candado.

## Antes → ahora (por archivo / función)

- `motor/runs/F003_F004_20261111/LECTURA.json` — antes estaba así: fecha 2026-11-11 y hashes antiguos para `casos/REGLAS.md`, `CONTRATO_CARPETAS.md` y `casos/fabrica/README.md`; ahora quedó así: fecha 2026-11-17, cuatro rutas citadas y SHA-256 del contenido vigente leído.
  sha256 antes: `9bccfed67bf7dc7a30e13f46edaee01f3b8cd72ca29d4bd9fe21c1b0ffb2acb5` | sha256 después: `fe396795156cdee6aaa80582f31ef49ddb5cbd0c01eddbc946b43abba885acc4`
  Commit: `f97e06ac32ae4b77c47e697c11ee829c56dc0160`.
- `motor/runs/F003_F004_20261111/REVISION.md` — antes estaba así: registraba que la evidencia de lectura seguía obsoleta; ahora quedó así: documenta la renovación de los cuatro archivos y mantiene explícito que el candado no se ejecutó y que U6 sigue NO_CALIBRADO.
  sha256 antes: `2cf68fc0d9cfa4d352edaa3e54f2d5cfae08ec16230a101592e4c9657acbc308` | sha256 después: `529d8e6de875ad3005bbd4d6fc92d700955b7f2e0eeb0cb7b7c9b350b975c281`
  Commit: `380eaef52cafe75ba2b14f059276872f41a13c87`.

## Hashes canónicos (sin modificación)

No se modificaron. Referencias declaradas por `motor/REGLAS.md`: Engine V5 `665c39a2861e58772522e91272563260d980908b1d4ab9f7092d3413d0c36082`; catálogo 244 `d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1`. No se recalcularon en esta intervención.

## Pruebas: no ejecutadas (0 passed, 0 skipped, 0 failed)

- Lectura y comprobación de vuelta de `LECTURA.json` y `REVISION.md`: verificada por GitHub.
- SHA-256 de los cuatro documentos de protocolo: recalculados sobre el contenido recuperado y registrados en `LECTURA.json`.
- `scripts/candado_entrega.py`: NO EJECUTADO; no hay runtime local del repositorio disponible en esta sesión.
- Motor U6 y tests: no ejecutados. No se cambió el estado predictivo NO_CALIBRADO.
