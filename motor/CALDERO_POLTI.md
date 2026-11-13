# Caldero Polti — todas las partes

Repo: `marcojpad-hash/motor-u6-storage`, rama `alterno/cameo-pesos` (antes solo archivo local; subido al repo 2026-11-13). Caldero Polti es **una sola pieza con dos mitades y un puente**:

- **Polti**: las 36 situaciones dramáticas de Georges Polti, que ya viven dentro del catálogo 244 como familias numeradas.
- **Caldero II**: el runtime de búsqueda ciega de arquetipos (busca en la web sin saber quién es el sujeto) y sus guardianes.
- **El puente** (`puente_souriau_caldero_polti_v1.py`): junta por corte las seis funciones de Souriau + el cuadrante del monomito (Caldero) + las Polti activas, y mide sus cambios entre cortes.

Todo es lateral: `can_decide_H=False`. Nada escribe H1/H2, nada reordena candidatas, nada toca Engine V5 ni el catálogo 244.

> **Versión de cableado (2026-11-12, commit 78b9a9a4, rama alterno/reconexion-2a1):** el cableado del Caldero hace que las pistas LLM **sí reordenen dentro de la banda 020**, como cuarto criterio de desempate (solo dentro de la banda, nunca fuera de ella). La frase «nada reordena candidatas» era exacta antes del cableado y ya no lo es: el reordenamiento existe, pero está confinado a la banda y no escribe H1/H2, no toca Engine V5 ni el catálogo 244. `can_decide_H` sigue siendo `False`.

## 1. Polti — las 36 situaciones dramáticas

Georges Polti (1895) dijo que toda historia se reduce a 36 situaciones. En el motor, las 36 son **familias del catálogo 244** (claves `1_...` a `36_...`):

1. súplica · 2. salvación · 3. venganza del crimen · 4. venganza de parientes · 5. persecución · 6. desastre · 7. caer víctima · 8. rebelión · 9. audaz empresa · 10. rapto · 11. enigma · 12. obtención · 13. enemistad de parientes · 14. rivalidad de parientes · 15. adulterio homicida · 16. locura · 17. fatal imprudencia · 18. crímenes involuntarios de amor · 19. asesinato de un pariente no reconocido · 20. sacrificio por un ideal · 21. sacrificio por los parientes · 22. todo sacrificado por una pasión · 23. necesidad de sacrificar a los seres queridos · 24. rivalidad de superior e inferior · 25. adulterio · 26. crímenes de amor · 27. descubrimiento de la deshonra de un ser querido · 28. obstáculos para el amor · 29. un enemigo amado · 30. ambición · 31. conflicto con un dios · 32. celos equivocados · 33. error de juicio · 34. remordimiento · 35. recuperación de lo perdido · 36. pérdida de los seres queridos.

### Cómo se detectan — `sidecar_polti_caldero.py`

- **Capa A**: las 36 Polti y los arquetipos ya están en el 244 (el tablero). No se agrega nada nuevo.
- **Capa B**: el sidecar observa ese tablero + el R732 y produce señales para ANTES de H.
- Por corte, toma el Top5 de cada eje (P, A, C) y filtra las familias que empiezan con número (`^\d+_` = Polti) y las que empiezan con `arquetipo_`. La unión de los tres ejes es el tablero Polti del corte.
- **Transición** entre cortes consecutivos: para cada familia, `d = p_ahora − p_antes`. Si una familia no está en el Top5 de un corte, su p es 0 en ese corte (no se inventa). Reporta los 8 movimientos más grandes y las 3 que más suben y las 3 que más bajan.
- **Proyección**: inercia del último tablero — las 3 Polti y los arquetipos que persisten al final. No es H, es solo lo que sigue vivo.
- **Convergencia**: qué familias están a la vez en el tubo y en Polti, y cuáles solo se ven en Polti.
- Alimenta_H = NO. Uso declarado: "Señales para formular H. No son H."

## 2. Caldero II — la búsqueda ciega de arquetipos

