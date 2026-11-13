# Re-corrida Semmelweis — comparación con la corrida original
**Orden de Marco (2026-11-12 ~22:03 CST):** volver a correr un caso para ver
qué tanto cambió, ahora que la auditoría de activación revisó cuáles decían
no ejecutado / no puesto / no programado / en pausa / por probarse / no
permitido / en observación.

**Corrida:** `SEMMELWEIS_RERUN_20261112`, misma entrada
(`casos/precedentes/SEMMELWEIS_HEROE_SIN_TRONO_20261112/entrada.json`),
corredor estándar, 66.923 s, exit 0, recibo COMPLETED.
RESULT: `motor/RESULT_SEMMELWEIS_RERUN_20261112.json`.

## Lo que NO cambió (el núcleo reproduce exacto)

| Medida | Original (19:37) | Re-corrida (22:03) |
|---|---|---|
| Tablero P final: heroe / sabio / sacrificio | 0.8013 / 0.7862 / 0.8013 | 0.8013 / 0.7862 / 0.8013 (idéntico) |
| dX | 0.635, 0.645, 0.512, 0.402, 0.524, 0.611 | idéntico |
| Mezcla color (externo/interno/situación) | 0.3173 / 0.3596 / 0.3231 | 0.3171 / 0.3597 / 0.3231 (gris, igual) |
| Monte Carlo | 21/21, 13,027 sims, todas convergidas | 21/21, 13,027 sims, todas convergidas |
| Caldero | EXECUTED_WITH_SOURCES_NO_LLM_HINTS, hints 0 | igual, hints 0 |
| Predictor vecinos prefijo | MEDIDA_O_ESTADO_NO_EMITIDO, 0 candidatos | igual |
| Compuerta cierre | cierre_propuesto False, LATENCIA_INFORMACIONAL | igual |
| SHERLOCK_RIGOR | LIMPIO | LIMPIO |
| Grado | FRÁGIL | FRÁGIL |

## Lo que SÍ cambió (la fusión, no el núcleo)

- **H1/H2 se voltearon:** original sabio (rank 29.016) / sacrificio;
  re-corrida sacrificio (29.222) / sabio (29.099). Margen 0.123, dentro de
  la banda de mezcla (0.25). El caso era FRÁGIL y sigue FRÁGIL.
- **Set abierto:** 15 → 16 hipótesis (entra monomito_01_mundo_ordinario,
  rank 18.58). Los rank_fusion del top subieron un poco (heroe 27.64 →
  28.45; jaldun 26.91 → 27.91).
- **Vecinos Caldero:** 74 → 84 tokens crudos (búsqueda web en vivo, otra
  hora, otros resultados). Siguen mapeando 0 al 244.
- **Manifiesto:** AVISO deriva=14, fuera=5 (la copia de trabajo cambió
  desde la corrida original: los laterales nuevos de esta noche).
- **StinkBox:** el registro importó 6,504 registros nuevos de
  STINKBOX_STORAGE entre corridas (estado persistente acumulado).

## Por qué cambió

El núcleo (Engine + tablero P + geometría) es determinista y reprodujo
exacto. Lo que se movió es la FUSIÓN (rank_fusion), que lee estado vivo y
persistente: la búsqueda web del Caldero (74→84 vecinos) y el StinkBox
(creció). El volteo H1/H2 está dentro de la fragilidad que el caso ya
tenía, no es un cambio de fondo.

## Veredicto sobre la auditoría

Los que parecían que sí y los que parecían que no se comportan exactamente
como la auditoría los clasificó. Nada de lo que estaba en pausa, por
probarse, en observación o sin permitir cambió de estado, porque nada se
activó. Lo que cambió fue el ambiente (la web y el StinkBox), no el motor.
