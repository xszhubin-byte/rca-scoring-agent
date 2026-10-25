import json,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class ValidatorTests(unittest.TestCase):
 def test_example(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'out.json';p.write_text((ROOT/'examples/rca_result.example.json').read_text(encoding='utf-8'),encoding='utf-8')
   r=subprocess.run([sys.executable,str(ROOT/'scripts/validate_result.py'),str(p)],capture_output=True,text=True)
   self.assertEqual(r.returncode,0,r.stderr)
   data=json.loads(p.read_text(encoding='utf-8'));self.assertIsNone(data['overall']['score'])
if __name__=='__main__':unittest.main()
