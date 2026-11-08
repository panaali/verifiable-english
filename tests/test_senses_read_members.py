"""sn-b6c: the members a `senses.read` route answer gains (byte spans and glosses in the sense map, the texts of
docs/spec/senses.md 3.2 and plan 2.8), each equal to Lean's and bound to the request; and their rebinding fuzz.
Retyping and dropping every field is `test_senses_route.py::test_genuine_response_field_mutations_are_rejected`."""
from __future__ import annotations

import json
from copy import deepcopy

import pytest

from ve.backends import lean as lean_backend
from ve.backends import senses as route
from ve.errors import CheckerUnavailable
from test_senses_route import WORLDS, read_in

LINES = "In this document, funny means amusing.\nIn this document, odd means strange.\n\n"
# Each golden's sense-map entries as (gloss, the source's bytes of their span), as Lean's `lexSpans` cuts them:
# a word after a preamble, a double space or a no-break space (two bytes), a glossed head with its gloss, and an
# open unit's two candidates over one word.
GOLDENS = [
    (LINES + "Every  funny joke is odd. The riddle is funny (meaning strange).",
     [("amusing", "funny"), ("strange", "odd"), ("strange", "funny (meaning strange)")]),
    ("The riddle is funny.", [("amusing", "funny"), ("strange", "funny")]),
    ("In this document, funny means amusing. The riddle is funny, in the sense of strange.",
     [("strange", "funny, in the sense of strange")]),
]
MIXED = LINES + "Every funny joke is odd. The riddle is funny (meaning strange). The riddle is funny."
UNNEEDED = "In this document, tells means says aloud. Alice tells the riddle."


def _slices(source: str, reading: dict) -> list:
    data = source.encode()
    return [(e["gloss"], data[e["byte_start"]:e["byte_stop"]].decode()) for e in reading["sense_map"]]


@pytest.mark.parametrize("source, expected", GOLDENS)
def test_each_span_is_the_bytes_of_its_words(source, expected):
    """R3: every span is the true span of its tokens in the request's source, and every gloss its sense's."""
    assert _slices(source, read_in(WORLDS["joke"](), source)["reading"]) == expected


def _problem(source, result):
    return route._response_problem(result, result["dictionary_id"], result["request_id"], source=source,
                                   binding=None)


SHIFTS = {"start-1": (-1, 0), "start+1": (1, 0), "stop-1": (0, -1), "stop+1": (0, 1),
          "preamble": (-60, -60), "past-end": (500, 500), "empty": (0, -5)}


@pytest.mark.parametrize("shift", SHIFTS, ids=list(SHIFTS))
def test_a_span_off_by_one_byte_is_refused(shift):
    """The relay's binding of a span (`_byte_spans_problem`): off by one byte at either edge, onto the preamble,
    past the source or emptied. `funny` is followed by a space here; a stretch onto a punctuation token is the
    golden test's (`test_each_span_is_the_bytes_of_its_words`)."""
    source = GOLDENS[0][0]
    genuine = read_in(WORLDS["joke"](), source)
    assert _problem(source, genuine) is None
    mutant = deepcopy(genuine)
    entry = mutant["reading"]["sense_map"][0]
    entry["byte_start"] += SHIFTS[shift][0]
    entry["byte_stop"] += SHIFTS[shift][1]
    assert "span" in _problem(source, mutant)


def test_spans_follow_their_tokens():
    """Two entries' bytes swapped (each still a word of the source), or one candidate's span moved off its twin's."""
    source = GOLDENS[0][0]
    genuine = read_in(WORLDS["joke"](), source)
    swapped = deepcopy(genuine)
    first, second = swapped["reading"]["sense_map"][:2]
    for key in ("byte_start", "byte_stop"):
        first[key], second[key] = second[key], first[key]
    assert _problem(source, swapped) == "sense-map spans are not in the order of their tokens"
    open_source = "The riddle is funny. The riddle is odd."
    twin = read_in(WORLDS["joke"](), open_source)
    assert _problem(open_source, twin) is None
    moved = deepcopy(twin)
    moved["reading"]["sense_map"][1].update(byte_start=21, byte_stop=24)  # `The`, a word of the next sentence
    assert _problem(open_source, moved) == "sense-map spans are not in the order of their tokens"


def _tampered(monkeypatch, change):
    """Lean's answers through the route, each changed by `change(reading)` before the relay reads it."""
    real = lean_backend.run_limited

    def changed(*args, **kwargs):
        answer = real(*args, **kwargs)
        rows = json.loads(answer.stdout)
        change(rows[0]["result"]["reading"])
        answer.stdout = json.dumps(rows).encode()
        return answer
    monkeypatch.setattr(lean_backend, "run_limited", changed)


