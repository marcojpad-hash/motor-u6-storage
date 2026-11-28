# Lectura funcional agnóstica — registro de implementación

Fecha: 2026-11-27. Rama: alterno/cameo-pesos.

## Base observada

- El contrato operativo V7 nombra el sistema Motor U7.
- confianza_apuesta_u7.py es un observador post-corrida B1–B6; el campo calibrada permanece false.
- respuesta_humana, traduccion_salida y verificar_salida_llm están cableados y probados, pero sus controles no equivalen a una lectura independiente contra el propósito particular de cada tarea.
- El verificador de salida revisa conformidad y referencias admitidas; no determina por sí solo si el artefacto sirve a su finalidad.
- El límite C-F8 permanece separado: review_pending de StinkBox sigue documentado como stub.

## Implementación

Se añade una etapa post-corrida agnóstica:
- contrato de tarea con propósito, audiencia, resultado deseado, restricciones, no-objetivos, evidencia y criterios configurables;
- skill de revisión para otro modelo, sin cadena de pensamiento ni autoevaluación del productor;
- paquete mínimo que solo incluye rutas declaradas y hashes;
- validador CLI prepare/apply que emite un sidecar FUNCTIONAL_GATE_RESULT_V1;
- gate fail-closed para handoff cuando gate_required=true y la revisión no es PASS.

La etapa no modifica RESULT, RECIBO, H1/H2, ranking, pesos, Engine V5 ni catálogo 244. No llama modelos ni consume créditos. La identidad del revisor queda DECLARED_ONLY, no autenticada.

## Integración

La revisión se realiza después de escribir RESULT porque necesita el hash final. Por eso se implementa como etapa explícita de handoff post-corrida, no dentro del predictor ni como una llamada previa en correr_estandar.py. El orquestador debe invocar apply antes de liberar el artefacto.

## Pruebas

Se incorpora una suite sintética para paquete mínimo, PASS, FAIL, UNKNOWN, ausencia de revisión, hash discordante, referencias inválidas, identidad declarada no independiente y modo observacional sin compuerta.

Estado CI: VERIFICADO. Run 46106989385, conclusión success; 134 passed en 50.30 s. Lectura de vuelta del run y del log completada. La etapa queda FUNCIONAL como validador post-run, no como integración automática en correr_estandar.py.
