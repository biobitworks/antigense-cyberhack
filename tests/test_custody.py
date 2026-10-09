import copy,importlib.util,json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import custody,cascade
class Tests(unittest.TestCase):
 def test_regression_matrix(self):
  self.assertTrue(cascade.auth('before',False,False))
  for a in [False,True]:
   for h in [False,True]:self.assertEqual(cascade.auth('after',a,h),a and h)
 def test_freeze_append_and_tamper(self):
  with tempfile.TemporaryDirectory() as d:
   b=Path(d);g=custody.freeze(b,cascade.ROOT);r=custody.append_step(b,{'name':'fault','state':'OBSERVED','checks':{'detected':True}})
   self.assertTrue(custody.verify(b,g['project_root'])['PASS']);self.assertFalse(custody.verify(b,'0'*64)['PASS'])
   s=b/'step-000002.json';o=json.loads(s.read_text());o['classification']['checks']['provided.detected']=False;s.write_text(json.dumps(o));self.assertFalse(custody.verify(b)['PASS'])
 def test_mmr_all_sizes(self):
  rows=[{'event_hash':custody.digest(str(i).encode()),'fco_id':'fco:'+str(i)} for i in range(40)]
  for i in range(41):self.assertEqual(custody.mmr(rows[:i])['root'],custody.independent_mmr_root(rows[:i]))
if __name__=='__main__':unittest.main()
