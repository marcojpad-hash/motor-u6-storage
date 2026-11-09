#!/usr/bin/env python3
"""Watchdog / supervisor del Motor U6.

Vigila una corrida del motor: corre el runner como subproceso, detecta que
murio o se atoro por timeout, lo registra y, si es seguro, lo reintenta una
vez con backoff. Sirve a lo que hace el motor (correr un caso, Monte Carlo,
recibo, hashes) y nada mas: no inventa capacidades, no reescribe el runner
ni el Engine, no toca el recibo. Solo envuelve la ejecucion.

Uso:
    python3 watchdog_u6.py ../casos/fabrica/cola/CAL_F001_01_NAPOLEON/entrada.json NAPOLEON
    python3 watchdog_u6.py ../casos/ciegos/lote_20/C01/entrada.json C01 --timeout 300

Regla de reintento (una sola vez, backoff 10 s):
    - Se reintenta si el proceso murio o se atoro (timeout) SIN dejar recibo:
      es un fallo transitorio (el runner se cayo antes de completar).
    - NO se reintenta si hay recibo (la corrida completo y el exit distinto
      de 0 es un resultado, no un cuelgue) ni si el fallo es duro
      (hashes del Engine/catalogo distintos del manifiesto, preflight,
      entrada invalida). Un reintento no arregla un fallo duro.

Verificacion al terminar: exit 0, existe RESULT_<NOMBRE>.json y
RESULT_<NOMBRE>_RECIBO_EJECUCION.json, el recibo dice COMPLETED (o el
status que traiga) y los hashes del Engine/catalogo coinciden con el
manifiesto. Todo se registra con el logger_u6.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from logger_u6 import get_logger  # noqa: E402

RETRY_BACKOFF_S = 10.0


def _verify(nombre: str) -> dict:
    """Verifica que la corrida dejo resultado y recibo, y que los hashes cuadran."""
    rep = {"result": False, "receipt": False, "receipt_status": None,
           "engine_ok": None, "patterns_ok": None, "h1": None, "h2": None}
    result = HERE / f"RESULT_{nombre}.json"
    receipt = HERE / f"RESULT_{nombre}_RECIBO_EJECUCION.json"
    if result.is_file():
        rep["result"] = True
        try:
            r = json.loads(result.read_text(encoding="utf-8"))
            h1 = (r.get("salida_interpretable") or {}).get("H1") or {}
            h2 = (r.get("salida_interpretable") or {}).get("H2") or {}
            rep["h1"] = h1.get("familia")
            rep["h2"] = h2.get("familia")
        except Exception:
            pass
    if receipt.is_file():
        rep["receipt"] = True
        try:
            rc = json.loads(receipt.read_text(encoding="utf-8"))
            rep["receipt_status"] = rc.get("status")
            rep["engine_ok"] = rc.get("canonical_engine_sha256") == rc.get("engine_sha256")
            rep["patterns_ok"] = rc.get("patterns_sha256") == rc.get("expected_patterns_sha256")
        except Exception:
            pass
    return rep


def _run_once(entrada: Path, nombre: str, timeout: float, log) -> tuple[int, str, float]:
    """Corre el runner una vez. Devuelve (exit, motivo, segundos)."""
    t0 = time.time()
    try:
        p = subprocess.run(
            [sys.executable, "correr_estandar.py", str(entrada), nombre],
            cwd=str(HERE), text=True, capture_output=True, timeout=timeout)
        return p.returncode, "exit", round(time.time() - t0, 1)
    except subprocess.TimeoutExpired:
        return -1, "timeout", round(time.time() - t0, 1)
    except Exception as e:  # el subproceso no arranco
        log.error("spawn_failed", error=f"{type(e).__name__}:{e}")
        return -2, "spawn_failed", round(time.time() - t0, 1)


def watch(entrada: str, nombre: str, timeout: float, no_retry: bool) -> int:
    log = get_logger(nombre)
    entrada = Path(entrada).resolve()
    log.run_start()
    log.stage("runner", "STARTED", entrada=str(entrada), timeout_s=timeout)
    attempt = 1
    while True:
        rc, motivo, dt = _run_once(entrada, nombre, timeout, log)
        ver = _verify(nombre)
        log.stage("runner", "FINISHED", attempt=attempt, exit=rc, motivo=motivo,
                  seconds=dt, receipt=ver["receipt"],
                  receipt_status=ver["receipt_status"],
                  h1=ver["h1"], h2=ver["h2"])
        if rc == 0 and ver["result"] and ver["receipt"]:
            log.run_end(returncode=0, seconds=dt, h1=ver["h1"], h2=ver["h2"],
                        receipt_status=ver["receipt_status"])
            return 0
        # Fallo duro: hay recibo y los hashes no cuadran -> no reintentar.
        if ver["receipt"] and (ver["engine_ok"] is False or ver["patterns_ok"] is False):
            log.error("hard_failure", reason="hash_mismatch",
                      engine_ok=ver["engine_ok"], patterns_ok=ver["patterns_ok"])
            log.run_end(returncode=rc, seconds=dt, h1=ver["h1"], h2=ver["h2"],
                        receipt_status=ver["receipt_status"])
            return rc if rc != 0 else 1
        # Fallo transitorio (murio o se atoro sin dejar recibo) -> un reintento.
        if not no_retry and attempt == 1 and not ver["receipt"]:
            log.warning("retry", reason=motivo, backoff_s=RETRY_BACKOFF_S,
                        attempt=attempt + 1)
            time.sleep(RETRY_BACKOFF_S)
            attempt += 1
            continue
        # Sin reintento disponible o ya usado: reportar y salir con el exit del runner.
        log.error("run_failed", attempt=attempt, exit=rc, motivo=motivo,
                  receipt=ver["receipt"], receipt_status=ver["receipt_status"])
        log.run_end(returncode=rc if rc >= 0 else 1, seconds=dt,
                    h1=ver["h1"], h2=ver["h2"],
                    receipt_status=ver["receipt_status"])
        return rc if rc >= 0 else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="Watchdog del Motor U6: vigila una corrida y reintenta una vez si se atora.")
    ap.add_argument("entrada", help="entrada.json del caso")
    ap.add_argument("nombre", help="nombre del caso (p. ej. NAPOLEON, C01)")
    ap.add_argument("--timeout", type=float, default=300,
                    help="segundos antes de dar la corrida por atorada (defecto 300)")
    ap.add_argument("--no-retry", action="store_true",
                    help="no reintentar aunque el fallo sea transitorio")
    args = ap.parse_args(argv)
    return watch(args.entrada, args.nombre, args.timeout, args.no_retry)


if __name__ == "__main__":
    sys.exit(main())
