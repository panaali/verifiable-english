"""T1d Part 2 (v3): an OFFLINE verification comparison for universal rule-level claims. No model
calls and no model-monitor study (dropped after the second review: a monitor holding the gold rules
can diff or re-run CHC, and every honest item would carry a label-revealing diff).

    PYTHONPATH=. UV_CACHE_DIR=/private/tmp/ve-uv-cache-t1d \\
      uv run --project experiments/T1d/solvers --locked python -m ve_experiments.t1d.part2

Writes experiments/T1d/part2-verification.json and part2-claims.jsonl.gz (every claim row).

Claims. Gold rule sets are generated from seeds SEED_BASE + attempt (claim FALSE by the independent
validator); every single-rule mutation candidate of every type is enumerated for every attempted gold
set. Selection uses the independent validator ONLY (v2 also required Z3 agreement, which selected
for agreement). The first N_RULESETS gold sets with a validator-true candidate of the assigned type
form the "selected" sample, but ALL attempted claims are denominators:
  golds       every attempted gold claim (false);
  candidates  every mutation candidate of every attempted gold set (true or false by the validator).

Verifiers, each reported as proved / refuted / unknown on every claim (VE and the ground check can
only prove; failure is "unknown", never "false"):
  validator   pure Python over tag vectors (reference; no ve, no solver);
  z3_chc      Z3 Spacer over constrained Horn clauses (a decider);
  ground_z3, ground_cvc5  ground inductiveness of the SAME DNF invariant VE uses (three queries);
  ve          closure@0 certificate from the dedicated untrusted builder, replayed in Python and, for
              every Python-valid certificate, by the Lean-proved checker.
Timing is end to end: VE and ground times include invariant construction. Every claim where a
definite verdict contradicts the validator is logged (candidate-level disagreement log).

Regressions on the selected sample: forged certificates for the false gold claims must not replay;
the mutant's certificate, REBOUND to the gold inputs (binding fields replaced, so the input check
passes), must fail logically (not at the binding) in Python and in Lean, and the Python failure must
be located at the mutated rule: the failing branch holds the gold's mutated edge case, or the failing
expansion is a disjunction node that contains it; for a dropped rule (which reshapes the step
disjunction) the failure must be in the step-case analysis. The v2 check stopped at the binding.
Also kept from v2: the generic `prove_entailment` attempt and the closed-world "unless" snapshots.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import gzip
import json
import multiprocessing
from pathlib import Path
import random
import subprocess
import time

from . import rules as R

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'experiments/T1d/part2-verification.json'
CLAIMS = ROOT / 'experiments/T1d/part2-claims.jsonl.gz'
N_RULESETS = 30
N_SNAPSHOTS = 16
GENERIC_SEARCH = {'rulesets': 3, 'max_steps': 200_000}
VERIFIERS = ('z3_chc', 'ground_z3', 'ground_cvc5', 've')


def _lean(name, env, ps, g, cert):
    from ve_experiments.t1c.certificates import LEAN, envelope, lean_replay
    if not LEAN.exists():
        return None
    return bool(lean_replay([envelope(name, env, ps, g, cert)])[0]['valid'])


def _trace_depth(node):
    return 1 + max([_trace_depth(c) for c in node.get('children', [])] or [0])


def verify(args):
    """Every verifier on one claim (worker process). Returns (row, certificate or None)."""
    name, rs, lean = args
    from . import z3check as Z
    row = {'name': name}
    v = R.validate(rs)
    row['validator'] = 'true' if v['claim_true'] else 'false'
    if not v['claim_true']:
        row['witness_bfs_violation'] = R.witness_state(rs, v['witness_types'], v['witness_rules'])['violation_by_bfs']
    t = time.time()
    chc = Z.chc_verdict(rs)
    row['z3_chc'] = {True: 'proved', False: 'refuted', None: 'unknown'}[chc]
    row['z3_chc_seconds'] = round(time.time() - t, 4)
    t = time.time()
    dnf, which = R.invariant_dnf(rs)
    inv_s = time.time() - t
    row['invariant'] = {'kind': which, 'cubes': len(dnf), 'literals': sum(len(c) for c in dnf), 'seconds': round(inv_s, 4)}
    for solver in ('z3', 'cvc5'):
        g = Z.ground_check(rs, dnf, solver)
        row[f'ground_{solver}'] = g['verdict']
        row[f'ground_{solver}_queries'] = g['queries']
        row[f'ground_{solver}_seconds'] = round(inv_s + g['seconds'], 4)
    ve = R.ve_certify_built(rs, dnf)
    row['ve_python'] = bool(ve['built'] and ve['python_replay_valid'])
    row['ve_seconds'] = round(inv_s + ve['build_seconds'] + ve.get('replay_seconds', 0), 4)
    cert = None
    if ve['built']:
        row['ve_replay_steps'] = ve['python_replay_steps']
        row['ve_trace_depth'] = _trace_depth(ve['certificate']['trace'])
        cert = ve['certificate']
    else:
        row['ve_failure'] = ve['reason']
    row['ve_lean'] = _lean(name, ve['env'], ve['premises'], ve['goal'], cert) if (lean and row['ve_python']) else None
    row['ve'] = 'proved' if row['ve_python'] and row['ve_lean'] is not False else 'unknown'
    return row, cert


def tally(rows):
    """proved / refuted / unknown per verifier, split by the validator's verdict."""
    out = {}
    for truth in ('true', 'false'):
        sub = [r for r in rows if r['validator'] == truth]
        out[f'validator_{truth}'] = {'n': len(sub), **{v: dict(sorted(Counter(r[v] for r in sub).items()))
                                                      for v in VERIFIERS}}
    return out


