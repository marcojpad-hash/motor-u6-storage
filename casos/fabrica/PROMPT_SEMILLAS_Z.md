# Prompt para el LLM que prepara semillas — protocolo biográfico Z90

Autoridad: [motor/PROTOCOLO_BIOGRAFICO_Z90.md](../../motor/PROTOCOLO_BIOGRAFICO_Z90.md). Este prompt corrige la regla antigua que decía que Z no era 90 % de vida.

> **Addendum 2026-11-23 — ruta entry-only obligatoria para casos nuevos.** El formato Python SEMILLAS_Z descrito abajo queda como legado documental; no ejecutar fabrica.py preparar-z. Para casos nuevos, producir JSON con {"cases":[...]} conforme a semillas_entrada/entrada_schema_v1.json y guardarlo localmente en casos/fabrica/semillas_entrada/. Usar preparar_entrada_solo.py, que escribe únicamente entrada.json y entrada.sha256; no crea destinos, desenlaces, resultados ni ejecuta el motor. No incluir H1/H2, hipótesis, ranking, familias, destinos ni desenlaces. Todas las fuentes de casos nuevos deben ser primarias. La gate exige primer corte exactamente en nacimiento, ventanas acumulativas desde nacimiento y último corte exactamente en Z90. El custodio independiente debe entregar el destino sellado por separado; el preparador no ejecuta el motor mientras no exista ese proceso independiente verificable.

## Definición de Z

- **Biografía cerrada (sujeto fallecido):** obtener fecha de nacimiento y muerte. Calcular Z90 como el punto situado al 90 % del intervalo nacimiento→muerte. Establecer `modo_z="historico"`, `z_trabajo=Z90` y `z90_date=Z90`. La fecha de muerte solo sirve para calcular el límite; nunca es evidencia predictiva.
- **Pregunta viva/actual:** establecer `modo_z="vivo"`, `z_trabajo=hoy` y `z90_date=hoy`. No inventar fecha de muerte.
- En ambos modos, ninguna afirmación, fuente, nota o corte puede incorporar información posterior a la fecha de cierre que corresponda.

## Cortes: cantidad variable, ventanas acumulativas

No existe un número fijo de cortes. No fuerces tres, siete, diez ni ningún otro número.

- En biografías cerradas, el primer corte cierra exactamente en la fecha de nacimiento; todas las ventanas cubren acumulativamente desde el nacimiento hasta su fecha de cierre; la última termina exactamente en Z90.
- En preguntas vivas, las ventanas se construyen desde el inicio documentado del periodo de observación hasta hoy.
- Añade un corte cuando exista un cambio de rol, crisis, decisión irreversible o cambio de dirección del vector (signo de velocidad/aceleración de tokens).
- Detén la segmentación cuando el siguiente corte candidato no cambie la trayectoria por debajo del umbral de saturación registrado.
- Cada corte debe declarar su motivo: cambio_de_rol, crisis, decision_irreversible, cambio_de_vector o saturacion.
- No uses desenlace, muerte ni información posterior a Z para elegir cortes. Z100 solo se libera después, por el custodio, para validación retrospectiva.

## Reparto ciego obligatorio

- **Preparador de entrada:** escribe únicamente `semillas_lote_X.py` (lista `SEMILLAS_Z`). No pide, abre, consulta ni escribe destinos. No ejecuta un comando que lea destinos o haga unblinding.
- **Custodio independiente:** crea aparte `destinos_lote_X.py` (lista `DESTINOS`), familias/destino, fuente y `prohibidas_post_Z`; sella los hashes y conserva el archivo fuera del entorno del preparador.
- `preparacion_ciega` debe identificar preparador y custodio distintos, con `vio_destino=false`. No basta con nombres de rol del mismo actor: deben ser ejecutores/conversaciones independientes reales.
- El preparador no ejecuta `fabrica.py correr`: la implementación actual abre desenlaces para evaluar. El unblinding corresponde al custodio después de congelar resultados y recibos.

## Texto para pegar al LLM preparador — formato JSON entry-only

