# Cuento: hechos frente a dichos y figuras

**Estado: PARCIAL.** Las tres llamadas reales produjeron H; solo V1 terminó con exit 0. V2/V3 terminaron con exit 4 (`INCOMPLETE_OUTPUT_DATA`). No se tocó código del motor.

## Diseño y alcance

- Rama `alterno/cameo-pesos`, código `ae27fe1` (actualizada por fast-forward antes de correr). Corridas del 11-nov-2026, 11:34 CDMX.
- Fuente leída: http://depoliticaehistoria.blogspot.com/2020/04/el-nino-proletario.html . No se incorporó el cuento completo: síntesis analítica no gráfica, sin autor, nombres propios ni calendario en el contenido de las entradas.
- V1: hechos observables. V2: hechos + dichos del narrador atribuidos a él. V3: V2 + figuras y calificativos. Cuatro cortes acumulativos iguales por tramo.
- P=grupo del narrador; A=contraparte que recibe las acciones (no un juicio de antagonismo moral); C=contexto. Los PAC y pesos 0.72 se mantuvieron idénticos para aislar los canales de TEXTO. No prueba el efecto de re-tokenizar los juicios como hechos ni todas las interpretaciones posibles.
- Ficción sin nacimiento/muerte biográficos ni Z: `case_kind=FICTION`, `z_work_kind=FICTION_NO_Z`. Sin fechas inventadas. Semilla 0, MC obligatorio, `FILTRO_017=activo`; memoria persistente separada y vacía al inicio para cada variante.

## H y ejecución

| Variante | H1 | H2 | Exit / recibo | CEB | Caldero |
|---|---|---|---|---|---|
| V1 | guardian_del_umbral | anacyclosis_05_democracia | 0 / COMPLETED | VERIFIED_FLOW_WITH_ANOMALIES | EJECUTADO web (duckduckgo_html, 8 resultados), llm=false |
| V2 | guardian_del_umbral | anacyclosis_05_democracia | 4 / INCOMPLETE_OUTPUT_DATA | INCOMPLETE | INTENTADO_FALLIDO; 0 resultados; PRE-H API_PENDING |
| V3 | guardian_del_umbral | anacyclosis_05_democracia | 4 / INCOMPLETE_OUTPUT_DATA | VERIFIED_FLOW_WITH_ANOMALIES | EJECUTADO web (duckduckgo_lite, 8 resultados), llm=false |

## Top 5

`índice` es el campo existente `indice_fusion_relativo_0_1`, soporte relativo NO probabilístico. Se conserva además `rank_fusion` crudo: incumple el rango de la rama (`FALLO_ESCALA`), no fue reparado ni normalizado por este ensayo. Los techos de fusión difieren entre corridas; no tratar los índices como probabilidades o comparación calibrada.

| Variante | Posición | Familia | Índice | rank_fusion crudo |
|---|---:|---|---:|---:|
| V1 | 1 | guardian_del_umbral | 0.568284 | 23.299651 |
| V1 | 2 | anacyclosis_05_democracia | 0.540958 | 22.179292 |
| V1 | 3 | sombra | 0.533820 | 21.886614 |
| V1 | 4 | 1_suplica | 0.504467 | 20.683135 |
| V1 | 5 | arquetipo_el_gobernante | 0.470930 | 19.308135 |
| V2 | 1 | guardian_del_umbral | 0.583543 | 22.174651 |
| V2 | 2 | anacyclosis_05_democracia | 0.554060 | 21.054292 |
| V2 | 3 | sombra | 0.546358 | 20.761614 |
| V2 | 4 | 1_suplica | 0.470828 | 17.891469 |
| V2 | 5 | picar_trickster | 0.465419 | 17.685913 |
| V3 | 1 | guardian_del_umbral | 0.571333 | 23.424651 |
| V3 | 2 | anacyclosis_05_democracia | 0.544007 | 22.304292 |
| V3 | 3 | sombra | 0.536869 | 22.011614 |
| V3 | 4 | 1_suplica | 0.504467 | 20.683135 |
| V3 | 5 | picar_trickster | 0.461852 | 18.935913 |

## Diferencias observadas y límites

- H1/H2 no cambian en estas salidas. Las 13 candidatas son el mismo conjunto: ninguna aparece ni desaparece. En top 5, `arquetipo_el_gobernante` (V1) sale y `picar_trickster` entra (V2/V3); ambas siguen presentes fuera/dentro del top según la variante.
- Los pesos relativos H1/H2 son V1 0.100141/0.095326; V2 0.104024/0.098769; V3 0.100679/0.095863. No son probabilidades. No validar automáticamente el significado de las etiquetas del catálogo a partir de esta prueba.
- `motor.annex.traza_P.crudo_P` es exactamente idéntico (244 familias × 4 cortes). Sus coordenadas y, por tanto, su forma no cambian; es coherente con PAC congelados. También coinciden `X_shape`, `dX_norm`, `persist_cos` y `kappa_dir` de R732. No se reactivó ni ajustó la capa de trayectoria aparcada.
- No toda la geometría auxiliar es idéntica: las funciones Souriau del marcador final pasan de `[luna]` en V1 a `[leon,luna,marte,tierra]` en V2/V3. Es una anotación funcional derivada del texto, no cambio en los vectores numéricos anteriores.
- **Confusor real:** Caldero ejecutó búsquedas vivas distintas en V1/V3 (165/182 tokens análogos) y falló en V2. La consulta ciega de V1/V3 tiene la misma huella, pero proveedor/resultados no son iguales. No se puede atribuir causalmente la variación de scores solo al juicio o al tono ni afirmar agnosticismo general. No se sustituyó el fallo por fixture.

