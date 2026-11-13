# Trazabilidad helicoidal y el eje — lo logrado en la última parte matemática del motor U6

**Fecha:** 12 de noviembre de 2026
**Qué es este documento:** el recuento de lo que se encontró y se midió en la última parte del trabajo matemático del motor U6: que las trayectorias son helicoidales, que tienen oscilaciones, y que pasamos de descubrir esas oscilaciones a encontrar un eje que las contiene y les da estabilidad. Todo lo que aquí se dice está verificado por ejecución; las cifras que aparecen son solo anclas de evidencia, no la explicación. La explicación está en palabras.

---

## 1. El punto de partida: el motor es plano

El motor no ve hélices. Su vectorización pega los tres tableros en una sola línea: primero las 244 familias del tablero interno, luego las 244 del externo, luego las 244 de la situación. De un corte al siguiente mide la distancia en línea recta entre dos puntos, y el ángulo entre dos rectas seguidas. Eso es todo lo que mide.

No hay radio en el motor. No hay ángulo alrededor de un eje. No hay avance a lo largo de un eje. El giro que se veía en las gráficas — esa vuelta de poco más de media circunferencia en Mozart y en Napoleón — no lo calculaba el motor: se calculaba en scripts de graficar, fuera de él. Y los dos tableros que no son el interno (el externo y el de la situación) están planos en el punto medio en todos los cortes de Mozart y de Napoleón: la hélice, si vive en algún lado, solo puede vivir en el tablero interno.

Ese era el problema que Marco señaló: la vectorización se maneja desde una bidimensionalidad muy simple. Había que ver si se podía hacer una vectorización basada en el modelo helicoidal, porque ahí podría estar parte del problema.

## 2. Lo que se encontró: las trayectorias son helicoidales y oscilan

La primera sonda tomó los tableros internos de Mozart y de Napoleón y les buscó la forma. El protocolo fue honesto: se ajustó todo solo con los primeros nueve cortes, sin ver el décimo, y el décimo se proyectó sin reajustar nada. Es el corte ciego.

Lo que salió:

- **La trayectoria da vueltas como un resorte.** El giro total se reproduce: en Mozart sale casi el mismo que el de los scripts locales, y en Napoleón también. La tubería de medición es confiable: mide lo mismo que ya se había medido por otro camino.
- **El radio respira.** No es un tubo fijo: se ensancha y se angosta de corte en corte, dentro de un margen. En Mozart el margen va de lo más angosto a lo más ancho en una proporción de más de cuatro a uno; en Napoleón, de más de diez a uno. Respira, no es rígido.
- **La fase no gira pareja.** El giro por paso es irregular: a veces da un paso grande, a veces casi no gira, a veces retrocede. El avance, en cambio, sí camina parejo: la trayectoria avanza de forma ordenada a lo largo de su dirección principal, mientras el giro va a trompicones.
- **La hélice predice mejor dónde cae el punto que la línea recta.** En los dos casos, la predicción helicoidal del décimo corte cae más cerca del punto real que la predicción plana. Pero no predice qué familias suben: de las cinco que más suben en el corte real, la hélice no acierta ninguna en ninguno de los dos casos. La plana acierta tres de cinco en Mozart. La geometría se predice; el contenido, no.

Ese es el muro, dicho en palabras: continuidad sí, emergencia no. El motor anticipa que la trayectoria sigue, no qué es lo nuevo que aparece.

## 3. El eje: no es el primer componente, se infiere

La segunda sonda buscó el eje. La primera sonda usaba como eje la dirección de mayor variación (el primer componente). Marco tenía razón en dudar de eso: el eje no está descubierto como tal, pero sí se puede inferir, y esa dirección es la que nos lleva hacia dónde, y sobre ella gira la parte cíclica.

El método: probar direcciones y quedarse con la que deja el radio más estable — la que menos varía — exigiendo que la trayectoria gire de verdad alrededor de ella, y trabajando en un espacio donde cada dirección se pone en su misma escala para quitar la distorsión de tamaño. Todo ajustado solo con los primeros nueve cortes.

Lo que salió:

