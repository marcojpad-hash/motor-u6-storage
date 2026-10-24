#!/usr/bin/env python3
"""Familia lateral mortalidad. No alimenta H ni ranking; no modifica el canon."""
from __future__ import annotations
import re, unicodedata, datetime
from typing import Any

def fold(s:str)->str:
 return ''.join(c for c in unicodedata.normalize('NFD', (s or '').lower()) if unicodedata.category(c)!='Mn')

def classify_death(text:str, case_subject:str|None=None, z90_date:str|None=None)->list[dict[str,Any]]:
 t=text or ''; f=fold(t); out=[]
 def emit(token, owner, match, status='CLASSIFIED', note=''):
  out.append({'token':token,'owner_axis':owner,'en_vocabulario_244':False,'status':status,'match':match,'note':note,'source_text':t[:200]})
 # Preserve local negation, do not produce positive death event.
 death=re.search(r'\b(muere|mueren|murio|murieron|muerte|fallece|fallecen|fallecio|fallecieron|morir|morira|moriran)\b', f)
 if death and re.search(r'\b(no|nunca|jamas|sin)\s+(?:\w+\s+){0,2}(muere|mueren|murio|murieron|muerte|fallece|fallecen|fallecio|fallecieron)\b', f):
  emit('mort_evento_negado','UNRESOLVED',death.group(0),'DISCARDED_NEGATION','R2: negación local conservada'); return out
 # Non-event finitude and representation precede generic lexical death.
 if re.search(r'\b(teme|temia|temor|miedo|piensa|pensar|conciencia|testamento|legado|finitud|morir)\b',f) and re.search(r'\b(muerte|morir|morir\w*|morira|moriran)\b',f):
  emit('mort_finitud_anticipada','P','muerte/morir','ALLOWED_PRE_Z90','Conciencia/temor anticipatorio; no evento')
  return out
 if re.search(r'\b(escribe|escribio|escribir|pinta|pinto|estudia|estudio|trata|tratado|investiga|representa|poema|novela|cuadro)\b',f) and re.search(r'\b(muerte|morir)\b',f):
  emit('mort_tema_representacion','C','muerte','CLASSIFIED','Representación/estudio; no evento')
  return out
 if not death: return out
 # Resolve explicit person/relationship before broad war/epidemic context terms.
 # identify other person in syntactic subject / possessive relationship
 other_patterns=[r'\bsu\s+(?:padre|madre|hijo|hija|hermano|hermana|esposo|esposa|marido|mujer|amigo|amiga)\b',r'\bla muerte de\s+[a-z][\w -]+',r'\bmuert[oa] de\s+[a-z][\w -]+',r'\bmuere\s+(?:el|la|los|las|un|una)\s+(?:rey|reina|maestro|maestra|disc[ií]pulo|disc[ií]pula|enemigo|rival|antagonista|general|emperador|emperatriz|presidente|jefe)\b']
 other=any(re.search(p,f) for p in other_patterns)
 # post-verb subject phrase (e.g. Muere su padre) and pre-verb possessive phrase (Su hermano muere)
 if re.search(r'\bmuere[n]?\s+(?:su\s+)?(?:padre|madre|hijo|hija|hermano|hermana|rey|reina|maestro|maestra|disc[ií]pulo|disc[ií]pula|enemigo|rival|antagonista)\b',f): other=True
 if re.search(r'\b(?:su\s+(?:padre|madre|hijo|hija|hermano|hermana|esposo|esposa|marido|mujer)|el\s+(?:rey|maestro|disc[ií]pulo|enemigo|rival|antagonista))\s+muere\b',f): other=True
 if other:
  sub='vinculo_cercano' if re.search(r'\b(padre|madre|hijo|hija|hermano|hermana|esposo|esposa|marido|mujer|amigo|amiga)\b',f) else ('antagonista' if re.search(r'\b(enemigo|rival|antagonista)\b',f) else ('autoridad_figura' if re.search(r'\b(rey|reina|maestro|maestra|disc[ií]pulo|disc[ií]pula|general|emperador|emperatriz|presidente|jefe)\b',f) else 'vinculo_no_resuelto'))
  emit('mort_evento_ajeno_'+sub,'A',death.group(0),'CLASSIFIED','Muerte de persona distinta al sujeto; no pasar a cuerpo_arco')
  return out
 # Collective event/context, only after explicit personal referent was checked.
 if re.search(r'\b(miles|cientos|millones|multitud|poblacion|soldados|civiles|victimas|masacre|hambruna|epidemia|peste|guerra)\b',f):
  emit('mort_contexto_colectivo','C',death.group(0),'CLASSIFIED','Mortalidad colectiva/contextual; no asignada a P')
  return out
 # resolve own only with explicit case subject match; generic subject without referent stays unresolved
 own=False
 if case_subject and re.search(r'\b'+re.escape(fold(case_subject))+r'\b',f):
  own=True
 elif re.match(r'^\s*[A-ZÁÉÍÓÚÑ][\wÁÉÍÓÚÑáéíóúñ.-]+\s+(?:muere|murio|fallece|fallecio)\b',t):
  # explicit narrative subject at sentence start (e.g. Casanova); still record what resolved it
  own=True
 if own:
  status='CLASSIFIED'
  note='Sujeto resuelto explícitamente; cuerpo_arco puede recibir cuerpo_muerte_propia solo tras guardia Z90'
  if not z90_date:
   status='TORTUGAS_MISSING_Z90'; note='Guardia fail-closed: falta Z90, no se entrega evento propio a cuerpo_arco'
  # Event date found in text, or supplied by case context if exact date is not embedded.
  years=re.findall(r'\b(1[0-9]{3}|20[0-9]{2})\b',t)
  if z90_date and years:
   try:
    if datetime.date(int(years[-1]),1,1)>datetime.date.fromisoformat(z90_date): status='REJECTED_POST_Z90'; note='R3: evento posterior a Z90; solo validación, no insumo pre-freeze'
   except ValueError: pass
  emit('mort_evento_propio','P',death.group(0),status,note)
  return out
 emit('mort_sujeto_no_resuelto','UNRESOLVED',death.group(0),'TORTUGAS','R1: no se rellena sujeto; no se asume evento propio')
 return out
