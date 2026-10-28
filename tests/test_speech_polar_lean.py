"""Speech acts' polar questions and their `Must`/`Can` refusal, read by Lean (question answering Q1.4, Q1.4b).

`parse_speech` sends a wording that begins with one of the contract's speech-acts prefixes (`speechPrefixes`), or with
F2's fronted `Is ` (Q1.4b), to `english.question` with `caller` "speech-acts" and relays the answer. Q1.4b's three
classes of changed verdicts (DRI 2026-10-27 item 4) have one test each: a gloss question gets Lean's refusal text, a
case-folded name is refused, and `Is every service reviewed?` is read as `ve ask` reads it. The later verdict rows
(DRI 2026-10-28 items 1-5) each have a test that the speech caller's verdict and text equal `ve ask`'s.
"""
from __future__ import annotations

import copy
import functools
import itertools
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
from ve.speech_acts import wording_text
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


@pytest.mark.parametrize("wording", ["Is alice reviewed?", "Is it the case that alice is reviewed?"])
def test_a_code_worded_refusal_is_leans_text_verbatim(monkeypatch, tmp_path, ve_ask_here, wording):
    """Loop recheck of fix round 5 (DRI 2026-10-28 b item 1 (c)): a refusal of a class that writes `Code: text` for
    Python's own checkers (`TypeMismatch`) carries Lean's lines verbatim (`question_lines`), the text `ve ask` prints,
    on the F1 and the F2 route alike; the code stays in its own field."""
    with pytest.raises(VEError) as caught:
        parse_speech(ENV, wording, ENV.speech_acts)
    assert caught.value.code == "TypeMismatch" and caught.value.span is not None
    assert str(caught.value) == caught.value.message == "\n".join(english_lean.question_lines(caught.value.lean_question))
    assert caught.value.to_dict()["message"] == "The question was read, and its formula does not pass the type check."
    assert_read_as_ve_ask(monkeypatch, tmp_path, ENV, wording, None, ask=ve_ask_here)


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
EVIDENCE = ROOT / "docs/question-answering/q1-4b/evidence"
sys.path.insert(0, str(EVIDENCE))
import speech_ab_f2  # noqa: E402  (the corpus: its environments and the reader's dimensions)

EXTRA = speech_ab_f2.extra_environments()


def extended(kind: str) -> Environment:
    return Environment(EXTRA[kind])


def _document(tmp_path, env) -> Path:
    document = tmp_path / "speech.ve.md"
    meta = {"format": "ve-document@1", "environment": env.to_dict(), "units": [{"id": "s1", "fence": "s1"}]}
    document.write_text("---\n" + json.dumps(meta) + "\n---\nAtlas is reviewed.\n```ve s1\nAtlas is reviewed.\n```\n")
    return document


def ve_ask(tmp_path, question: str, *options: str, env=ENV):
    """`ve ask DOCUMENT QUESTION --reading` over a document in `env`."""
    environ = {k: v for k, v in os.environ.items() if k in ENV_ALLOW or k.startswith("VE_")}
    return subprocess.run([sys.executable, "-m", "ve", "ask", str(_document(tmp_path, env)), question, "--reading",
                           *options], cwd=ROOT, env=environ, text=True, capture_output=True, timeout=HANG_TIMEOUT)


@pytest.fixture
def ve_ask_here(capsys):
    """`ve ask` as `ve_ask` runs it, through the same entry (`ve.__main__.main`) in this process, for the thousands of
    class (d) rows (a process each would take hours)."""
    from ve.__main__ import main

    def run(tmp_path, question: str, *options: str, env=ENV):
        capsys.readouterr()
        code = main(["ask", str(_document(tmp_path, env)), question, "--reading", *options])
        out = capsys.readouterr()
        return subprocess.CompletedProcess([], code, out.out, out.err)
    return run


VE_ASKS = object()  # `assert_read_as_ve_ask`'s body: whatever `ve ask` reads


