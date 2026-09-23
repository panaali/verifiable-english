"""T1d Part 2: universal rule-level claims under permitted policy changes.

A rule set says how access *steps* arise from base facts; the base facts themselves (who is a
member of what, which role grants which resource) and the tags on every entity may change freely,
subject only to the rule set's tag axioms and admin constraints ("permitted changes"). A claim such
as "no contractor can ever read a confidential resource" is then universal over every permitted
policy state:

    forall u. T1(u) -> forall x. T2(x) -> not tc[step](u, x)

where step(a, b) is the disjunction of the edge rules, each `rel(a, b) and guards(a) and guards(b)`.
Guards are tag literals; a negated guard is an "unless" clause.

Exactness of the tag-vector abstraction (used by the independent validator, the Z3 CHC baseline
and to pick invariants). Call the tag vector of an entity its *type*; valid types are those that
satisfy the tag axioms. The abstract graph has an arc s -> d iff some edge rule over relation rel
has its guards satisfied by (s, d) and every admin constraint on rel is satisfied by (s, d).
* Soundness: any concrete path u = n0 -> ... -> nk = x in any permitted state maps, type by type,
  to an abstract path (each concrete step comes from some fact rel(ni, ni+1) that satisfies rel's
  constraints and some rule's guards).
* Completeness: an abstract path t0 -> ... -> tk yields a permitted state with k+1 fresh distinct
  entities of those types and exactly one fact per arc (constraints are per-fact, so the state is
  permitted), and the concrete path follows. `witness_state` builds that state and plain BFS checks it.
So the claim is false iff the abstract graph has a path of length >= 1 from a T1 type to a T2 type.

Generation, validation, mutation and rendering use only the standard library and `ve` for encoding
and printing; the validator never imports `ve` or z3.

Trust (v3). TRUSTED, new code in this file: `premises()` and `goal()` (with `step_body`/`step_case`),
the encoding of a rule set into the VE premises and goal that the checker replays against; an error
there would make VE certify the wrong statement. They are checked by the renderer round trip
(tests), by the mutant-rebinding regression (a mutant's trace, rebound to the gold inputs, must fail
logically at the mutated rule) and by agreement with the independent validator on every attempted
claim. Also trusted: `validate` (the reference verdict). UNTRUSTED: `invariant_dnf`, `dnf_cover`
and the dedicated certificate builder (`build_certificate`); nothing they emit is believed
without replay.
"""
from __future__ import annotations

from collections import deque
from itertools import product
import hashlib
import json
import random

KINDS = ('user', 'group', 'role', 'resource')
# Attribute tags and the kind each implies.
ATTRIBUTES = {'contractor': 'user', 'employee': 'user', 'suspended': 'user',
              'external': 'group', 'restricted': 'group',
              'privileged': 'role', 'temporary': 'role',
              'confidential': 'resource', 'public': 'resource', 'archived': 'resource'}
TAGS = KINDS + tuple(ATTRIBUTES)
EXCLUSIVE = (('contractor', 'employee'), ('confidential', 'public'))
# Base relations: (source kinds, destination kinds, is an inheritance relation).
RELATIONS = {
    'member_of': (('user', 'group'), ('group',), True),
    'holds': (('user', 'group'), ('role',), False),
    'inherits': (('role',), ('role',), True),
    'grants': (('role',), ('resource',), False),
    'sponsored_by': (('user',), ('group',), True),
    'owns': (('user', 'group'), ('resource',), False),
    'delegates_to': (('role',), ('role', 'user'), True),
}
CLAIMS = (('contractor', 'confidential'), ('suspended', 'confidential'), ('contractor', 'archived'),
          ('external', 'confidential'), ('contractor', 'public'))
MUTATIONS = ('added_exception', 'narrowed_scope', 'dropped_inheritance', 'negation_flip')
SEED_BASE = 202610010100  # disjoint from T1c (2026092x...) and T1d Part 1 seeds


# ------------------------------------------------------------------ types and the abstract graph

def valid_types():
    """Every tag vector (frozenset of tags) that satisfies the tag axioms."""
    result = []
    for kind in KINDS:
        attrs = [a for a, k in ATTRIBUTES.items() if k == kind]
        for bits in product((False, True), repeat=len(attrs)):
            t = frozenset([kind] + [a for a, b in zip(attrs, bits) if b])
            if not any(x in t and y in t for x, y in EXCLUSIVE):
                result.append(t)
    return result


def lit_holds(lit, t):
    tag, positive = lit
    return (tag in t) == positive


def rule_allows(rule, s, d):
    return all(lit_holds(l, s) for l in rule['src']) and all(lit_holds(l, d) for l in rule['dst'])


def constraints_allow(ruleset, rel, s, d):
    src_kinds, dst_kinds, _ = RELATIONS[rel]
    if not any(k in s for k in src_kinds) or not any(k in d for k in dst_kinds):
        return False
    for c in ruleset['constraints']:
        if c['relation'] == rel and lit_holds(c['src'], s) and lit_holds(c['dst'], d):
            return False  # forbidden combination
    return True


