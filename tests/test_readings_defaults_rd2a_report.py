"""RD-2a's report against its saved evidence (build checklist 20).

Every number docs/readings-defaults/rd2a/DELTA.md states is read back from `evidence/gate.json` and the A/B files
saved beside it. Only saved evidence is read: no live git, build or dump, so the test passes unchanged after a sync
with `main` and after the merge.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "docs/readings-defaults/rd2a"
DELTA = (HERE / "DELTA.md").read_text()
GATE = json.loads((HERE / "evidence/gate.json").read_text())


def test_lean_counts_are_the_gates():
    lean = GATE["lean"]
    assert f"{lean['build_jobs']} jobs, success" in DELTA
    assert (f"{lean['audit_source_files']} source files, {lean['audit_theorems']} theorems "
            f"(base {lean['audit_theorems_base']})") in DELTA
    assert (f"{lean['statements']} statements (base {lean['statements_base']}), {lean['statements_changed']} changed, "
            f"{lean['statements_removed']} removed") in DELTA
    assert lean["statements"] > lean["statements_base"] and lean["statements_changed"] == 0


def test_statement_check_counts():
    rd1, rd2a = GATE["statement_check"]["rd1"], GATE["statement_check"]["rd2a"]
    assert f"RD-1: {rd1['exact']} exact, {rd1['pending']} pending; RD-2a: {rd2a['exact']} exact, " \
           f"{rd2a['pending']} pending" in DELTA
    assert rd2a["exact"] + rd2a["pending"] == rd2a["declarations"]
    assert f"{rd2a['exact']} of {rd2a['declarations']} exact" in DELTA


def test_suite_and_fixture_counts():
    chunks = GATE["suite"]["chunks"]
    passed = ", ".join(str(c["passed"]) for c in chunks[:-1]) + f" and {chunks[-1]['passed']} passed"
    skipped = ", ".join(str(c["skipped"]) for c in chunks[:-1]) + f" and {chunks[-1]['skipped']} skipped"
    assert f"{passed}; {skipped}; 0 failed" in DELTA
    assert all(c["failed"] == 0 for c in chunks)
    assert f"{GATE['suite']['slow_tests']['passed']} passed" in DELTA
    fixtures = GATE["service_fixtures"]
    assert f"{fixtures['tests']} passed, {fixtures['serial_seconds']} s serially" in DELTA
    # the fixture file holds that many tests
    source = (ROOT / fixtures["file"]).read_text()
    assert len(re.findall(r"^def test_", source, re.M)) == fixtures["tests"]


def test_ab_totals_are_the_saved_compares():
    ab = GATE["ab"]
    records = same = unlisted = 0
    for name in ab["files"]:
        compare = json.loads((HERE / "evidence" / name).read_text())
        records += sum(compare["records"].values())
        same += compare["totals"].get("same", 0)
        unlisted += compare["unlisted"]
        assert set(compare["totals"]) == {"same"}
    assert (records, same, unlisted) == (ab["records"], ab["same"], ab["unlisted"])
    assert f"{records} records, {same} the same, {unlisted} unlisted" in DELTA
    assert f"at `{ab['head']}` before the review fixes" in DELTA


def test_latency_rows():
    """Review B2's paired timing: every row of the table is the saved evidence's, both builds named."""
    timing = json.loads((HERE / "evidence" / GATE["latency"]).read_text())
    assert timing["rows"] and timing["before_build"] != timing["after_build"]
    assert f"(`{timing['before_build'][:8]}`)" in DELTA and f"(`{timing['after_build'][:8]}`)" in DELTA
    assert "six calls after a warm-up" in DELTA and timing["calls"] == 6
    for r in timing["rows"]:
        cells = [r[k][side] for k in ("s1_only", "validate", "elaborate") for side in ("before", "after")]
        assert f"| {r['fixed_units']} | " + " | ".join(str(c) for c in cells) + " |" in DELTA
    # the `deny` column is where B2's second admission was most of the cost: lower after at every size
    assert all(r["s1_only"]["after"] < r["s1_only"]["before"] for r in timing["rows"])


def test_seeded_bugs_name_real_tests():
    for bug in GATE["seeded_bugs"]:
        row = re.search(rf"^\| {bug['id']} \| (.*)$", DELTA, re.M)
        assert row, bug["id"]
        assert (ROOT / bug["file"]).exists()
        for test in bug.get("failed", []):
            path, name = test.split("::")
            assert re.search(rf"^def {re.escape(name)}\(", (ROOT / path).read_text(), re.M), test
            assert name in row[1], test
        if "failed_count" in bug:
            assert f"{bug['failed_count']} tests" in row[1]
    assert len(GATE["seeded_bugs"]) >= 3


def test_the_reported_head_is_the_last_commit_listed():
    commits = GATE["commits_before_report"]
    assert len(commits) == len(set(commits)) and all(re.fullmatch(r"[0-9a-f]{8}", c) for c in commits)
    assert f"HEAD before this report, `{commits[-1]}`" in DELTA
