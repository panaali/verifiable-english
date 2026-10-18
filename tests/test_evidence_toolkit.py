"""The evidence toolkit (tools/evidence, tools/batch_evidence.py --check) fails on evidence that shows nothing.

Known answers (docs/ARCHITECTURE-REVIEW-2026-10.md, AR-5a): the four historical false passes of copied
evidence scripts, each of which must FAIL here, and the classes around them (missing, duplicated and empty
latency keys, unavailable on both sides). Each failing case has a passing neighbour, so a checker that
rejects everything fails these tests too.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

from tools import batch_evidence
from tools.evidence import EvidenceError, ab, config, fuzz_ab, killed, latency as paired_tool, load, loads, report, scope
from tools.evidence import checkouts as evidence_checkouts, merge_base as evidence_merge_base
from tools.evidence import recording as evidence_recording, scope_range as evidence_scope_range

ROOT = Path(__file__).resolve().parents[1]
HEAD, BASE = "a" * 40, "b" * 40


def ids(value):
    """A test id without spaces: tools/mutants.py reads a failed node id up to the first space."""
    return re.sub(r"\W+", "-", value).strip("-")[:60] if isinstance(value, str) else None


# ---------------------------------------------------------------- latency

def _fake_run(cpu):
    """A `latency.run_command` stand-in: CPU ms from `cpu(root, path)`, one fixed output per input."""
    def run(root, command, item):
        return cpu(root, item), 0, f"checked {Path(item).name}\n"
    return run


def _same_name_documents(tmp_path):
    documents = []
    for directory in ("a", "b"):
        (tmp_path / directory).mkdir()
        documents.append(tmp_path / directory / "s1.ve.md")
        documents[-1].write_text(directory)
    return documents


def test_b1_two_documents_with_one_file_name_are_two_rows_and_the_slow_one_fails(tmp_path):
    """docs/lean-first/b1/latency.py:57 keyed rows by file name: `a/s1.ve.md` 50% slower was replaced by
    `b/s1.ve.md`'s row and the gate passed."""
    base, head = tmp_path / "base", tmp_path / "head"
    base.mkdir(), head.mkdir()
    slow, fast = _same_name_documents(tmp_path)
    cpu = _fake_run(lambda root, item: 15.0 if root == head and item == str(slow.resolve()) else 10.0)
    for order in ([slow, fast], [fast, slow]):
        samples, errors = paired_tool.measure(base, head, ["ve", "{input}"], [str(p) for p in order], 2, run=cpu)
        assert list(samples) == [str(p.resolve()) for p in order]
        assert errors == []
        assert paired_tool.row_problems(samples) == [
            f"latency sample {str(slow.resolve())!r}: head 15.0 ms is above 1.2 x base 10.0 ms"]
    samples, _ = paired_tool.measure(base, head, ["ve", "{input}"], [str(fast)], 2, run=cpu)
    assert paired_tool.row_problems(samples) == []


def test_latency_measure_compares_every_run_of_both_sides(tmp_path):
    base, head = tmp_path / "base", tmp_path / "head"
    base.mkdir(), head.mkdir()
    document = tmp_path / "d.ve.md"
    document.write_text("x")
    outputs = iter(["one\n", "one\n", "two\n", "one\n"])  # base, head, base, head: the base's second run differs

    def run(root, command, item):
        return 1.0, 0, next(outputs)
    samples, errors = paired_tool.measure(base, head, ["ve", "{input}"], [str(document)], 2, run=run)
    assert samples[str(document.resolve())]["same_output"] is False and errors
    assert paired_tool.row_problems(samples)
    empty = _fake_run(lambda root, item: 1.0)
    assert paired_tool.measure(base, head, ["ve", "{input}"], [str(document)], 1,
                           run=lambda r, c, i: (1.0, 0, ""))[1]  # an empty output shows nothing
    assert paired_tool.measure(base, head, ["ve", "{input}"], [str(document)], 1, run=empty)[1] == []


@pytest.mark.parametrize("arguments, message", [
    (lambda base, head, doc: (base, base, ["ve", "{input}"], [doc], 1), "same directory"),
    (lambda base, head, doc: (base, head, ["ve", "{input}"], [], 1), "needs inputs"),
    (lambda base, head, doc: (base, head, ["ve", "{input}"], [doc], 0), "needs inputs"),
    (lambda base, head, doc: (base, head, ["ve", "check"], [doc], 1), "naming {input}"),
    (lambda base, head, doc: (base, head, ["ve", "{input}"], [doc + ".missing"], 1), "no input"),
    (lambda base, head, doc: (base, head, ["ve", "{input}"], [doc, doc], 1), "occurs twice"),
], ids=ids)
def test_latency_measure_refuses_inputs_that_compare_nothing(tmp_path, arguments, message):
    base, head = tmp_path / "base", tmp_path / "head"
    base.mkdir(), head.mkdir()
    document = tmp_path / "d.ve.md"
    document.write_text("x")
    samples, errors = paired_tool.measure(*arguments(base, head, str(document)), run=_fake_run(lambda r, i: 1.0))
    assert samples == {} and message in errors[0]


PAIRED_RECORD = {"base_commit": BASE, "head_commit": HEAD, "pass": True, "allowance": 0.2,
           "samples": {"docs/a/s1.ve.md": {"base_cpu_ms": 10, "head_cpu_ms": 12},
                       "docs/b/s1.ve.md": {"base_cpu_ms": 10.0, "head_cpu_ms": 9.5}}}


def test_complete_latency_record_passes():
    assert paired_tool.problems(deepcopy(PAIRED_RECORD), HEAD, ["docs/a/s1.ve.md", "docs/b/s1.ve.md"]) == []


