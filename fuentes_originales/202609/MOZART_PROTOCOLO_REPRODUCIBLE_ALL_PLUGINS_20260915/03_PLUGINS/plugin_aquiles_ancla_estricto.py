#!/usr/bin/env python3
"""PLUGIN_AQUILES_ANCLA_ESTRICTO

No sustituye plugin_aquiles_h.py. Lo usa si existe.
No fabrica eje. No fabrica p_H. No fabrica umbral.

Contrato:
  COMPLETO = inicio + final_declarado (texto crudo).
  ANCLA    = Aquiles_N sobre replicar_fn que YA trae p_H del motor
             o estado SEGUIR_EMPUJANDO / NO_ENCONTRADO / NO_VERIFICADO.
  TRAZA    solo si ancla_ok.
  FREEZE   en Z_foto con la inercia que llego.
  TORTUGAS estado, no veredicto: reportar dX, persist, kappa; no cerrar H.
  TORTUGAS = resolución insuficiente → cortes más finos del MISMO texto
             (nunca cambiar familia; no inventar fuerza).

UMBRAL_INERCIA_CALIBRADO default None → sin umbral previo freeze queda
TORTUGAS / ABIERTA (no inventar umbral en la misma corrida).

PROHIBIDO:
  extraer eje por bigramas / frecuencia / primer sintagma
  ancla = nombre del sujeto
  ancla = Top-1 244
  final_declarado = H1
  trazar antes de ancla_ok
  peso de ficha en el completo
  replicar_fn = random.gauss
  inventar umbral de inercia en la misma corrida
"""
from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

EPS = 0.02
I_FLOOR = 0.02
N0 = 32
FACTOR = 2
N_FUSIBLE = 8192
M_VENTANAS = 3

PESO_FICHA = re.compile(
    r"(?:"
    r"\b\w+\s+[01]\.\d+\b"
    r"|peso\s*[:=]\s*[01]?\.\d+"
    r"|:\s*[01]\.\d+"
    r")",
    re.I,
)


# Default: sin umbral calibrado → freeze_en_Zfoto queda TORTUGAS/ABIERTA
UMBRAL_INERCIA_CALIBRADO = None


def _cargar_aquiles_h():
    # Preferir hermano junto a este archivo; /mnt/data solo fallback legacy.
    candidatos = [
        Path(__file__).resolve().parent / "plugin_aquiles_h.py",
        Path("/mnt/data/V15_1_integrado/plugin_aquiles_h.py"),
        Path("/tmp/pack12/pack_completo_2026-09-12/plugins/plugin_aquiles_h.py"),
    ]
    for p in candidatos:
        if p.is_file():
            spec = importlib.util.spec_from_file_location("plugin_aquiles_h", str(p))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod
    return None


_AQUILES_H = _cargar_aquiles_h()


