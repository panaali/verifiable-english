"""ap-4: the `act-readings` relay binds Lean's answer to its request and claims no more (act-phrases 7, AR1 to AR5;
DRI ruling R8; spec SR5).

Genuine answers of the mode are mutated one fault at a time (each member dropped, emptied, retyped, duplicated,
reordered; an index pushed out of range; a span pushed past the phrase; two readings made equal). Every mutant is
`CheckerUnavailable`, unless it only changes content Lean owns and binding cannot see: a text replaced by another, a
reading, an act or an index moved or dropped within the request (AR5: a reading dropped with its row is bound, and no
test claims otherwise). Those are listed in `UNSEEN`, each with its reason.
"""
from __future__ import annotations

import copy
import re

import pytest

from tests import lean_routes
from tests.test_acts_readings_lean import PILOT, V5, frame
from tests.test_discourse_answer import _nodes, _replaced
from ve import acts
from ve.backends import relay
from ve.errors import CheckerUnavailable

pytestmark = pytest.mark.skipif(not lean_routes.SERVICE.exists(), reason="ve_service is not built")

RETYPED = (7, True, None, [], {}, "x", -1, 999)
# Mutants binding cannot see, by the path they change and how (R8: Lean's content, not the request's).
UNSEEN = [
    # a text replaced by another non-empty text: the paraphrase, an act's text or act, a refusal's diagnostic
    (r"\('readings', \d+, 'paraphrase'\) := 'x'", "a paraphrase is Lean's text"),
    (r"\('readings', \d+, 'acts', \d+, '(act|text)'\) := 'x'", "an act's text is Lean's"),
    (r"\('diagnostic',\) := 'x'", "a diagnostic is Lean's text"),
    # the readings, a reading's acts or an act's tokens reordered, or one dropped with its row (AR5)
    (r"\('readings',\) (reversed|first dropped)", "AR5: the readings and their order are Lean's content"),
    (r"\('readings', \d+, 'acts'\) (reversed|first dropped)", "a reading's acts are Lean's content"),
    (r"\('readings', \d+, 'acts', \d+, 'from'\) (reversed|first dropped|first replaced by last|last replaced by first)",
     "which tokens an act reads is Lean's content while each index names a token once"),
    # an index or span moved, still naming a token or lying within the phrase in order
    (r"\('readings', \d+, 'acts', \d+, 'from', \d+\) := -?\d+", "an index that still names a token once"),
    (r"\('tokens', \d+, [01]\) := \d+", "a span bound that keeps the spans within the phrase, in order"),
]


def case_of(name):
    phrase, fixed, block, role, sign = PILOT[name]
    return acts.request(phrase, fixed=fixed, frames=block.get("frames", []), adverbs=block.get("adverbs", []),
                        role=role, sign=sign)


def genuine(case):
    return copy.deepcopy(relay.decide_once(acts.MODE, case))


def bound(row, case):
    """Whether the relay takes `row` as the answer to `case`."""
    try:
        acts.read_answer(row, case)
        return True
    except CheckerUnavailable:
        return False


def mutants(row):
    """One-fault mutants of every node of the row."""
    for path, value in _nodes(row):
        if not path:
            continue
        for other in RETYPED:
            if other != value or type(other) is not type(value):
                yield f"{path} := {other!r}", _replaced(row, path, other)
        if type(value) is int and type(value) is not bool:
            for other in (value + 1, value - 1):
                yield f"{path} := {other}", _replaced(row, path, other)
        if type(value) is str:
            yield f"{path} := ''", _replaced(row, path, "")
        if type(value) is list and value:
            variants = {"duplicated first": [value[0], *value], "duplicated last": [*value, value[-1]],
                        "first replaced by last": [value[-1], *value[1:]],
                        "last replaced by first": [*value[:-1], value[0]],
                        "reversed": value[::-1], "first dropped": value[1:]}
            for name, other in variants.items():
                if other != value:
                    yield f"{path} {name}", _replaced(row, path, other)
        if type(value) is dict:
            for key in value:
                yield f"{path} without {key}", _replaced(row, path, {k: v for k, v in value.items() if k != key})
    for key in row:
        yield f"without {key}", {k: v for k, v in row.items() if k != key}


