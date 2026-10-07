"""The public fault order and texts of malformed reports documents (lf-8 recheck B1).

Lean names every fault of a reports document (`lean/VE/Attribution/Preflight.lean`) in the
pre-batch Python's order and with its texts. The differential test runs every document of
`tests/reports_fault_corpus.py` (one- and two-fault mutants of a rich valid document) through
the public `check_document` and compares each answer with the base's
(`tests/data/reports_base_faults.json`, recorded at `9aaf918d` by
`docs/lean-first/b8/record_faults.py`). Every difference must fall in a group that
`docs/lean-first/b8/DELTA.md` lists for the DRI; the counts are the committed evidence.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from reports_fault_corpus import GROUPS, cases, classify, digest, outcome, seed, text
from ve.document import check_document
from ve.profiles import LANGUAGE, SPEC_REVISION

ROOT = Path(__file__).resolve().parents[1]
BASE = json.loads((ROOT / "tests/data/reports_base_faults.json").read_text())
EVIDENCE = json.loads((ROOT / "docs/lean-first/b8/evidence/fault-delta.json").read_text())


def answer(tmp_path, meta, source):
    path = tmp_path / "case.md"
    path.write_text(text(meta, source))
    return outcome(check_document, path)


def test_the_base_recording_is_for_this_corpus():
    assert BASE["checkout"] == "9aaf918d" and BASE["digest"] == digest(LANGUAGE, SPEC_REVISION)
    assert set(BASE["outcomes"]) == {case_id for case_id, _, _ in cases(LANGUAGE, SPEC_REVISION)}


def test_every_difference_from_the_base_is_a_listed_group(tmp_path):
    head = {case_id: answer(tmp_path, meta, source) for case_id, meta, source in cases(LANGUAGE, SPEC_REVISION)}
    result = classify(BASE["outcomes"], head)
    assert result["unlisted"] == []
    assert result == EVIDENCE
    delta = (ROOT / "docs/lean-first/b8/DELTA.md").read_text()
    for group in GROUPS:
        assert f"| {group} |" in delta and f"| {EVIDENCE['groups'][group]:,} |" in delta, group


def test_the_classifier_can_fail():
    """A changed text, a changed order and a changed verdict are each unlisted."""
    base = {"a": "VEError: InvalidInput: context c1", "b": "VEError: InvalidInput: bridge",
            "a & b": "VEError: InvalidInput: context c1", "units.4.x=int": "VEError: Expected a JSON object",
            "units.4.x=int & a": "VEError: InvalidInput: context c1"}
    for case_id, changed in (("a", "VEError: object expected"), ("a & b", "VEError: InvalidInput: bridge"),
                             ("b", "OK UNVERIFIED"), ("units.4.x=int & a", "VEError: object expected")):
        assert classify(base, {**base, case_id: changed})["unlisted"] == [case_id]
    assert classify(base, {**base, "units.4.x=int": "VEError: object expected"})["groups"]["W8.2"] == 1


def edited(**changes):
    meta, source = seed(LANGUAGE, SPEC_REVISION)
    for key, value in changes.items():
        meta[key] = value(copy.deepcopy(meta)) if callable(value) else value
    return meta, source


def with_row(section, index, **fields):
    def change(meta):
        meta[section][index].update(fields)
        return meta[section]
    return change


def without(section, index, field):
    def change(meta):
        del meta[section][index][field]
        return meta[section]
    return change


def with_act(act):
    def change(meta):
        meta["units"][0]["content"]["report"]["act"] = act
        return meta["units"]
    return change


@pytest.mark.parametrize("changes,expected", [
    # The reviewer's reproducers: each named its record before the batch.
    pytest.param({"bridges": "ab"}, "VEError: InvalidInput: bridge", id='bridges-string'),
    pytest.param({"bridges": {"id": "b1"}}, "VEError: InvalidInput: bridge", id='bridges-object'),
    pytest.param({"bridges": [7]}, "VEError: InvalidInput: bridge", id='bridges-int-row'),
    pytest.param({"scoped": "ab"}, "VEError: InvalidInput: scoped", id='scoped-string'),
    pytest.param({"scoped": {"id": "s1"}}, "VEError: InvalidInput: scoped", id='scoped-object'),
    pytest.param({"scoped": [7]}, "VEError: InvalidInput: scoped", id='scoped-int-row'),
    pytest.param({"contexts": with_row("contexts", 0, extra=1)},
                 "VEError: InvalidInput: context c1", id='context-extra-field'),
    pytest.param({"contexts": without("contexts", 0, "description")},
                 "VEError: InvalidInput: context c1", id='context-missing-field'),
    pytest.param({"assessments": with_row("assessments", 0, necessary=[["unary", "nope", ["const", "alice"]]])},
                 "UnknownSymbol: UnknownSymbol: Unknown predicate 'nope'", id='necessary-unknown-predicate'),
    pytest.param({"assessments": with_row("assessments", 0, version="1")},
                 "VEError: InvalidInput: assessment a1", id='version-string'),
    # Fault order: an assessment's fault precedes the bridges' and the units'.
    pytest.param({"assessments": with_row("assessments", 0, decided_by=""), "bridges": [7]},
                 "VEError: InvalidInput: assessment a1 needs decided_by", id='decided-by-before-bridges'),
    pytest.param({"assessments": with_row("assessments", 0, decided_by=""), "units": with_act("promised")},
                 "VEError: InvalidInput: assessment a1 needs decided_by", id='decided-by-before-units'),
    # null is not absence where Python's None was not.
    pytest.param({"contexts": None}, "VEError: InvalidInput: contexts must be a list", id='contexts-null'),
    pytest.param({"contexts": with_row("contexts", 0, tense=None)},
                 "VEError: ContextTense: c1", id='tense-null'),
    pytest.param({"assessments": with_row("assessments", 0, necessary=None)},
                 "VEError: InvalidInput: assessment a1", id='necessary-null'),
    pytest.param({"bridges": with_row("bridges", 0, path=None)},
                 "VEError: InvalidInput: bridge path", id='bridge-path-null'),
    pytest.param({"bridges": [None]}, "VEError: InvalidInput: bridge", id='bridges-null-row'),
    pytest.param({"bridges": ""}, "VEError: array expected", id='bridges-empty-string'),
    # A Python formula decoder text, under its code (W8.1).
    pytest.param({"assessments": with_row("assessments", 0, necessary=[7])},
                 "SyntaxError: SyntaxError: AST nodes must be nonempty tagged JSON arrays", id='necessary-not-a-formula'),
])
def test_reviewer_reproducers_keep_the_base_answer(tmp_path, changes, expected):
    assert answer(tmp_path, *edited(**changes)) == expected


def test_null_where_python_read_none_as_absent_is_accepted(tmp_path):
    """`reference_time`, `literal`, a package's statement and a scoped check's certificate
    may be null, as before the batch."""
    def null_statement(meta):
        meta["units"][4]["content"]["report"]["content"]["definition"]["content"] = None
        meta["units"][0]["content"]["report"]["content"]["report"]["literal"] = None
        return meta["units"]
    meta, source = edited(units=null_statement, scoped=with_row("scoped", 0, certificate=None))
    meta["scoped"].pop()  # s2's payload is the statement now removed
    assert answer(tmp_path, meta, source) == "OK UNVERIFIED"
