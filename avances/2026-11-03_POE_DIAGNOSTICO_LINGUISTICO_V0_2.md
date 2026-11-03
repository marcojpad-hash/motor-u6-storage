# Avance POE-U6 — diagnóstico real v0.2 (2026-11-03)

## Ejecutado
- CI run 41601242042: SUCCESS.
- Se ejecutaron clasificadores lingüísticos reales del repositorio.
- 22 frases: 13 negativas claras, 4 positivas claras, 5 ambiguas.
- 3 pares mínimos de género.
- 7 casos de causalidad, temporalidad, referencia y negación.
- Wrapper PREGUNTA_DETRAS_V2: 23 piezas revisadas, 13 marcas, bandera MARCA.

## Resultado corregido
- TP 3, FP 6, TN 7, FN 1.
- Precisión 33.33 %, recall 75 %, tasa FP 46.15 %.
- La primera pasada contó un interrogativo como positivo; la revisión semántica corrigió esa etiqueta y conservó el primer registro.
- Pares de género: 0/3 diferencias; el par elegido/a mantiene el mismo falso positivo en ambos géneros.
- Copi identifica afirmación del consecuente en T06.
- Se mantienen sin resolver ambigüedades referenciales T03/T04 y alcance de negación T05.

## Lectura
Los resultados positivos, negativos, mesetas y ausencias se conservan. No se exige 100 %. La medición revela simultáneamente recuperación de positivos, falsos positivos, un falso negativo, estabilidad contrafactual en una muestra pequeña y huecos de ambigüedad.

## Próximo paso técnico
Crear variante lateral del detector de perfilamiento y de anotación de ambigüedad. Mantener baseline v2.3.3 congelado y comparar sobre el mismo corpus, más un conjunto nuevo de contraste. Métrica principal: reducir falsos positivos sin perder verdaderos positivos; métrica secundaria: identificar ambigüedades sin forzar lectura única.

## Integridad
No se modificaron Engine V5 ni catálogo 244. Todo permanece en rama experimental. Informe completo: `informes/2026-11-03_POE_DIAGNOSTICO_LINGUISTICO_RESULTADOS_CORREGIDOS.md`.
