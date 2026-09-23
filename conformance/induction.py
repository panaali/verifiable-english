"""Untrusted induction examples and certificate construction.

The small explicit T9e schedule avoids adding a new composition/rebinding rule.
Every generated node is replayed independently by Python and Lean.
"""
import json
import runpy
from pathlib import Path

from ve.ast import (And, Binary, Body, Const, Eq, Exists, Forall, Implies, Named,
                    Not, Reach, Unary, Var, _to_data)
from ve.closure import (InductionInvariant, derive_induction, induction_candidates,
                        induction_step, invariant_at)
from ve.entailment import (_Searcher, _apply, _binding, _closed, _derive,
                           _initial_branch, _rule, check_entailment_certificate,
                           prove_entailment)

ROOT = Path(__file__).resolve().parents[1]


class Builder:
    def __init__(self, branch, node=None):
        self.branch = branch
        self.node = {} if node is None else node

    def expand(self, at=None, parameter=None):
        at = len(self.branch.formulas) - 1 if at is None else at
        alternatives = _derive(self.branch, at, parameter)
        children = [{} for _ in alternatives]
        self.node.update(rule=_rule(self.branch.formulas[at]), at=at, children=children)
        if parameter is not None:
            self.node['parameter'] = parameter
        return [Builder(_apply(self.branch, at, parameter, xs), node)
                for xs, node in zip(alternatives, children, strict=True)]

    def extra(self, rule, at, parameter=None):
        from ve.closure import derive_extra
        branch = self.branch.copy()
        branch.formulas.extend(derive_extra(branch, rule, at, parameter))
        child = {}
        self.node.update(rule=rule, at=at, children=[child])
        if parameter is not None:
            self.node['parameter'] = parameter
        return Builder(branch, child)

    def induct(self, env, at, sort, invariant):
        children = [{}, {}, {}]
        self.node.update(rule='closure-induct@1', at=at, sort=sort,
                         invariant=_to_data(invariant), children=children)
        result = []
        for xs, node in zip(derive_induction(env, self.branch, at, sort, invariant), children, strict=True):
            branch = self.branch.copy()
            branch.formulas.extend(xs)
            result.append(Builder(branch, node))
        return result

    def close(self):
        assert _closed(self.branch)
        self.node.update(rule='close')

    def solve(self):
        trace = _Searcher(1000, True, focused=True).prove(self.branch)
        assert trace is not None
        self.node.update(trace)


def transitivity(relation='s', sort='point'):
    r = lambda i, j: Reach('plus', Named(relation), Var(i), Var(j))
    return Forall(sort, Forall(sort, Forall(sort,
        Implies(And(r(2, 1), r(1, 0)), r(2, 0)))))


def prove_transitivity(builder):
    """The final formula is negative transitivity; use the old composition rule."""
    for _ in range(4):
        builder = builder.expand()[0]
    builder = builder.expand(len(builder.branch.formulas) - 2)[0]
    at = len(builder.branch.formulas) - 2
    builder.extra('closure-compose@0', at, str(at + 1)).close()


