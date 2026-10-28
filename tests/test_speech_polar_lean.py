"""Speech acts' polar questions and their `Must`/`Can` refusal, read by Lean (question answering Q1.4, Q1.4b).

`parse_speech` sends a wording that begins with one of the contract's speech-acts prefixes (`speechPrefixes`), or with
F2's fronted `Is ` (Q1.4b), to `english.question` with `caller` "speech-acts" and relays the answer. Q1.4b's three
classes of changed verdicts (DRI 2026-10-27 item 4) have one test each: a gloss question gets Lean's refusal text, a
case-folded name is refused, and `Is every service reviewed?` is read as `ve ask` reads it.
"""
from __future__ import annotations

import copy
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from ve import speech_english
from ve.backends import english_lean, relay
from ve.english import EnglishVocabulary
from ve.errors import CheckerUnavailable, ResourceLimit, VEError
from ve.speech_english import parse_speech

from subprocesses import HANG_TIMEOUT
from test_question_reading import _mutants
from test_speech_acts import environment
from ve.environment import Environment

ENV = environment()
MODAL_TEXT = "ModalQuestion: choose an explicit question"
SPEECH = english_lean.SPEECH_CALLER


def words(env=ENV):
    return EnglishVocabulary(env, _defer_overlay_refusals=True)


def case(question: str, caller: str | None = SPEECH, env=ENV) -> dict:
    """The request `read_question` sends for `question`."""
    out = {**english_lean.request(env, question, words(env), {}), "id": english_lean.QUESTION_MODE,
           "question": question}
    return out if caller is None else {**out, "caller": caller}


def live(question: str, caller: str | None = SPEECH, env=ENV) -> dict:
    row = relay.decide_once(english_lean.QUESTION_MODE, case(question, caller, env))
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
    assert speech_english._LEAN_PREFIXES == (*english_lean.QUESTION_CALLERS[SPEECH], "Is ")


@pytest.mark.parametrize("wording, body", [
    ("Is it the case that atlas is reviewed?", ["unary", "reviewed", ["const", "atlas"]]),
    ("Is it the case that every service is reviewed?", ["forall", "service", ["unary", "reviewed", ["var", 0]]]),
    ("  Is it the case that atlas is reviewed?\n", ["unary", "reviewed", ["const", "atlas"]]),
])
def test_an_f1_question_is_leans_reading(calls, wording, body):
    assert parse_speech(ENV, wording, ENV.speech_acts) == ({"mode": "polar", "body": body}, "question")
    assert calls == [SPEECH]


@pytest.mark.parametrize("wording", ["is it the case that atlas is reviewed?", "is atlas reviewed?",
                                     "IS ATLAS REVIEWED?", "Isatlas reviewed?", "Is", "Which one of atlas and beacon "
                                     "is reviewed?", "Atlas is reviewed?", "Does atlas click?"])
def test_a_wording_without_a_routed_prefix_is_not_sent(calls, wording):
    """The boundary of `Is `: a lower-case or capital `is`, no space after `Is`, and other speech acts."""
    try:
        parse_speech(ENV, wording, ENV.speech_acts)
    except VEError:
        pass
    assert calls == []


@pytest.mark.parametrize("wording", ["Is atlas reviewed?", "Is ?", "Is atlas reviewed", "Is it the case that?",
                                     "Is it the case thatatlas is reviewed?", "Is ATLAS reviewed?",
                                     "Is every service reviewed?", "Is a service reviewed?", "Is atlas?"])
def test_an_f2_wording_is_sent(calls, wording):
    """Q1.4b: every wording that begins with `Is ` is Lean's, read or refused, with no Python reading beside it."""
    try:
        parse_speech(ENV, wording, ENV.speech_acts)
    except VEError as exc:
        assert exc.lean_question is not None
    assert calls == [SPEECH]


def test_an_f1_refusal_is_leans_text_and_span(calls):
    with pytest.raises(VEError) as caught:
        parse_speech(ENV, "Is it the case that atlas is checked?", ENV.speech_acts)
    assert caught.value.lean_question["code"] == "NoDerivation"
    assert str(caught.value).startswith("The question has no reading with the current vocabulary.")
    assert caught.value.span is not None and calls == [SPEECH]


