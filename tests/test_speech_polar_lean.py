"""Speech acts' F1 polar questions and their `Must`/`Can` refusal, read by Lean (question answering Q1.4).

`parse_speech` sends a wording that begins with one of the contract's speech-acts prefixes (`speechPrefixes`) to
`english.question` with `caller` "speech-acts" and relays the answer; `Is <Name> …?` stays Python's until Q1.4b.
"""
from __future__ import annotations

import copy

import pytest

from ve import speech_english
from ve.backends import english_lean, relay
from ve.english import EnglishVocabulary
from ve.errors import CheckerUnavailable, VEError
from ve.speech_english import parse_speech

from test_question_reading import _mutants
from test_speech_acts import environment

ENV = environment()
MODAL_TEXT = "ModalQuestion: choose an explicit question"
SPEECH = english_lean.SPEECH_CALLER


def words(env=ENV):
    return EnglishVocabulary(env, _defer_overlay_refusals=True)


def case(question: str, caller: str | None = SPEECH) -> dict:
    """The request `read_question` sends for `question`."""
    out = {**english_lean.request(ENV, question, words(), {}), "id": english_lean.QUESTION_MODE,
           "question": question}
    return out if caller is None else {**out, "caller": caller}


def live(question: str, caller: str | None = SPEECH) -> dict:
    row = relay.decide_once(english_lean.QUESTION_MODE, case(question, caller))
    assert row.get("status") == "ok", row
    return row["result"]


@pytest.fixture
def calls(monkeypatch):
    """The callers of every `read_question` call the speech parser makes."""
    seen = []

    def spy(*args, caller=None, **kwargs):
        seen.append(caller)
        return english_lean.read_question(*args, caller=caller, **kwargs)

    monkeypatch.setattr(speech_english, "read_question", spy)
    return seen


# ------------------------------------------------------------------ the routed prefixes

def test_the_routed_prefixes_are_the_contracts():
    assert english_lean.QUESTION_CALLERS == {SPEECH: ("Is it the case that ", "Must ", "Can ")}
    assert speech_english._LEAN_PREFIXES == english_lean.QUESTION_CALLERS[SPEECH]


@pytest.mark.parametrize("wording, body", [
    ("Is it the case that atlas is reviewed?", ["unary", "reviewed", ["const", "atlas"]]),
    ("Is it the case that every service is reviewed?", ["forall", "service", ["unary", "reviewed", ["var", 0]]]),
    ("  Is it the case that atlas is reviewed?\n", ["unary", "reviewed", ["const", "atlas"]]),
])
def test_an_f1_question_is_leans_reading(calls, wording, body):
    assert parse_speech(ENV, wording, ENV.speech_acts) == ({"mode": "polar", "body": body}, "question")
    assert calls == [SPEECH]


@pytest.mark.parametrize("wording", ["Is it the case that?", "Is it the case thatatlas is reviewed?",
                                     "is it the case that atlas is reviewed?", "Is atlas reviewed?"])
def test_a_wording_without_the_f1_prefix_is_not_sent(calls, wording):
    """The prefix's boundary: no space after `that`, a lower-case `is`, and F2 (Python's until Q1.4b)."""
    try:
        parse_speech(ENV, wording, ENV.speech_acts)
    except VEError:
        pass
    assert calls == []


def test_an_f1_refusal_is_leans_text_and_span(calls):
    with pytest.raises(VEError) as caught:
        parse_speech(ENV, "Is it the case that atlas is checked?", ENV.speech_acts)
    assert caught.value.lean_question["code"] == "NoDerivation"
    assert str(caught.value).startswith("The question has no reading with the current vocabulary.")
    assert caught.value.span is not None and calls == [SPEECH]


# ------------------------------------------------------------------ the ModalQuestion refusal

@pytest.mark.parametrize("wording", ["Must alice open the desk?", "Can alice open the desk?", "Can check.",
                                     "Must check.", "Must alice?", "Can ?", "Must is it the case that?"])
def test_a_modal_wording_gets_leans_refusal(calls, wording):
    with pytest.raises(VEError) as caught:
        parse_speech(ENV, wording, ENV.speech_acts)
    assert type(caught.value) is VEError and str(caught.value) == MODAL_TEXT and caught.value.span is None
    assert caught.value.lean_question["code"] == "ModalQuestion" and calls == [SPEECH]


