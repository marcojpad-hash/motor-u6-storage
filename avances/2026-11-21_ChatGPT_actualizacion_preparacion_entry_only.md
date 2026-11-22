# 2026-11-21 — ChatGPT

## Qué cambió
Se corrigieron instrucciones contradictorias que todavía sugerían ejecutar la fábrica desde el preparador y que afirmaban que la gate Z90 no calculaba nacimiento/muerte. Se separó explícitamente el estado de la gate implementada del cableado pendiente en el runner estándar. No se creó una ruta entry-only ni se ejecutó la fábrica.

## Antes → ahora (por archivo / función)
- `casos/fabrica/README.md`: antes sugería `fabrica.py preparar` y `preparar-z` como pasos de preparación; ahora advierte que `preparar` escribe desenlace desde familias embebidas y que `preparar-z` carga semillas y destinos en el mismo proceso. El preparador solo entrega semillas.
  sha256 antes: 69715cbb0ca9ae531f17595a883c1306719db8bad15ac1a24256e4d2405c680c | sha256 después: 3bd25f86c9a78dd15be895c53b3b68b85b835a185b178d29a3354e04d83c2c06
- `casos/fabrica/PROMPT_SEMILLAS_Z.md`: antes permitía ejecutar `preparar-z` en un entorno controlado y decía que la gate no calculaba Z90; ahora prohíbe ejecutarlo desde el preparador y describe la gate implementada y el cableado pendiente.
  sha256 antes: 0395820c319df503728b93ca1723a37bd5cbff6bb865f549b3103da581049b06 | sha256 después: 96c11ee018b149c46e740db94dd876d54dd8eaff18cc98a97d376df5cf3ee91b
- `DELEGACIONES.md`: se sustituyeron los estados obsoletos de Z90 y se registró PR #8 como OPEN, `mergeable=false`, `mergeable_state=dirty`; head `5eda368d85851a42f6f82f069c56c93983c60da2`, base `be98ec8645364b1330104de996fbd6339033547c`. El PR contiene el guardián en su rama, pero el runner de la rama activa aún no lo invoca.
  sha256 antes: 04841d3035b5661db7ef040ea64dab8f9b051b17a0f4b110daceb45195a20d76 | sha256 después: a1c39f45da77dac292307b8c32251018df14fff40ed6d4254d99bcb5d036a285

## Hashes canónicos verificados (motor y catálogo)
- `motor/Engine_V5_CANONICO_SOLO.py`: `665c39a2861e58772522e91272563260d980908b1d4ab9f7092d3413d0c36082`.
- `motor/patterns_final_v14.json`: `d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1`.
- Fuente: `motor/SHA256SUMS_MOTOR.txt`. Ambos permanecieron sin cambios.

## Pruebas: 53 passed, 0 skipped, 0 failed (¿pasaron? sí)
Run CI [#44967844378](https://github.com/marcojpad-hash/motor-u6-storage/actions/runs/44967844378), commit probado `16db5d6701dd1484b6003557a4c248d1ffc58916`, verificó 53 pruebas y regeneró manifiestos en modo read-only. Ese run precede a las tres actualizaciones documentales de este registro; no se ejecutaron pruebas de motor en esta actualización. Los commits de documentación posteriores son `55a7122`, `fd86efa` y `019bdce`.

## Estado de preparación
- F007 revalidado: 8 sujetos, 2 cortes por sujeto, fuentes Wikipedia secundarias; el seed no incluye `fecha_nacimiento`, `fecha_muerte` ni `z90_date` completos. Los nombres de roles en `preparacion_ciega` no acreditan custodios/conversaciones independientes reales.
- `fabrica.py preparar-z` importa `SEMILLAS_Z` y `DESTINOS` en el mismo proceso y escribe entrada, desenlace y destino. `fabrica.py preparar` es legado y también escribe desenlace desde familias embebidas. No se ejecutó ninguno.
- La gate `motor/calibracion/gate_z90.py` implementa Z90 y valida fechas/ventanas/evidencia. La integración estándar sigue pendiente en PR #8, cuyo estado es dirty; la rama activa no contiene el guardián.
- No se abrieron destinos ni custodias, no se reejecutaron C01–C20, no se incrementó n, no se ejecutó el motor y no se modificaron `main`, motores canónicos, patrones, pesos, candados ni evidencia congelada.
