"""Request binding at the Python side of the Lean question reader."""
from __future__ import annotations

import copy

import pytest

from ve import Environment
from ve.english import EnglishVocabulary
from ve.backends import english_lean
from ve.errors import CheckerUnavailable, SyntaxError


ENV = Environment({
    "language": "ve.core@0", "profile": "relational-fol@0",
    "spec_revision": "ve-v0-draft-2026-09-20",
    "vocabulary": {
        "sorts": {"member": {"description": "Member", "verbalisation":
                             {"singular": "member", "plural": "members"}}},
        "predicates": {"eligible": {"arguments": ["member"], "description": "Eligible",
                                    "verbalisation": "{0} is eligible"}},
        "constants": {"ann": {"sort": "member", "description": "Ann"}},
    },
})
QUESTION = "Is Ann eligible?"


def _answer(case):
    words = EnglishVocabulary(ENV, _defer_overlay_refusals=True)
    return {"status": "one", "form": "fronted", "sentence": "Ann is eligible.",
            "ast": ["unary", "eligible", ["const", "ann"]], "spans": [],
            "identities": {**english_lean.identities(ENV, QUESTION, words, case["lexicon"]),
                           "question_version": "question@1"}}


def test_question_request_reuses_the_selected_english_case(monkeypatch):
    captured = []

    def transport(case):
        captured.append(copy.deepcopy(case))
        return _answer(case)

    monkeypatch.setattr(english_lean, "QUESTION_TRANSPORT", transport)
    words = EnglishVocabulary(ENV, _defer_overlay_refusals=True)
    result = english_lean.read_question(ENV, QUESTION, words, {})
    assert result["ast"] == ["unary", "eligible", ["const", "ann"]]
    assert captured[0] == {**english_lean.request(ENV, QUESTION, words, {}),
                           "id": "english.question", "question": QUESTION}


@pytest.mark.parametrize("mutation", [
    lambda r: r["identities"].update(source_sha256="0" * 64),
    lambda r: r["identities"].pop("environment_id"),
    lambda r: r["identities"].update(question_version=None),
    lambda r: r.update(ast=["unary", "unknown", ["const", "ann"]]),
    lambda r: r.update(ast=["unary", "eligible", ["const", "bo"]]),
])
def test_question_response_must_bind_the_request(monkeypatch, mutation):
    def transport(case):
        answer = _answer(case)
        mutation(answer)
        return answer

    monkeypatch.setattr(english_lean, "QUESTION_TRANSPORT", transport)
    with pytest.raises(CheckerUnavailable):
        english_lean.read_question(ENV, QUESTION, EnglishVocabulary(ENV, _defer_overlay_refusals=True), {})


def test_question_refusal_text_is_preserved(monkeypatch):
    def transport(case):
        answer = _answer(case)
        return {"status": "none", "code": "NoDerivation", "class": "SyntaxError",
                "text": "The question has no reading with the current vocabulary.",
                "identities": answer["identities"]}

    monkeypatch.setattr(english_lean, "QUESTION_TRANSPORT", transport)
    with pytest.raises(SyntaxError) as caught:
        english_lean.read_question(ENV, QUESTION, EnglishVocabulary(ENV, _defer_overlay_refusals=True), {})
    assert str(caught.value) == "The question has no reading with the current vocabulary."
    assert caught.value.lean_question["code"] == "NoDerivation"
