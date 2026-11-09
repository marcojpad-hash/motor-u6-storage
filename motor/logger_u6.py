#!/usr/bin/env python3
"""Logger estructurado del Motor U6.

Sirve a lo que hace el motor: correr casos, Monte Carlo, recibo y hashes.
No es un logger generico: cada evento es un paso de una corrida (inicio,
etapa, fin) con el case_id, los hashes del Engine y del catalogo, y el
recibo. Escribe a archivo (JSONL, una linea por evento) y a consola
(linea legible). No toca el recibo JSON del runner ni el resultado.

Uso:
    from logger_u6 import get_logger
    log = get_logger("C01")
    log.run_start(engine_sha="...", patterns_sha="...", input_sha="...")
    log.stage("motor_run", "COMPLETED", monte_carlo=True)
    log.run_end(returncode=0, seconds=14.5, h1="31_conflicto_con_un_dios",
                h2="30_ambicion", receipt_status="COMPLETED")

Variables de entorno:
    U6_LOG_LEVEL   DEBUG|INFO|WARNING|ERROR (defecto INFO)
    U6_LOG_DIR     directorio de logs (defecto motor/logs/)
    U6_LOG_CONSOLE 0 para no escribir a consola (defecto 1)
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

LEVELS = {"DEBUG": 10, "INFO": 20, "WARNING": 30, "ERROR": 40}
DEFAULT_LEVEL = os.environ.get("U6_LOG_LEVEL", "INFO").upper()
LOG_DIR = Path(os.environ.get("U6_LOG_DIR", str(Path(__file__).resolve().parent / "logs")))
CONSOLE = os.environ.get("U6_LOG_CONSOLE", "1") != "0"


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _log_file_for_today() -> Path:
    return LOG_DIR / ("u6_" + datetime.now(timezone.utc).strftime("%Y-%m-%d") + ".log")


class U6Logger:
    """Logger de corridas del motor. Un evento = un paso de una corrida."""

    def __init__(self, case_id=None, level=None, log_file=None, console=None):
        self.case_id = case_id
        self.level = LEVELS.get((level or DEFAULT_LEVEL).upper(), 20)
        self.console = CONSOLE if console is None else bool(console)
        self.log_file = log_file  # Path o None (None = sin archivo)

    def _emit(self, level: str, event: str, **fields):
        if LEVELS[level] < self.level:
            return
        rec = {"ts": _ts(), "level": level, "case_id": self.case_id,
               "event": event, **fields}
        if self.console:
            kv = " ".join(f"{k}={v}" for k, v in fields.items())
            print(f"{rec['ts']} [{level}] [{self.case_id or '-'}] {event}"
                  + (f" {kv}" if kv else ""), file=sys.stderr)
        if self.log_file is not None:
            try:
                self.log_file.parent.mkdir(parents=True, exist_ok=True)
                with open(self.log_file, "a", encoding="utf-8") as fh:
                    fh.write(json.dumps(rec, ensure_ascii=False, default=str) + "\n")
            except Exception:
                pass  # el log nunca rompe la corrida

    def debug(self, event: str, **fields):
        self._emit("DEBUG", event, **fields)

    def info(self, event: str, **fields):
        self._emit("INFO", event, **fields)

    def warning(self, event: str, **fields):
        self._emit("WARNING", event, **fields)

    def error(self, event: str, **fields):
        self._emit("ERROR", event, **fields)

    # --- Eventos propios del motor (correr casos, Monte Carlo, recibo, hashes) ---

    def run_start(self, engine_sha=None, patterns_sha=None, input_sha=None, **fields):
        self.info("run_start", engine_sha=(engine_sha or "")[:12],
                  patterns_sha=(patterns_sha or "")[:12],
                  input_sha=(input_sha or "")[:12], **fields)

    def stage(self, stage: str, status: str, **fields):
        self.info("stage", stage=stage, status=status, **fields)

    def run_end(self, returncode=None, seconds=None, h1=None, h2=None,
                receipt_status=None, **fields):
        level = "INFO" if returncode == 0 else "ERROR"
        self._emit(level, "run_end", returncode=returncode, seconds=seconds,
                   h1=h1, h2=h2, receipt_status=receipt_status, **fields)


def get_logger(case_id=None, level=None, log_file=None, console=None):
    """Devuelve un logger. log_file=None usa el archivo del dia (motor/logs/).
    Pasa log_file=False para no escribir archivo."""
    if log_file is None:
        log_file = _log_file_for_today()
    elif log_file is False:
        log_file = None
    return U6Logger(case_id=case_id, level=level, log_file=log_file, console=console)


class NullLogger:
    """Sustituto que no hace nada; el runner lo usa si el logger no se puede importar."""

    def __init__(self, *a, **k):
        pass

    def __getattr__(self, name):
        def _noop(*a, **k):
            return None
        return _noop
