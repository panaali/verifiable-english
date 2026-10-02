"""Profile-independent, deterministic multi-fault selection for wire tables.

Fault catalogues own their mutations and footprints. Selection uses only phase,
position, and footprint, so profiles share the same tier-A pair/triple policy.
"""

from itertools import combinations
import random


def choose_combinations(faults, *, phase, footprint, pairs=900, triples=600, seed=0, overlaps=None):
    """All disjoint same-phase pairs, sampled cross-phase pairs and triples. Two footprints are disjoint
    when `overlaps` says they are not; by default, when they share no element."""
    faults = list(faults)
    rng = random.Random(seed)
    prints = [footprint(fault) for fault in faults]
    overlaps = overlaps or (lambda a, b: bool(set(a) & set(b)))
    clash = {(i, j) for i, j in combinations(range(len(faults)), 2) if overlaps(prints[i], prints[j])}
    index = {id(fault): i for i, fault in enumerate(faults)}

    def disjoint(a, b):
        i, j = sorted((index[id(a)], index[id(b)]))
        return (i, j) not in clash
    candidate_pairs = [items for items in combinations(faults, 2) if disjoint(*items)]
    same = [items for items in candidate_pairs if phase(items[0]) == phase(items[1])]
    cross = [items for items in candidate_pairs if phase(items[0]) != phase(items[1])]
    yield from same
    yield from rng.sample(cross, min(pairs, len(cross)))
    candidates = [items for items in combinations(faults, 3)
                  if len({phase(item) for item in items}) >= 2
                  and all(disjoint(a, b) for a, b in combinations(items, 2))]
    yield from rng.sample(candidates, min(triples, len(candidates)))


def first_fault(combo, *, position):
    """The oracle's first independent fault in table expansion order."""
    return min(combo, key=position)
