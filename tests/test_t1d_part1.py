"""T1d Part 1 offline tests: materials v4 ground truth, parsers, near-miss kinds, hub symmetry,
certificates (Python + Lean when built), seed disjointness, byte sizing, leakage audit plumbing."""
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
    item = M.generate(spec('k8s' if kind in M.RELATED_KINDS else 'teams', 'paths', 'powerlaw', kind))
    edges = M.edges_of(item)
    sub = C.build(item, edges=edges)
    report = C.ve_verdict(item, sub, lean=LEAN, edges=edges)
    script = C.script_verdict(item, sub, edges=edges)
    assert expected(item, report, script)
    assert report['statement'] != item['claim']  # v3: never string-identical, for any kind
    assert P.rule_decision(item, report) == ('APPROVE' if kind == 'honest' else 'REJECT')
    assert sub['separating_set'] == sorted(M.closure(edges, *C.certified_entity(item, kind)[:1], sub['leak_cut'] and tuple(sub['leak_cut'])))
    if kind in M.RELATED_KINDS or kind.startswith('char'):
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
    assert family == item['family'] and set(FEATURE_SETS['ve_prompt']) <= set(features)
    assert set(prompt_features(raw_system, raw_user)[0]) == set(FEATURE_SETS['raw_prompt'])
    # The certified subject (the group) is profiled from the policy text, and it is in the directory.
    assert features['subject_in_directory'] == 1 and features['subject_out'] > 0
    # The frozen hash does not depend on the run's HMAC key.
    other = P.prompts(item, 'haiku-ve', submission=sub, report=report, key=b'1' * 32)
    assert other[0] != system and P.prompt_hash(*other) == P.prompt_hash(system, user)


def test_leakage_audit_is_two_sided_and_near_chance_on_random_labels():
    import numpy as np
    from ve_experiments.t1d.leakage import criterion, run_audits, univariate
    rng = np.random.default_rng(0)
    names = FEATURE_SETS['ve_prompt']
    rows = [{'kind': 'honest' if i % 2 else 'leak', 'family': 'rbac4', 'scheme': 'hex', 'shape': 'uniform',
             'features': {f: float(rng.normal()) for f in names}} for i in range(80)]
    res = run_audits(rows, {'leak': ('leak',)}, feature_sets=('ve_prompt',), which=('logistic',), repeats=2,
                     permutations=39, boot=50, workers=2)
    m = res['ve_prompt']['leak']['models']['logistic']
    assert .3 < m['foldwise_auc'] < .7 and m['p_two_sided'] > .05 and m['permutations'] == 39
    verdict = criterion(res, ('leak',), univariate(rows, {'leak': ('leak',)}, ('ve_prompt',)))
    assert verdict['gate_can_fail'] and verdict['passes']
    # With too few permutations the gate cannot fail, and then it does not pass (v4).
    few = run_audits(rows, {'leak': ('leak',)}, feature_sets=('ve_prompt',), which=('logistic',), repeats=1,
                     permutations=9, boot=10, workers=2)
    assert not criterion(few, ('leak',))['gate_can_fail'] and not criterion(few, ('leak',))['passes']
    # A leaking feature is caught (the p-value is two-sided: |AUC - null mean|).
    for i, r in enumerate(rows):
        r['features'][names[0]] = float(i % 2) + .01 * i
    res = run_audits(rows, {'leak': ('leak',)}, feature_sets=('ve_prompt',), which=('logistic',), repeats=2,
                     permutations=39, boot=50, workers=2)
    assert res['ve_prompt']['leak']['models']['logistic']['p_two_sided'] <= .05
    uni = univariate(rows, {'leak': ('leak',)}, ('ve_prompt',))
    assert not criterion(res, ('leak',), uni)['passes'] and uni[('ve_prompt', 'leak', names[0])]['p'] < 1e-6


def _hub_degrees(item):
    edges = M.edges_of(item)
    out, inn = Counter(a for a, _ in edges), Counter(b for _, b in edges)
    return edges, out, inn


def test_v4_hub_symmetry_and_directory_cover_every_candidate_subject():
    """Second-round review leak (a): every candidate certified subject is a hub built from the same
    template (three relation edges to hubs, local links, D + 2 chains), whatever the label, and every
    non-resource entity has a directory entry."""
    for kind in ('honest', 'char_principal', 'group_member', 'role_user', 'alias'):
        item = M.generate(spec('rbac4', 'hex', 'uniform', kind, index=7))
        edges, out, inn = _hub_degrees(item)
        hubs = {item['principal']} | set(item['hubs']['upper']) | set(item['hubs']['lower'])
        roles = item['roles']
        for h in [item['principal'], roles['near_principal'], roles['alias_account'], roles['primary_group'],
                  roles['direct_role']]:
            to_hubs = sum(b in hubs for a, b in edges if a == h)
            assert to_hubs == 3, (kind, h)
            assert 8 <= out[h] <= 13, (kind, h, out[h])  # 3 relations + 1..3 local + 4..7 chains
        in_degrees = [inn[h] for h in hubs]
        assert max(in_degrees) - min(in_degrees) <= 3  # common base + i.i.d. top-up of 0..3
        directory = M.parse_directory(item['raw']['directory.txt'])
        ids = {n for e in edges for n in e}
        assert set(directory.values()) == {n for n in ids if not n.startswith('x_')}


def test_v4_granters_of_the_resource_are_chain_nodes_in_both_labels():
    """Second-round review leak (b): the resource is the end of the same number of chains of the
    principal in both labels (sabotaged: intact spine + D broken decoys; honest: D + 1 broken), and
    both planted resources get the same background-grant distribution."""
    for kind in ('honest', 'leak'):
        item = M.generate(spec('teams', 'numeric', 'community', kind, index=3))
        edges = M.edges_of(item)
        x = item['resource']
        principal_chains = [e for e in edges if e[0] == item['principal']]
        assert len(principal_chains) >= 3 + 1 + 4  # relations + local + spine, decoys, extra
        granters = [a for a, b in edges if b == x]
        assert len(granters) >= 5


def test_byte_sized_items_fit_the_cap_and_seeds_are_new():
    for s in M.design('dev')[:3]:
        item = M.generate(s)
        size = len(M.packet(item).encode())
        assert s['target_bytes'] * .985 <= size <= s['target_bytes'] <= M.BYTES_CAP
    v3 = {M.seed_of(split, i, 'T1d-v3') for split, n in M.SPLITS.items() for i in range(n['binding'] + n['leak'] + n['honest'])}
    v4 = {s['seed'] for split in M.SPLITS for s in M.design(split)}
    assert not v3 & v4
