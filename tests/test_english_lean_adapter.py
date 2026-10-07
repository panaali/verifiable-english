"""E2 English admission: Lean authority, comparator isolation, and response binding."""
from __future__ import annotations

import copy
import hashlib
import json

import pytest

from ve import Environment
from ve import english as EN
from ve import english_grammar as EG
from ve.backends import english_lean as L
from ve.errors import CheckerUnavailable, SyntaxError, VEError


ENV = Environment({
    "language": "ve.core@0", "profile": "relational-fol@0", "spec_revision": "ve-v0-draft-2026-09-20",
    "vocabulary": {
        "sorts": {"item": {"description": "Item", "verbalisation": {"singular": "service", "plural": "services"}},
                  "agent": {"description": "Agent", "verbalisation": {"singular": "person", "plural": "people"}}},
        "predicates": {
            "active": {"arguments": ["item"], "description": "Deployed", "verbalisation": "{0} is deployed"},
            "reviewed": {"arguments": ["item"], "description": "Reviewed", "verbalisation": "{0} is reviewed"},
            "owns": {"arguments": ["agent", "item"], "description": "Owner", "verbalisation": "{0} owns {1}"}},
        "constants": {"legacy": {"sort": "item", "description": "Legacy"},
                      "alice": {"sort": "agent", "description": "Alice"}}}})
SOURCE = "Legacy is deployed."


def test_default_admission_calls_lean_and_not_python(monkeypatch):
    original = L.read
    calls = []
    def recorded(*args, **kwargs):
        calls.append((args, kwargs))
        return original(*args, **kwargs)
    monkeypatch.setattr(L, "read", recorded)
    monkeypatch.setattr(EN, "_python_reading", lambda *_args: pytest.fail("Python decided admission"))
    document = EN.parse_english(ENV, SOURCE)
    assert [EN.ast._to_data(f) for f in document.formulas] == [
        ["unary", "active", ["const", "legacy"]]]
    assert len(calls) == 1


def test_comparator_failure_cannot_change_lean_verdict(monkeypatch, tmp_path):
    log = tmp_path / "shadow.jsonl"
    monkeypatch.setenv("VE_ENGLISH_COMPARATOR", "1")
    monkeypatch.setenv("VE_SHADOW_LOG", str(log))
    monkeypatch.setattr(EN, "_python_reading", lambda *_args: (_ for _ in ()).throw(SyntaxError("planted")))
    assert EN.parse_english(ENV, SOURCE)
    records = [json.loads(line) for line in log.read_text().splitlines()]
    assert len(records) == 1
    assert records[0]["lean"]["status"] == "one"
    assert records[0]["python"]["class"] == "SyntaxError"


@pytest.mark.parametrize("override", ["python", "shadow", "rust-experimental"])
def test_other_authorities_cannot_decide_admission(monkeypatch, override):
    monkeypatch.setenv("VE_AUTHORITY_OVERRIDES", f"english.admission={override}")
    with pytest.raises(CheckerUnavailable, match="Lean-authoritative"):
        EN.parse_english(ENV, SOURCE)


def test_missing_or_malformed_reader_is_checker_unavailable(monkeypatch):
    def unavailable(_case):
        raise CheckerUnavailable("unavailable")
    monkeypatch.setattr(L, "TRANSPORT", unavailable)
    with pytest.raises(CheckerUnavailable, match="unavailable"):
        EN.parse_english(ENV, SOURCE)
    monkeypatch.setattr(L, "TRANSPORT", lambda _case: {"status": "one"})
    with pytest.raises(CheckerUnavailable):
        EN.parse_english(ENV, SOURCE)


def test_genuine_response_and_field_mutations_fail_closed():
    words = EN.EnglishVocabulary(ENV)
    case = L.request(ENV, SOURCE, words, {})
    response = L._transport(case)
    expected = L.identities(ENV, SOURCE, words, case["lexicon"])
    assert L.response_problem(response, expected, ENV, SOURCE) is None
    for field in response:
        mutated = copy.deepcopy(response)
        del mutated[field]
        assert L.response_problem(mutated, expected, ENV, SOURCE), field
        for value in (7, True, None, [], {}, ""):
            if type(value) is type(response[field]) and value == response[field]:
                continue
            mutated = copy.deepcopy(response)
            mutated[field] = value
            assert L.response_problem(mutated, expected, ENV, SOURCE), (field, value)
    for field in expected:
        mutated = copy.deepcopy(response)
        mutated["identities"][field] = "0" * 64
        assert L.response_problem(mutated, expected, ENV, SOURCE), field


def test_class_and_span_are_part_of_diagnostic_schema():
    words = EN.EnglishVocabulary(ENV)
    source = "Every sevice is reviewed."
    case = L.request(ENV, source, words, {})
    answer = L._transport(case)
    expected = L.identities(ENV, source, words, case["lexicon"])
    assert L.response_problem(answer, expected, ENV, source) is None
    for field in ("class", "span"):
        mutated = copy.deepcopy(answer)
        del mutated[field]
        assert L.response_problem(mutated, expected, ENV, source)
    mutated = copy.deepcopy(answer)
    mutated["class"] = "ResourceLimit"
    assert L.response_problem(mutated, expected, ENV, source)


def test_request_and_lock_identities():
    words = EN.EnglishVocabulary(ENV)
    case = L.request(ENV, SOURCE, words, {})
    assert set(case) == {"id", "environment", "lexicon", "source", "mode", "cap"}
    assert case["mode"] == "authoring" and case["cap"] == 2
    ids = L.identities(ENV, SOURCE, words, case["lexicon"])
    assert ids["source_sha256"] == hashlib.sha256(SOURCE.encode()).hexdigest()
    assert ids["lexicon_id"] == EG.lexicon_id(case["lexicon"])
    assert EG.actions_version() == json.loads((EG.HERE / "LOCK.json").read_text())["actions_version"]
