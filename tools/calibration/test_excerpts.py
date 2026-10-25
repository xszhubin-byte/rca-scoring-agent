"""Recover changed Go test functions at the pinned head, not just added lines."""
import re


def changed_test_names(patch):
    active=None;names=set()
    for line in patch.splitlines():
        if line.startswith('@@'):
            match=re.search(r'\bfunc (Test\w+)\(',line)
            active=match.group(1) if match else None
            continue
        if not line or line[0] not in (' ','+','-'):continue
        code=line[1:]
        found=re.match(r'func (Test\w+)\(',code)
        if found:active=found.group(1)
        if active and line[0] in ('+','-') and code.strip() and not code.lstrip().startswith('//'):
            names.add(active)
        if code=='}':active=None
    return sorted(names)


def extract_current_functions(content,names):
    starts=list(re.finditer(r'^func\s+(\w+)\s*\(',content,flags=re.M));result=[]
    for index,match in enumerate(starts):
        name=match.group(1)
        if name not in names:continue
        end=starts[index+1].start() if index+1<len(starts) else len(content)
        code=content[match.start():end].rstrip()
        result.append(dict(name=name,start_line=content[:match.start()].count('\n')+1,
                           end_line=content[:match.start()].count('\n')+code.count('\n')+1,code=code))
    missing=set(names)-{r['name'] for r in result}
    if missing:raise ValueError('Changed test absent from fetched head: '+','.join(sorted(missing)))
    return result
