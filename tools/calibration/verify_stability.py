#!/usr/bin/env python3
"""Check saved execution identity and byte provenance without rerunning a model."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]


def sha(data):return hashlib.sha256(data).hexdigest()


def verify(cohort,skill,private_events=None):
    cohort=Path(cohort);skill=Path(skill).resolve()
    protocol=json.loads((cohort/'protocol.json').read_text(encoding='utf-8'))
    checks=[];sessions=[];metas=[]
    proof_path=cohort/'session-proof.json'
    if private_events:
        proof={}
        for path in sorted(Path(private_events).glob('round-*-batch-*.events.jsonl')):
            identities=[]
            for line in path.read_text(encoding='utf-8').splitlines():
                try:e=json.loads(line)
                except ValueError:continue
                if e.get('type')=='thread.started' and e.get('thread_id'):identities.append(sha(e['thread_id'].encode()))
            proof[path.name.replace('.events.jsonl','')]=identities
        proof_path.write_bytes((json.dumps(proof,indent=2)+'\n').encode())
    proof=json.loads(proof_path.read_text(encoding='utf-8')) if proof_path.exists() else {}
    for rel,expected in protocol['runtime_hashes'].items():
        path=(skill/rel).resolve()
        checks.append(dict(check='frozen_runtime',key=rel,passed=path.is_relative_to(skill) and path.is_file() and sha(path.read_bytes())==expected))
    round_dirs=[cohort/f'round-{n:02d}' for n in range(1,protocol['rounds']+1)]
    signatures={}
    for n,folder in enumerate(round_dirs,1):
        paths=sorted(folder.glob('batch-*.meta.json'))
        checks.append(dict(check='round_has_batches',key=str(n),passed=bool(paths)))
        for path in paths:
            meta=json.loads(path.read_text(encoding='utf-8'));batch=path.name.split('.')[0];key=f'round-{n:02d}-{batch}'
            metas.append(meta)
            response=folder/(batch+'.response.json')
            checks.append(dict(check='response_hash',key=key,passed=response.exists() and sha(response.read_bytes())==meta['response_sha256']))
            checks.append(dict(check='clean_model_call',key=key,passed=meta['exit_code']==0 and not meta['tool_item_types']))
            signature=(meta['prompt_sha256'],meta['requested_model'],meta['reasoning_effort'],meta['cli_version'])
            signatures.setdefault(batch,[]).append(signature)
            ids=proof.get(key,[]);sessions.extend(ids)
            checks.append(dict(check='one_fresh_session',key=key,passed=len(ids)==1))
            checks.append(dict(check='requested_model_settings',key=key,passed=meta['requested_model']==protocol['model'] and meta['reasoning_effort']==protocol['reasoning_effort']))
    for batch,values in signatures.items():
        checks.append(dict(check='identical_inputs_and_settings',key=batch,passed=len(values)==protocol['rounds'] and len(set(values))==1))
    checks.append(dict(check='sessions_are_distinct',key='all',passed=bool(sessions) and len(sessions)==len(set(sessions))==len(metas)))
    result=dict(passed=all(c['passed'] for c in checks),model_calls=len(metas),distinct_sessions=len(set(sessions)),checks=checks,
        limitation='Consistency of producer records, not a cryptographic service attestation or proof of expert accuracy.')
    (cohort/'execution-verification.json').write_bytes((json.dumps(result,indent=2)+'\n').encode())
    return result


def main():
    p=argparse.ArgumentParser();p.add_argument('cohort');p.add_argument('--private-events');a=p.parse_args()
    result=verify(a.cohort,ROOT/'skills/rca-scoring',a.private_events)
    print(json.dumps(dict(passed=result['passed'],model_calls=result['model_calls'],distinct_sessions=result['distinct_sessions'])))
    if not result['passed']:raise SystemExit('Execution record verification failed')


if __name__=='__main__':main()
