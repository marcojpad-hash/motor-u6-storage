# Protocolo provisional de orquestación epistémica (POE-U6) — v0.1

**Estado:** propuesta experimental; no es todavía una implementación integrada en U6 ni una modificación del motor canónico.  
**Ámbito:** coordinar predictor, guardianes, resolución adaptativa, compuerta de cierre y memoria lateral.  
**Principio rector:** el orquestador administra el proceso de investigación; no decide la verdad ni sustituye al predictor.

## 1. Objetivo y separación de responsabilidades

El POE-U6 busca decidir **qué operación epistémica conviene ejecutar a continuación**, cuándo detenerse y qué dejar abierto. Debe mantener separadas cinco funciones:

1. **Predictor:** produce H1, H2, conjunto abierto y, si corresponde, escenarios. Es la única pieza que propone el orden predictivo.
2. **Guardianes:** buscan defectos, contradicciones, contaminación temporal, fragilidad y problemas de trazabilidad. Emiten objeciones tipadas; no reordenan ni reescriben hipótesis.
3. **Resolutor adaptativo:** ante una insuficiencia concreta, elige una operación adicional acotada (releer corte, contrastar fuente, descomponer contradicción o remedición multiescala). No inventa evidencia.
4. **Compuerta de suficiencia/cierre:** determina si el expediente puede cerrarse, debe quedar abierto o debe pausarse. Se ejecuta **después** de guardianes y remediciones, no antes.
5. **Memoria lateral:** conserva datos, decisiones operativas y procedencia con alcance y hash. Puede aportar contexto recuperable, pero no votar, ponderar ni alterar por sí sola H1/H2.

El LLM, si participa en una operación, es auxiliar de búsqueda, extracción o crítica. No puede asignar la verdad, cambiar el ranking ni liberar la compuerta.

## 2. Estado formal

En el paso t, el estado de trabajo es:

\[
S_t=(E_t,H_t,O_t,R_t,M_t,B_t,Z)
\]

- `E_t`: evidencia disponible, con fuente, fecha, corte, hash y nivel de independencia.
- `H_t`: salida del predictor: ranking, conjunto abierto y escenarios.
- `O_t`: objeciones abiertas; cada una tiene tipo, evidencia, componente afectado, estado y criterio de resolución.
- `R_t`: registro de operaciones realizadas y sus resultados.
- `M_t`: memoria lateral recuperada, siempre etiquetada por procedencia y alcance.
- `B_t`: presupuesto restante (operaciones, tiempo, llamadas externas y/o tokens).
- `Z`: corte temporal congelado. Ningún dato posterior a Z puede entrar en generación de hipótesis.

La verdad/desenlace `Y` queda fuera de `S_t`. Solo el evaluador la abre después de sellar las salidas y sus hashes.

## 3. Ciclo de control

### Fase 0 — Admisión y congelación

- Validar esquema, identidad del caso, fuentes, fechas, pesos y hashes.
- Congelar Z y guardar el hash de entrada.
- Rechazar o pausar si hay evidencia posterior a Z, desenlace filtrado, fuente no trazable o identidad de caso repetida.
- Mantener entrada, predicción y desenlace en compartimentos separados.

### Fase 1 — Predicción base

- Ejecutar el predictor con entrada congelada.
- Sellar H1, H2, conjunto abierto, escenarios, ranking, seed, versión y hashes.
- Registrar que `rank_fusion`, soporte y peso estructural no son probabilidades salvo calibración explícita.

### Fase 2 — Auditoría independiente

- Ejecutar guardianes sobre entrada, evidencia y salida sellada.
- Cada objeción debe contener: `id`, `tipo`, `evidencia`, `fuente/hash`, `corte`, `hipótesis/componente afectado`, `severidad`, `estado` y `criterio_de_resolucion`.
- Un término léxico aislado no constituye objeción. Para marcar una alerta se exige evidencia contextual independiente.
- Las objeciones no modifican H1/H2 ni el conjunto. Si un guardián propone una corrección, esta se registra como propuesta separada y requiere una nueva ejecución controlada del predictor.

### Fase 3 — Enrutamiento adaptativo

El controlador solo selecciona una operación nueva cuando existe al menos una condición:

