# El Caldero: por qué no se cableó — qué se descableó y qué contratos juegan una mala pasada
**Pregunta de Marco (2026-11-12 ~22:23 CST):** se supone que el Caldero ya
estaba cableado. ¿Por qué no se cableó? ¿Qué se descableó? ¿Hay contratos
que nos estén jugando una mala pasada?

**Método:** leer el cableado en la copia de trabajo y compararlo contra las
fuentes de septiembre (`biblioteca/motor_unico/MOTOR_UNICO_ESTANDAR_20260927/`,
el ZIP del motor). Todo con archivo:línea.

## Veredicto en una línea

**Nada se descableó: nunca se cableó completo.** El Caldero de septiembre
(1,790 líneas) no tenía ni el hilo de pistas, ni el puente al monomito, ni
el modo 020, ni la consulta dirigida. Todo eso se añadió después, por
parches (A5_20261107, PATCH19, etc.), y se añadió con contradicciones
internas. No es un cable que se cortó; es un cableado que se hizo torcido.
El motor de trabajo tiene 4,443 líneas contra 1,790 de septiembre.

## Lo que SÍ está cableado (corre de verdad)

- El sidecar corre: `_load("caldero_search", ...)` (MOTOR:2227) y
  `_load("caldero_pre_h", ...)` (MOTOR:1133). Búsqueda en vivo por
  `create_search_adapter` (Exa / OpenAI / ddgs / bing / searx / wiki /
  google). En Semmelweis trae 74-91 vecinos crudos.
- El hilo de pistas corre: `case.get("caldero_llm_neighbor_hints")` →
  guardián (MOTOR:2309) → sidecar `run(llm_neighbor_hints=...)` →
  `tokens_neighbors` → `neighbor_alignment` por familia (MOTOR:1343-1349)
  → `llm_hint_scores` en el cierre (MOTOR:3628-3645). Con 5 pistas el H1
  se voltea (verificado en la cadena del Caldero).
- El puente al monomito corre: MOTOR:2360-2381, el plugin
  `plugin_circulo_monomito_v2` recibe los vecinos del Caldero.

## Los 4 contratos que juegan una mala pasada

### 1. El contrato de entrada promete lo que el código no hace
`motor/CONTRATO_ENTRADA_LLM.txt`: "capa 2 / arquetipos: el LLM BUSCA y
mete el resultado en `caldero_search_sources` + `external_lights` — eso es
lo que alimenta Caldero y, cuando esté el archivo, StinkBox".
- **El sidecar NUNCA leyó `caldero_search_sources`**: 0 menciones en el
  sidecar de septiembre (503 líneas) y 0 en el de ahora (1,092 líneas).
  Solo dos laterales las leen (`_textos`, `filtro_identidad`, que queda
  ACTIVA_MUDA sin url ni `caldero_identity`).
- **Las `external_lights` en la forma del contrato ROMPEN la corrida**:
  el ejemplo del contrato es `{"token","peso","fuente":"capa2"}` (sin
  `branch`) y el consumidor exige `light["branch"]`
  (`motor_interrelacion_extensible_v0_1.py:94` → `KeyError: 'branch'`,
  MOTOR:2451). Las luces de Cameo SÍ llevan `"branch": "cameo"`. El
  contrato mismo trae el ejemplo que rompe.

### 2. El modo 020 es el default y deja las pistas en traza
- `MOTOR:3082`: `_CIERRE_MODO_U = os.getenv("CIERRE_TERMINAL") or "020"`.
  Nadie pone la variable → **toda corrida es modo 020**.
- `MOTOR:3696` (comentario del código): "CIERRE_020: orden = rank_fusion;
  tortugas/casos semejantes solo dentro de la banda; **pistas LLM solo
  traza**".
- `MOTOR:3919` en `_ordenar_020`: `pista_llm_arquetipos_traza = ...  #
  traza lateral; no entra al orden`.
- La rama NO-020 (018, MOTOR:3725-3740) SÍ las usa:
  `apoyo_busqueda_llm_arquetipos` es el 3er criterio del orden.
- **En septiembre NO existía nada de esto**: ni `_ordenar_020`, ni
  `llm_hint`, ni el modo 020. Se añadió después y se añadió dejando las
  pistas en traza por default. La orden del bus #50 (consulta LLM
  obligatoria) y el contrato dicen que las pistas deciden; el default del
  código dice que no.

### 3. El puente al monomito se reporta cableado llevando cero
- `MOTOR:2381`: `_mono["caldero_bridge"] = {"wired": True,
  "current_neighbors": _cal_current, ..., "mapping":
  "exact_existing_monomito_vocab_only"}`. El mapeo solo acepta
  vocabulario exacto del monomito (`_cal_current = {t for t in _cal_raw
  if t in _mono_vocab}`), así que ni la basura web ni las pistas pasan:
  `current_neighbors` es [] y `ignored_unmapped_neighbors` es todo.
- El stage reporta `"caldero_bridge": True, "current_caldero_neighbors":
  0, "feeds_predictor": True`. **El reporte dice cableado cuando no
  lleva nada.** En septiembre este puente NO existía: se cableó así
  desde su nacimiento, no se descableó.

### 4. La consulta dirigida existe pero está apagada por defecto
- `correr_estandar.py`: `CONSULTA_DIRIGIDA=off (defecto) no toca nada`.
  Solo `on` / `offline` / `mock` la corren. En septiembre el
  `correr_estandar` ni siquiera mencionaba `CONSULTA_DIRIGIDA`.
- El comentario en MOTOR:1073 dice "La consulta_dirigida NO se cablea
  aquí: ya vive en correr_estandar.py" — vive ahí, apagada. La orden del
  bus #50 dice obligatoria; el runner la deja apagada salvo que alguien
  ponga la variable. Nadie la pone → recibo `NO_CONFIGURADO`, 0
  preguntas.
- Bonus: la pre-orientación (PATCH19, MOTOR:1176-1230) sin puente ni
  fixture devuelve `API_PENDING` ("search provider not injected"). El
  puente solo se acepta si es llamada real de herramienta conectada
  (`status == EXECUTED` y `origin == connected_tool_call` + query ciega
  exacta + URLs válidas); el placeholder se rechaza POR DISEÑO.

## Por qué los vecinos son basura (el quinto cable torcido)

El sidecar creció de 503 a 1,092 líneas: la búsqueda en vivo se añadió
después de septiembre. Pero la extracción de vecinos es raspado de
palabras de los resultados web, no emparejamiento semántico: por eso
trae '11-uppgraderingen', 'accessing', 'although' y 0 de 86 intersectan
el 244. El puente de nombres es `legacy_exact_only` (MOTOR:1841):
solo coincidencia exacta. Basura + exacto = cero, por construcción.

## Qué habría que decidir (no implementado, decisiones de Marco)

1. **Contrato vs código**: o se corrige el contrato (las sources no
   alimentan al Caldero; las lights llevan `"branch"`), o se cablea el
   sidecar para leer las sources vía fixture
   (`allow_static_search_fixture`, el camino que el motor sí tiene).
2. **Modo del cierre**: si las pistas deben ordenar, el modo no puede
   ser 020 por default (o el 020 debe incluirlas como criterio). Con
   `CIERRE_TERMINAL=018` corre la rama que sí las usa.
3. **Puente al monomito**: o se relaja el mapeo (no exact-only), o se
   deja de reportar `wired: True` con 0 vecinos.
4. **Consulta dirigida**: o se enciende por defecto, o se quita la
   orden #50 de obligatoria.
