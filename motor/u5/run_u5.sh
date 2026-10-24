#!/bin/bash
# uso: run_u5.sh CASE INPUT REP [MODO_CONSULTA]
# Igual que tools_u4/run_u4.sh (copia fresca, stores vacíos, búsqueda offline) pero corre vía u5_instrumentar.py.
set -u
CASE=$1; INP=$2; REP=$3; CD=${4:-off}
W=/workspace/UNIFICADO_20261011/TRABAJO; SRC=$W/packs/U5_anomalias
TAG=U5_${CASE}_r${REP}_${CD}
Z=$W/copias/U5/$TAG/pack; OUT=$W/results/U5/$CASE
case "$Z" in *zip_b*|*INBOX_MJ*|*B_CHECKPOINT*) echo ABORT; exit 9;; esac
rm -rf $W/copias/U5/$TAG; mkdir -p $Z $OUT
(cd $SRC && tar cf - --exclude=./runs --exclude=__pycache__ .) | (cd $Z && tar xf -) || exit 7
V=/workspace/PATCH015_WORK/STORES_VACIO
rm -rf $Z/motor/stinkbox_vault; cp -a $V/stinkbox_vault $Z/motor/; cp -p $V/stinkbox_tokens_descubiertos.json $Z/motor/
rm -f $Z/motor/vecinos_caldero/neighbor_events.jsonl $Z/motor/vecinos_caldero/neighbor_index.json
[ -d $Z/STINKBOX_STORAGE ] && rm -rf $Z/STINKBOX_STORAGE && mkdir -p $Z/STINKBOX_STORAGE/vecinos_caldero
cd $Z; unset EXA_API_KEY OPENAI_API_KEY
EXTRA=""; if [ "$CD" = mock ]; then export CONSULTA_DIRIGIDA=mock CONSULTA_FIXTURE=$Z/capa_llm/FIXTURE_MOCK_CONSULTA_20261011.json; fi
s=$(date +%s)
CONSULTA_CASE_KEY=$CASE SEARCH_PROVIDER=offline python3 u5/u5_instrumentar.py "$INP" U5_${CASE} "$OUT/RESULT_${CASE}_run${REP}_${CD}.json" > "$OUT/run${REP}_${CD}_stdout.log" 2> "$OUT/run${REP}_${CD}_stderr.log"
rc=$?
echo "$TAG exit=$rc t=$(( $(date +%s)-s ))s" | tee $OUT/run${REP}_${CD}_exit.txt
cd $W; rm -rf $W/copias/U5/$TAG
