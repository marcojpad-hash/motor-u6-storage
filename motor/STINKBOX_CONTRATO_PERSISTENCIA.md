# CONTRATO DE PERSISTENCIA DE TOKENS STINKBOX — v1.0

**Vigencia:** 2026-10-20  
**Propósito:** conservar fuera de los ZIP del motor los tokens emitidos por las corridas y detectar tokens nuevos o recurrentes que puedan señalar familias/arquetipos ausentes.

## 1. Separación obligatoria

`STINKBOX_PERSISTENTE/` es un almacén independiente. No vive dentro del ZIP del motor y no se sustituye al instalar una actualización. Los ZIP pueden incluir el lector y el contrato, pero no son la fuente maestra de la memoria acumulada.

Antes de ejecutar una actualización, conservar esta carpeta. Después de la corrida, importar la carpeta de resultados o el ZIP de entrega con `stinkbox_registry.py ingest <ruta>`. El proceso solo añade evidencia y actualiza índices derivados; no borra registros anteriores.

## 2. Qué se conserva

- Token normalizado y forma original cuando esté disponible.
- Caso, corte, eje, fuente, tipo de evento y fecha, cuando esos campos existan.
- Número de observaciones deduplicadas, casos distintos y cortes distintos.
- Primera y última detección.
- Procedencia del artefacto importado y SHA-256 para auditoría.
- Estado de revisión: `NUEVO`, `RECURRENTE`, `PENDIENTE_REVISION`, `EQUIVALENTE_UNICO`, `DESCARTADO_CONSERVADO` o `FAMILIA_CANDIDATA`.
- Relación con el catálogo conocida solo cuando exista evidencia explícita. No inferir equivalencias por similitud superficial.

## 3. Qué cuenta como token nuevo

Un token es `NUEVO` si no figura en el registro persistente previo. Que aparezca en `token_events`, `token_frequency`, `persistent_neighbor_tokens` o `tokens_signature` prueba que fue observado por esa fuente, no que sea una familia arquetípica nueva.

Los tokens de `fuera_catalogo` / `stinkbox_tokens_descubiertos.json` se marcan aparte como `PENDIENTE_REVISION` o con el estado explícito que aporte la corrida. Se reportan por separado para que no se mezclen con palabras de texto corriente capturadas por `lateral_features`.

## 4. No hacer automáticamente

- No incorporar tokens al catálogo canónico de 244 patrones.
- No modificar H1/H2, P/A/C, R732, FREEZE ni pesos del motor.
- No declarar una familia ausente solo porque apareció un token.
- No borrar tokens descartados: conservarlos para reconocer recurrencias y reabrir revisión si aparece evidencia nueva.
- No reemplazar el registro persistente con un archivo proveniente de una actualización ZIP.

## 5. Deduplicación e importación

- Artefactos idénticos (mismo SHA-256) no se importan dos veces.
- Eventos de tokens se deduplican por identidad estable derivada de caso, corte, token, fuente, tipo y timestamp cuando esté disponible.
- Si el artefacto cambia, solo los eventos nuevos se añaden; los anteriores permanecen.
- El registro maestro es `data/registro_tokens.json`; el log append-only es `data/eventos_tokens.jsonl`; el inventario de importaciones es `data/artefactos_importados.json`.
- Los reportes se regeneran desde el registro; no son la fuente maestra.

## 6. Salidas para análisis de familias

Cada importación actualiza:

- `reports/tokens_nuevos.csv`: tokens nuevos frente al registro persistente.
- `reports/tokens_fuera_catalogo.csv`: candidatos explícitos fuera de catálogo.
- `reports/tokens_recurrentes.csv`: tokens vistos en más de un caso.
- `reports/resumen_tokens.md`: totales y advertencias de interpretación.

La decisión de concebir/cablear una familia se toma revisando recurrencia, coactivación, contexto/cortes, procedencia y equivalencias; el script solo organiza evidencia.

## 7. Ubicación y respaldo

Guardar `STINKBOX_PERSISTENTE/` en la biblioteca/dispositivo o almacenamiento duradero independiente de las entregas ZIP. Mantener una copia de respaldo versionada. No usar el interior del ZIP, `/tmp` ni una carpeta de extracción temporal como almacén maestro.

## 8. Uso

```bash
python stinkbox_registry.py ingest /ruta/al/ZIP_o_carpeta_de_corrida
python stinkbox_registry.py report
python stinkbox_registry.py status
```

Para iniciar la memoria histórica, se importó la entrega unificada `U6_UNIFICADO_20261020.zip`. Esa importación es una línea base histórica, no una nueva corrida del motor.


## 9. Cableado automático U6

`correr_estandar.py` resuelve `STINKBOX_HOME` fuera del paquete motor y define `STINKBOX_STORAGE_ROOT` antes de importar el motor. Al terminar la corrida, importa automáticamente el directorio de ejecución y el almacenamiento persistente en el registro; el recibo incluye la etapa `stinkbox_persistent_registry_ingest`. Si esa etapa falla, la corrida no se declara con persistencia confirmada. Puede fijarse la ruta con `STINKBOX_HOME=/ruta/duradera`.

## 10. Candidatos documentales Black Mirror

Los 18 conceptos de `STINKBOX_BLACK_MIRROR_CANDIDATOS.json` se conservan en un registro separado de tokens observados. No se cuentan como tokens emitidos por corridas, no se consideran integrados al motor y no modifican el catálogo de 244. Los conceptos con estado documental `NO_VERIFICADO` permanecen pendientes.


## 11. Conteo de observaciones y evidencias

Si el mismo token del mismo caso y corte aparece tanto en el registro de descubrimiento como en el archivo de StinkBox, se conserva la procedencia de ambos artefactos como eventos de evidencia, pero se cuenta una sola observación caso/corte/token. Esto evita inflar recurrencias por duplicación entre componentes.


## 12. Vocabulario de búsqueda externa

Los términos extraídos de resultados web se reportan en `reports/tokens_vocabulario_externo.csv`. Pueden ser vocabulario útil para orientación, pero no son automáticamente tokens fuera de catálogo ni evidencia de que falte una familia. Para proponer una familia se requiere evidencia explícita fuera de catálogo o recurrencia contextual suficiente, no una palabra genérica que apareció en un resumen bibliográfico.


## 13. Checkpoint antes de subcorridas

El runner indexa el almacenamiento inmediatamente después de la corrida primaria, antes de los análisis de cortes retenidos y la escritura de ledgers. El recibo conserva `stinkbox_persistent_registry_primary_checkpoint` además de la importación final. Así, un timeout en etapas posteriores no deja los tokens de la corrida primaria sin indexar.
