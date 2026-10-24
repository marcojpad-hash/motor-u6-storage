#!/usr/bin/env python3
"""Cargador lateral MÍNIMO de reanudación (no existía entrypoint de resume en el paquete).

Lee *_CHECKPOINT_REANUDABLE.json, verifica que input/runner sigan siendo los mismos bytes
(sha256) y que el resultado pausado no fue alterado; luego vuelve a ejecutar correr_estandar.py
sobre el MISMO input (el motor no es incremental: no hay re-entrada por corte, así que
"reanudar" = re-ejecución completa del input sellado). Escribe un archivo de linaje.
No toca motor, Engine ni patterns; no fabrica decisiones.
uso: python3 scripts/reanudar_desde_checkpoint.py CHECKPOINT.json NOMBRE SALIDA.json
"""
import hashlib, json, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main(argv):
    if len(argv) < 4: print(__doc__, file=sys.stderr); return 2
    ck_path, nombre, out = Path(argv[1]).resolve(), argv[2], Path(argv[3]).resolve()
    ck = json.loads(ck_path.read_text(encoding="utf-8"))
    checks = {"schema": ck.get("checkpoint_schema") == "U6_CONTINUITY_CHECKPOINT_V1",
              "status_pausada": ck.get("status") == "PAUSADA_REANUDABLE",
              "input_sha256": Path(ck["input_path"]).is_file() and sha(ck["input_path"]) == ck.get("input_sha256"),
              "runner_sha256": sha(ROOT / "correr_estandar.py") == ck.get("runner_sha256"),
              "result_pausado_sha256": Path(ck["result_path"]).is_file() and sha(ck["result_path"]) == ck.get("result_sha256")}
    if not all(checks.values()):
        print(json.dumps({"ok": False, "stage": "checkpoint_verification", "checks": checks}, ensure_ascii=False)); return 7
    proc = subprocess.run([sys.executable, str(ROOT / "correr_estandar.py"), ck["input_path"], nombre, str(out)],
                          cwd=str(ROOT), text=True, capture_output=True)
    lin = {"lineage_schema": "U6_RESUME_LINEAGE_V1", "checkpoint_path": str(ck_path), "checkpoint_sha256": sha(ck_path),
           "checks": checks, "paused_result_path": ck["result_path"], "paused_reason": (ck.get("continuidad_corrida") or {}).get("reason"),
           "resumed_output_path": str(out), "resumed_returncode": proc.returncode,
           "resumed_output_sha256": sha(out) if out.is_file() else "NO_ESCRITO",
           "modo": "RE_EJECUCION_COMPLETA_DEL_INPUT_SELLADO (motor sin re-entrada por corte)",
           "stdout_tail": proc.stdout[-1500:], "stderr_tail": proc.stderr[-1500:]}
    out.with_name(out.stem + "_LINAJE_REANUDACION.json").write_text(json.dumps(lin, ensure_ascii=False, indent=2), encoding="utf-8")
    sys.stdout.write(proc.stdout); sys.stderr.write(proc.stderr)
    return proc.returncode
if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