Caldero es el runtime que busca **en la web** situaciones parecidas a la del caso, **sin saber quién es el sujeto**. Es el que hace que el motor sea agnóstico y no solo mire su propio catálogo.

### 2.1 El sidecar de búsqueda — `sidecar_caldero_busqueda_arquetipos.py`

- Entrada ciega (`ArchetypeInput`): tokens, patrones y familias del caso. **No debe contener identidad real.**
- La identidad real vive solo en `SelfMatchIdentity` (nombre, fechas, hechos únicos) y **solo la consume el filtro externo**; nunca se entrega al resultado ni a la búsqueda.
- Flujo: construir la consulta ciega → buscar → **filtro de self-match** (descarta cualquier fuente que hable del propio sujeto: si la búsqueda devuelve al mismo personaje, se tira) → vecinos (tokens vecinos) → auditoría.
- Resultado: `caldero_input` (tokens vecinos) + `audit` (qué fuentes crudas entraron, cuántas se descartaron por self-match). `feeds_predictor=True`, `feeds_H=False`, `can_decide_H=False`.

### 2.2 Los buscadores — `caldero_buscadores.py`

Caldero usa **un buscador, no un LLM**: entra una consulta ciega, salen filas. Proveedores configurables (`CALDERO_BUSCADOR=auto|ddgs|ddg|ddg_lite|bing|searx|wiki|google|exa|brave|serper|tavily|offline`). En la corrida de Napoleón corrió con **DuckDuckGo Lite**: 1 consulta, 8 fuentes, 155 tokens tras filtro, `llm: False`. El recibo guarda el SHA-256 de la consulta, la fecha UTC y el estado HTTP. Si la búsqueda no aporta nada, el motor sigue igual (en Napoleón: 0 exact, 0 alias, no discriminó).

### 2.3 El almacén de vecinos — `vecinos_caldero_neighbor_store.py`

Guarda persistente (JSONL + índice) de los vecinos que encontró Caldero por caso: la consulta, los tokens vecinos y la auditoría (fuentes crudas, descartadas por self-match, `identity_exposed_to_caldero: False`). Nunca toca lo canónico. Es la memoria de "qué casos parecidos ya se buscaron".

### 2.4 El guardián de pistas LLM — `guardian_pistas_llm_caldero_v1.py`

"Quemaduras ajenas": Caldero busca situaciones similares para aprender de otros. Antes de este guardián, las pistas del LLM (`case.caldero_llm_neighbor_hints`) se anexaban CRUDAS a los vecinos, sin pasar el filtro de identidad que sí pasan las fuentes web. El guardián filtra cada pista ANTES de que llegue al sidecar:
- **IDENTIDAD**: si contiene nombre/alias/término de identidad del caso → descartado.
- **FUTURO**: marcadores de desenlace / post-Z (outcome, desenlace, finalmente, fracaso, éxito, muerte...) → descartado.
- **CALENDARIO**: años 1000–2099 → descartado.
- **FORMA**: vacío, más de 60 caracteres, URL, sin letras → descartado.
Determinista, sin red, sin LLM. `can_decide_H=False`.

### 2.5 El runner genérico — `caldero_II_runner_generico.py`

Runner independiente del caso: recibe un JSON (`case_id`, `archetype`, `identity`, `search_sources`, `llm_neighbor_hints`), corre el sidecar, persiste en el almacén y escribe el resultado. La identidad solo se usa en self-match; la consulta Caldero es ciega.

### 2.6 Zoom-out Acero — `caldero_zoomout_acero_v0_1.py` (experimental)

Idea en prueba: traza local de transición (escala Caldero) → vector + velocidad/dirección por corte → zoom OUT sobre toda la situación → perfil estructural acumulado → **ACERO**: un límite/nombre fuerte para la región que sobrevive → el siguiente corte prueba si esa región se contrae o se expande. **No es la implementación canónica de Caldero II**; es un proxy experimental hasta que se cablee el artefacto ejecutable.

## 3. Souriau — las seis funciones

