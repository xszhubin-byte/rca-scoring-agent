#!/usr/bin/env python3
"""Validate evidence-linked RCA V2 diagnostics; never compute a total rank."""
import argparse
import json
from collections import Counter
from pathlib import Path

import jsonschema
from review_contract import build_contract

ROOT = Path(__file__).resolve().parents[1]
RUBRIC = json.loads((ROOT/'references/v2-rubric.json').read_text(encoding='utf-8'))


def assess(document):
    d = json.loads(json.dumps(document))
    schema = json.loads((ROOT/'references/v2-result.schema.json').read_text(encoding='utf-8'))
    jsonschema.validate(d, schema)
    context = d['context']; evidence = {e['id']: e for e in d['evidence']}
    contract=build_contract(context,d['evidence']) if context.get('review_contract')=='1.0' else None
    claims = {c['id']: c for c in d['claims']}
    if len(evidence) != len(d['evidence']) or len(claims) != len(d['claims']):
        raise ValueError('Duplicate evidence or claim ID')
    runtime_checked = False; effectiveness_checked = False
    for claim in d['claims']:
        if set(claim['evidence_ids']) - set(evidence):
            raise ValueError('Unknown claim evidence ID')
        sources = [evidence[i] for i in claim['evidence_ids']]
        if claim['status'] in ('supported', 'refuted') and not sources:
            raise ValueError('Supported/refuted claim requires located evidence')
        if claim['kind'] in ('causal','fix') and claim['status'] in ('supported','refuted'):
            if not any(e['kind'] in ('diff','test_code','runtime_observation','test_execution')
                       and e['revision'] == context['revision'] and context['revision'] for e in sources):
                raise ValueError('Technical claim requires matching-revision technical evidence')
        if claim['kind'] == 'test_execution' and claim['status'] in ('supported','refuted'):
            execution = [e for e in sources if e['kind']=='test_execution'
                         and e['revision'] == context['revision'] and context['revision']
                         and e['test_name'] and e['assertion'] and e['command'] and e['environment']
                         and e['outcome'] in ('passed','failed')]
            if not execution:
                raise ValueError('Test execution claim lacks pinned assertion-linked execution evidence')
            runtime_checked = True
        if claim['kind']=='effectiveness' and claim['status']=='supported':
            if not any(e['kind']=='effectiveness_observation' and e['observation_window'] for e in sources):
                raise ValueError('Effectiveness claim lacks observation window')
            effectiveness_checked=True
    counts=Counter(); domains={name:[] for name in RUBRIC['dimensions']}
    for rule in RUBRIC['items']:
        key=rule['id']; item=d['items'][key]; basis=item['basis']; score=item['score']
        if contract and basis!=contract['items'][key]['basis']:
            raise ValueError(key+': rating state differs from frozen source-availability contract')
        counts[basis]+=1
        if set(item['evidence_ids'])-set(evidence) or set(item['claim_ids'])-set(claims):
            raise ValueError(key+': unknown evidence/claim reference')
        if basis in ('unknown','not_applicable') and score is not None:
            raise ValueError(key+': unknown/N/A must have null score')
        if basis=='not_applicable' and not item['na_reason'].strip():
            raise ValueError(key+': N/A requires scope justification')
        if key in ('P1','C1','R1') and basis=='not_applicable':
            raise ValueError(key+': core defect criterion cannot be excluded; missing evidence is unknown')
        if basis=='not_demonstrated' and score != 0:
            raise ValueError(key+': observed omission must score 0')
        if basis=='not_demonstrated' and (context['mode']=='artifact_review' or not context['text'] or not context['text_complete']):
            raise ValueError(key+': cannot infer report omission without report text')
        if basis=='observed' and (score is None or not item['evidence_ids']):
            raise ValueError(key+': observed rating needs a score and located evidence')
        if key=='V2' and basis=='observed':
            if not any(claims[c]['kind']=='test_execution' and claims[c]['status'] in ('supported','refuted')
                       for c in item['claim_ids']):
                raise ValueError('V2: execution rating requires an execution claim')
        if context['mode']=='owner_rca' and not context['text'] and basis not in ('unknown','not_applicable'):
            raise ValueError('No original Owner RCA; use unknown or explicitly switch to artifact review')
        domains[rule['dimension']].append(item)
    stage=d['closure_requested']
    if contract and stage!=contract['closure_from_records']:
        raise ValueError('Closure stage differs from recorded execution/implementation facts')
    if stage in ('implemented','executed','effectiveness_observed'):
        if not any(e['kind'] in ('diff','test_code','action_record') for e in evidence.values()):
            raise ValueError('Implementation maturity requires an implementation artifact')
    if stage in ('executed','effectiveness_observed') and not runtime_checked:
        raise ValueError('Execution maturity requires an assertion-linked execution claim')
    if stage=='effectiveness_observed' and not effectiveness_checked:
        raise ValueError('Effectiveness maturity requires follow-up observation')
    critical_refuted=[c['id'] for c in claims.values() if c['critical'] and c['status']=='refuted']
    known_critical_failure=any(d['items'][k]['basis'] in ('observed','not_demonstrated')
                               and d['items'][k]['score']==0 for k in ('C1','R1'))
    if context['mode']=='owner_rca' and not context['text']: decision='needs_input'
    elif critical_refuted or known_critical_failure: decision='revise'
    elif counts['unknown']:decision='needs_evidence'
    else:decision='reviewable'
    profile={}
    for name,items in domains.items():
        applicable=[i for i in items if i['basis']!='not_applicable']
        known=[i['score'] for i in applicable if i['score'] is not None]
        profile[name]={'ordinal_mean':round(sum(known)/len(known),2)
                       if applicable and len(known)==len(applicable) else None,
                       'known':len(known),'applicable':len(applicable)}
    return dict(version='2.0-experimental',case_id=context['case_id'],mode=context['mode'],
                review_contract=contract['version'] if contract else None,
                decision=decision,profile=profile,basis_counts=dict(counts),
                critical_refuted_claims=critical_refuted,closure=stage,
                overall=None,limitations=['Experimental profile, not validated weights or a personnel ranking.',
                                        'Evidence labels and judgments still require semantic review.'])


def main():
    p=argparse.ArgumentParser();p.add_argument('input');p.add_argument('--output');a=p.parse_args()
    value=assess(json.loads(Path(a.input).read_text(encoding='utf-8')))
    text=json.dumps(value,ensure_ascii=False,indent=2)+'\n'
    if a.output:Path(a.output).write_text(text,encoding='utf-8')
    else:print(text)


if __name__=='__main__':main()
