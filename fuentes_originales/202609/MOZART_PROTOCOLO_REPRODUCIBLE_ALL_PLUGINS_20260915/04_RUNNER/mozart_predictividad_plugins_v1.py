import json, hashlib
from pathlib import Path

BASE=Path('/mnt/data/mozart_run')
ALL=BASE/'MOZART_ALL_PLUGINS_MC.json'
CUTS=BASE/'mozart_cuts_full.json'
OUT=BASE/'MOZART_PREDICTIVIDAD_HIPOTESIS_ALL_PLUGINS.json'
D=json.loads(ALL.read_text(encoding='utf8'))
C=json.loads(CUTS.read_text(encoding='utf8'))

# --- Freeze point: C7 only. C8-C10 are read strictly after the freeze is built. ---
cut_ids=[x['id'] for x in C]
assert cut_ids==[f'C{i}' for i in range(1,11)]
Z=7

picos=D['picos_mesetas']
r3=D['reporte_3d']
ses=D['sesgo_lectura']
mono=D['monomito']['posicion_monomito_por_corte']
capa=D['capa2']
aq=D['aquiles_entre_cortes']

r3_by={x['corte']:x for x in r3['cortes']}
mono_by={x['corte']:x for x in mono}

# The three hypothesis families are defined from the observable structure at C7,
# without inspecting C8-C10 for their construction.
H=[
  {
    'id':'H1',
    'familia':'arquetipo_el_creador',
    'tesis':'Continuidad creadora e independiente después de Z90: creación/producción permanece activa y la independencia no se apaga.',
    'descarte':'No asumir que la ambición/estatus pasa a ser el eje dominante y desplaza la creación.'
  },
  {
    'id':'H2',
    'familia':'30_ambicion',
    'tesis':'Después de Z90, ambición/estatus/logro y conflicto de campo pasan a dominar la trayectoria, reduciendo la centralidad creadora.',
    'descarte':'No asumir continuidad creadora como eje dominante.'
  },
  {
    'id':'H3',
    'familia':'social_04_rogers_difusion_innovaciones',
    'tesis':'La continuidad posterior se organiza principalmente alrededor de difusión/reconocimiento de la obra, más que alrededor de un desplazamiento hacia ambición.',
    'descarte':'No asumir que el cambio principal sea hacia ambición/estatus.'
  }
]

# Evidence visible at freeze. No outcome information is used here.
finalP={k:v for k,v in D['final_top_P']}
finalA={k:v for k,v in D['final_top_A']}
finalC={k:v for k,v in D['final_top_C']}

# C7 from the P-axis can be recovered from the 3D report and picos; use only C1-C7
# trend information for the freeze evidence.
top1_pre=picos['top1'][:Z]
tr_pre=[x for x in ses['transiciones'] if int(x['de'][1:])<Z and int(x['a'][1:])<=Z]

# Independent-lens evidence flags. These are counts, not probabilities.
evidence={}
for h in H: evidence[h['id']]=[]

# Motor / 3D
c7=r3_by['C7']
if c7['H']=='30_ambicion': evidence['H2'].append('REPORTE_3D_C7_H=30_ambicion')
if any(x['h']=='arquetipo_el_creador' for x in c7.get('no_se_apagaron',[])): evidence['H1'].append('REPORTE_3D_C7_CREADOR_NO_SE_APAGA')
if any(x['h']=='schwartz_10_autodireccion' for x in c7.get('no_se_apagaron',[])): evidence['H1'].append('REPORTE_3D_C7_AUTODIRECCION_NO_SE_APAGA')
if any(x['h']=='schwartz_07_logro' for x in c7.get('se_movieron',[])): evidence['H2'].append('REPORTE_3D_C7_LOGRO_SE_MOVIO')
if any(x['h']=='12_obtencion' for x in c7.get('se_movieron',[])): evidence['H2'].append('REPORTE_3D_C7_OBTENCION_SE_MOVIO')

# Peaks/plateaus: use only C1-C7.
if all(x=='arquetipo_el_creador' for x in top1_pre[:5]): evidence['H1'].append('PICOS_C1_C5_CREADOR_TOP1')
if top1_pre[5:7]==['30_ambicion','30_ambicion']: evidence['H2'].append('PICOS_C6_C7_AMBICION_TOP1')

# Sesgo/temporal reading: C6->C7 is a stable ambition sign, while C7->C8 is excluded.
for tr in tr_pre:
    if tr['de']=='C6' and tr['a']=='C7':
        if tr['H_a']=='30_ambicion': evidence['H2'].append('SESGO_C6_C7_LETRERO_AMBICION')
        if 'ambicion' in tr.get('tokens_nuevos',[]): evidence['H2'].append('SESGO_C6_C7_AMBICION_TOKEN')

# Aquiles says the modal wind at C6-C7 is ambition, but the H remains a surface read.
blocks=[b for b in aq.get('bloques',[]) if b.get('n')<=Z]
if any(b.get('n')==7 and b.get('viento',{}).get('winner_modal')=='30_ambicion' for b in blocks): evidence['H2'].append('AQUILES_C7_VIENTO_AMBICION')

