#!/usr/bin/env python3
"""Corre las pruebas existentes (copias verbatim de CONSOLIDADO_GUARDIANES_20260927/tests y del sensor de perfil del narrador)
contra las piezas de MOTOR_UNICO_20260927/motor/. Arma un espejo temporal con la estructura que esperan
(guardianes/ = copia de motor/, rescate/ = rescate de guardianes, tests/ = copias) y no modifica nada fuera de /tmp."""
import json, shutil, subprocess, sys, tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; MOTOR = ROOT / "motor"
GROOT = Path("/workspace/CONSOLIDADO_GUARDIANES_20260927"); PN = Path("/workspace/PERFIL_NARRADOR_20260927/sensor")
R = []
def run(nombre, cmd, cwd):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env={"PYTHONDONTWRITEBYTECODE": "1", "PATH": "/usr/bin:/bin", "HOME": "/tmp"})
    out = (p.stdout + p.stderr).strip()
    n_pass, n_fail = out.count("[PASS]"), out.count("[FAIL]")
    print(f"== {nombre}: exit {p.returncode} · PASS {n_pass} · FAIL {n_fail}\n{out[-900:]}\n")
    R.append({"test": nombre, "exit": p.returncode, "n_pass_marcas": n_pass, "n_fail_marcas": n_fail, "ultima_linea": out.splitlines()[-1] if out else ""})
with tempfile.TemporaryDirectory() as td:
    td = Path(td); shutil.copytree(MOTOR, td / "guardianes"); shutil.copytree(GROOT / "rescate", td / "rescate")
    (td / "tests").mkdir(); shutil.copytree(GROOT / "tests/originales", td / "tests/originales")
    for f in ("run_tests_originales.py", "test_guardian_tropos.py"): shutil.copy2(GROOT / "tests" / f, td / "tests" / f)
    shutil.copy2(ROOT / "tests/test_nuevos_guardianes_UNICO.py", td / "tests/test_nuevos_guardianes.py")
    (td / "raw").mkdir()
    for f in sorted((ROOT / "raw").glob("RESULT_UNICO__*__r[12].json")): shutil.copy2(f, td / "raw" / f.name)
    rb = td / "runs" / "UNICO__BEZOS__PREFIX__r1"
    sys.path.insert(0, str(ROOT / "scripts")); import orquestador_unico as ou
    ou.orq.build("UNICO", rb); shutil.copytree(MOTOR / "familias_tokens", rb / "familias_tokens", dirs_exist_ok=True)
    shutil.copy2(ou.INPUTS / "BEZOS_PREFIX.json", rb / "_INPUT.json")
    run("originales (post hoc 0.5.0 y 0.5.1, latencia, polaridad, memento/acero smoke) con detrás 2.3.3", [sys.executable, "tests/run_tests_originales.py"], td)
    run("nuevos guardianes (Copi, falacias, acero, contrato sobre las 28 corridas UNICO)", [sys.executable, "tests/test_nuevos_guardianes.py"], td)
    run("guardián tropos Beristáin (92)", [sys.executable, "tests/test_guardian_tropos.py"], td)
if PN.is_dir():
    with tempfile.TemporaryDirectory() as td:
        td = Path(td); shutil.copytree(PN, td / "sensor")
        shutil.copy2(MOTOR / "sensor_perfil_narrador_v0_1.py", td / "sensor" / "sensor_perfil_narrador_v0_1.py")
        run("sensor perfil del narrador", [sys.executable, "test_sensor_perfil_narrador.py"], td / "sensor")
run("detrás v2 2.3.3 (falso positivo 'esta' demostrativo)", [sys.executable, str(ROOT / "tests/test_detras_2_3_3.py")], ROOT / "motor")
(ROOT / "tablas/RESULTADO_TESTS_UNICO.json").write_text(json.dumps(R, ensure_ascii=False, indent=1), encoding="utf-8")
sys.exit(0 if all(r["exit"] == 0 for r in R) else 1)
