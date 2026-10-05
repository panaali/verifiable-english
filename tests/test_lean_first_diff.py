"""`tools/lean_first_diff.py`: the base-against-head comparison of the lean-first gate (5.1 item 2)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools import lean_first_diff as diff
from ve.errors import CheckerUnavailable, InvalidModel, UnknownSymbol

ROOT = Path(__file__).resolve().parents[1]
OK = {"returned": {"values": [True], "environment_id": "e"}}
REJECTED = {"raised": {"code": "UnknownSymbol", "message": "UnknownSymbol: Unknown predicate 'p'"}}


def _write(path: Path, outcomes: dict, source="s") -> str:
    path.write_text("".join(json.dumps({"corpus": "c", "authority": "python", "case": case, "op": "op",
                                        "source_sha256": source, "outcome": outcome}) + "\n"
                            for case, outcome in outcomes.items()))
    return str(path)


def _compare(tmp_path, base, head, delta=None, base_source="s", head_source="s"):
    return diff.compare(_write(tmp_path / "base.jsonl", base, base_source),
                        _write(tmp_path / "head.jsonl", head, head_source), delta)


def test_identical_runs_have_no_difference(tmp_path):
    result = _compare(tmp_path, {"a": OK, "b": REJECTED}, {"a": OK, "b": REJECTED})
    assert result["totals"] == {"same": 2} and result["unlisted"] == 0


@pytest.mark.parametrize("head, klass", [
    ({"returned": {"values": [False], "environment_id": "e"}}, "verdict"),
    ({"returned": {"values": [True], "environment_id": "f"}}, "verdict"),
    ({"returned": {"values": [True]}}, "verdict"),
    ({"raised": {"code": "CheckerUnavailable", "message": "CheckerUnavailable: down"}}, "availability"),
    (REJECTED, "verdict"),
])
def test_each_change_of_an_answer_is_classed(tmp_path, head, klass):
    result = _compare(tmp_path, {"a": OK}, {"a": head})
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


def test_a_missing_record_is_a_difference(tmp_path):
    result = _compare(tmp_path, {"a": OK, "b": OK}, {"a": OK})
    assert result["unlisted"] == 1 and result["differences"][0]["head"] is None


def test_runs_over_different_corpus_files_are_refused(tmp_path):
    with pytest.raises(SystemExit, match="different corpus files"):
        _compare(tmp_path, {"a": OK}, {"a": OK}, head_source="t")


def test_public_records_are_mig3s():
    assert diff.outcome(lambda: (_ for _ in ()).throw(UnknownSymbol("x"))) == {
        "raised": {"code": "UnknownSymbol", "message": "UnknownSymbol: x"}}
    assert diff.outcome(lambda: (_ for _ in ()).throw(InvalidModel("InvalidModel(g): y", generator="g")))[
        "raised"]["generator"] == "g"
    assert diff.outcome(lambda: (_ for _ in ()).throw(CheckerUnavailable("CheckerUnavailable: z")))[
        "raised"]["code"] == "CheckerUnavailable"
    assert diff.public({"record_id": 1, "checker_build": 2, "kept": (1, 2)}) == {"kept": [1, 2]}


def test_the_conformance_corpus_records_every_operation(monkeypatch):
    monkeypatch.setenv("VE_AUTHORITY", "python")
    monkeypatch.setattr(diff, "CONFORMANCE", ("validation", "countermodels", "closure"))
    records = list(diff.conformance_records(ROOT, "python"))
    ops = {record["op"] for record in records}
    assert {"environment", "model", "typing", "meaning_id", "evaluate", "countermodel_check"} <= ops
    assert len({record["case"] for record in records}) == sum(
        len(json.loads((ROOT / f"conformance/{name}.json").read_text())) for name in diff.CONFORMANCE)


def test_a_message_with_a_line_separator_is_one_record(tmp_path):
    base = {"a": {"raised": {"code": "InvalidInput", "message": "x y\x85z"}}}
    path = _write(tmp_path / "r.jsonl", base)
    assert len(diff.load(path)) == 1


# lf-1 review B, the class of route_parity.py's empty pass: compare is evidence only over recorded runs.

def _records(path: Path, groups: dict) -> str:
    path.write_text("".join(json.dumps({"corpus": corpus, "authority": authority, "case": case, "op": "op",
                                        "source_sha256": "s", "outcome": outcome}) + "\n"
                            for (corpus, authority), outcomes in groups.items() for case, outcome in outcomes.items()))
    return str(path)


def _full(outcome=OK):
    return {group: {"a": outcome} for group in diff.expected_groups()}


def test_compare_refuses_the_same_file_and_runs_without_records(tmp_path, capsys):
    run = _records(tmp_path / "run.jsonl", _full())
    assert diff.main(["compare", run, run]) == 2
    empty = tmp_path / "empty.jsonl"
    empty.write_text("")
    assert diff.main(["compare", str(empty), run]) == 2
    assert diff.main(["compare", "/dev/null", "/dev/null"]) == 2
    assert "holds no record" in capsys.readouterr().err
    with pytest.raises(SystemExit, match="same file"):
        diff.compare(run, run, None)


def test_compare_fails_when_a_corpus_is_missing_on_a_side(tmp_path):
    full = _full()
    partial_groups = {g: v for g, v in full.items() if g[0] != "pilots"}
    base, head = _records(tmp_path / "b.jsonl", full), _records(tmp_path / "h.jsonl", partial_groups)
    assert diff.main(["compare", base, _records(tmp_path / "h2.jsonl", full)]) == 0
    result = diff.compare(base, head, {"verdict": []}, diff.expected_groups())
    assert result["problems"] == ["HEAD has no record of pilots/default"]
    assert diff.main(["compare", base, head]) == 1
    # A run of one corpus is evidence for that corpus when the comparison names it.
    probe = {g: v for g, v in full.items() if g[0] == "probe"}
    one, other = _records(tmp_path / "p1.jsonl", probe), _records(tmp_path / "p2.jsonl", probe)
    assert diff.main(["compare", one, other]) == 1
    assert diff.main(["compare", one, other, "--corpus", "probe"]) == 0


def test_compare_fails_when_a_corpus_checked_nothing_on_both_sides(tmp_path):
    down = {"raised": {"code": "CheckerUnavailable", "message": "CheckerUnavailable: no service"}}
    groups = {**_full(), ("probe", "lean"): {"a": down, "b": down}}
    base, head = _records(tmp_path / "b.jsonl", groups), _records(tmp_path / "h.jsonl", groups)
    result = diff.compare(base, head, None, diff.expected_groups())
    assert result["unlisted"] == 0 and result["unavailable_both"] == {"probe/lean": 2}
    assert result["problems"] == ["every record of probe/lean is unavailable on both sides"]
    assert diff.main(["compare", base, head]) == 1


def test_a_delta_entry_without_its_outcomes_lists_nothing(tmp_path):
    """A listed record must name both outcomes: an entry without `base` used to accept a record missing
    from BASE (None == None)."""
    base = _records(tmp_path / "b.jsonl", {("c", "python"): {"a": OK}})
    head = _records(tmp_path / "h.jsonl", {("c", "python"): {"a": OK, "b": OK}})
    entry = {"corpus": "c", "authority": "python", "case": "b", "op": "op", "head": OK}
    assert diff.compare(base, head, {"verdict": [entry]})["unlisted"] == 1
    assert diff.compare(base, head, {"verdict": [{**entry, "base": None}]})["unlisted"] == 0


def test_a_delta_listing_a_record_twice_is_unusable(tmp_path):
    """The latency tool's overwrite class (lf-1 recheck B): a record listed in two entries kept only the last."""
    changed = {"returned": {"values": [False], "environment_id": "e"}}
    entry = {"corpus": "c", "authority": "python", "case": "a", "op": "op", "base": OK, "head": changed}
    for delta in ({"verdict": [entry, entry]}, {"order": [{**entry, "head": REJECTED}], "verdict": [entry]}):
        with pytest.raises(diff.Unusable, match="twice"):
            _compare(tmp_path, {"a": OK}, {"a": changed}, delta)


