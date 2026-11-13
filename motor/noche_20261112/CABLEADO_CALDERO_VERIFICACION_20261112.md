# Cableado del Caldero — verificación por ejecución

**Fecha:** 2026-11-12 ~22:30–04:48 CST (noche del 12 al 13)
**Ámbito:** solo la copia de trabajo `~/workspace/u6-alterno/motor-cameo/`. Nada subido al repo.
**Orden:** Marco — el motor es orgánico, no mecánico; cada pieza va donde pertenece, todo unificado.

## Veredicto en una línea

Los 5 cables están puestos y verificados por ejecución. Las dos variantes completan con exit 0.
**La puerta pasa en las dos: el tablero P final es idéntico al original (0 valores distintos, diferencia máxima 0.0) y la dX es idéntica.**
El Caldero ahora lleva las fuentes y las pistas hasta el cierre. Lo que NO se movió: los cuartos
(el puente lleva 2 vecinos pero el plugin no los cuenta) y la consulta dirigida
(el adaptador real existe y responde, pero el validador rechaza las 28 preguntas por el año
incrustado en el ID del corte — eso es un cable que falta y una decisión de Marco).

## Archivos tocados (y respaldos)

| Archivo | Cambio | Respaldo |
|---|---|---|
| `motor/motor/MOTOR_V15_3_UNICO_20260927.py` | cables 2, 2b, 3, 5 | `.pre-cableado-caldero` (332,838 B) |
| `motor/correr_estandar.py` | cables 1 y 4 (runner) | `.pre-cableado-caldero` (62,518 B) |
| `motor/capa_llm/consulta_dirigida_v1.py` | cable 4 (adaptador real) | — (sin respaldo previo; el archivo no se tocaba antes) |
| `motor/motor/plugin_circulo_monomito_v2.py` | **no tocado** (respaldo hecho por precaución, 8,132 B) | `.pre-cableado-caldero` |

**Engine y 244 intactos** (SHA antes = después):
- Engine `665c39a2861e58772522e91272563260d980908b1d4ab9f7092d3413d0c36082`
- Catálogo `d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1`
- MOTOR ahora `066af6844dd540857beaf4e29302a05b0d7a789283cfdc82f349000257c6d666`
- correr_estandar ahora `0485503dbaf6e14a9432f51bf6b088b7a304e6ee5e2b32c559d5d42e54a04063`
- El manifiesto del recibo marca deriva en los archivos editados (esperado; no bloquea).

## Cable 1 — Fuentes → sidecar (por el fixture que ya existe)

**Dónde:** `correr_estandar.py`, tras el bloque FILTRO_017 y antes de CONSULTA_DIRIGIDA, antes de escribir `_INPUT.json`.
**Qué:** si el caso trae `caldero_search_sources` y no trae fixture, se construye
`caldero_search_fixture` desde las sources (id→title, texto→snippet, url si la hay) y se pone
`allow_static_search_fixture=True`. No se inventó otro camino ni se tocó el sidecar.
**Verificado en pequeño (antes de las corridas):** con las 5 sources de CON_PISTAS el sidecar
(StaticSearchAdapter + hints) da **67 tokens_neighbors: 62 de las fuentes + las 5 pistas**,
hints_n=5. En la corrida real: tokens_neighbors=67, las 5 pistas dentro
(busqueda_verdad, defensa_debil, sacrificio, persecucion, transmision_saber).

## Cable 2 — Luces "branch" (dos pasadas, no una)

**Dónde:** `MOTOR_V15_3_UNICO_20260927.py`, ~línea 2400 (primera pasada) y ~línea 2632 (segunda pasada).
**Qué:** si a la luz le falta `branch`, se le pone la `fuente` del contrato o `"capa2"`.
Se copia cada luz para no mutar el caso sellado. Las de Cameo ya traen branch.
**Hallazgo al verificar:** la primera pasada NO era la única. La variante CON_PISTAS
siguió muriendo con `KeyError: 'branch'` en la **segunda** pasada del bus de luces
(`stinkbox_to_light_bus_v1`, línea 2666, `_lights2`) — el REWIRE que incorpora la memoria
persistente del StinkBox. Se normalizó también esa. Tras el arreglo, CON_PISTAS completa.
**Verificado en pequeño:** `run_external` con las luces del contrato normalizadas
(busqueda_verdad→capa2, defensa_debil→capa2) corre sin KeyError.

