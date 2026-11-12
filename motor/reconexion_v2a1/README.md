# Reconexión v2.A.1 — RESERVA (no es la versión que se maneja ahorita)

Fecha: 2026-11-11 ~23:40 CST. Orden de Marco: ponerla abajo de la última
(`alterno/cameo-pesos`), como reserva, para verla. Si funciona bien, esta
se vuelve la anterior, o sea la verdadera.

## Qué es

La reconexión de los laterales que estaban cableados pero no tocaban nada.
" No deciden" se malentendió como "ignórenlo". No es así: no deciden H solos,
pero no están de adorno.

## La fuga (verificada en código, Napoleón 10 cortes)

- **Décimo Hombre → nada.** Calcula `contador_supervivencia` (53 contrafactuales)
  y NADIE lo lee. Seis candidatas sobreviven 0/53 y eso no hace nada.
- **Cuadrante del monomito → un contador.** El hub solo cuenta cuántos cortes
  tienen cuadrante activo; nunca lo usa para dirección.
- **Negativo → un reporte.** El Engine lee la señal de descarte solo para
  ponerla en un dict de resumen; no descarta ni cambia H.
- **Apoyo lateral (StinkBox/capa2) → un hilo.** 1 de 6 términos del
  `lateral_shared`, luego × 0.45 × core_support: ~7% como máximo.

## Qué reconecta esta versión

**El "no" del Décimo Hombre alimenta el negativo** (`negativo_reconectado_dh.py`):
supervivencia 0/53 → DESCARTE; supervivencia > 0 → SE_SOSTIENE.

Resultado verificado en Napoleón 10 cortes (`NEGATIVO_RECONECTADO_DH_NAPOLEON_10CORTES.json`):
- arquetipo_el_gobernante (36/53) → SE_SOSTIENE
- utopia_principio_mercado (6/53) → SE_SOSTIENE
- 30_ambicion (11/53) → SE_SOSTIENE
- situacion_dramatica_ambicion (0/53) → DESCARTE
- 12_obtencion (0/53) → DESCARTE

**5 → 3 sostenidos, 2 descartados.** Es lo que el negativo debía hacer desde
siempre: si hay 5–6 opciones, elimina 1–2 porque no eran. Ni 0/5 (proxy) ni
5/5 (exacto en grafo denso): 2/5.

## Parte 2: cuadrante → dirección (`direccion_cuadrante.py`)

El cuadrante solo se contaba y nunca se usaba para dirección. Reconectado:
la dirección es el próximo cuadrante en el ciclo Q1→Q2→Q3→Q4, y cada
candidata se mide con datos: su P media en los cortes del cuadrante siguiente
vs su P media en los cortes del cuadrante actual.

Verificado en Napoleón 10 cortes (`DIRECCION_CUADRANTE_NAPOLEON_10CORTES.json`):
- Secuencia: Q2→Q3→Q3→Q3→Q2→(—)→Q3→(—)→Q2→Q2. **Oscila Q2↔Q3, no progresa a Q4.**
- Actual (C10): Q2_Descenso. Dirección: Q3_Ordeal.
- gobernante +0.048 ALINEADA (DH 36/53, se sostiene)
- mercado +0.033 ALINEADA (DH 6/53, se sostiene)
- 30_ambicion +0.020 ALINEADA (DH 11/53, se sostiene)
- situación_ambicion −0.003 NO_ALINEADA (DH 0/53, descartada)
- 12_obtencion +0.022 ALINEADA (DH 0/53, descartada) — tensión real: crece
  hacia Q3 pero no sobrevive ningún contrafactual. El DH y la dirección no
  coinciden ahí; queda abierto, no se fuerza.

## Parte 3: la predictibilidad ajustada (`motor/motor/predictibilidad_set_021.py`)

Qué se modificó: el lateral que calcula la predictibilidad (Fórmula 22),
NO el Engine canónico. La Fórmula 22 original queda intacta para comparar;
se añade por hipótesis la variante ajustada.

- `dh_supervivencia_frac` = contador_supervivencia / 53 contrafactuales.
- `direccion_cuadrante_norm` = 0.5 + delta_P_hacia_el_cuadrante_siguiente × 5.
- `ajuste_reconexion` = media de las dos; `factor_reconexion` = 0.5 + 0.5×ajuste.
- `predictibilidad_estructural_ajustada_0_1` = K × F × factor + base_pp/100.

Verificado en Napoleón 10 cortes (corriendo el archivo modificado sobre el RESULT):
- Spread top 5: 0.0211 → 0.1127 (5.3×). Gap entre los dos primeros: 0.0009 → 0.0688 (76×).
- gobernante 0.5411 → 0.4767; mercado 0.5402 → 0.4051; 30_ambicion 0.5395 → 0.4079.
- OJO: la ajustada reordena el 2º lugar: 30_ambicion (0.4079) pasa por encima
  de mercado (0.4051). El rank_fusion y H1/H2 NO cambian (el archivo no los
  toca); lo que cambia es la predictibilidad ajustada. Eso es consecuencia
  real de la reconexión, no un artefacto: mercado sobrevive solo 6/53.

## Falta por reconectar (no en esta versión)

- Cuadrante del monomito → dirección que alimente predictibilidad_021.
- El peso del apoyo lateral (0.45 × lateral_shared × core_support) — está en
  el Engine, canónico, no se toca aquí.

## Archivos

- `negativo_reconectado_dh.py` — la reconexión (lee el RESULT local).
- `NEGATIVO_RECONECTADO_DH_NAPOLEON_10CORTES.json` — resultado verificado.
- `CONTRATO_LATERALES_NO_DECIDE_NO_ES_IGNORAR.md` — la corrección completa.
