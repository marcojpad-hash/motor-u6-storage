# CI — regresiones de salida humana y verificador

Fecha: 2026-11-27 (CDMX)  
Rama: `alterno/cameo-pesos`

## Cambio ejecutado

Se amplió `.github/workflows/test-motor-contracts.yml` para que los cambios en los módulos de salida y verificación activen el workflow y para ejecutar también:

- `motor/tests/test_cableado_respuesta_humana.py`
- `motor/tests/test_cableado_verificador.py`

Se añadieron los dos módulos correspondientes al registro de hashes del job. No se modificó lógica de predicción, motores canónicos, catálogo, pesos ni evidencia congelada.

## Verificación

- Commit: `bc8b41f13422ab4a6b191cf826dd30732fb06aec`
- GitHub Actions: [run 46096344973](https://github.com/marcojpad-hash/motor-u6-storage/actions/runs/46096344973)
- Resultado: `success`
- Pruebas: `123 passed in 86.40s`
- Manifiestos: regeneración de lectura y artefacto de verificación completados por el workflow.

Este registro acredita únicamente la ampliación de cobertura CI y la ejecución de esas pruebas; no acredita calibración ni ejecución de casos independientes.
