# 2026-10-25 — Filtro de tokens StinkBox / Caldero arquetipos v1 (GrokBot)

- Nuevo `motor/motor/filtro_tokens_arquetipos_v1.py`: descarta stopwords ES/EN, conectores, adverbios -mente, números/años, URLs, puntuación, tokens <4 letras, boilerplate de snippets (wikipedia, abstract, artículo…), cortes silábicos (conoci-miento). Conserva sustantivos/verbos/frases y compuestos (rivalidad_poder, ciudades-estado).
- `brechas()` compara contra catálogo 244 (`patterns_final_v14.json`, SOLO LECTURA) + `familias_tokens/` → tokens que aún no tenemos.
- `scripts/sincronizar_storage.py`: filtra al leer el StinkBox, al anexar y purga ruido previo en cada sync.
- `scripts/limpiar_tokens_stinkbox.py`: re-filtra `stinkbox/tokens.jsonl` y genera `stinkbox/REPORTE_FILTRO_TOKENS_<fecha>.md`.
- Limpieza: 2741 → 2396 tokens únicos (345 descartados). 1378 brechas vs catálogo.
- Tests: `motor/tests/test_filtro_tokens_arquetipos_v1.py` (4 OK).
- No se filtra en el Engine ni en el registro local (`stinkbox_registry`): el ruido se corta en la frontera hacia GitHub. Engine 665c39a2… y catálogo d827dcc3… intactos.
