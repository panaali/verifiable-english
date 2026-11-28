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
# The Lean counts a corpus runner records for a case whose steps Lean all accepted (`skipped` false: Lean ran).
CHECKED = {"certificates": 3, "certificates_accepted": 3, "documents": 2, "documents_admitted": 2, "skipped": False}
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
    sys.setrecursionlimit(54321)  # as the gitlab and copilot runners do at import
    if case in translation.UNAVAILABLE:
        from ve.errors import CheckerUnavailable
        raise CheckerUnavailable("CheckerUnavailable: the Lean service did not start")
    if case in translation.RAISE:
        if translation.RAISE[case] == "SystemExit":
            raise SystemExit(2)
        assert False, "a runner assertion"
    print("the runner's own summary line, not shown")
    if translation.POOL:  # the corpus runners ground a case's sub-cases in a process pool
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(max_workers=2) as pool:
            assert list(pool.map(_square, [2, 3])) == [4, 9]
    answers = json.loads((HERE / "answers.json").read_text())
    mine = answers[case]
    refused = {q: a for q, a in mine.items() if a.get("refused")}
    rec = {"id": case, "answers": {q: a for q, a in mine.items() if q not in refused and q not in translation.DROP},
           "lean": translation.LEAN.get(case, translation.CHECKED),
           "steps": [{"target": "pdur.f", "certified": 2, "inconsistent": True}] if case in translation.INCONSISTENT
           else [{"target": "x", "certified": 1}]}
    rec["answers"].update(translation.RAW.get(case, {}))  # answers that are not objects (a malformed run file)
    if rec["lean"] is None:  # a run file whose record carries no Lean counts
        del rec["lean"]
    if all(a["answer"] == "UNSUPPORTED" for a in mine.values()):
        rec |= {"scope": "out", "unsupported": "a contractor is not a team member (D11)"}
    records = [rec] + ([{"id": case, "scope": "in", "encoder_refused": True, "answers": refused}] if refused else [])
    if case in translation.TWICE:
        records.append(rec)
    Path(out).write_text(json.dumps({"records": records}))
    return {}
