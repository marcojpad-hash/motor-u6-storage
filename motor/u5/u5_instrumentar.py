#!/usr/bin/env python3
"""Envoltura instrumentada de correr_estandar.py (sin modificarlo).
Uso: python3 u5/u5_instrumentar.py <mismos argumentos que correr_estandar.py>
Registra, mientras corre de verdad:
  - llamadas a funciones por archivo .py (sys.setprofile, eventos 'call'), solo archivos bajo el pack/run dir;
  - archivos abiertos para lectura/escritura (audit hook 'open');
  - módulos importados (sys.modules) con su __file__.
Al terminar escribe <salida>_TRAZA_U5.json y genera el recibo U5 (u5_recibo.py). Devuelve el exit code del runner."""
import sys, os, json, time, threading, runpy, importlib.util
from pathlib import Path
U5 = Path(__file__).resolve().parent; PACK = U5.parent
sys.path.insert(0, str(U5))
argv = [str(PACK / "correr_estandar.py")] + sys.argv[1:]
src = Path(argv[1]).resolve()
nombre = argv[2] if len(argv) > 2 and not argv[2].endswith(".json") else src.stem
out = Path(argv[-1]).resolve() if len(argv) > 3 else PACK / f"RESULT_{nombre}.json"
calls = {}; opens = {}
pfx = str(PACK)
def prof(frame, event, arg):
    if event == "call":
        fn = frame.f_code.co_filename
        if fn.startswith(pfx):
            calls[fn] = calls.get(fn, 0) + 1
def hook(ev, args):
    if ev == "open" and args and isinstance(args[0], (str, bytes, os.PathLike)):
        p = os.fsdecode(args[0]) if not isinstance(args[0], str) else args[0]
        mode = args[1] if len(args) > 1 and isinstance(args[1], str) else "r"
        k = (os.path.abspath(p), "w" if any(c in (mode or "") for c in "wax+") else "r")
        opens[k] = opens.get(k, 0) + 1
sys.addaudithook(hook)
t0 = time.time(); rc = None; err = None
spec = importlib.util.spec_from_file_location("correr_estandar_u5", argv[0])
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
sys.setprofile(prof); threading.setprofile(prof)
try:
    rc = mod.main(argv)
except SystemExit as e:
    rc = e.code if isinstance(e.code, int) else 1
except Exception as e:
    import traceback; err = traceback.format_exc(); rc = 99
finally:
    sys.setprofile(None); threading.setprofile(None)
mods = {}
for name, m in list(sys.modules.items()):
    f = getattr(m, "__file__", None)
    if f and str(f).startswith(pfx): mods[name] = os.path.abspath(f)
traza = {"traza_version": "U5_TRAZA_V1", "metodo": "sys.setprofile(call)+sys.addaudithook(open)+sys.modules",
         "t0_epoch": t0, "t1_epoch": time.time(), "runner_exit": rc, "runner_exception": err,
         "argv": argv, "input": str(src), "output": str(out), "pack": pfx,
         "calls_por_archivo": calls,
         "aperturas": [{"path": p, "modo": m, "n": n} for (p, m), n in sorted(opens.items())],
         "modulos_importados": mods}
tp = out.with_name(out.stem + "_TRAZA_U5.json")
tp.parent.mkdir(parents=True, exist_ok=True)
tp.write_text(json.dumps(traza, ensure_ascii=False, indent=1), encoding="utf-8")
try:
    import u5_recibo
    u5_recibo.construir(tp)
except Exception:
    import traceback; print("U5_RECIBO_FALLO\n" + traceback.format_exc(), file=sys.stderr)
sys.exit(rc if isinstance(rc, int) else 1)