def abstract_arcs(ruleset):
    types = valid_types()
    arcs = {}
    for s in types:
        for d in types:
            for i, rule in enumerate(ruleset['rules']):
                if rule_allows(rule, s, d) and constraints_allow(ruleset, rule['relation'], s, d):
                    arcs.setdefault(s, {}).setdefault(d, i)
                    break
    return types, arcs


def validate(ruleset):
    """Independent validator: is the claim true? Returns verdict and a shortest abstract witness."""
    t1, t2 = ruleset['claim']
    types, arcs = abstract_arcs(ruleset)
    parent, todo = {}, deque()
    for s in (t for t in types if t1 in t):  # paths of length >= 1: seed with one arc
        for d, rule in arcs.get(s, {}).items():
            if d not in parent:
                parent[d] = (s, rule, True)
                todo.append(d)
    while todo:
        a = todo.popleft()
        if t2 in a:
            path, rules, node = [a], [], a
            while True:
                prev, rule, root = parent[node]
                rules.append(rule)
                path.append(prev)
                if root:
                    break
                node = prev
            path.reverse(); rules.reverse()
            return {'claim_true': False, 'witness_types': [sorted(t) for t in path], 'witness_rules': rules}
        for d, rule in arcs.get(a, {}).items():
            if d not in parent:
                parent[d] = (a, rule, False)
                todo.append(d)
    return {'claim_true': True, 'witness_types': None, 'witness_rules': None}


def forward_set(ruleset):
    """Types reachable in >= 0 steps from T1 types."""
    t1, _ = ruleset['claim']
    types, arcs = abstract_arcs(ruleset)
    seen = {t for t in types if t1 in t}
    todo = deque(seen)
    while todo:
        a = todo.popleft()
        for d in arcs.get(a, {}):
            if d not in seen:
                seen.add(d); todo.append(d)
    return seen


def backward_set(ruleset):
    """Types that reach a T2 type in >= 0 steps."""
    _, t2 = ruleset['claim']
    types, arcs = abstract_arcs(ruleset)
    rev = {}
    for s, ds in arcs.items():
        for d in ds:
            rev.setdefault(d, set()).add(s)
    seen = {t for t in types if t2 in t}
    todo = deque(seen)
    while todo:
        a = todo.popleft()
        for s in rev.get(a, ()):
            if s not in seen:
                seen.add(s); todo.append(s)
    return seen


# ------------------------------------------------------------------ concrete witness (independent)

def witness_state(ruleset, witness_types, witness_rules):
    """A permitted concrete state realising the abstract witness, and a plain BFS over its steps."""
    names = [f'e{i}' for i in range(len(witness_types))]
    tags = {n: set(t) for n, t in zip(names, witness_types)}
    facts = [(ruleset['rules'][r]['relation'], names[i], names[i + 1]) for i, r in enumerate(witness_rules)]
    # Permitted: tag axioms and per-fact constraints.
    for n, t in tags.items():
        assert frozenset(t) in set(valid_types()), n
    for rel, a, b in facts:
        assert constraints_allow(ruleset, rel, frozenset(tags[a]), frozenset(tags[b]))
    steps = [(a, b) for rel, a, b in facts for rule in ruleset['rules']
             if rule['relation'] == rel and rule_allows(rule, frozenset(tags[a]), frozenset(tags[b]))]
    adj = {}
    for a, b in steps:
        adj.setdefault(a, set()).add(b)
    t1, t2 = ruleset['claim']
    u = names[0]
    seen, todo = set(), deque([u])
    while todo:
        a = todo.popleft()
        for b in adj.get(a, ()):
            if b not in seen:
                seen.add(b); todo.append(b)
    violated = t1 in tags[u] and any(t2 in tags[x] for x in seen)
    return {'entities': {n: sorted(t) for n, t in tags.items()}, 'facts': [list(f) for f in facts],
            'violation_by_bfs': violated}


# ------------------------------------------------------------------ generation and mutation

def _lits_for(kinds, rng, count):
    pool = [a for a, k in ATTRIBUTES.items() if k in kinds]
    rng.shuffle(pool)
    return [(tag, rng.random() < .5) for tag in pool[:count]]


def generate(seed):
    """A random rule set whose claim is FALSE (gold), with at least one negated ("unless") guard."""
    rng = random.Random(seed)
    for _ in range(1000):
        rels = rng.sample(sorted(RELATIONS), rng.randint(4, 6))
        for must in ('grants', 'holds'):
            if must not in rels:
                rels.append(must)
        rules = []
        for rel in rels:
            src_k, dst_k, _ = RELATIONS[rel]
            for _ in range(1 if rng.random() < .75 else 2):
                rules.append({'relation': rel, 'src': _lits_for(src_k, rng, rng.choice((0, 0, 1))),
                              'dst': _lits_for(dst_k, rng, rng.choice((0, 1, 1)))})
        keys = [json.dumps([r['relation'], sorted(r['src']), sorted(r['dst'])]) for r in rules]
        if len(set(keys)) != len(keys) or not any(not pos for r in rules for _, pos in r['src'] + r['dst']):
            continue
        constraints = []
        for _ in range(rng.randint(1, 3)):
            rel = rng.choice(rels)
            src_k, dst_k, _ = RELATIONS[rel]
            a, b = _lits_for(src_k, rng, 1), _lits_for(dst_k, rng, 1)
            if a and b:
                constraints.append({'relation': rel, 'src': a[0], 'dst': b[0]})
        rng.shuffle(rules)
        rs = {'id': hashlib.sha256(f'T1d-rules:{seed}'.encode()).hexdigest()[:12], 'seed': seed,
              'rules': rules, 'constraints': constraints, 'claim': rng.choice(CLAIMS)}
        v = validate(rs)
        if not v['claim_true'] and 2 <= len(v['witness_rules']):
            return _canonical(rs)
    raise RuntimeError('no false-claim rule set for seed %d' % seed)


