import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/calibration'))
from run_stability import summarize, RUBRIC, response_schema, fixtures, evaluate, build_contract
import jsonschema


class StabilityMetrics(unittest.TestCase):
    def cohort(self,mutate=None):
        packet=dict(document=dict(context=dict(case_id='OPAQUE')),synthetic=True)
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)
            for n in range(1,4):
                folder=out/f'round-{n:02d}';folder.mkdir()
                raw=dict(case_id='OPAQUE',claims=[dict(id='q',status='supported')],
                         items={i['id']:dict(basis='observed',score=3) for i in RUBRIC['items']})
                reviewed=dict(case_id='OPAQUE',accepted=True,result=dict(decision='needs_evidence',closure='implemented'))
                if mutate:mutate(n,raw,reviewed)
                (folder/'batch-01.response.json').write_text(json.dumps(dict(cases=[raw])),encoding='utf-8')
                (folder/'batch-01.reviewed.json').write_text(json.dumps([reviewed]),encoding='utf-8')
            return summarize(out,3,[packet])

    def test_equal_results_pass_without_response_reuse(self):
        result=self.cohort()
        self.assertTrue(result['all_passed'])
        self.assertEqual(result['case_ratings'],3)

    def test_null_drift_fails_even_if_known_scores_equal(self):
        def mutate(n,raw,reviewed):
            if n==2:raw['items']['O1'].update(basis='unknown',score=None)
        result=self.cohort(mutate)
        self.assertFalse(result['all_passed'])
        self.assertIn('O1',result['case_reports'][0]['basis_changed_items'])

    def test_large_single_item_span_cannot_hide_in_average(self):
        def mutate(n,raw,reviewed):raw['items']['C1']['score']={1:2,2:3,3:4}[n]
        result=self.cohort(mutate)
        self.assertFalse(result['all_passed'])
        self.assertEqual(result['case_reports'][0]['max_numeric_span'],2)

    def test_claim_or_maturity_drift_fails(self):
        def mutate(n,raw,reviewed):
            if n==2:
                raw['claims'][0]['status']='unresolved'
                reviewed['result']['closure']='planned'
        result=self.cohort(mutate)
        self.assertFalse(result['all_passed'])
        self.assertFalse(result['case_reports'][0]['claim_status_consistent'])
        self.assertFalse(result['case_reports'][0]['closures_consistent'])

    def test_rejected_raw_result_is_not_a_stable_pass(self):
        def mutate(n,raw,reviewed):
            if n==2:reviewed['accepted']=False
        self.assertFalse(self.cohort(mutate)['all_passed'])

    def test_output_contract_blocks_artifact_report_omission(self):
        packets,_=fixtures();packet=packets[3]
        schema=response_schema([packet])
        item=dict(basis='observed',score=2,reason='Located code observation',evidence_ids=['patch'],claim_ids=[],na_reason='')
        case=dict(case_id=packet['document']['context']['case_id'],claims=[],
                  items={r['id']:copy.deepcopy(item) for r in RUBRIC['items']},closure_requested='implemented')
        for key,contract_item in packet['contract']['items'].items():
            case['items'][key].update(basis=contract_item['basis'],score=2 if contract_item['basis']=='observed' else None)
        jsonschema.validate(dict(cases=[case]),schema)
        case['items']['R3'].update(basis='not_demonstrated',score=0)
        with self.assertRaises(jsonschema.ValidationError):jsonschema.validate(dict(cases=[case]),schema)

    def test_output_contract_keeps_unknown_null(self):
        packets,_=fixtures();schema=response_schema([packets[0]])
        item=dict(basis='observed',score=2,reason='Located material',evidence_ids=['report'],claim_ids=[],na_reason='')
        case=dict(case_id='K01',claims=[],items={r['id']:copy.deepcopy(item) for r in RUBRIC['items']},closure_requested='implemented')
        case['items']['V2'].update(basis='unknown',score=None)
        jsonschema.validate(dict(cases=[case]),schema)
        case['items']['V2']['score']=0
        with self.assertRaises(jsonschema.ValidationError):jsonschema.validate(dict(cases=[case]),schema)

    def test_positive_execution_oracle_allows_content_dependent_decision(self):
        packets,expectations=fixtures();packet=packets[6]
        rating=dict(basis='observed',score=2,reason='Located fixture evidence',evidence_ids=['patch'],claim_ids=['q_fix'],na_reason='')
        response=dict(case_id='K07',claims=[dict(q,status='supported',evidence_ids=['execution' if q['kind']=='test_execution' else 'patch']) for q in packet['document']['questions']],
            items={r['id']:copy.deepcopy(rating) for r in RUBRIC['items']},closure_requested='executed')
        response['items']['V2'].update(evidence_ids=['execution'],claim_ids=['q_execution'])
        known=evaluate(dict(cases=[response]),[packet],expectations)[0]
        self.assertTrue(known['accepted'],known['issues'])
        self.assertEqual(known['result']['decision'],'reviewable')
        packet=copy.deepcopy(packet);packet['document']['context']['text_complete']=False
        packet['contract']=build_contract(packet['document']['context'],packet['document']['evidence'])
        for key in response['items']:
            if key!='V2':response['items'][key].update(basis='unknown',score=None,evidence_ids=[],claim_ids=[])
        partial=evaluate(dict(cases=[response]),[packet],expectations)[0]
        self.assertTrue(partial['accepted'],partial['issues'])
        self.assertEqual(partial['result']['decision'],'needs_evidence')


if __name__=='__main__':unittest.main()
