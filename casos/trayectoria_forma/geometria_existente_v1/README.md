# Trayectorias con la geometría existente del motor

**EJECUTADO:** Mozart histórico de diez cortes, Galileo, Hawking, Che y MLK. Ejercicio retrospectivo, descriptivo, sin decidir H, ranking ni apuesta. No se exige reproducir los 222.5° del otro modelo.

Se llama exactamente la geometría existente del adaptador: `pca3(P_FULL_244)` + `helix_diagnostics` con eje PCA por defecto. Cada caso tiene parámetros propios. No se reutilizan los de Mozart ni se invierte ningún eje para conseguir semejanzas.

Método fijado antes de los ajustes: [METODO_PREDECLARADO.md](METODO_PREDECLARADO.md). Radio: primer máximo global hasta primer mínimo posterior, mínimo tres puntos; fase OLS, seno en cuadrícula fija y detección por umbrales de residuales idénticos para todos. Las banderas son descriptivas, no pruebas estadísticas.

## Tabla ejecutada

Giro es **valor absoluto del cambio neto de fase**, no suma de todos los giros ni número de ciclos físicos. b está en 1/año y ω en grados/año, con las fechas de control disponibles. R0 se refiere al inicio del tramo ajustado.

| Caso | N | Giro neto abs. ° | Forma completa | R0 | b/año | R² radio | ω °/año | Seno explicado % | Régimen | Ruptura fase |
|---|---:|---:|---|---:|---:|---:|---:|---:|---|---|
| MOZART_10 | 10 | 94.35 | NO | 0.1266 | 0.06685 | 0.172 | -5.79 | 60.3 | C5 antes | C2 antes |
| GALILEO | 10 | 380.96 | NO | 0.1852 | 0.00388 | -0.009 | -5.28 | 79.3 | G_C10_Z90 antes | G_C8 antes |
| HAWKING | 6 | 27.44 | NO | N/D | N/D | N/D | 2.59 | 75.9 | N/D: tramo 2 puntos | C3 antes |
| CHE | 9 | 401.44 | SÍ | N/D | N/D | N/D | -32.25 | 75.8 | N/D: tramo 2 puntos | — |
| MLK | 8 | 37.96 | NO | N/D | N/D | N/D | 3.21 | 65.8 | N/D: tramo 2 puntos | — |

— significa sin bandera bajo el umbral, NO ausencia demostrada de ruptura. En los tres casos con tramo de dos puntos no se fuerza una exponencial de dos parámetros ni se anuncia R²=1: no hay ajuste válido bajo la regla fijada. No se cambia la regla después de ver los resultados.

## Forma y tramos

Cresta/valle se refieren al orden operacional definido, salto al segmento más largo que cruza el eje y supera 1.5×mediana; subida exige datos posteriores. NO es una clasificación invariante a rotaciones o reflejos.

| Caso | Tramo radio | Cresta | Valle previo al salto | Salto largo / cruza eje | Subida posterior |
|---|---|---|---|---|---|
| MOZART_10 | C1→C4 (4 puntos) | C2 | — | no / sí | no |
| GALILEO | G_C1→G_C8 (8 puntos) | G_C1 | — | sí / no | no |
| HAWKING | C4→C5 (2 puntos) | C1 | C2 | no / no | sí |
| CHE | C7→C8 (2 puntos) | C1 | C4 | sí / sí | sí |
| MLK | C4→C5 (2 puntos) | C3 | — | sí / sí | sí |

## Conclusión honesta

**No se repite la forma completa en este conjunto bajo esta definición: cumple 1/5, Che.** Eso no demuestra que exista una forma universal en Che ni refuta lo observado con la proyección externa. Las PCA de cada caso tienen cargas distintas y sus orientaciones no son una jurisdicción geométrica compartida entre sujetos; son el mismo procedimiento, no los mismos ejes físicos.

No aparece una contracción exponencial fuerte y común: Mozart tiene R²≈0.17; Galileo, R²<0 en escala de radio (peor que una constante en esa escala, aunque se haya ajustado log-radio). Hawking/Che/MLK tienen tramos insuficientes bajo la regla declarada. Los senos explican 60–79% EN MUESTRA, con frecuencia ajustada y solo 6–10 puntos: no es validación ni evidencia de periodicidad generalizable.

## Límites de los datos y Z90

