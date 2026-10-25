#!/usr/bin/env python3
"""Validate actual CLI responses, compute conservative scores and repeatability.

Original model responses are never rewritten. Evidence-based suppressions are
recorded explicitly alongside schema-normalized results.
"""
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

import jsonschema
from calibrate_snapshots import ROOT, V, empty_result, validate


def normalized_space(s):
    return re.sub(r'\s+', ' ', s).strip()


def process(item, snapshot):
    violations, suppressions = [], []
    if item['owner_score_eligible']:
        violations.append('Owner score wrongly eligible without Owner RCA.')
    body = normalized_space(snapshot['snapshot'].get('body') or '')
    if item['proxy_score_eligible']:
        for field in ('proxy_root_cause_quote', 'proxy_solution_quote'):
            quote = normalized_space(item[field])
            if not quote or quote not in body:
                violations.append(field + ' is not a verbatim body excerpt.')
    files = {f['filename'] for f in snapshot['files']}
    for name, dim in item['dimensions'].items():
        if set(dim['subscores']) != set(V.W[name][1]):
            violations.append(name + ': invalid subscore keys')
        for key, score in dim['subscores'].items():
            if score is not None and (isinstance(score, bool) or not 0 <= score <= 100):
                violations.append(name + '.' + key + ': score out of range')
            if score is not None and not item['proxy_score_eligible']:
                violations.append('Ineligible proxy received numerical subscore.')
        for ref in dim['file_references']:
            if ref not in files:
                violations.append('Unknown changed-file reference: ' + ref)
    if item['dimensions']['prevention']['subscores']['regression_evidence'] is not None:
        violations.append('Regression execution scored without raw logs.')
    result = empty_result(item['case_id'])
    if not item['proxy_score_eligible'] or violations:
        return dict(case_id=item['case_id'], input_origin='pr_author_proxy' if item['proxy_score_eligible'] else 'missing',
                    model_proxy_eligible=item['proxy_score_eligible'], review_violations=violations,
                    suppressions=suppressions, accepted_for_exploratory_scoring=False,
                    result=validate(result))
    result['owner_input'] = dict(symptom=None, root_cause=item['proxy_root_cause_quote'],
                                solution=item['proxy_solution_quote'])
    result['overall']['comment'] = 'Exploratory PR-author proxy, not an Owner RCA score or human-calibrated accuracy.'
    result['evidence'] = [dict(id='d1', type='diff', reference=snapshot['compare_url'],
                               summary='Observed fixed-SHA patches; no claim of local upstream execution.')]
    for name, model_dim in item['dimensions'].items():
        raw = dict(model_dim['subscores'])
        # Commit messages were retrieved via compare but not included in the model
        # packet. The packet contains PR title/body, never a commit message corpus.
        if name == 'authenticity' and raw['commit_consistency'] is not None:
            suppressions.append('authenticity: commit consistency unavailable in model packet; suppress dimension.')
            raw['commit_consistency'] = None
        has_missing = any(x is None for x in raw.values())
        if name == 'authenticity' and has_missing:
            raw = dict.fromkeys(raw, None)
        obj = result['dimensions'][name]
        obj.update(subscores=raw, status='insufficient_evidence' if has_missing else 'partially_supported',
                   evidence_ids=['d1'] if model_dim['file_references'] else [],
                   comment=('PR-author proxy. ' + model_dim['reason'])[:200])
    result = validate(result)
    return dict(case_id=item['case_id'], input_origin='pr_author_proxy',
                model_proxy_eligible=True, review_violations=[], suppressions=suppressions,
                accepted_for_exploratory_scoring=True, result=result)


