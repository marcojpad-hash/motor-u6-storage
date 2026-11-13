# Cadena Caldero — pistas LLM — verificación (Semmelweis, 2026-11-12/13)

**Veredicto en una línea: la cadena de pistas SÍ se mueve y SÍ cambia el resultado — el H1 se voltea de sabio a sacrificio — pero lo mueve por el lateral de vecinos, no por el desempate del cierre; y la variante de tres campos que pide el contrato NO corre: las `external_lights` en forma del contrato rompen la corrida.**

Fecha: 2026-11-12/13. Caso: `SEMMELWEIS_HEROE_SIN_TRONO_20261112` (7 cortes, Z C7_1861).
Copia de trabajo: `~/workspace/u6-alterno/motor-cameo/`. Nada subido al repo. Engine, 244, correr_estandar, teoria_color, equivalencias, no_duplicacion_latencia y rueda_conjuncion NO tocados. La entrada original queda intacta (verificado: no trae ninguno de los tres campos).

## 1. El hilo (lo que dice el contrato vs lo que hace el código)

Contrato leído: `motor/CONTRATO_ENTRADA_LLM.txt` (37 líneas). Dice que el LLM busca y mete el resultado en `caldero_search_sources` + `external_lights`, y que eso alimenta Caldero y StinkBox. Verificado en código, campo por campo:

| Campo del contrato | Lo que el código hace de verdad |
|---|---|
| `caldero_llm_neighbor_hints` | Hilo completo y cableado: guardián → sidecar `run(llm_neighbor_hints=...)` → `tokens_neighbors` → `neighbor_alignment` por familia → cierre `llm_hint_scores`. |
| `caldero_search_sources` | **El sidecar del Caldero NO lo lee.** El motor busca por puente conectado, por fixture (`caldero_search_fixture` + `allow_static_search_fixture=True`) o en vivo por web. Las sources solo las leen dos laterales: `_textos` (title/snippet) y `filtro_identidad` (necesita url + `caldero_identity`; sin ambas queda ACTIVA_MUDA). |
| `external_lights` | Las leen interrelación, arcos emocionales y StinkBox. PERO la forma del contrato (`{"token","peso","fuente":"capa2"}`, sin `branch`) **rompe la corrida**: `run_external` exige `light["branch"]` y levanta `KeyError: 'branch'`. |

## 2. Las pistas producidas (texto exacto del LM)

Dos llamadas a Gemini `gemini-3-flash-preview` (par gratis; el LM no conocía el desenlace). Llamada 1: pistas. Llamada 2: fuentes + luces, sobre las mismas 5 situaciones.

**Llamada 1 — `caldero_llm_neighbor_hints` (5):**

```json
[
  {"token": "busqueda_verdad", "family": "arquetipo_el_sabio", "relevance": 0.95},
  {"token": "defensa_debil", "family": "arquetipo_el_heroe", "relevance": 0.9},
  {"token": "sacrificio", "family": "20_sacrificio_por_un_ideal", "relevance": 0.9},
  {"token": "persecucion", "family": "5_persecucion", "relevance": 0.85},
  {"token": "transmision_saber", "family": "mentor", "relevance": 0.8}
]
```

**Llamada 1 — "qué suele suceder" (prosa del LM; el motor NO tiene campo para esto, vive solo en este reporte):**

- busqueda_verdad: "lo que suele suceder es que el individuo utiliza el análisis y la observación para cuestionar realidades aceptadas que otros ignoran por hábito."
- defensa_debil: "lo que suele suceder es que quien sostiene una verdad impopular frente a una mayoría poderosa se encuentra en una posición de vulnerabilidad constante."
- sacrificio: "lo que suele suceder es que el compromiso con un ideal superior desplaza el bienestar personal, llevando al individuo a priorizar la causa sobre su propia estabilidad."
- persecucion: "lo que suele suceder es que el entorno reacciona con hostilidad ante la disonancia, intentando silenciar o marginar a quien altera el orden establecido."
- transmision_saber: "lo que suele suceder es que el intento de compartir herramientas o conocimientos esenciales se topa con la resistencia al cambio de quienes deben recibirlos."