# lf-1 recheck 3 B: the comparison is type-strict JSON equality (the response validator's `same_json`), so a
# boolean answer that came back as an integer, or an integer that came back as a float, is a difference.

@pytest.mark.parametrize("old, new", [(True, 1), (False, 0), (1, 1.0), (0, False), (1.0, 1), (0, -0.0)])
def test_a_retyped_value_is_a_difference_on_every_path(tmp_path, old, new):
    base = {group: {"a": {"returned": {"values": [old]}}} for group in diff.expected_groups()}
    head = {group: {"a": {"returned": {"values": [new]}}} for group in diff.expected_groups()}
    base_path, head_path = _records(tmp_path / "b.jsonl", base), _records(tmp_path / "h.jsonl", head)
    result = diff.compare(base_path, head_path, None, diff.expected_groups())
    assert "same" not in result["totals"] and result["unlisted"] == len(base)
    assert {row["class"] for row in result["differences"]} == {"verdict"}
    assert diff.main(["compare", base_path, head_path]) == 1
    # A delta entry naming the other type lists nothing.
    entry = {"corpus": "c", "authority": "python", "case": "a", "op": "op"}
    retyped = {"returned": {"values": [new]}}
    assert _compare(tmp_path, {"a": {"returned": {"values": [old]}}}, {"a": retyped},
                    {"verdict": [{**entry, "base": {"returned": {"values": [new]}}, "head": retyped}]})["unlisted"] == 1
    assert diff.change_class({"returned": {"values": [old]}}, retyped) == "verdict"


