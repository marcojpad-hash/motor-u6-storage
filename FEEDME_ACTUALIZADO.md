# FEEDME actualizado — Motor U6 / ChatGPT

Este es el punto único de entrada y seguimiento para el trabajo de ChatGPT sobre Motor U6. Abrirlo al iniciar una tarea. El repositorio es la fuente de verdad; esta página dirige al protocolo, a las carpetas de seguimiento y a los registros.

## Arranque obligatorio

1. Leer [INICIO_SESION_CHATGPT.md](INICIO_SESION_CHATGPT.md) y [LLM_STARTUP_SIDECAR.md](LLM_STARTUP_SIDECAR.md).
2. Leer [INSTRUCCIONES_CONTINUIDAD_CHATGPT.md](INSTRUCCIONES_CONTINUIDAD_CHATGPT.md), [PROTOCOLO_EJECUCION_Y_LECTURA_LLM.md](PROTOCOLO_EJECUCION_Y_LECTURA_LLM.md) y [Playbook CEB](docs/CEB_INVESTIGAR_Y_RESOLVER.md).
3. Revisar [la auditoría de continuidad 2026-10-31](informes/2026-10-31_AUDITORIA_CONTINUIDAD_Y_ESTADO.md), el [mapa de versiones](docs/MAPA_VERSIONES_Y_AUTORIDAD.md), el cierre de F006 R7 y las dudas abiertas.
4. Buscar en Seguimiento si ya existe una duda, fallo o decisión equivalente antes de abrir una nueva.
5. Ejecutar la tarea con las herramientas disponibles; no limitarse a describir el plan.


## Motor unificado experimental U6 — 2026-11-04

- Rama: `experimental/u6-unificado-activo-20261104`.
- Informe de ejecución y resultados: [U6 unificado experimental](informes/2026-11-04_U6_UNIFICADO_EXPERIMENTAL.md).
- Runner: `motor/u6/U6_UNIFICADO_EXPERIMENTAL.py`.
- Workflow: [U6 unificado experimental — smoke y suite completa](.github/workflows/u6-unificado-experimental.yml).
- Resultado: 2/2 smokes con búsqueda viva; CEB 45,106 eventos; 159 pruebas pasadas, 2 omitidas; 0 errores críticos.
- No se modificaron Engine V5 ni el catálogo 244. La variante sigue en rama experimental, sin promover a main.

## Continuidad de investigación U6 — 2026-11-04

- **Antes de repetir el análisis**, leer [handoff de continuidad](docs/CONTINUIDAD_INVESTIGACION_U6_2026-11-04.md). Resume qué se inspeccionó, qué hallazgos quedaron establecidos y desde dónde debe continuar el siguiente modelo.
- Informe técnico de la reconstrucción: [RECONSTRUCCION_FUNCIONAL_U6](informes/2026-11-04_RECONSTRUCCION_FUNCIONAL_U6.md).
- Registro de avance: [ChatGPT — reconstrucción funcional](avances/2026-11-04_ChatGPT_reconstruccion_funcional_U6.md).
- No rehacer la descripción general: continuar con pruebas discriminantes y preguntas aún abiertas. El handoff no sustituye los contratos ni la inspección puntual del código requerido por una nueva tarea.

## Seguimiento: dudas, fallos y decisiones

- [Dudas técnicas](seguimiento/dudas/README.md): preguntas que pueden resolverse inspeccionando código, contratos o evidencia.
- [Bloqueos y fallos](seguimiento/bloqueos/README.md): piezas que no corren, errores, herramientas omitidas o resultados incompletos. Aplicar el playbook CEB y corregir la causa raíz permitida.
- [Decisiones del creador](seguimiento/decisiones/README.md): solo preguntas que de verdad requieren una decisión del creador; no delegarle comprobaciones que el asistente pueda hacer.
- [Resueltos](seguimiento/resueltos/README.md): cierre con evidencia, commit, pruebas y enlaces a la solución.

Cada incidente debe tener un archivo propio fechado. Formato sugerido: `AAAA-MM-DD_<tipo>_<tema>.md`. No borrar ni reescribir registros cerrados: crear una entrada nueva que los corrija o los enlace.

## Reglas que no se negocian

- Código inspeccionado no significa ejecución confirmada.
- Para una corrida, comprobar entrada, salida JSON y `_RECIBO_EJECUCION.json`, hashes, estado terminal, etapas y errores.
- Si una pieza requerida no corre, investigar la causa raíz, arreglar el cableado permitido y volver a probar. No basta con marcar el fallo.
- Preservar el campo completo y todos los datos, incluidas familias fuera del top y trayectorias en valle, meseta, ascenso o descenso.
- Separar observación, salida de módulo, decisión del predictor e inferencia.
- No modificar `motor/Engine_V5_CANONICO_SOLO.py` ni `motor/patterns_final_v14.json`.
- Documentar cada cambio técnico en `avances/` según `avances/REGLAS.md`.
- No afirmar resultados, pruebas ni persistencia que no se hayan verificado.

## Qué debe entregar cada tarea

1. Resultado concreto.
2. Evidencia: rutas, recibos, hashes, commit y pruebas disponibles.
3. Estado: confirmado, parcial, fallido o no verificado.
4. Solo si hace falta: una pregunta breve al creador que no pueda resolverse con los artefactos.

## Límite de auto-carga

GitHub no inyecta por sí solo este archivo en cada chat. Este FeedMe sirve como punto de entrada común para cualquier asistente con acceso al repositorio. Al comenzar una sesión relacionada con el motor, recuperar este archivo explícitamente; no pedir al usuario que vuelva a pegar el contenido.
