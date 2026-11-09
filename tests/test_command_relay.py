"""ci-2b (commands-imperatives CI-2 deliverables (4) and (5)): `read_command` relays Lean's `english.command` answer
verbatim and binds it to the request; the speech-source wrapper reads every resolved command fence again under the
payload's reading context (A2, `commandFence_needs_context`)."""
from __future__ import annotations

import copy
import json
from pathlib import Path

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
from ve.speech_document import SpeechSource, load_speech_document

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
    assert sorted(line.split(": ", 1)[0] for line in lines) == ["recheck_required", "review_required"]
    assert all(line.endswith("In this task, you are required to review the meaning.") for line in lines)


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


_ROLE_KINDS = {"instruction": "instruction", "attributed": ["attributed", "bob", "says", "instruction"],
               "hedged": ["hedged", "likely", "instruction"], "question": "question", "norm": "norm"}


def _as_mixed_part(metadata, source):
    """The fixture's one unit as the first `CHECKED` part of a `MIXED` unit `m`, an asserted line the second; the
    source with that line."""
    line = "Atlas is reviewed.\n"
    asserted = {**unit("a", 0, "asserted", {"ast": U("reviewed", "atlas")}), "span": [len(source), len(source + line)]}
    metadata["units"] = [{"id": "m", "span": [0, len(source + line)], "status": "MIXED",
                          "parts": [{**metadata["units"][0], "status": "CHECKED"}, {**asserted, "status": "CHECKED"}]}]
    return source + line


@pytest.mark.parametrize("mixed", [False, True], ids=["unit", "mixed-part"])
@pytest.mark.parametrize("kind", list(_ROLE_KINDS))
def test_a_fence_resolved_as_a_formula_in_place_of_its_role_is_refused(kind, mixed):
    """ci-2b F1 (3.2, `Wire.roleFits`): a fence whose kind wraps `instruction`, `question` or `norm`, resolved as a
    formula, would decode to no role and never be read (an instruction would vanish); Lean refuses it, plain, wrapped
    and as a `MIXED` part, with and without the reading context."""
    metadata, source, fences, _, context = _fenced()
    metadata["units"][0]["kind"] = _ROLE_KINDS[kind]
    if mixed:
        source = _as_mixed_part(metadata, source)
    for extra in ({"reading_context": context}, {}):
        with pytest.raises(VEError, match="^InvalidInput: resolved speech fences$"):
            decide_source(metadata, source, fences, resolved_fences={"x": {"ast": ["top"]}}, **extra)


@pytest.mark.parametrize("mixed", [False, True], ids=["unit", "mixed-part"])
@pytest.mark.parametrize("kind", ["instruction", "attributed", "hedged"])
def test_every_instruction_fence_is_read_as_a_command(kind, mixed):
    """The control of the refusal above: Lean's own reading of the same fence is accepted and read (the plain
    command active, a quoted one dormant), and a reading Lean does not give is refused."""
    metadata, source, fences, command, context = _fenced()
    metadata["units"][0]["kind"] = _ROLE_KINDS[kind]
    if mixed:
        source = _as_mixed_part(metadata, source)
    report = decide_source(metadata, source, fences, resolved_fences={"x": {"command": command}},
                           reading_context=context)
    assert ([c["unit"] for c in report["commands"]], report["dormant"]) == \
        ((["x"], []) if kind == "instruction" else ([], ["x"]))
    with pytest.raises(VEError, match="^InvalidInput: resolved speech fences$"):
        decide_source(metadata, source, fences, resolved_fences={"x": {"command": {**command, "force": "forbid",
                                                                          "act": "click_permitted"}}},
                      reading_context=context)


def test_an_asserted_fence_resolved_as_a_formula_is_its_assertion():
    """An asserted fence's role is a formula: `roleFits` keeps Python's resolution of it."""
    env = base_env()
    source = "Atlas is reviewed.\n"
    metadata = {"format": "ve-document@2", "environment": env,
                "units": [{**unit("a", 0, "asserted", {"fence": "a"}), "span": [0, len(source)],
                           "surface": "english"}]}
    assert decide_source(metadata, source, {"a": source}, resolved_fences={"a": {"ast": U("reviewed", "atlas")}})


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


def _document(tmp_path, lines, units, **meta):
    """A `ve-document@2` file of `lines` whose fenced units read their own line (A2's product path)."""
    from test_speech_acts_lean import F0
    env = meta.pop("environment", None) or F0()
    env["vocabulary"]["predicates"]["reviewed"]["verbalisation"] = "{0} is reviewed"
    starts = [sum(len(line) for line in lines[:i]) for i in range(len(lines) + 1)]
    placed = [{**u, "span": [starts[i], starts[i + 1]]} for i, u in enumerate(units)]
    fences = "".join(f"```ve {u['id']}\n{lines[i]}```\n" for i, u in enumerate(units)
                     if (u.get("content") or {}).get("fence"))
    path = tmp_path / "speech.ve.md"
    path.write_text("---\n" + json.dumps({"format": "ve-document@2", "environment": env, "units": placed, **meta})
                    + "\n---\n" + "".join(lines) + fences)
    return path


def _fence(uid, kind="instruction"):
    return {**unit(uid, 0, kind, {"fence": uid}), "surface": "english"}


RECORD = {"id": "q1", "premises": ["p"], "target": {"ast": U("reviewed", "atlas")}}
PROVE = "Prove that atlas is reviewed using these premises.\n"


