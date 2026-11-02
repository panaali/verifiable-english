"""The `document` mode's `undeclared_evaluative` field (judgment-terms-PLAN.md JT-3, part jt-3a; docs/spec/
judgment-terms.md 7, 8.4 and 11.7): Lean's list of the base predicates whose words match english-lean's catalogue
and that are not bound, and its relay (schema and binding only, R8).

Lean decides which predicates match; this file sends spec 11.7's predicates through the service and compares Lean's
answer with the spec's values, in Lean's order (the vocabulary's members by name). The relay binds each name to a
base predicate of the request (a regulated one included, not W3-defined) that is not a declared open term, in that
order with no repeat. A name Lean leaves out is Lean's decision, so dropping one is relayed as it is.
"""
from __future__ import annotations

import pytest

from tests.test_judgments_answer import relayed
from tests.test_judgments_document import ALPHA, J1, conj, defined, document, opened, record, regulated, u, unit
from ve.backends.lean_service import LeanService

# Spec 11.7's predicates, the regulated `make_reasonable_efforts` (F3′), a W3-defined name whose word matches a row,
# and two predicates whose words come from their `verbalisation`.
ACT = {"arguments": ["act"], "description": "an act"}
VOCAB = {
    "sorts": {"person": {"description": "a person"}, "act": {"description": "an act"}},
    "predicates": {**{p: dict(ACT) for p in ("reasonable_grounds", "due_date", "arbitrary", "just_as_real",
                                             "just_requirement", "necessary_condition", "arrest")},
                   "trial": {**ACT, "verbalisation": "{0} is a fair trial"},
                   "deadline": {**ACT, "verbalisation": "{0} is the due date"},
                   "reasonable_detention": defined(conj(u("arrest"), u("arbitrary"))),
                   "subjects": regulated("{0} prevent {1}", "person", "act"),
                   "make_reasonable_efforts": regulated("{0} do y to {1}", "person", "act")},
    "constants": {}}
BOUND = (J1, [unit("u1", opened("arbitrary"), ALPHA)])
UNBOUND = ([], [unit("u1", content=ALPHA)])
# Lean's values: 11.7's rows with `J = [arbitrary]` and `J = []`, with the regulated predicate and the two templates.
EXPECTED = {
    "bound": ["just_requirement", "make_reasonable_efforts", "reasonable_grounds", "trial"],
    "unbound": ["arbitrary", "just_requirement", "make_reasonable_efforts", "reasonable_grounds", "trial"],
}


@pytest.fixture(scope="module")
def service():
    with LeanService() as instance:
        yield instance


@pytest.fixture(scope="module")
def genuine(service):
    out = {}
    for name, (records, units) in {"bound": BOUND, "unbound": UNBOUND}.items():
        case = {"id": "d", "document": document(service, units, records, vocabulary=VOCAB), "admit": False}
        out[name] = case, service.run("document", [case])[0]
    return out


@pytest.mark.parametrize("name", EXPECTED)
def test_lean_lists_the_catalogue_matches_that_are_not_bound(genuine, name):
    """Spec 11.7: `due_date`, `just_as_real`, `necessary_condition` and `deadline` ("the due date") have the word in
    another sense; `arrest` and `subjects` match no row; `reasonable_detention` is W3-defined; `arbitrary` is listed
    only while unbound. The regulated `make_reasonable_efforts` is listed (F3′)."""
    case, row = genuine[name]
    assert row["status"] == "ok", row
    assert row["undeclared_evaluative"] == EXPECTED[name]
    assert relayed(case, row)


def test_a_regulated_predicate_is_listed_and_still_not_admitted(service, genuine):
    """F3′: listing `make_reasonable_efforts` for review does not make it admissible as a judgment (11.7)."""
    case, row = genuine["bound"]
    assert "make_reasonable_efforts" in row["undeclared_evaluative"] and relayed(case, row)
    records = [*J1, {**J1[0], "name": "make_reasonable_efforts", "arguments": ["person", "act"]}]
    case = {"id": "d", "document": document(service, BOUND[1], records, vocabulary=VOCAB), "admit": False}
    assert service.run("document", [case])[0] == {"id": "d", "status": "error",
                                                 "error": "JudgmentRegulated: make_reasonable_efforts"}


def mutants(names):
    """Each retyping of the field and of one member, each duplication, and each name that is no base predicate of the
    request or is a bound judgment."""
    deep = []
    for _ in range(10_000):
        deep = [deep]
    for value in (7, True, None, {}, "reasonable_grounds", 1.5, [[]], [7], [None], [True], ["\ud800"], [""],
                  [["reasonable_grounds"]], deep):
        yield f"retyped {repr(value)[:40]}", value
    for i, name in enumerate(names):
        yield f"member {i} retyped", [*names[:i], 7, *names[i + 1:]]
        yield f"member {i} doubled", [*names[:i + 1], name, *names[i + 1:]]
    yield "reversed", names[::-1]
    for extra in ("arbitrary", "absent", "reasonable_detention", "act", "person", "u1", "Reasonable_grounds"):
        yield f"{extra} added", sorted([*names, extra])


