# Sidecar de arranque para asistentes — Motor U6

Este sidecar es el punto de entrada operativo para tareas del motor. No sustituye el CEB ni crea otro recibo.

## Secuencia obligatoria
1. Leer `README.md`, `CONTRATO_CARPETAS.md`, `INSTRUCCIONES_CONTINUIDAD_CHATGPT.md` e `INICIO_SESION_CHATGPT.md`.
2. Leer `PROTOCOLO_EJECUCION_Y_LECTURA_LLM.md` y `docs/CEB_INVESTIGAR_Y_RESOLVER.md`.
3. Revisar las reglas de la carpeta afectada y los últimos informes/avances.
4. Para una corrida, inspeccionar la entrada, el JSON de salida y `_RECIBO_EJECUCION.json`; comprobar hashes, estado terminal, etapas y errores. No confundir código inspeccionado con ejecución confirmada.
5. Si el CEB marca `FALLO_EJECUCION`, seguir el playbook existente: leer alerta/acción/error/motivo, rastrear la llamada y corregir cableado, después repetir el smoke. No basta con señalar el fallo.
6. Preservar todas las observaciones y familias, incluidas las fuera del top o en valle/meseta/ascenso/descenso. Separar datos observados, salidas de módulos, decisión del predictor e inferencia.
7. No modificar `Engine_V5_CANONICO_SOLO.py` ni `patterns_final_v14.json`; no cambiar la lógica predictiva al reparar cableado.
8. Registrar cambios en `avances/` según sus reglas y verificar los archivos modificados.

## Texto para instrucciones persistentes de ChatGPT

Para cualquier tarea sobre Motor U6, abre el repositorio privado `https://github.com/marcojpad-hash/motor-u6-storage` y lee `LLM_STARTUP_SIDECAR.md` e `INICIO_SESION_CHATGPT.md` antes de actuar. Recupera los archivos mediante el conector GitHub; no supongas que se cargan automáticamente. Sigue el contrato de ejecución y el CEB existentes; no inventes un mecanismo duplicado. Para corridas, verifica entrada, salida y `_RECIBO_EJECUCION.json`, incluidos hashes y estado terminal. Si una pieza obligatoria no corre, investiga la causa raíz, repara el cableado permitido y vuelve a probar. Conserva todos los datos, incluso fuera del top o en valle/meseta/ascenso/descenso. No modifiques el motor canónico ni el catálogo 244. Documenta y verifica los cambios. Responde en español directo con evidencia real; no inventes ejecución.

## Límite

Un archivo del repositorio no se autoejecuta ni se auto-carga en la interfaz de ChatGPT. Para que el procedimiento se active en nuevos chats, el texto anterior debe quedar en las instrucciones del Proyecto de ChatGPT o en las instrucciones personalizadas. Este sidecar es compatible con agentes que sí leen explícitamente las instrucciones del repositorio.