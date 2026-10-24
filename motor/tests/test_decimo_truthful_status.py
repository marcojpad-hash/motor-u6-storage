from __future__ import annotations
import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("decimo_truthful_test", ROOT / "motor" / "decimo_hombre_esteroides_mayeutica_v1.py")
decimo = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = decimo
spec.loader.exec_module(decimo)

class TestDecimoTruthfulStatus(unittest.TestCase):
    def test_missing_candidate_dimensions_do_not_claim_adversarial_completion(self):
        result = {"predictor": {"candidates": [
            {"family": "hero", "rank_fusion": 0.9},
            {"family": "sage", "rank_fusion": 0.6},
        ]}}
        out = decimo.run({"case_id": "TEST_NO_DIMENSIONS", "cuts": []}, result)
        self.assertEqual(out["baseline_method"], "ORIGINAL_PREDICTOR_ORDER_NOT_RECOMPUTED")
        self.assertEqual(out["hipotesis_base"], "hero")
        self.assertEqual(out["status"], "EJECUTADO_CON_DIAGNOSTICO_INCOMPLETO")
        self.assertEqual(out["diagnosticos"]["dimension_counterfactuals_executed"], 0)
        self.assertEqual(out["diagnosticos"]["source_counterfactuals_executed"], 0)
        self.assertFalse(out["diagnosticos"]["token_core_counterfactual_executed"])
        self.assertEqual(out["orthogonal_residual_analysis"]["status"], "NOT_IMPLEMENTED")
        states = {x["ataque"]: x["estado"] for x in out["ataques"]}
        self.assertEqual(states["AQUILES_DIMENSIONAL"], "NO_EJECUTADO_SIN_DIMENSIONES_FINITAS")
        self.assertEqual(states["FUENTES_LATERALES"], "NO_EJECUTADO_SIN_FUENTES_DECLARADAS")
        self.assertEqual(states["AQUILES_SIN_EL_PALO"], "NO_EJECUTADO_SIN_CONTRAFACTUAL_VALIDO")
        attack = next(x for x in out["ataques"] if x["ataque"] == "AQUILES_SIN_EL_PALO")
        self.assertEqual(attack["estado_terminal"], "DIAGNOSTICO_REGISTRADO_SIN_PRUEBA_DE_RESOLUCION")
        reopen = next(x for x in out["ataques"] if x["ataque"] == "REAPERTURA_MAYEUTICA_DIALECTICA")
        self.assertEqual(reopen["estado"], "NO_REABIERTO_SIN_RIVAL_DERROTADOR")


    def test_attempted_core_ablation_without_candidates_is_not_called_resolved(self):
        result = {"predictor": {"candidates": [
            {"family": "hero", "rank_fusion": 0.9},
            {"family": "sage", "rank_fusion": 0.6},
        ]}}
        def runner(kind, target):
            if kind == "token_core":
                return {"predictor": {"candidates": [], "status": "INDETERMINADO"}, "removed_token": target}
            return {"predictor": {"candidates": []}}
        case = {"case_id": "TEST_CORE_ABLATION", "cuts": [{"id": "C1", "P": [["pillar", 0.8]], "A": [], "C": []}]}
        out = decimo.run(case, result, runner)
        self.assertTrue(out["diagnosticos"]["token_core_counterfactual_executed"])
        self.assertFalse(out["diagnosticos"]["token_core_counterfactual_ranked"])
        attack = next(x for x in out["ataques"] if x["ataque"] == "AQUILES_SIN_EL_PALO")
        self.assertEqual(attack["estado"], "NO_RESUELTO_SIN_RANKING_CONTRAFACTUAL")
        self.assertEqual(attack["n_candidatas_de_reejecucion"], 0)

if __name__ == "__main__":
    unittest.main(verbosity=2)
