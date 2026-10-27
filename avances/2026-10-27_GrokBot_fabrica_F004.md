# 2026-10-27 — GrokBot — fábrica de casos, lote F004

## Qué cambió
- Lote F004: 10 sujetos históricos nuevos, ninguno repetido de F001–F003 ni de los casos previos. Desenlaces: 3 auges, 1 meseta, 2 caídas y 4 rupturas.
- Semillas en `casos/fabrica/semillas_lote_F004.py`, con el mismo formato que F003. Cada afirmación lleva su enlace de Wikipedia en inglés, consultado el 2026-10-27.
- Preparado con `fabrica.py preparar-z`. La compuerta GATE_Z_TRABAJO_20261024 dio OK al segundo intento.
- Destinos, familias y lista negra del custodio: `/workspace/FABRICA_CUSTODIA/F004/destinos_lote_F004.py`, fuera del repo. Lo sellado vive en `cola/CAL_F004_*/`.
- **Aviso de ceguera (igual que F003).** Las semillas (`GrokBot-preparador-ciego-F004`) y los destinos (`GrokBot-custodio-rutina-F004`) los escribió el mismo ejecutor en la misma sesión. La ceguera es solo de procedimiento: hechos ≤ Z, compuerta Z y lista negra. Los sujetos se eligieron sabiendo su desenlace.
- Ajustes para pasar la compuerta. No se tocó el protocolo:
  - Dos evidencias tenían un claim_date de año completo (`1953`, `2001`) que cae después de Z. Se precisaron a `1953-06` y `2001-07`.
  - En Truman se quitaron "muere/murió" de la lista negra, porque el texto cita la muerte de Roosevelt, que es un hecho previo a Z.
  - Antes de correr, en Chanel se quitaron "muere/murió" (la muerte de Capel es de 1919, previa a Z). En Jrushchov se cambió "octubre" por "octubre de 1964", porque la crisis de octubre de 1962 es previa a Z. En Mendel se cambió "abad" por "nombrado abad"/"abad del monasterio", porque "abadía" aparece en un hecho previo.
  - En Lay se reemplazó "quiebra de la tienda familiar" por "fracaso", para no chocar con su lista negra.
- `lotes/F004_PRECOMPROMISO_REGLA.json` se escribió ANTES de correr, con la regla 022 congelada por su sha256 y los hashes de entrada, desenlace y destino de los 10 casos.
- `correr` se lanzó con `FABRICA_SYNC=0`, para respetar la orden de hacer un solo push. La sincronización StinkBox → repo (stinkbox/tokens.jsonl + casos/resultados/resultados.jsonl) se hizo después con las mismas funciones de `scripts/sincronizar_storage.py` (resumenes_lote, tokens_corrida, anexar_tokens), pero sin el commit ni el push propios. Todo va en un único commit.

## Antes → ahora
- casos/fabrica/cola/CAL_F004_01…10/: antes no existían; ahora tienen entrada.json, desenlace_sellado.json y destino_sellado.json.
- casos/fabrica/lotes/F004_PRECOMPROMISO_REGLA.json, F004_COMPROMISO.json y F004_RESUMEN.json: creados.
- casos/fabrica/calibracion_acumulada.csv: pasó de 30 a 40 filas. CALIBRACION_ACUMULADA.md: regenerado.
- casos/resultados/resultados.jsonl: +10 resúmenes (modelo GrokBot_fabrica).
- stinkbox/tokens.jsonl: +28 091 observaciones de las 10 corridas.

## Hashes canónicos verificados (antes y después: iguales)
- motor/motor/Engine_V5_CANONICO_SOLO.py `665c39a2861e58772522e91272563260d980908b1d4ab9f7092d3413d0c36082`
- motor/motor/patterns_final_v14.json (244) `d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1`
- motor/motor/apuesta_destino_personal_022.py `4252fd4564877183fd8be86f579fdde59635eb547c139a04dd79acedc349b302`
- Los candados de `correr` dieron true antes y después, también en la copia temporal. `git diff HEAD -- motor/` está vacío.

