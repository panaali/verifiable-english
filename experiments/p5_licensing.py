"""Offline public-prose licensing adjudication, adapted from round-5 p5v5/solve2.

Enumerate record branches and premise permutations with a GLOBAL relaxation
budget. Conditional alternatives never become facts. No hidden graph or label
is used by the search. Unlike the original first-witness DFS, retain all paths
and use immutable derived sets so backtracking cannot remove an earlier fact.
"""
import itertools
import json
import re
from experiments.p5_materials import HERE, read, write_json
from ve_experiments.paid import digest, PreflightError

PRED=re.compile(r'(unit\d+) is ([a-z][a-z-]*)(?: \(([^)]*)\))?')
def preds(s): return [(m.group(1),m.group(2),m.group(3) or '') for m in PRED.finditer(s)]
def parse_records(p):
    br=[];samp=None
    for r in p['records']:
        bi=0
        for s in [x for x in re.split(r'(?<=\.)\s+',r['text'].strip()) if x.strip()]:
            m=re.match(r'^If (.*), then (.*)\.$',s.strip())
            if m:
                br.append((r['id'],bi,tuple(sorted(preds(m.group(1)))),preds(m.group(2))[0]));bi+=1
            else:
                mm=(re.match(r'^The sample from lot (unit\d+) is (unit\d+)\.$',s.strip()) or
                    re.match(r'^Lot (unit\d+) supplied sample (unit\d+)\.$',s.strip()))
                if mm: samp=(mm.group(2),mm.group(1))
                else:
                    m3=re.match(r'^(unit\d+) is an? sample of lot (unit\d+)\.$',s.strip())
                    assert m3,repr(s); samp=(m3.group(1),m3.group(2))
    return br,samp
def parse_premises(p):
    facts=set();un=set();dec=set()
    for n in p['premises']:
        for s in [x.strip() for x in re.split(r'(?<=\.)\s+',n['text'].strip()) if x.strip()]:
            if s.startswith('Rules'): dec|=set(re.findall(r'r\d+',s))
            elif s.startswith('The checks that'): un|=set(preds(s))
            else: facts|=set(preds(s))
    return facts,un,dec
FRAMES=[re.compile(r'^\[(n\d+)\] Because (.+?), (unit\d+ is [a-z][a-z-]*)\.$'),
        re.compile(r'^\[(n\d+)\] Since (.+?), it follows that (unit\d+ is [a-z][a-z-]*)\.$'),
        re.compile(r'^\[(n\d+)\] Given that (.+?), we infer that (unit\d+ is [a-z][a-z-]*)\.$'),
        re.compile(r'^\[(n\d+)\] It follows that (unit\d+ is [a-z][a-z-]*) because (.+?) holds?\.$')]
def parse_arg(p):
    nodes=[]
    for blk in [b.strip() for b in p['argument'].split('\n\n') if b.strip()]:
        head=blk.split('. The checks that')[0]
        alt = blk[len(head):] if len(blk)>len(head) else ''
        hit=None
        for fi,F in enumerate(FRAMES):
            m=F.match(head if head.endswith('.') else head+'.')
            if m: hit=(fi,m);break
        assert hit,repr(blk[:200])
        fi,m=hit
        if fi==3: nid,ctxt,ptxt=m.group(1),m.group(2),m.group(3)
        else: nid,ptxt,ctxt=m.group(1),m.group(2),m.group(3)
        items=[]
        for part in re.split(r'\s+and\s+',ptxt.strip()):
            part=part.strip()
            b=re.match(r'^the immediately preceding ([a-z][a-z-]*) result$',part)
            if b: items.append(('BACK',b.group(1)))
            else:
                q=preds(part); assert len(q)==1,repr(part); items.append(('LIT',q[0]))
        c=preds(ctxt); assert len(c)==1
        nodes.append(dict(id=nid,items=items,concl=c[0],frame=fi,alt=alt,raw=blk))
    return nodes


AUTHORIZED_IDS = frozenset({
    'ib9279ca87379a78c8da58ec68a9d4b42',
    'i17fe028fca21d694ebe499666730b759', 'i2e2c86f4cdc3bc257bbd62ae18da8f55',
    'i55908f495028f09871bca06b09ab1c3c', 'i65def4f39ff74a9f99bff1cce8d7d954',
    'i9af8492c5aae07aa22ae6deeb7185eb6',
})
REPORT = 'checks/gemini-rendered-adjudication.json'