def test_an_f1_refusal_carries_leans_rephrasings(calls):
    """Review q1-4 F2: the refusal is Lean's text and then each rephrasing, the lines `ve ask` prints, never a text
    that ends at "Ask one of these instead:"."""
    with pytest.raises(VEError) as caught:
        parse_speech(ENV, "Is it the case that a service is reviewed?", ENV.speech_acts)
    answer = caught.value.lean_question
    assert answer["code"] == "IndefiniteQuestion" and calls == [SPEECH]
    assert str(caught.value).splitlines() == [
        'VE cannot tell whether "a" here means every or some. Ask one of these instead:',
        "Is it the case that every service is reviewed?", "Is it the case that some service is reviewed?"]
    assert str(caught.value).splitlines() == english_lean.question_lines(answer)


# ------------------------------------------------------------------ Q1.4b: F2's three classes (DRI 2026-10-27 item 4)

GLOSSES = {"staffed": "{0} is reviewed by staff", "despite": "{0} is reviewed despite remaining unreviewed",
           "atlas_linked": "{0} is linked to atlas", "vetted": "{0} is vetted"}


def glossed() -> Environment:
    raw = ENV.to_dict()
    for name, gloss in GLOSSES.items():
        raw["vocabulary"]["predicates"][name] = {"arguments": ["service"], "description": name,
                                                 "verbalisation": gloss}
    return Environment(raw)


GLOSSED = glossed()


def refused(env, wording: str) -> tuple[VEError, dict]:
    """The speech caller's refusal of `wording`, and Lean's answer to the same request sent by itself."""
    with pytest.raises(VEError) as caught:
        parse_speech(env, wording, env.speech_acts)
    return caught.value, live(wording, env=env)


@pytest.mark.parametrize("wording", ["Is atlas reviewed by staff?", "Is atlas reviewed despite remaining unreviewed?",
                                     "Is atlas linked to atlas?"])
def test_a_gloss_question_gets_leans_refusal_text(calls, wording):
    """Class (a): a declared gloss is no longer matched opaquely by Python; Lean's lexicon has no such wording, so
    the speech caller gets Lean's refusal, its text and its span, where the base answered with the gloss's
    predicate."""
    error, answer = refused(GLOSSED, wording)
    assert answer["code"] == "NoDerivation" and error.lean_question["code"] == "NoDerivation"
    assert str(error).splitlines() == english_lean.question_lines(answer)
    assert error.span is not None and calls == [SPEECH]


@pytest.mark.parametrize("env, wording, predicate", [(GLOSSED, "Is atlas vetted?", "vetted"),
                                                     (GLOSSED, "Is atlas reviewed?", "reviewed"),
                                                     (ENV, "Is beacon reviewed?", "reviewed")])
def test_a_gloss_leans_lexicon_reads_is_read(calls, env, wording, predicate):
    """The accepting side of class (a): a one-property gloss, which Lean's lexicon reads, is Lean's reading."""
    subject = wording.split()[1]
    assert parse_speech(env, wording, env.speech_acts) == (
        {"mode": "polar", "body": ["unary", predicate, ["const", subject]]}, "question")
    assert calls == [SPEECH]


def test_a_gloss_outside_the_environment_is_refused():
    """`Is atlas vetted?` is read only where `vetted` is declared."""
    error, answer = refused(ENV, "Is atlas vetted?")
    assert str(error).splitlines() == english_lean.question_lines(answer)


@pytest.mark.parametrize("wording", ["Is ATLAS reviewed?", "Is aTLAS reviewed?", "Is ATlas reviewed?",
                                     "Is BEACON reviewed?"])
def test_a_case_folded_name_is_refused(calls, wording):
    """Class (b): Python folded a name's case; Lean refuses a name not written as declared (or capitalised)."""
    error, answer = refused(ENV, wording)
    assert answer["code"] == "NoDerivation"
    assert str(error).splitlines() == english_lean.question_lines(answer)
    assert wording.split()[1] in str(error) and calls == [SPEECH]


