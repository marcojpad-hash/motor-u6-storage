# 2026-10-24 — Grok Bot (Puta 3): Calibración Lote 01

Se agregaron solo resúmenes livianos: H1, H2, apuesta, grado, margen y hashes. No se subieron corridas completas.
No hubo cambios de código. Engine `665c39a2…` y patrones `d827dcc3…` verificados OK con `sincronizar_storage.py antes`.

## Antes → ahora
- `casos/resultados/resultados.jsonl`: antes, sha256 `d65d78fffef6ab7d2046863220552b1c276f634ed688f9f14e131d71df020ab1` → ahora, sha256 `17da79a840fbda82d607267ddc13ba9cc5a987db4eb9e1ef1b41a5058ca4dd3c`. Se agregaron 9 resúmenes, CAL_LOTE01_01…10, sin el 06; un commit por caso vía `sincronizar_storage.py despues`.
- `casos/calibracion/LOTE_01_RESUMEN.json`: antes, no existía → ahora, sha256 `f0e2fd645f1499eac34db814a3a6e4a2437d76be9f3e17572cc3c4d4d39de4ed`.
- `stinkbox/tokens.jsonl`: sin cambio, sha256 `9afb61446d27…`. Hubo 0 observaciones nuevas.

## Resultado
- Casos sellados: 9 de 10. Beethoven quedó en exit 6 (pausa TORTUGAS): no se selló ni se reanudó.
- Acierto H1: 2 de 9 (Semmelweis y Ford).
- Brier LOO-Laplace, recortado 5–95 %: 0,2122.
- Brier diagnóstico del soporte de hipótesis: 0,1270.
- Informe completo: `/workspace/MOTOR_1019/CALIBRACION_LOTE_01/INFORME.md` (en el box).
