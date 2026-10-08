"""RD-4a's report against its saved evidence (build checklist 20).

Every number docs/readings-defaults/rd4a/DELTA.md states is read back from `evidence/gate.json`, the A/B compares and
`evidence/seeded-bugs.json` saved beside it. Only saved evidence is read: no live git, build or dump, so the test
passes unchanged after a sync with `main` and after the merge.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "docs/readings-defaults/rd4a"
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
    assert lean["audit_theorems"] > lean["audit_theorems_base"]


def test_statement_check_counts():
    check = GATE["statement_check"]
    rd1, rd2a, rd4a = check["rd1"], check["rd2a"], check["rd4a"]
    assert (f"RD-1: {rd1['exact']} exact, {rd1['pending']} pending; RD-2a: {rd2a['exact']} exact, "
            f"{rd2a['pending']} pending; RD-4a: {rd4a['exact']} exact, {rd4a['pending']} pending") in DELTA
    assert rd4a["exact"] + rd4a["pending"] == rd4a["declarations"]
    assert f"{rd4a['exact']} of {rd4a['declarations']} exact" in DELTA
    # the four theorems the report names are the batch's
    for name in ("mergeCompanions_extends", "mergeCompanions_identical", "mergeOpenTerms_identical",
                 "split_keeps_links"):
        assert f"`{name}`" in DELTA
    assert rd4a["theorems"] == 4


def test_suite_and_fixture_counts():
    chunks = GATE["suite"]["chunks"]
    passed = ", ".join(str(c["passed"]) for c in chunks[:-1]) + f" and {chunks[-1]['passed']} passed"
    skipped = ", ".join(str(c["skipped"]) for c in chunks[:-1]) + f" and {chunks[-1]['skipped']} skipped"
    assert f"{passed}; {skipped}; 0 failed" in DELTA
    assert all(c["failed"] == 0 and c["errors"] == 0 for c in chunks)
    assert f"full suite in {len(chunks)} chunks (`-n {GATE['suite']['workers']}`" in DELTA
    # every chunk at the reported head, or at the one commit the note names (it differs in no test of those chunks)
    heads = {c["head"] for c in chunks}
    assert heads <= {GATE["commits_before_report"][-1], "f99c84e4"} and "f99c84e4" in GATE["suite"]["note"]
    assert "f99c84e4" in GATE["commits_before_report"]
    fixtures = GATE["service_fixtures"]
    assert f"{fixtures['collected']} passed, {fixtures['serial_seconds']} s serially" in DELTA
    source = (ROOT / fixtures["file"]).read_text()
    assert len(re.findall(r"^def test_", source, re.M)) == fixtures["functions"]


def test_ab_totals_are_the_saved_compares():
    ab = GATE["ab"]
    records = same = unavailable = unlisted = 0
    for name in ab["files"]:
        compare = json.loads((HERE / "evidence" / name).read_text())
        records += sum(compare["records"].values())
        same += compare["totals"].get("same", 0)
        unavailable += compare["totals"].get("unavailable", 0)
        unlisted += compare["unlisted"]
        assert set(compare["totals"]) <= {"same", "unavailable"}
        # an unavailability is the same answer on both sides, never a difference
        for d in compare.get("differences", []):
            assert d["class"] == "unavailable" and d["base"] == d["head"], d["case"]
    assert (records, same, unavailable, unlisted) == (ab["records"], ab["same"], ab["unavailable_both"], ab["unlisted"])
    assert records == same + unavailable and ab["different"] == 0
    assert (f"{records} records, {same} the same, {unavailable} unavailable on both sides with the same answer, "
            f"0 different") in DELTA
    assert f"base `{GATE['base']}`" in DELTA
    for corpus in ab["not_recorded"]:
        assert f"`{corpus.split('/')[0]}`" in DELTA


def test_fixture_table_names_real_tests():
    source = (ROOT / "tests/test_readings_companions_lean.py").read_text()
    rows = re.findall(r"^\| (F-C\d+) \| (.*?) \|", DELTA, re.M)
    assert [r[0] for r in rows] == [f"F-C{k}" for k in range(1, 13)]
    for _, where in rows:
        for name in re.findall(r"`(test_\w+)`", where):
            assert re.search(rf"^def {name}\(", source, re.M), name


def test_seeded_bugs_name_real_tests():
    examples = (ROOT / "lean/VE/Readings/CompanionsExamples.lean").read_text().splitlines()
    for bug in GATE["seeded_bugs"]:
        row = re.search(rf"^\| {bug['id']} \| (.*)$", DELTA, re.M)
        assert row, bug["id"]
        assert (ROOT / bug["file"]).exists()
        assert bug["failed"], bug["id"]
        for test in bug["failed"]:
            path, name = test.split("::")
            name = name.split("[")[0]
            assert re.search(rf"^def {re.escape(name)}\(", (ROOT / path).read_text(), re.M), test
        if len(bug["failed"]) <= 2:
            for test in bug["failed"]:
                assert test.split("::")[1] in row[1], test
        else:
            assert f"{len(bug['failed'])} tests" in row[1]
        for line in bug["guard_errors_at_lines"]:
            assert examples[line - 1].startswith("#guard"), (bug["id"], line)
            assert f"line {line}" in row[1] or f"lines {line}" in row[1] or f"and {line}" in row[1], (bug["id"], line)
        for theorem in bug["sorried"]:
            assert f"`{theorem}`" in row[1], (bug["id"], theorem)
    assert len(GATE["seeded_bugs"]) >= 3
    # the evidence file the report cites holds the same bugs (M11 was run by hand on another test file)
    saved = json.loads((HERE / "evidence/seeded-bugs.json").read_text())
    assert [b["id"] for b in saved] == [b["id"] for b in GATE["seeded_bugs"] if b["id"] != "M11"]


def test_the_reported_head_is_the_last_commit_listed():
    commits = GATE["commits_before_report"]
    assert len(commits) == len(set(commits)) and all(re.fullmatch(r"[0-9a-f]{8}", c) for c in commits)
    assert f"HEAD before this report, `{commits[-1]}`" in DELTA
