from __future__ import annotations
import hashlib, json, os, threading, time, uuid, warnings, traceback, io, contextlib
from pathlib import Path
from typing import Any, Callable, Optional

CEB_VERSION = 'CEB_V0.6.3_FLOW_LINEAGE_RUNTIME_IDENTITY_PROJECTION'
_EMPTY = object()

def _now_ns(): return time.time_ns()
def _sha(v):
    try: raw=json.dumps(v,ensure_ascii=False,sort_keys=True,default=str,separators=(',',':')).encode()
    except Exception: raw=repr(v).encode('utf-8','replace')
    return hashlib.sha256(raw).hexdigest()

def _summary(v):
    try: n=len(v)
    except Exception: n=None
    return {'type':type(v).__name__,'sha256':_sha(v),'size':n,'empty': v is None or v=={} or v==[] or v==()}

class ObservableDict(dict):
    """Observable mapping with stable lineage across deepcopy/copy."""
    def __init__(self,*a,ceb=None,name='mapping',lineage_id=None,**kw):
        super().__init__(*a,**kw)
        self._ceb=ceb; self._ceb_name=name
        self._ceb_lineage = lineage_id or uuid.uuid4().hex

    def __deepcopy__(self, memo):
        import copy as _copy
        obj=ObservableDict(ceb=self._ceb,name=self._ceb_name,lineage_id=self._ceb_lineage)
        memo[id(self)]=obj
        for k,v in dict.items(self):
            dict.__setitem__(obj,_copy.deepcopy(k,memo),_copy.deepcopy(v,memo))
        return obj
    def _read(self,key):
        if self._ceb: self._ceb.read(self._ceb_name,key)
    def _write(self,key):
        if self._ceb: self._ceb.write(self._ceb_name,key)
    def __getitem__(self,key): self._read(key); return super().__getitem__(key)
    def get(self,key,default=None): self._read(key); return super().get(key,default)
    def __contains__(self,key): self._read(key); return super().__contains__(key)
    def setdefault(self,key,default=None): self._write(key); return super().setdefault(key,default)
    def __setitem__(self,key,value): self._write(key); return super().__setitem__(key,value)
    def __delitem__(self,key): self._write(key); return super().__delitem__(key)
    def pop(self,key,*a): self._write(key); return super().pop(key,*a)
    def popitem(self):
        self._write('*'); return super().popitem()
    def clear(self): self._write('*'); return super().clear()
    def update(self,*a,**kw):
        other=dict(*a,**kw)
        for k in other: self._write(k)
        return super().update(other)
    def __iter__(self):
        if self._ceb: self._ceb.iterate(self._ceb_name, 'iter')
        return super().__iter__()
    def keys(self):
        if self._ceb: self._ceb.iterate(self._ceb_name, 'keys')
        return super().keys()
    def items(self):
        # Yielding key/value pairs is actual value consumption. Record each key
        # separately instead of manufacturing one wildcard edge.
        parent=self
        for k,v in super().items():
            if parent._ceb: parent._ceb.read(parent._ceb_name,k)
            yield (k,v)
    def values(self):
        if self._ceb: self._ceb.iterate(self._ceb_name, 'values')
        return super().values()
    def copy(self):
        # Preserve observability across copies; never downgrade to plain dict.
        return ObservableDict(self, ceb=self._ceb, name=self._ceb_name)