## Cable 3 — Las pistas ordenan dentro de la banda 020

**Dónde:** `MOTOR_V15_3_UNICO_20260927.py` — `_clave_desempate_020`, la cadena diagnóstica
de `_ordenar_020`, el dict `banda` (`pistas_llm_en_orden: True`) y los dos comentarios
(MOTOR:3696 y :3919). No se cambió el default del modo.
**Qué:** el puntaje de pista (`pista_llm_arquetipos_traza`) entra como 4º criterio de
desempate, tras tortugas_votos, casos semejantes y tortugas_media, y antes de rank_fusion.
Solo reordena dentro del grupo de banda (eso lo garantiza `_ordenar_020`); nunca fuera.
**Verificado:**
- En el RESULT: `clave_desempate: "tortugas votos_argmax > resoluciones previas de casos
  semejantes > tortugas evidencia_media > pista_llm_arquetipos > rank_fusion > nombre"`,
  `pistas_llm_en_orden: True`, y la cadena diagnóstica ya lleva el valor de pista como
  4º elemento (p. ej. `[1, 0, 0.475915, 0.0, 28.333333]`).
- Prueba unitaria: con tortugas iguales, el candidato con pista 0.95 ordena antes que el de
  0.9 aunque tenga menos rank_fusion — la clave funciona.
- **Honesto: en estas dos corridas la pista no decidió ningún puesto.** En CON_PISTAS
  ningún grupo cambió (en [2,3] los casos semejantes discriminaron antes: sabio 1 vs heroe 0)
  y H1 está fuera de la banda (margen 0.568 > delta 0.25). En SOLO_HINTS los tres grupos que
  cambiaron lo hicieron por tortugas (votos/media), no por la pista. El cable está vivo y
  en la clave; en Semmelweis no tuvo nada que desempatar.

## Cable 4 — Consulta dirigida: adaptador real, default medido, bloqueo encontrado

**Dónde:** `motor/capa_llm/consulta_dirigida_v1.py` (clase nueva `AdaptadorGemini`) y
`correr_estandar.py` (el modo `"on"` ahora construye `AdaptadorGemini(case)`; si no se puede
construir, cae a OFFLINE con aviso y la corrida sigue).
**Qué es el adaptador:** subprocess al CLI del conector Gemini (`custom.gemini/bin/client.py`,
modelo `gemini-3-flash-preview`), prompt con los hechos del corte + reglas estrictas,
parseo JSON robusto. Nunca levanta: cualquier fallo devuelve None (SIN_RESPUESTA).
**Verificado en pequeño:** una pregunta real de Semmelweis → Gemini respondió en ~7.6 s
("Junto al protagonista se encuentran sus progenitores y familiares…"), el filtro la
**ACEPTÓ** (sin motivos de rechazo); los tokens propuestos (progenitores, educadores) no son
vocabulario del catálogo, así que entraron 0 tokens — el texto sí se acepta.
**Medición con default-on (corrida completa, `SEMMELWEIS_SOLO_HINTS_CONSULTA_ON_20261112`,
68.547 s, exit 0, COMPLETED):**
- Traza: adaptador `gemini-3-flash-preview`, **28 preguntas, 28 PREGUNTA_RECHAZADA,
  0 respuestas, 0 tokens aceptados**, `verificacion_no_escribe_H: OK`.
- Motivo de las 28: **Q_ANIO**. El texto de la pregunta es "Hasta el corte C1_1831 (nada
  posterior a la fecha del corte): ¿qué otros agentes…?" — el ID del corte lleva el año
  incrustado (1831) y `validar_pregunta` (RX_ANIO) rechaza cualquier pregunta con un año.
  **Esto es preexistente, no lo causó el cableado:** afecta a TODAS las entradas actuales,
  porque los IDs son C1_1799, C1_1884, C1_1831, C7_1861… (también los CAL). Con Mock u
  Offline pasaría exactamente lo mismo: la consulta aporta 0 en estos casos.
