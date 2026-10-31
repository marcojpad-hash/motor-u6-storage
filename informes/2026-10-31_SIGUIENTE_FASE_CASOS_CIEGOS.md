# Motor U6 — siguiente fase de validación independiente

Fecha: 2026-10-31  
Alcance: exclusivamente Motor U6 / V15.3. No incluye CAPCOT.

## Estado comprobado

- La auditoría del 31-oct documenta F006 R7 como corrida recuperada y persistida, con Engine V5 y catálogo 244 intactos.
- F006 R7 repite `CAL_F005_01_COURBET` con el mismo `input_sha256` de F005. Es reevaluación, no muestra independiente.
- Resultado mixto: H1 y H2 fallaron; set abierto y escenario principal acertaron; destino personal predijo auge y el desenlace fue ruptura.
- La evaluación del peso tiene n=1 y declara muestra insuficiente. No cambiar pesos ni lógica con esa evidencia.
- El plan C01–C20 continúa pendiente. Los cuatro registros históricos B-01/N-02/C-03/H-01 son freezes de modelos, no corridas del motor.

## Corrección metodológica incorporada

Se creó [PROTOCOLO_CUSTODIA_INDEPENDIENTE.md](../casos/ciegos/PROTOCOLO_CUSTODIA_INDEPENDIENTE.md) para separar selector de cohorte, preparador Z, custodio independiente, runner y auditor. La regla central es que preparador y custodio no pueden ser el mismo actor para un caso. Si no existe separación real, el caso se clasifica como ensayo metodológico, no como ciego certificado.

El protocolo no altera el Engine V5, el catálogo de 244 patrones, gate Z ni los resultados existentes.

## Trabajo que sigue

1. Acordar una fuente/cohorte de sujetos independientes y un selector que no formule predicciones.
2. Asignar un preparador Z y un custodio distinto. El custodio mantiene destinos, desenlaces y lista negra fuera del alcance del preparador y del runner.
3. Preparar C01–C20 con evidencia primaria fechada hasta Z y ejecutar `preparar-z` con los dos paquetes separados.
4. Comprometer SHA-256 de entrada, destino, desenlace, Engine V5 y patrones antes de correr.
5. Ejecutar, congelar salida y recibo, y abrir desenlaces solo tras verificar el compromiso.
6. Evaluar H1, H2, set, escenario, destino exacto y polaridad por separado.

## Umbrales

- Al menos 10 casos independientes para comparar pesos.
- Al menos 20 pares previos/posteriores sellados para calibrar `predictibilidad_021`.
- Ninguna reevaluación del mismo input incrementa n.

## Bloqueo real

La infraestructura de fábrica y el contrato de sellado ya están documentados. Lo que falta no es otra modificación al motor: faltan 20 entradas independientes con fuentes válidas y una separación verificable entre quien prepara Z y quien custodia el desenlace. No se fabrican sujetos ni etiquetas para llenar los slots.

## Estado

- Protocolo de custodia: creado y releído desde GitHub.
- Motor canónico y patrones: sin cambios.
- Casos C01–C20: pendientes.
- Próxima acción: preparar cohorte y handoff a custodio independiente; ejecutar solo cuando la separación de roles esté demostrada.
