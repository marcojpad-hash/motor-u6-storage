#!/bin/bash
# uso: run_u5.sh CASE INPUT REP [MODO_CONSULTA]
# U6: igual que u5/run_u5.sh (copia fresca, stores vacíos, búsqueda offline, vía u5_instrumentar.py) pero sobre el pack U6.
set -u
CASE=$1; INP=$2; REP=$3; CD=${4:-off}
W=/workspace/UNIFICADO_20261011/TRABAJO; SRC=$W/packs/U6_correcciones
TAG=U6_${CASE}_r${REP}_${CD}
Z=$W/copias/U6/$TAG/pack; OUT=$W/results/U6/$CASE
case "$Z" in *zip_b*|*INBOX_MJ*|*B_CHECKPOINT*) echo ABORT; exit 9;; esac
rm -rf $W/copias/U6/$TAG; mkdir -p $Z $OUT
(cd $SRC && tar cf - --exclude=./runs --exclude=__pycache__ .) | (cd $Z && tar xf -) || exit 7
# U6_UNIFICADO_20261020: memoria/ (ledger append-only del sidecar_latentes) NO se pierde al borrar la copia.
MEMORIA_PERSISTENTE=${MEMORIA_PERSISTENTE:-$W/MEMORIA_PERSISTENTE}
mkdir -p "$MEMORIA_PERSISTENTE" $Z/memoria
cp -a "$MEMORIA_PERSISTENTE"/. $Z/memoria/ 2>/dev/null || true
V=/workspace/PATCH015_WORK/STORES_VACIO
rm -rf $Z/motor/stinkbox_vault; cp -a $V/stinkbox_vault $Z/motor/; cp -p $V/stinkbox_tokens_descubiertos.json $Z/motor/
rm -f $Z/motor/vecinos_caldero/neighbor_events.jsonl $Z/motor/vecinos_caldero/neighbor_index.json
[ -d $Z/STINKBOX_STORAGE ] && rm -rf $Z/STINKBOX_STORAGE && mkdir -p $Z/STINKBOX_STORAGE/vecinos_caldero
cd $Z; unset EXA_API_KEY OPENAI_API_KEY
EXTRA=""; if [ "$CD" = mock ]; then export CONSULTA_DIRIGIDA=mock CONSULTA_FIXTURE=$Z/capa_llm/FIXTURE_MOCK_CONSULTA_20261011.json; fi
s=$(date +%s)
CONSULTA_CASE_KEY=$CASE SEARCH_PROVIDER=offline python3 u5/u5_instrumentar.py "$INP" U6_${CASE} "$OUT/RESULT_${CASE}_run${REP}_${CD}.json" > "$OUT/run${REP}_${CD}_stdout.log" 2> "$OUT/run${REP}_${CD}_stderr.log"
rc=$?
echo "$TAG exit=$rc t=$(( $(date +%s)-s ))s" | tee $OUT/run${REP}_${CD}_exit.txt
# devolver memoria/ (solo añade/actualiza; nunca borra lo que ya había) antes de borrar la copia
cp -a $Z/memoria/. "$MEMORIA_PERSISTENTE"/ 2>/dev/null || true
cd $W; rm -rf $W/copias/U6/$TAG