@pytest.mark.parametrize("wording", ["Must", "Can", "Must ", "Mustard is reviewed?", "Canned check.",
                                     "must alice open the desk?", "MUST check.", "May alice open the desk?",
                                     "Must\talice open the desk?"])
def test_a_wording_near_a_modal_one_is_not_refused_as_modal(calls, wording):
    """Around the boundary: no space after the word (a trailing space is trimmed), a longer word, another case, another
    word, another space."""
    with pytest.raises(VEError) as caught:
        parse_speech(ENV, wording, ENV.speech_acts)
    assert str(caught.value) != MODAL_TEXT and calls == []


def test_lean_refuses_as_modal_only_for_the_speech_caller():
    assert live("Must alice open the desk?")["code"] == live("Can check.")["code"] == "ModalQuestion"
    # `ve ask` reads a fronted `must` (its auxiliaries) and refuses `Can` as a form it does not read.
    assert live("Must alice open the desk?", caller=None)["code"] == "NoDerivation"
    assert live("Can alice open the desk?", caller=None)["code"] == "QuestionForm"
    assert live("Is it the case that atlas is reviewed?", caller=None)["status"] == "one"


@pytest.mark.parametrize("caller", ["speech", "Speech-acts", "speech-acts ", "", 1, ["speech-acts"]])
def test_lean_refuses_a_caller_it_does_not_know(caller):
    with pytest.raises(VEError, match='InvalidInput: caller is "speech-acts" when present'):
        relay.decide_once(english_lean.QUESTION_MODE, {**case("Must check."), "caller": caller})


# ------------------------------------------------------------------ the relay's binding checks

def test_the_caller_is_sent_only_when_given(monkeypatch):
    sent = []
    monkeypatch.setattr(english_lean, "QUESTION_TRANSPORT", lambda c: sent.append(c) or live(c["question"]))
    english_lean.read_question(ENV, "Is it the case that atlas is reviewed?", words(), {}, caller=SPEECH)
    with pytest.raises(CheckerUnavailable):  # the answer Lean gave the speech caller is not `ve ask`'s
        english_lean.read_question(ENV, "Must check.", words(), {})
    assert sent[0]["caller"] == SPEECH and "caller" not in sent[1]


@pytest.mark.parametrize("caller", ["speech", "", "ask"])
def test_the_relay_refuses_a_caller_outside_the_contract(caller):
    with pytest.raises(ValueError, match="unknown question caller"):
        english_lean.read_question(ENV, "Must check.", words(), {}, caller=caller)


@pytest.mark.parametrize("caller, refused", [(SPEECH, False), (None, True)])
def test_a_modal_answer_is_bound_to_the_speech_caller(monkeypatch, caller, refused):
    genuine = live("Must check.")
    monkeypatch.setattr(english_lean, "QUESTION_TRANSPORT", lambda c: copy.deepcopy(genuine))
    with pytest.raises(CheckerUnavailable if refused else VEError) as caught:
        english_lean.read_question(ENV, "Must check.", words(), {}, caller=caller)
    assert ("malformed" in str(caught.value)) is refused


@pytest.mark.parametrize("question", ["Must check.", "Is it the case that atlas is reviewed?",
                                      "Is it the case that atlas is checked?"])
def test_every_mutation_of_a_genuine_speech_answer_is_refused(monkeypatch, question):
    genuine = live(question)
    seen = 0
    for name, mutant in _mutants(genuine):
        monkeypatch.setattr(english_lean, "QUESTION_TRANSPORT", lambda c, m=mutant: copy.deepcopy(m))
        with pytest.raises(CheckerUnavailable, match="malformed"):
            english_lean.read_question(ENV, question, words(), {}, caller=SPEECH)
        seen += 1
    assert seen > 20


@pytest.mark.parametrize("change", [
    lambda r: r.update(status="none"),
    lambda r: r.update(code="QuestionForm"),
    lambda r: r.update(code="Budget"),
    lambda r: r.update(span=[0, 4]),
], ids=["status", "code-of-another-status", "code-elsewhere", "span-not-in-the-row"])
def test_modal_mutations_inside_their_kinds_are_refused(monkeypatch, change):
    mutant = live("Must check.")
    change(mutant)
    monkeypatch.setattr(english_lean, "QUESTION_TRANSPORT", lambda c: copy.deepcopy(mutant))
    with pytest.raises(CheckerUnavailable, match="malformed"):
        english_lean.read_question(ENV, "Must check.", words(), {}, caller=SPEECH)
