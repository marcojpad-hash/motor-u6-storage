# U6 unificado experimental — ejecución y pruebas

**Fecha:** 2026-11-04  
**Repositorio:** marcojpad-hash/motor-u6-storage  
**Rama:** experimental/u6-unificado-activo-20261104  
**Base main:** 33a163f8d4664a0e99dbe5c8d7c122eea34f3962  
**Commit de ejecución:** b2cbd858a4a19c24a8d0062985c203938ec69db8  
**Workflow:** U6 unificado experimental — smoke y suite completa  
**Run:** 41812300055 — SUCCESS  
**Evidencia:** artifact U6_UNIFICADO_EXPERIMENTAL_EVIDENCIA, artifact ID 13313630201.

## 1. Qué se construyó

Se añadió `motor/u6/U6_UNIFICADO_EXPERIMENTAL.py`, una capa ejecutable experimental sobre el motor integrado V15.3 existente. No reemplaza el motor canónico: activa el camino integrado y elimina las ablaciones configuradas para una corrida, con registro de componentes, búsqueda viva, CEB y StinkBox aislados por caso.

Modo de activación:
- `CONSOLIDADO_OFF=""`: sin ablaciones heredadas.
- `FAMILIAS_TOKENS=1`.
- `MODO_ESTRICTO=0`: se desactiva el modo estricto de cierre en esta variante.
- Flags `LAT_*` existentes se fuerzan a `1`; en estos runners no había flags `LAT_*` externos preexistentes.
- Caldero ejecuta búsqueda viva con proveedor automático.
- StinkBox, CEB y neighbor store quedan aislados en directorios temporales por caso.

Los módulos conservan su rol declarado: los votos y señales laterales alimentan las etapas previstas; sensores, trazabilidad y auditoría no se convierten artificialmente en escritores de H. Se habilita la ejecución, no se cambia sin fundamento la semántica de cada módulo.

## 2. Smoke tests

Ambos smokes se ejecutaron con búsqueda externa real, no fixture estático ni modo offline.

| Caso | Estado | Búsqueda | Candidatas | H1 | H2 |
|---|---|---:|---:|---|---|
| Courbet | EXECUTION_CONFIRMED | ddgs: 8 resultados | 7 | 30_ambicion | 20_sacrificio_por_un_ideal |
| Haber | EXECUTION_CONFIRMED | ddgs: 8 resultados | 8 | 30_ambicion | schwartz_07_logro |

En ambos:
- Catálogo de 244 patrones: `CANONICAL_VERIFIED`.
- Inventario de componentes: 52/52 presentes.
- Errores críticos: 0.
- Componentes por estado de ejecución: 51 `EXECUTED`, 4 `EXECUTED_SIN_SENAL`, 1 `ABSORBIDO_EN_GUARDIA_TRANSVERSAL`, 1 `EXECUTED_SIN_HALLAZGOS`, 1 `SUPERADA`, 1 `SIN_PREFIJO_EN_INPUT`, 3 `HUB_ACTIVA_MUDA`, 3 `HUB_ACTIVA`, 1 `NOT_APPLICABLE`, 1 `EXECUTED_DIAGNOSTIC`, 1 `PRESENTE`, 1 `RESUELTO_OPERACIONALMENTE`, 1 `EXECUTED_WITH_CONCLUSION`.
- Registro de componentes: 76 `ACTIVA`, 42 `ACTIVA_MUDA`, 12 `SUPERADA`, 1 `MARCAJE`, 1 `GUARDIAN_FILTRO`, 2 `FUERA_DEL_MOTOR`, 1 `PROHIBIDA`. No quedó ningún `NO_CORRE` ni `APAGADA_POR_FLAG`.

`ACTIVA_MUDA` significa que la pieza fue ejecutada pero no produjo señal útil en ese caso; no significa que no esté cableada. `SUPERADA` significa que la función fue sustituida por una versión posterior. `FUERA_DEL_MOTOR` y `PROHIBIDA` se mantienen como estados de inventario, no se declaran ejecutadas.

## 3. CEB y trazabilidad

El CEB escribió ledger real por caso:
- Courbet: 23,157 eventos.
- Haber: 21,949 eventos.
- Total: 45,106 eventos CEB.

Rutas de los ledgers en el runner:
- `/tmp/u6_unificado_ceb/CAL_F005_01_COURBET_U6EXP1/CAL_F005_01_COURBET_U6EXP1.flow_ledger.jsonl`
- `/tmp/u6_unificado_ceb/CAL_F005_02_HABER_U6EXP1/CAL_F005_02_HABER_U6EXP1.flow_ledger.jsonl`

StinkBox y los neighbor stores también se aislaron por caso. La evidencia completa fue subida al artifact de Actions (2 casos, ledgers y stores).

## 4. Corrección de inventario

La primera integración detectó una contradicción: el inventario estático marcaba `caldero_run.py (Caldero II 2.0)` como `NO_CORRE`, mientras el hub lateral ya documentaba que la escaleta lineal fue sustituida por `plugin_circulo_monomito_v2.py` (Caldero II circular Q1-Q4). Se corrigió el estado a `SUPERADA`, dejando explícita la sustitución. El runner CLI `caldero_II_runner_generico.py` se conserva como utilidad independiente; no es dependencia obligatoria de cada corrida general.

## 5. Cobertura y pendientes reales

La validación del catálogo quedó en estado `OK`, sin marcas duras. No obstante:
- 235 de 244 patrones tienen mapeo en el puente lateral; 9 no tienen token lateral asociado.
- El registro de semillas Capa 2 cita 16 tokens que no existen en el catálogo canónico; se conservan como vocabulario de registro, no se insertan en los 244.
- Dynamis utiliza 11 tokens laterales propios fuera del catálogo, por diseño.
- 42 componentes aparecen como `ACTIVA_MUDA` en estos dos casos. Hay que estudiar cuáles son sensores condicionales y cuáles deberían producir una señal para estos inputs; no convertir ausencia de señal en fallo de cableado.
- Dos elementos siguen `FUERA_DEL_MOTOR`: una herramienta específica de predictibilidad semántica y el laboratorio Sofista/red-team. El motor falso permanece `PROHIBIDA`; no se carga ni se ejecuta.
- H1 fue `30_ambicion` en ambos casos. Esto merece una prueba de concentración/ablación con casos independientes; no demuestra por sí solo sesgo ni acierto.

## 6. Suite

Orden ejecutado:
1. Smoke Courbet.
2. Smoke Haber.
3. Suite completa.

Resultado de CI: **159 passed, 2 skipped**. Workflow completo: SUCCESS.

## 7. Integridad del canon

No se modificaron Engine V5 ni el catálogo:
- Engine V5: SHA-256 `665c39a2861e58772522e91272563260d980908b1d4ab9f7092d3413d0c36082`.
- Catálogo 244: SHA-256 `d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1`.

## 8. Conclusión

La integración experimental **sí arranca, ejecuta el núcleo y las capas laterales, hace búsqueda viva, conserva trazabilidad CEB/StinkBox y produce H/candidatas en los dos smokes**. La suite automatizada pasa.

Esto acredita funcionamiento operacional de esta ruta en dos casos. No acredita todavía precisión predictiva, generalización, ni que cada sensor aporte señal en cualquier caso. La siguiente prueba útil es una matriz emparejada de ablación y cobertura para las 42 piezas `ACTIVA_MUDA`, los 9 patrones sin puente lateral y los dos módulos fuera del motor.

No promover a `main` ni sustituir el motor canónico con esta versión hasta terminar esa validación.
