"""The S3 fixture comparison reports actual outcomes and fails on changed readings."""
from __future__ import annotations

from collections import Counter
import json

import pytest

from conformance import english_lean_s3_compare as C
from conformance import english_lean_s3_python as F
from ve import Environment
from ve.backends import english_lean as adapter
from ve.english import EnglishVocabulary


def _case(fixture_id):
    return next(row for row in C.cases() if row["id"] == fixture_id and row["variant"] == "spec")


def _none_route(_executable, mode, requests):
    assert mode == "english.read"
    answers = []
    for request in requests:
        env = Environment(request["environment"])
        words = EnglishVocabulary(env)
        identities = adapter.identities(env, request["source"], words, request["lexicon"])
        answers.append({"id": request["id"], "status": "ok", "result": {
            "status": "none", "code": "NoDerivation", "text": "No reading.",
            "sentence": 0, "identities": identities}})
    return answers


def test_fixture_corpus_covers_every_spec_fixture_and_its_selected_wording():
    rows = C.cases()
    fixture_ids = {fixture_id for fixture_id, _, _, _ in F._fixtures()}
    assert {(row["id"], row["variant"]) for row in rows if row["variant"] == "spec"} == {
        (fixture_id, "spec") for fixture_id in fixture_ids}
    assert len(rows) > len(fixture_ids)
    assert any(row["variant"] == "python-selection" and "classified as" in row["source"] for row in rows)


def test_comparison_detects_an_accepted_sentence_changed_to_no_reading():
    report = C.compare([_case("or20"), _case("or1")], transport=_none_route)
    assert report["cases"] == 2
    assert report["agreement"] == 1
    assert report["differences"] == 1
    assert report["rows"][0]["record"]["classes"] == []
    assert "verdict" in report["rows"][1]["record"]["classes"]
    assert report["by_environment"]["FO"] == {
        "cases": 2, "agreement": 1, "differences": 1, "lean_statuses": {"none": 2}}


def test_comparison_rejects_a_response_for_a_different_request():
    def wrong_id(executable, mode, requests):
        rows = _none_route(executable, mode, requests)
        rows[0]["id"] = "some-other-request"
        return rows

    report = C.compare([_case("or20")], transport=wrong_id)
    record = report["rows"][0]["record"]
    assert record["lean"]["status"] == "unavailable"
    assert record["lean"]["code"] == "CheckerUnavailable"
    assert report["differences"] == 1


def test_comparison_refuses_an_empty_corpus():
    with pytest.raises(ValueError, match="empty"):
        C.compare([])


def test_committed_report_counts_are_derived_from_individual_records():
    report = json.loads(C.REPORT.read_text())
    rows = report["rows"]
    assert report["cases"] == len(rows) == len(C.cases())
    assert report["agreement"] == sum(not row["record"]["classes"] for row in rows)
    assert report["differences"] == sum(bool(row["record"]["classes"]) for row in rows)
    assert {row["environment"] for row in rows} == set(report["by_environment"])
    for name, summary in report["by_environment"].items():
        own = [row for row in rows if row["environment"] == name]
        assert summary == {
            "cases": len(own),
            "agreement": sum(not row["record"]["classes"] for row in own),
            "differences": sum(bool(row["record"]["classes"]) for row in own),
            "lean_statuses": dict(Counter(row["record"]["lean"]["status"] for row in own)),
        }
