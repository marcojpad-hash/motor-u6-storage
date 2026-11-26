# Avance 2026-11-25 — Versión Unificada 7 (V7)

Rama: `alterno/version-unificada-7` (pusheada a origin; fusión en
`alterno/cameo-pesos` PENDIENTE de suite verde en ventana tranquila).
Base: `53ea887`. Documentos: `docs/VERSION_UNIFICADA_7.md`,
`docs/CONTRATOS_OPERATIVOS_V7.md`, `motor/CANDADO_OPERATIVO_V7.json`
(verificar con `scripts/verificar_candado_v7.py`).

## Qué se hizo

- Rama V7 creada desde `origin/alterno/cameo-pesos`; lateral enunciativo
  (PR #38) fusionado (merge `792d881`, canónicos intactos).
- Orquestador: PR #10 pusheado por conector (commit `28e935d`) y fusionado
  en main (merge `8253eaf`, 14/14 pruebas en verde).
- Auditoría exhaustiva por nodo (A/B/C en `~/workspace/u6-wiring/verify-v7/`).
- Reparaciones P0/P1: A-F1 (verificar_salida_llm cableado), A-F2 (observar),
  C-F5 (U7 B5 + fix --t1), A-F5, A-F3, dorados SHA_UNICO y p_momento,
  SHA_ESPERADO (3 entradas), 5 cierres documentales.
- Reparaciones P2: C-F4 (candado de plugins en run()), C-F3 (plan_contorno en
  excepts de cierre), B-H4 (violaciones del verificador a objeciones),
  B-H1 (señales fuertes del lateral a motivo de cierre), A-F4 (gate Z90 en
  run()), C-F1 (filtro zoom devuelve descartes al Caldero).
- Cierre de los 8 fallos de la suite (finisher): 2 dorados SHA actualizados
  (esteroides `1fa9b779` → `5f494ace`, modo estricto `c0fe7fbd` →
  `9143a098`); C-F3 reparado en `motor/motor/ceb_runtime_v0_6_flow.py`
  (`call()` sin traza si el ledger está cerrado; `close()` limpia el
  global); acero inestable sin cambio de código. Dirigida 11/11 en verde.
- B5 segunda mitad (hallazgo de ChatGPT, verificado en código): sin
  `tops_t1`, b5 = 0.5 neutral (patrón B4); test nuevo
  `test_b5_sin_tops_t1_es_neutral_05`.
- U7 cableado a la ruta: `correr_estandar.py` lo invoca tras construir el
  RESULT; puntaje + B1-B6 en `result["confianza_apuesta_u7"]` y etapa en el
  recibo. Solo lee el RESULT; H idénticas. `U7_CONFIAZA_APUESTA=off` lo
  desactiva con registro visible. NOT_CALIBRATED declarado en el módulo y
  en `docs/VERSION_UNIFICADA_7.md` (pesos iguales = placeholder; calibrar
  exige pares U7 vs desenlaces reales, con n suficiente). Test U7 en CI
  (`test-motor-contracts.yml`).
- La línea alterna queda absorbida en V7; NO hay alterna 2.0.

## Verificación

- Smoke base Themistocles (53ea887): exit 0, H1 gobernante 32.986716, H2
  enemistad 30.99436, recibo COMPLETED.
- Smoke V7 final (THEMISTOCLES_V7_FINAL2): exit 0, H idénticas a la base,
  U7 EJECUTADA (S 0.7428, confianza 63.9, `calibrada: False`), B5 con
  datos reales, 0 nulos.
- Suite pre-reparaciones: 429 passed / 8 failed / 2 skipped (2507.44 s).
- Suite tras reparaciones (sin B5/U7): 437 passed / 0 failed / 2 skipped
  (1945.74 s).
- Suite final (con B5 + cableado U7): 434 passed / 7 failed / 2 skipped
  (4656.64 s). Las 7 son corridas reales que fallan con el TIMEOUT de 90 s
  del subprocess primario (`correr_estandar.py:857`, preexistente) por
  saturación de CPU: renders ffmpeg de CAPCOT en paralelo (load 6.89–
  14.89 en una celda de 1.5 CPU). Re-corrido 3 veces, mismo TIMEOUT en
  las 7 (el verificador pasó una vez). No es defecto de V7; el hook U7
  corre después del motor y no puede causarlas.
- Tests U7: 10/10 en verde.
- Candado V7 generado y verificado: 33 hashes OK, canónicos intactos,
  runner V7 `89062ad0…` ≠ runner 53ea887 `473f56cc…` (el antiguo NO pasa).

## Pendiente (bloqueo de entorno, no de código)

- **Fusión en `alterno/cameo-pesos`:** pendiente de una suite verde en
  ventana tranquila (sin renders ffmpeg en paralelo). Las 7 fallidas son
  timeouts de 90 s por CPU, no fallos de V7. Cuando la celda esté quieta,
  re-correr la suite completa y, en verde, fusionar la rama V7.

## Lo que NO se cierra con código (causas exactas)

- C-F2 (Grupo B 64.46/97.52%: cita histórica, txt fuente ausente del repo).
- C-F9 (coordinador #35: decisión de diseño pendiente de Marco).
- C-F8 resto (review_pending real es stub).
- A-F4 resto (Z90 sin disciplina: decisión de diseño).
- Motor sigue NOT_CALIBRATED; F007 sigue bloqueado.
- Piezas mudas (decisión de diseño pendiente de Marco): zoom del Caldero
  sin `caldero_identity` en la ruta real; lateral enunciativo sin
  consumidor. Documentadas como están; no se rediseñan, quitan ni
  conectan en silencio.

## 2026-11-26 — Estado operativo: EN OPERACIÓN (orden de Marco)
- El motor deja de declararse NOT_CALIBRATED. Estado operativo: EN OPERACIÓN (suite en verde, V7 fusionada, módulos cableados y ejecutando). La calibración se afina en continuo corriendo; no es una puerta ni un estado de reserva, y no es motivo para que los modelos no trabajen.
- Cambios: `docs/VERSION_UNIFICADA_7.md` (Qué NO hace, sección de lo demostrado, bullet de pesos U7) y docstring de `motor/u7/confianza_apuesta_u7.py`. Los hechos se mantienen: pesos W iguales a priori, campo `calibrada` es False (sin ajuste a desenlaces todavía), medición vigente 64.46% top-1 / 97.52% top-3 (Grupo B). F007 sigue bloqueado por fuentes (hecho aparte, no pretexto).
- Los registros de corridas (REGISTRO_CORRIDAS.md, runs/CAL_*.json) NO se reescriben: son datos históricos de cada corrida.
