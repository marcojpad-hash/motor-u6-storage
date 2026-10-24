#!/usr/bin/env python3
"""
CALDERO_ZOOMOUT_ACERO_V0_1

Experimental lateral for V15.3.
Does NOT modify Engine V5, patterns 244, R732, H or FREEZE.

Idea under test:
  local transition trace (Caldero-scale)
      -> vector + speed/direction at each cut
      -> zoom OUT over the whole situation/query
      -> cumulative structural profile
      -> ACERO: a strong boundary/name for the currently surviving region
      -> next cut tests contraction/expansion of that region.

Important: this is NOT the canonical Caldero II implementation. It consumes
its available trajectory representation from a V15.3 result and explicitly
marks itself as an EXPERIMENTAL PROXY until the executable Caldero II artifact
is wired in.
"""
from __future__ import annotations
import argparse, hashlib, json, math
from pathlib import Path
from typing import Any


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cosine(a: dict[str,float], b: dict[str,float]) -> float:
    keys = set(a)|set(b)
    aa=sum(a.get(k,0.0)**2 for k in keys)
    bb=sum(b.get(k,0.0)**2 for k in keys)
    if aa==0 or bb==0: return 0.0
    return sum(a.get(k,0.0)*b.get(k,0.0) for k in keys)/(math.sqrt(aa)*math.sqrt(bb))


def movement_vectors(result: dict[str,Any]) -> list[dict[str,Any]]:
    traza=result.get('annex',{}).get('traza_P',{})
    out=[]
    for v in traza.get('vectores',[]):
        vec={m['h']:float(m['d']) for m in v.get('movimiento',[]) if float(m.get('d',0))!=0}
        out.append({'vector':v.get('vector'), 'n':v.get('n'), 'vec':vec})
    return out


def top_positive(vec: dict[str,float], k:int=5):
    return sorted(vec.items(), key=lambda x:(-x[1],x[0]))[:k]


def run(result: dict[str,Any], source: str) -> dict[str,Any]:
    moves=movement_vectors(result)
    # Cumulative structural direction. This is the zoom-out object.
    cumulative={}
    local=[]
    previous={}
    acero_names=[]
    for i,m in enumerate(moves):
        v=m['vec']
        speed=math.sqrt(sum(x*x for x in v.values()))
        direction=top_positive(v,5)
        for h,d in v.items(): cumulative[h]=cumulative.get(h,0.0)+d
        cum_speed=math.sqrt(sum(x*x for x in cumulative.values()))
        persistence=cosine(previous,v) if previous else None
        # ACERO: strongest cumulative positive structural signal at this scale.
        acero=top_positive(cumulative,3)
        # Boundary = retain only dimensions whose cumulative share is >= 20%
        # of the strongest positive cumulative coordinate. This is an
        # intentionally strong experimental boundary, not a canonical rule.
        maxv=acero[0][1] if acero else 0.0
        survivors=[h for h,d in sorted(cumulative.items(),key=lambda x:(-x[1],x[0]))
                   if d>=0.20*maxv and d>0]
        acero_name=acero[0][0] if acero else None
        acero_names.append(acero_name)
        local.append({
            'transition':m['vector'],
            'caldero_proxy':True,
            'speed_l2':speed,
            'direction_top5':direction,
            'persistence_vs_previous':persistence,
            'zoom_out_cumulative_top5':acero,
            'acero_name':acero_name,
            'acero_survivor_region':survivors,
            'acero_region_size':len(survivors),
            'interpretation':'LOCAL_TRANSITION' if i==0 else 'LOCAL_PLUS_ZOOM_OUT',
        })
        previous=v
    # Global trajectory: direction of cumulative displacement and contraction.
    global_top=top_positive(cumulative,10)
    return {
        'schema':'caldero_zoomout_acero_v0_1',
        'status':'EXPERIMENTAL_LATERAL',
        'source':source,
        'source_sha256':sha256(Path(source)),
        'canonical_modified':False,
        'engine_modified':False,
        'patterns_modified':False,
        'feeds_H':False,
        'freeze_modified':False,
        'caldero_status':'PROXY_FROM_V153_TRAZA_P_NOT_CALDERO_II_EXECUTION',
        'purpose':'test zoom-out from local transition vectorization into a situation-level trajectory and repeated strong ACERO boundaries',
        'acero_rule_v0_1':'name = strongest cumulative positive coordinate; survivor region = cumulative positive coordinates >=20% of strongest',
        'moves':local,
        'global_profile':{
            'n_transitions':len(moves),
            'cumulative_top10':global_top,
            'acero_name_sequence':acero_names,
            'final_acero_name':acero_names[-1] if acero_names else None,
            'final_region_size':local[-1]['acero_region_size'] if local else 0,
        },
        'limits':'No claim of predictive validity. This run tests whether repeated local vectors plus strong boundary labels produce a stable/constricting situation-level region.',
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('input')
    ap.add_argument('-o','--output',required=True)
    args=ap.parse_args()
    src=Path(args.input)
    result=json.loads(src.read_text(encoding='utf-8'))
    out=run(result,str(src))
    Path(args.output).write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({
        'output':args.output,
        'status':out['status'],
        'caldero_status':out['caldero_status'],
        'final_acero_name':out['global_profile']['final_acero_name'],
        'final_region_size':out['global_profile']['final_region_size'],
        'acero_name_sequence':out['global_profile']['acero_name_sequence'],
        'global_top10':out['global_profile']['cumulative_top10']
    },ensure_ascii=False,indent=2))

if __name__=='__main__': main()