def math_cases():
    from conformance.certificates import envelope
    theory = runpy.run_path(str(ROOT / 'usecases/math-mini-paper/theory.py'))
    cases = []
    for spec in theory['THEOREMS']:
        name = spec['id']
        if name not in ('T9', 'T9e'):
            continue
        env, ps, goal = spec['env'], [f for _, f in spec['premises']], spec['goal']
        if name == 'T9':
            result = prove_entailment(env, ps, goal, max_steps=3000,
                invariants=[InductionInvariant(Binary('s', Var(1), Var(0)), ('w:0',))])
            assert result.certificate, result
            cert = result.certificate
        else:
            root = Builder(_initial_branch(env, tuple(ps), goal))
            b = root
            for _ in range(3):
                b = b.expand()[0]
            b = b.expand(len(b.branch.formulas) - 2)[0]
            direct, tail = b.expand()
            direct.solve()
            tail = tail.expand()[0].expand()[0]
            hint = InductionInvariant(And(Reach('plus', Named('s'), Var(1), Var(0)),
                                           transitivity()), ('w:0',))
            at = len(tail.branch.formulas) - 1
            _, sort, invariant, _ = next(c for c in induction_candidates(env, tail.branch, [hint])
                                         if c[0] == at)
            base, step, continuation = tail.induct(env, at, sort, invariant)
            path_base, trans_base = base.expand()
            path_base.solve()
            prove_transitivity(trans_base)
            # Preservation: open the two fresh variables a,b and P(a) & r(a,b).
            for _ in range(3):
                step = step.expand()[0]
            negative_target = len(step.branch.formulas) - 1
            step = step.expand(negative_target - 1)[0]
            step = step.expand(len(step.branch.formulas) - 2)[0]
            trans_at = len(step.branch.formulas) - 1
            path_step, trans_step = step.expand(negative_target)
            prove_transitivity(trans_step)
            # Inclusion instantiated at the freshly generated a,b.
            a, b = f'w:{path_step.branch.next_witness - 2}', f'w:{path_step.branch.next_witness - 1}'
            path_step = path_step.expand(0, a)[0].expand(parameter=b)[0]
            no_edge, s_edge = path_step.expand()
            no_edge.close()
            s_edge = s_edge.extra('closure-edge@0', len(s_edge.branch.formulas) - 1)
            # Use the transitivity conjunct of P(a) at x,a,b.
            s_edge = s_edge.expand(trans_at, 'w:0')[0].expand(parameter=a)[0].expand(parameter=b)[0]
            no_pair, path = s_edge.expand()
            for child in no_pair.expand():
                child.close()
            path.close()
            continuation.expand()[0].close()
            cert = {**_binding(env, tuple(ps), goal), 'trace': root.node}
        checked = check_entailment_certificate(env, ps, goal, cert)
        assert checked.valid, checked
        cases.append(envelope(name + '_induction', env, ps, goal, cert))
    return cases


def policy_cases():
    from conformance.certificates import envelope
    from ve.environment import Environment
    env = Environment({
        'language': 've.core@0.1', 'profiles': ['closure@0', 'relational-fol@0'],
        'spec_revision': 've-v0.1-closure-2026-09-21',
        'vocabulary': {
            'sorts': {'entity': {'description': 'Group or resource'}},
            'constants': {c: {'sort': 'entity', 'description': c} for c in ('g1', 'g2', 'resource')},
            'predicates': {'group': {'arguments': ['entity'], 'description': 'Member of group G'},
                           'link': {'arguments': ['entity', 'entity'], 'description': 'Nesting or access edge'}}}})
    p, edge = Unary('group', Var(0)), Named('link')
    ps = [Unary('group', Const('g1')), Unary('group', Const('g2')),
          Binary('link', Const('g1'), Const('g2')), Binary('link', Const('g2'), Const('g1')),
          induction_step('entity', edge, p), Not(Unary('group', Const('resource')))]
    cases = []
    for kind in ('plus', 'star'):
        goal = Forall('entity', Implies(p, Not(Reach(kind, edge, Var(0), Const('resource')))))
        proof = prove_entailment(env, ps, goal, invariants=[p], max_steps=3000)
        assert proof.certificate, proof
        cases.append(envelope('policy_cyclic_' + kind, env, ps, goal, proof.certificate))
    return cases


def schema_cases():
    """Exercise both binder depths, polarities inside P, and captured parameters."""
    from conformance.certificates import envelope
    from conformance.closure_certificates import environment
    env = environment()
    a, b = Const('a'), Const('b')
    edges = [Named('rel'), Body('item', Binary('rel', Var(1), Var(0))),
             Body('item', Reach('star', Body('item', Binary('rel', Var(1), Var(0))), Var(1), Var(0)))]
    invariants = [Unary('p', Var(0)), Not(Unary('p', Var(0))), Eq(Var(0), a),
                  Forall('item', Implies(Binary('rel', Var(1), Var(0)), Unary('p', Var(0)))),
                  Reach('star', Body('item', And(Binary('rel', Var(1), Var(0)),
                        Not(Eq(Var(0), Var(2))))), a, Var(0))]
    cases = []
    for ei, edge in enumerate(edges):
        for pi, p in enumerate(invariants):
            for kind in ('plus', 'star'):
                ps = [Reach(kind, edge, a, b), invariant_at(p, a), induction_step('item', edge, p)]
                goal = invariant_at(p, b)
                trace = {'rule': 'closure-induct@1', 'at': 0, 'sort': 'item',
                         'invariant': _to_data(p), 'children': [{'rule': 'close'}] * 3}
                cert = {**_binding(env, tuple(ps), goal), 'trace': trace}
                cases.append(envelope(f'induction_schema_{ei}_{pi}_{kind}', env, ps, goal, cert))
    # A captured variable passes the invariant binder, forall/exists, and nested
    # Body binders. A single existential supplies the ambient parameter.
    for kind in ('plus', 'star'):
        edge = Body('item', And(Binary('rel', Var(1), Var(0)), Not(Eq(Var(0), Var(2)))))
        p = Exists('item', And(Eq(Var(0), Var(2)), Reach('star',
            Body('item', And(Binary('rel', Var(1), Var(0)), Eq(Var(3), Var(4)))), Var(1), Var(0))))
        parts = [Reach(kind, edge, a, b), invariant_at(p, a), induction_step('item', edge, p)]
        antecedent = And(parts[0], And(parts[1], parts[2]))
        goal = Forall('item', Implies(antecedent, invariant_at(p, b)))
        root = Builder(_initial_branch(env, (), goal))
        node = root.expand()[0].expand()[0]
        node = node.expand(len(node.branch.formulas) - 2)[0]
        at = len(node.branch.formulas) - 2
        node = node.expand()[0]
        for child in node.induct(env, at, 'item', p):
            child.close()
        cases.append(envelope('induction_captured_' + kind, env, [], goal,
                              {**_binding(env, (), goal), 'trace': root.node}))
    return cases