@pytest.mark.parametrize("wording, name", [("Is atlas reviewed?", "atlas"), ("Is Atlas reviewed?", "atlas"),
                                           ("Is Beacon reviewed?", "beacon")])
def test_a_name_as_declared_or_capitalised_is_read(wording, name):
    """The accepting side of class (b): the declared name, and the name with its first letter capitalised."""
    assert parse_speech(ENV, wording, ENV.speech_acts)[0]["body"] == ["unary", "reviewed", ["const", name]]


ROOT = Path(__file__).resolve().parents[1]
ENV_ALLOW = ("PATH", "HOME", "LANG", "LC_ALL", "TMPDIR", "PYTHONPATH", "PYTHONNOUSERSITE", "PYTHONPYCACHEPREFIX")


def ve_ask(tmp_path, question: str, *options: str):
    """`ve ask DOCUMENT QUESTION --reading` over a document in the speech environment."""
    document = tmp_path / "speech.ve.md"
    meta = {"format": "ve-document@1", "environment": ENV.to_dict(), "units": [{"id": "s1", "fence": "s1"}]}
    document.write_text("---\n" + json.dumps(meta) + "\n---\nAtlas is reviewed.\n```ve s1\nAtlas is reviewed.\n```\n")
    env = {k: v for k, v in os.environ.items() if k in ENV_ALLOW or k.startswith("VE_")}
    return subprocess.run([sys.executable, "-m", "ve", "ask", str(document), question, "--reading", *options],
                          cwd=ROOT, env=env, text=True, capture_output=True, timeout=HANG_TIMEOUT)


@pytest.mark.parametrize("wording, body", [
    ("Is every service reviewed?", ["forall", "service", ["unary", "reviewed", ["var", 0]]]),
    ("Is some service reviewed?", ["exists", "service", ["unary", "reviewed", ["var", 0]]]),
    ("Is a service reviewed?", None)])
def test_a_quantified_f2_question_is_read_as_ve_ask_reads_it(monkeypatch, tmp_path, wording, body):
    """Class (c): `Is every service reviewed?` (and `some`), which Python refused as `UnknownAlternative`, gets the
    same verdict and text through the speech caller as through `ve ask`; `Is a service reviewed?` gets the same
    refusal, whose rephrasings are those two questions (spec 4.1 row 14)."""
    seen = []

    def spy(*args, **kwargs):
        try:
            answer = english_lean.read_question(*args, **kwargs)
        except VEError as exc:
            seen.append(exc.lean_question)
            raise
        seen.append(answer)
        return answer

    monkeypatch.setattr(speech_english, "read_question", spy)
    done = ve_ask(tmp_path, wording)
    structured = json.loads(ve_ask(tmp_path, wording, "--json").stdout)["result"]
    if body is None:
        with pytest.raises(VEError) as caught:
            parse_speech(ENV, wording, ENV.speech_acts)
        assert done.returncode == 2 and str(caught.value).splitlines() == done.stdout.splitlines()
        assert structured["rephrasings"] == [wording.replace(" a ", " every "), wording.replace(" a ", " some ")]
    else:
        assert parse_speech(ENV, wording, ENV.speech_acts) == ({"mode": "polar", "body": body}, "question")
        assert done.returncode == 0 and english_lean.question_lines(seen[0]) == done.stdout.splitlines()
        assert structured["ast"] == body
    assert seen[0]["status"] == structured["status"] and seen[0]["text"] == structured["text"]


NESTED = "Is it the case that " + "it is not the case that " * 49 + "atlas is reviewed?"


