"""Profile-independent, deterministic multi-fault selection for wire tables.

Fault catalogues own their mutations and footprints. Selection uses only phase,
position, and footprint, so profiles share the same tier-A pair/triple policy.
"""

from itertools import combinations
import random


def choose_combinations(faults, *, phase, footprint, pairs=900, triples=600, seed=0):
    """All disjoint same-phase pairs, sampled cross-phase pairs and triples."""
    faults = list(faults)
    rng = random.Random(seed)
    candidate_pairs = [items for items in combinations(faults, 2)
                       if not set(footprint(items[0])) & set(footprint(items[1]))]
    same = [items for items in candidate_pairs if phase(items[0]) == phase(items[1])]
    cross = [items for items in candidate_pairs if phase(items[0]) != phase(items[1])]
    yield from same
    yield from rng.sample(cross, min(pairs, len(cross)))
    candidates = [items for items in combinations(faults, 3)
                  if len({phase(item) for item in items}) >= 2
                  and all(not set(footprint(a)) & set(footprint(b))
                          for a, b in combinations(items, 2))]
    yield from rng.sample(candidates, min(triples, len(candidates)))


def first_fault(combo, *, position):
    """The oracle's first independent fault in table expansion order."""
    return min(combo, key=position)
