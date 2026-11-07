# 2026-11-07 — Pecas (Muse)

## Qué cambió

Cierre del cableado pendiente de la automation A5 (documentado en
`docs/HANDOFF_MOTOR_GROK.md` y `docs/SCRIPT_AUTOMATIONS_GROK_MOTOR.md`):
los 5 ítems quedan cableados en el runner único, la fábrica, el sidecar del
Caldero y los scripts del StinkBox, con pruebas nuevas y documentación del
sesgo de continuidad. Rama: `a5-cableado-20261107`. HEAD de partida: `9de8612a`.

Correcciones a la premisa (verificadas en el código antes de afirmar nada):
- El cierre 017 NO estaba "solo en tests": `consulta_dirigida_v1` YA estaba
  cableada en `motor/correr_estandar.py:569-587`. Lo que faltaba era el
  `filtro_entrada_dirigida` en cualquier sitio y la `consulta_dirigida`
  dentro del runner único.
- La `consulta_dirigida` NO se duplicó dentro de `run()`: ya vive en
  `correr_estandar.py` y duplicarla aplicaría sus preguntas dos veces en la
  corrida estándar. El filtro 017 sí va en `run()` (compuerta pura de entrada,
  idempotente) y en `correr_estandar.py` (para que `_INPUT.json` sellado sea
  el caso que el motor consume).

## Antes → ahora (por archivo / función)

- casos/fabrica/fabrica.py::preparar_z — antes estaba así: `preparar_z` armaba
  `entrada.json` desde semillas + destinos y nunca escribía
  `caldero_llm_neighbor_hints` (siempre `[]` en el contrato) → ahora quedó
  así: el gancho `_validar_pistas_llm()` (espejo de `_gate()`) valida el campo
  opcional `pistas_llm` de la semilla con el guardián como única autoridad y
  escribe `caldero_llm_neighbor_hints` + `caldero_llm_neighbor_hints_audit`
  en cada `entrada.json` (siempre, `[]` por defecto sin pistas).
  sha256 antes: eeadadfd7df53ca28c0cbdf2e03bd0d88d83f9e35855ef70958d4bfd9aea1eb7 | sha256 después: 7b1fa271150bc7667b8b4ab3a7657ae03594c3268e92821ec92d24b487843be8
  (diff: loader `_validar_pistas_llm()` + gancho en `preparar_z`, ~10 líneas)
- casos/fabrica/pistas_llm_caldero_v1.py::validar_pistas_llm — archivo NUEVO:
  valida `pistas_llm` (dicts token + familia del catálogo 244 + relevance
  0..1); familia fuera de catálogo / forma inválida / relevance fuera de
  [0,1] / guardián ausente rechazan el lote; los descartes del guardián
  quedan en la auditoría (huellas sha256, no el texto).
  sha256 antes: (no existía) | sha256 después: 59a39919113e96ae325d6993a1f2ff4a6f04ca1ce87eb23af8b5da3aafafd270
- casos/fabrica/PLANTILLA_semillas_z.py — antes estaba así: sin mención de
  pistas → ahora quedó así: campo opcional `pistas_llm` documentado como
  comentario en la plantilla.
  sha256 antes: 3a6ffef7cec8d352784a746708caceeaffcd0226f01bcad182fc0d74a1d64e88 | sha256 después: cbc6c9af6937a5609ac62cca29d5a0615017010a19aa6951927aedf2f51397fc
- casos/fabrica/PROMPT_SEMILLAS_Z.md — antes estaba así: 8 reglas →
  ahora quedó así: regla 9 nueva sobre pistas LLM del Caldero.
  sha256 antes: 9a8206d50a61ece08ceb964e56a97adfc58cb6d0a0bfcd9a582dfcbccbdd89fd | sha256 después: 0bfc50f598c51454df88677f31cfb8927fa0d715ac107c598768ac8602528762
- motor/motor/MOTOR_V15_3_UNICO_20260927.py::_do_caldero — antes estaba así:
  las pistas aceptadas no quedaban en la auditoría; `_resolver_cierre_operativo_017`
  leía las pistas crudas del caso para `llm_hint_scores` (una pista descartada
  por el guardián aún podía colarse en el desempate) → ahora quedó así: la
  auditoría guarda `aceptadas_detalle` y el cierre operativo usa SOLO las
  pistas que pasaron el guardián (fallback al caso crudo solo si la auditoría
  no existe, salidas viejas).
  sha256 antes: 23cd6749a2cce0da555fec3306c6ab7a44cedef429c319673d29fae6468b1f19 | sha256 después: 6818261d3ebffdba3296d05531e86059e2110917a9a3a5d0af8a9ca9076e977d
  (diff: 4 sitios + helpers nuevos `_normalizar_fecha_corte`,
  `_resolver_z_corte`, `_cargar_filtro_017`, `_aplicar_filtro_017`; ver abajo)
