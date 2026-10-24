#!/usr/bin/env python3
"""Regenera los puentes de laterales (PUENTE_244_FAMILIAS.json + MATRIZ_EQUIVALENCIAS_ESCALA.json) contra
OTRO catálogo de patrones, sin tocar el original. Usa las mismas reglas (reglas_equivalencias.py) y el mismo
constructor (construir_equivalencias_ORIGINAL.py = copia de EQUIVALENCIAS_ESCALA_20260927), quitando solo
el candado "sha == v14 y len == 244" y escribiendo en una carpeta de salida.
Uso: regenerar_puentes.py --patterns RUTA_CATALOGO.json [--out DIR]
Salida por defecto: puentes_regenerados/<sha8_catalogo>/ . Para usarlos: orquestador_unico.py ... --catalogo RUTA --puentes DIR
"""
import argparse, hashlib, importlib.util, sys, json
from pathlib import Path
HERE = Path(__file__).resolve().parent
ap = argparse.ArgumentParser(); ap.add_argument("--patterns", required=True); ap.add_argument("--out", default=None)
a, rest = ap.parse_known_args()
pat = Path(a.patterns).resolve(); s = hashlib.sha256(pat.read_bytes()).hexdigest()
out = Path(a.out) if a.out else HERE.parent / "puentes_regenerados" / s[:8]
out.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(HERE))
spec = importlib.util.spec_from_file_location("constr", HERE / "construir_equivalencias_ORIGINAL.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
m.HERE = out
def cargar_patterns(p):
    d = json.loads(Path(p).read_text(encoding="utf-8"))
    assert isinstance(d, dict) and len(d) > 0, "catálogo vacío"
    return d, hashlib.sha256(Path(p).read_bytes()).hexdigest()
m.cargar_patterns = cargar_patterns
sys.argv = [sys.argv[0], "--patterns", str(pat)] + rest
m.main()
print(json.dumps({"catalogo": str(pat), "sha256": s, "salida": str(out)}, ensure_ascii=False))
