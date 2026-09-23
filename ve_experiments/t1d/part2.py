"""T1d Part 2 feasibility (offline, no model calls).

    UV_CACHE_DIR=/private/tmp/ve-uv-cache-t1d \
      uv run --with z3-solver==5.1.0.0 python -m ve_experiments.t1d.part2

Writes experiments/T1d/part2-feasibility.json:
* 30 generated rule sets (seeds SEED_BASE + attempt), gold claim FALSE, each with one accepted
  mutant (claim TRUE) of an assigned type (cycled over the four mutation types; a rule set with
  no valid mutant of its type is skipped and logged); per type, the acceptance rate over all
  candidate single-rule mutations.
* For every claim instance: validator verdict, concrete witness + BFS (false claims), Z3 CHC
  verdict (primary baseline), Z3 FOL+TransitiveClosure verdict (secondary; unknown expected),
  VE certification (untrusted builder, Python and Lean replay), forged-certificate rejection on
  false claims, and non-replay of the mutant's certificate against the gold rule set.
* A documented attempt with the generic `prove_entailment` search on the first mutants.
* Closed-world "unless" snapshots: separating-set certificates with negated guards and tag
  completion axioms (Python and Lean replay), plus a forged (negation-flip) variant.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import random
import time

from . import rules as R

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'experiments/T1d/part2-feasibility.json'
N_RULESETS = 30
N_SNAPSHOTS = 16
GENERIC_SEARCH = {'rulesets': 3, 'max_steps': 200_000}


def _lean(name, env, ps, g, cert):
    from ve_experiments.t1c.certificates import LEAN, envelope, lean_replay
    if not LEAN.exists():
        return None
    return bool(lean_replay([envelope(name, env, ps, g, cert)])[0]['valid'])


def _trace_depth(node):
    return 1 + max([_trace_depth(c) for c in node.get('children', [])] or [0])


def claim_row(rs, name, z3):
    from ve import check_entailment_certificate
    row = {'name': name}
    v = R.validate(rs)
    row['validator_claim_true'] = v['claim_true']
    if not v['claim_true']:
        w = R.witness_state(rs, v['witness_types'], v['witness_rules'])
        row['witness_length'] = len(v['witness_rules'])
        row['witness_bfs_violation'] = w['violation_by_bfs']
    t = time.time()
    row['z3_chc_claim_true'] = z3.chc_verdict(rs)
    row['z3_chc_seconds'] = round(time.time() - t, 3)
    t = time.time()
    row['z3_fol_claim_true'] = z3.fol_verdict(rs)
    row['z3_fol_seconds'] = round(time.time() - t, 3)
    dnf, which = R.invariant_dnf(rs)
    row['invariant'] = {'kind': which, 'cubes': len(dnf), 'literals': sum(len(c) for c in dnf)}
    ve = R.ve_certify_built(rs, dnf)
    row['ve_certificate_built'] = ve['built']
    if ve['built']:
        row['ve_python_replay_valid'] = ve['python_replay_valid']
        row['ve_python_replay_steps'] = ve['python_replay_steps']
        row['ve_lean_replay_valid'] = _lean(name, ve['env'], ve['premises'], ve['goal'], ve['certificate'])
        row['ve_trace_depth'] = _trace_depth(ve['certificate']['trace'])
        row['ve_build_seconds'] = ve['build_seconds']
    else:
        row['ve_build_failure'] = ve['reason']
    row['ve_certified'] = bool(ve['built'] and ve['python_replay_valid'] and row.get('ve_lean_replay_valid') is not False)
    if not v['claim_true']:
        forged = R.ve_certify_built(rs, dnf, forge=True)
        row['forged'] = {'forged_leaves': forged.get('forged_leaves'),
                         'python_replay_valid': forged['python_replay_valid'],
                         'python_replay_status': forged.get('python_replay_status'),
                         'lean_replay_valid': _lean(name + '-forged', forged['env'], forged['premises'],
                                                    forged['goal'], forged['certificate'])}
    return row, ve


def run():
    from . import z3check as z3
    rows, skipped = [], []
    type_stats = {k: Counter() for k in R.MUTATIONS}
    attempt = 0
    t_start = time.time()
    while len(rows) < N_RULESETS:
        seed = R.SEED_BASE + attempt
        attempt += 1
        kind = R.MUTATIONS[len(rows) % len(R.MUTATIONS)]
        gold = R.generate(seed)
        if z3.chc_verdict(gold) is not False:
            skipped.append({'seed': seed, 'reason': 'Z3 does not confirm the gold claim is false'})
            continue
        chosen = {}
        for k in R.MUTATIONS:
            rng = random.Random(seed * 7 + R.MUTATIONS.index(k))
            ch, tried, accepted = R.mutate(gold, k, rng, z3_verdict=z3.chc_verdict)
            type_stats[k]['gold_rule_sets'] += 1
            type_stats[k]['candidates'] += tried
            type_stats[k]['accepted_candidates'] += accepted
            type_stats[k]['rule_sets_with_valid_mutant'] += ch is not None
            chosen[k] = ch
        if chosen[kind] is None:
            skipped.append({'seed': seed, 'reason': f'no valid {kind} mutant'})
            continue
        desc, mutant = chosen[kind]
        gold_row, _ = claim_row(gold, gold['id'] + '-gold', z3)
        mut_row, mut_ve = claim_row(mutant, gold['id'] + '-mutant', z3)
        # The mutant's certificate is valid only relative to the mutant.
        from ve import check_entailment_certificate
        cross = None
        if mut_ve['built']:
            gp, gg = R.premises(gold), R.goal(gold)
            chk = check_entailment_certificate(R.ve_env(), gp, gg, mut_ve['certificate'], max_steps=2_000_000)
            cross = {'python_replay_valid': chk.valid, 'status': chk.status, 'detail': chk.detail[:160],
                     'lean_replay_valid': _lean(gold['id'] + '-cross', R.ve_env(), gp, gg, mut_ve['certificate'])}
        english_gold, english_mut = R.render_english(gold).splitlines(), R.render_english(mutant).splitlines()
        rows.append({'id': gold['id'], 'seed': seed, 'claim': gold['claim'], 'rules': len(gold['rules']),
                     'constraints': len(gold['constraints']),
                     'negated_guards_in_gold': sum(not p for r in gold['rules'] for _, p in r['src'] + r['dst']),
                     'mutation': desc, 'gold': gold_row, 'mutant': mut_row,
                     'mutant_certificate_against_gold': cross,
                     'english_lines_changed': sum(a != b for a, b in zip(english_gold, english_mut))
                     + abs(len(english_gold) - len(english_mut)),
                     'render_bytes': {'json': len(R.render_json(gold)), 'english': len(R.render_english(gold)),
                                      've': len(R.render_ve(gold))},
                     'gold_ruleset': gold, 'mutant_ruleset': mutant})
        print(len(rows), gold['id'], kind, mut_row['ve_certified'], flush=True)
    part2_seconds = round(time.time() - t_start, 1)

    # Generic search, documented: the same claims with the library's own proof search.
    from ve import prove_entailment
    generic = []
    for r in rows[:GENERIC_SEARCH['rulesets']]:
        m = r['mutant_ruleset']
        dnf, _ = R.invariant_dnf(m)
        t = time.time()
        res = prove_entailment(R.ve_env(), R.premises(m), R.goal(m), invariants=[R.invariant_formula(dnf)],
                               max_steps=GENERIC_SEARCH['max_steps'])
        generic.append({'id': r['id'], 'status': res.status, 'steps': res.steps, 'seconds': round(time.time() - t, 1)})

    # Closed-world "unless" snapshots.
    snaps = []
    for i in range(N_SNAPSHOTS):
        s = R.generate_snapshot(R.SNAP_SEED + i)
        facts = [tuple(f) for f in s['facts']]
        tags = {k: set(v) for k, v in s['tags'].items()}
        no_negated = [{**r, 'src': [l for l in r['src'] if l[1]], 'dst': [l for l in r['dst'] if l[1]]}
                      for r in R.SNAP_RULES]
        try:
            row = R.certify_snapshot(s)
            env, ps, g, S = R.snapshot_encoding(s)
        except R.OpenBranch as e:
            row = {'id': s['id'], 'python_replay_valid': False, 'lean_replay_valid': False, 'failure': str(e)}
        row['negated_guard_essential'] = s['resource'] in R._snap_reach(facts, tags, no_negated, s['principal'])
        row['forged_negation_flip'] = R.forged_snapshot(s)
        snaps.append(row)

    true_rows = [r['mutant'] for r in rows]
    false_rows = [r['gold'] for r in rows]
    all_rows = true_rows + false_rows
    ve_verdict = lambda c: True if c['ve_certified'] else None  # VE certifies or is silent
    summary = {
        'rule_sets': len(rows), 'attempts': attempt, 'skipped': len(skipped),
        'claims_true_mutants': len(true_rows), 'claims_false_gold': len(false_rows),
        'validator_z3chc_agreement': sum(c['validator_claim_true'] == c['z3_chc_claim_true'] for c in all_rows) / len(all_rows),
        'witness_bfs_confirms_false_gold': sum(bool(c.get('witness_bfs_violation')) for c in false_rows) / len(false_rows),
        've_certification_rate_true_claims': sum(c['ve_certified'] for c in true_rows) / len(true_rows),
        've_certified_false_claims': sum(c['ve_certified'] for c in false_rows),
        'forged_certificates_rejected_python': sum(not c['forged']['python_replay_valid'] for c in false_rows) / len(false_rows),
        'forged_certificates_rejected_lean': sum(c['forged']['lean_replay_valid'] is False for c in false_rows) / len(false_rows),
        've_vs_z3chc_agreement': sum((c['ve_certified'] and c['z3_chc_claim_true'] is True)
                                     or (not c['ve_certified'] and c['z3_chc_claim_true'] is False)
                                     for c in all_rows) / len(all_rows),
        'mutant_certificate_rejected_against_gold': sum(r['mutant_certificate_against_gold'] is not None
                                                        and not r['mutant_certificate_against_gold']['python_replay_valid']
                                                        for r in rows) / len(rows),
        'z3_fol_verdicts': {'true_claims': dict(Counter(str(c['z3_fol_claim_true']) for c in true_rows)),
                            'false_claims': dict(Counter(str(c['z3_fol_claim_true']) for c in false_rows))},
        'mutation_types_assigned': dict(Counter(r['mutation']['kind'] for r in rows)),
        'mutation_acceptance': {k: {**v, 'candidate_acceptance_rate': round(v['accepted_candidates'] / max(1, v['candidates']), 3),
                                    'rule_set_rate': round(v['rule_sets_with_valid_mutant'] / max(1, v['gold_rule_sets']), 3)}
                                for k, v in type_stats.items()},
        've_python_replay_steps_max': max(c.get('ve_python_replay_steps', 0) for c in true_rows),
        've_trace_depth_max': max(c.get('ve_trace_depth', 0) for c in true_rows),
        've_build_seconds_max': max(c.get('ve_build_seconds', 0) for c in true_rows),
        'z3_chc_seconds_max': max(c['z3_chc_seconds'] for c in all_rows),
        'part2_seconds': part2_seconds,
        'generic_prove_entailment': generic,
        'closed_world_unless': {
            'snapshots': len(snaps),
            'certified_python_and_lean': sum(bool(s['python_replay_valid']) and s.get('lean_replay_valid') is not False
                                             for s in snaps),
            'negated_guard_essential': sum(s['negated_guard_essential'] for s in snaps),
            'forged_negation_flip_rejected': sum(1 for s in snaps if s['forged_negation_flip']
                                                 and not s['forged_negation_flip']['python_replay_valid']),
            'forged_negation_flip_constructed': sum(1 for s in snaps if s['forged_negation_flip']),
            'set_size_range': [min(s.get('set_size', 0) for s in snaps), max(s.get('set_size', 0) for s in snaps)]},
    }
    result = {'created_at': datetime.now(timezone.utc).isoformat(), 'model_calls': 0,
              'z3_version': z3.Z3_VERSION, 'seed_base': R.SEED_BASE, 'snapshot_seed': R.SNAP_SEED,
              'summary': summary, 'skipped': skipped, 'rows': rows, 'snapshots': snaps,
              'example_renderings': {'id': rows[0]['id'], 'json': R.render_json(rows[0]['gold_ruleset']),
                                     'english': R.render_english(rows[0]['gold_ruleset']),
                                     've': R.render_ve(rows[0]['gold_ruleset'])}}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=1, sort_keys=True, default=list) + '\n')
    print(json.dumps(summary, indent=1, default=list))
    return result


if __name__ == '__main__':
    run()
