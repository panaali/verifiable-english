"""T1d Part 2 baseline: a competent non-VE verifier for universal rule-level claims (Z3).

Two encodings, neither using VE:
* `chc_verdict` (primary): constrained Horn clauses solved by Z3's Spacer engine. The unknown
  is Reach1(t), "some entity of tag vector t is reachable in >= 1 steps from a T1 entity", over
  one Boolean per tag. Tag axioms, relation typing, admin constraints and rule guards become
  clause bodies. The query Reach1(t) and T2(t) is unsat exactly when the claim holds (the
  tag-vector abstraction is exact; see rules.py).
* `fol_verdict` (secondary): a direct first-order encoding over an uninterpreted sort with Z3's
  TransitiveClosure of a defined step relation, asking for a counterexample state. Quantified
  axioms plus transitive closure are outside a decidable fragment, so `unknown` is expected and
  reported.
Import z3 lazily: the rest of T1d runs without it (`uv run --with z3-solver==5.1.0.0 ...`).
"""
from __future__ import annotations

from .rules import ATTRIBUTES, EXCLUSIVE, KINDS, RELATIONS, TAGS

Z3_VERSION = '5.1.0.0'


def _z3():
    import z3
    return z3


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


def fol_verdict(rs, timeout_ms=5000):
    """Direct FOL + TransitiveClosure counterexample search: True/False/None (unknown)."""
    z3 = _z3()
    N = z3.DeclareSort('Entity')
    B = z3.BoolSort()
    tag = {t: z3.Function(t, N, B) for t in TAGS}
    rel = {r: z3.Function(r, N, N, B) for r in RELATIONS}
    step = z3.Function('step', N, N, B)
    tc = z3.TransitiveClosure(step)
    a, b = z3.Consts('a b', N)
    solver = z3.Solver()
    solver.set('timeout', timeout_ms)
    va = {t: tag[t](a) for t in TAGS}
    vb = {t: tag[t](b) for t in TAGS}
    solver.add(z3.ForAll([a], _type_constraints(z3, va)))
    for r, (sk, dk, _) in RELATIONS.items():
        solver.add(z3.ForAll([a, b], z3.Implies(rel[r](a, b), z3.And(z3.Or(*[va[k] for k in sk]),
                                                                     z3.Or(*[vb[k] for k in dk])))))
    for c in rs['constraints']:
        solver.add(z3.ForAll([a, b], z3.Implies(rel[c['relation']](a, b),
                                                z3.Not(z3.And(_lit(z3, c['src'], va), _lit(z3, c['dst'], vb))))))
    cases = [z3.And(rel[r['relation']](a, b), *[_lit(z3, l, va) for l in r['src']],
                    *[_lit(z3, l, vb) for l in r['dst']]) for r in rs['rules']]
    solver.add(z3.ForAll([a, b], step(a, b) == (z3.Or(*cases) if cases else z3.BoolVal(False))))
    u, x = z3.Consts('u x', N)
    t1, t2 = rs['claim']
    solver.add(tag[t1](u), tag[t2](x), tc(u, x))
    result = solver.check()
    if result == z3.unsat:
        return True
    if result == z3.sat:
        return False
    return None
