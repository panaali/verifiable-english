"""Source generation and independent, closed-world RBAC ground truth."""
from collections import defaultdict, deque
import csv
import hashlib
import io
import json
import random
import re

SEEDS = {'dev': 202609230100, 'gate': 202609240100, 'full': 202609250100}
SEMANTICS = '''This is the complete, case-sensitive, monotone RBAC policy. There are no denies,
wildcards, implicit grants, or external memberships. Identifiers are exact strings.
CSV member,group means member belongs to group, transitively through nested groups.
YAML principal,role grants that role to the principal (user or group); role,resource
lets holders of that role access the resource. Repeated principals accumulate grants.
Prose inheritance means the named inheriting role receives all permissions of the
other role, transitively. Access is a directed path through these facts.''' 


def bfs(edges, start, end):
    adjacency = defaultdict(list)
    for a, b in edges:
        adjacency[a].append(b)
    parents, todo = {start: None}, deque([start])
    while todo:
        a = todo.popleft()
        for b in adjacency[a]:
            if b not in parents:
                parents[b] = a
                todo.append(b)
    path = []
    if end in parents:
        node = end
        while node is not None:
            path.append(node)
            node = parents[node]
        path.reverse()
    return {'reachable': end in parents, 'path': path, 'visited': sorted(parents)}


def source_rows(raw):
    rows = []
    for filename, body in raw.items():
        for n, line in enumerate(body.splitlines(), 1):
            if line and line not in ('member,group', 'bindings:'):
                rows.append({'id': f'{filename}:{n}', 'text': line, 'file': filename})
    return rows


def parse_row(row):
    line = row['text']
    if row['file'] == 'membership.csv':
        a, b = next(csv.reader([line]))
    elif row['file'] == 'bindings.yaml':
        match = re.fullmatch(r'  - \{(principal|role): ([a-z0-9_]+), (role|resource): ([a-z0-9_]+)\}', line)
        if not match or (match[1], match[3]) not in (('principal', 'role'), ('role', 'resource')):
            raise ValueError('invalid YAML binding')
        a, b = match[2], match[4]
    else:
        patterns = [r'Role ([a-z0-9_]+) inherits all permissions of role ([a-z0-9_]+)\.',
                    r'Every permission of role ([a-z0-9_]+) is also a permission of role ([a-z0-9_]+)\.',
                    r'Holders of role ([a-z0-9_]+) receive the permissions of role ([a-z0-9_]+)\.']
        for i, pattern in enumerate(patterns):
            match = re.fullmatch(pattern, line)
            if match:
                a, b = (match[2], match[1]) if i == 1 else (match[1], match[2])
                break
        else:
            raise ValueError('invalid inheritance rule')
    return [a, b]


