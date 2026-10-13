"""`ve ask` end to end (docs/spec/question-answering.md 4, 8; plan Q2.5): the CLI reads the question, generates the
route's evidence, sends the request to Lean's `ask` mode and prints Lean's lines, nothing else. Python only runs the
CLI and displays: the printed lines are the answer's `text`, recorded by `tools/ask_fixtures.py` from the same
generators, and the exit code is the lead's (0 answered, 3 unknown, 2 not read, 4 a limit, 5 unavailable).
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from subprocesses import HANG_TIMEOUT

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("ask_fixtures", ROOT / "tools/ask_fixtures.py")
AF = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(AF)

ENV_ALLOW = ("PATH", "HOME", "LANG", "LC_ALL", "TMPDIR", "PYTHONPATH", "PYTHONNOUSERSITE", "PYTHONPYCACHEPREFIX")


def cli(*args):
    env = {k: v for k, v in os.environ.items() if k in ENV_ALLOW or k.startswith("VE_")}
    return subprocess.run([sys.executable, "-m", "ve", "ask", *map(str, args)], cwd=ROOT, env=env,
                          text=True, capture_output=True,
                          timeout=int(os.environ.get("VE_ASK_CLI_TIMEOUT", HANG_TIMEOUT)))


@pytest.mark.parametrize("ident", ["G1", "G2", "G3", "G4", "G10", "U2", "U3", "U5", "U6", "U7",
                                   "A1", "A2", "A3", "A4", "A5", "A7", "A8"])
def test_ve_ask_prints_leans_lines(ident, tmp_path):
    """The printed lines are Lean's text for the recorded request: the generators are deterministic, so the CLI's
    own request gets the recorded answer."""
    entry = AF.load(ident)
    options = []
    if ident.startswith("A"):
        evidence = tmp_path / "recorded-evidence.json"
        evidence.write_text(json.dumps(entry["case"]["evidence"]))
        options = ["--evidence", evidence]
    done = cli(ROOT / entry["path"], entry["question"], *options)
    assert done.returncode == (3 if entry["result"]["lead"] == "unknown" else 0), (done.stdout, done.stderr)
    assert done.stdout.splitlines() == entry["result"]["text"]


def test_q2_f8_contentless_units_reach_both_generators():
    """All unit kinds may omit content; the case encoder preserves that absence."""
    from ve.ask import _Plain, _zero_generator, environment
    units = [{"id": "u", "kind": "exposition"}, {"id": "v", "kind": "norm"},
             {"id": "w", "kind": "asserted"}]
    plain = {"environment": environment((ROOT / AF.GROUP).read_bytes()), "units": units}
    assert _Plain(plain)._premises() == []
    norms = {"environment": environment((ROOT / (AF.AGENT + "a-unspecified.ve.md")).read_bytes()),
             "units": units}
    generated = _zero_generator(norms)
    assert generated.units == units and generated.assertions == []


def test_q2_f9_answer_accepts_separator_words_in_acts_and_reading_names(tmp_path):
    """The valid reading document from F9 completes the answer through Lean's frame gate."""
    from tests.test_readings_s2_document import _completion_document
    from ve.ask import answer
    path = _completion_document(tmp_path)[2]
    result = answer(path, path.read_bytes(),
                    "Is it the case that for every agent, for every user, that agent must help that user?")
    assert result["lines"] and any(line["frame"].startswith("R1") for line in result["lines"])


def test_ve_ask_refuses_the_recorded_unsupported_profile():
    """F3: A1d remains a refusal from the same CLI entry point."""
    entry = AF.load("A1d")
    done = cli(ROOT / entry["path"], entry["question"])
    assert done.returncode != 0
    assert entry["error"]["class"] in done.stderr


def test_the_leads_are_the_specs():
    """G1 yes with its two sentences cited; G3 a situation from the countermodel; G4 ruled out."""
    g1 = cli(ROOT / AF.load("G1")["path"], "Is every member eligible?").stdout.splitlines()
    assert g1[:2] == ["You asked whether every member is eligible.", "Yes."]
    assert [line.split(" says")[0] for line in g1[2:4]] == ["Sentence 1", "Sentence 2"]
    g3 = cli(ROOT / AF.load("G3")["path"], "Is every member verified?").stdout.splitlines()
    assert g3[1].startswith("Not necessarily") and g3[2].startswith(
        "Here is a situation the document allows where it fails: ")
    g4 = cli(ROOT / AF.load("G4")["path"], "Is it the case that no member is eligible?").stdout.splitlines()
    assert g4[1] == "No. The document rules this out."


