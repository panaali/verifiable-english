"""T1d Part 1 offline tests: materials v2 ground truth, parsers, near-miss kinds, certificates
(Python + Lean when built), seed disjointness, design balance, leakage audit plumbing."""
from collections import Counter
from itertools import product

import pytest

from ve_experiments.t1c import certificates as C1
from ve_experiments.t1d import certificates as C
from ve_experiments.t1d import materials as M
from ve_experiments.t1d import protocol as P
from ve_experiments.t1d.leakage import FEATURE_SETS, prompt_features, split_prompt
from ve_experiments.t1d.part1 import expected, seed_collisions

LEAN = C1.LEAN.exists()
GRANTS = 3000


def spec(family, scheme='hex', shape='uniform', kind='honest', index=0):
    return {'seed': M.seed_of('test', hash((family, scheme, shape, kind, index)) & 0xffff), 'split': 'test',
            'index': index, 'family': family, 'scheme': scheme, 'shape': shape, 'grants': GRANTS,
            'sabotaged': kind != 'honest', 'kind': kind}


@pytest.mark.parametrize('family,scheme', list(product(sorted(M.FAMILIES), M.SCHEMES)))
def test_every_family_and_scheme_round_trips_with_ground_truth(family, scheme):
    for kind in ('honest', 'alias'):
        item = M.generate(spec(family, scheme, M.SHAPES[len(family) % 4], kind))
        edges = M.parse_policy(item)
        assert len(edges) == len(set(edges)) == GRANTS
        assert (item['resource'] in M.forward(edges, item['principal'])) == item['sabotaged']
        assert item['claim'] == f"{item['claim_principal']} cannot access {item['resource']}."
        assert M.parse_directory(item['raw']['directory.txt'])[item['claim_principal']] == item['principal']
        assert M.generate(spec(family, scheme, M.SHAPES[len(family) % 4], kind)) == item  # deterministic


def test_twins_differ_in_exactly_one_character():
    for family, scheme in product(sorted(M.FAMILIES), M.SCHEMES):
        item = M.generate(spec(family, scheme))
        for a, b in ((item['principal'], item['roles']['near_principal']), (item['resource'], item['roles']['near_resource'])):
            assert len(a) == len(b) and sum(x != y for x, y in zip(a, b)) == 1


def test_parsers_reject_malformed_files():
    with pytest.raises(ValueError):
        M.parse_file('colon', 'member: groups', 'member: groups\nu_0001 g_0002\n')
    with pytest.raises(ValueError):
        M.parse_file('csv', 'a,b', 'a,b\nx,y,z\n')
    with pytest.raises(ValueError):
        M.parse_file('yaml', '# h', '# h\n  - orphan\n')
    with pytest.raises(ValueError):
        M.parse_file('kv', '# h', '# h\na => b, b\n')
    with pytest.raises(ValueError):
        M.parse_file('arrow', '# h', '# h\na -> b')  # missing final newline
    with pytest.raises(ValueError):
        M.parse_file('jsonl', 'r', '{"relation": "r"}\n{"relation": "r", "from": "a", "to": "b"}\n')
    head = M.DIRECTORY[1] + '\n'
    assert M.parse_directory(head + 'Ada K. Chen = u_0001\n') == {'Ada K. Chen': 'u_0001'}
    for bad in ('Ada K. Chen = u_0001\nAda K. Chen = u_0002\n', 'Ada K. Chen = u_0001\nBen L. Fox = u_0001\n',
                'ada chen = u_0001\n', 'Ada K. Chen: u_0001\n'):
        with pytest.raises(ValueError):
            M.parse_directory(head + bad)


def test_validation_catches_a_wrong_label():
    item = M.generate(spec('rbac4'))
    bad = dict(item, sabotaged=True)
    with pytest.raises(AssertionError):
        M.validate(bad, set(M.parse_policy(item)))


@pytest.mark.parametrize('kind', ('honest',) + M.SABOTAGE_KINDS)
def test_certificate_outcomes_by_kind(kind):
    item = M.generate(spec('k8s' if kind in M.SEMANTIC_KINDS else 'teams', 'paths', 'powerlaw', kind))
    edges = M.edges_of(item)
    sub = C.build(item, edges=edges)
    report = C.ve_verdict(item, sub, lean=LEAN, edges=edges)
    script = C.script_verdict(item, sub, edges=edges)
    assert expected(item, report, script)
    assert report['statement'] != item['claim']  # v3: never string-identical, for any kind
    assert P.rule_decision(item, report) == ('APPROVE' if kind == 'honest' else 'REJECT')
    assert M.PAD_RANGE[0] <= len(sub['separating_set']) <= M.PAD_RANGE[1] + 20
    if kind in M.SEMANTIC_KINDS or kind.startswith('char'):
        # Valid for another statement, which is true under the policy; the claim itself is false.
        assert report['verdict'] == 'VALID' and report['statement'] != item['claim']
        assert item['resource'] in M.forward(edges, item['principal'])
        if LEAN:
            assert report['lean_replay_valid'] is True
    if kind == 'alias':
        assert [item['principal'], item['roles']['alias_account']] in edges
    if kind == 'leak':
        assert sub['forged_leaves'] == 1 and script['leaking_edge_count'] == 1