def _limpiar(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def _nombres_sujeto(sujeto: str) -> set:
    if not sujeto:
        return set()
    parts = re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+", sujeto)
    out = {p.lower() for p in parts if len(p) > 2}
    return out


def build_completo(inicio: str, final_declarado: str) -> Dict[str, Any]:
    if not inicio or not final_declarado:
        raise ValueError("COMPLETO requiere inicio + final_declarado")
    blob = f"{inicio}\n{final_declarado}"
    if PESO_FICHA.search(blob):
        raise ValueError("PROHIBIDO: peso de ficha en el completo")
    return {
        "inicio": inicio.strip(),
        "final_declarado": final_declarado.strip(),
        "completo_texto": f"{inicio.strip()} || {final_declarado.strip()}",
        "nota": "arco declarado, no H1",
    }


def extraer_eje_candidato(*_a, **_k) -> None:
    """Eliminado. No hay eje por heuristica textual."""
    raise RuntimeError(
        "extraer_eje_candidato esta prohibido. "
        "Pasa eje_candidato desde fuera (tokens con cita) "
        "o deja ancla en NO_VERIFICADO."
    )


def _replicar_es_demo(fn: Callable) -> bool:
    src = getattr(fn, "__name__", "") + str(getattr(fn, "__code__", None) and fn.__code__.co_names)
    return "gauss" in src.lower() or "random" in src.lower()


def evaluar_ancla(
    completo: Dict[str, Any],
    replicar_fn: Optional[Callable[[], Dict[str, Any]]] = None,
    eje_candidato: Optional[str] = None,
    sujeto: str = "",
    bloques: Optional[List[int]] = None,
) -> Dict[str, Any]:
    """Ancla solo si hay eje dado + replicar_fn de motor.

    replicar_fn debe devolver {p_H, I, winner, topk} del engine.
    No se acepta gauss/demo.
    """
    base = {
        "capa": "AQUILES_ANCLA",
        "completo": {
            "inicio": completo["inicio"],
            "final_declarado": completo["final_declarado"],
        },
        "eje_candidato": eje_candidato,
        "estado_H": None,
        "N_min": None,
        "ancla_ok": False,
        "atencion": [],
        "fuera": [],
        "estado_traza": "ABIERTA",
        "H1": None,
        "tortugas": True,
        "nota_prohibido": "ancla != Top1_244, final_declarado != H1, no elimina sesgo",
    }

    if eje_candidato:
        toks = set(_limpiar(eje_candidato).split())
        if toks & _nombres_sujeto(sujeto):
            base["estado_H"] = "NO_VERIFICADO"
            base["motivo"] = "eje_candidato coincide con el nombre del sujeto"
            return base

    if not eje_candidato:
        base["estado_H"] = "NO_VERIFICADO"
        base["motivo"] = "no hay eje_candidato; prohibido fabricarlo por bigrama"
        return base

    if replicar_fn is None:
        base["estado_H"] = "NO_VERIFICADO"
        base["motivo"] = "no hay replicar_fn de motor"
        return base

    if _replicar_es_demo(replicar_fn):
        base["estado_H"] = "NO_VERIFICADO"
        base["motivo"] = "replicar_fn es demo/gauss; no es motor"
        return base

    if _AQUILES_H is None or not hasattr(_AQUILES_H, "bootstrap_hasta_parar"):
        base["estado_H"] = "NO_VERIFICADO"
        base["motivo"] = "plugin_aquiles_h.py no disponible o sin bootstrap_hasta_parar"
        return base

    res = _AQUILES_H.bootstrap_hasta_parar(
        replicar=replicar_fn,
        bloques=bloques,
        eps_p=EPS,
        m=M_VENTANAS,
        n0=N0,
        fusible=N_FUSIBLE,
    )
    estado = res.get("estado_H")
    base["estado_H"] = estado
    base["N_min"] = res.get("N_min")
    base["aquiles_detalle"] = {
        k: res[k]
        for k in ("estado_H", "N_min", "n_replicas_usadas", "toque_fusible", "fusible")
        if k in res
    }
    base["ancla_ok"] = estado == "PARA_DE_EMPUJAR_H"
    if not base["ancla_ok"]:
        base["motivo"] = estado or "Aquiles_N no quieto"
    return base


def filtro_atencion(
    cortes: List[Dict[str, Any]],
    tokens_con_cita: List[str],
    sujeto: str = "",
) -> Dict[str, List[str]]:
    """Dentro = el corte cita un token de la lista. No usa el nombre del sujeto."""
    universales = {
        "liderazgo",
        "sacrificio",
        "audacia",
        "valentia",
        "creatividad",
        "autonomia",
        "resiliencia",
        "empatia",
        "altruismo",
    }
    prohibidos = _nombres_sujeto(sujeto)
    toks = [_limpiar(t) for t in tokens_con_cita if _limpiar(t) and _limpiar(t) not in prohibidos]
    dentro: List[str] = []
    fuera: List[str] = []
    for c in cortes:
        cid = c.get("id") or _limpiar(c.get("texto", ""))[:40]
        txt = _limpiar(c.get("texto", ""))
        if any(t in txt for t in toks):
            dentro.append(cid)
        elif any(u in txt for u in universales):
            fuera.append(f"{cid}:universal_suelto")
        else:
            fuera.append(f"{cid}:no_toca_token_con_cita")
    return {"atencion": dentro, "fuera": fuera}


def freeze_en_Zfoto(
    traza_5x3: Dict[str, Any],
    ancla_out: Dict[str, Any],
    umbral: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """Inercia = ultimo salto. Sin umbral previo -> TORTUGAS/ABIERTA.

    Si umbral is None, usa UMBRAL_INERCIA_CALIBRADO (default None).
    Tortugas = resolución insuficiente → cortes más finos mismo texto.
    """
    out = dict(ancla_out)
    R = (traza_5x3 or {}).get("R732") or {}
    persist = R.get("persist_cos") or []
    kappa = R.get("kappa_dir") or []
    dX = R.get("dX_norm") or []
    inercia = {
        "persist_cos_Z": persist[-1] if persist else None,
        "kappa_Z": kappa[-1] if kappa else None,
        "dX_Z": dX[-1] if dX else None,
    }
    out["inercia_que_llego"] = inercia
    out["H1"] = None
    out["H2"] = None
    out["H3"] = None

    if not ancla_out.get("ancla_ok"):
        out["estado_traza"] = "ABIERTA"
        out["inercia_visible"] = False
        out["tortugas"] = True
        out["motivo"] = "no ancla_ok; no freeze limpio"
        return out

    if umbral is None:
        umbral = UMBRAL_INERCIA_CALIBRADO

    if umbral is None:
        out["estado_traza"] = "ABIERTA"
        out["inercia_visible"] = False
        out["tortugas"] = True
        out["motivo"] = (
            "UMBRAL_INERCIA_CALIBRADO=None; umbral no fijado antes de ver el numero "
            "→ TORTUGAS/ABIERTA (resolución insuficiente: cortes más finos mismo texto)"
        )
        return out

    pmin = umbral.get("persist")
    kmin = umbral.get("kappa")
    pz = inercia["persist_cos_Z"]
    kz = inercia["kappa_Z"]
    if pz is None or kz is None or pmin is None or kmin is None:
        out["estado_traza"] = "ABIERTA"
        out["inercia_visible"] = False
        out["tortugas"] = True
        out["motivo"] = "faltan persist/kappa o umbral"
        return out

    visible = abs(pz) >= pmin and kz >= kmin
    out["umbral_usado"] = {"persist": pmin, "kappa": kmin}
    out["inercia_visible"] = bool(visible)
    if visible:
        out["estado_traza"] = "CONGELADA_EN_Z_FOTO"
        out["tortugas"] = False
        out["regla"] = "Z_foto no es veredicto. H1 las pone el investigador, no max(board)"
    else:
        out["estado_traza"] = "ABIERTA"
        out["tortugas"] = True
        out["motivo"] = "vector no se lee con el umbral declarado de antemano"
    return out


if __name__ == "__main__":
    comp = build_completo(
        inicio="20 marzo 1928, Latrobe, Pennsylvania.",
        final_declarado="1968, Mister Rogers' Neighborhood sale a cadena nacional (NET).",
    )
    ancla = evaluar_ancla(comp, replicar_fn=None, eje_candidato=None, sujeto="Fred Rogers")
    print(json.dumps(ancla, ensure_ascii=False, indent=2))