Étienne Souriau: toda obra dramática se reparte entre seis funciones. En el motor son: **león, sol, tierra, marte, balanza, luna**.

### 3.1 El reparto — `marco_funciones_souriau.py`

`distribuir(cuts)` reparte los tokens de cada corte entre las seis funciones. El modo por defecto es `personajes_016` (por personajes del corte); la variante posicional anterior (león = P[:5], sol = P[:3], tierra = C[:5], marte = A[:5]) era un artefacto — sol quedaba casi siempre dentro de león — y quedó solo como variante medible (`SOURIAU_FUNCIONES_016=posicional`). También reporta la **inercia**: qué tokens de león pasan a marte en el corte siguiente (el protagonista que se vuelve antagonista) y si el reparto quedó quieto.

### 3.2 El marco 7783 — `marco_7783.py`

Una **zona** es un reparto de las seis funciones. Cada función tiene un estado por corte:
- `0 = vacía` (sin tokens), `1 = presente`, `2 = cúmulo` (la función aparece en un cúmulo).
- La zona se codifica en base 3 sobre las seis funciones: `zona = ((((e1)·3 + e2)·3 + e3)·3 + e4)·3 + e5)·3 + e6) mod 7783`.
- Como cada función solo tiene 3 estados, solo hay **3^6 = 729 zonas alcanzables** de las 7783. La regla que lleva las seis funciones al espacio completo 7783 **no está definida en disco: PENDIENTE de la regla de Mj** (no se inventa).
- `visitar` suma **calor**: cada vez que un corte cae en una zona, esa zona gana 1 de calor (persistente en `zonas_7783.json`). Las 8 zonas más calientes se reportan. `can_decide_H=False`.

## 4. El monomito — el círculo de Campbell en 4 cuadrantes

`plugin_circulo_monomito_v2.py` — lente lateral, no patrón. No toca Engine ni el catálogo.

- **Q1 Separación (pasos 1–3)**: mundo ordinario, llamada a la aventura, rechazo de la llamada. Pregunta: origen.
- **Q2 Descenso (pasos 4–6)**: encuentro con el mentor, cruce del primer umbral, pruebas/aliados/enemigos. Pregunta: con qué, contra quién.
- **Q3 Ordalía (pasos 7–9)**: acercamiento a la cueva interior, prueba suprema, recompensa. Pregunta: dónde se rompe.
- **Q4 Retorno (pasos 10–12)**: camino de regreso, resurrección/transformación, retorno con el elixir. Pregunta: qué queda.
- Las listas Q1–Q4 son **candidatas, no asignación exclusiva** (R1). La posición real se resuelve por co-ocurrencia + pregunta activa (R2). Ciclo nuevo cuando reaparece el mundo ordinario (R4).
- **Catarsis**: cierre en Q4 por conexión contextual con otro hilo (anagnórisis/peripecia).
- Hilos que sigue: formación, desafío, sombra/consumo, vínculo (cada uno con sus tokens ancla).

## 5. El puente — Souriau + Caldero + Polti en un solo vector

`puente_souriau_caldero_polti_v1.py` (PATCH 009, 2026-10-06). Lo consume la trazabilidad (`sidecar_trazabilidad_temporal`, campo aditivo) desde el hub `laterales_unico_v1`.

Por corte construye un vector de **46 dimensiones**:
- 6 estados de las funciones Souriau (0 vacía / 1 presente / 2 cúmulo).
- 4 bits de cuadrante Caldero (Q1–Q4 activos).
- 36 bits de Polti activas (1–36).
- Además: zona 7783 del corte, calor acumulado de esa zona en el caso, cúmulos y pares en cúmulo, y la **discrepancia entre agentes**: `|e_a − e_b|` por cada par de las seis funciones (15 pares) — cuánto discrepan los seis agentes dentro del corte.

