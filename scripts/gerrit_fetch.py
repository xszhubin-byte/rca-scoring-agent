#!/usr/bin/env python3
"""Fetch pinned Gerrit evidence using stdlib; never print secrets."""
import argparse,base64,json,os,sys,urllib.request,urllib.parse,urllib.error
from pathlib import Path

def get(base,change,path,auth):
    url=base.rstrip('/')+'/a/changes/'+urllib.parse.quote(change,safe='')+path
    req=urllib.request.Request(url,headers={'Accept':'application/json'})
    if auth:
        req.add_header('Authorization','Basic '+base64.b64encode(auth.encode()).decode())
    with urllib.request.urlopen(req,timeout=25) as r: data=r.read(8_000_000).decode('utf-8')
    if data.startswith(")]}'"):data=data.split('\n',1)[1]
    return json.loads(data)

def main():
    p=argparse.ArgumentParser();p.add_argument('--change',required=True);p.add_argument('--out',required=True);p.add_argument('--max-files',type=int,default=25);p.add_argument('--max-chars',type=int,default=40000);a=p.parse_args()
    base=os.environ.get('GERRIT_URL');user=os.environ.get('GERRIT_USER');token=os.environ.get('GERRIT_HTTP_PASSWORD')
    if not base:sys.exit('Missing GERRIT_URL')
    if not base.startswith('https://') and os.environ.get('GERRIT_ALLOW_HTTP')!='1':sys.exit('Require HTTPS Gerrit URL')
    auth=f'{user}:{token}' if user and token else None
    cid=a.change
    detail=get(base,cid,'/detail',auth)
    rev=detail.get('current_revision')
    if not rev:sys.exit('Change has no current revision')
    qrev=urllib.parse.quote(rev,safe='')
    commit=get(base,cid,f'/revisions/{qrev}/commit',auth)
    files=get(base,cid,f'/revisions/{qrev}/files',auth)
    paths=[x for x in files if x!='/COMMIT_MSG']
    # First fetch changed-file metadata. Diff hunks are bounded, and the agent may request targeted files later.
    output={'change_id':detail.get('change_id',cid),'change_number':detail.get('_number'),'project':detail.get('project'),'status':detail.get('status'),'revision':rev,'subject':detail.get('subject'),'url':detail.get('web_links',[{}])[0].get('url') or base.rstrip('/')+'/c/'+str(detail.get('_number','')),'commit_message':commit.get('message'),'files':paths,'diffs':{},'coverage':{'total_files':len(paths),'fetched_files':0,'truncated':False}}
    for f in paths[:a.max_files]:
        try:
            diff=get(base,cid,f'/revisions/{qrev}/files/{urllib.parse.quote(f,safe="")}/diff',auth)
            chunks=[]
            for block in diff.get('content',[]):
                if 'ab' in block:chunks.append({'context':block['ab'][:8]})
                if 'a' in block:chunks.append({'removed':block['a'][:100]})
                if 'b' in block:chunks.append({'added':block['b'][:100]})
            txt=json.dumps(chunks,ensure_ascii=False)
            if len(txt)>a.max_chars:output['coverage']['truncated']=True;chunks=[{'truncated_excerpt':txt[:a.max_chars]}]
            output['diffs'][f]={'change_type':diff.get('change_type'),'content':chunks}
        except (urllib.error.HTTPError,urllib.error.URLError,ValueError) as e:
            output['diffs'][f]={'error':type(e).__name__,'message':'Diff unavailable'}
    output['coverage']['fetched_files']=len(output['diffs'])
    if len(paths)>a.max_files:output['coverage']['truncated']=True
    dest=Path(a.out);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'Wrote {dest} revision={rev} files={len(paths)} fetched={len(output["diffs"])}')
if __name__=='__main__':
    try:main()
    except urllib.error.HTTPError as e:sys.exit(f'Gerrit HTTP {e.code}; check credentials, change ID and access')
    except urllib.error.URLError:sys.exit('Gerrit connection failed')
