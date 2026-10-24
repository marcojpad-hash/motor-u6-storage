#!/usr/bin/env python3
"""Interrelación externa extensible para V15.3/V0.9.

Contrato: 244/R732 permanecen intactos. Esta capa solo representa y relaciona
activaciones exteriores. No genera familias, no añade evidencia y no alimenta H.
"""
from collections import defaultdict
import hashlib, json
from pathlib import Path

VERSION = "INTERRELACION_EXTENSIBLE_V0.1"
ALIMENTA_H = False

class InterrelationEngine:
    def __init__(self):
        self.lights = {}
        self.activations = []
        self.failures = []

    def register(self, token, branch, stereotype=None, axes=()):
        if not token or not branch:
            raise ValueError("FAIL_INVALID_LIGHT")
        if token in self.lights:
            old = self.lights[token]
            new = {"token":token,"branch":branch,"stereotype":stereotype,"axes":tuple(sorted(set(axes)))}
            if old != new:
                raise ValueError("FAIL_CONFLICTING_REGISTRATION:" + token)
            return
        self.lights[token] = {"token":token,"branch":branch,"stereotype":stereotype,"axes":tuple(sorted(set(axes)))}

    def activate(self, cut, token, strength=None, source="external"):
        if token not in self.lights:
            self.failures.append({"code":"FAIL_UNKNOWN_TOKEN","token":token,"cut":cut})
            raise KeyError("FAIL_UNKNOWN_TOKEN:" + token)
        self.activations.append({"cut":cut,"token":token,"strength":strength,"source":source})

    def cut_hyperrelations(self):
        by_cut = defaultdict(list)
        for a in self.activations: by_cut[a["cut"]].append(a)
        out=[]
        for cut in sorted(by_cut, key=str):
            unique={}
            for a in by_cut[cut]: unique.setdefault(a["token"], a)
            tokens=sorted(unique)
            if len(tokens)>=2:
                out.append({"cut":cut,"tokens":tokens,
                    "branches":sorted({self.lights[t]["branch"] for t in tokens}),
                    "axes":sorted({x for t in tokens for x in self.lights[t]["axes"]}),
                    "type":"COACTIVATION","unit_evidence":1})
        return out

    def token_trajectories(self):
        by=defaultdict(set)
        for a in self.activations: by[a["token"]].add(a["cut"])
        return {t:sorted(c,key=str) for t,c in sorted(by.items())}

    def movement(self):
        by=defaultdict(set)
        for a in self.activations: by[a["cut"]].add(a["token"])
        cuts=sorted(by,key=str); out=[]
        for prev,cur in zip(cuts,cuts[1:]):
            A,B=by[prev],by[cur]
            out.append({"from":prev,"to":cur,"persist":sorted(A&B),"enter":sorted(B-A),"exit":sorted(A-B)})
        return out

    def venn(self, cut):
        result=defaultdict(set)
        for a in self.activations:
            if a["cut"]!=cut: continue
            light=self.lights[a["token"]]
            for axis in light["axes"]: result[axis].add(a["token"])
            result["branch:"+light["branch"]].add(a["token"])
        return {k:sorted(v) for k,v in sorted(result.items())}

    def run(self):
        return {"hyperrelations":self.cut_hyperrelations(),
                "trajectories":self.token_trajectories(),
                "movement":self.movement(),
                "venn_sets":{str(c):self.venn(c) for c in sorted({a["cut"] for a in self.activations},key=str)},
                "raw_activations":list(self.activations),
                "unique_tokens":sorted(self.lights),
                "failures":list(self.failures),
                "ALIMENTA_H":False}

def run_external(external_lights, cuts):
    """Run only on explicitly supplied external taxonomy/activations.

    Supported activation forms:
      light: {token, branch, stereotype, axes}
      cut: {id, external_activations:[token | {token,strength,source}]}
    """
    eng=InterrelationEngine()
    for light in external_lights or []:
        eng.register(light["token"], light["branch"], light.get("stereotype"), light.get("axes",()))
    for c in cuts or []:
        cid=c.get("id")
        for item in c.get("external_activations",[]) or []:
            if isinstance(item,str): token=item; strength=None; source="external"
            else: token=item["token"]; strength=item.get("strength"); source=item.get("source","external")
            eng.activate(cid,token,strength,source)
    out=eng.run()
    out["taxonomy_sha256"]=hashlib.sha256(json.dumps(list(external_lights or []),ensure_ascii=False,sort_keys=True).encode()).hexdigest()
    out["config_sha256"]=hashlib.sha256(VERSION.encode()).hexdigest()
    return out


def assert_monotonic_extension(base_lights, base_cuts, added_light, added_activations):
    """Adding a member cannot alter existing relations/evidence; it may add relations."""
    base=run_external(base_lights,base_cuts)
    lights=list(base_lights)+[added_light]
    cuts=[]
    for c in base_cuts:
        cc=dict(c); cc["external_activations"]=list(c.get("external_activations",[]) or [])
        cuts.append(cc)
    for cut,token in added_activations:
        for cc in cuts:
            if cc.get("id")==cut: cc["external_activations"].append(token)
    ext=run_external(lights,cuts)
    base_h=[x for x in base["hyperrelations"]]
    ext_h=[x for x in ext["hyperrelations"]]
    existing=set(t for t in base["unique_tokens"])
    # Project extended relations back onto the old member set and recompute
    # their structural fields; adding a member must not mutate the old relation.
    projected=[]
    for h in ext_h:
        toks=[t for t in h["tokens"] if t in existing]
        if len(toks)<2: continue
        projected.append({"cut":h["cut"],"tokens":toks,
            "branches":sorted({base_l["branch"] for base_l in base_lights if base_l["token"] in toks}),
            "axes":sorted({a for base_l in base_lights if base_l["token"] in toks for a in base_l.get("axes",[])}),
            "type":h["type"],"unit_evidence":1})
    unchanged = sorted(base_h,key=lambda x:(str(x["cut"]),x["tokens"])) == sorted(projected,key=lambda x:(str(x["cut"]),x["tokens"]))
    return {"ok":unchanged,"base":base,"extended":ext,"existing_relations_unchanged":unchanged,
            "new_member":added_light["token"],"principle":"monotonic_extensibility"}
