# codebase-memory-mcp en el motor U6

## Qué es

codebase-memory-mcp (DeusData/codebase-memory-mcp, licencia MIT) es un
servidor MCP local en un solo binario en C. Indexa un repositorio en un
grafo de conocimiento persistente (SQLite) y responde consultas
estructurales: buscar símbolos, seguir llamadas, leer fragmentos y ver
la arquitectura, sin volver a leer todos los archivos en cada pregunta.

No necesita API key. Todo corre en local: el índice, las consultas y el
servidor. El servidor hace una única comprobación de actualizaciones por
sesión contra el endpoint público de releases de su propio proyecto; no
envía datos del repositorio.

Versión instalada en la máquina de Pecas: **0.12.1** (release del
16 de octubre de 2026). Binario verificado con SHA-256 contra el
`checksums.txt` oficial de la release.

## Para qué sirve en este repo

El motor U6 tiene 638 archivos (código Python, contratos, casos,
informes, scripts). Con el grafo se puede preguntar, por ejemplo:

- Dónde vive el cableado de una pieza (`search_graph` por nombre).
- Qué llama a `correr_estandar.main` y qué llama ella
  (`trace_path` en ambas direcciones).
- Cómo se conectan el runner único, el Caldero, el filtro 017 y el
  filtro StinkBox (`get_architecture`).

El índice actual (7 de noviembre de 2026) tiene **13 531 nodos y
27 173 aristas**, se construyó en 12 segundos y no dejó fuera ningún
archivo analizable: 0 omitidos, 0 con parse parcial, 0 inutilizables.

La copia local que se indexó es un espejo de `main` reconstruido
archivo por archivo con la API de lectura de GitHub (638 archivos,
cada uno verificado por SHA contra la API). Falta solo
`stinkbox/tokens.jsonl` (17 MB), demasiado grande para esa API; el
grafo no lo necesita porque es un almacén de datos, no código.

## Instalación

En la máquina de Pecas el binario ya está en:

```text
~/workspace/codebase-memory-mcp/bin/codebase-memory-mcp
```

Para instalarlo en otra máquina Linux x86_64, descarga el archive de la
última release y verifica su checksum antes de extraerlo (no uses
`curl ... | bash` sin inspeccionar):

```bash
# Descarga desde https://github.com/DeusData/codebase-memory-mcp/releases
# Archivo: codebase-memory-mcp-linux-amd64.tar.gz + checksums.txt
sha256sum -c checksums.txt
tar xzf codebase-memory-mcp-linux-amd64.tar.gz --no-same-owner
./install.sh --dir <destino> --skip-config
```

La instalación con `--skip-config` no auto-configura ningún agente.
La activación del binario rechaza directorios de instalación con
permiso de escritura de grupo; usa un directorio con modo 755.

## Indexar este repo

Con el cliente MCP local (sin daemon permanente):

```bash
python3 ~/workspace/custom-connectors/custom.codebase-memory-mcp/bin/client.py \
  call-tool --name index_repository --arguments-file /tmp/cbm-args.json
```

Con este contenido en `/tmp/cbm-args.json`:

```json
{
  "repo_path": "/home/hatch/workspace/cbm-repos/motor-u6-storage",
  "mode": "full",
  "name": "motor-u6-storage"
}
```

El índice vive en `~/.cache/codebase-memory-mcp/` (un archivo
`.db` por proyecto). Vuelve a correr `index_repository` cuando el
repositorio cambie; el servidor no lo observa entre llamadas.

Estado del índice:

```bash
python3 ~/workspace/custom-connectors/custom.codebase-memory-mcp/bin/client.py \
  call-tool --name index_status --arguments-file /tmp/cbm-args.json
```

Con `{"project": "motor-u6-storage", "diagnostics": "summary"}`.

## Consultarlo

Ejemplos verificados contra este índice:

Buscar un símbolo:

```json
{
  "project": "motor-u6-storage",
  "query": "correr_estandar",
  "limit": 5
}
```

Devuelve, entre otros, `motor.correr_estandar.sha`,
`motor.correr_estandar._envolver`, `motor.correr_estandar._build`,
`motor.correr_estandar._fam` y `motor.correr_estandar.main` en
`motor/correr_estandar.py`.

Seguir una llamada:

```json
{
  "project": "motor-u6-storage",
  "function_name": "motor-u6-storage.motor.correr_estandar.main",
  "direction": "both",
  "depth": 2
}
```

Devuelve 44 llamados (entre ellos `sha`,
`_sanitize_json_contract`, `_continuity_result_payload`,
`_receipt_status` y `_declared_absent_hashes`) y 1 llamador.

Las llamadas se hacen con el mismo cliente:

```bash
python3 ~/workspace/custom-connectors/custom.codebase-memory-mcp/bin/client.py \
  call-tool --name search_graph --arguments-file /tmp/cbm-args.json
python3 ~/workspace/custom-connectors/custom.codebase-memory-mcp/bin/client.py \
  call-tool --name trace_path --arguments-file /tmp/cbm-args.json
```

Otras operaciones útiles: `search_code` (texto literal),
`get_code_snippet` (fuente de un símbolo), `get_file_outline`
(esquema de un archivo), `get_architecture` (vista general),
`query_graph` (Cypher de solo lectura), `list_projects`.

## Caveat honesto

El proyecto es pre-1.0 (versión 0.12.1) y tenía 560 issues abiertos
el 7 de noviembre de 2026. Su propio paper (arXiv:2603.27277) reporta
83% de calidad de respuesta frente a 92% de exploración manual
archivo por archivo, a cambio de unas 10 veces menos tokens y 2,1
veces menos llamadas a herramientas, medido en 31 repositorios reales.

Traducción práctica: el grafo responde rápido y barato a preguntas
estructurales, pero no sustituye leer el código cuando la respuesta
importa. Verifica siempre en el archivo fuente lo que el grafo afirme,
sobre todo antes de cambiar código.

## Notas

- El archivo `.mcp.json` de la raíz de este repo configura el servidor
  local para los clientes MCP que lo lean. La ruta del binario es la de
  la máquina de Pecas; ajústala si lo instalas en otro sitio.
- El grafo es solo de lectura: no modifica el motor, no toca el
  Engine V5 canónico (`motor/Engine_V5_CANONICO_SOLO.py`) ni el
  catálogo de 244 patrones (`motor/patterns_final_v14.json`). Es una
  herramienta de consulta, no una fuente de verdad del proyecto.
- Para afirmar una ejecución o interpretar resultados, sigue
  `PROTOCOLO_EJECUCION_Y_LECTURA_LLM.md`: el código inspeccionado no
  demuestra que se ejecutó. El grafo no cambia eso.
- No se suben al repo los archivos `.db` del índice. El índice es
  local y se reconstruye con `index_repository`.
