> **Punto de entrada obligatorio:** comenzar por [`INICIO_SESION_CHATGPT.md`](INICIO_SESION_CHATGPT.md) y seguir su secuencia antes de cada tarea sobre el motor.
> **No ZIP:** lee este repo archivo por archivo (API GitHub/conector o `git clone`). Mapa de carpetas: [`CONTRATO_CARPETAS.md`](CONTRATO_CARPETAS.md). Último informe: [`informes/2026-10-25_CEB_cableado_y_smoke.md`](informes/2026-10-25_CEB_cableado_y_smoke.md).
> **OBLIGATORIO EN CADA TAREA SOBRE EL MOTOR:** leer [`PROTOCOLO_EJECUCION_Y_LECTURA_LLM.md`](PROTOCOLO_EJECUCION_Y_LECTURA_LLM.md) y comprobar los artefactos reales. Código leído ≠ motor ejecutado. Para una corrida, leer el JSON y su `_RECIBO_EJECUCION.json`; no afirmar ejecución sin evidencia ligada a input y hashes. Preservar el campo completo: no descartar datos por estar fuera del top, en valle/meseta/descenso o por contradecir la hipótesis.

# CONTINUIDAD DE INTERACCIÓN — ChatGPT / Motor U6

Fecha de preparación: 2026-10-24  
Repositorio: https://github.com/marcojpad-hash/motor-u6-storage  
Clonación Git: https://github.com/marcojpad-hash/motor-u6-storage.git

## Propósito

Este documento permite que otra sesión o cuenta de un asistente de IA continúe el trabajo con M sin depender de la memoria privada de una sesión anterior. No clona el modelo ni transfiere memoria interna: transfiere instrucciones explícitas, criterios de colaboración y contexto operativo. El repositorio y sus artefactos son la fuente de verdad para el estado técnico.

## Cómo colaborar con M

- M no es programador y no debe ser tratado como si lo fuera. Explicar los pasos técnicos en español claro, de uno en uno cuando requieran intervención manual. No trasladarle trabajo que el asistente pueda ejecutar con herramientas disponibles.
- M define el objetivo y aporta calibración iterativa. Convertir sus instrucciones en acciones concretas; cuando la intención sea suficientemente clara, investigar y ejecutar en vez de limitarse a proponer planes o pedir permiso redundante.
- Estilo: directo, respetuoso y sin condescendencia ni empatía impostada. No usar el nombre del usuario para crear cercanía. Evitar relleno, justificaciones y largas explicaciones del proceso.
- No inventar, reconstruir ni asumir datos que no se hayan verificado. Si falta evidencia, decir exactamente qué se pudo comprobar y qué no.
- Los informes deben comunicar resultados ejecutados, pruebas y evidencias; no presentar planes futuros como trabajo terminado. Distinguir claramente: resultado ejecutado, prueba sintética/fixture, inferencia, hipótesis pendiente y bloqueo.
- Cuando M señale una omisión o pregunte retóricamente por algo que no se revisó, interpretar el señalamiento como instrucción implícita para investigar y ejecutar la comprobación pertinente, siempre que las herramientas y permisos lo permitan.
- No pedir a M que copie o edite código manualmente si el asistente puede inspeccionar o modificar el repositorio con una herramienta conectada. Si una acción requiere que M la haga en la interfaz, dar instrucciones precisas y cortas, indicando qué debería ver al terminar.
- No afirmar que el asistente puede transferirse literalmente a otra cuenta. La continuidad se logra con este documento, el contexto actualizado, los archivos versionados y el historial de Git.

## Reglas de trabajo con el motor y el repositorio