def disagreements(rows):
    """Definite verdicts that contradict the validator (proved on a false claim, refuted on a true one)."""
    bad = []
    for r in rows:
        for v in VERIFIERS:
            if (r[v] == 'proved' and r['validator'] == 'false') or (r[v] == 'refuted' and r['validator'] == 'true'):
                bad.append({'name': r['name'], 'verifier': v, 'verdict': r[v], 'validator': r['validator']})
    return bad


# ------------------------------------------------------------------ mutant rebinding regression

def _disjunction_nodes(formula, target):
    """(Or-tree nodes of the gold step disjunction that contain `target`, all its Or-tree nodes)."""
    from ve.ast import Or
    nodes, every = [], []

    def walk(f):
        if f == target:
            return True
        if type(f) is Or:
            every.append(f)
            hit = walk(f.left) | walk(f.right)
            if hit:
                nodes.append(f)
            return hit
        return False
    walk(formula)
    return nodes, every


def rebind_regression(gold, desc, cert):
    from ve.entailment import (CLOSURE_CHECKER_VERSION, _binding, _initial_branch, _Replayer,
                               check_entailment_certificate)
    env, gp, gg = R.ve_env(), R.premises(gold), R.goal(gold)
    rebound = {**cert, **_binding(env, tuple(gp), gg)}
    chk = check_entailment_certificate(env, gp, gg, rebound, max_steps=2_000_000)
    binding_failure = any(s in chk.detail for s in ('bound to different inputs', 'wire schema'))
    failure = {}

    class Locate(_Replayer):
        def replay(self, branch, node, depth=0):
            try:
                super().replay(branch, node, depth)
            except Exception:
                if not failure:  # the deepest failing node is recorded first
                    failure.update(branch=branch, node=node if isinstance(node, dict) else {})
                raise
    located = None
    try:
        Locate(2_000_000, env.closure, env=env, induction=rebound['checker_version'] == CLOSURE_CHECKER_VERSION).replay(
            _initial_branch(env, tuple(gp), gg), rebound['trace'])
    except Exception:
        case = R.step_case(gold['rules'][desc['rule']])
        nodes, every = _disjunction_nodes(R.step_body(gold).formula, case)
        branch, node = failure['branch'], failure['node']
        strict = any(it.formula == case for it in branch.formulas)
        at = node.get('at')
        expanded = branch.formulas[at].formula if isinstance(at, int) and 0 <= at < len(branch.formulas) else None
        shape = expanded is not None and any(expanded == n for n in nodes)
        in_step = expanded is not None and any(expanded == n for n in every)
        cases = {R.step_case(r) for r in gold['rules']}
        any_case = any(it.formula in cases for it in branch.formulas)
        # Literal mutations: the failing branch must hold the gold's mutated case (or the failing split
        # is a disjunction node containing it). A dropped rule changes the SHAPE of the step
        # disjunction, so the mutant's case analysis no longer lines up with the gold's; there the
        # failure must be at a split of the step disjunction or on a branch holding one of its cases.
        dropped = desc['kind'] == 'dropped_inheritance'
        located = {'failing_rule': node.get('rule'), 'expanded_formula': type(expanded).__name__,
                   'branch_holds_mutated_case': strict, 'failing_expansion_is_disjunction_containing_it': shape,
                   'failing_expansion_in_step_disjunction': in_step, 'branch_holds_a_step_case': any_case,
                   'at_mutated_rule': bool(strict or shape or (dropped and (in_step or any_case)))}
    return {'python_valid': chk.valid, 'python_status': chk.status, 'python_detail': chk.detail[:160],
            'logical_failure': (not chk.valid) and chk.status == 'InvalidCertificate' and not binding_failure,
            'located': located, 'lean_valid': _lean(gold['id'] + '-rebound', env, gp, gg, rebound)}


