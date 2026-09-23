"""Mixed-format fact files for T1e: writers and the TRUSTED loader.

Five files per policy, in three formats:

* ``people.csv``       users: id, name, employment (contractor/employee/blank), status
                       (active/suspended), sponsors (team ids separated by ";")    -> sponsored_by
* ``teams.yaml``       teams: id, tags (external/restricted), members (users or teams), roles
                                                                                  -> member_of, holds
* ``roles.json``       roles: id, tags (privileged/temporary), inherits (parent roles), grants
                                                                                  -> inherits, grants
* ``assignments.csv``  user, role                                                 -> holds
* ``resources.yaml``   resources: id, classification (confidential/public/internal), archived,
                       owners (users or teams)                                    -> owns

The loader (`load`) maps the files to the fixed relational schema of ``policy.py``; every arm
receives the same loaded facts, so the untrusted artefact covers the prose rules only. The YAML
used here is a small fixed subset (block sequence of mappings, flow lists, scalars); the loader
rejects anything else. Standard library only.
"""
from __future__ import annotations

import csv
import io
import json

FILES = ('people.csv', 'teams.yaml', 'roles.json', 'assignments.csv', 'resources.yaml')

SCHEMA = """Fixed fact schema (the trusted loader builds these from the fact files; all arms use it).
Entities: every id listed in people.csv (kind user), teams.yaml (group), roles.json (role),
resources.yaml (resource).
Kind tags:      user(x), group(x), role(x), resource(x)
Attribute tags: contractor(x) / employee(x)  people.csv employment column
                suspended(x)                 people.csv status column is "suspended"
                external(x), restricted(x)   teams.yaml tags
                privileged(x), temporary(x)  roles.json tags
                confidential(x), public(x)   resources.yaml classification ("internal" = neither)
                archived(x)                  resources.yaml archived: true
Relations (a, b):
  member_of(a, b)     a is listed under members of team b (a is a user or a team)
  holds(a, b)         a user a has role b in assignments.csv, or role b is listed under roles of team a
  inherits(a, b)      role b is listed under inherits of role a (b is a parent role of a)
  grants(a, b)        resource b is listed under grants of role a
  sponsored_by(a, b)  team b is listed in the sponsors column of user a
  owns(a, b)          a is listed under owners of resource b (a is a user or a team)
Everything not listed is false (closed world).
"""


def _flow(values):
    return '[' + ', '.join(values) + ']'


def write(world, names, rng):
    """world: {"entities": {id: {"kind", "tags"}}, "relations": {rel: [[a, b], ...]}} -> {file: text}."""
    ents = world['entities']
    rel = {r: [tuple(p) for p in world['relations'].get(r, [])] for r in
           ('member_of', 'holds', 'inherits', 'grants', 'sponsored_by', 'owns')}
    of_kind = lambda k: [e for e in ents if ents[e]['kind'] == k]
    users, groups, roles, res = (of_kind(k) for k in ('user', 'group', 'role', 'resource'))
    for xs in (users, groups, roles, res):
        rng.shuffle(xs)

    out = io.StringIO()
    w = csv.writer(out, lineterminator='\n')
    w.writerow(['id', 'name', 'employment', 'status', 'sponsors'])
    for u in users:
        tags = set(ents[u]['tags'])
        emp = 'contractor' if 'contractor' in tags else 'employee' if 'employee' in tags else ''
        sponsors = sorted(b for a, b in rel['sponsored_by'] if a == u)
        rng.shuffle(sponsors)
        w.writerow([u, names.get(u, ''), emp, 'suspended' if 'suspended' in tags else 'active', ';'.join(sponsors)])
    people = out.getvalue()

    lines = ['teams:']
    for g in groups:
        members = [a for a, b in rel['member_of'] if b == g]
        team_roles = [b for a, b in rel['holds'] if a == g]
        rng.shuffle(members); rng.shuffle(team_roles)
        lines += [f'- id: {g}', f'  tags: {_flow(sorted(ents[g]["tags"]))}',
                  f'  members: {_flow(members)}', f'  roles: {_flow(team_roles)}']
    teams = '\n'.join(lines) + '\n'

    role_rows = []
    for r in roles:
        inh = [b for a, b in rel['inherits'] if a == r]
        gr = [b for a, b in rel['grants'] if a == r]
        rng.shuffle(inh); rng.shuffle(gr)
        role_rows.append({'id': r, 'tags': sorted(ents[r]['tags']), 'inherits': inh, 'grants': gr})
    roles_json = json.dumps({'roles': role_rows}, indent=2) + '\n'

    out = io.StringIO()
    w = csv.writer(out, lineterminator='\n')
    w.writerow(['user', 'role'])
    pairs = [(a, b) for a, b in rel['holds'] if ents[a]['kind'] == 'user']
    rng.shuffle(pairs)
    for a, b in pairs:
        w.writerow([a, b])
    assignments = out.getvalue()

    lines = ['resources:']
    for x in res:
        tags = set(ents[x]['tags'])
        cls = 'confidential' if 'confidential' in tags else 'public' if 'public' in tags else 'internal'
        owners = [a for a, b in rel['owns'] if b == x]
        rng.shuffle(owners)
        lines += [f'- id: {x}', f'  classification: {cls}', f'  archived: {"true" if "archived" in tags else "false"}',
                  f'  owners: {_flow(owners)}']
    resources = '\n'.join(lines) + '\n'
    return {'people.csv': people, 'teams.yaml': teams, 'roles.json': roles_json,
            'assignments.csv': assignments, 'resources.yaml': resources}