@pytest.mark.parametrize("name", EXPECTED)
def test_every_mutant_of_the_field_is_refused(genuine, name):
    """A bound judgment (`arbitrary` under `J1`), a W3-defined name, a sort, a unit id, an undeclared name, a repeat, a
    retyped member and a reordered list are refused by the schema or the binding."""
    case, row = genuine[name]
    names = row["undeclared_evaluative"]
    seen = 0
    for label, mutated in mutants(names):
        if mutated == names:
            continue
        seen += 1
        assert not relayed(case, {**row, "undeclared_evaluative": mutated}), label
    assert seen > 20


def test_a_bound_judgment_listed_is_refused_and_unbound_it_is_relayed(genuine):
    """Both directions of the binding on the one name: `arbitrary` is relayed where it is not a declared open term
    and refused where it is."""
    case, row = genuine["bound"]
    assert not relayed(case, {**row, "undeclared_evaluative": ["arbitrary", *row["undeclared_evaluative"]]})
    case, row = genuine["unbound"]
    assert "arbitrary" in row["undeclared_evaluative"] and relayed(case, row)


@pytest.mark.parametrize("names, accepted", [
    (["just_requirement", "reasonable_grounds"], True),
    ([], True),
    (["arrest", "due_date", "make_reasonable_efforts", "subjects"], True),
    (["reasonable_grounds", "just_requirement"], False),
    (["just_requirement", "just_requirement"], False),
], ids=["a name dropped", "empty", "other base predicates", "out of order", "repeated"])
def test_which_predicates_match_is_lean_s(genuine, names, accepted):
    """The binding decides no match: a bound list other than Lean's is relayed as it is (R8); only a list out of
    Lean's order, with a repeat, or naming what is not a base predicate is refused."""
    case, row = genuine["bound"]
    assert relayed(case, {**row, "undeclared_evaluative": names}) == accepted


def test_the_field_is_there_exactly_under_the_profile(service, genuine):
    """Under `judgments@0` an answer without the field is unbound; without the profile the answer has none, and one
    added is extra."""
    case, row = genuine["bound"]
    assert not relayed(case, {k: v for k, v in row.items() if k != "undeclared_evaluative"})
    plain = ["definitions@0", "documents@1", "norms@0", "relational-fol@0"]
    case = {"id": "d", "document": document(service, UNBOUND[1], [], vocabulary=VOCAB, profiles=plain),
            "admit": False}
    row = service.run("document", [case])[0]
    assert row["status"] == "ok" and "undeclared_evaluative" not in row and relayed(case, row)
    assert not relayed(case, {**row, "undeclared_evaluative": ["reasonable_grounds"]})


def test_a_vocabulary_at_the_predicate_limit_is_reported_whole(service):
    """The report reads each predicate once; its size is the vocabulary's, which `max_predicates` (256) bounds: a
    vocabulary of 256 matching predicates is answered whole, and one more is `ResourceLimit` before any report."""
    def case(n):
        vocabulary = {"sorts": {"act": {"description": "an act"}},
                      "predicates": {f"reasonable_{i:03d}": dict(ACT) for i in range(n)}, "constants": {}}
        return {"id": "d", "document": document(service, [unit("u1", content={"ast": ["top"]})], [],
                                                vocabulary=vocabulary), "admit": False}
    row = service.run("document", [case(256)])[0]
    assert row["status"] == "ok" and row["undeclared_evaluative"] == [f"reasonable_{i:03d}" for i in range(256)]
    assert relayed(case(256), row)
    row = service.run("document", [case(257)])[0]
    assert row["status"] == "error" and row["error"] == "ResourceLimit: vocabulary size"


# jt-3p (DRI 2026-10-31, reviews/dri-decisions-20261031-jt-3a.md item 3): the catalogue's phrase row "good judgment".
GOOD_VOCAB = {
    "sorts": {"act": {"description": "an act"}},
    "predicates": {**{p: dict(ACT) for p in ("good_judgment", "good_conduct", "judgment_good", "court_judgment",
                                             "arrest")},
                   "judgment_use": {**ACT, "verbalisation": "{0} uses good judgment"}},
    "constants": {}}
GOOD_ALPHA = {"ast": ["forall", "act", ["implies", conj(u("arrest"), u("good_judgment")), ["bottom"]]]}


@pytest.mark.parametrize("records, units, expected", [
    ([], [unit("u1", content=GOOD_ALPHA)], ["good_judgment", "judgment_use"]),
    ([record("good_judgment")], [unit("u1", opened("good_judgment"), GOOD_ALPHA)], ["judgment_use"]),
], ids=["unbound", "bound"])
def test_the_good_judgment_phrase_row_is_listed_only_where_written_in_order(service, records, units, expected):
    """A row's word is a phrase: `good_judgment` (and a template that writes "good judgment") is listed while
    unbound and left out once bound; `good_conduct`, `judgment_good` and `court_judgment` hold only part of the
    phrase, or both words out of order, and are never listed."""
    case = {"id": "d", "document": document(service, units, records, vocabulary=GOOD_VOCAB), "admit": False}
    row = service.run("document", [case])[0]
    assert row["status"] == "ok", row
    assert row["undeclared_evaluative"] == expected
    assert relayed(case, row)
