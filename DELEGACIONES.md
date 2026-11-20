# Delegaciones Motor U6

Tablero vivo del callback del motor. Quien delega escribe aquí. Quien recibe lee aquí.

Este tablero es del Motor U6 (repo `motor-u6-storage`, rama de trabajo `alterno/cameo-pesos`). El motor es un proyecto aparte y no lleva delegaciones en el tablero de CAPCOT (`capcot-capsulas-imaginantes/ajustes_entre_modelos/DELEGACIONES.md`), que lo dice así expresamente. Las órdenes por el bus viven como issues "[BUS] indicacion - <modelo>" en `agente-cero-costo`; este tablero es el espejo legible en el repo del motor.

Reglas: protocolo de ejecución y lectura en `PROTOCOLO_EJECUCION_Y_LECTURA_LLM.md`; arranque en `INICIO_SESION_CHATGPT.md`; custodia independiente; gate Z90 vigente; no tocar Engine V5 ni patterns 244; no calibrar con n=1; PRs sin fusionar sin Marco.

## Pendientes

### 1. Orden permanente — corridas diarias del Motor U6 por ChatGPT
- DE: Pecas (por orden de Marco, dueño, 2026-11-16)
- PARA: ChatGPT (cuenta marco.jp@live.com.mx)
- QUÉ: ejecutar ejercicios/corridas del Motor U6, meta ~30 corridas/día de casos NUEVOS e independientes asignados por el protocolo (lotes nuevos F007+), con reporte por corrida en el repo; preparar la verificación de la cohorte C01–C20 sin abrir la custodia (la abre Pecas); además búsqueda/investigación/programación cuando se pida por la misma vía. Sin cambiar pesos, sin tocar Engine V5 ni el catálogo de 244, sin declarar calibración, con custodia independiente y gate Z90 vigente. Retoma las órdenes abiertas de la reasignación Grok→ChatGPT del 2026-11-12: #36, #37, #38, #47, #48, #49, #50, #63, #64.
- ORDEN: issue "[BUS] indicacion - ChatGPT" en `agente-cero-costo`, #465 — https://github.com/marcojpad-hash/agente-cero-costo/issues/465
- PARA CUÁNDO: permanente, desde 2026-11-16; acuse diario al cierre del día
- ESTADO: PENDIENTE
- NOTA: C01–C20 ya están corridos (lote_20, 2026-11-08); no re-correrlos para inflar n. Fecha blanda: créditos ChatGPT caducan ~2026-11-24 (sin verificar). Límite honesto: el cuello de botella es la preparación de casos nuevos con fuentes y custodia, no la ejecución (~14–23 s por corrida).

## En progreso

(nada)

## Hechas

(nada)


## Seguimiento ChatGPT — 2026-11-20

La orden permanente del issue agente-cero-costo #465 sigue **PENDIENTE** en su objetivo principal de corridas nuevas e independientes. No se declara corrida nueva ni se incrementa n.

- Se preparó la tabla de predicciones congeladas C01–C20 en `casos/ciegos/lote_20/PREPARACION_UNBLINDING_CHATGPT.md` (commit `2668a0b9fd8419cbc6c8c3b9a0199dae61afd6a3`; lectura de vuelta blob `4366c717fd340112eadd52a343152fa3ae0dbc55`). Contiene 20/20 slots, H1/H2, escenario y destino personal predicho desde `SALIDA_CONGELADA.json`. **No se leyó `custodia/`, no se consultaron desenlaces y no se calculó HIT/MISS.** El unblinding sigue reservado a Pecas/custodio independiente.
- Revisión de F007: `semillas_lote_F007.py` contiene ocho sujetos con dos cortes por sujeto y referencias secundarias de Wikipedia; `destinos_lote_F007.py` lo identifica como ensayo metodológico del mismo actor. No acredita independencia de custodia ni un lote F007 preparado; la cola de fábrica visible contiene solo F001–F005. No se ejecutó ni se contó como casos independientes.
- Siguiente operación válida: preparar sujetos nuevos con fuentes primarias y cortes Z verificables; enviar el material de destino a custodio independiente; solo después ejecutar runner real y guardar RESULT/RECIBO/CEB/manifiesto. No reejecutar C01–C20.
