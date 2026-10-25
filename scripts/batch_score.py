#!/usr/bin/env python3
"""Invoke installed Claude Code CLI once per input record; each prompt requests validated JSON."""
import argparse,json,subprocess,sys,os
from pathlib import Path

def main():
 p=argparse.ArgumentParser();p.add_argument('--input',required=True,help='JSONL with defect_id, symptom, root_cause, solution, changes');p.add_argument('--outdir',required=True);p.add_argument('--model');p.add_argument('--timeout',type=int,default=300);a=p.parse_args()
 out=Path(a.outdir).resolve();out.mkdir(parents=True,exist_ok=True)
 skill=Path(__file__).resolve().parents[1]
 for line_no,line in enumerate(Path(a.input).read_text(encoding='utf-8').splitlines(),1):
  if not line.strip():continue
  try:
   item=json.loads(line);name=str(item['defect_id']);assert name and all(c.isalnum() or c in '-_' for c in name)
   target=out/(name+'.json')
   prompt=(f'Use the rca-scoring skill at {skill / "SKILL.md"}. Evaluate this defect using the rubric and Gerrit evidence. '
     f'Input JSON: {json.dumps(item,ensure_ascii=False)}. '
     f'Write the FULL schema-compliant result JSON to {target}. Run python {skill / "scripts/validate_result.py"} {target}. '
     'If Gerrit access fails, record insufficient_evidence; never invent code evidence. Return only the output path.')
   cmd=['claude','-p',prompt,'--output-format','text','--permission-mode','acceptEdits']
   if a.model:cmd+=['--model',a.model]
   proc=subprocess.run(cmd,cwd=str(skill),capture_output=True,text=True,timeout=a.timeout,env=os.environ.copy())
   if proc.returncode!=0 or not target.exists():raise RuntimeError((proc.stderr or proc.stdout)[-350:])
   chk=subprocess.run([sys.executable,str(skill/'scripts/validate_result.py'),str(target)],capture_output=True,text=True)
   if chk.returncode:raise RuntimeError(chk.stderr[-350:])
   print(f'OK {name}: {target}')
  except Exception as e:print(f'ERROR line {line_no}: {e}',file=sys.stderr)
if __name__=='__main__':main()
