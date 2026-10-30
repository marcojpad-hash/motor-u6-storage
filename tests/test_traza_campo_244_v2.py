import importlib.util
import pathlib
import shutil
import tempfile
import unittest

# Carga exactamente el punto de entrada que consume MOTOR_V15_3_NATIVO_V0_9_UNICO.
MODULE = pathlib.Path(__file__).resolve().parents[1] / "motor" / "motor" / "traza_campo_244.py"
SPEC = importlib.util.spec_from_file_location("traza_campo_244_runtime", MODULE)
traza = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(traza)


class TrazaCampo244RuntimeSpecs(unittest.TestCase):
    def setUp(self):
        self.A = {"H1": 0.50, "H2": 0.50, "H3": 0.70}
        self.B = {"H1": 0.51, "H3": 0.69}
        self.C = {"H1": 0.73, "H2": 0.66, "H3": 0.68}
        self.cortes = [("A", self.A), ("B", self.B), ("C", self.C)]

    def test_runtime_entrypoint_uses_v2_and_does_not_impute(self):
        r = traza.analizar(self.cortes)
        self.assertEqual(r["modulo"], "TRAZA_CAMPO_244_V2")
        self.assertEqual(r["n_hipotesis"], 3)
        h2 = next(x for x in r["fichas"] if x["h"] == "H2")
        self.assertEqual(h2["P"], [0.5, None, 0.66])
        self.assertEqual(h2["d"], [None, None])
        self.assertEqual(r["integridad"]["n_valores_ausentes"], 1)

    def test_delta_and_rank_require_two_observed_endpoints(self):
        r = traza.analizar(self.cortes)
        ab, bc = r["vectores"]
        self.assertEqual((ab["n_delta_observados"], ab["n_datos_ausentes"]), (2, 1))
        self.assertEqual((bc["n_delta_observados"], bc["n_datos_ausentes"]), (2, 1))
        h2 = next(x for x in ab["movimiento"] if x["h"] == "H2")
        self.assertIsNone(h2["d"])
        self.assertIsNone(h2["drango"])
        self.assertEqual(h2["estado"], "DATO_AUSENTE")

    def test_renewable_signal_skips_missing_endpoint(self):
        r = traza.origenes_renovables(self.cortes, delta_senal=0.05)
        self.assertFalse(any(x["h"] == "H2" and x["en"] == "B"
                             for x in r["todas_las_cruces"]))
        self.assertTrue(any(x["h"] == "H1" and x["en"] == "C"
                            for x in r["todas_las_cruces"]))


    def test_adapter_resolves_v2_after_runner_relocates_it(self):
        source_root = pathlib.Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            runtime = root / "runs" / "ESTANDAR_CASE"
            runtime.mkdir(parents=True)
            shutil.copy2(source_root / "motor" / "motor" / "traza_campo_244.py",
                         runtime / "traza_campo_244.py")
            shutil.copy2(source_root / "motor" / "traza_campo_244_v2.py",
                         root / "traza_campo_244_v2.py")
            spec = importlib.util.spec_from_file_location("traza_relocated", runtime / "traza_campo_244.py")
            relocated = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(relocated)
            result = relocated.analizar(self.cortes)
            self.assertEqual(result["modulo"], "TRAZA_CAMPO_244_V2")
            self.assertEqual(result["integridad"]["n_valores_ausentes"], 1)

    def test_empty_input_rejected(self):
        with self.assertRaises(ValueError):
            traza.analizar([])

    def test_nonfinite_value_rejected(self):
        with self.assertRaises(ValueError):
            traza.analizar([("A", {"H1": float("nan")})])

    def test_negative_signal_threshold_rejected(self):
        with self.assertRaises(ValueError):
            traza.origenes_renovables(self.cortes, delta_senal=-0.01)

    def test_single_cut_has_no_transition_vectors(self):
        r = traza.analizar([("A", {"H1": 0.4})])
        self.assertEqual(r["vectores"], [])
        self.assertEqual(r["fichas"][0]["neto"], 0.0)


if __name__ == "__main__":
    unittest.main()
