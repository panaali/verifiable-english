"""`ve ask` on a staged-route translation directory (ve/staged_ask.py; row ask-policy-batch4).

Before: `ve ask` took only a ve-document file. A statute-corpus policy translation (a directory: translation.py, run.py,
questions-enc.jsonl) had no document, so every question about it was refused (the policy text itself: "ve-document@1
needs JSON front matter"; the directory: "Is a directory"), although its runner answers the case's questions with
Lean-checked certificates. Now a directory is asked of its own runner on the one case the question belongs to.

The fixture runner below stands for a corpus runner (no Lean): it writes the run file a corpus runner writes, with the
answers it is told to, so these tests pin what `ve ask` does with each kind of record, not the runner's proofs.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from subprocesses import HANG_TIMEOUT

ROOT = Path(__file__).resolve().parents[1]
ENV_ALLOW = ("PATH", "HOME", "LANG", "LC_ALL", "TMPDIR", "PYTHONPATH", "PYTHONNOUSERSITE", "PYTHONPYCACHEPREFIX")

CASES = [
    {"id": "C001", "scope": "in", "facts": "Ada took 20 days of PTO in 2026.",
     "questions": [{"qid": "C001-1", "text": "How many days off a year does the policy expect Ada to take at least?"},
                   {"qid": "C001-2", "text": "Has Ada taken the minimum time off the policy expects for 2026?"},
                   {"qid": "C001-3", "text": "Does the policy describe its minimum as merely a guide for Ada?"},
                   {"qid": "C001-4", "text": "What is the latest day Ada may log her leave?"},
                   {"qid": "C001-5", "text": "Is Ada paid for her sixth day off sick?"},
                   {"qid": "C001-6", "text": "May Ada book it?"},
                   {"qid": "C001-7", "text": "May Ada claim rights to the copies?"}]},
    {"id": "C002", "scope": "in", "facts": "Ben took 26 days.",
     "questions": [{"qid": "C002-1", "text": "Has Ben taken the minimum time off the policy expects for 2026?"},
                   {"qid": "C002-2", "text": "May Ada book it?"}]},
    {"id": "C003", "scope": "out", "facts": "A contractor.",
     "questions": [{"qid": "C003-1", "text": "Is the contractor covered?"}]},
]
ANSWERS = {
    "C001": {"C001-1": {"answer": "25 days", "value": "25"}, "C001-2": {"answer": "no"},
             "C001-3": {"answer": "OPEN", "why": "no form of the translation carries this question"},
             "C001-4": {"answer": "DATE", "value": "2027-01-04"},
             "C001-5": {"answer": "OPEN", "lean_rejected": True},
             "C001-6": {"answer": "OPEN"},
             "C001-7": {"answer": "OPEN", "refused": "unit 11 is not written: the translation has no wording for it"}},
    "C002": {"C002-1": {"answer": "yes"}, "C002-2": {"answer": "yes"}},
    "C003": {"C003-1": {"answer": "UNSUPPORTED"}},
}
RUNNER = '''
import json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import translation  # the runner imports its directory's modules by their bare names, as the corpus runners do

def _square(n):
    return n * n


def main(argv=None):
    args = list(argv)
    case = args[args.index("--cases") + 1]
    out = args[args.index("--out") + 1]
    (HERE / "calls.jsonl").open("a").write(json.dumps(args) + "\\n")
    if case in translation.UNAVAILABLE:
        from ve.errors import CheckerUnavailable
        raise CheckerUnavailable("CheckerUnavailable: the Lean service did not start")
    print("the runner's own summary line, not shown")
    if translation.POOL:  # the corpus runners ground a case's sub-cases in a process pool
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(max_workers=2) as pool:
            assert list(pool.map(_square, [2, 3])) == [4, 9]
    answers = json.loads((HERE / "answers.json").read_text())
    mine = answers[case]
    refused = {q: a for q, a in mine.items() if a.get("refused")}
    rec = {"id": case, "answers": {q: a for q, a in mine.items() if q not in refused},
           "lean": {"certificates": 3, "certificates_accepted": 3}}
    records = [rec] + ([{"id": case, "scope": "in", "encoder_refused": True, "answers": refused}] if refused else [])
    if case in translation.TWICE:
        records.append(rec)
    Path(out).write_text(json.dumps({"records": records}))
    return {}
'''


def staged(tmp_path: Path, *, unavailable=(), answers=ANSWERS, name="policy", pool=False, twice=()) -> Path:
    d = tmp_path / name
    d.mkdir()
    (d / "translation.py").write_text(
        f"UNAVAILABLE = {list(unavailable)!r}\nPOOL = {pool!r}\nTWICE = {list(twice)!r}\n")
    (d / "run.py").write_text(RUNNER)
    (d / "questions-enc.jsonl").write_text("".join(json.dumps(c) + "\n" for c in CASES))
    (d / "answers.json").write_text(json.dumps(answers))
    return d


def calls(d: Path) -> list[list[str]]:
    path = d / "calls.jsonl"
    return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []


def ask(*args):
    from ve.__main__ import main
    return main(["ask", *map(str, args)])


def cli(*args):
    env = {k: v for k, v in os.environ.items() if k in ENV_ALLOW or k.startswith("VE_")}
    return subprocess.run([sys.executable, "-m", "ve", "ask", *map(str, args)], cwd=ROOT, env=env, text=True,
                          capture_output=True, timeout=HANG_TIMEOUT)


def test_a_staged_directory_answers_the_cases_question_from_its_runner(tmp_path):
    """Fails on the old code: a directory was opened as a document file ("Is a directory", exit 2)."""
    d = staged(tmp_path)
    done = cli(d, "Has Ada taken the minimum time off the policy expects for 2026?", "--case", "C001")
    assert (done.returncode, done.stdout, done.stderr) == (0, "no\n", "")
    assert calls(d)[0][:2] == ["--cases", "C001"] and calls(d)[0][2] == "--out" and len(calls(d)) == 1


def test_an_amount_and_a_typed_value_print_the_runners_answer(tmp_path, capsys):
    d = staged(tmp_path)
    assert ask(d, "How many days off a year does the policy expect Ada to take at least?") == 0
    assert ask(d, "What is the latest day Ada may log her leave?", "--case", "C001") == 0
    assert capsys.readouterr().out.splitlines() == ["25 days", "2027-01-04"]


def test_the_question_is_found_by_its_text_and_needs_case_only_when_several_cases_ask_it(tmp_path, capsys):
    d = staged(tmp_path)
    assert ask(d, "  Has Ben taken the minimum time off the policy expects for 2026?  ") == 0
    assert capsys.readouterr().out == "yes\n"
    assert ask(d, "May Ada book it?") == 2
    err = capsys.readouterr().err
    assert "more than one case (C001, C002)" in err and "--case" in err
    assert ask(d, "May Ada book it?", "--case", "C002") == 0
    assert capsys.readouterr().out == "yes\n"
    assert [c[1] for c in calls(d)] == ["C002", "C002"]


@pytest.mark.parametrize("question, why", [
    ("Does the policy describe its minimum as merely a guide for Ada?",
     "OPEN: no form of the translation carries this question"),
    ("Is Ada paid for her sixth day off sick?", "OPEN: Lean did not admit every document the staged answer rests on"),
    ("May Ada book it?", "OPEN: the translation's rules establish no answer for this case"),
    ("May Ada claim rights to the copies?", "OPEN: unit 11 is not written: the translation has no wording for it"),
])
def test_no_answer_refuses_at_once_with_the_run_files_reason(tmp_path, capsys, question, why):
    d = staged(tmp_path)
    assert ask(d, question, "--case", "C001") == 3
    out = capsys.readouterr()
    assert (out.out, out.err) == ("", why + "\n")


def test_a_case_with_a_second_record_answers_from_the_record_that_holds_the_question(tmp_path, capsys):
    """The copilot runner writes a case's encoder refusals as a second record of the same case id (failed: "wrote 2
    records"); a question held by two records is a malformed run file (exit 5)."""
    d = staged(tmp_path)
    assert ask(d, "Has Ada taken the minimum time off the policy expects for 2026?", "--case", "C001") == 0
    assert capsys.readouterr().out == "no\n"
    assert ask(staged(tmp_path, twice=["C002"], name="twice"), "May Ada book it?", "--case", "C002") == 5
    assert "2 records hold C002-2" in capsys.readouterr().err


