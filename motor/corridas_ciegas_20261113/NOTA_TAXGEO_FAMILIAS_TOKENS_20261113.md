# Taxonomía geopolítica en familias_tokens/ — 2026-11-13

## Qué se hizo
Las 10 familias de la taxonomía geopolítica (`motor/laterales/taxonomia_geopolitica/familias_geopolitica.json`,
90 tokens: 50 favor + 40 contra) se partieron en 10 archivos individuales en
`motor/motor/familias_tokens/`, donde el motor las carga (glob `*.json` en
`laterales_unico_v1.voto_familias_tokens`).

## Por qué
El motor carga las familias laterales globbeando `motor/motor/familias_tokens/*.json`.
La taxonomía vivía en `motor/laterales/taxonomia_geopolitica/`, donde ningún código
la referencia por nombre, así que sus tokens no se activaban. Nada está "cableado"
per se: el motor activa los tokens por su estructura al cargar los archivos de
`familias_tokens/`. Mover los archivos a donde el motor busca es la solución.

## Verificación por ejecución (motor-cameo, 2026-11-13)
- Llamada directa al código real del motor (`laterales_unico_v1.voto_familias_tokens`,
  caso Napoleón 10 cortes): **n_familias cargadas: 26** (antes 16), **taxonomía presente:
  10 de 10**, 9 tokens por familia, 275 tokens totales en familias_tokens/ (antes 185).
- Los 90 tokens no colisionan con el 244 (0 colisiones) ni con nombres de familia
  existentes. Pesos preservados tal cual (contra positivos 0.75–0.85, como en la fuente).
- Voto en el caso Napoleón: ACTIVA_MUDA, 0 señal (sin solape de palabras con el caso).
  Esperado: los laterales solo votan cuando hay solape; no deciden H (can_decide_H: False).
- `en_puente`: 0 para las 10 familias (sus tokens no están en PUENTE_244_FAMILIAS.json).
  Igual que 15 de las 26 familias laterales; no es un fallo del traspaso.
- La corrida completa Napoleón 10 cortes (NAPOLEON_10CORTES_TAXGEO) llegó al timeout
  interno de 90 s dos veces (antes corría en 84–88 s); el RESULT no se escribió.
  Pendiente: revisar si el costo extra de 10 familias empuja el tiempo sobre el límite.

## Archivos
- `motor/motor/familias_tokens/cibernetica_ceguera_sensorial_algedonica.json`
- `motor/motor/familias_tokens/comunes_colapso_por_sobreexplotacion.json`
- `motor/motor/familias_tokens/geopolitica_interdependencia_armada.json`
- `motor/motor/familias_tokens/geopolitica_sobreextension_imperial_kennedy.json`
- `motor/motor/familias_tokens/geopolitica_trampa_recursos_rentismo.json`
- `motor/motor/familias_tokens/institucional_deriva_extractiva.json`
- `motor/motor/familias_tokens/juego_compromiso_irreversible_chicken.json`
- `motor/motor/familias_tokens/juego_escalada_dilema_seguridad.json`
- `motor/motor/familias_tokens/sistemica_acoplamiento_estrecho_accidente_normal.json`
- `motor/motor/familias_tokens/transicion_salida_voz_lealtad_hirschman.json`
- Esta nota: `motor/corridas_ciegas_20261113/NOTA_TAXGEO_FAMILIAS_TOKENS_20261113.md`
