"""B1 report claims are checked from saved evidence, never a moving git diff."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/test-speed-b1/evidence"
sys.path.insert(0, str(ROOT / "tools"))
import test_map  # noqa: E402


def saved(name: str) -> dict:
    return json.loads((EVIDENCE / name).read_text())


def test_ten_shadow_rounds_cover_saved_full_suite_failures():
    rows = saved("shadow.json")["rounds"]
    assert len(rows) == 10
    assert len({row["gate_commit"] for row in rows}) == 10
    assert any(row["full_failure_nodeids"] for row in rows)
    for row in rows:
        gate_file = ROOT / row["gate_file"]
        raw = gate_file.read_bytes()
        gate = json.loads(raw)
        assert hashlib.sha256(raw).hexdigest() == row["gate_sha256"]
        assert gate["commit_sha"] == row["gate_commit"]
        assert all(len(commit) == 40 for commit in row["round_commits"])
        assert gate["status"] == row["gate_status"]
        assert len(row["round_commits"]) == 3
        assert len(row["selected"]) == row["selected_count"] <= row["full_count"]
        failures = sorted({failure["nodeid"] for failure in gate.get("failures", ()) if "nodeid" in failure})
        assert failures == row["full_failure_nodeids"]
        outside = sorted({node.split("::")[0] for node in failures} - set(row["selected"]))
        assert outside == row["failures_outside_selection"] == []


def test_five_manifest_edits_select_saved_map_readers():
    report = saved("manifest-seeds.json")
    raw = (EVIDENCE / "coverage-map.json.gz").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == report["map_sha256"]
    coverage = test_map.load(EVIDENCE / "coverage-map.json.gz")
    assert coverage["version"] == report["map_version"] == test_map.VERSION
    assert len(coverage["tests"]) == report["map_tests"]
    assert sorted(test for test, status in coverage["status"].items() if status["exit"] not in (0, 5)) \
        == sorted(report["map_failed_units"])
    rows = report["seeds"]
    assert len(rows) == 5 and len({row["operation"] for row in rows}) == 5
    for row in rows:
        op_id = row["operation"]
        readers = sorted(coverage["tests"][i] for i in coverage["operations"][op_id])
        assert readers == row["recorded_entry_readers"]
        assert len(coverage["presence"].get(op_id, ())) == row["recorded_presence_readers"]
        assert set(readers) <= set(row["selected"])
        assert "tests/test_assurance_manifest.py" in row["selected"]
        assert len(row["selected"]) == row["selected_count"] < row["full_count"]


def test_six_saved_seeded_bugs_were_rejected_and_restored():
    rows = saved("mutants.json")["mutants"]
    assert len(rows) == 6
    assert {row["file"] for row in rows} >= {
        "tools/select_tests.py", "tools/test_map_recorder.py", "ve/assurance.py",
        "ve/backends/service_schema.py"}
    for row in rows:
        assert row["mutant_exit"] != 0 and row["restored_exit"] == 0
        assert row["test"] in row["failure_excerpt"] and "FAILED" in row["failure_excerpt"]


def test_report_numbers_are_derived_from_saved_evidence():
    text = (ROOT / "docs/test-speed-b1/REPORT.md").read_text()
    shadow = saved("shadow.json")["rounds"]
    seeds = saved("manifest-seeds.json")["seeds"]
    mutants = saved("mutants.json")["mutants"]
    coverage = test_map.load(EVIDENCE / "coverage-map.json.gz")
    assert f"{len(shadow)} fix rounds" in text
    assert f"{sum(len(row['full_failure_nodeids']) for row in shadow)} full-suite test failures" in text
    assert f"{len(seeds)} manifest edits" in text
    assert f"{len(mutants)} seeded bugs" in text
    assert f"{len(coverage['tests'])} units" in text
    assert f"{len(coverage['operations'])} distinct entry-read IDs" in text
    assert f"{len(coverage['presence'])} presence-check IDs" in text
    assert f"{sum(row['selected_count'] == row['full_count'] for row in shadow)} rounds selected all " \
        f"{len(coverage['tests'])} units" in text
    assert f"{sum(row['selection_full'] for row in shadow)} rounds explicitly fell back" in text
    for row in seeds:
        assert f"{row['operation']} | {row['selected_count']}/{row['full_count']}" in text
