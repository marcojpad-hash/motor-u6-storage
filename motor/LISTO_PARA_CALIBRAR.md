# Listo para calibrar — copia U6_CONT_AGNOSTICO_20261024 (24-oct-2026)

Esta carpeta es una **copia de trabajo**. El original `IN_t860b/U6_UNIFICADO_20261020` no se tocó.
Tampoco se tocaron los dos candados, verificados antes y después:
- `motor/Engine_V5_CANONICO_SOLO.py` = `665c39a2861e…`
- `motor/patterns_final_v14.json` (244 patrones) = `d827dcc38826…`

## Qué quedó arreglado

1. **La pausa ya no muestra una apuesta autorizada.** Si TORTUGAS falla y la corrida se pausa (exit 6), el runner reescribe estos campos a `PAUSADA_REANUDABLE`:
   - `resolucion_operativa_final`;
   - `resolucion_operativa_terminal_017` y su `decision`;
   - `cierre_final`, `estado_final` y `predictor.terminal_resolution`.
   
   Además:
   - Las apuestas (`salida_interpretable.apuesta_multiescenario`, `apuesta`, `apuesta_trayectoria`, `hipotesis_trayectoria_abierta.apuesta`) pasan a `APUESTA_NO_AUTORIZADA_PAUSA_REANUDABLE`, con `apuesta_autorizada=false`.
   - El valor anterior se guarda en `*_previo_a_pausa`.
   - H1 y H2 se conservan, pero quedan marcadas `PROVISIONAL_NO_AUTORIZADA_POR_PAUSA`.
   - La lista de campos reescritos va en `continuidad_corrida.campos_reescritos_por_pausa`.
2. **La compuerta de continuidad lee bien a TORTUGAS.**
   - Busca el estado en `resolucion_operativa_terminal_017.tortugas`, `cierre_guardianes.tortugas` y `predictor/prediccion.terminal_resolution`.
   - Ahora el estado se informa como `ERROR` y ya no como `NO_REGISTRADO`.
   - `last_valid_cut` queda indexado; por ejemplo `{index: 2, id: "C3_480BC", n_cortes: 3}`.
3. **Huella de mortalidad.** En `matriz_mortalidad_z90.data_table_sha256` hay tres casos:
   - si hay tabla real, va su sha256;
   - si las filas vienen en el input, va el sha256 de esas filas;
   - si no hay tabla, va `NO_APLICA_SIN_TABLA`, con `data_table_sha256_motivo` y `data_table_estado`.
   
   No se inventa ningún hash. La ausencia sigue visible en el recibo, en `huellas_declaradas_ausentes`. Por eso la corrida termina `COMPLETED` con exit 0, sin esconder el hueco.
4. **Manifiesto regenerado.**
   - Incluye los archivos nuevos y cambiados, y también `motor/_vendor_buscador/` completo.
   - Las carpetas de salida (`tests_integracion/_out/`, `evidencia_agnostico/`, `SALIDAS/`, `salida_cal_*`) se declaran estado mutable.
   - El preflight da `MATCH`, con 0 archivos con deriva, 0 ausentes y 0 fuera del manifiesto.
5. **Pruebas offline del buscador.**
   - `tests/test_caldero_buscadores_offline.py`: la cadena de buscadores salta al siguiente proveedor cuando uno falla, no inventa resultados si fallan todos, salta los proveedores con clave cuando no hay clave y valida el selector. La red queda bloqueada.
   - `tests_integracion/test_interruptor_busqueda_viva_offline.py`: con `CALDERO_BUSQUEDA_VIVA=1` se ignora el puente grabado y se usa la cadena, simulada y sin red. La query ciega no cambia: tiene el mismo sha que el puente. Sin el interruptor se usa el puente grabado.
6. **Arnés de calibración portado** desde TIRADA a `calibracion/`. Incluye `arnes_calibracion.py`, las plantillas, la guía y `tests/test_arnes_calibracion.py`. Quedó adaptado a la salida de esta copia:
   - lee la apuesta desde `salida_interpretable.apuesta_multiescenario`;
   - calcula `huella_salida_sha256`, porque aquí no existe `nucleo_estable`;
   - acepta exit 0 y 5 y no sella corridas pausadas (exit 6);
   - tiene un modo seco, `validar`.
   
   Además se agregó `correr_caso_nuevo.sh`.

