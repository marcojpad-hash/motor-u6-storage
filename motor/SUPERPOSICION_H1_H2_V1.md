# SUPERPOSICIÓN H1/H2 v1 — lectura de hipótesis que se superponen

**Estado:** ESPECIFICACIÓN (observación, no cambia rank_fusion ni H1/H2).
**Origen:** Marco, 2026-11-13. El segundo token / segunda llamada que viene con los
tokens de la vectorización SE SUPERPONE, no se sobrepone, no se anula, no se suma.
Precedente: héroe en monomito (Campbell).

## Principio

Cuando dos familias están activas a la vez (p. ej. sabio 0.8 y creador 0.8 en el
mismo corte), **coexisten, cada una con su identidad**. No compiten por un solo
lugar, no se restan, no se suman en un puntaje único. El estado es la
superposición de las dos.

## Lo que el motor hace hoy (y por qué no es superposición)

- `rank_fusion` ordena las familias por un solo puntaje; H1 es la primera,
  H2 la segunda.
- `margen = rank_fusion(H1) − rank_fusion(H2)` (resta, competencia).
- `top1_top2_empate` si |H1 − H2| ≤ EMPATE_EPS (empate, competencia).

Eso lee H1/H2 como una competencia con ganador y margen. No lee superposición.

## Lectura por superposición (lo que se codifica)

Para un caso, con H1 y H2 y sus puntajes por corte:

1. **Coexistencia:** si H1 y H2 están ambas ≥ 0.7 en el mismo corte, el estado
   es superposición de las dos, no empate. Se reporta como `H1+H2`
   (p. ej. `sabio+creador`), no como "H1 gana a H2 por margen X".
2. **Identidad:** cada familia conserva su peso por corte; no se fusionan en
   un solo puntaje. La superposición se describe por el par (peso_H1, peso_H2)
   por corte.
3. **Subtipo por compañeras:** el subtipo de H1 se lee por la familia con la
   que superpone. Ejemplos medidos (k Tusi):
   - sabio+creador+héroe (Einstein +0.429, Rembrandt +0.744): subtipo
     creador-héroe, k positivo.
   - sabio+mentor (Hawking −0.700): subtipo maestro, k negativo.
   - sabio+audaz/aventurero (Tulipán v2 −0.463): subtipo aventurero.
4. **Margen reinterpretado:** el margen (H1−H2) NO mide cuánto gana H1;
   mide la asimetría de la superposición. Margen ~0 = superposición
   simétrica (las dos pesan igual); margen grande = superposición
   asimétrica (una pesa más, pero la otra sigue presente).

## Lo que NO es superposición

- No es suma: sabio 0.8 + creador 0.8 no es 1.6 de nada.
- No es anulación: que H1 sea sabio no anula a creador.
- No es solapamiento: creador no queda escondido detrás de sabio.
- No es jerarquía: no hay una familia arriba y otra abajo; hay dos
  presentes a la vez.

## Pendiente

Codificar la lectura (lateral de observación) que, por caso, reporte el par
superpuesto H1+H2, su simetría por corte y el subtipo por compañeras.
No toca rank_fusion ni el ranking.
