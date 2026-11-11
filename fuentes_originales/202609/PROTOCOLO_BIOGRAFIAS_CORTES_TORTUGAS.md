# PROTOCOLO — Biografías por cortes + tortugas (uso operativo Grok Bot)

Alineado con PROTOCOLO ESTUDIOS V15.1 (trazabilidad/inercia/P1-P2), aplicado a bios.

## 1. Marco
- Motor preferido para bios ciegas: `MOTOR_V15_1_10CORTES_LIMPIO.py` (hash candado `48333cd11b9234f1`, M=0.998).
- Base intacta: Engine_V5 + `patterns_final_v14.json` (244). No inventar tokens.
- Pregunta = marco de la foto (define qué tokens se empiezan a prender).

## 2. Z_foto
- Default: **Z = 90% de la vida** (queda ~10% de lifespan). No usar “10 años antes” salvo que lo pidas.
- Post-Z **sellado** hasta inversa.

## 3. Secuencia
1. Armar cuts nacimiento→Z (hechos + P/A/C con tokens válidos).
2. Correr limpio (`correr_5x3`).
3. Leer campo completo: reporte_3d (H/se_movieron/no_se_apagaron), top5 anexo, R732 (dX, persist_cos, kappa_dir).
4. Congelar Alfa/Beta de **rumbo** (investigador). Prohibido H1=max(board).
5. Si el estudio es prospectivo corte-a-corte: SALIDA MÍNIMA del protocolo completo (P1/P2, apuesta, validación, ingeniería inversa) — ver `PROTOCOLO_ESTUDIOS_V15_1_...`.
6. Inversa post-Z solo cuando abras el sello.

## 4. Tortugas (uso que nos funcionó)
**Tortugas ≠ veredicto.** = resolución insuficiente para congelar certeza/%.

Señales típicas en Z:
- `persist_cos` ≈ 0 (o muy bajo)
- `kappa_dir` ≈ 1 (piso / ruido)
- empates a 3 en candidatos (misma p tras round)

Qué hacer:
- Reportar TORTUGAS con los números.
- Conservar Alfa/Beta de rumbo.
- **No** inventar freeze kappa, familia nueva, ni fuerza.
- Si hace falta nitidez: subdividir el **mismo** texto en cortes más finos y remedir (no inventar hechos).

## 5. Luces vs protocolo completo
- **Mapa de luces:** rápido para inventariar (qué se prendió: sacrificio, f2, monomito…).
- **Protocolo completo:** trazabilidad (qué se podía decir *antes* del siguiente corte).
Pipeline: luces → si importa → protocolo completo.

## 6. Sidecars / laterales
No mezclar salidas de Caldero B / monomito / pregunta_dirigida con el tablero limpio sin etiquetar.
Aquiles OFF en limpio; si se enciende, es traza de picos/mesetas, no veredicto.

## 7. Entrega a Cloud
Pocos archivos densos: markers + reporte + PARA_CLOUD.txt + (si aplica) PROTOCOLO_POR_CORTE.
Marcar FALTANTE / NO_VERIFICADO / RECONSTRUIDO cuando falte algo.
