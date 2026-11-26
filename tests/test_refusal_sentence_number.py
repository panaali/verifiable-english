"""A document fence's refusal names the fence's sentence (row plain-vocab-refusal-number-1126; design
reviews/refusal-number-design-1126.md, orchestrator ruling 2026-11-26T21:02Z).

Lean writes every number: `english.read` takes an optional `sentence_base` (the sentences before the source, absent
0), and every per-sentence refusal text counts from it while the `sentence` field and the spans stay the source's own.
`Service.Document.contentOf` sends the fence's index in the body, and Python's own document path
(`ve/document/load.py`) sends the same field from the same order; Python never edits Lean's text.

Regression tests (each failed before the change, when every fence read alone said "Sentence 1"): a 3-fence document
whose 2nd or last fence is refused, on Lean's document mode and on Python's own path, for each refusal class; and the
field itself on `english.read`. Compatibility tests (pass before and after): the 1st fence still says "Sentence 1", a
single-fence document's text is the one `english.read` gives without the field, and a request without the field is
answered as before.
"""
from __future__ import annotations

import json

import pytest

from conformance import english_lean_s3_fixtures as fixtures
from ve import document as D
from ve.backends import english_lean
from ve.backends.lean_service import CheckerUnavailable
from ve.backends.relay import decide
from ve.document import load as D_load
from ve.english import EnglishVocabulary
from ve.environment import Environment
from ve.errors import VEError

GOOD = "Legacy is deployed."
NONE = "They are deployed."                      # NoDerivation
MANY = "Every deployed service is reviewed."     # Ambiguous (with the `dservice` sort)
IT = "It is reviewed."                           # rejected: "it" refers to nothing in its own fence
EMPTY = "."                                      # EmptySentence, a lexical rejection that names its sentence


def environment() -> dict:
    """Base spec 8.5's `F` with the `dservice` sort, under which `MANY` has two readings
    (tests/test_english_e2_responses.py `_deployed_service`)."""
    raw = fixtures.F()
    raw["vocabulary"]["sorts"]["dservice"] = {"description": "dservice",
                                             "verbalisation": {"singular": "deployed service",
                                                               "plural": "deployed services"}}
    return raw


def document(tmp_path, sentences: list[str]):
    """A `ve-document@1` document with one prose line and one English fence per sentence, in body order."""
    body, units, cursor = b"", [], 0
    for k, sentence in enumerate(sentences, 1):
        prose = f"Claim {k}.\n".encode()
        body += prose + f"```ve u{k}\n{sentence}\n```\n".encode()
        units.append({"id": f"u{k}", "span": [cursor, cursor + len(prose)], "kind": "asserted",
                      "meaning": "specified", "support": "assumption", "content": {"fence": f"u{k}"},
                      "surface": "english"})
        cursor += len(prose)
    front = {"format": "ve-document@1", "environment": environment(), "units": units}
    path = tmp_path / "fences.ve.md"
    path.write_bytes(b"---\n" + json.dumps(front).encode() + b"\n---\n" + body)
    return path


def lean_refusal(path, monkeypatch) -> str:
    """Lean's document mode's refusal of the document, raised verbatim; Python's own loader never runs."""
    def refuse(*args, **kwargs):
        raise AssertionError("Python's own document loader ran on a document Lean owns")
    with monkeypatch.context() as patch:
        patch.setattr(D_load, "_load_document", refuse)
        with pytest.raises(VEError) as raised:
            D.load_document(path)
    return str(raised.value)


def python_refusal(path) -> str:
    """Python's own document path (`_load_document`), whose English fences Lean's `english.read` reads."""
    with pytest.raises(VEError) as raised:
        D._load_document(path.read_bytes(), path, None)
    return str(raised.value)


PATHS = {"lean": lambda path, monkeypatch: lean_refusal(path, monkeypatch),
         "python": lambda path, monkeypatch: python_refusal(path)}

