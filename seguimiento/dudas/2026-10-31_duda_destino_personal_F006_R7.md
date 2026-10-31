# Duda técnica: error de destino en F006 R7

## Pregunta concreta
¿Por qué la apuesta de destino personal marcó \`auge\` cuando el desenlace sellado de Courbet fue \`ruptura\`, aunque el set abierto y el escenario principal acertaron?

## Evidencia
- Lote: \`F006_TRAZA_V2_R7\`, fecha 2026-10-30.
- Caso: \`CAL_F005_01_COURBET\`; es la misma entrada/hash que F005, no un caso independiente.
- H1 \`30_ambicion\`: fallo. H2 \`20_sacrificio_por_un_ideal\`: fallo.
- Set abierto: acierto; escenario principal \`CONTINUIDAD_ASCENDENTE\`: acierto.
- Destino apostado: \`auge\`; real: \`ruptura\`; acierto exacto: 0; polaridad: 0.
- Evaluación de peso 0: n=1, muestra insuficiente (<10); no elegir peso. El peso no fue aplicado por el motor.
- \`predictibilidad_021\` indica que la calibración predictiva requiere al menos 20 pares sellados de predictibilidad previa y desenlace posterior. La referencia histórica de 15 biografías/121 predicciones corresponde al predictor lateral de trayectorias, no al motor V15.3 completo.

## Comprobaciones
- Recibo de ejecución COMPLETED.
- Engine V5 SHA-256 665c... y catálogo 244 SHA-256 d827... coinciden.
- Monte Carlo ejecutado: 6,310 simulaciones, 9/9 llamadas convergentes.
- CEB Caldero/piezas: OK.
- No hay base para ajustar el motor a partir de esta repetición.

## Próximo protocolo
1. No reutilizar Courbet como caso nuevo.
2. Incorporar casos independientes con nuevo \`case_id\`, freeze Z, input y desenlace sellados por separado.
3. Registrar antes del desenlace H1/H2, set, escenario, destino y predictibilidad estructural.
4. Mantener el motor canónico y los patrones congelados.
5. No elegir peso hasta contar con al menos 10 casos independientes para esa comparación; no calibrar \`predictibilidad_021\` hasta reunir al menos 20 pares predictibilidad/desenlace.
6. Reportar por separado acierto de H1, H2, set, escenario, destino exacto y polaridad. No mezclar métricas.

## Estado
Pendiente de nueva muestra independiente. No se propone cambiar el modelo ni reinterpretar el resultado de Courbet.
