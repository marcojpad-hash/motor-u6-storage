#!/usr/bin/env python3
"""Append-only registry for StinkBox tokens, independent from motor ZIPs."""
from __future__ import annotations
import argparse, csv, hashlib, json, re, zipfile, os
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
# Store state outside motor ZIPs. A standalone copy inside the persistent folder
# uses its own data directory; a copy embedded in U6 uses STINKBOX_HOME or user home.
if os.environ.get('STINKBOX_HOME'):
    STORE_ROOT = Path(os.environ['STINKBOX_HOME']).expanduser()
elif (ROOT / 'data' / 'registro_tokens.json').is_file():
    STORE_ROOT = ROOT
else:
    STORE_ROOT = Path.home() / 'STINKBOX_PERSISTENTE'
DATA = STORE_ROOT / 'data'
REPORTS = STORE_ROOT / 'reports'
REGISTRY = DATA / 'registro_tokens.json'
EVENTS = DATA / 'eventos_tokens.jsonl'
ARTIFACTS = DATA / 'artefactos_importados.json'


def utcnow(): return datetime.now(timezone.utc).isoformat()
def sha(b: bytes): return hashlib.sha256(b).hexdigest()
def norm(s): return re.sub(r'\s+', ' ', str(s or '').strip()).casefold()
def load_json_bytes(b):
    try: return json.loads(b.decode('utf-8-sig'))
    except Exception: return None

def read_registry():
    if REGISTRY.exists(): return json.loads(REGISTRY.read_text(encoding='utf-8'))
    return {'schema':'stinkbox_token_registry_v1','created_utc':utcnow(),'updated_utc':utcnow(),'tokens':{}}
def read_artifacts():
    if ARTIFACTS.exists(): return json.loads(ARTIFACTS.read_text(encoding='utf-8'))
    return {'schema':'stinkbox_artifacts_v1','artifacts':{}}
