# APARTADO EN ESPERA — calibrar cuando haya más casos; no concluyente

Por instrucción de Mj se detiene aquí el estudio del límite. La corrida local que ya había terminado y sus archivos se conservan, sin nuevos cálculos ni calibraciones tras el STOP.

## Material archivado

- `limite_giro.py`, `METODO.md`: implementación y diseño exploratorio.
- `RESULTADOS.json`, `DISTRIBUCIONES.npz`: resultados locales sin validación/calibración sobre más casos; **no concluyentes**.
- `GIRO_VS_N.png`: figura exploratoria anterior a la pausa, no evidencia de señal biográfica.
- `EJECUCION.log`, `TESTS.log`, `test_limite_giro.py`: trazabilidad y pruebas técnicas; que pasen no valida una hipótesis biográfica.

## Estado y límites de uso

Giro, misma cresta y radio en U se consideran **artefactos de la proyección**, no señal. El salto residual no ha acreditado señal robusta frente a los controles y multiplicidad; ver `../control_nulo_v1/SENALES_POR_PASO.md`.

El límite y su calibración quedan pendientes de más casos. SINDy, Markov, Laplace y cliodinámica también quedan pendientes: no se presentan aquí como modelos ejecutados o validados.

No se alimenta motor, H, ranking ni apuesta. No se modificaron Engine/244 ni `motor/motor/*.py`. **No reanudar por iniciativa automática. Commit local; sin push.**
