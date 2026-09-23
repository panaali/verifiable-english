"""T1e offline materials: generator, fact formats, mutation operators, arm renderers/rewriters,
trusted executors, fidelity audit and leakage features. No model calls."""
import json
import random

import pytest

from ve_experiments.t1e import arms as A
from ve_experiments.t1e import datalog as D
from ve_experiments.t1e import facts as F
from ve_experiments.t1e import fidelity as FI
from ve_experiments.t1e import leakage as L
from ve_experiments.t1e import materials as M
from ve_experiments.t1e.mutations import (COUNT_PRESERVING, FAMILIES, active, apply, candidates, redundant,
                                          well_formed)
from ve_experiments.t1e.policy import blocked_hops, can_access


@pytest.fixture(scope='module')
def items():
    # two items per condition from a test-only seed namespace (disjoint from every split)
    out = []
    for i, cond in enumerate(list(FAMILIES) * 2):
        out.append(M.generate(M.seed_of('pytest', i), cond, 'pytest'))
    for i, fam in enumerate(FAMILIES):
        out.append(M.generate(M.seed_of('pytest', 100 + i), 'honest', 'pytest', shadow=fam))
    return out


# ------------------------------------------------------------------ generator

def test_generation_is_deterministic():
    a = M.generate(M.seed_of('pytest', 99), 'negation_flip')
    b = M.generate(M.seed_of('pytest', 99), 'negation_flip')
    assert M.dumps([a]) == M.dumps([b])


def test_split_seeds_are_disjoint():
    seen = {}
    for split, design in M.SPLITS.items():
        for i in range(sum(design.values())):
            s = M.seed_of(split, i)
            assert s not in seen, (split, seen.get(s))
            seen[s] = split


def test_split_condition_counts():
    for split, design in M.SPLITS.items():
        conds = [c for c, _ in M.conditions(split)]
        assert {c: conds.count(c) for c in set(conds)} == design
        shadows = [s for c, s in M.conditions(split) if c == 'honest']
        assert all(shadows.count(f) == n for f, n in design.items() if f != 'honest')


@pytest.mark.parametrize('fam', FAMILIES)
def test_honest_shadow_matches_sabotage_construction(fam):
    seed = M.seed_of('pytest-shadow', FAMILIES.index(fam))
    sab = M.generate(seed, fam)
    hon = M.generate(seed, 'honest', shadow=fam)
    # same world and the same displayed rules; only the gold rules (and so the prose) differ
    assert hon['world'] == sab['world'] and hon['spine'] == sab['spine']
    assert hon['displayed_rules'] == active(sab['displayed_rules'])
    assert hon['rules'] == hon['displayed_rules'] and sab['rules'] != active(sab['displayed_rules'])


def test_items_validate_and_truth(items):
    for it in items:
        assert M.validate(it)
        honest = it['condition'] == 'honest'
        assert it['truth'] == {'claim_true': honest, 'displayed_claim_true': True}
        assert len(blocked_hops(it['world'], active(it['displayed_rules']), it['spine'])) == 1
        assert len(blocked_hops(it['world'], it['rules'], it['spine'])) == (1 if honest else 0)
        assert (it['mutation'] is None) == honest
        assert not redundant(it['rules']) and not redundant(it['displayed_rules'])
        assert all(well_formed(r) for r in it['rules'])


def test_policy_text_has_every_rule_and_informational_sections(items):
    for it in items:
        nums = [s['n'] for s in it['sections']]
        assert nums == list(range(1, len(nums) + 1))
        for s in it['sections']:
            assert f'§{s["n"]}. {s["text"]}' in it['policy_md']
        assert any(s['rule'] is None for s in it['sections'])


def test_public_item_hides_labels(items):
    pub = M.public_item(items[0])
    text = json.dumps(pub)
    for leak in ('condition', 'mutation', 'displayed_rules', 'honest', 'truth'):
        assert leak not in pub
    assert items[0]['claim'] in text


# ------------------------------------------------------------------ fact formats

def test_fact_files_round_trip(items):
    for it in items:
        assert F.normalise(F.load(it['files'])) == F.normalise(it['world'])
        assert set(it['files']) == set(F.FILES)