def assert_read_as_ve_ask(monkeypatch, tmp_path, env, wording: str, body, ask=ve_ask) -> dict:
    """The speech caller's verdict and text for `wording` equal `ve ask`'s (run by `ask`) in the same environment (DRI
    2026-10-28 item 5 (ii)): `body` is the formula both read, None when both refuse it, or `VE_ASKS` for `ve ask`'s own
    reading (its `ast` when it reads one, else None: the differential over generated wordings). Returns `ve ask`'s
    JSON result."""
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
    done = ask(tmp_path, wording, env=env)
    structured = json.loads(ask(tmp_path, wording, "--json", env=env).stdout)["result"]
    if body is VE_ASKS:
        body = structured["ast"] if structured["status"] == "one" else None
    if body is None:
        with pytest.raises(VEError) as caught:
            parse_speech(env, wording, env.speech_acts)
        assert done.returncode == (4 if isinstance(caught.value, ResourceLimit) else 2)  # `ve ask`'s EXIT_LIMIT
        assert str(caught.value).splitlines() == done.stdout.splitlines()
        assert type(caught.value).__name__ == seen[0]["class"] == structured["class"]
    else:
        assert parse_speech(env, wording, env.speech_acts) == ({"mode": "polar", "body": body}, "question")
        assert done.returncode == 0 and english_lean.question_lines(seen[0]) == done.stdout.splitlines()
        assert structured["ast"] == body
    assert seen[0]["status"] == structured["status"] and seen[0]["text"] == structured["text"]
    return structured


def saved_verdict(env: str, wording: str) -> dict:
    """The one `verdict` row of the saved delta for this case."""
    rows = json.loads((EVIDENCE / "delta.json").read_text())["rows"]
    match = [row for row in rows if row["env"] == env and row["wording"] == wording]
    assert len(match) == 1 and match[0]["class"] == "verdict"
    return match[0]


@functools.cache
def recorded() -> frozenset[tuple[str, str]]:
    """The (env, wording) pairs of the saved head corpus (`evidence/head.json.gz`)."""
    return frozenset((r["env"], r["wording"]) for r in speech_ab_f2.recordings(str(EVIDENCE))[1])


@pytest.mark.parametrize("name", ["atlas", "beacon"])
def test_a_declared_negative_verbalisation_has_a_recorded_verdict_change(monkeypatch, tmp_path, name):
    """F1, DRI 2026-10-28 item 1: with this declared negative form, Lean reads negation where the base refused the
    question, as `ve ask` reads it."""
    wording = f"Is {name} not reviewed?"
    body = ["not", ["unary", "reviewed", ["const", name]]]
    assert_read_as_ve_ask(monkeypatch, tmp_path, extended("negative"), wording, body)
    row = saved_verdict("negative", wording)
    assert row["base"]["code"] == "SyntaxError" and row["head"]["content"]["body"] == body


@pytest.mark.parametrize("name", ["atlas2", "atlas_two", "beacon2", "beacon_two"])
def test_a_declared_name_with_digit_or_underscore_has_both_verdict_changes(monkeypatch, tmp_path, name):
    """F1, DRI 2026-10-28 item 2: bare and quoted spellings exchange acceptance, each as `ve ask` answers it; both
    outcomes are saved."""
    env = extended("names")
    bare, quoted = f"Is {name} reviewed?", f'Is "{name}" reviewed?'
    atom = ["unary", "reviewed", ["const", name]]
    assert assert_read_as_ve_ask(monkeypatch, tmp_path, env, bare, None)["code"] == "NoDerivation"
    assert_read_as_ve_ask(monkeypatch, tmp_path, env, quoted, atom)
    row = saved_verdict("names", bare)
    assert row["base"]["content"]["body"] == atom and row["head"]["code"] == "SyntaxError"
    row = saved_verdict("names", quoted)
    assert row["base"]["code"] == "InvalidInput" and row["head"]["content"]["body"] == atom


def test_a_no_question_is_read_as_ve_ask_reads_it(monkeypatch, tmp_path):
    """F3, DRI 2026-10-28 item 3: `Is no service reviewed?`, which the base refused as `UnknownAlternative`, gets the
    same verdict and text through the speech caller as through `ve ask`."""
    wording = "Is no service reviewed?"
    body = ["not", ["exists", "service", ["unary", "reviewed", ["var", 0]]]]
    assert_read_as_ve_ask(monkeypatch, tmp_path, ENV, wording, body)
    assert saved_verdict("speech", wording)["base"]["message"] == "UnknownAlternative: wording, no"


@pytest.mark.parametrize("wording", ["Is atlas checked?", "Is atlas Checked?"])
def test_an_unverbalised_predicate_is_read_as_ve_ask_reads_it(monkeypatch, tmp_path, wording):
    """F4, DRI 2026-10-28 item 4: a predicate declared without a verbalisation, which the base refused, is read with
    Lean's default words, as `ve ask` reads it."""
    body = ["unary", "checked", ["const", "atlas"]]
    assert_read_as_ve_ask(monkeypatch, tmp_path, extended("unverbalised"), wording, body)
    assert saved_verdict("unverbalised", wording)["base"]["code"] == "SyntaxError"


