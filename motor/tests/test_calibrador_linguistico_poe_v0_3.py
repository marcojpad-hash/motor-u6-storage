import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "motor" / "orquestacion" / "calibrador_linguistico_poe_v0_3.py"
spec = importlib.util.spec_from_file_location("poe_calibrator_v03", SCRIPT)
calibrator = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = calibrator
spec.loader.exec_module(calibrator)


class TestPoeCalibratorV03(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = calibrator.run()

    def test_same_case_baseline_comparison_records_all_signs(self):
        base = self.report["gold_corpus"]["baseline_metrics"]
        new = self.report["gold_corpus"]["corrected_metrics"]
        self.assertEqual((base["tp"], base["fp"], base["tn"], base["fn"]), (3, 6, 7, 1))
        self.assertEqual((new["tp"], new["fp"], new["tn"], new["fn"]), (4, 0, 13, 0))
        self.assertGreater(new["recall"], base["recall"])
        self.assertLess(new["false_positive_rate"], base["false_positive_rate"])

    def test_baseline_marks_are_preserved_not_deleted(self):
        rows = self.report["gold_corpus"]["results"]
        for cid in ("N01", "N02", "N04", "N10", "N12", "N13"):
            self.assertTrue(rows[cid]["baseline"]["marcajes"])
            self.assertTrue(rows[cid]["non_profile_observations"])

    def test_reported_attribution_is_not_asserted_as_system_fact(self):
        row = self.report["gold_corpus"]["results"]["P05"]
        self.assertEqual(row["attributed_profile_marks"][0]["class"], "ATRIBUCION_REPORTADA")
        self.assertFalse(row["attributed_profile_marks"][0]["asserted_by_system"])
        self.assertTrue(row["profile_detected"])

    def test_rhetorical_litotes_is_separate_from_profile(self):
        row = self.report["gold_corpus"]["results"]["A03"]
        self.assertTrue(row["evaluative_marks"])
        self.assertFalse(row["profile_detected"])

    def test_referential_ambiguity_is_retained_without_forced_resolution(self):
        rows = self.report["ambiguity_and_logic"]["cases"]
        t03 = next(x for x in rows if x["id"] == "T03")
        t04 = next(x for x in rows if x["id"] == "T04")
        self.assertTrue(any(x["type"] == "REFERENTE_CAUSAL_AMBIGUO" for x in t03["ambiguities_corrected"]))
        self.assertTrue(any(x["type"] == "REFERENTE_SUBORDINADA_ELIPTICA" for x in t04["ambiguities_corrected"]))

    def test_challenge_set_is_reported_separately(self):
        base = self.report["challenge_corpus"]["baseline_metrics"]
        new = self.report["challenge_corpus"]["corrected_metrics"]
        self.assertEqual(len(new["rows"]), 10)
        self.assertLessEqual(new["fp"], base["fp"])
        self.assertGreaterEqual(new["tn"], base["tn"])

    def test_gender_pairs_keep_equal_outputs_and_explain_shared_errors(self):
        pairs = self.report["gender_counterfactuals"]["pairs"]
        self.assertEqual(len(pairs), 3)
        self.assertEqual(self.report["gender_counterfactuals"]["n_different"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