'''


def staged(tmp_path: Path, *, unavailable=(), answers=ANSWERS, name="policy", pool=False, twice=(), raises=None,
           drop=(), inconsistent=(), lean=None, raw=None) -> Path:
    d = tmp_path / name
    d.mkdir()
    (d / "translation.py").write_text(
        f"UNAVAILABLE = {list(unavailable)!r}\nPOOL = {pool!r}\nTWICE = {list(twice)!r}\nRAISE = {raises or {}!r}\n"
        f"DROP = {list(drop)!r}\nINCONSISTENT = {list(inconsistent)!r}\nCHECKED = {CHECKED!r}\n"
        f"LEAN = {lean or {}!r}\nRAW = {raw or {}!r}\n")
    (d / "run.py").write_text(RUNNER)
    (d / "questions-enc.jsonl").write_text("".join(json.dumps(c) + "\n" for c in CASES))
    (d / "answers.json").write_text(json.dumps(answers))
    return d


def answered(out: str) -> str:
    """The printed answers without the provenance block that follows each (ve/provenance.py; row
    answer-provenance-block, tested in tests/test_answer_provenance.py): every answer is followed by exactly one."""
    from ve.provenance import ROLES
    lines, kept = out.splitlines(keepends=True), []
    while lines:
        line = lines.pop(0)
        kept.append(line)
        assert line != "Provenance of this answer:\n", out  # a block with no answer before it
        if lines and lines[0] == "Provenance of this answer:\n":
            block = lines[:1]
            del lines[0]
            while lines and lines[0].startswith("  "):
                block.append(lines.pop(0))
            assert block[-1].startswith(f"  {ROLES[-1][1]}: "), block
    return "".join(kept)


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
    assert (done.returncode, answered(done.stdout), done.stderr) == (0, "no\n", "")
    assert calls(d)[0][:2] == ["--cases", "C001"] and calls(d)[0][2] == "--out" and len(calls(d)) == 1


def test_an_amount_and_a_typed_value_print_the_runners_answer(tmp_path, capsys):
    d = staged(tmp_path)
    assert ask(d, "How many days off a year does the policy expect Ada to take at least?") == 0
    assert ask(d, "What is the latest day Ada may log her leave?", "--case", "C001") == 0
    assert answered(capsys.readouterr().out).splitlines() == ["25 days", "2027-01-04"]


def test_the_question_is_found_by_its_text_and_needs_case_only_when_several_cases_ask_it(tmp_path, capsys):
    d = staged(tmp_path)
    assert ask(d, "  Has Ben taken the minimum time off the policy expects for 2026?  ") == 0
    assert answered(capsys.readouterr().out) == "yes\n"
    assert ask(d, "May Ada book it?") == 2
    err = capsys.readouterr().err
    assert "more than one case (C001, C002)" in err and "--case" in err
    assert ask(d, "May Ada book it?", "--case", "C002") == 0
    assert answered(capsys.readouterr().out) == "yes\n"
    assert [c[1] for c in calls(d)] == ["C002", "C002"]


@pytest.mark.parametrize("question, why", [
    ("Does the policy describe its minimum as merely a guide for Ada?",
     "OPEN: no form of the translation carries this question"),
    ("Is Ada paid for her sixth day off sick?", "OPEN: Lean did not admit every document the staged answer rests on"),
    ("May Ada book it?", "OPEN: the runner established no answer for this question and recorded no reason"),
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
    assert answered(capsys.readouterr().out) == "no\n"
    assert ask(staged(tmp_path, twice=["C002"], name="twice"), "May Ada book it?", "--case", "C002") == 5
    assert "2 records hold C002-2" in capsys.readouterr().err


def test_an_out_of_scope_case_is_unsupported_with_the_records_reason(tmp_path, capsys):
    assert ask(staged(tmp_path), "Is the contractor covered?") == 3
    assert capsys.readouterr().err == ("UNSUPPORTED: the case is outside the translation's scope: a contractor is not "
                                       "a team member (D11)\n")


def test_an_open_answer_names_the_steps_the_case_log_marks_inconsistent(tmp_path, capsys):
    assert ask(staged(tmp_path, inconsistent=["C001"]), "May Ada book it?", "--case", "C001") == 3
    assert capsys.readouterr().err == ("OPEN: the runner established no answer for this question and recorded no "
                                       "reason (the case's step log marks 1 step(s) inconsistent: pdur.f)\n")


@pytest.mark.parametrize("kind", ["assert", "SystemExit"])
def test_a_runner_that_fails_is_checker_unavailable_never_exit_1(tmp_path, capsys, kind):
    """Review A1: a runner's own failure (an assert, its argparse exiting) was a traceback with exit 1 ("violated")."""
    d = staged(tmp_path, raises={"C002": kind})
    assert ask(d, "May Ada book it?", "--case", "C002") == 5
    err = capsys.readouterr().err
    assert err.startswith("CheckerUnavailable: the runner ") and "failed on case 'C002'" in err
    assert ("AssertionError: a runner assertion" if kind == "assert" else "SystemExit: 2") in err


def test_a_question_the_runner_does_not_carry_is_open_with_that_reason(tmp_path, capsys):
    """Review B3: a qid of questions-enc.jsonl that no record holds was exit 5 ("0 records hold")."""
    assert ask(staged(tmp_path, drop=["C002-2"]), "May Ada book it?", "--case", "C002") == 3
    assert capsys.readouterr().err == ("OPEN: the runner's case table does not carry C002-2 (no record of case C002 "
                                       "holds it)\n")


def test_a_typed_answer_without_its_value_is_malformed_not_an_answer(tmp_path, capsys):
    bad = {**ANSWERS, "C002": {"C002-1": {"answer": "DATE"}, "C002-2": {"answer": None}}}
    d = staged(tmp_path, answers=bad)
    assert ask(d, "Has Ben taken the minimum time off the policy expects for 2026?") == 5
    assert ask(d, "May Ada book it?", "--case", "C002") == 5
    first, second = capsys.readouterr().err.splitlines()
    assert first.startswith("CheckerUnavailable: the runner's answer for C002-1 is malformed")
    assert second.startswith("CheckerUnavailable: the runner's answer for C002-2 is malformed")


@pytest.mark.parametrize("line, said", [
    ("{not json", "questions-enc.jsonl:4 is not JSON"),
    ('{"id": "C004", "questions": [{"qid": "C004-1"}]}', "questions-enc.jsonl:4 is not a case"),
])
def test_a_malformed_questions_file_is_not_read(tmp_path, capsys, line, said):
    d = staged(tmp_path)
    with (d / "questions-enc.jsonl").open("a") as f:
        f.write(line + "\n")
    assert ask(d, "May Ada book it?", "--case", "C002") == 2
    assert said in capsys.readouterr().err
    assert calls(d) == []


def test_a_question_asked_twice_in_one_case_is_not_read(tmp_path, capsys):
    """Review B1: the first of two same-text questions of one case was answered silently."""
    d = staged(tmp_path)
    table = [{**c, "questions": c["questions"] + [{"qid": "C002-3", "text": "May Ada book it?"}]} if c["id"] == "C002"
             else c for c in CASES]
    (d / "questions-enc.jsonl").write_text("".join(json.dumps(c) + "\n" for c in table))
    assert ask(d, "May Ada book it?", "--case", "C002") == 2
    assert "case C002 asks this question more than once (C002-2, C002-3)" in capsys.readouterr().err


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
    assert set(got.pop("provenance")) >= {"source", "translation", "ve_commit", "checker", "date"}
    assert got == {"operation": "question.answer", "route": "staged", "question": "encoded", "answer": "staged_route",
                   "proof": "lean_checked", "intent": "unconfirmed", "case": "C001", "qid": "C001-1",
                   "record": {"answer": {"answer": "25 days", "value": "25"},
                              "lean": CHECKED},
                   "text": "25 days"}
    assert ask("--json", d, "May Ada book it?", "--case", "C001") == 3
    got = json.loads(capsys.readouterr().out)
    assert got["proof"] == "not_checked" and got["answer"] == "no_answer" and got["text"].startswith("OPEN:")


# Row lean-checked-refuse (orchestrator ruling 2026-11-27 192403Z item 1): the label "lean_checked" rested on "the
# runner's rule" and was set for any answer the runner did not mark OPEN or UNSUPPORTED; the record's Lean counts were
# passed through and never read, and a run made with the runner's --no-lean (no step sent to Lean) answered with the
# label. Each test below but the last fails on the old code (exit 0, the answer printed, proof "lean_checked").
Q_ADA = "How many days off a year does the policy expect Ada to take at least?"


def _refused(capsys, d, *, said):
    assert ask(d, Q_ADA, "--case", "C001") == 3
    out = capsys.readouterr()
    assert out.out == "" and "25" not in out.err and out.err.startswith("not checked: ") and said in out.err, out
    assert ask("--json", d, Q_ADA, "--case", "C001") == 3
    got = json.loads(capsys.readouterr().out)
    assert got["proof"] == "not_checked" and got["answer"] == "no_answer" and got["text"].startswith("not checked: ")
    assert "25" not in json.dumps(got), got  # no answer anywhere in the output, its value included
    return got


def test_a_rejected_certificate_refuses_the_answer_and_shows_the_counts(tmp_path, capsys):
    """(a) Lean rejected one of the case's three step certificates: no answer, "not checked" with the counts."""
    lean = {**CHECKED, "certificates_accepted": 2}
    got = _refused(capsys, staged(tmp_path, lean={"C001": lean}),
                   said="Lean accepted 2 of 3 step certificates and admitted 2 of 2 documents of case C001")
    assert got["record"] == {"lean": lean}


def test_an_unadmitted_document_refuses_the_answer(tmp_path, capsys):
    _refused(capsys, staged(tmp_path, lean={"C001": {**CHECKED, "documents_admitted": 1}}),
             said="admitted 1 of 2 documents")


@pytest.mark.parametrize("lean", [
    {"certificates": 0, "certificates_accepted": 0, "documents": 0, "documents_admitted": 0, "skipped": True},
    {**CHECKED, "skipped": True},  # even with counts that look accepted: the run says it skipped Lean
], ids=["as-the-runners-write-it", "with-full-counts"])
def test_a_run_made_without_lean_never_carries_the_label(tmp_path, capsys, lean):
    """(b) The corpus runners' --no-lean path records `skipped` true (they wrote the answers, unchecked, with 0 counts)."""
    _refused(capsys, staged(tmp_path, lean={"C001": lean}), said="the run skipped Lean")


@pytest.mark.parametrize("lean, said", [
    (None, "the run file records no Lean counts for case C001"),
    ({k: v for k, v in CHECKED.items() if k != "skipped"}, "does not record that Lean ran"),  # a record from before
    ({"certificates": 3, "certificates_accepted": 3}, "does not record that Lean ran"),
    ({k: v for k, v in CHECKED.items() if k != "documents_admitted"}, "Lean counts are incomplete"),
    ({**CHECKED, "certificates": 0, "certificates_accepted": 0}, "accepted 0 of 0 step certificates"),
    ({**CHECKED, "certificates_accepted": True, "certificates": 1}, "Lean counts are incomplete"),
    ({**CHECKED, "skipped": "no"}, "does not record that Lean ran"),
], ids=["no-counts", "no-skipped-field", "no-skipped-field-or-documents", "a-count-missing", "no-certificate", "a-bool-count", "skipped-not-a-bool"])
def test_a_record_without_complete_counts_is_refused(tmp_path, capsys, lean, said):
    """(c) Fail closed: a record that does not show Lean checked the case is refused."""
    _refused(capsys, staged(tmp_path, lean={"C001": lean}), said=said)


def test_a_rejected_step_in_one_case_leaves_another_cases_answers(tmp_path, capsys):
    d = staged(tmp_path, lean={"C001": {**CHECKED, "certificates_accepted": 0}})
    assert ask(d, "May Ada book it?", "--case", "C002") == 0
    assert answered(capsys.readouterr().out) == "yes\n"


def test_an_answer_that_is_not_an_object_is_malformed_and_not_shown(tmp_path, capsys):
    """Review B2: a non-object answer was OPEN with its raw value in the --json record, whatever the counts."""
    d = staged(tmp_path, raw={"C002": {"C002-2": "yes"}}, lean={"C002": {**CHECKED, "certificates_accepted": 0}})
    assert ask("--json", d, "May Ada book it?", "--case", "C002") == 5
    got = json.loads(capsys.readouterr().out)
    assert got["proof"] == "not_checked" and "yes" not in json.dumps(got) and "not an object" in got["text"], got


def test_an_open_answer_keeps_its_reason_whatever_the_counts(tmp_path, capsys):
    d = staged(tmp_path, lean={"C001": None})
    assert ask(d, "Is Ada paid for her sixth day off sick?", "--case", "C001") == 3
    assert capsys.readouterr().err == "OPEN: Lean did not admit every document the staged answer rests on\n"


def test_an_all_accepted_record_is_lean_checked_as_before(tmp_path, capsys):
    """(d) Every certificate accepted, every document admitted, Lean ran: the answer and the label, as before."""
    d = staged(tmp_path)
    assert ask(d, Q_ADA, "--case", "C001") == 0
    assert answered(capsys.readouterr().out) == "25 days\n"
    assert ask("--json", d, Q_ADA, "--case", "C001") == 0
    got = json.loads(capsys.readouterr().out)
    assert (got["proof"], got["text"], got["record"]["lean"]) == ("lean_checked", "25 days", CHECKED)


@pytest.mark.parametrize("use_case", ["gitlab_expenses", "ftr_per_diem", "uc_award"])
def test_the_corpus_runners_record_whether_they_skipped_lean(use_case):
    """Every corpus runner with a --no-lean path records `lean.skipped` (a record without it is refused), read from
    the source so the test needs no Lean: the field is set from the flag, next to the counts."""
    source = (ROOT / "usecases" / use_case / ("run" + ".py")).read_text(encoding="utf-8")
    assert 'add_argument("--no-lean"' in source
    assert '"skipped": bool(args.no_lean)}' in source


@pytest.mark.parametrize("use_case, case", [("gitlab_expenses", "G001"), ("ftr_per_diem", "T001"), ("uc_award", "U001")])
def test_a_real_no_lean_run_is_refused_and_its_lean_run_is_checked(tmp_path, use_case, case):
    """The real runners: their --no-lean run writes answers (not OPEN) with `skipped` true, which `checked` refuses;
    their Lean run (the one `ve ask` makes) records `skipped` false and counts that pass."""
    from ve.staged_ask import checked
    env = {k: v for k, v in os.environ.items() if k in ENV_ALLOW or k.startswith("VE_")}
    runs = {}
    for flag in ("--no-lean", None):
        out = tmp_path / f"{flag or 'lean'}.json"
        done = subprocess.run([sys.executable, "-B", f"usecases/{use_case}/run.py", "--cases", case, "--out", str(out),
                               *([flag] if flag else [])], cwd=ROOT, env=env, text=True, capture_output=True,
                              timeout=HANG_TIMEOUT)
        assert done.returncode == 0, done.stderr[-2000:]
        runs[flag] = [r for r in json.loads(out.read_text())["records"] if r.get("id") == case]
    skipped = runs["--no-lean"]
    assert skipped and all(r["lean"]["skipped"] is True and checked(r).startswith("not checked: the run skipped Lean")
                           for r in skipped)
    assert any(a.get("answer") not in ("OPEN", "UNSUPPORTED") for r in skipped for a in r["answers"].values())
    assert all(r["lean"]["skipped"] is False and checked(r) is None for r in runs[None]), [r["lean"] for r in runs[None]]
    # Review B3: and `ve ask` on the real directory prints that run's answer with the label (uc_award's amounts are
    # written under "gbp", which the route reads as malformed, so its non-amount answers are asked).
    texts = {q["qid"]: q["text"] for line in (ROOT / "usecases" / use_case / "questions-enc.jsonl").read_text().splitlines()
             if line.strip() for c in [json.loads(line)] if c["id"] == case for q in c["questions"]}
    qid, want = next((q, a) for r in runs[None] for q, a in r["answers"].items()
                     if a.get("answer") not in ("OPEN", "UNSUPPORTED", "AMOUNT") and q in texts)
    done = cli(ROOT / "usecases" / use_case, texts[qid], "--case", case, "--json")
    got = json.loads(done.stdout)
    assert (done.returncode, got["proof"], got["record"]["answer"]) == (0, "lean_checked", want), done.stderr[-2000:]


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
    assert answered(capsys.readouterr().out).splitlines() == ["yes", "no"]
    path, limit = list(sys.path), sys.getrecursionlimit()
    assert ask(second, "May Ada book it?", "--case", "C001") == 5
    assert "translation" not in sys.modules
    assert (sys.path, sys.getrecursionlimit()) == (path, limit)  # review A2, B5: the runner's sys.path and limit


def test_sys_path_and_the_recursion_limit_are_put_back_after_an_answer(tmp_path, capsys):
    path, limit = list(sys.path), sys.getrecursionlimit()
    assert ask(staged(tmp_path), "May Ada book it?", "--case", "C002") == 0
    assert (sys.path, sys.getrecursionlimit()) == (path, limit) and limit != 54321


def test_a_runner_that_uses_a_process_pool_answers(tmp_path):
    """The gitlab-expenses and copilot runners map a case's sub-cases over a process pool: its workers import the
    runner's functions by the runner's own module name from its directory (failed with a synthetic module name)."""
    done = cli(staged(tmp_path, pool=True), "May Ada book it?", "--case", "C002")
    assert (done.returncode, answered(done.stdout)) == (0, "yes\n"), done.stderr


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
