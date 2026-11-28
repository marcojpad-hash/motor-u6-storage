# Corrección CEB: clasificación de fallo opcional

**Fecha:** 2026-11-27, corte 22:37 CDMX  
**Rama:** alterno/cameo-pesos

## Diagnóstico

FlowVerifier convertía todo evento STAGE_ERROR en estado FAILED. El reporte de ejecución distingue un componente opcional mediante status=OPTIONAL_STAGE_FAILED y required=false, pero esa semántica no se aplicaba al resumen CEB. El resultado era INCOMPLETE aun cuando el componente no era obligatorio.

## Cambio

- Solo cuando status=OPTIONAL_STAGE_FAILED y required=false, los stages fallidos correspondientes se clasifican FAILED_OPTIONAL_STAGE.
- Se conserva la anomalía explícita OPTIONAL_STAGE_FAILED y su error.
- Si el stage opcional no aparece en el ledger, se registra OPTIONAL_STAGE_FAILURE_NOT_OBSERVED.
- El estado global pasa a VERIFIED_FLOW_WITH_ANOMALIES; nunca a VERIFIED_FLOW sin anomalías.
- Fallos required=true o sin required=false permanecen FAILED y producen INCOMPLETE.

## Pruebas y CI

- Se agregaron dos regresiones en motor/tests/test_ceb_closed_audit_hook.py: fallo opcional no bloqueante y fallo requerido bloqueante.
- Se amplió .github/workflows/test-motor-contracts.yml para incluir el runtime CEB y su suite en paths y pytest.
- Primer intento del workflow: run 46109075723 terminó failure sin jobs por una línea YAML mal ubicada. Se corrigió la lista de rutas y la continuación del comando pytest.
- Verificación final: run 46109112168, job runner-contract SUCCESS, 138 passed in 84.46 s.
- Regeneración de manifiestos: CI ejecutó motor/scripts/regenerar_manifestos_trabajo.py y subió artifact 15248309793. El SHA-256 verificado del runtime CEB es 25935b543556ccf4f309a92b9fdea6111b7c85e4850d74b377998bad33e81e7a.

## Límites

- Es una corrección de semántica del observador CEB; no altera RESULT, RECIBO, H1/H2, ranking, pesos ni motor canónico.
- No se ejecutó una cohorte nueva ni se incrementó n. No se abrió custodia, destinos ni evidencia congelada.
- ULTIMO_ESTADO.json y ULTIMO_ESTADO.md siguen siendo snapshots atrasados; el último registro visible en ellos es del 10-nov. La evidencia de este corte es el run, sus logs y el artifact de Actions.
