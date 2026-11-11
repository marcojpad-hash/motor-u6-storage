# Smoke StinkBox cableado — Napoleón

- Fecha: 2026-11-11 ~03:07 CST. Rama: `alterno/cameo-pesos`.
- Cambio: solo `motor/motor/stinkbox_transport_v0_2.py` (base rama = original de main, sha256 a0253e6e2f51fd36).
  - `_load_persistent_stinkbox_tokens`: carga en solo lectura los tokens de otros vaults
    `stinkbox_*.json` + `stinkbox_tokens_descubiertos.json`. Sin inventar equivalentes,
    sin escribir en las fuentes, sin mutar el canon. El vault del caso actual se excluye.
  - `transport(extra_tokens)`: esos tokens entran al `candidate_support`.
  - `persistent_input` queda registrado en el RESULT. Los descubiertos se registran como
    luces persistentes (branch `stinkbox_discovered`; se activan solo si se re-observan).
  - Engine V5 y catálogo 244 intactos. FEEDS_H sigue False; el sombrero blanco no se toca.

## Smoke NAPOLEON_STINKBOX_CABLEADO (misma entrada que NAPOLEON_CAMEO_NUEVO)

- Exit 0, recibo COMPLETED, 19.094 s, Engine/patterns MATCH.
- Tokens persistentes cargados: 177 (vault Churchill + descubiertos, incl. oficio).
- `global.unique_tokens`: 175 -> 297. `candidate_support` no-cero: 48 -> 69/244.
- 24 patrones cambiaron soporte (ej. 30_ambicion 0.167 -> 0.333).
- Luz `oficio` registrada (branch stinkbox_discovered, fuente stinkbox_tokens_descubiertos.json).
- H1/H2 SIN cambio: 31_conflicto_con_un_dios / 30_ambicion, rank_fusion H1 28.74557.
- H2 stinkbox_support: 0.583 -> 0.667. El cable alimenta al predictor; en Napoleón no movió H.

## Archivos

- Recibo: `RESULT_NAPOLEON_STINKBOX_CABLEADO_RECIBO_EJECUCION.json` (sha256 2b7dadad3a09bd07...).
- El RESULT completo (6.4 MB) NO se sube por el conector (binario/grande); queda en local
  con sha256 4b0e17390f0cb41c.... Su hash está en el recibo.
- Transporte parcheado sha256: 7b9f761299ce21ac...

Ledger: hecho `stinkbox-cableado-smoke` en ~/workspace/guardian/HECHOS.json.
