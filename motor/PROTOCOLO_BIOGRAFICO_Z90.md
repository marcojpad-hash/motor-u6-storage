# Protocolo operativo biográfico — Z90 (Mj, 2026-11-11)

El arreglo operativo acordado para los ejercicios biográficos es trabajar desde el nacimiento hasta Z90, mediante cortes temporales acumulativos y variables según la biografía. No se fija un número universal de cortes.

Primero, sobre tu pregunta: la persona muere en Z100, pero la fecha de muerte no se utiliza como información predictiva. Se utiliza para establecer el límite biográfico y calcular Z90.

### Protocolo operativo

1\. Establecer los límites biográficos.

* Obtener fecha de nacimiento y fecha de muerte.

* Calcular el intervalo total de vida.

* Definir Z90 como el punto que corresponde al 90 % de ese intervalo.

2\. Construir los cortes.

* Se empieza en el nacimiento.

* Cada corte tiene una fecha de cierre.

* Las ventanas son acumulativas: C1 abarca desde el nacimiento hasta su fecha de cierre; C2, desde el nacimiento hasta una fecha posterior, y así sucesivamente.

* El último corte termina en Z90.

* El número de cortes depende de la biografía y de la resolución temporal que se necesite. No se imponen siete ni diez por regla general.

3\. Ejecutar cada corte sin información futura.

* Solo se permite información que ya existía hasta la fecha de cierre de ese corte.

* No se introducen acontecimientos posteriores.

* Se generan y congelan las hipótesis correspondientes.

4\. Sellar el resultado en Z90.

* La predicción queda cerrada.

* El 10 % final de la vida queda fuera de la información predictiva.

* Z100 se libera después, exclusivamente para validar el resultado y realizar análisis retrospectivo.

### Ejemplo que sí tenemos documentado: Mozart

10 cortes ejecutados

* Nacimiento: 27 de enero de 1756.

* Z90: 4 de mayo de 1788.

* Cortes: C1 a C10.

* Cada corte utilizó información acumulada hasta su fecha.

* El resultado se congeló en Z90.

Este es el precedente operativo concreto, no el Churchill diagnóstico de un solo corte.

La regla central: no predecimos conociendo el desenlace. Construimos diez, o los cortes que correspondan, ventanas históricas progresivas y hacemos que el motor trabaje sin acceso al futuro.

Fixture del precedente Mozart: casos/precedentes/MOZART_10_CORTES/INPUT_FROZEN.json

## Implementación de la compuerta Z90 (2026-11-21)

- En biografía cerrada, las fechas `fecha_nacimiento` y `fecha_muerte` son exactas `YYYY-MM-DD`.
- Se calcula `Z90 = nacimiento + floor(0.9 × (muerte − nacimiento en días))`. Se truncan fracciones de día para no rebasar el 90 %. El caso Mozart (1756-01-27 a 1791-12-05) produce 1788-05-04.
- `z_trabajo` y `z90_date` deben coincidir exactamente con ese resultado.
- Cada corte usa `date` como fecha de cierre y `window_start` como inicio de ventana. En todos los cortes, `window_start` debe ser la fecha de nacimiento; los cierres deben crecer estrictamente y el último debe ser exactamente Z90.
- La evidencia de cada corte debe respetar su propio cierre: `claim_date <= cuts[i].date`; para fuentes primarias también `source_date <= cuts[i].date`.
- La compuerta valida estructura y fechas, no demuestra independencia humana del custodio ni que el contenido de los vectores sea semánticamente acumulativo. Eso sigue requiriendo custodia independiente y revisión externa.
