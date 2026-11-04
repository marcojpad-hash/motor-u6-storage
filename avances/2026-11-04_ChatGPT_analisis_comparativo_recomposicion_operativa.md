# 2026-11-04 — ChatGPT — análisis comparativo de recomposición operativa

## Qué cambió

Se añadió un análisis comparativo nuevo, basado en inspección del código actual y en la lectura crítica de los tres estudios comparativos que ya existían del 3-nov.

Documento:
- docs/ANALISIS_COMPARATIVO_RECOMPOSICION_OPERATIVA_U6_2026-11-04.md

Commit del documento: bf157983ebaa1885b5c797ce551f47d44b2ca74d  
Blob SHA GitHub del documento: 64de6229b88fdbe51586f71dda82651addda1524  
SHA-256 físico: NO_CALCULADO_EN_ESTA_INTERVENCION (no se confunde el blob SHA con SHA-256).

## Antes → ahora

- Antes: existían una genealogía técnica, una auditoría de formalismos y un estudio comparativo general del 3-nov.
- Ahora: existe una comparación de transposición operativa, mecanismo por mecanismo, que vincula operador, objeto, función dentro de U6, contrato, efecto arquitectónico y límite de equivalencia.

Hallazgos nuevos/acotaciones principales:
1. Se identificó explícitamente el doble filtro temprano: CUELLO_K=5 tokens por eje/corte antes del Engine y top-3/0.65 de familias por tablero/corte después de puntuar las 244.
2. Se precisó que el universo abierto posterior es variable, pero parte de la unión de candidatas supervivientes; no equivale a explorar las 244 familias completas.
3. Se describió la fusión real: dimensiones numéricas, constantes/duplicadas excluidas, rangos fraccionales con empates, señales laterales candidatas y discriminantes añadidas individualmente, y posible segunda pasada de resolución.
4. Se delimitó la transposición de Bayes, Monte Carlo, geometría, set-cover y ranking, sin atribuirles semánticas que no conservan.
5. Se corrigieron afirmaciones demasiado amplias: no está demostrada una lógica paraconsistente formal, DeLP/ABA, determinismo total, memoria append-only de toda la evidencia ni trazabilidad semántica completa.
6. Se ubicó la posible contribución en la recomposición bajo contratos de autoridad y transformación, pendiente de ablaciones y benchmarks.

## Archivos modificados

- docs/ANALISIS_COMPARATIVO_RECOMPOSICION_OPERATIVA_U6_2026-11-04.md — nuevo archivo.
- avances/2026-11-04_ChatGPT_analisis_comparativo_recomposicion_operativa.md — este registro.

No se modificó código, contratos vigentes, Engine V5 canónico ni catálogo 244.

## Hashes canónicos verificados

- Engine V5 SHA-256 esperado: 665c39a2861e58772522e91272563260d980908b1d4ab9f7092d3413d0c36082.
- Catálogo 244 SHA-256 esperado: d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1.
- Se consultó docs/MAPA_VERSIONES_Y_AUTORIDAD.md; esta intervención no descargó los bytes canónicos para recalcular esos SHA-256.

## Pruebas

- 0 passed, 0 skipped, 0 failed.
- No se ejecutó suite: cambio exclusivamente documental.
- Verificación de persistencia: el documento comparativo fue leído de vuelta desde main; blob SHA confirmado como 64de6229b88fdbe51586f71dda82651addda1524.
- No se ejecutó corrida predictiva ni smoke.

## Estado

DOCUMENTACIÓN COMPARATIVA CREADA Y VERIFICADA POR LECTURA POSTERIOR. No se afirma novedad mundial, mejora predictiva ni validación empírica de la recomposición.