CLASS_D = [(row["env"], row["wording"], row["head"].get("content", {}).get("body"))
           for row in json.loads((EVIDENCE / "delta.json").read_text())["rows"]
           if speech_ab_f2.unverbalised(row) and row["wording"].split()[1] != "atlas"]


@pytest.mark.parametrize("env, wording, body", CLASS_D, ids=[w for _, w, _ in CLASS_D])
def test_every_quantified_unverbalised_verdict_row_is_read_as_ve_ask_reads_it(monkeypatch, tmp_path, env, wording,
                                                                              body):
    """DRI 2026-10-28 item 5 (class (d)): every other saved verdict row of the reader's dimensions (a grammar
    determiner over a predicate without a verbalisation) is Lean's reading, equal to `ve ask`'s."""
    assert len(CLASS_D) == 6
    assert_read_as_ve_ask(monkeypatch, tmp_path, extended(env), wording, body)


OPENING = [(row["env"], row["wording"], row["head"].get("content", {}).get("body"))
           for row in json.loads((EVIDENCE / "delta.json").read_text())["rows"] if speech_ab_f2.opening(row)]


@pytest.mark.parametrize("env, wording, body", OPENING, ids=[f"{e}:{w!r}" for e, w, _ in OPENING])
def test_every_opening_verdict_row_is_read_as_ve_ask_reads_it(monkeypatch, tmp_path, ve_ask_here, env, wording, body):
    """Recheck 2 F5, DRI 2026-10-28 item 5 (class (d)): every saved verdict row of an `Is ` question this item added
    (a sentence opening, a declared word in any slot, a case, spacing or nesting variant), in either direction, gets
    the same verdict and text through the speech caller as through `ve ask` (run in this process: 6,608 rows), for
    the wording the speech caller reads: `wording_text` trims the space around every unit's wording for every reader
    (unchanged here) and `ve ask` reads its question untrimmed, so a row with space around it is compared trimmed
    (REPORT.md FOLLOW-UP)."""
    assert len(OPENING) == speech_ab_f2.DECIDED["opening"]
    read = wording_text(wording)
    assert read.startswith("Is ") and read in wording and wording.strip(" \t\n\r\x0b\x0c") == read
    assert_read_as_ve_ask(monkeypatch, tmp_path, extended(env), read, body, ask=ve_ask_here)


def test_the_class_d_delta_rows_are_the_generators_and_name_the_trimmed_comparison():
    """Loop recheck F12, DRI 2026-10-28 b item 2: DELTA.md's class (d) rows P20-P109 are `delta_md`'s, and the Ruling
    cell of every row whose group holds a wording with space around it says it is compared on `wording_text`."""
    rows = speech_ab_f2.delta_md(str(EVIDENCE / "delta.json"), 20)
    assert rows in (EVIDENCE.parent / "DELTA.md").read_text()
    assert sum(map(speech_ab_f2.trimmed, OPENING_ROWS)) == 2760
    lines = rows.splitlines()
    noted = [line for line in lines if speech_ab_f2.TRIMMED in line]
    assert 0 < len(noted) < len(lines) == 90
    count = lambda line: int(line.split(" | ")[1].rsplit(", ", 1)[1].removesuffix(" rows").replace(",", ""))
    assert sum(map(count, lines)) == len(OPENING_ROWS) and sum(map(count, noted)) >= 2760
    for line in lines:  # a row whose first wording has space around it is always noted
        first = json.loads('"' + line.split(" | ")[3].strip("`") + '"')
        assert wording_text(first) == first or speech_ab_f2.TRIMMED in line


# ------------------------------------------------------------------ class (d) by structure (DRI 2026-10-28 b item 1)

OPENING_ROWS = [row for row in json.loads((EVIDENCE / "delta.json").read_text())["rows"] if speech_ab_f2.opening(row)]
HUNT = speech_ab_f2.hunt_recording(str(EVIDENCE))
RECHECKED = set(speech_ab_f2.RECHECKED)


def _routed(wording: str) -> bool:
    """Whether the trimmed wording starts with a prefix the speech parser routes to Lean (`_LEAN_PREFIXES`)."""
    try:
        return wording_text(wording).startswith(speech_english._LEAN_PREFIXES)
    except VEError:
        return False


