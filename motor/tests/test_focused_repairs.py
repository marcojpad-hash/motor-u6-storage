from __future__ import annotations
import importlib.util
import tempfile
import unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

runner = load('runner_under_test', ROOT / 'correr_estandar.py')
so3 = load('souriau_so3_under_test', ROOT / 'motor' / 'souriau_momentum_so3.py')
forman = load('forman_under_test', ROOT / 'motor' / 'forman_ricci_weighted_graph.py')
stink = load('stink_under_test', ROOT / 'motor' / 'stinkbox_transport_v0_2.py')
ricci_proxy = load('ricci_proxy_under_test', ROOT / 'motor' / 'ricci_forman_coocurrencia_v0_1.py')

class TestT1Comparator(unittest.TestCase):
    def test_reads_predictor_candidates(self):
        r = runner.puntuar_t1({'H1':'hero','H2':'sage'}, [], {'predictor':{'candidates':[{'family':'hero'}]}})
        self.assertEqual(r['hit_H'], 'HIT_H1')
        self.assertEqual(r['tops_t1_con_evidencia_predictiva'], ['hero'])

    def test_recovered_candidates_do_not_create_hit(self):
        r = runner.puntuar_t1({'H1':'hero','H2':'sage'}, [], {'predictor':{'candidates':[{'family':'hero','recovered_from_cut':True}]}})
        self.assertEqual(r['hit_H'], 'INCONCLUSO_CANDIDATOS_RECUPERADOS_NO_PRONOSTICO')
        self.assertEqual(r['tops_t1_con_evidencia_predictiva'], [])

    def test_empty_candidates_are_inconclusive_not_miss(self):
        r = runner.puntuar_t1({'H1':'hero','H2':'sage'}, [], {'cuts':[{}]})
        self.assertEqual(r['hit_H'], 'INCONCLUSO_SIN_CANDIDATOS_T1')

    def test_terminal_candidates_are_read(self):
        r = runner.puntuar_t1({'H1':'hero','H2':'sage'}, [], {'resolucion_operativa_terminal_017':{'candidates':[{'family':'sage'}]}})
        self.assertEqual(r['hit_H'], 'HIT_H2')

class TestMathPrimitives(unittest.TestCase):
    def test_so3_momentum_map_basis(self):
        self.assertEqual(so3.momentum_map_so3((1,0,0),(0,1,0)), (0.0,0.0,1.0))

    def test_so3_rejects_wrong_dimension(self):
        with self.assertRaises(ValueError): so3.momentum_map_so3((1,2),(1,2,3))

    def test_forman_single_edge(self):
        r = forman.forman_ricci({'u':1,'v':1}, [{'u':'u','v':'v','weight':1}])
        self.assertAlmostEqual(r['curvatures'][0]['forman_ricci'], 2.0)


    def test_existing_ricci_sidecar_discloses_proxy_status(self):
        r = ricci_proxy.correr_cuts([{'P':[('a',0.2)]},{'P':[('b',0.8)]}])
        self.assertEqual(r['curvature_method'], 'TEMPORAL_WEIGHT_DRIFT_PROXY_NOT_EXACT_FORMAN')
        self.assertFalse(r['forman_ricci_verified'])

    def test_forman_triangle(self):
        nodes={'a':1,'b':1,'c':1}
        edges=[{'u':'a','v':'b','weight':1},{'u':'b','v':'c','weight':1},{'u':'c','v':'a','weight':1}]
        r=forman.forman_ricci(nodes, edges)
        for e in r['curvatures']: self.assertAlmostEqual(e['forman_ricci'], 0.0)

class TestStinkboxPersistence(unittest.TestCase):
    def test_tokens_survive_reopen(self):
        with tempfile.TemporaryDirectory() as td:
            b=stink.StinkBox('TEST_CASE',td)
            self.assertEqual(b.archive_tokens(cut_id='C1', tokens=['Alpha','Beta','alpha'], source='unit_test'), 2)
            b2=stink.StinkBox('TEST_CASE',td)
            self.assertEqual(b2.data['token_frequency']['alpha'],1)
            self.assertEqual(b2.data['token_frequency']['beta'],1)
            self.assertEqual(len(b2.data['token_events']),2)
            self.assertIn('alpha|beta', b2.data['coactivation'])

if __name__ == '__main__': unittest.main(verbosity=2)

class TestBlindSearchQuality(unittest.TestCase):
    def test_person_is_used_only_by_external_self_match_filter(self):
        sidecar = load('caldero_sidecar_under_test', ROOT / 'motor' / 'sidecar_caldero_busqueda_arquetipos.py')
        main = load('main_identity_under_test', ROOT / 'motor' / 'MOTOR_V15_3_UNICO_20260927.py')
        case = {'person': 'Themistocles', 'cuts': [{'P': [['liderazgo', 0.8]], 'A': [], 'C': []}]}
        identity = sidecar.SelfMatchIdentity.from_mapping(main._case_identity(case))
        filt = sidecar.SelfMatchFilter(identity)
        self_match = sidecar.SearchSource(url='https://example.org/themistocles', title='Themistocles: Leadership', snippet='Naval strategy')
        analogue = sidecar.SearchSource(url='https://example.org/ancient-greece', title='Military commitments in ancient Greece', snippet='Political bargaining and collective military mobilization')
        self.assertEqual(filt.match_reason(self_match), 'name_match')
        self.assertIsNone(filt.match_reason(analogue))
        blind = main._build_pre_h_blind_input(case, {}, {})
        self.assertNotIn('themistocles', ' '.join(blind['tokens'] + blind['patterns'] + blind['families']))

    def test_search_tokenizer_removes_spanish_english_stopwords_and_number_noise(self):
        sidecar = load('caldero_sidecar_tokens_under_test', ROOT / 'motor' / 'sidecar_caldero_busqueda_arquetipos.py')
        tokens = sidecar.extract_tokens('de la estrategia naval, the leadership 2035 224 y coalición')
        self.assertEqual(tokens, ['estrategia', 'naval', 'leadership', 'coalición'])
