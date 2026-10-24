#!/usr/bin/env python3
"""Verifica un recibo U5: recalcula self_sha256 y los sha256 de archivos.
Uso: python3 u5/u5_verificar.py RECIBO_U5.json [--pack DIR]
 - archivos_clave: se recalcula sobre el path registrado.
 - archivos_cargados: si el path ya no existe (runs/ borrado), se recalcula sobre fuente_en_pack dentro de --pack
   (por defecto el pack U5). estado_mutable se informa pero no cuenta como fallo (cambia por diseño).
Salida: JSON con ok/fallos. exit 0 = verificado."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from u5_comun import sha_file, self_hash, PACK

def verificar(rp, pack=PACK):
    R = json.loads(Path(rp).read_text(encoding="utf-8"))
    res = {"recibo": str(rp), "self_sha256_registrado": R.get("self_sha256"), "self_sha256_recalculado": self_hash(R)}
    res["self_ok"] = res["self_sha256_registrado"] == res["self_sha256_recalculado"]
    fallos, ok, mut, nover = [], 0, 0, []
    for a in R.get("archivos_clave", []):
        p = Path(a["path"])
        if a["rol"] == "u5_tool": continue  # herramientas pueden evolucionar; se reportan aparte
        if not p.is_file() and a.get("rel_pack"): p = Path(pack) / a["rel_pack"]
        if not p.is_file(): nover.append(a["path"]); continue
        if sha_file(p) == a["sha256"]: ok += 1
        else: fallos.append({"path": str(p), "rol": a["rol"], "registrado": a["sha256"], "actual": sha_file(p)})
    for a in R.get("archivos_cargados", []):
        if "sha256" not in a: continue
        if a["clase"] == "estado_mutable": mut += 1; continue
        p = Path(a["path"])
        if not p.is_file() and a.get("fuente_en_pack"): p = Path(pack) / a["fuente_en_pack"]
        if not p.is_file(): nover.append(a["path"]); continue
        h = sha_file(p)
        if h == a["sha256"]: ok += 1
        else: fallos.append({"path": str(p), "registrado": a["sha256"], "actual": h})
    res.update({"hashes_ok": ok, "hash_fallos": fallos, "no_verificables_ausentes": nover, "estado_mutable_omitido": mut})
    res["ok"] = res["self_ok"] and not fallos
    return res

if __name__ == "__main__":
    a = sys.argv[1:]; pack = PACK
    if "--pack" in a: i = a.index("--pack"); pack = Path(a[i + 1]); a = a[:i] + a[i + 2:]
    r = verificar(a[0], pack); print(json.dumps(r, ensure_ascii=False, indent=1)); sys.exit(0 if r["ok"] else 1)
