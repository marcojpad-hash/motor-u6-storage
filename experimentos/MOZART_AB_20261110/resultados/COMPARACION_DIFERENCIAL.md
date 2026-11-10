# Mozart — comparación A/B

- A: plugins disponibles + Caldero II 2.0; búsqueda estática explícita con fuentes históricas pre-Z90, ejecutada también por caldero_II_runner_generico.py.
- B: mismos cortes, motor y semilla; Caldero II OFF. Se desactivan búsqueda, runner genérico, memoria de vecinos, cuadrantes Monomito y zoom-out Caldero solo en la copia aislada de B.
- Las demás capas y plugins permanecen; sidecar Polti-Caldero se conserva como lente independiente del Caldero II objeto de esta ablación.
- Monte Carlo: ON en ambas.
- Input: diez cortes recuperados de RESULT histórico; el input fuente independiente no apareció en Library/paquete.
- Z90: 1788-05-04.
- Fuentes Caldero: siete fuentes históricas; src8 se excluyó porque contiene el estreno vienés del 7 de mayo de 1788, posterior al Z90.

## Resultados
- H1 A: schwartz_10_autodireccion
- H1 B: schwartz_10_autodireccion
- H2 A: utopia_mentalidad_liberal
- H2 B: utopia_mentalidad_liberal
- H1 idéntica: True
- H2 idéntica: True

## Integridad
- Motor V15.3 SHA-256: ef9aad3bcbd01a00ac80a5b1face55913b527d470042f710d01d4838c4e3edf3
- Engine V5 SHA-256: 665c39a2861e58772522e91272563260d980908b1d4ab9f7092d3413d0c36082
- Patterns SHA-256: d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1 (244 patrones)
- Mismo motor/Engine/patterns A/B: True

## Estados de componentes
- A: {"ABSORBIDO_EN_GUARDIA_TRANSVERSAL": 1, "ERROR": 1, "EXECUTED": 50, "EXECUTED_DIAGNOSTIC": 1, "EXECUTED_FIXTURE": 2, "EXECUTED_SIN_HALLAZGOS": 1, "EXECUTED_SIN_SENAL": 3, "EXECUTED_WITH_CONCLUSION": 1, "HUB_ACTIVA": 4, "HUB_ACTIVA_MUDA": 2, "NOT_APPLICABLE": 1, "PRESENTE": 1, "RESUELTO_OPERACIONALMENTE": 1, "SIN_PREFIJO_EN_INPUT": 1, "SUPERADA": 1}
- B: {"ABSORBIDO_EN_GUARDIA_TRANSVERSAL": 1, "EXECUTED": 47, "EXECUTED_DIAGNOSTIC": 1, "EXECUTED_SIN_HALLAZGOS": 1, "EXECUTED_SIN_SENAL": 3, "EXECUTED_WITH_CONCLUSION": 1, "HUB_ACTIVA": 3, "HUB_ACTIVA_MUDA": 3, "NOT_APPLICABLE": 1, "NOT_AVAILABLE": 1, "PLUGIN_SALTADO": 3, "PRESENTE": 1, "RESUELTO_OPERACIONALMENTE": 1, "SIN_PREFIJO_EN_INPUT": 1, "SKIPPED_INTERNAL_ANALYSIS": 2}
Los componentes omitidos, ausentes o con error permanecen etiquetados así en TRAZA_PLUGINS.json.
