# Trayectoria descriptiva — gate de reproducción FALLIDO

> **Instrucción posterior PC1/PC2 rotada:** gate real bloqueado por adjuntos y RESULT exactos ausentes. Ver [GATE_TRANSFORMACION_EXTERNA.json](GATE_TRANSFORMACION_EXTERNA.json). El script `proyeccion_tusi_modelo_externo.py` es reconstruido, NO copia verificada del adjunto. No se aplicó esa nueva transformación a los cuatro casos.


> **Actualización:** el diagnóstico inicial se conserva como antecedente. Por la nueva instrucción se ejecutaron los cinco sujetos con la geometría existente, sin exigir 222.5°; ver [geometria_existente_v1/README.md](geometria_existente_v1/README.md).


**No es predicción. No entra al motor, H, ranking ni apuesta. No se compararon los demás sujetos.**

## Resultado

No localicé la transformación exacta `P → eje Tusi × transversal/ondulación` usada por el otro modelo. Las tres imágenes indicadas en la tarea no existen en este entorno (Read: `File not found`), por lo que tampoco pude verificar sus ejes visualmente. Esto es una carencia de insumos del entorno, no un defecto del motor.

Se buscó en la rama y `/workspace`: `Tusi`, `eje_tusi`, `zri`, `helice`, `INSUFFICIENT_CUTS_FOR_HELIX_TEST`, `adaptador de convergencia`, `geometria_multicapa`, además de etiquetas y números de referencia. Las coincidencias de números aislados en resultados ajenos no identifican una proyección. No se afirma haber inspeccionado todos los archivos comprimidos posibles.

Código relacionado localizado, sin modificar:
- `motor/motor/geometria_multicapa/adaptador_convergencia_real_v1.py`: `trayectorias`, `pca3`, `helice_tablero`.
- `motor/motor/geometria_multicapa/v153_convergencia_multinivel_v0_3.py`: `helix_diagnostics`.
- `motor/motor/geometria_multicapa/teseracto_recursivo_geometria_v0_4.py`: proyección PAC y advertencia de cortes insuficientes; no define los ejes de las imágenes.
- `motor/motor/puente_souriau_caldero_polti_v1.py`: anillos y acople Tusi; no es la proyección P pedida.

## Prueba de reproducción, no sustitución del método

Candidata elegida: **la implementación existente** `pca3(P_FULL_244)` y `helix_diagnostics` con eje PCA predeterminado; se llama el código, no se inventa una transformación ni se le cambia el eje hasta conseguir los números. Es la candidata directamente empleada por el adaptador para analizar la hélice de la traza P; no se afirma que sea el plano Tusi original.

Se encontró Mozart completo C1–C10 en el resultado histórico U10. Sus primeros siete vectores P difieren como máximo 0.0001 de la calibración vigente, pero no son idénticos ni se certifica que sean el resultado usado en las imágenes. El extracto P completo se guarda fielmente con SHA de la fuente para poder repetir el diagnóstico sin depender de la ruta histórica.

**Gate declarado:** giro absoluto de Mozart a no más de 2° de 222.5°. Es una condición necesaria, no suficiente para validar la transformación. También habrían debido reproducirse aproximadamente R0/b/ω; no se aprobaría una coincidencia angular aislada.

| Mozart completo | Referencia recibida, no verificada | Candidata existente |
|---|---:|---:|
| Cortes | 10 | 10 |
| Giro absoluto | 222.5° | 94.354572° |
| Giro firmado | no especificado | −94.354572° |
| R0 / b / ω / seno | 0.448 / 0.0759 por año / 8.44° por año / 83% | **NO AJUSTADOS** tras fallar el gate |

El signo puede invertirse por orientación de los ejes PCA, pero el valor absoluto tampoco coincide. Por instrucción de la tarea, la comparación se detiene. **Esto no refuta los números originales, no prueba que la forma no se repita, ni constituye una falla del motor: significa que aún no se puede reproducir ese ejercicio.**

## Casos disponibles, sin comparación

| Caso | Cortes en result vigente | Z90 de control | Giro / forma / R0 / b / R² / ω / seno / cambio / ruptura |
|---|---:|---|---|
| MOZART_ORIGINAL_20260915 | 7 | 1788-05-04 | NO EVALUADO: gate Mozart fallido |
| GALILEO_20260924 | 10 | 1634-03-26 | NO EVALUADO: gate Mozart fallido |
| HAWKING | 6 | 2010-08-01 | NO EVALUADO: gate Mozart fallido |
| CHE | 9 | 1963-11-03 | NO EVALUADO: gate Mozart fallido |
| MLK | 8 | 1964-05-03 | NO EVALUADO: gate Mozart fallido |
| Napoleón de las imágenes | traza exacta no identificada | no verificada para ese ejercicio | NO EVALUADO: gate Mozart fallido |

El result de Mozart de `calibracion_z90/` solo contiene C1–C7: no debe anunciarse como reproducción del giro C1–C10. El de Hawking contiene seis cortes. La existencia de datos sellados de validación no equivale a tener una traza completa pos-Z90 ya calculada por el mismo modelo. No se mezclaron ni rellenaron trazas.

## Artefactos y reproducción

```bash
PYTHONDONTWRITEBYTECODE=1 python3 casos/trayectoria_forma/auditar_reproduccion.py
# Salida esperada: exit 2, FALLO_REPRODUCCION_PROYECCION_ORIGINAL_NO_LOCALIZADA.
```

- `MOZART_P10_EXTRACTO.json`: P_FULL_244 de los diez cortes históricos, fuente y SHA; no crea ni cambia pesos.
- `RESULTADOS.json`: prueba, tolerancia, valores, hashes de módulos y estado de cada caso.
- `MOZART_10_CORTES_DIAGNOSTICO_PCA_NO_TUSI.png` y `MOZART_7_CORTES_CALIBRACION_DIAGNOSTICO_PCA_NO_TUSI.png`: **solo diagnósticos de la candidata que falló**. No son los gráficos Tusi pedidos. Usan índice de corte en el tercer eje, no años inventados. No presentan residuales de una fórmula que no se pudo reproducir.

La regla de selección del tramo exponencial, detección de régimen y ruptura, y ajuste de seno no se ejecutó ni calibró sobre los otros sujetos después de fallar el gate. No se ajustaron parámetros de Mozart a otros casos ni se ensayaron ejes hasta conseguir una semejanza.

## Conclusión

**No determinado si la forma se repite.** Falta identificar la proyección exacta, sus coordenadas P por corte, origen/normalización y eje temporal del ejercicio original. El código geométrico existente no reproduce el giro informado usando la candidata declarada. Se conserva el fallo reproducible en lugar de anunciar una coincidencia inexistente.

Integridad: el script comprobó por SHA antes/después los 133 archivos Python del motor y archivos canónicos encontrados; intactos. No se ejecutó el Engine ni se escribió en `motor/motor/`, en el catálogo o en las hipótesis. Los archivos de `motor/logs/` ya eran ajenos y no se incluyeron.