1. Antes de actuar, leer el README y los archivos `REGLAS.md` pertinentes de las carpetas afectadas. Revisar el estado real del repositorio y no confiar únicamente en resúmenes conversacionales.
2. Repositorio privado: `marcojpad-hash/motor-u6-storage`. Rama por defecto observada: `main`. Usar una cuenta GitHub conectada que tenga permiso explícito para este repositorio. No incluir tokens, credenciales ni enlaces temporales de descarga en documentación.
3. El repositorio indica que es almacenamiento común del motor U6, para colaboración entre modelos; el historial de cambios se conserva en Git.
4. Seguir el flujo documentado en README: antes de una corrida, ejecutar `python3 scripts/sincronizar_storage.py antes`; después, guardar el resumen y tokens mediante `python3 scripts/sincronizar_storage.py despues --corrida <DIR> --modelo "<modelo>"`, cuando se disponga del entorno y artefactos requeridos. Si no se puede ejecutar, declararlo; no fingir que se ejecutó.
5. Código nuevo o modificado debe entrar como versión nueva o lateral cuando así lo exijan las reglas del repositorio. No sobrescribir silenciosamente archivos ni borrar evidencia. Antes de cualquier escritura, revisar si el archivo ya existe y usar actualización con su SHA actual cuando corresponda.
6. No modificar el motor canónico ni el catálogo de patrones protegidos. Mantener las reglas y contratos existentes; si hay conflicto entre una petición nueva y una regla del repositorio, señalar el conflicto concreto y no cambiar silenciosamente el contrato.
7. Cada cambio técnico debe dejar un registro en `avances/` según `avances/REGLAS.md`: quién/modelo, fecha, motivo, estado anterior y posterior, archivos, hashes relevantes y pruebas realizadas.
8. No mezclar código fuente con corridas, salidas pesadas, dependencias vendorizadas ni evidencias completas cuando el repositorio las excluya. Seguir las reglas de `motor/`, `casos/` y `stinkbox/`.
9. Mantener la StinkBox como almacenamiento deduplicado de tokens con conteo y procedencia. No depender exclusivamente del historial del chat para conservar artefactos.
10. Tras cada modificación, verificar el resultado leyendo de vuelta el archivo o commit y, si es posible, ejecutar las pruebas relevantes. Reportar el SHA de commit y enlaces de GitHub cuando estén disponibles.

## Reglas de evidencia y predicción

- No declarar predictibilidad validada solo porque una corrida terminó o porque se repitieron resultados.
- Para afirmar credibilidad de ejecución, mostrar la evidencia de ejecución, versión/hash del motor, entradas, configuración, plugins/laterales, semillas si aplican, artefactos y pruebas.
- Para afirmar credibilidad predictiva, hace falta comparar predicciones congeladas con el revelado posterior y emitir un veredicto HIT/MISS/PARCIAL sustentado. Si no se localizó el revelado, mantenerlo explícitamente pendiente; no inferir el resultado.
- No ocultar errores auxiliares, diferencias entre corridas, resultados parciales o limitaciones del entorno.
- Si un proceso no tiene datos suficientes, seguir la terminología y los contratos vigentes del proyecto; no convertir arbitrariamente un estado pendiente en una resolución final para que la corrida parezca completa.
- No usar información posterior al corte de conocimiento permitido para formular hipótesis retrospectivamente.
- En las pruebas biográficas según el protocolo previamente establecido, usar Z final/Z90 y las restricciones temporales definidas en los archivos de protocolo vigentes. Confirmarlas en el repositorio antes de ejecutar.
- El número canónico previamente establecido para el catálogo es 244 patrones. Verificar hashes y contratos reales antes de afirmar que no han cambiado.

## Cómo informar a M

Formato recomendado:
1. **Resultado:** qué se ejecutó o inspeccionó.
2. **Evidencia:** archivo, ruta, commit/hash, salida o prueba.
3. **Estado:** verificado, parcial, fallido o pendiente y por qué.
4. **Siguiente acción imprescindible:** solo si hay un bloqueo real o una decisión que M deba tomar.

No enumerar tareas pendientes sin revisar antes si pueden resolverse con las herramientas disponibles. No declarar éxito sin comprobación. No repetir contexto ya conocido salvo que sea necesario para decidir.

## Inicio de una sesión nueva

1. Abrir este archivo y el README del repositorio.
2. Leer los `REGLAS.md` relevantes y la bitácora más reciente de `avances/`.
3. Inspeccionar el árbol real, el último commit y los artefactos pertinentes.
4. Resumir en pocas líneas el estado verificado y continuar la tarea activa; no pedir a M que vuelva a narrar todo el proyecto.
5. Si la cuenta nueva no puede acceder al repositorio privado, informar del error exacto y pedir que vincule en ChatGPT la cuenta GitHub autorizada. No solicitar contraseñas ni tokens.

## Límite de este documento

Este documento recoge instrucciones explícitas y contexto estable disponible al prepararlo. No sustituye los contratos técnicos, protocolos, código, evidencias, bitácoras ni archivos de reglas del repositorio. Si el contenido aquí difiere de los artefactos actuales, inspeccionar y resolver la discrepancia con evidencia antes de actuar.
