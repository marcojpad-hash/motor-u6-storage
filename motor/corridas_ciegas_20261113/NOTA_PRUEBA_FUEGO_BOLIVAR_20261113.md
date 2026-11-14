# Prueba de fuego — Bolívar (biografía nueva, v2)

**Fecha:** 2026-11-13 ~19:05 CST
**Origen:** Gemini ofreció dos opciones (prueba de fuego con biografía nueva
o blindar el documento). Pecas hizo la prueba de fuego.
**Caso:** Bolívar, `RESULT_BOLIVAR_CON_TEXTO_EVIDENCIA_Z90_U6_20261113.json`
(10 cortes). NO estaba en la comparación de 5 casos (Napoleón, Mozart,
Tesla, Transición1, Mandela). Es biografía nueva para la lectura de gravedad.

## Resultado

- **Régimen:** MESeta_O_ESTABILIZACION (en meseta).
- **Comportamiento:** 11 familias bajo top5 suben; 3 familias cocinándose
  abajo; 1 emergente.
- **Punto no considerado:** `weber_02_autoridad_carismatica` (rango Z 6,
  pendiente 1.869, ASCENSO_LENTO). Es la autoridad carismática — el rasgo
  que define a Bolívar como Libertador — y NO está en el top. El sensor lo
  encuentra mirando abajo, donde los modelos no miran.
- **Sol:** `arquetipo_el_gobernante`, peso Z **0.8155** (coincide con la
  verificación de 55 casos: Bolívar 0.8155). El gobernante es el atractor.
- **Nudos:** 11 | capturados 0 | siendo jalados 9 | **acercándose 1** |
  resisten 0.
  - `utopia_autonomia_atenas` (dist 0.182, pend 0.2857) es ACERCANDOSE: lejos
    del Sol con pendiente media. En v1 habría caído en EN_TRANSITO
    (contradicción). La corrección v2 se valida en un caso nuevo.
  - `weber_02_autoridad_carismatica` (dist 0.011, pend 1.869) es EN_TRANSITO:
    a 0.011 del Sol, a punto de ser capturado, moviéndose muy rápido.
- **Cometa:** **C5** (9 nudos suben, salto total **1.045**) — el segundo salto
  más grande medido (Mandela C3_1961: 1.077 con 10 nudos).
- **Proporcionalidad:** **-0.232**, confianza **MEDIA**, n=11. Negativa como
  Mozart (consolidación: cerca del Sol sube más rápido). El signo es estable
  desde C5 (-0.068) hasta C8 (-0.076) hasta el final (-0.232).

## Proyectivo (honesto)

- **Hasta C5:** alerta de pulso en 10 nudos en C5. El cometa real ES C5.
  El pulso y el cometa coinciden: la alerta dice "cometa en los siguientes
  1-3 cortes" pero el cometa ya está ocurriendo en ese mismo corte. La
  alerta es "hay un cometa activo o inminente", no "vendrá en k+1..k+3".
- **Hasta C8:** alerta de pulso en 2 nudos en C8, "posible cometa en los
  siguientes 1-3 cortes". **No llegó ningún cometa nuevo** (el mayor salto
  ya fue C5). La alerta puede ser un falso positivo: un pulso entra pero no
  se convierte en cometa grande. En Napoleón la alerta de C8 sí predijo C9;
  en Bolívar la de C8 no se cumplió. La alerta es una advertencia, no una
  garantía.
- **Dirección:** el signo negativo (consolidación) ya se veía desde C5
  (-0.068) y se mantuvo hasta el final (-0.232). La dirección sí se anticipa.

## Veredicto de la prueba de fuego

El instrumento funciona en una biografía nueva sin tocarlo: entra en meseta,
encuentra el punto no considerado (autoridad carismática, el rasgo de
Bolívar), el Sol llega al techo (~0.8155), el cometa es grande y la
proporcionalidad es negativa con confianza MEDIA. Y la prueba también muestra
los límites honestos: la alerta de cometa puede coincidir con el cometa o ser
un falso positivo. Eso no rompe el instrumento; lo acota.

## Archivos

- Lectura completa: `motor/corridas_ciegas_20261113/LECTURA_BOLIVAR_V2_20261113.json`
- Esta nota: `motor/corridas_ciegas_20261113/NOTA_PRUEBA_FUEGO_BOLIVAR_20261113.md`
