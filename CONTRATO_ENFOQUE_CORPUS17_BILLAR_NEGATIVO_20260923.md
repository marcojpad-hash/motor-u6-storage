# CONTRATO — Enfoque Corpus 17 / Billar / Negativo (Forman-Ricci)

Fecha: 2026-11-11. Rama: `alterno/cameo-pesos`.
Este contrato repara una referencia rota: `motor/motor/lectura_negativo_ricci_vs_billar_v0_1.py`
citaba este archivo y no existía. Ahora existe y es el que manda sobre dónde vive
Forman-Ricci y qué hace.

Regla de este contrato (Marco): un contrato dice QUÉ HACE cada componente, no solo
qué parece ser.

## §1. Forman-Ricci es GEOMETRÍA, no tokens

Forman-Ricci vive en la capa de **geometría / vectorización, parte de trazabilidad**.
NO vive en la capa de tokens y NO se busca ahí.

- NO buscar Forman-Ricci en `motor/motor/capa_interrelacion_tokens.py` (la capa de
  interrelación entre familias por tokens). No está ahí y no va ahí. Esa capa es de
  tokens; Forman-Ricci es curvatura sobre un grafo.
- La confusión viene de que una de las lentes (`ricci_forman_coocurrencia_v0_1.py`)
  LEE tokens P como entrada para armar su grafo. Leer tokens como entrada no la hace
  un componente de tokens: la curvatura que calcula es geométrica.

Si alguien no encuentra a Forman-Ricci, es porque lo está buscando en el lado de
tokens. Está en `motor/motor/`, en geometría.

## §2. Los tres archivos y QUÉ HACE cada uno

### 2.1 `motor/motor/forman_ricci_weighted_graph.py` — la primitiva (geometría)

QUÉ HACE: calcula la curvatura exacta de Forman-Ricci, 1-dimensional y ponderada,
sobre un grafo explícito que se le pasa como entrada.

- Entrada: nodos `{node_id: peso positivo finito}` y aristas
  `[{u, v, weight}]` con pesos positivos finitos. Sin 2-celdas.
- Para cada arista e=(u,v) calcula
  `F(e) = w(e)·(w(u)/w(e) + w(v)/w(e) − Σ w(u)/√(w(e)·w(e′)) − Σ w(v)/√(w(e)·w(e′)))`
  sobre las aristas incidentes a u y a v.
- Salida: `status = COMPUTED_EXPLICIT_WEIGHTED_GRAPH`, curvaturas por arista,
  media, `topology_source = explicit_input`, `integrated_into_H = False`.
- QUÉ NO HACE: no está cableada a los cortes P/A/C. Su propio contrato lo dice:
  esos cortes no especifican una topología de grafo validada ni pesos de nodo/arista.
  No decide H. No hay afirmación de integración al laboratorio.

### 2.2 `motor/motor/ricci_forman_coocurrencia_v0_1.py` — la lente lateral (indicador)

QUÉ HACE: calcula una curvatura tipo Ricci-Forman a partir de la coocurrencia de
tokens P entre cortes consecutivos.

- Para cada par de cortes consecutivos toma los P de cada corte, calcula la media
  de sus pesos y saca la curvatura como `tanh(media_siguiente − media_actual)`,
  ponderada por el número de pares. La media de Ric_F por arista es la misma cuenta
  que usa el motor para su métrica lateral.
- Corre un nulo real por permutación del orden de los cortes (SEED_NULO=20260921,
  n_rep=40, determinista) para contestar si la curvatura media observada depende del
  orden temporal o sale igual al azar.
- `Alimenta_H = NO`. No decide H.
- QUÉ ES: esta es la "Ricci" que el motor usa hoy. Ver §3: es un indicador, no la
  curvatura geométrica validada.

### 2.3 `motor/motor/lectura_negativo_ricci_vs_billar_v0_1.py` — la lectura por negativo (PROPUESTA)

QUÉ HACE: compara Ricci–Forman vs Billar por familia/candidato y DESCARTA candidatos.
No dice qué es algo; dice qué NO es.

- Billar = cuello de ruido: qué pares no convergen / qué región se vació → resta
  candidatos. Ricci negativo = la familia está en una región que "abre"
  (media de Ric_F de sus aristas incidentes < 0).
- Cuadrantes (converge billar × curvatura negativa Ricci):
  - SOLO_BILLAR → 0 señales negativas → SE_SOSTIENE (no resta).
  - AMBOS → discordancia (billar junta órbita, Ricci abre) → TENSION_LATENTE.
  - NINGUNO → discordancia (billar no ve convergencia, Ricci cohesiona) →
    DESCARTE_DEBIL_LATENTE.
  - SOLO_RICCI → 2 señales negativas (no converge + abre) → DESCARTE (resta el
    candidato).
  - SIN_RICCI → solo billar informa → LATENTE.
- Gating por nulo: si |z| < Z_MIN (2.0) en una lente, su señal se marca
  "sin_señal_vs_nulo" y la etiqueta lleva sufijo _BAJO_NULO (se reporta, no se
  promueve). Si una lente no tiene señal vs nulo → LATENTE (no "no hay caso", no
  inventar).
- QUÉ NO HACE: el negativo es descarte, no letrero. No elige H.
  `Alimenta_H = NO`. `writes_H = False`. Solo lectura sobre los JSON de entrada.
  No importa Engine ni 244.
