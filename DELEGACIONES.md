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


## Seguimiento de órdenes reasignadas — 20-nov-2026, run operador

La orden permanente #465 continúa **PENDIENTE** en su objetivo principal: no se declaró ninguna corrida F007+ ni se incrementó n.

### Issue #64 — guardián Z90 en correr_estandar

- **Implementación propuesta en PR:** [PR #8](https://github.com/marcojpad-hash/motor-u6-storage/pull/8), rama `fix/issue-64-guardian-z90-correr-estandar`, head `5eda368d85851a42f6f82f069c56c93983c60da2`, destino `alterno/cameo-pesos`.
- **Evidencia:** check `runner-contract` SUCCESS, run [#43399816075](https://github.com/marcojpad-hash/motor-u6-storage/actions/runs/43399816075); ocho pruebas específicas declaradas en `motor/tests/test_guardian_z90_correr_estandar.py`.
- **Estado real:** PR abierto, sin merge; por tanto, el cableado no está integrado en esta rama. Además, el PR invoca la gate actual, que todavía no calcula Z90 desde nacimiento/muerte. Clasificación: **IMPLEMENTADO_EN_PR_NO_INTEGRADO; Z90_FUNCIONAL_INCOMPLETO**.

### Issue #49 — cortes variables y Z90

- El protocolo normativo ya existe en `motor/PROTOCOLO_BIOGRAFICO_Z90.md`.
- Se corrigieron en esta rama `casos/fabrica/README.md`, `casos/fabrica/PROMPT_SEMILLAS_Z.md`, `motor/CONTRATO_ENTRADA_LLM.txt`, `INSTRUCCIONES_CONTINUIDAD_CHATGPT.md` y el docstring de `motor/calibracion/gate_z90.py`.
- Se eliminó la regla documental de tres cortes fijos; se explicitó Z90, ventanas acumulativas desde nacimiento, primer corte en nacimiento, último en Z90, número variable y separación preparador/custodio.
- **Brecha pendiente:** la lógica de `validar_entrada()` aún no calcula Z90 ni verifica nacimiento/muerte, ventanas acumulativas o extremos de cortes. El docstring ahora lo declara expresamente. No se ejecutó el motor ni se afirmó cumplimiento de gate.

Commits documentales: `c9df16250741348a1ce4bdee0814164b97d98ead`, `c27ae38f2a4b003d3ff95b0a306c579de6778cba`, `45e4abd88882a96c36439990f8ef3b80ee93681a`, `5f52acbda3553be89b01d12ee99ad86116cffb30`, `4d2ea0a06437262b9e127f6bbbe4acb1892d9484`.

### Otras órdenes #36, #37, #38, #47, #48, #50 y #63

Siguen abiertas en el bus adicional `agente-cero-costo`. Se consultaron en solo lectura. No se modificó ese repositorio ni se atribuyó avance no verificado. Sus trabajos de supervisor, Cancerbero, consulta dirigida/vecinos, sidecar histórico, inputs humanos y consulta LLM obligatoria siguen fuera de la evidencia de cierre de este run.

