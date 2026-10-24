#!/usr/bin/env python3
"""Congela la BASE ESTABLE: escribe BASE_ESTABLE_MANIFEST.json con sha del motor, del catálogo, de cada pieza
(motor/ + todo lo que el orquestador pone en el directorio de corrida), de scripts e inputs, y la LÍNEA BASE
(tabla de corridas de los 7 casos × FULL/PREFIX) contra la cual se medirán cambios futuros. A ciegas."""
import hashlib, json, shutil, sys, tempfile, time
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts")); import orquestador_unico as ou
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
T = json.loads((ROOT / "tablas/TABLA_UNICO.json").read_text())
PAT = Path("/workspace/pred_hist_bio_in/TRANSFER_V15_1/patterns_final_v14.json")
with tempfile.TemporaryDirectory() as td:
    rd = Path(td) / "rd"; ou.orq.build("UNICO", rd); shutil.copytree(ou.MOTOR / "familias_tokens", rd / "familias_tokens")
    run_dir = {str(p.relative_to(rd)): sha(p) for p in sorted(rd.rglob("*")) if p.is_file() and "__pycache__" not in p.parts}
motor_files = {str(p.relative_to(ROOT / "motor")): sha(p) for p in sorted((ROOT / "motor").rglob("*")) if p.is_file() and "__pycache__" not in p.parts}
scripts = {p.name: sha(p) for p in sorted((ROOT / "scripts").glob("*")) if p.is_file()}
tests = {str(p.relative_to(ROOT / "tests")): sha(p) for p in sorted((ROOT / "tests").rglob("*")) if p.is_file() and "__pycache__" not in p.parts}
inputs = {f"{c}_{m}.json": sha(ou.INPUTS / f"{c}_{m}.json") for c in ("BEZOS", "G0924", "G0926", "GCAL", "JOBS", "M35A", "MUSK") for m in ("FULL", "PREFIX")}
F0 = {(r["caso"], r["modo"]): r["UNICO_FAMILIAS_TOKENS_0"] for r in json.loads((ROOT / "tablas/ABLACION_VOTOS_LATERALES.json").read_text())}
cat = json.loads(PAT.read_text())
man = {"nombre": "BASE_ESTABLE_MOTOR_UNICO_V15_3_20260927", "congelado_hora_local": time.strftime("%Y-%m-%d %H:%M CST (UTC-6)"),
       "motor": {"archivo": "motor/MOTOR_V15_3_UNICO_20260927.py", "sha256": sha(ROOT / "motor/MOTOR_V15_3_UNICO_20260927.py"), "version": "V15.3_UNICO_20260927",
                 "nombre_en_run_dir": ou.orq.UNIF},
       "catalogo": {"archivo": "patterns_final_v14.json", "ruta_origen": str(PAT), "sha256": sha(PAT), "n_patrones": len(cat),
                    "configurable_por": "MOTOR_PATTERNS_PATH (env) o orquestador --catalogo RUTA; puentes con --puentes DIR (scripts/regenerar_puentes.py)"},
       "engine": {"archivo": "Engine_V5_CANONICO_SOLO.py", "sha256": ou.orq.ENGINE_OK, "bytes": 30507},
       "engine_prohibido_sha256": ou.orq.ENGINE_FAKE,
       "flags_por_defecto": {"MODO_ESTRICTO": "1 (on)", "FAMILIAS_TOKENS": "1 (on, EXPERIMENTAL)", "LAT_<PIEZA>": "1 (on)", "PYTHONHASHSEED": "0", "CONSOLIDADO_OFF": "''"},
       "piezas_motor_dir": motor_files, "piezas_run_dir": run_dir, "scripts": scripts, "tests": tests, "inputs": inputs,
       "linea_base": {"descripcion": "7 casos × FULL/PREFIX, r1 (r2 idéntica). top10/cierres/motivos por corrida; sha_nucleo = sha de [ranking, H1, H2, reporte_caso].",
                      "corridas": [{k: f.get(k) for k in ("caso", "modo", "top1", "top2", "top10", "H1", "H2", "cierre_vigente", "motivos_vigente", "cierre_estricto", "motivos_estricto",
                                                           "guardianes", "negativo_top1", "negativo_top2", "voto_familias_top1", "voto_familias_top2",
                                                           "aquiles_remuestreo_ganador", "aquiles_remuestreo_coincide_top1", "convergencia_lateral",
                                                           "sha_nucleo", "determinista_r1_r2_json_completo", "determinista_r1_r2_nucleo")} | {"referencia_FAMILIAS_TOKENS_0": F0.get((f["caso"], f["modo"]))} for f in T]},
       "equivalencias": {"UNICO_con_votos_laterales_apagados_vs_ESTRICTO_tirada": json.loads((ROOT / "tablas/UNICO_VOTOS0_vs_ESTRICTO.json").read_text())},
       "tests": json.loads((ROOT / "tablas/RESULTADO_TESTS_UNICO.json").read_text()),
       "candados": {"antes": json.loads((ROOT / "tablas/CANDADOS_ANTES.json").read_text()), "despues": json.loads((ROOT / "tablas/CANDADOS_DESPUES.json").read_text())},
       "como_medir_cambios": "bash scripts/correr_todo.sh [--catalogo RUTA --puentes DIR]; python3 scripts/analizar_unico.py; python3 scripts/comparar_corridas.py --raw raw"}
(ROOT / "BASE_ESTABLE_MANIFEST.json").write_text(json.dumps(man, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps({"motor": man["motor"]["sha256"][:16], "catalogo": man["catalogo"]["sha256"][:16], "n_patrones": man["catalogo"]["n_patrones"],
                  "piezas_motor_dir": len(motor_files), "piezas_run_dir": len(run_dir), "corridas": len(man["linea_base"]["corridas"])}))
