#!/usr/bin/env bash
# Corre la línea base: 7 casos × FULL/PREFIX × 2 repeticiones + smokes. Uso: bash scripts/correr_todo.sh [--catalogo RUTA] [--puentes DIR]
set -euo pipefail
cd "$(dirname "$0")/.."
EXTRA=("$@")
python3 scripts/candados.py ANTES
for c in BEZOS G0924 G0926 GCAL JOBS M35A MUSK; do for m in FULL PREFIX; do for r in 1 2; do
  python3 scripts/orquestador_unico.py $c $m $r "${EXTRA[@]}"
done; done; done
python3 scripts/orquestador_unico.py GCAL FULL 1 --tag SMOKE_ESTRICTO0_FAMILIAS0 --env MODO_ESTRICTO=0 --env FAMILIAS_TOKENS=0 "${EXTRA[@]}"
python3 scripts/orquestador_unico.py MUSK PREFIX 1 --tag SMOKE_ESTRICTO0_FAMILIAS0 --env MODO_ESTRICTO=0 --env FAMILIAS_TOKENS=0 "${EXTRA[@]}"
python3 scripts/candados.py DESPUES