def _canonical(rs):
    for r in rs['rules']:
        r['src'] = [list(l) for l in r['src']]; r['dst'] = [list(l) for l in r['dst']]
    for c in rs['constraints']:
        c['src'] = list(c['src']); c['dst'] = list(c['dst'])
    rs['claim'] = list(rs['claim'])
    return json.loads(json.dumps(rs))


def _tuples(rs):
    out = json.loads(json.dumps(rs))
    for r in out['rules']:
        r['src'] = [tuple(l) for l in r['src']]; r['dst'] = [tuple(l) for l in r['dst']]
    for c in out['constraints']:
        c['src'] = tuple(c['src']); c['dst'] = tuple(c['dst'])
    out['claim'] = tuple(out['claim'])
    return out


def candidates(rs, kind):
    """Every single-rule mutation of the given kind, as (description, mutated rule set)."""
    rs = _tuples(rs)
    out = []
    for i, rule in enumerate(rs['rules']):
        src_k, dst_k, inherit = RELATIONS[rule['relation']]
        if kind in ('added_exception', 'narrowed_scope'):
            positive = kind == 'narrowed_scope'
            for side, kinds in (('src', src_k), ('dst', dst_k)):
                used = {t for t, _ in rule[side]}
                for tag in sorted(a for a, k in ATTRIBUTES.items() if k in kinds and a not in used):
                    m = json.loads(json.dumps(rs, default=list))
                    m['rules'][i][side] = [list(l) for l in rule[side]] + [[tag, positive]]
                    out.append(({'kind': kind, 'rule': i, 'side': side, 'literal': [tag, positive]}, m))
        elif kind == 'dropped_inheritance' and inherit:
            m = json.loads(json.dumps(rs, default=list))
            del m['rules'][i]
            out.append(({'kind': kind, 'rule': i, 'relation': rule['relation']}, m))
        elif kind == 'negation_flip':
            for side in ('src', 'dst'):
                for j, (tag, pos) in enumerate(rule[side]):
                    m = json.loads(json.dumps(rs, default=list))
                    m['rules'][i][side][j] = [tag, not pos]
                    out.append(({'kind': kind, 'rule': i, 'side': side, 'literal': [tag, not pos]}, m))
    return [(d, _canonical(m)) for d, m in out]


def mutate(rs, kind, rng, z3_verdict=None):
    """Accepted mutant: claim false under gold, true under the mutant (validator, and Z3 if given)."""
    cands = candidates(rs, kind)
    rng.shuffle(cands)
    tried = accepted_total = 0
    chosen = None
    for desc, m in cands:
        tried += 1
        ok = validate(m)['claim_true']
        if ok and z3_verdict is not None:
            ok = z3_verdict(m) is True
        if ok:
            accepted_total += 1
            if chosen is None:
                chosen = (desc, m)
    return chosen, tried, accepted_total


# ------------------------------------------------------------------ invariants (untrusted helper)

def _cube_ok(cube, off):
    return not any(all(lit_holds(l, t) for l in cube) for t in off)


def dnf_cover(on, off):
    """Espresso-style expand + greedy cover; invalid tag vectors are don't-cares."""
    if not on:
        return []
    primes = set()
    for t in on:
        cube = [(tag, tag in t) for tag in TAGS]
        for lit in sorted(cube, key=lambda l: (l[0] in KINDS, not l[1], l[0])):  # drop attributes first
            trial = [l for l in cube if l != lit]
            if _cube_ok(trial, off):
                cube = trial
        primes.add(tuple(sorted(cube)))
    uncovered, cover = set(on), []
    while uncovered:
        best = max(sorted(primes), key=lambda c: (sum(all(lit_holds(l, t) for l in c) for t in uncovered), -len(c)))
        cover.append(list(best))
        uncovered = {t for t in uncovered if not all(lit_holds(l, t) for l in best)}
    return cover


def invariant_dnf(rs):
    """The smaller of forward-reachable set and complement of backward set, as a DNF."""
    types = valid_types()
    fwd = forward_set(rs)
    bwd = backward_set(rs)
    a = dnf_cover(fwd, [t for t in types if t not in fwd])
    comp = [t for t in types if t not in bwd]
    b = dnf_cover(comp, list(bwd))
    size = lambda d: sum(len(c) for c in d) + len(d)
    return (a, 'forward') if size(a) <= size(b) else (b, 'backward_complement')


