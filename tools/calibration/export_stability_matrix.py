#!/usr/bin/env python3
"""Expose every raw item score and span; never average away an outlier."""
import argparse
import csv
import itertools
import json
from pathlib import Path


def export(cohort):
    cohort=Path(cohort)
    protocol=json.loads((cohort/'protocol.json').read_text(encoding='utf-8'))
    prompt=json.loads((cohort/'prompt_template.json').read_text(encoding='utf-8'))['instruction']
    rubric=json.loads(prompt.split('\nRUBRIC:\n',1)[1].rsplit('\nINPUTS:\n',1)[0])
    packets=json.loads((cohort/'fixtures.json').read_text(encoding='utf-8'))
    runs=[]
    for n in range(1,protocol['rounds']+1):
        cases={}
        for p in sorted((cohort/f'round-{n:02d}').glob('batch-*.response.json')):
            for case in json.loads(p.read_text(encoding='utf-8'))['cases']:
                if case['case_id'] in cases:raise ValueError('Duplicate case ID')
                cases[case['case_id']]=case
        if set(cases)!={p['document']['context']['case_id'] for p in packets}:raise ValueError('Incomplete round')
        runs.append(cases)
    rows=[]
    for packet in packets:
        cid=packet['document']['context']['case_id']
        for item in rubric['items']:
            ratings=[run[cid]['items'][item['id']] for run in runs]
            values=[r['score'] for r in ratings];known=[v for v in values if v is not None]
            pairs=[abs(a-b) for a,b in itertools.combinations(known,2)]
            basis_same=len({r['basis'] for r in ratings})==1
            null_same=len({v is None for v in values})==1
            row=dict(case_id=cid,is_synthetic=packet['synthetic'],source_pr=packet['source_pr'],
                     mode=packet['document']['context']['mode'],item=item['id'],dimension=item['dimension'],
                     basis_program_constrained=bool(packet.get('contract')),basis_consistent=basis_same,
                     numeric_observations=len(known),score_repeatability_measured=len(known)==protocol['rounds'],
                     max_span=max(known)-min(known) if known else None,
                     mean_pairwise_absolute_delta=round(sum(pairs)/len(pairs),6) if pairs else None,
                     item_span_gate_passed=basis_same and null_same and (not known or max(known)-min(known)<=1))
            for n,r in enumerate(ratings,1):row[f'round_{n}_basis']=r['basis'];row[f'round_{n}_score']=r['score']
            rows.append(row)
    with (cohort/'score-matrix.csv').open('w',encoding='utf-8',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    (cohort/'item-stability.json').write_bytes((json.dumps(rows,ensure_ascii=False,indent=2)+'\n').encode())
    return dict(item_rows=len(rows),numeric_rows=sum(r['score_repeatability_measured'] for r in rows),
                span_failures=sum(not r['item_span_gate_passed'] for r in rows))


def main():
    p=argparse.ArgumentParser();p.add_argument('cohort');a=p.parse_args()
    print(json.dumps(export(a.cohort)))


if __name__=='__main__':main()
