"""CI-3 (commands-imperatives section 7) through `english.command`: steps, `Then` steps and conditions written first,
and the saved A/B's b1 rows pinned to their Lean fixtures (DRI 2026-10-28 item 2(b))."""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from tests import lean_routes
from tests.lean_service_corpus import command_cases
from test_speech_source_lean import lean  # noqa: F401  (the speech-source route fixture)

ROOT = Path(__file__).resolve().parents[1]
AB = json.loads((ROOT / "docs/commands-imperatives/ci-3/AB.json").read_text())


@pytest.mark.parametrize("row", [r for r in AB["changed"] if r["class"] == "b1"], ids=lambda r: r["wording"])
def test_each_b1_row_is_a_route_fixture_that_reads(row):
    fixtures = (ROOT / "lean/VE/Commands/RunExamples.lean").read_text()
    assert f'"{row["wording"]}"' in fixtures
    assert row["base"].startswith("VE.Commands.StepOutcome.refused")
    assert row["head"].split()[0].rsplit(".", 1)[1] in ("one", "steps", "many")


def _refusal(head):
    """The (code, text) of an A/B head `VE.Commands.StepOutcome.refused "<code>" "<text>"` (Lean's `repr`)."""
    match = re.fullmatch(r'VE\.Commands\.StepOutcome\.refused\s+"(\w+)"\s+"(.*)"', head, re.S)
    assert match, head
    return match.group(1), match.group(2)


@pytest.mark.parametrize("row", [r for r in AB["changed"] if r["class"] == "rr"], ids=lambda r: r["wording"])
def test_each_rr_row_is_a_route_fixture_refused_with_its_code(row):
    """reviews/dri-decisions-20261109-ci-3-codes.md item 1's condition: every refused -> refused row stays an exact-code
    guard of RunExamples.lean (`abRefused`, refused through the mode with that code and text)."""
    fixtures = (ROOT / "lean/VE/Commands/RunExamples.lean").read_text()
    table = fixtures[fixtures.index("def abRefused"):fixtures.index("#guard abRefused.all")]
    code, text = _refusal(row["head"])
    assert f'("{row["wording"]}", "{code}", "' in table
    assert code == "NoDerivation" or text in fixtures
    assert row["base"].startswith("VE.Commands.StepOutcome.refused")


def test_saved_ab_has_no_stop_row_and_no_surface_kind_flip():
    assert [r["wording"] for r in AB["changed"] if r["class"] not in ("b1", "b2", "rr")] == []
    assert AB["surface_kind_flips"] == [] and AB["corpus_if_then_literals"] == 0


def ask(wording):
    [case] = [c for c in command_cases() if c["id"] == "click"]
    [row] = lean_routes.rows("english.command", [{**case, "wording": wording}])
    return row["result"]


@pytest.mark.parametrize("wording", ["  Click Check, then do not share the token.",
                                     "  Click Check, then  click Check."])
def test_a_sequence_reads_one_reading_per_step_with_spans_into_the_wording(wording):
    answer = ask(wording)
    assert answer["outcome"] == "steps"
    assert len(answer["readings"]) == 2
    for reading in answer["readings"]:
        [fill] = reading["fills"]
        start, end = fill["span"]
        assert wording[start:end].lower() == fill["words"].lower()
    assert answer["paraphrase"].startswith("In this task, you are required to do these in order: first click check, then ")


def test_then_and_preposed_condition_read_one_with_their_flag():
    then, preposed = ask("Then click Check."), ask("If atlas is reviewed, click Check.")
    assert (then["outcome"], then["after_previous"], preposed["after_previous"]) == ("one", True, False)
    assert preposed["reading"]["command"]["guard"] == ["unary", "reviewed", ["const", "atlas"]]
    assert ask("Click Check.")["after_previous"] is False


def test_a_then_instruction_unit_is_refused_by_the_speech_source_route(lean):
    """The document check (finding (c), O3) is wired after the core check, by each unit's effective kind."""
    from test_speech_acts_conformance import reading_set
    from test_speech_acts_lean import U, command, unit
    from test_speech_source_lean import base_env, placed, run_source

    click = command("require", "click_required", ["check"])

    def check(line, u, sets=()):
        return run_source({"format": "ve-document@2", "environment": base_env(), "units": placed([line], [u]),
                           "reading_sets": list(sets)}, line)

    refused = "ThenWithoutStep: a Then step names no earlier instruction step as its antecedent"
    assert refused in check("Then click check.\n", unit("x", 0, "instruction", click))["error"]
    assert check("Click check.\n", unit("x", 0, "instruction", click))["status"] == "ok"
    signed = check("Then click check.\n", unit("c", 0, "asserted", {"ast": U("reviewed", "atlas")}),
                   [reading_set("c", 1, "authored", "instruction", click)])
    assert refused in signed["error"]


SEQUENCE = "Click check, then do not share the token.\n"
SEQUENCE_PARTS = "InvalidInput: a sequence of steps is one instruction unit whose parts are its steps, each with its step's command"


def _sequence(first, second, kind="instruction"):
    """The plan's document form of a sequence: one `MIXED` unit `m` whose parts `a`, `b` are its steps (split before
    `, then `), each with an explicit command, and the reading context Python sends."""
    from test_speech_acts_lean import unit
    from test_speech_source_lean import base_env
    from ve.english import EnglishVocabulary
    from ve.english_grammar import export
    from ve.environment import Environment
    env = base_env()
    cut = SEQUENCE.index(", then ")
    parts = [{**unit("a", 0, kind, first), "span": [0, cut], "status": "CHECKED"},
             {**unit("b", cut, kind, second), "span": [cut, len(SEQUENCE)], "status": "CHECKED"}]
    metadata = {"format": "ve-document@2", "environment": env,
                "units": [{"id": "m", "span": [0, len(SEQUENCE)], "status": "MIXED", "parts": parts}]}
    return metadata, {"lexicon": export(EnglishVocabulary(Environment(env), _defer_overlay_refusals=True))}