- motor/motor/MOTOR_V15_3_UNICO_20260927.py::_run_pre_h_analogical_search —
  antes estaba así: la rama fixture devolvía `"status":"EXECUTED"` →
  ahora quedó así: `"status":"EXECUTED_FIXTURE"` + `"provider":"provided_fixture"`.
- motor/motor/MOTOR_V15_3_UNICO_20260927.py::run (bloque CALDERO) — antes
  estaba así: la fila del componente `sidecar_caldero_busqueda_arquetipos.py`
  hardcodeaba `"status":"EXECUTED"` aunque el recibo dijera
  `EXECUTED_FIXTURE` → ahora quedó así: la fila usa
  `_caldero_attempt["status"]`. El recibo `_caldero_attempt` ya distinguía
  EXECUTED vs EXECUTED_FIXTURE y el CEB ya mapeaba a SIMULADO_FIXTURE.
- motor/motor/MOTOR_V15_3_UNICO_20260927.py::run — antes estaba así: el
  filtro 017 no existía en `run()` → ahora quedó así: tras `_validate_case`,
  `_aplicar_filtro_017(case)` aplica la compuerta (modo por env `FILTRO_017`:
  `traza` por defecto, `activo`, `off`); la traza queda en
  `result["filtro_entrada_dirigida_017"]`. Si la capa no está en el pack o la
  compuerta falla, la traza dice `NO_DISPONIBLE`/`ERROR` y la corrida sigue
  con el caso crudo (capa LLM opcional, no compuerta de decisión). El
  catálogo se pasa explícito: el fallback del filtro apunta a una ruta que no
  existe en el pack y devolvería un catálogo vacío en silencio.
- motor/motor/MOTOR_V15_3_UNICO_20260927.py::run + _run_pre_h_analogical_search —
  antes estaba así: el bloque Caldero nunca referenciaba `z_work`/`freeze`;
  no había corte temporal → ahora quedó así: `_resolver_z_corte(case)`
  (Z := `case["freeze"]` ≡ `z_trabajo`, fallback `z90_date`; NUNCA
  `z_work_date` sin normalizar: en entradas viejas es un id de corte como
  `C3_1895B`) y el sidecar recibe `cutoff_date` + `corte_modo` (env
  `CALDERO_CORTE_TEMPORAL`, `leniente` por defecto) en las 3 llamadas
  (Caldero principal, pre-H puente, pre-H fixture). `_caldero_attempt` y
  `_meta011` (store) registran `z_corte` + `corte_temporal`.
- motor/motor/sidecar_caldero_busqueda_arquetipos.py::CalderoArchetypeSearchSidecar.run —
  antes estaba así: el único filtro era self-match (identidad), sin fecha;
  `tokenize_sources` perdía la fecha aunque viniera en metadata → ahora quedó
  así: `TemporalCutoffFilter` como segundo filtro tras self-match y antes de
  tokenizar (`run(..., cutoff_date, corte_modo)`). Fuente con fecha conocida
  > Z se descarta (`post_z`); fuente sin fecha se descarta en `estricto` y se
  conserva con marca en `leniente` (defecto). La fecha de publicación nunca
  es `consultado_utc`. Auditoría nueva `audit["corte_temporal"]` (z_corte,
  modo, conteos, descartadas con fecha, conservadas sin fecha, tokens antes/
  después del corte); `raw_sources_before_self_match` sigue listando todas.
  Consecuencia documentada: en `estricto`, con la cadena auto actual, casi
  todas las fuentes caen (DDG/Bing/Wiki/Google/Brave/Tavily/OpenAI/OpenRouter
  no entregan fecha; solo sobreviven Exa/Searx/Serper). Por eso el defecto es
  `leniente`: el corte descarta lo que se sabe post-Z sin vaciar el Caldero
  (lo que vaciaría el Caldero dispararía la compuerta de la fábrica), y la
  auditoría deja visible la parte no verificada. `estricto` queda disponible
  por env para casos con proveedor fechado.
  sha256 antes: 0abdbdafe277e8426e3632c75d9caa2ec7a493354eb51cd0675e2c269e71d4fc | sha256 después: 3e00ec89cfc1037f88ea3a60d40048818c6c447c078b92b886eb60038bf4fdf9
  (diff: clase `TemporalCutoffFilter` + `run()` + autotest
  `test_corte_temporal_vecinos_le_z`; además se corrigió el fixture del
  autotest `test_audit_keeps_raw_sources_and_discard_reason`, que fallaba ya
  en HEAD 9de8612a porque "otro" es stopword de `extract_tokens` y "x"/"y"
  miden <3: el snippet pasó de "x y" a "audaz empresa")
