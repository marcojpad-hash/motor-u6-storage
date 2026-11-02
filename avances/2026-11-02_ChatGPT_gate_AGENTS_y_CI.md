# 2026-11-02 — ChatGPT — gate AGENTS y CI de arranque

## Qué cambió
Se añadió una instrucción de repositorio específica para ChatGPT Codex y un workflow de GitHub Actions que valida la presencia y referencias mínimas de los documentos obligatorios de arranque. Esto cubre el agente Codex compatible con AGENTS.md y valida el contrato documental en GitHub Actions. No convierte una conversación normal de ChatGPT en Codex ni garantiza que esta interfaz cargue AGENTS.md automáticamente.

## Antes → ahora (por archivo / función)
- `AGENTS.md` — antes no había instrucciones de repositorio en el formato reconocido por agentes Codex; ahora contiene el gate de lectura, ejecución, evidencia, protección canónica y respuesta.
  blob SHA antes: N/A | blob SHA después: `0f7940d0b815bbcf76a4458a409ffcd4c792e6fa`
- `.github/workflows/chatgpt-startup-contract.yml` — antes no había un workflow específico que comprobara los documentos de arranque ChatGPT; ahora se ejecuta en push a main, pull requests que toquen esos documentos y manualmente. Comprueba existencia y referencias obligatorias.
  blob SHA antes: N/A | commit que lo incorpora: `a99dff483eef4441b0ffd4f000d9f4dd81abd301`

## Hashes canónicos verificados (motor y catálogo)
No se recalcularon en esta intervención; no se modificaron.

## Pruebas: 0 passed, 0 skipped, 0 failed (¿pasaron? pendiente)
GitHub Actions creó el run `41423482337`, evento push, workflow `ChatGPT startup contract`, commit `a99dff483eef4441b0ffd4f000d9f4dd81abd301`. Al momento de esta entrada el run estaba QUEUED; no se declara PASS.