@pytest.mark.parametrize("change, expected, message", [
    (lambda s: s.pop("docs/b/s1.ve.md"), ["docs/a/s1.ve.md", "docs/b/s1.ve.md"], "no sample for 'docs/b/s1.ve.md'"),
    (lambda s: s.update({"": {"base_cpu_ms": 1, "head_cpu_ms": 1}}), [], "empty key"),
    (lambda s: s.update({"  ": {"base_cpu_ms": 1, "head_cpu_ms": 1}}), [], "empty key"),
    (lambda s: s.clear(), [], "latency evidence is empty"),
    (lambda s: s.update({"x": {"base_cpu_ms": None, "head_cpu_ms": None}}), [], "not measured on both sides"),
    (lambda s: s.update({"x": {"base_cpu_ms": 0, "head_cpu_ms": 0}}), [], "not measured on both sides"),
    (lambda s: s.update({"x": {"base_cpu_ms": True, "head_cpu_ms": 1}}), [], "not measured on both sides"),
    (lambda s: s.update({"x": {"base_cpu_ms": float("nan"), "head_cpu_ms": 1}}), [], "not measured on both sides"),
    (lambda s: s.update({"x": {"base_cpu_ms": 10, "head_cpu_ms": 12.01}}), [], "above 1.2 x base"),
    (lambda s: s.update({"x": {"base_cpu_ms": 1, "head_cpu_ms": 1, "same_output": False}}), [], "same output"),
    (lambda s: s.update({"x": {"base_cpu_ms": float("inf"), "head_cpu_ms": float("inf")}}), [],
     "not measured on both sides"),
], ids=ids)
def test_missing_empty_unavailable_or_slow_latency_rows_fail(change, expected, message):
    record = deepcopy(PAIRED_RECORD)
    change(record["samples"])
    errors = paired_tool.problems(record, HEAD, expected)
    assert any(message in error for error in errors), errors
    assert "latency evidence is empty, malformed or above the 20% Lean CPU budget" in errors


def test_a_duplicated_latency_key_is_refused_when_read():
    """`json.loads` keeps the last of two rows with one key, so a slow row can vanish before any check."""
    text = '{"head_commit": "%s", "pass": true, "samples": {"s1.ve.md": {"base_cpu_ms": 10, "head_cpu_ms": 15},' \
           ' "s1.ve.md": {"base_cpu_ms": 10, "head_cpu_ms": 10}}}' % HEAD
    assert paired_tool.problems(json.loads(text), HEAD) == []  # what the copies saw
    with pytest.raises(EvidenceError, match="occurs twice"):
        loads(text)
    with pytest.raises(ValueError, match="occurs twice"):
        paired_tool.paired(["k", "k"], lambda k: 1.0, lambda k: 1.0, 1)


def test_latency_record_head_and_pass_are_its_own():
    assert paired_tool.problems({**PAIRED_RECORD, "head_commit": "c" * 40}, HEAD) == [
        "latency budget was not measured and passed on HEAD"]
    assert paired_tool.problems({**PAIRED_RECORD, "pass": False}, HEAD)
    saved = paired_tool.record(BASE, HEAD, {"k": {"base_cpu_ms": 10, "head_cpu_ms": 13}}, "test")
    assert saved["pass"] is False and paired_tool.problems(saved, HEAD)


def test_paired_alternates_base_and_head():
    calls = []
    samples = paired_tool.paired(["k"], lambda k: calls.append("base") or 2.0, lambda k: calls.append("head") or 3.0, 3)
    assert calls == ["base", "head"] * 3
    assert samples == {"k": {"pairs": 3, "base_cpu_ms": 2.0, "head_cpu_ms": 3.0}}


def test_schedstat_reads_or_reports_unavailable(tmp_path):
    (tmp_path / "s").write_text("123 45 6\n")
    assert paired_tool.schedstat(str(tmp_path / "s")) == (123, 45)
    assert paired_tool.schedstat(str(tmp_path / "missing")) is None
    with pytest.raises(OSError):
        paired_tool.cpu_ns(-1)


# ---------------------------------------------------------------- corpus A/B

def test_lf0_empty_ab_files_fail(tmp_path):
    """The shared A/B tool accepted empty evidence (lf-0)."""
    base, head = tmp_path / "base.jsonl", tmp_path / "head.jsonl"
    for text in ("", "\n\n  \n"):
        base.write_text(text), head.write_text(text)
        comparison, errors = ab.compare(base, head, BASE, HEAD)
        assert comparison is None and errors == [f"{base}: the recording is empty", f"{head}: the recording is empty"]
    comparison, errors = ab.compare(tmp_path / "none.jsonl", head, BASE, HEAD)
    assert comparison is None and errors[0].endswith("no recording")


def test_ab_runs_lean_first_diff_and_reports_what_it_refuses(tmp_path):
    base, head = tmp_path / "base.jsonl", tmp_path / "head.jsonl"
    base.write_text('{"x": 1}\n'), head.write_text('{"x": 1}\n')
    comparison, errors = ab.compare(base, head, BASE, HEAD, corpora=["conformance"])
    assert comparison is None
    assert errors[0].startswith("lean_first_diff compare could not compare (exit 2)") and "no record" in errors[0]


AB = {"base_commit": BASE, "head_commit": HEAD, "unlisted": 0, "unavailable_both": {},
      "records": {f"{name}/python": 3 for name in sorted(ab.REQUIRED_CORPORA)}}


@pytest.mark.parametrize("change, message", [
    ({}, None),
    ({"records": {}}, "omitted a required corpus"),
    ({"records": {**AB["records"], "probe/python": 0}}, "omitted a required corpus"),
    ({"unavailable_both": {"readings/lean": 2}}, "omitted signed unavailable rows"),
    ({"unlisted": 1}, "unlisted result"),
    ({"unlisted": None}, "unlisted result"),
    ({"head_commit": BASE}, "did not run on HEAD"),
], ids=ids)
def test_saved_ab_known_answers(change, message):
    errors = ab.problems({**deepcopy(AB), **change}, HEAD)
    if message is None:
        assert errors == []
    else:
        assert any(message in error for error in errors), errors


# ---------------------------------------------------------------- fuzz A/B

ENTRY_A = {"id": "env-a", "signature": "aaaa", "answers": {
    "python": {"outcome": "error", "code": "InvalidInput", "text": "fields do not match: expected [sort]"},
    "lean": {"outcome": "error", "code": "InvalidInput",
             "text": "fields do not match: expected [sort, description], got [verbalisation]"},
    "rust": {"outcome": "error", "code": "InvalidInput", "text": "x"}}}
ENTRY_B = {"id": "env-b", "signature": "bbbb", "answers": {"python": {"outcome": "ok"}, "lean": {"outcome": "ok"}}}
BASELINE = [ENTRY_A, ENTRY_B]


def _report(not_reproduced=(), new=(), findings=None, answers=None):
    return {"seed": 1, "scale": 1, "corpus": {"environment": {"envelope": 3}},
            "mutants": {"environment": {"zero-fault": 1, "one-fault": 4, "two-fault": 2}},
            "findings": findings or {"environment": {"envelope:code": 2}},
            "answers": answers or {"environment": {"lean:error": 5, "lean:ok": 2}},
            "new": list(new), "baseline": {"entries": 2, "seen_in_sample": 1, "unreviewed": [],
                                           "not_reproduced": list(not_reproduced)}}