def test_the_hunt_recording_is_the_generators_fixed_seed_sample():
    """DRI 2026-10-28 b item 1 (c): evidence/hunt-base.json.gz records, at the base, exactly `hunt_sample` (a fixed-
    seed sample of both hunt generators, then F8-F11 and F13), so the relay and differential tests below run over the
    committed generators' sample and not a chosen list."""
    sample = speech_ab_f2.hunt_sample()
    assert [(r["env"], r["wording"]) for r in HUNT] == [(env, wording) for env, wording, _ in sample]
    assert {name for *_, name in sample} == {"hunt_one", "hunt_two", "rechecked"}
    assert RECHECKED <= {(r["env"], r["wording"]) for r in HUNT}


@pytest.mark.parametrize("source", ["corpus", "hunt"])
def test_every_wording_the_base_read_through_is_is_in_its_acceptance_set(source):
    """DRI 2026-10-28 b item 1 (a): a wording the base read through the deleted `Is ` branch (an `Is ` wording outside
    the F1 prefixes) is in `in_base_set`, over the saved corpus and the hunt sample; and in the corpus every member the
    set holds was read at the base, so the set is the base's, not a superset."""
    base = speech_ab_f2.recordings(str(EVIDENCE))[0] if source == "corpus" else HUNT
    assert speech_ab_f2.outside_base_set(base) == []
    members = [r for r in base if speech_ab_f2.in_base_set(EXTRA[r["env"]], r["wording"])]
    assert all("content" in r["outcome"] for r in members)
    assert len(members) == (708 if source == "corpus" else 0)


@pytest.mark.parametrize("env, wording, read", [
    ("speech", "Is atlas reviewed?", True), ("speech", " Is ATLAS REVIEWED?\t", True),
    ("glossed", "Is Beacon reviewed BY staff?", True), ("f0-checked", "Is tom a cat?", True),
    ("speech", "Is atlas  reviewed?", False), ("speech", "Is atlas not reviewed?", False),
    ("speech", "Is every service reviewed?", False), ("speech", 'Is "atlas" reviewed?', False),
    ("speech", "is atlas reviewed?", False), ("speech", "Is atlas reviewed", False),
    ("unverbalised", "Is atlas checked?", False), ("speech", "Is alice reviewed?", False),
    ("speech", "Is atlas reviewed?\xa0", False)])
def test_the_base_acceptance_set_is_a_declared_name_and_form_up_to_case_and_trimmed_space(env, wording, read):
    """DRI 2026-10-28 b item 1 (a): `in_base_set` holds for `Is <name> <declared form>?` up to ASCII case and the
    space `wording_text` trims, and for nothing else: not inner spacing, a negative form, a determiner, a quoted name,
    `is`, a missing `?`, an undeclared form, a name of another sort, or a non-ASCII space."""
    assert speech_ab_f2.in_base_set(EXTRA[env], wording) is read


RELAY_CHUNKS = 32


@functools.cache
def relay_cases() -> list[tuple[str, str, str]]:
    """(source, env, wording): every saved corpus wording whose trimmed text starts with a routed prefix or is not
    ASCII (refused before any route), and every hunt-sample wording."""
    out = [("corpus", r["env"], r["wording"]) for r in speech_ab_f2.recordings(str(EVIDENCE))[1]
           if _routed(r["wording"]) or not r["wording"].isascii()]
    return out + [("rechecked" if (r["env"], r["wording"]) in RECHECKED else "hunt", r["env"], r["wording"])
                  for r in HUNT]


def assert_relayed(env_name: str, wording: str, monkeypatch) -> None:
    """`parse_speech` gives a wording whose trimmed text starts with `_LEAN_PREFIXES` to `read_question` exactly once,
    with `wording_text(wording)`, this environment, the speech vocabulary, no options and `caller=SPEECH_CALLER`, and
    returns its `ast` unchanged or raises its refusal unchanged; any other wording never reaches it."""
    env = speech_ab_f2._environment(env_name)
    seen, ast, refusal = [], ["recorded ast"], VEError("SyntaxError: recorded refusal")

    def recorder(*args, caller=None, **kwargs):
        seen.append((args, caller, kwargs))
        if len(seen) == 2:
            raise refusal
        return {"ast": ast}

    monkeypatch.setattr(speech_english, "read_question", recorder)
    try:
        text = wording_text(wording)
    except VEError:
        text = None
    if text is None or not text.startswith(speech_english._LEAN_PREFIXES):
        with pytest.raises(VEError):  # a wording outside the routed prefixes: refused or read by another route
            parse_speech(env, wording, env.speech_acts)
        assert seen == []
        return
    content, kind = parse_speech(env, wording, env.speech_acts)
    assert (content, kind) == ({"mode": "polar", "body": ast}, "question") and content["body"] is ast
    (args, caller, kwargs), = seen
    assert caller == SPEECH and kwargs == {} and len(args) == 4
    assert args[0] is env and args[1] == text and type(args[2]) is EnglishVocabulary and args[3] == {}
    with pytest.raises(VEError) as caught:
        parse_speech(env, wording, env.speech_acts)
    assert caught.value is refusal and len(seen) == 2 and seen[1][0][1] == text


