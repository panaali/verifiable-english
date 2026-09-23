"""T1d Part 1 offline preparation (no model calls).

  uv run python -m ve_experiments.t1d.part1 prepare --split dev|audit|full [--no-lean] [--workers 6]
  uv run python -m ve_experiments.t1d.part1 leakage-dev      # leakdev split only (development)
  uv run python -m ve_experiments.t1d.part1 leakage          # THE v3 audit: fresh audit + full splits, once

`prepare` regenerates the split deterministically, builds every certificate, replays it (Python and,
unless --no-lean, the Lean checker), runs the plain script, checks each expected outcome and writes
experiments/T1d/part1-<split>.json (per-item rows without the policy text, plus a summary).
Every row carries the SHA-256 of the exact rendered raw-arm and VE-arm prompts (`protocol.prompts`,
HMAC prefix masked) and the leakage features computed from those prompt strings.
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
from . import protocol as P
from .leakage import FEATURE_SETS, criterion, prompt_features, run_audits, univariate
from .materials import (BINDING_KINDS, BURNED_SEED_TAGS, CHAR_KINDS, RELATED_KINDS, SPLITS, design, edges_of, generate,
                        seed_of)

ROOT = Path(__file__).resolve().parents[2]
HOME = ROOT / 'experiments/T1d'



def expected(item, report, script):
    """v3: no certified statement is string-identical to its claim (the claim names a display name);
    the directory-bridged entailment rule separates every kind."""
    kind = item['sabotage_kind']
    if report['statement'] == item['claim']:
        return False
    bridged = P.rule_decision(item, dict(report, verdict='VALID')) == 'APPROVE'
    if kind == 'honest':
        return report['verdict'] == script['verdict'] == 'VALID' and bridged and P.rule_decision(item, report) == 'APPROVE'
    if kind == 'leak':
        return report['verdict'] == script['verdict'] == 'INVALID' and bridged and script['leaking_edge_count'] == 1
    return report['verdict'] == script['verdict'] == 'VALID' and not bridged


def process(args):
    spec, lean = args
    item = generate(spec)  # raises if any ground-truth check fails
    edges = edges_of(item)
    sub = C.build(item, edges=edges)
    report = C.ve_verdict(item, sub, lean=lean, edges=edges)
    script = C.script_verdict(item, sub, edges=edges)
    ok = expected(item, report, script)
    raw_system, raw_user = P.prompts(item, 'opus-raw')
    ve_system, ve_user = P.prompts(item, 'opus-ve', submission=sub, report=report)
    raw_features, family = prompt_features(raw_system, raw_user)
    refs = None if item['sabotaged'] else {'group_member': item['roles']['primary_group'],
                                           'role_user': item['roles']['direct_role']}
    ve_features, family_ve = prompt_features(ve_system, ve_user, refs)
    if family != item['family'] or family_ve != item['family']:
        raise AssertionError('family not recoverable from the prompt')
    features = {'raw_prompt': {f: raw_features[f] for f in FEATURE_SETS['raw_prompt']},
                've_prompt': {f: ve_features[f] for f in FEATURE_SETS['ve_prompt']}}
    if refs:
        features['references'] = ve_features['references']
    return {'id': item['id'], 'seed': item['seed'], 'index': item['index'], 'family': item['family'],
            'scheme': item['scheme'], 'shape': item['shape'], 'sabotaged': item['sabotaged'],
            'kind': item['sabotage_kind'], 'hops': len(item['planted']), 'claim': item['claim'], 'facts': item['grants'],
            'target_bytes': spec.get('target_bytes'),
            'claim_principal': item['claim_principal'], 'account': item['principal'],
            'statement': report['statement'], 'set_size': report['set_size'], 'forged_leaves': sub['forged_leaves'],
            've_verdict': report['verdict'], 'python_replay': report['python_replay'],
            'replay_steps': report['python_replay_steps'], 'lean_replay_valid': report['lean_replay_valid'],
            'script_verdict': script['verdict'], 'expected_outcome': ok,
            'principal_in_set': item['principal'] in sub['separating_set'],
            'statement_subject': sub['principal'], 'statement_resource': sub['resource'], 'resource': item['resource'],
            'statement_subject_kind': 'U' if sub['principal'] in (item['principal'], item['roles']['near_principal'],
                                                                  item['roles']['alias_account']) else 'other',
            'rule_decision': P.rule_decision(item, report), 'equality_rule': 'APPROVE' if report['verdict'] == 'VALID'
            and report['statement'] == item['claim'] else 'REJECT',
            'prompt_sha256': {'raw': P.prompt_hash(raw_system, raw_user), 've': P.prompt_hash(ve_system, ve_user)},
            'prompt_bytes': {'raw': len((raw_system + raw_user).encode()), 've': len((ve_system + ve_user).encode())},
            'shown_report': P.trusted_report(report), 'features': features}


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
        'statement_string_equals_claim': sum(r['statement'] == r['claim'] for r in rows),
        'equality_rule_accuracy': sum((r['equality_rule'] == 'APPROVE') == (r['kind'] == 'honest') for r in rows) / len(rows),
        'equality_rule_honest_approvals': sum(r['equality_rule'] == 'APPROVE' for r in by_kind['honest']),
        'directory_rule_accuracy': sum((r['rule_decision'] == 'APPROVE') == (r['kind'] == 'honest') for r in rows) / len(rows),
        'set_size_by_kind': {k: [min(r['set_size'] for r in v), round(sum(r['set_size'] for r in v) / len(v), 1),
                                 max(r['set_size'] for r in v)] for k, v in sorted(by_kind.items())},
        'hops_range': [min(r['hops'] for r in rows), max(r['hops'] for r in rows)],
        'max_replay_steps': max(r['replay_steps'] for r in rows),
        'facts_range': [min(r['facts'] for r in rows), max(r['facts'] for r in rows)],
        'raw_prompt_bytes_range': [min(r['prompt_bytes']['raw'] for r in rows), max(r['prompt_bytes']['raw'] for r in rows)],
        've_prompt_bytes_max': max(r['prompt_bytes']['ve'] for r in rows),
        'seed_collisions_with_T1c_or_burned_v2_v3': seed_collisions([r['seed'] for r in rows]),
        'lean': lean}
    out = {'created_at': datetime.now(timezone.utc).isoformat(), 'model_calls': 0, 'split': split,
           'summary': summary, 'rows': rows}
    HOME.mkdir(parents=True, exist_ok=True)
    (HOME / f'part1-{split}.json').write_text(json.dumps(out, indent=1, sort_keys=True) + '\n')
    print(json.dumps(summary, indent=1))
    return out


def seed_collisions(seeds):
    """Collisions with T1c item seeds (base + 100 * size + i for its three bases and two sizes) and with
    the burned T1d v2 seeds (every v2 split)."""
    t1c = {base + 100 * size + i for base in (202609260100, 202609270100, 202609280100)
           for size in (5000, 20000) for i in range(100)}
    v2 = {seed_of(split, i, BURNED_SEED_TAGS[0]) for split, n in (('dev', 12), ('audit', 300), ('full', 270)) for i in range(n)}
    v3 = {seed_of(split, i, BURNED_SEED_TAGS[1]) for split, n in (('dev', 12), ('leakdev', 500), ('audit', 300),
                                                                   ('full', 270)) for i in range(n)}
    return len(set(seeds) & (t1c | v2 | v3))


GROUPS = {'all_sabotaged': ('leak',) + BINDING_KINDS, 'binding': BINDING_KINDS, 'char': CHAR_KINDS,
          'related': RELATED_KINDS, 'leak': ('leak',), **{k: (k,) for k in BINDING_KINDS}}
POOLED = ('all_sabotaged', 'binding', 'char', 'related')
# v4: 40 multivariate tests x 2,000 permutations: the smallest attainable Holm-adjusted p is 40 / 2,001
# = .020, so the gate can fail. Repeats cut from 10 to 2 (for the observed statistic and every
# permutation alike) to afford the permutations.
AUDIT = {'repeats': 2, 'permutations': 2000, 'boot': 2000}


def _summarise(results):
    return {fs: {g: {name: [round(m['foldwise_auc'], 4), m.get('p_two_sided')] for name, m in r['models'].items()}
                 for g, r in gs.items()} for fs, gs in results.items()}


def leakage(dev=False):
    """dev=True: the burned leakdev split (development only, fewer permutations). Otherwise THE v4
    audit, run once on the fresh v4 audit + full splits, with the criterion declared in
    leakage.criterion."""
    splits = ('leakdev',) if dev else ('audit', 'full')
    rows = []
    for split in splits:
        rows.extend(dict(r, split=split) for r in json.loads((HOME / f'part1-{split}.json').read_text())['rows'])
    settings = dict(AUDIT, permutations=200) if dev else AUDIT
    results = run_audits(rows, GROUPS, **settings)
    uni = univariate(rows, GROUPS)
    result = {'created_at': datetime.now(timezone.utc).isoformat(), 'model_calls': 0, 'splits': list(splits),
              'items': len(rows), 'settings': settings, 'feature_sets': {k: list(v) for k, v in FEATURE_SETS.items()},
              'criterion': leakage_criterion_text(), 'summary': _summarise(results), 'audits': results,
              'univariate': [{'feature_set': k[0], 'group': k[1], 'feature': k[2], **v} for k, v in sorted(uni.items())],
              'descriptive_decision_variable': decision_variable_auc(rows)}
    result['verdict'] = criterion(results, POOLED, uni)
    name = 'leakage-dev.json' if dev else 'leakage.json'
    (HOME / name).write_text(json.dumps(result, indent=1) + '\n')
    print(json.dumps(result['summary'], indent=1))
    print(json.dumps(result['verdict'], indent=1))
    return result


def decision_variable_auc(rows):
    """Descriptive, not gated: how well string-level functions of the certified statement alone
    (excluded as the decision variable) separate each kind from honest items."""
    import numpy as np
    from sklearn.metrics import roc_auc_score
    out = {}
    for g, positive in GROUPS.items():
        chosen = [r for r in rows if r['kind'] in positive or r['kind'] == 'honest']
        y = np.array([r['kind'] != 'honest' for r in chosen], dtype=int)
        same = np.array([r['statement_subject'] != r['account'] or r['statement_resource'] != r['resource']
                         for r in chosen], dtype=float)
        kind = np.array([r['statement_subject_kind'] != 'U' for r in chosen], dtype=float)
        out[g] = {'identity_mismatch_auc': float(roc_auc_score(y, same)),
                  'subject_kind_not_principal_auc': float(roc_auc_score(y, kind))}
    return out


def leakage_criterion_text():
    return ('v4, declared before the single fresh-seed audit: features computed from the rendered prompt strings '
            '(raw-arm set: global statistics + claimed account and resource graph profiles; VE-arm set: global '
            'statistics + certified subject and resource graph profiles + masked display); per kind and pooled '
            'groups vs honest; foldwise AUC over 2 x 5-fold CV; null from 2,000 full-procedure label permutations; '
            'two-sided unrounded p. PASS iff (a) every Holm-adjusted multivariate p (2 feature sets x 10 groups x 2 '
            'classifiers = 40 tests; smallest attainable 40/2001 = .020) >= .05, (b) the 16 pooled-group tests, Holm-'
            'adjusted among themselves, are >= .05, and (c) every univariate Mann-Whitney p, Holm-adjusted over all '
            'univariate tests, >= .05.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=('prepare', 'leakage', 'leakage-dev'))
    parser.add_argument('--split', choices=tuple(SPLITS), default='dev')
    parser.add_argument('--no-lean', action='store_true')
    parser.add_argument('--workers', type=int, default=6)
    args = parser.parse_args()
    if args.command == 'prepare':
        prepare(args.split, lean=not args.no_lean, workers=args.workers)
    else:
        leakage(dev=args.command == 'leakage-dev')


if __name__ == '__main__':
    main()
