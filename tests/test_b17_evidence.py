"""Batch 17 report assertions read only saved evidence, never moving Git refs."""

import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/lean-first/b17/evidence"
REPORT = ROOT / "docs/lean-first/b17/REPORT.md"


def saved(name):
    return json.loads((EVIDENCE / name).read_text())


def scope_report():
    scope = saved("scope.json")
    report = REPORT.read_text()
    assert scope["range"] == "main..HEAD --no-merges"
    commits = scope["commits"]
    assert commits and scope["captured_head"] == commits[0]
    assert len(commits) == len(set(commits))
    assert all(re.fullmatch("[0-9a-f]{40}", commit) for commit in commits)
    assert all(row["commit"] in commits for row in scope["files"])
    assert "Source commits (saved): " + ", ".join(commits) in report
    return scope, report


def test_b17_report_change_metrics_from_saved_scope():
    scope, report = scope_report()
    files = scope["files"]
    totals = scope["totals"]
    assert totals == {
        "added": sum(row["added"] for row in files),
        "deleted": sum(row["deleted"] for row in files),
        "lean_added": sum(row["added"] for row in files if row["path"].endswith(".lean")),
        "python_deleted": sum(row["deleted"] for row in files if row["path"].endswith(".py")),
    }
    assert f"Total lines deleted: {totals['deleted']}" in report
    assert f"Lean lines added: {totals['lean_added']}" in report
    assert f"Python lines deleted: {totals['python_deleted']}" in report


def test_b17_report_gate_from_saved_clean_run():
    scope, report = scope_report()
    gate = saved("gate.json")
    counts = gate["counts"]
    assert gate["commit_sha"] == scope["captured_head"]
    assert gate["status"] == "passed" and gate["dirty"] is False
    assert counts["selected"] == counts["passed"] + counts["skipped"] + counts["failed"]
    assert counts["failed"] == 0 and gate["failures"] == []
    assert f"Full gate: {counts['passed']} passed, {counts['skipped']} skipped, 0 failed" in report
    assert f"Rust: {counts['rust_passed']} passed" in report


def test_b17_report_ab_from_saved_comparison():
    _, report = scope_report()
    ab = saved("ab.json")
    assert ab["totals"] == {"same": sum(ab["records"].values()) - len(ab["unavailable_both"]),
                            "unavailable": len(ab["unavailable_both"])}
    assert ab["totals"]["same"] + ab["totals"]["unavailable"] == sum(ab["records"].values())
    assert all(row["class"] == "unavailable" and row["base"] == row["head"]
               for row in ab["differences"])
    assert len(ab["differences"]) == ab["totals"]["unavailable"]
    assert f"A/B: {ab['totals']['same']} identical outcomes, {ab['totals']['unavailable']} unavailable on both sides" in report
    assert f"Pilots: {ab['records']['pilots/default']} documents" in report


def test_b17_report_difffuzz_from_saved_run():
    _, report = scope_report()
    ci = saved("difffuzz-ci.json")
    assert ci["passed"] is True and ci["new"] == []
    assert ci["baseline"]["unreviewed"] == [] and ci["baseline"]["not_reproduced"] == []
    assert f"Difffuzz CI: {ci['baseline']['entries']} baseline entries, 0 new signatures" in report


def test_b17_report_seeded_failures_from_saved_runs():
    _, report = scope_report()
    entries = saved("mutants.json")["mutants"]
    assert len(entries) >= 3 and len({row["name"] for row in entries}) == len(entries)
    assert all(row["mutant"]["exit_code"] != 0 and row["mutant"]["failed_test"]
               and row["restored"]["exit_code"] == 0 for row in entries)
    assert f"Seeded mutants: {len(entries)} failed as expected" in report
    assert all(row["name"] in report for row in entries)
