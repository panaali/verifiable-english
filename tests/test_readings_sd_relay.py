"""The relay of Lean's soft-completion rows (rd-9-soft-chain.md 3; plan SC-4, SC-8): Python checks the row's schema
and its binding to the request (DRI ruling R8), never its meaning. A genuine Lean row passes; every mutation of a
field the relay binds, retyped or rebound, is `CheckerUnavailable`.
"""
from __future__ import annotations

import copy

import pytest

from tests import lean_routes
from tests.test_readings_s1_lean import run
from tests.test_readings_sd_lean import LEAN, doc4, env4, fsd1
from ve import readings_route
from ve.errors import CheckerUnavailable


@pytest.fixture(scope="module")
def lean():
    if not lean_routes.SERVICE.exists():
        pytest.skip("the Lean service has not been built")
    return LEAN


def _case(kind, raw, document):
    return {"id": kind, "kind": kind, "environment": raw, "document": document}


@pytest.fixture(scope="module")
def elaborated(lean):
    raw = env4()
    case = _case("readings-elaborate", raw, doc4(raw))
    [row] = run(lean, [case])
    assert row["status"] == "ok", row
    return row, case


@pytest.fixture(scope="module")
def validated(lean):
    raw, document, _ = fsd1()
    case = _case("readings-validate", raw, document)
    [row] = run(lean, [case])
    assert row["status"] == "ok", row
    return row, case


def test_genuine_soft_rows_pass_the_relay(elaborated, validated):
    row, case = elaborated
    readings_route._completion_elaborate(copy.deepcopy(row), case)
    row, case = validated
    readings_route._check(copy.deepcopy(row), case)


def _soft(row):
    return row["soft_premises"][1]["premises"]


MUTATIONS = {
    "soft_premises dropped": lambda row: row.pop("soft_premises"),
    "soft_premises emptied": lambda row: row.__setitem__("soft_premises", []),
    "soft_premises retyped": lambda row: row.__setitem__("soft_premises", {}),
    "entry duplicated": lambda row: row["soft_premises"].append(copy.deepcopy(row["soft_premises"][0])),
    "entries reordered": lambda row: row["soft_premises"].reverse(),
    "index out of range": lambda row: row["soft_premises"][1].__setitem__("index", 7),
    "set renamed": lambda row: row["soft_premises"][0].__setitem__("set", "rs9"),
    "label of an undeclared rule": lambda row: _soft(row)[0].__setitem__(
        "label", "soft:exception:no-such-rule:sufficient:0"),
    "coherence of an undeclared rule": lambda row: _soft(row)[1].__setitem__(
        "label", "soft:coherence:must-x,no-such-rule"),
    "label of another kind": lambda row: _soft(row)[0].__setitem__("label", "unsaid:pair:x_required,x_permitted"),
    "exception role unknown": lambda row: _soft(row)[0].__setitem__("label", "soft:exception:must-x:other:0"),
    "label retyped": lambda row: _soft(row)[0].__setitem__("label", 7),
    "ast null": lambda row: _soft(row)[0].__setitem__("ast", None),
    "premise duplicated": lambda row: _soft(row).append(copy.deepcopy(_soft(row)[0])),
    "an F_p unit on the soft chain": lambda row: row["filled"]["units"].append(
        {"unit": "unsaid--y-permitted", "content": {"norm": {
            "name": "unsaid--y-permitted", "predicate": "y_permitted", "sign": True, "mode": "strict",
            "guard": ["unary", "unsaid__y_permitted", ["var", 0]], "unless": [], "over": [], "rank": None,
            "alterable": [], "exception": None, "hard": False}}}),
}


@pytest.mark.parametrize("name", sorted(MUTATIONS))
def test_a_mutated_soft_row_is_unavailable(elaborated, name):
    row, case = elaborated
    mutant = copy.deepcopy(row)
    MUTATIONS[name](mutant)
    with pytest.raises(CheckerUnavailable):
        readings_route._completion_elaborate(mutant, case)


def test_two_faults_together_are_unavailable(elaborated):
    """Two faults at once: a reordered entry list and a relabelled premise."""
    row, case = elaborated
    mutant = copy.deepcopy(row)
    MUTATIONS["entries reordered"](mutant)
    mutant["soft_premises"][0]["premises"][0]["label"] = "soft:coherence:a,b"
    with pytest.raises(CheckerUnavailable):
        readings_route._completion_elaborate(mutant, case)


@pytest.mark.parametrize("name", ["soft_premises dropped", "soft_premises retyped", "entries reordered"])
def test_a_mutated_soft_validate_row_is_unavailable(validated, name):
    row, case = validated
    mutant = copy.deepcopy(row)
    MUTATIONS[name](mutant)
    with pytest.raises(CheckerUnavailable):
        readings_route._check(mutant, case)


# `readings-verdicts` under the soft completion (plan SC-5, SC-8): the answer's soft labels are bound to the rules the
# request declares (`readings_route.soft_label`, the one binder `soft_premises` uses too).

@pytest.fixture(scope="module")
def coherent_conflict(lean):
    from tests.test_readings_sd_lean import _packages, _verdicts
    raw = env4()
    raw["vocabulary"]["predicates"]["x_permitted"]["regulated"]["default"] = "allow"
    document = doc4(raw)
    need_not, readings = document["units"][0]["content"], document["reading_sets"][0]["readings"]
    evidence = [{"choice": [["rs1", i]], "conflict": {"packages": _packages(
        lean, raw, document, [("rs1", i)], need_not, readings[i]["content"])}} for i in (0, 1)]
    case = _case("readings-verdicts", raw, document)
    case.update(question="conflict", evidence=evidence, assumed=[["rs1", 1]])
    row = _verdicts(lean, raw, document, "conflict", evidence, assumed=[["rs1", 1]])
    assert row["result"]["conditional_on"] == ["soft:coherence:must-x,need-not-x"], row
    return row, case


def _verdicts_frame(case):
    from ve.readings_verdicts import _Frame
    return _Frame(case, [[["rs1", 0]], [["rs1", 1]]], True, ["rs1"])


def test_a_genuine_soft_verdict_binds(coherent_conflict):
    from ve.readings_verdicts import _check_answer
    row, case = coherent_conflict
    _check_answer(copy.deepcopy(row), case, _verdicts_frame(case))


@pytest.mark.parametrize("label", ["soft:coherence:must-x,no-such-rule", "soft:coherence:must-x,must-x",
                                   "soft:coherence:must-x", "soft:exception:no-such-rule:sufficient:0",
                                   "soft:exception:must-x:other:0", "soft:exception:must-x:sufficient:01",
                                   "soft:exception:must-x", "soft:other:must-x"])
def test_a_soft_label_the_request_does_not_declare_is_unavailable(coherent_conflict, label):
    from ve.readings_verdicts import _check_answer
    row, case = coherent_conflict
    mutant = copy.deepcopy(row)
    mutant["labels"] = [label]
    with pytest.raises(CheckerUnavailable):
        _check_answer(mutant, case, _verdicts_frame(case))