@pytest.mark.parametrize("chunk", range(RELAY_CHUNKS))
def test_parse_speech_relays_every_routed_corpus_and_hunted_wording_unchanged(monkeypatch, chunk):
    """DRI 2026-10-28 b item 1 (b): over every routed (or non-ASCII) wording of the saved corpus and every wording of
    the hunt sample (F8-F11 and F13 among them), the speech parser makes no decision of its own between the wording
    and Lean's reader (`assert_relayed`), so any `Is ` wording outside the base's set reads as Lean reads it."""
    cases = relay_cases()
    assert len(cases) > 290_000 and {s for s, *_ in cases} == {"corpus", "hunt", "rechecked"}
    for _, env, wording in cases[chunk::RELAY_CHUNKS]:
        assert_relayed(env, wording, monkeypatch)


@pytest.mark.parametrize("env, wording", sorted(RECHECKED), ids=[f"rechecked:{e}:{w!r}" for e, w in sorted(RECHECKED)])
def test_a_rechecked_wording_is_relayed_unchanged(monkeypatch, env, wording):
    """Loop recheck F8-F11, F13 (DRI 2026-10-28 b item 1 (b)): each wording the recheck found outside the base's set
    is relayed to Lean's reader unchanged."""
    assert_relayed(env, wording, monkeypatch)


DIFFERENTIAL = [(r["env"], r["wording"]) for r in HUNT if _routed(r["wording"])
                and not wording_text(r["wording"]).startswith(("Must ", "Can "))]


@pytest.mark.parametrize("env, wording", DIFFERENTIAL, ids=[
    f"{'rechecked' if (e, w) in RECHECKED else 'hunt'}:{e}:{w!r}" for e, w in DIFFERENTIAL])
def test_a_hunted_wording_gets_ve_asks_verdict_and_text(monkeypatch, tmp_path, ve_ask_here, env, wording):
    """DRI 2026-10-28 b item 1 (c), loop recheck F8-F11 and F13: for every routed wording of the hunt sample (modal
    ones excepted, as item 5), the speech caller's verdict and text equal `ve ask`'s on `wording_text(wording)`."""
    assert len(DIFFERENTIAL) > 2_000 and RECHECKED <= set(DIFFERENTIAL)
    assert_read_as_ve_ask(monkeypatch, tmp_path, extended(env), wording_text(wording), VE_ASKS, ask=ve_ask_here)


def test_the_corpus_asks_every_declared_word_in_every_slot_and_records_it():
    """F5, F6, F7, DRI note 2026-10-28c (a): `coverage` finds the saved corpus complete: every environment the evidence
    asks in (Q1.4's and the three added), every grammar rule (but those needing a two-place verbalisation, which none
    declares), every declared word in every slot and every pair of words in every two slots, the case and spacing
    variants and each rule's sentence in each formula place, all recorded."""
    assert set(EXTRA) == {"speech", "glossed", "f0-reviewed", "f0-checked", "negative", "names", "unverbalised"}
    assert speech_ab_f2.coverage(speech_ab_f2.all_sentences(), recorded()) == []
    cases = {(env, w) for env, w, _ in speech_ab_f2.opening_cases()}
    for wording in ("Is there a service that is reviewed?", "Is this impossible?",
                    "Is every service that is reviewed reviewed?"):
        assert ("speech", wording) in cases


@pytest.mark.parametrize("env", sorted(EXTRA))
def test_the_corpus_words_are_every_word_the_environment_declares(env):
    """DRI note 2026-10-28c (a): each category's words are the environment's whole declaration, never a chosen one:
    every constant bare and quoted, every sort's nouns (its name when it declares none), every one-place predicate's
    positive and not-form."""
    declared = EXTRA[env]["vocabulary"]
    words = speech_ab_f2.vocabulary(EXTRA[env])
    assert sorted(w for (w,) in words["constant"]) == sorted([*declared["constants"],
                                                              *(f'"{c}"' for c in declared["constants"])])
    for sort, d in declared["sorts"].items():
        nouns = {d["verbalisation"]["singular"], d["verbalisation"]["plural"]} if "verbalisation" in d else {sort}
        assert nouns <= {w for (w,) in words["noun"]}
    for name, p in declared["predicates"].items():
        if len(p["arguments"]) == 1:
            forms = (p.get("verbalisation") or f"{{0}} is {name}", p.get("negative_verbalisation")
                     or f"{{0}} is not {name}")
            assert {tuple(form.split()[1:]) for form in forms} <= set(words["relative"])


