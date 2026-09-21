"""Deterministic closure certificates, hostile mutations and retained search gaps."""
import copy

from ve.ast import (And, Binary, Body, Bottom, Const, Eq, Exists, Forall, Implies,
                    Named, Not, Or, Reach, Top, Unary, Var)
from ve.closure import unfold
from ve.entailment import _binding, check_entailment_certificate, prove_entailment
from ve.environment import Environment


def environment():
    from conformance.certificates import environment as base
    raw = base().to_dict()
    raw.pop('profile')
    raw.update(language='ve.core@0.1', profiles=['closure@0', 'relational-fol@0'],
               spec_revision='ve-v0.1-closure-2026-09-21')
    raw['vocabulary']['predicates']['other'] = {'arguments': ['item', 'item'], 'description': 'Other'}
    return Environment(raw)


def reviewer_queries():
    env = environment()
    a, b, c = map(Const, ('a', 'b', 'c'))
    edge = Named('rel')
    reach = lambda x, y: Reach('plus', edge, x, y)
    inclusion = Forall('item', Forall('item', Implies(Binary('rel', Var(1), Var(0)),
                                                     Binary('other', Var(1), Var(0)))))
    symmetric = Forall('item', Forall('item', Implies(Binary('rel', Var(1), Var(0)),
                                                     Binary('rel', Var(0), Var(1)))))
    body = Reach('plus', Body('item', Binary('rel', Var(1), Var(0))), a, b)
    return env, {
        'transitivity': ([reach(a, b), reach(b, c)], reach(a, c)),
        'monotonicity': ([inclusion, reach(a, b)], Reach('plus', Named('other'), a, b)),
        'named_body': ([reach(a, b)], body),
        'body_named': ([body], reach(a, b)),
        'last_edge': ([reach(a, b)], Exists('item', Binary('rel', Var(0), b))),
        'first_edge': ([reach(a, b)], Exists('item', Binary('rel', a, Var(0)))),
        'symmetric_reversal': ([symmetric, reach(a, b)], reach(b, a)),
    }


def positive_cases():
    from conformance.certificates import envelope, replay_python
    env, queries = reviewer_queries()
    cases, outcomes = [], {}
    for name, (ps, goal) in queries.items():
        result = prove_entailment(env, ps, goal, max_steps=400)
        outcomes[name] = {'status': result.status, 'steps': result.steps}
        if name not in ('monotonicity', 'symmetric_reversal'):
            assert result.status == 'Found', (name, result)
        if result.certificate:
            cases.append(envelope('closure_review_' + name, env, ps, goal, result.certificate))
    a, b, c = map(Const, ('a', 'b', 'c'))
    for name, ps, goal in [
        ('three_paths', [Reach('plus', Named('rel'), a, b), Reach('plus', Named('rel'), b, c),
                         Reach('plus', Named('rel'), c, Const('d'))], Reach('plus', Named('rel'), a, Const('d'))),
        ('edge_star', [Binary('rel', a, b)], Reach('star', Named('rel'), a, b)),
        ('two_edges', [Binary('rel', a, b), Binary('rel', b, c)], Reach('plus', Named('rel'), a, c)),
    ]:
        proof = prove_entailment(env, ps, goal, max_steps=100)
        assert proof.status == 'Found', (name, proof)
        cases.append(envelope('closure_' + name, env, ps, goal, proof.certificate))
    edges = [Named('rel'), Body('item', Binary('rel', Var(1), Var(0))),
             Body('item', And(Binary('rel', Var(1), Var(0)), Not(Eq(Var(0), a)))),
             Body('item', Reach('star', Body('item', Binary('rel', Var(1), Var(0))), Var(1), Var(0)))]
    for ei, edge in enumerate(edges):
        for kind in ('plus', 'star'):
            f = Reach(kind, edge, a, b)
            g = unfold(f, 'item')
            for positive in (False, True):
                ps, goal = ([f], g) if positive else ([g], f)
                cert = {**_binding(env, tuple(ps), goal), 'trace': {
                    'rule': f'closure-{kind}@0', 'at': 0 if positive else 1,
                    'children': [{'rule': 'close'}]}}
                cases.append(envelope(f'closure_unfold_{ei}_{kind}_{positive}', env, ps, goal, cert))
            for kind2 in ('plus', 'star'):
                ps = [f, Reach(kind2, edge, b, c)]
                result_kind = 'star' if kind == kind2 == 'star' else 'plus'
                goal = Reach(result_kind, edge, a, c)
                proof = prove_entailment(env, ps, goal, max_steps=100)
                assert proof.status == 'Found', proof
                cases.append(envelope(f'closure_compose_{ei}_{kind}_{kind2}', env, ps, goal, proof.certificate))
        for last in (False, True):
            from ve.closure import edge_at, shift
            f = Reach('plus', edge, a, b)
            sf = shift(f)
            goal = Exists('item', edge_at(sf.edge, Var(0), sf.right) if last else edge_at(sf.edge, sf.left, Var(0)))
            proof = prove_entailment(env, [f], goal, max_steps=100)
            assert proof.status == 'Found', proof
            cases.append(envelope(f'closure_end_{ei}_{last}', env, [f], goal, proof.certificate))
    # Captured outer variables survive quantifiers AND nested two-local binders.
    for kind in ('plus', 'star'):
        for nested in (False, True):
            edge = Body('item', And(Binary('rel', Var(1), Var(0)), Not(Eq(Var(0), Var(2)))))
            if nested:
                edge = Body('item', Reach('star', edge, Var(1), Var(0)))
            f = Reach(kind, edge, Var(0), b)
            g = unfold(f, 'item')
            for positive in (False, True):
                left, right = (f, g) if positive else (g, f)
                ps, goal = [Exists('item', And(left, Not(right)))], Bottom()
                trace = {'rule': f'closure-{kind}@0', 'at': 3 if positive else 5,
                         'children': [{'rule': 'close'}]}
                for at in (4, 2, 0):
                    trace = {'rule': 'expand', 'at': at, 'children': [trace]}
                cert = {**_binding(env, tuple(ps), goal), 'trace': trace}
                cases.append(envelope(f'closure_captured_{kind}_{nested}_{positive}', env, ps, goal, cert))
    # Equality acts on constants, captured variables and both endpoints, but not local indices.
    for kind in ('plus', 'star'):
        f = Reach(kind, Body('item', And(Binary('rel', Var(1), Var(0)), Not(Eq(Var(0), a)))), a, b)
        g = Reach(kind, Body('item', And(Binary('rel', Var(1), Var(0)), Not(Eq(Var(0), b)))), b, a)
        ps = [Eq(a, b), f]
        cert = {**_binding(env, tuple(ps), g), 'trace': {'rule': 'close'}}
        cases.append(envelope('closure_congruence_' + kind, env, ps, g, cert))
    for kind in ('plus', 'star'):
        for nested in (False, True):
            def body(captured):
                f = And(Binary('rel', Var(1), Var(0)), Not(Eq(Var(0), captured)))
                if nested:
                    # Here captured is a local of the enclosing Body and stays local.
                    f = Reach('star', Body('item', f), Var(1), Var(0))
                return Body('item', f)
            p = Forall('item', Reach(kind, body(Var(2)), Var(0), b))
            g = Reach(kind, body(b), b, a)
            if nested:
                # The actual outer capture passes both nested Body binders.
                p = Forall('item', Reach(kind, Body('item', Reach('star',
                    Body('item', And(Binary('rel', Var(1), Var(0)), Not(Eq(Var(0), Var(4))))),
                    Var(1), Var(0))), Var(0), b))
                g = Reach(kind, Body('item', Reach('star',
                    Body('item', And(Binary('rel', Var(1), Var(0)), Not(Eq(Var(0), b)))),
                    Var(1), Var(0))), b, a)
            ps = [Eq(a, b), p]
            cert = {**_binding(env, tuple(ps), g), 'trace': {'rule': 'expand', 'at': 1,
                'parameter': 'c:a', 'children': [{'rule': 'close'}]}}
            cases.append(envelope(f'closure_bound_congruence_{kind}_{nested}', env, ps, g, cert))
    # Empty-sort universals need no witness, and star adds no inhabitant.
    raw = env.to_dict(); raw['vocabulary']['constants'] = {}
    empty = Environment(raw)
    goal = Forall('item', Reach('star', Named('rel'), Var(0), Var(0)))
    proof = prove_entailment(empty, [], goal, max_steps=50)
    assert proof.status == 'Found', proof
    cases.append(envelope('closure_empty_sort_universal', empty, [], goal, proof.certificate))
    for case in cases:
        assert replay_python(case), case['id']
    return cases, outcomes


