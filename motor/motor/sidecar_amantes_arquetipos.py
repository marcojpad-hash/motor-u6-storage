#!/usr/bin/env python3
"""SIDECAR_AMANTES_ARQUETIPOS — subcapa post-tokens (como guerra)

Namespace: ama.*
Candados: NO F/244/Engine/FREEZE. Alimenta_H=NO.
NO se prende junto al bus principal: solo POST + gatillo de vínculo.
Sin gatillo → LATENCIA (no inventa romance).
"""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set

HERE = Path(__file__).resolve().parent
DEFAULT_REG = HERE / "registro_sidecar_amantes_arquetipos.json"

GATILLOS_DEFAULT = {
    "vinculo", "deseo", "celos", "triangulo", "duelo", "amante", "pasion",
    "abandono", "reconciliacion", "ruptura", "posesion", "idealizacion",
    "amor", "odio", "celos", "infidelidad", "secreto", "salvacion",
    "prohibido", "alianza",
}


def _snake(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower().replace("ñ", "n")
    s = re.sub(r"[^a-z0-9_]+", "_", s)
    return re.sub(r"_+", "_", s).strip("_")


def _norm(xs: Sequence[Any]) -> Set[str]:
    out: Set[str] = set()
    for x in xs:
        if isinstance(x, str):
            out.add(_snake(x))
        elif isinstance(x, (list, tuple)) and x:
            out.add(_snake(str(x[0])))
        elif isinstance(x, dict):
            t = x.get("token") or x.get("name") or x.get("id")
            if t:
                out.add(_snake(str(t)))
    return out


def load_registro(path: Optional[Path] = None) -> Dict[str, Any]:
    return json.loads((path or DEFAULT_REG).read_text(encoding="utf-8"))


def _campo_desde_entradas(
    pinchos_por_corte: Optional[Dict[str, Sequence[Any]]],
    luces_activas: Optional[Iterable[str]],
    hechos: Optional[Sequence[str]],
) -> Set[str]:
    campo: Set[str] = set()
    if pinchos_por_corte:
        for v in pinchos_por_corte.values():
            campo |= _norm(v)
    if luces_activas:
        for L in luces_activas:
            campo.add(_snake(str(L)))
            # also bare leaf
            if "." in str(L):
                campo.add(_snake(str(L).split(".")[-1]))
    if hechos:
        campo |= _norm(hechos)
    return campo


def hay_gatillo(campo: Set[str], gatillos: Optional[Iterable[str]] = None) -> bool:
    gats = set(gatillos or GATILLOS_DEFAULT)
    # prefix matches vin./ama. already in campo leaves
    if any(x.startswith("vin") or x.startswith("ama") for x in campo):
        return True
    return bool(campo & {_snake(g) for g in gats})


def leer(
    pinchos_por_corte: Optional[Dict[str, Sequence[Any]]] = None,
    luces_activas: Optional[Sequence[str]] = None,
    hechos: Optional[Sequence[str]] = None,
    forzar: bool = False,
    top_n: int = 8,
    registro_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Evalúa sidecar amantes.

    forzar=False (default): sin gatillo → modo LATENCIA, sin prender arquetipos.
    """
    reg = load_registro(Path(registro_path) if registro_path else None)
    items = ((reg.get("packs") or {}).get("ama") or {}).get("items") or []
    campo = _campo_desde_entradas(pinchos_por_corte, luces_activas, hechos)
    trigger = forzar or hay_gatillo(campo)

    base = {
        "plugin": "SIDECAR_AMANTES_ARQUETIPOS",
        "namespace": "ama",
        "subcapa": True,
        "orden": "POST_TOKENS_PRINCIPALES",
        "engine_tocado": False,
        "candados": reg.get("candados"),
        "politica_activacion": reg.get("politica_activacion"),
        "n_catalogo": len(items),
        "Alimenta_H": "NO",
    }

    if not trigger:
        return {
            **base,
            "modo": "LATENCIA",
            "activado": False,
            "motivo": "sin_gatillo_vinculo_deseo_celos_triangulo_duelo",
            "encendidos": [],
            "luces": [],
        }

    scored = []
    for it in items:
        fav = it.get("pesos_favor") or {}
        blob = _norm([it.get("id"), it.get("token_gemini"), *fav.keys(), *(it.get("luces_sugeridas") or [])])
        # explode id pieces
        iid = str(it.get("id") or "")
        blob |= _norm(iid.replace(".", " ").replace("_", " ").split())
        hits = sorted(blob & campo)
        score = round(len(hits) / max(len(blob), 1), 4)
        if hits or forzar:
            scored.append({
                "id": it.get("id"),
                "token_gemini": it.get("token_gemini"),
                "hits": hits,
                "score": score,
                "Alimenta_H": "NO",
                "estado": "ON" if hits else "LATENCIA_FORZADA",
            })
    scored.sort(key=lambda r: (-r["score"], r["id"] or ""))
    enc = [r for r in scored if r["hits"]][:top_n]

    return {
        **base,
        "modo": "ACTIVO_POST_PRINCIPAL",
        "activado": True,
        "motivo": "gatillo_o_forzado",
        "campo_n": len(campo),
        "encendidos": enc,
        "luces": [r["id"] for r in enc],
        "inventario_n": len(items),
    }


if __name__ == "__main__":
    # sin gatillo → LATENCIA
    a = leer({"A": ["aprendizaje", "matematicas"]})
    # con gatillo celos/deseo
    b = leer({"A": ["celos", "deseo", "triangulo"], "B": ["abandono"]})
    print(json.dumps({
        "sin_gatillo": {"modo": a["modo"], "activado": a["activado"]},
        "con_gatillo": {"modo": b["modo"], "activado": b["activado"], "luces": b["luces"][:6]},
        "candados": b["candados"],
    }, ensure_ascii=False, indent=2))