def test_a_question_not_read_is_refused_with_leans_words():
    """G5: an indefinite question is Lean's refusal with its rephrasings (exit 2), and no answer line."""
    done = cli(ROOT / AF.load("G1")["path"], "Is a member eligible?")
    assert done.returncode == 2
    lines = done.stdout.splitlines()
    assert lines == ['VE cannot tell whether "a" here means every or some. Ask one of these instead:',
                     "Is every member eligible?", "Is some member eligible?"]


def test_the_json_is_leans_result_with_the_honesty_fields():
    entry = AF.load("G1")
    done = cli(ROOT / entry["path"], entry["question"], "--json")
    assert done.returncode == 0
    record = json.loads(done.stdout)
    assert {k: record[k] for k in ("operation", "intent", "proof", "answer")} == {
        "operation": "question.answer", "intent": "unconfirmed", "proof": "lean_checked", "answer": "lean"}
    assert record["result"] == entry["result"]
    reading = json.loads(cli(ROOT / entry["path"], entry["question"], "--reading", "--json").stdout)
    assert reading["operation"] == "question.read" and reading["answer"] == "not_asked"


@pytest.mark.parametrize("error,exit_code", [
    ("CheckerUnavailable", 5), ("ResourceLimit", 4), ("VEError", 2),
])
def test_q2_d2_json_error_never_claims_a_checked_answer(error, exit_code, tmp_path, monkeypatch, capsys):
    from ve import ask
    from ve import errors
    path = tmp_path / "document.ve.md"
    path.write_text("source")

    def fail(*_args):
        raise getattr(errors, error)("refused")

    monkeypatch.setattr(ask, "answer", fail)
    assert ask.main([str(path), "Is it so?", "--json"]) == exit_code
    record = json.loads(capsys.readouterr().out)
    assert record["error"]["class"] == error
    assert record["proof"] == "not_checked" and record["answer"] == "no_answer"
    assert "result" not in record


def test_q2_d8_more_than_64_readings_reports_leans_limit(tmp_path):
    from tests.test_document import unit, write_doc
    from tests.test_readings_nd_lean import doc1, env1
    from ve.document import _environment
    from ve.readings import s1_content_meaning_id
    raw = env1()
    env = _environment(raw)
    text = b"Every agent must help each user.\n" * 7
    units, sets = [], []
    width = len(b"Every agent must help each user.\n")
    for k in range(7):
        uid, set_id = f"u{k}", f"rs{k}"
        document, _ = doc1(raw, set_id=set_id, unit=uid, rule=f"must-help-{k}")
        reading_set = document["reading_sets"][0]
        for candidate in reading_set["readings"]:
            candidate["meaning_id"] = s1_content_meaning_id(env, set_id, candidate)
        sets.append(reading_set)
        units.append(unit(uid, k * width, (k + 1) * width, "norm", "specified"))
    path = write_doc(tmp_path, text, units, environment_json=raw, reading_sets=sets)
    done = cli(path, "Is it the case that for every agent, for every user, that agent must help that user?", "--json")
    assert done.returncode == 4, (done.stdout, done.stderr)
    record = json.loads(done.stdout)
    assert record["error"] == {"class": "ResourceLimit", "message":
                               "ResourceLimit: There are more than 64 ways to read this document's open sentences. "
                               "VE did not check them all."}
    assert record["proof"] == "not_checked" and record["answer"] == "no_answer"


VARIANTS = {"nbsp": "Is every member eligible?", "double space": "Is every  member eligible?",
            "tab": "Is every\tmember eligible?", "carriage return": "Is every member eligible?\r",
            "curly quote": "Is “every” member eligible?", "kelvin": "Is every member eligibleK?",
            "dotted I": "İs every member eligible?", "control": "Is every member\u0007 eligible?"}


@pytest.mark.parametrize("name", sorted(VARIANTS))
def test_ask_reads_the_question_as_the_reader_does(name):
    """Build checklist 3 and 10: a question with odd spacing or characters reaches the answer only through Lean's
    reader. `ve ask` refuses what `ve ask --reading` refuses, with the same words and exit code, and answers only a
    question the reader reads, opening with the reader's A0 line."""
    path = ROOT / AF.load("G1")["path"]
    question = VARIANTS[name]
    read = cli(path, question, "--reading")
    answered = cli(path, question)
    if read.returncode != 0:
        assert (answered.returncode, answered.stdout) == (read.returncode, read.stdout), name
    else:
        assert answered.returncode in (0, 3)
        assert answered.stdout.splitlines()[0] == read.stdout.splitlines()[0], name