## Cómo correr un caso nuevo
```
cp calibracion/PLANTILLA_CASO_NUEVO.json casos_cal/MI_CASO.json   # llenar cortes con datos anteriores al freeze
./correr_caso_nuevo.sh casos_cal/MI_CASO.json MI_CASO              # -> SALIDAS/RESULT_MI_CASO.json + recibo
```
Códigos de salida:
- 0 = COMPLETED;
- 5 = completado con hueco de metadato;
- 6 = pausada. Para reanudar: `python3 scripts/reanudar_desde_checkpoint.py SALIDAS/RESULT_MI_CASO_CHECKPOINT_REANUDABLE.json SALIDAS/RESULT_MI_CASO_R.json`;
- 3 o 4 = error.

La búsqueda en vivo viene encendida por defecto. Se apaga con `CALDERO_BUSQUEDA_VIVA=0` y el buscador se elige con `CALDERO_BUSCADOR=auto|ddgs|bing|…`.

## Cómo calibrar
1. Revisar los casos sin correr nada: `python3 calibracion/arnes_calibracion.py validar casos_cal/`
2. Sellar, **antes** de conocer el desenlace: `python3 calibracion/arnes_calibracion.py correr casos_cal/ salida_cal_AAAAMMDD/ --pesos 0`
3. Evaluar, cuando el desenlace real ya se conoce. Primero se llena `desenlaces.json` a partir de `calibracion/PLANTILLA_DESENLACES.json`; luego:
   `python3 calibracion/arnes_calibracion.py evaluar salida_cal_AAAAMMDD/REGISTRO_CALIBRACION.json desenlaces.json`
   - El resultado trae la tasa de acierto (H1, set abierto y escenario principal), Laplace (k+1)/(n+2) y Brier LOO recortado a 5–95 %.
   - El registro sellado no se reescribe y cualquier cambio posterior se detecta.
4. Tras cambiar cualquier archivo de `motor/`: `python3 -B scripts/regenerar_manifestos_trabajo.py`

## Límites honestos
- **No hay peso geométrico que barrer.** El motor de esta copia mete la geometría como dimensiones normales del rank_fusion y no expone `GEOMETRIA_PESO`. Por eso el arnés usa un solo peso nominal (0) y rechaza un barrido con `MOTOR_SIN_GEOMETRIA_PESO`, en lugar de producir corridas idénticas disfrazadas. Lo que se calibra es el acierto y el Brier del motor tal como está. Portar el peso de TIRADA sumaría la geometría dos veces y no se hizo; es una decisión pendiente.
- **No se corrieron los 15 casos sellados** y el arnés no los usa. Con menos de 10 desenlaces, la evaluación avisa `MUESTRA_INSUFICIENTE`.
- **La mortalidad no tiene datos reales.** La matriz queda `WIRED_WAITING_VERIFIED_MORTALITY_DATA` y no alimenta H.
- **La búsqueda en vivo depende de la red y del buscador.** El orden y el contenido de los resultados pueden variar entre corridas. En la prueba de humo, H1 y H2 coincidieron con la corrida anterior y los puntajes difirieron en menos de 0,5.
- **Dos pruebas siguen saltadas**, porque faltan el código 0.5.0 original y el fixture Bezos; no se inventaron.
- **Un checkpoint queda atado a la versión exacta del runner.** Los checkpoints viejos, anteriores a este cambio de `correr_estandar.py`, ya no reanudan y devuelven exit 7, a propósito.

## Storage común (motor-u6-storage)
Antes de cada corrida: `python3 scripts/sincronizar_storage.py antes` desde la raíz del repo (trae la versión nueva, reporta cambios en `motor/` y `stinkbox/`, verifica hashes canónicos). Después: `python3 scripts/sincronizar_storage.py despues --corrida <DIR> --modelo "<modelo>"` (sube solo el resumen y los tokens StinkBox nuevos; nunca la corrida completa ni cambios al motor canónico o al catálogo).
