#!/usr/bin/env python3
"""Independent stdlib check of headline post hoc arithmetic against raw trials."""
import itertools, json
from collections import defaultdict
from pathlib import Path
from statistics import mean
ROOT=Path(__file__).resolve().parents[2]
rows=[json.loads(l) for l in (ROOT/'experiments/E1/runs/e1-scored-0921/trials.jsonl').read_text().splitlines()]
items={r['id']:r for r in map(json.loads,(ROOT/'experiments/E1/items/scored.jsonl').read_text().splitlines())}
reported=json.loads((ROOT/'paper/generated/posthoc-e1.json').read_text())
for j in ['14B','32B']:
 for e in ['none','attacker']:
  for v in ['ve_strict','ve_fluent']:
   for weak in [False,True]:
    a={r['item_id']:r for r in rows if j in r['judge'] and r['condition']==v+'|'+e and r['label']=='bad' and (not weak or items[r['item_id']].get('direction')=='weaker')}
    b={r['item_id']:r for r in rows if j in r['judge'] and r['condition']=='fol_symbols|'+e and r['label']=='bad' and (not weak or items[r['item_id']].get('direction')=='weaker')}
    assert a.keys()==b.keys()
    groups=defaultdict(list)
    for k,r in a.items():groups[r['template']].append(int(r['approved'])-int(b[k]['approved']))
    d=list(map(mean,groups.values()));observed=mean(d)
    total=0
    for signs in itertools.product([-1,1],repeat=len(d)):
     total+=abs(mean(x*s for x,s in zip(d,signs)))>=abs(observed)-1e-12
    p=total/2**len(d);key=('weakening/' if weak else '')+f'{j}/{v}/{e}';out=reported[key]
    assert abs(out['mean']-observed)<1e-12 and out['p_two_sided']==p,key
    assert out['interval'][0]<=observed<=out['interval'][1]
    if weak:assert len(a)==243 and len(d)==9
print('Independent raw-trial check: 16 paired estimates/p values and weakening counts agree.')
# Check every Markdown table has the declared number of columns. Condition names
# in historical source tables used unescaped vertical bars; never silently drop cells.
import re
body=(ROOT/'paper/build/paper.md').read_text()
for block in re.findall(r'(?:^\|.*\n)+',body,re.M):
 lines=block.strip().splitlines()
 widths=[len(re.split(r'(?<!\\)\|',x))-2 for x in lines]
 assert len(set(widths))==1,(lines[0],widths)
print('All assembled Markdown tables have consistent column counts.')