def test_forged_honest_certificate_rejected():
    item = M.generate(spec('orgchart', 'names'))
    edges = M.edges_of(item)
    sub = C.build(item, edges=edges)
    smaller = dict(sub, separating_set=[n for n in sub['separating_set'] if n != item['roles']['primary_group']])
    assert C.ve_verdict(item, smaller, lean=False, edges=edges)['verdict'] == 'INVALID'
    assert C.script_verdict(item, smaller, edges=edges)['verdict'] == 'INVALID'


def test_ve_names_are_injective_and_valid():
    names = C.ve_names(['a.b@corp.example', 'a_b@corp.example', '/g/x/y1', 'X-1/y2', 'U123456'])
    assert len(set(names.values())) == 5
    assert all(v[0].isalpha() and v == v.lower() for v in names.values())


def test_design_counts_disjoint_fresh_seeds_and_held_out_strata():
    full = M.design('full')
    counts = Counter(s['kind'] for s in full)
    assert counts['honest'] == 160 and counts['leak'] == 10 and all(counts[k] == 20 for k in M.BINDING_KINDS)
    dev = M.design('dev')
    assert {s['family'] for s in dev} <= set(M.DEV_FAMILIES) and {s['scheme'] for s in dev} <= set(M.DEV_SCHEMES)
    assert set(M.HELD_OUT_FAMILIES) <= {s['family'] for s in full} and set(M.SCHEMES) <= {s['scheme'] for s in full}
    seeds = [s['seed'] for split in M.SPLITS for s in M.design(split)]
    assert len(seeds) == len(set(seeds)) and seed_collisions(seeds) == 0  # vs T1c and the burned v2 seeds


def test_prompts_show_only_the_frozen_fields_and_features_come_from_the_text():
    item = M.generate(spec('folders', 'names', 'community', 'group_member'))
    edges = M.edges_of(item)
    sub = C.build(item, edges=edges)
    report = C.ve_verdict(item, sub, lean=False, edges=edges)
    raw_system, raw_user = P.prompts(item, 'haiku-raw')
    system, user = P.prompts(item, 'haiku-ve', submission=sub, report=report)
    for text in (system, user):
        for leaked in ('separating_set', 'python_replay', 'replay_steps', 'trace nodes', 'premises', 'invariant',
                       'set_size'):
            assert leaked not in text.split('CLAIM: ')[-1] and leaked not in system
    texts, claim, cert = split_prompt(user)
    assert claim == item['claim'] and set(cert) == {'statement', 'principal', 'resource', 'proof'}
    assert all(texts[name] == item['raw'][name] for name in item['raw'])
    features, family = prompt_features(system, user)
    assert family == item['family'] and set(FEATURE_SETS['ve_prompt']) == set(features)
    assert set(prompt_features(raw_system, raw_user)[0]) == set(FEATURE_SETS['raw_prompt'])
    # The frozen hash does not depend on the run's HMAC key.
    other = P.prompts(item, 'haiku-ve', submission=sub, report=report, key=b'1' * 32)
    assert other[0] != system and P.prompt_hash(*other) == P.prompt_hash(system, user)


def test_leakage_audit_is_two_sided_and_near_chance_on_random_labels():
    import numpy as np
    from ve_experiments.t1d.leakage import criterion, run_audits
    rng = np.random.default_rng(0)
    names = FEATURE_SETS['ve_prompt']
    rows = [{'kind': 'honest' if i % 2 else 'leak', 'family': 'rbac4', 'scheme': 'hex', 'shape': 'uniform',
             'features': {f: float(rng.normal()) for f in names}} for i in range(80)]
    res = run_audits(rows, {'leak': ('leak',)}, feature_sets=('ve_prompt',), which=('logistic',), repeats=2,
                     permutations=19, boot=50, workers=2)
    m = res['ve_prompt']['leak']['models']['logistic']
    assert .3 < m['foldwise_auc'] < .7 and m['p_two_sided'] > .05 and m['permutations'] == 19
    assert criterion(res, ('leak',))['passes']
    # A leaking feature is caught (the p-value is two-sided: |AUC - null mean|).
    for i, r in enumerate(rows):
        r['features'][names[0]] = float(i % 2) + .01 * i
    res = run_audits(rows, {'leak': ('leak',)}, feature_sets=('ve_prompt',), which=('logistic',), repeats=2,
                     permutations=19, boot=50, workers=2)
    assert res['ve_prompt']['leak']['models']['logistic']['p_two_sided'] <= .05
