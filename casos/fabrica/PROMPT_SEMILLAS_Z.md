# Prompt para el LLM que prepara semillas — protocolo biográfico Z90

Autoridad: [motor/PROTOCOLO_BIOGRAFICO_Z90.md](../../motor/PROTOCOLO_BIOGRAFICO_Z90.md). Este prompt corrige la regla antigua que decía que Z no era 90 % de vida.

## Definición de Z

- **Biografía cerrada (sujeto fallecido):** obtener fecha de nacimiento y muerte. Calcular Z90 como el punto situado al 90 % del intervalo nacimiento→muerte. Establecer `modo_z="historico"`, `z_trabajo=Z90` y `z90_date=Z90`. La fecha de muerte solo sirve para calcular el límite; nunca es evidencia predictiva.
- **Pregunta viva/actual:** establecer `modo_z="vivo"`, `z_trabajo=hoy` y `z90_date=hoy`. No inventar fecha de muerte.
- En ambos modos, ninguna afirmación, fuente, nota o corte puede incorporar información posterior a la fecha de cierre que corresponda.

## Cortes: cantidad variable, ventanas acumulativas

No existe un número fijo de cortes. No fuerces tres, siete, diez ni ningún otro número.

- En biografías cerradas, la primera ventana empieza en el nacimiento; cada ventana posterior vuelve a cubrir acumulativamente desde el nacimiento hasta su fecha de cierre; la última termina exactamente en Z90.
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

## Texto para pegar al LLM preparador

> Prepara solo la ENTRADA de cada caso. No consultes ni infieras el desenlace.
>
> 1. Para una biografía cerrada, verifica nacimiento y muerte con fuentes aptas y calcula Z90 = nacimiento + 90 % del intervalo de vida. Para una pregunta viva, Z = fecha de hoy. Escribe `modo_z`, `z_trabajo`, `z90_date`, y, en biografía cerrada, `fecha_nacimiento` y `fecha_muerte`.
> 2. Construye ventanas acumulativas y variables según el protocolo. En biografía cerrada, la primera inicia en nacimiento y la última termina exactamente en Z90. No fijes un número de cortes.
> 3. Justifica cada corte por cambio de rol, crisis, decisión irreversible o cambio de dirección del vector; detente por saturación con umbral registrado. Incluye el motivo de cada corte.
> 4. Solo usa información que ya existía hasta la fecha de cierre de ese corte. Para cada afirmación incluye `afirmacion`, `source_url`, `source_date`, `claim_date`, `tipo_fuente` y `conocido_en_Z: "sí"`. Exige `claim_date <= fecha_del_corte`; para fuente primaria, también `source_date <= fecha_del_corte`.
> 5. En modo vivo, las fuentes secundarias deben ser copias congeladas: `web.archive.org/web/AAAAMMDD…` con snapshot <= Z, o permalink (`oldid=`/revision) con `snapshot_date <= Z`. Nunca Wikipedia en vivo.
> 6. En modo histórico, una fuente secundaria solo puede usarse con preparación ciega real y custodio independiente. Prioriza fuentes primarias contemporáneas.
> 7. No menciones años posteriores al cierre, no uses lenguaje de futuro, no insinúes desenlaces y no añadas pistas post-Z.
> 8. Usa únicamente tokens del vocabulario vigente de 244 patrones y pesos 0,60–0,84. Los pesos son fuerza de codificación, no probabilidad.
> 9. No incluyas familias de desenlace, destino personal, lista negra ni palabras prohibidas; eso pertenece exclusivamente al custodio.
> 10. Si no puedes verificar una fecha, fuente o límite Z, deja el caso fuera del lote; no rellenes huecos por inferencia.

## Pistas LLM del Caldero (opcional)

Cada sujeto puede incluir `pistas_llm`: lista de `{"token":"...","family":"<familia del catálogo 244>","relevance":0..1}`. Son vecinos propuestos para traza/desempate; no deciden H. Prohibidos nombres/alias del sujeto, años posteriores, futuro y palabras de desenlace. Una familia fuera de catálogo rechaza el lote.

## Comando de fábrica

`python3 casos/fabrica/fabrica.py preparar-z semillas_lote_X.py destinos_lote_X.py`

Este comando recibe ambos archivos; por ello solo puede ejecutarse en un entorno controlado que no revele destinos al preparador. No ejecutar `correr` desde el entorno del preparador: el runner actual abre desenlaces y la separación debe conservarse hasta que exista una ruta de ejecución sin unblinding.

**Límite de implementación:** la gate actual valida reglas temporales/evidenciales R1–R7, pero aún no calcula Z90 desde nacimiento/muerte ni comprueba las ventanas acumulativas. El prompt no sustituye esa validación de código. No declarar un lote Z90 válido hasta que la gate y sus pruebas cubran esas reglas.
