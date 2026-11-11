import unittest
import numpy as np
from control_nulo import SineCache,generate,summary,holm,matrix_projection
from medir_trayectorias import shape_ordered
from medir_trayectorias import fit_sine

class NullTests(unittest.TestCase):
    def test_cache_matches_reference_irregular_and_duplicate_times(self):
        t=np.array([0.,1,2.2,4,7,7,8]);y=np.array([.2,.1,-.3,.2,.4,.1,.5]);q=SineCache(t)
        self.assertAlmostEqual(q.percent(y)[0],fit_sine(t,y)["pct"],places=8)
        self.assertTrue(np.isnan(q.percent(np.ones(7))[0]))
    def test_permutation_preserves_rows_and_covariance(self):
        X=np.random.default_rng(1).normal(size=(6,8));arr,orders=generate("permutacion",X,np.random.default_rng(2),10)
        for x,order in zip(arr,orders):
            np.testing.assert_array_equal(x,X[order]);np.testing.assert_allclose(np.cov(x,rowvar=False),np.cov(X,rowvar=False),atol=1e-12)
    def test_constant_family_stays_constant(self):
        X=np.column_stack([np.ones(7)*.5,np.arange(7),np.arange(7)**2])
        for kind in ("caminata_gaussiana","iid_gaussiano"):
            out,_=generate(kind,X,np.random.default_rng(3),20);np.testing.assert_array_equal(out[:,:,0],np.ones((20,7))*.5)
    def test_walk_expected_sample_variance_formula(self):
        for n in (6,7,10):
            C=np.minimum.outer(np.arange(1,n+1),np.arange(1,n+1))
            expected=(np.trace(C)-C.sum()/n)/(n-1)
            self.assertAlmostEqual(expected,(n+1)/6)
    def test_midrank_and_missing_fit(self):
        q=summary(2,[1,2,2,4,np.nan]);self.assertEqual(q["percentil"],50);self.assertEqual(q["n_validos"],4);self.assertAlmostEqual(q["p_superior"],.8)
        self.assertIsNone(summary(None,[1,2])["percentil"])
    def test_2d_row_permutations_preserve_invariants_of_full_subspace(self):
        rng=np.random.default_rng(77);X=rng.normal(size=(7,12));fams=["f"+str(i) for i in range(12)]
        q=matrix_projection(X,fams);XY=np.column_stack(q[:2])
        for _ in range(10):
            order=rng.permutation(7);full=matrix_projection(X[order],fams);plane=matrix_projection(XY[order],["x","y"])
            np.testing.assert_allclose(full[2],plane[2],atol=1e-12)
            self.assertAlmostEqual(abs(full[3][-1]-full[3][0]),abs(plane[3][-1]-plane[3][0]),places=8)
            variants=[shape_ordered(plane[0],sign*plane[1])["coincide"] for sign in (1,-1)]
            actual=shape_ordered(full[0],full[1])["coincide"]
            self.assertLessEqual(min(variants),actual);self.assertLessEqual(actual,max(variants))
    def test_holm(self):
        rows=[{"caso":str(i),"nulos":{"test":{"metricas":{"m":{"p_superior":p}}}}} for i,p in enumerate([.001,.02,.9])]
        holm(rows,"m");self.assertEqual([q["nulos"]["test"]["metricas"]["m"]["p_superior_holm"] for q in rows],[.003,.04,.9])

if __name__=="__main__":unittest.main()
