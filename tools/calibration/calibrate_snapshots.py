#!/usr/bin/env python3
"""Offline evidence eligibility audit plus controlled validator regression.

Real-case outputs abstain when owner RCA is absent. Probe scores are synthetic
and must never be interpreted as scores of the referenced public PR.
"""
import contextlib
import copy
import importlib.util
import io
import json
import re
import tempfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('validator', ROOT / 'legacy/v1.4/scripts/validate_result.py')
V = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(V)


def validate(document):
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / 'result.json'
        path.write_text(json.dumps(document, ensure_ascii=False), encoding='utf-8')
        with contextlib.redirect_stdout(io.StringIO()):
            V.main(path)
        return json.loads(path.read_text(encoding='utf-8'))


def empty_result(case_id):
    return {
        'schema_version': '1.0', 'defect_id': case_id,
        'owner_input': {'symptom': None, 'root_cause': '', 'solution': ''},
        'gerrit': [], 'evidence': [],
        'dimensions': {name: {
            'score': None, 'level': None, 'status': 'insufficient_evidence',
            'comment': 'Missing owner-authored RCA; public PR text is not owner input.',
            'evidence_ids': [], 'subscores': dict.fromkeys(subs, None)
        } for name, (_, subs) in V.W.items()},
        'overall': {'score': None, 'level': None, 'comment': 'Evidence audit only; no quality score.'},
        'manual_review_required': True
    }


def probe_input(case_id, evidence_type='diff'):
    d = empty_result(case_id + '-SYNTHETIC')
    d['owner_input'] = dict(symptom='Synthetic fixture', root_cause='Synthetic cause', solution='Synthetic fix')
    d['evidence'] = [dict(id='p1', type=evidence_type, reference='fixture:synthetic', summary='Constructed evidence, not a PR claim')]
    for name, obj in d['dimensions'].items():
        obj.update(status='partially_supported', evidence_ids=['p1'])
        obj['subscores'] = dict.fromkeys(obj['subscores'], 95)
    return d


def regress(case_id):
    rows = []
    def check(name, document, expected=None, rejects=False):
        try:
            out = validate(document)
            actual = {'overall': out['overall']['score'],
                      **{n: x['score'] for n, x in out['dimensions'].items()},
                      'review': out['manual_review_required']}
            passed = not rejects and all(actual[k] == value for k, value in expected.items())
            rows.append(dict(name=name, passed=passed, expected=expected, actual=actual))
        except (ValueError, KeyError) as exc:
            rows.append(dict(name=name, passed=rejects, expected='reject' if rejects else expected, error=type(exc).__name__))
    check('all_missing_abstains', empty_result(case_id), {'overall': None})
    check('commit_only_caps', probe_input(case_id, 'commit'), {'authenticity': 69, 'relevance': 79, 'prevention': 69, 'overall': 80.6})
    check('diff_without_test_cap', probe_input(case_id), {'authenticity': 95, 'relevance': 95, 'prevention': 69, 'overall': 91.1})
    check('test_type_allows_numeric_ceiling', probe_input(case_id, 'test'), {'overall': 95})
    d = probe_input(case_id); d['dimensions']['authenticity']['status'] = 'contradicted'
    check('contradiction_cap', d, {'authenticity': 39, 'review': True, 'overall': 77.1})
    d = probe_input(case_id, 'commit'); d['dimensions']['prevention']['status'] = 'verified'
    check('claim_cannot_be_verified', d, rejects=True)
    d = probe_input(case_id); d['dimensions']['authenticity']['status'] = 'insufficient_evidence'
    check('missing_authenticity_rejects_numeric', d, rejects=True)
    d = probe_input(case_id); d['dimensions']['depth']['evidence_ids'] = ['unknown']
    check('unknown_evidence_id_rejected', d, rejects=True)
    d = probe_input(case_id); d['evidence'].append(copy.deepcopy(d['evidence'][0]))
    check('duplicate_evidence_id_rejected', d, rejects=True)
    return rows