def _rows(env: str, tag: str, change) -> dict:
    """`all_sentences` with the rows of one rule's sentence changed by `change`."""
    sentences = {e: dict(s) for e, s in speech_ab_f2.all_sentences().items()}
    template, rows = sentences[env][tag]
    sentences[env][tag] = (template, change(rows))
    return sentences


def _without(env: str, tag: str) -> dict:
    return {e: {t: v for t, v in s.items() if (e, t) != (env, tag)} for e, s in speech_ab_f2.all_sentences().items()}


SAFE = {  # DRI note 2026-10-28c (a): each case the audit must refuse, and what its refusal names
    "a declared constant missing from a slot": (
        lambda: _rows("names", "atom.eq", lambda rows: [f for f in rows if f[0] != ("atlas2",)]), None,
        "names atom.eq: slot 1 (constant) 'atlas2'"),
    "a quoted spelling missing": (
        lambda: _rows("names", "sentence.plain", lambda rows: [f for f in rows if not f[0][0].startswith('"')]), None,
        "names sentence.plain: slot 1 (constant) '\"atlas2\"'"),
    "an environment missing": (
        lambda: {e: s for e, s in speech_ab_f2.all_sentences().items() if e != "names"}, None,
        "names: environment never asked"),
    "a grammar rule with no sentence": (
        lambda: _without("speech", "formula.negation"), None, "speech formula.negation: grammar rule with no sentence"),
    "a predicate form missing": (
        lambda: _rows("negative", "sentence.plain", lambda rows: [f for f in rows if f[1] != ("is", "not", "reviewed")]),
        None, "negative sentence.plain: slot 2 (relative) 'is not reviewed'"),
    "a second slot never varied": (
        lambda: _rows("names", "atom.eq", lambda rows: [(f[0], rows[0][1]) for f in rows]), None,
        "names atom.eq: slot 2 (constant) '\"atlas2\"'"),
    "a pair never asked together (F7)": (
        speech_ab_f2.all_sentences, ("names", 'Is "atlas2" the same as beacon?'),
        "names atom.eq: slot 1 (constant) '\"atlas2\"' with slot 2 (constant) 'beacon'"),
    "a case variant never asked (hunt 1)": (
        speech_ab_f2.all_sentences, ("speech", "Is Every service reviewed?"),
        "speech formula.universal: case variant 'Is Every service reviewed?'"),
    "a member shape of the base's acceptance set never asked (DRI 2026-10-28 b item 1 (a))": (
        speech_ab_f2.all_sentences, ("glossed", "Is atlas reviewed by STAFF?"),
        "glossed base set 'atlas is reviewed by staff': case variant 'Is atlas reviewed by STAFF?' never asked"),
    "a nesting never asked (hunt 1)": (
        lambda: _without("speech", speech_ab_f2.nest_tag("negation", 6, "formula.universal")), None,
        "speech negation: formula.universal in formula place 6 never asked"),
}


@pytest.mark.parametrize("case", SAFE)
def test_the_audit_fails_on_an_incomplete_corpus_and_names_the_gap(monkeypatch, capsys, case):
    """DRI note 2026-10-28c (a): the audit says the corpus is complete under one condition only; a word, spelling,
    form, slot, pair, variant, nesting, rule or environment the corpus never asked fails it, and the failure names
    it."""
    sentences, unrecorded, named = SAFE[case]
    sentences = sentences()
    base, head, rows = speech_ab_f2.recordings(str(EVIDENCE))
    if unrecorded:
        head = [r for r in head if (r["env"], r["wording"]) != unrecorded]
    assert any(line.startswith(named) for line in speech_ab_f2.coverage(sentences, {
        (r["env"], r["wording"]) for r in head}))
    monkeypatch.setattr(speech_ab_f2, "all_sentences", lambda: sentences)
    monkeypatch.setattr(speech_ab_f2, "recordings", lambda folder: (base, head, rows))
    capsys.readouterr()
    assert speech_ab_f2.check(str(EVIDENCE / "delta.json")) == 1
    assert "unasked: " in capsys.readouterr().out