@pytest.mark.parametrize("kind", ["instruction", ["attributed", "bob", "says", "instruction"],
                                  ["hedged", "likely", "instruction"]], ids=["plain", "attributed", "hedged"])
def test_a_sequence_unit_s_parts_are_read_against_the_whole_wording(kind):
    """Review F2: a `MIXED` sequence's parts must be `readStep`'s steps of the whole wording, in order. Reversed step
    commands are refused, with or without the reading context; the steps in order are accepted with it."""
    from test_speech_acts_lean import command
    from ve.backends.speech_source import EXECUTABLE, decide_source
    from ve.errors import VEError
    if not EXECUTABLE.exists():
        pytest.skip("the Lean routes have not been built")
    click = command("require", "click_required", ["check"])
    share = command("forbid", "share_permitted", ["token1"])
    reversed_, context = _sequence(share, click, kind)
    with pytest.raises(VEError, match="^InvalidInput: command reading context$"):
        decide_source(reversed_, SEQUENCE, {})
    with pytest.raises(VEError) as caught:
        decide_source(reversed_, SEQUENCE, {}, reading_context=context)
    assert caught.value.message == SEQUENCE_PARTS + " (unit m)"
    in_order, context = _sequence(click, share, kind)
    report = decide_source(in_order, SEQUENCE, {}, reading_context=context)
    assert [u["id"] for u in report["units"]] == ["a", "b"]


def test_python_s_retry_sends_a_sequence_its_reading_context():
    """`SpeechSource` retries a source Lean refuses for its reading context, so a sequence in order loads and a
    reversed one is refused with Lean's text."""
    from test_speech_acts_lean import command
    from ve.backends.speech_source import EXECUTABLE
    from ve.errors import VEError
    from ve.speech_document import SpeechSource
    if not EXECUTABLE.exists():
        pytest.skip("the Lean routes have not been built")
    click = command("require", "click_required", ["check"])
    share = command("forbid", "share_permitted", ["token1"])
    assert SpeechSource(_sequence(click, share)[0], SEQUENCE.encode(), {}).document_id
    with pytest.raises(VEError) as caught:
        SpeechSource(_sequence(share, click)[0], SEQUENCE.encode(), {})
    assert caught.value.message == SEQUENCE_PARTS + " (unit m)"


def _relayed(wording, source="many"):
    """`english.command`'s genuine row for `wording` over the binding inventory's `many` environment (or the corpus'
    `click` case), with the request it answers."""
    from test_relay_binding_inventory import _command_sources
    from ve.backends import english_lean, relay
    from ve.english import EnglishVocabulary
    from ve.environment import Environment
    if source == "many":
        raw, _, queries = _command_sources()["many"]
    else:
        [case] = [c for c in command_cases() if c["id"] == "click"]
        raw, queries = case["environment"], case["queries"]
    env = Environment(raw)
    case = english_lean.command_request(env, wording, EnglishVocabulary(env), {}, unit="u1", queries=queries)
    return relay.decide_once(english_lean.COMMAND_MODE, case), case


@pytest.mark.parametrize("wording, source, problem", [
    ("Click Check, then do not share the token.", "click", "the steps outcome is not bound to the request"),
    ("Review the meaning, then review the meaning.", "many", "alternatives are not one reading each")])
def test_the_relay_refuses_a_sequence_it_does_not_bind_yet(wording, source, problem):
    """Until ci-3c binds them, a genuine `steps` answer and a `many` of sequences are CheckerUnavailable, never a
    Python verdict and never a crash (R8)."""
    from ve.backends import english_lean
    from ve.errors import CheckerUnavailable
    row, case = _relayed(wording, source)
    with pytest.raises(CheckerUnavailable, match=problem):
        english_lean.command_answer(row, case)


def _mutants(alternatives):
    yield [alternatives[1], alternatives[0]]                   # reordered
    yield alternatives[:1]                                     # one dropped
    yield alternatives + alternatives[:1]                      # duplicated
    yield [{**alternatives[0], "readings": []}, alternatives[1]]          # emptied
    yield [{**alternatives[0], "readings": [0, 1]}, alternatives[1]]      # a sequence over both readings
    yield [alternatives[0], {**alternatives[1], "readings": [2]}]         # an index out of range
    yield [alternatives[0], {**alternatives[1], "readings": [0]}]         # a reading named twice


def test_a_many_answer_s_alternatives_are_bound_to_its_readings():
    """The genuine `many` of single readings relays; each rebound alternative list is CheckerUnavailable."""
    import copy
    from ve.backends import english_lean
    from ve.errors import CheckerUnavailable
    row, case = _relayed("Review the meaning.")
    assert english_lean.command_answer(row, case)["alternatives"] == [
        {"shape": "core", "readings": [0]}, {"shape": "core", "readings": [1]}]
    for alternatives in _mutants(row["result"]["alternatives"]):
        bad = copy.deepcopy(row)
        bad["result"]["alternatives"] = alternatives
        with pytest.raises(CheckerUnavailable):
            english_lean.command_answer(bad, case)


def test_a_then_step_is_relayed_with_its_flag():
    from ve.backends import english_lean
    row, case = _relayed("Then click Check.", "click")
    answer = english_lean.command_answer(row, case)
    assert (answer["outcome"], answer["after_previous"]) == ("one", True)
