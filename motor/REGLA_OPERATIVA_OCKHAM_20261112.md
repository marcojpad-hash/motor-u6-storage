# REGLA OPERATIVA — NAVAJA DE OCKHAM

**Orden de Mj (2026-11-12 ~21:38 CST):** en la regla operativa hace falta
meter una navaja de Ockham. ("Vaca de ojama" era navaja de Ockham, dictado
deformado; ya decodificado.)

**Verificado:** CERO menciones de Ockham / Occam / navaja en todo el motor
y en el workspace. La navaja no existe en la metodología. Este documento
la mete. No toca el RUTEO de 2026-09-14
(`casos/35A_ESTUDIO/01_DATOS/RUTEO_PERFIL_VS_PREDICTIBILIDAD.txt`, archivo
de caso sellado): lo complementa, no lo reescribe.

---

## La navaja, en palabras

No multiplicar mecanismos más allá de lo necesario. Si una lectura
existente ya mide lo que el mecanismo nuevo mediría, el mecanismo nuevo
no se construye. Si dos lecturas empatan, se queda la más simple. Todo
lateral nuevo debe nombrar qué mide que nada existente mida.

En pendejo: si ya tienes una regla que lo mide, no hagas otra que lo
mida igual. Y si lo nuevo no mide nada nuevo, no es un mecanismo, es
un adorno.

## Criterios operativos (la navaja como lista de chequeo)

1. **Nombrar la medición.** Antes de construir un lateral, escribir en
   una línea qué mide que ninguna lectura existente mida. Si la línea
   no se puede escribir, el lateral no se construye.
2. **Reutilizar antes de construir.** La maquinaria existente (asignación
   por compañía, tableros sombra, p_final, frentes de latencia) se
   prueba primero; el mecanismo nuevo solo cubre el hueco que queda.
3. **El empate se lo queda lo simple.** Si dos lecturas dan el mismo
   veredicto, se queda la más simple y la otra se corta (o queda como
   despliegue derivado, no como mecanismo).
4. **Números no inventados.** Un mecanismo no inventa una distribución
   donde el caso no da datos (por ejemplo, repartir una masa
   proporcional a pesos del catálogo). Lo que no se mide se reporta
   como cero o ausente, no se rellena por suposición.
5. **La puerta es comparación, no re-derivación.** Un lateral nuevo se
   chequea contra resultados ya guardados; no reimplementa el conteo
   contra el que se chequea.

## Conexión con el RUTEO (2026-09-14)

El RUTEO ya trae la navaja en otro terreno: una luz que nace del MARCO
del hablante se taguea PERFIL_MARCO y se DESACOPLA del contador de
predictibilidad — no merece un mecanismo predictivo nuevo. La navaja
es el mismo instinto aplicado a los mecanismos: una lectura nueva que
solo vuelve a decir una luz de perfil no merece un mecanismo nuevo.
Y la gemela del RUTEO (regla 3: HIT estructural solo con HECHO/corte
mapeable nuevo, no con reincidencia del estilo de hablar) es la gemela
de la navaja: un mecanismo que solo vuelve a contar lo que ya se contó
no da un HIT nuevo.

## Conexión con Sherlock (el filo humano de la navaja)

Sherlock ya existe y corre: `plugin_metodo_rigor.py` (Holmes / Hecate /
Schopenhauer) + bloque SHERLOCK_RIGOR en `guardianes_control_v1.py`.
No toca F, no puntúa. Sus tres preguntas SON el filo humano de la
navaja:

- **Holmes** — "tokens de HECHOS del corte o de mi tesis?": si los
  insumos del mecanismo son tokens de la tesis, el mecanismo mide la
  tesis, no el caso. Es el criterio 1 de la navaja (nombrar la
  medición) aplicado a mano.
- **Hecate** — "pedí más de lo mismo / forcé una lámpara?": si el
  mecanismo sigue apuntando al mismo letrero, está repitiendo, no
  midiendo. Es el criterio 2 (reutilizar antes de construir) aplicado
  a mano.
- **Schopenhauer** — "defiendo lo que vi o leo el tablero?": si la
  auditoría defiende el mecanismo en vez de reportar sus fallos, la
  navaja no se aplicó. Es el veredicto de la navaja aplicado a mano.

El auto no sustituye las 4 líneas humanas ("Es alarma",
`plugin_metodo_rigor.py`). La navaja se aplica a mano, caso por caso,
con esas tres preguntas; el auto solo levanta la alarma.

## Estado

Este documento ES la regla, escrita. Aplicarla a los laterales
existentes es decisión de Mj, lateral por lateral. La primera
aplicación (auditoría Ockham de la vinculación, con chequeo Sherlock)
está en `~/workspace/u6-alterno/OCKHAM_VINCULACION_AUDITORIA_20261112.md`,
como propuesta, no como implementación.
