# Sidecar de arranque — Motor U7

Contrato operativo único: `docs/CONTRATOS_OPERATIVOS_V7.md`. Repositorio con slug histórico `motor-u6-storage`; rama operativa `alterno/cameo-pesos`.

1. Leer `README.md`, `FEEDME_ACTUALIZADO.md`, `INICIO_SESION_CHATGPT.md` y el contrato operativo único.
2. Leer `PROTOCOLO_EJECUCION_Y_LECTURA_LLM.md` y el playbook CEB.
3. Confirmar rama, commit y hashes canónicos. No modificar Engine V5 ni catálogo 244.
4. Ejecutar mediante `motor/correr_estandar.py`; no duplicar componentes ya cableados ni usar contratos archivados como autoridad.
5. `control_flujo_soluciones.py` atiende errores de cierre en UNICO, fallos del subproceso primario, errores de salida y excepciones no controladas del runner. Produce contornos; no salta Engine/244/Z90 ni altera H.
6. Leer RESULT y `_RECIBO_EJECUCION.json`; comprobar hashes, estado terminal, etapas, errores y completitud.
7. Registrar cambios en `avances/`, releer los archivos y ejecutar pruebas. Código presente no prueba ejecución.

No pedir al usuario que repita contexto ya documentado. Buscar primero el mecanismo existente, ejecutar las acciones autorizadas y dejar evidencia.

Límite: GitHub no auto-carga este archivo en la interfaz; debe recuperarse explícitamente al iniciar una sesión nueva.
