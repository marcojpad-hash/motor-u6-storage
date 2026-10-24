import importlib.util, json, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BUNDLE=ROOT/'tests'/'fixtures'/'legacy'
SUMMARY=ROOT/'tests'/'fixtures'/'mortality_ablation_summary.json'
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    import sys; sys.modules[name]=mod
    spec.loader.exec_module(mod)
    return mod
old=load('old_area',BUNDLE/'sidecar_area_tokens_v1_BEFORE.py')
new=load('new_area',BUNDLE/'sidecar_area_tokens_v1.py')
mort=load('mortality',BUNDLE/'familias_tokens'/'mortalidad_clasificador_lateral_v0_1.py')
CASES=[
 ('propia','Casanova muere en Praga en 1798','mort_evento_propio','REJECTED_POST_Z90'),
 ('ajena','Muere su padre y queda huérfano','mort_evento_ajeno_vinculo_cercano','CLASSIFIED'),
 ('ajena','La muerte de Anna Maria lo devasta','mort_evento_ajeno_vinculo_no_resuelto','CLASSIFIED'),
 ('ajena','Murió su madre en 1750','mort_evento_ajeno_vinculo_cercano','CLASSIFIED'),
 ('ajena','Su hermano muere en la guerra','mort_evento_ajeno_vinculo_cercano','CLASSIFIED'),
 ('ajena','Muere el rey y el reino se divide','mort_evento_ajeno_autoridad_figura','CLASSIFIED'),
 ('ajena','El maestro muere y el discípulo hereda','mort_evento_ajeno_autoridad_figura','CLASSIFIED'),
 ('negada','No murió en el naufragio','mort_evento_negado','DISCARDED_NEGATION'),
 ('cuerpo','Enferma gravemente en 1796; agoniza varios días','cuerpo_agonia','CLASSIFIED'),
 ('finitud','Teme a la muerte y piensa en ella','mort_finitud_anticipada','ALLOWED_PRE_Z90'),
 ('tema','Escribe un tratado sobre la muerte','mort_tema_representacion','CLASSIFIED'),
 ('contexto','Mueren miles en la hambruna','mort_contexto_colectivo','CLASSIFIED')]
for label,text,token,status in CASES:
    oldrows=old.tokens_cuerpo_desde_texto(text)
    newrows=new.tokens_cuerpo_desde_texto(text,case_subject='Casanova',z90_date='1791-12-31')
    toks=[r['token'] for r in newrows]
    statuses=[r.get('status') or (r.get('mortality_class') or {}).get('status') for r in newrows]
    assert token in toks,(text,token,toks)
    if label!='cuerpo': assert status in statuses,(text,status,statuses)
    else: assert 'cuerpo_enfermedad' in toks and 'cuerpo_agonia' in toks,(text,toks)
r=mort.classify_death('Muere durante el viaje',case_subject='Casanova',z90_date='1791-12-31')
assert r[0]['token']=='mort_sujeto_no_resuelto',r
r2=new.tokens_cuerpo_desde_texto('Casanova muere en Praga en 1798',case_subject='Casanova')
assert not any(x['token']=='cuerpo_muerte_propia' for x in r2),r2
r3=new.tokens_cuerpo_desde_texto('Casanova muere en Praga en 1780',case_subject='Casanova',z90_date='1791-12-31')
assert any(x['token']=='cuerpo_muerte_propia' for x in r3),r3
engine=ROOT/'motor'/'Engine_V5_CANONICO_SOLO.py'; pats=ROOT/'motor'/'patterns_final_v14.json'
assert hashlib.sha256(engine.read_bytes()).hexdigest()=='665c39a2861e58772522e91272563260d980908b1d4ab9f7092d3413d0c36082'
assert hashlib.sha256(pats.read_bytes()).hexdigest()=='d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1'
s=json.loads(SUMMARY.read_text())
for k in ('H1','H2'):
    assert s['on'][k]['family']==s['off'][k]['family']
    assert s['on'][k]['rank_fusion']==s['off'][k]['rank_fusion']
print(f'PASS: {len(CASES)} acceptance cases + R1/R3 + canonical hashes + paired ablation summary')
