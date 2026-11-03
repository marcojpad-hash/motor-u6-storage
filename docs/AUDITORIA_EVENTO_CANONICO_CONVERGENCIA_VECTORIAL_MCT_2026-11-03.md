# Auditoría de equivalencia: evento canónico y convergencia vectorial MCT

**Fecha:** 2026-11-03  
**Repositorio:** `marcojpad-hash/motor-u6-storage`  
**Rama inspeccionada:** `main`  
**Alcance:** lectura de arquitectura y código existente. No se modificó código del motor ni el catálogo canónico.

## Dictamen

**U6 ya contiene piezas reales de vectorización, comparación de trayectorias, convergencia geométrica y reconvergencia temporal. No contiene todavía el equivalente completo del evento canónico definido para MCT.**

El equivalente más cercano está repartido entre:

1. `geometria_multicapa/adaptador_convergencia_real_v1.py`: compara los tres tableros P/A/C como trayectorias paralelas dentro de una misma corrida.
2. `geometria_multicapa/v153_convergencia_multinivel_v0_3.py`: compara distancias entre trayectorias y puede medir contracción, intersección observada y consistencia entre niveles si estos se suministran.
3. `geometria_multicapa/teseracto_recursivo_geometria_v0_4.py`: sigue trayectorias de patrones en coordenadas abstractas P/A/C, cuenta contracciones de distancia y deriva agrupaciones jerárquicas exploratorias.
4. `geometria_multicapa/sidecar_latentes_v1.py`: registra precedencia, coocurrencia, cambios simultáneos, desaparición y reaparición de relaciones token-token.
5. `hipotesis_trayectoria_abierta_v1.py`: agrupa hipótesis por régimen de trayectoria (ascendente, descendente, meseta, giro/divergencia), no por identidad de un vector final común.

**Diferencia decisiva:** esas piezas observan convergencia entre tableros, familias, patrones o relaciones de una misma ejecución. El evento canónico MCT requiere detectar que trayectorias de realidades independientes, con condiciones y desarrollos distintos, llegan a un mismo acontecimiento/vector esencial. Esa comparación transversal entre mundos no está implementada en lo inspeccionado.

## Evidencia por módulo

### 1. Adaptador de convergencia real

Archivo: `motor/motor/geometria_multicapa/adaptador_convergencia_real_v1.py`

- El encabezado declara expresamente que P/A/C son tres trayectorias paralelas, no niveles jerárquicos; R732 concatena P|A|C.
- `pares_tableros()` compara P~A, P~C y A~C por corte en el espacio completo de 244 dimensiones, calcula distancia, contracción, coincidencias proyectadas y falsos positivos de proyección.
- La convergencia exacta se marca con una tolerancia sobre la distancia de extremo; la contracción temporal se informa aparte.
- El adaptador declara `can_decide_H=False`, `Alimenta_H=NO`, `reordena=False`.
- La salida incluye una limitación explícita: no hay jerarquía sincronizada guardada; P/A/C son tableros paralelos, no niveles; no hay subcortes y el ajuste afín holdout no es identificable con 8 cortes en 244 dimensiones.

Lectura: sí existe comparación vectorial entre trayectorias, pero no es todavía comparación de realidades autónomas ni detección de un evento común semánticamente equivalente.

### 2. Comparador geométrico multinivel

Archivo: `motor/motor/geometria_multicapa/v153_convergencia_multinivel_v0_3.py`

- `compare_trajectories()` calcula distancia completa por corte, distancia mínima, contracción monotónica, convergencia de extremo y posibles falsos positivos al proyectar dimensiones.
- `fit_affine_map_holdout()` permite mapear un nivel hijo al espacio de un padre y medir residuo en cortes retenidos.
- `recursive_hierarchy()` compara niveles sincronizados, con mapas explícitos opcionales, y calcula residuos entre niveles.

Lectura: el instrumental matemático genérico para comparar trayectorias y niveles existe. Sin embargo, el código no genera por sí mismo realidades independientes, no define un vector-evento común ni determina equivalencia semántica entre resultados.

### 3. Teseracto recursivo

Archivo: `motor/motor/geometria_multicapa/teseracto_recursivo_geometria_v0_4.py`

- Construye trayectorias de patrones en coordenadas abstractas [P_i,A_i,C_i].
- Calcula contracción de distancia entre pares de patrones y sensibilidad a umbrales.
- Deriva una jerarquía Ward sobre puntos PAC medios.
- El propio módulo etiqueta esa jerarquía como inferida/exploratoria, no como niveles ontológicos nativos, y advierte que no demuestra una recursión ontológica.

Lectura: aporta estructura geométrica y agrupamiento; no identifica acontecimientos canónicos entre mundos.

### 4. Sidecar de latentes y reconvergencia

Archivo: `motor/motor/geometria_multicapa/sidecar_latentes_v1.py`

- `convergencia()` registra precedencia temporal, coocurrencia de tokens y cambios simultáneos de familias/tokens.
- `trayectorias()` detecta cuando una relación token-token reaparece después de un hueco y la compara con su primer contexto.
- Clasifica la reaparición como `MISMA` o `NUEVA_POSIBLE_GIRO` según forma y Jaccard de contexto.

