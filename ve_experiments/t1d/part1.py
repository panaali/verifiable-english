"""T1d Part 1 offline preparation (no model calls).

  uv run python -m ve_experiments.t1d.part1 prepare --split dev|audit|full [--no-lean] [--workers 6]
  uv run python -m ve_experiments.t1d.part1 leakage

`prepare` regenerates the split deterministically, builds every certificate, replays it (Python and,
unless --no-lean, the Lean checker), runs the plain script, checks each expected outcome and writes
experiments/T1d/part1-<split>.json (per-item rows without the policy text, plus a summary).
`leakage` fits surface-feature classifiers on the audit and full splits and writes leakage.json.
Items are not stored: they are regenerated from seeds; the frozen copy is written at freeze time.
"""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
from multiprocessing import Pool
import json
from pathlib import Path

from . import certificates as C
from .leakage import audit, item_features
from .materials import BINDING_KINDS, SEMANTIC_KINDS, SPLITS, design, edges_of, generate

ROOT = Path(__file__).resolve().parents[2]
HOME = ROOT / 'experiments/T1d'


def expected(item, report, script):
    kind = item['sabotage_kind']
    same = report['statement'] == item['claim']
    if kind == 'honest':
        return report['verdict'] == script['verdict'] == 'VALID' and same
    if kind == 'leak':
        return report['verdict'] == script['verdict'] == 'INVALID' and same and script['leaking_edge_count'] == 1
    return report['verdict'] == script['verdict'] == 'VALID' and not same


def process(args):
    spec, lean = args
    item = generate(spec)  # raises if any ground-truth check fails
    edges = edges_of(item)
    sub = C.build(item, edges=edges)
    report = C.ve_verdict(item, sub, lean=lean, edges=edges)
    script = C.script_verdict(item, sub, edges=edges)
    ok = expected(item, report, script)
    return {'id': item['id'], 'seed': item['seed'], 'index': item['index'], 'family': item['family'],
            'scheme': item['scheme'], 'shape': item['shape'], 'sabotaged': item['sabotaged'],
            'kind': item['sabotage_kind'], 'hops': len(item['planted']), 'claim': item['claim'],
            'statement': report['statement'], 'set_size': report['set_size'], 'forged_leaves': sub['forged_leaves'],
            've_verdict': report['verdict'], 'python_replay': report['python_replay'],
            'replay_steps': report['python_replay_steps'], 'lean_replay_valid': report['lean_replay_valid'],
            'script_verdict': script['verdict'], 'expected_outcome': ok,
            'principal_in_set': item['principal'] in sub['separating_set'],
            'features': item_features(item, sub, report)}


def prepare(split, *, lean=True, workers=6):
    specs = design(split)
    with Pool(workers) as pool:
        rows = pool.map(process, [(s, lean) for s in specs], chunksize=1)
    by_kind = defaultdict(list)
    for r in rows:
        by_kind[r['kind']].append(r)
    summary = {
        'items': len(rows), 'counts': SPLITS[split], 'by_kind': {k: len(v) for k, v in sorted(by_kind.items())},
        'families': dict(Counter(r['family'] for r in rows)), 'schemes': dict(Counter(r['scheme'] for r in rows)),
        'shapes': dict(Counter(r['shape'] for r in rows)),
        'ground_truth_checks_passed': len(rows),
        'expected_outcome_all': all(r['expected_outcome'] for r in rows),
        'honest_certified_python': sum(r['python_replay'] == 'Valid' for r in by_kind['honest']),
        'honest_certified_lean': sum(r['lean_replay_valid'] is True for r in by_kind['honest']),
        've_script_agreement': sum(r['ve_verdict'] == r['script_verdict'] for r in rows) / len(rows),
        'leak_invalid': sum(r['ve_verdict'] == 'INVALID' for r in by_kind['leak']),
        'binding_valid_for_other_statement': {k: sum(r['ve_verdict'] == 'VALID' and r['statement'] != r['claim']
                                                     for r in by_kind[k]) for k in BINDING_KINDS},
        'set_size_by_kind': {k: [min(r['set_size'] for r in v), round(sum(r['set_size'] for r in v) / len(v), 1),
                                 max(r['set_size'] for r in v)] for k, v in sorted(by_kind.items())},
        'hops_range': [min(r['hops'] for r in rows), max(r['hops'] for r in rows)],
        'max_replay_steps': max(r['replay_steps'] for r in rows),
        'seed_collisions_with_T1c': seed_collisions([r['seed'] for r in rows]),
        'lean': lean}
    out = {'created_at': datetime.now(timezone.utc).isoformat(), 'model_calls': 0, 'split': split,
           'summary': summary, 'rows': rows}
    HOME.mkdir(parents=True, exist_ok=True)
    (HOME / f'part1-{split}.json').write_text(json.dumps(out, indent=1, sort_keys=True) + '\n')
    print(json.dumps(summary, indent=1))
    return out


def seed_collisions(seeds):
    """T1c item seeds: base + 100 * size + i for its three bases and two sizes."""
    t1c = {base + 100 * size + i for base in (202609260100, 202609270100, 202609280100)
           for size in (5000, 20000) for i in range(100)}
    return len(set(seeds) & t1c)


def leakage():
    rows = []
    for split in ('audit', 'full'):
        rows.extend(dict(r, split=split) for r in json.loads((HOME / f'part1-{split}.json').read_text())['rows'])
    result = {'created_at': datetime.now(timezone.utc).isoformat(), 'model_calls': 0,
              'criterion': 'near chance: every classifier AUC <= 0.60 and its bootstrap 95% CI includes 0.5 '
                           '(pooled audit+full items, honest vs sabotaged, surface features only)',
              'audits': {}}
    kinds = ('leak',) + BINDING_KINDS
    plan = {'all_sabotaged': kinds, 'binding': BINDING_KINDS, 'semantic': SEMANTIC_KINDS, 'leak': ('leak',)}
    plan.update({k: (k,) for k in BINDING_KINDS})
    for name, positive in plan.items():
        result['audits'][name] = audit(rows, positive=positive, permutations=100 if name == 'all_sabotaged' else 30)
        print(name, json.dumps(result['audits'][name]['models']), flush=True)
    main = result['audits']['all_sabotaged']['models']
    result['passes'] = all(m['auc'] <= .60 and m['ci95'][0] <= .5 for m in main.values())
    (HOME / 'leakage.json').write_text(json.dumps(result, indent=1) + '\n')
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=('prepare', 'leakage'))
    parser.add_argument('--split', choices=tuple(SPLITS), default='dev')
    parser.add_argument('--no-lean', action='store_true')
    parser.add_argument('--workers', type=int, default=6)
    args = parser.parse_args()
    if args.command == 'prepare':
        prepare(args.split, lean=not args.no_lean, workers=args.workers)
    else:
        leakage()


if __name__ == '__main__':
    main()
