"""sn-b6c: the members a `senses.read` route answer gains (byte spans and glosses in the sense map, the texts of
docs/spec/senses.md 3.2 and plan 2.8), each equal to Lean's and bound to the request; and their rebinding fuzz.
sn-b6d: the re-read of a rendering under a candidate's projection, and Lean's line for a word and gloss.
Retyping and dropping every field is `test_senses_route.py::test_genuine_response_field_mutations_are_rejected`."""
from __future__ import annotations

import hashlib
import json
from copy import deepcopy

import pytest

from ve.backends import lean as lean_backend
from ve.backends import senses as route
from ve.english_grammar import actions_version
from ve.errors import CheckerUnavailable, VEError
from test_senses_route import GENUINE, PACK, S2_WORLD, WORLDS, read_in

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


# sn-b6d (1): the re-read (`VE.Senses.Run.rereadJson`), R3 (reviews/dri-decisions-20261108-sn-b6c.md item 3).
TWO = "The riddle is funny."
S16 = "The riddle is odd."


def reread(source, sentence, candidate, rendering, budget=route.WORK_BUDGET):
    env, overlay = WORLDS["joke"]()
    return route.read(env, source, [PACK], overlay=overlay, budget=budget,
                      reread=(sentence, candidate, rendering))["reading"]


@pytest.mark.parametrize("source, candidate, rendering, outcome", [
    (TWO, 0, TWO, "same"), (TWO, 1, TWO, "same"),
    (TWO, 0, "The riddle is funny (meaning amusing).", "same"),
    (TWO, 0, "The riddle is funny (meaning strange).", "different"),  # the other candidate's formula
    (S16, 0, S16, "same"), (S16, 0, "The riddle is purple.", "different"),
    ("In this document, odd means strange. " + TWO, 1, "The riddle is odd and funny.", "different"),
])
def test_each_candidate_rereads_under_its_own_projection(source, candidate, rendering, outcome):
    """R3: Lean's outcome for a rendering of a candidate (a unit after a preamble line counts it: sentence 1)."""
    sentence = 1 if source.startswith("In this") else 0
    assert reread(source, sentence, candidate, rendering)["reread"] == {
        "sentence": sentence, "candidate": candidate, "outcome": outcome}


def test_a_base_projection_rendering_is_refused():
    """The task's test (plan B7's seeded bug): each candidate's bare rendering is `same` only under its own projection
    (the base projection, with no line for `funny`, does not resolve it: the unit is open), and what a renderer
    writes under the base projection (sn-b7b8: a quoted sense name) is `different`."""
    assert reread(TWO, 0, 0, TWO)["status"] == "open"
    assert [reread(TWO, 0, j, TWO)["reread"]["outcome"] for j in (0, 1)] == ["same", "same"]
    for j in (0, 1):
        quoted = 'The riddle is classified as "sense__funny_' + str(j + 1) + '".'
        assert reread(TWO, 0, j, quoted)["reread"]["outcome"] == "different"


def test_a_rendering_that_is_not_one_sentence_is_refused_by_lean():
    for rendering, why in ((TWO + " " + TWO, "is not one sentence"), ("", r"does not lex \(EmptyDocument\)"),
                           ("The riddle is funny", r"does not lex \(Unterminated\)")):
        with pytest.raises(VEError, match=why):
            reread(TWO, 0, 0, rendering)
    with pytest.raises(VEError, match="no candidate"):
        reread(TWO, 0, 2, TWO)
    with pytest.raises(VEError, match="no unit"):
        reread(TWO, 1, 0, TWO)
    with pytest.raises(VEError, match="Invalid senses request"):
        reread(TWO, -1, 0, TWO)


LONG = "Every joke that is funny is funny and every joke that is funny is funny."


def test_the_reread_is_unknown_when_its_budget_ends():
    """DRI item 3: the budget case is `unknown`; the same rendering under an adequate budget is `different` (it reads
    to another formula). The source itself reads within both budgets."""
    assert reread(TWO, 0, 0, LONG, budget=4000)["reread"]["outcome"] == "unknown"
    assert reread(TWO, 0, 0, LONG)["reread"]["outcome"] == "different"


