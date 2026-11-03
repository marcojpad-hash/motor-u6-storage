# 2026-11-03 — Ejecución piloto del protocolo de orquestación epistémica v0.1

## Alcance y límite de la prueba

Se formalizó POE-U6 v0.1 y se ejecutó una suite de **14 pruebas de contrato** sobre un modelo de referencia aislado. Las pruebas corren en Python 3.13.5 y terminaron con **14 passed, 0 failed**.

**Importante:** la suite no importa ni ejecuta Engine V5/V15.3, ni los guardianes reales, ni el runner real. Es una comparación de comportamiento del protocolo formalizado con fixtures controlados. Sirve para verificar reglas, separación de autoridad y rutas ON/OFF; no mide eficacia predictiva de U6 ni demuestra que el motor actual ya tenga este orquestador.

## Comparaciones ejecutadas

| Comparación | Condición A | Condición B | Resultado del fixture |
|---|---|---|---|
| E1 Guardianes | ON | OFF | Misma H1 y mismo set; ON añade objeción tipada, OFF no. |
| E2 Compuerta | ON | OFF | Con pendiente concreta, ON bloquea cierre y OFF permite cerrar. |
| E3 Set abierto | Set de 3 | H1 única | La verdad del fixture queda fuera de H1 y dentro del set; cobertura sube, cardinalidad también. |
| E4 Memoria | ON | OFF | ON recupera una nota con procedencia; H1 no cambia. La memoria no vota. |
| E5 Adaptación | ON | Pipeline fijo | Con insuficiencia y señal nueva, ON ejecuta una operación adicional y cambia H1; OFF conserva ranking base. |

El caso E5 es una demostración del flujo de referencia: la señal nueva está presente en el fixture por diseño. No es una predicción real ni una prueba de que TORTUGAS/U6 resuelva casos reales.

## Tres controles transversales

### C1 — Falsos positivos
- Tres términos neutrales de control (elegido, delegado, pública) no disparan la regla contextual de referencia cuando aparecen solos.
- La misma regla sí marca cuando el fixture añade una señal contextual independiente.
- Resultado: 0/3 falsos disparos en el microconjunto neutral. No equivale a una tasa de falsos positivos de los guardianes U6.

### C2 — Costo
- El contador de operaciones del modelo de referencia permanece dentro del presupuesto de 10 operaciones del test.
- La adaptación solo agrega una operación cuando hay insuficiencia/contradicción.
- No se midieron CPU, wall time ni tokens del motor real. El presupuesto de 2 rondas/6 operaciones del protocolo queda como parámetro propuesto, no como valor ya validado.

### C3 — Generalización
- Los invariantes de salida se probaron en tres fixtures: biografía, ciencia y evento, con tres identificadores de modelo simulados.
- No se ejecutaron tres LLM reales ni se midió transferencia predictiva entre dominios. Es una prueba de invariantes, no una evaluación de generalización empírica.

## Pruebas concretas

- 3 pruebas E1: guardianes observacionales, vocabulario neutral sin alerta, señal contextual independiente requerida.
- 2 pruebas E2: bloqueo por pendiente y cierre cuando no hay pendientes.
- 2 pruebas E3: cobertura/cardinalidad del set y ausencia de declaración de probabilidad.
- 2 pruebas E4: memoria no altera H1 y deduplicación/aislamiento por caso.
- 2 pruebas E5: adaptación bajo insuficiencia y no activación cuando no hay disparador.
- 3 controles: falsos positivos neutrales, presupuesto acotado e invariantes por estrato.

## Relación con la auditoría real U6 del 3-nov

La auditoría previa sobre F006 y la calibración deduplicada sigue siendo la evidencia del motor real:
- Guardianes ejecutados en F006; costo observado ≈0.84 % de la corrida; sin comparación real ON/OFF.
- Compuerta ejecutada en un caso sin pendientes bloqueadores; sin comparación real ON/OFF.
- Set abierto 12/40 frente a H1 8/40 y H2 5/40 en 40 casos históricos independientes; es cobertura descriptiva, no ablación.
- Memoria persistió y deduplicó en F006; sin comparación real ON/OFF.
- TORTUGAS ejecutó 6 remediciones; no separó el top1 en F006; sin baseline fijo emparejado.

Por tanto, las pruebas de protocolo no sustituyen ni amplían artificialmente esos denominadores.

## Resultado

**POE-U6 v0.1 supera las 14 pruebas de contrato del modelo de referencia.** Las cinco comparaciones lógicas responden como se esperaba en fixtures controlados. Los tres controles también pasan en el alcance sintético definido.

**Todavía no hay evidencia experimental causal sobre el motor real.** La siguiente fase exige implementar el controlador como lateral aislado y preparar casos nuevos con entradas congeladas y desenlaces sellados, para correr cada par ON/OFF con el mismo input, seed, versión y entorno. El plan de fábrica prohíbe reutilizar casos sellados como casos independientes.

## Artefactos

- `docs/PROTOCOLO_ORQUESTACION_EPISTEMICA_PROVISIONAL_V0_1.md`
- `tests/test_orquestacion_epistemica_provisional.py`
- Este informe.
