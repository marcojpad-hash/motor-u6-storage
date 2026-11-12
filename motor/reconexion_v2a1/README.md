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

## Falta por reconectar (no en esta versión)

- Cuadrante del monomito → dirección que alimente predictibilidad_021.
- El peso del apoyo lateral (0.45 × lateral_shared × core_support) — está en
  el Engine, canónico, no se toca aquí.

## Archivos

- `negativo_reconectado_dh.py` — la reconexión (lee el RESULT local).
- `NEGATIVO_RECONECTADO_DH_NAPOLEON_10CORTES.json` — resultado verificado.
- `CONTRATO_LATERALES_NO_DECIDE_NO_ES_IGNORAR.md` — la corrección completa.
