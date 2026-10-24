#!/usr/bin/env python3
"""Caldero II genérico: runner independiente del caso Marco-16.

Entrada JSON:
{
  "case_id": "CASO",
  "archetype": {"tokens": [...], "patterns": [...], "families": [...]},
  "identity": {"name":..., "birth_date":..., "death_date":..., "unique_facts":[...]},
  "search_sources": [{"url":...,"title":...,"snippet":...}],
  "llm_neighbor_hints": [...]
}

La identidad solo se usa en self-match; la query Caldero es ciega.
No toca Engine, 244, P/A/C, FREEZE ni H1/H2.
"""
from __future__ import annotations
import argparse, importlib.util, json, sys
from pathlib import Path

BASE=Path(__file__).resolve().parent

def load(name, path):
    # U6 BUG FIX: registrar el módulo en sys.modules ANTES de ejecutarlo; sin esto @dataclass del sidecar falla
    # (AttributeError en dataclasses._is_type, Python 3.13) y el runner canónico no arrancaba.
    spec=importlib.util.spec_from_file_location(name,str(path)); mod=importlib.util.module_from_spec(spec); sys.modules[name]=mod; spec.loader.exec_module(mod); return mod

cal=load('caldero_sidecar', BASE/'sidecar_caldero_busqueda_arquetipos.py')
storemod=load('neighbor_store', BASE/'vecinos_caldero_neighbor_store.py')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('input',type=Path); ap.add_argument('--out',type=Path,default=None); ap.add_argument('--store',type=Path,default=BASE/'vecinos_caldero'); args=ap.parse_args()
    d=json.loads(args.input.read_text(encoding='utf-8'))
    case_id=str(d['case_id'])
    a=cal.ArchetypeInput(**(d.get('archetype') or {}))
    ident=cal.SelfMatchIdentity(**(d.get('identity') or {}))
    sources=[cal.SearchSource(**x) for x in (d.get('search_sources') or [])]
    side=cal.CalderoArchetypeSearchSidecar(cal.StaticSearchAdapter(sources),cal.SelfMatchFilter(ident))
    result=side.run(a)
    result['llm_neighbor_hints']=list(d.get('llm_neighbor_hints') or [])
    args.store.mkdir(parents=True,exist_ok=True)
    store=storemod.NeighborStore(args.store)
    ci=result['caldero_input']; audit=result['audit']
    persist=store.append(case_id=case_id,query=a.tokens and ' '.join(a.tokens) or audit.get('query_exact',''),tokens_neighbors=list(ci.get('tokens_neighbors') or []),audit_meta={'raw_sources':len(audit.get('raw_sources_before_self_match') or []),'discarded_self_match':len(audit.get('discarded_by_self_match') or []),'identity_exposed_to_caldero':False})
    result['persistence']={'status':'PERSISTED',**persist}
    result['case_id']=case_id; result['feeds_predictor']=True; result['feeds_H']=False; result['can_decide_H']=False
    text=json.dumps(result,ensure_ascii=False,indent=2)
    if args.out: args.out.write_text(text+'\n',encoding='utf-8')
    else: print(text)
if __name__=='__main__': main()
