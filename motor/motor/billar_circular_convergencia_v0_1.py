#!/usr/bin/env python3
"""billar_circular_convergencia_v0_1.py

Lateral. No toca Engine_V5 / 244 / FREEZE / H.
Alimenta_H = NO.

Mapa (circular billiard en el borde = rotación de Poincaré):
  Un punto = una familia que aparece en P_top5_ANEXO.
  Fase inicial φ0(familia) = 2π * frac(sha256(nombre)[:8] / 2^32)  # solo fase, no velocidad
  ω_t(familia) = 2π * Δp_t
      Δp_t = p_t - p_{t-1}  si hay p en t y t-1
             0              si falta uno de los dos (no inventar p)
  φ_t = (φ_{t-1} + ω_t) mod 2π
  Posición z = (cos φ, sin φ) en el círculo unidad.

Esto ES el mapa de billar circular de ángulo constante por paso:
reflexión en el borde reduce a rotación. No es Kuramoto (sin acoplar).

Convergencia: distancia euclídea |z_a - z_b| <= TAU en el mismo corte.
Control nulo: permutar las series Δp de cada familia (misma longitud,
mismas magnitudes, orden roto). Semilla fija.
"""
from __future__ import annotations

import hashlib
import json
import sys  # U6
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

VERSION = "billar_circular_v0_1"
ALIMENTA_H = "NO"
TAU = 0.35
SEED_NULO = 20260921
TOCA = {
    "TOCA_Engine_V5": "NO",
    "TOCA_244": "NO",
    "TOCA_FREEZE": "NO",
    "TOCA_H": "NO",
    "Alimenta_H": ALIMENTA_H,
}

FORMULA = (
    "omega_t = 2*pi*(p_t - p_{t-1}) si ambos p existen; else 0. "
    "phi_t = (phi_{t-1} + omega_t) mod 2pi. "
    "phi0 = 2*pi*frac(int(sha256(nombre)[:8],16)/2**32). "
    "z=(cos phi, sin phi). "
    "conv si ||z_i-z_j|| <= TAU en el mismo corte. "
    "p ausente no se rellena con 0.5."
)


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _phi0(nombre: str) -> float:
    h = int(hashlib.sha256(nombre.encode("utf-8")).hexdigest()[:8], 16)
    return (h / 2**32) * 2.0 * np.pi


def extraer_series_p(cuts: List[Dict[str, Any]]) -> Tuple[List[str], Dict[str, List[float | None]]]:
    ids = [c.get("corte") or c.get("id") for c in cuts]
    nombres = set()
    por_corte = []
    for c in cuts:
        m = {}
        for row in c.get("P_top5_ANEXO") or []:
            if not row:
                continue
            nom, p = row[0], float(row[1])
            m[nom] = p
            nombres.add(nom)
        por_corte.append(m)
    series = {n: [por_corte[t].get(n) for t in range(len(cuts))] for n in sorted(nombres)}
    return ids, series


def trayectorias(series: Dict[str, List[float | None]]) -> Dict[str, Any]:
    out = {}
    n = len(next(iter(series.values()))) if series else 0
    for nom, ps in series.items():
        phi = _phi0(nom)
        phis = [float(phi)]
        omegas = [0.0]
        zs = [[float(np.cos(phi)), float(np.sin(phi))]]
        for t in range(1, n):
            a, b = ps[t - 1], ps[t]
            if a is None or b is None:
                w = 0.0
            else:
                w = 2.0 * np.pi * (float(b) - float(a))
            phi = (phi + w) % (2.0 * np.pi)
            omegas.append(float(w))
            phis.append(float(phi))
            zs.append([float(np.cos(phi)), float(np.sin(phi))])
        out[nom] = {"phi": phis, "omega": omegas, "z": zs, "p": ps}
    return out


def convergencias(tray: Dict[str, Any], ids: List[str], tau: float = TAU) -> List[Dict[str, Any]]:
    names = list(tray)
    n = len(ids)
    ev = []
    for t in range(n):
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                a, b = names[i], names[j]
                za = np.array(tray[a]["z"][t])
                zb = np.array(tray[b]["z"][t])
                d = float(np.linalg.norm(za - zb))
                if d <= tau:
                    ev.append(
                        {
                            "corte": ids[t],
                            "t": t,
                            "familias": [a, b],
                            "distancia": round(d, 6),
                            "phi": {
                                a: round(tray[a]["phi"][t], 6),
                                b: round(tray[b]["phi"][t], 6),
                            },
                            "p_en_corte": {
                                a: tray[a]["p"][t],
                                b: tray[b]["p"][t],
                            },
                            "nota": "p=null = familia no estaba en Top5 de ese corte",
                        }
                    )
    return ev