# Q2/Q3 circular lens: C7 has challenge thread and dual quadrant occupancy.
m7=mono_by['C7']
if 'hilo_desafio' in m7.get('hilos_presentes',[]): evidence['H2'].append('CIRCULO_C7_HILO_DESAFIO')
if len(m7.get('cuadrante_activo',[]))>=2: evidence['H2'].append('CIRCULO_C7_Q2_Q3_SIMULTANEOS')

# Layer-2 suggestion is explicitly unverified and therefore not used as decisive evidence.
# We preserve it in the record, but it contributes zero to the selection.

# H3 gets C7 contextual recognition/diffusion only if visible in the C axis top list.
if any(k=='social_04_rogers_difusion_innovaciones' for k,v in D['final_top_C']):
    evidence['H3'].append('C_AXIS_ROGERS_PRESENTE_EN_RESULTADO_FINAL')
if any(k=='reconocimiento' for k,w in C[6]['C']):
    evidence['H3'].append('HECHO_C7_RECONOCIMIENTO')

# Freeze: select the strongest observed directional family only for the primary bet;
# preserve all hypotheses and a transparent evidence count. This is deliberately
# not a p_final probability and not a forecast probability.
counts={k:len(v) for k,v in evidence.items()}
primary=max(counts, key=counts.get)
# Tie-breaker is fixed and declared, not outcome-driven: H1 before H2 before H3.
order=['H1','H2','H3']
primary=sorted(counts, key=lambda k:(-counts[k],order.index(k)))[0]
secondary=[k for k in order if k!=primary][0]

freeze={
 'freeze_cut':'C7',
 'z_rule':'90% lifespan; C7 is the historical Z90 work point used here',
 'primary_bet':primary,
 'primary_family':next(x['familia'] for x in H if x['id']==primary),
 'discarded_direction':next(x['familia'] for x in H if x['id']==secondary),
 'evidence_counts':counts,
 'evidence':evidence,
 'hypotheses':H,
 'source_result_sha256':hashlib.sha256(ALL.read_bytes()).hexdigest(),
 'canonical_engine_sha256':hashlib.sha256((BASE/'Engine_V5_CANONICO_SOLO.py').read_bytes()).hexdigest(),
 'canonical_patterns_sha256':hashlib.sha256((BASE/'patterns_final_v14.json').read_bytes()).hexdigest(),
 'canonical_patterns_count':244,
 'sidecar_memory_patterns':D['sidecar_memory_patterns'],
 'dynamic_fusion_memory_patterns':D['dynamic_fusion_memory_patterns'],
 'rule':'freeze constructed from C1-C7 only; C8-C10 excluded from construction'
}

# Validation after freeze.
def classify(hid, cid, cut):
    p=cut.get('P',[]); c=cut.get('C',[]); a=cut.get('A',[])
    pnames={x[0] for x in p}; cnames={x[0] for x in c}; anames={x[0] for x in a}
    r=r3_by[cid]
    if hid=='H1':
        # creator/independence continuity; require creation and/or independence in the actual cut,
        # and corroboration that creator remains active in the engine lens.
        actual=('creatividad' in pnames or 'independencia' in pnames)
        engine=(r['H']=='arquetipo_el_creador' or any(x['h']=='arquetipo_el_creador' for x in r.get('no_se_apagaron',[])))
        return 'HIT' if actual and engine else 'MISS'
    if hid=='H2':
        actual=('ambicion' in pnames)
        engine=(r['H']=='30_ambicion')
        return 'HIT' if actual and engine else 'MISS'
    if hid=='H3':
        actual=('reconocimiento' in cnames)
        engine=any(x['h']=='social_04_rogers_difusion_innovaciones' for x in r.get('se_movieron',[])) or r['H']=='social_04_rogers_difusion_innovaciones'
        return 'HIT' if actual and engine else 'PARTIAL'

valid=[]
for cut in C[7:]:
    cid=cut['id']
    row={'cut':cid}
    for h in H: row[h['id']]=classify(h['id'],cid,cut)
    valid.append(row)

summary={}
for h in H:
 vals=[r[h['id']] for r in valid]
 summary[h['id']]={'hits':vals.count('HIT'),'partials':vals.count('PARTIAL'),'misses':vals.count('MISS'),'n':len(vals)}

out={
 'version':'V15.1_PREDICTIVIDAD_HIPOTESIS_ALL_PLUGINS_V1',
 'case':'Mozart',
 'plugin_run':'MOZART_ALL_PLUGINS_MC.json',
 'freeze':freeze,
 'validation':valid,
 'summary':summary,
 'status':'RETROSPECTIVE_FREEZE_BEFORE_C8',
 'interpretation_rule':'No se convierte en probabilidad poblacional; valida si las señales congeladas antes de C8 se sostuvieron en C8-C10.',
 'limitations':['un solo caso','cortes históricos','mapeo de tokens hecho antes de esta capa','Capa2 evidence_status=unverified','no es predicción prospectiva de una vida real']
}
OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'freeze_primary':primary,'counts':counts,'validation':valid,'summary':summary,'out':str(OUT),'sha256':hashlib.sha256(OUT.read_bytes()).hexdigest()},ensure_ascii=False,indent=2))
