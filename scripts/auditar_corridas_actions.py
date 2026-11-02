#!/usr/bin/env python3
"""Audita ejecuciones recientes de GitHub Actions y registra tiempos en America/Mexico_City."""
from __future__ import annotations
import datetime as dt
import json
import os
import pathlib
import urllib.error
import urllib.request
from zoneinfo import ZoneInfo

API = os.environ["GITHUB_API_URL"].rstrip("/")
REPO = os.environ["GITHUB_REPOSITORY"]
TOKEN = os.environ["GH_TOKEN"]
CDMX = ZoneInfo("America/Mexico_City")
OUT = pathlib.Path("avances/auditoria_corridas")
NOW = dt.datetime.now(dt.timezone.utc)
SINCE = NOW - dt.timedelta(days=7)


def api(path: str) -> dict:
    req = urllib.request.Request(
        API + "/repos/" + REPO + path,
        headers={"Accept": "application/vnd.github+json", "Authorization": "Bearer " + TOKEN,
                 "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "motor-u6-run-auditor"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def parse(value):
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00")) if value else None


def local(value):
    parsed = parse(value)
    return parsed.astimezone(CDMX).isoformat(timespec="seconds") if parsed else None


def main():
    runs = api("/actions/runs?per_page=100").get("workflow_runs", [])
    selected = []
    for run in runs:
        created = parse(run.get("created_at"))
        if not created or created < SINCE or run.get("status") != "completed":
            continue
        rid = run["id"]
        jobs = api(f"/actions/runs/{rid}/jobs?per_page=100").get("jobs", [])
        artifacts = api(f"/actions/runs/{rid}/artifacts?per_page=100").get("artifacts", [])
        started = run.get("run_started_at")
        ended = run.get("updated_at") if run.get("conclusion") else None
        duration = None
        if started and ended:
            duration = round((parse(ended) - parse(started)).total_seconds(), 3)
        selected.append({
            "run_id": rid, "run_attempt": run.get("run_attempt"), "workflow": run.get("name"),
            "event": run.get("event"), "actor": (run.get("actor") or {}).get("login"),
            "branch": run.get("head_branch"), "head_sha": run.get("head_sha"),
            "created_at_utc": run.get("created_at"), "created_at_cdmx": local(run.get("created_at")),
            "started_at_utc": started, "started_at_cdmx": local(started),
            "finished_at_utc": ended, "finished_at_cdmx": local(ended),
            "duration_seconds": duration, "status": run.get("status"), "conclusion": run.get("conclusion"),
            "url": run.get("html_url"),
            "jobs": [{"name": j.get("name"), "status": j.get("status"), "conclusion": j.get("conclusion"),
                      "started_at_utc": j.get("started_at"), "finished_at_utc": j.get("completed_at"),
                      "duration_seconds": round((parse(j["completed_at"]) - parse(j["started_at"])).total_seconds(), 3)
                      if j.get("started_at") and j.get("completed_at") else None}
                     for j in jobs],
            "artifacts": [{"name": a.get("name"), "created_at_utc": a.get("created_at"),
                           "expired": a.get("expired"), "size_in_bytes": a.get("size_in_bytes")}
                          for a in artifacts],
        })
    selected.sort(key=lambda x: (x["created_at_utc"], x["run_id"]), reverse=True)
    OUT.mkdir(parents=True, exist_ok=True)
    payload = {"timezone": "America/Mexico_City", "window_days": 7, "runs": selected}
    json_path = OUT / "ULTIMO_ESTADO.json"
    md_path = OUT / "ULTIMO_ESTADO.md"
    json_text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    lines = ["# Auditoría automática de corridas Motor U6", "",
             "Ventana: últimos 7 días. Horas mostradas en America/Mexico_City; marcas UTC conservadas en JSON.", "",
             "| Run | Workflow | Evento | Creación CDMX | Inicio CDMX | Fin CDMX | Duración (s) | Estado |",
             "|---:|---|---|---|---|---|---:|---|"]
    for r in selected:
        lines.append(f"| {r['run_id']} | {r['workflow']} | {r['event']} | {r['created_at_cdmx']} | {r['started_at_cdmx'] or 'NO_DISPONIBLE'} | {r['finished_at_cdmx'] or 'NO_DISPONIBLE'} | {r['duration_seconds'] if r['duration_seconds'] is not None else 'NO_DISPONIBLE'} | {r['conclusion']} |")
    lines += ["", "## Fallos y cancelaciones", ""]
    bad = [r for r in selected if r["conclusion"] not in ("success", "neutral", "skipped")]
    if bad:
        for r in bad:
            failed_jobs = [j for j in r["jobs"] if j["conclusion"] not in ("success", "neutral", "skipped")]
            lines.append(f"- Run {r['run_id']} ({r['workflow']}): {r['conclusion']}; jobs: " +
                         (", ".join(f"{j['name']}={j['conclusion']}" for j in failed_jobs) or "sin detalle de job") +
                         f"; {r['url']}")
    else:
        lines.append("- Sin fallos/cancelaciones en la ventana consultada.")
    lines += ["", "## Límites", "",
              "- Este snapshot cubre los últimos 7 días y hasta 100 ejecuciones devueltas por la API.",
              "- Si GitHub no entrega una marca temporal, queda NO_DISPONIBLE; no se sustituye por la hora del commit.",
              "- La auditoría registra y clasifica; no reintenta corridas ni abre desenlaces sellados."]
    md_text = "\n".join(lines) + "\n"
    changed = (not json_path.exists() or json_path.read_text(encoding="utf-8") != json_text or
               not md_path.exists() or md_path.read_text(encoding="utf-8") != md_text)
    if changed:
        json_path.write_text(json_text, encoding="utf-8")
        md_path.write_text(md_text, encoding="utf-8")
        print(f"AUDIT_UPDATED runs={len(selected)} failures={len(bad)}")
    else:
        print(f"AUDIT_UNCHANGED runs={len(selected)} failures={len(bad)}")


if __name__ == "__main__":
    main()
