import importlib.util
import pathlib
import unittest

MODULE = pathlib.Path(__file__).resolve().parents[1] / "motor" / "traza_campo_244_v2.py"
SPEC = importlib.util.spec_from_file_location("traza_campo_244_v2", MODULE)
traza = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(traza)


class TrazaCampo244V2Specs(unittest.TestCase):
    def setUp(self):
        self.A = {"H1": 0.50, "H2": 0.50, "H3": 0.70}
        self.B = {"H1": 0.51, "H3": 0.69}
        self.C = {"H1": 0.73, "H2": 0.66, "H3": 0.68}
        self.cortes = [("A", self.A), ("B", self.B), ("C", self.C)]

    def test_union_preserved_and_missing_not_imputed(self):
        r = traza.analizar(self.cortes)
        self.assertEqual(r["n_hipotesis"], 3)
        h2 = next(x for x in r["fichas"] if x["h"] == "H2")
        self.assertEqual(h2["P"], [0.5, None, 0.66])
        self.assertEqual(h2["d"], [None, None])
        self.assertEqual(r["integridad"]["n_valores_ausentes"], 1)

    def test_delta_counts_only_observed_pairs(self):
        r = traza.analizar(self.cortes)
        ab, bc = r["vectores"]
        self.assertEqual((ab["n_delta_observados"], ab["n_datos_ausentes"]), (2, 1))
        self.assertEqual((bc["n_delta_observados"], bc["n_datos_ausentes"]), (2, 1))
        h1 = next(x for x in ab["movimiento"] if x["h"] == "H1")
        self.assertAlmostEqual(h1["d"], 0.01, places=6)
        h2 = next(x for x in ab["movimiento"] if x["h"] == "H2")
        self.assertIsNone(h2["d"])
        self.assertEqual(h2["estado"], "DATO_AUSENTE")

    def test_rank_changes_only_when_present_in_both_cuts(self):
        r = traza.analizar(self.cortes)
        h2_ab = next(x for x in r["vectores"][0]["movimiento"] if x["h"] == "H2")
        self.assertIsNone(h2_ab["drango"])
        h1_ab = next(x for x in r["vectores"][0]["movimiento"] if x["h"] == "H1")
        self.assertIsNotNone(h1_ab["drango"])

    def test_empty_input_rejected(self):
        with self.assertRaises(ValueError):
            traza.analizar([])

    def test_nonfinite_value_rejected(self):
        with self.assertRaises(ValueError):
            traza.analizar([("A", {"H1": float("nan")})])

    def test_negative_signal_threshold_rejected(self):
        with self.assertRaises(ValueError):
            traza.origenes_renovables(self.cortes, delta_senal=-0.01)

    def test_renewable_crossings_skip_missing_endpoint(self):
        r = traza.origenes_renovables(self.cortes, delta_senal=0.05)
        self.assertFalse(any(x["h"] == "H2" and x["en"] == "B"
                             for x in r["todas_las_cruces"]))
        self.assertTrue(any(x["h"] == "H1" and x["en"] == "C"
                            for x in r["todas_las_cruces"]))

    def test_single_cut_has_no_transition_vectors(self):
        r = traza.analizar([("A", {"H1": 0.4})])
        self.assertEqual(r["vectores"], [])
        self.assertEqual(r["fichas"][0]["neto"], 0.0)


if __name__ == "__main__":
    unittest.main()
