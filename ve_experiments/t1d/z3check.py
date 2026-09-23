"""T1d Part 2 non-VE verifiers for universal rule-level claims (Z3 and cvc5; offline).

Run in the separately locked solver project (z3-solver 5.1.0.0, cvc5 1.4.0; hashes in
experiments/T1d/solvers/uv.lock):

    PYTHONPATH=. uv run --project experiments/T1d/solvers --locked python -m ve_experiments.t1d.part2

* `chc_verdict` (competent decider): constrained Horn clauses solved by Z3's Spacer engine. The
  unknown is Reach1(t), "some entity of tag vector t is reachable in >= 1 steps from a T1 entity",
  over one Boolean per tag. Tag axioms, relation typing, admin constraints and rule guards become
  clause bodies. The query Reach1(t) and T2(t) is unsat exactly when the claim holds (the
  tag-vector abstraction is exact; see rules.py). Verdicts: proved / refuted / unknown.
* `ground_check` (the reviewers' competent baseline for the SAME invariant VE uses): three ground
  propositional queries over two tag vectors s, d, solved by Z3 or by cvc5:
    initiation   valid(s) & T1(s) & valid(d) & step(s, d) & ~Inv(d)   unsat
    consecution  valid(s) & Inv(s) & valid(d) & step(s, d) & ~Inv(d)  unsat
    safety       valid(d) & Inv(d) & T2(d)                            unsat
  All unsat: proved. Any sat: the invariant fails (verdict unknown; this check never refutes).
  Like CHC, it relies on the tag-vector abstraction; VE's certificate does not (its premises are
  first-order formulas over entities, replayed by a Lean-proved checker).
The v2 direct FOL + TransitiveClosure encoding is dropped: it is a strawman next to these two.
Solvers are imported lazily; the rest of T1d runs without them.
"""
from __future__ import annotations

import time

from .rules import ATTRIBUTES, EXCLUSIVE, KINDS, RELATIONS, TAGS

Z3_VERSION = '5.1.0.0'
CVC5_VERSION = '1.4.0'


def _z3():
    import z3
    return z3


def _cvc5():
    from cvc5 import pythonic
    return pythonic


def _type_constraints(z3, v):
    kinds = [v[k] for k in KINDS]
    parts = [z3.Or(*kinds)] + [z3.Not(z3.And(a, b)) for i, a in enumerate(kinds) for b in kinds[i + 1:]]
    parts += [z3.Implies(v[a], v[k]) for a, k in ATTRIBUTES.items()]
    parts += [z3.Not(z3.And(v[a], v[b])) for a, b in EXCLUSIVE]
    return z3.And(*parts)


def _lit(z3, lit, v):
    tag, pos = lit
    return v[tag] if pos else z3.Not(v[tag])


def _edge(z3, rs, s, d):
    cases = []
    for rule in rs['rules']:
        rel = rule['relation']
        src_k, dst_k, _ = RELATIONS[rel]
        typing = [z3.Or(*[s[k] for k in src_k]), z3.Or(*[d[k] for k in dst_k])]
        forbidden = [z3.Not(z3.And(_lit(z3, c['src'], s), _lit(z3, c['dst'], d)))
                     for c in rs['constraints'] if c['relation'] == rel]
        guards = [_lit(z3, l, s) for l in rule['src']] + [_lit(z3, l, d) for l in rule['dst']]
        cases.append(z3.And(*(typing + forbidden + guards)))
    return z3.Or(*cases) if cases else z3.BoolVal(False)


def chc_verdict(rs, timeout_ms=20000):
    """True (claim holds), False (violation reachable) or None (unknown)."""
    z3 = _z3()
    fp = z3.Fixedpoint()
    fp.set(engine='spacer')
    fp.set('timeout', timeout_ms)
    B = z3.BoolSort()
    reach = z3.Function('reach1', *([B] * len(TAGS)), B)
    s = {t: z3.Bool('s_' + t) for t in TAGS}
    d = {t: z3.Bool('d_' + t) for t in TAGS}
    fp.register_relation(reach)
    fp.declare_var(*s.values(), *d.values())
    t1, t2 = rs['claim']
    step = z3.And(_type_constraints(z3, s), _type_constraints(z3, d), _edge(z3, rs, s, d))
    fp.rule(reach(*[d[t] for t in TAGS]), [s[t1], step])
    fp.rule(reach(*[d[t] for t in TAGS]), [reach(*[s[t] for t in TAGS]), step])
    result = fp.query(z3.And(reach(*[d[t] for t in TAGS]), d[t2]))
    if result == z3.unsat:
        return True
    if result == z3.sat:
        return False
    return None


def _inv(S, dnf, v):
    cubes = [S.And(*[_lit(S, l, v) for l in cube]) if len(cube) > 1 else
             (_lit(S, cube[0], v) if cube else S.BoolVal(True)) for cube in dnf]
    return S.Or(*cubes) if len(cubes) > 1 else (cubes[0] if cubes else S.BoolVal(False))


def ground_check(rs, dnf, solver='z3', timeout_ms=20000):
    """Ground inductiveness of the DNF invariant; returns {'verdict': 'proved'|'unknown', ...}."""
    S = _z3() if solver == 'z3' else _cvc5()
    t0 = time.time()
    s = {t: S.Bool('s_' + t) for t in TAGS}
    d = {t: S.Bool('d_' + t) for t in TAGS}
    t1, t2 = rs['claim']
    valid_s, valid_d = _type_constraints(S, s), _type_constraints(S, d)
    step = _edge(S, rs, s, d)
    inv_s, inv_d = _inv(S, dnf, s), _inv(S, dnf, d)
    queries = {'initiation': [valid_s, s[t1], valid_d, step, S.Not(inv_d)],
               'consecution': [valid_s, inv_s, valid_d, step, S.Not(inv_d)],
               'safety': [valid_d, inv_d, d[t2]]}
    results = {}
    for name, parts in queries.items():
        sv = S.Solver()
        if solver == 'z3':
            sv.set('timeout', timeout_ms)
        sv.add(*parts)
        r = sv.check()
        results[name] = 'unsat' if r == S.unsat else ('sat' if r == S.sat else 'unknown')
    verdict = 'proved' if all(v == 'unsat' for v in results.values()) else 'unknown'
    return {'verdict': verdict, 'queries': results, 'seconds': round(time.time() - t0, 4)}
