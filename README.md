> **MEMORIA COMPARTIDA OBLIGATORIA:** Antes de cualquier trabajo, cualquier modelo debe leer [AGENTS.md](AGENTS.md), [el protocolo transversal](https://github.com/marcojpad-hash/memoria-compartida/blob/main/PROTOCOLO_MEMORIA_COMPARTIDA_OBLIGATORIA.md) y [el índice de memoria](https://github.com/marcojpad-hash/memoria-compartida/blob/main/INDICE.md); consultar los hechos pertinentes y sincronizar los hechos durables al terminar. No empezar desde la memoria conversacional.

# motor-u6-storage


 > **Contrato transversal obligatorio para todos los modelos:** [Contrato de trabajo multi-modelo](https://github.com/marcojpad-hash/orquestador-central/blob/main/docs/CONTRATO_TRABAJO_MULTI_MODELO.md). Declarar capacidades reales antes de asumir permisos o ejecución.
> **FeedMe actualizado:** abre primero [`FEEDME_ACTUALIZADO.md`](FEEDME_ACTUALIZADO.md). Centraliza arranque, contratos, dudas, bloqueos, decisiones y resoluciones. Después sigue [`INICIO_SESION_CHATGPT.md`](INICIO_SESION_CHATGPT.md) y [`LLM_STARTUP_SIDECAR.md`](LLM_STARTUP_SIDECAR.md).
> **Para modelos (ChatGPT, Claude, Grok Bot):**
> - Lee primero [`CONTRATO_CARPETAS.md`](CONTRATO_CARPETAS.md): qué hay en cada carpeta.
> - Última auditoría: [`informes/2026-10-31_AUDITORIA_CONTINUIDAD_Y_ESTADO.md`](informes/2026-10-31_AUDITORIA_CONTINUIDAD_Y_ESTADO.md).
- Mapa de versiones y hashes: [`docs/MAPA_VERSIONES_Y_AUTORIDAD.md`](docs/MAPA_VERSIONES_Y_AUTORIDAD.md).
> - Continuidad: [`INSTRUCCIONES_CONTINUIDAD_CHATGPT.md`](INSTRUCCIONES_CONTINUIDAD_CHATGPT.md).
> - **Antes de afirmar una ejecución o interpretar resultados, aplica [`PROTOCOLO_EJECUCION_Y_LECTURA_LLM.md`](PROTOCOLO_EJECUCION_Y_LECTURA_LLM.md).** Lee el recibo junto al JSON de salida; el código inspeccionado no demuestra que se ejecutó.
> - **No uses ZIP/zipball.** Lee archivo por archivo con la API de GitHub/conector o `git clone`.
Almacenamiento común (privado) del motor U6 de predicción narrativa de Mj. Lo leen y escriben Claude, ChatGPT y Grok Bot. Funciona como lo que hacíamos con Notion, pero sin un modelo de lenguaje que coordine: las reglas están escritas en cada carpeta (`REGLAS.md`) y el historial lo lleva git.

## Carpetas

| Carpeta | Qué contiene |
|---|---|
| `motor/` | Motor U6 agnóstico (código, contratos, pruebas, calibración) y laterales en `motor/laterales/`. Sin corridas, sin vendor, sin evidencias. |
| `casos/` | Solo hashes de casos y entradas, la plantilla de caso nuevo y **resúmenes** de resultados (`casos/resultados/resultados.jsonl`). Nunca corridas completas. |
| `stinkbox/` | Tokens StinkBox deduplicados con conteo y procedencia (`tokens.jsonl`), índice de artefactos de origen y candidatos documentales. |
| `avances/` | Bitácora de cambios: quién, cuándo, qué cambió (antes → después), hashes y pruebas. |
| `informes/` | Resúmenes por sesión para Mj y modelos. |
| `docs/` | Documentos estables de método. |
| `scripts/` | `sincronizar_storage.py` (antes y después de cada corrida). |

## Cómo contribuye cualquier modelo

1. Antes de correr: `python3 scripts/sincronizar_storage.py antes` (hace `git pull`, muestra qué cambió en `motor/` y `stinkbox/`, verifica los hashes canónicos; sin red sigue en modo local).
2. Los cambios de código entran como **versiones nuevas** (archivo nuevo o lateral), nunca sobrescribiendo en silencio. Solo se suben archivos modificados.
3. Cada cambio va en un commit con descripción y una entrada en `avances/` con el formato "antes estaba así → ahora quedó así", diff legible por archivo/función y sha antes/después.
4. Después de correr: `python3 scripts/sincronizar_storage.py despues --corrida <DIR> --modelo "<Claude|ChatGPT|Grok Bot>"` sube solo el resumen de la corrida y los tokens StinkBox nuevos. Sin credenciales, deja parches JSONL en `_pendiente_subir/`.
5. Nada se borra ni se sobrescribe en silencio. El motor canónico y el catálogo nunca se tocan.

## Liviano

Sin binarios, sin `_vendor_buscador`, sin salidas de corrida. Las dependencias del buscador se instalan con `pip install ddgs primp lxml click` si no están las bibliotecas empacadas (ver `motor/motor/SPEC_BUSCADOR_AGNOSTICO.md`).
