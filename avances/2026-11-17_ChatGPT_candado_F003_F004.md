# 2026-11-17 — ChatGPT

## Qué cambió

Se ejecutó el candado oficial de entrega de F003/F004 en GitHub Actions y se registró el resultado en la revisión del lote. El candado aprobó el paquete: 227 criterios pasados y cero incumplidos.

## Antes → ahora (por archivo / función)

- `.github/workflows/validate-f003-f004-candado.yml::validate` — antes el checkout dependía del SHA del PR temporal y apuntaba al repositorio/commit equivocado; ahora fija explícitamente `alterno/cameo-pesos`, donde reside el paquete que debe validarse. El workflow es de solo lectura y se activa ante cambios relevantes en el paquete o sus contratos.
  sha256 antes: `73e6edb659c95fdfbe6267d49eb9d9ca9e51da8389345fd5709da074d540f5d0` | sha256 después: `430c151ea5d99565456eeadfc52d4582023baedef54b0766c10a8466fdf495d3`
  Diff funcional: `ref: ${{ github.event.pull_request.head.sha || 'alterno/cameo-pesos' }}` → `ref: alterno/cameo-pesos`.

- `motor/runs/F003_F004_20261111/REVISION.md` — antes registraba la renovación documental pero no la ejecución del candado; ahora incluye run, job, comando, estado literal y conteo de criterios.
  sha256 antes: `529d8e6de875ad3005bbd4d6fc92d700955b7f2e0eeb0cb7b7c9b350b975c281` | sha256 después: `bde6cbbf7219e0bab65f0db4982d76122a83c00e88cad1f1dd6efe77d331d7b3`
  Commit de actualización: `9f8f13198c4a7b5436814c9280cda72f3fcbbbc7`.

- `scripts/candado_entrega.py::Candado.run` — sin cambios de código; ejecutado tal como está en el repositorio.

## Resultado de ejecución

- Workflow run: [44179107422](https://github.com/marcojpad-hash/motor-u6-storage/actions/runs/44179107422), run #5.
- Job: `validate`, ID `134378330680`.
- Python: 3.11.18.
- Comando: `python scripts/candado_entrega.py motor/runs/F003_F004_20261111 --repo .`.
- Salida: `CANDADO_ENTREGA: PASA`.
- Criterios: **227 pasados; 0 incumplidos**.
- El paquete F003/F004 cumple el contrato y puede conservarse en `motor/runs/F003_F004_20261111/`.

## Hashes canónicos verificados (motor y catálogo)

Engine V5 y catálogo 244 no se modificaron. Sus hashes no se recalcularon en esta intervención; no se presenta una nueva verificación de esos dos archivos.

## Pruebas: 0 passed, 0 skipped, 0 failed (¿pasaron? no aplica)

No se ejecutó una suite independiente de tests ni el motor. Los 227 criterios aprobados corresponden al candado oficial, no a tests predictivos. El estado `NO_CALIBRADO` permanece; no se recalificaron casos ni se convirtieron soportes estructurales en probabilidades.

## Limpieza de la prueba temporal

El PR temporal #15 se cerró sin merge. Su archivo marcador se retiró de la rama de prueba. El workflow de validación queda en `main` para futuras revisiones de cambios relevantes.
