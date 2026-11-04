# 2026-11-04 — ChatGPT — U6 unificado experimental

## Qué cambió
Se creó una ruta experimental ejecutable que activa el motor integrado V15.3 sin tocar Engine V5 ni el catálogo 244. Se añadieron smokes reales con búsqueda viva, persistencia aislada de CEB/StinkBox, tests de activación y workflow CI. Se corrigió una fila obsoleta del inventario estático de Caldero II.

Informe completo: `informes/2026-11-04_U6_UNIFICADO_EXPERIMENTAL.md`.

## Antes → ahora (por archivo / función)

- `motor/u6/U6_UNIFICADO_EXPERIMENTAL.py` — antes: no existía una entrada experimental que forzara ablations vacías, habilitara Familias Tokens y desactivara MODO_ESTRICTO para la prueba. → ahora: wrapper de ejecución del motor V15.3; activa las capas, ejecuta búsqueda viva, asigna stores temporales por caso y verifica el ledger CEB.
  - sha256 antes: AUSENTE | sha256 después: `d820d6cad7f9a3e57bdec7640194f136903cfb737ea7b6c249e462a8cfb80c5a`
  - commit de implementación y verificación CEB: `b2cbd858a4a19c24a8d0062985c203938ec69db8`

- `motor/tests/test_u6_unificado_experimental.py` — antes: AUSENTE. → ahora: dos pruebas para el modo de activación y la presencia de los artefactos canónicos.
  - sha256 antes: AUSENTE | sha256 después: `1271e610b40821d085ab7c60edb57afdefd79f5d4a9da5f87697a9ef7e41e8c0`
  - commit: `5d0eb2291ffe89b92137f0448e01454e2cfa08c7`

- `.github/workflows/u6-unificado-experimental.yml` — antes: AUSENTE. → ahora: workflow que ejecuta primero dos smokes con búsqueda viva y después la suite completa; publica evidencia, ledgers y stores.
  - sha256 antes: AUSENTE | sha256 después: `3771354f7d5e8f78ebafb1b4059982913c0e043b71aed35bc86205e1455e1633`
  - commit con paths de activación: `0a5f0931eff198ec99860acc4490a21c5b33cc6e`

- `motor/motor/INVENTARIO_COMPONENTES_UNICO.json` — antes: `caldero_run.py (Caldero II 2.0)` figuraba como NO_CORRE por requerir escaleta externa, en contradicción con la sustitución documentada por el puente circular Q1-Q4. → ahora: SUPERADA, con explicación de sustitución por `plugin_circulo_monomito_v2.py`.
  - sha256 antes: `8328b3e40dd184fe6b9b757579b24f869e056b819ce08a9a109d23693d310874` | sha256 después: `a91bb13cd45ab28a34f1a6b21d8719374ee6606debfa514491df3aadad4b4ac1`
  - commit: `ff75688236e3f5f11ae7f81ed79868c69fd9223b`

## Hashes canónicos verificados (motor y catálogo)
- Engine V5: `665c39a2861e58772522e91272563260d980908b1d4ab9f7092d3413d0c36082` — sin cambios.
- Catálogo 244: `d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1` — sin cambios.

## Pruebas: 159 passed, 2 skipped, 0 failed (¿pasaron? sí)

- Smoke Courbet: EXECUTION_CONFIRMED; búsqueda ddgs 8 resultados; 52/52 componentes del inventario presentes; 0 errores críticos; CEB 23,157 eventos.
- Smoke Haber: EXECUTION_CONFIRMED; búsqueda ddgs 8 resultados; 52/52 componentes del inventario presentes; 0 errores críticos; CEB 21,949 eventos.
- Total CEB: 45,106 eventos.
- Workflow Actions: run `41812300055`, SUCCESS.
- Artifact: `13313630201`, `U6_UNIFICADO_EXPERIMENTAL_EVIDENCIA`.

## Alcance de la conclusión
Se confirmó funcionamiento operacional en dos smokes y suite automatizada. No se midió acierto predictivo. Se mantienen identificados: 42 piezas ACTIVA_MUDA en estos casos, 9 patrones sin mapeo lateral, 2 módulos FUERA_DEL_MOTOR y 1 motor falso PROHIBIDA. La variante permanece en rama experimental; no se promueve a main.