- objeción con evidencia y criterio de resolución explícitos;
- empate o insuficiencia que impide distinguir candidatas;
- contradicción relevante entre fuentes/cortes;
- hueco de evidencia que puede resolverse dentro del presupuesto;
- fallo de integridad o procedencia que exige reparación.

Cada operación candidata debe declarar antes de ejecutarse:

`operation_id`, `pregunta_operativa`, `objetivo`, `fuentes permitidas`, `resultado esperado`, `costo estimado`, `criterio de éxito`, `criterio de parada` y `riesgo de filtración temporal`.

Selección provisional: primero se atienden fallos de integridad/temporalidad; después contradicciones con evidencia independiente; después ambigüedades que puedan separar candidatas; por último, mejoras de presentación que no afectan la decisión. No se usa una puntuación numérica de ganancia de información hasta que exista calibración que la justifique.

Tras cada operación:

1. registrar resultado y costo;
2. comprobar si la objeción cambió a `RESUELTA`, `NO_RESUELTA` o `NO_VERIFICABLE`;
3. comprobar si apareció evidencia nueva válida, sin sobrescribir la evidencia anterior;
4. si no hubo progreso, cambiar de estrategia una vez; si vuelve a no haber progreso, pausar y conservar el estado abierto.

**Presupuesto inicial sugerido para el piloto:** máximo 2 rondas adaptativas y 6 operaciones por caso. Son límites experimentales provisionales, no constantes del motor. Una operación que no puede ejecutarse dentro del presupuesto queda como pendiente; no se simula su éxito.

### Fase 4 — Remedición y conjunto abierto

- Solo se remedirá la dimensión/corte señalado por una objeción o por una regla previa.
- Las nuevas mediciones se adjuntan; no sustituyen ni borran las anteriores.
- El conjunto abierto se evalúa por cobertura, precisión, cardinalidad media y utilidad frente a H1. No se permite declarar éxito solo por aumentar cobertura.
- Si ninguna candidata queda suficientemente separada, el resultado correcto es empate/abstención, no una selección forzada.

### Fase 5 — Compuerta final

La compuerta se ejecuta después de guardianes y operaciones adaptativas. Estados:

- `CERRAR`: no quedan bloqueadores; evidencia y procedencia satisfacen contrato; la salida declara incertidumbre residual.
- `MANTENER_ABIERTO`: existe una cuestión relevante resoluble y queda presupuesto.
- `PAUSAR`: evidencia insuficiente, conflicto no resoluble, presupuesto agotado o fallo de integridad.
- `RECHAZAR`: contaminación temporal, desenlace filtrado, entrada inválida o ruptura de candado.

Regla mínima: un bloqueador abierto con evidencia concreta impide `CERRAR`. Un aviso no sustentado o una marca léxica aislada no debe bloquear por sí sola.

### Fase 6 — Persistencia y evaluación

- Persistir únicamente después de sellar la corrida; append-only, deduplicación por hash y procedencia.
- La memoria recuperada en un caso nuevo debe indicar origen, caso, fecha, hash y regla de alcance. Prohibido mezclar memorias de casos distintos sin una regla explícita y evaluada.
- La memoria no puede alterar H1/H2 ni reabrir un caso sellado. Si se usa para una nueva inferencia, se crea una corrida nueva con input y hash nuevos.
- El desenlace se abre después del sello y se evalúa con reglas preinscritas.

## 4. Invariantes obligatorios

1. **No fuga temporal:** toda evidencia usada para generar hipótesis es ≤ Z.
2. **No autoridad del guardián:** guardianes objetan, no deciden.
3. **No autoridad de memoria:** memoria conserva y recupera procedencia, no vota.
4. **No cierre prematuro:** la compuerta va después de la última objeción/remedición.
5. **No bucle infinito:** cada operación tiene presupuesto, éxito y parada.
6. **No probabilidad ficticia:** ranking y soporte estructural no se reportan como probabilidad calibrada.
7. **No reetiquetado:** el desenlace y las reglas de evaluación se sellan antes de abrir resultados.
8. **No confusión de niveles:** prueba unitaria, ejecución, eficacia predictiva y generalización son evidencias distintas.

## 5. Cinco comparaciones emparejadas

