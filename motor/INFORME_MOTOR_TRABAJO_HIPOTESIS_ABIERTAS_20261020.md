# Informe de corrección — motor de trabajo U6

**Entrega:** `V15.3_UNICO_WORKING_OPEN_HYPOTHESES_20261020_R1`  
**Tipo:** copia de trabajo independiente. El motor canónico y el catálogo de 244 patrones no fueron modificados.

## Cambios realizados

1. La salida primaria ahora es un conjunto abierto de hipótesis (`hipotesis`), sin límite fijo. `H1/H2` permanecen solo como aliases de compatibilidad.
2. La vectorización temporal por candidato incorpora señales micro/meso/macro, aceleración, convergencia multiescala, alineación de inercia y respuesta a curvatura/giro a la fusión de ranking.
3. Se integraron al motor de trabajo los módulos geométricos que antes corrían en el paquete lateral: `sidecar_latentes_v1`, `adaptador_convergencia_real_v1` (convergencia/Tusi) y `teseracto_recursivo_geometria_v0_4`. Sus diagnósticos se conservan compactados y aportan enlaces de trazabilidad; no se presentan como probabilidades ni como prueba física.
4. El conjunto necesario/suficiente 021 sigue aportando el núcleo. Las candidatas fuera de ese núcleo con dos o más enlaces explícitos de trazabilidad pueden entrar como hipótesis complementarias, identificadas por su rol.
5. La apuesta se construye después del conjunto y agrupa hipótesis por régimen de trayectoria. Puede contener uno o varios escenarios; no está obligada a elegir una sola hipótesis. Sus pesos son soporte estructural relativo, no probabilidades calibradas.
6. El comparador T+1 evalúa el conjunto sellado, no solo H1/H2. Las subcorridas internas se aíslan en procesos separados y no instalan CEB primario, evitando contaminación entre ledgers. La corrida primaria conserva CEB completo.
7. El audit hook de CEB es único por proceso y se enruta al ledger activo. Los hooks de corridas anteriores ya no intentan escribir en ledgers cerrados.
8. Los manifiestos se regeneran sin ciclos de hashes y el runner copia `geometria_multicapa` al directorio temporal de ejecución.

## Corrida estándar verificada

- Caso: `CASO_NUEVO_20261013_01_CATALOG_REPAIR_R2`, 3 cortes.
- Duración reportada por el runner: **17.475 s**.
- Motor: `V15.3_UNICO_WORKING_OPEN_HYPOTHESES_20261020_R1`.
- Candidatas principales: 4 hipótesis emitidas: `13_enemistad_de_parientes`, `social_08_girard_mimesis_y_chivo_expiatorio`, `30_ambicion`, `sombra`.
- La segunda entra como `complementaria_trazabilidad_geometrica`, no por ser H2.
- Geometría multicapas: `EXECUTED`; búsqueda externa: `EXECUTED_WITH_RESULTS` (1 consulta, 3 resultados); Monte Carlo: 7.273 simulaciones, 9/9 llamadas convergieron.
- Apuesta: `CONTINUIDAD_ASCENDENTE`, agrupando las cuatro hipótesis; peso estructural agregado 1.0, explícitamente **no probabilidad**.
- T+1: 3 hipótesis selladas en el corte previo; 2 aparecen en la evidencia del corte retenido. Resultado `HIT_HIPOTESIS_SET`. No es una validación del desenlace futuro.
- Corrida primaria y subcorridas T+1 aisladas en procesos separados; ledger CEB primario preservado junto al resultado.
- StinkBox persistente: checkpoint e importación `OK`; el input repetido fue deduplicado y no añadió eventos. En el almacén de prueba había 73 cadenas únicas.
- Contrato JSON: una ausencia de `data_table_sha256` en la matriz de mortalidad se convirtió en `TORTUGAS`; no quedaron null/NaN en el JSON final. El recibo se marca `COMPLETED_WITH_TORTUGAS`, no como salida totalmente libre de incidencias.
- Hash del JSON de resultado: `2ba58aa88bdd0b85bb2baa0e3f30d24e7d5c30e492d08ec4b56ec09badc41c01`. Hash del recibo: `a62d00a91b71f9564879e17418686ef2593179ee4302c9a4b0cf09b9ac9d7baf`.

## Pruebas

`94 passed, 2 skipped, 0 failed`. Las dos omisiones son referencias históricas ausentes: motor 0.5.0 y fixture histórico Bezos. No se inventaron líneas base para reemplazarlas.

## Hashes verificados

- `Engine_V5_CANONICO_SOLO.py`: `665c39a2861e58772522e91272563260d980908b1d4ab9f7092d3413d0c36082`
- `patterns_final_v14.json`: `d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1`
- Motor de trabajo: `f0c901950de18a0b02b5a28d84ce57af258f624ce6969ed8a20d4a675f240fda`

El preflight del manifiesto quedó en `MATCH`, sin deriva ni archivos ausentes. La calibración predictiva del desenlace sigue pendiente de revelados posteriores sellados por caso. Esta entrega corrige la cardinalidad y el flujo de hipótesis/apuesta; no declara una calibración lograda.