@pytest.mark.parametrize("wording, read", [
    (NESTED, True),  # 298 tokens in the body
    (NESTED.replace("that it", "that it is not the case that it", 1), False),  # 304
    ("Is it the case that " + "it is not the case that " * 55 + "atlas is reviewed?", False),  # review q1-4 F1
    ("Is it the case that atlas is" + " " * 4059 + "reviewed?", True),  # 4096 bytes
    ("Is it the case that atlas is" + " " * 4060 + "reviewed?", False),  # 4097 bytes
], ids=["tokens-298", "tokens-304", "nested-55", "bytes-4096", "bytes-4097"])
def test_the_question_limits_are_leans(calls, wording, read):
    """Review q1-4 F1: an F1 question is read under Lean's question limits (300 tokens, 4,096 bytes); one over them is
    Lean's `QuestionTooLong`, with Lean's answer riding along, and Python holds no limit of its own. The merge base read
    the over-limit questions; DELTA.md's V1 reserves that change for the DRI."""
    if read:
        assert parse_speech(ENV, wording, ENV.speech_acts)[1] == "question"
    else:
        with pytest.raises(ResourceLimit) as caught:
            parse_speech(ENV, wording, ENV.speech_acts)
        assert caught.value.lean_question["code"] == "QuestionTooLong"
        assert str(caught.value) == "The question is longer than VE reads. Ask a shorter question."
    assert calls == [SPEECH]


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


def test_lean_reads_with_the_speech_callers_auxiliaries():
    """Speech acts read with `["is"]`: a fronted `may`, which `ve ask` reads, is a form the speech caller does not."""
    assert live("May alice open the desk?")["code"] == "QuestionForm"
    assert live("May alice open the desk?", caller=None)["code"] == "NoDerivation"
    assert live("Is atlas reviewed?")["status"] == live("Is atlas reviewed?", caller=None)["status"] == "one"


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


def _deep(depth: int = 10_000):
    value: list = []
    for _ in range(depth):
        value = [value]
    return value


@pytest.mark.parametrize("question", ["Must check.", "Is it the case that atlas is reviewed?"])
@pytest.mark.parametrize("value", ["\ud800", "deep"], ids=["lone-surrogate", "deep-list"])
def test_a_surrogate_or_deep_field_is_refused(monkeypatch, question, value):
    genuine = live(question)
    for key in genuine:
        mutant = {**genuine, key: _deep() if value == "deep" else value}
        monkeypatch.setattr(english_lean, "QUESTION_TRANSPORT", lambda c, m=mutant: m)
        with pytest.raises(CheckerUnavailable):
            english_lean.read_question(ENV, question, words(), {}, caller=SPEECH)


@pytest.mark.parametrize("caller", ["\ud800", "deep", 1.5, True, {}], ids=["surrogate", "deep", "float", "bool", "obj"])
def test_lean_refuses_a_malformed_caller(caller):
    with pytest.raises(VEError):
        relay.decide_once(english_lean.QUESTION_MODE, {**case("Must check."), "caller": _deep(100)
                                                        if caller == "deep" else caller})


# ------------------------------------------------------------------ the lone-surrogate check, both sides (review q1-4 F3)

SURROGATES = ["\ud800", "\udbff", "\udc00", "\udfff"]
NEAR_SURROGATES = ["\ud7ff", "\ue000", "\ufb01", "\U0001f600", "\U00010000", "\U0010ffff", "\xe9"]


@pytest.mark.parametrize("char", SURROGATES + NEAR_SURROGATES)
@pytest.mark.parametrize("where", ["value", "key", "nested"])
def test_the_surrogate_check_refuses_exactly_the_surrogates(char, where):
    value = {"value": {"text": f"a{char}b"}, "key": {f"a{char}": 1}, "nested": {"x": [[1, char]]}}[where]
    assert english_lean._has_surrogate(value) is (char in SURROGATES)


@pytest.mark.parametrize("char", NEAR_SURROGATES)
@pytest.mark.parametrize("question, caller", [
    ("Is atlas {} reviewed?", None),
    ("Is it the case that atlas {} is reviewed?", None),
    ("Is it the case that atlas {} is reviewed?", SPEECH),
], ids=["ask-f2", "ask-f1", "speech-f1"])
def test_a_genuine_answer_quoting_a_character_near_the_surrogates_is_relayed(char, question, caller):
    """Lean's answer quotes the character back (`Unknown English phrase …`): the relay raises it as Lean's
    `NoDerivation`, never as `CheckerUnavailable`."""
    with pytest.raises(VEError) as caught:
        english_lean.read_question(ENV, question.format(char), words(), {}, caller=caller)
    assert not isinstance(caught.value, CheckerUnavailable)
    assert caught.value.lean_question["code"] == "NoDerivation" and char in str(caught.value)