def positive_cases():
    from conformance.certificates import replay_python
    cases = schema_cases() + math_cases() + policy_cases()
    for case in cases:
        assert replay_python(case), case['id']
    return cases


def forged_cases():
    import copy
    from conformance.certificates import replay_python
    base = schema_cases()[0]
    mutations = {
        'old_version': lambda c: c['certificate'].update(checker_version='ve-tableau-closure-checker@0'),
        'unknown_version': lambda c: c['certificate'].update(checker_version='ve-tableau-closure-checker@2'),
        'wrong_index': lambda c: c['certificate']['trace'].update(at=2),
        'bool_index': lambda c: c['certificate']['trace'].update(at=True),
        'missing_branch': lambda c: c['certificate']['trace'].update(children=[{'rule': 'close'}] * 2),
        'extra_branch': lambda c: c['certificate']['trace'].update(children=[{'rule': 'close'}] * 4),
        'extra_field': lambda c: c['certificate']['trace'].update(parameter='w:0'),
        'wrong_sort': lambda c: c['certificate']['trace'].update(sort='place'),
        'unknown_sort': lambda c: c['certificate']['trace'].update(sort='absent'),
        'free_variable': lambda c: c['certificate']['trace'].update(invariant=['unary', 'p', ['var', 1]]),
        'unknown_predicate': lambda c: c['certificate']['trace'].update(invariant=['unary', 'absent', ['var', 0]]),
        'changed_invariant': lambda c: c['certificate']['trace'].update(invariant=['not', c['certificate']['trace']['invariant']]),
        'false_invariant': lambda c: c['certificate']['trace'].update(invariant=['bottom']),
        'true_invariant': lambda c: c['certificate']['trace'].update(invariant=['top']),
    }
    cases = []
    for name, mutate in mutations.items():
        case = copy.deepcopy(base)
        case['id'] = 'induction_forged_' + name
        mutate(case)
        cases.append(case)
    # Rebind identities after changing assumptions: these must fail logically,
    # not merely because a commitment became stale.
    from ve.ast import formula_from_data
    from ve.environment import Environment
    from conformance.certificates import envelope
    env = Environment(base['environment'])
    ps = [formula_from_data(env, f) for f in base['premises']]
    goal = formula_from_data(env, base['conclusion'])
    from ve.ast import Top
    for name, changed in [('no_base', [ps[0], Top(), ps[2]]),
                          ('no_step', [ps[0], ps[1], Top()]),
                          ('negative_path', [Not(ps[0]), ps[1], ps[2]])]:
        cert = {**_binding(env, tuple(changed), goal), 'trace': copy.deepcopy(base['certificate']['trace'])}
        cases.append(envelope('induction_forged_' + name, env, changed, goal, cert))
    for case in cases:
        assert not replay_python(case), case['id']
    return cases


if __name__ == '__main__':
    from conformance.certificates import invoke
    good, bad = positive_cases(), forged_cases()
    rows = invoke(ROOT / 'lean/.lake/build/bin/ve_conformance', good + bad)
    assert [r['valid'] for r in rows] == [True] * len(good) + [False] * len(bad), rows
    print(json.dumps({'python_accepted': len(good), 'lean_accepted': len(good),
                      'python_rejected': len(bad), 'lean_rejected': len(bad)}, indent=2))
