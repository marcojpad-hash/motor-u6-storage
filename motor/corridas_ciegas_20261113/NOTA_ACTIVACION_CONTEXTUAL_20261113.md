# Confirmación: activación conceptual según el contexto — 2026-11-13

## Pregunta de Marco
"Confirmamos que sí se active de esa forma": activación CONCEPTUAL dependiendo
del contexto donde está el token, no una matriz específica y rígida.

## Resultado (verificación por ejecución, script reproducible)
`verif_activacion_contextual.py` (mismo candidato, mismo motor, misma función
`laterales_unico_v1.voto_familias_tokens`; solo cambia el contexto del caso):

- **Contexto B** (cortes recientes con `retiro_voluntario`, token del 244 que está
  en los tokens propios de 30_ambición Y en las palabras de la entrada del puente
  `separacion_fundador_gestion_madurez`, familia ciclo_vida_organizacional_adizes):
  estado **ACTIVA**, voto ambición = **1.0**, gobernante = 0.0.
- **Contexto A** (cortes con `cooperacion`, que NO está en los tokens propios de
  ambición): estado **ACTIVA_MUDA**, voto 0.0 / 0.0.

## Conclusión
No hay tabla fija que diga "ambición siempre activa X". La activación depende de
qué tokens trae el caso (el contexto). Superposición: se activa en conjunto según
la carga semántica, sin deduplicación ni doble peso. El puente tiene 171 entradas
(familia lateral, token, D, E, pol empuja/frena, words = tokens del 244).
