# Contrato de capacidad — Lectura funcional agnóstica V1

**Estado:** implementada como etapa post-corrida separada; CI verificado: run 46106989385, 134 pruebas aprobadas en 50.30 s.  
**Ámbito:** Motor U7, rama operativa alterno/cameo-pesos.  
**Naturaleza:** lateral de diagnóstico funcional del artefacto; no es predictor ni calibrador.

## Propósito

Comprobar si la salida final de una tarea cumple el propósito concreto declarado en su contrato, conserva coherencia con esa intención y permite reconstruir la relación entre entrada, evidencia y resultado.

La capacidad evalúa el funcionamiento del artefacto en contexto. No sustituye un validador estructural, una verificación factual, la lógica del predictor ni la lectura humana de la respuesta. No impone una lista editorial fija: los criterios de aceptación proceden del contrato particular de cada tarea.

## Alcance

Puede evaluar respuestas, análisis, informes, planes, código, guiones u otros artefactos. El contrato de tarea define qué significa que el artefacto funcione. La capacidad no infiere el propósito desde la salida ni permite que el productor se autoapruebe.

Queda fuera de alcance:
- decidir o recalcular H1/H2, ranking, polaridad, margen o pesos;
- modificar RESULT, RECIBO, entrada, evidencia congelada o archivos canónicos;
- afirmar verdad por coherencia narrativa;
- inferir rasgos psicológicos o perfilar a la persona;
- solicitar o almacenar cadena de pensamiento privada;
- llamar a un modelo, gastar créditos o publicar datos por sí misma.

## Entradas

1. **Contrato de tarea**: identificador, propósito, audiencia, resultado deseado, restricciones, no-objetivos, requisitos de evidencia, rutas JSON de entrada/salida/evidencia y decisión de si la lectura es compuerta.
2. **Entrada original**: solo las rutas declaradas por el contrato.
3. **RESULT final**: solo las rutas de artefacto y evidencia declaradas por el contrato.
4. **Revisión independiente**: JSON emitido por un modelo distinto del productor, ligado a los hashes del paquete.

El comando prepare construye un paquete mínimo. No copia campos fuera de las rutas declaradas; por tanto, las notas del productor y datos no necesarios no llegan al revisor.

## Salida

El comando apply produce un sidecar FUNCTIONAL_GATE_RESULT_V1 con:
- PASS, FAIL o INDETERMINATE;
- ALLOWED, BLOCKED o NOT_GATING;
- criterios evaluados, referencias de evidencia, requisitos no satisfechos y flags;
- hashes del input, RESULT, contrato, artefacto, paquete y revisión;
- estado de independencia declarado.

El sidecar no modifica RESULT ni RECIBO. La evidencia original permanece inmutable.

## Diagnóstico y regla de decisión

- **PASS**: todos los criterios del contrato pasan, cada criterio tiene evidencia rastreable y no hay flags críticas.
- **FAIL**: al menos un criterio falla o existe una flag crítica.
- **INDETERMINATE**: falta evidencia, el contrato no permite evaluar o la revisión no se puede vincular/verificar.
- **ALLOWED**: únicamente PASS cuando gate_required=true.
- **BLOCKED**: FAIL o INDETERMINATE cuando gate_required=true.
- **NOT_GATING**: el contrato declara gate_required=false; el diagnóstico se conserva, pero no bloquea el handoff.

El código vuelve a calcular la decisión a partir de los checks; no confía en el veredicto declarado por el revisor.

## Procedimiento operativo

1. El productor termina la corrida y escribe RESULT/RECIBO.
2. El contrato selecciona las rutas mínimas necesarias de input, artefacto y evidencia.
3. prepare crea un paquete ligado a hashes.
4. Un modelo independiente revisa el paquete usando el skill agnóstico.
5. apply valida esquema, hashes, criterios, referencias y separación declarada de modelos.
6. El orquestador consulta el sidecar antes del handoff. Si la compuerta es obligatoria y el resultado no es PASS, no libera el artefacto.

Comandos:

    python motor/lectura_funcional_v1.py prepare --input INPUT.json --result RESULT.json --contract CONTRATO.json --out PAQUETE_FUNCIONAL.json
    python motor/lectura_funcional_v1.py apply --package PAQUETE_FUNCIONAL.json --review REVISION_FUNCIONAL.json --out RESULT_LECTURA_FUNCIONAL.json

Si no se entrega revisión, apply emite INDETERMINATE y bloquea cuando gate_required=true.

## Independencia y límites de verificación

El validador exige modelo y run_id distintos, rol independent_reviewer y una declaración explícita de independencia. La identidad real del modelo no está autenticada criptográficamente; por eso el sidecar informa DECLARED_ONLY, nunca VERIFIED. La autenticación de identidad es una compuerta futura separada.

El revisor no entrega cadena de pensamiento. Entrega checks concisos, notas breves y referencias verificables a los fragmentos incluidos. El sistema no evalúa la calidad del razonamiento privado.

## Relación con U7 y controles existentes

El contrato operativo V7 define el sistema como Motor U7, pero la pieza llamada confianza_apuesta_u7.py es un observador lateral post-corrida B1–B6; sus pesos siguen calibrada=false. No es un evaluador de propósito funcional.

respuesta_humana, traduccion_salida y verificar_salida_llm ya producen y verifican prosa, concordancia, fidelidad, orden de H1/H2, grado y objeciones. Ninguno sustituye una lectura independiente que compare el artefacto final con un contrato de propósito específico.

La nueva lectura es ortogonal a esas piezas. Tampoco resuelve C-F8: el review_pending de StinkBox continúa siendo el stub documentado. No se afirma que el cierre canónico ya esté reparado.

## Criterios de aceptación de esta implementación

- paquete mínimo por rutas JSON declaradas;
- hashes que atan revisión a contrato, entrada, RESULT y artefacto;
- criterios arbitrarios definidos por cada contrato, sin checks CAPCOT codificados;
- PASS/FAIL/INDETERMINATE recomputado;
- fail-closed ante revisión ausente, hashes discordantes, criterio desconocido o referencia inválida;
- gate limitada al handoff, sin mutar RESULT/RECIBO/H1/H2;
- pruebas sintéticas en el workflow de contratos.

## Estado de integración

**CABLEADO_POSTRUN:** CLI prepare/apply y sidecar implementados.  
**INTEGRADO_EN_RUNNER:** NO; la revisión ocurre después de que existe RESULT y requiere otro modelo. El orquestador debe invocar apply antes de liberar el artefacto.  
**FUNCIONAL:** verificado por CI 46106989385 (134 passed, 50.30 s).  
**INDEPENDENCIA_VERIFICADA:** no; por ahora solo se valida la declaración del revisor.