def test_the_reviewers_reproduction_exits_one(tmp_path):
    """`{"values":[true]}` against `{"values":[1]}` exited 0 with `"same": 1`."""
    for old, new in ((True, 1), (False, 0)):
        base = _records(tmp_path / "b.jsonl", {g: {"a": {"returned": {"values": [old]}}} for g in diff.expected_groups()})
        head = _records(tmp_path / "h.jsonl", {g: {"a": {"returned": {"values": [new]}}} for g in diff.expected_groups()})
        assert diff.main(["compare", base, head]) == 1
        assert "same" not in diff.compare(base, head, None)["totals"]


def test_a_wording_pair_matches_only_its_own_types(tmp_path):
    """Python's set membership equates `(true, 2)` with `(1, 2)`; a signed pair names its texts exactly."""
    base, head = {"raised": {"code": "X", "message": 1}}, {"raised": {"code": "X", "message": 2}}
    assert _compare(tmp_path, {"a": base}, {"a": head}, {"wording": [{"base": 1, "head": 2}]})["unlisted"] == 0
    assert _compare(tmp_path, {"a": base}, {"a": head}, {"wording": [{"base": True, "head": 2}]})["unlisted"] == 1
    assert _compare(tmp_path, {"a": base}, {"a": head}, {"wording": [{"base": 1.0, "head": 2}]})["unlisted"] == 1


@pytest.mark.parametrize("case", [1, True, None, 1.0, ["a"]])
def test_a_record_key_that_is_not_a_string_is_unusable(tmp_path, case):
    """Keys `1` and `true` would pair two different records (Python hashes them alike)."""
    path = tmp_path / "r.jsonl"
    path.write_text(json.dumps({"corpus": "c", "authority": "python", "case": case, "op": "op",
                                "source_sha256": "s", "outcome": OK}) + "\n")
    with pytest.raises(diff.Unusable, match="must be strings"):
        diff.load(str(path))
    good = _write(tmp_path / "g.jsonl", {"a": OK})
    entry = {"corpus": "c", "authority": "python", "case": case, "op": "op", "base": OK, "head": OK}
    with pytest.raises(diff.Unusable, match="must be strings"):
        diff.compare(good, _write(tmp_path / "g2.jsonl", {"a": OK}), {"verdict": [entry]})


def test_stage2_parity_classifies_a_retyped_output_as_a_change():
    """The same class in `tools/stage2_parity.py`: its projection was compared with `==`."""
    from tools import stage2_parity
    row = {"cell": "A", "status": "ok", "output": {"values": [True]}}
    assert stage2_parity._classify(row, dict(row)) .startswith("same")
    for new in (1, 1.0):
        assert stage2_parity._classify(row, {**row, "output": {"values": [new]}}) == "different"
