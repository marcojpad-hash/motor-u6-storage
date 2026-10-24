#!/usr/bin/env python3
"""Puente de revisión diaria con Xiaomi MiMo (API compatible con OpenAI).

Fuentes oficiales (consultadas 2026-10-24):
- https://mimo.mi.com/docs/en-US/api/chat/openai-api  -> POST https://api.xiaomimimo.com/v1/chat/completions,
  header `api-key: $MIMO_API_KEY`; modelos: mimo-v2.6-flash, mimo-v2.6-pro, mimo-v2.6-pro-ultraspeed.
- https://mimo.mi.com/docs/quick-start/first-api-call -> base_url pay-as-you-go https://api.xiaomimimo.com/v1
  (Token Plan: https://token-plan-cn.xiaomimimo.com/v1 con llave tp-...).
- https://mimo.mi.com/models/en-US/mimo-v2.6-flash -> specs y precios.
Nota: MiMo-V2.5/V2.5-Pro se retiraron el 2026-10-21; usar serie V2.6.

Solo lee el repo (git log/diff). Nunca modifica motor/ ni casos/.
Solo stdlib. Uso: python3 scripts/revision_mimo.py [--dry-run]
"""
from __future__ import annotations
import argparse, datetime as dt, json, os, subprocess, sys, urllib.request, urllib.error
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DIR = REPO / "avances" / "mimo"
SHA_FILE = DIR / ".ultimo_sha"
USO_FILE = DIR / "uso.json"
BASE_URL = os.environ.get("MIMO_BASE_URL", "https://api.xiaomimimo.com/v1")
MODELO = os.environ.get("MIMO_MODEL", "mimo-v2.6-flash")
TOPE_DIARIO = int(os.environ.get("MIMO_TOPE_DIARIO", "200000"))  # tokens/día
MAX_SALIDA = 4000
MAX_CHARS_DIFF = int(os.environ.get("MIMO_MAX_CHARS", "24000"))
FECHA_LIMITE = dt.date(2026, 12, 31)
PROTEGIDO = ("motor/", "casos/")  # se resumen solo por stat, nunca se mandan completos

def git(*a, cwd=None) -> str:
    return subprocess.run(["git", *a], cwd=cwd or REPO, check=True, capture_output=True, text=True).stdout

def leer_uso() -> dict:
    if USO_FILE.exists():
        return json.loads(USO_FILE.read_text())
    return {"dias": {}, "llamadas": []}

def tokens_hoy(uso: dict, hoy: str) -> int:
    return uso.get("dias", {}).get(hoy, 0)

def commits_nuevos(cwd=None) -> tuple[str | None, list[str]]:
    base = SHA_FILE.read_text().strip() if SHA_FILE.exists() else None
    head = git("rev-parse", "HEAD", cwd=cwd).strip()
    if base == head:
        return base, []
    rango = f"{base}..{head}" if base else head
    args = ["rev-list", "--reverse", rango] + ([] if base else ["-n", "20"])
    shas = git(*args, cwd=cwd).split()
    return base, shas

def resumen_diff(base: str | None, shas: list[str], limite: int = MAX_CHARS_DIFF, cwd=None) -> str:
    if not shas:
        return ""
    desde = base or f"{shas[0]}^"
    try:
        git("rev-parse", desde, cwd=cwd)
    except subprocess.CalledProcessError:
        desde = subprocess.run(["git", "hash-object", "-t", "tree", "--stdin"], cwd=cwd or REPO, input="", capture_output=True, text=True, check=True).stdout.strip()  # árbol vacío
    hasta = shas[-1]
    partes = ["## Commits", git("log", "--format=%h %ad %an: %s", "--date=short", hasta, f"-n{len(shas)}", cwd=cwd)]
    partes += ["## Stat", git("diff", "--stat", desde, hasta, cwd=cwd)]
    patch = git("diff", "-U2", desde, hasta, "--", ".", *[f":(exclude){p}" for p in PROTEGIDO],
                ":(exclude)avances/mimo", cwd=cwd)
    partes += ["## Diff (sin motor/ ni casos/)", patch]
    texto = "\n".join(partes)
    if len(texto) > limite:
        texto = texto[:limite] + f"\n...[recortado a {limite} caracteres]"
    return texto

