"""ci-2b (commands-imperatives CI-2 deliverables (4) and (5)): `read_command` relays Lean's `english.command` answer
verbatim and binds it to the request; the speech-source wrapper reads every resolved command fence again under the
payload's reading context (A2, `commandFence_needs_context`)."""
from __future__ import annotations

import copy

import pytest

from lean_service_corpus import command_cases
from test_speech_acts_lean import U, unit
from test_speech_source_lean import base_env
from ve.backends import english_lean, relay
from ve.backends.speech_source import EXECUTABLE, decide_source
from ve.english import EnglishVocabulary
from ve.english_grammar import export
from ve.environment import Environment
from ve.errors import AmbiguousDerivation, CheckerUnavailable, ResourceLimit, VEError
from ve.speech_document import SpeechSource

pytestmark = pytest.mark.skipif(not EXECUTABLE.exists(), reason="the Lean routes have not been built")


def _read(case, **change):
    env = Environment(case["environment"])
    return english_lean.read_command(env, change.get("wording", case["wording"]), EnglishVocabulary(env), {},
                                     unit=case["unit"], queries=change.get("queries", case["queries"]))


def test_read_command_relays_lean_verbatim():
    cases = {case["id"]: case for case in command_cases()}
    one = _read(cases["click"])
    assert one["reading"]["command"] == {"force": "require", "act": "click_required", "args": ["check"],
                                         "guard": ["top"]}
    assert one["reading"]["fills"] == [{"constant": "check", "words": "check", "span": [6, 11]}]
    assert _read(cases["prove"])["reading"]["query"] == "q1"
    for name, cls, message in (("mismatch", VEError, "QueryMismatch: u1"),
                               ("may", VEError, "PermissionNotCommand: use an equality-guarded W1 rule"),
                               ("long", ResourceLimit, "VE stopped reading this command at its work limit.")):
        with pytest.raises(cls) as caught:
            _read(cases[name])
        assert caught.value.message == message, name


def test_many_is_raised_with_leans_paraphrases():
    from test_relay_binding_inventory import _command_sources
    raw, wording, queries = _command_sources()["many"]
    with pytest.raises(AmbiguousDerivation) as caught:
        _read({"environment": raw, "wording": wording, "queries": queries, "unit": "u1"})
    lines = caught.value.message.split("\n")
    assert len(lines) == 2 and all(line.startswith("In this task, you are required to review") for line in lines)


@pytest.mark.parametrize("fill", [{"constant": "ghost"}, {"constant": "alice"}, {"constant": "q1", "words": "q1"},
                                  {"words": "the token"}, {"span": [5, 11]}, {"span": None}])
def test_a_fill_the_request_does_not_hold_is_unavailable(monkeypatch, fill):
    """R8: a fill naming a constant the request does not hold, one of another sort, words not at its span, or no span
    without a query record, is `CheckerUnavailable`."""
    case = {c["id"]: c for c in command_cases()}["click"]
    genuine = relay.decide_once("english.command", english_lean.command_request(
        Environment(case["environment"]), case["wording"], EnglishVocabulary(Environment(case["environment"])), {},
        unit=case["unit"], queries=case["queries"]))
    forged = copy.deepcopy(genuine)
    forged["result"]["reading"]["fills"][0].update(fill)
    forged["result"]["reading"]["command"]["args"] = [forged["result"]["reading"]["fills"][0]["constant"]]
    monkeypatch.setattr(relay, "decide_once", lambda mode, request: copy.deepcopy(forged))
    with pytest.raises(CheckerUnavailable):
        _read(case)


def _fenced(wording="Click check."):
    """A W2 source whose one unit is an instruction fence (A2)."""
    env = base_env()
    source = wording + "\n"
    metadata = {"format": "ve-document@2", "environment": env,
                "units": [{**unit("x", 0, "instruction", {"fence": "x"}), "span": [0, len(source)],
                           "surface": "english"}]}
    command = {"force": "require", "act": "click_required", "args": ["check"], "guard": ["top"]}
    context = {"lexicon": export(EnglishVocabulary(Environment(env), _defer_overlay_refusals=True))}
    return metadata, source, {"x": source}, command, context


def test_a_command_fence_needs_the_reading_context():
    """`commandFence_needs_context`'s fixture: a resolved command fence with no reading context is refused."""
    metadata, source, fences, command, context = _fenced()
    with pytest.raises(VEError, match="^InvalidInput: command reading context$"):
        decide_source(metadata, source, fences, resolved_fences={"x": {"command": command}})
    report = decide_source(metadata, source, fences, resolved_fences={"x": {"command": command}},
                           reading_context=context)
    assert [c["unit"] for c in report["commands"]] == ["x"]


@pytest.mark.parametrize("change", [{"force": "forbid", "act": "click_permitted"}, {"guard": U("reviewed", "atlas")},
                                    {"args": ["panel"]}])
def test_a_resolved_command_lean_does_not_read_is_refused(change):
    metadata, source, fences, command, context = _fenced()
    if change.get("args") == ["panel"]:
        metadata["environment"]["vocabulary"]["constants"]["panel"] = {"sort": "control", "description": "panel"}
        context = {"lexicon": export(EnglishVocabulary(Environment(metadata["environment"]),
                                                       _defer_overlay_refusals=True))}
    with pytest.raises(VEError, match="^InvalidInput: resolved speech fences$"):
        decide_source(metadata, source, fences, resolved_fences={"x": {"command": {**command, **change}}},
                      reading_context=context)


def test_a_question_fence_needs_no_reading_context():
    env = base_env()
    source = "Is atlas reviewed?\n"
    metadata = {"format": "ve-document@2", "environment": env,
                "units": [{**unit("q", 0, "question", {"fence": "q"}), "span": [0, len(source)],
                           "surface": "english"}]}
    question = {"question": {"mode": "polar", "body": U("reviewed", "atlas")}}
    assert decide_source(metadata, source, {"q": source}, resolved_fences={"q": question})["questions"]


def test_a_document_reads_its_command_fence_through_lean():
    metadata, source, fences, command, _ = _fenced()
    document = SpeechSource(metadata, source.encode(), fences)
    assert [(c["unit"], c["force"]) for c in document.report["commands"]] == [("x", "require")]
    assert document.legend.split("\n")[:2] == ["This document is task t1.", "In this task, you are alice."]
    metadata, source, fences, _, _ = _fenced("Click Ask.")
    with pytest.raises(VEError, match="^InvalidInput: no single speech-act reading$"):
        SpeechSource(metadata, source.encode(), fences)