def _now(entry_answers):
    return {"classes": [], "answers": entry_answers, "signature": "0000"}


def test_identical_fuzz_reports_have_no_difference():
    result = fuzz_ab.compare(_report(), _report(), BASELINE, [])
    assert result == {"compared": 7, "explained": [], "unexplained": []}


def test_b10a_a_replay_verdict_swap_fails():
    """docs/lean-first/b10a/trace_fuzzer.py stopped hashing before the baseline replay: Lean replay verdicts
    [true, false] becoming [false, true] left the counts and the hashed part equal, and the gate passed."""
    base = _report([{"id": "env-b", "status": "fixed", "now": _now({})}])
    head = _report([{"id": "env-a", "status": "fixed", "now": _now({})}])
    assert len(base["baseline"]["not_reproduced"]) == len(head["baseline"]["not_reproduced"])
    result = fuzz_ab.compare(base, head, BASELINE, [])
    assert sorted((row["id"], row["base"], row["head"]) for row in result["unexplained"]) == [
        ("env-a", "reproduces", "fixed"), ("env-b", "fixed", "reproduces")]
    evidence = {"head_commit": HEAD, "pass": True, "runs": [{"run": "--ci", **result}]}
    assert fuzz_ab.problems(evidence, HEAD) == ["fuzz A/B run --ci has 2 unexplained difference(s)"]


def test_a_changed_replay_answer_with_the_same_status_fails():
    changed = {**ENTRY_B["answers"], "lean": {"outcome": "error", "code": "ResourceLimit", "text": "budget"}}
    base = _report([{"id": "env-b", "status": "changed", "now": _now(ENTRY_B["answers"])}])
    head = _report([{"id": "env-b", "status": "changed", "now": _now(changed)}])
    assert [row["id"] for row in fuzz_ab.compare(base, head, BASELINE, [])["unexplained"]] == ["env-b"]
    # a replay rule names a status change, so it cannot explain an answer changed under one status
    same_status = [{"kind": "replay", "id": "env-b", "base": "changed", "head": "changed"}]
    assert [row["id"] for row in fuzz_ab.compare(base, head, BASELINE, same_status)["unexplained"]] == ["env-b"]
    fixed = [{"kind": "replay", "id": "env-b", "base": "changed", "head": "fixed"}]
    head = _report([{"id": "env-b", "status": "fixed", "now": _now(changed)}])
    assert fuzz_ab.compare(base, head, BASELINE, fixed)["unexplained"] == []


KNOWN = [{"kind": "known_rejection", "base_lean_prefix": "fields do not match: expected [sort, description], got ["}]


def test_b10b_an_unexplained_new_lean_answer_after_a_known_rejection_fails():
    """docs/lean-first/b10b/fuzzer_gate.py:85 accepted any new Lean answer after the DF-19 rejection: an
    arbitrary ResourceLimit error passed as explained."""
    arbitrary = {**ENTRY_A["answers"], "lean": {"outcome": "error", "code": "ResourceLimit", "text": "budget"}}
    head = _report([{"id": "env-a", "status": "changed", "now": _now(arbitrary)}])
    result = fuzz_ab.compare(_report(), head, BASELINE, KNOWN)
    assert [row["id"] for row in result["unexplained"]] == ["env-a"] and result["explained"] == []


def test_a_new_lean_answer_that_agrees_with_python_after_the_known_rejection_is_explained():
    agrees = {**ENTRY_A["answers"], "lean": ENTRY_A["answers"]["python"]}
    head = _report([{"id": "env-a", "status": "fixed", "now": _now(agrees)}])
    result = fuzz_ab.compare(_report(), head, BASELINE, KNOWN)
    assert result["unexplained"] == [] and [row["id"] for row in result["explained"]] == ["env-a"]
    # the same change with Python's answer changed too is not the known rejection's fix
    moved = {**agrees, "python": {"outcome": "ok"}, "lean": {"outcome": "ok"}}
    head = _report([{"id": "env-a", "status": "fixed", "now": _now(moved)}])
    assert fuzz_ab.compare(_report(), head, BASELINE, KNOWN)["unexplained"]


def test_head_only_signatures_and_count_changes_need_a_rule():
    new = {"signature": "cccc", "surface": "environment", "classes": ["code"], "answers": {}}
    result = fuzz_ab.compare(_report(), _report(new=[new]), BASELINE, [])
    assert [row["kind"] for row in result["unexplained"]] == ["new"]
    result = fuzz_ab.compare(_report(new=[new]), _report(), BASELINE, [])
    assert result["unexplained"] == [] and result["explained"][0]["fixed_on_head"] is True
    head = _report(findings={"environment": {"envelope:code": 1}})
    rule = {"kind": "count", "field": "findings", "surface": "environment", "key": "envelope:code", "base": 2,
            "head": 1}
    assert fuzz_ab.compare(_report(), head, BASELINE, [])["unexplained"]
    assert fuzz_ab.compare(_report(), head, BASELINE, [rule])["unexplained"] == []
    assert fuzz_ab.compare(_report(), head, BASELINE, [{**rule, "head": 0}])["unexplained"]


@pytest.mark.parametrize("change", [
    lambda r: r.update(seed=2),
    lambda r: r["mutants"]["environment"].update({"one-fault": 5}),
    lambda r: r["baseline"].update(unreviewed=["env-a"]),
    lambda r: r["baseline"].update(entries=3),
], ids=ids)
def test_another_sample_or_baseline_fails(change):
    head = _report()
    change(head)
    assert fuzz_ab.compare(_report(), head, BASELINE, [])["unexplained"]


def test_a_fuzz_run_that_compared_nothing_fails():
    empty = _report()
    empty["mutants"] = {"environment": {"zero-fault": 0, "one-fault": 0, "two-fault": 0}}
    result = fuzz_ab.compare(empty, deepcopy(empty), BASELINE, [])
    assert result["compared"] == 0 and result["unexplained"]
    assert fuzz_ab.problems({"head_commit": HEAD, "pass": True, "runs": []}, HEAD) == ["fuzz A/B ran nothing"]
    assert fuzz_ab.problems({"head_commit": HEAD, "pass": True,
                             "runs": [{"run": "--ci", "compared": 0, "unexplained": []}]}, HEAD)
    assert fuzz_ab.problems({"head_commit": HEAD, "pass": True,
                             "runs": [{"run": "--ci", "compared": 7, "unexplained": []}]}, HEAD) == []


