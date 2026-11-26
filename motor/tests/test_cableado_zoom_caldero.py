"""V7 (C-F1): el filtro de identidad zoom devuelve sus descartes al Caldero.

Antes el zoom corría pero no devolvía descartes al Caldero (ACTIVA_MUDA
perpetuo). Ahora las fuentes que SON el sujeto del caso
(misma_identidad_zoom_in) salen de tokens_neighbors, pero solo si ningún
otro recurso las sostiene.
"""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # motor/
MOTOR_DIR = ROOT / "motor"
UNICO = MOTOR_DIR / "MOTOR_V15_3_UNICO_20260927.py"


def _load_unico():
    spec = importlib.util.spec_from_file_location("motor_unico_v7_cf1", str(UNICO))
    mod = importlib.util.module_from_spec(spec)
    sys.modules["motor_unico_v7_cf1"] = mod
    spec.loader.exec_module(mod)
    return mod


_URL_A = "https://example.com/themistocles"
_URL_B = "https://example.com/sea-power"


def _out_sintetico():
    return {
        "audit": {"raw_sources_before_self_match": [
            {"url": _URL_A, "title": "Themistocles, el estratega de Salamina",
             "snippet": "Themistocles convenció a los atenienses de construir la flota."},
            {"url": _URL_B, "title": "Sea Power in the Peloponnesian War",
             "snippet": "Estudio de la estrategia marítima durante la guerra."},
        ]},
        "caldero_input": {"tokens_neighbors": [
            {"token": "solo_a", "source_refs": [_URL_A]},
            {"token": "solo_b", "source_refs": [_URL_B]},
            {"token": "ambos", "source_refs": [_URL_A, _URL_B]},
            {"token": "sin_refs", "source_refs": []},
        ]},
    }


def test_zoom_descarta_fuente_misma_identidad_y_poda_tokens():
    m = _load_unico()
    out = _out_sintetico()
    audit = m._aplicar_filtro_zoom_caldero(out, {"person": "Themistocles"})
    assert audit["status"] == "EXECUTED", audit
    assert audit["n_descartadas"] == 1, audit
    assert audit["n_tokens_antes"] == 4 and audit["n_tokens_despues"] == 3, audit
    toks = {r["token"] for r in out["caldero_input"]["tokens_neighbors"]}
    assert toks == {"solo_b", "ambos", "sin_refs"}, toks


def test_zoom_sin_identidad_queda_activa_muda_y_no_toca_tokens():
    m = _load_unico()
    out = _out_sintetico()
    audit = m._aplicar_filtro_zoom_caldero(out, {})
    assert audit["status"] == "ACTIVA_MUDA", audit
    assert len(out["caldero_input"]["tokens_neighbors"]) == 4


def test_zoom_en_corrida_real_themistocles(tmp_path):
    # Vivo (subproceso correr_estandar.py, THEMISTOCLES): el zoom corre en la
    # corrida real, no descarta nada (las 3 fuentes no son el sujeto) y H
    # queda intacta.
    entrada = ROOT / "inputs" / "THEMISTOCLES_FREEZE_480BC_CATALOG_REPAIR_R2.json"
    salida = tmp_path / "resultado_cf1.json"
    r = subprocess.run([sys.executable, "correr_estandar.py", str(entrada),
                        "V7_CF1_SMOKE", str(salida)],
                       cwd=str(ROOT), capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-2000:]
    res = json.loads(salida.read_text(encoding="utf-8"))
    cb = (res.get("features") or {}).get("caldero_busqueda_arquetipos") or {}
    z = (cb.get("audit") or {}).get("zoom_identity")
    assert z is not None, "sin zoom_identity en una corrida real"
    assert z.get("status") == "EXECUTED", z
    assert z.get("n_descartadas") == 0, z
    assert z.get("n_tokens_antes") == z.get("n_tokens_despues") == 72, z
    assert (res.get("H1") or {}).get("family") == "arquetipo_el_gobernante"
    assert (res.get("H2") or {}).get("family") == "13_enemistad_de_parientes"
