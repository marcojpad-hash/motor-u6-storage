# Antecedentes de motores — archivo histórico

Esta carpeta conserva copias byte-a-byte (contenido UTF-8 recuperado por GitHub) de los tres componentes de motor enumerados en `docs/CONTINUIDAD_INVESTIGACION_U6_2026-11-04.md`.

## Alcance

- Son copias de consulta y trazabilidad; no sustituyen los archivos fuente.
- No constituyen un paquete autónomo ejecutable.
- No se modificó ningún archivo fuente ni se alteró el motor canónico.
- El catálogo de 244 patrones no se copia aquí: no es un motor.
- La rama operativa de U6 es `alterno/cameo-pesos`; `main` permanece SOLO_CONSULTA.

## Inventario y procedencia

| Componente | Archivo fuente | Blob SHA fuente |
|---|---|---|
| Engine V5 canónico protegido | `motor/motor/Engine_V5_CANONICO_SOLO.py` | `9f332bd799b3f32e5d16665d187c066e5b0311d3` |
| V15.3 nativo | `motor/motor/MOTOR_V15_3_NATIVO_V0_9_UNICO.py` | `c0702138f51bef49348bc558b6c96b5bf0a6fce5` |
| V15.3 integrado | `motor/motor/MOTOR_V15_3_UNICO_20260927.py` | `9aed52a83069447163969836f7c61666de1d5173` |

Cada copia debe conservar el mismo blob SHA que su fuente. Estos hashes son identificadores Git de blob, no SHA-256.

## Autoridad

La selección del Engine V5 canónico y el candado continúan gobernados por `motor/ACTIVE_ENGINE_SELECTION.json` y `motor/CANDADO_ENGINE.json`. Las copias de esta carpeta no participan en la selección ni en la ejecución del motor.