@pytest.mark.parametrize("recording", ["corpus", "hunt"])
@pytest.mark.parametrize("wording", ["Is every service reviewed?", "Is atlas not reviewed?", "Is atlas  reviewed?"])
def test_the_audit_fails_when_the_base_read_outside_its_acceptance_set(monkeypatch, capsys, recording, wording):
    """DRI 2026-10-28 b item 1 (a): `check` exits 1 and names the wording when a base recording (the corpus or the
    hunt sample) has a reading of the deleted `Is ` branch outside `in_base_set`."""
    base, head, rows = speech_ab_f2.recordings(str(EVIDENCE))
    read = {"env": "speech", "wording": wording, "outcome": {"kind": "question", "content": {}, "warnings": []}}
    if recording == "corpus":
        monkeypatch.setattr(speech_ab_f2, "recordings", lambda folder: ([*base, read], head, rows))
    else:
        monkeypatch.setattr(speech_ab_f2, "hunt_recording", lambda folder: [*HUNT, read])
    capsys.readouterr()
    assert speech_ab_f2.check(str(EVIDENCE / "delta.json")) == 1
    assert f"the base read speech {wording!r} outside" in capsys.readouterr().out


HUNTED = [("names", 'Is it not the case that "atlas2" is reviewed?'), ("names", 'Is "atlas2" the same as beacon?'),
          ("f0-reviewed", "Is it not the case that atlas is reviewed?"), ("speech", "Is Every service reviewed?"),
          ("speech", "Is atlas  reviewed?"), ("speech", "Is every service reviewed? "),
          ("speech", "Is it not the case that every service is reviewed?"),
          ("speech", "Is it not the case that either atlas is reviewed or atlas is reviewed, or both?"),
          ("speech", " Is every service reviewed?"), ("names", "Is BEACON reviewed?"),
          ("glossed", "Is atlas reviewed YET never reviewed?")]


@pytest.mark.parametrize("env, wording", HUNTED, ids=[f"{e}:{w!r}" for e, w in HUNTED])
def test_every_hunted_form_is_asked_and_recorded_as_a_signed_verdict(env, wording):
    """Loop recheck 2 F7 (another declared name, in another slot) and the forms DRI note 2026-10-28c's hunts found
    (Q1.4's own environments, a case, spacing or nesting variant, a leading space, a case-folded name, a gloss in
    capitals): each is a corpus case saved as a class (d) verdict row, in either direction; that each equals `ve
    ask`'s reading is `test_every_opening_verdict_row_is_read_as_ve_ask_reads_it`."""
    assert (env, wording) in {(e, w) for e, w, _ in speech_ab_f2.opening_cases()}
    assert speech_ab_f2.opening(saved_verdict(env, wording))


F6 = ["Is every service not reviewed?", "Is some service not reviewed?", "Is no service not reviewed?",
      "Is there a service that is not reviewed?", "Is every service that is not reviewed reviewed?"]


@pytest.mark.parametrize("wording", F6)
def test_a_declared_not_form_is_asked_in_every_opening_and_recorded(wording):
    """Loop recheck 1 F6: with the not-form declared (`negative`), openings the base refused and Lean reads are
    corpus cases, in each place and each polarity, saved as verdict rows of class (d); that each equals `ve ask`'s
    reading is `test_every_opening_verdict_row_is_read_as_ve_ask_reads_it`."""
    assert ("negative", wording) in {(env, w) for env, w, _ in speech_ab_f2.opening_cases()}
    row = saved_verdict("negative", wording)
    assert speech_ab_f2.opening(row) and "error" in row["base"] and row["head"]["kind"] == "question"


def test_every_opening_sentence_is_spelled_in_both_polarities():
    """Loop recheck 1 F6's class: each place a predicate fills in an opening sentence is spelled with its positive and
    its not-form (the declared one where there is one), so an environment's negative words are never left unasked."""
    for env, raw in EXTRA.items():
        relative = speech_ab_f2.vocabulary(raw)["relative"]
        assert {"not" in form for form in relative} == {True, False}
        template, rows = speech_ab_f2.all_sentences()[env]["guard.two"]
        slots = [t for t in template if type(t) is speech_ab_f2._Slot]
        places = [i for i, t in enumerate(slots) if t == "relative"]
        assert len(places) == 3  # `every <noun> who <relative> and <relative> <relative>`
        for i, j in itertools.combinations(places, 2):  # every form, and every pair of forms, in each two places
            assert {(f[i], f[j]) for f in rows} == set(itertools.product(relative, relative))


