# 2026-11-04 — Estados crudos clasificados como ACTIVA_MUDA

## Pregunta verificable

¿Por qué cuatro filas con estados crudos distintos de ACTIVA_MUDA aparecen dentro de la lista ACTIVA_MUDA?

## Evidencia

En MOTOR_V15_3_UNICO_20260927.py, el registro usa un fallback equivalente a:

- Estado conocido: usar _MAPA_ESTADO[estado].
- Estado desconocido que empieza por EXEC: clasificar como ACTIVA.
- Cualquier otro estado desconocido: clasificar como ACTIVA_MUDA.

La matriz de ablación de Courbet y Haber encontró estos cuatro estados crudos:

| Pieza | Estado crudo | Interpretación del estado |
|---|---|---|
| plugin_guardia_no_cruce.py | ABSORBIDO_EN_GUARDIA_TRANSVERSAL | La función está absorbida en la guardia transversal |
| cameo_to_244_adapter_v1.py | NOT_APPLICABLE | No aplica; falta el mapeo correspondiente |
| matriz_clases | PRESENTE | Registro de presencia/inventario |
| resolucion_operativa_terminal_017 | RESUELTO_OPERACIONALMENTE | Etapa de resolución ya resuelta |

No describen cuatro piezas que se ejecutaron sin producir señal. El fallback las incorpora indebidamente al conteo ACTIVA_MUDA.

## Comprobaciones

- Dos casos independientes: Courbet y Haber.
- 42 filas ACTIVA_MUDA reportadas por caso.
- Los cuatro estados anteriores aparecen en ambos casos.
- Al excluirlos, quedan 38 filas con estado ACTIVA_MUDA por caso; no equivalen a 38 módulos independientes.
- La etapa resolucion se probó como control adicional en ambos casos: no cambió H1/H2, el orden de candidatas ni rank_fusion.
- Informe de ablación: informes/2026-11-04_ABLACION_ACTIVA_MUDA_U6.md.
- Workflow y evidencia: https://github.com/marcojpad-hash/motor-u6-storage/actions/runs/41881474178.

## Estado

**Causa identificada; corrección de código pendiente.**

No se modificó MOTOR_V15_3_UNICO_20260927.py. El protocolo CEB vigente prohíbe modificar el Engine V15.3 y cambiar su lógica. La corrección requiere una modificación autorizada del mapa de estados; no debe ocultarse el problema cambiando solo el conteo del informe.

Los estados ABSORBIDO_EN_GUARDIA_TRANSVERSAL y NOT_APPLICABLE deben conservar su semántica de absorbido/no aplicable según el contrato CEB. PRESENTE y RESUELTO_OPERACIONALMENTE tampoco deben caer en el estado por defecto ACTIVA_MUDA.