**Llamada 2 — `caldero_search_sources` (5, forma del contrato + title/snippet para el lector de laterales; SIN url, SIN nombres, SIN años):**

- src1 "El Observador de Anomalías": "El análisis sistemático y la observación empírica permiten detectar fallas en el conocimiento aceptado por la mayoría mediante el estudio de patrones."
- src2 "La Resistencia de la Convicción": "La vulnerabilidad de quien sostiene una postura fundamentada ante instituciones poderosas que perciben la nueva evidencia como una amenaza directa."
- src3 "Priorización de la Causa": "La entrega total a un propósito que trasciende los intereses personales, enfocándose íntegramente en la defensa de un bien común superior."
- src4 "Reacción Ante la Disonancia": "La marginación activa y el descrédito como mecanismos de defensa de un sistema ante ideas que generan disonancia en el orden establecido."
- src5 "El Intento de Instrucción": "El esfuerzo persistente por instruir y mejorar las prácticas ajenas a pesar de la resistencia cultural y el rechazo de quienes deberían recibirlas."

Aviso honesto: estas fuentes NO son resultados de una búsqueda web en vivo; son textos compuestos por el LM desde su conocimiento. El motor las trataría como texto aportado, no como búsqueda verificada. La vía que sí certifica búsqueda es el puente de herramienta conectada (`caldero_search_bridge`, status EXECUTED + origin connected_tool_call), que no es esta.

**Llamada 2 — `external_lights` (5, forma del contrato, pesos 0.60–0.84):**

```json
[
  {"token": "busqueda_verdad", "peso": 0.84, "fuente": "capa2"},
  {"token": "defensa_debil", "peso": 0.79, "fuente": "capa2"},
  {"token": "sacrificio", "peso": 0.79, "fuente": "capa2"},
  {"token": "persecucion", "peso": 0.75, "fuente": "capa2"},
  {"token": "transmision_saber", "peso": 0.72, "fuente": "capa2"}
]
```

## 3. Las variantes (dos, no una)

- `casos/precedentes/SEMMELWEIS_HEROE_SIN_TRONO_CON_PISTAS_20261112/entrada.json` — TRES campos (hints + sources + lights). Es la variante que pide el contrato.
- `casos/precedentes/SEMMELWEIS_HEROE_SIN_TRONO_SOLO_HINTS_20261112/entrada.json` — SOLO hints. Se creó después, porque la de tres campos rompe la corrida (ver §4); esta aísla el hilo de pistas para poder verificar la cadena. Cortes idénticos al original en las dos (verificado por comparación).

## 4. Las corridas (qué pasó, sin maquillar)

| Intento | Variante | Resultado | Tiempo |
|---|---|---|---|
| 1 | tres campos, corredor estándar | **ERROR: `KeyError: 'branch'`** en `MOTOR_V15_3_UNICO_20260927.py:2451` (interrelación) → `motor_interrelacion_extensible_v0_1.py:94` (`run_external`: `eng.register(light["token"], light["branch"], ...)`). Sin RESULT. | 11.4 s |
| 2 | solo-hints, corredor estándar | **TIMEOUT** del subproceso primario (90 s fijos, `correr_estandar.py:704`). Sin RESULT. | 94.5 s |
| 3 | solo-hints, corrida directa (mismo comando que el corredor, sin el timeout de 90 s; precedente Noether) | **MUERTA por reinicio del runtime** a los ~7 min: log de 0 bytes, sin RESULT. No dejó efecto (no existe `_PRIMARY_RESULT.json`). | ~7 min |
| 4 | solo-hints, corrida directa (re-lanzada, mismo comando) | **COMPLETÓ, exit 0.** RESULT 11.5 MB en `motor/runs/ESTANDAR__SEMMELWEIS_SOLO_HINTS_20261112/_PRIMARY_RESULT.json`, copiado a `motor/RESULT_SEMMELWEIS_HEROE_SIN_TRONO_SOLO_HINTS_20261112.json`. Sin recibo del corredor (COMPLETADO_DIRECTO, como Noether). | ~13.7 min (820 s) |