def generate(seed, grants, sabotaged, *, positive=False):
    rng = random.Random(seed)
    used = set()
    def name(prefix):
        while True:
            value = f'{prefix}_{rng.randrange(16**4):04x}'
            if value not in used:
                used.add(value)
                return value
    user, target = name('u'), name('x')
    # Shared suffix names make decoys visually close without label/position leakage.
    groups = [name('g') for _ in range(rng.randint(2, 6))]
    # Exactly 6..10 hops, at least two roles (a real inheritance step).
    nroles = rng.randint(max(2, 5-len(groups)), min(4, 9-len(groups)))
    roles = [name('r') for _ in range(nroles)]
    spine = [user, *groups, *roles, target]
    planted = list(zip(spine, spine[1:]))
    facts = []
    def add_path(nodes, broken=None):
        for i, (a, b) in enumerate(zip(nodes, nodes[1:])):
            if i == broken:
                # A near-matching principal, with no incoming link, breaks only this path.
                a = a + '_v2'
            kind = 'csv' if b.startswith('g_') else 'prose' if a.startswith('r_') and b.startswith('r_') else 'yaml'
            facts.append((kind, a, b))
    add_path(spine, None if sabotaged else rng.randrange(1, len(spine)-2))
    for d in range(7):
        decoy = [user, *[g + f'_d{d}' for g in groups], *[r + f'_d{d}' for r in roles], target]
        add_path(decoy, rng.randrange(1, len(decoy)-2))
    # A substantial unrelated RBAC network; all group edges increase layer.
    users = [name('u') for _ in range(24)]
    layers = [[name('g') for _ in range(15)] for _ in range(6)]
    role_layers = [[name('r') for _ in range(20)] for _ in range(3)]
    resources = [name('x') for _ in range(30)]
    seen = {(a, b) for _, a, b in facts}
    while len(facts) < grants:
        choice = rng.randrange(4)
        if choice == 0:
            level = rng.randrange(6)
            a, b = rng.choice(users if level == 0 else layers[level-1]), rng.choice(layers[level])
            kind = 'csv'
        elif choice == 1:
            a, b = rng.choice(users + sum(layers, [])), rng.choice(role_layers[0])
            kind = 'yaml'
        elif choice == 2:
            level = rng.randrange(2)
            a, b = rng.choice(role_layers[level]), rng.choice(role_layers[level+1])
            kind = 'prose'
        else:
            a, b = rng.choice(sum(role_layers, [])), rng.choice(resources)
            kind = 'yaml'
        if (a, b) not in seen:
            seen.add((a, b))
            facts.append((kind, a, b))
    rng.shuffle(facts)
    csv_lines, yaml_lines, prose = ['member,group'], ['bindings:'], []
    for kind, a, b in facts:
        if kind == 'csv':
            csv_lines.append(f'{a},{b}')
        elif kind == 'yaml':
            yaml_lines.append(f'  - {{role: {a}, resource: {b}}}' if b.startswith('x_') else f'  - {{principal: {a}, role: {b}}}')
        else:
            prose.append(rng.choice([f'Role {a} inherits all permissions of role {b}.',
                                    f'Every permission of role {b} is also a permission of role {a}.',
                                    f'Holders of role {a} receive the permissions of role {b}.']))
    raw = {'bindings.yaml': '\n'.join(yaml_lines)+'\n', 'membership.csv': '\n'.join(csv_lines)+'\n',
           'inheritance.txt': '\n'.join(prose)+'\n'}
    edges = [parse_row(r) for r in source_rows(raw)]
    assert {tuple(e) for e in edges} == {(a,b) for _,a,b in facts}
    truth = bfs(edges, user, target)
    assert len(edges) == grants and truth['reachable'] == sabotaged
    if sabotaged:
        assert 6 <= len(truth['path'])-1 <= 10
        assert all(not bfs([e for e in edges if e != list(p)], user, target)['reachable'] for p in planted)
    claim = f'{user} {"can" if positive else "cannot"} access {target}.'
    return {'id': hashlib.sha256(str(seed).encode()).hexdigest()[:12], 'seed': seed, 'grants': grants,
            'raw': raw, 'user': user, 'target': target, 'claim': claim, 'positive': positive,
            'sabotaged': truth['reachable'] != positive, 'truth': truth, 'edges': edges,
            'max_group_depth': len(groups)}


def dataset(split):
    count, sizes = (20, [1500,5000]) if split == 'gate' else (40, [1500,5000]) if split == 'full' else (8, [1500,5000])
    result = []
    for size in sizes:
        labels = [False, True] * (count//2)
        random.Random(SEEDS[split]+size).shuffle(labels)
        for i, sabotaged in enumerate(labels):
            result.append(generate(SEEDS[split]+size*100+i, size, sabotaged,
                                   positive=(split == 'dev' and i % 2 == 1)))
    return result


def packet(item):
    return SEMANTICS + '\n\n' + '\n'.join(f'FILE {name}\n{body}' for name, body in item['raw'].items()) + '\nCLAIM: ' + item['claim']
