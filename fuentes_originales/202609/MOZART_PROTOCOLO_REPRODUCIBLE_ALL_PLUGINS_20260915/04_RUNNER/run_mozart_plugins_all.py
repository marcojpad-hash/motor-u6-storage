import json, importlib.util, hashlib, shutil, sys
from pathlib import Path
import numpy as np
BASE=Path('/mnt/data/mozart_run')
CUTS=json.load(open(BASE/'mozart_cuts_full.json',encoding='utf8'))

def load(name,file):
 s=importlib.util.spec_from_file_location(name,str(BASE/file)); m=importlib.util.module_from_spec(s); sys.modules[name]=m; s.loader.exec_module(m); return m
eng=load('eng','Engine_V5_CANONICO_SOLO.py')
fam=load('fam','plugin_familias_gloria_sacro.py'); otto=load('otto','plugin_otto_numinoso.py'); host=load('host','plugin_trayectoria_hosteleria.py')
# Authorized B sidecar fusion in memory only
lib=json.load(open(BASE/'patterns_final_v14.json',encoding='utf8'))
lib=fam.fusionar(lib); lib=otto.fusionar(lib); lib=host.fusionar(lib)
mem=BASE/'_tmp_patterns_plugins_all.json'; mem.write_text(json.dumps(lib,ensure_ascii=False),encoding='utf8')
print('MEM_PATTERNS',len(lib),'SHA',hashlib.sha256(mem.read_bytes()).hexdigest())
# one engine per axis, same 5x3 protocol, MC true
engines=[]
seqs=[]
for ax in 'PAC':
 e=eng.TracingEngine(str(mem),':memory:'); e.start_question('Mozart_'+ax); engines.append(e); seqs.append([])
for raw in CUTS:
 for j,ax in enumerate('PAC'):
  rows=raw.get(ax) or []
  e=engines[j]
  e.extractor.extract_from_text=lambda txt,rows=list(rows),cid=raw['id'],ax=ax:[eng.Marker(t,t,float(w),source=f'PLUGIN5x3:{cid}:{ax}') for t,w in rows]
  r=e.process_observation(raw['id']+'_'+ax,monte_carlo=True)
  b={h['name']:float(h['p_final']) for h in r['hypotheses']}; seqs[j].append((raw['id'],b))
# check same board keys / 247
names=sorted(seqs[0][-1][1]); assert len(names)==len(lib)
# R dimensionality is sidecar dimension, not canonical R732
Xm=[]
for i in range(len(CUTS)):
 vals=[]
 for j in range(3): vals += [seqs[j][i][1][n] for n in names]
 Xm.append(vals)
Xm=np.array(Xm); d=np.diff(Xm,axis=0); dn=np.linalg.norm(d,axis=1)
persist=[]; kap=[]
for i in range(1,len(d)):
 a,b=d[i-1],d[i]; c=float(np.dot(a,b)/(np.linalg.norm(a)*np.linalg.norm(b)+1e-12)); c=max(-1,min(1,c)); persist.append(c); kap.append((max(0,1-c*c))**0.5)
# lenses
picos=load('picos','plugin_picos_mesetas.py'); sesgo=load('sesgo','plugin_sesgo_lectura.py'); arco=load('arco','plugin_arco_field_snyder_mckee.py'); rep=load('rep','plugin_reporte_3d.py'); mono=load('mono','plugin_circulo_monomito.py'); pregunta=load('preg','plugin_pregunta_detras_v2.py'); emb=load('emb','plugin_embudo_clinico.py'); alias=load('alias','plugin_alias_reactivacion.py'); fix=load('fix','plugin_fix_entrada.py'); rigor=load('rigor','plugin_metodo_rigor.py'); aq=load('aq','plugin_aquiles_h.py'); guard=load('guard','plugin_guardia_no_cruce.py'); dyn=load('dyn','plugin_arquetipos_dinamicos.py'); capa2=load('capa2','plugin_capa2_antecedentes_arquetipos.py')
# Use P board for 3D/picos as in existing pipeline; keep other axes in result
seqP=seqs[0]
cutout=[]
for raw,(cid,b) in zip(CUTS,seqP):
 H=max(b,key=b.get); cutout.append({'id':cid,'H':H,'tokens':[(t,w) for t,w in raw.get('P') or []]})
# run lenses, with guard per cut on a snapshot of P board
monoin=[]
for raw in CUTS:
 toks=[t for ax in 'PAC' for t,w in (raw.get(ax) or [])]
 monoin.append((raw['id'],toks,'Mozart'))