El crash de las luces se predijo por ejecución directa ANTES de la corrida: `run_external([{"token":"sacrificio","peso":0.7,"fuente":"capa2"}], [])` levanta `KeyError: 'branch'`; con `"branch"` presente funciona (`unique_tokens: ['sacrificio']`). El `ceb.call` re-lanza la excepción y no hay try/except alrededor de esa llamada, así que la corrida entera muere. La interrelación corre ANTES que arcos y StinkBox, así que con luces en forma del contrato ni siquiera llegan a ejecutarse esos consumidores.

## 5. La cadena eslabón por eslabón (variante solo-hints vs sin pistas)

Baseline sin pistas: H1 `arquetipo_el_sabio` (rank_fusion 29.0159, FRÁGIL), H2 `20_sacrificio_por_un_ideal` (28.4168, FRÁGIL), margen 0.5990. Status Caldero: `EXECUTED_WITH_SOURCES_NO_LLM_HINTS`, `llm_neighbor_hints_n` 0, 74 vecinos web.

### 5.1 Pistas → guardián: 5 de 5 aceptadas, 0 descartadas

`guardian_pistas_llm_caldero_v1.py`: entrada 5, aceptadas 5, descartadas []. Verificado antes de correr, ejecutando el propio guardián con los términos de identidad del caso (`ignaz`, `semmelweis`). Las 5 familias existen en el 244 y los 5 tokens son favor de su familia.

### 5.2 Pistas → sidecar → vecinos: 91 vecinos = 86 web + 5 pistas

`tokens_neighbors` n: 74 → **91**. Las 5 pistas entran como `{"token": ..., "source": "llm_hint"}`. Status Caldero: `EXECUTED_WITH_LLM_HINTS`. `llm_neighbor_hints_n`: 0 → **5**.

### 5.3 Vecinos mapeados al 244: 5 de 5 pistas; 0 de 86 web

- De los 86 tokens web, **0** intersectan favor/contra de ninguna familia del 244 (medido contra el catálogo). La basura web sigue siendo inerte: no mueve nada.
- Las 5 pistas SÍ son tokens del 244 y caen en favor de sus familias. Por eso el cambio de H1 es atribuible SOLO a las pistas, no a la variación de la búsqueda web (que además es no determinista: 74 vecinos en una corrida, 86 en la otra).
- Puente al monomito: `current_neighbors` **[]** en las dos corridas (91 crudos, 91 ignorados). Ninguna pista es vocabulario monomito (`exact_existing_monomito_vocab_only`).

### 5.4 Vecinos → rank_fusion: EL H1 SE VOLTEA

Con pistas: H1 **`20_sacrificio_por_un_ideal`** (29.7224), H2 **`arquetipo_el_sabio`** (29.4048), FRÁGIL, margen 0.3176 (la carrera se cierra). Los 19 candidatos son los mismos en las dos corridas; ninguno entra ni sale.

Mecanismo medido (feature vector por candidato, `predictor/candidates[i]/features`):

| familia | alineación vecinos base → con pistas | delta rank_fusion |
|---|---|---|
| 20_sacrificio_por_un_ideal | 0.5000 → 0.5714 (+0.0714) | +1.3056 |
| heroe | 0.5000 → 0.5714 (+0.0714) | +1.3056 |
| arquetipo_el_heroe | 0.5000 → 0.5714 (+0.0714) | +1.3056 |
| arquetipo_el_sabio | 0.5000 → 0.5500 (+0.0500) | +0.3889 |
| spengler_02 | 0.5000 → 0.5833 (+0.0833) | +1.7222 |
| jaldun_01_asabiyyah | 0.5000 → 0.5714 (+0.0714) | +1.5278 |
| monomito_05 / arquetipo_heroe | 0.5000 → 0.5000 (0.0000) | 0.0000 |

