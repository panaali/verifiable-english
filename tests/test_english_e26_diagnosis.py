"""English E2.6: Lean's diagnosis of a sentence without a reading (`VE.EnglishGrammar.diagnose`, spec 4.5) says what
the hand parser said, where it said it: the words the rules read next, the phrase written where a declared wording
may come with the nearest declared wordings, or a declared wording the text extends. Each case is a frozen
readability attempt (W08, W12, W14) or a `ve propose` fixture, with the hand parser's message and span beside it."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from ve.english import EnglishVocabulary, _python_reading, parse_english
from ve.environment import Environment
from ve.errors import VEError

ROOT = Path(__file__).resolve().parents[1]
LEAN = ROOT / "lean/.lake/build/bin/ve_service"
pytestmark = pytest.mark.skipif(not LEAN.exists(), reason="the Lean service has not been built")
NO_READING = "Sentence 1 has no reading with the current vocabulary. "
HELP = " Use the English paraphrase as a writing example."


def env_of(name, overlay=None):
    env = Environment(json.loads((ROOT / name).read_text()))
    return env, ({"vocabulary": json.loads((ROOT / overlay).read_text())} if overlay else {})


def refusals(env, options, text):
    """Lean's refusal (the public one) and the hand parser's, for the same text."""
    with pytest.raises(VEError) as lean:
        parse_english(env, text, **options)
    with pytest.raises(VEError) as python:
        _python_reading(env, text, EnglishVocabulary(env, **options), options)
    return lean.value, python.value


def inside(outer, inner):
    return outer.start <= inner.start and inner.end <= outer.end


CASES = [
    # (environment, overlay, text, Lean's text after the code text, the span Lean gives)
    ("usecases/us-constitution-14th-s1/environment.json", "usecases/us-constitution-14th-s1/environment.english.json",
     "For every person, if that person was born in the United States and that person is subject to the jurisdiction "
     "of the United States, then that person is a citizen of the United States.",
     "Expected ', then ' here." + HELP, (62, 66)),
    ("examples/environment.json", None, "No service is deployed and is not reviewed.",
     "Expected '.' here." + HELP, (22, 26)),
    ("examples/environment.json", None, "Every service is deployed or reviewed, or both.",
     "Expected '.' here." + HELP, (25, 28)),
    ("examples/environment.json", None, "No service that is deployed is not reviewed.",
     "Unknown English phrase 'that'. Nearest declared wordings: 'owns {1}'; 'person'; 'service'.", (10, 15)),
    ("usecases/birthright-citizenship-debate/environment.json",
     "usecases/birthright-citizenship-debate/environment.english.json",
     "Every person who is born in the United States and is subject to US jurisdiction is a UK citizen.",
     "Unknown English phrase 'is a UK citizen'. Nearest declared wordings: 'is a US citizen'; 'child'; 'person'.",
     (79, 95)),
    ("usecases/birthright-citizenship-debate/environment.json",
     "usecases/birthright-citizenship-debate/environment.english.json",
     "Every person is a US citizen of record.",
     "Phrase 'is a US citizen of record' extends existing wording 'us_citizen': '{0} is a US citizen'; declare "
     "distinct wording by hand.", (12, 38)),
]


@pytest.mark.parametrize("name, overlay, text, said, span", CASES, ids=[c[3][:24] for c in CASES])
def test_lean_says_what_the_hand_parser_said_where_it_said_it(name, overlay, text, said, span):
    env, options = env_of(name, overlay)
    lean, python = refusals(env, options, text)
    assert str(lean).startswith(NO_READING + said), str(lean)
    assert (lean.span.start, lean.span.end) == span
    assert inside(lean.span, python.span), (lean.span, python.span)
    # Every name the hand parser quoted is quoted again, but for its one-letter fragment of `that` (W12), which
    # Lean quotes whole at the same place.
    for name_quoted in str(python).split("'")[1::2]:
        assert f"'{name_quoted}'" in str(lean) or (name_quoted == "t" and "'that'" in str(lean)), name_quoted


def test_a_sentence_that_ends_early_names_what_may_come_at_its_end():
    env, options = env_of("examples/environment.json")
    lean, _ = refusals(env, options, "Every service is.")
    assert str(lean).startswith(NO_READING + "Expected ")
    assert "'deployed'" in str(lean) and "'reviewed'" in str(lean)
    assert lean.span.start == len("Every service is")


def test_the_diagnosis_is_lean_s_in_the_answer_not_the_relay_s():
    """The `none` answer carries the diagnosis in Lean's own `text` and `span`; the relay adds only Lean's advice."""
    from ve.backends import english_lean
    env, options = env_of("examples/environment.json")
    text = "No service is deployed and is not reviewed."
    reading = english_lean.read(env, text, EnglishVocabulary(env), options)
    assert reading.status == "none"
    assert reading.response["text"] == NO_READING + "Expected '.' here." + HELP
    assert reading.response["span"] == [22, 26]
    assert reading.message() == reading.response["text"]