def forged_cases(positive):
    from conformance.certificates import envelope, replay_python
    cases = []
    for base in positive:
        mutations = {
            'version': lambda c: c['certificate'].update(checker_version='ve-tableau-checker@2'),
            'identity': lambda c: c['certificate'].update(environment_id='0' * 64),
            'rule': lambda c: c['certificate']['trace'].update(rule='induction'),
        }
        if base['certificate']['trace']['rule'] != 'close':
            mutations.update({
                'index': lambda c: c['certificate']['trace'].update(at=999999),
                'branches': lambda c: c['certificate']['trace'].update(children=[]),
                'parameter': lambda c: c['certificate']['trace'].update(parameter='w:0'),
            })
        if base['premises']:
            mutations['sign'] = lambda c: c.update(premises=[['not', p] for p in c['premises']])
        for name, mutate in mutations.items():
            case = copy.deepcopy(base)
            case['id'] += '_forged_' + name
            mutate(case)
            assert not replay_python(case), case['id']
            cases.append(case)
    env = environment()
    a, b, c = map(Const, ('a', 'b', 'c'))
    R = lambda k, x, y: Reach(k, Named('rel'), x, y)
    attacks = [
        ('star_last', [R('star', a, b)], Exists('item', Binary('rel', Var(0), b)), 'closure-last@0', None),
        ('star_first', [R('star', a, b)], Exists('item', Binary('rel', a, Var(0))), 'closure-first@0', None),
        ('wrong_middle', [R('plus', a, b), R('plus', a, c)], R('plus', a, c), 'closure-compose@0', '1'),
        ('negative_path', [Not(R('plus', a, b)), R('plus', b, c)], R('plus', a, c), 'closure-compose@0', '1'),
        ('different_edges', [R('plus', a, b), Reach('plus', Named('other'), b, c)], R('plus', a, c), 'closure-compose@0', '1'),
        ('star_not_plus', [R('star', a, b), R('star', b, c)], R('plus', a, c), 'closure-compose@0', '1'),
        ('reverse_edge', [Binary('rel', a, b)], R('plus', b, a), 'closure-edge@0', None),
        ('locals_swapped', [Reach('plus', Body('item', Binary('rel', Var(1), Var(0))), a, b)],
         Reach('plus', Body('item', Binary('rel', Var(0), Var(1))), a, b), 'close', None),
    ]
    for name, ps, goal, rule, parameter in attacks:
        trace = {'rule': rule} if rule == 'close' else {'rule': rule, 'at': 0, 'children': [{'rule': 'close'}]}
        if parameter is not None: trace['parameter'] = parameter
        cert = {**_binding(env, tuple(ps), goal), 'trace': trace}
        case = envelope('closure_attack_' + name, env, ps, goal, cert)
        assert not replay_python(case), name
        cases.append(case)
    return cases
