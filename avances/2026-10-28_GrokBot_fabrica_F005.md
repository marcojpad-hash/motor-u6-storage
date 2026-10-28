# 2026-10-28 — GrokBot — fábrica de casos, lote F005

## Qué cambió
- Lote F005: 10 sujetos históricos nuevos, ninguno repetido de F001–F004, Lote 01 ni casos previos (Mozart, Musk, Pío, Casanova). Desenlaces: 3 auges, 0 mesetas, 2 caídas y 5 rupturas.
- Semillas en `casos/fabrica/semillas_lote_F005.py`, con el mismo formato que F004. Cada afirmación lleva su enlace de Wikipedia en inglés, consultado el 2026-10-28.
- Preparado con `fabrica.py preparar-z`. La compuerta GATE_Z_TRABAJO_20261024 dio OK al segundo intento.
- Destinos, familias y lista negra del custodio: `/workspace/FABRICA_CUSTODIA/F005/destinos_lote_F005.py`, fuera del repo. Lo sellado vive en `cola/CAL_F005_*/`.
- **Aviso de ceguera (igual que F003–F004).** Las semillas (`GrokBot-preparador-ciego-F005`) y los destinos (`GrokBot-custodio-rutina-F005`) los escribió el mismo ejecutor en la misma sesión. La ceguera es solo de procedimiento: hechos ≤ Z, compuerta Z y lista negra. Los sujetos se eligieron sabiendo su desenlace.
- Ajustes para pasar la compuerta. No se tocó el protocolo:
  - La compuerta trata una fecha parcial como posterior a cualquier fecha completa del mismo periodo (`_peor` rellena con -99). Por eso cortes y claim_dates de año o mes completo chocaban con Z en el último día de ese periodo. Se movió Z al primer día del periodo siguiente: Haber 1933-01-01, Einstein 1905-01-01, Jobs 1996-11-01, Isabel 1558-11-01 y Melville 1851-10-01. Ningún hecho nuevo entró por eso.
  - Jobs C3 y sus evidencias pasaron de `1996` a `1996-10`. Melville C3 y su evidencia pasaron de `1851` a `1851-09`.
  - Kreuger: el token `vulnerabilidad_sistemica` no está en el vocabulario del 244. Se cambió por `vulnerabilidad`.
- `lotes/F005_PRECOMPROMISO_REGLA.json` se escribió ANTES de correr, con la regla 022 congelada por su sha256 y los hashes de entrada, desenlace y destino de los 10 casos.
- `correr` se lanzó con `FABRICA_SYNC=0`, para hacer un solo push. La sincronización StinkBox → repo (stinkbox/tokens.jsonl + casos/resultados/resultados.jsonl) se hizo después con las mismas funciones de `scripts/sincronizar_storage.py` (resumenes_lote, tokens_corrida, anexar_tokens), sin el commit ni el push propios. Todo va en un único commit.

## Antes → ahora
- casos/fabrica/cola/CAL_F005_01…10/: antes no existían; ahora tienen entrada.json, desenlace_sellado.json y destino_sellado.json.
- casos/fabrica/lotes/F005_PRECOMPROMISO_REGLA.json, F005_COMPROMISO.json y F005_RESUMEN.json: creados.
- casos/fabrica/calibracion_acumulada.csv: pasó de 40 a 50 filas. CALIBRACION_ACUMULADA.md: regenerado.
- casos/resultados/resultados.jsonl: +10 resúmenes (modelo GrokBot_fabrica).
- stinkbox/tokens.jsonl: +33 324 observaciones de las 10 corridas.

## Hashes canónicos verificados (antes y después: iguales)
- motor/motor/Engine_V5_CANONICO_SOLO.py `665c39a2861e58772522e91272563260d980908b1d4ab9f7092d3413d0c36082`
- motor/motor/patterns_final_v14.json (244) `d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1`
- motor/motor/apuesta_destino_personal_022.py `4252fd4564877183fd8be86f579fdde59635eb547c139a04dd79acedc349b302`
- Los candados de `correr` dieron true antes y después, también en la copia temporal. `git diff HEAD -- motor/` está vacío.

## Pruebas
- motor/tests/test_arnes_calibracion.py: 7/7.
- Corrida F005: 10 casos, 8 sellados y 2 NO_SELLADO, `correr` con exit 0. Registro sellado sha256 9e5380152ab6d9a96a8e9dff02cc970de1d3f4cf8517da760f548c610b41f702.
  - Los NO_SELLADO son Jobs y Nicolás II. Salieron con exit 6, TORTUGAS_REMEDIR y pausa reanudable (APUESTA_NO_AUTORIZADA_PAUSA_REANUDABLE). Es comportamiento previsto y no cuenta.
  - Su apuesta provisional, sin sellar, era MESETA en ambos.
