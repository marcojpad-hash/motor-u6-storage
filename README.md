# motor-u6-storage

Almacenamiento común (privado) del motor U6 de predicción narrativa de Mj. Lo leen y escriben Claude, ChatGPT y Grok Bot. Funciona como lo que hacíamos con Notion, pero sin un modelo de lenguaje que coordine: las reglas están escritas en cada carpeta (`REGLAS.md`) y el historial lo lleva git.

## Carpetas

| Carpeta | Qué contiene |
|---|---|
| `motor/` | Motor U6 agnóstico (código, contratos, pruebas, calibración) y laterales en `motor/laterales/`. Sin corridas, sin vendor, sin evidencias. |
| `casos/` | Solo hashes de casos y entradas, la plantilla de caso nuevo y **resúmenes** de resultados (`casos/resultados/resultados.jsonl`). Nunca corridas completas. |
| `stinkbox/` | Tokens StinkBox deduplicados con conteo y procedencia (`tokens.jsonl`), índice de artefactos de origen y candidatos documentales. |
| `avances/` | Bitácora de cambios: quién, cuándo, qué cambió (antes → después), hashes y pruebas. |
| `scripts/` | `sincronizar_storage.py` (antes y después de cada corrida). |

## Cómo contribuye cualquier modelo

1. Antes de correr: `python3 scripts/sincronizar_storage.py antes` (hace `git pull`, muestra qué cambió en `motor/` y `stinkbox/`, verifica los hashes canónicos; sin red sigue en modo local).
2. Los cambios de código entran como **versiones nuevas** (archivo nuevo o lateral), nunca sobrescribiendo en silencio. Solo se suben archivos modificados.
3. Cada cambio va en un commit con descripción y una entrada en `avances/` con el formato "antes estaba así → ahora quedó así", diff legible por archivo/función y sha antes/después.
4. Después de correr: `python3 scripts/sincronizar_storage.py despues --corrida <DIR> --modelo "<Claude|ChatGPT|Grok Bot>"` sube solo el resumen de la corrida y los tokens StinkBox nuevos. Sin credenciales, deja parches JSONL en `_pendiente_subir/`.
5. Nada se borra ni se sobrescribe en silencio. El motor canónico y el catálogo nunca se tocan.

## Liviano

Sin binarios, sin `_vendor_buscador`, sin salidas de corrida. Las dependencias del buscador se instalan con `pip install ddgs primp lxml click` si no están las bibliotecas empacadas (ver `motor/motor/SPEC_BUSCADOR_AGNOSTICO.md`).