## Sombrero blanco: lo que realmente filtró

- En las tres variantes: entrada/salida `ACTIVA_MUDA`, salida limpia, 4 textos admitidos, **0 textos excluidos, 0 ruido de protocolo, 0 tokens fuera del catálogo y 0 campos probabilísticos prohibidos**.
- Los dichos y figuras de V2/V3 permanecieron enteros entre los textos admitidos. El guardián implementado no separó semánticamente hechos, juicios y metáforas en este ensayo. «Salida limpia» aquí verifica vocabulario/familias/protocolo; NO certifica la regla literaria de «solo filmable».
- Filtro 017 activo: 0 modificaciones en las tres entradas; V1 sin banderas y V2/V3 con una advertencia `FUTURO_MUERTE_NO_FINAL` en C3 por la palabra «muerte» en un dicho. Se admitió el texto.
- Preflight inicial detectó falsos nombres (`Ahora`, `Con`, `Me`, `La`, `Era`, inicios de cita). Se normalizó la inicial de las citas a minúscula, sin cambiar contenido ni desactivar filtros. La auditoría inicial queda en `FILTRO_FALSOS_POSITIVOS_INICIALES.json`.

## Fallos exactos; no están resueltos

1. V2/V3: faltan `$.matriz_mortalidad_z90.classified_mortality_events[0].date` y `[1].date`. La matriz crea dos eventos en C3/C4 desde el dicho sobre la muerte (repetido por cortes acumulativos), con `date=None`, y el serializador los marca `DATO_AUSENTE_REQUIERE_CLASIFICACION`. De ahí exit 4. Código inspeccionado: `matriz_mortalidad_z90_v0_2.py:29-38,197-208` no omite ficción ni distingue esos dichos; el runner la llama en `correr_estandar.py:693-696`. No inventar fechas ni eliminar el dicho para forzar OK.
2. V2: `RuntimeError:Ningún buscador respondió`. ddgs: `No module named duckduckgo_search`; DDG HTML/Bing/Google sin URLs verificables; DDG lite: `SSL: UNEXPECTED_EOF_WHILE_READING`; SearXNG sin respuesta; Wikipedia: `HTTP Error 429: Too Many Requests`; proveedores con clave saltados sin clave. Recibo completo en `NUMEROS.json` y salida cruda local. Caldero CEB `FAILED`, orientación PRE-H `API_PENDING`. No se reintentó ni se usó una vía sustitutiva.
3. Las tres: CEB `REPORTED_EXECUTED_NOT_OBSERVED` para `geometria_multicapa_integrada_working_v1`. V1/V3 quedan `VERIFIED_FLOW_WITH_ANOMALIES`, no «todo OK».
4. V1/V3 declaran búsqueda web con `llm=false`; V2 falla sin llamada verificada. No hay evidencia de que Caldero haya invocado al LLM exigido por Mj. Tener resultados web no cumple esa exigencia.
5. `rank_fusion` sigue fuera de 0.01–0.999: `FALLO_ESCALA` vigente.

## Evidencia y persistencia

- Entradas: `V1_INPUT.json`, `V2_INPUT.json`, `V3_INPUT.json`. Auditoría: `FILTRO_PREFLIGHT.json`, `NUMEROS.json` (todas las 13 candidatas), `METODO.json`, `VALIDACION.json`, `MANIFIESTO.json`.
- 30 checks de correspondencia de inputs/outputs, hashes canónicos, PAC, trazas y conjuntos: 30 pasan; no son pruebas de completitud del runner ni borran los fallos anteriores. MC: cada variante 12 llamadas, 4800 simulaciones, 12 convergidas.
- Engine V5 y catálogo 244 conservan `665c39a2…` / `d827dcc3…`.
- Los crudos `V*_RESULT.json`, recibos `V*_RESULT_RECIBO_EJECUCION.json`, ledgers CEB y logs existen localmente en este mismo directorio y sus hashes están en el manifiesto. No se versionan los ~62 MB de corrida: `casos/REGLAS.md` y `CONTRATO_CARPETAS.md` lo prohíben; solo entradas, resúmenes y huellas.
- Publicación externa no realizada por este executor: la petición del propietario pide revisar la variable, no autoriza de forma explícita esta publicación concreta. Commit local preparado para que el coordinador gestione la autorización. No se creó issue, PR ni se hizo merge.

**Conclusión acotada:** las dos H se mantienen, pero cambian puntajes y el quinto lugar; el sombrero implementado dejó pasar dichos y figuras. Dos corridas quedan incompletas, Caldero varió/falló y no llamó a LLM. La prueba no demuestra que el sistema sea agnóstico al juicio.
