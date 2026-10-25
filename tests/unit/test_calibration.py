import unittest, json, tempfile, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]/'legacy/v1.4'
BASE=json.loads((ROOT/'examples/rca_result.example.json').read_text(encoding='utf-8'))
class Calibration(unittest.TestCase):
 def run_case(self,d):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'x.json';p.write_text(json.dumps(d,ensure_ascii=False),encoding='utf-8');r=subprocess.run([sys.executable,str(ROOT/'scripts/validate_result.py'),str(p)],capture_output=True,text=True)
   return r,json.loads(p.read_text(encoding='utf-8'))
 def test_missing_evidence_no_overall(self):
  r,d=self.run_case(BASE);self.assertEqual(r.returncode,0,r.stderr);self.assertIsNone(d['overall']['score'])
 def test_commit_only_cap(self):
  d=json.loads(json.dumps(BASE));d['evidence']=[dict(id='c1',type='commit',reference='fixture:commit',summary='Author statement')];a=d['dimensions']['authenticity'];a.update(status='partially_supported',evidence_ids=['c1']);a['subscores']={k:95 for k in a['subscores']}
  r,o=self.run_case(d);self.assertEqual(r.returncode,0,r.stderr);self.assertEqual(o['dimensions']['authenticity']['score'],69)
 def test_contradiction_cap(self):
  d=json.loads(json.dumps(BASE));d['evidence']=[dict(id='d1',type='diff',reference='fixture:diff',summary='Contradiction')];a=d['dimensions']['authenticity'];a.update(status='contradicted',evidence_ids=['d1']);a['subscores']={k:95 for k in a['subscores']}
  r,o=self.run_case(d);self.assertEqual(r.returncode,0,r.stderr);self.assertEqual(o['dimensions']['authenticity']['score'],39);self.assertTrue(o['manual_review_required'])
 def test_claimed_test_not_verified(self):
  d=json.loads(json.dumps(BASE));d['evidence']=[dict(id='c1',type='commit',reference='fixture:claim',summary='Author says tests passed')];p=d['dimensions']['prevention'];p.update(status='partially_supported',evidence_ids=['c1']);p['subscores']={k:95 for k in p['subscores']}
  r,o=self.run_case(d);self.assertEqual(r.returncode,0,r.stderr);self.assertEqual(o['dimensions']['prevention']['score'],69)
 def test_false_verified_rejected(self):
  d=json.loads(json.dumps(BASE));d['evidence']=[dict(id='c1',type='commit',reference='fixture:claim',summary='Only commit')];p=d['dimensions']['prevention'];p.update(status='verified',evidence_ids=['c1']);p['subscores']={k:95 for k in p['subscores']}
  r,_=self.run_case(d);self.assertNotEqual(r.returncode,0)
 def test_missing_authenticity_mixed_scores_rejected(self):
  d=json.loads(json.dumps(BASE));d['dimensions']['authenticity']['subscores']['diff_support']=0
  r,_=self.run_case(d);self.assertNotEqual(r.returncode,0)
if __name__=='__main__':unittest.main()
