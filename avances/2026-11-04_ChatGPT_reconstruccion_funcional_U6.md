# 2026-11-04 — ChatGPT — reconstrucción funcional de U6

## Qué se hizo
Se reconstruyó la descripción funcional de U6 desde el camino central ejecutable y se contrastó con la documentación conceptual y literatura relacionada. El informe completo queda en:

- informes/2026-11-04_RECONSTRUCCION_FUNCIONAL_U6.md

## Antes → después
- Antes: la descripción trataba el conjunto como un «motor» monolítico de inferencia y daba por sentados mecanismos descritos en el corpus conceptual.
- Ahora: se distingue U6 como arquitectura de análisis longitudinal de evidencia estructural; Engine V5 como componente canónico; V15.3 nativo como productor de tableros P/A/C; V15.3 integrado como agregador de candidatas, ranking, hipótesis y escenarios; y CEB/StinkBox como instrumentación/memoria con alcances delimitados.

## Hallazgos de código que corrigen la descripción
1. La entrada activa es JSON estructurado por cortes P/A/C; el adaptador nativo reemplaza el extractor de texto por tokens/pesos ya preparados.
2. PatternLibrary.get_patterns_for_question() devuelve todas las familias; la activación por campo semántico de la pregunta descrita en el corpus no ocurre en esa función.
3. El núcleo produce tres tableros de 244 puntuaciones y un vector R732 por corte.
4. El filtro de candidatas conserva hasta tres familias por eje/corte con p_final >= 0.65. El predictor trabaja sobre la unión de esas candidatas, no necesariamente sobre las 244 familias.
5. rank_fusion es fusión de rangos y señales relativas; no es probabilidad.
6. SET 021 implementa cobertura de evidencia con umbral 0.90; «necesario y suficiente» no es una prueba lógica formal.
7. La hipótesis abierta agrupa candidatas observadas por régimen de trayectoria; compartir régimen no equivale a converger en un acontecimiento.
8. Monte Carlo estima el término P_azar; no simula futuros completos ni mundos independientes.
9. La proyección longitudinal usa extrapolación lineal del último delta.
10. MCT exige comparación entre realidades independientes y vector-evento común; el propio informe de auditoría declara que esa capa no está implementada.

## Literatura contrastada
Se revisaron antecedentes de ATMS/temporal ATMS, t-DeLP, Multiple Hypothesis Tracking, narratología computacional 2026 y equifinalidad en teoría general de sistemas. La coincidencia de conceptos no se trató como identidad formal ni como prueba de falta de novedad.

## Ejecución y límites
- No se ejecutó una corrida nueva.
- No se modificó Engine V5 ni el catálogo de 244 patrones.
- Se revisó el snapshot de GitHub Actions: los éxitos más recientes corresponden al workflow de auditoría, no a nuevas corridas predictivas.
- No se afirma revisión línea por línea de los 194 archivos Python.
- No se afirma novedad mundial ni superioridad predictiva.

## Hashes y commits
- Rama: main
- HEAD observado antes de la intervención: d7bb1d7c087f56c8b8606f8cd32d8a9c10b2ebae
- Commit del informe: c51fcf00c4980f05a869d34dc01b85299fe66358

## Estado
RECONSTRUCCIÓN DOCUMENTAL COMPLETADA; pruebas empíricas y ablaciones propuestas, no ejecutadas en esta intervención.
