# Corrida real de fábrica — traza 244
Fecha: 2026-10-30
Lote: F006_TRAZA_V2_R7
Caso sellado: CAL_F005_01_COURBET (Gustave Courbet)
Commit probado: fbf09612c39f35e69d48f26f75c6f2ee94388db9

## Resultado
La fábrica terminó el caso con código 0 y recibo COMPLETED. CEB terminó en VERIFIED_FLOW, sin anomalías. compuerta_caldero=OK y compuerta_piezas=OK. Los hashes del Engine canónico y del catálogo coincidieron antes y después.

## Evidencia
Ejecución: https://github.com/marcojpad-hash/motor-u6-storage/actions/runs/41020723134
Artefacto: https://github.com/marcojpad-hash/motor-u6-storage/actions/runs/41020427712/artifacts/12961710969
Input SHA-256: a81708648e0fe77f5a12ef24eb3a26553fa82cb427068de9b3530fe0dd638b5c
Resultado SHA-256: bd1da1cad157add7fdd860ec4a7404f13bedb232de057ce1afea751620502f3c
Duración: 14.069 s. Monte Carlo: 6,310 simulaciones; 9/9 observaciones convergieron.
Traza ejecutada: TRAZA_CAMPO_244_V2; 244 hipótesis y 2 vectores.
La pieza hipotesis_trayectoria_abierta_v1 quedó EXECUTED_AND_CONNECTED en CEB.

## Fallas y correcciones
1. El adaptador no encontraba V2 después de que la fábrica copiaba el runner a un directorio temporal. Se corrigió la búsqueda de la implementación entre los ancestros y se añadió una prueba que reproduce esa reubicación.
2. La primera corrida real falló por falta de NumPy en el entorno limpio. Se añadió NumPy a las dependencias del workflow.
3. CEB marcaba la pieza de hipótesis abiertas como declarada pero no observada. Se conectó la pieza al trazador activo y se marcó su salida final como terminal. R6 confirmó CEB VERIFIED_FLOW sin anomalías.

## Suite
8 pruebas aprobadas, 0 fallidas:
https://github.com/marcojpad-hash/motor-u6-storage/actions/runs/41019795987

## Resultado predictivo observado
H1=30_ambicion; H2=20_sacrificio_por_un_ideal.
Desenlace sellado: persecución, caer víctima, rebelión y arquetipo del rebelde.
Acierto H1, H2, conjunto y apuesta: 0. Destino real: ruptura; destino pronosticado: auge.
La ejecución técnica quedó resuelta; este caso fue un fallo de acierto predictivo y queda identificado como tal.

## Candados
Engine: 665c39a2861e58772522e91272563260d980908b1d4ab9f7092d3413d0c36082.
Catálogo: d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1.
Ambos permanecieron intactos.
