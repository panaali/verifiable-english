"""The search-budget relay reads only a typed answer bound to its request (R8).

Genuine `search-budget` rows from the Lean service, over the corpus's answered cases, are mutated one and two
faults at a time: each member dropped, emptied, retyped (null, booleans, an integer, a fraction, a string, an
array, an object), an entry of `sorts` dropped, duplicated, reordered or added, and a field added. Every mutant
is `CheckerUnavailable` from `ve.search._bind_budget` (the relay's binding) or changes nothing it returns: the
budget it binds names only the request's sorts, each at most once, at its position. Another value of the same
type (one budget for another, a negative count aside), or a raised entry made null (the sort searched at the
shared bound again, which can only narrow the search), is Lean's to give: R8 leaves it to Lean.
"""
from __future__ import annotations

from copy import deepcopy
from itertools import combinations

import pytest

from tests.premise_scale_fixtures import search_budget_cases
from ve.backends.relay import rows
from ve.errors import CheckerUnavailable
from ve.search import _bind_budget

RETYPES = (None, True, False, 0, 7, 7.5, -1, "7", "", [], {}, [None])


@pytest.fixture(scope="module")
def genuine():
    cases = [c for c in search_budget_cases() if "sorts" in c and all(type(s) is str for s in c["sorts"])]
    answered = rows("search-budget", cases)
    assert all(row["status"] == "ok" for row in answered)
    return list(zip(cases, answered))


def paths(value, path=()):
    """Every member path of an answer, the answer's own entries of `sorts` included."""
    yield path
    if isinstance(value, dict):
        for key, item in value.items():
            yield from paths(item, (*path, key))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from paths(item, (*path, index))


def at(value, path):
    for key in path:
        value = value[key]
    return value


def single_mutations(row):
    """(name, function from an answer to its mutant) for every one-fault mutation of `row`."""
    for path in paths(row):
        if not path:
            continue
        parent, key = path[:-1], path[-1]

        def drop(r, parent=parent, key=key):
            container = at(r, parent)
            del container[key]
        yield f"drop {path}", drop
        for retype in RETYPES:
            if type(retype) is type(at(row, path)) and retype != -1:
                continue  # another value of the same type is Lean's to give (R8), not a retype
            if retype is None and len(path) == 2 and path[0] == "sorts":
                continue  # a raised entry made null is "not raised": Lean's to say, and it only narrows the search
            def set_(r, parent=parent, key=key, retype=retype):
                at(r, parent)[key] = deepcopy(retype)
            yield f"retype {path} {retype!r}", set_
        if isinstance(at(row, path), list) and at(row, path):
            def duplicate(r, path=path):
                at(r, path).append(deepcopy(at(r, path)[0]))
            yield f"duplicate {path}", duplicate

            def reverse(r, path=path):
                at(r, path).reverse()
            yield f"reverse {path}", reverse
        if isinstance(at(row, path), dict):
            def extra(r, path=path):
                at(r, path)["extra"] = 1
            yield f"extra {path}", extra
    yield "extra top", lambda r: r.__setitem__("extra", 1)
    yield "add sort entry", lambda r: r["sorts"].append({"sort": "principal_type", "least": 3, "most": 3})


def assert_refused_or_same(case, genuine_row, mutant):
    expected = _bind_budget(genuine_row, case)
    try:
        got = _bind_budget(mutant, case)
    except CheckerUnavailable:
        return
    assert got == expected, mutant


def test_genuine_answers_bind(genuine):
    bound = {case["id"]: _bind_budget(row, case).sort_bounds for case, row in genuine}
    assert bound["constants"] == {"principal_type": (3, 3)}
    assert bound["chain"] == {"principal_type": (3, 3)}
    assert bound["plain"] == bound["order"] == bound["capped"] == {}


def test_one_fault_mutants_are_refused_or_change_nothing(genuine):
    total = 0
    for case, row in genuine:
        for name, mutate in single_mutations(row):
            mutant = deepcopy(row)
            mutate(mutant)
            if mutant == row:
                continue
            assert_refused_or_same(case, row, mutant)
            total += 1
    assert total > 200


def test_two_fault_mutants_are_refused_or_change_nothing(genuine):
    total = 0
    for case, row in genuine:
        singles = list(single_mutations(row))
        for (a, first), (b, second) in combinations(singles[::3], 2):
            mutant = deepcopy(row)
            try:
                first(mutant)
                second(mutant)
            except (KeyError, IndexError, TypeError, AttributeError):
                continue  # the first fault removed what the second changes
            if mutant != row:
                assert_refused_or_same(case, row, mutant)
                total += 1
    assert total > 1000


def test_every_field_is_typed(genuine):
    """No member of an answer is read whatever its type: some retype of each is refused."""
    case, row = next((c, r) for c, r in genuine if c["id"] == "constants")
    for path in paths(row):
        if not path:
            continue
        refused = 0
        for retype in RETYPES:
            mutant = deepcopy(row)
            at(mutant, path[:-1])[path[-1]] = deepcopy(retype)
            try:
                _bind_budget(mutant, case)
            except CheckerUnavailable:
                refused += 1
        assert refused, path


def test_an_answer_to_another_request_is_refused(genuine):
    """Rebinding: an answer bound to a case with other sorts or another id is not this case's answer."""
    case, row = next((c, r) for c, r in genuine if c["id"] == "constants")
    for other in ({**case, "sorts": ["principal_type"]}, {**case, "sorts": [*case["sorts"], "extra"]},
                  {**case, "id": "another"}):
        with pytest.raises(CheckerUnavailable):
            _bind_budget(row, other)
    swapped = {**case, "sorts": list(reversed(case["sorts"]))}
    with pytest.raises(CheckerUnavailable):
        _bind_budget(row, swapped)  # each raised entry names the sort at its position
