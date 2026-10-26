# CEB: honestidad del estado Caldero (20261025)

Hallazgo (auditoría ChatGPT sobre 0895df0, revisado por Mj): la tabla CEB marcaba `sidecar_caldero_busqueda_arquetipos.py` como EXECUTED solo porque `caldero_busqueda` estaba presente, aunque las fuentes fueran precargadas/fixture.

Cambio (solo `motor/motor/laterales_unico_v1.py`, solo reporte CEB):
- La foto `_foto_estado_010.caldero_busqueda` ahora incluye `provider`, `attempt_status`, `query_count`, `result_count`, `cal_status`, `error` tomados de `features.external_archetype_search_receipt` (recibo que UNICO ya escribe).
- `estado_honesto_caldero()` reemplaza el binario EXECUTED/CABLEADO_ESPERANDO en la fila del sidecar y en `neighbor_store`:
  - EJECUTADO: proveedor externo real, status EXECUTED, ≥1 consulta y ≥1 resultado (misma regla que `correr_estandar.search_performed`).
  - INTENTADO_FALLIDO: hubo intento pero falló o 0 resultados.
  - NO_INVOCADO: sin salida Caldero.
  - OMITIDO_POR_CONDICION: SKIPPED_INTERNAL_ANALYSIS (compuerta).
  - SIMULADO_FIXTURE: provider provided_fixture/static_fixture o status EXECUTED_FIXTURE.
- Test: `tests/test_ceb_caldero_honestidad.py` (fixture ⇒ SIMULADO_FIXTURE, nunca EJECUTADO).

Sin cambios en matemática de predicción, Engine (665c39a2…) ni catálogo 244 (d827dcc3…).
