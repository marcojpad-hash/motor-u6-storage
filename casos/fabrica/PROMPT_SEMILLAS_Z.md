# Prompt para el LLM que escribe semillas (compuerta Z_trabajo)

Z_trabajo es el corte donde se para el caso. No es un año biográfico tipo "90 % de vida". En una pregunta de hoy, Z_trabajo es la fecha de hoy.

## Reparto ciego (obligatorio)
- **Preparador de la entrada** (p. ej., ChatGPT en una conversación NUEVA): solo escribe `semillas_lote_X.py` (lista `SEMILLAS_Z`). No pide, no ve y no escribe el final.
- **Custodio del destino** (Mj u otra conversación): escribe aparte `destinos_lote_X.py` (lista `DESTINOS`): familias, destino (auge/meseta/caida/ruptura), fuente y `prohibidas_post_Z` (palabras del final: lugar de prisión, "muere", "abdica", nombres del desenlace).
- La fábrica exige que `preparacion_ciega.custodio_destino` coincida con `DESTINOS[id].custodio`, que preparador y custodio sean distintos y que `vio_destino` sea false.

## Texto para pegar al LLM preparador
> Vas a escribir la ENTRADA de un caso para el motor. Z_trabajo = {AAAA-MM-DD}. modo_z = {historico | vivo}.
> 1. Solo puedes usar hechos ATESTIGUADOS que ya habían ocurrido en Z_trabajo o antes. Si conoces cómo termina la historia, NO lo uses, ni lo insinúes, ni lo elijas como pista.
> 2. No escribas nada en futuro ni predicciones ("será", "va a", "terminará", "finalmente", "más tarde", "probablemente", "will", "eventually").
> 3. No menciones ningún año posterior al de Z_trabajo.
> 4. Para cada corte, enlista cada afirmación en `evidencia` con: `afirmacion`, `source_url`, `source_date` (fecha de publicación de la fuente), `claim_date` (fecha del hecho, ≤ Z), `tipo_fuente` (primaria = publicada en o antes de Z; secundaria = publicada después) y `conocido_en_Z: "sí"`. Si un dato no se conocía en Z, quítalo.
> 5. En modo vivo, las secundarias tienen que ser copias congeladas: `web.archive.org/web/AAAAMMDD…` con fecha ≤ Z, o un permalink (`oldid=`) con `snapshot_date` ≤ Z. Nunca Wikipedia en vivo.
> 6. En modo histórico, las secundarias solo se aceptan con preparación ciega declarada.
> 7. Usa fechas completas (AAAA-MM-DD) cuando puedas. Una fecha parcial cuenta como el ÚLTIMO día de su periodo.
> 8. Tokens: solo del vocabulario de los 244, con pesos de 0,60 a 0,84.
9. Pistas LLM del Caldero (opcional, A5 2026-11-07): en cada sujeto puedes añadir `pistas_llm`: lista de `{"token": "...", "family": "<familia del catálogo 244>", "relevance": 0..1}`. Son arquetipos que propones como vecinos; el motor NO decide con ellas, solo las usa como traza y desempate, y pasan por el guardián. Prohibido: nombres o alias del sujeto, palabras de desenlace o futuro, años. Si una pista no pasa el guardián, la fábrica la descarta y lo deja en la auditoría de la entrada; la familia fuera del catálogo rechaza el lote.

## Comando
`python3 casos/fabrica/fabrica.py preparar-z semillas_lote_X.py destinos_lote_X.py`
Si una sola afirmación viola la compuerta, se rechaza el lote entero y no se escribe nada. Plantillas: `PLANTILLA_semillas_z.py` y `PLANTILLA_destinos_z.py`.