- ESTADO: **PROPUESTA, no cableado, no tubo.**
- ENTRADAS: el script pide el layout UNIFICADO (`RESULT_G_E_V0163_D_lentes_{caso}.json`
  + `lentes_billar_ricci_outputs/BILLAR_V0_2_{caso}.json` + `RICCI_V0_1_{caso}.json`).
  Esas entradas NO existen en general para las corridas actuales (F001/F002 y
  precedentes no traen ese layout). Sin ellas el script no corre tal cual; las
  features embebidas en el RESULT (`billar_circular_v0_2`, `ricci_forman_v0_1`) son
  lo que hay para leerlo. Ver §7.

## §3. La distinción que hay que conservar

Hay DOS cosas distintas que se llaman "Ricci" y NO se deben mezclar:

1. **La curvatura geométrica validada** (`forman_ricci_weighted_graph.py`): la
   primitiva exacta sobre un grafo explícito. NO está cableada a P/A/C ni integrada
   a H.
2. **El indicador que el motor usa hoy** (`ricci_forman_coocurrencia_v0_1.py`): un
   indicador / proxy de deriva temporal. Como dicen `motor/REGISTRO_CORRIDAS.md` y
   `motor/PATCH_REPORT_20261014_R1.md`: "Ricci sigue siendo un indicador de deriva
   temporal, no curvatura Ricci–Forman geométrica validada" y "la métrica lateral
   Ricci activa sigue siendo un proxy de deriva temporal; no se presenta como
   curvatura exacta de Forman integrada al ranking".

No presentar el indicador de deriva como si fuera la curvatura exacta integrada al
ranking. No son lo mismo.

## §4. La tríada: billar / Poincaré / Forman-Ricci

La tríada del motor (ver `motor/motor/SPEC_SCHRODINGER_V0_1.md` §9):

- **Billar** (circular en el borde) ES rotación de Poincaré: estabiliza.
- **Forman-Ricci** es la lectura del negativo: transforma. Para que algo sea,
  también tuvo que dejar de ser — uno estabiliza y el otro transforma.
- Forman-Ricci no dice qué es, dice qué no es: si hay 5–6 opciones, elimina 1–2
  porque no eran. El negativo debe decidir qué masa se destruye (solo lo que no
  es) para que la certeza se preserve.

## §5. Estado y regla

- **Estado de la lectura por negativo: PROPUESTA, no cableada.** Nada del negativo
  se cablea hasta que se entienda (regla de Marco, 2026-11-11). El negativo hay que
  entenderlo primero: debe decidir qué masa se destruye (solo lo que no es) para
  que la certeza se preserve.
- La primitiva geométrica (`forman_ricci_weighted_graph.py`) tampoco está cableada
  a P/A/C por diseño (esos cortes no especifican una topología de grafo validada).
- No cablear el negativo en este contrato. Este contrato solo pone bien dónde vive
  y qué hace.

## §7. Por qué el indicador entró por otro lado (y por qué se comporta raro)

- **Las entradas UNIFICADO no existen en general.** El layout que pide la lectura
  por negativo (`RESULT_G_E_V0163_D_lentes_*` + `lentes_billar_ricci_outputs/`)
  no existe para las corridas actuales. No es que esté bloqueando al otro: **el
  negativo NO bloquea nada** — es PROPUESTA, no cableado, no toca el motor ni a
  ningún otro componente.
- **Por qué el "Ricci" entró por otro lado:** como no se encontraba la curvatura
  Forman-Ricci exacta (la primitiva pide un grafo explícito con topología validada
  que los cortes P/A/C no especifican), la "Ricci" que usa el motor entró por el
  lado de la lente de coocurrencia (§2.2): un proxy de deriva temporal hecho con
  tokens P entre cortes. Por eso se comporta raro: **no es la curvatura exacta,
  es un sustituto que entró por donde pudo.** En Napoleón (F001) el proxy da
  media 0.0438 y sus 3 valores más grandes son todos positivos (0.0677) — no hay
  señal negativa que descartar en esa corrida; y el método mismo dice
  `TEMPORAL_WEIGHT_DRIFT_PROXY_NOT_EXACT_FORMAN`, `forman_ricci_verified: False`.
- **Para que embone:** si se quiere la curvatura exacta, hay que darle a la
  primitiva un grafo explícito con topología y pesos validados (eso no lo dan los
  cortes P/A/C). Mientras tanto, el indicador de deriva se llama indicador, no
  curvatura, y no se presenta como integrado al ranking.

## §8. Referencias

- Citado por: `motor/motor/lectura_negativo_ricci_vs_billar_v0_1.py` (encabezado).
- `motor/motor/forman_ricci_weighted_graph.py` (primitiva; su propio contrato en el
  docstring).
- `motor/motor/ricci_forman_coocurrencia_v0_1.py` (lente lateral; `Alimenta_H = NO`).
- `motor/REGISTRO_CORRIDAS.md`: "Ricci sigue siendo un indicador de deriva temporal,
  no curvatura Ricci–Forman geométrica validada."
- `motor/PATCH_REPORT_20261014_R1.md`: la métrica lateral Ricci activa es un proxy de
  deriva temporal.
- `motor/motor/SPEC_SCHRODINGER_V0_1.md` §9: la tríada billar / Poincaré / Forman-Ricci.
- `motor/README_MOTOR.md`: PATCH_STACK 003 (`003_ricci_P_top5_y_negativo_schema.md`) y
  009 (`009_marco_7783_geometria_y_210141_marcaje.md`); docs en `SPECS_CONTRATOS.zip`.
- Verificado 2026-11-11: `motor/motor/capa_interrelacion_tokens.py` NO menciona a
  Ricci; ningún contrato ni índice existente ubica a Forman-Ricci bajo tokens. El
  problema era la referencia rota (este contrato no existía) y la falta de un lugar
  que dijera dónde vive y qué hace.