- motor/motor/filtro_tokens_arquetipos_v2.py::conservar/motivo_descarte —
  archivo NUEVO, superconjunto estricto de v1 (v1 no se toca): además de v1,
  descarta `con_digitos` (cualquier dígito salvo allowlist `formula10`,
  `r732`), `ingles_generico` (knowledge, science, development, influence…),
  `generico_es` (obra, ejemplo, documento…), `mes_calendario` (enero,
  february…), `prefijo_procedencia` (`src_…`). Exención de catálogo primero
  (verificado: ninguna palabra basura observada está en el catálogo de 947
  tokens; protege contenido real como `sacrificio`, `rivalidad_poder`).
  Desviaciones documentadas: `muy_corto` se mantiene en <4 (NO se endurece a
  <5 porque descartaría contenido real de 4 letras que el test de v1 conserva:
  `dios`, `amor`, `arte`); nombres propios (`mozart`, `viena`) NO se detectan
  en v2 (fase 2: exige lista curada; tras el casefold se pierde la mayúscula).
  sha256 antes: (no existía) | sha256 después: 5c9813d443ab4579ec454a7a134e0d8ebfa205398c38a4dc2862be1fe6b4d36c
- scripts/sincronizar_storage.py::_filtro_tok — antes estaba así: usaba v1 y
  era fail-open (si el módulo no cargaba, admitía todo en silencio) → ahora
  quedó así: usa v2 y es fail-closed (si no carga, no admite ningún token,
  con aviso por stderr).
  sha256 antes: 1cfc1b31d465c53a8dc7a0ba59ec7f6f6fdba817189d02954ffb04a9835b9067 | sha256 después: 3fb8a1e6d0050474c1b68ccc56de06a3e99081f03ce419db4489aa24e2051e9f
- scripts/limpiar_tokens_stinkbox.py — antes estaba así: re-filtraba con v1 y
  borraba los descartados en silencio → ahora quedó así: re-filtra con v2 y
  los descartados quedan en cuarentena en
  `stinkbox/tokens_descartados_v2_<fecha>.jsonl` (con su motivo).
  sha256 antes: 789622b394b1f9d3fb54e1d4480a6988959222054992f2a54fe2034c0debdee9 | sha256 después: d91bd4d98b222a5957a973c9f63208a036165fe03b4164e58b4913a347607006
- motor/capa_llm/filtro_entrada_dirigida_017.py::compuerta — antes estaba
  así: `"status":"EXECUTED"` hardcodeado incluso en modo `traza` (nada se
  ejecutaba) → ahora quedó así: `EXECUTED` solo en `activo`,
  `TRAZA_SIN_MODIFICACION` en `traza`.
  sha256 antes: 533d68e042f0d5305fa3e84712f08e6ff6cb628e308028f29314740e36a85705 | sha256 después: 282b9284abd17bb9a735f026260ae0723828a4fe9a7dda820e1fb993b19c90d7
- motor/correr_estandar.py — antes estaba así: sin filtro 017; el recibo
  `_RECIBO_EJECUCION.json` no tenía etapas de filtro ni de consulta →
  ahora quedó así: bloque `FILTRO_017` antes del bloque de consulta
  (`traza` por defecto, `activo`, `off`; se aplica ANTES de escribir
  `_INPUT.json`); `result["filtro_entrada_dirigida_017"]` si `run()` no la
  dejó; etapas nuevas en el recibo: `filtro_entrada_dirigida_017` y
  `consulta_dirigida`.
  sha256 antes: 54c9c6bdd453b5252018f8ebecace7a6f8be1f87de7700ae758a14d638c17e09 | sha256 después: 19b5585c26b092c8ec6f4d17973f1fd6835f00475f956648da4865b8e1f45c33
- casos/fabrica/CALIBRACION_ACUMULADA.md — antes estaba así: sin ninguna
  mención de "sesgo" (solo tabla y totales) → ahora quedó así: sección
  "Sesgo de continuidad (acumulado)" con la tabla por lote (F002 7/8
  CONTINUIDAD_ASCENDENTE, 4 de esos 7 en caída/ruptura; F003 9/9 incluidas
  las 6 caídas/rupturas; F004 9/10, H1 0/6 en caídas/rupturas; F005 4/8
  CONTINUIDAD_ASCENDENTE + 4 MESETA, ningún escenario de bajada, 6/8
  caídas/rupturas, H1 0/8) y el matiz: el sesgo es del escenario
  principal/H1, no de la apuesta 022 (la 022 lee la bajada en polaridad,
  F005 5/8 y acumulado 27/40, pero confunde caída con ruptura y nunca
  apuesta ruptura; H1 solo acierta en auges de logro).
  sha256 antes: 96b2b8c88e6445e42ace3f984792ca16a46e34b4bec42a74ab24e189ba24ed45 | sha256 después: 2acf0209f76f17ca58572f7d25a674fc0023272bcccaeb74e5f2412c6d12dfd8