- Consecuencia medida: con `on`, el tablero P, la dX y el rank_fusion son **idénticos**
  a la corrida con `off` (H1 29.750158 / H2 29.460316 en las dos). **El default `off` se
  dejó como está, y la medición muestra que cambiarlo a `on` no movería nada en
  Semmelweis** — el cable que falta no es el default, es la regla Q_ANIO contra el ID
  del corte (o que la plantilla de pregunta no incruste el ID crudo). Eso toca el filtro
  de seguridad de la consulta: **decisión de Marco, no se tocó.**

## Cable 5 — Puente al monomito por familia, con reporte honesto

**Dónde:** `MOTOR_V15_3_UNICO_20260927.py`, ~línea 2381 (puente) y el status del componente.
**Qué:** un vecino mapea si es token favor/contra de alguna familia monomito_XX (vía el
catálogo, `_patterns()`) **o** si está en el vocabulario de candidatos del plugin (ruta
anterior, se conserva; unión, nunca se admite menos que antes). El dict del puente ahora
dice si lleva o no lleva: `lleva_vecinos`, `estado` (CON_VECINOS / SIN_VECINOS),
`mapeo_por_token` (token → familia:cuarto:signo), `mapping` ya no dice
`exact_existing_monomito_vocab_only`.
**Medido (simulación antes de codificar, confirmada en las corridas):**
- SOLO_HINTS (94 vecinos: 89 web + 5 pistas): **0 mapean.** Ninguna pista es favor/contra
  de monomito. El puente reporta `SIN_VECINOS`, 94 crudos, 0 llevados.
- CON_PISTAS (67 vecinos: 62 de las fuentes + 5 pistas): **2 mapean.**
  `hostilidad` → monomito_06_pruebas_aliados_y_enemigos:Q2:favor y
  `estabilidad` → monomito_08_la_odisea_o_prueba_suprema:Q3:contra.
  El puente reporta `CON_VECINOS`, `current_neighbors: [estabilidad, hostilidad]`.
- **Los cuartos NO se movieron en ninguna de las dos** (C1 Q2, C5 Q4, C7 Q3, resto vacío,
  idénticos a la corrida original sin pistas). Por qué: los dos tokens mapeados **no están
  en `tokens_candidatos` del plugin** (`plugin_circulo_monomito_v2.py`), que es el único
  vocabulario que el plugin usa para resolver cuartos. El puente los lleva y los reporta,
  pero el plugin los ignora al puntuar.
- **Pendiente (decisión):** alinear el vocabulario del plugin con el catálogo por cuarto
  (que `hostilidad`/`estabilidad` cuenten de verdad para los cuartos). No se hizo porque
  `ESTRUCTURAS_CANDIDATAS` la consumen también `laterales_unico_v1.py:968` (venn),
  `sidecar_venn_sistemas_v1.py:11` (caldero_Q) y `cuartos_monomito.py:73`: extenderla cambia
  la resolución de cuartos para los tokens de corte en todos los casos, no solo para los
  vecinos del Caldero. Además hay una cuestión de diseño sin resolver: `estabilidad` es
  **contra** de monomito_08 — ¿un token en contra cuenta como evidencia a favor de la
  etapa? El puente lo registra con su signo; el plugin debería decidirlo.

## Resultados de las corridas de verificación (corredor estándar)

