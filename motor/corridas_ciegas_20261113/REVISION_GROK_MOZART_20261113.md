# Revisión Grok — Reproducción gravedad Mozart (Z90)

**Fecha:** 2026-11-13 ~19:00 CST  
**Modelo:** Grok 4.7  
**Rama:** `alterno/reconexion-2a1`  
**Delegación:** `DELEGACION_GROK_REPRODUCIR_GRAVEDAD_20261113.md`

## 1. Bloqueo de entrada

La delegación pide aplicar las fórmulas sobre:

`motor/RESULT_MOZART_CON_TEXTO_Z90_20261113.json`

Ese archivo **no está** en la rama `alterno/reconexion-2a1` (ni en `motor/`, ni en `motor/corridas_ciegas_20261113/`, ni bajo otro nombre con "MOZART"). Los RESULT disponibles son Napoleón, Transición1/2, Anónimos y calibración. Sin el RESULT completo no se puede recomputar de forma independiente `peso_Z` de cada nudo, los saltos por corte ni la correlación de Pearson a partir de `P_FULL_244`.

Lo que sí está y se usó:

- Paper y Spec (fórmulas).
- `motor/COMPARACION_GRAVEDAD_CASOS_20261113.json` (valores ya calculados para Mozart).
- Implementación `motor/motor/lateral_comportamiento_post_meseta_v1.py` (solo para verificar que las fórmulas del paper coinciden con el código; no se ejecutó sobre Mozart).

## 2. Valores conocidos vs. lo publicado

Fuente: `COMPARACION_GRAVEDAD_CASOS_20261113.json` y tabla 12 del paper. Coinciden entre sí.

| Campo | Publicado (paper / comparación) | Estado |
|-------|----------------------------------|--------|
| Sol (H1) | `utopia_autonomia_atenas` | Coincide |
| Peso Sol Z | 0.7985 | Coincide |
| Nudos | 6 | Coincide |
| Capturados | 0 | Coincide |
| Siendo jalados | 1 (`predictivo_02_mdp_politica_optima`) | Coincide |
| Resisten | 1 (`dumezil_f3_fecundidad`) | Coincide |
| Cometa | C6, 6 nudos, salto 0.482 | Coincide |
| Proporcionalidad | **-0.777** | Coincide |
| Punto no considerado | `situacion_dramatica_ambicion` (rango Z 10, pendiente 0.3571) | Coincide |
| Cocina abajo | 3 familias / 0 tokens; emergentes: 2 | Coincide |

No se re-calcularon estos números desde el RESULT porque el archivo no está. La coincidencia es entre las dos fuentes publicadas, no una reproducción independiente como la de Gemini sobre Napoleón.

## 3. Revisión del spec y del paper

### 3.1 ¿Las fórmulas se entienden y se pueden reproducir sin el código?

Sí. El paper (§3–§9) y el Spec JSON dan:

- Condición de meseta (`MESeta_O_ESTABILIZACION`).
- Comportamiento (conteos de cocina, emergentes, formas).
- Punto no considerado (primer emergente o subiendo que no está en el top).
- Sol = H1, peso en Z desde `P_FULL_244`.
- Estados de nudo: CAPTURADO (`dist ≤ 0.01`), SIENDO_JALADO (`dist > 0.05` y `pend ≥ 0.5`), RESISTE (`dist > 0.05` y `pend < 0.2`), resto EN_TRANSITO.
- Cometa = corte con mayor `(nudos_que_suben, salto_total)` donde salto > 0.05.
- Proporcionalidad = Pearson(pendiente, distancia_al_sol), mínimo 3 nudos.
- Proyectivo: captura por extrapolación monótona + alerta de pulso.

Estas reglas coinciden con `leer_gravedad` y `proyectar_gravedad` en el lateral. No hace falta el código para entenderlas.

### 3.2 ¿Falta algo para reproducirlo en cualquier caso?

Sí, para un caso nuevo:

1. El RESULT completo con `motor.cuts[].P_FULL_244` y `movimiento_de_fondo.familias_bajo_top5_subiendo_de_rango` (pendiente y rango). Sin eso no se puede calcular distancia, estado, cometa ni Pearson.
2. El ejemplo trabajado de Napoleón en el Spec es autosuficiente. Mozart no tiene un ejemplo trabajado con la lista de nudos y sus pesos; solo el resumen. Por eso Gemini pudo reproducir Napoleón al 100 % y aquí no se puede hacer lo mismo con Mozart.
3. El campo `corte` en cada elemento de `motor.cuts` es necesario para nombrar el cometa (C6, C9, etc.).

### 3.3 ¿La proporcionalidad negativa de Mozart (-0.777) tiene sentido?

Sí, con la interpretación del Spec (§8.4 / `formulas.gravedad.proporcionalidad.interpretacion`):

- **Negativa** = cerca del Sol sube más rápido = gravedad clásica / consolidación.
- **Positiva** = lejos del Sol sube más rápido = convergencia (caer hacia el Sol).

Napoleón +0.568 es convergencia (los lejanos aceleran). Mozart -0.777 es el caso opuesto: los que ya están cerca del Sol (`utopia_autonomia_atenas` a 0.7985) son los que suben más rápido. Eso es coherente con "consolidación" y con que haya 0 capturados y solo 1 siendo jalado. El signo no es un error de signo en la fórmula; es el patrón que el Spec predice para un campo que se está cerrando alrededor del atractor.

### 3.4 ¿El límite honesto está bien planteado?

Sí. El Spec y el paper (§9.3) dejan claro que el cometa es retrospectivo: el salto lo produce un pulso nuevo de `masa_favor` que llega con los tokens del corte. No se puede predecir el corte exacto ni el tamaño antes de que entre el pulso. Lo proyectivo es la extrapolación de la tendencia de distancia y la alerta cuando el pulso ya entró (intervalo observado 3–4 cortes: Napoleón C5→C9, Mozart C6→C9). Eso no promete el corte del cometa; solo avisa.

## 4. Conclusión

- Los valores publicados para Mozart son internamente consistentes (paper = comparación JSON).
- El Spec es legible y reproducible sin código, siempre que se tenga el RESULT.
- La proporcionalidad negativa es la interpretación correcta según el Spec (consolidación).
- El límite honesto está bien puesto.
- **No se puede afirmar una reproducción independiente de Mozart** hasta que esté disponible `RESULT_MOZART_CON_TEXTO_Z90_20261113.json` (o equivalente) con `P_FULL_244` y la lista de nudos.

## 5. Qué falta para cerrar

Subir el RESULT de Mozart a la rama (o indicar la ruta real si ya existe bajo otro nombre). Con eso se puede recomputar sol, nudos, cometa y Pearson y comparar cifra por cifra como hizo Gemini con Napoleón.