def main():
    directory = ROOT/'data/calibration/codex_v1_4'
    snapshots = json.loads((ROOT/'data/calibration/evidence_v1_4/snapshots.json').read_text(encoding='utf-8'))
    by_id = {x['case_id']: x for x in snapshots}
    schema = json.loads((directory/'response.schema.json').read_text(encoding='utf-8'))
    items, metas = [], []
    for p in sorted(directory.glob('batch-*.json')):
        if '.meta.' in p.name: continue
        d=json.loads(p.read_text(encoding='utf-8'));jsonschema.validate(d,schema)
        items.extend(d['cases'])
        meta=json.loads(p.with_suffix('.meta.json').read_text(encoding='utf-8'))
        assert meta['exit_code'] == 0
        metas.append(meta)
    assert len(items)==50 and len({x['case_id'] for x in items})==50, 'Need all 50 CLI results'
    reviewed=[process(x,by_id[x['case_id']]) for x in items]
    repeats=[]
    baseline={x['case_id']: x for x in items}
    for p in sorted(directory.glob('repeat-*.json')):
        if '.meta.' in p.name:continue
        d=json.loads(p.read_text(encoding='utf-8'));jsonschema.validate(d,schema)
        meta=json.loads(p.with_suffix('.meta.json').read_text(encoding='utf-8'))
        assert meta['exit_code']==0;metas.append(meta)
        for x in d['cases']:
            first=baseline[x['case_id']]; diffs=[];missing_disagreements=0
            for name in V.W:
                for key in V.W[name][1]:
                    a=first['dimensions'][name]['subscores'][key];b=x['dimensions'][name]['subscores'][key]
                    if a is None or b is None:
                        missing_disagreements += (a is None)!=(b is None)
                    else:diffs.append(abs(a-b))
            repeats.append(dict(run=p.stem,case_id=x['case_id'],
                                eligibility_agreement=first['proxy_score_eligible']==x['proxy_score_eligible'],
                                comparable_subscores=len(diffs),nullness_disagreements=missing_disagreements,
                                mean_absolute_self_delta=round(sum(diffs)/len(diffs),3) if diffs else None,
                                max_absolute_self_delta=max(diffs) if diffs else None,
                                review=process(x,by_id[x['case_id']])))
    usage=Counter()
    for meta in metas:
        for u in meta['usage']:usage.update(u)
    summary=dict(cli='Codex CLI',cli_version=metas[0]['cli_version'],
                 resolved_model=None,model_limitation='CLI default; actual model identifier absent from captured events.',
                 primary_cases=50,primary_batches=10,independent_cli_invocations=len(metas),
                 proxy_eligible_by_model=sum(x['proxy_score_eligible'] for x in items),
                 accepted_proxy_cases=sum(x['accepted_for_exploratory_scoring'] for x in reviewed),
                 with_review_violations=sum(bool(x['review_violations']) for x in reviewed),
                 with_evidence_suppressions=sum(bool(x['suppressions']) for x in reviewed),
                 finite_overall_proxy_scores=sum(x['result']['overall']['score'] is not None for x in reviewed),
                 repeated_case_ratings=len(repeats),
                 repeat_eligibility_agreements=sum(x['eligibility_agreement'] for x in repeats),
                 token_usage=dict(usage),upstream_go_tests_executed=0,human_gold_labels=0,
                 accuracy_mae=None,human_agreement_kappa=None)
    for name,value in [('reviewed_results.json',reviewed),('repeatability.json',repeats),('summary.json',summary)]:
        (directory/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    eligibility=json.loads((ROOT/'data/calibration/executed_v1_4/eligibility.json').read_text(encoding='utf-8'))
    audit={x['case_id']:x for x in eligibility}
    with (directory/'case_summary.csv').open('w',newline='',encoding='utf-8') as stream:
        fields=['case_id','head_sha','diff_complete','changed_test_files','model_proxy_eligible','accepted_proxy',
                *V.W,'overall','review_violations','suppressions']
        writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader()
        for x in reviewed:
            a=audit[x['case_id']];r=x['result']
            writer.writerow(dict(case_id=x['case_id'],head_sha=a['head_sha'],diff_complete=a['diff_complete'],
                                 changed_test_files=len(a['changed_test_files']),model_proxy_eligible=x['model_proxy_eligible'],
                                 accepted_proxy=x['accepted_for_exploratory_scoring'],
                                 **{n:r['dimensions'][n]['score'] for n in V.W},overall=r['overall']['score'],
                                 review_violations=' | '.join(x['review_violations']),suppressions=' | '.join(x['suppressions'])))
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