| | Original sin pistas | Rerun sin pistas | SOLO_HINTS pre-cableado | **SOLO_HINTS cableado** | **CON_PISTAS cableado** |
|---|---|---|---|---|---|
| H1 | sabio | sacrificio 29.222 | sacrificio 29.7224 | **sacrificio 29.750158** | **sacrificio 31.833492** |
| H2 | sacrificio | sabio 29.099 | sabio 29.4048 | **sabio 29.460316** | **sabio 31.265872** |
| Margen | — | 0.123 | 0.3176 | **0.289842** | **0.56762** |
| Grado | FRÁGIL | FRÁGIL | FRÁGIL | **FRÁGIL** | **FRÁGIL** |
| Set abierto | 15 | 16 | 15 | **16** | **16** |
| Segundos | 65.852 | 66.923 | ~13.7 min (directa) | **67.473** | **65.449** |
| Recibo | COMPLETED | COMPLETED | COMPLETED | **COMPLETED** | **COMPLETED** |
| hints_n | 0 | 0 | 5 | **5** | **5** |
| tokens_neighbors | 74 web | 84 web | 91 (86 web + 5) | **94 (89 web + 5)** | **67 (62 fixture + 5)** |

**Puerta (las dos cableadas):** P final heroe 0.8013 / sabio 0.7862 / sacrificio 0.8013 —
**0 valores distintos, diferencia máxima 0.0** contra el original. dX
[0.635, 0.645, 0.512, 0.402, 0.524, 0.611] idéntica a precisión completa. **PASA.**

**Qué movió cada cable, con números:**
- Cable 1 + 2 juntos (fuentes→fixture y luces al bus): CON_PISTAS sube el rank_fusion
  +2.08 frente a SOLO_HINTS cableado (H1 29.75 → 31.83) sin cambiar H1/H2. Antes del
  cableado CON_PISTAS ni siquiera completaba (KeyError). El set en 16 viene del ambiente
  (StinkBox crecido), no del cableado: ya era 16 en el rerun sin pistas.
- Cable 3 (pista en banda): 0 puestos movidos en estas dos corridas (ver arriba).
- Cable 5 (puente): 2 vecinos llevados en CON_PISTAS, 0 en SOLO_HINTS; cuartos sin cambio.
- Cable 4 (consulta): 0 en Semmelweis (Q_ANIO, ver arriba).
- La web sigue inerte: en SOLO_HINTS los 89 vecinos web son basura (esta hora, spam de moda:
  lehenga, kaftan, salwar…); 0 mapean al 244. El puente ya no miente sobre eso: dice
  SIN_VECINOS.

## Lo que queda pendiente (con motivo exacto)

1. **Alinear el vocabulario del plugin de cuartos con el catálogo** (cable 5, segunda mitad):
   `ESTRUCTURAS_CANDIDATAS` es compartida por venn, caldero_Q y cuartos_monomito; extenderla
   cambia cuartos en todos los casos. Y hay que decidir si un token **contra** cuenta como
   evidencia de la etapa. Decisión de Marco.
2. **La regla Q_ANIO contra el ID del corte** (cable 4, segunda mitad): la consulta no puede
   preguntar nada mientras la plantilla incruste el ID con año y el validador rechace años.
   Toca el filtro de seguridad: decisión de Marco (cambiar la plantilla a "corte N" o
   eximir el ID en el validador).
3. **El default de CONSULTA_DIRIGIDA** queda en `off`: medido que con `on` no cambia nada en
   Semmelweis (28/28 rechazadas). Cuando se resuelva el punto 2, habrá que medir de nuevo
   y decidir el default con números.
4. **La prosa "qué suele suceder" del LM** sigue sin consumidor en el motor (ya estaba así;
   fuera del alcance de este cableado).
5. **No se subió nada al repo.** Los RESULT crudos (11–13 MB) quedan en la copia de trabajo;
   los archivos cableados y este reporte están para revisión antes de subir.

## Archivos de evidencia (copia de trabajo)

- `motor/RESULT_SEMMELWEIS_SOLO_HINTS_CABLEADO_20261112.json` (+ recibo)
- `motor/RESULT_SEMMELWEIS_CON_PISTAS_CABLEADO_20261112.json` (+ recibo)
- `motor/RESULT_SEMMELWEIS_SOLO_HINTS_CONSULTA_ON_20261112.json` (+ recibo +
  `RESULT_..._CONSULTA_SELLADO.json` con las 28 preguntas rechazadas)
- `motor/RESULT_SEMMELWEIS_HEROE_SIN_TRONO_20261112.json` (original, referencia de la puerta)
