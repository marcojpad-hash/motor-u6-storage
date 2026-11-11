import unittest
import numpy as np
from limite_giro import verify,project,population,rw_population_formula,cos_formula,parabola_formula

class LimitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.v=verify()
    def test_oracle_matches_exact_svd(self):
        self.assertLess(max(x["error_giro"] for x in self.v["svd_fiel"]),1e-7)
    def test_general_upper_bound_approached(self):
        a=[x for x in self.v["ejemplos"] if x["tipo"]=="supremo_binomial"]
        self.assertEqual(len(a),28);self.assertGreater(a[-1]["giro"],5218)
    def test_no_positive_general_lower_bound(self):
        a=[x for x in self.v["ejemplos"] if x["tipo"]=="contraejemplo_inferior_n4"]
        self.assertLess(a[-1]["giro"],.012)
        self.assertLess(max(x["giro"] for x in self.v["ejemplos"] if x["tipo"]=="giro_cero_n_ge_5"),1e-7)
    def test_restricted_formulas(self):
        for x in self.v["ejemplos"]:
            if x["tipo"]=="formulas_cos_parabola":self.assertLess(max(x["error_cos"],x["error_parabola"]),1e-7)
    def test_brownian_population_formula(self):
        for n in (3,6,10,30,64):self.assertAlmostEqual(population(n,"RW")["giro"],rw_population_formula(n),places=7)
    def test_same_covariance_different_smooth_winding(self):
        a,b=self.v["mismo_rho_curvas_suaves_distinto_giro"];self.assertAlmostEqual(a["rho"],b["rho"]);self.assertGreater(b["giro"]-a["giro"],300)
    def test_curvature_identity_and_polar_integral(self):
        a=self.v["integral"];self.assertAlmostEqual(a["integral_grados"],a["formula_grados"],places=5);self.assertAlmostEqual(a["identidad_curvatura_grados"],a["formula_grados"],places=7)
if __name__=="__main__":unittest.main()
