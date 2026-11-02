# INICIO DE SESIÓN — ChatGPT / Motor U6

**Punto de entrada obligatorio para toda tarea relacionada con Motor U6.** No asumir que GitHub se carga automáticamente en una conversación: abrir y leer este archivo explícitamente antes de analizar o modificar el motor.

## Secuencia de arranque (orden único y obligatorio)

1. Leer `FEEDME_ACTUALIZADO.md`; revisar sus enlaces de seguimiento y la entrada reciente pertinente.
2. Leer `README.md`, `CONTRATO_CARPETAS.md`, `INSTRUCCIONES_CONTINUIDAD_CHATGPT.md` y `LLM_STARTUP_SIDECAR.md`.
3. Leer completo `PROTOCOLO_EJECUCION_Y_LECTURA_LLM.md`.
4. Leer `informes/2026-10-31_AUDITORIA_CONTINUIDAD_Y_ESTADO.md`, `docs/MAPA_VERSIONES_Y_AUTORIDAD.md`, `docs/CEB_INVESTIGAR_Y_RESOLVER.md`, `avances/REGLAS.md` y las reglas de las carpetas afectadas.
5. Revisar dudas, bloqueos, resueltos y avances recientes antes de proponer trabajo. Buscar primero si el componente, recibo, prueba o mecanismo ya existe.
6. Identificar repo, rama y commit actuales; inspeccionar los archivos y símbolos reales que afectan la tarea. No basarse en memoria, resúmenes ni fragmentos de búsqueda cuando se necesita el archivo completo.
7. Si hay corrida, vincular input, runner, revisión, salida JSON y `_RECIBO_EJECUCION.json`; comprobar hashes, estado terminal, etapas, errores, pausas y completitud. Código presente o cableado no demuestra ejecución.
8. Preservar el campo completo y todas las familias/datos. No filtrar por rango, top, valle, meseta, ascenso, descenso, aparente irrelevancia o contradicción con una hipótesis. Separar observación, salida de módulo, decisión del predictor e inferencia.
9. Antes de escribir, revisar contratos y estado. No modificar `Engine_V5_CANONICO_SOLO.py` ni `patterns_final_v14.json`. No crear otro contrato, recibo, registro o validador si ya existe uno que cubre la función. Si hay conflicto documental, resolverlo en los documentos vigentes y dejar una sola ruta de autoridad.
10. Ejecutar las comprobaciones y reparaciones permitidas con las herramientas disponibles; no convertir el diagnóstico en una lista de tareas para el usuario. Si una herramienta o permiso impide una acción, identificar el bloqueo exacto y agotar las alternativas disponibles.
11. Verificar cada cambio releyendo el archivo/commit; ejecutar pruebas cuando haya entorno real. Registrar el cambio en `avances/` según sus reglas. No afirmar prueba ni ejecución sin artefacto.
12. Entregar primero el resultado y su evidencia. No pedir contexto ya documentado ni trasladar al usuario trabajo que el asistente pueda hacer.

## Instrucción persistente para ChatGPT

Pega este bloque en las instrucciones del Proyecto de ChatGPT que uses para Motor U6 (o en las instrucciones personalizadas si trabajas fuera de un Proyecto):

> Para cualquier tarea relacionada con Motor U6, abre primero el repositorio privado https://github.com/marcojpad-hash/motor-u6-storage y lee INICIO_SESION_CHATGPT.md; sigue su secuencia sin pedirme que repita el contexto. No asumas que los archivos del repositorio se cargan solos: recupéralos mediante el conector GitHub antes de actuar. Lee el contrato de ejecución y los artefactos reales. Código inspeccionado no equivale a ejecución confirmada. Para una corrida, comprueba entrada, salida JSON y _RECIBO_EJECUCION.json, hashes, estado terminal y errores. Revisa el CEB existente antes de proponer mecanismos nuevos. Preserva todos los datos y familias, incluidos los que estén fuera del top o en valle/meseta/ascenso/descenso, y no descartes evidencia por contradecir una hipótesis. No modifiques el motor canónico ni patterns_final_v14.json. No inventes ni afirmes resultados no verificados. Registra cambios y pruebas según las reglas del repositorio. Responde en español directo, con resultados y evidencia, sin relleno ni tareas manuales innecesarias.

## Límite operativo

Este archivo es un punto de entrada documentado, no un mecanismo mágico de auto-carga. ChatGPT no lee automáticamente archivos privados de GitHub al abrir cada chat. La instrucción persistente de arriba hace explícita la obligación de recuperarlo; si el conector no está disponible en una sesión, hay que indicarlo y no fingir que se leyó.
