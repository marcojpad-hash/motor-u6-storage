# INICIO DE SESIÓN — ChatGPT / Motor U6

**Punto de entrada obligatorio para toda tarea relacionada con Motor U6.** No asumir que GitHub se carga automáticamente en una conversación: abrir y leer este archivo explícitamente antes de analizar o modificar el motor.

## Secuencia de arranque

1. Leer `README.md`, `CONTRATO_CARPETAS.md` e `INSTRUCCIONES_CONTINUIDAD_CHATGPT.md`.
2. Leer `PROTOCOLO_EJECUCION_Y_LECTURA_LLM.md` completo.
3. Leer `informes/2026-10-25_CEB_cableado_y_smoke.md`, `avances/REGLAS.md`, las reglas de las carpetas afectadas y las entradas recientes de `avances/`.
4. Revisar el CEB existente y sus contratos antes de proponer o crear mecanismos nuevos. Investigar `docs/CEB_INVESTIGAR_Y_RESOLVER.md` y los módulos/artefactos CEB reales que correspondan a la tarea. No duplicar recibos, registros ni validaciones ya implementados.
5. Inspeccionar los archivos y commits reales que afectan la tarea. No basarse únicamente en recuerdos, resúmenes de chat ni fragmentos de búsqueda.
6. Si la tarea incluye una corrida, identificar su entrada, runner, salida JSON y `_RECIBO_EJECUCION.json`. Comprobar hashes, estado terminal, etapas, errores, datos incompletos y cualquier pausa. La existencia del código o de un archivo de salida aislado no prueba que esa corrida se ejecutó correctamente.
7. Preservar el campo completo y todas las familias/datos relevantes. No filtrar por estar fuera del top, en valle, meseta, ascenso, descenso, por parecer irrelevante o por contradecir una hipótesis. Separar dato observado, salida de módulo, decisión del predictor e interpretación del analista.
8. Antes de escribir, revisar contratos y estado actual. No modificar `Engine_V5_CANONICO_SOLO.py` ni `patterns_final_v14.json`. No sobrescribir evidencia ni inventar resultados. Registrar cambios en `avances/` conforme a sus reglas.
9. Verificar cada cambio releyendo el archivo/commit y ejecutar pruebas solo cuando exista un entorno real disponible. Informar el estado exacto: inspeccionado, ejecución confirmada, fallida, no verificada o incompleta.
10. Entregar primero el resultado y su evidencia; explicar únicamente los bloqueos reales. No pedir al usuario que repita el contexto ya documentado ni que haga manualmente trabajo que las herramientas permitan resolver.

## Instrucción persistente para ChatGPT

Pega este bloque en las instrucciones del Proyecto de ChatGPT que uses para Motor U6 (o en las instrucciones personalizadas si trabajas fuera de un Proyecto):

> Para cualquier tarea relacionada con Motor U6, abre primero el repositorio privado https://github.com/marcojpad-hash/motor-u6-storage y lee INICIO_SESION_CHATGPT.md; sigue su secuencia sin pedirme que repita el contexto. No asumas que los archivos del repositorio se cargan solos: recupéralos mediante el conector GitHub antes de actuar. Lee el contrato de ejecución y los artefactos reales. Código inspeccionado no equivale a ejecución confirmada. Para una corrida, comprueba entrada, salida JSON y _RECIBO_EJECUCION.json, hashes, estado terminal y errores. Revisa el CEB existente antes de proponer mecanismos nuevos. Preserva todos los datos y familias, incluidos los que estén fuera del top o en valle/meseta/ascenso/descenso, y no descartes evidencia por contradecir una hipótesis. No modifiques el motor canónico ni patterns_final_v14.json. No inventes ni afirmes resultados no verificados. Registra cambios y pruebas según las reglas del repositorio. Responde en español directo, con resultados y evidencia, sin relleno ni tareas manuales innecesarias.

## Límite operativo

Este archivo es un punto de entrada documentado, no un mecanismo mágico de auto-carga. ChatGPT no lee automáticamente archivos privados de GitHub al abrir cada chat. La instrucción persistente de arriba hace explícita la obligación de recuperarlo; si el conector no está disponible en una sesión, hay que indicarlo y no fingir que se leyó.
