# REVISION — lote TRADUCTOR_V28_20261113

Revisión de los 3 casos. Leído para esta entrega: `CONTRATO_GUARDAR_CORRIDAS.md`,
`PROTOCOLO_EJECUCION_Y_LECTURA_LLM.md` y `casos/REGLAS.md` (ver `LECTURA.json`).

## Hallazgos sistemáticos

- Los 3 recibos dicen COMPLETED; los SHA-256 de RESULT y entrada registrados en cada
  recibo coinciden con los archivos reales (verificados al construir el lote).
- El `monte_carlo` del RESULT es nulo en los 3 casos, así que el INTERPRETABLE lo trae
  vacío (`{}`), igual que en el lote F003_F004_20261111. No se inventa ningún valor.
- El traductor de salida v2.8 (`motor/motor/lateral_traduccion_salida_v1.py`, VERSION
  `v2.8_20261114`) se verificó por ejecución sobre los 3 casos con el script
  `motor/tests/test_traductor_v24.py`: 0 violaciones en los 3. La lectura de LIMBO_6C
  quedó guardada en `LECTURA_LIMBO_6C_v28.json` (lectura en la prosa del input + anexo
  con los números). Las lecturas de MOZART_NINO_7C y CAL_F001_02_TESLA_7C dieron
  0 violaciones pero sus salidas no se guardaron a archivo.
- Los RESULT crudos (~32 MB entre los 3) no se suben; su SHA-256 queda en
  `MANIFIESTO.json` y en cada INTERPRETABLE.

## Por caso

- LIMBO_6C (6 cortes, 113.586 s): H1 `eterno_retorno_01_caos_primordial`, H2 `apego_03_evitativo`,
  grado AJUSTADA, 10 hipótesis en el conjunto abierto. Es el caso vivo
  (primera persona, historia contada por la persona): el tema central es un estado
  en el que ya está, no un destino; el cierre de la lectura v2.8 dice el crecimiento
  del tema central, no un movimiento hacia él.
- MOZART_NINO_7C (7 cortes, 77.98 s): H1 `arquetipo_el_creador`, H2 `9_audaz_empresa`,
  grado AJUSTADA, 7 hipótesis en el conjunto abierto. Niño genio:
  el tema se fija temprano (a los 4 años).
- CAL_F001_02_TESLA_7C (7 cortes, 76.987 s): H1 `22_todo_sacrificado_por_una_pasion`, H2 `30_ambicion`,
  grado FRAGIL, 10 hipótesis en el conjunto abierto. Caso de
  calibración F001 con 7 cortes (case_id CAL_F001_02_TESLA_7C, distinto del
  CAL_F001_02_TESLA del lote F001_F002_20261111).
