#!/usr/bin/env python3
"""Regenera manifiestos sin ciclos de hash para el motor de trabajo U6."""
import hashlib, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
MUTABLE = ["runs/", "STINKBOX_STORAGE/", "motor/stinkbox_vault/", "motor/vecinos_caldero/neighbor_events.jsonl",
           "motor/vecinos_caldero/neighbor_index.json", "motor/stinkbox_tokens_descubiertos.json", "memoria/", "resultados_unificado/",
           # LISTO_CALIBRAR_20261024: salidas de pruebas/evidencia/casos y sellos de calibración son estado de corrida
           "tests_integracion/_out/", "evidencia_agnostico/", "SALIDAS/", "salida_cal_", "casos_cal/"]
VENDOR = "motor/_vendor_buscador/"
EXCLUDE_ALL = {"UNIFICACION_SHA256_MANIFEST.json", "MANIFIESTO_COMPACTO_SHA256.json", "SHA256SUMS_MOTOR.txt"}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(exclude):
    out=[]
    for p in sorted(ROOT.rglob('*')):
        if not p.is_file() or '__pycache__' in p.parts or p.suffix == '.pyc': continue
        rel=p.relative_to(ROOT).as_posix()
        if rel in exclude or any(rel.startswith(x) for x in MUTABLE): continue
        out.append({'path':rel,'bytes':p.stat().st_size,'sha256':sha(p)})
    return out
# Manifest used by correr_estandar: no self-reference, no compact-manifest cycle.
files=rows({"UNIFICACION_SHA256_MANIFEST.json","MANIFIESTO_COMPACTO_SHA256.json","SHA256SUMS_MOTOR.txt"})
man={'files':files,'files_count':len(files),'hash_algorithm':'SHA-256','schema':'UNIFICACION_SHA256_MANIFEST_V1',
     'excluidos_estado_mutable':MUTABLE,
     'seccion_vendor_declarada':{'prefijo':VENDOR,'incluido_en_files':True,'archivos':sum(1 for f in files if f['path'].startswith(VENDOR)),
                                 'nota':'dependencias vendorizadas del buscador agnóstico (ddgs y deps); hasheadas archivo por archivo'},
     'note':'U6 motor de trabajo 2026-10-20: el manifiesto y los sumarios de hashes se excluyen entre sí para evitar ciclos. Deriva de archivos operativos = AVISO; Engine y patterns canónicos distintos = BLOQUEO.'}
(ROOT/'UNIFICACION_SHA256_MANIFEST.json').write_text(json.dumps(man,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# Compact inventory includes the operational manifest; excludes itself and the flat SHA list.
files=rows({"MANIFIESTO_COMPACTO_SHA256.json","SHA256SUMS_MOTOR.txt"})
compact={'fecha':'2026-10-20','politica':'Inventario exacto del paquete motor de trabajo; excluye este manifiesto, SHA256SUMS_MOTOR.txt, caches y estado mutable.', 'files':files}
(ROOT/'MANIFIESTO_COMPACTO_SHA256.json').write_text(json.dumps(compact,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# Flat checksum file is auxiliary and is intentionally excluded from both JSON manifests.
lines=[]
for p in sorted(ROOT.rglob('*')):
    rel=p.relative_to(ROOT).as_posix()
    if not p.is_file() or '__pycache__' in p.parts or p.suffix=='.pyc' or rel=='SHA256SUMS_MOTOR.txt': continue
    if any(rel.startswith(x) for x in MUTABLE): continue
    lines.append(f'{sha(p)}  ./{rel}')
(ROOT/'SHA256SUMS_MOTOR.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'unification_manifest_files':len(man['files']),'compact_manifest_files':len(compact['files']),'sha256_lines':len(lines)},ensure_ascii=False))