def control_nulo(series: Dict[str, List[float | None]], ids: List[str], n_rep: int = 40) -> Dict[str, Any]:
    rng = np.random.default_rng(SEED_NULO)
    reales_tray = trayectorias(series)
    n_real = len(convergencias(reales_tray, ids))
    cuentas = []
    for _ in range(n_rep):
        mez: Dict[str, List[float | None]] = {}
        for nom, ps in series.items():
            vals = [x for x in ps if x is not None]
            if len(vals) < 2:
                mez[nom] = list(ps)
                continue
            perm = list(rng.permutation(vals))
            it = iter(perm)
            mez[nom] = [next(it) if x is not None else None for x in ps]
        cuentas.append(len(convergencias(trayectorias(mez), ids)))
    arr = np.array(cuentas, dtype=float)
    return {
        "n_rep": n_rep,
        "semilla": SEED_NULO,
        "n_conv_real": n_real,
        "n_conv_nulo_media": round(float(arr.mean()), 4),
        "n_conv_nulo_std": round(float(arr.std()), 4),
        "n_conv_nulo_min": int(arr.min()),
        "n_conv_nulo_max": int(arr.max()),
        "z_score": round(float((n_real - arr.mean()) / (arr.std() + 1e-9)), 4),
        "regla": "z>2 sugiere más convergencias que el azar de las mismas Δp desordenadas. z~0 = geometría, no señal.",
    }


def vectorizar(ev: List[Dict[str, Any]], cuts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    by_id = {c.get("corte"): c for c in cuts}
    out = []
    for e in ev:
        c = by_id.get(e["corte"]) or {}
        toks = []
        for eje in ("P_top5_ANEXO", "A_top5_ANEXO", "C_top5_ANEXO"):
            for row in c.get(eje) or []:
                toks.append({"eje": eje[0], "familia": row[0], "p": row[1]})
        out.append(
            {
                **e,
                "tablero_corte": toks,
                "Alimenta_H": ALIMENTA_H,
            }
        )
    return out


def correr(path_json: str | Path, etiqueta: str = "caso") -> Dict[str, Any]:
    path = Path(path_json)
    raw = json.loads(path.read_text(encoding="utf-8"))
    cuts = raw.get("cuts") or []
    ids, series = extraer_series_p(cuts)
    tray = trayectorias(series)
    ev = convergencias(tray, ids)
    nulo = control_nulo(series, ids)
    return {
        "version": VERSION,
        "caso": etiqueta,
        "fuente": str(path),
        "fuente_sha256": _sha256_file(path) if path.exists() else None,
        "estado_input": raw.get("estado_input"),
        "n_cuts": len(ids),
        "cortes": ids,
        "n_familias_punto": len(series),
        "familias": list(series),
        "formula": FORMULA,
        "tau": TAU,
        "R732_dX_norm_fuente": (raw.get("R732") or {}).get("dX_norm"),
        "aviso": (
            "RECONSTRUIDO no es input original. No narrar órbita estable. "
            "Orden = orden del array cuts, no reordenar por ID."
        ),
        "n_convergencias": len(ev),
        "convergencias": vectorizar(ev, cuts),
        "control_nulo": nulo,
        "H1": None,
        "H2": None,
        **TOCA,
    }


if __name__ == "__main__":
    # U6 A7: antes rutas fijas /home/workdir/... (de otra máquina, inexistentes). Ahora: argv[1]=RESULT de entrada, argv[2]=salida.
    if len(sys.argv) < 2:
        raise SystemExit("uso: python3 billar_circular_convergencia_v0_1.py RESULT.json [SALIDA.json]")
    src = Path(sys.argv[1])
    out = correr(src, etiqueta=src.stem)
    dest = Path(sys.argv[2]) if len(sys.argv) > 2 else src.with_name(src.stem + "_BILLAR_CIRCULAR_V0_1.json")
    dest.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "ok": True,
        "n_fam": out["n_familias_punto"],
        "n_conv": out["n_convergencias"],
        "nulo": out["control_nulo"],
        "out": str(dest),
        **{k: out[k] for k in TOCA},
    }, ensure_ascii=False, indent=2))