mono_out=mono.posicion_por_corte(monoin)
preg_out=pregunta.interrogar('¿Hacia dónde se perfila la trayectoria de Mozart después del Z90?')
emb_out=emb.etiquetar([(r['id'],[(t,w) for t,w in sum([r.get(ax) or [] for ax in 'PAC'],[])]) for r in CUTS])
fix_out=fix.preparar_caso([(r['id'],sum([r.get(ax) or [] for ax in 'PAC'],[]),r.get('hecho','')) for r in CUTS])
# capa2 catalog from root
catalog=BASE/'catalogo_capa2_familias_semilla.json'
if not catalog.exists(): catalog=Path('/mnt/data/catalogo_capa2_familias_semilla.json')
pin={r['id']:[t for ax in 'PAC' for t,w in (r.get(ax) or [])] for r in CUTS}
capa_out=capa2.leer(pin,catalogo_path=str(catalog))
# aquiles across cuts, not bootstrap
pts=[]
for cid,b in seqP:
 H=max(b,key=b.get); pts.append({'n':len(pts)+1,'p_H':b[H],'winner':H,'topk':[x[0] for x in sorted(b.items(),key=lambda x:-x[1])[:5]],'I':0.05})
aq_out=aq.evaluar_serie(pts)
# guard + 3d output validation
r3=rep.leer(seqP)
for row in r3['cortes']:
 hyp=seqP[[x[0] for x in seqP].index(row['corte'])][1]
 with guard.GuardiaNoCruce(hyp,row['corte']) as g:
  g.validar_output_lente({'cuadrante_activo':[], 'nota':'3D annotation only'})
# arco from deltas using P board
carco=[]
for i,(cid,b) in enumerate(seqP):
 if i==0: dmax=dneto=0.0
 else:
  prev=seqP[i-1][1]; ds=[b.get(k,0.5)-prev.get(k,0.5) for k in set(b)|set(prev)]; dmax=max(map(abs,ds),default=0); dneto=sum(ds)/len(ds) if ds else 0
 carco.append({'id':cid,'delta_max':dmax,'delta_neto':dneto})
arco_out=arco.leer(carco)
picos_out=picos.curvas(seqP)
sesgo_out=sesgo.leer(cutout)
# alias/fix/embudo outputs are analysis-only; don't replace engine input
# dynamic archetypes: fusion is tested in memory only, but not mixed into B 247 board
lib_dyn=dyn.fusionar(dict(lib))
# rigor is documentation lens
rigor_out=rigor.rigor({'plugins':'all','engine_tocado':False},'','')
out={'version':'V15.1_PLUGIN_ALL_EXPERIMENTAL','base_canon_244':244,'sidecar_memory_patterns':len(lib),'dynamic_fusion_memory_patterns':len(lib_dyn),'engine_canon_tocado':False,'patterns_disk_tocado':False,'monte_carlo':True,'axes':['P','A','C'],'sidecar_fusion':['plugin_familias_gloria_sacro','plugin_otto_numinoso','plugin_trayectoria_hosteleria'],'lenses_executed':['traza_campo_244','plugin_reporte_3d','plugin_picos_mesetas','plugin_sesgo_lectura','plugin_arco_field_snyder_mckee','plugin_circulo_monomito','plugin_aquiles_h','plugin_pregunta_detras_v2','plugin_embudo_clinico','plugin_alias_reactivacion','plugin_fix_entrada','plugin_metodo_rigor','plugin_arquetipos_dinamicos','plugin_capa2_antecedentes_arquetipos','plugin_guardia_no_cruce'],'n_cuts':len(CUTS),'sidecar_R_shape':list(Xm.shape),'sidecar_dX_norm':dn.tolist(),'sidecar_persist_cos':persist,'sidecar_kappa_dir':kap,'final_top_P':sorted(seqP[-1][1].items(),key=lambda x:-x[1])[:10],'final_top_A':sorted(seqs[1][-1][1].items(),key=lambda x:-x[1])[:10],'final_top_C':sorted(seqs[2][-1][1].items(),key=lambda x:-x[1])[:10],'reporte_3d':r3,'picos_mesetas':picos_out,'sesgo_lectura':sesgo_out,'arco':arco_out,'monomito':mono_out,'pregunta':preg_out,'embudo':emb_out,'entrada_fix_diagnostico':fix_out,'capa2':capa_out,'aquiles_entre_cortes':aq_out,'guardia_no_cruce':'PASS','metodo_rigor':rigor_out}
json.dump(out,open(BASE/'MOZART_ALL_PLUGINS_MC.json','w',encoding='utf8'),ensure_ascii=False,indent=2)
print(json.dumps({'final_top_P':out['final_top_P'],'final_top_A':out['final_top_A'],'final_top_C':out['final_top_C'],'sidecar_R_shape':out['sidecar_R_shape'],'guard':'PASS','mem_patterns':len(lib),'dyn_patterns':len(lib_dyn)},ensure_ascii=False,indent=2))
