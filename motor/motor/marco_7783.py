"""Zonas del marco 7783. No es el catalogo literario de 210141.
Una zona es un reparto de las seis funciones. La visita suma calor.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, List

N = 7783
STORE = Path(__file__).resolve().parent / "zonas_7783.json"

def _estado(tokens: List[str], cumulo: Dict[str, List[str]], nombre: str) -> int:
    if not tokens:
        return 0
    if any(nombre in fn for fn in cumulo.values()):
        return 2
    return 1

def zona_de(reparto: Dict[str, Any]) -> int:
    fn = reparto.get("funciones") or {}
    cumulo = reparto.get("cumulo") or {}
    acc = 0
    for i, nombre in enumerate(("leon", "sol", "tierra", "marte", "balanza", "luna")):
        acc = acc * 3 + _estado(fn.get(nombre) or [], cumulo, nombre)
    return acc % N

def visitar(por_corte: List[Dict[str, Any]]) -> Dict[str, Any]:
    prev = {}
    if STORE.is_file():
        try:
            prev = json.loads(STORE.read_text(encoding="utf-8"))
        except Exception:
            prev = {}
    calor = prev.get("calor") or {}
    visitas = []
    for c in por_corte or []:
        z = zona_de(c)
        key = str(z)
        calor[key] = int(calor.get(key) or 0) + 1
        visitas.append({"corte": c.get("corte"), "zona": z, "calor": calor[key]})
    STORE.write_text(json.dumps({"n": N, "calor": calor}, ensure_ascii=False), encoding="utf-8")
    ranking = sorted(calor.items(), key=lambda kv: -kv[1])[:8]
    return {"status": "EXECUTED", "n_zonas": N, "visitas": visitas, "mas_calientes": [{"zona": int(k), "calor": v} for k, v in ranking], "can_decide_H": False}