La alineación sube 0.5×(1/denominador) por cada token pista en favor: sacrificio tiene denominador 7 (+0.0714), sabio 10 (+0.0500), spengler 6 (+0.0833). Por eso el sacrificio le gana al sabio: mismo +1 favor, denominador más chico. Y ojo: **las pistas levantan a todas las familias que comparten el token, no solo a la familia nombrada** — `sacrificio` alimenta también a `heroe` y a `jaldun_01`; `busqueda_verdad` alimenta también a `spengler_02` (que sube MÁS que el sabio, +1.7222, sin que ninguna pista lo nombre). Es la misma duplicación del lateral de no-duplicación, ahora a favor de las pistas.

### 5.5 Pistas → cierre (llm_hint_scores): TRAZA, NO desempate

- `llm_hint_scores` existen: `pista_llm_arquetipos_traza` en candidatos — 20_sacrificio 0.9, sabio 0.95, arquetipo_el_heroe 0.9. (`mentor` 0.8 y `5_persecucion` 0.85 no aparecen porque no son candidatos del set de 19.)
- Pero en modo 020 el cierre NO las usa para ordenar: `_ordenar_020` (`MOTOR_V15_3_UNICO_20260927.py:3919`) escribe `c["pista_llm_arquetipos_traza"] = float(...)  # traza lateral; no entra al orden`. No existe `apoyo_busqueda_llm_arquetipos` en ningún candidato de esta corrida. **El volteo de H1 vino por el lateral de vecinos (alineación → rank_fusion), no por el desempate del cierre.** En la rama no-020 las pistas sí serían criterio de orden (4ª prioridad), pero esta corrida es modo 020.

### 5.6 Pistas → predictor de vecinos por prefijo: NO SE MUEVE (0 candidatos)

Status en las dos corridas: `SIN_PREFIJO_EN_INPUT` — "ningún corte inicial trae estado monomítico". El predictor lee SOLO los cortes (`_prefijo_monomito`: clave explícita o token P/A/C exacto del vocabulario de las 15 biografías). Las pistas van al Caldero, no a los cortes. Ninguna pista es nombre de etapa del predictor. **Por el hilo del contrato, el predictor no se puede mover con pistas.** Para moverlo haría falta tocar los cortes (clave `estado_monomito` o token de etapa), que es otro hilo, no este.

### 5.7 Pistas → cuartos del monomito: NO SE MUEVEN

Cuadrantes por corte IDÉNTICOS en las dos corridas (ver `CUARTOS_MONOMITO_SEMMELWEIS_20261112.md`): C1 Q2, C5 Q4, C7 Q3, resto vacío; Q1 nunca activo. El puente Caldero aporta 0 vecinos al vocabulario monomito en ambas. Los cuartos salen solo de los tokens de los cortes.

### 5.8 Pistas → StinkBox (persistencia): SÍ, las 5 quedan guardadas

`persistent_neighbor_lights`: 3,252 luces; las 5 pistas están entre ellas (branch `caldero_memory`, source `vecinos_caldero/neighbor_index.json`). El pre-H reusa los vecinos: `pre_h_lateral_tokens.unique_tokens` n=91 con las 5 pistas presentes. Las pistas ya son memoria persistente para corridas futuras.

### 5.9 caldero_search_sources: SIN MEDIR en corrida viva

La variante de tres campos murió en interrelación antes de producir RESULT, así que el efecto de las sources en ejecución NO se midió. Por código: el sidecar no las lee; `_textos` leería title/snippet; `filtro_identidad` queda ACTIVA_MUDA sin url ni `caldero_identity`.

### 5.10 "Qué suele suceder": SIN consumidor en el motor

La prosa del LM (ver §2) no entra a ningún campo del motor. El predictor, que es el que debería decir "lo que suele suceder después", lee prefijos de etapas de los cortes, no prosa del LM. La segunda mitad de la pregunta de Marco ("qué suele suceder en esas situaciones") hoy solo vive en este reporte.

## 6. Veredicto honesto

