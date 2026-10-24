# Reglas de `stinkbox/`

1. **Solo agregar** (append-only): cada token nuevo entra con procedencia (sha256 del artefacto de corrida y fecha).
2. Si el token **ya existe, se aumenta su conteo** y se añade la procedencia; no se repite la línea.
3. **Nunca borrar.**
4. Los tokens **fuera de catálogo viven aquí** hasta ser revisados.
5. **StinkBox no decide H.**
6. Archivos: `tokens.jsonl` (un token por línea: token, conteo, eventos_evidencia, estado, casos, fuentes, ejes, procedencia), `artefactos_procedencia.json` (sha256 → ruta original y fecha), `familias_candidatas_documentales.json` (candidatos de literatura; no son tokens observados), `MANIFIESTO_EXPORT.json`.
7. Se actualiza con `scripts/sincronizar_storage.py despues`, nunca a mano sin entrada en `avances/`.
