"""Selection and oracle rules are independent of any profile catalogue."""

from conformance.wire_contract import choose_combinations, first_fault


def test_disjoint_footprints_and_first_position():
    faults = [
        ("a", 1, (1, 0), ("/x",)),
        ("b", 1, (1, 1), ("/y",)),
        ("c", 2, (2, 0), ("/x",)),
        ("d", 2, (2, 1), ("/z",)),
    ]
    options = dict(phase=lambda fault: fault[1], footprint=lambda fault: fault[3],
                   pairs=10, triples=10, seed=7)
    chosen = list(choose_combinations(faults, **options))
    assert chosen == list(choose_combinations(faults, **options))
    assert (faults[0], faults[1]) in chosen
    assert (faults[0], faults[2]) not in chosen
    for combo in chosen:
        assert len({p for fault in combo for p in fault[3]}) == len(combo)
        assert first_fault(combo, position=lambda fault: fault[2]) == min(
            combo, key=lambda fault: fault[2])
