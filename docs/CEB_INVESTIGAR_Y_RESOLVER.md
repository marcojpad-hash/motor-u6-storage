# CEB: investigar y resolver (regla Mj, 2026-10-25)

Ninguna pieza del motor está de adorno. Vale para TODAS las piezas, no solo para Caldero.
El CEB sirve para encontrar **dónde** falló algo, para que el modelo averigüe **por qué** no corrió y **lo arregle**.
No basta con decir "aquí hay un problema".

## Regla operativa: convertir la intención en una vía implementable

La primera formulación de una solución no es la única forma de alcanzar el objetivo. Si el método, herramienta, proveedor, formato o ruta inicialmente elegidos no funcionan, **no se debe concluir de inmediato que el objetivo no se puede realizar**. La obligación es averiguar cómo hacerlo con los recursos, capacidades y permisos realmente disponibles.

Principio rector: **no confundir «esta vía no funcionó» con «esto no se puede hacer». La pregunta siguiente es «¿cómo lo hacemos?»**.

Ante una propuesta o tarea que encuentre una limitación, el agente debe:

1. **Conservar la intención y precisar el resultado:** identificar qué resultado busca Mj y qué condiciones son invariantes. Separar el objetivo de la primera herramienta, formato, proveedor o procedimiento sugerido.
2. **Tipar el obstáculo real:** distinguir entre falta de conocimiento, error de formulación, dependencia ausente, incompatibilidad, límite técnico, falta de datos, falta de capacidad del agente, permiso/autorización inexistente, restricción contractual, riesgo de seguridad o límite material de recursos. No agruparlos bajo un «no se puede» genérico.
3. **Buscar una transformación viable:** revisar componentes ya disponibles y probados, analogías funcionales, rutas alternativas, herramientas compatibles, cambios de formato, descomposición en subtareas, adaptadores o una implementación incremental. Cambiar el medio o la secuencia cuando sea necesario, preservando el resultado y las invariantes.
4. **Proponer y ejecutar el siguiente experimento útil:** elegir la alternativa que mejor conserve la intención y respete los contratos; probar primero la unidad mínima que permita distinguir si funciona. No quedarse en enumerar posibilidades cuando el agente tiene herramientas y autorización para comprobarlas.
5. **Verificar el resultado:** aportar evidencia de ejecución y comprobar que la alternativa satisface el objetivo. Una explicación convincente, un archivo escrito, un fixture o una prueba que no mide esa propiedad no demuestran implementación real.
6. **Iterar con aprendizaje:** si la alternativa falla, registrar qué se aprendió, descartar la vía fallida cuando corresponda y elegir otra estrategia. Repetir lo mismo sin evidencia nueva no cuenta como progreso.
7. **Informar el estado con precisión:** distinguir entre implementado, ejecutado, verificado, pendiente por dependencia, bloqueado por autorización y no viable bajo las condiciones actuales. Explicar qué condición concreta falta y qué vía queda por explorar.

### Límites de esta obligación

- Esta regla **no autoriza** a ignorar contratos, candados canónicos, permisos, límites de seguridad, propiedad de datos ni instrucciones expresas de Mj.
- No se deben inventar capacidades, credenciales, resultados, evidencia ni una viabilidad que no se haya comprobado.
- La falta de permiso no se resuelve eludiendo controles: se identifica el permiso exacto y se prepara el camino autorizado.
- Un presupuesto agotado, una herramienta no disponible o el fallo de un proveedor describen el estado de esa ejecución; por sí solos no demuestran que el objetivo sea imposible.
- Si ninguna alternativa puede ejecutarse en las condiciones presentes, se declara **NO_RESUELTO_BAJO_CONDICIONES_ACTUALES**, con causa, evidencia, alternativas examinadas y condición necesaria para reabrir. No se convierte esa etiqueta en una afirmación universal de imposibilidad.

Esta regla complementa la obligación de búsqueda y resolución descrita en `docs/BRUJULA_OBLIGACION_BUSQUEDA_RESOLUCION.md`: el agente no debe limitarse a explicar el obstáculo; debe transformar la intención en un plan comprobable y recorrerlo hasta resolver o documentar con precisión el límite real.

## Qué significa cada severidad
| severidad | qué quiere decir | qué se hace |
|---|---|---|
| OK | corrió | nada |
| INFO_CORRIO_SIN_SENAL (ACTIVA_MUDA) | corrió, pero no aportó o no llegó a H en este caso | revisar `motivo` si se repite en todos los casos |
| INFO_OMISION_CONTRACTUAL | el contrato permite que no corra (required=False, SUPERADA, NOT_APPLICABLE, absorbida) | nada |
| **FALLO_EJECUCION** | debía correr y no corrió (NO_CORRE, APAGADA_POR_FLAG, API_PENDING, NO_INVOCADO, SIN_EJECUCION, NO_ENCONTRADO_EN_STORE, SIMULADO_FIXTURE, INTENTADO_FALLIDO, OMITIDO sin contrato) | **pasos de abajo** |
| **REQUIERE_CONTRATO** | estado que no conocemos: no se da por OK sin revisar | definir con Mj si debe correr en la fábrica |

## Cuando el CEB marque FALLO_EJECUCION, el modelo que esté trabajando debe:
1. **Leer la razón**: los campos `alerta`, `accion`, `error` y `aporte`/`motivo` de la fila (en `alertas_ejecucion` del estado verificado o en `compuerta_piezas` del RESUMEN del lote).
2. **Encontrar la causa raíz**: abrir el archivo de la pieza (`archivo`) y la rama que la llama en `laterales_unico_v1.py` o en la fábrica; reproducir con un solo caso.
3. **Arreglar el cableado o el camino de ejecución** (import, ruta, flag, credencial/API, proveedor, store). Prohibido: tocar el Engine (`MOTOR_V15_3_UNICO_*`), el catálogo 244, o cambiar la lógica de predicción.
4. **Volver a correr el smoke** y confirmar que la pieza queda en OK. No se cierra el trabajo dejando la etiqueta puesta.

Si se va a dejar una pieza sin arreglar, se escribe en avances/ por qué y quién decide; no se oculta.

## Compuerta de fábrica
`casos/fabrica/fabrica.py` → `compuerta_piezas`: junta todas las piezas con FALLO_EJECUCION/REQUIERE_CONTRATO de todos los casos del lote,
imprime una línea `[CEB] severidad pieza estado casos -> accion` por pieza y sale con **código 9** si hay algún FALLO_EJECUCION
(igual que la compuerta de Caldero). REQUIERE_CONTRATO se reporta pero no tumba el lote. `FABRICA_PIEZAS_REQUERIDAS=0` la vuelve solo aviso.

## Piezas cubiertas
Todas las filas del registro de laterales (`reg`) y del estado verificado (`filas`), entre ellas:
Caldero (búsqueda externa, caldero_ii_cuadrantes, caldero_run.py superada), Souriau (lente_souriau, souriau_v1_4, marco_7783_geometria),
Polti (vía puente/marco 7783), StinkBox (stinkbox_transport_v0_2, stinkbox_to_light_bus_v1, sombrero_blanco), billar (negativo_ricci_vs_billar),
analogical (pre_h_analogical_search V0.18; API_PENDING = FALLO), neighbor_store (vecinos_caldero), puentes (familias_tokens_puente, cameo, name_bridge),
Z-RI, Tusi, Schrödinger, trazabilidad, integración semántica, aquiles, perfil_narrador, guardianes de entrada/salida, dynamis, y cualquier pieza nueva que entre por `_pieza()`.