- Galileo, Hawking, Che y MLK usan todos los cortes ya presentes en sus RESULT de calibración; **no se inventan trazas pos-Z90**.
- Hawking termina en 2000, antes de Z90 2010. No se concluye nada sobre el tramo ausente.
- MLK tiene C7 y C8 con el mismo cierre de control: no se asigna velocidad al salto ni se lo llama ruptura física. Sus cierres fueron reconstruidos.
- Che conserva el orden del RESULT (C1,C3,C2,...); no se reordena por número de corte.
- Galileo cierra un día antes de su Z90 calculada. La bandera final figura **antes**, no después.
- Mozart es una traza histórica completa, NO acreditada como la de las coordenadas externas. Sus años son cierres reconstruidos del sobre vigente. El cierre convencional C10=1791-12-31 queda después de la muerte; los parámetros por año de este ejercicio son aproximados y no una cronología biográfica precisa. No se sustituyen por años de un CSV que no está disponible.
- Con tan pocos puntos, desenrollar fase admite ambigüedad. Los giros de >360° no prueban una vuelta física completa.

## Coordenadas externas: insumo no disponible

Read devolvió `File not found` para AMBOS CSV recibidos en la delegación:
- `.../attachments/1ccd6adb25bc88f74627e1f5749cf15ba27ec28134897193c11f7d122431e050.csv`
- `.../attachments/75cbc2c846e73e7b5b778942c4f14fd21ffadf40186d61a953f4ab9e35df3a7b.csv`

Las rutas completas constan en MANIFIESTO.json y en `../coordenadas_modelo_externo/ESTADO.json`. No pude copiarlos, ajustarlos, graficarlos ni contrastarlos con los vectores P. **No se infiere ni se aplica una transformación externa sin reproducir ambos casos.** No se afirma que no exista la transformación: estos insumos no están presentes en este entorno.

## Reutilización

```bash
PYTHONDONTWRITEBYTECODE=1 python3 casos/trayectoria_forma/medir_trayectorias.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s casos/trayectoria_forma -p test_medir_trayectorias.py -v
```

`MANIFIESTO.json` referencia fixtures JSON fieles de los cinco casos; contienen P_FULL_244, cierre por corte, Z90, fuente y hashes. Para nuevos casos, agregar una entrada `{"file":"entradas/CASO.json"}` sin cambiar el método.

El lector admite también CSV externos con columnas explícitas `corte,año,x_tusi,y_transversal,radio,fase_grados` y entrada de manifiesto `{"file":"ruta.csv","case_id":"NOMBRE","z90":1788.34}`. Preserva las coordenadas/tiempos externos y los rotula **coordenadas externas (transformación no disponible)**; no aplica PCA otra vez ni inventa su transformación. Ese camino solo fue probado con fixture SINTÉTICO, no con los CSV reales ausentes. Puede usarse `--manifest RUTA --outdir CARPETA`; el método debe acompañar el manifiesto.

## Pruebas y evidencia

- Diez pruebas unitarias: OK; `TESTS.log`.
- Ejecución de los cinco casos: exit 0; `EJECUCION.log`, `RESULTADOS.json` y cinco PNG.
- SHA antes/después: 133 archivos protegidos intactos. Ninguna modificación a Engine, 244 ni `motor/motor/*.py`.
- No se ejecutó el Engine ni se reescribieron resultados o apuestas.

## Instrucción posterior: proyección exacta PC1/PC2 rotada

La descripción posterior recibida usa `motor.annex.traza_P.crudo_P`, centrado, PC1/PC2 y rotación del segmento C1→Cn a horizontal. **No es** el plano radial de hélice PC2/PC3 usado arriba. Por eso las dos tablas no se pueden mezclar ni llamar equivalentes.

El adjunto `.py` tampoco existe en la ruta indicada, y en esta rama ni en `/workspace` se localizaron `RESULT_MOZART_Z90_PRECEDENTE.json`, `RESULT_NAPOLEON_Z90_10CORTES.json` ni el input de Napoleón solicitado. El input de Mozart precedente sí está presente; no basta sin su RESULT y los CSV de referencia.

Dejé `../proyeccion_tusi_modelo_externo.py` **reconstruido de la descripción, no copiado del original**, con lectura de crudo_P, n variable y gate por coordenadas CSV (tolerancia 0.001 por componente, simultáneamente ambos casos requerida antes de aplicar). Sus pruebas sintéticas pasan, pero **el gate real sigue bloqueado**, no fallido por discrepancia numérica. `../GATE_TRANSFORMACION_EXTERNA.json` registra todos los faltantes.

Los cuatro RESULT de calibración sí contienen crudo_P (244 familias). No se les aplicó esta segunda transformación porque la última instrucción la condiciona a reproducir ambos casos externos. Los PNG y la tabla de este subdirectorio siguen siendo exclusivamente el ejercicio anterior con geometría radial existente.
