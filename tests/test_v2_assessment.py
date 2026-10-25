import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from assess_v2 import assess, RUBRIC

REV='a'*40


def source(kind='diff'):
    return dict(id='e1',kind=kind,reference='fixture:located',revision=REV,
                test_name=None,assertion=None,command=None,environment=None,outcome=None,observation_window=None)


def fixture():
    return dict(context=dict(case_id='SYNTHETIC',mode='owner_rca',profile='routine',
                             text='Complete synthetic report.',text_complete=True,revision=REV),
                evidence=[source()],claims=[],closure_requested='implemented',
                items={r['id']:dict(basis='unknown',score=None,reason='Unavailable evidence.',
                    evidence_ids=[],claim_ids=[],na_reason='') for r in RUBRIC['items']})


class V2Assessment(unittest.TestCase):
    def test_unknown_does_not_become_zero_or_partial_mean(self):
        d=fixture();d['items']['P1'].update(basis='observed',score=4,evidence_ids=['e1'])
        out=assess(d)
        self.assertIsNone(out['profile']['problem']['ordinal_mean'])
        self.assertEqual(out['profile']['problem']['known'],1)
        self.assertIsNone(out['overall'])

    def test_missing_owner_does_not_block_explicit_artifact_mode(self):
        d=fixture();d['context']['text']=None
        self.assertEqual(assess(d)['decision'],'needs_input')
        d['context']['mode']='artifact_review'
        d['items']['R1'].update(basis='observed',score=3,evidence_ids=['e1'])
        self.assertEqual(assess(d)['decision'],'needs_evidence')

    def test_unknown_is_not_a_numeric_score(self):
        d=fixture();d['items']['P1']['score']=0
        with self.assertRaises(ValueError):assess(d)

    def test_ci_success_cannot_verify_defect_execution(self):
        d=fixture();d['evidence']=[source('ci_status')]
        d['claims']=[dict(id='c1',kind='test_execution',text='Regression passed',status='supported',evidence_ids=['e1'],critical=True)]
        with self.assertRaisesRegex(ValueError,'assertion-linked'):assess(d)

    def test_wrong_revision_log_cannot_verify_current_patch(self):
        d=fixture();e=source('test_execution');e.update(revision='b'*40,test_name='TestDefect',
            assertion='No reconcile error',command='go test -run TestDefect',environment='fixture',outcome='passed')
        d['evidence'].append(dict(e,id='e2'))
        d['claims']=[dict(id='c1',kind='test_execution',text='Regression passed',status='supported',evidence_ids=['e2'],critical=True)]
        with self.assertRaisesRegex(ValueError,'pinned'):assess(d)

    def test_matching_execution_can_advance_maturity(self):
        d=fixture();e=source('test_execution');e.update(test_name='TestDefect',assertion='No reconcile error',
            command='go test -run TestDefect',environment='fixture',outcome='passed')
        d['evidence'].append(dict(e,id='e2'))
        d['claims']=[dict(id='c1',kind='test_execution',text='Regression passed',status='supported',evidence_ids=['e2'],critical=True)]
        d['items']['V2'].update(basis='observed',score=3,evidence_ids=['e2'],claim_ids=['c1'])
        d['closure_requested']='executed'
        self.assertEqual(assess(d)['closure'],'executed')

    def test_executed_failure_does_not_mean_success(self):
        d=fixture();e=source('test_execution');e.update(test_name='TestDefect',assertion='No reconcile error',
            command='go test -run TestDefect',environment='fixture',outcome='failed')
        d['evidence'].append(dict(e,id='e2'))
        d['claims']=[dict(id='c1',kind='test_execution',text='Regression passed',status='refuted',evidence_ids=['e2'],critical=True)]
        d['items']['V2'].update(basis='observed',score=0,evidence_ids=['e2'],claim_ids=['c1'])
        d['closure_requested']='executed'
        self.assertEqual(assess(d)['closure'],'executed')
        self.assertEqual(assess(d)['decision'],'revise')

    def test_critical_refutation_is_not_compensated(self):
        d=fixture()
        for item in d['items'].values():item.update(basis='observed',score=4,evidence_ids=['e1'])
        d['items']['V2'].update(basis='unknown',score=None,evidence_ids=[])
        d['claims']=[dict(id='c1',kind='fix',text='Patch adds a mutex',status='refuted',evidence_ids=['e1'],critical=True)]
        out=assess(d)
        self.assertEqual(out['decision'],'revise');self.assertIsNone(out['overall'])

    def test_na_needs_scope_reason(self):
        d=fixture();d['items']['O1']['basis']='not_applicable'
        with self.assertRaisesRegex(ValueError,'scope justification'):assess(d)

    def test_core_failure_cannot_be_hidden_with_na(self):
        d=fixture();d['items']['R1'].update(basis='not_applicable',na_reason='Not considered important')
        with self.assertRaisesRegex(ValueError,'cannot be excluded'):assess(d)

    def test_truncated_report_cannot_establish_omission(self):
        d=fixture();d['context']['text_complete']=False
        d['items']['O1'].update(basis='not_demonstrated',score=0)
        with self.assertRaisesRegex(ValueError,'report text'):assess(d)

    def test_claim_only_does_not_prove_technical_fact(self):
        d=fixture();d['evidence'].append(dict(source('author_statement'),id='e2'))
        d['claims']=[dict(id='c1',kind='causal',text='Author claims root cause',status='supported',evidence_ids=['e2'],critical=True)]
        with self.assertRaisesRegex(ValueError,'technical evidence'):assess(d)

    def test_implementation_is_not_long_term_effectiveness(self):
        d=fixture();d['closure_requested']='effectiveness_observed'
        with self.assertRaisesRegex(ValueError,'Execution maturity'):assess(d)


if __name__=='__main__':unittest.main()
