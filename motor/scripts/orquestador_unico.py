# ESTÁNDAR: no uses este script en frío. Usa ../correr_estandar.py
# Este archivo sigue amarrado a TIRADA_ESTRICTA + CONSOLIDADO (rutas /workspace).
# Se deja por compatibilidad de la batería de 7 casos.
"""
Uso:
  orquestador_unico.py CASO MODO REP [--catalogo RUTA.json] [--puentes DIR] [--tag TAG] [--env K=V ...] [--keep]
  orquestador_unico.py NOMBRE --input RUTA.json [--catalogo RUTA.json] [--env K=V ...]
--catalogo: usa otro catálogo de patrones (se copia al run dir con su nombre y se fija MOTOR_PATTERNS_PATH).
            Sin --catalogo = patterns_final_v14.json (d827dcc3).
A CIEGAS: no lee resultados registrados. Solo inputs y piezas.
"""
import importlib.util, json, os, shutil, subprocess, sys, time, hashlib
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
_TIRADA = Path("/workspace/TIRADA_ESTRICTA_20260927/scripts/orquestador_estricto.py")
if not _TIRADA.is_file():
    raise SystemExit("Este orquestador necesita TIRADA_ESTRICTA. En frío usa: python3 correr_estandar.py cuts.json NOMBRE")
spec = importlib.util.spec_from_file_location("orq_estricto", "/workspace/TIRADA_ESTRICTA_20260927/scripts/orquestador_estricto.py")
oe = importlib.util.module_from_spec(spec); spec.loader.exec_module(oe)
orq = oe.orq
MOTOR = ROOT / "motor"
EXTRA = sorted(p for p in MOTOR.iterdir() if p.is_file() and p.name != "MOTOR_V15_3_UNICO_20260927.py" and p.suffix in (".py", ".json"))
orq.VERSIONS["UNICO"] = {**orq.VERSIONS["ESTRICTO"], "motor": MOTOR / "MOTOR_V15_3_UNICO_20260927.py",
                         "extra": list(orq.VERSIONS["ESTRICTO"]["extra"]) + EXTRA}
INPUTS = Path("/workspace/CONSOLIDADO_DIAGNOSTICO_20260927/inputs")
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()

def correr(name, inp, raw_dir, catalogo=None, env_extra=None, keep_run=False, ver="UNICO", puentes=None):
    rd = ROOT / "runs" / f"{ver}__{name}"
    if rd.exists(): shutil.rmtree(rd)
    orq.build(ver, rd)
    shutil.copytree(MOTOR / "familias_tokens", rd / "familias_tokens", dirs_exist_ok=True)
    shutil.copy2(inp, rd / "_INPUT.json")
    puentes_info = None
    if puentes:  # puentes regenerados para otro catálogo (scripts/regenerar_puentes.py)
        puentes_info = {}
        for fn in ("PUENTE_244_FAMILIAS.json", "MATRIZ_EQUIVALENCIAS_ESCALA.json"):
            src = Path(puentes) / fn
            if src.is_file(): shutil.copy2(src, rd / fn); puentes_info[fn] = sha(src)
    env = {**os.environ, "PYTHONHASHSEED": "0", "PYTHONDONTWRITEBYTECODE": "1", "CONSOLIDADO_OFF": ""}
    cat_info = {"ruta_origen": None, "sha256": orq.PAT_OK, "es_default_v14": True}
    if catalogo:
        catalogo = Path(catalogo); dst = rd / ("CATALOGO__" + catalogo.name)
        shutil.copy2(catalogo, dst); env["MOTOR_PATTERNS_PATH"] = str(dst)
        cat_info = {"ruta_origen": str(catalogo), "sha256": sha(catalogo), "es_default_v14": sha(catalogo) == orq.PAT_OK}
    else:
        env.pop("MOTOR_PATTERNS_PATH", None)
    env.update(env_extra or {})
    raw_dir.mkdir(parents=True, exist_ok=True)
    out = raw_dir / f"RESULT_{ver}__{name}.json"
    t0 = time.time()
    p = subprocess.run([sys.executable, orq.UNIF, "_INPUT.json", str(out)], cwd=rd, capture_output=True, text=True, timeout=1800, env=env)
    dt = time.time() - t0
    canon = (orq.sha(rd / "Engine_V5_CANONICO_SOLO.py") == orq.ENGINE_OK and orq.sha(rd / "patterns_final_v14.json") == orq.PAT_OK)
    meta = {"name": f"{ver}__{name}", "version": ver, "input": str(inp), "input_sha256": orq.sha(inp), "exit": p.returncode,
            "seconds": round(dt, 3), "canon_run_dir_after_ok": canon, "catalogo": cat_info, "puentes": puentes_info, "env_extra": env_extra or {},
            "motor_sha256": sha(MOTOR / "MOTOR_V15_3_UNICO_20260927.py"),
            "output": str(out) if out.exists() else None, "stderr_tail": p.stderr[-3000:] if p.returncode else ""}
    (raw_dir / f"META_{ver}__{name}.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    if not keep_run: shutil.rmtree(rd)
    return meta

def main():
    a = sys.argv[1:]
    cat = a[a.index("--catalogo") + 1] if "--catalogo" in a else None
    tag = a[a.index("--tag") + 1] if "--tag" in a else ""
    env = {}
    for i, x in enumerate(a):
        if x == "--env": k, v = a[i + 1].split("=", 1); env[k] = v
    keep = "--keep" in a
    pz = a[a.index("--puentes") + 1] if "--puentes" in a else None
    if "--input" in a:
        name = a[0]; inp = Path(a[a.index("--input") + 1])
    else:
        case, mode, rep = a[:3]; name = f"{case}__{mode}__r{rep}"; inp = INPUTS / f"{case}_{mode}.json"
    if tag: name = f"{name}__{tag}"
    raw = ROOT / ("raw" if not tag else "raw_variantes")
    m = correr(name, inp, raw, cat, env, keep, puentes=pz)
    print(json.dumps({k: m[k] for k in ("name", "exit", "seconds", "canon_run_dir_after_ok")}))
if __name__ == "__main__": main()
