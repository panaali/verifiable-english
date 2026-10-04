"""`tools/lean_first_diff.py`: the base-against-head comparison of the lean-first gate (5.1 item 2)."""
from __future__ import annotations

import json
from pathlib import Path
import re

import pytest

from tools import lean_first_diff as diff
from ve.errors import CheckerUnavailable, InvalidModel, UnknownSymbol

ROOT = Path(__file__).resolve().parents[1]
OK = {"returned": {"values": [True], "environment_id": "e"}}
REJECTED = {"raised": {"code": "UnknownSymbol", "message": "UnknownSymbol: Unknown predicate 'p'"}}


def _write(path: Path, outcomes: dict, source="s", authority="python") -> str:
    """One record per case; a case `name#op` is case `name` of operation `op`."""
    path.write_text("".join(json.dumps({"corpus": "c", "authority": authority, "case": case.split("#")[0],
                                        "op": (case.split("#") + ["op"])[1], "source_sha256": source,
                                        "outcome": outcome}) + "\n"
                            for case, outcome in outcomes.items()))
    return str(path)


# An accepted and a rejected input, the same on both sides, as every real corpus holds.
CONTROLS = {"control-accepted": OK, "control-rejected": REJECTED}


def _expected(expected: dict) -> dict:
    """`expected_cases`' form of {group: cases}: a set names cases recorded through `op` alone; a
    dict gives each case its operations' function."""
    return {group: cases if isinstance(cases, dict) else {case: diff.only("op") for case in cases}
            for group, cases in expected.items()}


def _compare(tmp_path, base, head, delta=None, base_source="s", head_source="s", expected=None, controls=True):
    if controls:
        base, head = {**CONTROLS, **base}, {**CONTROLS, **head}
    if expected is None:
        expected = {("c", "python"): {case.split("#")[0] for case in [*base, *head]}}
    elif controls:
        expected = {group: {**_expected({group: cases})[group], **{case: diff.only("op") for case in CONTROLS}}
                    for group, cases in expected.items()}
    return diff.compare(_write(tmp_path / "base.jsonl", base, base_source),
                        _write(tmp_path / "head.jsonl", head, head_source), delta, expected=_expected(expected))


def test_identical_runs_have_no_difference(tmp_path):
    result = _compare(tmp_path, {"a": OK, "b": REJECTED}, {"a": OK, "b": REJECTED}, controls=False)
    assert result["totals"] == {"same": 2} and result["unlisted"] == 0


@pytest.mark.parametrize("head, klass", [
    ({"returned": {"values": [False], "environment_id": "e"}}, "verdict"),
    ({"returned": {"values": [True], "environment_id": "f"}}, "verdict"),
    ({"returned": {"values": [True]}}, "verdict"),
    ({"raised": {"code": "CheckerUnavailable", "message": "CheckerUnavailable: down"}}, "availability"),
    (REJECTED, "verdict"),
])
def test_each_change_of_an_answer_is_classed(tmp_path, head, klass):
    result = _compare(tmp_path, {"a": OK, "b": OK}, {"a": head, "b": OK})
    assert [row["class"] for row in result["differences"]] == [klass] and result["unlisted"] == 1


def test_a_rejection_with_another_code_is_order_and_its_text_alone_is_wording(tmp_path):
    other = {"raised": {"code": "TypeMismatch", "message": "TypeMismatch: x"}}
    reworded = {"raised": {"code": "UnknownSymbol", "message": "Unknown predicate 'p'"}}
    result = _compare(tmp_path, {"a": REJECTED, "b": reworded}, {"a": other, "b": REJECTED})
    assert [row["class"] for row in result["differences"]] == ["order", "wording"]


def test_only_signed_wording_pairs_and_records_are_accepted(tmp_path):
    reworded = {"raised": {"code": "UnknownSymbol", "message": "Unknown predicate 'p'"}}
    pair = {"base": "Unknown predicate 'p'", "head": "UnknownSymbol: Unknown predicate 'p'"}
    assert _compare(tmp_path, {"a": reworded}, {"a": REJECTED}, {"wording": [pair]})["unlisted"] == 0
    assert _compare(tmp_path, {"a": reworded}, {"a": REJECTED},
                    {"wording": [{**pair, "head": "other"}]})["unlisted"] == 1
    changed = {"returned": {"values": [False], "environment_id": "e"}}
    entry = {"corpus": "c", "authority": "python", "case": "a", "op": "op", "base": OK, "head": changed}
    assert _compare(tmp_path, {"a": OK}, {"a": changed}, {"verdict": [entry]})["unlisted"] == 0
    assert _compare(tmp_path, {"a": OK}, {"a": changed}, {"order": [entry]})["unlisted"] == 1
    assert _compare(tmp_path, {"a": OK}, {"a": changed}, {"verdict": [{**entry, "head": OK}]})["unlisted"] == 1


def _after_op(held):
    """Case `a`'s operations: `op`, then `other` when `op` returned (as `CONFORMANCE_OPS` chains)."""
    return {"op"} | ({"other"} if "returned" in (held.get("op") or {}) else set())


