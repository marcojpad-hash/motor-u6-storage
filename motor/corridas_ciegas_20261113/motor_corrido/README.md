# Motor y runner que corrieron las ciegas Z90 (2026-11-13)

Corrección tras auditoría de Claude (punto 1) y aclaración del punto 3.
La rama trae ahora motor `cfb13415…` y runner `8e53cc16…` (con el cambio
de etiqueta de calibración). Esos NO son los que corrieron las 8 ciegas.

## El motor que corrió — SÍ recuperado, verificado byte a byte

Hay DOS motores, uno por lote. Los dos archivos están en esta carpeta,
extraídos de la historia git y verificados: su sha256 coincide con el
motor copiado dentro de cada run dir Y con el recibo de cada corrida.

| Motor (sha256) | Commit | Casos que corrió |
|---|---|---|
| `066af6844dd54085…` | 78b9a9a | Lote 1: Einstein (ANONIMO), Rembrandt (ANONIMO2), Elvis (ANONIMO3) |
| `b4d4d657e0691da4…` | d3eab75 | Lote 2: Che (ANONIMO4), Tulipomanía (TRANSICION1), Revolución (TRANSICION2) |

Archivos:
- `MOTOR_V15_3_UNICO_20260927__066af684.py` — motor del lote 1 (78b9a9a).
- `MOTOR_V15_3_UNICO_20260927__b4d4d657.py` — motor del lote 2 (d3eab75).

La diferencia entre ambos NO es solo etiquetas: d3eab75 ("cuartos") añadió
`rutas_vecinos` al puente del monomito (el plugin suma favor y contra
como evidencia del cuarto) + 32 líneas en `plugin_circulo_monomito_v2.py`.
Es cambio de lógica.

El motor `c8da733e…` (cabeza anterior de la rama, commit c9e5436) solo
corrió `TEST_CALIBRACION` (ver abajo). El MANIFIESTO decía `c8da733e`
como motor de las corridas; eso es incorrecto para las 8 ciegas.

## El runner que corrió — NO recuperable (solo sobrevive su hash)

Los recibos dicen que corrió el runner `0485503dbaf6e14a…` en 7 corridas
y `322803286cb82a8a…` en 1 (Einstein, ANONIMO).

**Esos dos archivos no existen en ningún lado.** Se buscó en:
- Las 9 copias de `correr_estandar.py` del workspace (motor-cameo,
  motor-autorizado, biblioteca, cableado_push, subir-corridas-20261113,
  u6-a5-stage, u6-issue64, cbm-repos, wt-reconexion-calib).
- Los 9 commits de la historia git que tocaron `correr_estandar.py`
  (afa0717→4ac577fa, fb2b023→54c9c6bd, 170d8ae→19b5585c,
  6136224→05a88874, 366c176→3a0d88a9, 78b9a9a→1f44c5bc,
  c9e5436→a8688e56, 4dbf3af/494ecd8→8e53cc16).
- Los run dirs (`motor/runs/ESTANDAR__*`): el runner copia los archivos
  del motor, pero NO se copia a sí mismo; no hay `correr_estandar.py`
  en ningún run dir.

Revertir solo el cambio de etiquetas en la copia actual da `9c74ec84…`,
no `0485503d…`: el runner cambió más que eso. **El runner exacto que
corrió está perdido como archivo; solo sobrevive su hash en los
RECIBO_EJECUCION.json.** No se puede comprobar qué hacía exactamente.
Esto queda documentado aquí para que nadie lo dé por recuperado.

## TEST_CALIBRACION es ANONIMO4 repetido — NO es una 9ª muestra

**Sí, TEST_CALIBRACION es el mismo caso que ANONIMO4 (Che), repetido.**
Verificado por ejecución comparando los dos RESULT y los dos INPUT:

- Mismo caso: los 7 cortes del INPUT son idénticos (solo difiere el
  `case_id`); misma descripción ("Biografía anonimizada #4 (corte en
  Z90). Rebelión política con ruptura violenta"); mismo `random_seed` 0.
- Mismo resultado: H1 `arquetipo_el_gobernante` / H2
  `sustancias_03_severo` en los dos.
- Mismo Monte Carlo: 21 llamadas, 21 convergidas, **13,617
  simulaciones en los dos**.

Es un re-run (probablemente chequeo de regresión tras el cambio de
etiquetas c9e5436 — y confirma que las etiquetas no alteraron el
resultado, porque da exactamente lo mismo). **La muestra son las 8
ciegas, no 9. TEST_CALIBRACION no cuenta como muestra independiente.**

La corrida de verificación de la etiqueta (`RESULT_VERIF_CALIB_LABEL2`,
Che, también 13,617) es OTRO re-run del mismo caso Che, hecho solo
para verificar que la etiqueta nueva imprime bien. Tampoco es una
muestra nueva.
