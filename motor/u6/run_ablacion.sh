#!/bin/bash
# uso: run_ablacion.sh CASE CFG   (CFG: picos_off | frye_off | cuello_pos | todo_off)  — atribución de cambios U6 (sin instrumentar)
set -u
CASE=$1; CFG=$2; W=/workspace/UNIFICADO_20261011/TRABAJO; SRC=$W/packs/U6_correcciones
INP=$W/inputs_sellados/IN_${CASE}.json; TAG=ABL_${CFG}_${CASE}; Z=$W/copias/U6_ABL/$TAG/pack; OUT=$W/results/U6/_ABLACION/$CFG
rm -rf $W/copias/U6_ABL/$TAG; mkdir -p $Z $OUT
(cd $SRC && tar cf - --exclude=./runs --exclude=__pycache__ .) | (cd $Z && tar xf -) || exit 7
V=/workspace/PATCH015_WORK/STORES_VACIO
rm -rf $Z/motor/stinkbox_vault; cp -a $V/stinkbox_vault $Z/motor/; cp -p $V/stinkbox_tokens_descubiertos.json $Z/motor/
rm -f $Z/motor/vecinos_caldero/neighbor_events.jsonl $Z/motor/vecinos_caldero/neighbor_index.json
[ -d $Z/STINKBOX_STORAGE ] && rm -rf $Z/STINKBOX_STORAGE && mkdir -p $Z/STINKBOX_STORAGE/vecinos_caldero
cd $Z; unset EXA_API_KEY OPENAI_API_KEY
case $CFG in
 picos_off) export CONSOLIDADO_OFF=picos_score_u6;;
 frye_off) export CONSOLIDADO_OFF=frye_normalizado_u6;;
 cuello_pos) export U6_DESEMPATE_CUELLO=posicion;;
 solo_cuello) export CONSOLIDADO_OFF=picos_score_u6,frye_normalizado_u6;;
 solo_frye) export CONSOLIDADO_OFF=picos_score_u6 U6_DESEMPATE_CUELLO=posicion;;
 solo_picos) export CONSOLIDADO_OFF=frye_normalizado_u6 U6_DESEMPATE_CUELLO=posicion;;
 todo_off) export CONSOLIDADO_OFF=picos_score_u6,frye_normalizado_u6 U6_DESEMPATE_CUELLO=posicion;;
esac
SEARCH_PROVIDER=offline python3 correr_estandar.py "$INP" U6_${CASE} "$OUT/RESULT_${CASE}.json" > "$OUT/${CASE}_stdout.log" 2> "$OUT/${CASE}_stderr.log"
echo "$TAG exit=$?"; cd $W; rm -rf $W/copias/U6_ABL/$TAG
