# U6 — Índice de entradas previas y protección de separación

Fecha: 2026-11-23
Rama: alterno/cameo-pesos
Alcance: preparación entry-only; no ejecución del motor.

## Cambios ejecutados

- casos/fabrica/preparar_entrada_solo.py ahora construye un índice de case_id y sujetos visibles antes de escribir una entrada.
- Fuentes leídas por el índice: casos/resultados/resultados.jsonl (solo case_id/person), casos/ciegos/**/entrada.json (solo entradas y excluyendo rutas custodia), casos/fabrica/semillas_entrada/*.json (excepto el esquema y el lote actual), casos/fabrica/entradas_solo/*/entrada.json y literales id/person de SEMILLAS_Z en semillas_lote_F007.py mediante ast.parse.
- C01–C20 quedan reservados por nombre de directorio. No se leen SALIDA_CONGELADA, destinos, desenlaces ni custodia.
- El índice falla cerrado si un archivo previo visible no se puede leer o parsear. No escribe entradas cuando el índice está incompleto.
- La salida informa que la unicidad contra identidades selladas C01–C20 debe ser comprobada por el custodio con su índice privado. El preparador no intenta inferirlas ni abrir custodia.

## Verificación

- Commit de lógica: 9dc49f272612f93814e206ad51c475092e38abf2.
- Commit de fixture corregido: 9f99f15de4bef42544157865ff8881c0f41f225e.
- CI: run #45172870551, job runner-contract SUCCESS, 78 passed in 1.09s.
- Run #45172749593 falló por un fixture AST que escribía el texto literal \\n; se corrigió el fixture usando chr(10). No se atribuye como prueba exitosa.
- El CI ejecutó los contratos y pruebas; no ejecutó casos reales ni incrementó n.

## Estado de cohorte

- F007 sigue sin aptitud: 8 sujetos, dos cortes por sujeto, fuentes secundarias Wikipedia, sin fecha exacta de nacimiento/muerte ni Z90 completo.
- La gate Z90 actual calcula Z90 desde nacimiento/muerte, exige cierres acumulativos desde nacimiento y último corte exactamente en Z90. F007 no satisface ese contrato.
- No hay JSON nuevo en semillas_entrada ni entradas staged en entradas_solo. No hay cohorte sellada entregada por el custodio.
- PR #8 sigue OPEN / NOT MERGED. No se modificó main, no se fusionó, no se ejecutó el motor y no se abrieron destinos_lote_F007.py ni custodias.

## Siguiente compuerta mínima

El custodio independiente debe entregar una cohorte sellada y comprobar duplicados de sujeto contra su índice privado de C01–C20. Cada caso nuevo requiere fuente primaria fechada, Z congelado antes de H1/H2, evidencia no posterior a Z, hashes y recibos. Hasta entonces no preparar ni contar nuevas corridas.

