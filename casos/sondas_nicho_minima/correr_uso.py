#!/usr/bin/env python3
"""Corre una etapa de USO (U0..U4) sobre las 5 sondas + Napoleón F001
+ 2 casos largos (Mozart 10 + Napoleón 10), y extrae H1/H2 + estabilidad.

Etapas (acumulativas, por partes):
  U0: observación (las 4 piezas solo como traza; baseline de USO).
  U1: nicho USADO (voto nicho_campo alimenta el ranking; USO_NICHO=1).
  U2: + alias USADO (tokens del alias en la entrada, eje P).
  U3: + embudo USADO (RUIDO_ALIAS quita los clínicos; PERFIL_VENTANA deja).
  U4: + fix USADO (remap ambicion->autonomia por corte; la entrada ES
      el caso preparado).

Uso:  python3 casos/sondas_nicho_minima/correr_uso.py <ETAPA>
Sale: motor/runs_uso/<ETAPA>/RESUMEN_<ETAPA>.json
      casos/sondas_nicho_minima/uso/<ETAPA>/<CASO>.json  (entradas preparadas)
      motor/RESULT_<ETAPA>_<CASO>.json                   (completo, del runner)
Cada etapa arranca con el StinkBox VACÍO (como en la etapa anterior).
No modifica el motor; solo corre y extrae. La entrada original no se toca.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]          # repo (motor-autorizado)
MOTOR = ROOT / "motor"
SONDAS = ROOT / "casos" / "sondas_nicho_minima"
USO_DIR = SONDAS / "uso"

sys.path.insert(0, str(SONDAS))
from estabilidad import estabilidad  # noqa: E402
from preparar_uso import preparar  # noqa: E402

CASOS = [
    ("SONDA_MONROE_TIPO", SONDAS / "SONDA_MONROE_TIPO.json"),
    ("SONDA_ALEJANDRO_TIPO", SONDAS / "SONDA_ALEJANDRO_TIPO.json"),
    ("SONDA_JOSE_A", SONDAS / "SONDA_JOSE_A.json"),
    ("SONDA_JOSE_EF", SONDAS / "SONDA_JOSE_EF.json"),
    ("SONDA_FREUD_C", SONDAS / "SONDA_FREUD_C.json"),
    ("NAPOLEON_F001", ROOT / "casos" / "fabrica" / "cola" / "CAL_F001_01_NAPOLEON" / "entrada.json"),
    ("MOZART_10", ROOT / "casos" / "precedentes" / "MOZART_10_CORTES" / "INPUT_FROZEN.json"),
    ("NAPOLEON_10", Path("/home/hatch/workspace/u6-alterno/motor-cameo/casos/precedentes/NAPOLEON_10_CORTES/entrada.json")),
]

ETAPAS = ("U0", "U1", "U2", "U3", "U4")


def main():
    etapa = sys.argv[1]
    assert etapa in ETAPAS, f"etapa debe ser una de {ETAPAS}"
    outdir = MOTOR / "runs_uso" / etapa
    outdir.mkdir(parents=True, exist_ok=True)
    # Control: cada etapa arranca con el StinkBox VACÍO.
    for d in (ROOT / "STINKBOX_PERSISTENTE", ROOT / "STINKBOX_STORAGE"):
        shutil.rmtree(d, ignore_errors=True)
    env = os.environ.copy()
    env["STINKBOX_HOME"] = str(ROOT / "STINKBOX_PERSISTENTE")
    env["STINKBOX_STORAGE_ROOT"] = str(ROOT / "STINKBOX_STORAGE")
    if etapa in ("U1", "U2", "U3", "U4"):
        env["USO_NICHO"] = "1"  # el voto nicho_campo alimenta el ranking
    resumen = {"etapa": etapa, "casos": {}}
    for nombre, entrada in CASOS:
        tag = f"{etapa}_{nombre}"
        # Preparación de la entrada según la etapa (U0/U1: cruda).
        entrada_uso = entrada
        reportes = {}
        if etapa in ("U2", "U3", "U4"):
            orig = json.loads(Path(entrada).read_text(encoding="utf-8"))
            prep, reportes = preparar(orig, etapa)
            pdir = USO_DIR / etapa
            pdir.mkdir(parents=True, exist_ok=True)
            entrada_uso = pdir / f"{nombre}.json"
            entrada_uso.write_text(json.dumps(prep, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"[{etapa}] corriendo {nombre} ...", flush=True)
        p = subprocess.run(
            [sys.executable, "correr_estandar.py", str(entrada_uso), tag],
            cwd=str(MOTOR), env=env, text=True, capture_output=True, timeout=900)
        res = MOTOR / f"RESULT_{tag}.json"
        # exit=4 es INCOMPLETE_OUTPUT_DATA (falta un path en el recibo,
        # pre-existente: $.efectividad_corte_retenido.previo_error), pero
        # el RESULT se escribe completo. Solo es FALLO si no hay RESULT.
        if not res.is_file():
            resumen["casos"][nombre] = {"error": f"exit={p.returncode} sin RESULT",
                                        "stderr": p.stderr[-800:], "stdout": p.stdout[-800:]}
            print(f"[{etapa}] {nombre}: FALLO exit={p.returncode} sin RESULT", flush=True)
            continue
        try:
            est = estabilidad(res)
        except Exception as e:
            est = {"error_estabilidad": f"{type(e).__name__}: {e}"}
        s = {"exit": p.returncode, "entrada": str(entrada_uso),
             "preparacion": reportes, "estabilidad": est}
        resumen["casos"][nombre] = s
        print(f"[{etapa}] {nombre}: H1={est.get('H1')} H2={est.get('H2')} "
              f"margen={est.get('margen_final_H1H2')} persist={est.get('persist_cos', {}).get('media')}", flush=True)
    (outdir / f"RESUMEN_{etapa}.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[{etapa}] resumen en {outdir}/RESUMEN_{etapa}.json")


if __name__ == "__main__":
    main()
