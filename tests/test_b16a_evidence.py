"""Batch 16a report checks read committed snapshots, never moving Git refs."""

import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/lean-first/b16a/evidence"
REPORT = ROOT / "docs/lean-first/b16a/REPORT.md"


def saved(name):
    return json.loads((EVIDENCE / name).read_text())


def scope_and_report():
    scope = saved("scope.json")
    report = REPORT.read_text()
    assert scope["range"] == "main..HEAD --no-merges"
    assert scope["commits"] and scope["captured_head"] == scope["commits"][0]
    assert len(scope["commits"]) == len(set(scope["commits"]))
    assert all(re.fullmatch(r"[0-9a-f]{40}", item) for item in scope["commits"])
    assert all(item["commit"] in scope["commits"] for item in scope["files"])
    assert "Source commits (saved): " + ", ".join(scope["commits"]) in report
    return scope, report


def test_report_line_counts_use_saved_main_range():
    scope, report = scope_and_report()
    files = scope["files"]
    assert scope["totals"] == {
        "added": sum(item["added"] for item in files),
        "deleted": sum(item["deleted"] for item in files),
        "lean_added": sum(item["added"] for item in files if item["path"].endswith(".lean")),
        "python_deleted": sum(item["deleted"] for item in files if item["path"].endswith(".py")),
    }
    assert f"Total lines deleted: {scope['totals']['deleted']}" in report
    assert f"Lean lines added: {scope['totals']['lean_added']}" in report
    assert f"Python lines deleted: {scope['totals']['python_deleted']}" in report


def test_report_gate_numbers_use_saved_clean_run():
    scope, report = scope_and_report()
    gate = saved("gate.json")
    counts = gate["counts"]
    assert gate["commit_sha"] == scope["captured_head"]
    assert gate["status"] == "passed" and gate["dirty"] is False
    assert counts["selected"] == counts["passed"] + counts["skipped"] + counts["failed"]
    assert counts["failed"] == 0 and gate["failures"] == []
    assert f"Full gate: passed; {counts['passed']} passed, {counts['skipped']} skipped" in report
    assert f"Rust: {counts['rust_passed']} passed" in report


def test_report_ab_numbers_use_saved_public_outcomes():
    _, report = scope_and_report()
    ab = saved("ab.json")
    assert ab["differences"] == [] and ab["unlisted"] == 0
    assert ab["totals"] == {"same": sum(ab["records"].values())}
    assert f"A/B identical: {ab['totals']['same']} public outcomes" in report
    assert f"Pilots identical: {ab['records']['pilots/default']} documents" in report


def test_report_difffuzz_numbers_use_saved_baselines():
    _, report = scope_and_report()
    ci = saved("difffuzz-ci.json")
    dates = saved("seeds.json")["rows"]
    assert ci["passed"] is True and ci["new"] == []
    assert ci["baseline"]["unreviewed"] == [] and ci["baseline"]["not_reproduced"] == []
    assert len(dates) == 14 and len({item["seed"] for item in dates}) == 14
    assert all(item["head_new"] == item["base_new"] and item["head_only"] == 0
               and item["head_signature_sha256"] == item["base_signature_sha256"]
               for item in dates)
    assert f"CI baseline: {ci['baseline']['entries']} entries, 0 new signatures" in report
    assert f"Date seeds: {len(dates)} paired; {sum(item['head_new'] for item in dates)} inherited signatures; 0 head-only" in report


def test_report_mutants_use_saved_failures():
    _, report = scope_and_report()
    mutants = saved("mutants.json")
    assert len(mutants) >= 3
    assert len({item["mutant"] for item in mutants}) == len(mutants)
    assert all(item["build_exit"] == 0 and item["test_exit"] != 0
               and "FAILED " in item["failure_excerpt"] for item in mutants)
    assert f"Seeded mutants: {len(mutants)} failed as expected" in report
    assert all(item["mutant"] in report for item in mutants)
