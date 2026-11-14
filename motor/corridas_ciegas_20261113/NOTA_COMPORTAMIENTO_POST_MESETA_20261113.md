# Lateral comportamiento post-meseta — 2026-11-13

## Idea (Marco)
No es leer nada más el fondo. Una vez que la medición SE ESTABILIZA (meseta),
se ve el COMPORTAMIENTO: cómo se mueve TODO en general. Eso da trazabilidad y
puede hacer emerger un punto que antes no se había considerado. Y se tiene que
MENCIONAR tal cual en la salida, porque si no los modelos que traducen el motor
no lo ven: su entrenamiento es ver los top, entonces no ven lo que pasa abajo.
Equivalente a cuando se encontró el eje con las fórmulas después de ver la hélice.

## Pieza
`motor/motor/lateral_comportamiento_post_meseta_v1.py` (SENSOR, can_decide_H False).
Contrato: `motor/COMPORTAMIENTO_POST_MESETA_V1.md`.
- `leer_resultado(result)`: lectura completa sobre un RESULT (fondo + picos + régimen).
- `observar(case, motor, pred)`: sensor para post_predictor (lee el régimen de pred).

## Verificación (FINAL27)
`leer_resultado` contra `RESULT_NAPOLEON_10CORTES_FINAL27.json`: en_meseta True,
7 familias bajo el top5 suben de rango, 0 cocinando, 0 emergentes por umbral,
punto no considerado `dumezil_f2_fuerza` (rango Z 23, pendiente 1.0286,
LATENTE_DORMIDO). Lectura guardada en
`motor/corridas_ciegas_20261113/LECTURA_COMPORTAMIENTO_POST_MESETA_FINAL27.json`.

## Cableado (hunk, PENDIENTE de aplicar a la rama)
El hunk está aplicado SOLO en la copia motor-cameo (`motor/motor/laterales_unico_v1.py`,
en `post_predictor`, después de `par_superpuesto_entrada`, antes de `return out`).
NO se sube el archivo completo (la copia trae otros cableados locales). Hunk:

```python
    def comportamiento_post_meseta():
        # COMPORTAMIENTO_POST_MESETA_V1: una vez estabilizado (meseta), ver el
        # comportamiento de TODO (no solo el fondo). Sensor post-predictor;
        # solo observa, no decide H. El fondo corre después de post_predictor,
        # así que aquí solo se deja constancia del régimen; la lectura completa
        # se hace con leer_resultado() sobre el RESULT.
        m, _ = _load(base, "lateral_comportamiento_post_meseta_v1.py", "lu_comp_post_meseta")
        if m is None:
            return "NO_CORRE", "falta lateral_comportamiento_post_meseta_v1.py", None
        r = m.observar(case, motor, pred)
        if not r.get("en_meseta"):
            return "ACTIVA_MUDA", f"no en meseta (regimen={r.get('regimen')})", r
        return "ACTIVA", f"en meseta ({r.get('regimen')}): lectura completa con leer_resultado()", r
    out["comportamiento_post_meseta"] = _pieza("comportamiento_post_meseta", "lateral_comportamiento_post_meseta_v1.py", "SENSOR (comportamiento una vez estabilizado, post-predictor; no decide H)", comportamiento_post_meseta, base, reg)
```

El ancla es `out["par_superpuesto_entrada"] = _pieza(...)` seguida de `return out`.
