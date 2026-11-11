# CAMEO lateral institutional event layer v1
import json,re
from pathlib import Path
VERSION="CAMEO_LATERAL_V1"
FEEDS_H=True; CAN_DECIDE_H=False; MUTATES_CANON=False
PROFILES={
 "institucional":("institucion","regimen","constitucion","gobierno","estado","parlamento","congreso","tribunal","eleccion","coalicion","quorum","mocion","sancion"),
 "judicial":("tribunal","juez","corte","amparo","demanda","litigio","sentencia","constitucional","judicial"),
 "legislativo":("parlamento","congreso","senado","diputado","ley","mocion","quorum","votacion","comite","comisión"),
 "electoral":("eleccion","electoral","partido","voto","coalicion","campaña","circunscripcion"),
 "comercio_t_mec":("tmec","usmca","comercio","arancel","panel","controversia","energia","maiz","telecom","inversion"),
 "seguridad":("seguridad","policia","militar","emergencia","ciber","sancion","represion"),
 "diplomatico":("diplomacia","embajada","negociacion","mediacion","acuerdo","relaciones","cooperacion")
}
def _load():
 p=Path(__file__).with_name("cameo_codebook_lateral_v1.json")
 return json.loads(p.read_text(encoding="utf-8"))["codes"]
# Pesos CAMEO (motor alterno, experimento Napoleón): misma regla del canónico
# (PatternLibrary.get_weight): peso_efectivo = 0.5 + (peso - 0.5) * multiplicador.
# evidence_status unverified -> 0.4. Sin peso_equivalente -> 0.5 (neutral).
EVIDENCE_MULTIPLIERS={"primary_verified":1.0,"secondary_verified":0.7,"outdated":0.5,"unverified":0.4,"contestado_academicamente":0.4,"contradicted_partial":0.2,"contradicted":0.1}
def _peso_efectivo(d):
 pe=d.get("peso_equivalente")
 if pe is None: return 0.5
 mult=EVIDENCE_MULTIPLIERS.get(d.get("evidence_status"),1.0)
 return round(0.5+(float(pe)-0.5)*mult,6)
def _con_peso(c,d):
 return {"code":c,"token":d["token"],"label":d["label"],"peso_equivalente":d.get("peso_equivalente"),"evidence_status":d.get("evidence_status"),"peso_efectivo":_peso_efectivo(d)}
def classify(question):
 q=str(question or "").casefold(); scores={k:sum(1 for w in ws if w in q) for k,ws in PROFILES.items()}; m=max(scores.values()) if scores else 0
 active=[k for k,v in scores.items() if v==m and v>0]
 return active or ["institucional"]
def evaluate(question,texts=None):
 codes=_load(); profiles=classify(question); blob=" ".join(map(str,texts or [])) .casefold()
 hits=[]
 # explicit CAMEO code references in source/input
 for c,d in codes.items():
  if re.search(r"(?<!\d)"+re.escape(c)+r"(?!\d)",blob): hits.append((c,"explicit_code"))
 # question-profile vocabulary selects the relevant subfamily; no invented institutional token
 rootmap={"institucional":{"02","03","04","05","06","08","09","10","11","12","13","14","16","17"},"judicial":{"06","09","11","12","17"},"legislativo":{"02","03","04","10","11","12","13","14"},"electoral":{"02","03","08","10","11","12","13","14"},"comercio_t_mec":{"02","03","04","05","06","10","11","12","13","16"},"seguridad":{"08","09","13","15","16","17","19"},"diplomatico":{"02","03","04","05","06","07","08","10","12","13","16"}}
 roots=set().union(*(rootmap[p] for p in profiles)); selected=[(c,d) for c,d in codes.items() if d["root"] in roots]
 sel_con_peso=[_con_peso(c,d) for c,d in selected]
 pe_vals=[x["peso_efectivo"] for x in sel_con_peso if x["peso_efectivo"] is not None]
 peq_vals=[x["peso_equivalente"] for x in sel_con_peso if x["peso_equivalente"] is not None]
 return {"status":"EXECUTED","version":VERSION,"profiles":profiles,"available_codes":len(codes),"selected_code_count":len(selected),"explicit_hits":[{"code":c,"reason":r,**_con_peso(c,codes[c])} for c,r in hits],"selected_codes":sel_con_peso,"selected_peso_equivalente_mean":round(sum(peq_vals)/len(peq_vals),6) if peq_vals else None,"selected_peso_efectivo_mean":round(sum(pe_vals)/len(pe_vals),6) if pe_vals else None,"selected_peso_efectivo_sum":round(sum(pe_vals),6) if pe_vals else None,"feeds_H":True,"can_decide_H":False,"mutates_canonical":False,"role":"question_conditioned_lateral_institutional_taxonomy"}
