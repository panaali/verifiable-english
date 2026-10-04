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