def test_a_long_rendering_ends_within_its_limits():
    """The evaluator rule (DRI 2026-10-27): the rendering is lexed once under S2's length limit and read once against
    the request's budget; a large well-formed one ends within the deadline, a longer one is refused by the lexer."""
    chain = LONG[:-1] + " and every joke that is funny is funny" * 50 + "."
    assert reread(TWO, 0, 0, chain)["reread"]["outcome"] == "different"
    with pytest.raises(VEError, match=r"does not lex \(TextTooLong\)"):
        reread(TWO, 0, 0, LONG[:-1] + " and every joke that is funny is funny" * 300 + ".")


def test_a_refused_reading_has_no_reread():
    answer = reread("Alice tells the riddle.", 0, 0, TWO, budget=1)
    assert answer["status"] == "budget" and "reread" not in answer


def _raw(member, value, budget=route.WORK_BUDGET):
    """Lean's row for a request whose member is `value`, past the relay's own request checks."""
    env, overlay = WORLDS["joke"]()
    case = route.request(env, TWO, [PACK.decode()], overlay=overlay, budget=budget, **{member: value})
    [row] = lean_backend.run("senses.read", route.EXECUTABLE, [case], runner="ve_senses_route",
                             timeout=lean_backend.configured_timeout(lean_backend.ROUTE_TIMEOUT))
    return row


@pytest.mark.parametrize("budget", [route.WORK_BUDGET, 1], ids=["admitted", "refused"])
@pytest.mark.parametrize("member, value", [
    ("reread", 7), ("reread", {}), ("reread", {"sentence": 0, "candidate": 0}),
    ("reread", {"sentence": True, "candidate": 0, "rendering": TWO}),
    ("reread", {"sentence": 0, "candidate": 0, "rendering": TWO + " " + TWO}),
    ("line", 7), ("line", {"word": 1, "gloss": "amusing"}), ("line", {"word": "funny", "gloss": "amusing", "x": 1}),
])
def test_lean_refuses_a_malformed_member_before_reading(member, value, budget):
    """The members are decoded before any reading, on an admitted and on a refused reading alike."""
    row = _raw(member, value, budget)
    assert row["status"] == "error" and "result" not in row
    assert _raw(member, {"reread": {"sentence": 0, "candidate": 0, "rendering": TWO},
                         "line": {"word": "funny", "gloss": "amusing"}}[member], budget)["status"] == "ok"


@pytest.mark.parametrize("value", [["funny", "amusing"], ("funny",), ("funny", 1)])
def test_the_relay_refuses_a_malformed_line_request(value):
    env, overlay = WORLDS["joke"]()
    with pytest.raises(VEError, match="Invalid senses request"):
        route.read(env, TWO, [PACK], overlay=overlay, line=value)


# sha256 of each GENUINE answer (`json.dumps(result, sort_keys=True, separators=(",", ":"))`), recorded with main's
# ve_senses_route at the merge base 9ba8aeaed, before sn-b6d.
MAIN_DIGESTS = {
    "open": "d7b986ecb1c554d2d1c36ce969bf0f6d3b7d878c08f646494e149fd947a5713d",
    "one": "5db5cb38e0c3bf791f13df6f9ed025b8c7521c4a4b339fc238ccabd43de5159b",
    "none": "9e3fae925071db320bb2fa4264e73f3dde70c8831e706ca2428fc6aed6d12448",
    "budget": "f5fde6c89931d2e9e7ef481bfeaa4d44d5a13e74f5e69c19ca3c75fbc56ea783",
    "many": "685c74c70564c3fb3c33a7ec41dc8b92a02fc87ad8e4a404fc67784e5938ab79",
    "diverge": "16e81c8a6d010aba52b9e316cce94aa5712107c01b1fce62cda2e6d38a7adee0",
    "dictionary": "fa6aeeb8259e0031f55a03e80b39c97cd40555e8026ce97af1fae5b1db7ef440",
    "warnings": "6323bc83475d9afa1ab7b029340ff5e3516b8362615f6b481f3403b5d03c28b4",
    "hint": "ac05d1f92a51efd2a5112c85c48c9002d97f1d6007236260bd28e46e096c9593",
}
# The grammar's `actions_version` in a reading's identities when those digests were recorded. It moves with the grammar
# on purpose (et-5 and en-e3a each made it 46; their merge made it 47), so an answer's version is checked against the
# lock's, its owner, and the rest against main's bytes with the recorded version in its place.
MAIN_ACTIONS_VERSION = "45"


