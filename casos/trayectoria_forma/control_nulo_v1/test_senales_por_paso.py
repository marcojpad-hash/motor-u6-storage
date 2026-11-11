import unittest
import numpy as np
from senales_por_paso import local_metrics,summarize,adjust_holm

class StepTests(unittest.TestCase):
    def test_linear_phase_has_zero_residual_and_correct_weight(self):
        t=np.arange(6.);phase=.5+.3*t;r=np.array([1.,.5,.01,.03,.4,1.2]);q=(r*np.cos(phase),r*np.sin(phase),r,np.rad2deg(phase))
        m=local_metrics(q,t);np.testing.assert_allclose(m["arco_residual_abs"],0,atol=1e-14);self.assertAlmostEqual(m["fase_R2"],1.);np.testing.assert_allclose(m["arco_bruto"],.3*(r[1:]+r[:-1])/2)
    def test_reflection_preserves_phase_arc_and_distance_not_depth(self):
        t=np.arange(7.);phase=np.array([.1,.3,.7,1.8,2.8,3.0,3.1]);r=np.array([1,.7,.4,.1,.2,.5,.8]);x=r*np.cos(phase);y=r*np.sin(phase)
        a=local_metrics((x,y,r,np.rad2deg(phase)),t);b=local_metrics((x,-y,r,np.rad2deg(-phase)),t)
        for k in ("arco_residual_abs","distancia_euclidea","arco_bruto"):np.testing.assert_allclose(a[k],b[k],atol=1e-12)
        self.assertAlmostEqual(a["fase_R2"],b["fase_R2"]);self.assertAlmostEqual(a["profundidad_valle"],b["profundidad_reflejada"])
    def test_residual_equals_delta_minus_own_omega_dt(self):
        t=np.array([0.,1.,1.,3.,4.,9.]);r=np.array([1,.3,.01,.6,.8,1]);p=np.array([.1,.2,.9,1.,1.1,1.2]);m=local_metrics((r*np.cos(p),r*np.sin(p),r,np.rad2deg(p)),t)
        np.testing.assert_allclose(m["arco_residual_firmado"],m["radio_medio"]*np.deg2rad(m["delta_fase_grados"]-m["omega_grados"]*np.diff(t)),atol=1e-12)
    def test_holm_family(self):
        q=[{"p_superior":.01},{"p_superior":.02},{"p_superior":.9}];adjust_holm(q);self.assertEqual(q[0]["holm_m"],3);self.assertAlmostEqual(q[0]["p_holm"],.03);self.assertAlmostEqual(q[1]["p_holm"],.04)
if __name__=="__main__":unittest.main()