def test_a_missing_record_is_a_difference(tmp_path):
    """An operation that runs on one side only, since what it builds on returned there only."""
    result = _compare(tmp_path, {"a": OK, "a#other": OK}, {"a": REJECTED}, expected={("c", "python"): {"a": _after_op}})
    assert result["unlisted"] == 2
    assert [(row["op"], row["class"], row["head"]) for row in result["differences"]] == [
        ("op", "verdict", REJECTED), ("other", "verdict", None)]


# lf-0 looprecheck1 B1: a recording holds every operation each case requires, not only the case.

@pytest.mark.parametrize("base, head", [
    ({"a": OK, "a#other": OK}, {"a": OK}),                       # a required operation dropped
    ({"a": OK}, {"a": OK}),                                      # ... on both sides
    ({"a": REJECTED, "a#other": OK}, {"a": REJECTED}),           # an operation nothing requires
    ({"a": OK, "a#other": OK, "a#third": OK}, {"a": OK, "a#other": OK, "a#third": OK}),
])
def test_a_recording_must_hold_exactly_the_operations_of_each_case(tmp_path, base, head):
    with pytest.raises(diff.Unusable, match="does not hold the c/python operations"):
        _compare(tmp_path, base, head, expected={("c", "python"): {"a": _after_op}})
    # A probe or pilot case is recorded through its one operation.
    with pytest.raises(diff.Unusable, match="operations"):
        _compare(tmp_path, {"a": OK}, {"a": OK}, expected={("c", "python"): {"a": diff.only("cell")}})


def test_runs_over_different_corpus_files_are_refused(tmp_path):
    with pytest.raises(diff.Unusable, match="different corpus files"):
        _compare(tmp_path, {"a": OK}, {"a": OK}, head_source="t")


# lf-0 review B3: evidence that cannot show preservation gives no verdict.

def test_empty_recordings_are_unusable(tmp_path):
    with pytest.raises(diff.Unusable, match="does not hold"):
        _compare(tmp_path, {}, {}, expected={("c", "python"): {"a"}}, controls=False)
    with pytest.raises(diff.Unusable, match="no case"):
        _compare(tmp_path, {}, {}, expected={("c", "python"): set()}, controls=False)
    with pytest.raises(diff.Unusable, match="no recording"):
        diff.compare(str(tmp_path / "absent"), str(tmp_path / "absent"), None,
                     expected=_expected({("c", "python"): {"a"}}))


@pytest.mark.parametrize("base, head", [
    ({"a": OK}, {"a": OK, "b": OK}),            # a case missing on one side
    ({"a": OK, "b": OK}, {"a": OK}),
    ({"a": OK, "b": OK, "z": OK}, {"a": OK, "b": OK, "z": OK}),  # a case the corpus does not define
])
def test_a_recording_must_hold_exactly_the_corpus(tmp_path, base, head):
    with pytest.raises(diff.Unusable, match="does not hold"):
        _compare(tmp_path, base, head, expected={("c", "python"): {"a", "b"}})


def test_a_missing_authority_is_unusable(tmp_path):
    with pytest.raises(diff.Unusable, match="c/lean"):
        _compare(tmp_path, {"a": OK}, {"a": OK}, expected={("c", "python"): {"a"}, ("c", "lean"): {"a"}})


DOWN = {"raised": {"code": "CheckerUnavailable", "message": "CheckerUnavailable: down"}}
PILOT_DOWN = {"exit": 5, "stderr": [], "stdout": '{"status": "CheckerUnavailable"}'}


@pytest.mark.parametrize("down", [DOWN, PILOT_DOWN, {"timeout": 600}])
def test_wholly_unavailable_recordings_are_unusable(tmp_path, down):
    with pytest.raises(diff.Unusable, match="every c/python record is unavailable"):
        _compare(tmp_path, {"a": down, "b": down}, {"a": down, "b": down}, controls=False)


@pytest.mark.parametrize("constant", [OK, REJECTED, {"exit": 0, "stdout": "{}", "stderr": []},
                                      {"exit": 1, "stdout": "{}", "stderr": []}])
def test_constant_answer_recordings_are_unusable(tmp_path, constant):
    """Two recordings of a checker that accepts (or rejects) everything compare equal: no evidence."""
    with pytest.raises(diff.Unusable, match="every c/python record is"):
        _compare(tmp_path, {"a": constant, "b": constant}, {"a": constant, "b": constant}, controls=False)


def test_a_record_unavailable_on_both_sides_needs_a_signed_reason(tmp_path):
    entry = {"corpus": "c", "authority": "python", "case": "b", "op": "op"}
    other = {"raised": {"code": "CheckerUnavailable", "message": "CheckerUnavailable: other"}}
    for head in (DOWN, other):
        result = _compare(tmp_path, {"a": OK, "b": DOWN}, {"a": OK, "b": head})
        assert result["unlisted"] == 1 and result["differences"][0]["class"] == "unavailable"
        assert _compare(tmp_path, {"a": OK, "b": DOWN}, {"a": OK, "b": head},
                        {"unavailable": [{**entry, "reason": "the readings route needs 1,540 s"}]})["unlisted"] == 0
        for reason in ({}, {"reason": ""}, {"reason": 7}):
            assert _compare(tmp_path, {"a": OK, "b": DOWN}, {"a": OK, "b": head},
                            {"unavailable": [{**entry, **reason}]})["unlisted"] == 1
    # A signed unavailable record does not accept an availability change.
    result = _compare(tmp_path, {"a": OK, "b": DOWN}, {"a": OK, "b": OK},
                      {"unavailable": [{**entry, "reason": "r"}]})
    assert result["unlisted"] == 1 and result["differences"][0]["class"] == "availability"


