# CEB: investigar y resolver (regla Mj, 2026-10-25)

Ninguna pieza del motor está de adorno. Vale para TODAS las piezas, no solo para Caldero.
El CEB sirve para encontrar **dónde** falló algo, para que el modelo averigüe **por qué** no corrió y **lo arregle**.
No basta con decir "aquí hay un problema".

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
