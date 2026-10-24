"""Traza semiotica. No escribe H. Marca, no anula."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, List

def _toks(corte: Dict[str, Any]) -> List[str]:
    out = []
    for eje in ("P", "A", "C"):
        for item in corte.get(eje) or []:
            out.append(str(item[0] if isinstance(item, (list, tuple)) else item))
    return out

def revisar(case: Dict[str, Any], holes: Dict[str, Any]) -> Dict[str, Any]:
    cat = Path(__file__).resolve().parent / "patterns_final_v14.json"
    familias = {}
    favor_por_token = {}
    contra_por_token = {}
    if cat.is_file():
        lib = json.loads(cat.read_text(encoding="utf-8"))
        for fam, p in lib.items():
            if not isinstance(p, dict):
                continue
            for t in (p.get("tokens_favor") or {}):
                familias.setdefault(t, set()).add(fam)
                favor_por_token.setdefault(t, set()).add(fam)
            for t in (p.get("tokens_contra") or {}):
                familias.setdefault(t, set()).add(fam)
                contra_por_token.setdefault(t, set()).add(fam)
    disparadores = []
    filas = []
    for c in case.get("cuts") or []:
        toks = _toks(c)
        for t in toks:
            fams = familias.get(t, set())
            otros = set()
            for u in toks:
                if u != t:
                    otros |= familias.get(u, set())
            aislado = bool(fams) and not (fams & otros)
            nombre_familia = t in (familias and {}) or ("_" in t and t not in familias)
            if aislado:
                disparadores.append({"token": t, "corte": c.get("id"), "motivo": "SIGNO_AISLADO", "capa": "contexto"})
            if t not in familias:
                disparadores.append({"token": t, "corte": c.get("id"), "motivo": "SIGNIFICANTE_SIN_OBJETO", "capa": "catalogo"})
            filas.append({"token": t, "corte": c.get("id"), "aislado": aislado, "en_catalogo": t in familias, "nombre_familia": nombre_familia})
    votos={}
    votos_favor={}
    votos_contra={}
    for row in filas:
        t = row["token"]
        w = 0.4 if row["aislado"] else 1.0
        for fam in favor_por_token.get(t, ()):
            votos_favor[fam]=votos_favor.get(fam,0.0)+w
        for fam in contra_por_token.get(t, ()):
            votos_contra[fam]=votos_contra.get(fam,0.0)+w
    for fam in set(votos_favor) | set(votos_contra):
        votos[fam] = votos_favor.get(fam, 0.0) - votos_contra.get(fam, 0.0)
    return {
        "status": "EXECUTED",
        "can_decide_H": False,
        "feeds_predictor": False,
        "n_filas": len(filas),
        "n_disparadores": len(disparadores),
        "disparadores": disparadores[:12],
        "por_familia": {k: {"score": round(v,6), "favor": round(votos_favor.get(k,0.0),6), "contra": round(votos_contra.get(k,0.0),6)} for k,v in votos.items()},
    }