- **El eje no es el primer componente.** Está inclinado respecto a él: cuarenta y seis grados en Mozart, sesenta y ocho en Napoleón. El primer componente no era el eje.
- **Con el eje inferido, el radio se estabiliza.** La variación del radio baja a menos de la mitad de lo que era con el primer componente, en los dos casos. El tubo se vuelve tubo de verdad.
- **La fase se empareja.** El giro por paso se vuelve más parejo, y hay un detalle que llama la atención: la mediana del giro por paso es la misma en los dos casos, treinta y siete grados hacia atrás por paso. Es un patrón a vigilar: puede ser propiedad del motor y no del caso.
- **La predicción del décimo corte mejora en todo lo geométrico, en los dos casos.** El error cae a menos de la mitad, y la correlación sube. Pero el muro sigue: de las cinco familias que más suben, la hélice con el eje inferido no acierta ninguna en ninguno de los dos casos.

Y hay dos matices honestos. Con el eje inclinado, el avance se vuelve brincón: el último paso es un brinco grande en los dos casos. Y solo nueve puntos ajustan el eje, así que hay riesgo de sobreajuste; el décimo corte es el resguardo, y en geometría pasó.

## 4. La ruptura del margen

Marco preguntó qué pasa cuando la trayectoria se sale del margen. En Mozart, el radio real del décimo corte se sale del margen que se había medido a ciegas, y la fase se invierte: después de girar hacia atrás paso tras paso, el último paso gira hacia adelante. Pasa justo en el décimo corte, que es la fecha de trabajo, el corte Z. Y la hipótesis principal se sostuvo.

En Napoleón, el radio real del décimo corte queda dentro del margen. Pero acelera: el movimiento se dispara en los últimos pasos.

Hay que decirlo claro: el motor no tiene regla de margen de radio. El margen es construcción de la sonda, no del motor. El marcador que sí trae el motor mide otra cosa — velocidad y curvatura — y marcó el décimo corte de Mozart como giro fuerte y el de Napoleón como movimiento acelerado. La ruptura de radio y la ruptura de velocidad son dos cosas distintas, y cada caso rompió una.

## 5. El barrido de mortalidad: el radio que crece hacia el final

La inferencia de Marco fue que la ruptura del margen podría ser la señal de predicción de muerte y fatalidad. Se midió en los treinta y cinco casos de calibración, que tienen solo tres cortes cada uno, así que ahí no se puede hablar de romper un margen — no hay prefijo con el que definirlo — pero sí se puede medir si el radio crece hacia el final o se contrae.

Lo que salió: en casi la mitad de los casos el radio crece hacia el final, y en la otra mitad se contrae. Cuando crece, el desenlace trae fatalidad dura en más de la mitad de los casos; cuando se contrae, solo en uno de cada cinco. Es una tendencia, no una ley: hay casos que crecen y no terminan en fatalidad, y casos que se contraen y sí.

Lo que no anuncia nada es la velocidad: que el último paso acelere no se junta con la fatalidad. Y el marcador del motor marca casi todo como giro fuerte, así que no distingue nada ahí.

## 6. Noether y Carson: corridos desde cero, y la geometría es la misma que en septiembre

Los dos casos ciegos sellados del checkpoint de septiembre — Noether y Carson, siete cortes cada uno — se extrajeron de la biblioteca y se corrieron desde cero con el motor actual. Los dos tienen el desenlace sellado conocido: acierto en la apuesta, y muerte después del corte final (Noether en 1935, Carson en 1964).

Lo que salió:

- **La geometría es idéntica a la de septiembre.** Los movimientos, la persistencia y la curvatura salen iguales a los de sus freezes, corte por corte. El motor actual reproduce lo que el motor de septiembre midió.
- **Noether rompe el margen en el corte final; Carson no.** En Noether el radio real del séptimo corte se sale del margen del prefijo, por poco. En Carson queda dentro, cómodo.
- **Las dos terminan en generatividad y muerte.** Noether: la obra perdura y muere en 1935. Carson: la obra perdura y muere en 1964. La ruptura no dice si el final es desastre o generatividad: marca el final, no su sabor.
- **Y hay una trampa que el motor sí cae.** En Noether el motor corona como primera hipótesis al gobernante — el letrero de prestigio que el freeze de septiembre advirtió que no había que coronar. El acierto de septiembre era juicio humano (el mentor-teórico), no el máximo del tablero. En Carson el motor corona al creador, con el mentor de segunda, y eso sí alinea con el acierto sellado.

