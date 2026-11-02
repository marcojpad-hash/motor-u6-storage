# AGENTS.md — instrucciones obligatorias para ChatGPT Codex en Motor U6

Este archivo es la instrucción de repositorio para el agente de código de ChatGPT (Codex). Tiene prioridad operativa sobre resúmenes de conversación y memoria del modelo. No reemplaza los contratos técnicos: los activa.

## Gate obligatorio antes de cualquier tarea
Antes de responder, inspeccionar, buscar, editar o ejecutar algo relacionado con Motor U6:
1. Leer `FEEDME_ACTUALIZADO.md`.
2. Leer `INICIO_SESION_CHATGPT.md` y seguir su secuencia completa.
3. Leer `INSTRUCCIONES_CONTINUIDAD_CHATGPT.md`, `LLM_STARTUP_SIDECAR.md` y `PROTOCOLO_EJECUCION_Y_LECTURA_LLM.md`.
4. Consultar el último informe y los registros de seguimiento/avances pertinentes.
5. Identificar rama y commit. No asumir que el contexto conversacional representa el estado actual del repo.

No iniciar una respuesta sustantiva sobre U6 hasta completar este gate. Si un archivo no puede leerse, detener la conclusión afectada y registrar exactamente cuál falló; no sustituirlo por memoria.

## Regla de ejecución
- Convertir señalamientos y objetivos claros en inspección, reparación o prueba ejecutada; no devolver al usuario tareas que el agente puede realizar.
- Buscar primero implementación, contrato, runner, tests y recibos existentes. No duplicar mecanismos.
- Ante FALLO_EJECUCION del CEB, seguir `docs/CEB_INVESTIGAR_Y_RESOLVER.md`: hallar causa raíz, reparar cableado permitido y volver a ejecutar el smoke.
- Diferenciar CODIGO_PRESENTE, CABLEADO_VERIFICADO, EJECUTADO_VERIFICADO y PROBADO.
- No afirmar éxito sin leer los artefactos y resultados de la ejecución concreta.
- No descartar observaciones o familias por rango, top, forma o contradicción con una hipótesis.
- No modificar `Engine_V5_CANONICO_SOLO.py` ni `patterns_final_v14.json`.
- Registrar cambios en `avances/` y verificar por lectura posterior.

## Respuesta
Entregar primero el resultado ejecutado, luego evidencia (rutas, commit, run, recibos, hashes y pruebas). No responder con disculpas, promesas, planes futuros ni listas de trabajo para el usuario cuando el trabajo sea ejecutable.

## Alcance real
Estas instrucciones se aplican automáticamente a agentes compatibles con `AGENTS.md`, en particular ChatGPT Codex cuando trabaja sobre este repositorio. Una conversación normal de ChatGPT que no esté ejecutándose como agente de código no recibe automáticamente los archivos del repositorio; no afirmar que este archivo la controla.
