#!/usr/bin/env python3
"""Corre el lote 20 ciego con el runner (offline, motor agnóstico) y congela
las salidas. Reanudable: salta los casos que ya tienen SALIDA_CONGELADA.json
y RECIBO_EJECUCION.json. No abre la custodia (identidad/desenlace/destino).
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

REPO = Path("/home/hatch/workspace/cbm-repos/motor-u6-storage")
BASE = REPO / "casos" / "ciegos" / "lote_20"
MOTOR = REPO / "motor"
SLOTS = [f"C{i:02d}" for i in range(1, 21)]


def frozen_output(result: dict, receipt: dict) -> dict:
    h1 = (result.get("salida_interpretable") or {}).get("H1") or result.get("H1") or {}
    h2 = (result.get("salida_interpretable") or {}).get("H2") or result.get("H2") or {}
    apuesta = result.get("apuesta") or {}
    principal = apuesta.get("apuesta_principal") or {}
    conjunto = ((result.get("salida_interpretable") or {}).get("conjunto_hipotesis_abiertas") or {})
    return {
        "case_id": result.get("case_id"),
        "freeze": result.get("freeze"),
        "congelado_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "H1": {"familia": h1.get("familia"), "grado": h1.get("grado"),
               "porcentaje_relleno": h1.get("porcentaje_relleno"),
               "peso_relativo": h1.get("peso_relativo"),
               "predictibilidad_estructural_pct": h1.get("predictibilidad_estructural_pct")},
        "H2": {"familia": h2.get("familia"), "grado": h2.get("grado"),
               "porcentaje_relleno": h2.get("porcentaje_relleno"),
               "peso_relativo": h2.get("peso_relativo"),
               "predictibilidad_estructural_pct": h2.get("predictibilidad_estructural_pct")},
        "set": [h.get("familia") for h in (conjunto.get("hipotesis") or [])],
        "escenario_principal": principal.get("escenario"),
        "apuesta": {"estado": apuesta.get("estado"),
                    "escenarios": apuesta.get("escenarios"),
                    "apuesta_principal": principal},
        "destino_predicho": result.get("apuesta_destino_personal"),
        "monte_carlo": (result.get("motor") or {}).get("monte_carlo_audit"),
        "result_sha256": receipt.get("output_sha256"),
        "recibo_status": receipt.get("status"),
        "engine_sha256": receipt.get("canonical_engine_sha256"),
        "patterns_sha256": receipt.get("patterns_sha256"),
    }


def main():
    env = {**os.environ, "CALDERO_BUSCADOR": "offline", "SEARCH_PROVIDER": "offline"}
    resumen = []
    for slot in SLOTS:
        d = BASE / slot
        salida = d / "SALIDA_CONGELADA.json"
        recibo = d / "RECIBO_EJECUCION.json"
        if salida.is_file() and recibo.is_file():
            print(f"{slot}: ya congelado, se salta")
            resumen.append({"slot": slot, "estado": "YA_CONGELADO"})
            continue
        t0 = time.time()
        p = subprocess.run(
            [sys.executable, "correr_estandar.py",
             str(BASE / slot / "entrada.json"), slot],
            cwd=str(MOTOR), env=env, text=True,
            capture_output=True, timeout=300)
        dt = round(time.time() - t0, 1)
        result_path = MOTOR / f"RESULT_{slot}.json"
        receipt_path = MOTOR / f"RESULT_{slot}_RECIBO_EJECUCION.json"
        if p.returncode != 0 or not result_path.is_file() or not receipt_path.is_file():
            print(f"{slot}: FALLO exit={p.returncode} dt={dt}s")
            print((p.stdout or "")[-500:])
            print((p.stderr or "")[-500:])
            resumen.append({"slot": slot, "estado": "FALLO", "exit": p.returncode, "segundos": dt})
            continue
        result = json.loads(result_path.read_text(encoding="utf-8"))
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        frozen = frozen_output(result, receipt)
        salida.write_text(json.dumps(frozen, ensure_ascii=False, indent=2), encoding="utf-8")
        recibo.write_text(receipt_path.read_text(encoding="utf-8"), encoding="utf-8")
        h1 = frozen["H1"]["familia"]
        h2 = frozen["H2"]["familia"]
        print(f"{slot}: OK exit={p.returncode} {dt}s H1={h1} H2={h2} recibo={receipt.get('status')}")
        resumen.append({"slot": slot, "estado": "OK", "exit": p.returncode,
                        "segundos": dt, "H1": h1, "H2": h2,
                        "recibo": receipt.get("status")})
    out = BASE / "RESUMEN_LOTE_20.json"
    out.write_text(json.dumps({"lote": "LOTE_20_CIEGO", "casos": resumen,
                               "generado_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())},
                              ensure_ascii=False, indent=2), encoding="utf-8")
    ok = sum(1 for r in resumen if r["estado"] in ("OK", "YA_CONGELADO"))
    print(f"\n{ok}/20 congelados. Resumen en {out}")


if __name__ == "__main__":
    main()