def test_a_fenced_proof_task_reads_the_documents_records(tmp_path):
    """The wrapper's context carries the document's query records: one matching record is the proof task's fill;
    two are `QueryMismatch` (P3′); a follows question's record whose id is no `query` constant is not sent."""
    from test_speech_acts_lean import F0
    env = F0()
    env["vocabulary"]["constants"]["q2"] = {"sort": "query", "description": "q2"}
    lines, asserted = ["Atlas is reviewed.\n", PROVE], unit("p", 0, "asserted", {"ast": U("reviewed", "atlas")})
    document = load_speech_document(_document(tmp_path, lines, [asserted, _fence("f")], queries=[RECORD],
                                              environment=copy.deepcopy(env)))
    [command] = document.report["commands"]
    assert command["unit"] == "f" and command["paraphrase"].endswith("to submit a proof of q1.")
    with pytest.raises(VEError, match="^QueryMismatch: f$"):
        load_speech_document(_document(tmp_path, lines, [asserted, _fence("f")], environment=copy.deepcopy(env),
                                       queries=[RECORD, {**RECORD, "id": "q2"}]))
    lines = ["Atlas is reviewed.\n", "Does it follow from these premises that atlas is reviewed?\n", "Click check.\n"]
    follows = unit("w", 0, "question", {"question": {"mode": "follows", "query": "q9"}})
    path = _document(tmp_path, lines, [asserted, follows, _fence("c")], queries=[{**RECORD, "id": "q9"}])
    assert [c["unit"] for c in load_speech_document(path).report["commands"]] == ["c"]


def test_a_fenced_command_reads_the_effective_scope_and_its_condition(tmp_path):
    """A document's binding gives the addressee the wrapper reads with; a condition is the reading's guard."""
    from test_speech_acts_lean import F0
    env = F0()
    env["speech_acts"].pop("addressee")
    lines = ["In this task, you are alice.\n", "Click check, if atlas is reviewed.\n"]
    units = [unit("u0", 0, "binding", {"binding": {"you": "alice"}}), _fence("c")]
    document = load_speech_document(_document(tmp_path, lines, units, environment=env))
    [command] = document.report["commands"]
    assert command["paraphrase"] == "In this task, you are required to click check, where the stated condition holds."
    assert document.legend.split("\n")[1] == "In this task, you are alice."
    with pytest.raises(VEError, match="^UnboundSlot: you$"):
        load_speech_document(_document(tmp_path, lines[1:], [_fence("c")], environment=copy.deepcopy(env)))


def test_an_attributed_instruction_fence_is_a_command_fence(tmp_path):
    """`hasCommandFence` reads a kind that wraps `instruction` (S34): an attributed one is read and needs the context."""
    from ve.speech_document import _resolve_fences
    lines = ["Click check.\n"]
    path = _document(tmp_path, lines, [_fence("c", ["attributed", "bob", "says", "instruction"])])
    assert load_speech_document(path).report["dormant"] == ["c"]
    meta = json.loads(path.read_text().split("\n---\n")[0][4:])
    resolved, _ = _resolve_fences(meta, {"c": lines[0]})
    with pytest.raises(VEError, match="^InvalidInput: command reading context$"):
        decide_source(meta, lines[0], {"c": lines[0]}, resolved_fences=resolved)


@pytest.mark.parametrize("wording, status", [("Click check.", 0), ("Click Ask.", 2)])
def test_ve_speech_acts_reads_a_fenced_command(tmp_path, wording, status):
    """The plan's fixture through the CLI: a command Lean reads exits 0, one it refuses exits 2 with Lean's text."""
    import subprocess
    import sys
    from subprocesses import HANG_TIMEOUT
    path = _document(tmp_path, [wording + "\n"], [_fence("c")])
    run = subprocess.run([sys.executable, "-m", "ve", "speech-acts", str(path)], capture_output=True, text=True,
                         timeout=HANG_TIMEOUT, cwd=Path(__file__).resolve().parents[1])
    assert run.returncode == status, run.stderr
    if status:
        assert json.loads(run.stdout)["error"]["message"] == "InvalidInput: no single speech-act reading"


def _many_fences(n):
    """`n` units, each a fenced "Click check." with Lean's reading resolved, and the reading context."""
    metadata, _, _, command, context = _fenced()
    line = "Click check.\n"
    metadata["units"] = [{**_fence(f"c{i}"), "span": [i * len(line), (i + 1) * len(line)]} for i in range(n)]
    return metadata, line * n, {f"c{i}": line for i in range(n)}, {f"c{i}": {"command": command} for i in range(n)}, \
        context


def test_command_fences_are_charged_before_they_are_read():
    """The common rule: 200 command fences (a large well-formed document, under the 256 rules every document may
    hold) are each read once under one context; past `VE.Limits.maxCases` fences the wrapper refuses before reading
    any, and so before Python resolves one."""
    from ve.limits import MAX_CASES
    metadata, source, fences, resolved, context = _many_fences(200)
    assert len(decide_source(metadata, source, fences, resolved_fences=resolved,
                             reading_context=context)["commands"]) == 200
    metadata, source, fences, resolved, context = _many_fences(MAX_CASES + 1)
    for extra in ({}, {"resolved_fences": resolved, "reading_context": context}):
        with pytest.raises(ResourceLimit, match=f"^ResourceLimit: speech fences exceed {MAX_CASES}$"):
            decide_source(metadata, source, fences, **extra)