class FlowLedger:
    def __init__(self,root,run_id=None):
        self.root=Path(root); self.root.mkdir(parents=True,exist_ok=True)
        self.run_id=run_id or uuid.uuid4().hex
        self.path=self.root/f'{self.run_id}.flow_ledger.jsonl'
        self._closed=False; self._lock=threading.RLock(); self._seq=0
        self.stages={}; self.key_producers={}; self.object_producers={}; self.lineage_producers={}; self.read_edges=[]; self.terminals=set(); self.io_events=[]; self.warnings=[]
        self._audit_installed=False
        try:
            _install_audit_hook()
            self._audit_installed=True
        except Exception:
            pass
        # Capture runtime warnings even when they occur outside a FlowTracer.call().
        # This is critical for detecting real short-circuits that bypass a traced stage.
        self._prev_showwarning = warnings.showwarning
        self._prev_filters = list(warnings.filters)
        warnings.simplefilter('always', ResourceWarning)
        def _ceb_showwarning(message, category, filename, lineno, file=None, line=None):
            sid=getattr(_CTX,'stage',None) or 'UNSCOPED_RUNTIME'
            rec={'category':getattr(category,'__name__',str(category)),'message':str(message),
                 'filename':str(filename),'lineno':int(lineno),'line':line,'stage_id':sid,
                 'stack':traceback.format_stack(limit=12)[:-1]}
            self.warnings.append(rec)
            if sid in self.stages:
                self.stages[sid]['warnings']=self.stages[sid].get('warnings',0)+1
            self.emit('RUNTIME_WARNING',sid,rec)
            try:
                self._prev_showwarning(message,category,filename,lineno,file,line)
            except Exception:
                pass
        warnings.showwarning=_ceb_showwarning
        self.emit('RUN_START','run',{'ceb_version':CEB_VERSION})
    def record_execution_identity(self, artifacts, source_module=None):
        """Record the exact executable artifacts used by this CEB run.

        This is authoritative runtime provenance: paths are resolved, bytes are
        hashed, and source capabilities are detected from the exact files that
        were loaded. No filename/version label is trusted as a substitute.
        """
        rows=[]
        for role, value in (artifacts or {}).items():
            if value is None: continue
            path=Path(value).resolve()
            row={"role":role,"path":str(path),"present":path.is_file()}
            if path.is_file():
                raw=path.read_bytes()
                row["sha256"]=hashlib.sha256(raw).hexdigest()
                row["bytes"]=len(raw)
                if path.suffix == ".py":
                    txt=raw.decode("utf-8","replace")
                    row["capabilities"]={
                        "projection_longitudinal": "proyeccion_longitudinal" in txt or "x(Z+k)=x(Z)+k*(x(Z)-x(Z-1))" in txt,
                        "transicion_dinamica": "transicion_dinamica" in txt,
                    }
            rows.append(row)
        payload={"source_module":str(Path(source_module).resolve()) if source_module else None,
                 "artifacts":rows}
        self.execution_identity=payload
        self.emit('EXECUTION_IDENTITY','run',payload)
        return payload

    def audit_artifact_integrity(self, root, critical_patterns=None, authorized=None):
        """Verify the physical package and the exact files selected at runtime.

        This is intentionally byte-level: duplicate critical artifacts with different
        hashes, renamed stale Engine copies, or a loaded file outside the package are
        execution-integrity anomalies rather than ordinary warnings.
        """
        root=Path(root).resolve()
        critical_patterns=critical_patterns or [
            "Engine_V5_CANONICO_SOLO*.py",
            "patterns_final_v14.json",
            "MOTOR_V15_3_UNICO_20260927.py",
            "MOTOR_V15_3_NATIVO_V0_9_UNICO.py",
        ]
        authorized=authorized or {}
        files=[]
        for pat in critical_patterns:
            files.extend(root.rglob(pat))
        uniq=[]; seen=set()
        for p in files:
            try: rp=p.resolve()
            except Exception: continue
            if rp in seen or not rp.is_file(): continue
            seen.add(rp); uniq.append(rp)
        groups={}
        for p in uniq:
            raw=p.read_bytes(); h=hashlib.sha256(raw).hexdigest()
            name=p.name
            key=("Engine_V5_CANONICO_SOLO.py" if name.startswith("Engine_V5_CANONICO_SOLO") and name.endswith(".py") else name)
            groups.setdefault(key,[]).append({"path":str(p),"name":name,"sha256":h,"bytes":len(raw)})
        anomalies=[]
        for name,rows in groups.items():
            hashes={r["sha256"] for r in rows}
            if len(hashes)>1:
                anomalies.append({"type":"DUPLICATE_CRITICAL_ARTIFACT_DIFFERENT_HASH","name":name,"copies":rows})
        for role, expected in authorized.items():
            if not expected: continue
            p=Path(expected).resolve()
            if not str(p).startswith(str(root)+os.sep) and p!=root:
                anomalies.append({"type":"EXECUTED_ARTIFACT_OUTSIDE_PACKAGE","role":role,"path":str(p),"package_root":str(root)})
        payload={"root":str(root),"critical_patterns":critical_patterns,"groups":groups,"anomalies":anomalies,"ok":not anomalies}
        self.register('execution_integrity','execution_integrity')
        self.start('execution_integrity',[payload])
        self.output('execution_integrity',payload)
        self.emit('EXECUTION_INTEGRITY_AUDIT','execution_integrity',payload)
        self.end('execution_integrity',payload)
        if not payload['ok']:
            self.terminal('execution_integrity','integrity_failure')
        return payload

    def emit(self,event,stage_id,payload=None,parent_stage_id=None):
        with self._lock:
            if self._closed: raise RuntimeError('CEB_LEDGER_CLOSED')
            self._seq+=1
            r={'schema':CEB_VERSION,'seq':self._seq,'event_id':uuid.uuid4().hex,'run_id':self.run_id,'stage_id':stage_id,'parent_stage_id':parent_stage_id,'event':event,'timestamp_ns':_now_ns(),'process_id':os.getpid(),'thread_id':threading.get_ident(),'payload':payload or {}}
            with self.path.open('a',encoding='utf8') as f:
                f.write(json.dumps(r,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n'); f.flush(); os.fsync(f.fileno())
            return r
    def register(self,sid,name=None,parent=None,metadata=None):
        self.stages.setdefault(sid,{'name':name or sid,'started':0,'ended':0,'output':0,'output_empty':0,'error':0,'warnings':0,'reads':0,'writes':0,'consumers':set()})
        return self.emit('STAGE_REGISTER',sid,{'name':name or sid,'metadata':metadata or {}},parent)
    def start(self,sid,inputs=None,parent=None):
        self.stages.setdefault(sid,{'name':sid,'started':0,'ended':0,'output':0,'output_empty':0,'error':0,'warnings':0,'reads':0,'writes':0,'consumers':set()})['started']+=1
        return self.emit('STAGE_START',sid,{'inputs':[_summary(x) for x in (inputs or [])]},parent)
    def _register_provenance(self,sid,value,depth=0,seen=None):
        if seen is None: seen=set()
        if value is None or depth>2 or id(value) in seen: return
        seen.add(id(value))
        self.object_producers[id(value)]=sid
        lineage=getattr(value,'_ceb_lineage',None)
        if lineage: self.lineage_producers[lineage]=sid
        if isinstance(value,dict):
            vals=list(dict.values(value))
        elif isinstance(value,(list,tuple,set)):
            vals=list(value)
        else:
            vals=[]
        for child in vals: self._register_provenance(sid,child,depth+1,seen)

    def output(self,sid,value):
        self.stages[sid]['output']+=1
        self._register_provenance(sid,value)
        sm=_summary(value)
        if sm['empty']: self.stages[sid]['output_empty']+=1
        return self.emit('STAGE_OUTPUT',sid,{'output':sm})
    def end(self,sid,value=None,error=None):
        self.stages[sid]['ended']+=1
        return self.emit('STAGE_END',sid,{'output':_summary(value) if value is not None else None,'error':None if error is None else {'type':type(error).__name__,'message':str(error)}})
    def error(self,sid,e): self.stages[sid]['error']+=1; return self.emit('STAGE_ERROR',sid,{'type':type(e).__name__,'message':str(e)})
    def iterate(self,mapping,operation):
        sid=getattr(_CTX,'stage',None)
        if not sid: return
        self.stages[sid]['reads']+=1
        # Iterating a mapping proves structural access, not consumption of every key.
        self.emit('DATA_ITERATE',sid,{'mapping':mapping,'operation':operation,'evidence':'mapping_iteration_no_key_edge'})

    def read(self,mapping,key):
        sid=getattr(_CTX,'stage',None)
        if not sid: return
        self.stages[sid]['reads']+=1
        producers=[]
        if key=='*':
            producers=[p for (m,k),p in self.key_producers.items() if m==mapping and p!=sid]
        else:
            p=self.key_producers.get((mapping,key))
            if p and p!=sid: producers=[p]
        prod=producers[0] if len(producers)==1 else None
        self.emit('DATA_READ',sid,{'mapping':mapping,'key':str(key),'producer':prod,'producer_candidates':producers})
        for producer in dict.fromkeys(producers):
            self.read_edges.append((producer,sid,mapping,str(key)))
            self.stages[producer]['consumers'].add(sid)
            self.emit('FLOW_CONSUMED',sid,{'producer':producer,'consumer':sid,'mapping':mapping,'key':str(key),'evidence':'shared_mapping_key' if key!='*' else 'shared_mapping_wildcard'})
    def write(self,mapping,key):
        sid=getattr(_CTX,'stage',None)
        if not sid: return
        self.stages[sid]['writes']+=1
        k=(mapping,key)
        prev=self.key_producers.get(k)
        self.key_producers[k]=sid
        self.emit('DATA_WRITE',sid,{'mapping':mapping,'key':str(key),'previous_producer':prev})
    def seed_mapping(self,mapping_name,mapping,producer_stage):
        for key in dict(mapping).keys():
            self.key_producers[(mapping_name,key)] = producer_stage
            self.emit('DATA_SEED',producer_stage,{'mapping':mapping_name,'key':str(key),'producer':producer_stage})
    def checkpoint(self,sid,name=None,payload=None):
        self.register(sid,name or sid)
        self.start(sid,[])
        self.emit('STAGE_CHECKPOINT',sid,payload or {})
        self.end(sid,None)
        return payload or {}

    def terminal(self,sid,reason='explicit_terminal'):
        self.terminals.add(sid); return self.emit('STAGE_TERMINAL',sid,{'reason':reason})
    def skip(self,sid,reason,detail=''): return self.emit('STAGE_SKIP',sid,{'reason_code':reason,'reason_detail':detail})
    def close(self):
        if not self._closed:
            # Resource-lifecycle checkpoint: collect unreachable objects while the CEB
            # warning hook is still installed. This makes unclosed DB/files visible
            # even when the leak would otherwise surface only at interpreter exit.
            audit_sid = 'resource_lifecycle_audit'
            self.register(audit_sid, audit_sid)
            self.start(audit_sid, [])
            old_stage = getattr(_CTX, 'stage', None)
            old_ledger = getattr(_CTX, 'ledger', None)
            _CTX.stage = audit_sid
            _CTX.ledger = self
            try:
                import gc
                gc.collect()
            finally:
                _CTX.stage = old_stage
                _CTX.ledger = old_ledger
            self.end(audit_sid, {'runtime_warning_count': len(self.warnings)})
            self.emit('RUN_END','run',{'terminal_stages':sorted(self.terminals),'runtime_warning_count':len(self.warnings)})
            self._closed=True
            try:
                if getattr(self,'_prev_showwarning',None) is not None:
                    warnings.showwarning=self._prev_showwarning
                if getattr(self,'_prev_filters',None) is not None:
                    warnings.filters[:] = self._prev_filters
            except Exception:
                pass
        return {'status':'CLOSED','run_id':self.run_id}

class _Ctx(threading.local): pass
_CTX=_Ctx()
_AUDIT_HOOK_INSTALLED = False
_AUDIT_HOOK_LOCK = threading.Lock()

def _global_audit_hook(event, args):
    """Single process-wide audit hook routed only to the currently active CEB ledger.

    Python audit hooks cannot be removed. Installing one closure per run made old hooks
    accumulate, write into closed ledgers, and slow/hang retained-cut runs and calibration
    batches. A thread-local active-ledger pointer keeps the hook bounded and run-local.
    """
    if event not in {'open', 'os.open'}:
        return
    ledger = getattr(_CTX, 'ledger', None)
    sid = getattr(_CTX, 'stage', None)
    if ledger is None or ledger._closed or not sid:
        return
    path = str(args[0]) if args else ''
    if path == str(ledger.path):
        return
    mode = str(args[1]) if len(args) > 1 else ''
    writable = any(x in mode for x in ('w', 'a', 'x', '+'))
    ledger.io_events.append((sid, event, path, mode, writable))
    try:
        ledger.emit('IO_ACCESS', sid, {'event': event, 'path': path, 'mode': mode, 'writable': writable})
    except RuntimeError:
        # A close can race with a late runtime I/O event; do not break the operation.
        return

def _install_audit_hook():
    global _AUDIT_HOOK_INSTALLED
    if _AUDIT_HOOK_INSTALLED:
        return
    with _AUDIT_HOOK_LOCK:
        if not _AUDIT_HOOK_INSTALLED:
            import sys
            sys.addaudithook(_global_audit_hook)
            _AUDIT_HOOK_INSTALLED = True

class FlowTracer:
    def __init__(self,ledger,parent=None): self.ledger=ledger; self.parent=parent; self.counts={}
    def observable(self,mapping,name): return ObservableDict(mapping,ceb=self.ledger,name=name)
    def call(self,name,fn,*args,shared=None,terminal=False,**kwargs):
        base=str(name or getattr(fn,'__name__','anonymous')); self.counts[base]=self.counts.get(base,0)+1; sid=f'{base}#{self.counts[base]}'
        self.ledger.register(sid,base,self.parent,{'callable':getattr(fn,'__qualname__',repr(fn)),'module':getattr(fn,'__module__',None)})
        self.ledger.start(sid,list(args)+list(kwargs.values()),self.parent)
        old=getattr(_CTX,'stage',None); old_ledger=getattr(_CTX,'ledger',None)
        _CTX.stage=sid; _CTX.ledger=self.ledger
        for value in (shared or []):
            producer=self.ledger.object_producers.get(id(value))
            lineage=getattr(value,'_ceb_lineage',None)
            if not producer and lineage:
                producer=self.ledger.lineage_producers.get(lineage)
            if producer and producer!=sid:
                self.ledger.stages[producer]['consumers'].add(sid)
                self.ledger.read_edges.append((producer,sid,'object','<shared>'))
                self.ledger.emit('FLOW_CONSUMED',sid,{'producer':producer,'consumer':sid,'evidence':'shared_object_identity'})
        stderr_buf=io.StringIO()
        try:
            with warnings.catch_warnings():
                warnings.simplefilter('always')
                with contextlib.redirect_stderr(stderr_buf):
                    out=fn(*args,**kwargs)
            stderr_text=stderr_buf.getvalue()
            if stderr_text.strip():
                self.ledger.emit('STDERR_OUTPUT',sid,{'text':stderr_text[-12000:],'warning_count':self.ledger.stages.get(sid,{}).get('warnings',0)})
            if isinstance(out, dict) and not isinstance(out, ObservableDict):
                out=ObservableDict(out,ceb=self.ledger,name=f'output:{sid}')
            self.ledger.output(sid,out); self.ledger.end(sid,out)
            if terminal: self.ledger.terminal(sid)
            return out
        except BaseException as e:
            stderr_text=stderr_buf.getvalue()
            if stderr_text.strip():
                self.ledger.emit('STDERR_OUTPUT',sid,{'text':stderr_text[-12000:],'warning_count':self.ledger.stages.get(sid,{}).get('warnings',0)})
            self.ledger.error(sid,e); self.ledger.end(sid,None,e); raise
        finally:
            _CTX.stage=old; _CTX.ledger=old_ledger
    def latest_id(self,name):
        ids=[x for x in self.ledger.stages if x==name or x.startswith(name+'#')]
        return sorted(ids)[-1] if ids else None
    def mark_terminal(self,name,reason='explicit_terminal'):
        # Resolve latest dynamic instance of a base name.
        ids=[x for x in self.ledger.stages if x==name or x.startswith(name+'#')]
        if ids: self.ledger.terminal(sorted(ids)[-1],reason)

def _diagnose_warning(rec):
    msg=str(rec.get('message') or '').lower()
    cat=str(rec.get('category') or '')
    if 'unclosed database' in msg or ('sqlite' in msg and 'unclosed' in msg):
        return 'RESOURCE_LEAK_UNCLOSED_DATABASE'
    if 'mean of empty slice' in msg or 'invalid value encountered in scalar divide' in msg:
        return 'NUMERIC_EMPTY_AGGREGATE'
    if cat.endswith('ResourceWarning'):
        return 'RESOURCE_WARNING'
    if cat.endswith('RuntimeWarning'):
        return 'RUNTIME_NUMERIC_WARNING'
    return 'RUNTIME_WARNING'


class FlowVerifier:
    def __init__(self,path): self.path=Path(path)
    def _load(self): return [json.loads(x) for x in self.path.read_text(encoding='utf8').splitlines() if x.strip()]
    def verify(self,report=None):
        recs=self._load(); stages={}; edges=[]; anomalies=[]; run_end=0; execution_identity=None
        for r in recs:
            if r['event']=='RUN_END': run_end+=1
            if r['event']=='EXECUTION_IDENTITY': execution_identity=r.get('payload') or {}
            if r['event']=='EXECUTION_INTEGRITY_AUDIT':
                for a in (r.get('payload') or {}).get('anomalies') or []:
                    anomalies.append(a)
            sid=r.get('stage_id')
            if sid=='run': continue
            s=stages.setdefault(sid,{'name':sid,'registered':False,'started':0,'ended':0,'output':0,'output_empty':0,'error':0,'warnings':0,'reads':0,'writes':0,'io_access':[],'io_writes':0,'consumers':[],'terminal':False})
            e=r['event']; p=r.get('payload') or {}
            if e=='STAGE_REGISTER': s['registered']=True; s['name']=p.get('name') or sid
            elif e=='STAGE_START': s['started']+=1
            elif e=='STAGE_END': s['ended']+=1
            elif e=='STAGE_OUTPUT':
                s['output']+=1
                if (p.get('output') or {}).get('empty'): s['output_empty']+=1
            elif e=='STAGE_ERROR': s['error']+=1
            elif e=='RUNTIME_WARNING': s['warnings']+=1; anomalies.append({'type':'RUNTIME_WARNING','stage_id':sid,'component':s.get('name'),'diagnosis':_diagnose_warning(p),**p})
            elif e=='STDERR_OUTPUT': s.setdefault('stderr',[]).append(p.get('text',''))
            elif e=='DATA_READ': s['reads']+=1
            elif e=='DATA_WRITE': s['writes']+=1
            elif e=='IO_ACCESS':
                s['io_access'].append(p.get('path'))
                if p.get('writable'): s['io_writes']+=1
                else:
                    read_path=str(p.get('path') or '')
                    for psid,ps in stages.items():
                        if psid==sid: continue
                        for wp in ps.get('io_access',[]):
                            if wp and (str(wp)==read_path):
                                ps['consumers'].append(sid)
                                edges.append({'producer':psid,'consumer':sid,'evidence':'io_same_path','path':read_path})
                                break
            elif e=='FLOW_CONSUMED':
                edges.append(p); producer=p.get('producer');
                if producer in stages: stages[producer]['consumers'].append(sid)
            elif e=='STAGE_TERMINAL': s['terminal']=True
            elif e=='STAGE_CHECKPOINT': s['output']+=1
        for sid,s in stages.items():
            if s['error']: s['status']='FAILED'
            elif s['started'] and not s['ended']: s['status']='STARTED_NOT_CLOSED'
            elif not s['started'] and s['registered']: s['status']='REGISTERED_NOT_STARTED'
            elif s['started'] and s['ended']:
                s['status']='EXECUTED_WITH_WARNINGS' if s.get('warnings') else ('EXECUTED_AND_CONNECTED' if (s['consumers'] or s['terminal'] or not s['output']) else ('OUTPUT_PERSISTED_WITHOUT_CONSUMER' if s.get('io_writes') else 'OUTPUT_NO_OBSERVED_CONSUMER'))
            else: s['status']='UNKNOWN'
        if report:
            reported=report.get('execution',{}).get('component_status') or report.get('component_status') or []
            if isinstance(reported,dict): reported=list(reported.values())
            def norm(x):
                x=str(x or '').split('#',1)[0].strip().lower()
                x=x.replace('\\','/')
                if '(' in x: x=x.split('(',1)[0]
                if x.endswith('.py'): x=x[:-3]
                for suffix in ('.pre_predictor.output','.post_predictor.output','.output','.pre_predictor','.post_predictor','.pre_h','.post_h'):
                    if x.endswith(suffix): x=x[:-len(suffix)]
                return x
            byname={}
            for sid,s in stages.items(): byname.setdefault(norm(s.get('name') or sid),[]).append((sid,s))
            for rr in reported:
                if not isinstance(rr,dict) or not rr.get('component'): continue
                name=rr['component']; nname=norm(name); matches=byname.get(nname,[])
                if not matches:
                    matches=[(sid,ss) for sid,ss in stages.items() if norm(ss.get('name') or sid)==nname or norm(ss.get('name') or sid).startswith(nname+'.')]
                lname=str(name).lower()
                if '(pre)' in lname: matches=[x for x in matches if '.pre_predictor' in x[0]]
                if '(post)' in lname: matches=[x for x in matches if '.post_predictor' in x[0]]
                claimed=str(rr.get('status','')).upper(); feeds=bool(rr.get('feeds_H',False) or rr.get('feeds_predictor',False))
                non_authoritative = claimed in {'AUDIT_ONLY','PLUGIN_SALTADO','APAGADO_ABLACION','CABLEADO_NO_EJECUTADO','CABLEADO_ESPERANDO_LLM_SEARCH','API_PENDING','ACTIVA_MUDA','ABSORBIDO_EN_GUARDIA_TRANSVERSAL'}
                if claimed=='EXECUTED' and not matches:
                    anomalies.append({'type':'REPORTED_EXECUTED_NOT_OBSERVED','component':name})
                    continue
                for sid,s in matches:
                    if non_authoritative and s['status']=='FAILED':
                        s['status']='FAILED_NON_AUTHORITATIVE'
                        anomalies.append({'type':'NON_AUTHORITATIVE_STAGE_FAILED','component':name,'claimed':claimed,'actual':'FAILED'})
                        continue
                    if claimed=='EXECUTED' and s['status'] in {'FAILED','STARTED_NOT_CLOSED','REGISTERED_NOT_STARTED'}:
                        anomalies.append({'type':'REPORT_EXECUTION_MISMATCH','component':name,'claimed':claimed,'actual':s['status']})
                    if feeds and s['output']==0:
                        anomalies.append({'type':'FEEDS_WITHOUT_OUTPUT','component':name,'status':s['status']})
                    if feeds and s['output_empty'] and not s['consumers'] and not s['terminal']:
                        anomalies.append({'type':'FEEDS_EMPTY_OUTPUT_NOT_CONSUMED','component':name,'status':s['status'],'diagnosis':'DECLARED_FEED_EMPTY_OR_SHORT_CIRCUITED'})
                    if feeds and s['output'] and not s['consumers'] and not s['terminal']:
                        anomalies.append({'type':'FEEDS_OUTPUT_NOT_CONSUMED','component':name,'status':s['status'],'diagnosis':'DECLARED_FEED_WITHOUT_OBSERVED_CONSUMER'})
                    if feeds and s.get('io_writes') and not s['consumers'] and not s['terminal']:
                        anomalies.append({'type':'FEEDS_OUTPUT_ONLY_PERSISTED','component':name,'status':s['status'],'diagnosis':'DECLARED_FEED_ONLY_PERSISTED_NO_CONSUMER'})
        if report and execution_identity:
            declared_identity=report.get('execution_identity')
            if declared_identity and declared_identity != execution_identity:
                anomalies.append({'type':'EXECUTION_IDENTITY_MISMATCH','diagnosis':'result_identity_differs_from_runtime_ledger'})

        bad=[sid for sid,s in stages.items() if sid!='run' and s['status'] in {'FAILED','STARTED_NOT_CLOSED','REGISTERED_NOT_STARTED','UNKNOWN'}]
        wiring_diagnostics=[]
        for a in anomalies:
            if a.get('type')=='REPORTED_EXECUTED_NOT_OBSERVED':
                wiring_diagnostics.append({'type':'WIRING_DECLARED_EXECUTED_NOT_OBSERVED','component':a.get('component'),'diagnosis':'declared_executed_but_no_runtime_stage'})
            elif a.get('type') in {'FEEDS_OUTPUT_NOT_CONSUMED','FEEDS_EMPTY_OUTPUT_NOT_CONSUMED','FEEDS_OUTPUT_ONLY_PERSISTED'}:
                wiring_diagnostics.append({'type':'WIRING_DECLARED_BUT_NOT_OBSERVED','component':a.get('component'),'diagnosis':a.get('diagnosis'),'status':a.get('status')})
            elif a.get('type')=='RUNTIME_WARNING':
                wiring_diagnostics.append({'type':a.get('diagnosis'),'component':a.get('component'),'stage_id':a.get('stage_id'),'source':a.get('filename'),'line':a.get('lineno'),'message':a.get('message'),'stack':a.get('stack')})
        status='VERIFIED_FLOW' if run_end==1 and not bad and not anomalies else ('INCOMPLETE' if run_end!=1 or bad else 'VERIFIED_FLOW_WITH_ANOMALIES')
        return {'ceb_version':CEB_VERSION,'status':status,'stages':stages,'edges':edges,'anomalies':anomalies,'wiring_diagnostics':wiring_diagnostics,'run_end_count':run_end,'terminal_stages':[sid for sid,s in stages.items() if s['terminal']], 'execution_identity':execution_identity}
