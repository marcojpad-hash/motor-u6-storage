#!/usr/bin/env python3
"""PLUGIN_CAPA2_ANTECEDENTES_ARQUETIPOS

Segunda capa lateral (NO toca Engine_V5 ni patterns_final_v14).

Para qué:
  1) Reconocimiento de familias-tipo (prototipo / trayectoria / vínculo / estilo).
  2) Vecinos **estereotipo** (capa estereotipos_situacionales): molde + contexto
     situacional → sugieren **luces faltantes** en el tablero.

No es: diagnóstico clínico, buffet de apuestas, predicción cerrada, merge al 244.

Entrada típica:
  pinchos_por_corte: {"A": ["ambicion", ...], "B": [...]}
  edad_aprox_por_corte: opcional
  catalogo_path: JSON (default al lado)

Salida:
  matches por capa, early_signal, sugerencia_una_familia, descartes,
  vecinos_estereotipo, luces_faltantes_sugeridas.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set

HERE = Path(__file__).resolve().parent
DEFAULT_CATALOG = HERE / "catalogo_capa2_familias_semilla.json"

def _resolve_catalog(path: Optional[Path] = None) -> Path:
    name = "catalogo_capa2_familias_semilla.json"
    if path is not None:
        p = Path(path)
        if p.is_file():
            return p
        raise FileNotFoundError(p)
    here = Path(__file__).resolve().parent
    for c in [here / name, here.parent / "03_LATERALES_VIGENTES" / name, here.parent / "02_TUBO" / name]:
        if c.is_file():
            return c
    raise FileNotFoundError(name)


CAPAS_PROTOTIPO = {"historica_trayectoria", "vinculo_amoroso", "estilo_psic"}
CAPA_ESTEREOTIPO = "estereotipos_situacionales"


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
    p = _resolve_catalog(Path(path) if path else None)
    return json.loads(p.read_text(encoding="utf-8"))


def _score_family(tokens: Set[str], fam: Dict[str, Any]) -> Dict[str, Any]:
    favor = _norm_tokens(fam.get("pinchos_favor") or [])
    contra = _norm_tokens(fam.get("pinchos_contra") or [])
    hit_f = sorted(tokens & favor)
    hit_c = sorted(tokens & contra)
    den = max(len(favor), 1)
    score = (len(hit_f) - 0.5 * len(hit_c)) / den
    tipo = fam.get("tipo_vecino")
    if not tipo:
        tipo = "estereotipo" if fam.get("capa") == CAPA_ESTEREOTIPO else "prototipo"
    return {
        "id": fam.get("id"),
        "capa": fam.get("capa"),
        "nombre": fam.get("nombre"),
        "tipo_vecino": tipo,
        "score": round(score, 4),
        "hits_favor": hit_f,
        "hits_contra": hit_c,
        "ventana_edad": fam.get("ventana_edad"),
        "antecedente_tipo": fam.get("antecedente_tipo"),
        "contextos_situacionales": list(fam.get("contextos_situacionales") or []),
        "luces_sugeridas": sorted(_norm_tokens(fam.get("luces_sugeridas") or [])),
        "prototipo_padre": fam.get("prototipo_padre"),
        "nota": fam.get("nota"),
    }


def _early_signal(
    pinchos_por_corte: Dict[str, Sequence[Any]],
    edad_aprox: Optional[Dict[str, Any]],
    fam: Dict[str, Any],
) -> Dict[str, Any]:
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


def _luces_faltantes(
    tokens_campo: Set[str],
    estereotipos_rankeados: Sequence[Dict[str, Any]],
    *,
    min_score: float = 0.15,
    top_n: int = 5,
) -> Dict[str, Any]:
    """De estereotipos que pegan: luces_sugeridas − lo ya presente en el campo."""
    sugeridas: Dict[str, Dict[str, Any]] = {}
    usados = []
    for row in estereotipos_rankeados:
        if float(row.get("score") or 0) < min_score:
            continue
        if not row.get("hits_favor"):
            continue
        usados.append(row["id"])
        for luz in row.get("luces_sugeridas") or []:
            if luz in tokens_campo:
                continue
            slot = sugeridas.setdefault(
                luz,
                {
                    "token": luz,
                    "por_estereotipos": [],
                    "contextos": [],
                    "motivo": "estereotipo_situacional_sugiere_luz_ausente_en_campo",
                },
            )
            if row["id"] not in slot["por_estereotipos"]:
                slot["por_estereotipos"].append(row["id"])
            for ctx in row.get("contextos_situacionales") or []:
                if ctx not in slot["contextos"]:
                    slot["contextos"].append(ctx)
    ordered = sorted(
        sugeridas.values(),
        key=lambda r: (-len(r["por_estereotipos"]), r["token"]),
    )[:top_n]
    return {
        "tokens": [r["token"] for r in ordered],
        "detalle": ordered,
        "estereotipos_usados": usados,
        "regla": "luces = sugerencia de lectura; NO pilar; NO freeze; NO merge 244",
    }


def _attach_gemini_packs(pinchos_por_corte: Dict[str, Sequence[Any]], hechos_extra: Optional[Sequence[Any]] = None) -> Dict[str, Any]:
    """Cablea sidecar Gemini + hilado temporal al bus sin afectar H. Fallo suave."""
    try:
        from sidecar_luces_gemini_packs import leer as _leer_gem
        out = _leer_gem(pinchos_por_corte, hechos_extra=hechos_extra, hilado=True)
        return {
            "cableado": True,
            "editable": True,
            "modo": out.get("modo"),
            "conteos": out.get("conteos"),
            "luces": (out.get("luces_faltantes_sugeridas") or {}).get("tokens") or [],
            "candados": out.get("candados"),
            "hilado": {
                "por_corte": out.get("por_corte"),
                "estados_n": out.get("estados_n"),
                "estados": out.get("estados"),
                "arrastres_parpadeo": out.get("arrastres_parpadeo"),
                "trazabilidad": out.get("trazabilidad"),
            },
            "nota": "hilado ON: PARPADEO conserva lo previo; Alimenta_H=NO; editable",
        }
    except Exception as e:
        return {"cableado": False, "error": str(e), "editable": True}



def _attach_amantes_sidecar(
    pinchos_por_corte: Dict[str, Sequence[Any]],
    luces_previas: Optional[Sequence[str]] = None,
) -> Dict[str, Any]:
    """Sidecar ama.* POST-principal. Fallo suave. Sin gatillo → LATENCIA."""
    try:
        from sidecar_amantes_arquetipos import leer as _leer_ama
        out = _leer_ama(pinchos_por_corte, luces_activas=luces_previas)
        return {
            "cableado": True,
            "subcapa": True,
            "modo": out.get("modo"),
            "activado": out.get("activado"),
            "luces": out.get("luces") or [],
            "encendidos": out.get("encendidos") or [],
            "candados": out.get("candados"),
            "nota": "POST tokens; sin gatillo=LATENCIA; Alimenta_H=NO",
        }
    except Exception as e:
        return {"cableado": False, "error": str(e), "subcapa": True}



def _attach_control_latencia(
    pinchos_por_corte: Dict[str, Sequence[Any]],
    *,
    clave: str = "matriz_capa2",
    texto_polaridad: Optional[str] = None,
) -> Dict[str, Any]:
    """CONTROL estructural (siempre-on). No sidecar. No mueve H."""
    try:
        from control_latencia_decimo_hombre import actualizar_expediente, polaridad_con_latencia, en_banda_empate
        tokens = []
        for v in pinchos_por_corte.values():
            for x in v:
                if isinstance(x, str):
                    tokens.append(x)
                elif isinstance(x, dict) and (x.get("token") or x.get("id")):
                    tokens.append(str(x.get("token") or x.get("id")))
        if texto_polaridad:
            out = polaridad_con_latencia(
                texto_polaridad,
                clave=f"{clave}::polaridad",
                tokens_contexto=tokens,
            )
            return {
                "rol": "CONTROL_ESTRUCTURAL",
                "cableado": True,
                "siempre_on": True,
                "Alimenta_H": "NO",
                "via": "polaridad_con_latencia",
                "lectura_momento": out.get("lectura_momento"),
                "accion": (out.get("dinamica") or {}).get("accion"),
                "expediente": (out.get("dinamica") or {}).get("expediente"),
                "interpretacion": out.get("interpretacion"),
            }
        # sin texto: p por densidad de tokens (proxy); empate si campo pobre
        n = len(set(tokens))
        p = 0.50 if n < 3 else min(0.72, 0.45 + 0.04 * n)
        dyn = actualizar_expediente(
            clave,
            tema="matriz_capa2",
            p_momento=p,
            tokens_nuevos=tokens,
        )
        return {
            "rol": "CONTROL_ESTRUCTURAL",
            "cableado": True,
            "siempre_on": True,
            "Alimenta_H": "NO",
            "via": "actualizar_expediente",
            "accion": dyn.get("accion"),
            "expediente": dyn.get("expediente"),
            "candados": dyn.get("candados"),
            "regla": dyn.get("regla"),
            "en_banda_empate": en_banda_empate((dyn.get("expediente") or {}).get("p") or 0.5),
        }
    except Exception as e:
        return {"rol": "CONTROL_ESTRUCTURAL", "cableado": False, "error": str(e), "Alimenta_H": "NO"}



def leer(
    pinchos_por_corte: Dict[str, Sequence[Any]],
    edad_aprox_por_corte: Optional[Dict[str, Any]] = None,
    catalogo_path: Optional[str] = None,
    top_k: int = 3,
    min_score_luces: float = 0.15,
    hechos_extra: Optional[Sequence[Any]] = None,
    texto_polaridad: Optional[str] = None,
) -> Dict[str, Any]:
    cat = load_catalog(Path(catalogo_path) if catalogo_path else None)
    all_toks: Set[str] = set()
    for v in pinchos_por_corte.values():
        all_toks |= _norm_tokens(v)

    por_capa: Dict[str, List[Dict[str, Any]]] = {}
    for capa, familias in (cat.get("capas") or {}).items():
        scored = []
        for fam in familias:
            fam = dict(fam)
            fam["capa"] = capa
            if capa == CAPA_ESTEREOTIPO:
                fam.setdefault("tipo_vecino", "estereotipo")
            else:
                fam.setdefault("tipo_vecino", "prototipo")
            row = _score_family(all_toks, fam)
            row["early"] = _early_signal(pinchos_por_corte, edad_aprox_por_corte, fam)
            scored.append(row)
        scored.sort(key=lambda r: r["score"], reverse=True)
        por_capa[capa] = scored[:top_k]

    # prototipos (capas tipológicas) → candidato único transversal
    flat_proto = [
        r
        for capa, rows in por_capa.items()
        if capa in CAPAS_PROTOTIPO
        for r in rows
    ]
    flat_proto.sort(key=lambda r: r["score"], reverse=True)
    sugerida = flat_proto[0] if flat_proto and flat_proto[0]["score"] > 0 else None
    descartes = [r["id"] for r in flat_proto[1:4] if r["score"] > 0]

    # estereotipos: ranking completo de esa capa (no solo top_k interno ya cortado)
    estereo_rows = list(por_capa.get(CAPA_ESTEREOTIPO) or [])
    # re-score full estereotipo list for luces (not truncated to top_k only)
    full_estereo = []
    for fam in (cat.get("capas") or {}).get(CAPA_ESTEREOTIPO) or []:
        fam = dict(fam)
        fam["capa"] = CAPA_ESTEREOTIPO
        fam.setdefault("tipo_vecino", "estereotipo")
        row = _score_family(all_toks, fam)
        row["early"] = _early_signal(pinchos_por_corte, edad_aprox_por_corte, fam)
        full_estereo.append(row)
    full_estereo.sort(key=lambda r: r["score"], reverse=True)

    luces = _luces_faltantes(all_toks, full_estereo, min_score=min_score_luces)

    return {
        "plugin": "PLUGIN_CAPA2_ANTECEDENTES_ARQUETIPOS",
        "version": 2,
        "engine_tocado": False,
        "evidence_status": "unverified",
        "candados": {
            "TOCA_F": "NO",
            "TOCA_244": "NO",
            "TOCA_Engine_V5": "NO",
            "TOCA_FREEZE": "NO",
            "ES_PILAR": "NO",
        },
        "distincion": {
            "prototipo": "familias tipológicas (historica / vinculo / estilo)",
            "estereotipo": (
                "vecinos con contexto situacional; alimentan luces_faltantes_sugeridas"
            ),
        },
        "regla_oficio": (
            "Este plugin SUGIERE. El cierre sigue siendo "
            "1 familia_unica + 1 descarte + 1 frase. "
            "Estereotipos → luces a mirar, no apuesta ni freeze."
        ),
        "tokens_campo": sorted(all_toks),
        "por_capa": por_capa,
        "sugerencia_una_familia": sugerida,
        "descartes_sugeridos": descartes,
        "vecinos_estereotipo": full_estereo[:top_k],
        "luces_faltantes_sugeridas": luces,
        "luces_gemini_packs": _attach_gemini_packs(pinchos_por_corte, hechos_extra=hechos_extra),
        "sidecar_amantes": _attach_amantes_sidecar(pinchos_por_corte),
        "control_latencia": _attach_control_latencia(pinchos_por_corte, texto_polaridad=texto_polaridad),
        "periodicidad": {
            "idea": (
                "Compara early_signal entre familias: "
                "misma estructura puede asomar adolescente (Alejandro) "
                "o cuajar adulto maduro (César)."
            )
        },
    }


if __name__ == "__main__":
    # smoke: campo tipo teórico + obstáculo (faltan varias luces de estereotipo)
    demo = {
        "A": ["aprendizaje", "ambicion"],
        "B": ["teorizacion", "obstaculo"],
        "C": ["teorizacion", "obstaculo", "reconocimiento"],
        "D": ["teorizacion", "dependencia", "desgaste_fisico"],
    }
    edades = {"A": 22, "B": 28, "C": 35, "D": 42}
    out = leer(demo, edades)
    print(json.dumps({
        "version": out["version"],
        "sugerencia": (out["sugerencia_una_familia"] or {}).get("id"),
        "estereo_top": [r["id"] for r in out["vecinos_estereotipo"]],
        "luces_faltantes": out["luces_faltantes_sugeridas"]["tokens"],
    }, ensure_ascii=False, indent=2))
