"""Sombrero blanco del token nuevo. No lo vuelve canon. Lo deja en StinkBox."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, List

STORE = Path(__file__).resolve().parent / "stinkbox_tokens_descubiertos.json"

def revisar(holes: Dict[str, Any], case_id: str) -> Dict[str, Any]:
    nuevos: List[Dict[str, Any]] = []
    for cid, rec in (holes or {}).items():
        if not isinstance(rec, dict):
            continue
        for item in rec.get("fuera_catalogo") or []:
            eq = item.get("equivalente")
            nuevos.append({
                "case_id": case_id,
                "corte": item.get("corte") or cid,
                "eje": item.get("eje"),
                "token": item.get("token"),
                "equivalente": eq,
                "estado": "EQUIVALENTE_UNICO" if eq else "PENDIENTE_REVISION",
                "entra_a_canon": False,
            })
    prev = []
    if STORE.is_file():
        try:
            prev = json.loads(STORE.read_text(encoding="utf-8")).get("tokens") or []
        except Exception:
            prev = []
    vistos = {(x.get("token"), x.get("case_id"), x.get("corte")) for x in prev}
    for n in nuevos:
        key = (n["token"], n["case_id"], n["corte"])
        if key not in vistos:
            prev.append(n)
            vistos.add(key)
    STORE.write_text(json.dumps({"tokens": prev}, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"status": "EXECUTED", "can_decide_H": False, "n_esta_corrida": len(nuevos), "n_stinkbox": len(prev), "esta_corrida": nuevos}
