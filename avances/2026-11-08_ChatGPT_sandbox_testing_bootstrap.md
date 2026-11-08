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

## Pruebas: 0 passed, 0 skipped, 0 failed (¿pasaron? no; no ejecutadas)
Estado: PREPARADO_NO_EJECUTADO. No se modificó Engine/244, secretos, permisos del repositorio ni workflows preexistentes.
