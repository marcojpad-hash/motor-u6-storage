#!/usr/bin/env python3
"""SIDECAR_LUCES_GEMINI_PACKS — cableado Capa 2 con hilado temporal

Packs: soc.* / hist.* / ar.* / sit.*
Candados: NO F / 244 / Engine / FREEZE. Alimenta_H = NO.

Hilado: activación POR CORTE → sidecar_trazabilidad_temporal
estados ON / PARPADEO / NO_APARECIDO_AUN / OFF (k=2 por defecto; PATCH 004: antes LATENCIA).
PARPADEO = lo de un corte previo sigue vivo sin reaparición inmediata.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set

HERE = Path(__file__).resolve().parent
DEFAULT_REG = HERE / "registro_luces_gemini_packs.json"
K_HILADO = 2


def _norm(xs: Sequence[Any]) -> Set[str]:
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


def load_registro(path: Optional[Path] = None) -> Dict[str, Any]:
    p = Path(path) if path else DEFAULT_REG
    return json.loads(p.read_text(encoding="utf-8"))


def _item_blob(item: Dict[str, Any]) -> Set[str]:
    parts: List[str] = [
        str(item.get("id") or ""),
        str(item.get("token_gemini") or ""),
        str(item.get("pack") or ""),
    ]
    parts += [str(x) for x in (item.get("luces_sugeridas") or [])]
    parts += [str(x) for x in (item.get("pesos_favor") or {}).keys()]
    iid = str(item.get("id") or "")
    parts += iid.replace(".", " ").replace("_", " ").split()
    return _norm(parts)


def _activar_ids(
    campo: Set[str],
    reg: Dict[str, Any],
    want: Set[str],
    *,
    exigir_autorref_ar: bool = True,
) -> List[str]:
    """IDs de pack que cruzan el campo del corte. ar.* no inventa sin autorref."""
    autores = {
        "identidad", "autoimagen", "autoconcepto", "deseo", "intencion",
        "conviccion", "duda", "miedo", "agencia", "impotencia",
        "autorreferencia", "yo", "self",
    }
    on: List[str] = []
    for ns, pack in (reg.get("packs") or {}).items():
        if ns not in want:
            continue
        if ns == "ar" and exigir_autorref_ar and not (campo & autores):
            continue
        for item in pack.get("items") or []:
            blob = _item_blob(item)
            # también favor leaves vía puente
            puente = (reg.get("puente_244") or {}).get("mapa") or {}
            fav = item.get("pesos_favor") or {}
            luces = list(item.get("luces_sugeridas") or fav.keys())
            extra = set()
            for L in luces:
                leaf = L.split(".")[-1] if isinstance(L, str) else str(L)
                extra.add(leaf.lower())
                if leaf in puente:
                    extra.add(str(puente[leaf]).lower())
            if (blob | extra) & campo:
                iid = item.get("id")
                if iid:
                    on.append(str(iid))
    return sorted(set(on))


def leer_hilado(
    pinchos_por_corte: Dict[str, Sequence[Any]],
    *,
    hechos_extra: Optional[Sequence[str]] = None,
    registro_path: Optional[str] = None,
    packs: Optional[Sequence[str]] = None,
    k: int = K_HILADO,
    top_n: int = 24,
) -> Dict[str, Any]:
    """Activa packs POR CORTE y traza estados temporales (hilado).

    No toca H/freeze/244/Engine. ar.* exige autorreferencia explícita.
    """
    from sidecar_trazabilidad_temporal import trazar_temporal

    reg = load_registro(Path(registro_path) if registro_path else None)
    want = set(packs or ["soc", "hist", "ar", "sit", "pat", "ins", "sab", "vin", "cue", "fam", "cla", "hpe"])
    extra = _norm(hechos_extra or [])

    # orden de cortes: respetar orden de inserción del dict
    cortes_act: List[Dict[str, Any]] = []
    por_corte: Dict[str, List[str]] = {}
    for cid, toks in pinchos_por_corte.items():
        campo = _norm(toks) | extra
        ids = _activar_ids(campo, reg, want)
        por_corte[str(cid)] = ids
        cortes_act.append({"id": str(cid), "tokens": ids})

    known = []
    for ns in want:
        for it in ((reg.get("packs") or {}).get(ns) or {}).get("items") or []:
            if it.get("id"):
                known.append(str(it["id"]))

    traza = trazar_temporal(cortes_act, k=k, known_tokens=known)

    # resumen estados
    por_estado: Dict[str, List[str]] = {"ON": [], "PARPADEO": [], "NO_APARECIDO_AUN": [], "OFF": []}  # PATCH 004: antes LATENCIA
    detalle = []
    for row in traza.get("tokens") or []:
        est = row.get("estado_actual") or "NO_APARECIDO_AUN"
        tid = row.get("token")
        if est in por_estado and tid:
            # NO_APARECIDO_AUN de known nunca vistos: no inundar resumen
            if est == "NO_APARECIDO_AUN" and not row.get("apariciones"):
                continue
            por_estado[est].append(tid)
            detalle.append({
                "id": tid,
                "estado": est,
                "apariciones": row.get("apariciones") or [],
                "primera": row.get("primera_aparicion"),
                "ultima": row.get("ultima_aparicion"),
                "Alimenta_H": "NO",
            })

    # hilado_ok: apareció antes, no en último corte, queda PARPADEO
    cortes_ids = [c["id"] for c in cortes_act]
    ultimo = cortes_ids[-1] if cortes_ids else None
    arrastres = [
        d for d in detalle
        if d["estado"] == "PARPADEO"
        and ultimo
        and ultimo not in d["apariciones"]
        and len(d["apariciones"]) >= 1
    ]

    return {
        "plugin": "SIDECAR_LUCES_GEMINI_PACKS",
        "modo": "HILADO_POR_CORTE",
        "version": reg.get("version"),
        "engine_tocado": False,
        "candados": {
            **(reg.get("candados") or {}),
            "Alimenta_H": "NO",
            "hilado_temporal": "ON",
            "k_parpadeo": k,
        },
        "politica": {
            **(reg.get("politica") or {}),
            "editable_pesos": True,
            "ar_sin_inventar": True,
            "nota_hilado": (
                "ON=en corte actual; PARPADEO=visto hace ≤k cortes (no se apaga); "
                "NO_APARECIDO_AUN=aún no apareció (no es LATENTE); OFF=más de k cortes sin evidencia"
            ),
        },
        "conteos": {ns: ((reg.get("packs") or {}).get(ns) or {}).get("n", 0) for ns in want},
        "por_corte": {cid: {"n": len(ids), "ids": ids} for cid, ids in por_corte.items()},
        "estados": {k: v[:top_n] for k, v in por_estado.items()},
        "estados_n": {k: len(v) for k, v in por_estado.items()},
        "arrastres_parpadeo": arrastres[:top_n],
        "detalle_activos": detalle[: top_n * 2],
        "trazabilidad": {
            "plugin": traza.get("plugin"),
            "k": traza.get("k"),
            "cableado_bus": True,
            "TOCA_F": "NO",
            "TOCA_244": "NO",
            "TOCA_Engine_V5": "NO",
        },
        "luces_faltantes_sugeridas": {
            "tokens": por_estado["ON"][:top_n] + por_estado["PARPADEO"][:top_n],
            "regla": "luces con estado; Alimenta_H=NO; no fuse 244",
        },
    }


def leer(
    pinchos_por_corte: Optional[Dict[str, Sequence[Any]]] = None,
    registro_path: Optional[str] = None,
    packs: Optional[Sequence[str]] = None,
    top_n: int = 12,
    hechos_extra: Optional[Sequence[str]] = None,
    k: int = K_HILADO,
    hilado: bool = True,
) -> Dict[str, Any]:
    """Entrada de bus. Por defecto usa hilado por corte si hay pinchos."""
    if pinchos_por_corte and hilado:
        return leer_hilado(
            pinchos_por_corte,
            hechos_extra=hechos_extra,
            registro_path=registro_path,
            packs=packs,
            k=k,
            top_n=top_n,
        )

    # fallback inventario (sin cortes)
    reg = load_registro(Path(registro_path) if registro_path else None)
    want = set(packs or ["soc", "hist", "ar", "sit", "pat", "ins", "sab", "vin", "cue", "fam", "cla", "hpe"])
    return {
        "plugin": "SIDECAR_LUCES_GEMINI_PACKS",
        "modo": "INVENTARIO_CABLEADO_SIN_CRUCE",
        "version": reg.get("version"),
        "engine_tocado": False,
        "candados": reg.get("candados"),
        "politica": reg.get("politica"),
        "conteos": {ns: ((reg.get("packs") or {}).get(ns) or {}).get("n", 0) for ns in want},
        "activados_top": [],
        "inventario_n": sum(((reg.get("packs") or {}).get(ns) or {}).get("n", 0) for ns in want),
        "luces_faltantes_sugeridas": {"tokens": [], "detalle": [], "regla": "inventario"},
        "nota": "Sin pinchos_por_corte: solo inventario. Pasa cortes para hilado.",
    }


if __name__ == "__main__":
    demo = {
        "A": ["aprendizaje", "ambicion"],
        "B": ["teorizacion", "obstaculo"],
        "C": ["autoridad", "sancion", "persecucion", "censura"],
        "D": ["juicio", "restriccion"],
    }
    out = leer(demo, hechos_extra=["autoridad", "juicio", "presion"])
    print(json.dumps({
        "modo": out["modo"],
        "estados_n": out.get("estados_n"),
        "por_corte": {k: v["n"] for k, v in (out.get("por_corte") or {}).items()},
        "arrastres_n": len(out.get("arrastres_parpadeo") or []),
        "candados": out.get("candados"),
    }, ensure_ascii=False, indent=2))
