# Smoke CEB F002 (Galilei, Pasteur) — 2026-10-25
Antes: fábrica salía con código 9 `FALLO_EJECUCION_CALDERO` en 4 "casos": `*_RECIBO_EJECUCION` y `*_CEB_LEDGER_MANIFIESTO`.
Causa raíz: `compuerta_caldero`/`compuerta_piezas` leían `corridas/*.json` y trataban los sidecars del arnés como casos (sin fila CEB → SIN_RECIBO_CEB). Falso positivo.
Arreglo: `_corridas_caso()` excluye sidecars. Engine y 244 intactos; predicción sin cambios.
Después: Caldero EJECUTADO en ambos casos; compuerta_piezas OK (0 FALLO_EJECUCION, 0 REQUIERE_CONTRATO); exit 0.
pre_h_analogical_search(V0.18): ACTIVA/OK (ya no API_PENDING). Resto: OK o ACTIVA_MUDA (corrió sin señal), caldero_run.py SUPERADA (contractual).
