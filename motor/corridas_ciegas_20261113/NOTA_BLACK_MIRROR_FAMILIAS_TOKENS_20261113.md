# Black Mirror en familias_tokens/ — 2026-11-13

## Qué se hizo
Los 18 conceptos Black Mirror de tecnodistopía (`STINKBOX_BLACK_MIRROR_CANDIDATOS.json`,
familia `black_mirror_tecnodistopia_lateral`, registro documental StinkBox, NO integrados
al motor hasta ahora) se convirtieron en la familia lateral
`motor/motor/familias_tokens/black_mirror_tecnodistopia_lateral.json`.

## Por qué
Regla de Marco 2026-11-13: todo lo que llega al StinkBox nutre el repositorio de
tokens (`familias_tokens/`, junto al 244) y se activa en conjunto según la carga
semántica — sin deduplicación, sin que uno se sobreponga al otro (superposición),
sin doble peso. Los 18 conceptos estaban solo como registro documental
(`integrated_into_motor: False`).

## Pesos (asignación explícita)
Los candidatos no traían pesos de origen. Asignación por estatus documental,
documentada en el archivo: VERIFICADO -> 0.78 (16 tokens), NO_VERIFICADO -> 0.65
(2 tokens). Todos en favor (son conceptos distópicos que apoyan la lectura
tecnodistopía); contra vacío, como las familias mort_*.

## Verificación por ejecución (motor-cameo, 2026-11-13)
- Llamada directa al código real del motor (`laterales_unico_v1.voto_familias_tokens`,
  caso Napoleón 10 cortes): **n_familias cargadas: 27** (antes 26),
  **Black Mirror presente, 18 tokens**; tokens laterales totales: 293 (antes 275).
- 0 colisiones con el 244 y 0 con otros laterales. `en_puente`: 0 (igual que 15 de
  las 27 familias laterales). Voto ACTIVA_MUDA en Napoleón (sin solape de palabras
  con el caso; los laterales no deciden H).

## Pendiente (pregunta abierta de Marco 2026-11-13)
El problema de los "finales": ¿qué nos dice que algo ES un final como tal?
Un final también puede ser un inicio. Parte compleja, sin resolver.