def test_the_command_exits_2_on_unusable_evidence(tmp_path):
    empty = tmp_path / "empty.jsonl"
    empty.write_text("")
    assert diff.main(["compare", str(empty), str(empty), "--corpus", "conformance", "--authority", "python"]) == 2


def test_expected_cases_come_from_the_corpora():
    expected = diff.expected_cases(ROOT, ("probe", "conformance"), ("python", "lean"))
    assert set(expected) == {("probe", "python"), ("probe", "lean"), ("conformance", "python"),
                             ("conformance", "lean")}
    baseline = json.loads((ROOT / diff.PROBE_BASELINE).read_text())
    assert len(expected["probe", "lean"]) == len(baseline["cells"]) + sum(
        len(baseline[section]) for section in diff.PROBE_SECTIONS) > 0
    assert len(expected["conformance", "python"]) == sum(
        len(json.loads((ROOT / f"conformance/{name}.json").read_text())) for name in diff.CONFORMANCE)


# lf-0 review C: type changes are differences.

@pytest.mark.parametrize("old, new", [([True], [1]), ([False], [0]), ([1], [1.0]), ([0], [False])])
def test_a_type_change_is_a_verdict_difference(tmp_path, old, new):
    base = {"returned": {"values": old, "environment_id": "e"}}
    head = {"returned": {"values": new, "environment_id": "e"}}
    result = _compare(tmp_path, {"a": base}, {"a": head})
    assert [row["class"] for row in result["differences"]] == ["verdict"] and result["unlisted"] == 1
    entry = {"corpus": "c", "authority": "python", "case": "a", "op": "op",
             "base": {"returned": {"values": new, "environment_id": "e"}}, "head": head}
    # A listed entry naming the other type does not accept it either.
    assert _compare(tmp_path, {"a": base}, {"a": head}, {"verdict": [entry]})["unlisted"] == 1
    assert _compare(tmp_path, {"a": base}, {"a": head}, {"verdict": [{**entry, "base": base}]})["unlisted"] == 0


def test_public_records_are_mig3s():
    assert diff.outcome(lambda: (_ for _ in ()).throw(UnknownSymbol("x"))) == {
        "raised": {"code": "UnknownSymbol", "message": "UnknownSymbol: x"}}
    assert diff.outcome(lambda: (_ for _ in ()).throw(InvalidModel("InvalidModel(g): y", generator="g")))[
        "raised"]["generator"] == "g"
    assert diff.outcome(lambda: (_ for _ in ()).throw(CheckerUnavailable("CheckerUnavailable: z")))[
        "raised"]["code"] == "CheckerUnavailable"
    assert diff.public({"record_id": 1, "checker_build": 2, "kept": (1, 2)}) == {"kept": [1, 2]}


def test_the_conformance_corpus_records_every_operation(monkeypatch):
    """The recorder and the completeness check read one table (`CONFORMANCE_OPS`): a recording is
    complete, and the looprecheck1 B1 reproducer, the same recording with only its `environment`
    records, or without one later operation, is unusable."""
    monkeypatch.setenv("VE_AUTHORITY", "python")
    monkeypatch.setattr(diff, "CONFORMANCE", ("validation", "countermodels", "closure"))
    records = {("conformance", "python", r["case"], r["op"]): {"outcome": r["outcome"]}
               for r in diff.conformance_records(ROOT, "python")}
    assert {key[3] for key in records} == {op for op, _, _ in diff.CONFORMANCE_OPS}
    expected = diff.expected_cases(ROOT, ("conformance",), ("python",))
    assert {key[2] for key in records} == expected["conformance", "python"].keys()
    diff.completeness("recording", records, expected)
    environment_only = {key: row for key, row in records.items() if key[3] == "environment"}
    assert len(environment_only) < len(records)
    with pytest.raises(diff.Unusable, match="required operations missing"):
        diff.completeness("recording", environment_only, expected)
    for op, _, _ in diff.CONFORMANCE_OPS[1:]:
        dropped = next(key for key in records if key[3] == op)
        with pytest.raises(diff.Unusable, match=re.escape(f"1 required operations missing (first {dropped[2:]!r})")):
            diff.completeness("recording", {k: v for k, v in records.items() if k != dropped}, expected)


def test_a_message_with_a_line_separator_is_one_record(tmp_path):
    base = {"a": {"raised": {"code": "InvalidInput", "message": "x y\x85z"}}}
    path = _write(tmp_path / "r.jsonl", base)
    assert len(diff.load(path)) == 1