- Recibos de ejecución, 10/10 en cada etapa: motor_run COMPLETED, monte_carlo EXECUTED, external_archetype_search EXECUTED_WITH_RESULTS, hash Engine/catálogo MATCH, candado_plugins OK y stinkbox ingest OK.
- terminal_resolution: RESUELTO_OPERACIONALMENTE en 8 casos y PAUSADA_REANUDABLE en 2.
- unification_manifest_check dio DRIFT_WARNED en 10/10. Es un aviso, igual que en lotes previos.
- Compuerta Caldero: OK, 12/12 EJECUTADO. Incluye los 2 checkpoints reanudables.
- Compuerta piezas (CEB): OK, con 0 FALLO_EJECUCION y 0 REQUIERE_CONTRATO.
- Severidades CEB en las 10 salidas: 326 OK, 604 INFO_CORRIO_SIN_SENAL y 10 INFO_OMISION_CONTRACTUAL. La omisión es solo `caldero_run.py`, pieza superada por caldero_ii_cuadrantes.

## Resultados F005
| Caso (Z) | Real | H1 | Set | Apuesta | Destino apostado | Destino |
|---|---|---|---|---|---|---|
| Courbet 1871-05-01 | ruptura | no | no | no | auge | no |
| Haber 1933-01-01 | ruptura | no | no | no | caida | no (polaridad sí) |
| Einstein 1905-01-01 | auge | no (H2 sí) | sí | sí | auge | sí |
| Hoover 1928-12-31 | caida | no | no | no | auge | no |
| Mussolini 1943-01-01 | ruptura | no | no | no | caida | no (polaridad sí) |
| Kreuger 1931-09-30 | ruptura | no | no | no | caida | no (polaridad sí) |
| Jobs 1996-11-01 | auge | NO_SELLADO | — | — | — | — |
| Nicolás II 1916-12-31 | ruptura | NO_SELLADO | — | — | — | — |
| Isabel I 1558-11-01 | auge | no | no | no | meseta | no (polaridad sí) |
| Melville 1851-10-01 | caida | no | no | no | auge | no |

F005 (8 evaluados): H1 0/8, H2 1/8, set 1/8, apuesta 1/8, destino exacto 1/8, polaridad 5/8.

## Acumulado (50 filas, 45 evaluados, 5 no sellados)
H1 9/45 (20 %), H2 5/45 (11 %), set 13/45 (29 %), apuesta 10/45 (22 %), destino exacto 15/40, polaridad 27/40.

## Patrón visible
- **H1 = 30_ambicion en 7 de 8 sellados.** La excepción fue Einstein (mbti_factor_intuicion_n). Ambición es el comodín del motor cuando la entrada describe ascenso, sea cual sea el desenlace. H1 acertó 0/8, el peor lote hasta ahora.
- **Escenario principal:** CONTINUIDAD_ASCENDENTE en 4 casos y MESETA en 4. Ningún caso dio un escenario de bajada, aunque 6 de los 8 sellados cayeron o se rompieron.
- **La regla 022 nunca apostó ruptura.**
  - Las 3 rupturas que leyó a la baja (Haber, Mussolini, Kreuger) las dio como caída. Es la misma confusión caída/ruptura de F003–F004.
  - Courbet (ruptura) salió como auge.
- **Las caídas tras la cima se leen como auge.** Hoover (recién electo) y Melville (tras la ambición creciente) son caídas que el motor leyó como auge: el mismo error de "cima = sigue subiendo" que Durant o Arbuckle.
- **Isabel I:** remontada desde la persecución, apostada como meseta. Acierta la polaridad (arriba/igual), pero no el destino exacto.

## Fuentes flojas
- Todo viene de Wikipedia en inglés en vivo: fuente secundaria, consultada el 2026-10-28, sin copias congeladas.
- Jobs C3: Wikipedia solo da "1996" para WebObjects y para "Apple was struggling". Se fechó en 1996-10, como conocido antes de Z.
- Melville C3: el artículo dice que la obra ballenera le llevó casi año y medio (primera mención el 1 de mayo de 1850), sin mes de cierre. Se fechó en 1851-09.
- Kreuger C1: el control de dos tercios a tres cuartos de la producción mundial viene sin fecha ("entre las guerras"). Se fechó en 1928.
- Haber C3: la preocupación creciente por el nacionalsocialismo se fechó en 1931 ("hacia 1931" en el artículo).
- Kreuger C3: los rumores de inestabilidad son "a mediados de 1931" en el artículo. Se fecharon en 1931-07.
