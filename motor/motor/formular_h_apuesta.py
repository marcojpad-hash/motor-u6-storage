#!/usr/bin/env python3
"""Cierra el tramo que el contrato pide y el tubo no hacía:
señales → H1/H2 + apuesta + falsadores + freeze.
Prohibido H1 = max(board).
Alimenta_H de sidecars sigue NO: este módulo lee features, no las reescribe.
"""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

BASE = Path(__file__).resolve().parent
ALIMENTA_H_SIDECARS = "NO"


def _sha(obj: Any) -> str:
    raw = json.dumps(obj, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _cands(motor: Dict[str, Any]) -> List[Dict[str, Any]]:
    return list(motor.get("candidatos_final_P_0a3") or [])


def _top1_name(motor: Dict[str, Any]) -> Optional[str]:
    cuts = motor.get("cuts") or []
    if not cuts:
        return None
    rows = cuts[-1].get("P_top5_ANEXO") or []
    return rows[0][0] if rows else None


def tabla_c(tokens: Sequence[str], lib: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Luces que la biblioteca encendería con los tokens congelados (antes de t+1)."""
    toks = set(tokens)
    luces = []
    items = lib.items() if isinstance(lib, dict) else []
    for name, pat in items:
        if not isinstance(pat, dict):
            continue
        fav = pat.get("tokens_favor") or {}
        con = pat.get("tokens_contra") or {}
        sf = sum(float(fav[t]) for t in toks if t in fav)
        sc = sum(float(con[t]) for t in toks if t in con)
        neto = round(sf - sc, 4)
        if neto > 0:
            luces.append({"familia": name, "neto": neto, "favor_hit": sorted(toks & set(fav)),
                          "contra_hit": sorted(toks & set(con))})
    luces.sort(key=lambda x: -x["neto"])
    return luces[:12]


def _tokens_ultimo(cuts_in: Sequence[Dict[str, Any]]) -> List[str]:
    if not cuts_in:
        return []
    last = cuts_in[-1]
    toks = []
    for eje in ("P", "A", "C"):
        for pair in last.get(eje) or []:
            toks.append(str(pair[0]))
    return toks


def formular(out_pre: Dict[str, Any], cuts_in: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    motor = out_pre.get("motor") or {}
    feat = out_pre.get("features") or {}
    polti = (feat.get("polti_caldero") or {})
    proy = polti.get("proyeccion") or {}
    geo = feat.get("geometria") or {}
    cands = _cands(motor)
    fam_cands = [c.get("familia") for c in cands if c.get("familia")]
    polti_p = list(proy.get("polti_persistentes") or [])
    arq_p = list(proy.get("arquetipos_persistentes") or [])
    top1 = _top1_name(motor)

    canales_h1 = []
    nucleo = None
    for fam in fam_cands:
        if fam in polti_p or fam.startswith("arquetipo_"):
            nucleo = fam
            canales_h1.append(f"candidato+lente:{fam}")
            break
    if nucleo is None and polti_p:
        nucleo = polti_p[0]
        canales_h1.append(f"polti:{nucleo}")
    if nucleo is None and arq_p:
        nucleo = arq_p[0]
        canales_h1.append(f"arquetipo:{nucleo}")
    if nucleo is None and len(fam_cands) >= 2:
        nucleo = fam_cands[1] if fam_cands[0] == top1 else fam_cands[0]
        canales_h1.append(f"candidato_no_top1:{nucleo}")
    if nucleo is None and fam_cands:
        nucleo = fam_cands[0]
        canales_h1.append(f"candidato_unico:{nucleo}")

    if top1 and nucleo == top1:
        canales_h1.append("aviso:coincidió_con_top1_pero_no_se_eligió_por_ser_top1")

    h2_nucleo = None
    canales_h2 = []
    for fam in fam_cands:
        if fam != nucleo:
            h2_nucleo = fam
            canales_h2.append(f"candidato_rival:{fam}")
            break
    if h2_nucleo is None:
        a_top = []
        cuts_m = motor.get("cuts") or []
        if cuts_m:
            a_top = [r[0] for r in (cuts_m[-1].get("A_top5_ANEXO") or [])]
        for fam in a_top:
            if fam != nucleo:
                h2_nucleo = fam
                canales_h2.append(f"eje_A:{fam}")
                break

    persist = geo.get("persist_ultima")
    kappa = geo.get("kappa_ultimo")
    dX = geo.get("dX_ultimo")
    if persist is None:
        apuesta_tipo = "INSUFICIENTE_TRAYECTORIA"
        apuesta_txt = "No hay dX/persistencia (pocos cortes). Apuesta: el núcleo H1 sigue visible; no se afirma rumbo."
    elif persist >= 0.5:
        apuesta_tipo = "INERCIA"
        apuesta_txt = f"El siguiente corte mantiene el núcleo {nucleo} y no voltea al rival {h2_nucleo}."
    elif persist <= 0:
        apuesta_tipo = "BIFURCACION"
        apuesta_txt = f"El rumbo no persiste (cos={persist}). El rival {h2_nucleo} puede subir."
    else:
        apuesta_tipo = "DEBIL"
        apuesta_txt = f"Persistencia débil ({persist}). H1 {nucleo} sigue como lectura; no se cierra."

    h1 = {
        "enunciado": f"La estructura hasta Z se lee como {nucleo} por convergencia de canales, no por Top-1.",
        "nucleo": nucleo,
        "canales": canales_h1,
        "top1_tablero": top1,
        "regla": "H1≠max(board)",
    }
    h2 = {
        "enunciado": (
            f"Lectura rival: {h2_nucleo}."
            if h2_nucleo else
            "Sin rival canalizado. H2=indeterminado."
        ),
        "nucleo": h2_nucleo,
        "canales": canales_h2 or ["indeterminado"],
    }
    apuesta = {
        "tipo": apuesta_tipo,
        "texto": apuesta_txt,
        "persist_cos": persist,
        "kappa_dir": kappa,
        "dX_norm": dX,
        "t_plus_1": "aún oculto",
    }
    falsadores = [
        f"Si t+1 apaga {nucleo} y no aparece en tablero ni Polti, H1 cae.",
        f"Si t+1 sube {h2_nucleo} por encima de {nucleo} en P y A, gana H2.",
        "Si persisten ambas sin orden, empate: latencia, no cierre.",
    ]

    lib = {}
    p244 = BASE / "patterns_final_v14.json"
    if p244.exists():
        lib = json.loads(p244.read_text(encoding="utf-8"))
    tokens_z = _tokens_ultimo(cuts_in)
    c_pred = tabla_c(tokens_z, lib)

    freeze = {
        "sello": True,
        "ts": time.time(),
        "n_cuts": len(list(cuts_in)),
        "pregunta": out_pre.get("pregunta"),
        "sha_cuts": _sha(list(cuts_in)),
        "sha_h": _sha({"H1": h1, "H2": h2, "apuesta": apuesta}),
        "t_plus_1_abierto": False,
        "monte_carlo_en_v15_3": False,
    }
    return {
        "H1": h1,
        "H2": h2,
        "apuesta": apuesta,
        "falsadores": falsadores,
        "tabla_C": c_pred,
        "freeze": freeze,
        "fase": "H_SELLADA",
        "escribe_H": True,
        "origen_H": "formular_h_apuesta.py",
        "Alimenta_H_sidecars": ALIMENTA_H_SIDECARS,
    }


def puntuar_t1(sello: Dict[str, Any], cuts_t1: Sequence[Dict[str, Any]], motor_t1: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Solo después del freeze. No reescribe H."""
    fr = sello.get("freeze") or {}
    if not fr.get("sello"):
        return {"ok": False, "razon": "no hay freeze"}
    h1 = (sello.get("H1") or {}).get("nucleo")
    h2 = (sello.get("H2") or {}).get("nucleo")
    c_pred = [x["familia"] for x in (sello.get("tabla_C") or [])]
    tops = []
    if motor_t1:
        last = (motor_t1.get("cuts") or [{}])[-1]
        tops = [r[0] for r in (last.get("P_top5_ANEXO") or [])]
        tops += [r[0] for r in (last.get("A_top5_ANEXO") or [])]
    hit_c = sorted(set(c_pred) & set(tops))
    hit_h = None
    if h1 and h1 in tops:
        hit_h = "HIT_H1"
    elif h2 and h2 in tops:
        hit_h = "HIT_H2"
    else:
        hit_h = "MISS"
    return {
        "ok": True,
        "t_plus_1_abierto": True,
        "hit_rate_cableado": round(len(hit_c) / max(1, len(c_pred)), 4),
        "luces_C_que_aparecieron": hit_c,
        "hit_H": hit_h,
        "H_intacta": True,
        "freeze_sha_h": fr.get("sha_h"),
    }