@pytest.mark.parametrize("name, place, pack, source, budget", GENUINE, ids=[g[0] for g in GENUINE])
def test_a_golden_request_without_the_members_keeps_its_answer(name, place, pack, source, budget):
    """DRI item 3: every golden request without `reread` or `line` keeps main's answer (equal canonical JSON), but
    for the grammar's actions version, which must be the lock's."""
    answer = read_in(S2_WORLD() if place == "s2" else WORLDS[place](), source, pack, budget=budget)
    identities = answer.get("reading", {}).get("identities")
    if identities is not None:
        assert identities["actions_version"] == actions_version()
        identities["actions_version"] = MAIN_ACTIONS_VERSION
    assert hashlib.sha256(json.dumps(answer, sort_keys=True, separators=(",", ":")).encode()).hexdigest() == \
        MAIN_DIGESTS[name]


def test_the_members_only_add_to_the_answer():
    """With `reread` and `line` asked, the answer is the one without them plus the two members (and its own request
    identity)."""
    env, overlay = WORLDS["joke"]()
    plain = route.read(env, TWO, [PACK], overlay=overlay)
    asked = route.read(env, TWO, [PACK], overlay=overlay, reread=(0, 1, TWO), line=("funny", "strange"))
    assert asked.pop("line") == {"word": "funny", "gloss": "strange", "text": "In this document, funny means strange."}
    assert asked["reading"].pop("reread") == {"sentence": 0, "candidate": 1, "outcome": "same"}
    assert asked.pop("request_id") != plain.pop("request_id") and asked == plain


def _tampered_result(monkeypatch, change):
    real = lean_backend.run_limited

    def changed(*args, **kwargs):
        answer = real(*args, **kwargs)
        rows = json.loads(answer.stdout)
        change(rows[0]["result"])
        answer.stdout = json.dumps(rows).encode()
        return answer
    monkeypatch.setattr(lean_backend, "run_limited", changed)


REREADS = {
    "sentence": lambda r: r["reading"]["reread"].update(sentence=1),
    "candidate-other": lambda r: r["reading"]["reread"].update(candidate=0),
    "candidate-out-of-range": lambda r: r["reading"]["reread"].update(candidate=2),
    "outcome": lambda r: r["reading"]["reread"].update(outcome="maybe"),
    "dropped": lambda r: r["reading"].pop("reread"),
    "extra": lambda r: r["reading"]["reread"].update(rendering=TWO),
}


@pytest.mark.parametrize("change", REREADS, ids=list(REREADS))
def test_reread_rebinding_is_refused(monkeypatch, change):
    """The re-read names the request's unit and candidate, one of the answer's, with one of Lean's outcomes."""
    _tampered_result(monkeypatch, REREADS[change])
    with pytest.raises(CheckerUnavailable, match="re-read|missing or unknown"):
        reread(TWO, 0, 1, TWO)


def test_an_unasked_reread_is_refused(monkeypatch):
    _tampered_result(monkeypatch, lambda r: r["reading"].update(reread={"sentence": 0, "candidate": 0,
                                                                        "outcome": "same"}))
    with pytest.raises(CheckerUnavailable, match="missing or unknown"):
        read_in(WORLDS["joke"](), TWO)


# sn-b6d (2): Lean's line for a requested word and gloss (`VE.Senses.Run.lineJson`, `lineOf`), R3.
def line(word, gloss):
    env, overlay = WORLDS["joke"]()
    return route.read(env, TWO, [PACK], overlay=overlay, line=(word, gloss))["line"]


def test_the_line_is_leans():
    assert line("funny", "amusing") == {"word": "funny", "gloss": "amusing",
                                        "text": "In this document, funny means amusing."}
    assert line("tells", "says aloud")["text"] == "In this document, tells means says aloud."
    assert line("funny", "purple") == {"word": "funny", "gloss": "purple", "code": "UnknownGloss"}
    assert line("zany", "amusing") == {"word": "zany", "gloss": "amusing", "code": "UnknownWord"}
    env, overlay = WORLDS["joke"]()  # on a refused reading too
    assert route.read(env, "Alice tells the riddle.", [PACK], overlay=overlay, budget=1, line=("odd", "strange"))[
        "line"] == {"word": "odd", "gloss": "strange", "text": "In this document, odd means strange."}