# ------------------------------------------------------------------ run

def run():
    from . import z3check as Z
    t_start = time.time()
    attempts, selected, skipped = [], [], []
    attempt = 0
    while len(selected) < N_RULESETS:
        seed = R.SEED_BASE + attempt
        attempt += 1
        kind = R.MUTATIONS[len(selected) % len(R.MUTATIONS)]
        gold = R.generate(seed)
        cands = []
        for k in R.MUTATIONS:
            order = R.candidates(gold, k)
            random.Random(seed * 7 + R.MUTATIONS.index(k)).shuffle(order)
            cands.extend((k, i, d, m) for i, (d, m) in enumerate(order))
        # Selection by the validator only: the first (shuffled) validator-true candidate of the assigned type.
        choice = next(((i, d, m) for k, i, d, m in cands if k == kind and R.validate(m)['claim_true']), None)
        attempts.append({'seed': seed, 'gold': gold, 'candidates': cands, 'assigned': kind, 'chosen': choice})
        if choice is None:
            skipped.append({'seed': seed, 'reason': f'no validator-true {kind} mutant'})
        else:
            selected.append(len(attempts) - 1)
    print('attempts', attempt, 'selected', len(selected), flush=True)

    jobs = []
    for a in attempts:
        gid = a['gold']['id']
        jobs.append((f'{gid}-gold', a['gold'], True))
        jobs.extend((f'{gid}-{k}-{i}', m, True) for k, i, _, m in a['candidates'])
    rows, certs = {}, {}
    with multiprocessing.get_context('fork').Pool(9) as pool:
        for n, (row, cert) in enumerate(pool.imap_unordered(verify, jobs, chunksize=8)):
            rows[row['name']] = row
            if cert is not None and row['ve_python']:
                certs[row['name']] = cert
            if n % 1000 == 0:
                print('verified', n, '/', len(jobs), flush=True)
    gold_rows = [rows[f"{a['gold']['id']}-gold"] for a in attempts]
    cand_rows = [rows[f"{a['gold']['id']}-{k}-{i}"] for a in attempts for k, i, _, _ in a['candidates']]

    sel = []
    for idx in selected:
        a = attempts[idx]
        gold = a['gold']
        i, desc, mutant = a['chosen']
        gid = gold['id']
        mname = f"{gid}-{a['assigned']}-{i}"
        grow, mrow = rows[f'{gid}-gold'], rows[mname]
        dnf, _ = R.invariant_dnf(gold)
        forged = R.ve_certify_built(gold, dnf, forge=True)
        forged_row = {'forged_leaves': forged.get('forged_leaves'), 'python_valid': forged['python_replay_valid'],
                      'lean_valid': _lean(gid + '-forged', forged['env'], forged['premises'], forged['goal'],
                                          forged['certificate'])}
        rebind = rebind_regression(gold, desc, certs[mname]) if mrow['ve'] == 'proved' else None
        sel.append({'id': gid, 'seed': a['seed'], 'claim': gold['claim'], 'rules': len(gold['rules']),
                    'mutation': desc, 'mutant_name': mname, 'gold': grow, 'mutant': mrow,
                    'forged_gold_certificate': forged_row, 'mutant_rebound_to_gold': rebind,
                    'gold_ruleset': gold, 'mutant_ruleset': mutant})
        print(len(sel), gid, desc['kind'], mrow['ve'], rebind and rebind['logical_failure'],
              rebind and rebind['located'] and rebind['located']['at_mutated_rule'], flush=True)
    verification_seconds = round(time.time() - t_start, 1)

    from ve import prove_entailment
    generic = []
    for r in sel[:GENERIC_SEARCH['rulesets']]:
        m = r['mutant_ruleset']
        dnf, _ = R.invariant_dnf(m)
        t = time.time()
        res = prove_entailment(R.ve_env(), R.premises(m), R.goal(m), invariants=[R.invariant_formula(dnf)],
                               max_steps=GENERIC_SEARCH['max_steps'])
        generic.append({'id': r['id'], 'status': res.status, 'steps': res.steps, 'seconds': round(time.time() - t, 1)})

    snaps = []
    for i in range(N_SNAPSHOTS):
        s = R.generate_snapshot(R.SNAP_SEED + i)
        facts = [tuple(f) for f in s['facts']]
        tags = {k: set(v) for k, v in s['tags'].items()}
        no_negated = [{**r, 'src': [l for l in r['src'] if l[1]], 'dst': [l for l in r['dst'] if l[1]]}
                      for r in R.SNAP_RULES]
        try:
            row = R.certify_snapshot(s)
        except R.OpenBranch as e:
            row = {'id': s['id'], 'python_replay_valid': False, 'lean_replay_valid': False, 'failure': str(e)}
        row['negated_guard_essential'] = s['resource'] in R._snap_reach(facts, tags, no_negated, s['principal'])
        row['forged_negation_flip'] = R.forged_snapshot(s)
        snaps.append(row)

    sel_true, sel_false = [r['mutant'] for r in sel], [r['gold'] for r in sel]
    rebinds = [(r['mutation']['kind'], r['mutant_rebound_to_gold']) for r in sel if r['mutant_rebound_to_gold']]
    at_rule = lambda rb: bool(rb['located'] and rb['located']['at_mutated_rule'])

    def timing(rs, key):
        xs = sorted(r[key] for r in rs)
        return {'median': xs[len(xs) // 2], 'max': xs[-1]}
    all_rows = list(rows.values())
    summary = {
        'attempts': attempt, 'selected_rule_sets': len(sel), 'skipped': len(skipped),
        'claims_evaluated': len(rows), 'selection': 'independent validator only (no solver in the selection)',
        'selected_60': tally(sel_true + sel_false),
        'all_attempted_gold_claims': tally(gold_rows),
        'all_mutation_candidates': tally(cand_rows),
        'all_claims': tally(all_rows),
        'disagreements_with_validator': disagreements(all_rows),
        've_python_valid_but_lean_invalid': sum(r['ve_python'] and r['ve_lean'] is False for r in all_rows),
        've_python_valid_lean_not_run': sum(r['ve_python'] and r['ve_lean'] is None for r in all_rows),
        'witness_bfs_confirms_every_false_claim': all(r.get('witness_bfs_violation') for r in all_rows
                                                      if r['validator'] == 'false'),
        'forged_gold_certificates_rejected': {
            'python': sum(not r['forged_gold_certificate']['python_valid'] for r in sel),
            'lean': sum(r['forged_gold_certificate']['lean_valid'] is False for r in sel), 'of': len(sel)},
        'mutant_rebound_to_gold': {
            'checked': len(rebinds),
            'python_rejected': sum(not rb['python_valid'] for _, rb in rebinds),
            'python_logical_failure_not_binding': sum(rb['logical_failure'] for _, rb in rebinds),
            'python_failure_at_mutated_rule': sum(at_rule(rb) for _, rb in rebinds),
            'lean_rejected': sum(rb['lean_valid'] is False for _, rb in rebinds),
            'by_mutation': {k: {'n': sum(kk == k for kk, _ in rebinds),
                                'at_mutated_rule': sum(at_rule(rb) for kk, rb in rebinds if kk == k)}
                            for k in R.MUTATIONS}},
        'mutation_types_selected': dict(Counter(r['mutation']['kind'] for r in sel)),
        'candidate_acceptance_by_validator': {
            k: {'candidates': sum(1 for a in attempts for kk, *_ in a['candidates'] if kk == k),
                'validator_true': sum(rows[f"{a['gold']['id']}-{kk}-{i}"]['validator'] == 'true'
                                      for a in attempts for kk, i, _, _ in a['candidates'] if kk == k)}
            for k in R.MUTATIONS},
        'seconds_end_to_end_selected_true_claims': {v: timing(sel_true, f'{v}_seconds') for v in VERIFIERS},
        've_replay_steps_max': max((r.get('ve_replay_steps', 0) for r in all_rows if r['ve_python']), default=0),
        've_trace_depth_max': max((r.get('ve_trace_depth', 0) for r in all_rows if r['ve_python']), default=0),
        'verification_seconds': verification_seconds,
        'generic_prove_entailment': generic,
        'closed_world_unless': {
            'snapshots': len(snaps),
            'certified_python_and_lean': sum(bool(s['python_replay_valid']) and s.get('lean_replay_valid') is not False
                                             for s in snaps),
            'negated_guard_essential': sum(s['negated_guard_essential'] for s in snaps),
            'forged_negation_flip_rejected': sum(1 for s in snaps if s['forged_negation_flip']
                                                 and not s['forged_negation_flip']['python_replay_valid']),
            'forged_negation_flip_constructed': sum(1 for s in snaps if s['forged_negation_flip'])},
    }
    result = {'created_at': datetime.now(timezone.utc).isoformat(), 'model_calls': 0,
              'solvers': {'z3': Z.Z3_VERSION, 'cvc5': Z.CVC5_VERSION, 'project': 'experiments/T1d/solvers (uv.lock)'},
              've_commit': ve_commit(), 'seed_base': R.SEED_BASE, 'snapshot_seed': R.SNAP_SEED,
              'summary': summary, 'skipped': skipped, 'selected': sel, 'snapshots': snaps,
              'claims_file': CLAIMS.name}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=1, sort_keys=True, default=list) + '\n')
    with gzip.open(CLAIMS, 'wt') as f:  # every claim row (the candidate-level log), one JSON per line
        for r in sorted(all_rows, key=lambda r: r['name']):
            f.write(json.dumps(r, sort_keys=True) + '\n')
    print(json.dumps({k: v for k, v in summary.items() if k != 'generic_prove_entailment'}, indent=1, default=list))
    return result


def ve_commit():
    """The last commit that touched ve/ (the checker used), its tree hash, and whether ve/ is clean."""
    git = lambda *a: subprocess.run(['git', *a], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    return {'last_commit_touching_ve': git('log', '-1', '--format=%H', '--', 've'),
            've_tree': git('rev-parse', 'HEAD:ve'), 've_dirty': bool(git('status', '--porcelain', '--', 've'))}


if __name__ == '__main__':
    run()
