# Corridas ciegas Z90 — 2026-11-13

Ocho corridas ciegas completas (recibo COMPLETED), selladas en el repo por el desbloqueo oficial de Marco.

## Las ocho

| Caso | Sujeto | H1 | H2 |
|---|---|---|---|
| ANONIMO_Z90 | Einstein (1879–1955) | sabio | creador |
| ANONIMO2_Z90 | Rembrandt (1606–1669) | sabio | erizo |
| ANONIMO3_Z90 | Elvis v1 (1935–1977) | 20_sacrificio | sabio |
| ANONIMO3_Z90_v2 | Elvis v2 (con consumo_sustancias) | 20_sacrificio | erizo |
| TRANSICION1_Z90 | Tulipomanía (1634–1637) | creador | sabio |
| TRANSICION1_Z90_v2 | Tulipomanía + tokens Minsky | sabio | minsky_03_ponzi |
| TRANSICION2_Z90 | Revolución Francesa (1789–1799) | tainter_01 | sustancias_03 |
| ANONIMO4_Z90 | Che Guevara (1928–1967) | gobernante | sustancias_03 |

Detalle y hallazgos: `HALLAZGOS_TOKENS_CIEGOS_Z90_20261113.md` (con los hashes SHA-256 de cada entrada y salida).

## Archivos

- Reporte por corrida: `REPORTE_<CASO>.md` (en esta carpeta).
- Recibo de ejecución: `RESULT_<CASO>_RECIBO_EJECUCION.json` (en esta carpeta).
- Entrada: `casos/precedentes/<CASO>/entrada.json`.
- RESULT crudo (10–13 MB): fuera por tamaño; referenciado por SHA-256 en el HALLAZGOS (precedente F003/F004).

## Notas

- El héroe no corona en ninguna de las 8. El trono corona H1 por primera vez en Che (gobernante, 35.22, el puntaje más alto de las pruebas ciegas).
- sustancias_03_severo es falso positivo sistemático: top 2 en 4 de 8 corridas sin consumo real (Rembrandt, Elvis, Revolución, Che).
- Einstein: la salida en el HALLAZGOS es el hash del recibo; el archivo actual en `motor/` fue reescrito por los laterales post-corrida (que además dieron un NameError `_gate_z90` después de escribir RESULT y recibo). Las otras 7 salidas son el hash del archivo actual.
