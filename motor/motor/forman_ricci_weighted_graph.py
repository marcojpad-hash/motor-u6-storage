"""Exact 1-dimensional weighted Forman-Ricci curvature on an explicit graph.

Input graph contract:
  nodes: {node_id: positive finite node weight}
  edges: [{"u": node_id, "v": node_id, "weight": positive finite edge weight}]

For edge e=(u,v), no 2-cells are present:
F(e)=w(e)*(w(u)/w(e)+w(v)/w(e)
  - sum_{e'~u,e'!=e} w(u)/sqrt(w(e)*w(e'))
  - sum_{e'~v,e'!=e} w(v)/sqrt(w(e)*w(e')))
This primitive is deliberately not wired to P/A/C cuts: those do not specify a
validated graph topology or node/edge weights. No claim of lab integration.
"""
from __future__ import annotations
import math
from typing import Any, Mapping, Sequence

def forman_ricci(nodes: Mapping[str, float], edges: Sequence[Mapping[str, Any]]) -> dict:
    nw = {str(k): float(v) for k, v in nodes.items()}
    if not nw or any(not math.isfinite(w) or w <= 0 for w in nw.values()):
        raise ValueError("node weights must be nonempty, positive, finite")
    es=[]; seen=set()
    for i,e in enumerate(edges):
        if not all(k in e for k in ("u","v","weight")):
            raise ValueError(f"edge {i} must provide u, v, weight")
        u,v=str(e["u"]),str(e["v"]); w=float(e["weight"])
        if u==v or u not in nw or v not in nw: raise ValueError(f"edge {i} has invalid endpoints")
        if not math.isfinite(w) or w<=0: raise ValueError(f"edge {i} weight must be positive finite")
        key=frozenset((u,v))
        if key in seen: raise ValueError("parallel/duplicate edges are not supported by this contract")
        seen.add(key); es.append({"u":u,"v":v,"weight":w})
    out=[]
    for i,e in enumerate(es):
        u,v,w=e["u"],e["v"],e["weight"]
        value=nw[u]+nw[v]
        for j,f in enumerate(es):
            if i==j: continue
            if f["u"]==u or f["v"]==u: value -= nw[u]*math.sqrt(w/f["weight"])
            if f["u"]==v or f["v"]==v: value -= nw[v]*math.sqrt(w/f["weight"])
        if not math.isfinite(value): raise ArithmeticError("non-finite Forman curvature")
        out.append({"u":u,"v":v,"weight":w,"forman_ricci":value})
    return {"status":"COMPUTED_EXPLICIT_WEIGHTED_GRAPH", "dimension":1, "n_nodes":len(nw), "n_edges":len(es),
            "curvatures":out, "mean":(sum(x["forman_ricci"] for x in out)/len(out) if out else None),
            "topology_source":"explicit_input", "integrated_into_H":False}
