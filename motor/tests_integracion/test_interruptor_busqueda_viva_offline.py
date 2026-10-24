"""OFFLINE: CALDERO_BUSQUEDA_VIVA=1 ignora el puente grabado y usa la cadena agnóstica (simulada, red bloqueada).
Query ciega intacta (mismo sha que el puente grabado). Sin el interruptor se usa el puente grabado."""
import json, os, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
INP = ROOT / "inputs" / "THEMISTOCLES_FREEZE_480BC_CATALOG_REPAIR_R2.json"
OUT = ROOT / "tests_integracion" / "_out"


def _run(viva, name):
    e = {k: v for k, v in os.environ.items() if k not in ("CALDERO_BUSQUEDA_VIVA", "U6_HARNESS_TORTUGAS_FALLA")}
    e["PYTHONDONTWRITEBYTECODE"] = "1"; e["U6_HARNESS_BUSCADOR_MOCK"] = "1"
    e["PYTHONPATH"] = str(ROOT / "tests_integracion" / "harness_site") + os.pathsep + e.get("PYTHONPATH", "")
    if viva: e["CALDERO_BUSQUEDA_VIVA"] = "1"
    out = OUT / f"RESULT_{name}.json"
    p = subprocess.run([sys.executable, str(ROOT / "correr_estandar.py"), str(INP), name, str(out)], cwd=str(ROOT), env=e,
                       text=True, capture_output=True, timeout=600)
    return p, json.loads(out.read_text(encoding="utf-8"))


def test_interruptor_viva_offline():
    OUT.mkdir(exist_ok=True)
    bridge = json.loads(INP.read_text(encoding="utf-8"))["caldero_search_bridge"]
    p, r = _run(True, "IT_VIVA_MOCK")
    assert p.returncode in (0, 5), p.stderr[-2000:]
    rec = r["external_archetype_search_receipt"]
    assert rec["provider"] == "mock_ok" and rec["status"] == "EXECUTED" and rec["result_count"] == 3
    assert rec["bridge_grabado_ignorado"] == bridge.get("bridge_id")
    assert rec["query_sha256"] == bridge["blind_query_sha256"]
    assert [a["status"] for a in rec["attempts"]] == ["FAILED", "EXECUTED"]
    p2, r2 = _run(False, "IT_PUENTE_GRABADO")
    assert p2.returncode in (0, 5), p2.stderr[-2000:]
    rec2 = r2["external_archetype_search_receipt"]
    assert "bridge_grabado_ignorado" not in rec2 and rec2["provider"] != "mock_ok"
    assert rec2["query_sha256"] == rec["query_sha256"]