@pytest.mark.parametrize("rule", [
    {"kind": "known_rejection", "base_lean_prefix": ""},
    {"kind": "known_rejection"},
    {"kind": "replay", "id": "env-a", "base": "reproduces"},
    {"kind": "count", "field": "corpus", "surface": "s", "key": "k", "base": 1, "head": 2},
    {"kind": "anything"},
], ids=ids)
def test_malformed_fuzz_rules_are_refused(rule):
    assert fuzz_ab.rule_problems([rule])
    with pytest.raises(EvidenceError):
        fuzz_ab.compare(_report(), _report(), BASELINE, [rule])


def test_replay_outside_the_baseline_or_twice_is_refused():
    with pytest.raises(EvidenceError):
        fuzz_ab.compare(_report(), _report([{"id": "env-z", "status": "fixed", "now": {}}]), BASELINE, [])
    twice = [{"id": "env-a", "status": "fixed", "now": {}}] * 2
    with pytest.raises(EvidenceError):
        fuzz_ab.compare(_report(), _report(twice), BASELINE, [])


# ---------------------------------------------------------------- report, mutants, toml, --check

def test_report_renders_numbers_from_the_evidence(tmp_path):
    (tmp_path / "scope.json").write_text(json.dumps({"head": "0123456789" * 4,
                                                     "commits": [{"hash": "f" * 40}, {"hash": "e" * 40}]}))
    (tmp_path / "share.json").write_text(json.dumps({"x": {"documents": 10, "lean": 4}}))
    (tmp_path / "mutants.json").write_text(json.dumps({"mutants": [
        {"id": "M1", "file": "a.py", "killed": True, "killed_by": ["t"]},
        {"id": "M2", "file": "a.py", "killed": False}]}))
    lines = ["{{literal}} {scope.head|short}: {scope.commits|len} commits {scope.commits|map:hash|short|code|join:, }",
             "{share.x.documents|minus:share.x.lean} left; {mutants|killed}/{mutants.mutants|len} killed"]
    assert report.render(tmp_path, lines) == ("{literal} 01234567: 2 commits `ffffffff`, `eeeeeeee`\n"
                                              "6 left; 1/2 killed")
    for bad in ("{scope.nothing}", "{scope.head|len}", "{scope.head|unknown}", "{missing.x}", "{scope.head", "}"):
        with pytest.raises(EvidenceError):
            report.render(tmp_path, [bad])
    text = "a\n<!-- BEGIN GENERATED M -->\nold\n<!-- END GENERATED M -->\nb"
    assert report.block(report.replace_block(text, "M", "new"), "M") == "new"
    with pytest.raises(EvidenceError):
        report.block(text + text, "M")


@pytest.mark.parametrize("record, expected", [
    ({"id": "M1", "file": "ve/x.py", "killed": True, "killed_by": ["tests/test_x.py::t"]}, True),
    ({"id": "M1", "file": "ve/x.py", "killed": True, "killed_by": []}, False),
    ({"id": "M1", "file": "ve/x.py", "killed": False, "killed_by": ["t"]}, False),
    ({"id": "M1", "killed": True, "killed_by": ["t"]}, False),
    ({"bug": "b", "file": "ve/x.py", "test": "t", "exit_code": 1, "failure_excerpt": "1 failed"}, True),
    ({"bug": "b", "file": "ve/x.py", "test": "t", "exit_code": 0, "failure_excerpt": "1 failed"}, False),
    ({"bug": "b", "file": "ve/x.py", "test": "t", "exit_code": 1, "failure_excerpt": ""}, False),
    ({"bug": "b", "file": "ve/x.py", "exit_code": 1, "failure_excerpt": "x"}, False),
], ids=ids)
def test_a_mutant_counts_only_when_its_named_test_failed(record, expected):
    assert killed(record) is expected


def test_mutant_records_need_three_distinct_killed_mutants():
    rows = [{"id": f"M{i}", "file": "ve/x.py", "killed": True, "killed_by": ["t"]} for i in range(3)]
    assert batch_evidence.mutant_problems({"mutants": rows}) == []
    assert batch_evidence.mutant_problems({"mutants": rows[:2]})
    assert batch_evidence.mutant_problems(rows[:2] + [rows[0]])
    assert batch_evidence.mutant_problems(rows[:2] + [{**rows[2], "killed": False}])


def _git(repo, *args):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false", *args],
                          cwd=repo, check=True, capture_output=True, text=True).stdout.strip()