def search(packet, budget):
    branches, _ = parse_records(packet)
    facts, _, declared = parse_premises(packet)
    nodes = parse_arg(packet)
    paths = []

    def visit(i, derived, path, spent):
        if i == len(nodes):
            paths.append(path)
            return
        node = nodes[i]
        for rid, branch, antecedents, conclusion in branches:
            if (rid not in declared or conclusion[:2] != node['concl'][:2]
                    or len(antecedents) != len(node['items'])):
                continue
            for ants in sorted(set(itertools.permutations(antecedents))):
                inputs = []; cost = 0
                for (kind, value), required in zip(node['items'], ants):
                    if kind == 'BACK':
                        previous = next((s for s in reversed(path)
                                         if s['conclusion'][1] == value), None)
                        available = [tuple(previous['conclusion'])] if previous else []
                        producer = previous['step_id'] if previous else None
                    else:
                        available = sorted(f for f in facts | derived if f[:2] == value[:2])
                        producer = None
                    exact = required in available
                    near = [f for f in available if f[1] == required[1]
                            and (f[0] == required[0]) != (f[2] == required[2])]
                    if not exact and not near:
                        break
                    got = required if exact else near[0]
                    mismatch = None if exact else ('sense' if got[0] == required[0] else 'unit')
                    cost += int(not exact)
                    inputs.append({'required':list(required), 'available':list(got),
                                   'producer':producer, 'mismatch':mismatch})
                else:
                    if spent + cost <= budget:
                        step = {'step_id':node['id'], 'record':rid, 'branch':branch,
                                'conclusion':list(conclusion), 'inputs':inputs,
                                'relaxations':cost}
                        visit(i+1, derived | {conclusion}, path+[step], spent+cost)
    visit(0, frozenset(), [], 0)
    # Premise permutations can describe the same complete reading.
    return list({digest(path):path for path in paths}.values())


def analyse(packet):
    exact = search(packet, 0)
    paths = exact or search(packet, 1)
    if not paths:
        raise PreflightError('no reading within one total relaxation: '+packet['id'])
    failures = [{s['step_id'] for s in path if s['relaxations']} for path in paths]
    unavoidable = sorted(set.intersection(*failures))
    kinds = {a['mismatch'] for path in paths for s in path for a in s['inputs'] if a['mismatch']}
    kind = 'benign' if exact else 'shift' if kinds == {'sense'} else 'smuggle' if kinds == {'unit'} else 'uncertain'
    return {'kind':kind, 'minimum_relaxations':0 if exact else 1,
            'zero_relaxation_assignments':len(exact), 'minimum_assignment_count':len(paths),
            'unavoidable_unlicensed_steps':unavoidable,
            'unlicensed_step_count':len(unavoidable), 'assignments':paths}


def resolution(item, review_row):
    evidence = analyse(item['payload'])
    defect = bool(review_row['review']['issues']) or not review_row['review']['ready']
    return {'item_id':item['id'], 'packet_sha256':digest(item['payload']),
            'review_sha256':digest(review_row), 'adjudicator':'Worker X / GPT-6 Astra',
            'outcome':'defect_claim_rejected' if defect else 'diagnosis_rejected',
            'reason':('Exactly one unavoidable unlicensed step, n03: n05 establishes '
                      'unit4 clear (contamination absent) via r15 branch 3, whereas r09 '
                      'requires optically transparent. This is the intended shift. '
                      'The alleged additional free shift at n20 is licensed by r10: '
                      'n16/r05 supplies space available and n06/r14 supplies fee waived.'
                      if defect else 'A complete zero-relaxation assignment licenses every step; '
                      'the proposed meaning-shift diagnosis is rejected.'),
            'method':'exhaustive public-record sense assignment; total relaxation budgets 0 then 1',
            'evidence':evidence}


def matches_reference(row, label):
    evidence = row['evidence']
    return (evidence['kind'] == label['kind'] and
            (evidence['minimum_relaxations'] == 0 if label['kind'] == 'benign' else
             evidence['minimum_relaxations'] == 1 and
             evidence['unavoidable_unlicensed_steps'] == label['acceptable_locations'][0]))


def adjudicate(base=HERE):
    items = {r['id']:r for split in ('dev','scored') for r in read(base/f'materials/{split}.jsonl.gz')}
    reviews = {r['item_id']:r for r in json.loads((base/'checks/gemini-rendered-submission.json').read_text())}
    labels = {r['id']:r for r in read(base/'labels.jsonl.gz')}
    rows = [resolution(items[i], reviews[i]) for i in sorted(AUTHORIZED_IDS)]
    if not all(matches_reference(row, labels[row['item_id']]) for row in rows):
        raise PreflightError('mechanical adjudication disagrees with intended diagnosis')
    report = {'authority':'Explicit Worker X instruction, 2026-09-22; six documented disputes only',
              'source_method':'round-5 Claude p5-review-v5/p5v5.py and solve2.py',
              'original_reviews_preserved':True, 'generation_calls':0, 'adjudications':rows}
    write_json(base/REPORT, report)
    return report


def verified_resolutions(base, items, reviews, labels):
    path = base/REPORT
    if not path.exists():
        return {}
    rows = json.loads(path.read_text())['adjudications']
    if len(rows) != len(AUTHORIZED_IDS) or {r['item_id'] for r in rows} != AUTHORIZED_IDS:
        raise PreflightError('adjudication must cover exactly the six authorized disputes')
    verified = {}
    for row in rows:
        i = row['item_id']
        if row != resolution(items[i], reviews[i]) or not matches_reference(row, labels[i]):
            raise PreflightError('stale or invalid licensing adjudication: '+i)
        verified[i] = row
    return verified


if __name__ == '__main__':
    report = adjudicate()
    print(json.dumps([{k:r[k] for k in ('item_id','outcome')} |
                      {k:r['evidence'][k] for k in ('kind','unavoidable_unlicensed_steps')}
                      for r in report['adjudications']], indent=2))
