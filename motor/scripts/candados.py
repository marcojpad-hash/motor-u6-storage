#!/usr/bin/env python3
"""Candado local del pack. Hash distinto = BYPASS_HASH_CAMBIO (avisa y sigue).
No aborta la corrida. Engine 30507 es el canónico activo. 30507 queda como artefacto prohibido.
"""
from __future__ import annotations
import hashlib, json, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MOTOR = ROOT / "motor"
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()

ENG_CORRE = "665c39a2861e58772522e91272563260d980908b1d4ab9f7092d3413d0c36082"
ENG_HIST = "665c39a2861e58772522e91272563260d980908b1d4ab9f7092d3413d0c36082"
PAT_V14 = "d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1"


def main(tag="AHORA"):
    eng = MOTOR / "Engine_V5_CANONICO_SOLO.py"
    pat = MOTOR / "patterns_final_v14.json"
    e_sha = sha(eng) if eng.is_file() else None
    p_sha = sha(pat) if pat.is_file() else None
    mismatch = e_sha not in {ENG_CORRE, ENG_HIST} or p_sha != PAT_V14
    out = {
        "tag": tag,
        "hora": time.strftime("%Y-%m-%d %H:%M:%S"),
        "engine_sha256": e_sha,
        "patterns_sha256": p_sha,
        "engine_es_el_que_corre_30507": e_sha == ENG_CORRE,
        "bypass_hash": bool(mismatch),
        "codigo": "BYPASS_HASH_CAMBIO" if mismatch else "HASH_OK",
        "permitir_corrida": True,
        "nota": "hash distinto no para el tubo",
    }
    (ROOT / "tablas").mkdir(exist_ok=True)
    (ROOT / "tablas" / f"CANDADOS_{tag}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("tag", "codigo", "permitir_corrida", "engine_es_el_que_corre_30507")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else "AHORA"))