def test_scope_is_the_batch_commits_without_merges(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    (repo / "a.txt").write_text("1\n")
    _git(repo, "add", "-A"), _git(repo, "commit", "-qm", "base")
    _git(repo, "checkout", "-qb", "batch")
    (repo / "b.txt").write_text("1\n2\n")
    _git(repo, "add", "-A"), _git(repo, "commit", "-qm", "one")
    _git(repo, "checkout", "-q", "main")
    (repo / "c.txt").write_text("1\n")
    _git(repo, "add", "-A"), _git(repo, "commit", "-qm", "main moves")
    _git(repo, "checkout", "-q", "batch")
    _git(repo, "merge", "-q", "--no-edit", "main")
    (repo / "a.txt").write_text("2\n")
    _git(repo, "add", "-A"), _git(repo, "commit", "-qm", "two")
    saved = scope("main", "HEAD", repo)
    assert [c["subject"] for c in saved["commits"]] == ["two", "one"]
    assert saved["head"] == _git(repo, "rev-parse", "HEAD") == saved["commits"][0]["hash"]
    assert saved["changes"] == [{"path": "a.txt", "added": 1, "deleted": 1}, {"path": "b.txt", "added": 2, "deleted": 0}]
    assert batch_evidence.scope_problems(saved) == []
    assert batch_evidence.scope_history_problems(saved, cwd=repo) == []
    changed = deepcopy(saved)
    changed["commits"][0]["subject"] = "invented"
    assert "scope commits differ" in batch_evidence.scope_history_problems(changed, cwd=repo)[0]
    changed = deepcopy(saved)
    changed["changes"] = [{"path": "tools/not-in-the-commit.py", "added": 1, "deleted": 0}]
    assert "scope changes differ" in batch_evidence.scope_history_problems(changed, cwd=repo)[0]
    with pytest.raises(EvidenceError):
        scope("HEAD", "HEAD", repo)


GATE = {"commit_sha": HEAD, "dirty": False, "status": "passed", "stages": list(batch_evidence.REQUIRED_STAGES),
        "failures": [], "counts": {"passed": 5, "skipped": 1, "failed": 0, "selected": 6, "deselected": 1,
                                   "collected": 7, "rust_passed": 2}}
SCOPE = {"base": BASE, "head": HEAD, "commits": [{"hash": HEAD, "subject": "s"}],
         "changes": [{"path": "tools/x.py", "added": 1, "deleted": 0}]}
MUTANTS = {"mutants": [{"id": f"M{i}", "file": "tools/x.py", "killed": True, "killed_by": ["t"]} for i in range(3)]}
TOML = '''batch = "test"
[scope]
file = "scope.json"
[gate]
file = "gate.json"
[mutants]
file = "mutants.json"
[report]
file = "REPORT.md"
marker = "T"
lines = ["gate {gate.commit_sha|short}: {gate.counts.passed} passed"]
'''


@pytest.fixture
def batch(tmp_path, monkeypatch):
    """A complete batch directory; the toolkit's repository root is moved to tmp_path."""
    monkeypatch.setattr(config, "ROOT", tmp_path)
    monkeypatch.setattr(batch_evidence, "scope_history_problems", lambda saved, main: [])
    monkeypatch.setattr(batch_evidence, "mutant_source_problems", lambda mutants, head: [])
    directory = tmp_path / "docs/t/b"
    (directory / "evidence").mkdir(parents=True)
    for name, value in (("scope", SCOPE), ("gate", GATE), ("mutants", MUTANTS)):
        (directory / "evidence" / f"{name}.json").write_text(json.dumps(value))
    (directory / "evidence.toml").write_text(TOML)
    (directory / "REPORT.md").write_text("<!-- BEGIN GENERATED T -->\ngate aaaaaaaa: 5 passed\n"
                                         "<!-- END GENERATED T -->\n")
    return directory


def _write(directory, name, value):
    (directory / "evidence" / f"{name}.json").write_text(json.dumps(value))


def test_a_complete_batch_passes_the_check(batch, capsys):
    assert batch_evidence.check(batch) == (HEAD, [])
    assert batch_evidence.main(["--check", str(batch)]) == 0
    assert f"batch evidence PASS on {HEAD}" in capsys.readouterr().out


@pytest.mark.parametrize("name, change, message", [
    ("gate", {"commit_sha": BASE}, "did not run on a clean HEAD"),
    ("gate", {"failures": [{"test": "t"}]}, "lists failures"),
    ("gate", {"counts": {**GATE["counts"], "selected": 7}}, "do not add up"),
    ("gate", {"counts": {**GATE["counts"], "passed": 4, "failed": 1}}, "show a failure"),
    ("gate", {"stages": list(batch_evidence.REQUIRED_STAGES)[:-1]}, "incomplete or failed"),
    ("scope", {"commits": []}, "lists no commits"),
    ("scope", {"commits": [{"hash": BASE}]}, "not its head"),
    ("scope", {"changes": []}, "no changed paths"),
    ("mutants", {"mutants": MUTANTS["mutants"][:2]}, "fewer than 3"),
], ids=ids)
def test_stale_or_incomplete_batch_evidence_fails_the_check(batch, name, change, message):
    value = {"scope": SCOPE, "gate": GATE, "mutants": MUTANTS}[name]
    _write(batch, name, {**deepcopy(value), **change})
    head, errors = batch_evidence.check(batch)
    assert any(message in error for error in errors), errors


def test_a_report_number_typed_by_hand_fails_the_check(batch):
    (batch / "REPORT.md").write_text("<!-- BEGIN GENERATED T -->\ngate aaaaaaaa: 6 passed\n<!-- END GENERATED T -->\n")
    assert batch_evidence.check(batch)[1] == ["the T block of REPORT.md is not the rendering of the evidence "
                                              "(python -m tools.evidence report)"]


def test_a_batch_changing_ve_or_lean_needs_its_corpus_ab(batch):
    _write(batch, "scope", {**SCOPE, "changes": [{"path": "ve/x.py", "added": 1, "deleted": 0}]})
    assert "names no [ab]" in batch_evidence.check(batch)[1][0]
    (batch / "evidence.toml").write_text(TOML + '[ab]\nfile = "ab.json"\n')
    _write(batch, "ab", AB)
    assert batch_evidence.check(batch)[1] == []
    _write(batch, "ab", {**AB, "unavailable_both": {"readings/lean": 1}})
    assert "corpus comparison omitted signed unavailable rows" in batch_evidence.check(batch)[1]


def test_named_latency_and_fuzz_ab_are_checked(batch):
    (batch / "evidence.toml").write_text(TOML + '[latency]\nfile = "latency.json"\nworkloads = ["docs/a/s1.ve.md", '
                                         '"docs/b/s1.ve.md"]\n[fuzz_ab]\nfile = "fuzz.json"\n')
    _write(batch, "latency", PAIRED_RECORD)
    _write(batch, "fuzz", {"base_commit": BASE, "head_commit": HEAD, "pass": True, "rules": [],
                           "runs": [{"run": "--ci", "compared": 3, "explained": [], "unexplained": []}]})
    assert batch_evidence.check(batch)[1] == []
    _write(batch, "latency", {**PAIRED_RECORD, "samples": {"docs/a/s1.ve.md": PAIRED_RECORD["samples"]["docs/a/s1.ve.md"]}})
    assert "latency evidence has no sample for 'docs/b/s1.ve.md'" in batch_evidence.check(batch)[1]
    (batch / "evidence" / "latency.json").write_text(
        '{"head_commit": "%s", "pass": true, "samples": {"docs/a/s1.ve.md": {"base_cpu_ms": 1, "head_cpu_ms": 9}, '
        '"docs/a/s1.ve.md": {"base_cpu_ms": 1, "head_cpu_ms": 1}, "docs/b/s1.ve.md": {"base_cpu_ms": 1, '
        '"head_cpu_ms": 1}}}' % HEAD)
    with pytest.raises(EvidenceError, match="occurs twice"):
        batch_evidence.check(batch)


def test_tally_claims_check_a_ledger_against_its_table(batch):
    _write(batch, "rows", [{"g": "x", "c": "p"}, {"g": "x", "c": "q"}, {"g": "y", "c": "p"}])
    _write(batch, "table", {"x": {"other": {"p": 1, "q": 1}, "lean": 3, "all": 5},
                            "y": {"other": {"p": 1}, "lean": 0, "all": 1}})
    claim = '[[claims]]\nkind = "tally"\nrows = "rows"\ngroup = "g"\nfield = "c"\ntable = "table"\ncounts = "other"\n'
    (batch / "evidence.toml").write_text(TOML + claim + 'total = "all"\nrest = "lean"\n')
    assert batch_evidence.check(batch)[1] == []
    _write(batch, "table", {"x": {"other": {"p": 2}, "lean": 3, "all": 5}, "y": {"other": {"p": 1}, "lean": 0, "all": 1}})
    assert batch_evidence.check(batch)[1] == ["tally rows: x counts differ from table"]


@pytest.mark.parametrize("text, message", [
    (TOML + "[gates]\nfile = \"g.json\"\n", "unknown key 'gates'"),
    (TOML.replace('[mutants]\nfile = "mutants.json"\n', ""), "missing 'mutants'"),
    (TOML + '[latency]\nfile = "l.json"\n', "[latency] misses 'workloads'"),
    (TOML + '[latency]\nfile = "l.json"\nworkloads = []\n', "not a non-empty list"),
    (TOML + '[latency]\nfile = "l.json"\nworkload = ["a"]\nworkloads = ["a"]\n', "unknown key 'workload'"),
    (TOML.replace('batch = "test"', 'batch = ""'), "batch is not a name"),
    (TOML.replace('file = "mutants.json"', 'file = "mutants.json"\nmin = 0'), "min is not a whole number of at least 3"),
    (TOML + '[latency]\nfile = "l.json"\nworkloads = ["a"]\nallowance = 0.5\n', "allowance is not between 0 and 0.2"),
    (TOML.replace('batch = "test"', 'batch = "test"\nevidence = "../../../.."'), "outside the repository"),
], ids=ids)
def test_a_toml_that_would_check_nothing_is_refused(batch, text, message):
    (batch / "evidence.toml").write_text(text)
    with pytest.raises(EvidenceError, match=message.replace("[", r"\[").replace("]", r"\]")):
        batch_evidence.check(batch)


def test_check_cli_reports_errors_and_refuses_mixed_forms(batch, capsys):
    _write(batch, "gate", {**GATE, "dirty": True})
    assert batch_evidence.main(["--check", str(batch)]) == 1
    assert "full gate did not run on a clean HEAD" in capsys.readouterr().out
    with pytest.raises(SystemExit):
        batch_evidence.main(["--check", str(batch), HEAD])
    with pytest.raises(SystemExit):
        batch_evidence.main(["--check", str(batch), "--report-dir", "docs"])


def test_evidence_cli_runs_as_a_module_and_as_a_directory():
    for command in ([sys.executable, "-m", "tools.evidence"], [sys.executable, str(ROOT / "tools/evidence")]):
        done = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        assert done.returncode == 2 and "scope,latency,ab,fuzz_ab,mutants,report" in done.stderr


def test_load_refuses_empty_and_missing_files(tmp_path):
    (tmp_path / "e.json").write_text("")
    for path in (tmp_path / "e.json", tmp_path / "missing.json"):
        with pytest.raises(EvidenceError):
            load(path)


def test_the_mutants_command_is_the_one_harness():
    from tools import mutants
    from tools.evidence.__main__ import COMMANDS
    assert COMMANDS["mutants"] is mutants.main


# ---------------------------------------------------------------- the latency tools on the shared module

class _Service:
    def __init__(self, executable):
        self.executable = executable

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def _readings_batch(monkeypatch, tmp_path, names, head_ms):
    from tools import readings_batch_latency as tool
    corpus = tmp_path / "corpus.json"
    corpus.write_text(json.dumps([{"case": name, "environment": {}, "document": {"units": [], "reading_sets": []}}
                                  for name in names]))
    out = tmp_path / "latency.json"
    monkeypatch.setattr(tool, "LeanService", _Service)
    monkeypatch.setattr(tool, "checkouts", lambda base_root, head_root: (BASE, HEAD))
    monkeypatch.setattr(tool, "answer", lambda service, case: ("returned", []))
    monkeypatch.setattr(tool, "measure",
                        lambda service, case, calls: head_ms if "head" in str(service.executable) else 10.0)
    monkeypatch.setattr(sys, "argv", ["readings_batch_latency.py", str(tmp_path / "base"), str(tmp_path / "head"),
                                      str(corpus), HEAD, str(out), "--pairs", "2"])
    return tool.main, out


@pytest.mark.parametrize("head_ms, status", [(12.0, 0), (12.5, 1)])
def test_readings_batch_latency_applies_the_shared_rule(monkeypatch, tmp_path, head_ms, status):
    main, out = _readings_batch(monkeypatch, tmp_path, ["c0", "c1", "c2"], head_ms)
    assert main() == status
    saved = load(out)
    assert sorted(saved["samples"]) == ["c0", "c1", "c2"] and saved["pass"] is (status == 0)
    assert all(row["pairs"] == 2 and row["calls_per_side"] == 200 for row in saved["samples"].values())
    assert (paired_tool.problems(saved, HEAD, ["c0", "c1", "c2"]) == []) is (status == 0)


def test_readings_batch_latency_refuses_two_cases_with_one_name(monkeypatch, tmp_path):
    main, out = _readings_batch(monkeypatch, tmp_path, ["c0", "c1", "c0"], 10.0)
    with pytest.raises(RuntimeError, match="two readings cases are named c0"):
        main()
    assert not out.exists()


# ---------------------------------------------------------------- evidence tied to the batch (arch-20261010-2)

def _commit(repo, name, text, message):
    (repo / name).parent.mkdir(parents=True, exist_ok=True)
    (repo / name).write_text(text)
    _git(repo, "add", "-A"), _git(repo, "commit", "-qm", message)
    return _git(repo, "rev-parse", "HEAD")


@pytest.fixture
def history(tmp_path):
    """`main` at m0; the batch from m0 changes ve/x.py, then tools/t.py; then `main` moves to m1."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    m0 = _commit(repo, "a.txt", "1\n", "m0")
    _git(repo, "checkout", "-qb", "batch")
    product = _commit(repo, "ve/x.py", "x = 1\n", "product")
    tool = _commit(repo, "tools/t.py", "t = 1\n", "tool")
    _git(repo, "checkout", "-q", "main")
    m1 = _commit(repo, "c.txt", "1\n", "m1")
    _git(repo, "checkout", "-q", "batch")
    return repo, m0, product, tool, m1


def test_f1_a_scope_from_inside_the_batch_fails_before_and_after_the_merge(history):
    """Review F1: a fix round saved its scope with `--base <reviewed commit>`, dropping the batch's earlier `ve/`
    commit (so no [ab] was required), and the check replayed only `base..head`."""
    repo, m0, product, tool, m1 = history
    full, short = scope("main", tool, repo), evidence_scope_range(product, tool, repo)
    assert full["base"] == m0 and [c["hash"] for c in full["commits"]] == [tool, product]
    assert batch_evidence.scope_history_problems(full, cwd=repo) == []
    assert batch_evidence.scope_history_problems(short, cwd=repo) == [
        f"scope base {product[:8]} is not the batch's merge base {m0[:8]} with main",
        f"scope commits differ from the batch's {m0[:8]}..{tool[:8]} --no-merges (its merge base with main)",
        f"scope changes differ from the batch's {m0[:8]}..{tool[:8]} --no-merges (its merge base with main)"]
    # The merge base does not move when the batch merges and main goes on.
    _git(repo, "checkout", "-q", "main")
    _git(repo, "merge", "-q", "--no-ff", "--no-edit", "batch")
    _commit(repo, "d.txt", "1\n", "m2")
    assert evidence_merge_base(tool, "main", repo) == m0
    assert scope("main", tool, repo) == full  # the writer names the same base as the check
    assert batch_evidence.scope_history_problems(full, cwd=repo) == []
    assert len(batch_evidence.scope_history_problems(short, cwd=repo)) == 3


def _adopting_main(repo):
    """A later `main` commit that adopted the batch's `ve/x.py` change on its own."""
    _git(repo, "checkout", "-q", "main")
    adopted = _commit(repo, "ve/x.py", "x = 1\n", "main adopts x = 1")
    _git(repo, "checkout", "-q", "batch")
    return adopted


@pytest.mark.parametrize("which", ["later-main", "main-that-adopted-the-change", "inside-the-batch"])
def test_f1_recheck_only_the_merge_base_names_the_scope(history, which):
    """Recheck F1: a later `main` commit whose range holds the very same commits and changes passed as the
    scope's base; an A/B against it (one that adopted the batch's change) would show no difference. Every
    base other than the merge base fails, whatever its range holds."""
    repo, m0, product, tool, m1 = history
    base = {"later-main": lambda: m1, "main-that-adopted-the-change": lambda: _adopting_main(repo),
            "inside-the-batch": lambda: product}[which]()
    saved = evidence_scope_range(base, tool, repo)
    if which != "inside-the-batch":
        same = evidence_scope_range(m0, tool, repo)
        assert (saved["commits"], saved["changes"]) == (same["commits"], same["changes"])  # the very same range
    errors = batch_evidence.scope_history_problems(saved, cwd=repo)
    assert errors[0] == f"scope base {base[:8]} is not the batch's merge base {m0[:8]} with main", errors
    assert batch_evidence.scope_history_problems(scope("main", tool, repo), cwd=repo) == []


def test_f1_a_head_that_reached_main_without_a_merge_needs_main_before_it(history):
    repo, m0, product, tool, m1 = history
    _git(repo, "checkout", "-q", "main")
    _git(repo, "reset", "-q", "--hard", tool)  # main fast-forwarded onto the batch
    with pytest.raises(EvidenceError, match="without a merge commit"):
        evidence_merge_base(tool, "main", repo)
    saved = evidence_scope_range(m0, tool, repo)
    assert "cannot be reproduced" in batch_evidence.scope_history_problems(saved, cwd=repo)[0]
    assert batch_evidence.scope_history_problems(saved, m0, cwd=repo) == []  # --main names main before it


FUZZ = {"base_commit": BASE, "head_commit": HEAD, "pass": True, "rules": [],
        "runs": [{"run": "--ci", "compared": 3, "explained": [], "unexplained": []}]}
AB_RECORDS = {"ab": (lambda record, base: ab.problems(record, HEAD, base=base), AB),
              "latency": (lambda record, base: paired_tool.problems(record, HEAD, base=base), PAIRED_RECORD),
              "fuzz_ab": (lambda record, base: fuzz_ab.problems(record, HEAD, base), FUZZ)}


@pytest.mark.parametrize("name", sorted(AB_RECORDS))
@pytest.mark.parametrize("base, change, message", [
    pytest.param(BASE, {}, None, id="the-batch-base"),
    pytest.param(BASE, {"base_commit": HEAD}, "with itself", id="head-against-head"),
    pytest.param(BASE, {"base_commit": "c" * 40}, "not on the batch's merge base", id="another-base"),
    pytest.param(BASE, {"base_commit": None}, "names no base commit", id="no-base"),
    pytest.param(BASE, {"base_commit": BASE[:8]}, "names no base commit", id="short-base"),
    pytest.param(None, {"base_commit": None}, None, id="positional-form-record-before-the-toolkit"),
    pytest.param(None, {"base_commit": HEAD}, "with itself", id="positional-form-head-against-head"),
])
def test_f2_every_ab_record_compared_the_batch_base_with_its_head(name, base, change, message):
    """Review F2: a fuzz A/B of the head against itself passed, and no A/B record's base met the scope's."""
    problems, record = AB_RECORDS[name]
    record = {**deepcopy(record), **change}
    if change.get("base_commit", "") is None:
        del record["base_commit"]
    errors = problems(record, base)
    assert errors == [] if message is None else any(message in error for error in errors), errors


def test_f2_ab_measurements_take_both_commits_from_two_clean_checkouts(history, tmp_path):
    repo, m0, product, tool, m1 = history
    same, other = tmp_path / "same", tmp_path / "other"
    _git(repo, "worktree", "add", "-q", "--detach", str(same), tool)
    _git(repo, "worktree", "add", "-q", "--detach", str(other), m0)
    assert evidence_checkouts(other, repo) == (m0, tool)
    for base_root, message in ((repo, "same directory"), (same, "both at")):
        with pytest.raises(EvidenceError, match=message):
            evidence_checkouts(base_root, repo)
    (other / "a.txt").write_text("changed\n")
    with pytest.raises(EvidenceError, match="uncommitted changes"):
        evidence_checkouts(other, repo)
    document = tmp_path / "d.ve.md"
    document.write_text("x")
    assert paired_tool.main(["measure", "--base-root", str(same), "--head-root", str(repo), "--command",
                             "cat {input}", "--input", str(document), "--out", str(tmp_path / "l.json")]) == 1
    assert not (tmp_path / "l.json").exists()
    recording = tmp_path / "r.jsonl"
    recording.write_text('{"x": 1}\n')
    assert ab.compare(recording, recording, tool, tool) == (None, [f"corpus comparison compared the head {tool} "
                                                                   "with itself"])


def test_f2_a_mutant_counts_only_for_its_file_at_the_head(history):
    repo, m0, product, tool, m1 = history
    rows = [{"id": "M1", "file": "tools/t.py", "killed": True, "killed_by": ["t"],
             "source_sha256": hashlib.sha256(b"t = 1\n").hexdigest()},
            {"id": "L1", "file": "ve/x.py", "test": "t", "exit_code": 1, "failure_excerpt": "x"}]
    assert batch_evidence.mutant_source_problems(rows, tool, repo) == []
    assert batch_evidence.mutant_source_problems([{**rows[0], "source_sha256": "0" * 64}], tool, repo) == [
        f"seeded mutant M1 ran on another tools/t.py than the one at {tool}"]
    assert batch_evidence.mutant_source_problems([{**rows[0], "file": "tools/gone.py"}], tool, repo) == [
        f"seeded mutant M1: tools/gone.py is not a file at {tool}"]
    assert batch_evidence.mutant_source_problems([{k: v for k, v in rows[0].items() if k != "source_sha256"}],
                                                 tool, repo)


@pytest.mark.parametrize("section", sorted(config.SECTIONS), ids=ids)
def test_f3_no_section_reads_a_file_outside_the_repository(batch, section):
    """Review F3: `[gate] file = "/tmp/.../gate.json"` passed; every section's file is resolved inside."""
    outside = batch.parents[2].parent / f"outside-{section}.json"
    outside.write_text(json.dumps({"scope": SCOPE, "gate": GATE, "mutants": MUTANTS}.get(section, {})))
    tables = {"scope": {"file": "scope.json"}, "gate": {"file": "gate.json"}, "mutants": {"file": "mutants.json"}}
    tables[section] = {**{"latency": {"workloads": ["w"]}, "report": {"marker": "T", "lines": ["x"]}}.get(section, {}),
                       "file": str(outside)}
    (batch / "evidence.toml").write_text('batch = "test"\n' + "".join(
        f"[{name}]\n" + "".join(f"{key} = {json.dumps(value)}\n" for key, value in table.items())
        for name, table in tables.items()))
    with pytest.raises(EvidenceError, match="outside the repository"):
        batch_evidence.check(batch)


def test_f3_the_check_lists_every_file_it_reads(batch):
    with evidence_recording() as opened:
        batch_evidence.check(batch)
    assert sorted({path.relative_to(batch).as_posix() for path in opened}) == [
        "REPORT.md", "evidence.toml", "evidence/gate.json", "evidence/mutants.json", "evidence/scope.json"]


def test_f1_f2_f3_a_committed_batch_passes_and_each_untied_piece_fails(history, monkeypatch):
    """End to end in a repository: the evidence of a batch passes at its report commit; a scope from inside
    the batch (F1), a fuzz A/B of the head against itself (F2) and evidence that is ignored or not committed
    (F3) each fail."""
    repo, m0, product, tool, m1 = history
    monkeypatch.setattr(config, "ROOT", repo)
    monkeypatch.setattr(batch_evidence, "ROOT", repo)
    monkeypatch.chdir(repo)  # main's report-commit check reads Git where it runs
    directory = repo / "docs/t/b"
    evidence = directory / "evidence"
    evidence.mkdir(parents=True)
    rows = [{"id": f"M{i}", "file": "tools/t.py", "killed": True, "killed_by": ["t"],
             "source_sha256": hashlib.sha256(b"t = 1\n").hexdigest()} for i in range(3)]
    for name, value in (("scope", scope("main", tool, repo)), ("gate", {**GATE, "commit_sha": tool}),
                        ("mutants", {"mutants": rows}), ("ab", {**AB, "base_commit": m0, "head_commit": tool})):
        (evidence / f"{name}.json").write_text(json.dumps(value))
    (directory / "evidence.toml").write_text(TOML.split("[report]")[0] + '[ab]\nfile = "ab.json"\n')
    report_commit = _commit(repo, "docs/t/b/README", "b\n", "report")
    assert batch_evidence.check(directory, "main", report_commit) == (tool, [])
    assert batch_evidence.main(["--check", str(directory), "--report-commit", report_commit]) == 0

    (evidence / "scope.json").write_text(json.dumps(evidence_scope_range(product, tool, repo)))
    assert any("differ from the batch's" in error for error in batch_evidence.check(directory)[1])
    # Recheck F1: scope and A/B both from a later main that adopted the change: same range, A/B shows nothing.
    _git(repo, "checkout", "-q", "--", "docs")
    adopted = _adopting_main(repo)
    (evidence / "scope.json").write_text(json.dumps(evidence_scope_range(adopted, tool, repo)))
    (evidence / "ab.json").write_text(json.dumps({**AB, "base_commit": adopted, "head_commit": tool}))
    assert batch_evidence.check(directory)[1] == [
        f"scope base {adopted[:8]} is not the batch's merge base {m0[:8]} with main"]
    _git(repo, "checkout", "-q", "--", "docs")

    (directory / "evidence.toml").write_text(TOML.split("[report]")[0] + '[ab]\nfile = "ab.json"\n'
                                             '[fuzz_ab]\nfile = "fuzz.json"\n')
    (evidence / "fuzz.json").write_text(json.dumps({**FUZZ, "base_commit": tool, "head_commit": tool}))
    errors = batch_evidence.check(directory, "main", report_commit)[1]
    assert f"fuzz A/B compared the head {tool} with itself" in errors
    assert "docs/t/b/evidence/fuzz.json is not committed as read at " + report_commit in errors
    assert "docs/t/b/evidence.toml is not committed as read at " + report_commit in errors

    (repo / ".gitignore").write_text("fuzz.json\n")
    (evidence / "fuzz.json").write_text(json.dumps({**FUZZ, "base_commit": m0, "head_commit": tool}))
    later = _commit(repo, "docs/t/b/README", "c\n", "report again")
    assert batch_evidence.check(directory, "main", later)[1] == [
        f"docs/t/b/evidence/fuzz.json is not committed as read at {later}"]
