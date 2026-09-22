"""Public prose/record soundness and reference-profile audit; no formal graph input."""
from collections import Counter
import re

from experiments.p5_paraphrase import inference_parts
from experiments.p5_materials import HERE, read
from ve_experiments.paid import digest

ATOM = re.compile(r'(unit\d+) is ([a-z-]+)(?: \(([a-z -]+)\))?')
REFERENCE = re.compile(r'the immediately preceding ([a-z-]+) result')


def inspect(packet):
    glossary = {}
    for g in packet['glossary']:
        meaning = g['sense'].split(': ', 1)[1].split(' (R', 1)[0]
        glossary.setdefault(g['term'], set()).add(meaning)

    def atoms(text):
        result = []
        for unit, term, sense in ATOM.findall(text):
            if not sense:
                if len(glossary[term]) != 1:
                    raise ValueError('unqualified ambiguous source atom')
                sense = next(iter(glossary[term]))
            if sense not in glossary[term]:
                raise ValueError('unglossed source sense')
            result.append((unit, term, sense))
        return result

    rules = []
    for record in packet['records']:
        for ant, con in re.findall(r'If (.*?), then (.*?)\.', record['text']):
            rules.append((set(atoms(ant)), atoms(con)[0]))
    facts = set()
    for premise in packet['premises']:
        facts.update(atoms(premise['text'].split('. The checks that')[0]))
    closure = set(facts)
    while True:
        extended = closure | {out for ins, out in rules if ins <= closure}
        if extended == closure:
            break
        closure = extended
    prior, profiles, failures, issue_types, frames = [], [], [], [], set()
    for paragraph in packet['argument'].split('\n\n'):
        node_id, text = paragraph[1:].split('] ', 1)
        premises, conclusion, _, frame = inference_parts(text)
        frames.add(frame)
        if '(' in text or ')' in text:
            raise ValueError('sense tag in inference prose')
        surface_con = ATOM.fullmatch(conclusion)
        if not surface_con:
            raise ValueError('invalid conclusion')
        available = set()
        for unit, term, _ in ATOM.findall(premises):
            candidates = {a for a in facts | set(prior) if a[:2] == (unit, term)}
            if not candidates:
                raise ValueError('unestablished literal premise')
            available.update(candidates)
        for term in REFERENCE.findall(premises):
            if not prior or prior[-1][1] != term:
                raise ValueError('invalid immediate reference')
            available.add(prior[-1])
            refs = [a for a in prior if a[1] == term]
            profiles.append({'node': node_id, 'counts': [len(refs), len({a[2] for a in refs}), len({a[0] for a in refs})]})
        relevant = [(ins, out) for ins, out in rules if out[:2] == surface_con.groups()[:2]]
        licensed = {out for ins, out in relevant if ins <= available}
        if not licensed:
            failures.append(node_id)
            missing = min((ins - available for ins, _ in relevant), key=len)
            if len(missing) != 1 or not REFERENCE.search(premises):
                raise ValueError('defect is not a single source-grounded bridge')
            required = next(iter(missing)); actual = prior[-1]
            if required[:2] == actual[:2] and required[2] != actual[2]:
                issue_types.append('shift')
            elif required[1:] == actual[1:] and required[0] != actual[0]:
                issue_types.append('smuggle')
            else:
                raise ValueError('defect is neither a sense shift nor a unit bridge')
            licensed = {out for _, out in relevant}
        if len(licensed) != 1:
            raise ValueError('record does not uniquely resolve the conclusion sense')
        prior.append(licensed.pop())
    return {'failures': failures, 'issue_types':issue_types, 'root_derivable': prior[-1] in closure,
            'profiles': profiles, 'frames': sorted(frames)}


def audit(base=HERE):
    items = read(base/'materials/dev.jsonl.gz') + read(base/'materials/scored.jsonl.gz')
    labels = {r['id']:r for r in read(base/'labels.jsonl.gz')}
    invalid = []; root_counts = Counter(); unique_hits = 0; ranks = Counter()
    for item in items:
        label = labels[item['id']]
        try:
            result = inspect(item['payload'])
            expected = [] if label['kind'] == 'benign' else label['acceptable_locations'][0]
            profiles = result['profiles']
            balanced = len(profiles) == 4 and all(r['counts'] == [3,2,2] for r in profiles)
            root_counts['derivable' if result['root_derivable'] else 'underivable'] += 1
            target = label['acceptable_locations'][0][0]
            ranks[next(n for n,r in enumerate(profiles) if r['node'] == target)] += 1
            maxima = [r['node'] for r in profiles if r['counts'][0] == max(q['counts'][0] for q in profiles)]
            unique_hits += label['kind'] != 'benign' and maxima == [target]
            if result['issue_types'] != ([] if label['kind']=='benign' else [label['kind']]) or result['failures'] != expected or result['root_derivable'] != (label['kind'] == 'benign') or not balanced or result['frames'] != list(range(4)):
                invalid.append(item['id'])
        except (ValueError, KeyError, StopIteration) as exc:
            invalid.append({'id':item['id'], 'error':str(exc)})
    return {'passed':len(items)==84 and not invalid, 'items':len(items), 'invalid':invalid,
            'root_counts':dict(root_counts), 'reference_profile':[3,2,2], 'references_per_packet':4,
            'critical_ordinal_counts':dict(ranks), 'unique_maximum_localizations':unique_hits,
            'flawed_packets':56, 'frames_per_packet':4, 'packet_sha256':digest([i['payload'] for i in items]),
            'generation_calls':0}