# ------------------------------------------------------------------ VE encoding

def ve_env():
    from ve.environment import Environment
    preds = {t: {'arguments': ['entity'], 'description': f'is tagged {t}'} for t in TAGS}
    preds.update({r: {'arguments': ['entity', 'entity'], 'description': f'base fact: {r.replace("_", " ")}'}
                  for r in RELATIONS})
    return Environment({'language': 've.core@0.1', 'profiles': ['closure@0', 'relational-fol@0'],
                        'spec_revision': 've-v0.1-closure-2026-09-21',
                        'vocabulary': {'sorts': {'entity': {'description': 'user, group, role or resource'}},
                                       'predicates': preds, 'constants': {}}})


def _balanced(parts, make):
    if len(parts) == 1:
        return parts[0]
    mid = len(parts) // 2
    return make(_balanced(parts[:mid], make), _balanced(parts[mid:], make))


def _conj(parts):
    from ve.ast import And, Top
    return _balanced(list(parts), And) if parts else Top()


def _disj(parts):
    from ve.ast import Bottom, Or
    return _balanced(list(parts), Or) if parts else Bottom()


def _lit(lit, var):
    from ve.ast import Not, Unary, Var
    atom = Unary(lit[0], Var(var))
    return atom if lit[1] else Not(atom)


def step_case(rule):
    """TRUSTED: one edge rule as a formula over Var(1) (source) and Var(0) (destination)."""
    from ve.ast import Binary, Var
    return _conj([Binary(rule['relation'], Var(1), Var(0))] + [_lit(l, 1) for l in rule['src']]
                 + [_lit(l, 0) for l in rule['dst']])


def step_body(rs):
    """TRUSTED. Body edge: Var(1) is the source, Var(0) the destination."""
    from ve.ast import Body
    return Body('entity', _disj([step_case(r) for r in rs['rules']]))


def premises(rs):
    """TRUSTED. Tag axioms and admin constraints (the permitted-change envelope), as closed formulas."""
    from ve.ast import And, Binary, Bottom, Forall, Implies, Not, Or, Unary, Var
    ps = []
    ps.append(Forall('entity', _disj([Unary(k, Var(0)) for k in KINDS])))
    for i, a in enumerate(KINDS):
        for b in KINDS[i + 1:]:
            ps.append(Forall('entity', Not(And(Unary(a, Var(0)), Unary(b, Var(0))))))
    for a, k in ATTRIBUTES.items():
        ps.append(Forall('entity', Implies(Unary(a, Var(0)), Unary(k, Var(0)))))
    for a, b in EXCLUSIVE:
        ps.append(Forall('entity', Not(And(Unary(a, Var(0)), Unary(b, Var(0))))))
    for rel, (sk, dk, _) in RELATIONS.items():
        ps.append(Forall('entity', Forall('entity', Implies(Binary(rel, Var(1), Var(0)), And(
            _disj([Unary(k, Var(1)) for k in sk]), _disj([Unary(k, Var(0)) for k in dk]))))))
    for c in rs['constraints']:
        ps.append(Forall('entity', Forall('entity', Implies(Binary(c['relation'], Var(1), Var(0)),
                                                             Not(And(_lit(c['src'], 1), _lit(c['dst'], 0)))))))
    return ps


def goal(rs):
    """TRUSTED. forall u. T1(u) -> forall x. T2(x) -> not tc+[step](u, x)."""
    from ve.ast import Forall, Implies, Not, Reach, Unary, Var
    t1, t2 = rs['claim']
    return Forall('entity', Implies(Unary(t1, Var(0)), Forall('entity', Implies(
        Unary(t2, Var(0)), Not(Reach('plus', step_body(rs), Var(1), Var(0)))))))


def invariant_formula(dnf):
    return _disj([_conj([_lit(l, 0) for l in cube]) for cube in dnf])


def ve_certify(rs, *, max_steps=200_000, dnf=None):
    """Untrusted search with the supplied invariant, then trusted Python replay."""
    from ve import check_entailment_certificate, prove_entailment
    env = ve_env()
    ps, g = premises(rs), goal(rs)
    if dnf is None:
        dnf, _ = invariant_dnf(rs)
    result = prove_entailment(env, ps, g, invariants=[invariant_formula(dnf)], max_steps=max_steps)
    replay = None
    if result.certificate is not None:
        replay = check_entailment_certificate(env, ps, g, result.certificate, max_steps=max_steps)
    return {'status': result.status, 'steps': result.steps, 'certificate': result.certificate,
            'python_replay_valid': bool(replay and replay.valid), 'env': env, 'premises': ps, 'goal': g}


# ------------------------------------------------------------------ renderers (one checked source)

def render_json(rs):
    return json.dumps({'rules': rs['rules'], 'constraints': rs['constraints'], 'claim': rs['claim']},
                      indent=1, sort_keys=True)


def _english_lit(lit, who):
    tag, pos = lit
    return f'{who} is {"" if pos else "not "}{tag}'


def _a(word):
    return 'an' if word[0] in 'aeiou' else 'a'


