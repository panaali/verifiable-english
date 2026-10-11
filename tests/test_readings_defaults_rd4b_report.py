"""RD-4b's report is checked against immutable evidence captured from the clean code head.

No test in this file calls Git or reads a moving branch or worktree diff. In particular the saved commit list is
`main..HEAD --no-merges` at the code head before the report was committed, so a later sync or merge cannot change it.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest


HERE = Path(__file__).resolve().parents[1] / "docs/readings-defaults/rd4b"


def saved():
    paths = [HERE / "DELTA.md", *(HERE / "evidence" / (name + ".json")
                                   for name in ("scope", "gate", "checks", "mutants"))]
    if any(not p.is_file() for p in paths):
        pytest.skip("RD-4b evidence is written after the clean code-head gate")
    report = paths[0].read_text()
    scope, gate, checks, mutants = [json.loads(p.read_text()) for p in paths[1:]]
    return report, scope, gate, checks, mutants


def test_rd4b_report_commit_scope_is_the_saved_no_merge_range():
    report, scope, _, _, _ = saved()
    assert scope["range"] == "main..HEAD --no-merges"
    commits = scope["commits"]
    assert commits and len(commits) == len(set(commits))
    assert all(len(value) == 40 for value in commits)
    assert scope["head"] == commits[-1]
    assert str(len(commits)) + " code commits" in report
    for commit in commits:
        assert commit[:8] in report
    stats = scope["numstat"]
    assert [item["commit"] for item in stats] == commits
    assert all(type(row["added"]) is int and type(row["deleted"]) is int
               and row["added"] >= 0 and row["deleted"] >= 0
               for item in stats for row in item["files"])
    added = sum(row["added"] for item in stats for row in item["files"])
    deleted = sum(row["deleted"] for item in stats for row in item["files"])
    assert f"{added:,} added lines" in report and f"{deleted:,} deleted lines" in report


def test_rd4b_report_gate_numbers_are_saved_and_clean():
    report, scope, gate, checks, _ = saved()
    assert gate["commit_sha"] == scope["head"] and gate["dirty"] is False
    assert gate["status"] == "passed" and gate["failures"] == []
    assert gate["stages"] == ["toolchains", "lean_build", "lean_audit", "rust_build", "cargo_test", "pytest"]
    counts = gate["counts"]
    assert counts["failed"] == 0 and counts["passed"] > 0 and counts["rust_passed"] > 0
    assert counts["selected"] == counts["passed"] + counts["skipped"] + counts["failed"]
    for key in ("passed", "skipped", "rust_passed", "collected"):
        assert f"{counts[key]:,}" in report
    assert checks["statement_check"]["rd4b"] == {"declarations": 16, "theorems": 6, "exact": 16, "pending": 0}
    assert f"{checks['audit']['sources']:,} source files" in report
    assert f"{checks['audit']['theorems']:,} audited theorems" in report


def test_rd4b_report_seeded_bugs_have_saved_failing_tests():
    report, _, _, _, mutants = saved()
    rows = mutants["mutants"]
    assert len(rows) >= 3 and len({row["name"] for row in rows}) == len(rows)
    for row in rows:
        assert row["exit_code"] != 0 and row["failed_id_present"] is True
        assert f"FAILED {row['test']}" in row["failure_tail"]
        assert row["name"] in report and row["test"] in report
        assert len(row["source_sha256_after_restore"]) == 64


def test_rd4b_report_acceptance_labels_and_limits():
    report, _, _, checks, _ = saved()
    assert "AGENT" in report and "HUMAN" in report and "EXTERNAL" in report
    assert "Not run" in report
    for test in checks["acceptance_tests"]:
        assert test in report


def test_rd4b_ab_is_checked_from_saved_recordings_and_comparisons():
    report, scope, _, _, _ = saved()
    ab = json.loads((HERE / "evidence/ab.json").read_text())
    raw = json.loads((HERE / "evidence/ab-raw-compare.json").read_text())
    normalized = json.loads((HERE / "evidence/ab-normalized-compare.json").read_text())
    assert ab["base_commit"] == scope["merge_base"] and ab["head_commit"] == scope["head"]
    rows = ab["recordings"]["rows"]
    assert rows == sum(normalized["records"].values()) == sum(ab["recordings"]["corpora"].values())
    assert raw["records"] == normalized["records"] == ab["recordings"]["corpora"]
    assert raw["totals"] == ab["raw"]["totals"] == {"same": rows - 7, "wording": 7}
    assert normalized["totals"] == ab["normalized"]["totals"] == {"same": rows}
    assert normalized["unlisted"] == ab["normalized"]["unlisted"] == 0
    assert len(raw["differences"]) == len(ab["raw"]["differences"]) == 7
    before = ab["normalization"]["base_from"]
    after = ab["normalization"]["head_from"]
    for row in ab["raw"]["differences"]:
        assert row["class"] == "wording" and "/probes/senses-documents/" in row["case"]
        assert len(row["base_stderr"]) == len(row["head_stderr"]) == 1
        assert before in row["base_stderr"][0] and after in row["head_stderr"][0]
        assert row["base_stderr"][0].replace(before, "<scratch>/pack.json") == (
            row["head_stderr"][0].replace(after, "<scratch>/pack.json"))
    digests = ab["recordings"]["sha256"]
    assert all(len(value) == 64 for value in digests.values())
    assert digests["base_normalized"] == digests["head_normalized"]
    assert f"{rows:,} records" in report
    assert f"{raw['totals']['same']:,} same" in report
    assert f"{rows:,} same, 0 unlisted" in report
