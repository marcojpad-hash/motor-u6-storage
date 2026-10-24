#!/usr/bin/env python3
"""U6 #4: regenera UNIFICACION_SHA256_MANIFEST.json del pack (mismo schema V1 + lista de exclusiones de estado mutable)."""
import hashlib, json
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
EXCL = ["runs/", "STINKBOX_STORAGE/", "motor/stinkbox_vault/", "motor/vecinos_caldero/neighbor_events.jsonl",
        "motor/vecinos_caldero/neighbor_index.json", "motor/stinkbox_tokens_descubiertos.json", "memoria/", "resultados_unificado/"]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
files = []
for p in sorted(ROOT.rglob("*")):
    if not p.is_file() or "__pycache__" in p.parts or p.suffix == ".pyc": continue
    rel = str(p.relative_to(ROOT))
    if rel == "UNIFICACION_SHA256_MANIFEST.json" or any(rel.startswith(x) for x in EXCL): continue
    files.append({"bytes": p.stat().st_size, "path": rel, "sha256": sha(p)})
man = {"files": files, "files_count": len(files), "hash_algorithm": "SHA-256", "schema": "UNIFICACION_SHA256_MANIFEST_V1",
       "excluidos_estado_mutable": EXCL,
       "note": "Regenerado para U6_MOTOR_SOLO_20261020 (zip motor; antes U6_UNIFICADO 2026-10-20). Cubre todo el pack salvo este archivo y el estado mutable listado "
               "(stores que el harness vacía/reemplaza y runs/). correr_estandar lo verifica en preflight: deriva = AVISO en el recibo; "
               "Engine 665c39a2 / patterns d827dcc3 distintos = BLOQUEO (rc=5)."}
(ROOT / "UNIFICACION_SHA256_MANIFEST.json").write_text(json.dumps(man, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(len(files), "archivos")
