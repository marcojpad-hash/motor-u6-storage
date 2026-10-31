# Protocolo de custodia independiente — lote ciego U6

Fecha: 2026-10-31  
Estado: propuesta operativa complementaria al PLAN_20_CASOS_MOTOR.md. No modifica motor, catálogo, gate Z ni resultados históricos.

## Problema que resuelve
Los cuatro casos históricos B-01/N-02/C-03/H-01 no ejecutaron el motor. F006/Courbet repite un input ya contado. F003 documentó que preparador de semillas y custodio de desenlaces fueron el mismo ejecutor en la misma sesión. Esos materiales no permiten afirmar una muestra de 20 corridas ciegas independientes con separación fuerte de funciones.

## Separación obligatoria de funciones

| Rol | Puede ver | No puede ver ni hacer |
|---|---|---|
| Selector de cohorte | Marco de selección, criterios de inclusión y lista inicial de sujetos | No formula predicciones ni modifica desenlaces |
| Preparador Z | Fuentes y hechos con fecha <= Z; crea P/A/C y evidencia pre-Z | No accede a desenlace sellado, destino ni lista negra |
| Custodio independiente | Identidad, desenlace posterior y destino; crea archivos sellados y lista negra | No redacta ni corrige la entrada pre-Z ni interviene en la predicción |
| Runner | Entrada comprometida, motor y patrones congelados | No abre desenlaces antes de congelar salida y recibo |
| Auditor | Compromisos, hashes, recibos y después los pares entrada/salida/desenlace | No altera entradas, predicciones ni etiquetas |

Una misma persona o agente no puede ocupar simultáneamente Preparador Z y Custodio independiente para el mismo caso. Si no hay dos actores independientes, el caso queda como ensayo metodológico, no como caso ciego certificado.

## Secuencia por caso

1. El selector asigna un sujeto nuevo y un case_id único, sin usar Courbet ni ningún input_sha256 ya evaluado.
2. El preparador redacta únicamente hechos con fecha <= Z, adjunta fuente por afirmación y construye P/A/C bajo el contrato vigente. No consulta el desenlace.
3. El custodio independiente prepara por separado el destino y el desenlace sellado, además de la lista negra. No comparte etiquetas con el preparador ni el runner.
4. La fábrica ejecuta preparar-z con los dos paquetes separados y aplica gate_z90.py. Una sola violación rechaza el lote.
5. Antes de correr, se comprometen SHA-256 de entrada, destino, desenlace, Engine V5 y catálogo de 244 patrones.
6. El runner ejecuta en copia temporal. Congela salida, recibo, métricas H1/H2, set, escenario, destino y predictibilidad.
7. Solo después de verificar el compromiso se abre el desenlace. Se evalúan por separado acierto de H1, H2, set, escenario, destino exacto y polaridad.
8. El auditor comprueba independencia del case_id, input_sha256, fuente, fechas, hashes y roles. Una reevaluación nunca aumenta n.

## Umbrales y reglas
- C01–C20 son veinte sujetos/entradas independientes, no veinte ejecuciones repetidas.
- No elegir pesos con menos de 10 casos independientes para la comparación correspondiente.
- No calibrar predictibilidad_021 antes de reunir 20 pares sellados de predictibilidad previa y desenlace posterior.
- Mantener Engine V5 y patterns_final_v14.json intactos.
- Si se rompe la separación de roles, se filtra un desenlace o falta un recibo, el caso no cuenta como ciego certificado.
- No rellenar slots con sujetos sintéticos, reevaluaciones ni entradas sin fuente primaria suficiente.

## Entrega del lote
Cada CXX conserva la estructura definida en PLAN_20_CASOS_MOTOR.md: entrada, compromiso, salida congelada, recibo y desenlace sellado bajo custodia separada. El registro del lote incluye matriz de roles y estado de cada slot.

## Estado al crear este protocolo
- Slots C01–C20: PENDIENTE.
- Casos históricos B-01/N-02/C-03/H-01: archivo de modelos, no corridas de motor.
- F006/Courbet: reevaluación, no caso nuevo.
- Ninguna modificación al motor ni a los patrones.