- .github/workflows/test-motor-contracts.yml — antes estaba así: pytest sobre
  3 archivos; sin paths del runner/sidecar/filtro → ahora quedó así: pytest
  incluye `motor/tests/test_cableado_017.py`,
  `motor/tests/test_filtro_tokens_arquetipos_v2.py`,
  `tests/test_caldero_corte_temporal.py`; paths (push y PR) incluyen runner,
  sidecar, filtro v2, filtro 017 y los tests nuevos; instala `numpy`
  (test_cableado_017 importa el runner); el paso de hashes registra también
  sidecar, filtro v2 y filtro 017.
  sha256 antes: 311c8df39421712354466d1fbc9970f397bae0b187ffeb40e7c1c69d4f8041ef | sha256 después: 9930259f68123f7e561de2efe64629c2685a82f64b87f4522200e3ce4065387d
- motor/tests/test_filtro_tokens_arquetipos_v2.py — test NUEVO (8 tests:
  superconjunto de v1, dígitos, allowlist, genéricos, meses/prefijos,
  nombres propios fase 2, exención de catálogo, filtrar).
  sha256 antes: (no existía) | sha256 después: 2fc568994d249fb17d17cc9002371940584efa9c3fb89617118a7221de0240b2
- motor/tests/test_cableado_017.py — test NUEVO (5 tests: compuerta traza,
  compuerta activo + sidecar, `_resolver_z_corte`, `_aplicar_filtro_017` en
  el runner importado, cableado presente en runner y correr_estandar).
  sha256 antes: (no existía) | sha256 después: d64c1bad4261e8be60453550518accfc339755f154054b85d6391a8e607e9fcf
- tests/test_caldero_corte_temporal.py — test NUEVO (5 tests: pre-Z/post-Z,
  fecha exacta Z inclusiva, sin fecha estricto/leniente, misma terna vía
  `from_mapping`, auditoría sin Z).
  sha256 antes: (no existía) | sha256 después: bb0504b76732d9540b57b1d0bdd88e3c569c1e8bff2bbece95e39d1663895ca7

## Hashes canónicos verificados (motor y catálogo)

- `motor/Engine_V5_CANONICO_SOLO.py`: NO TOCADO (sha256 `665c39a2…`, sin cambio).
- `motor/patterns_final_v14.json`: NO TOCADO (sha256
  `d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1`, 244 patrones,
  verificado por lectura directa en esta sesión).
- Los manifiestos (`UNIFICACION_SHA256_MANIFEST.json`,
  `MANIFIESTO_COMPACTO_SHA256.json`, `SHA256SUMS_MOTOR.txt`) se regeneran solos
  vía el workflow `fabrica-real-traza` al pushear (no se editan a mano).
- `motor/README_MOTOR.md` no se tocó: es un snapshot histórico (2026-10-13);
  la autoridad actual está en `docs/MAPA_VERSIONES_Y_AUTORIDAD.md`.

## Pruebas: 29 passed, 0 failed (¿pasaron? sí, en local; CI pendiente)

- Sidecar autotests (`python3 sidecar_caldero_busqueda_arquetipos.py`):
  7 passed, 0 failed (6 originales + `test_corte_temporal_vecinos_le_z` nuevo;
  el fixture de `test_audit_keeps_raw_sources_and_discard_reason` se corrigió:
  fallaba ya en HEAD 9de8612a).
- `motor/tests/test_filtro_tokens_arquetipos_v2.py` +
  `motor/tests/test_filtro_tokens_arquetipos_v1.py` (harness stdlib, pytest no
  instalado en local): 12 passed, 0 failed.
- `tests/test_caldero_corte_temporal.py` + `motor/tests/test_cableado_017.py`
  (harness stdlib): 10 passed, 0 failed.
- `validar_pistas_llm` (ítem 1, aislado): pista buena aceptada; pista con año
  y pista con nombre del sujeto descartadas en auditoría; familia fuera de
  catálogo rechaza el lote; sin pistas devuelve `[]` sin errores.
- `py_compile` de los 13 archivos Python tocados/nuevos: OK.
- NO se ejecutó el runner completo ni `fabrica.py` en local (prohibido por la
  tarea); NO se ejecutó `limpiar_tokens_stinkbox.py` ni
  `sincronizar_storage.py` (escriben en el StinkBox). La integración de
  corrida completa queda para CI: `test-motor-contracts` en el PR y el smoke
  real (`fabrica-real-traza`, caso sellado `CAL_F005_01_COURBET` con búsqueda
  viva, compuertas Caldero y piezas) al fusionar a `main`.
