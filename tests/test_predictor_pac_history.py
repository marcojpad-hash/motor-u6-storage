import importlib.util
import pathlib
import unittest

MODULE = (pathlib.Path(__file__).resolve().parents[1] / "motor" / "motor" / "MOTOR_V15_3_UNICO_20260927.py")
SPEC = importlib.util.spec_from_file_location("motor_v153_pac_test", MODULE)
motor = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(motor)


class CandidateHistoryPACTests(unittest.TestCase):
    def test_candidate_from_a_or_c_is_not_dropped(self):
        cuts = [{"P_candidatos_0a3": [{"familia": "p_family"}], "A_candidatos_0a3": [{"familia": "a_only"}, {"familia": "shared"}], "C_candidatos_0a3": [{"familia": "c_only"}, {"familia": "shared"}]}]
        histories = motor._candidate_histories_from_cuts(cuts)
        self.assertEqual({row["familia"] for row in histories[0]}, {"p_family", "a_only", "c_only", "shared"})

    def test_axis_provenance_is_deduplicated_and_preserved(self):
        cut = {"P_candidatos_0a3": [{"familia": "shared"}, {"familia": "shared"}], "A_candidatos_0a3": [{"familia": "shared"}], "C_candidatos_0a3": [{"familia": "shared"}]}
        self.assertEqual(motor._candidate_history_for_cut(cut), [{"familia": "shared", "ejes": ["P", "A", "C"]}])

    def test_invalid_or_empty_entries_are_ignored(self):
        cut = {"P_candidatos_0a3": [None, {}, {"familia": ""}, {"familia": "ok"}], "A_candidatos_0a3": "not-a-list", "C_candidatos_0a3": [{"otra_clave": "x"}]}
        self.assertEqual(motor._candidate_history_for_cut(cut), [{"familia": "ok", "ejes": ["P"]}])

    def test_multiple_cuts_keep_independent_histories(self):
        cuts = [{"A_candidatos_0a3": [{"familia": "only_a"}]}, {"C_candidatos_0a3": [{"familia": "only_c"}]}]
        self.assertEqual(motor._candidate_histories_from_cuts(cuts), [[{"familia": "only_a", "ejes": ["A"]}], [{"familia": "only_c", "ejes": ["C"]}]])


if __name__ == "__main__":
    unittest.main()
