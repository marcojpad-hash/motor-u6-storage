#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, sys
ROOT=Path(__file__).resolve().parents[1]
ENGINE=ROOT/'motor/Engine_V5_CANONICO_SOLO.py'
PAT=ROOT/'motor/patterns_final_v14.json'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    rows=[]; anomalies=[]
    for pat in ('Engine_V5_CANONICO_SOLO*.py','patterns_final_v14.json','MOTOR_V15_3_UNICO_20260927.py','MOTOR_V15_3_NATIVO_V0_9_UNICO.py'):
        for p in ROOT.rglob(pat):
            if p.is_file() and 'runs' not in p.relative_to(ROOT).parts: rows.append((p.name,str(p.relative_to(ROOT)),sha(p),p.stat().st_size))
    by={}
    for name,path,h,b in rows:
        key='Engine_V5_CANONICO_SOLO.py' if name.startswith('Engine_V5_CANONICO_SOLO') and name.endswith('.py') else name
        by.setdefault(key,[]).append({'path':path,'name':name,'sha256':h,'bytes':b})
    for name,copies in by.items():
        if name == 'Engine_V5_CANONICO_SOLO.py' and len(copies) != 1:
            anomalies.append({'type':'DUPLICATE_CRITICAL_ARTIFACT_MULTIPLE_COPIES','name':name,'copies':copies})
        elif len({x['sha256'] for x in copies})>1:
            anomalies.append({'type':'DUPLICATE_CRITICAL_ARTIFACT_DIFFERENT_HASH','name':name,'copies':copies})
    expected='665c39a2861e58772522e91272563260d980908b1d4ab9f7092d3413d0c36082'
    if not ENGINE.is_file() or sha(ENGINE)!=expected:
        anomalies.append({'type':'AUTHORIZED_ENGINE_HASH_MISMATCH','path':str(ENGINE),'sha256':sha(ENGINE) if ENGINE.is_file() else None})
    out={'ok':not anomalies,'engine':{'path':str(ENGINE),'sha256':sha(ENGINE) if ENGINE.is_file() else None},'patterns_sha256':sha(PAT) if PAT.is_file() else None,'anomalies':anomalies,'files':rows}
    print(json.dumps(out,ensure_ascii=False,indent=2))
    return 0 if out['ok'] else 1
if __name__=='__main__': sys.exit(main())
