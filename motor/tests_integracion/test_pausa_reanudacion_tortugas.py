"""Integración: TORTUGAS forzado a fallar (monkeypatch vía sitecustomize del harness, sin editar motor)
-> PAUSADA_REANUDABLE, exit 6, sin apuesta final autorizada, checkpoint escrito; luego reanudación."""
import json, os, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
INP = ROOT / "inputs" / "THEMISTOCLES_FREEZE_480BC_CATALOG_REPAIR_R2.json"
OUT = ROOT / "tests_integracion" / "_out"

def _env(falla):
    e = {k: v for k, v in os.environ.items() if k not in ("CALDERO_BUSQUEDA_VIVA",)}  # puente grabado: sin red, determinista
    e["PYTHONDONTWRITEBYTECODE"] = "1"
    if falla:
        e["U6_HARNESS_TORTUGAS_FALLA"] = "1"
        e["PYTHONPATH"] = str(ROOT / "tests_integracion" / "harness_site") + os.pathsep + e.get("PYTHONPATH", "")
    else:
        e.pop("U6_HARNESS_TORTUGAS_FALLA", None)
    return e

def test_pausa_y_reanudacion():
    OUT.mkdir(exist_ok=True)
    paused = OUT / "RESULT_PAUSA.json"
    p = subprocess.run([sys.executable, str(ROOT / "correr_estandar.py"), str(INP), "IT_TORTUGAS_PAUSA", str(paused)],
                       cwd=str(ROOT), env=_env(True), text=True, capture_output=True, timeout=600)
    assert p.returncode == 6, (p.returncode, p.stderr[-2000:])
    r = json.loads(paused.read_text(encoding="utf-8"))
    assert r["estado_ejecucion"] == "PAUSADA_REANUDABLE"
    cont = r["continuidad_corrida"]
    assert cont["status"] == "PAUSADA_REANUDABLE" and cont["final_decision_authorized"] is False
    fin = r["resolucion_operativa_final"]
    assert fin.get("tortugas_ejecutado") is False and fin.get("estado_durante_corrida") == "RESOLUCION_REQUERIDA"
    rec = json.loads((OUT / "RESULT_PAUSA_RECIBO_EJECUCION.json").read_text(encoding="utf-8"))
    assert rec["status"] == "PAUSED_REQUIRES_RESUME"
    # Ningún campo muestra apuesta autorizada ni cierre de H mientras está pausada
    assert fin["status"] == "PAUSADA_REANUDABLE" and fin["decision_final_autorizada"] is False
    assert r["resolucion_operativa_terminal_017"]["decision"]["status"] == "PAUSADA_REANUDABLE"
    assert r["salida_interpretable"]["apuesta_multiescenario"]["estado"] == "APUESTA_NO_AUTORIZADA_PAUSA_REANUDABLE"
    assert r["salida_interpretable"]["apuesta_multiescenario"]["apuesta_autorizada"] is False
    assert r["H_estado"] == "PROVISIONAL_NO_AUTORIZADA_POR_PAUSA" and r.get("H1")
    _txt = json.dumps({k: v for k, v in r.items() if k not in ("features", "decimo_hombre_esteroides")})
    assert '"APUESTA_MULTIESCENARIO_SELLABLE"' not in _txt.replace('_previo_a_pausa": "APUESTA_MULTIESCENARIO_SELLABLE"', "")
    assert cont["tortugas_status_observed"] == "ERROR"
    assert isinstance(cont["last_valid_cut"], dict) and cont["last_valid_cut"]["index"] == cont["last_valid_cut"]["n_cortes"] - 1
    assert json.loads(p.stdout.strip().splitlines()[-1])["ok"] is False
    ck = OUT / "RESULT_PAUSA_CHECKPOINT_REANUDABLE.json"
    assert ck.is_file()
    ckd = json.loads(ck.read_text(encoding="utf-8"))
    assert ckd["status"] == "PAUSADA_REANUDABLE" and ckd["continuidad_corrida"]["final_decision_authorized"] is False
    # Reanudación con TORTUGAS operativo
    resumed = OUT / "RESULT_REANUDADO.json"
    q = subprocess.run([sys.executable, str(ROOT / "scripts" / "reanudar_desde_checkpoint.py"), str(ck), "IT_TORTUGAS_REANUDADO", str(resumed)],
                       cwd=str(ROOT), env=_env(False), text=True, capture_output=True, timeout=600)
    assert q.returncode in (0, 5), (q.returncode, q.stderr[-2000:])  # 5 = COMPLETED_WITH_METADATA_GAP (hueco conocido)
    s = json.loads(resumed.read_text(encoding="utf-8"))
    assert "continuidad_corrida" not in s and s.get("estado_ejecucion") != "PAUSADA_REANUDABLE"
    assert s["resolucion_operativa_final"]["tortugas_ejecutado"] is True
    assert s["resolucion_operativa_final"]["status"] == "RESUELTO_OPERACIONALMENTE"
    rec2 = json.loads((OUT / "RESULT_REANUDADO_RECIBO_EJECUCION.json").read_text(encoding="utf-8"))
    assert rec2["status"] in ("COMPLETED", "COMPLETED_WITH_METADATA_GAP")
    lin = json.loads((OUT / "RESULT_REANUDADO_LINAJE_REANUDACION.json").read_text(encoding="utf-8"))
    assert all(lin["checks"].values())