def llamar_mimo(key: str, resumen: str) -> tuple[str, dict]:
    cuerpo = {
        "model": MODELO,
        "messages": [
            {"role": "system", "content": "Eres revisor de código. Responde en español, conciso: riesgos, bugs, "
             "violaciones de reglas (nunca tocar el Engine canónico ni los 244 patrones/hashes), y sugerencias."},
            {"role": "user", "content": resumen},
        ],
        "max_completion_tokens": MAX_SALIDA,
        "stream": False,
        "thinking": {"type": "disabled"},
    }
    req = urllib.request.Request(f"{BASE_URL}/chat/completions", data=json.dumps(cuerpo).encode(),
                                 headers={"api-key": key, "Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=180) as r:
        data = json.loads(r.read())
    return data["choices"][0]["message"]["content"], data.get("usage", {})

def main(argv=None, hoy: dt.date | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="no llama a la API ni escribe nada")
    a = ap.parse_args(argv)
    hoy = hoy or dt.date.today()
    if hoy > FECHA_LIMITE:
        print(f"Alto: fecha límite {FECHA_LIMITE} superada. No se llama a MiMo."); return 0
    base, shas = commits_nuevos()
    if not shas:
        print("Sin commits nuevos desde", base, "- nada que revisar."); return 0
    resumen = resumen_diff(base, shas)
    estimado = len(resumen) // 3 + MAX_SALIDA
    uso = leer_uso(); usados = tokens_hoy(uso, hoy.isoformat())
    print(f"{len(shas)} commit(s) {shas[0][:8]}..{shas[-1][:8]}; resumen {len(resumen)} chars; "
          f"~{estimado} tokens estimados; hoy usados {usados}/{TOPE_DIARIO}; modelo {MODELO} @ {BASE_URL}")
    if usados + estimado > TOPE_DIARIO:
        print("Alto: se superaría el tope diario de tokens."); return 0
    if a.dry_run:
        print("--dry-run: no se llama a la API ni se escribe nada.\n---\n" + resumen[:1500]); return 0
    key = os.environ.get("MIMO_API_KEY", "").strip()
    if not key:
        print("MIMO_API_KEY no definida - salida limpia sin llamar."); return 0
    try:
        texto, usage = llamar_mimo(key, resumen)
    except (urllib.error.URLError, KeyError, ValueError) as e:
        print("Error llamando a MiMo:", e); return 1
    total = int(usage.get("total_tokens") or 0)
    DIR.mkdir(parents=True, exist_ok=True)
    out = DIR / f"{hoy.isoformat()}_revision.md"
    with out.open("a") as f:
        f.write(f"# {hoy.isoformat()} — Revisión MiMo ({MODELO})\n\n## Shas revisados\n"
                + "\n".join(f"- {s}" for s in shas)
                + f"\n\n## Tokens\nprompt={usage.get('prompt_tokens')} completion={usage.get('completion_tokens')} total={total}\n\n"
                + f"## Revisión\n{texto}\n\n")
    uso.setdefault("dias", {})[hoy.isoformat()] = usados + total
    uso.setdefault("llamadas", []).append({"fecha": dt.datetime.now().isoformat(timespec="seconds"), "modelo": MODELO,
                                           "desde": base, "hasta": shas[-1], "n_commits": len(shas), "usage": usage})
    USO_FILE.write_text(json.dumps(uso, indent=2, ensure_ascii=False) + "\n")
    SHA_FILE.write_text(shas[-1] + "\n")
    print("Revisión escrita en", out.relative_to(REPO), "tokens:", total)
    return 0

if __name__ == "__main__":
    sys.exit(main())
