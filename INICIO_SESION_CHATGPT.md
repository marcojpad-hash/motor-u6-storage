# Inicio de sesión — Motor U7

**Autoridad única:** [`docs/CONTRATOS_OPERATIVOS_V7.md`](docs/CONTRATOS_OPERATIVOS_V7.md). Repositorio: `marcojpad-hash/motor-u6-storage` (slug histórico). Rama operativa: `alterno/cameo-pesos`.

## Secuencia obligatoria
1. Leer `README.md`, `FEEDME_ACTUALIZADO.md` y este inicio.
2. Leer el contrato operativo único y `PROTOCOLO_EJECUCION_Y_LECTURA_LLM.md`.
3. Leer las reglas de la carpeta afectada y el último registro de `avances/`.
4. Confirmar rama y commit actuales. No usar `main` como base de trabajo ni consultar contratos archivados como instrucciones activas.
5. Buscar primero si la capacidad, módulo, prueba o recibo ya existe. Distinguir archivo, cableado, integración y ejecución confirmada.
6. Usar `motor/correr_estandar.py` para corridas. Esta ruta ejecuta UNICO, los controles de entrada, Z90 declarado, candados, guardianes, CEB, salida humana, traducción, verificación y observador U7.
7. Ante una excepción o fallo, aplicar `control_flujo_soluciones.py`: registrar PIEDRA/CONTORNO/SIGUIENTE/EVIDENCIA y seguir por una alternativa segura. No saltar candados duros ni convertir un fallo en éxito.
8. Para cada corrida, leer RESULT y `_RECIBO_EJECUCION.json`, vincular input, hashes, commit, etapas, estado terminal y errores. Código leído no equivale a ejecución.
9. Preservar todos los datos y familias, también fuera del top y en valle/meseta/ascenso/descenso. Separar observación, salida de módulo, decisión del predictor e inferencia.
10. No modificar `motor/Engine_V5_CANONICO_SOLO.py` ni `motor/patterns_final_v14.json`. No calibrar con datos no sellados ni declarar probabilidades calibradas sin evidencia.
11. Registrar cambios en `avances/`, releer los archivos modificados y ejecutar las pruebas pertinentes. No inventar pruebas ni persistencia.
12. Entregar resultados y evidencia; no trasladar al usuario comprobaciones que puedan ejecutarse con las herramientas disponibles.

## Identidad

El nombre operativo es **Motor U7**. El repositorio mantiene el slug histórico `motor-u6-storage`; algunas rutas U6/V15.3 siguen por compatibilidad. No crear ni operar un segundo U7: la línea unificada vigente está en `alterno/cameo-pesos`.

## Límite de auto-carga

GitHub no inyecta este archivo automáticamente en un chat nuevo. El asistente debe recuperar explícitamente este inicio y el contrato único mediante la conexión GitHub antes de actuar.
