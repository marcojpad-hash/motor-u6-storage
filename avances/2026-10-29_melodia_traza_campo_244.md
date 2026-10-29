# Avance — traza de la melodía del campo 244 — 2026-10-29

- Se inspeccionó el módulo existente `motor/motor/traza_campo_244.py` (blob SHA `c7c1d50252f38f473a03fbdd355363ad2a7013a2`).
- Causa identificada: imputación silenciosa de hipótesis ausentes como `0.5`, con potencial de fabricar deltas y rangos.
- Se añadió `motor/traza_campo_244_v2.py` como alternativa aislada, con preservación de ausencias y autoprueba.
- Se añadió el informe de resolución en `seguimiento/resueltos/`.
- Estado: alternativa creada; autoprueba no ejecutada en entorno del repositorio; integración no realizada.
- Sin cambios al motor canónico ni al catálogo 244.
