# Contrato de trabajo: hipótesis abiertas, trayectoria geométrica y apuesta

**Versión:** `V15.3_UNICO_WORKING_OPEN_HYPOTHESES_20261020_R1`  
**Ámbito:** motor alterno de trabajo U6. No modifica `Engine_V5_CANONICO_SOLO.py` ni `patterns_final_v14.json`.

## Orden lógico obligatorio

1. **Entrada congelada hasta Z.** Ninguna etapa de generación de hipótesis o apuesta consulta desenlaces posteriores.
2. **Vectorización temporal P/A/C + R732.** La señal de cada familia se observa por corte; se calculan apoyos de trayectoria micro, meso y macro, aceleración, convergencia multiescala, alineación con inercia y respuesta a curvatura/giro. Las dimensiones candidatas que discriminan entran a `rank_fusion`; las constantes/duplicadas siguen sujetas al guardián de dimensiones.
3. **Geometría multicapas y trazabilidad.** Antes de construir el conjunto abierto se ejecutan los módulos integrados `sidecar_latentes_v1`, `adaptador_convergencia_real_v1` (Tusi, comparación de trayectorias y nulo) y `teseracto_recursivo_geometria_v0_4`. Sus resultados se conservan en forma compacta. Los enlaces relacionales explícitos pueden mantener hipótesis complementarias fuera del conjunto mínimo 021 si acumulan al menos dos enlaces de trazabilidad. Esto no reordena `rank_fusion` ni transforma el diagnóstico geométrico en probabilidad.
4. **Conjunto abierto de hipótesis.** La salida primaria es `hipotesis` / `hipotesis_trayectoria_abierta.hipotesis`, con cardinalidad variable, sin máximo fijo. El set necesario/suficiente 021 aporta el núcleo; los candidatos complementarios por trazabilidad se identifican con su rol y conteo de enlaces. Las alternativas excluidas se conservan en `alternativas_fuera_del_set`.
5. **Apuesta posterior al conjunto.** `apuesta` y `apuesta_trayectoria` agrupan hipótesis por continuidad ascendente, continuidad descendente, meseta/estabilización, giro/divergencia o trayectoria insuficiente. Un escenario puede agrupar varias hipótesis; el desenlace no está obligado a ser una hipótesis individual ni uno de los alias históricos H1/H2.
6. **Revelado/calibración.** Los pesos de soporte son estructurales y relativos, no probabilidades. La calibración empírica requiere desenlaces posteriores sellados por caso.

## Compatibilidad

- `H1` y `H2` permanecen como campos históricos para módulos anteriores; **no definen el tamaño del conjunto ni la apuesta primaria**.
- Si hay cero hipótesis, no se inventa una. Si hay una, no se duplica como H2. Si hay más, se conservan las necesarias y suficientes y las complementarias con trazabilidad explícita.
- El registro de StinkBox se mantiene fuera del ZIP y no se sustituye en actualizaciones del motor.
- La geometría helicoidal/recursiva es descriptiva en el espacio abstracto de puntuaciones P/A/C; no constituye prueba física ni validación predictiva por sí misma.

## Evidencia de verificación de esta entrega

- Corrida real de integración: `CASO_NUEVO_20261013_01_CATALOG_REPAIR_R2`, 3 cortes.
- Candidatas del predictor: 4; hipótesis primarias emitidas: 4, incluidas por el set 021 y por enlaces repetidos de trazabilidad.
- Geometría multicapas: `EXECUTED`; búsqueda externa: `EXECUTED`.
- Apuesta: un escenario agregado `CONTINUIDAD_ASCENDENTE` con 4 hipótesis; no es una probabilidad calibrada.
- Corrida primaria y comparación T+1 ejecutadas en subprocesos aislados; el ledger CEB primario se preservó junto al resultado. Comparación T+1: el conjunto sellado en el corte previo tenía 3 hipótesis; 2 reaparecieron en la evidencia del corte retenido (`HIT_HIPOTESIS_SET`). Esto mide continuidad de candidatos, no revela el desenlace futuro ni calibra la apuesta.
- StinkBox persistente: checkpoint e importación `OK`; no añadió eventos porque la misma huella de entrada ya estaba registrada (deduplicación efectiva). Total de tokens únicos en ese almacén de prueba: 73.
- Pruebas del paquete: 94 aprobadas, 2 omitidas por referencias históricas ausentes, 0 fallidas.
- `Engine_V5_CANONICO_SOLO.py` y `patterns_final_v14.json` conservan sus hashes canónicos.