def unseen(label):
    return any(re.fullmatch(pattern, label) for pattern, _ in UNSEEN)


@pytest.mark.parametrize("name", ["A11", "A12", "A9"])
def test_every_mutant_is_no_answer_or_lean_content_binding_cannot_see(name):
    case = case_of(name)
    row = genuine(case)
    assert bound(row, case)
    accepted = [label for label, mutant in mutants(row) if bound(mutant, case) and not unseen(label)]
    assert not accepted, accepted


def test_a_refusal_and_a_limit_are_bound_and_their_mutants_are_not():
    for case in (acts.request("{0} to seek asylum", frames=V5["frames"], sign=False),
                 acts.request("{0} to seek" + " a" * 200, frames=[frame("seek")])):
        row = genuine(case)
        assert row["verdict"] in ("REFUSED", "LIMIT") and bound(row, case)
        accepted = [label for label, mutant in mutants(row) if bound(mutant, case) and not unseen(label)]
        assert not accepted, accepted
        # a refusal relayed as a listing of nothing, or with a reading, is no answer
        assert not bound({**row, "verdict": "LISTED"}, case)
        listed = genuine(case_of("A11"))
        assert not bound({**row, "readings": listed["readings"]}, case)


def test_ar1_genuine_answer_is_bound_and_shown():
    case = case_of("A11")
    row = genuine(case)
    shown = acts.read_answer(row, case)
    assert shown == {k: row[k] for k in ("verdict", "tokens", "readings")}
    assert shown["verdict"] == "LISTED" and len(shown["readings"]) == 2


def test_ar2_a_token_index_past_the_last_token_is_no_answer():
    case = case_of("A11")
    row = genuine(case)
    row["readings"][0]["acts"][0]["from"][-1] = len(row["tokens"])
    with pytest.raises(CheckerUnavailable, match="a token index is out of range"):
        acts.read_answer(row, case)


def test_ar3_a_span_past_the_phrase_is_no_answer():
    case = case_of("A11")
    row = genuine(case)
    row["tokens"][-1][1] = len(case["phrase"].encode("utf-8")) + 1
    with pytest.raises(CheckerUnavailable, match="a token span is not within the phrase"):
        acts.read_answer(row, case)


def test_ar4_two_equal_readings_are_no_answer():
    case = case_of("A11")
    row = genuine(case)
    row["readings"][1] = copy.deepcopy(row["readings"][0])
    with pytest.raises(CheckerUnavailable, match="two readings have the same acts"):
        acts.read_answer(row, case)
    row = genuine(case)
    row["readings"][1]["paraphrase"] = row["readings"][0]["paraphrase"]
    with pytest.raises(CheckerUnavailable, match="two readings have the same paraphrase"):
        acts.read_answer(row, case)


def test_ar5_a_reading_dropped_with_its_row_is_bound():
    """What binding cannot show (spec 7): Lean's `phraseReadings_exact` covers a missing reading, not the relay."""
    case = case_of("A11")
    row = genuine(case)
    row["readings"] = row["readings"][:1]
    assert acts.read_answer(row, case)["readings"] == row["readings"]


def test_an_index_twice_in_one_act_and_spans_out_of_order_are_no_answer():
    case = case_of("A11")
    row = genuine(case)
    row["readings"][0]["acts"][0]["from"][1] = row["readings"][0]["acts"][0]["from"][0]
    with pytest.raises(CheckerUnavailable, match="a token index occurs twice in one act"):
        acts.read_answer(row, case)
    row = genuine(case)
    row["tokens"][0], row["tokens"][1] = row["tokens"][1], row["tokens"][0]
    with pytest.raises(CheckerUnavailable, match="a token span is not within the phrase, in order and disjoint"):
        acts.read_answer(row, case)


def test_an_answer_to_another_case_is_no_answer():
    case = case_of("A11")
    row = genuine(case)
    assert not bound({**row, "id": "other"}, case)
    assert not bound(row, {**case, "phrase": case["phrase"][:40]})
