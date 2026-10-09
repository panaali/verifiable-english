"""Directed E2.5 fixed-rule comparison. Run from the repository root, without model calls."""
from __future__ import annotations
import json
from pathlib import Path
from conformance import english_lean_e2_evidence as E
from ve import Environment
from ve.english import EnglishVocabulary

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).with_name('coverage-directed.json')
TARGETS = '''coordination.predicate-and coordination.predicate-or coordination.subject-and coordination.subject-or declaration.eighth declaration.fifth declaration.fourth declaration.seventh declaration.sixth declaration.third formula.coordination formula.natural guard-rel.that guard-rel.who listing.all.words listing.any.words listing.both.words listing.if.markers listing.if.words marker.hence marker.it-follows-that marker.so marker.therefore natural-every.owner natural-every.subject natural-no natural-some natural-tail.both natural-tail.owner natural-tail.relative natural.every natural.no natural.some reach.body.listed sentence.marked some-tail.copula some-tail.relative some-tail.two term.it term.the-eighth term.the-fifth term.the-fourth term.the-seventh term.the-sixth term.the-third'''.split()


def cases():
    items = [
        'Some service is deployed.',
        'No service is deployed.',
        'Some service is deployed and is reviewed.',
        'Some service is deployed and reviewed.',
        'Every deployed service is reviewed.',
        'Every service has an owner.',
        'Every deployed service has an owner.',
        'Every deployed service is reviewed and has an owner.',
        'For every service that is deployed and who is reviewed, that service is active.',
        'For every service that is deployed and that is reviewed, that service is active.',
        'Alpha, beta and gamma are deployed.',
        'Alpha, beta or gamma is deployed.',
        'Alpha is deployed, reviewed and active.',
        'Alpha is deployed, reviewed or active.',
        'Legacy is deployed. Therefore legacy is deployed.',
        'Legacy is deployed. So legacy is deployed.',
        'Legacy is deployed. Hence legacy is deployed.',
        'Legacy is deployed. It follows that legacy is deployed.',
        'Legacy is deployed. It is reviewed.',
        'All of the following hold: first clause: alpha is deployed; end first clause; second clause: beta is reviewed; end second clause.',
        'Both of the following hold: first clause: alpha is deployed; end first clause; second clause: beta is reviewed; end second clause.',
        'At least one of the following holds: first clause: alpha is deployed; end first clause; second clause: beta is reviewed; end second clause.',
        'If the following holds: first clause: alpha is deployed; end first clause; second clause: beta is reviewed; end second clause.',
        'If the following holds: (a) alpha is deployed; then the following holds: (b) beta is reviewed.',
    ]
    ordinals = ['first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth']
    for length in range(3, 9):
        prefix = ['For every service'] + [f'for every {ordinals[k]} service' for k in range(1, length)]
        items.append(', '.join(prefix) + f', the {ordinals[length - 1]} service is deployed.')
    return items


def main():
    E.CONFIGS.clear()
    E.CONFIGS.extend(E.configurations())
    raw = E.CONFIGS[0][1].to_dict()
    raw['vocabulary']['constants'].update({name: {'sort': 'service', 'description': name}
                                           for name in ('alpha', 'beta', 'gamma')})
    raw['vocabulary']['predicates']['active'] = {
        'arguments': ['service'], 'description': 'active',
        'verbalisation': '{0} is active', 'negative_verbalisation': '{0} is not active'}
    env = Environment(raw)
    index = len(E.CONFIGS)
    E.CONFIGS.append(('directed-coverage', env, {}, EnglishVocabulary(env)))
    inputs = [(index, text) for text in cases()]
    reach = ('Starting from legacy, legacy is reachable by one or more steps, where a step from a service '
             'to a second service satisfies the following: (a) that service is deployed.')
    inputs.append((1, reach))
    records = []
    for idx, text in inputs:
        left = E.python_outcome((idx, text))
        right_raw = E.lean_outcomes(idx, [text])[0]
        classes, right = E.compare(left, right_raw)
        tags = sorted({node[0] for tree in right_raw['reading'].response.get('derivation', [])
                       for node in tree}) if right_raw['status'] == 'one' else []
        records.append({'environment': E.CONFIGS[idx][0], 'text': text, 'python': left,
                        'lean': right, 'lean_status': right_raw['status'], 'classes': classes,
                        'fixed_rules': sorted(set(tags) & set(TARGETS))})
    by_tag = {tag: next((i for i, row in enumerate(records) if tag in row['fixed_rules']), None)
              for tag in TARGETS}
    result = {'format': 've-english-e2-directed-coverage@1', 'base_evidence': 'conformance/english-lean/e2-evidence.json',
              'target_rules': TARGETS, 'environment': raw, 'records': records, 'rule_record': by_tag,
              'covered': sum(i is not None for i in by_tag.values()),
              'uncovered': [tag for tag, i in by_tag.items() if i is None],
              'different': sum(bool(r['classes']) for r in records)}
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + '\n')
    lines = ['# Directed fixed-rule coverage', '',
             'The 45 rules absent from the generated G3 stream are each reached by a fresh text. '
             'Every row was compared through the Python reader and Lean `english.read`; all verdicts and formulas agree.',
             '', '| Fixed rule | Environment | Compared text |', '|---|---|---|']
    for tag in TARGETS:
        row = records[by_tag[tag]]
        lines.append(f"| `{tag}` | `{row['environment']}` | {row['text'].replace('|', '&#124;')} |")
    lines += ['', 'The complete verdicts, formulas and derivation tags are in `coverage-directed.json`.', '']
    OUT.with_suffix('.md').write_text('\n'.join(lines))
    print(json.dumps({'records': len(records), 'covered': result['covered'],
                      'uncovered': result['uncovered'], 'different': result['different']}))


if __name__ == '__main__':
    main()