- **La cadena de pistas SÍ se mueve y SÍ decide algo**: con 5 pistas el H1 cambia de sabio a sacrificio y el margen se cierra de 0.599 a 0.318. El mecanismo es el lateral de vecinos (alineación), no el desempate del cierre.
- **Pero el movimiento es grueso, no fino**: las pistas levantan a todas las familias que comparten el token (jaldun y spengler suben más que los nombrados). Sin la regla de no-duplicación, una pista es un voto que se reparte.
- **Dos eslabones NO se mueven por este hilo**: el predictor (0 candidatos, lee cortes) y los cuartos (idénticos, puente con 0 mapeados).
- **El contrato NO corre completo**: `external_lights` en su forma escrita rompe la corrida (`KeyError: 'branch'`, medido dos veces). `caldero_search_sources` no alimenta al Caldero (el sidecar no las lee), y su efecto en vivo quedó sin medir porque la corrida murió antes.
- **La mitad "qué suele suceder" no tiene dónde entrar**: la prosa del LM no la consume nada del motor.

## 7. Qué sigue faltando (abierto, sin cerrar)

1. **Decidir la forma de `external_lights`**: el consumidor exige `branch`. La reparación mínima sería que la luz lleve `"branch": "capa2"` (el nombre de capa del propio contrato). NO se aplicó: es decisión de Marco, porque cambia lo que el LM produce y lo que el contrato dice.
2. **Decidir qué se hace con `caldero_search_sources`**: el contrato dice que alimentan al Caldero y el código dice que no. O se cablea el sidecar para leerlas (vía fixture con `allow_static_search_fixture`, que es el camino que el motor sí tiene), o se corrige el contrato. Sin decidir esto, las fuentes son texto que solo leen dos laterales.
3. **Darle consumidor al "qué suele suceder"**: hoy la prosa del LM no entra al motor. O se traduce a etapas del monomito en los cortes (y entonces el predictor sí votaría), o se acepta que esa mitad vive fuera del motor.
4. **Mover el predictor y los cuartos por este hilo, si se quiere**: con pistas no se puede; haría falta que el LM marcara etapas por corte (otro campo, otra decisión).
5. **La no-duplicación sobre las pistas**: un token pista alimenta a varias familias a la vez (sacrificio → heroe + 20_sacrificio + jaldun_01). El lateral de no-duplicación existe pero no está cableado a este hilo.
6. **El timeout de 90 s del corredor**: la corrida solo-hints lo rebasó dos veces (94.5 s); solo completó por corrida directa (~13.7 min). El corredor estándar no alcanza para este caso.

## 8. Archivos

- Reporte de cuartos: [CUARTOS_MONOMITO_SEMMELWEIS_20261112.md](sandbox://workspace/u6-alterno/CUARTOS_MONOMITO_SEMMELWEIS_20261112.md)
- Script nuevo (solo lectura, no toca nada protegido): `~/workspace/u6-alterno/motor-cameo/motor/laterales/teoria_color/cuartos_monomito.py`
- Variante tres campos: `~/workspace/u6-alterno/motor-cameo/casos/precedentes/SEMMELWEIS_HEROE_SIN_TRONO_CON_PISTAS_20261112/entrada.json`
- Variante solo-hints: `~/workspace/u6-alterno/motor-cameo/casos/precedentes/SEMMELWEIS_HEROE_SIN_TRONO_SOLO_HINTS_20261112/entrada.json`
- RESULT con pistas (directo, sin recibo): `~/workspace/u6-alterno/motor-cameo/motor/RESULT_SEMMELWEIS_HEROE_SIN_TRONO_SOLO_HINTS_20261112.json` (11.5 MB; original en `motor/runs/ESTANDAR__SEMMELWEIS_SOLO_HINTS_20261112/_PRIMARY_RESULT.json`)
- RESULT sin pistas (baseline): `~/workspace/u6-alterno/motor-cameo/motor/RESULT_SEMMELWEIS_HEROE_SIN_TRONO_20261112.json`
- Entrada original intacta: `~/workspace/u6-alterno/motor-cameo/casos/precedentes/SEMMELWEIS_HEROE_SIN_TRONO_20261112/entrada.json`
- Prompts LM (para repetir): `/tmp/prompt_semmelweis.txt`, `/tmp/prompt_semmelweis_fuentes.txt`