LINES_TAMPERED = {
    "word-swapped": ("funny", "amusing", lambda l: l.update(word="amusing", gloss="funny")),
    "gloss": ("funny", "amusing", lambda l: l.update(gloss="strange")),
    "text-for-unknown": ("funny", "purple", lambda l: (l.pop("code"), l.update(text="x"))),
    "code-for-known": ("funny", "amusing", lambda l: (l.pop("text"), l.update(code="UnknownGloss"))),
    "code-other": ("zany", "amusing", lambda l: l.update(code="Unresolved")),
    "code-word-for-gloss": ("funny", "purple", lambda l: l.update(code="UnknownWord")),
    "code-gloss-for-word": ("zany", "amusing", lambda l: l.update(code="UnknownGloss")),
    "text-empty": ("funny", "amusing", lambda l: l.update(text="")),
}


@pytest.mark.parametrize("change", LINES_TAMPERED, ids=list(LINES_TAMPERED))
def test_line_rebinding_is_refused(monkeypatch, change):
    word, gloss, mutate = LINES_TAMPERED[change]
    _tampered_result(monkeypatch, lambda r: mutate(r["line"]))
    with pytest.raises(CheckerUnavailable, match="line"):
        line(word, gloss)


ONLY_TYPED = {
    "text-x": (lambda r: r["line"].update(text="x"), ("line", "text"), "x"),
    "text-other-gloss": (lambda r: r["line"].update(text="In this document, funny means strange."), ("line", "text"),
                         "In this document, funny means strange."),
    "text-other-word": (lambda r: r["line"].update(text="In this document, odd means strange."), ("line", "text"),
                        "In this document, odd means strange."),
    "outcome-different": (lambda r: r["reading"]["reread"].update(outcome="different"), ("reread", "outcome"),
                          "different"),
    "outcome-unknown": (lambda r: r["reading"]["reread"].update(outcome="unknown"), ("reread", "outcome"), "unknown"),
}


@pytest.mark.parametrize("change", ONLY_TYPED, ids=list(ONLY_TYPED))
def test_leans_text_and_outcome_are_only_typed(monkeypatch, change):
    """Review sn-b6d F1 (DELTA rows 1-2): the relay binds the line's word and gloss and the re-read's unit and
    candidate, but Lean's English (the line's `text`) and verdict (the re-read's `outcome`) are only typed (R8): a
    well-typed changed value reaches the caller as Lean gave it, since Python does not recompute Lean's answer.
    Their typing is `test_line_rebinding_is_refused[text-empty]`, `test_reread_rebinding_is_refused[outcome]` and
    `test_senses_route.py::test_genuine_response_field_mutations_are_rejected`."""
    mutate, (member, field), value = ONLY_TYPED[change]
    _tampered_result(monkeypatch, mutate)
    env, overlay = WORLDS["joke"]()
    result = route.read(env, TWO, [PACK], overlay=overlay, reread=(0, 1, TWO), line=("funny", "amusing"))
    answer = result["line"] if member == "line" else result["reading"]["reread"]
    assert answer[field] == value
    assert (result["line"]["word"], result["line"]["gloss"]) == ("funny", "amusing")
    assert (result["reading"]["reread"]["sentence"], result["reading"]["reread"]["candidate"]) == (0, 1)


@pytest.mark.parametrize("change", ["dropped", "unasked"])
def test_a_line_is_there_exactly_when_asked(monkeypatch, change):
    if change == "dropped":
        _tampered_result(monkeypatch, lambda r: r.pop("line"))
        call = lambda: line("funny", "amusing")  # noqa: E731
    else:
        _tampered_result(monkeypatch, lambda r: r.update(line={"word": "funny", "gloss": "amusing", "text": "x"}))
        call = lambda: read_in(WORLDS["joke"](), TWO)  # noqa: E731
    with pytest.raises(CheckerUnavailable, match="request and dictionary identities"):
        call()


def test_a_candidate_with_its_lines_emptied_is_refused(monkeypatch):
    """Found by the relay mutation gate on the asked fixture (sn-b6d): a candidate resolves a word, so Lean always
    writes it a line."""
    _tampered_result(monkeypatch, lambda r: r["reading"]["units"][0]["candidates"][0].update(lines=""))
    with pytest.raises(CheckerUnavailable, match="candidate is malformed"):
        read_in(WORLDS["joke"](), S16)
