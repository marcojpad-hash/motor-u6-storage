# Revisión independiente — Puente de Schrödinger V0_1/V0_2

**Fecha:** 2026-11-11  
**Repositorio:** `marcojpad-hash/motor-u6-storage`  
**Rama revisada:** `alterno/cameo-pesos`  
**Commit revisado:** `6de8b676a7670ad3f5246efa4a979ada3fc2e328`  
**Dictamen:** **NO APROBABLE todavía**. El cableado existe y V0_1 reduce TV en los dos casos reportados, pero la implementación no coincide completamente con la definición de posición del SPEC y tiene fallos de borde/convergencia. V0_2 sí permite mover la media mediante marginales suaves, pero hereda y añade problemas de cálculo y de interpretación de masa.

## Alcance y límites

Revisión estática independiente de SPEC, implementación, sensor y llamada del motor. No se ejecutó el motor ni los tests del repositorio. No se modificaron código, SPEC, Engine, catálogo, candados, ramas ni parámetros. La única escritura de esta revisión es este informe y su entrada de bitácora.

Hashes canónicos **recalculados y coincidentes** en la rama revisada:
- Engine V5: `665c39a2861e58772522e91272563260d980908b1d4ab9f7092d3413d0c36082`.
- Catálogo: `d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1`, 244 patrones.
- Fuente de selección: `motor/ACTIVE_ENGINE_SELECTION.json`.

## 1. ¿La función de costo penaliza la oscilación transversal?

El costo implementado combina distancia transversal `alpha·|υ_i−υ_j|`, distancia Tusi `beta·|τ_i−τ_j|`, diferencia de exceso/activación `gamma·|e_i(t)−e_j(t+1)|` y un coste adicional `delta` cuando el par cambia de signo transversal. Eso penaliza emparejamientos entre familias con polaridad opuesta; no es, por sí mismo, una función objetivo sobre TV de la trayectoria.

La propiedad que el propio SPEC reconoce es correcta: con marginales duras, la esperanza del punto medio de un plan con marginales `μ_t` y `μ_{t+1}` queda fijada por esas marginales. Cambiar el plan cambia el acoplamiento y la dispersión, no la media del punto medio. Por tanto:

- **V0_1 sí puede entregar una trayectoria determinista con menor TV y amplitud** mediante la interpolación de puntos medios y el anclaje de extremos.
- **La reducción de la media/TV no la causa el costo de Schrödinger.** La produce la regla de interpolación; el costo selecciona el acoplamiento y afecta la dispersión.
- La salida no estima una «probabilidad de oscilamiento»: produce una trayectoria regularizada y métricas deterministas. El lenguaje del objetivo debe decir «reducción medida de TV/amplitud» salvo que se modele explícitamente una distribución sobre trayectorias.

Los resultados Mozart/Napoleón de §1 son compatibles con un suavizador local, pero no demuestran que el costo sea el mecanismo que reduce la TV.