def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix+'.tmp')
    tmp.write_text(json.dumps(obj,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    tmp.replace(path)
def event_id(e):
    fields = [e.get('case_id'),e.get('cut_id'),e.get('token_norm'),e.get('source'),e.get('kind'),e.get('timestamp')]
    return sha(json.dumps(fields,ensure_ascii=False,separators=(',',':')).encode())

def walk_artifacts(source: Path):
    """Yield (label, bytes) for relevant JSON files in a folder or ZIP."""
    if source.is_file() and zipfile.is_zipfile(source):
        with zipfile.ZipFile(source) as z:
            for n in z.namelist():
                low=n.lower()
                if not low.endswith('.json'): continue
                if ('stinkbox_storage/stinkbox_' in low or low.endswith('/stinkbox_tokens_descubiertos.json') or low.endswith('/neighbor_index.json')):
                    try: yield f'{source.name}!/{n}', z.read(n)
                    except Exception: pass
    elif source.is_file() and source.suffix.lower()=='.json':
        yield str(source), source.read_bytes()
    elif source.is_dir():
        for p in source.rglob('*.json'):
            low=str(p).lower().replace('\\','/')
            if ('stinkbox_storage/stinkbox_' in low or 'stinkbox_tokens_descubiertos.json' in low or low.endswith('/neighbor_index.json')):
                try: yield str(p), p.read_bytes()
                except Exception: pass

def token_event(token, case_id, cut_id=None, source=None, kind=None, timestamp=None, axis=None, status=None, artifact=None):
    t=norm(token)
    if not t: return None
    return {'token_norm':t,'token_original':str(token).strip(),'case_id':str(case_id or 'CASO_DESCONOCIDO'),
            'cut_id':str(cut_id or ''),'source':str(source or 'fuente_no_especificada'),'kind':str(kind or 'observado'),
            'timestamp':str(timestamp or ''),'axis':str(axis or ''),'explicit_status':str(status or ''),'artifact':artifact or ''}

def extract(label, raw, obj):
    out=[]
    if not isinstance(obj,dict): return out
    digest=sha(raw); base={'artifact':label,'artifact_sha256':digest}
    # Dedicated discovery register: strongest signal for outside-catalog candidates.
    if isinstance(obj.get('tokens'),list) and ('stinkbox_tokens_descubiertos' in label.lower()):
        for x in obj['tokens']:
            if not isinstance(x,dict): continue
            out.append(token_event(x.get('token'),x.get('case_id'),x.get('corte'), 'stinkbox_tokens_descubiertos', 'fuera_catalogo', x.get('timestamp'), x.get('eje'), x.get('estado'), label))
    # Case-local StinkBox schema.
    case_id=obj.get('case_id')
    if case_id and isinstance(obj.get('token_events'),list):
        for x in obj['token_events']:
            if isinstance(x,dict): out.append(token_event(x.get('token'),case_id,x.get('cut_id'),x.get('source'),x.get('kind'),x.get('timestamp'),artifact=label))
    if case_id and isinstance(obj.get('token_frequency'),dict):
        seen={e['token_norm'] for e in out}
        for t,count in obj['token_frequency'].items():
            if norm(t) not in seen:
                out.append(token_event(t,case_id,source='token_frequency_snapshot',kind=f'frequency_snapshot:{count}',timestamp=obj.get('updated_at'),artifact=label))
    if case_id and isinstance(obj.get('persistent_neighbor_tokens'),list):
        for t in obj['persistent_neighbor_tokens']:
            out.append(token_event(t,case_id,source='persistent_neighbor_tokens',kind='neighbor_memory',timestamp=obj.get('updated_at'),artifact=label))
    if case_id and isinstance(obj.get('resolved_front_history'),list):
        for rec in obj['resolved_front_history']:
            if not isinstance(rec,dict): continue
            for t in rec.get('tokens_signature') or []:
                out.append(token_event(t,case_id,rec.get('cut_id'),'resolved_front_history','tokens_signature',artifact=label))
    # Caldero neighbor index.
    if 'neighbor_index.json' in label.lower() and isinstance(obj.get('neighbors'),dict):
        for t,rec in obj['neighbors'].items():
            rec=rec if isinstance(rec,dict) else {}
            for c in rec.get('cases') or ['CASO_NO_ESPECIFICADO']:
                out.append(token_event(t,c,source='vecinos_caldero.neighbor_index',kind='neighbor_index',timestamp=rec.get('first_seen_utc'),artifact=label))
    # Preserve explicit outside-catalog statuses if this is an embedded discovery file.
    return [e for e in out if e and e['token_norm']]

def ensure_event_log_ids():
    ids=set()
    if EVENTS.exists():
        with EVENTS.open(encoding='utf-8') as f:
            for line in f:
                try: ids.add(json.loads(line)['event_id'])
                except Exception: continue
    return ids

def ingest(source):
    source=Path(source).expanduser().resolve()
    if not source.exists(): raise SystemExit(f'No existe la ruta: {source}')
    reg=read_registry(); art=read_artifacts(); known_art=art['artifacts']; ids=ensure_event_log_ids()
    n_art=0; n_event=0; n_new=0; n_candidates=0; skipped=0
    for label, raw in walk_artifacts(source):
        digest=sha(raw); artifact_key=digest
        if artifact_key in known_art:
            skipped+=1; continue
        obj=load_json_bytes(raw)
        extracted=extract(label,raw,obj)
        now=utcnow()
        known_art[artifact_key]={'label':label,'sha256':digest,'bytes':len(raw),'imported_utc':now,'events_extracted':len(extracted)}
        n_art+=1
        for e in extracted:
            eid=event_id(e)
            if eid in ids: continue
            ids.add(eid); e['event_id']=eid; e['observed_utc']=now; e['artifact_sha256']=digest
            EVENTS.parent.mkdir(parents=True,exist_ok=True)
            with EVENTS.open('a',encoding='utf-8') as f: f.write(json.dumps(e,ensure_ascii=False,separators=(',',':'))+'\n')
            n_event+=1
            t=e['token_norm']; rec=reg['tokens'].get(t)
            if rec is None:
                rec={'token':t,'first_seen_utc':now,'last_seen_utc':now,'status':'NUEVO','introduced_after_baseline':True,'observations':0,'evidence_events':0,'occurrence_ids':[],'cases':[],'cuts':[],'sources':[],'kinds':[],'axes':[],'artifacts':[],'explicit_statuses':[],'event_ids':[]}
                reg['tokens'][t]=rec; n_new+=1
            rec['last_seen_utc']=now
            rec['evidence_events']=int(rec.get('evidence_events', rec.get('observations', 0)))+1
            occurrence_cut=e['cut_id']
            prefix=e['case_id']+'::'
            if occurrence_cut.startswith(prefix): occurrence_cut=occurrence_cut[len(prefix):]
            occurrence_id=sha(json.dumps([e['case_id'],occurrence_cut,e['token_norm']],ensure_ascii=False,separators=(',',':')).encode())
            occurrence_ids=rec.setdefault('occurrence_ids',[])
            if occurrence_id not in occurrence_ids:
                occurrence_ids.append(occurrence_id); rec['observations']=int(rec.get('observations',0))+1
            for field,val in [('cases',e['case_id']),('cuts',e['cut_id']),('sources',e['source']),('kinds',e['kind']),('axes',e['axis']),('artifacts',label),('explicit_statuses',e['explicit_status'])]:
                if val and val not in rec[field]: rec[field].append(val)
            rec['event_ids'].append(eid)
            if e['explicit_status'] in ('PENDIENTE_REVISION','FAMILIA_CANDIDATA','EQUIVALENTE_UNICO','DESCARTADO_CONSERVADO'):
                rec['status']=e['explicit_status']; n_candidates+=1
            elif len(rec['cases'])>1 and rec['status']=='NUEVO': rec['status']='RECURRENTE'
    reg['updated_utc']=utcnow(); write_json(REGISTRY,reg); write_json(ARTIFACTS,art)
    report()
    print(json.dumps({'status':'OK','source':str(source),'artifacts_imported':n_art,'artifacts_skipped_same_sha':skipped,'new_event_records':n_event,'new_token_strings':n_new,'explicit_review_observations':n_candidates,'unique_tokens_total':len(reg['tokens'])},ensure_ascii=False,indent=2))

def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore'); w.writeheader()
        for r in rows:
            row={}
            for k in fields:
                value=r.get(k, '')
                if k=='evidence_events' and value=='': value=r.get('observations', 0)
                row[k]='; '.join(map(str,value)) if isinstance(value,list) else value
            w.writerow(row)

def sync_documentary_candidates():
    """Keep literature-derived family proposals separate from observed run tokens."""
    candidates_source = ROOT / 'STINKBOX_BLACK_MIRROR_CANDIDATOS.json'
    if not candidates_source.is_file():
        candidates_source = STORE_ROOT / 'STINKBOX_BLACK_MIRROR_CANDIDATOS.json'
    target = DATA / 'familias_candidatas_documentales.json'
    if candidates_source.is_file() and not target.is_file():
        DATA.mkdir(parents=True, exist_ok=True)
        target.write_bytes(candidates_source.read_bytes())
    if not target.is_file():
        return 0
    try:
        doc=json.loads(target.read_text(encoding='utf-8'))
        candidates=doc.get('candidates') or []
    except Exception:
        return 0
    REPORTS.mkdir(parents=True,exist_ok=True)
    fields=['token','registry_status','documentary_status','definition','mapping_244','sources','integrated_into_motor','must_not_count_as_observed_token','notes']
    write_csv(REPORTS/'familias_candidatas_documentales.csv', candidates, fields)
    return len(candidates)

def report():
    reg=read_registry(); rows=list(reg['tokens'].values())
    documentary_candidates=sync_documentary_candidates()
    REPORTS.mkdir(parents=True,exist_ok=True)
    fields=['token','status','observations','evidence_events','cases','cuts','sources','kinds','axes','first_seen_utc','last_seen_utc','explicit_statuses','artifacts']
    write_csv(REPORTS/'tokens_nuevos.csv',[r for r in rows if r.get('introduced_after_baseline',False)],fields)
    write_csv(REPORTS/'tokens_fuera_catalogo.csv',[r for r in rows if any(k in ('fuera_catalogo','PENDIENTE_REVISION','FAMILIA_CANDIDATA') for k in r.get('kinds',[])) or r.get('status') in ('PENDIENTE_REVISION','FAMILIA_CANDIDATA')],fields)
    write_csv(REPORTS/'tokens_recurrentes.csv',[r for r in rows if len(r.get('cases',[]))>1 or r.get('status')=='RECURRENTE'],fields)
    external_vocab=[r for r in rows if 'lateral_features' in (r.get('sources') or []) and 'external' in (r.get('kinds') or []) and not (r.get('explicit_statuses') or [])]
    write_csv(REPORTS/'tokens_vocabulario_externo.csv',external_vocab,fields)
    art=read_artifacts()['artifacts']
    lines=['# Resumen del registro persistente StinkBox','',f'- Actualizado: {reg.get("updated_utc","")}',f'- Tokens únicos registrados: {len(rows)}',f'- Artefactos importados (SHA-256 únicos): {len(art)}',f'- Tokens de línea base histórica: {sum(r.get("status")=="LINEA_BASE" for r in rows)}',f'- Tokens nuevos desde la línea base: {sum(bool(r.get("introduced_after_baseline",False)) for r in rows)}',f'- Tokens nuevos asociados a vocabulario externo (no son familias por sí solos): {sum(bool(r.get("introduced_after_baseline",False)) and r in external_vocab for r in rows)}',f'- Tokens observados en más de un caso: {sum(len(r.get("cases",[]))>1 for r in rows)}',f'- Tokens con señal explícita de revisión: {sum(bool(r.get("explicit_statuses")) for r in rows)}',f'- Candidatos documentales separados (no observados en corridas): {documentary_candidates}','', '## Interpretación', 'Un token nuevo es nuevo para este registro persistente, no necesariamente un arquetipo nuevo. El vocabulario extraído de fuentes externas se lista por separado y no equivale a una familia faltante. Solo los hallazgos explícitos fuera de catálogo y las recurrencias con contexto/cortes deben entrar a revisión de familias.', '', '## Archivos maestros', '- `data/registro_tokens.json`: índice acumulado.', '- `data/eventos_tokens.jsonl`: eventos deduplicados.', '- `data/artefactos_importados.json`: SHA-256 de artefactos importados.', '- `reports/*.csv`: vistas derivadas; se pueden regenerar.', '- `reports/tokens_vocabulario_externo.csv`: términos de fuentes externas, separados de hallazgos fuera de catálogo.', '- `data/familias_candidatas_documentales.json`: candidatos de fuentes documentales, separados de tokens observados.', '- `reports/familias_candidatas_documentales.csv`: lista de familias candidatas para revisar/cablear.']
    (REPORTS/'resumen_tokens.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    return {'tokens':len(rows),'artifacts':len(art)}

def status():
    reg=read_registry(); art=read_artifacts()['artifacts']
    print(json.dumps({'registry':str(REGISTRY),'events_log':str(EVENTS),'artifacts_imported':len(art),'unique_tokens':len(reg['tokens']),'report':str(REPORTS/'resumen_tokens.md')},ensure_ascii=False,indent=2))

def main():
    ap=argparse.ArgumentParser(description=__doc__); sub=ap.add_subparsers(dest='cmd',required=True)
    i=sub.add_parser('ingest'); i.add_argument('source')
    sub.add_parser('report'); sub.add_parser('status')
    a=ap.parse_args()
    if a.cmd=='ingest': ingest(a.source)
    elif a.cmd=='report': print(json.dumps(report(),indent=2))
    else: status()
if __name__=='__main__': main()