@pytest.mark.parametrize('file,old,new', [
    ('teams.yaml', 'teams:', 'groups:'),
    ('people.csv', 'id,name,employment,status,sponsors', 'id,name,status'),
    ('resources.yaml', 'classification: ', 'class: '),
])
def test_loader_rejects_malformed(items, file, old, new):
    files = dict(items[0]['files'])
    files[file] = files[file].replace(old, new, 1)
    with pytest.raises((F.FactError, ValueError)):
        F.load(files)


def test_loader_rejects_wrong_kind(items):
    files = dict(items[0]['files'])
    w = F.load(files)
    user = next(e for e, v in w['entities'].items() if v['kind'] == 'user')
    res = next(e for e, v in w['entities'].items() if v['kind'] == 'resource')
    files['assignments.csv'] += f'{user},{res}\n'   # holds(user, resource): wrong kind
    with pytest.raises(F.FactError):
        F.load(files)


# ------------------------------------------------------------------ mutations

def test_mutation_semantics_examples():
    rules = [{'relation': 'grants', 'src': [], 'dst': [['confidential', False]]},
             {'relation': 'member_of', 'src': [['contractor', True]], 'dst': []}]
    assert apply(rules, {'kind': 'negation_flip', 'rule': 0, 'side': 'dst', 'tag': 'confidential'})[0]['dst'] \
        == [['confidential', True]]
    assert apply(rules, {'kind': 'exception_swap', 'rule': 0, 'side': 'dst', 'tag': 'confidential',
                         'new_tag': 'archived'})[0]['dst'] == [['archived', False]]
    assert apply(rules, {'kind': 'scope_swap', 'rule': 1, 'side': 'src', 'tag': 'contractor',
                         'new_tag': 'suspended'})[1]['src'] == [['suspended', True]]
    assert apply(rules, {'kind': 'relation_swap', 'rule': 1, 'relation': 'member_of',
                         'new_relation': 'sponsored_by'})[1]['relation'] == 'sponsored_by'
    assert apply(rules, {'kind': 'added_exception', 'rule': 1, 'side': 'dst', 'tag': 'external'})[1]['dst'] \
        == [['external', False]]
    assert apply(rules, {'kind': 'dropped_rule', 'rule': 0})[0] is None
    assert rules[0]['dst'] == [['confidential', False]]  # apply does not mutate its input


def test_candidates_are_well_formed_and_typed(items):
    for it in items:
        for fam in FAMILIES:
            for d, m in candidates(it['rules'], fam):
                assert d['kind'] == fam
                assert all(well_formed(r) for r in active(m))
                assert m == apply(it['rules'], d)


def _counts(rules):
    live = active(rules)
    return (len(live), sum(len(r['src']) + len(r['dst']) for r in live))


def test_count_preserving_families_keep_counts(items):
    for it in items:
        if it['condition'] in COUNT_PRESERVING:
            assert _counts(it['rules']) == _counts(it['displayed_rules'])


def test_accepted_mutation_turns_false_claim_true(items):
    for it in items:
        if it['mutation']:
            assert can_access(it['world'], it['rules'], it['principal'], it['resource'])
            assert not can_access(it['world'], active(it['displayed_rules']), it['principal'], it['resource'])


# ------------------------------------------------------------------ arms: renderers, rewriters, executors

@pytest.mark.parametrize('arm', A.ARMS)
def test_rewrite_of_gold_equals_render_of_mutant(items, arm):
    for it in items:
        gold = A.render(arm, it['sections'], it['rules'])
        shown = A.render(arm, it['sections'], it['displayed_rules'])
        assert A.normalise(arm, gold, it['sections']) == gold
        if it['mutation']:
            assert A.rewrite(arm, gold, it['sections'], it['mutation']) == shown
        else:
            assert gold == shown


@pytest.mark.parametrize('arm', A.ARMS)
def test_executors_agree_with_reference(items, arm):
    for it in items:
        for rules in (it['rules'], it['displayed_rules']):
            text = A.render(arm, it['sections'], rules)
            out = A.execute(arm, text, it['world'], it['principal'], it['resource'])
            assert out == {'status': 'ok',
                           'can_access': can_access(it['world'], active(rules), it['principal'], it['resource'])}


