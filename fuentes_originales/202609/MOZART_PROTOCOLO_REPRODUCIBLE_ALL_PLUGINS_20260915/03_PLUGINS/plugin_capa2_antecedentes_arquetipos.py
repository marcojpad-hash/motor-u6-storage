#!/usr/bin/env python3
"""PLUGIN_CAPA2_ANTECEDENTES_ARQUETIPOS

Segunda capa lateral (NO toca Engine_V5 ni patterns_final_v14).

Para qué:
  Reconocimiento de patrones contra un catálogo de familias-tipo
  (histórica / vínculo-amoroso / estilo-psic), con ventana de edad /
  periodicidad: "ya se ve a los 15" vs "cuaja a los 50".

No es:
  - diagnóstico clínico
  - buffet de 3 apuestas (el oficio sigue: 1 familia + 1 descarte)
  - predicción de evento cerrado
  - merge al 244

Entrada típica:
  pinchos_por_corte: {"A": ["ambicion", "fama", ...], "B": [...]}
  edad_aprox_por_corte: {"A": 16, "B": 24, ...}  # opcional
  catalogo_path: JSON del catálogo (default al lado de este archivo)

Salida:
  matches por capa, early_signal (¿ya se veía temprano?),
  sugerencia_una_familia (candidato), descartes_sugeridos,
  evidence_status=unverified hasta calibrar.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set

HERE = Path(__file__).resolve().parent
DEFAULT_CATALOG = HERE / "catalogo_capa2_familias_semilla.json"


def _norm_tokens(xs: Sequence[Any]) -> Set[str]:
    out: Set[str] = set()
    for x in xs:
        if isinstance(x, str):
            out.add(x.strip().lower())
        elif isinstance(x, (list, tuple)) and x:
            out.add(str(x[0]).strip().lower())
        elif isinstance(x, dict):
            t = x.get("token") or x.get("name") or x.get("id")
            if t:
                out.add(str(t).strip().lower())
    return out


def load_catalog(path: Optional[Path] = None) -> Dict[str, Any]:
    p = Path(path) if path else DEFAULT_CATALOG
    return json.loads(p.read_text(encoding="utf-8"))


def _score_family(tokens: Set[str], fam: Dict[str, Any]) -> Dict[str, Any]:
    favor = _norm_tokens(fam.get("pinchos_favor") or [])
    contra = _norm_tokens(fam.get("pinchos_contra") or [])
    hit_f = sorted(tokens & favor)
    hit_c = sorted(tokens & contra)
    # score simple: favor - 0.5*contra, normalizado por tamaño de favor
    den = max(len(favor), 1)
    score = (len(hit_f) - 0.5 * len(hit_c)) / den
    return {
        "id": fam.get("id"),
        "capa": fam.get("capa"),
        "nombre": fam.get("nombre"),
        "score": round(score, 4),
        "hits_favor": hit_f,
        "hits_contra": hit_c,
        "ventana_edad": fam.get("ventana_edad"),
        "antecedente_tipo": fam.get("antecedente_tipo"),
        "nota": fam.get("nota"),
    }


def _early_signal(
    pinchos_por_corte: Dict[str, Sequence[Any]],
    edad_aprox: Optional[Dict[str, Any]],
    fam: Dict[str, Any],
) -> Dict[str, Any]:
    """¿Los pinchos de la familia ya pegan temprano?

    Edad NO forzosa: sin edad_aprox solo se mira orden de cortes.
    Virtuoso temprano vs arranque tardío = cola opcional, no requisito.
    """
    favor = _norm_tokens(fam.get("pinchos_favor") or [])
    cortes = list(pinchos_por_corte.keys())
    early = []
    for cid in cortes:
        toks = _norm_tokens(pinchos_por_corte[cid])
        hit = sorted(toks & favor)
        if not hit:
            continue
        edad = None
        if edad_aprox and cid in edad_aprox:
            try:
                edad = float(edad_aprox[cid])
            except (TypeError, ValueError):
                edad = None
        early.append({"corte": cid, "edad": edad, "hits": hit, "n": len(hit)})
    vmin = (fam.get("ventana_edad") or {}).get("ya_se_ve_desde")
    ya = False
    if early:
        # si hay hits en el primer tercio de cortes, o edad <= ya_se_ve_desde
        n = len(cortes)
        first = set(cortes[: max(1, n // 3)])
        if any(e["corte"] in first for e in early):
            ya = True
        if vmin is not None:
            for e in early:
                if e["edad"] is not None and e["edad"] <= float(vmin):
                    ya = True
    return {
        "ya_se_ve_temprano": ya,
        "evidencias": early,
        "lectura": (
            "señal temprana tipo 'Alejandro ~15–16'"
            if ya
            else "cuaja más tarde o aún no asoma (tipo 'César tarda')"
        ),
    }


def leer(
    pinchos_por_corte: Dict[str, Sequence[Any]],
    edad_aprox_por_corte: Optional[Dict[str, Any]] = None,
    catalogo_path: Optional[str] = None,
    top_k: int = 3,
) -> Dict[str, Any]:
    cat = load_catalog(Path(catalogo_path) if catalogo_path else None)
    # tokens globales del freeze
    all_toks: Set[str] = set()
    for v in pinchos_por_corte.values():
        all_toks |= _norm_tokens(v)

    por_capa: Dict[str, List[Dict[str, Any]]] = {}
    for capa, familias in (cat.get("capas") or {}).items():
        scored = []
        for fam in familias:
            fam = dict(fam)
            fam["capa"] = capa
            row = _score_family(all_toks, fam)
            row["early"] = _early_signal(pinchos_por_corte, edad_aprox_por_corte, fam)
            scored.append(row)
        scored.sort(key=lambda r: r["score"], reverse=True)
        por_capa[capa] = scored[:top_k]

    # candidato único transversal (max score entre capas)
    flat = [r for rows in por_capa.values() for r in rows]
    flat.sort(key=lambda r: r["score"], reverse=True)
    sugerida = flat[0] if flat and flat[0]["score"] > 0 else None
    descartes = [r["id"] for r in flat[1:4] if r["score"] > 0]

    return {
        "plugin": "PLUGIN_CAPA2_ANTECEDENTES_ARQUETIPOS",
        "version": 1,
        "engine_tocado": False,
        "evidence_status": "unverified",
        "regla_oficio": (
            "Este plugin SUGIERE. El cierre sigue siendo "
            "1 familia_unica + 1 descarte + 1 frase. "
            "No uses el top_k como buffet de apuestas."
        ),
        "tokens_campo": sorted(all_toks),
        "por_capa": por_capa,
        "sugerencia_una_familia": sugerida,
        "descartes_sugeridos": descartes,
        "periodicidad": {
            "idea": (
                "Compara early_signal entre familias: "
                "misma estructura puede asomar adolescente (Alejandro) "
                "o cuajar adulto maduro (César)."
            )
        },
    }


if __name__ == "__main__":
    # smoke: pinchos estilo freeze Wilde temprano
    demo = {
        "A": ["ambicion", "fama", "creador", "arte_prestigio"],
        "D": ["trickster", "camaleon", "fama", "extraversion"],
        "E": ["camaleon", "trickster", "escritores_creativos", "oratoria"],
        "F": ["ambicion", "perdida_seres_queridos", "camaleon"],
    }
    edades = {"A": 14, "D": 19, "E": 20, "F": 21}
    out = leer(demo, edades)
    print(json.dumps(out, ensure_ascii=False, indent=2)[:2500])
