# 2026-11-08 — ChatGPT — sandbox-testing bootstrap

## Qué cambió
Preparación lateral de sandbox-testing. No se ejecutaron pruebas, workflows ni dispatches.

## Antes → ahora (por archivo / función)
- sandbox_runtime/runner_main.py — no había preflight lateral → runner fail-closed que valida schemas y repo/ref/SHA, bloquea con inventario incompleto.
- sandbox_runtime/contracts/sandbox-job-v1.schema.json — nuevo contrato tipado Draft 2020-12.
- sandbox_runtime/contracts/llm-bridge-response-v1.schema.json — nuevo contrato que impide que el LLM se autodeclare verificado.
- sandbox_runtime/policy/protected-paths.json — dos rutas conocidas; complete=false explícito.
- .github/workflows/sandbox-testing.yml — workflow manual, read-only, Ubuntu 24.04, sin secretos; no disparado.
- sandbox_runtime/source-manifest.json — refs y hashes observados.
- sandbox_runtime/execution-plan.json — plantilla con SHA placeholder; no apta para ejecución.

## Hashes canónicos verificados
Referencias documentales del MAPA_VERSIONES_Y_AUTORIDAD.md; no se recalcularon en esta fase:
- Engine V5: 665c39a2861e58772522e91272563260d980908b1d4ab9f7092d3413d0c36082.
- Catálogo 244: d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1.

## Pruebas locales controladas — 2026-11-08

Entorno real disponible: contenedor Linux (systemd-detect-virt = container-other), no una VM dedicada acreditada. Se ejecutó el runner localmente con los archivos del branch y el SHA de rama, sin dispatch.

- Intento 1: BLOQUEADO por incompatibilidad entre el schema estricto y dos propiedades de metadata incluidas en execution-plan.json (activation_status, execution_authorized). Se corrigió el plan en el branch eliminando esas propiedades ajenas al contrato.
- Intento 2: schemas y plan pasaron validación; resultado esperado BLOCKED porque protected-paths.json conserva complete=false. Exit code 2. Reporte: status=BLOCKED, reason=protected-path inventory incomplete; fail closed.
- Engine invocado: false. LLM llamado: false. Dispatch realizado: false.
- No se ejecutó smoke ni código del motor.

Esto prueba el comportamiento de bloqueo del preflight, no acredita ejecución de motor ni aislamiento VM. Estado: PREPARACIÓN + PREFLIGHT LOCAL EJECUTADO Y BLOQUEADO POR DISEÑO. No se modificó Engine/244, secretos, permisos del repositorio ni workflows preexistentes.
