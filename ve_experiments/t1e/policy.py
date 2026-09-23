"""T1e policy semantics (TRUSTED reference) and the prose renderer for rules.

A policy is a set of *access rules* over a fixed relational schema. Each rule is an edge rule

    rel(a, b) and guards(a) and guards(b)  =>  a gets the access of b

with guards that are tag literals: a positive literal is an "only if" condition, a negated literal
an "unless" exception. A principal can access a resource iff the resource is reachable from the
principal by one or more rule steps (least fixpoint; closed world over the listed facts and tags).
This is the T1d Part 2 rule language restricted to a concrete, finite policy snapshot.

A rule is a dict {"relation": rel, "src": [[tag, positive], ...], "dst": [[tag, positive], ...]}.
"src" literals constrain a (the entity that gains access), "dst" literals constrain b.
Standard library only; nothing here imports `ve`.
"""
from __future__ import annotations

from collections import deque
from itertools import product
import json

KINDS = ('user', 'group', 'role', 'resource')
# Attribute tags and the kind each applies to.
ATTRIBUTES = {'contractor': 'user', 'employee': 'user', 'suspended': 'user',
              'external': 'group', 'restricted': 'group',
              'privileged': 'role', 'temporary': 'role',
              'confidential': 'resource', 'public': 'resource', 'archived': 'resource'}
TAGS = KINDS + tuple(ATTRIBUTES)
EXCLUSIVE = (('contractor', 'employee'), ('confidential', 'public'))
# Base relations: (source kinds, destination kinds). rel(a, b) lets a step to b under some rule.
RELATIONS = {
    'member_of': (('user', 'group'), ('group',)),
    'holds': (('user', 'group'), ('role',)),
    'inherits': (('role',), ('role',)),
    'grants': (('role',), ('resource',)),
    'sponsored_by': (('user',), ('group',)),
    'owns': (('user', 'group'), ('resource',)),
}
INHERITANCE = ('member_of', 'inherits', 'sponsored_by')


def attrs_for(kinds):
    return sorted(a for a, k in ATTRIBUTES.items() if k in kinds)


def valid_types(kinds=KINDS):
    """Every tag vector (frozenset: kind + attributes) that satisfies the tag axioms."""
    out = []
    for kind in kinds:
        attrs = attrs_for((kind,))
        for bits in product((False, True), repeat=len(attrs)):
            t = frozenset([kind] + [a for a, b in zip(attrs, bits) if b])
            if not any(x in t and y in t for x, y in EXCLUSIVE):
                out.append(t)
    return out


# ------------------------------------------------------------------ reference semantics (TRUSTED)

def lit_holds(lit, tags):
    tag, positive = lit
    return (tag in tags) == bool(positive)


def rule_allows(rule, tags_a, tags_b):
    return all(lit_holds(l, tags_a) for l in rule['src']) and all(lit_holds(l, tags_b) for l in rule['dst'])


def type_of(world, e):
    return frozenset([world['entities'][e]['kind']] + list(world['entities'][e]['tags']))


def step_edges(world, rules):
    """Every (a, b) with a rule step, and the index of the first rule that allows it."""
    out = {}
    for rel, pairs in world['relations'].items():
        for a, b in pairs:
            ta, tb = type_of(world, a), type_of(world, b)
            for i, r in enumerate(rules):
                if r['relation'] == rel and rule_allows(r, ta, tb):
                    out.setdefault((a, b), i)
                    break
    return out


def reachable(world, rules, start):
    """Entities reachable from start by one or more rule steps."""
    adj = {}
    for a, b in step_edges(world, rules):
        adj.setdefault(a, set()).add(b)
    seen, todo = set(), deque([start])
    while todo:
        n = todo.popleft()
        for m in adj.get(n, ()):
            if m not in seen:
                seen.add(m)
                todo.append(m)
    return seen


def can_access(world, rules, principal, resource):
    return resource in reachable(world, rules, principal)


def fact_steps(world, path):
    """For a list of entities forming a fact path, the relation of each hop."""
    out = []
    for a, b in zip(path, path[1:]):
        rels = [rel for rel, pairs in world['relations'].items() if [a, b] in pairs or (a, b) in pairs]
        out.append(rels)
    return out


def blocked_hops(world, rules, spine):
    """Indices of spine hops that no rule allows (the spine is a list of (a, rel, b))."""
    out = []
    for i, (a, rel, b) in enumerate(spine):
        ta, tb = type_of(world, a), type_of(world, b)
        if not any(r['relation'] == rel and rule_allows(r, ta, tb) for r in rules):
            out.append(i)
    return out


