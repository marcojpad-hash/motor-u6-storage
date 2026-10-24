from __future__ import annotations
import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
CANON_SHA = "d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1"

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

main = load("v153_main_contract_test", ROOT / "motor" / "MOTOR_V15_3_UNICO_20260927.py")
native = load("v153_native_contract_test", ROOT / "motor" / "MOTOR_V15_3_NATIVO_V0_9_UNICO.py")

class TestCanonicalCatalogContract(unittest.TestCase):
    def test_catalog_schema_is_named_pattern_map_not_numeric_vectors(self):
        path = ROOT / "motor" / "patterns_final_v14.json"
        import json
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertIsInstance(data, dict)
        self.assertEqual(len(data), 244)
        first = next(iter(data.values()))
        self.assertIn("tokens_favor", first)
        self.assertIn("tokens_contra", first)
        self.assertNotIn("vector", first)

    def test_main_default_catalog_hash_and_count_are_enforced(self):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("MOTOR_PATTERNS_PATH", None)
            os.environ.pop("MOTOR_PATTERNS_SHA256", None)
            r = main._verify_patterns_contract()
        self.assertEqual(r["status"], "CANONICAL_VERIFIED")
        self.assertEqual(r["sha256"], CANON_SHA)
        self.assertEqual(r["n_patterns"], 244)

    def test_main_rejects_tampered_default_catalog(self):
        with tempfile.TemporaryDirectory() as td:
            bad = Path(td) / "patterns.json"
            bad.write_text('{"one": {}}', encoding="utf-8")
            with patch.object(main, "_PATTERNS_PATH", return_value=bad), patch.dict(os.environ, {}, clear=False):
                os.environ.pop("MOTOR_PATTERNS_PATH", None)
                with self.assertRaisesRegex(RuntimeError, "CANONICAL_PATTERNS_HASH_MISMATCH"):
                    main._verify_patterns_contract()

    def test_native_default_catalog_hash_and_count_are_enforced(self):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("MOTOR_PATTERNS_PATH", None)
            os.environ.pop("MOTOR_PATTERNS_SHA256", None)
            lib, _ = native.load_canonical()
        self.assertEqual(len(lib), 244)
        self.assertEqual(native._CATALOG_INTEGRITY["status"], "CANONICAL_VERIFIED")
        self.assertEqual(native._CATALOG_INTEGRITY["sha256"], CANON_SHA)

    def test_native_rejects_tampered_default_catalog(self):
        with tempfile.TemporaryDirectory() as td:
            bad = Path(td) / "patterns.json"
            bad.write_text('{"one": {}}', encoding="utf-8")
            with patch.object(native, "_PATTERNS_PATH", return_value=bad), patch.dict(os.environ, {}, clear=False):
                os.environ.pop("MOTOR_PATTERNS_PATH", None)
                with self.assertRaisesRegex(RuntimeError, "CANONICAL_PATTERNS_HASH_MISMATCH"):
                    native.load_canonical()

    def test_terminal_normalizer_does_not_rewrite_unresolved_states_as_resolved(self):
        raw = {
            "resolucion_operativa_final": {"status": "RESUELTO_OPERACIONALMENTE"},
            "decimo_hombre_esteroides": {"ataques": [
                {"estado": "NO_RESUELTO_SIN_RANKING_CONTRAFACTUAL"},
                {"estado": "NO_REABIERTO_SIN_RIVAL_DERROTADOR"},
            ]},
            "nota": "LATENTE EMPATE SIN_CANDIDATOS",
        }
        cleaned = main._normalizar_salida_terminal(raw)
        states = [x["estado"] for x in cleaned["decimo_hombre_esteroides"]["ataques"]]
        self.assertEqual(states[0], "NO_RESUELTO_SIN_RANKING_CONTRAFACTUAL")
        self.assertEqual(states[1], "NO_REABIERTO_SIN_RIVAL_DERROTADOR")
        self.assertEqual(cleaned["nota"], "LATENTE EMPATE SIN_CANDIDATOS")

    def test_presentation_layer_never_reintroduces_null_for_missing_fill(self):
        import math
        raw = {
            "H1": {"family": "h1", "rank_fusion": 0.5, "margen": 0.0, "peso_relativo": 0.5},
            "H2": {"family": "h2", "rank_fusion": 0.5, "margen": 0.0, "peso_relativo": 0.5},
            "predictor": {"candidates": [
                {"family": "h1", "features": {}}, {"family": "h2", "features": {}}
            ]},
            "cierre_final": {"margen": 0.0, "grado": "FRAGIL", "mezcla": {}}
        }
        out = main._aplicar_equivalencia_presentacion(raw)
        self.assertEqual(out["H1"]["porcentaje_relleno"], "TORTUGAS")
        self.assertEqual(out["H2"]["porcentaje_relleno"], "TORTUGAS")
        self.assertEqual(out["H1"]["porcentaje_relleno_estado"], "TORTUGAS_SIN_MEDIDA_DE_RELLENO")
        def walk(x):
            if isinstance(x, dict):
                for v in x.values(): yield from walk(v)
            elif isinstance(x, list):
                for v in x: yield from walk(v)
            else: yield x
        vals = list(walk(out))
        self.assertFalse(any(v is None for v in vals))
        self.assertFalse(any(isinstance(v, float) and not math.isfinite(v) for v in vals))

    def test_custom_catalog_requires_matching_hash_if_pinned(self):
        with tempfile.TemporaryDirectory() as td:
            custom = Path(td) / "custom.json"
            custom.write_text('{"one": {"tokens_favor": {"a": 0.6}}}', encoding="utf-8")
            with patch.object(native, "_PATTERNS_PATH", return_value=custom), patch.dict(os.environ, {"MOTOR_PATTERNS_PATH": str(custom), "MOTOR_PATTERNS_SHA256": "wrong"}, clear=False):
                with self.assertRaisesRegex(RuntimeError, "CUSTOM_PATTERNS_HASH_MISMATCH"):
                    native.load_canonical()


    def test_tortugas_executes_below_separation_gate_even_outside_narrow_020_band(self):
        candidates = [
            {"family": "H1", "rank_fusion": 10.0},
            {"family": "H2", "rank_fusion": 9.2},
            {"family": "H3", "rank_fusion": 8.0},
            {"family": "H4", "rank_fusion": 7.0},
        ]
        pred = {"calibracion_estructural": {"entropia": {"n_candidatos": 4}}}
        prior_tortugas = {
            "status": "EJECUTADO",
            "veredicto": "TORTUGAS_NO_SEPARA_TOP1",
            "apoyo_por_candidata": {
                "H1": {"votos_argmax": 0, "evidencia_media": 0.45},
                "H2": {"votos_argmax": 2, "evidencia_media": 0.46},
                "H3": {"votos_argmax": 1, "evidencia_media": 0.40},
                "H4": {"votos_argmax": 0, "evidencia_media": 0.35},
            },
        }
        ordered, tortugas, band = main._ordenar_020(
            candidates, pred, [], [], {}, {}, {}, {}, {}, tortugas_prev=prior_tortugas
        )
        self.assertFalse(band["hay_casi_igualdad"])
        self.assertTrue(band["requiere_medicion_tortugas"])
        self.assertTrue(band["tortugas_ejecutado"])
        self.assertFalse(band["tortugas_aplicado_al_orden"])
        self.assertTrue(band["tortugas_no_reordena_fuera_de_banda"])
        self.assertEqual(tortugas["status"], "EJECUTADO")
        self.assertEqual([x["family"] for x in ordered], ["H1", "H2", "H3", "H4"])
        self.assertEqual(ordered[0]["apoyo_tortugas_votos"], 0)

if __name__ == "__main__":
    unittest.main(verbosity=2)