## Pruebas
- motor/tests/test_arnes_calibracion.py: 7/7.
- Corrida F004: 10/10 sellados, `correr` con exit 0. Registro sellado sha256 210e7b1f3b3d42e4db7de251c022573bec0b16b411753deaf5a5d10f377db5bc.
- Recibos de ejecución, 10/10 en cada etapa: motor_run COMPLETED, monte_carlo EXECUTED, external_archetype_search EXECUTED_WITH_RESULTS, hash Engine/catálogo MATCH, candado_plugins OK y stinkbox ingest OK.
- unification_manifest_check dio DRIFT_WARNED en 10/10. Es un aviso, igual que en lotes previos.
- Compuerta Caldero: OK, 10/10 EJECUTADO.
- Compuerta piezas (CEB): OK, con 0 FALLO_EJECUCION y 0 REQUIERE_CONTRATO.
- Severidades CEB en las 10 salidas: 349 OK, 581 INFO_CORRIO_SIN_SENAL (la pieza corrió y no encontró señal) y 10 INFO_OMISION_CONTRACTUAL.
- La omisión es solo `caldero_run.py`, "pieza histórica sustituida (contrato: ya no debe correr)". La sustituye caldero_ii_cuadrantes, que dio OK 10/10.

## Resultados F004
| Caso (Z) | Real | H1 | Set | Apuesta | Destino apostado | Destino |
|---|---|---|---|---|---|---|
| Wagner 1864-01-01 | auge | sí | sí | sí | auge | sí |
| J.-L. David 1794-07-01 | caida | no | no | no | auge | no |
| Oppenheimer 1953-10-01 | caida | no | no | no | caida | sí |
| Mendel 1867-01-01 | meseta | sí | sí | sí | meseta | sí |
| Jrushchov 1964-01-01 | ruptura | no | no | no | caida | no (polaridad sí) |
| Truman 1948-08-01 | auge | no (H2 sí) | no | no | caida | no |
| Chanel 1920-01-01 | auge | sí | sí | sí | auge | sí |
| Lesseps 1887-01-01 | ruptura | no | no | no | caida | no (polaridad sí) |
| Kenneth Lay 2001-08-01 | ruptura | no | no | no | ruptura | sí |
| Luis II de Baviera 1886-01-01 | ruptura | no | no | no | caida | no (polaridad sí) |

F004: H1 3/10, H2 1/10, set 3/10, apuesta 3/10, destino exacto 5/10, polaridad 8/10.

## Acumulado (40 filas, 37 evaluados, 3 no sellados)
H1 9/37 (24 %), H2 4/37, set 12/37 (32 %), apuesta 9/37 (24 %), destino exacto 14/32, polaridad 22/32.

## Patrón visible
- **Sesgo de continuidad, sin cambios.** El escenario principal salió CONTINUIDAD_ASCENDENTE en 9 de 10 casos. La excepción fue Oppenheimer (MESETA). H1 y H2 siguen saliendo de logro, ambición o audacia (schwartz_07_logro, 30_ambicion, 9_audaz_empresa), aunque la persona vaya a caer.
- **H1 solo acierta en auges de logro o en el sabio.** Acertó en Wagner, Chanel y Mendel, igual que Dickens, Carnegie y Pasteur en lotes previos. En las 6 caídas/rupturas acertó 0/6.
- **La apuesta de destino 022 sí lee la bajada.**
  - Acertó la polaridad en 5 de 6 caídas/rupturas. Falló J.-L. David, donde apostó auge.
  - Volvió a confundir caída con ruptura: Jrushchov, Lesseps y Luis II dieron caída cuando vino ruptura, igual que Fouquet, Law y Pedro II en F003.
  - Truman, caso de remontada, salió como caída: el mismo error que Lincoln en F003.
- **Rareza para revisar (no la toqué).** En Truman, H2 = schwartz_07_logro, pero la lista "hipotesis" del registro es [9_audaz_empresa, mauss_02_deuda_de_honor]. Por eso H2 cuenta como acierto y el set no. H2 y la segunda hipótesis del set no coinciden; Claude o ChatGPT deberían revisarlo en el arnés.

## Fuentes flojas
- Todo viene de Wikipedia en inglés en vivo: fuente secundaria, consultada el 2026-10-27, sin copias congeladas.
- Lesseps C3: Wikipedia no fecha los deslizamientos y muertes. El texto dice "dogged the project" después de 1882, y se fechó en 1886 como corte.
- Lay C3, evidencia 1 ("aprobaba sin preguntar por los detalles"): es la caracterización del artículo Enron_scandal, sin fecha precisa. Se fechó en 2001-07.
- Mendel C3: que su superior Napp lo desanimó viene de una carta sin fecha exacta en el artículo. Se fechó en 1863.