> Prepara solo el input JSON. No consultes ni infieras destinos.
>
> 1. Devuelve un objeto JSON con una propiedad `cases` que contenga una lista de entradas completas. Sigue `semillas_entrada/entrada_schema_v1.json`; no generes módulos Python.
> 2. Usa un sujeto y case_id nuevos. No repitas sujetos ya usados en resultados ni en entradas existentes.
> 3. Congela Z antes de formular H1/H2. No incluyas H1, H2, hipótesis, predicciones, ranking ni desenlace en el JSON.
> 4. En biografía cerrada, calcula Z90 desde nacimiento/muerte; el primer corte debe cerrar exactamente en nacimiento, todas las ventanas comienzan en nacimiento y el último corte cierra exactamente en Z90. No fijes número de cortes.
> 5. Cada afirmación requiere claim_date, source_date y source_url. Para casos nuevos, tipo_fuente debe ser primaria; ambas fechas deben ser anteriores o iguales al cierre del corte.
> 6. Usa únicamente tokens del catálogo vigente de 244 patrones y pesos entre 0.60 y 0.84 en P/A/C.
> 7. Incluye preparacion_ciega con preparador_entrada, custodio_destino y vio_destino=false. Esto registra roles declarados, no demuestra por sí solo independencia real.
> 8. No incluyas destinos, familias, desenlaces, prohibidas_post_Z, resultados ni archivos de custodia.
> 9. No llames modelos ni generes pistas LLM. Si una fuente, fecha, sujeto, token o peso no se puede verificar, excluye el caso.
> 10. Entrega solo el JSON. No ejecutes el script, no corras el motor y no aumentes n.

## Pistas LLM del Caldero (opcional)

Cada sujeto puede incluir `pistas_llm`: lista de `{"token":"...","family":"<familia del catálogo 244>","relevance":0..1}`. Son vecinos propuestos para traza/desempate; no deciden H. Prohibidos nombres/alias del sujeto, años posteriores, futuro y palabras de desenlace. Una familia fuera de catálogo rechaza el lote.

## Ruta de preparación

- El CLI entry-only es: `python3 casos/fabrica/preparar_entrada_solo.py casos/fabrica/semillas_entrada/<lote>.json`.
- Solo acepta JSON dentro de semillas_entrada/. No recibe ruta de destinos ni importa módulos Python.
- La salida es local y está excluida de Git: entradas_solo/<case_id>/entrada.json y entrada.sha256.
- No ejecutar `fabrica.py preparar-z` ni `fabrica.py correr` desde el preparador. La ruta entry-only no constituye una corrida y no prueba la independencia del custodio.

## Estado de implementación al 2026-11-23

`motor/calibracion/gate_z90.py` está en revisión `Z90_BIRTH_DEATH_WINDOWS_V2_20261123`: calcula Z90 desde nacimiento/muerte, exige primer corte exactamente en nacimiento, ventanas acumulativas desde nacimiento, cierres crecientes y último cierre en Z90; en modo histórico también rechaza fuentes secundarias fechadas después del corte. CI de la rama activa pasó 62 pruebas tras estos cambios. La integración en `motor/correr_estandar.py` está en `alterno/cameo-pesos`; PR #8 permanece OPEN/NOT MERGED y no se fusiona sin autorización. La ruta entry-only JSON está implementada y cubierta por pruebas; todavía falta un custodio independiente verificable y entrega de cohorte sellada. F007 no cumple fuentes primarias ni custodia y no debe ejecutarse.

## Campos Z90 obligatorios en cada corte

Para biografías cerradas, entrega `fecha_nacimiento` y `fecha_muerte` exactas. Calcula Z90 como nacimiento + `(días_entre_nacimiento_y_muerte * 9) // 10`; fija `z_trabajo` y `z90_date` exactamente en esa fecha.

En cada objeto de `cuts`, incluye `window_start` igual a la fecha de nacimiento y `date` como fecha de cierre exacta. Todos los cortes son acumulativos desde el nacimiento, sus cierres son estrictamente crecientes y el último cierra exactamente en Z90. No uses fechas parciales en cortes biográficos cerrados.
