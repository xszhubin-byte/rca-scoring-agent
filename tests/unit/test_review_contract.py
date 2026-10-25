import copy
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/calibration'))
from run_stability import fixtures
from review_contract import build_contract
from assess_v2 import assess


class ReviewContract(unittest.TestCase):
    def test_report_subject_stays_report_despite_good_patch(self):
        packets,_=fixtures();d=packets[0]['document'];contract=build_contract(d['context'],d['evidence'])
        self.assertEqual(contract['items']['L2']['subject'],'report_explanation_only')
        self.assertEqual(contract['items']['L2']['available_source_ids'],['report'])
        self.assertNotIn('score',contract['items']['L2'])
        self.assertEqual(contract['items']['V2']['basis'],'unknown')

    def test_current_patch_does_not_reveal_history_or_followup(self):
        packets,_=fixtures();contract=packets[3]['contract']
        for key in ['O1','O2','O3','L1','L4']:
            self.assertEqual(contract['items'][key]['basis'],'unknown',key)
        self.assertEqual(contract['items']['R1']['basis'],'observed')

    def test_failed_execution_is_still_recorded_execution(self):
        packets,_=fixtures()
        self.assertEqual(packets[7]['contract']['closure_from_records'],'executed')
        self.assertEqual(packets[7]['contract']['items']['V2']['basis'],'observed')
        self.assertEqual(packets[5]['contract']['closure_from_records'],'implemented')
        self.assertEqual(packets[5]['contract']['items']['V2']['basis'],'unknown')

    def test_text_rewording_does_not_assign_quality_scores(self):
        packets,_=fixtures();first=packets[0]['contract'];second=packets[1]['contract']
        self.assertEqual(first,second)
        self.assertTrue(all('score' not in item for item in first['items'].values()))

    def test_report_requires_located_source_record(self):
        packets,_=fixtures();d=copy.deepcopy(packets[0]['document'])
        d['evidence']=[e for e in d['evidence'] if e['kind']!='author_statement']
        with self.assertRaisesRegex(ValueError,'located author_statement'):build_contract(d['context'],d['evidence'])

    def test_runtime_rejects_wrong_material_state(self):
        packets,_=fixtures();packet=packets[3];fixed=packet['document']
        document={k:copy.deepcopy(v) for k,v in fixed.items() if k!='questions'}
        document.update(claims=[],closure_requested=packet['contract']['closure_from_records'],
            items={key:dict(basis=v['basis'],score=2 if v['basis']=='observed' else None,
                reason='Fixture only',evidence_ids=['patch'] if v['basis']=='observed' else [],claim_ids=[],na_reason='')
                for key,v in packet['contract']['items'].items()})
        self.assertEqual(assess(document)['review_contract'],'1.0')
        document['items']['L4'].update(basis='observed',score=2,evidence_ids=['patch'])
        with self.assertRaisesRegex(ValueError,'frozen source-availability'):assess(document)


if __name__=='__main__':unittest.main()
