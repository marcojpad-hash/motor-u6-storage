#!/usr/bin/env python3
"""
MOTOR_V15_1_10CORTES_LIMPIO.py

Contrato:
- 244 intacto. Solo patterns_final_v14.json.
- sidecar OFF. No fusionar otto / hosteleria / gloria_sacro.
- Aquiles OFF. Wroas OFF. σ NO vive aquí.
- H1/H2 las congela el investigador, no max(board).
- Token ausente del 244 = error. Hueco = lista vacía, no 0.5.
- Top5 es anexo, no veredicto.

Uso:
  from MOTOR_V15_1_10CORTES_LIMPIO import correr_5x3
  out = correr_5x3(cuts, pregunta="Malcolm_X")
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

BASE = Path(__file__).resolve().parent
VERSION = "V15.1_10CORTES_LIMPIO"
HASH_CANDADO = "48333cd11b9234f1"
M = 0.998
N_CANON = 244
P_MIN_CANDIDATO = 0.65
MAX_CANDIDATOS = 3

ON = ("traza_campo_244.py", "plugin_reporte_3d.py", "plugin_familias_gloria_sacro.py", "plugin_otto_numinoso.py", "plugin_trayectoria_hosteleria.py", "plugin_arco_field_snyder_mckee.py", "plugin_picos_mesetas.py", "plugin_sesgo_lectura.py", "plugin_alias_reactivacion.py", "plugin_fix_entrada.py", "plugin_embudo_clinico.py", "plugin_pregunta_detras.py", "plugin_metodo_rigor.py", "plugin_arquetipos_dinamicos.py", "plugin_guardia_no_cruce.py",)
OFF = (
    "plugin_familias_gloria_sacro.py",
    "plugin_otto_numinoso.py",
    "plugin_trayectoria_hosteleria.py",
    "plugin_aquiles_h.py",
    "plugin_wroas.py",
    "plugin_arco_field_snyder_mckee.py",
    "plugin_picos_mesetas.py",
    "plugin_sesgo_lectura.py",
    "plugin_alias_reactivacion.py",
    "plugin_fix_entrada.py",
    "plugin_embudo_clinico.py",
    "plugin_pregunta_detras.py",
    "plugin_metodo_rigor.py",
)

Token = Tuple[str, float]
Eje = Sequence[Token]
Corte = Dict[str, Any]


def _load(modname: str, filename: str):
    path = BASE / filename
    if not path.exists():
        raise FileNotFoundError(f"Falta {filename} junto a este script")
    spec = importlib.util.spec_from_file_location(modname, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_canonical() -> Tuple[Dict[str, Any], set]:
    path = BASE / "patterns_final_v14.json"
    if not path.exists():
        raise FileNotFoundError("Falta patterns_final_v14.json")
    lib = json.loads(path.read_text(encoding="utf-8"))
    if len(lib) != N_CANON:
        raise RuntimeError(f"244 roto: len={len(lib)}")
    tokens: set = set()
    for p in lib.values() if isinstance(lib, dict) else lib:
        if not isinstance(p, dict):
            continue
        tokens |= set(p.get("tokens_favor", {}) or [])
        tokens |= set(p.get("tokens_contra", {}) or [])
    return lib, tokens


def validar_corte(cid: str, P: Eje, A: Eje, C: Eje, canonical: set) -> Dict[str, int]:
    holes = {}
    for eje, rows in (("P", P), ("A", A), ("C", C)):
        seen = []
        for tok, w in rows:
            if tok not in canonical:
                raise RuntimeError(f"NON_CANONICAL_TOKEN {cid} {eje} {tok}")
            if not (0.60 <= float(w) <= 0.84):
                raise RuntimeError(f"PESO_FUERA_DE_CODIGO {cid} {eje} {tok} {w}")
            if tok in seen:
                raise RuntimeError(f"TOKEN_DUPLICADO {cid} {eje} {tok}")
            seen.append(tok)
        if len(rows) > 5:
            raise RuntimeError(f"MAS_DE_5 {cid} {eje}")
        holes[eje] = 5 - len(rows)
    return holes


def _engine(eng, pat: str, pregunta: str):
    e = eng.TracingEngine(pat, ":memory:")
    e.start_question(pregunta)
    return e


def _board(eng, engine, cid: str, rows: Eje) -> Dict[str, float]:
    engine.extractor.extract_from_text = (
        lambda txt, rows=list(rows), cid=cid: [
            eng.Marker(t, t, float(w), source=f"5x3:{cid}") for t, w in rows
        ]
    )
    r = engine.process_observation(cid, monte_carlo=True)
    return {h["name"]: float(h["p_final"]) for h in r["hypotheses"]}


def _top(board: Dict[str, float], k: int = 5) -> List[List[Any]]:
    return [[n, p] for n, p in sorted(board.items(), key=lambda x: -x[1])[:k]]


def _candidatos(board: Dict[str, float]) -> List[Dict[str, Any]]:
    out = []
    for n, p in sorted(board.items(), key=lambda x: -x[1]):
        if p >= P_MIN_CANDIDATO:
            out.append({"familia": n, "p": p})
        if len(out) >= MAX_CANDIDATOS:
            break
    return out


def correr_5x3(
    cuts: Sequence[Corte],
    pregunta: str = "caso",
    annex_traza: bool = True,
) -> Dict[str, Any]:
    """
    cuts = [
      {"id": "C1", "P": [("token", 0.72), ...], "A": [...], "C": [...]},
      ...
    ]
    10 cortes recomendados. Menos de 10 no inventa C8-C10.
    """
    lib, canonical = load_canonical()
    eng = _load("eng_v5", "Engine_V5_CANONICO_SOLO.py")

    ep = _engine(eng, str(BASE / "patterns_final_v14.json"), pregunta + "_P")
    ea = _engine(eng, str(BASE / "patterns_final_v14.json"), pregunta + "_A")
    ec = _engine(eng, str(BASE / "patterns_final_v14.json"), pregunta + "_C")

    seqP, seqA, seqC = [], [], []
    cutout = []
    holes_all = {}
    names_ref: Optional[List[str]] = None
    Xs: List[np.ndarray] = []

    for raw in cuts:
        cid = raw["id"]
        P, A, C = raw.get("P") or [], raw.get("A") or [], raw.get("C") or []
        holes_all[cid] = validar_corte(cid, P, A, C, canonical)

        bp = _board(eng, ep, cid + "_P", P)
        ba = _board(eng, ea, cid + "_A", A)
        bc = _board(eng, ec, cid + "_C", C)

        names = sorted(bp.keys())
        if names_ref is None:
            names_ref = names
        if names != names_ref or sorted(ba) != names_ref or sorted(bc) != names_ref:
            raise RuntimeError(f"BOARD_INCOMPLETO {cid}: no rellenar con 0.5")

        xt = np.concatenate(
            [
                np.array([bp[n] for n in names_ref], dtype=float),
                np.array([ba[n] for n in names_ref], dtype=float),
                np.array([bc[n] for n in names_ref], dtype=float),
            ]
        )
        if xt.size != 732:
            raise RuntimeError(f"R732_ROTO {cid} dim={xt.size}")

        Xs.append(xt)
        seqP.append((cid, bp))
        seqA.append((cid, ba))
        seqC.append((cid, bc))
        cutout.append(
            {
                "corte": cid,
                "n_tokens": {"P": len(P), "A": len(A), "C": len(C)},
                "holes": holes_all[cid],
                "P_top5_ANEXO": _top(bp),
                "A_top5_ANEXO": _top(ba),
                "C_top5_ANEXO": _top(bc),
                "P_candidatos_0a3": _candidatos(bp),
                "X_dim": int(xt.size),
            }
        )

    Xm = np.stack(Xs)
    dX = np.diff(Xm, axis=0)
    dX_norm = np.linalg.norm(dX, axis=1).tolist()
    persist = []
    kappa = []
    for i in range(1, len(dX)):
        a, b = dX[i - 1], dX[i]
        na, nb = np.linalg.norm(a), np.linalg.norm(b)
        cos = float(np.dot(a, b) / (na * nb + 1e-12))
        cos = max(-1.0, min(1.0, cos))
        persist.append(cos)
        kappa.append(float(np.sqrt(max(0.0, 1.0 - cos * cos))))

    annex: Dict[str, Any] = {}
    if annex_traza:
        try:
            tc = _load("traza244", "traza_campo_244.py")
            r3 = _load("rep3d", "plugin_reporte_3d.py")
            annex["traza_P"] = tc.analizar(seqP)
            annex["reporte_3d_P"] = r3.leer(seqP)
        except FileNotFoundError:
            annex["traza_P"] = "plugin ausente"
            annex["reporte_3d_P"] = "plugin ausente"

    lastP = seqP[-1][1] if seqP else {}
    return {
        "version": VERSION,
        "hash_candado": HASH_CANDADO,
        "M": M,
        "sidecar": False,
        "n_canon": len(lib),
        "plugins_ON": list(ON),
        "plugins_OFF": list(OFF),
        "engine_executed": True,
        "top5_es_anexo": True,
        "H1": None,
        "H2": None,
        "regla_H": "H1/H2 las congela el investigador despues de ver hechos+candidatos 0-3. Prohibido H1=max(board).",
        "sigma": None,
        "detector_no_aplica_aqui": True,
        "pregunta": pregunta,
        "n_cuts": len(cuts),
        "holes": holes_all,
        "cuts": cutout,
        "R732": {
            "X_shape": list(Xm.shape),
            "dX_norm": dX_norm,
            "persist_cos": persist,
            "kappa_dir": kappa,
            "nota": "kappa/dX diagnostican trayectoria. No deciden H1/H2.",
        },
        "candidatos_final_P_0a3": _candidatos(lastP),
        "annex": annex,
    }


if __name__ == "__main__":
    print(
        json.dumps(
            {
                "ok": True,
                "file": "MOTOR_V15_1_10CORTES_LIMPIO.py",
                "sidecar": False,
                "H1": None,
                "msg": "Importa correr_5x3. No fusiona 244. No apostar Top1.",
            },
            ensure_ascii=False,
        )
    )
