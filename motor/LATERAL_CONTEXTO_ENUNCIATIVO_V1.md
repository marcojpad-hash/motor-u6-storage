# Lateral de contexto enunciativo — adaptación Motor U6

**Versión:** 1.0  
**Código:** `motor/motor/lateral_contexto_enunciativo_v1.py`  
**Consumidor:** `motor/motor/guardianes_control_v1.py`  
**Bloque de salida:** `CONTEXTO_ENUNCIATIVO`.

## Función

Clon funcional de la implementación agnóstica del Orquestador Central, adaptado al contrato de U6. Registra juicios expresados, orientación valorativa, reiteraciones, asimetrías, encuadres adversariales, cierres discursivos y funciones lingüísticas. Conserva el fragmento, origen y enunciador declarado en el caso cuando existe.

## Cableado

1. `correr_guardianes()` ejecuta el lateral después de Beristáin, dentro del paquete posterior al predictor.
2. La entrada usa `textos_de_entrada(case)` y los metadatos `case.enunciador` o `case.speaker`.
3. El lateral emite un bloque trazable `CONTEXTO_ENUNCIATIVO`.
4. `attach_context()` adjunta referencias a Sherlock/Rigor, Falacias, Copi, Beristáin y el bloque de rigor (Holmes, Hécate y Schopenhauer). Las referencias no cambian las banderas ni las salidas de esos controles.
5. El lateral no sustituye Sombrero Blanco, que conserva su admisión factual independiente.

## Candados

`can_decide_H=false`, `escribe_H=false`, `escribe_patterns=false`, `reordena_candidatos=false`, `modifica_input=false`. No puntúa, no genera hipótesis y no declara sesgo, favoritismo, intención ni motivación como hecho. Las asimetrías y recurrencias son señales de comparación, no veredictos.

## Clonación y autonomía

Esta instancia U6 permanece en su rama y conectada al paquete de guardianes del motor. La instancia agnóstica vive en `orquestador-central/runtime/diagnostics/`. Son dos implementaciones independientes bajo un contrato funcional común; clonar no retira ni desconecta U6.

## Pruebas de integración

- Caso CTX-01: dos valoraciones positivas reiteradas sobre un actor y dos negativas sobre otro; comprueba carga reiterada, asimetría, atribución explícita del enunciador y referencia contextual a Sherlock/Rigor sin alterar su bandera.
- Caso CTX-02: input factual neutro; comprueba salida limpia y cero marcas.
- Las pruebas se ejecutan dentro de `motor/tests/test_runner_json_contract.py`, incluida en el workflow `Motor runner contract tests`.