def test_arms_share_anchors(items):
    for it in items[:4]:
        anchors = {}
        for arm in A.ARMS:
            _, secs, _ = A.split_sections(arm, A.render(arm, it['sections'], it['displayed_rules']))
            anchors[arm] = [(n, a.split(' ', 1)[1]) for n, a, _ in secs]
        assert anchors['ve'] == anchors['script'] == anchors['datalog']
        assert [n for n, _ in anchors['ve']] == [s['n'] for s in it['sections']]


def _agent_style(arm, text):
    """Rewrite a canonical artefact into a different but equivalent authoring style."""
    import re
    if arm == 'script':
        out = []
        for line in text.split('\n'):
            if line.startswith('def rule_'):
                line = line.replace('(a, b):', '(src, dst):')
            elif line.startswith('    return rel('):
                expr = re.sub(r"\(not (tag\([^)]*\))\)", r"not \1", line[len('    return '):])
                expr = expr.replace(', a, b)', ', src, dst)').replace('tag(a,', 'tag(src,').replace('tag(b,', 'tag(dst,')
                parts = expr.split(' and ')
                line = '    return ' + ' and '.join([parts[0]] + list(reversed(parts[1:])))
            out.append(line)
        return '\n'.join(out)
    if arm == 'datalog':
        return '\n'.join(l.replace('(A, B)', '(X, Y)').replace('(A)', '(X)').replace('(B)', '(Y)')
                         if l.startswith('access(') else l for l in text.split('\n'))
    return text.replace('x0', 'u').replace('x1', 'v')


@pytest.mark.parametrize('arm', A.ARMS)
def test_rewriter_on_agent_style_artefacts(items, arm):
    for it in items:
        if not it['mutation']:
            continue
        agent = _agent_style(arm, A.render(arm, it['sections'], it['rules']))
        assert A.execute(arm, agent, it['world'], it['principal'], it['resource'])['can_access'] is True
        honest = A.normalise(arm, agent, it['sections'])
        sabotaged = A.rewrite(arm, agent, it['sections'], it['mutation'])
        # honest and sabotaged differ only in the mutated section's unit
        _, hs, _ = A.split_sections(arm, honest)
        _, ss, _ = A.split_sections(arm, sabotaged)
        target = next(s['n'] for s in it['sections'] if s['rule'] == it['mutation']['rule'])
        diff = [n for (n, _, hu), (_, _, su) in zip(hs, ss) if hu != su]
        assert diff == [target]
        out = A.execute(arm, sabotaged, it['world'], it['principal'], it['resource'])
        assert out == {'status': 'ok', 'can_access': False}
        if arm == 'script':
            assert 'def rule_' in sabotaged and '(src, dst):' in sabotaged
        if arm == 'datalog':
            assert 'access(X, Y) :-' in sabotaged


def test_ve_checker_rejects_bad_shapes(items):
    it = items[0]
    text = A.render('ve', it['sections'], it['rules'])
    bad = text.replace('(x0 gets_access_of x1)', '(x1 gets_access_of x0)', 1)
    assert A.execute('ve', bad, it['world'], it['principal'], it['resource'])['status'] == 'invalid'
    stmt = next(l for l in text.split('\n') if l.startswith('for every'))
    sneaky = stmt.replace('if (', 'if ((x0 gets_access_of x1) or (', 1).replace('), then', ')), then', 1)
    assert A.execute('ve', text.replace(stmt, sneaky), it['world'], it['principal'], it['resource'])['status'] \
        == 'invalid'


def test_script_failure_is_invalid(items):
    it = items[0]
    text = A.render('script', it['sections'], it['rules']).replace('QUERY = FACTS', 'QUERY = FACTZ')
    assert A.execute('script', text, it['world'], it['principal'], it['resource'])['status'] == 'invalid'


def test_rewrite_refuses_informational_target(items):
    it = next(i for i in items if i['condition'] == 'negation_flip')
    dropped = [None if k == it['mutation']['rule'] else r for k, r in enumerate(it['rules'])]
    text = A.render('datalog', it['sections'], dropped)
    with pytest.raises(ValueError):
        A.rewrite('datalog', text, it['sections'], it['mutation'])


# ------------------------------------------------------------------ Datalog engine