def test_the_corpus_records_every_grammar_determiner_and_predicate_form():
    """The added corpus is generated from the grammar's determiners, so a determiner the grammar gains is a recorded
    case (in both environments, both polarities) before its delta can be audited."""
    assert set(speech_ab_f2.determiners()) >= {"every", "some", "no"}
    cases = speech_ab_f2.reader_cases()
    assert {(env, wording) for env, wording, _ in cases} <= recorded()
    for det in speech_ab_f2.determiners():
        for env, word in (("speech", "reviewed"), ("unverbalised", "checked"), ("unverbalised", "Checked")):
            assert {(env, f"Is {det} service {word}?"), (env, f"Is {det} service not {word}?")} <= recorded()


def test_the_extended_delta_audits_every_verdict_as_signed():
    """Every verdict row of the saved delta is in exactly one signed class, with the recorded counts."""
    script = EVIDENCE / "speech_ab_f2.py"
    for command in ("audit", "check"):
        done = subprocess.run([sys.executable, str(script), command, str(EVIDENCE / "delta.json")],
                              capture_output=True, text=True, timeout=HANG_TIMEOUT)
        assert done.returncode == 0, done.stdout + done.stderr
        summary = json.loads(done.stdout)
        assert {key: summary[key] for key in speech_ab_f2.DECIDED} == speech_ab_f2.DECIDED
        assert summary["failing"] == 0


@pytest.mark.parametrize("env, wording, mutation", [
    ("negative", "Is atlas not reviewed?", "remove"), ("negative", "Is atlas not reviewed?", "change_head"),
    ("speech", "Is no service reviewed?", "remove"), ("speech", "Is no service reviewed?", "change_head"),
    ("unverbalised", "Is atlas checked?", "remove"), ("unverbalised", "Is no service Checked?", "change_head"),
    ("speech", "Is there a service that is reviewed?", "remove"), ("speech", "Is this impossible?", "remove"),
    ("speech", "Is every service that is reviewed reviewed?", "remove"),
    ("negative", "Is every service not reviewed?", "remove"),
    ("negative", "Is there a service that is not reviewed?", "remove"),
    ("negative", "Is every service that is not reviewed reviewed?", "remove"),
    ("names", 'Is "atlas2" the same as beacon?', "remove")])
def test_the_delta_audit_catches_missing_or_unclassified_verdicts(env, wording, mutation):
    """A missing case or a verdict outside its class cannot pass the audit (`audit` over the recordings' rows)."""
    rows = list(speech_ab_f2.recordings(str(EVIDENCE))[2])
    at = next(i for i, row in enumerate(rows) if row["env"] == env and row["wording"] == wording)
    if mutation == "remove":
        del rows[at]
    else:
        rows[at] = copy.deepcopy(rows[at])
        rows[at]["head"]["content"]["body"] = ["unary", "reviewed", ["const", "atlas"]]
    counts, bad = speech_ab_f2.audit(rows)
    assert bad or counts != speech_ab_f2.DECIDED


def test_the_audit_fails_on_a_delta_that_is_not_the_recordings_summary(tmp_path):
    """delta.json is checked against base.json.gz and head.json.gz beside it: a verdict row removed from it fails."""
    delta = json.loads((EVIDENCE / "delta.json").read_text())
    del delta["rows"][0]
    (tmp_path / "delta.json").write_text(json.dumps(delta))
    for name in ("base.json.gz", "head.json.gz"):
        (tmp_path / name).symlink_to(EVIDENCE / name)
    done = subprocess.run([sys.executable, str(EVIDENCE / "speech_ab_f2.py"), "audit", str(tmp_path / "delta.json")],
                          capture_output=True, text=True, timeout=HANG_TIMEOUT)
    assert done.returncode == 1 and "delta.json is not the summary" in done.stdout


@pytest.mark.parametrize("wording, body", [
    ("Is every service reviewed?", ["forall", "service", ["unary", "reviewed", ["var", 0]]]),
    ("Is some service reviewed?", ["exists", "service", ["unary", "reviewed", ["var", 0]]]),
    ("Is a service reviewed?", None)])
def test_a_quantified_f2_question_is_read_as_ve_ask_reads_it(monkeypatch, tmp_path, wording, body):
    """Class (c): `Is every service reviewed?` (and `some`), which Python refused as `UnknownAlternative`, gets the
    same verdict and text through the speech caller as through `ve ask`; `Is a service reviewed?` gets the same
    refusal, whose rephrasings are those two questions (spec 4.1 row 14)."""
    structured = assert_read_as_ve_ask(monkeypatch, tmp_path, ENV, wording, body)
    if body is None:
        assert structured["rephrasings"] == [wording.replace(" a ", " every "), wording.replace(" a ", " some ")]


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