def canonical(rules):
    return json.loads(json.dumps(rules))


# ------------------------------------------------------------------ prose (gold source text)

NOUNS = {  # relation -> (source noun, destination noun)
    'member_of': ('member', 'team'),
    'holds': ('holder', 'role'),
    'inherits': ('inheriting role', 'parent role'),
    'grants': ('role', 'resource'),
    'sponsored_by': ('sponsored user', 'sponsoring team'),
    'owns': ('owner', 'resource'),
}
MAIN = {
    'member_of': ('Members of a team get all of the access that the team has',
                  'Anyone who belongs to a team (directly listed as a member) can access whatever that team can access',
                  'Belonging to a team gives the member the same access as the team'),
    'holds': ('Whoever holds a role gets the access of that role',
              'Holding a role gives the holder everything the role can access',
              'A user or team assigned a role can access what the role can access'),
    'inherits': ('A role that inherits from a parent role also has the access of the parent role',
                 'Roles inherit the access of the parent roles they list',
                 'An inheriting role can access whatever its parent role can access'),
    'grants': ('A role can access every resource that it grants',
               'Each role gives access to the resources listed under its grants',
               'A resource granted by a role is accessible to that role'),
    'sponsored_by': ('A user sponsored by a team inherits the access of that team',
                     'Sponsored users get the access of their sponsoring team',
                     'Sponsorship gives the sponsored user the access of the sponsoring team'),
    'owns': ('Owners can access the resources they own',
             'Whoever owns a resource can access it',
             'A resource is accessible to each of its owners'),
}
TAG_PHRASE = {'contractor': 'a contractor', 'employee': 'an employee', 'suspended': 'suspended',
              'external': 'external', 'restricted': 'restricted', 'privileged': 'privileged',
              'temporary': 'temporary', 'confidential': 'confidential', 'public': 'public',
              'archived': 'archived', 'user': 'a user', 'group': 'a team', 'role': 'a role',
              'resource': 'a resource'}
ONLY_IF = ('but only if', 'provided that', 'but only when')
UNLESS = ('unless', 'except when', 'but not if')
INFORMATIONAL = (
    'Access reviews are carried out every quarter by the security team.',
    'Tags are maintained by the data governance group and may change at any time.',
    'The fact files are exported nightly from the directory service.',
    'Requests for new roles go through the service desk.',
    'Team identifiers start with team_ and role identifiers start with role_.',
    'Suspended accounts are reviewed within five working days.',
    'Each resource lists its classification in resources.yaml.',
    'Questions about this policy go to the access-governance mailbox.',
    'Role descriptions are kept in the internal wiki.',
    'This policy replaces the previous version dated last spring.',
    'Changes to this policy are announced one week in advance.',
    'Audit logs are retained for two years.',
    'Contractor contracts are renewed every six months.',
    'Team leads confirm memberships at the start of each quarter.',
    'The sponsor column in people.csv may list several teams separated by semicolons.',
)


def _cond(lit, side, rel):
    noun = NOUNS[rel][0 if side == 'src' else 1]
    return f'the {noun} is {TAG_PHRASE[lit[0]]}'


def rule_sentence(rule, rng):
    """One English sentence for a rule; wording drawn from rng (paraphrase variety)."""
    rel = rule['relation']
    lits = [('src', l) for l in rule['src']] + [('dst', l) for l in rule['dst']]
    pos = [_cond(l, s, rel) for s, l in lits if l[1]]
    neg = [_cond(l, s, rel) for s, l in lits if not l[1]]
    text = rng.choice(MAIN[rel])
    if pos:
        text += ', ' + rng.choice(ONLY_IF) + ' ' + ' and '.join(pos)
    if neg:
        text += ', ' + rng.choice(UNLESS) + ' ' + ' or '.join(neg)
    return text + '.'


PREAMBLE = ('Access policy. A principal (a user) can access a resource only through a chain of one or '
            'more access steps allowed by the numbered rules below: each rule says when an entity gets '
            'the access of another entity it is linked to in the fact files. Numbered paragraphs that '
            'state no such rule are informational. Tags and links not listed in the fact files do not '
            'hold.')


def render_policy(sections):
    """sections: list of {"n": int, "text": str, "rule": index or None}."""
    lines = [PREAMBLE, '']
    for s in sections:
        lines.append(f'§{s["n"]}. {s["text"]}')
    return '\n'.join(lines) + '\n'