def main():
    evidence = json.loads((ROOT / 'data/calibration/evidence_v1_4/snapshots.json').read_text(encoding='utf-8'))
    originals = json.loads((ROOT / 'data/calibration/50_real_github_cases.json').read_text(encoding='utf-8'))
    original_by_id = {c['case_id']: c for c in originals}
    audits, results, probes = [], [], []
    for c in evidence:
        cid = c['case_id']; src = original_by_id[cid]; snap = c.get('snapshot', {})
        files = c.get('files', [])
        changed_tests = [f['filename'] for f in files if f['filename'].endswith('_test.go') or f['filename'].startswith('e2e/')]
        checks = c.get('checks', [])
        tests = [x for x in checks if any(w in x['name'].lower() for w in ('test', 'e2e', 'integration', 'verify'))]
        missing = []
        if not src.get('owner_root_cause') or not src.get('owner_solution'): missing.append('owner_authored_root_cause_and_solution')
        if not snap.get('head_sha'): missing.append('pinned_head_sha')
        if not c.get('diff_complete'): missing.append('complete_text_diff')
        # A green name alone does not prove the defect-specific assertion ran.
        missing.extend(['defect_specific_test_log_and_assertion_mapping', 'two_independent_human_gold_labels'])
        clean_body = re.sub(r'<!--.*?-->', '', snap.get('body') or '', flags=re.S).strip()
        content_body = re.sub(r'(?im)^\s*(?:fixes|closes|issue\s*:?)\s+.*$', '', clean_body).strip()
        audits.append(dict(case_id=cid, head_sha=snap.get('head_sha'),
                           pr_body_present=bool((snap.get('body') or '').strip()),
                           pr_body_beyond_template_and_issue_link=bool(content_body),
                           input_origin='owner_input_missing', production_score_eligible=False,
                           files=len(files), expected_files=snap.get('changed_files'),
                           diff_complete=c.get('diff_complete', False), changed_test_files=changed_tests,
                           check_runs=len(checks), test_named_checks=len(tests),
                           successful_test_named_checks=sum(x.get('conclusion') == 'success' for x in tests),
                           workflow_jobs=len(c.get('jobs', [])), missing_evidence=missing,
                           retrieval_errors=c.get('errors', [])))
        d = empty_result(cid)
        if files:
            d['evidence'].append(dict(id='diff_snapshot', type='diff',
                reference=c['compare_url'], summary='Fixed-SHA diff retrieved; no owner claim was inferred.'))
        results.append(validate(d))
        probes.append(dict(case_id=cid, synthetic=True, cases=regress(cid)))
    totals = Counter()
    for a in audits:
        for key in ('diff_complete', 'pr_body_present', 'pr_body_beyond_template_and_issue_link'):
            totals[key] += bool(a[key])
        totals['with_changed_test_files'] += bool(a['changed_test_files'])
        totals['with_check_runs'] += bool(a['check_runs'])
        totals['with_successful_test_named_checks'] += bool(a['successful_test_named_checks'])
        totals['with_workflow_jobs'] += bool(a['workflow_jobs'])
        totals['with_retrieval_errors'] += bool(a['retrieval_errors'])
    rows = [r for p in probes for r in p['cases']]
    summary = dict(real_cases=len(audits), **totals,
                   raw_log_attempts=sum(bool(c.get('log_attempt')) for c in evidence),
                   raw_logs_available=sum(bool(c.get('log_attempt', {}).get('available')) for c in evidence),
                   abstained_owner_scores=len(results), controlled_probe_count=len(rows),
                   controlled_probe_passed=sum(r['passed'] for r in rows),
                   unique_controlled_scenarios=9, upstream_tests_executed=0,
                   human_gold_labels=0, model_accuracy_mae=None, model_agreement_kappa=None)
    out = ROOT / 'data/calibration/executed_v1_4'; out.mkdir(exist_ok=True)
    for name, value in [('eligibility.json', audits), ('owner_scores.json', results),
                        ('controlled_regression.json', probes), ('summary.json', summary)]:
        (out / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2))
    if summary['controlled_probe_passed'] != len(rows):
        raise SystemExit('Controlled regression failures; inspect output.')


if __name__ == '__main__':
    main()