# ------------------------------------------------------------------ TRUSTED loader

class FactError(ValueError):
    pass


def _yaml_list(text, top, keys):
    """Parse the fixed YAML subset: `top:` then `- k: v` blocks with exactly `keys` in order."""
    lines = [l for l in text.split('\n') if l.strip()]
    if not lines or lines[0] != f'{top}:':
        raise FactError(f'{top}: missing header')
    rows, cur = [], None
    for line in lines[1:]:
        if line.startswith('- '):
            cur = {}
            rows.append(cur)
            body = line[2:]
        elif line.startswith('  ') and cur is not None:
            body = line[2:]
        else:
            raise FactError(f'{top}: bad line {line!r}')
        key, sep, value = body.partition(': ')
        if not sep or key in cur:
            raise FactError(f'{top}: bad entry {line!r}')
        value = value.strip()
        if value.startswith('['):
            if not value.endswith(']'):
                raise FactError(f'{top}: bad list {line!r}')
            inner = value[1:-1].strip()
            value = [v.strip() for v in inner.split(',')] if inner else []
        cur[key] = value
    for r in rows:
        if list(r) != list(keys):
            raise FactError(f'{top}: unexpected keys {list(r)}')
    return rows


def load(files):
    """{file: text} -> world. Raises FactError on anything outside the fixed formats."""
    ents, rels = {}, {r: set() for r in ('member_of', 'holds', 'inherits', 'grants', 'sponsored_by', 'owns')}

    def add(e, kind, tags):
        if e in ents:
            raise FactError(f'duplicate id {e}')
        ents[e] = {'kind': kind, 'tags': sorted(tags)}

    people = list(csv.reader(io.StringIO(files['people.csv'])))
    if people[0] != ['id', 'name', 'employment', 'status', 'sponsors']:
        raise FactError('people.csv header')
    sponsors = []
    for row in people[1:]:
        uid, _, emp, status, sp = row
        if emp not in ('', 'contractor', 'employee') or status not in ('active', 'suspended'):
            raise FactError(f'people.csv row {row}')
        add(uid, 'user', ([emp] if emp else []) + (['suspended'] if status == 'suspended' else []))
        sponsors += [(uid, g) for g in sp.split(';') if g]
    teams = _yaml_list(files['teams.yaml'], 'teams', ('id', 'tags', 'members', 'roles'))
    for t in teams:
        if not set(t['tags']) <= {'external', 'restricted'}:
            raise FactError(f'teams.yaml tags {t["tags"]}')
        add(t['id'], 'group', t['tags'])
    roles = json.loads(files['roles.json'])['roles']
    for r in roles:
        if set(r) != {'id', 'tags', 'inherits', 'grants'} or not set(r['tags']) <= {'privileged', 'temporary'}:
            raise FactError(f'roles.json entry {r}')
        add(r['id'], 'role', r['tags'])
    resources = _yaml_list(files['resources.yaml'], 'resources', ('id', 'classification', 'archived', 'owners'))
    for x in resources:
        cls, arch = x['classification'], x['archived']
        if cls not in ('confidential', 'public', 'internal') or arch not in ('true', 'false'):
            raise FactError(f'resources.yaml entry {x}')
        add(x['id'], 'resource', ([cls] if cls != 'internal' else []) + (['archived'] if arch == 'true' else []))

    for a, g in sponsors:
        rels['sponsored_by'].add((a, g))
    for t in teams:
        rels['member_of'].update((m, t['id']) for m in t['members'])
        rels['holds'].update((t['id'], r) for r in t['roles'])
    for r in roles:
        rels['inherits'].update((r['id'], p) for p in r['inherits'])
        rels['grants'].update((r['id'], x) for x in r['grants'])
    assign = list(csv.reader(io.StringIO(files['assignments.csv'])))
    if assign[0] != ['user', 'role']:
        raise FactError('assignments.csv header')
    rels['holds'].update((a, b) for a, b in assign[1:])
    for x in resources:
        rels['owns'].update((o, x['id']) for o in x['owners'])

    from .policy import RELATIONS
    for rel, pairs in rels.items():
        sk, dk = RELATIONS[rel]
        for a, b in pairs:
            if a not in ents or b not in ents or ents[a]['kind'] not in sk or ents[b]['kind'] not in dk:
                raise FactError(f'{rel}({a}, {b}): unknown id or wrong kind')
    return {'entities': dict(sorted(ents.items())),
            'relations': {r: sorted([list(p) for p in ps]) for r, ps in rels.items()}}


def normalise(world):
    """Canonical form of a world (sorted), for equality checks."""
    return {'entities': {e: {'kind': v['kind'], 'tags': sorted(v['tags'])} for e, v in sorted(world['entities'].items())},
            'relations': {r: sorted([list(p) for p in world['relations'].get(r, [])])
                          for r in ('member_of', 'holds', 'inherits', 'grants', 'sponsored_by', 'owns')}}