def test_an_out_of_scope_case_is_unsupported(tmp_path, capsys):
    assert ask(staged(tmp_path), "Is the contractor covered?") == 3
    assert capsys.readouterr().err.startswith("UNSUPPORTED: the case is outside the translation's scope")


@pytest.mark.parametrize("args, said", [
    (["Is this a question no case asks?"], "is not one of the questions of any case"),
    (["Has Ben taken the minimum time off the policy expects for 2026?", "--case", "C001"],
     "is not one of the questions of case C001"),
    (["May Ada book it?", "--case", "C009"], "has no case 'C009' (its cases: C001, C002, C003)"),
    (["May Ada book it?", "--case", "C001", "--reading"], "a staged-route translation has none"),
])
def test_a_question_the_directory_does_not_hold_is_not_read_and_the_runner_does_not_run(tmp_path, capsys, args, said):
    d = staged(tmp_path)
    assert ask(d, *args) == 2
    assert said in capsys.readouterr().err
    assert calls(d) == []


def test_a_directory_that_is_no_staged_translation_names_what_it_lacks(tmp_path, capsys):
    """Fails on the old code: "[Errno 21] Is a directory"."""
    (tmp_path / "plain").mkdir()
    (tmp_path / "plain" / "run.py").write_text("")
    assert ask(tmp_path / "plain", "Is it?") == 2
    err = capsys.readouterr().err
    assert "not a staged-route translation: it has no translation.py, questions-enc.jsonl" in err
    assert "a ve-document is asked as a file" in err


