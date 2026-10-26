# 2026-10-25 GrokBot — Caldero arquetipos (guardián de pistas LLM) + PRE-H reutiliza búsqueda + StinkBox→GitHub

Engine 665c39a2… y catálogo 244 d827dcc3… SIN CAMBIOS (verificados antes/después).

## 1. Caldero → búsqueda de ARQUETIPOS («quemaduras ajenas») — prioridad
- Ya estaba viva en F002 (duckduckgo_html/lite, query ciega, SelfMatchFilter sobre fuentes web).
- HUECO: `caldero_llm_neighbor_hints` (lo que trae el LLM) se anexaba CRUDO a tokens_neighbors, sin filtro.
- FIX: `motor/motor/guardian_pistas_llm_caldero_v1.py` (identidad / futuro-desenlace / calendario / forma) se aplica
  en el runner MOTOR_V15_3 antes de llamar al sidecar; si hay pistas y falta el guardián, la etapa falla (no pasa crudo).
  Auditoría en `features.caldero_busqueda_arquetipos.audit.guardian_pistas_llm`.
## 2. PRE-H analógica (etapa SEPARADA, secundaria)
- API_PENDING porque el sidecar no emite `status`; la reutilización exigía status=="EXECUTED". Ahora acepta recibo de
  proveedor vivo (no fixture). Smoke PASTEUR: API_PENDING → EXECUTED, 162 tokens, proveedor duckduckgo_lite.
## 3. StinkBox → GitHub
- Lote 01 subía 0: (a) el StinkBox vive en STINKBOX_STORAGE_ROOT (~/STINKBOX_PERSISTENTE/STINKBOX_STORAGE), no en la
  corrida; (b) formato real usa token_frequency/persistent_neighbor_tokens, no `tokens`; (c) el arnés deja
  corridas/*__w0.json, no _PRIMARY_RESULT.json. Arreglado en scripts/sincronizar_storage.py (--stinkbox, modo lote).
- fabrica.py llama `sincronizar_storage.py despues --corrida DIR` tras cada lote con candados OK (FABRICA_SYNC=0 apaga).
## 4. Pendiente (CEB honestidad)
- laterales_unico_v1 marca Caldero por `presente`; propuesta 5 estados: AUSENTE / FIXTURE / FALLIDO / VIVO_SIN_TOKENS / VIVO_CON_TOKENS. No aplicado aquí.
