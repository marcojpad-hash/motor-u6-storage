# Informe 2026-10-25 — CEB: cableado y smoke F002

Para Mj y ChatGPT. Español llano.

## 1. Para qué sirve el CEB
El CEB (registro de ejecución) existe para **encontrar dónde fallan las herramientas** del motor, de modo que los modelos las arreglen. Regla base: **todas las piezas deben ejecutarse**; ninguna es decorativa.

## 2. Qué se hizo hoy
- **Caldero de arquetipos + guardián** (`5abc402`): las pistas del LLM pasan por un guardián antes del sidecar; PRE-H reutiliza la búsqueda viva (ya no queda en API_PENDING).
- **Sincronización StinkBox → GitHub** (`5abc402`, `1df3cb9`): la fábrica sube tokens; corrida F002 dejó 18 481 observaciones.
- **Filtro de tokens** (`0895df0`): quita stopwords, boilerplate, números y URLs. `tokens.jsonl` pasó de 2741 a 2396.
- **Pistas de brechas por familia** (`0895df0`): reporte de familias faltantes contra el catálogo 244 (solo lectura; el catálogo no se tocó).
- **Honestidad del CEB** (`293b715`): estados reales del Caldero (EJECUTADO / INTENTADO_FALLIDO / NO_INVOCADO / OMITIDO_POR_CONDICION / SIMULADO_FIXTURE). Un fixture ya no se reporta como ejecutado.
- **Regla Mj "no decorativo / debe ejecutarse"** (`568d460` Caldero, `8a2aab4` TODAS las piezas): herramienta no ejecutada = FALLO_EJECUCION o REQUIERE_CONTRATO; la fábrica corta con exit 9.

## 3. Smoke F002 (Galilei / Pasteur)
- Las piezas reales se ejecutaron bien.
- Hubo una falsa alarma FALLO_EJECUCION_CALDERO: la compuerta contaba sidecars (RECIBO_EJECUCION, CEB_LEDGER) como piezas. Corregido en `df7ea53`. Smoke OK.

## 4. Qué falta
La predictibilidad todavía necesita **más casos ciegos** y cubrir las **familias faltantes**. El cableado ya no es el cuello de botella.

## 5. Commits clave
`5abc402`, `1df3cb9`, `0895df0`, `293b715`, `568d460`, `8a2aab4`, `df7ea53`

## 6. Cómo debe leer el repo ChatGPT (y cualquier modelo)
- **Nunca por ZIP/zipball.** Leer archivo por archivo con la API de GitHub / conector, o `git clone`.
- Empezar por [`CONTRATO_CARPETAS.md`](../CONTRATO_CARPETAS.md) y [`INSTRUCCIONES_CONTINUIDAD_CHATGPT.md`](../INSTRUCCIONES_CONTINUIDAD_CHATGPT.md).
- Detalle técnico: `avances/2026-10-25_*`, `avances/CEB_HONESTIDAD_CALDERO_20261025.md`, `avances/REGLA_MJ_HERRAMIENTAS_SE_EJECUTAN_20261025.md`, `docs/CEB_INVESTIGAR_Y_RESOLVER.md`.