def test_json_carries_the_honesty_fields_and_the_record(tmp_path, capsys):
    d = staged(tmp_path)
    q = "How many days off a year does the policy expect Ada to take at least?"
    assert ask("--json", "--case", "C001", d, q) == 0
    got = json.loads(capsys.readouterr().out)
    assert got == {"operation": "question.answer", "route": "staged", "question": "encoded", "answer": "staged_route",
                   "proof": "lean_checked", "intent": "unconfirmed", "case": "C001", "qid": "C001-1",
                   "record": {"answer": {"answer": "25 days", "value": "25"},
                              "lean": {"certificates": 3, "certificates_accepted": 3}},
                   "text": "25 days"}
    assert ask("--json", d, "May Ada book it?", "--case", "C001") == 3
    got = json.loads(capsys.readouterr().out)
    assert got["proof"] == "not_checked" and got["text"].startswith("OPEN:")


def test_checker_unavailable_in_the_runner_is_exit_5(tmp_path, capsys):
    assert ask(staged(tmp_path, unavailable=["C001"]), "May Ada book it?", "--case", "C001") == 5
    assert "the Lean service did not start" in capsys.readouterr().err


def test_two_directories_in_one_process_each_run_their_own_runner(tmp_path, capsys):
    """The runner's bare-name modules (`translation`) are dropped after each run, so the second directory's are read."""
    first = staged(tmp_path, name="first")
    other = {**ANSWERS, "C002": {"C002-1": {"answer": "no"}, "C002-2": {"answer": "no"}}}
    second = staged(tmp_path, answers=other, name="second", unavailable=["C001"])
    q = "Has Ben taken the minimum time off the policy expects for 2026?"
    assert (ask(first, q), ask(second, q)) == (0, 0)
    assert capsys.readouterr().out.splitlines() == ["yes", "no"]
    assert ask(second, "May Ada book it?", "--case", "C001") == 5
    assert "translation" not in sys.modules


def test_a_runner_that_uses_a_process_pool_answers(tmp_path):
    """The gitlab-expenses and copilot runners map a case's sub-cases over a process pool: its workers import the
    runner's functions by the runner's own module name from its directory (failed with a synthetic module name)."""
    done = cli(staged(tmp_path, pool=True), "May Ada book it?", "--case", "C002")
    assert (done.returncode, done.stdout) == (0, "yes\n"), done.stderr


def test_a_module_named_like_the_runner_is_put_back(tmp_path, capsys, monkeypatch):
    import types
    mine = types.ModuleType("run")
    monkeypatch.setitem(sys.modules, "run", mine)
    assert ask(staged(tmp_path), "May Ada book it?", "--case", "C002") == 0
    assert sys.modules["run"] is mine


def test_a_document_file_keeps_leans_route(tmp_path):
    """A file is still a ve-document asked of Lean: the policy text itself is refused as before."""
    text = tmp_path / "policy.md"
    text.write_text("We offer our team unlimited time off.\n")
    done = cli(text, "Is it?")
    assert done.returncode == 2 and "ve-document@1 needs JSON front matter" in done.stderr
