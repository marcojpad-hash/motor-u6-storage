#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Auditoría dirigida de activación de laterales/plugins (SOLO LECTURA).
Escanea el código de la copia de trabajo y el RESULT de Semmelweis y
produce una tabla de evidencia por componente.
Uso: python3 auditoria_activacion.py
Salida: auditoria_activacion_evidencia.json en el mismo directorio.
"""
import json
import re
from pathlib import Path

ROOT = Path("/home/hatch/workspace/u6-alterno/motor-cameo/motor")
RESULT = ROOT / "RESULT_SEMMELWEIS_HEROE_SIN_TRONO_20261112.json"
RECIBO = ROOT / "RESULT_SEMMELWEIS_HEROE_SIN_TRONO_20261112_RECIBO_EJECUCION.json"
RUN_DIR = ROOT / "runs/ESTANDAR__SEMMELWEIS_HEROE_SIN_TRONO_20261112"

STATE_RES = [
    ("PROPUESTA", re.compile(r"PROPUESTA")),
    ("EN_REVISION", re.compile(r"EN_REVISI[OÓ]N|EN REVISI[OÓ]N")),
    ("NO_IMPLEMENTADO", re.compile(r"NO_IMPLEMENTADO|NO IMPLEMENTADO|NOT_IMPLEMENTED|SIN_IMPLEMENTAR")),
    ("ESPERANDO", re.compile(r"ESPERANDO(_RESPUESTA)?|ESPERANDO RESPUESTA|PENDING")),
    ("PENDIENTE", re.compile(r"PENDIENTE")),
    ("DESACTIVADO", re.compile(r"DESACTIVAD[OA]|DISABLED|APAGAD[OA]")),
    ("NO_CORRE", re.compile(r"NO_CORRE|NO CORRE|NO_EJECUTA|SKIP")),
    ("NO_DISPONIBLE", re.compile(r"NO_DISPONIBLE|NO DISPONIBLE|NOT_AVAILABLE|AUSENTE")),
    ("CABLEADA_SIN_SENAL", re.compile(r"CABLEADA_SIN_SENAL|SIN_SENAL|SIN SEÑAL|SIN_SEÑAL")),
    ("can_decide_H_False", re.compile(r"can_decide_H\s*[:=]\s*False")),
    ("can_decide_H_True", re.compile(r"can_decide_H\s*[:=]\s*True")),
    ("estado_str", re.compile(r'"estado"\s*:\s*"([^"]+)"|\'estado\'\s*:\s*\'([^\']+)\'|estado\s*=\s*"([^"]+)"')),
    ("enabled_False", re.compile(r"(enabled|activo|habilitado|autorizado)\s*[:=]\s*(False|0|\"no\"|'no')", re.I)),
    ("enabled_True", re.compile(r"(enabled|activo|habilitado|autorizado)\s*[:=]\s*(True|1)", re.I)),
    ("TODO_FIXME", re.compile(r"TODO|FIXME|XXX|HACK")),
]

def scope_files():
    files = []
    for pat in ["motor/*.py", "laterales/**/*.py", "reconexion_v2a1/*.py",
                "geometria_multicapa/*.py", "correr_estandar.py"]:
        files.extend(sorted(ROOT.glob(pat)))
    # excluir __pycache__ y runs
    return [f for f in files if "__pycache__" not in str(f)]

def scan_states(path):
    text = path.read_text(errors="ignore")
    hits = {}
    for name, rx in STATE_RES:
        found = []
        for i, line in enumerate(text.splitlines(), 1):
            m = rx.search(line)
            if m:
                found.append({"linea": i, "texto": line.strip()[:220]})
                if len(found) >= 6:
                    break
        if found:
            hits[name] = found
    return hits, len(text.splitlines())

def wiring_refs():
    """Textos de los archivos que cablean: correr_estandar, motor UNICO, laterales_unico."""
    out = {}
    for f in [ROOT / "correr_estandar.py",
              ROOT / "motor/MOTOR_V15_3_UNICO_20260927.py",
              ROOT / "motor/laterales_unico_v1.py"]:
        out[f.name] = f.read_text(errors="ignore") if f.exists() else ""
    return out

def main():
    refs = wiring_refs()
    # RESULT: stages y features
    res = json.loads(RESULT.read_text())
    features_keys = sorted((res.get("features") or {}).keys())
    ceb_stages = (res.get("ceb") or {}).get("stages") or {}
    if isinstance(ceb_stages, list):
        ceb_stages = {s.get("name", "?"): s for s in ceb_stages}
    lat = res.get("laterales_unico") or {}
    recibo = json.loads(RECIBO.read_text()) if RECIBO.exists() else {}
    recibo_stages = recibo.get("stages") or recibo.get("etapas") or {}

    rows = []
    for f in scope_files():
        rel = str(f.relative_to(ROOT))
        stem = f.stem
        states, nlines = scan_states(f)
        wired = {}
        for src, txt in refs.items():
            wired[src] = (stem in txt) or (f.name in txt)
        # presencia en el RESULT
        in_features = [k for k in features_keys if stem.replace("_", "") in k.replace("_", "") or stem in k]
        in_ceb = [k for k in ceb_stages if stem in k or stem.replace("_", "") in k.replace("_", "")]
        in_lat = [k for k in lat.keys() if stem in str(k) or stem.replace("_", "") in str(k).replace("_", "")]
        rows.append({
            "componente": stem,
            "archivo": rel,
            "lineas": nlines,
            "estados": states,
            "cableado_correr_estandar": wired["correr_estandar.py"],
            "cableado_motor_unico": wired["MOTOR_V15_3_UNICO_20260927.py"],
            "cableado_laterales_unico": wired["laterales_unico_v1.py"],
            "en_features_result": in_features,
            "en_ceb_stages": in_ceb,
            "en_laterales_unico_result": in_lat,
        })

    evidencia = {
        "componentes": rows,
        "result_features_keys": features_keys,
        "result_ceb_stages": {k: {"started": v.get("started"), "ended": v.get("ended"),
                                  "error": v.get("error"), "output": v.get("output"),
                                  "output_empty": v.get("output_empty")}
                              for k, v in ceb_stages.items()} if isinstance(ceb_stages, dict) else {},
        "result_laterales_unico_keys": sorted(lat.keys()) if isinstance(lat, dict) else [],
        "recibo_keys": sorted(recibo.keys()) if isinstance(recibo, dict) else [],
        "recibo_stages": recibo_stages,
    }
    out = Path("/home/hatch/workspace/u6-alterno/auditoria_activacion_evidencia.json")
    out.write_text(json.dumps(evidencia, ensure_ascii=False, indent=1))
    print("componentes:", len(rows))
    print("features keys:", len(features_keys))
    print("ceb stages:", len(ceb_stages))
    print("laterales_unico keys:", len(lat) if isinstance(lat, dict) else 0)
    print("escrito:", out)

if __name__ == "__main__":
    main()
