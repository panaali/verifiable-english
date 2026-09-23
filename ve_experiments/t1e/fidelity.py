"""Authoring-fidelity audit for T1e (independent of the author; no model calls).

An authored artefact (any arm) is FAITHFUL for an item iff
  1. it is well formed: every numbered section of policy.md has exactly one anchor, in order,
     quoting the section text verbatim; and every rule unit is inside the rewritable fragment
     (one relation literal plus tag guards) or the section is marked informational;
  2. its unit semantics equal the gold rule of the section (exact, per section; informational
     sections must be marked informational), AND
  3. its trusted execution agrees with the reference semantics of the gold rules on the item's own
     query and on N perturbed worlds (tags re-drawn, facts added/removed, random principal and
     resource), in the style of P3's differential testing.

(2) is exact for canonical-fragment artefacts; (3) is what catches wrong closure/query code in the
script arm and anything outside the fragment. The gate uses (1)-(3) jointly.
"""
from __future__ import annotations

import random

from . import arms as A
from .materials import NEXT, _tags
from .policy import RELATIONS, can_access


def perturb(world, rng, p_tag=.3, edits=6):
    ents = {e: {'kind': v['kind'], 'tags': list(v['tags'])} for e, v in world['entities'].items()}
    for e, v in ents.items():
        if rng.random() < p_tag:
            v['tags'] = _tags(rng, v['kind'])
    rels = {r: {tuple(p) for p in world['relations'].get(r, [])} for r in RELATIONS}
    names = sorted(ents)
    for _ in range(edits):
        if rng.random() < .5:
            r = rng.choice(sorted(RELATIONS))
            if rels[r]:
                rels[r].discard(rng.choice(sorted(rels[r])))
        else:
            a, b = rng.choice(names), rng.choice(names)
            opts = [rel for rel, k in NEXT[ents[a]['kind']] if k == ents[b]['kind']]
            if a != b and opts:
                rels[rng.choice(opts)].add((a, b))
    return {'entities': ents, 'relations': {r: sorted([list(p) for p in ps]) for r, ps in rels.items()}}


def structure(arm, text, item):
    """(ok, detail, per-section semantic rules or None)."""
    try:
        _, secs, _ = A.split_sections(arm, text)
    except ValueError as exc:
        return False, str(exc), None
    want = [(s['n'], A.anchor(arm, s)) for s in item['sections']]
    got = [(n, a) for n, a, _ in secs]
    if got != want:
        return False, 'anchors differ from the numbered sections', None
    sem = []
    for (n, _, lines), s in zip(secs, item['sections']):
        try:
            sem.append(A.unit_semantics(arm, lines))
        except Exception as exc:
            return False, f'§{n}: {exc}', None
    return True, '', sem


def _norm(rule):
    if rule is None:
        return None
    return (rule['relation'], sorted(map(tuple, rule['src'])), sorted(map(tuple, rule['dst'])))


def audit(arm, text, item, n_worlds=100, seed=0):
    ok, detail, sem = structure(arm, text, item)
    exact = ok and all(_norm(u) == _norm(None if s['rule'] is None else item['rules'][s['rule']])
                       for u, s in zip(sem, item['sections']))
    rng = random.Random(seed)
    users = [e for e, v in item['world']['entities'].items() if v['kind'] == 'user']
    res = [e for e, v in item['world']['entities'].items() if v['kind'] == 'resource']
    worlds = [(item['world'], item['principal'], item['resource'])]
    for _ in range(n_worlds):
        worlds.append((perturb(item['world'], rng), rng.choice(users), rng.choice(res)))
    disagreements = invalid = 0
    for w, p, r in worlds:
        out = A.execute(arm, text, w, p, r)
        if out['status'] != 'ok':
            invalid += 1
        elif out['can_access'] != can_access(w, item['rules'], p, r):
            disagreements += 1
    return {'well_formed': ok, 'detail': detail, 'exact_units': exact, 'worlds': len(worlds),
            'disagreements': disagreements, 'invalid': invalid,
            'faithful': ok and exact and disagreements == 0 and invalid == 0}