Entre cortes consecutivos reporta los **deltas**:
- Qué funciones cambian (de qué estado a qué estado) y la distancia de Hamming.
- Transición de zona y **revisita** (si el corte vuelve a una zona ya visitada).
- Qué cuadrantes entran y cuáles salen.
- Qué Polti entran y cuáles salen.
- La regla que lleva las seis funciones al espacio completo 7783 sigue pendiente (ver 3.2).

## 6. Cómo se conecta (el flujo)

1. El motor corre los cortes y produce P/A/C + R732.
2. El sidecar Polti lee el Top5 de cada eje y saca las Polti y arquetipos por corte, sus transiciones y su proyección.
3. Caldero busca en la web (ciego) y deja vecinos + auditoría; el guardián filtra las pistas LLM antes de que entren.
4. Souriau reparte los tokens en seis funciones; marco_7783 calcula la zona y suma calor.
5. El monomito resuelve el cuadrante por corte.
6. El puente junta todo en el vector de 46 por corte + deltas entre cortes.
7. La trazabilidad temporal lo consume como campo aditivo; el hub `laterales_unico_v1` lo distribuye. Nada de esto decide H: son señales para formular H.

## 7. Ejemplo concreto: Napoleón (corrida 2026-11-11)

Del resultado real (`motor/RESULT_NAPOLEON_PRUEBA.json`, features `polti_caldero` y `caldero_busqueda_arquetipos`):

- **C1_1799** (ascenso): `30_ambicion`, `12_obtencion`, `9_audaz_empresa`.
- **C2_1805** (Austerlitz): las mismas tres. Transición C1→C2: `12_obtencion` sube (+0,0937), `9_audaz_empresa` baja (−0,0213), `30_ambicion` baja (−0,0053). El arquetipo del gobernante sube (+0,1064).
- **C3_1812** (Rusia): aparece **`31_conflicto_con_un_dios` de la nada (0 → 0,7404, +0,7404)** y desaparece `9_audaz_empresa` (0,6918 → 0). El giro de la historia está ahí: la audaz empresa se apaga y entra el conflicto con un dios. Por eso H1 salió `31_conflicto_con_un_dios`.
- **Proyección** (inercia del último tablero): `30_ambicion`, `31_conflicto_con_un_dios`, `12_obtencion`; arquetipo persistente: `arquetipo_el_gobernante`.
- **Búsqueda Caldero**: DuckDuckGo Lite, 1 consulta, 8 fuentes, 155 tokens tras filtro. Resultado: 0 exact, 0 alias, no discriminó — la búsqueda no aportó nada al ranking. El motor siguió siendo agnóstico.
- **Puente**: zonas [0, 3] (2 transiciones, 1 revisita); discrepancia media 1,0; cúmulos 0; cuadrante presente en 3/3 cortes; Polti en 3/3. Ojo: en esta corrida las seis funciones Souriau salieron **vacías** (estado 0 en las seis), así que la zona fue 0 — el lado Souriau del puente no tuvo dato en Napoleón; el lado Caldero/Polti sí disparó.

> Nota 2026-11-13: en la corrida fresca Z90 de Napoleón (10 cortes, 2026-11-11), `funciones_souriau` se ejecuta y produce valores, pero los conjuntos salen casi vacíos (tamaño 0 en la mayoría de los cortes, 1 en uno, región `AUTORIDAD_1`). Habla poco, no está mudo del todo.

## 8. Qué NO hace Caldero Polti

- No decide H1/H2. Todo el apartado es `can_decide_H=False`, `Alimenta_H=NO`. Desde el cableado del 2026-11-12, las pistas LLM reordenan dentro de la banda 020 como cuarto criterio (ver nota de versión arriba); sigue sin decidir H ni tocar lo canónico.
- La búsqueda Caldero no sabe quién es el sujeto: si devuelve al propio personaje, el filtro de self-match la descarta.
- La proyección Polti es inercia, no predicción: dice qué sigue vivo en el último tablero, no qué va a pasar.
- El marco 7783 no está completo: solo 729 zonas son alcanzables y la regla para el espacio entero está pendiente de Mj.
- El zoom-out Acero es experimental, no canónico.
