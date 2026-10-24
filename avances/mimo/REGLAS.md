# Reglas de `avances/mimo/` — revisión diaria con Xiaomi MiMo

- Script: `scripts/revision_mimo.py` (solo stdlib). Comando diario:
  `cd motor-u6-storage && git pull --rebase && python3 scripts/revision_mimo.py`
- Endpoint: `https://api.xiaomimimo.com/v1/chat/completions` (OpenAI-compatible, header `api-key`).
  Modelo por defecto: `mimo-v2.6-flash` (alternativas: `mimo-v2.6-pro`, `mimo-v2.6-pro-ultraspeed`).
  Fuentes: https://mimo.mi.com/docs/en-US/api/chat/openai-api · https://mimo.mi.com/docs/quick-start/first-api-call · https://mimo.mi.com/models/en-US/mimo-v2.6-flash
  (Token Plan: `MIMO_BASE_URL=https://token-plan-cn.xiaomimimo.com/v1` con llave `tp-...`.)
- Llave solo por variable de entorno `MIMO_API_KEY`. Nunca se sube al repo.
- Sin commits nuevos o sin llave → sale con 0 sin llamar.
- Tope diario: `MIMO_TOPE_DIARIO` (default 200000 tokens). Diff recortado a `MIMO_MAX_CHARS` (default 24000).
- Alto total después del 2026-12-31.
- `--dry-run`: muestra qué mandaría; no llama ni escribe.
- Salidas: `AAAA-MM-DD_revision.md` (shas + tokens + revisión), `uso.json` (bitácora), `.ultimo_sha` (último revisado).
- El diff enviado excluye `motor/` y `casos/` (solo aparecen en `--stat`). El script nunca modifica el Engine canónico, los 244 patrones ni sus hashes.
- Las revisiones son opinión de MiMo: no se aplican cambios automáticamente.
- Pruebas offline: `python3 -m pytest -q tests/test_revision_mimo.py`.
