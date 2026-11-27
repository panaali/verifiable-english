"""A document fence's refusal names the fence's sentence (row plain-vocab-refusal-number-1126; design
reviews/refusal-number-design-1126.md, orchestrator ruling 2026-11-26T21:02Z).

Lean writes every number: `english.read` takes an optional `sentence_base` (the sentences before the source, absent
0), and every per-sentence refusal text counts from it while the `sentence` field and the spans stay the source's own.
`Service.Document.contentOf` sends the fence's index in the body, and Python's own document path
(`ve/document/load.py`) sends the same field from the same order; Python never edits Lean's text.

Regression tests (each failed before the change, when every fence read alone said "Sentence 1"): a 3-fence document
whose 2nd or last fence is refused, on Lean's document mode and on Python's own path, for each refusal class; and the
field itself on `english.read`. Compatibility tests (pass before and after): the 1st fence still says "Sentence 1", a
single-fence document's text is the one `english.read` gives without the field. A non-natural value whose request the
service's restricted JSON already refuses (a negative number) is refused before and after.
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
PREMISE = "Therefore legacy is deployed."        # ConclusionWithoutPremise
# IllTyped: a reach formula reads under the base grammar and fails the typed check without `closure@0`
# (docs/question-answering/q1-4bd/evidence/english_read_delta.py `REACH`).
REACH = ("Starting from legacy, legacy is reachable by zero or more steps, where a step from a service to a second "
         "service satisfies this condition: that service is deployed.")


def environment() -> dict:
    """Base spec 8.5's `F` with the `dservice` sort, under which `MANY` has two readings
    (tests/test_english_e2_responses.py `_deployed_service`)."""
    raw = fixtures.F()
    raw["vocabulary"]["sorts"]["dservice"] = {"description": "dservice",
                                             "verbalisation": {"singular": "deployed service",
                                                               "plural": "deployed services"}}
    return raw


def document(tmp_path, sentences: list[str], order: list[int] | None = None, surfaces: list[str] | None = None):
    """A `ve-document@1` document with one prose line and one fence per sentence (unit `u<k>` holds sentence k);
    the units are listed in span order, and the fences follow it unless `order` places them otherwise (the body's j-th
    fence is unit `u<order[j] + 1>`'s). `surfaces` gives each fence's surface."""
    order = list(range(len(sentences))) if order is None else order
    body, units, cursor = b"", [], 0
    for j, k in enumerate(order):
        body += f"Claim {j + 1}.\n".encode() + f"```ve u{k + 1}\n{sentences[k]}\n```\n".encode()
    for k, sentence in enumerate(sentences, 1):
        prose = f"Claim {k}.\n".encode()
        units.append({"id": f"u{k}", "span": [cursor, cursor + len(prose)], "kind": "asserted",
                      "meaning": "specified", "support": "assumption", "content": {"fence": f"u{k}"},
                      "surface": (surfaces or ["english"] * len(sentences))[k - 1]})
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
          EMPTY: "Sentence {n} is empty.",
          PREMISE: "Sentence {n} is marked as a conclusion, and no earlier sentence is a premise.",
          REACH: "Sentence {n} was read, and its formula does not pass the type check."}
# With a base the premise texts say the premises are the fence's own: each fence is read alone (review B1).
IN_FENCE = "Sentence {n} is marked as a conclusion, and no earlier sentence in its fence is a premise."


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


@pytest.mark.parametrize("route", sorted(PATHS))
def test_a_conclusion_fence_says_its_own_fence_has_no_premise(tmp_path, monkeypatch, route):
    """Review B1: sentences 1 and 2 are above it, so the text says the premise is missing in its fence."""
    text = PATHS[route](document(tmp_path, [GOOD, GOOD, PREMISE]), monkeypatch)
    assert IN_FENCE.format(n=3) in text, text


@pytest.mark.parametrize("route", sorted(PATHS))
def test_the_number_follows_the_body_not_the_unit_list(tmp_path, monkeypatch, route):
    """The fences placed in another order than their units (review B3): the number is the fence's place in the body.
    Unit u1, read first, holds the bad sentence; its fence is the body's 3rd."""
    text = PATHS[route](document(tmp_path, [NONE, GOOD, GOOD], order=[1, 2, 0]), monkeypatch)
    assert STARTS[NONE].format(n=3) in text, text


def test_a_strict_fence_before_it_is_counted(tmp_path):
    """Every fence counts, a strict one too. Lean's document mode leaves this document to Python's own path."""
    text = python_refusal(document(tmp_path, ["true.", NONE], surfaces=["strict", "english"]))
    assert STARTS[NONE].format(n=2) in text, text


def raw(source: str, env_raw: dict | None = None, **fields) -> dict:
    """Lean's whole `english.read` row for `source` over the document environment (or `env_raw`), identities
    included."""
    env = Environment.from_dict(env_raw or environment())
    case = english_lean.request(env, source, EnglishVocabulary(env, _defer_overlay_refusals=True), {})
    return decide("english.read", [{**case, **fields}])[0]


@pytest.mark.parametrize("bad", [NONE, MANY, IT, EMPTY, REACH],
                         ids=["none", "many", "rejected", "empty", "ill-typed"])
def test_english_read_counts_its_texts_from_a_nonzero_base(bad):
    result = raw(bad, sentence_base=4)["result"]
    assert result["text"].startswith(STARTS[bad].format(n=5)), result
    # The field and the span stay the source's own: they index the text sent.
    plain = raw(bad)["result"]
    assert {k: v for k, v in result.items() if k != "text"} == {k: v for k, v in plain.items() if k != "text"}


def test_a_conclusion_without_premise_counts_from_the_base_and_names_its_fence():
    result = raw(PREMISE, sentence_base=4)["result"]
    assert (result["code"], result["text"], result["sentence"]) == ("ConclusionWithoutPremise", IN_FENCE.format(n=5), 0)
    assert raw(PREMISE)["result"]["text"] == STARTS[PREMISE].format(n=1)


def test_an_obligation_s_unproved_text_counts_from_the_base():
    """Review B2: the `unproved` text Python raises when the derivation is not found."""
    source = f"{GOOD} Therefore legacy is reviewed."
    [plain], [based] = (raw(source, **fields)["result"]["obligations"] for fields in ({}, {"sentence_base": 2}))
    assert plain["unproved"].startswith("Sentence 2 is marked as a conclusion, and no checked derivation from the "
                                        "earlier premises was found: "), plain
    assert based["unproved"].startswith("Sentence 4 is marked as a conclusion, and no checked derivation from the "
                                        "earlier premises in its fence was found: "), based
    assert {k: v for k, v in based.items() if k != "unproved"} == {k: v for k, v in plain.items() if k != "unproved"}


def test_the_every_cannot_rewrites_count_from_the_base():
    """The blocked wording with rewrites (`riskEveryCannotText`) over the agent-ops environment."""
    from test_risk_english import ops_raw
    text = "every action available to bot cannot lead to loss."
    based, plain = (raw(text, ops_raw(), **fields)["result"] for fields in ({"sentence_base": 2}, {}))
    assert based["code"] == "BlockedWording" and based["text"].startswith("Sentence 3 has two readings."), based
    assert plain["text"].startswith("Sentence 1 has two readings."), plain


def test_a_later_sentence_of_the_source_adds_the_base():
    result = raw(f"{GOOD} {NONE}", sentence_base=2)["result"]
    assert result["text"].startswith(STARTS[NONE].format(n=4)) and result["sentence"] == 1, result


@pytest.mark.parametrize("value", ["1", -1, True, [1], {}])
def test_a_sentence_base_that_is_not_a_natural_number_is_invalid_input(value):
    # A negative number may be refused by the service's restricted JSON before the mode reads it (a float always is,
    # by its JSON reader, so it never reaches the mode and is not listed here).
    with pytest.raises((VEError, CheckerUnavailable), match="sentence_base is a natural number|restricted JSON"):
        raw(NONE, sentence_base=value)


@pytest.mark.parametrize("source", [GOOD, NONE, MANY, IT, EMPTY, PREMISE, f"{GOOD} {NONE}"])
def test_a_request_without_the_field_answers_as_with_base_0(source):
    """Absent is 0 (fails before the change only because the field was unknown then)."""
    assert json.dumps(raw(source)) == json.dumps(raw(source, sentence_base=0))


# ---------------------------------------------------------------- compatibility: unchanged answers
# Byte-identity with main of every request without the field is pinned by the recorded fixtures that replay through
# the service (tests/test_ask_fixtures.py, tests/test_lean_service.py, tests/test_pk1_route_case_differential.py).

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


