import importlib.util
from pathlib import Path
import unittest
p=Path(__file__).resolve().parents[1]/'correr_estandar.py'
spec=importlib.util.spec_from_file_location('runner',p)
runner=importlib.util.module_from_spec(spec); spec.loader.exec_module(runner)
class TestRunnerNoMcPath(unittest.TestCase):
 def test_no_mc_after_output(self):
  src,name,out,no_mc=runner._parse_standard_args(['correr_estandar.py','input.json','CASE','result.json','--no-mc'])
  self.assertEqual(out.name,'result.json'); self.assertTrue(no_mc)
 def test_no_mc_before_output(self):
  src,name,out,no_mc=runner._parse_standard_args(['correr_estandar.py','input.json','CASE','--no-mc','result.json'])
  self.assertEqual(out.name,'result.json'); self.assertTrue(no_mc)
 def test_default_output(self):
  src,name,out,no_mc=runner._parse_standard_args(['correr_estandar.py','input.json','CASE'])
  self.assertEqual(out.name,'RESULT_CASE.json'); self.assertFalse(no_mc)
if __name__=='__main__': unittest.main(verbosity=2)