def test_datalog_recursion_and_negation():
    prog = D.parse_program('a(X, Y) :- e(X, Y), !bad(Y).\nr(X, Y) :- a(X, Y).\nr(X, Z) :- r(X, Y), a(Y, Z).\n')
    db = D.evaluate(prog, {'e': {('p', 'q'), ('q', 's'), ('s', 't')}, 'bad': {('s',)}})
    assert db['r'] == {('p', 'q'), ('s', 't')}  # q -> s is blocked, so p cannot reach t
    db = D.evaluate(prog, {'e': {('p', 'q'), ('q', 's'), ('s', 't')}, 'bad': set()})
    assert ('p', 't') in db['r'] and ('p', 's') in db['r']


@pytest.mark.parametrize('src', ['p(X) :- !q(X).', 'p(X, Y) :- q(X).', 'p(X) :- q(X), !p(X).', 'p(X) :- q(X)'])
def test_datalog_rejects_unsafe_or_unstratified(src):
    with pytest.raises(D.DatalogError):
        D.evaluate(D.parse_program(src), {'q': {('a',)}})


def test_datalog_clause_round_trip():
    c = D.parse_clause('access(A, B) :- grants(A, B), !archived(B), privileged(A).')
    assert D.format_clause(c) == 'access(A, B) :- grants(A, B), !archived(B), privileged(A).'


# ------------------------------------------------------------------ fidelity audit

@pytest.mark.parametrize('arm', A.ARMS)
def test_fidelity_gold_is_faithful_and_mutant_is_not(items, arm):
    it = next(i for i in items if i['condition'] == 'relation_swap')
    gold = A.render(arm, it['sections'], it['rules'])
    res = FI.audit(arm, gold, it, n_worlds=25 if arm == 'script' else 60)
    assert res['faithful'] and res['disagreements'] == 0
    bad = FI.audit(arm, A.render(arm, it['sections'], it['displayed_rules']), it, n_worlds=5)
    assert not bad['faithful'] and not bad['exact_units']


def test_fidelity_rejects_missing_anchor(items):
    it = items[0]
    text = A.render('datalog', it['sections'], it['rules'])
    first = A.anchor('datalog', it['sections'][0])
    assert not FI.audit('datalog', text.replace(first + '\n', '', 1), it, n_worlds=0)['well_formed']


def test_perturb_respects_schema(items):
    rng = random.Random(0)
    w = FI.perturb(items[0]['world'], rng)
    from ve_experiments.t1e.policy import RELATIONS
    for r, pairs in w['relations'].items():
        sk, dk = RELATIONS[r]
        assert all(w['entities'][a]['kind'] in sk and w['entities'][b]['kind'] in dk for a, b in pairs)


# ------------------------------------------------------------------ leakage features

def test_leakage_features_use_rendered_text_only(items):
    rows = L.rows(items[:6])
    for r in rows:
        assert set(r['views']) == set(L.VIEWS_NUMERIC)
        assert r['views']['facts']['distance'] >= 2
        for arm in A.ARMS:
            assert r['views'][f'artefact_{arm}']['units'] >= 4


def test_artefact_counts_agree_across_arms(items):
    for it in items:
        feats = [L.artefact_features(arm, L.displayed(it, arm)) for arm in A.ARMS]
        for k in ('units', 'info_units', 'literals', 'neg_literals', 'distinct_relations'):
            assert len({f[k] for f in feats}) == 1, k


def test_holm():
    assert L.holm([.01, .04, .03]) == pytest.approx([.03, .06, .06])


# ------------------------------------------------------------------ statistics

def test_mcnemar_exact():
    from ve_experiments.t1e.stats import mcnemar_exact
    assert mcnemar_exact(0, 0) == 1.0
    assert mcnemar_exact(10, 0) == pytest.approx(2 * 0.5 ** 10)
    assert mcnemar_exact(3, 7) == mcnemar_exact(7, 3)


def test_newcombe_paired_properties():
    from ve_experiments.t1e.stats import newcombe_paired
    for a, b, c, d in ((12, 9, 2, 21), (30, 0, 0, 30), (5, 20, 3, 32), (0, 0, 0, 60)):
        n = a + b + c + d
        lo, hi = newcombe_paired(a, b, c, d)
        diff = (b - c) / n
        assert -1 <= lo <= diff <= hi <= 1
        lo2, hi2 = newcombe_paired(a, c, b, d)
        assert lo2 == pytest.approx(-hi) and hi2 == pytest.approx(-lo)