@pytest.mark.parametrize("change, message", [
    (lambda r: r["sense_map"][0].update(byte_stop=r["sense_map"][0]["byte_stop"] + 1), "span"),
    (lambda r: r["sense_map"][0].update(gloss="purple"), "sense-map occurrence"),  # no gloss of the request's
    (lambda r: r["sense_map"][0].update(gloss=""), "sense-map occurrence"),
], ids=["span", "gloss-unknown", "gloss-empty"])
def test_a_tampered_entry_through_the_route_is_unavailable(monkeypatch, change, message):
    _tampered(monkeypatch, change)
    with pytest.raises(CheckerUnavailable, match=message):
        read_in(WORLDS["joke"](), GOLDENS[0][0])


def test_the_texts_of_a_source_answer_are_leans():
    """R3: the warnings (plan 2.8) and NoSenseFits (spec 3.2) with their slots; the fault texts are
    `test_senses_route.py::test_every_refusal_carries_its_arguments`', the unit texts the `#guard`s'."""
    assert read_in(WORLDS["joke"](), MIXED)["reading"]["warnings"] == [{
        "code": "Mixed", "word": "funny",
        "text": "The word funny is used in two senses here: amusing (sentences 3, 5) and strange (sentence 4)."}]
    assert read_in(WORLDS["joke"](), UNNEEDED)["reading"]["warnings"] == [{
        "code": "Unneeded", "word": "tells", "text": "The line for tells is not needed: tells has one sense."}]
    assert read_in(WORLDS["joke"](), LINES + "The riddle is funny.")["reading"]["warnings"] == []
    none = read_in(WORLDS["joke"](), "Alice is funny.")["reading"]
    assert none["hint"] == {"code": "NoSenseFits", "text": "Sentence 1 has no reading under any sense of funny. "
                                                           "The senses of funny here are: amusing; strange."}
    # two unresolved words with no reading: S2's `none` without a hint (DRI 20261108 item 2)
    assert "hint" not in read_in(WORLDS["joke"](), "Alice is funny and odd.")["reading"]


WARNINGS = {
    "mixed-dropped": lambda w: w.pop(0),
    "mixed-word": lambda w: w[0].update(word="odd"),
    "extra-mixed": lambda w: w.append(dict(w[0])),
    "unneeded-unknown-word": lambda w: w.append({"code": "Unneeded", "word": "zany", "text": "x"}),
    "unneeded-twice": lambda w: w.extend([{"code": "Unneeded", "word": "odd", "text": "x"}] * 2),
    "unneeded-before-mixed": lambda w: w.insert(0, {"code": "Unneeded", "word": "odd", "text": "x"}),
    "code": lambda w: w[0].update(code="Unresolved"),
}


@pytest.mark.parametrize("change", WARNINGS, ids=list(WARNINGS))
def test_warning_rebinding_is_refused(monkeypatch, change):
    """One Mixed warning per `mixed` word, in order, then distinct Unneeded words of the request's dictionary."""
    assert read_in(WORLDS["joke"](), MIXED)["reading"]["warnings"]
    _tampered(monkeypatch, lambda r: WARNINGS[change](r["warnings"]))
    with pytest.raises(CheckerUnavailable, match="warning"):
        read_in(WORLDS["joke"](), MIXED)


TEXTS = {
    # (fixture, change of the reading)
    "fault-text-dropped": ("In this document, funny means purple. The riddle is funny.", lambda r: r.pop("text")),
    "fault-text-unasked": ("In this document, zany means amusing. The riddle is funny.",
                           lambda r: r.update(text="x")),
    "hint-code": ("Alice is funny.", lambda r: r["hint"].update(code="Unresolved")),
    "hint-empty": ("Alice is funny.", lambda r: r["hint"].update(text="")),
    "hint-on-budget": ("Alice tells the riddle.", lambda r: r.update(hint={"code": "NoSenseFits", "text": "x"})),
    "unit-text-dropped": ("The riddle is funny.", lambda r: r["units"][0].pop("text")),
    "resolved-unit-text": (UNNEEDED, lambda r: r["units"][0].update(text="x")),
}


@pytest.mark.parametrize("name", TEXTS, ids=list(TEXTS))
def test_text_rebinding_is_refused(monkeypatch, name):
    """A text is where Lean writes one and nowhere else: a fault of the three texted codes, NoSenseFits beside
    NoDerivation only, every open unit and no resolved one."""
    source, change = TEXTS[name]
    budget = 1 if name == "hint-on-budget" else route.WORK_BUDGET
    read_in(WORLDS["joke"](), source, budget=budget)
    _tampered(monkeypatch, change)
    with pytest.raises(CheckerUnavailable):
        read_in(WORLDS["joke"](), source, budget=budget)
