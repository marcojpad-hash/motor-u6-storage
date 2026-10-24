import importlib.util
from pathlib import Path
import unittest

MOD_PATH = Path(__file__).resolve().parents[1] / 'motor' / 'marcador_limite_geometrico_v0_1.py'
spec = importlib.util.spec_from_file_location('marker', MOD_PATH)
marker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(marker)

class TestMarcadorLimiteGeometrico(unittest.TestCase):
    def _run(self, moves, mode='ESTIMADO_DESDE_PREFIJO', endpoint=None):
        xs = [[0.0, 0.0]]
        x = 0.0
        for d in moves:
            x += d
            xs.append([x, 0.0])
        cuts = [{'id': f'C{i+1}'} for i in range(len(xs))]
        dx = [abs(m) for m in moves]
        pc, kap = [], []
        for a,b in zip(moves, moves[1:]):
            den=abs(a*b)
            cos=(a*b/den) if den else 0.0
            pc.append(cos); kap.append((max(0.0,1-cos*cos))**0.5)
        spec={'modo':mode}
        if endpoint: spec['terminal_cut_id']=endpoint
        return marker.evaluar_marcador(xs,cuts,dx,pc,kap,spec)

    def test_contraction_candidate(self):
        out=self._run([4.0,2.0,1.0])
        self.assertEqual(out['status'],'EXECUTED_DIAGNOSTIC')
        self.assertEqual(out['current_marker']['regime'],'CONVERGENCIA_CANDIDATA')
        self.assertFalse(out['feeds_H'])
        self.assertEqual(out['rank_effect'],'NONE')

    def test_acceleration_candidate(self):
        out=self._run([1.0,2.0,4.0])
        self.assertEqual(out['current_marker']['regime'],'MOVIMIENTO_ACELERADO')

    def test_inertia_observed(self):
        out=self._run([0.0,0.0,0.0])
        self.assertEqual(out['current_marker']['regime'],'INMOVILIDAD_OBSERVADA')

    def test_retrospective_terminal_requires_endpoint(self):
        with self.assertRaises(ValueError):
            self._run([1.0,2.0], mode='RETROSPECTIVO_CON_LIMITE')

    def test_retrospective_distance_only_when_endpoint_is_observed(self):
        out=self._run([1.0,2.0], mode='RETROSPECTIVO_CON_LIMITE', endpoint='C3')
        self.assertTrue(out['per_cut'][-1]['is_terminal'])
        self.assertEqual(out['per_cut'][-1]['distance_to_terminal_normalized'],0.0)
        self.assertTrue(out['per_cut'][0]['terminal_distance_available'])

    def test_forecast_does_not_expose_endpoint(self):
        out=self._run([1.0,2.0], mode='ESTIMADO_DESDE_PREFIJO', endpoint='C3')
        self.assertEqual(out['terminal_cut_id'],'NO_EXPOSED_IN_FORECAST')
        self.assertFalse(out['per_cut'][-1]['terminal_distance_available'])

    def test_souriau_function_cycle_is_attached_without_rank_effect(self):
        base=self._run([2.0,1.0,0.5])
        souriau={
          'status':'EXECUTED',
          'por_corte':[
            {'corte':'C1','funciones':{'leon':['A'],'luna':['B']}},
            {'corte':'C2','funciones':{'leon':['A'],'luna':['B']}},
            {'corte':'C3','funciones':{'leon':['A'],'luna':['B']}},
            {'corte':'C4','funciones':{'leon':['A'],'luna':['B']}},
          ],
          'inercia':[{'quieto':True,'leon_pasa_a_marte':[],'cambios_de_funcion':[]} for _ in range(3)]
        }
        out=marker.integrar_funciones_souriau(base,souriau)
        self.assertTrue(out['per_cut'][-1]['firma_funcional_recurrente'])
        self.assertEqual(out['rank_effect'],'NONE')
        self.assertFalse(out['feeds_H'])

if __name__ == '__main__':
    unittest.main(verbosity=2)


def test_native_marker_ablation_switch_is_explicit_and_rank_neutral():
    native = (Path(__file__).resolve().parents[1] / 'motor' / 'MOTOR_V15_3_NATIVO_V0_9_UNICO.py').read_text(encoding='utf-8')
    assert 'if _ml_config.get("enabled") is False:' in native
    assert '"status":"DISABLED_FOR_ABLATION"' in native
    assert '"rank_effect":"NONE"' in native