Con los cuatro casos largos, el recuento queda así: rompen el margen Mozart y Noether; no rompen Napoleón y Carson. Queda como hipótesis a probar, con solo dos y dos, que los que rompen mueren de golpe y los que no rompen declinan lento. No es conclusión.

## 7. La regla de los límites y lo que falta en el catálogo

La regla que puso Marco: los valores viven entre los dos límites, con el punto medio como base, y no deberían tocar los límites. Si se toca un límite es porque se acabó el mundo, se murieron. La ruptura del margen es eso mismo en geometría: la trayectoria tocó el límite.

Y se verificó en el catálogo: no hay familia para la muerte propia. La muerte solo aparece de costado — el duelo después de la pérdida, la pérdida de los seres queridos, matar a otro, la imprudencia fatal, el riesgo suicida. El motor puede mostrar la ruptura en el dibujo, pero no tiene con qué nombrarla. Si la ruptura del margen es la señal de muerte, el motor no tiene familia para decirlo. Ese es el mismo muro que el de la emergencia, visto desde el otro lado.

## 8. Qué queda

- **El eje con pocos puntos.** Nueve puntos ajustan el eje en los casos largos, seis en Noether y Carson. Hacen falta casos con más cortes para que el eje no sea un ajuste a la medida.
- **El traductor de tiempo y acciones.** Los cortes no se sabe si van conforme a tiempo o a acciones, y el tiempo distorsiona en unos casos sí y en otros no. Hay que separar la progresión por acciones del tiempo transcurrido y empatarlas.
- **La parábola del estado completo.** La parábola por familia no predice el corte siguiente. Falta probar la parábola sobre el estado completo, no familia por familia.
- **El muro sigue.** La geometría se predice; qué familias suben, no. Y la ruptura marca el final, no su sabor.
- **La familia que falta.** Si la ruptura es la señal de muerte, el catálogo necesita una familia para la muerte propia, o el motor seguirá mostrando algo que no puede nombrar.

---

## Fuentes

Scripts y reportes (todo en `~/workspace/u6-alterno/`):

- `sonda_helicoidal.py` y `sonda_helicoidal_reporte.json` — sonda v1 (eje = primer componente).
- `sonda_helicoidal.png` — figura: perfil horizontal y polar por caso, con el margen del radio.
- `sonda_helicoidal_v2.py` y `sonda_helicoidal_v2_reporte.json` — sonda v2 (eje inferido por ajuste de hélice).
- `sonda_helicoidal_v2.png` — figura: perfil horizontal y polar con el eje inferido.
- `barrido_mortalidad.py` y `barrido_mortalidad_reporte.json` — barrido de mortalidad en los 35 casos F001–F004.
- `sonda_noether.py`, `sonda_noether_reporte.json`, `sonda_carson_reporte.json` — sondas de Noether y Carson (7 cortes, corridos desde cero con el motor actual).
- `convertir_noether_carson.py` — conversión de los dos casos del checkpoint de septiembre al formato de entrada actual.
- `matriz_finales_arquetipo.json` — matriz de finales por arquetipo (dentro de un arquetipo hay tipos distintos con finales distintos).

Corridas frescas: `motor/runs/ESTANDAR__NOETHER_CIEGO_Z90_20261112/_PRIMARY_RESULT.json` y `motor/runs/ESTANDAR__CARSON_CIEGO_Z90_20261112/_PRIMARY_RESULT.json` (copia de trabajo `~/workspace/u6-alterno/motor-cameo/`).

Casos de origen: checkpoint de septiembre en la biblioteca personal de Marco (`CHECKPOINT_MOTOR_CLONABLE_20260914.zip`, Drive), carpeta `09_CIEGOS_Z90_SELLADOS/`.