Referencias: [SPEC §1–§3](https://github.com/marcojpad-hash/motor-u6-storage/blob/alterno/cameo-pesos/motor/motor/SPEC_SCHRODINGER_V0_1.md#L15), [SPEC §5](https://github.com/marcojpad-hash/motor-u6-storage/blob/alterno/cameo-pesos/motor/motor/SPEC_SCHRODINGER_V0_1.md#L109), [Sinkhorn V0_1](https://github.com/marcojpad-hash/motor-u6-storage/blob/alterno/cameo-pesos/motor/motor/schrodinger_transport_v0_1.py#L175).

## 2. Sinkhorn y delta=0.1

El Sinkhorn balanceado usa escalamiento de filas/columnas y devuelve `convergio` junto con el error marginal. La estructura del algoritmo es coherente con OT entrópico de marginales fijas. La elección de `delta=0.1` está explicada como ajuste numérico para evitar un kernel casi bloqueado y conseguir convergencia en las transiciones reportadas. Eso justifica probarlo como parámetro operativo; **no demuestra que 0.1 sea un valor científico óptimo o universal**. La prueba que falta es sensibilidad de `delta` y de `epsilon` en más casos, con registro por transición.

Hay un fallo de control: `transportar_trayectoria` recibe `info` de Sinkhorn, pero no rechaza ni degrada una transición con `info["convergio"] == False`; al final devuelve `TRANSPORTE_OK` de forma incondicional. El sensor puede entonces marcarse `ACTIVA` y marcar los anillos como consumidos sin que todas las transiciones hayan convergido. V0_2 repite el problema: recibe el diagnóstico del Sinkhorn no balanceado, pero devuelve `TRANSPORTE_OK` sin comprobarlo.

Antes de aprobar: propagar el estado por transición; si cualquier plan requerido no converge, devolver un estado no exitoso o una degradación explícita. `consumido=True` debe depender de convergencia comprobada, no solo de que la función haya retornado.

Referencias: [V0_1 transporte](https://github.com/marcojpad-hash/motor-u6-storage/blob/alterno/cameo-pesos/motor/motor/schrodinger_transport_v0_1.py#L286), [V0_2 transporte](https://github.com/marcojpad-hash/motor-u6-storage/blob/alterno/cameo-pesos/motor/motor/schrodinger_transport_v0_2.py#L211).

## 3. μ_t y μ_t⁻: la medida de déficit sí es necesaria, pero hay un bug

Bajo la definición de posición firmada `Z⁺m⁺ − Z⁻m⁻`, la medida de déficit no es señal añadida arbitrariamente: es la parte negativa necesaria para reconstruir el exceso con signo. El argumento conceptual del §2 es correcto.

La implementación de `mu_t_neg` usa `float(P.get(k) or 0.5)`. En Python, un valor válido `0.0` es falsy y se sustituye por `0.5`. Una familia con `p=0` debería aportar déficit `0.5`, pero el código le asigna déficit cero. `masas()` sí cuenta ese déficit, de modo que `Z⁻` y `μ_t⁻` dejan de representar la misma medida. V0_2 importa esta misma función, así que hereda el defecto.

Corrección requerida: distinguir clave ausente/valor nulo de un cero válido; por ejemplo, usar el valor por defecto solo cuando la clave no exista y tratar `None` explícitamente. Añadir tests con `p=0.0`, `p=0.5`, clave ausente y `None`.

Referencia: [mu_t_neg, línea 72](https://github.com/marcojpad-hash/motor-u6-storage/blob/alterno/cameo-pesos/motor/motor/schrodinger_transport_v0_1.py#L63).

## 4. El punto medio no coincide con el punto medio de la posición cruda

El SPEC define la posición cruda por corte como `pos(t)=Z_t⁺m_t⁺−Z_t⁻m_t⁻` y afirma que el punto medio del puente es `(pos(t)+pos(t+1))/2`. El código primero promedia las masas `Z`, promedia las medias de coordenadas `m` y luego multiplica ambos promedios:

`mid_code = ((Z_t+Z_{t+1})/2) · ((m_t+m_{t+1})/2)`

Eso no equivale en general a:

`mid_raw = (Z_t·m_t + Z_{t+1}·m_{t+1})/2`

La diferencia es `(Z_t−Z_{t+1})(m_{t+1}−m_t)/4`. Solo desaparece si la masa o la media de coordenadas no cambia entre los cortes. El mismo patrón aparece en V0_1 y V0_2: V0_2 obtiene momentos bajo marginales suaves, los promedia y después los multiplica por la masa media de los extremos.

Antes de aprobar, hay que elegir una de dos cosas:
1. Si el puente debe ser el punto medio de la **posición cruda**, ponderar por separado el momento de cada extremo con su `Z_t` y `Z_{t+1}` (en V0_2, usando además las marginales suaves de fila y columna por separado).
2. Si se pretende interpolar por separado composición normalizada y masa total, conservar el producto de promedios, pero redefinirlo explícitamente en el SPEC y retirar la afirmación de que siempre es `(pos(t)+pos(t+1))/2`.

Esta discrepancia puede cambiar los puntos medios y las métricas de reducción; los valores reportados no deben tratarse como definitivos hasta resolverla.

Referencias: [V0_1 mid_pos](https://github.com/marcojpad-hash/motor-u6-storage/blob/alterno/cameo-pesos/motor/motor/schrodinger_transport_v0_1.py#L286), [V0_2 mid_pos](https://github.com/marcojpad-hash/motor-u6-storage/blob/alterno/cameo-pesos/motor/motor/schrodinger_transport_v0_2.py#L211).

## 5. V0_2: formulación, masa y casos vacíos

La actualización de Sinkhorn no balanceado con `q=ρ/(ρ+ε)` es consistente con el objetivo escrito en §9.1; no encontré un error en el exponente de las actualizaciones. La relajación de marginales sí permite que el costo mueva la media, a diferencia de V0_1.

Quedan tres problemas:

- Si uno de los lados tiene masa cero en cualquiera de los dos extremos, el código fija el punto medio de ese lado en `(0,0)`. Si se busca el punto medio de las posiciones de extremo, eso borra por completo el extremo no vacío en vez de representar el caso límite (por ejemplo, la mitad de su contribución). Debe definirse y probarse explícitamente.
- `masa_media` y `kl_media` promedian solo planes no vacíos. Los planes vacíos se excluyen del denominador aunque se les asigna `masa_destruida=1`. Por tanto, el resumen puede subestimar la destrucción cuando hay lados vacíos.
- `M` es masa retenida en planes de medidas laterales normalizadas y se promedia por plan no vacío. No equivale directamente al porcentaje de masa cruda total de `P_FULL_244` destruida, porque los lados +/− se normalizan por separado y tienen masas crudas `Z⁺/Z⁻` distintas. Renombrar el indicador o reportar también la masa cruda ponderada por lado y transición.

El default `rho=0.1` sigue abierto en el propio SPEC; además `rho` (penalización KL de marginales) y `delta` (coste de cruce de polaridad) son parámetros de distinto papel. Que compartan valor numérico requiere sensibilidad y justificación, no solo igualdad por conveniencia.

Referencia: [V0_2 transporte y métricas](https://github.com/marcojpad-hash/motor-u6-storage/blob/alterno/cameo-pesos/motor/motor/schrodinger_transport_v0_2.py#L200).

## 6. memento_inversa P→A→C

La función no invierte ni reconstruye una memoria temporal. Valida el orden, reordena las claves presentes y devuelve las faltantes. Además, el sensor no le pasa los vectores P/A/C, sino conteos de familias no planas del último corte. Es, por ahora, un **ordenador de metadatos de actividad**, no una operación inversa de memento ni una parte del cálculo de trayectoria.

El orden P→A→C puede conservarse como orden de presentación si es la decisión deseada, pero hay que ajustar el nombre y el texto del SPEC/docstring para no atribuirle una recuperación que no hace. El docstring aún dice «decisión de Pecas, abierta a corrección de Mj», mientras §6/§352–368 del SPEC presenta el orden como cerrado: reconciliar esa contradicción.

Referencias: [memento_inversa](https://github.com/marcojpad-hash/motor-u6-storage/blob/alterno/cameo-pesos/motor/motor/schrodinger_transport_v0_1.py#L350), [llamada desde el sensor](https://github.com/marcojpad-hash/motor-u6-storage/blob/alterno/cameo-pesos/motor/motor/laterales_unico_v1.py#L763).

## 7. Cableado real e influencia sobre H

**Cableado en código: verificado.** `laterales_unico_v1.pre_predictor` carga el sensor, ejecuta V0_1 y después intenta V0_2; si V0_2 falta o lanza una excepción, registra el problema y conserva V0_1. El motor llama a `laterales_unico_v1.pre_predictor` antes del predictor.

**Influencia sobre H: no.** El detalle del hub se guarda en `features["laterales_unico_detalle"]`, que está en `BRIDGE_EXCLUDE`; el sensor está dentro del detalle de `sensores_pre`, no dentro del diccionario `votos`. El registro del motor declara `feeds_H=False` y `can_decide_H=False`; la salida del puente declara `Alimenta_H=NO` y `writes_H=False`. Por tanto, está cableado como sensor/diagnóstico, no como voto que cambie H o el ranking. Eso coincide con el límite declarado en el handoff.

La etiqueta `ACTIVA` y `consumido=True` deben depender de la convergencia efectiva; hoy dependen de `estado=TRANSPORTE_OK`, que se devuelve aunque algún Sinkhorn no haya convergido.

Referencias: [sensor en laterales](https://github.com/marcojpad-hash/motor-u6-storage/blob/alterno/cameo-pesos/motor/motor/laterales_unico_v1.py#L717), [llamada pre_predictor](https://github.com/marcojpad-hash/motor-u6-storage/blob/alterno/cameo-pesos/motor/motor/MOTOR_V15_3_UNICO_20260927.py#L2653), [exclusión del puente de nombres](https://github.com/marcojpad-hash/motor-u6-storage/blob/alterno/cameo-pesos/motor/motor/MOTOR_V15_3_UNICO_20260927.py#L821).

## 8. Pruebas y evidencia de las corridas

- Existen `test_schrodinger_v0_1.py` y `test_schrodinger_v0_2.py`; sus datos son sintéticos y pequeños. No cubren `p=0`, lados vacíos, masas crudas variables, no convergencia ni causalidad por prefijos.
- `motor/tests/run_tests_unico.py` no incluye esos tests.
- No hay runs de GitHub Actions en `alterno/cameo-pesos` para esta revisión.
- El commit `6de8b676` y el SPEC reportan resultados Mozart/Napoleón, pero el RESULT/recibo de `NAPOLEON_SCHRODINGER_V01` está en una copia local externa; no está persistido en la rama. El handoff menciona `INCOMPLETE_OUTPUT_DATA`. Por eso los números son **reportados en SPEC/commit, no reproducibles independientemente desde GitHub en esta revisión**.
- La revisión no ejecutó tests ni el motor por el límite de solo lectura/documentación.

## 9. Estado real del SPEC

El handoff que solicita esta revisión dice «6 decisiones abiertas». Ya no coincide con el SPEC actual: §352–368 marca seis decisiones cerradas/implementadas y §370–376 deja dos abiertas (default `rho=0.1` y extremos V0_2). También hay contradicción entre el docstring de `memento_inversa` y el estado del SPEC. El encabezado del SPEC sigue siendo propuesta para aprobación; la frase del comentario V0_2 que atribuye a Mj la decisión «AMBOS» no sustituye una aprobación explícita del documento.

## 10. Cambios mínimos antes de aprobar

1. Corregir el manejo de `p=0.0` en `mu_t_neg`; añadir pruebas para cero, ausente y `None`.
2. Resolver la discrepancia entre producto de promedios y promedio de posiciones crudas; actualizar código y SPEC de forma coherente en ambas versiones.
3. Definir el punto medio cuando un lado está vacío.
4. Propagar `convergio=False` y prohibir `TRANSPORTE_OK/ACTIVA/consumido=True` cuando el plan requerido no converge.
5. Corregir la métrica `M`: incluir planes vacíos o cambiar el nombre/denominador y reportar masa cruda por lado.
6. Aclarar que V0_1 reduce TV por interpolación y que el costo controla acoplamiento/dispersión; no afirmar que estima probabilidad de oscilación.
7. Renombrar o redefinir `memento_inversa`; reconciliar el docstring con el SPEC y probar componentes A/C no planos.
8. Ampliar pruebas: soporte 244, ceros, lados vacíos, masas variables, no convergencia, prefijos causales (PCA sin cortes posteriores al origen de predicción), sensibilidad `delta/epsilon/rho` y controles nulos. Incorporarlas al runner/CI.
9. Guardar en la rama el input congelado, RESULT, recibo completo, hashes, parámetros y entorno de las corridas Mozart/Napoleón; no dejar la evidencia solo en una copia local.
10. Resolver explícitamente `rho` y extremos V0_2, y alinear los comentarios de código, el handoff y el SPEC.

**Veredicto final:** el cableado lateral está presente y el planteamiento V0_1 produce una trayectoria más suave en los dos casos reportados, pero la reducción no es causada por el costo de transporte. V0_2 es la extensión adecuada si se busca que el costo mueva la media, y su actualización de Sinkhorn es coherente con el objetivo, pero no debe aprobarse hasta corregir la ponderación por masa, los ceros, los vacíos y el control de convergencia, además de persistir evidencia reproducible. Mantener ambos como experimentales y sin influencia sobre H mientras tanto.

## Archivos revisados

- `motor/motor/SPEC_SCHRODINGER_V0_1.md` — blob `223e2841ec3142899e050e36f8e692b5d04571e0`.
- `motor/motor/schrodinger_transport_v0_1.py` — blob `7c069fa0b1d499b84116e7e3a95b67592316fce6`.
- `motor/motor/schrodinger_transport_v0_2.py` — blob `22227b3db1164b99cc16b9aca35bf0e9eae60956`.
- `motor/motor/laterales_unico_v1.py` — blob `e156bbe331a3fc7570fd0e79a88cc2dd8fa23ab0`.
- `motor/motor/MOTOR_V15_3_UNICO_20260927.py` — blob `9aed52a83069447163969836f7c61666de1d5173`.
- `motor/tests/test_schrodinger_v0_1.py`, `motor/tests/test_schrodinger_v0_2.py`, `motor/tests/run_tests_unico.py`.