def render_english(rs):
    lines = ['Tag axioms: every entity is exactly one of user, group, role, resource; '
             + '; '.join(f'{a} entities are {k}s' for a, k in ATTRIBUTES.items())
             + '; nothing is both ' + ' or both '.join(f'{a} and {b}' for a, b in EXCLUSIVE) + '.']
    for rel, (sk, dk, _) in RELATIONS.items():
        lines.append(f'Permitted change: {_a(rel)} "{rel}" fact may link a {" or ".join(sk)} to a {" or ".join(dk)}.')
    for c in rs['constraints']:
        lines.append(f'Permitted change: no "{c["relation"]}" fact may link a source that '
                     f'{_english_lit(c["src"], "")[1:]} to a destination that {_english_lit(c["dst"], "")[1:]}.')
    for i, r in enumerate(rs['rules'], 1):
        cond = [_english_lit(l, 'the source') for l in r['src'] if l[1]] + \
               [_english_lit(l, 'the destination') for l in r['dst'] if l[1]]
        unless = [_english_lit((t, True), 'the source') for t, p in r['src'] if not p] + \
                 [_english_lit((t, True), 'the destination') for t, p in r['dst'] if not p]
        text = f'Rule {i}: {_a(r["relation"])} "{r["relation"]}" fact gives the source the access of the destination'
        if cond:
            text += ' when ' + ' and '.join(cond)
        if unless:
            text += ', unless ' + ' or '.join(unless)
        lines.append(text + '.')
    t1, t2 = rs['claim']
    lines.append(f'Claim: under every permitted policy, no {t1} entity can reach a {t2} entity by a chain of one or more rule steps.')
    return '\n'.join(lines)


def render_ve(rs):
    from ve.ast import Document
    from ve.printer import print_document
    env = ve_env()
    return print_document(env, Document(tuple(premises(rs)) + (goal(rs),)))


# ------------------------------------------------------------------ untrusted certificate builder
# The generic `prove_entailment` search exhausts 1,000,000 steps on these rule sets (see part2.py),
# so the agent side uses a dedicated builder: closure induction with the supplied invariant, ground
# instantiation of the premises at the focus parameters, then a unit-propagating propositional
# tableau over the checker's own derivation functions. Nothing it emits is believed without replay.

class OpenBranch(Exception):
    pass


class _Builder:
    def __init__(self, branch, node):
        self.branch, self.node = branch, node

    def expand(self, at, parameter=None):
        from ve.entailment import _apply, _derive, _rule
        alternatives = _derive(self.branch, at, parameter)
        children = [{} for _ in alternatives]
        self.node.update(rule=_rule(self.branch.formulas[at]), at=at, children=children)
        if parameter is not None:
            self.node['parameter'] = parameter
        return [_Builder(_apply(self.branch, at, parameter, xs), c) for xs, c in zip(alternatives, children)]

    def induct(self, env, at, sort, invariant):
        from ve.ast import _to_data
        from ve.closure import derive_induction
        children = [{}, {}, {}]
        self.node.update(rule='closure-induct@1', at=at, sort=sort, invariant=_to_data(invariant), children=children)
        out = []
        for xs, c in zip(derive_induction(env, self.branch, at, sort, invariant), children):
            branch = self.branch.copy()
            branch.formulas.extend(xs)
            out.append(_Builder(branch, c))
        return out

    def close(self):
        self.node.clear()
        self.node['rule'] = 'close'


def _state(branch):
    from ve.ast import Binary, Eq, Unary
    from ve.entailment import _term_token
    parent = {t: t for t in branch.parameters}

    def find(x):
        while parent[x] != x:
            x = parent[x]
        return x
    for it in branch.formulas:
        f = it.formula
        if type(f) is Eq and it.positive:
            a, b = find(_term_token(f.left, it.bindings)), find(_term_token(f.right, it.bindings))
            if a != b:
                parent[b] = a
    lits = {}
    for it in branch.formulas:
        f = it.formula
        tok = lambda t: find(_term_token(t, it.bindings))
        if type(f) is Unary:
            lits[('u', f.predicate, tok(f.term))] = it.positive
        elif type(f) is Binary:
            lits[('b', f.predicate, tok(f.left), tok(f.right))] = it.positive
        elif type(f) is Eq and not it.positive:
            lits[('eq', frozenset((tok(f.left), tok(f.right))))] = False
    return find, lits


def _ev(f, bindings, st):
    from ve import ast as A
    from ve.entailment import _term_token
    find, lits = st
    k = type(f)
    if k is A.Top:
        return True
    if k is A.Bottom:
        return False
    if k is A.Not:
        v = _ev(f.body, bindings, st)
        return None if v is None else not v
    if k in (A.And, A.Or, A.Implies):
        left = _ev(f.left, bindings, st)
        if k is A.Implies:
            left = None if left is None else not left
        right = _ev(f.right, bindings, st)
        vals = (left, right)
        if k is A.And:
            return False if False in vals else (True if vals == (True, True) else None)
        return True if True in vals else (False if vals == (False, False) else None)
    tok = lambda t: find(_term_token(t, bindings))
    if k is A.Unary:
        return lits.get(('u', f.predicate, tok(f.term)))
    if k is A.Binary:
        return lits.get(('b', f.predicate, tok(f.left), tok(f.right)))
    if k is A.Eq:
        a, b = tok(f.left), tok(f.right)
        return True if a == b else lits.get(('eq', frozenset((a, b))))
    return None