Cada comparación usa el mismo input congelado, misma versión, seed, entorno, presupuesto base y desenlace sellado. Solo cambia el factor declarado. Orden de condiciones aleatorizado cuando sea posible; cada condición usa workspace limpio y registra hashes.

| ID | Condición A | Condición B | Resultado primario | Métricas de protección |
|---|---|---|---|---|
| E1 | Guardianes ON | Guardianes OFF | Objeciones útiles detectadas y errores prevenidos | Falsos positivos, predictor inmutable, costo |
| E2 | Compuerta ON | Compuerta OFF | Cierres incorrectos bloqueados | Falsos bloqueos, cierres correctos, costo |
| E3 | Set abierto | Solo H1 | Cobertura de desenlace | Precisión del set, cardinalidad media, cobertura incremental |
| E4 | Memoria ON | Memoria OFF | Recuperación útil y continuidad | Contaminación entre casos, duplicados, procedencia, costo |
| E5 | Resolución adaptativa ON | Pipeline fijo | Mejora de separación/acierto frente al costo | Operaciones extra, latencia, falsas activaciones, pausas |

No combinar varios interruptores en la primera ablación. Las interacciones factoriales se prueban después de identificar efectos individuales.

## 6. Tres controles transversales

### C1 — Falsos positivos

Un evaluador independiente etiqueta cada alerta como `TP`, `FP`, `FN` o `INDETERMINADA`. Reportar precisión, recall y tasa FP con denominadores; separar marca léxica, objeción lógica y objeción temporal. Los desacuerdos se conservan, no se resuelven por mayoría automática.

### C2 — Costo

Medir wall time, CPU si disponible, operaciones, llamadas externas, tokens, bytes y tasa de pausa. Reportar costo incremental emparejado `Δ = costo_ON − costo_OFF`, mediana, dispersión e intervalos. No sumar etapas anidadas como tiempos independientes.

### C3 — Generalización

Estratificar por dominio, tipo de caso y modelo. Mantener casos de evaluación no usados para ajustar reglas. Reportar cada estrato y resultado agregado; no inferir generalización fuera de los dominios y modelos realmente probados.

## 7. Tamaño y análisis

- Piloto mínimo recomendado: 20 casos independientes; no se considera confirmatorio ni suficiente para estimar efectos pequeños.
- Para una afirmación confirmatoria, calcular tamaño muestral antes de abrir desenlaces, usando tasa base y efecto mínimo relevante preinscritos.
- No contar reejecuciones del mismo input como nuevos casos. Deduplicar por `case_id` y SHA-256 de entrada.
- Reportar aciertos como conteos y tasas, junto con intervalos de confianza; para condiciones emparejadas, analizar discordancias por caso.
- Reportar abstenciones/pausas como resultados, no eliminarlas silenciosamente del denominador.

## 8. Contrato mínimo de registro

Cada corrida debe conservar:

- `protocol_version`, `case_id`, `input_sha256`, `freeze_Z`, `engine_sha256`, `catalog_sha256`, `seed`, `condition`, `model_id`, `domain`;
- `H1`, `H2`, `open_set`, `scenario`, `ranking_sha256` antes y después de auditoría;
- lista completa de objeciones y su adjudicación;
- operaciones adaptativas, disparador, resultados, costos y presupuesto restante;
- memoria recuperada/escrita con hashes y alcance;
- estado de compuerta y razones;
- recibo de ejecución, tiempos y errores;
- desenlace separado, hash sellado y evaluación posterior.

## 9. Qué demuestra y qué no demuestra esta versión

Esta especificación permite probar coherencia del protocolo, orden de fases, separación de autoridad, límites de costo y contratos de registro. Por sí sola no demuestra que U6 ya implemente este controlador, que los guardianes sean precisos ni que la orquestación mejore la predicción. El controlador adaptativo descrito aquí es una propuesta formal provisional; no se debe atribuir a la Brújula ni a código existente sin verificar su implementación y cableado.

## 10. Criterio de promoción a v1.0

Promover solo cuando: (a) exista implementación lateral aislada; (b) pase pruebas de contrato; (c) las cinco ablaciones se ejecuten sobre inputs nuevos emparejados; (d) los tres controles tengan etiquetas y mediciones; (e) el reporte incluya resultados negativos y pausas; y (f) Engine V5 y catálogo 244 conserven sus hashes.
