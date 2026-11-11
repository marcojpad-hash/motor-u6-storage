#!/usr/bin/env python3
import sys
sys.dont_write_bytecode = True
import unittest
from pathlib import Path
import tempfile
import json,gzip,importlib.util,warnings
import numpy as np
from medir_trayectorias import fit_radius, fit_phase, fit_sine, shape, shape_ordered, frame, event, load_case
from proyeccion_tusi_modelo_externo import project_crudo,project_result,compare_csv

class TrayectoriaTests(unittest.TestCase):
    def test_exponencial_propia(self):
        t=np.arange(6,dtype=float);r=.4*np.exp(-.2*t)
        q=fit_radius(t,r)
        self.assertAlmostEqual(q["R0"],.4,places=10)
        self.assertAlmostEqual(q["b"],.2,places=10)
        self.assertAlmostEqual(q["R2"],1,places=10)
        self.assertEqual(q["regime_status"],"NO_EVALUABLE_SIN_POSTRAMO")
    def test_tramo_dos_puntos_no_se_fuerza(self):
        q=fit_radius(np.arange(5.),np.array([.1,.2,.5,.6,.2]))
        self.assertEqual(q["n_fit"],2);self.assertIsNone(q["R0"])
    def test_fase_lineal(self):
        t=np.arange(8.);q=fit_phase(t,np.deg2rad(3+8*t))
        self.assertAlmostEqual(q["omega"],8,places=10)
        self.assertIsNone(q["rupture"])
    def test_fechas_duplicadas_no_inventan_velocidad(self):
        q=fit_phase(np.array([0.,1,2,2]),np.array([0.,.1,.2,2]))
        self.assertEqual(q["saltos_sin_duracion"],[3])
        self.assertNotIn(3,q["rupture_flags"])
    def test_seno_dentro_de_muestra(self):
        t=np.arange(10.);q=fit_sine(t,.01+.08*np.sin(2*np.pi*t/8+.3))
        self.assertGreater(q["pct"],99.9)
    def test_forma_operacional(self):
        q=shape([0,.1,.2,.3,2,2.1,2.2],[.2,.1,-.1,-.05,.03,.1,.2])
        self.assertTrue(q["coincide"]);self.assertEqual(q["valle"],2)
    def test_z90_control(self):
        self.assertEqual(event(0,["C1"],np.array([2000.]),2000.)["frente_z90"],"EN_Z90")
    def test_no_muta_vectores(self):
        P=np.random.default_rng(5).normal(size=(10,244));before=P.copy()
        frame(P);np.testing.assert_array_equal(P,before)
    def test_transformacion_reconstruida_n_variable(self):
        rng=np.random.default_rng(10)
        for n in (6,10):
            raw={"f"+str(k):rng.normal(size=n).tolist() for k in range(8)}
            q=project_crudo(raw)
            self.assertEqual(len(q["radio"]),n)
            self.assertAlmostEqual(q["y_transversal"][-1]-q["y_transversal"][0],0,places=10)
            np.testing.assert_allclose(np.hypot(q["x_tusi"],q["y_transversal"]),q["radio"],atol=1e-12)
            self.assertAlmostEqual(np.mean(q["x_tusi"]),0,places=10)
    def test_forma_pc12_ordenada(self):
        q=shape_ordered([0,.1,.2,.3,2,2.1,2.2],[.2,.1,-.1,-.05,.03,.1,.2])
        self.assertTrue(q["coincide"])
    def test_prefijo_no_creciente_fijado(self):
        q=fit_radius(np.arange(5.),np.array([.5,.3,.2,.25,.1]),"initial_nonincreasing_prefix")
        self.assertEqual(q["end"],2)
        self.assertEqual(q["n_fit"],3)
    def test_regla_radio_maximo_final_conservada(self):
        q=fit_radius(np.arange(5.),np.array([.5,.3,.1,.4,.6]))
        self.assertEqual(q["estado"],"SIN_CORTES_POSTERIORES_AL_MAXIMO")
    def test_equivalencia_script_fiel_real(self):
        root=Path(__file__).resolve().parent
        source=root/"coordenadas_modelo_externo/proyeccion_tusi_modelo_externo.py"
        sp=importlib.util.spec_from_file_location("original_externo_fiel",source);mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod)
        fixture=root/"tusi_pc12_v1/gate_mozart"
        d=json.loads(gzip.decompress((fixture/"result.json.gz").read_bytes()));inp=json.loads((fixture/"entrada.json").read_text());q=project_result(d,inp)
        with tempfile.TemporaryDirectory() as tmp:
            rp=Path(tmp)/"r.json";rp.write_text(json.dumps(d))
            with warnings.catch_warnings():
                warnings.simplefilter("ignore",ResourceWarning)
                actual=mod.load(rp,fixture/"entrada.json")
        for expected,key in zip(actual,["x_tusi","y_transversal","radio","fase_grados","year"]):
            np.testing.assert_allclose(expected,q[key],atol=1e-12)
        check=compare_csv(q,root/"coordenadas_modelo_externo/tabla_coordenadas_mozart.csv")
        self.assertTrue(check["passed"])
    def test_csv_externo_reutilizable(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"ejemplo.csv"
            p.write_text("corte,año,x_tusi,y_transversal,radio,fase_grados\nC1,2000,1,0,1,0\nC2,2001,0,1,1,90\nC3,2002,-1,0,1,180\n")
            data,*_=load_case({"file":p.name,"case_id":"EJEMPLO_SINTETICO","z90":2001.5},Path(d))
            self.assertEqual(data["consistencia_radio_max_error"],0)
            self.assertEqual(data["geometry"],"COORDENADAS_EXTERNAS_PC12_RESULT_FUENTE_NO_DISPONIBLE")

if __name__=="__main__":unittest.main()