def _alternatives(it):
    from ve import ast as A
    f, pos = it.formula, it.positive
    if type(f) is A.Implies:
        return [(f.left, not pos), (f.right, pos)]
    return [(f.left, pos), (f.right, pos)]


def _score(formula, positive, bindings, st):
    """None if satisfied on the branch; else the number of open alternatives (0 = conflict)."""
    from ve import ast as A
    v = _ev(formula, bindings, st)
    if v == positive:
        return None
    if v is not None:
        return 0
    k = type(formula)
    if (k is A.Or and positive) or (k is A.And and not positive) or (k is A.Implies and positive):
        alts = _alternatives(type('S', (), {'formula': formula, 'positive': positive})())
        if any(_ev(f, bindings, st) == sgn for f, sgn in alts):
            return None
        return sum(_ev(f, bindings, st) is None for f, _ in alts)
    return 1


def _instance(branch, premise, tokens):
    """The formula and bindings a (nested) gamma instantiation would add."""
    f, bindings = branch.formulas[premise].formula, ()
    for t in tokens:
        f, bindings = f.body, (t,) + bindings
    return f, bindings


def _refute(node, forge, stats, pending):
    from ve.entailment import _closed, _kind
    while True:
        b = node.branch
        stats['nodes'] += 1
        if stats['nodes'] > stats['limit']:
            raise OpenBranch('builder node budget exhausted')
        if _closed(b):
            node.close()
            return True
        st = _state(b)
        # Expand an alpha/not/delta formula only if it still carries information (depth economy:
        # every expansion is one nesting level, and the wire format allows 256 JSON levels).
        simple = next((i for i, it in enumerate(b.formulas)
                       if i not in b.expanded and _kind(it) in ('alpha', 'not', 'delta')
                       and (_kind(it) == 'delta' or _score(it.formula, it.positive, it.bindings, st) is not None)), None)
        if simple is None:
            best = None
            for i, it in enumerate(b.formulas):
                if i in b.expanded or _kind(it) != 'beta':
                    continue
                score = _score(it.formula, it.positive, it.bindings, st)
                if score is not None and (best is None or score < best[0]):
                    best = (score, 'beta', i)
            for j, (premise, tokens) in enumerate(pending):
                f, bindings = _instance(b, premise, tokens)
                score = _score(f, True, bindings, st)
                if score is not None and (best is None or score < best[0]):
                    best = (score, 'gamma', j)
            if best is None:
                if forge:
                    node.close()
                    stats['forged'] += 1
                    return False
                raise OpenBranch('open branch: the invariant does not close this case')
            if best[1] == 'gamma':
                premise, tokens = pending[best[2]]
                pending = pending[:best[2]] + pending[best[2] + 1:]
                at = premise
                for t in tokens:
                    [node] = node.expand(at, t)
                    at = len(node.branch.formulas) - 1
                continue
            ok = True
            for child in node.expand(best[2]):
                ok = _refute(child, forge, stats, pending) and ok
            return ok
        [node] = node.expand(simple)


def _saturate(node):
    """Expand alpha/not/delta formulas (not betas, gammas or paths)."""
    from ve.entailment import _kind
    while True:
        b = node.branch
        i = next((i for i, it in enumerate(b.formulas)
                  if i not in b.expanded and _kind(it) in ('alpha', 'not', 'delta')), None)
        if i is None:
            return node
        [node] = node.expand(i)


def _pending(branch, n_premises, focus):
    """Premise instances the builder may use: 1-variable premises at each focus parameter,
    2-variable premises at the ordered focus pair (source, destination)."""
    from ve.ast import Forall
    out = []
    for i in range(n_premises):
        f = branch.formulas[i].formula
        if type(f) is not Forall:
            continue
        if type(f.body) is Forall:
            if len(focus) == 2:
                out.append((i, (focus[0], focus[1])))
        else:
            out.extend((i, (t,)) for t in focus)
    return out


def build_certificate(env, ps, g, invariant, sort='entity', *, forge=False, limit=200_000):
    """Returns (certificate, forged_leaf_count). Raises OpenBranch if an honest proof fails."""
    from ve import ast as A
    from ve.entailment import _binding, _initial_branch, _kind, _term_token
    import sys
    sys.setrecursionlimit(max(sys.getrecursionlimit(), 20000))
    root = _Builder(_initial_branch(env, tuple(ps), g), {})
    node = _saturate(root)
    at = next(i for i, it in enumerate(node.branch.formulas) if it.positive and type(it.formula) is A.Reach)
    reach = node.branch.formulas[at]
    u = _term_token(reach.formula.left, reach.bindings)
    x = _term_token(reach.formula.right, reach.bindings)
    base, step, cont = node.induct(env, at, sort, invariant)
    stats = {'nodes': 0, 'forged': 0, 'limit': limit}
    for child, focus in ((base, [u]), (cont, [x]), (step, None)):
        before = child.branch.next_witness
        child = _saturate(child)
        if focus is None:
            focus = [f'w:{before}', f'w:{before + 1}']
        _refute(child, forge, stats, _pending(child.branch, len(ps), focus))
    return {**_binding(env, tuple(ps), g), 'trace': root.node}, stats


