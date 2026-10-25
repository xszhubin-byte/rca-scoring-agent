#!/usr/bin/env python3
"""Freeze appraisal subject and evidence availability, never quality scores.

Material availability is not factual support. Claim verdicts and quality scores
remain independent judgments. A well-formed execution record proves that an
execution was recorded, not that the defect was fixed or the record is authentic.
"""
import argparse
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RULES=json.loads((ROOT/'references/v2-rubric.json').read_text(encoding='utf-8'))
ARTIFACT_SOURCES={
    'P1':{'issue','design','test_code'},'P2':{'issue','test_code','runtime_observation'},
    'P3':{'issue','runtime_observation'},'P4':{'design','test_code'},
    'C1':{'diff','test_code','design'},'C2':{'diff','test_code','design'},
    'C3':{'diff','test_code','design'},'C4':{'diff','test_code','design'},
    'O1':{'introduction_history'},'O2':{'verification_history'},'O3':{'process_record'},
    'O4':{'test_code','design'},
    'R1':{'diff'},'R2':{'diff'},'R3':{'diff'},'R4':{'diff'},
    'V1':{'test_code'},'V3':{'test_code'},'V4':{'test_code','test_scope_record'},
    'L1':{'sweep_record'},'L2':{'diff','test_code'},'L3':{'diff','action_record'},
    'L4':{'closure_plan'}}


def execution_sources(context,evidence):
    return [e for e in evidence if e['kind']=='test_execution' and context['revision']
            and e['revision']==context['revision'] and all(e.get(k) for k in ('test_name','assertion','command','environment'))
            and e.get('outcome') in ('passed','failed')]


def build_contract(context,evidence):
    has_text=bool(context.get('text'))
    report=context['mode'] in ('owner_rca','pr_author_proxy')
    missing_owner=report and not has_text
    report_sources=[e['id'] for e in evidence if e['kind']=='author_statement']
    if report and has_text and context.get('text_complete') and not report_sources:
        raise ValueError('A complete report needs a located author_statement evidence record')
    execution=execution_sources(context,evidence)
    items={}
    for rule in RULES['items']:
        key=rule['id']
        if missing_owner:
            basis='unknown';subject='missing_report';sources=[]
        elif key=='V2':
            basis='observed' if execution else 'unknown';subject='execution_record_quality';sources=[e['id'] for e in execution]
        elif report:
            basis='observed' if context.get('text_complete') else 'unknown'
            subject='report_explanation_only';sources=report_sources if basis=='observed' else []
        else:
            allowed=ARTIFACT_SOURCES[key]
            available=[e for e in evidence if e['kind'] in allowed
                       and (e['revision'] in (None,context['revision']))]
            basis='observed' if available else 'unknown';subject='supplied_artifact_only';sources=[e['id'] for e in available]
        items[key]=dict(basis=basis,subject=subject,available_source_ids=sources)
    stage='implemented' if any(e['kind'] in ('diff','test_code','action_record') for e in evidence) else 'planned'
    if execution and stage=='implemented':stage='executed'
    if stage=='executed' and any(e['kind']=='effectiveness_observation' and e.get('observation_window') for e in evidence):
        stage='effectiveness_observed'
    return dict(version='1.0',items=items,closure_from_records=stage,
                source_policy='Declared evidence kinds require provenance review; availability is not factual correctness.')


def main():
    p=argparse.ArgumentParser();p.add_argument('input');p.add_argument('--output',required=True);a=p.parse_args()
    d=json.loads(Path(a.input).read_text(encoding='utf-8'))
    Path(a.output).write_text(json.dumps(build_contract(d['context'],d['evidence']),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':main()
