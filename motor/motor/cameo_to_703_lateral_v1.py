"""CAMEO -> existing 703-token lateral bridge.

Only uses explicit CAMEO code -> existing 703 token mappings. No new weights,
no new 244 patterns, no canonical mutation. Event detection is deterministic
and limited to explicit Spanish lexical triggers declared in CODE_TRIGGERS.
"""
from __future__ import annotations
import json, re, unicodedata
from pathlib import Path
VERSION="CAMEO_TO_703_LATERAL_V1"

CODEBOOK_FILE="cameo_to_703_lateral_v1.json"

def _load_config():
    d=json.loads((Path(__file__).with_name(CODEBOOK_FILE)).read_text(encoding="utf-8"))
    return d.get("code_to_token") or {}, d.get("code_triggers_es") or {}

def _norm(s):
    s=unicodedata.normalize('NFKD',str(s)).encode('ascii','ignore').decode().casefold()
    return re.sub(r'\s+',' ',s)

def _validate_targets(patterns):
    code_to_token,_=_load_config()
    vocab=set()
    for p in (patterns or {}).values():
        vocab |= set((p.get('tokens_favor') or {})) | set((p.get('tokens_contra') or {}))
    return {c:t for c,t in code_to_token.items() if t in vocab}

def detect(texts, patterns):
    valid=_validate_targets(patterns)
    _, code_triggers=_load_config()
    events=[]
    for text in texts or []:
        blob=_norm(text)
        for code, triggers in code_triggers.items():
            if code not in valid:
                continue
            matched=next((tr for tr in triggers if _norm(tr) in blob), None)
            if matched:
                token=valid.get(code)
                events.append({"code":code,"trigger":matched,"token":token,"text":str(text)})
    # one event per code/text; no invented repetition
    seen=set(); out=[]
    for e in events:
        k=(e['code'],e['text'])
        if k not in seen:
            out.append(e); seen.add(k)
    return out, valid

def candidate_scores(events, candidates, patterns):
    scores={c:0.0 for c in candidates}
    details={c:{"favor_hits":[],"contra_hits":[]} for c in candidates}
    for e in events:
        tok=e.get('token')
        if not tok: continue
        for c in candidates:
            p=patterns.get(c,{})
            fav=set((p.get('tokens_favor') or {}).keys())
            con=set((p.get('tokens_contra') or {}).keys())
            if tok in fav:
                scores[c]+=1.0
                details[c]['favor_hits'].append({"token":tok,"code":e['code']})
            elif tok in con:
                scores[c]-=1.0
                details[c]['contra_hits'].append({"token":tok,"code":e['code']})
    # keep only positive margin: no weight, just count difference
    scores={c:max(0.0,v) for c,v in scores.items()}
    vals=list(scores.values())
    return scores, details, bool(vals) and max(vals)>min(vals)

def run(cuts, candidates, patterns):
    per_cut={}; all_events=[]
    for cut in cuts or []:
        events,_=detect(cut.get('facts') or [],patterns)
        per_cut[str(cut.get('id'))]=events
        all_events.extend(events)
    scores,details,disc=candidate_scores(all_events,candidates,patterns)
    return {"status":"EXECUTED","version":VERSION,"events":all_events,"events_by_cut":per_cut,
            "candidate_scores":scores,"candidate_details":details,
            "feeds_H":disc,"can_decide_H":False,"mutates_canonical":False,
            "mapping":"CAMEO_CODE_TO_EXISTING_703_TOKEN_ONLY","new_weights":False}