def ve_certify_built(rs, dnf=None, *, forge=False):
    from ve import check_entailment_certificate
    import time
    env, ps, g = ve_env(), premises(rs), goal(rs)
    if dnf is None:
        dnf, _ = invariant_dnf(rs)
    t0 = time.time()
    try:
        cert, stats = build_certificate(env, ps, g, invariant_formula(dnf), forge=forge)
    except OpenBranch as e:
        return {'built': False, 'reason': str(e), 'certificate': None, 'python_replay_valid': False,
                'build_seconds': round(time.time() - t0, 3), 'env': env, 'premises': ps, 'goal': g}
    t1 = time.time()
    replay = check_entailment_certificate(env, ps, g, cert, max_steps=2_000_000)
    return {'built': True, 'forged_leaves': stats['forged'], 'builder_nodes': stats['nodes'], 'certificate': cert,
            'python_replay_valid': replay.valid, 'python_replay_status': replay.status,
            'python_replay_steps': replay.steps, 'build_seconds': round(t1 - t0, 3),
            'replay_seconds': round(time.time() - t1, 3), 'env': env, 'premises': ps, 'goal': g}


# ------------------------------------------------------------------ closed-world "unless" snapshots
# A concrete policy state (named entities, listed facts, listed tags), closed-world as in T1c: the
# trusted harness extracts, for each member of the separating set S, one completion axiom per
# relation, one completion axiom per tag ("the only confidential entities are ..."), the listed
# positive tag facts, and distinct-names facts. The step relation is a Body with guards, including
# negated guards ("unless"). Guards are essential by construction: without them u would reach x.

SNAP_TAGS = ('contractor', 'suspended', 'confidential', 'public')
SNAP_RULES = (
    {'relation': 'member_of', 'src': [], 'dst': []},
    {'relation': 'holds', 'src': [['suspended', False]], 'dst': []},          # unless the holder is suspended
    {'relation': 'grants', 'src': [], 'dst': [['confidential', False]]},      # unless the resource is confidential
    {'relation': 'sponsored_by', 'src': [['contractor', True]], 'dst': []},   # only contractors inherit via sponsor
)
SNAP_SEED = 202610020100


def _snap_reach(facts, tags, rules, start):
    adj = {}
    for rel, a, b in facts:
        for r in rules:
            if r['relation'] == rel and all((t in tags.get(a, ())) == p for t, p in r['src']) \
                    and all((t in tags.get(b, ())) == p for t, p in r['dst']):
                adj.setdefault(a, set()).add(b)
    seen, todo = {start}, deque([start])
    while todo:
        n = todo.popleft()
        for m in adj.get(n, ()):
            if m not in seen:
                seen.add(m); todo.append(m)
    return seen


def generate_snapshot(seed):
    rng = random.Random(seed)
    unguarded = [{'relation': r['relation'], 'src': [], 'dst': []} for r in SNAP_RULES]
    for _ in range(10000):
        n_users, n_groups, n_roles, n_res = rng.randint(2, 3), rng.randint(2, 3), rng.randint(2, 3), rng.randint(2, 4)
        users = [f'usr{i}' for i in range(n_users)]; groups = [f'grp{i}' for i in range(n_groups)]
        roles = [f'rol{i}' for i in range(n_roles)]; res = [f'res{i}' for i in range(n_res)]
        facts = set()
        for _ in range(rng.randint(6, 12)):
            rel = rng.choice(['member_of', 'holds', 'grants', 'sponsored_by', 'member_of', 'holds'])
            a = rng.choice({'member_of': users + groups, 'holds': users + groups, 'grants': roles,
                            'sponsored_by': users}[rel])
            b = rng.choice({'member_of': groups, 'holds': roles, 'grants': res, 'sponsored_by': groups}[rel])
            if a != b:
                facts.add((rel, a, b))
        tags = {}
        for u in users:
            tags[u] = {t for t in ('contractor', 'suspended') if rng.random() < .4}
        for x in res:
            tags[x] = {rng.choice(['confidential', 'public'])} if rng.random() < .8 else set()
        u, x = users[0], rng.choice(res)
        if 'contractor' not in tags[u] or 'confidential' not in tags[x]:
            continue
        facts = sorted(facts)
        if x in _snap_reach(facts, tags, SNAP_RULES, u) or x not in _snap_reach(facts, tags, unguarded, u):
            continue
        # Every guard kind should matter somewhere: require that the blocked path uses a negated guard.
        return {'id': hashlib.sha256(f'T1d-snap:{seed}'.encode()).hexdigest()[:12], 'seed': seed,
                'entities': users + groups + roles + res, 'facts': [list(f) for f in facts],
                'tags': {k: sorted(v) for k, v in tags.items() if v}, 'principal': u, 'resource': x}
    raise RuntimeError('no snapshot for seed %d' % seed)


