# Hunks pendientes — revisión por ejecución (2026-11-15)

Copia: `~/workspace/u6-alterno/motor-cameo/` (rama alterno/reconexion-2a1).
Verificado por ejecución, no solo por lectura de código.

## 1. par_superpuesto_entrada — APLICADO Y VERIFICADO

- Lateral: `motor/motor/lateral_par_superpuesto_entrada_v1.py` (v1_20261113),
  `observar(entrada, motor, pred)`.
- Cableado: `motor/motor/laterales_unico_v1.py`, `post_predictor`, líneas 1169–1180
  (`out["par_superpuesto_entrada"] = _pieza(...)`).
- Verificación por ejecución: RESULT `NAPOLEON_10CORTES_FINAL27`
  (`motor/runs/ESTANDAR__NAPOLEON_10CORTES_FINAL27/_PRIMARY_RESULT.json`),
  `laterales_unico.post.par_superpuesto_entrada` presente
  (contrato PAR_SUPERPUESTO_ENTRADA_V1, `declarado=false` — correcto, el input
  FINAL27 no trae el campo). También presente en `NAPOLEON_CON_TEXTO_Z90_20261115`.
- Conclusión: el hunk YA está aplicado en la copia local (venía en el snapshot
  de FINAL27). Nada que aplicar aquí; falta que llegue a la rama por el flujo
  normal (hunks, no archivo completo).

## 2. comportamiento_post_meseta — APLICADO EN LA COPIA, VERIFICADO AHORA

- Lateral: `motor/motor/lateral_comportamiento_post_meseta_v1.py` (v3_20261113),
  `observar(case, motor, pred, fondo=None, picos=None)`, `leer_resultado()`,
  `proyectar_gravedad()`.
- Cableado: `motor/motor/laterales_unico_v1.py`, `post_predictor`, líneas 1182–1195
  (`out["comportamiento_post_meseta"] = _pieza(...)`).
- Verificación por ejecución: NO estaba en el snapshot de FINAL27
  (grep 0 en `motor/runs/ESTANDAR__NAPOLEON_10CORTES_FINAL27/laterales_unico_v1.py`
  y ausente en su RESULT). SÍ está en la copia actual y SÍ corre:
  RESULT `NAPOLEON_CON_TEXTO_Z90_20261115`,
  `laterales_unico.post.comportamiento_post_meseta` presente
  (contrato COMPORTAMIENTO_POST_MESETA_V1, `en_meseta=false` en post_predictor —
  solo nota de régimen). La lectura completa con `leer_resultado()` sobre el RESULT
  da `en_meseta=True`, Sol `arquetipo_el_gobernante` 0.7813, 7 nudos, cometa C9
  (3 nudos, salto 0.32), proporcionalidad 0.568 NO CONCLUYENTE (BAJA_MUESTRA);
  `proyectar_gravedad()` da `cometa_previsto=null`.
  (Detalle guardado en `motor/runs/ESTANDAR__NAPOLEON_CON_TEXTO_Z90_20261115/LECTURA_NAPOLEON_CON_TEXTO.json`.)
- Conclusión: el hunk YA está aplicado en la copia local; falta que llegue a la
  rama por el flujo normal (las líneas 1182–1195, no el archivo completo).

## 3. traduccion_salida — NO APLICADO; el hunk NO existe documentado; y post_predictor es el punto EQUIVOCADO

- Lateral: `motor/motor/lateral_traduccion_salida_v1.py` (v2.8_20261114),
  `traducir(result, entrada)` + `observar(case, motor, pred)` que llama
  `traducir(pred, case)`.
- Cableado: AUSENTE en `motor/motor/laterales_unico_v1.py` (grep 0 para
  `traduccion_salida`). Tampoco lo llama `correr_estandar.py`
  (grep 0 para `traduc`/`LECTURA`); ninguna corrida estándar emite LECTURA.json.
- El doc `motor/TRADUCCION_SALIDA_V1.md` afirma: "El hunk de cableado en
  post_predictor de `laterales_unico_v1.py` queda DOCUMENTADO aquí" — FALSO:
  el archivo no contiene ningún hunk (ningún bloque de código de reemplazo).
  `motor/corridas_ciegas_20261113/NOTA_TRADUCCION_SALIDA_20261113.md` (línea 51)
  repite la misma frase. El doc además está desactualizado: dice
  VERSION v1_20261113 (el lateral es v2.8_20261114) y la regla "agnóstica y
  ambigua como profecía" ya no está vigente.
- ¿Se PUEDE aplicar con reemplazos exactos? SÍ, mecánicamente: el ancla es
  exacto (líneas 1195–1196: la línea
  `out["comportamiento_post_meseta"] = _pieza(...)` seguida de `    return out`),
  y `_pieza(nombre, archivo, rol, fn, base, reg, **extra)` acepta la llamada.
  El hunk sería el `def traduccion_salida(): ...` + la línea
  `out["traduccion_salida"] = _pieza("traduccion_salida", "lateral_traduccion_salida_v1.py", "SENSOR (traducción de salida a prosa; no decide H)", traduccion_salida, base, reg)`
  insertados antes de `return out` (línea 1196).
- PERO sería HUECO en post_predictor — verificado por ejecución: `pred` (el dict
  del predictor que recibe post_predictor) NO trae H1, H2 ni movimiento_de_fondo
  (se ensamblan en el RESULT después de post_predictor; verificado en el RESULT
  de NAPOLEON_CON_TEXTO: `predictor` no tiene esas claves, el RESULT sí).
  `traducir(pred, case)` daría h1=None, h2=None, sin `series_familias` → lectura
  degenerada (frase genérica segura). El punto correcto para una traducción real
  es DESPUÉS del RESULT sellado, en `correr_estandar.py` (emitir LECTURA.json
  junto a RESULT+RECIBO), no en post_predictor.
- Hallazgo adicional (verificado por ejecución): al correr `traducir()` sobre el
  RESULT de NAPOLEON_CON_TEXTO devuelve `violaciones=['heroe']` y la lectura se
  reemplaza por la frase genérica segura. Es la colisión conocida: la familia
  suelta `heroe` del 244 colisiona con la palabra común "héroe" en la prosa
  (`arquetipos_luces` trae `arquetipo_heroe`). El anexo sale completo y correcto
  (H1/H2, Sol 0.7813, cometa C9, etc.); solo la lectura se pierde. El guardia
  `_verificar_lectura` necesita distinguir el ID de familia de la palabra común.
  Esto NO es un hunk de cableado: es un arreglo del guardia del traductor,
  pendiente de decisión.
