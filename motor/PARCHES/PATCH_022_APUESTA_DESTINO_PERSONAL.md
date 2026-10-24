# PATCH 022 — Apuesta de destino personal (2026-10-24)

Autorizado por Mj ("Sí", 24-oct-2026). Siguiente número después de 021 (predictibilidad_set_021).

## Qué hace
Agrega un campo NUEVO `apuesta_destino_personal` con una sola etiqueta: `auge | meseta | caida | ruptura`.
No reemplaza nada: H1/H2, set abierto y apuesta temática multiescenario quedan igual (el campo trae
`H_y_apuesta_tematica_intactos: true` como comprobación). `can_decide_H=False`. Se apaga con `DESTINO_022=0`.

## Regla (módulo `motor/motor/apuesta_destino_personal_022.py`)
Lee `movimiento_de_fondo.series_familias` (activación por corte de las familias del catálogo 244, cortes <= Z) y suma tres polos
fijados por el significado del nombre de la familia: RUPTURA (quiebre brusco), CAIDA (pérdida de posición o de apoyo), AUGE (ganancia o consolidación).
balance = AUGE − (CAIDA + RUPTURA). Umbrales: los de movimiento_de_fondo (EPS 0,01; GRANDE 0,0624; NETO 0,03).
1. ruptura: RUPTURA salta >= GRANDE en el último tramo y lo adverso domina en Z.
2. caida: el balance empeora >= NETO, o lo adverso domina y sube, o el eje del sujeto se apaga con balance negativo.
3. auge: el balance mejora >= NETO y lo favorable domina en Z.
4. meseta: lo demás.

## Archivos
- nuevo: `motor/motor/apuesta_destino_personal_022.py`
- `motor/motor/MOTOR_V15_3_UNICO_20260927.py`: hook después de `result.update(_u4_attach)`
- `motor/calibracion/arnes_calibracion.py`: extrae `apuesta_destino_personal`; evalúa `y_destino` y `y_destino_polaridad` si el desenlace trae `destino`
- `casos/fabrica/fabrica.py`: `destino_sellado.json` aparte (con hash en el compromiso), columnas de destino y `--rehacer`
- Diff: `PATCH_022_APUESTA_DESTINO_PERSONAL.diff`

## Límites honestos
Las listas de polos se escribieron cuando ya se conocían los desenlaces de F001 (5 casos). El acierto en F001 NO valida la regla;
la prueba real son los lotes nuevos sellados. La regla queda congelada por su sha256 (`lotes/F001_D022_PRECOMPROMISO_REGLA.json`).