def snapshot_encoding(snap, separating_set=None):
    """TRUSTED extraction: (env, premises, goal, S)."""
    from ve.ast import Binary, Body, Const, Eq, Forall, Implies, Not, Reach, Unary, Var
    from ve.environment import Environment
    facts = [tuple(f) for f in snap['facts']]
    tags = {k: set(v) for k, v in snap['tags'].items()}
    S = sorted(separating_set if separating_set is not None
               else _snap_reach(facts, tags, SNAP_RULES, snap['principal']))
    preds = {t: {'arguments': ['entity'], 'description': f'is tagged {t}'} for t in SNAP_TAGS}
    preds.update({r['relation']: {'arguments': ['entity', 'entity'], 'description': r['relation']} for r in SNAP_RULES})
    env = Environment({'language': 've.core@0.1', 'profiles': ['closure@0', 'relational-fol@0'],
                       'spec_revision': 've-v0.1-closure-2026-09-21',
                       'vocabulary': {'sorts': {'entity': {'description': 'policy entity'}}, 'predicates': preds,
                                      'constants': {e: {'sort': 'entity', 'description': e} for e in snap['entities']}}})
    member = lambda names: _disj([Eq(Var(0), Const(n)) for n in names])
    ps = []
    for s in S:
        for r in SNAP_RULES:
            targets = sorted(b for rel, a, b in facts if rel == r['relation'] and a == s)
            atom = Binary(r['relation'], Const(s), Var(0))
            ps.append(Forall('entity', Implies(atom, member(targets)) if targets else Not(atom)))
    for t in SNAP_TAGS:
        holders = sorted(e for e, ts in tags.items() if t in ts)
        ps.extend(Unary(t, Const(e)) for e in holders)
        ps.append(Forall('entity', Implies(Unary(t, Var(0)), member(holders)) if holders else Not(Unary(t, Var(0)))))
    tagged = sorted(tags)
    for s in S:
        for o in sorted(set(tagged) | {snap['resource']}):
            if o != s:
                ps.append(Not(Eq(Const(s), Const(o))))
    cases = [_conj([Binary(r['relation'], Var(1), Var(0))] + [_lit(l, 1) for l in r['src']]
                   + [_lit(l, 0) for l in r['dst']]) for r in SNAP_RULES]
    goal_ = Not(Reach('plus', Body('entity', _disj(cases)), Const(snap['principal']), Const(snap['resource'])))
    return env, ps, goal_, S


def certify_snapshot(snap, *, lean=True):
    from ve import check_entailment_certificate
    from ve.ast import Const, Eq, Var
    env, ps, g, S = snapshot_encoding(snap)
    inv = _disj([Eq(Var(0), Const(n)) for n in S])
    cert, stats = build_certificate(env, ps, g, inv)
    replay = check_entailment_certificate(env, ps, g, cert, max_steps=2_000_000)
    lean_valid = None
    if lean:
        from ve_experiments.t1c.certificates import LEAN, envelope, lean_replay
        if LEAN.exists():
            lean_valid = bool(lean_replay([envelope(snap['id'], env, ps, g, cert)])[0]['valid'])
    depth = lambda n: 1 + max([depth(c) for c in n.get('children', [])] or [0])
    return {'id': snap['id'], 'set_size': len(S), 'premises': len(ps), 'python_replay_valid': replay.valid,
            'python_replay_status': replay.status, 'python_replay_detail': replay.detail[:120],
            'python_replay_steps': replay.steps, 'lean_replay_valid': lean_valid, 'builder_nodes': stats['nodes'],
            'trace_depth': depth(cert['trace'])}


def forged_snapshot(snap):
    """Sabotage: drop the guard-blocked target from the policy view of S (a leak). Must not replay."""
    from ve import check_entailment_certificate
    from ve.ast import Const, Eq, Var
    facts = [tuple(f) for f in snap['facts']]
    tags = {k: set(v) for k, v in snap['tags'].items()}
    unguarded = [{'relation': r['relation'], 'src': [], 'dst': []} for r in SNAP_RULES]
    # Claim the resource is unreachable from a principal that CAN reach it once the guard on the
    # resource is ignored: remove the confidential tag (the negation-flip mistranscription).
    flipped = json.loads(json.dumps(snap))
    flipped['tags'][snap['resource']] = [t for t in flipped['tags'].get(snap['resource'], []) if t != 'confidential']
    if not flipped['tags'][snap['resource']]:
        del flipped['tags'][snap['resource']]
    reach = _snap_reach(facts, {k: set(v) for k, v in flipped['tags'].items()}, SNAP_RULES, snap['principal'])
    if snap['resource'] not in reach:
        return None
    S = sorted(reach - {snap['resource']})
    env, ps, g, _ = snapshot_encoding(flipped, S)
    inv = _disj([Eq(Var(0), Const(n)) for n in S])
    cert, stats = build_certificate(env, ps, g, inv, forge=True)
    replay = check_entailment_certificate(env, ps, g, cert, max_steps=2_000_000)
    return {'id': snap['id'], 'forged_leaves': stats['forged'], 'python_replay_valid': replay.valid}
