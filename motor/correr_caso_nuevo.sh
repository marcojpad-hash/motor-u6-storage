#!/usr/bin/env bash
# Uso: ./correr_caso_nuevo.sh INPUT.json NOMBRE   -> SALIDAS/RESULT_NOMBRE.json (+ _RECIBO_EJECUCION.json)
# Adaptado de TIRADA a esta copia: llama a correr_estandar.py (no existe laterales_unificado/ aquí).
# Sin GEOMETRIA_PESO: este motor no expone ese peso. Búsqueda agnóstica viva por defecto (CALDERO_BUSQUEDA_VIVA=0 la apaga).
# Códigos de salida: 0 COMPLETED · 5 COMPLETED_WITH_METADATA_GAP · 6 PAUSADA_REANUDABLE (ver scripts/reanudar_desde_checkpoint.py) · 3/4 error.
set -u; IN="$(realpath "$1")"; D="$(cd "$(dirname "$0")" && pwd)"; cd "$D"; mkdir -p "$D/SALIDAS"
env -u STINKBOX_HOME CALDERO_BUSQUEDA_VIVA="${CALDERO_BUSQUEDA_VIVA:-1}" CALDERO_BUSCADOR="${CALDERO_BUSCADOR:-auto}" \
  FAMILIAS_TOKENS="${FAMILIAS_TOKENS:-1}" MODO_ESTRICTO="${MODO_ESTRICTO:-1}" CONSULTA_DIRIGIDA="${CONSULTA_DIRIGIDA:-offline}" \
  python3 -B correr_estandar.py "$IN" "$2" "$D/SALIDAS/RESULT_$2.json"
rc=$?; echo "exit=$rc"; exit $rc