# refused sentence -> the start of its text when it is sentence `n`
STARTS = {NONE: "Sentence {n} has no reading with the current vocabulary.",
          MANY: "Sentence {n} can be read in more than one way.",
          IT: "Sentence {n} uses \"it\"",
          EMPTY: "Sentence {n} is empty."}


# ---------------------------------------------------------------- regression: the fence's own number

@pytest.mark.parametrize("route", sorted(PATHS))
@pytest.mark.parametrize("bad", [NONE, MANY, IT, EMPTY], ids=["none", "many", "rejected", "empty"])
def test_the_second_fence_s_refusal_names_sentence_2(tmp_path, monkeypatch, route, bad):
    text = PATHS[route](document(tmp_path, [GOOD, bad, GOOD]), monkeypatch)
    assert STARTS[bad].format(n=2) in text, text
    assert "Sentence 1 " not in text, text


@pytest.mark.parametrize("route", sorted(PATHS))
def test_the_last_fence_s_refusal_names_sentence_3(tmp_path, monkeypatch, route):
    text = PATHS[route](document(tmp_path, [GOOD, GOOD, NONE]), monkeypatch)
    assert STARTS[NONE].format(n=3) in text, text


def raw(source: str, **fields) -> dict:
    """Lean's whole `english.read` row for `source` over the document environment, identities included."""
    env = Environment.from_dict(environment())
    case = english_lean.request(env, source, EnglishVocabulary(env, _defer_overlay_refusals=True), {})
    return decide("english.read", [{**case, **fields}])[0]


@pytest.mark.parametrize("bad", [NONE, MANY, IT, EMPTY], ids=["none", "many", "rejected", "empty"])
def test_english_read_counts_its_texts_from_a_nonzero_base(bad):
    result = raw(bad, sentence_base=4)["result"]
    assert result["text"].startswith(STARTS[bad].format(n=5)), result
    # The field and the span stay the source's own: they index the text sent.
    plain = raw(bad)["result"]
    assert {k: v for k, v in result.items() if k != "text"} == {k: v for k, v in plain.items() if k != "text"}


def test_a_later_sentence_of_the_source_adds_the_base():
    result = raw(f"{GOOD} {NONE}", sentence_base=2)["result"]
    assert result["text"].startswith(STARTS[NONE].format(n=4)) and result["sentence"] == 1, result


@pytest.mark.parametrize("value", ["1", -1, True, [1], {}])
def test_a_sentence_base_that_is_not_a_natural_number_is_invalid_input(value):
    # A negative number may be refused by the service's restricted JSON before the mode reads it (a float always is,
    # by its JSON reader, so it never reaches the mode and is not listed here).
    with pytest.raises((VEError, CheckerUnavailable), match="sentence_base is a natural number|restricted JSON"):
        raw(NONE, sentence_base=value)


# ---------------------------------------------------------------- compatibility: unchanged answers

@pytest.mark.parametrize("route", sorted(PATHS))
def test_the_first_fence_s_refusal_still_names_sentence_1(tmp_path, monkeypatch, route):
    text = PATHS[route](document(tmp_path, [NONE, GOOD, GOOD]), monkeypatch)
    assert STARTS[NONE].format(n=1) in text, text


@pytest.mark.parametrize("route", sorted(PATHS))
@pytest.mark.parametrize("bad", [NONE, MANY, IT, EMPTY], ids=["none", "many", "rejected", "empty"])
def test_a_single_fence_document_says_what_english_read_says(tmp_path, monkeypatch, route, bad):
    text = PATHS[route](document(tmp_path, [bad]), monkeypatch)
    assert raw(bad)["result"]["text"] in text, text
    assert STARTS[bad].format(n=1) in text, text


@pytest.mark.parametrize("source", [GOOD, NONE, MANY, IT, EMPTY, f"{GOOD} {NONE}"])
def test_a_request_without_the_field_answers_as_with_base_0(source):
    assert json.dumps(raw(source)) == json.dumps(raw(source, sentence_base=0))
