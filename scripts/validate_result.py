import json,sys
from pathlib import Path
from decimal import Decimal,ROUND_HALF_UP
import jsonschema
W={'normative':(15,dict(completeness=30,clarity=25,structure=20,terminology=15,concision=10)),'authenticity':(25,dict(commit_consistency=20,diff_support=35,scenario_consistency=20,traceability=15,cross_source_consistency=10)),'relevance':(25,dict(root_fix_match=35,causal_closure=25,coverage=20,targeting=10,solution_soundness=10)),'depth':(20,dict(symptom_vs_cause=20,trigger_conditions=20,causal_chain=30,systemic_mechanism=20,contributing_factors=10)),'prevention':(15,dict(regression_evidence=30,edge_tests=20,similar_issue_sweep=20,preventive_action=20,followup=10))}
def rnd(x):return float(Decimal(str(x)).quantize(Decimal('.1'),rounding=ROUND_HALF_UP))
def lvl(x):return None if x is None else next((k for t,k in [(90,'A'),(80,'B'),(70,'C'),(60,'D')] if x>=t),'E')
def main(path):
 p=Path(path); d=json.loads(p.read_text(encoding='utf-8')); ids=[e['id'] for e in d['evidence']]
 if len(ids)!=len(set(ids)):raise ValueError('duplicate evidence ids')
 for name,(weight,subs) in W.items():
  obj=d['dimensions'][name]; raw=obj['subscores']
  if set(raw)!=set(subs):raise ValueError(f'{name}: wrong subscore keys')
  if set(obj['evidence_ids'])-set(ids):raise ValueError(f'{name}: unknown evidence IDs')
  score=None if any(v is None for v in raw.values()) else rnd(sum(raw[k]*w/100 for k,w in subs.items()))
  types={e['type'] for e in d['evidence'] if e['id'] in obj['evidence_ids']}
  independent=bool(types.intersection({'diff','log','test','other'}))
  if obj['status']=='insufficient_evidence' and name=='authenticity':
   if any(v is not None for v in raw.values()):raise ValueError('authenticity insufficient_evidence requires null subscores')
  if name=='authenticity':
   if obj['status'] in ('insufficient_evidence','not_applicable'):score=None
   if score is not None and not independent:score=min(score,69)
   if obj['status']=='contradicted':
    if score is not None:score=min(score,39)
    d['manual_review_required']=True
  if name=='relevance' and score is not None and not independent:score=min(score,79)
  if name=='prevention' and score is not None and not bool(types.intersection({'test','log'})):
   score=min(score,69)
  if name in ('authenticity','relevance','prevention') and obj['status']=='verified' and not independent:
   raise ValueError(f'{name}: verified requires independent evidence')
  if score is None and obj['status'] in ('verified','partially_supported'):
   raise ValueError(f'{name}: scored status without score')
  obj['score']=score;obj['level']=lvl(score)
  if obj['status']=='contradicted':d['manual_review_required']=True
 vals=[d['dimensions'][n]['score'] for n in W]
 total=None if any(x is None for x in vals) else rnd(sum(d['dimensions'][n]['score']*w/100 for n,(w,_) in W.items()))
 d['overall']['score']=total;d['overall']['level']=lvl(total)
 schema=json.loads((Path(__file__).resolve().parents[1]/'references/output.schema.json').read_text(encoding='utf-8'))
 jsonschema.validate(d,schema)
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(f'VALID score={total} level={lvl(total)}')
if __name__=='__main__':main(sys.argv[1])
