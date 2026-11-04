# 2026-11-04 — ChatGPT — Ablación ACTIVA_MUDA U6

## Entregables
- Runner: motor/u6/ABLACION_ACTIVA_MUDA_U6_20261104.py.
- Informe: informes/2026-11-04_ABLACION_ACTIVA_MUDA_U6.md.
- Duda: seguimiento/dudas/2026-11-04_duda_clasificacion_estados_activa_muda.md.
- Continuidad actualizada: docs/CONTINUIDAD_INVESTIGACION_U6_2026-11-04.md.

## SHA-256 antes → después
- Runner experimental: d820d6cad7f9a3e57bdec7640194f136903cfb737ea7b6c249e462a8cfb80c5a → da6f7d8edeb7a8f97bab9feee530ae0d3a3b6d64a467cdb7f62752109bc3ecd1.
- Script de ablación: AUSENTE → ab67d0c50dbdeb3d86de0d3464046ced75db070893e4bcd5d16b9b96e178e3b4.
- Workflow: 3771354f7d5e8f78ebafb1b4059982913c0e043b71aed35bc86205e1455e1633 → b1cdbe4b7b32ec3b3e8785daa71df82a5227fb86abe36858b974e7ec5f48919c.
- Test: 1271e610b40821d085ab7c60edb57afdefd79f5d4a9da5f87697a9ef7e41e8c0 → f12ad446ba7da454532688182d0dd5212e6415a1929bb11544641982ecdaa52c (comentario, sin cambio funcional).

## Resultados ejecutados
- Run matriz 41881474178: SUCCESS; artifact ID 13349688124.
- 41 ablaciones: 21 Courbet, 20 Haber; 41/41 switches confirmados; 0 errores críticos.
- H1/H2: 0 cambios. Orden de candidatas: 0 cambios. rank_fusion: 0 cambios; máxima variación 0.0.
- Suite: 159 passed, 2 skipped.
- Run posterior 41885012941: SUCCESS; dos smokes correctos; suite 159 passed, 2 skipped; matriz omitida por condición manual.

## Hallazgos
- Las 42 filas ACTIVA_MUDA por caso no son 42 módulos decisores: todas tienen can_decide_H=false; las 13 filas de origen motor declaran alimenta_predictor=false y alimenta_H=false.
- 39 targets corresponden a filas ACTIVA_MUDA con switch independiente (20 Courbet, 19 Haber). Dos controles adicionales de resolucion se probaron aparte porque el estado crudo RESUELTO_OPERACIONALMENTE cayó en ACTIVA_MUDA.
- Cuatro estados crudos están mal clasificados por el fallback: ABSORBIDO_EN_GUARDIA_TRANSVERSAL, NOT_APPLICABLE, PRESENTE y RESUELTO_OPERACIONALMENTE. Queda registrado; no se tocó el motor V15.3 protegido.
- Se verificaron 45 archivos StinkBox con 45 case_id únicos. Las rutas quedaron anidadas por acumulación de STINKBOX_STORAGE_ROOT, pero cada ejecución escribió su archivo propio; higiene de rutas pendiente.

## Integridad
- Engine V5 y catálogo 244 conservaron sus hashes canónicos.
- No se modificó Engine V5, motor V15.3 ni catálogo 244.
- La matriz mide cambios en las salidas de dos casos; no mide precisión ni generalización.
- Rama experimental; no se promovió a main.

## Evidencia
- https://github.com/marcojpad-hash/motor-u6-storage/actions/runs/41881474178
- https://github.com/marcojpad-hash/motor-u6-storage/actions/runs/41885012941
