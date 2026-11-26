# 2026-11-26 — ChatGPT — correcciones del workflow de regresión U7

## Qué cambió

Se completó la corrección del selector de casos en el workflow exploratorio después de revisar el YAML resultante. Se corrigieron dos detalles de ejecución que impedían considerar validado el disparo: el commit anterior se obtiene del payload `github.event.before` (no de una variable de entorno inexistente), y el checkout descarga el historial completo para que `git diff` pueda comparar ambos commits. También se aseguró la copia del ledger CEB al artefacto.

## Antes → ahora

- `.github/workflows/ejecutar-caso-exploratorio-u7.yml`:
  - Antes: referenciaba `GITHUB_EVENT_BEFORE`, que no es una variable estándar de GitHub Actions.
  - Ahora: recibe `EVENT_BEFORE: ${{ github.event.before }}` en el entorno del paso.
  - Antes: checkout shallow, sin garantía de que el commit anterior estuviera disponible para `git diff`.
  - Ahora: `fetch-depth: 0`.
  - Antes: el artefacto no conservaba el ledger CEB.
  - Ahora: copia `motor/RESULT_<CASE_ID>_CEB_LEDGER_*.jsonl` junto con entrada, resultado, recibo y manifiestos.
- Git blob SHA previo: `1887662b4a0766e65d87e82022bb0d21c091df39`
- Git blob SHA actual: `e6a38fc08733de8979f660934e7ad41c225a1c94`
- Commit: `552291bf9def84fa7e42ee318a32ed78f433aab0`

## Pruebas

- Lectura posterior del YAML: confirmadas las referencias a `EVENT_BEFORE`, `fetch-depth: 0`, selección de un único JSON modificado, regeneración/persistencia de manifiestos y copia del ledger CEB.
- No se declara ejecución de Actions ni corrección de CEB confirmadas hasta inspeccionar el artefacto de la corrida de regresión posterior a este commit.
