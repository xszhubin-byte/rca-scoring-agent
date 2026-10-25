import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/calibration'))
from verify_stability import verify


class ExecutionProvenance(unittest.TestCase):
    def setup_record(self,root):
        cohort=root/'cohort';cohort.mkdir();skill=root/'skill';skill.mkdir()
        (skill/'SKILL.md').write_bytes(b'Frozen skill')
        protocol=dict(rounds=3,model='fixed-model',reasoning_effort='medium',runtime_hashes={'SKILL.md':hashlib.sha256(b'Frozen skill').hexdigest()})
        (cohort/'protocol.json').write_text(json.dumps(protocol))
        proof={}
        for n in range(1,4):
            rd=cohort/f'round-{n:02d}';rd.mkdir();response=b'{"cases":[]}'
            (rd/'batch-01.response.json').write_bytes(response)
            meta=dict(response_sha256=hashlib.sha256(response).hexdigest(),exit_code=0,tool_item_types=[],
                      prompt_sha256='same-prompt',requested_model='fixed-model',reasoning_effort='medium',cli_version='fixed-cli')
            (rd/'batch-01.meta.json').write_text(json.dumps(meta))
            proof[f'round-{n:02d}-batch-01']=[hashlib.sha256(str(n).encode()).hexdigest()]
        (cohort/'session-proof.json').write_text(json.dumps(proof))
        return cohort,skill

    def test_saved_response_tampering_is_detected(self):
        with tempfile.TemporaryDirectory() as td:
            cohort,skill=self.setup_record(Path(td))
            self.assertTrue(verify(cohort,skill)['passed'])
            (cohort/'round-02/batch-01.response.json').write_bytes(b'{"cases":["changed"]}')
            self.assertFalse(verify(cohort,skill)['passed'])

    def test_reused_session_or_changed_prompt_does_not_pass(self):
        with tempfile.TemporaryDirectory() as td:
            cohort,skill=self.setup_record(Path(td))
            proof=json.loads((cohort/'session-proof.json').read_text());proof['round-02-batch-01']=proof['round-01-batch-01']
            (cohort/'session-proof.json').write_text(json.dumps(proof))
            self.assertFalse(verify(cohort,skill)['passed'])
            cohort2=Path(td)/'other';cohort2.mkdir();second,skill2=self.setup_record(cohort2)
            p=second/'round-02/batch-01.meta.json';meta=json.loads(p.read_text());meta['prompt_sha256']='different';p.write_text(json.dumps(meta))
            self.assertFalse(verify(second,skill2)['passed'])


if __name__=='__main__':unittest.main()