Lectura: aquí existe una noción de reconvergencia temporal de relaciones previamente observadas. No equivale a que varias realidades distintas converjan en el mismo acontecimiento vectorial. La palabra reconvergencia se usa en un sentido local de reaparición de una relación.

### 5. Hipótesis abiertas y apuesta

Archivo: `motor/motor/hipotesis_trayectoria_abierta_v1.py`

- La cardinalidad de hipótesis es variable.
- Las hipótesis se agrupan por régimen: continuidad ascendente, continuidad descendente, meseta/estabilización o giro/divergencia.
- `hipotesis_que_convergen` identifica hipótesis que comparten ese régimen.
- El soporte agregado es estructural, no probabilidad calibrada.
- La geometría se conserva como contexto descriptivo; no se convierte en probabilidad ni prueba física.

Lectura: el motor ya agrupa trayectorias por comportamiento común. Pero compartir un régimen no significa alcanzar el mismo vector-evento. Dos hipótesis pueden ser ambas ascendentes y terminar en acontecimientos incompatibles.

## Estado de equivalencia

| Requisito del evento canónico MCT | Estado en U6 inspeccionado |
|---|---|
| Vectorización por corte | EXISTE (P/A/C y R732) |
| Comparación de trayectorias | EXISTE |
| Medición de contracción y distancia | EXISTE |
| Detección de intersección/convergencia geométrica | EXISTE, acotada al espacio y tolerancias de cada módulo |
| Reconvergencia de relaciones tras desaparición | EXISTE en sidecar token-token |
| Agrupación de hipótesis por régimen común | EXISTE |
| Realidades autónomas con motores/condiciones independientes | NO IDENTIFICADO en estos módulos |
| Vector-evento canónico común entre realidades | NO IDENTIFICADO |
| Equivalencia esencial del acontecimiento separada de detalles variables | NO IDENTIFICADA |
| Detección de convergencia independiente sin transferencia de conclusiones entre mundos | NO IDENTIFICADA |
| Registro de no-convergencia y ramas que no alcanzan el evento | Parcial en diagnósticos de distancia; no como resultado del multiverso |

## Diferencia conceptual que no debe perderse

El evento canónico MCT no es:

- un evento de auditoría o log;
- una hipótesis que recibe muchos votos;
- una coincidencia de tokens;
- un régimen compartido como continuidad ascendente;
- una intersección causada por una proyección que descarta dimensiones;
- una agrupación Ward de puntos PAC;
- una conclusión impuesta al conjunto de mundos.

Es un **vector/estado-evento invariante que emerge como resultado común de trayectorias independientes**. Los detalles periféricos pueden variar; las propiedades esenciales del acontecimiento deben coincidir dentro de una métrica y tolerancia explícitas.

## Qué falta para cerrar el equivalente

No hace falta reemplazar la geometría existente. Hace falta una capa nueva por encima de ella:

1. **World/Reality ID:** cada trayectoria debe pertenecer a una realidad con estado, supuestos y evolución propios.
2. **Aislamiento:** los mundos no comparten hipótesis ni resultados durante la fase de exploración independiente. Pueden compartir el conjunto de observaciones iniciales cuando el experimento lo requiera.
3. **Event vector:** representación vectorial del acontecimiento final o intermedio, separando dimensiones esenciales y periféricas.
4. **Cross-world matcher:** compara vectores-evento de mundos distintos, no solamente P/A/C del mismo mundo.
5. **Convergence class:** agrupa resultados equivalentes y conserva distancia, tolerancia, soporte de mundos independientes y estabilidad ante nuevas ramas.
6. **Counterexamples:** conserva mundos que no convergen, convergencias parciales y rupturas posteriores.
7. **Anti-leakage:** demuestra que la convergencia no fue causada por compartir conclusiones, datos futuros o supuestos idénticos inadvertidos.

La detección debería distinguir al menos:
- coincidencia exacta;
- equivalencia dentro de tolerancia;
- convergencia parcial en dimensiones esenciales;
- convergencia solo proyectada (posible falso positivo);
- convergencia temporal transitoria;
- divergencia/no convergencia.

No se debe llamar canónico a un evento solo porque la distancia entre trayectorias disminuya. La contracción es una señal de aproximación; la convergencia canónica requiere coincidencia del vector-evento esencial y replicación independiente.

## Integración recomendada

Ubicar el nuevo observatorio después de que cada mundo haya producido su trayectoria y antes de cualquier síntesis global:

`observaciones compartidas -> mundos aislados -> trayectorias propias -> vectores-evento -> comparador transversal -> clases de convergencia canónica`

La geometría U6 existente se reutiliza como instrumento de análisis de trayectorias, no como sustituto del comparador de eventos entre realidades.

**Conclusión:** la arquitectura ya contiene los precursores matemáticos y varias nociones parciales de convergencia. No contiene aún el evento canónico en el sentido preciso que se definió en esta conversación. La brecha no es “añadir más geometría”; es introducir la unidad de realidad independiente y comparar sus vectores-evento a través de mundos.
