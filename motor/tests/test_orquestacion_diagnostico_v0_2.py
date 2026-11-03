import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "motor" / "orquestacion" / "diagnostico_falsos_positivos_v0_2.py"
spec = importlib.util.spec_from_file_location("poe_diagnostic", SCRIPT)
diagnostic = importlib.util.module_from_spec(spec)
import sys
sys.modules[spec.name] = diagnostic
spec.loader.exec_module(diagnostic)


class TestPoeLinguisticDiagnostic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = diagnostic.run()

    def test_gold_labels_are_separated_before_scoring(self):
        metrics = self.report["profile_detection"]
        self.assertEqual(metrics["n_total"], 22)
        self.assertEqual(metrics["n_negative"], 13)
        self.assertEqual(metrics["n_positive"], 4)
        self.assertEqual(metrics["n_ambiguous_excluded_from_binary_metrics"], 5)
        self.assertEqual(metrics["tp"] + metrics["fn"], 4)
        self.assertEqual(metrics["fp"] + metrics["tn"], 13)

    def test_counterfactual_gender_pairs_are_reported(self):
        bias = self.report["gender_counterfactuals"]
        self.assertEqual(bias["n_pairs"], 3)
        self.assertEqual(len(bias["pairs"]), 3)
        self.assertGreaterEqual(bias["n_different"], 0)

    def test_ambiguity_cases_are_not_silently_dropped(self):
        cases = self.report["ambiguity_and_argumentation"]["cases"]
        self.assertEqual(len(cases), 7)
        self.assertTrue(all("marks" in c and "causals" in c and "gold_issue" in c for c in cases))
        self.assertTrue(any(c["gold_issue"] == "referente_pronominal_ambiguo" and not c["copi_ambiguity_marked"] for c in cases))

    def test_real_guardian_wrapper_is_executed(self):
        block = self.report["actual_guardian_wrapper"]
        self.assertEqual(block["guardian"], "PREGUNTA_DETRAS_V2")
        self.assertIn(block["bandera"], ("LIMPIO", "MARCA", "ERROR"))

    def test_report_keeps_interpretive_limits(self):
        rules = self.report["interpretation_rules"]
        self.assertTrue(any("no equivale a falsedad" in x for x in rules))
        self.assertTrue(any("no se cuentan como FP ni FN" in x for x in rules))


if __name__ == "__main__":
    unittest.main(verbosity=2)
